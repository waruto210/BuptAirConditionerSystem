import threading
from customer.slave import Slave
from operator import attrgetter
import time
import datetime
import math
from master.views import scheduler
import logging
from record_manager.RecordManager import RecordManager
from airconfig.config import config
from customer.models import State
from django.core import serializers

logger = logging.getLogger('collect')
CAL_INTERVAL = config.cal_interval
WAIT_INTERVAL = config.wait_interval
RATE_INTERVAL = config.rate_interval
TEMP_RATE = config.temp_rate
# ROOM_LIST = ['101', '102', '103', '104', '105', '201', '202', '203', '204', '205']


class MainMachine:
    def __init__(self):

        self.service_queue: list[Slave] = []
        self.wait_queue: list[Slave] = []
        self.pause_queue: list[Slave] = []

        self.lock = threading.RLock()
        # 默认参数
        self.off_rate = TEMP_RATE # 停止送风后室温变化率
        self.power_on = True
        self.default_work_mode = 0
        self.default_sp_mode = 1
        self.env_temp = 26
        self.cold_sub = 18
        self.cold_sup = 26
        self.hot_sub = 26
        self.hot_sup = 30
        self.fee_rates = [1 / 3, 2 / 3, 1] # 低中高风速的费率
        self.max_run = 2


    def get_params(self):
        self.lock.acquire()
        try:
            return self.default_work_mode, self.default_sp_mode, self.cold_sub, self.cold_sup, \
                   self.hot_sub, self.hot_sup, self.env_temp
        finally:
            self.lock.release()

    def is_on(self):
        self.lock.acquire()
        try:
            return self.power_on
        finally:
            self.lock.release()

    def init_default(self, is_on):
        self.lock.acquire()
        try:
            self.power_on = is_on
        finally:
            self.lock.release()

    def set_params(self, word_mode, cold_sub, cold_sup,
                   hot_sub, hot_sup, env_temp, fee, max_run):
        self.lock.acquire()
        try:
            self.default_work_mode = word_mode
            self.env_temp = env_temp
            self.cold_sub = cold_sub
            self.cold_sup = cold_sup
            self.hot_sub = hot_sub
            self.hot_sup = hot_sup
            self.fee_rates = self.fee_rates * fee
            self.max_run = max_run
        finally:
            self.lock.release()

    def add_service(self, room_id: str, phone_num: str, req_time: int, sp_mode: int):
        s = Slave(room_id=room_id, phone_num=phone_num, req_time=req_time, sp_mode=sp_mode, temp_rate=TEMP_RATE)
        if sp_mode != 1:
            scheduler.add_job(change_temp_rate, 'interval', id=room_id + 'change_temp_rate', seconds=RATE_INTERVAL,
                              args=[room_id])
        # 修改工作状态
        s.set_is_work(1)
        s.change_fan_spd(sp_mode)
        # 增加一次被调度
        RecordManager.plus_ticket_schedule_count(room_id, phone_num)
        self.service_queue.append(s)

    def add_wait(self, room_id: str, phone_num: str, req_time: int, sp_mode: int, timer=True):
        s = Slave(room_id=room_id, phone_num=phone_num, req_time=req_time, sp_mode=sp_mode, temp_rate=TEMP_RATE)
        logger.info("room_id: " + str(room_id) + "添加到等待队列")
        if timer:
            s.wait_timer = True
            logger.info("room_id: " + str(room_id) + "设置等待计时器")
            scheduler.add_job(finish_wait, 'date', id=room_id + 'wait',
                              run_date=(datetime.datetime.now() + datetime.timedelta(seconds=WAIT_INTERVAL)),
                              args=[room_id])
        # 修改工作状态
        s.set_is_work(0)
        s.change_fan_spd(sp_mode)
        self.wait_queue.append(s)

    def delete_if_exists(self, room_id):
        for item in self.service_queue:
            if item.room_id == room_id:
                self.delete_service(room_id)
                return
        for item in self.wait_queue:
            if item.room_id == room_id:
                self.delete_wait(room_id)
                return
        for item in self.pause_queue:
            if item.room_id == room_id:
                self.delete_pause(room_id)
                return

    def delete_service(self, room_id: str):
        for i in range(len(self.service_queue)):
            if self.service_queue[i].room_id == room_id:
                if self.service_queue[i].sp_mode != 1:
                    scheduler.remove_job(job_id=room_id + 'change_temp_rate')
                return self.service_queue.pop(i)

    def delete_wait(self, room_id: str):
        for i in range(len(self.wait_queue)):
            if self.wait_queue[i].room_id == room_id:
                if self.wait_queue[i].wait_timer is True:
                    scheduler.remove_job(job_id=(room_id + 'wait'))
                return self.wait_queue.pop(i)

    def delete_pause(self, room_id: str):
        for i in range(len(self.pause_queue)):
            if self.pause_queue[i].room_id == room_id:
                return self.pause_queue.pop(i)

    def move_to_pause(self, room_id):
        s = self.delete_service(room_id)
        # 修改状态
        s.set_is_work(2)
        self.pause_queue.append(s)

    def move_to_wait(self, room_id):
        s = self.delete_service(room_id)
        self.add_wait(room_id=room_id, phone_num=s.phone_num, req_time=int(time.time()), sp_mode=s.sp_mode)
        return s

    def move_to_service(self, room_id):
        s = self.delete_wait(room_id)
        self.add_service(room_id=room_id, phone_num=s.phone_num, req_time=int(time.time()), sp_mode=s.sp_mode)
        return s

    def wait_to_service(self):
        if len(self.wait_queue) == 0 or len(self.service_queue) == self.max_run:
            return
        self.wait_queue.sort(key=attrgetter('inverse_sp', 'req_time'))
        s = self.delete_wait(self.wait_queue[0].room_id)
        self.add_service(room_id=s.room_id, phone_num=s.phone_num, req_time=int(time.time()), sp_mode=s.sp_mode)
        return s

    def new_request(self, room_id: str, phone_num: str, req_time: int, sp_mode: int):
        if len(self.service_queue) < self.max_run:
            self.add_service(room_id, phone_num, req_time, sp_mode)
        else:
            # 风速最低，服务时间最长的拍第0
            self.service_queue.sort(key=attrgetter('sp_mode', 'req_time'))
            if self.service_queue[0].sp_mode < sp_mode:
                self.move_to_wait(self.service_queue[0].room_id)
                self.add_service(room_id, phone_num, req_time, sp_mode)
            elif self.service_queue[0].sp_mode == sp_mode:
                # 优先级相当，要添加计时器
                self.add_wait(room_id, phone_num, req_time, sp_mode)
            else:
                # 优先级低，不断等
                self.add_wait(room_id, phone_num, req_time, sp_mode, timer=False)

    # 结束等待的请求，返回来处理
    def wait_over(self, room_id):
        # 风速最低，服务时间最长的排第0
        self.false_wait_timer(room_id)
        self.service_queue.sort(key=attrgetter('sp_mode', 'req_time'))
        s = self.get_slave(room_id)
        if self.service_queue[0].sp_mode <= s.sp_mode:
            self.move_to_wait(self.service_queue[0].room_id)
            self.move_to_service(room_id)

    def change_rate(self, room_id):
        machine.lock.acquire()
        try:
            for item in self.service_queue:
                if item.room_id == room_id:
                    if item.sp_mode == 0:
                        item.temp_rate *= 0.8
                    elif item.sp_mode == 2:
                        item.temp_rate *= 1.2
                    logger.info("room_id: " + str(room_id) + " 温度变化率: " + str(item.temp_rate))
                    return
        finally:
            self.lock.release()

    def get_queue_pos(self, room_id):
        for item in self.service_queue:
            if item.room_id == room_id:
                return 'service'
        for item in self.wait_queue:
            if item.room_id == room_id:
                return 'wait'
        for item in self.service_queue:
            if item.room_id == room_id:
                return 'pause'

    def get_slave(self, room_id):
        for item in self.service_queue:
            if item.room_id == room_id:
                return item
        for item in self.wait_queue:
            if item.room_id == room_id:
                return item
        for item in self.pause_queue:
            if item.room_id == room_id:
                return item
        return None

    def false_wait_timer(self, room_id):
        for item in self.wait_queue:
            if item.room_id == room_id:
                item.wait_timer = False

    def get_rate_fee(self, room_id):
        self.lock.acquire()
        try:
            for item in self.service_queue:
                if item.room_id == room_id:
                    return item.temp_rate, self.fee_rates[item.sp_mode]
        finally:
            self.lock.release()

    def change_goal_temp(self, room_id, goal_temp):
        try:
            self.lock.acquire()
            s = self.get_slave(room_id=room_id)
            s.change_goal_temp(goal_temp=goal_temp)
        finally:
            self.lock.release()

    def change_work_mode(self, room_id, work_mode):
        try:
            self.lock.acquire()
            s = self.get_slave(room_id=room_id)
            s.change_work_mode(work_mode=work_mode)
        finally:
            self.lock.release()

    def change_fan_speed(self, room_id, phone_num, sp_mode):
        self.lock.acquire()
        try:
            # 删掉旧请求，调度等待队列
            self.delete_if_exists(room_id)
            self.wait_to_service()
            # 加入新请求
            self.new_request(room_id=room_id, phone_num=phone_num, req_time=int(time.time()), sp_mode=sp_mode)
        finally:
            self.lock.release()

    def cal_cost_and_temp(self, room_id, phone_num):
        self.lock.acquire()
        try:
            s = self.get_slave(room_id=room_id)
            curr_temp = s.get_curr_temp()
            goal_temp = s.get_goal_temp()

            temp_rate = s.temp_rate
            fee_rate = self.fee_rates[s.sp_mode]
            if temp_rate is None or fee_rate is None:
                logger.error("get rate and fee error!")
                return
            curr_temp = cal_curr_temp(curr_temp, goal_temp, temp_rate)
            logger.info("room_id: " + str(room_id) + " 服务中," + "当前温度:" + str(curr_temp))
            delta_fee = fee_rate * CAL_INTERVAL / 60

            # 记录温度和费用
            s.set_curr_temp(curr_temp)
            s.add_fee(delta_fee)
            RecordManager.plus_ticket_cost(room_id, phone_num, delta_fee, CAL_INTERVAL)
        finally:
            self.lock.release()

    def cal_wait_temp(self, room_id):
        self.lock.acquire()
        try:
            s = self.get_slave(room_id)
            curr_temp = s.get_curr_temp()
            env_temp = self.env_temp
            off_rate = self.off_rate
            if math.isclose(env_temp, curr_temp) is not True:
                curr_temp = cal_curr_temp(curr_temp, env_temp, off_rate)
                s.set_curr_temp(curr_temp)
                logger.info("room_id: " + str(room_id) + "等待中, 当前温度: " + str(curr_temp))
        finally:
            self.lock.release()

    def finish_wait(self, room_id):
        self.lock.acquire()
        try:
            self.wait_over(room_id)
        finally:
            self.lock.release()
        return

    def cal_pause_temp(self, room_id):
        self.lock.acquire()
        try:
            s = self.get_slave(room_id)
            curr_temp = s.get_curr_temp()
            goal_temp = s.get_goal_temp()
            env_temp = self.env_temp
            off_rate = self.off_rate
            #  和目标温度温差尚未达到1度
            if math.fabs(goal_temp - curr_temp) < 1:
                # 未回落到室温
                if math.isclose(env_temp, curr_temp) is not True:
                    curr_temp = cal_curr_temp(curr_temp, env_temp, off_rate)
                    s.set_curr_temp(curr_temp)
                    logger.info("room_id: " + str(room_id) + "向室温回落到" + str(curr_temp))
        finally:
            self.lock.release()

    def one_room_power_off(self, room_id):
        self.lock.acquire()
        try:
            s = self.get_slave(room_id)
            if s is not None:
                s.set_is_work(None)
                s.set_is_on(False)
                s.set_curr_temp(self.env_temp)
            self.delete_if_exists(room_id)
            self.wait_to_service()
        finally:
            self.lock.release()

    def one_room_power_on(self, room_id, phone_num, goal_temp, sp_mode, work_mode):
        self.lock.acquire()
        try:
            self.new_request(room_id=room_id, phone_num=phone_num, req_time=int(time.time()), sp_mode=sp_mode)
            s = self.get_slave(room_id)
            s.set_is_on(True)
            s.change_goal_temp(goal_temp)
            s.set_curr_temp(self.env_temp)
            s.change_work_mode(work_mode)
            return s.get_is_work()
        finally:
            self.lock.release()

    def one_room_pause(self, room_id):
        self.lock.acquire()
        try:
            # 将当前房间加入停止队列
            self.move_to_pause(room_id)
            # 选择一个等待状态的放假加入服务队列
            self.wait_to_service()
        finally:
            self.lock.release()

    def one_room_restart(self, room_id, phone_num):
        self.lock.acquire()
        try:
            s = self.delete_pause(room_id)
            self.new_request(room_id=room_id, phone_num=phone_num, req_time=int(time.time()), sp_mode=s.sp_mode)
        finally:
            self.lock.release()
        return s.get_is_work()

    def get_one_room_state(self, room_id):
        self.lock.acquire()
        try:
            s = self.get_slave(room_id)
            return s.get_poll_state()
        finally:
            self.lock.release()

    def check_info(self):
        self.lock.acquire()
        try:
            ret = serializers.serialize('json', State.objects.all())
            return ret
        finally:
            self.lock.release()

    def check_one_room(self, room_id):
        self.lock.acquire()
        try:
            ret = serializers.serialize('json', State.objects.filter(room_id=room_id))
            return ret
        finally:
            self.lock.release()


machine = MainMachine()


def cal_service_cost_temp(room_id, phone_num):
    machine.cal_cost_and_temp(room_id, phone_num)


def change_temp_rate(room_id):
    machine.change_rate(room_id)


# 等待时温度变化
def cal_wait_temp(room_id):
    machine.cal_wait_temp(room_id)


def finish_wait(room_id):
    logger.info("room_id: " + str(room_id) + " 等待超时")
    machine.finish_wait(room_id)


# 达到目标温度后温度变化
def cal_pause_temp(room_id):
    machine.cal_pause_temp(room_id)


def cal_curr_temp(curr_temp, target_temp, rate):
    if target_temp > curr_temp:
        curr_temp += rate * CAL_INTERVAL / 60
        curr_temp = min(target_temp, curr_temp)
    else:
        curr_temp -= rate * CAL_INTERVAL / 60
        curr_temp = max(target_temp, curr_temp)
    return curr_temp
