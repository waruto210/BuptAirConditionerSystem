import threading
from customer.slave import Slave
from operator import attrgetter
import time
from customer.models import State, get_current_ticket
import datetime
import math
from master.views import scheduler

CAL_INTERVAL = 5
WAIT_INTERVAL = 30
RATE_INTERVAL = 15


class MainMachine:

    def __init__(self):

        self.service_queue: list[Slave] = []
        self.wait_queue: list[Slave] = []
        self.pause_queue: list[Slave] = []

        self.lock = threading.RLock()
        # 默认参数
        self.off_rate = 2
        self.power_on = True
        self.default_work_mode = 0
        self.default_sp_mode = 1
        self.env_temp = 26
        self.cold_sub = 18
        self.cold_sup = 26
        self.hot_sub = 26
        self.hot_sup = 30
        self.fees = [1 / 3, 2 / 3, 1]
        self.max_run = 1

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
            self.fees = self.fees * fee
            self.max_run = max_run
        finally:
            self.lock.release()

    def add_service(self, room_id: str, phone_num: str, req_time: int, sp_mode: int):
        s = Slave(room_id=room_id, phone_num=phone_num, req_time=req_time, sp_mode=sp_mode, is_run=True)
        state = State.objects.get(room_id=room_id)
        state.is_work = True
        state.save()

        ticket = get_current_ticket(room_id, phone_num)
        ticket.schedule_count += 1
        ticket.save()

        self.service_queue.append(s)

    def add_wait(self, room_id: str, phone_num: str, req_time: int, sp_mode: int, timer=True):
        s = Slave(room_id=room_id, phone_num=phone_num, req_time=req_time, sp_mode=sp_mode, is_run=False)
        print("room_id: ", room_id, "添加到等待队列")
        if timer:
            s.wait_timer = True
            print("room_id: ", room_id, "设置等待计时器")
            scheduler.add_job(wait, 'date', id=room_id + 'wait',
                              run_date=(datetime.datetime.now() + datetime.timedelta(seconds=WAIT_INTERVAL)),
                              args=[room_id])
        state = State.objects.get(room_id=room_id)
        state.is_work = False
        state.save()
        self.wait_queue.append(s)

    def delete_service(self, room_id: str):
        for i in range(len(self.service_queue)):
            if self.service_queue[i].room_id == room_id:
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
        s.is_run = False
        state = State.objects.get(room_id=room_id)

        state.is_work = False
        state.save()
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
        if len(self.wait_queue) == 0:
            return None
        self.wait_queue.sort(key=attrgetter('inverse_sp', 'req_time'))
        s = self.delete_wait(self.wait_queue[0].room_id)
        self.add_service(room_id=s.room_id, phone_num=s.phone_num, req_time=int(time.time()), sp_mode=s.sp_mode)
        return s

    def get_pos(self, room_id):
        for item in self.service_queue:
            if item.room_id == room_id:
                return 'service'
        for item in self.wait_queue:
            if item.room_id == room_id:
                return 'wait'
        for item in self.service_queue:
            if item.room_id == room_id:
                return 'pause'

    def get_s(self, room_id):
        for item in self.service_queue:
            if item.room_id == room_id:
                return item
        for item in self.wait_queue:
            if item.room_id == room_id:
                return item

    def set_wait_timer(self, room_id):
        for item in self.wait_queue:
            if item.room_id == room_id:
                item.wait_timer = False

    def change_sp(self, room_id, sp_mode):
        for item in self.service_queue:
            if item.room_id == room_id:
                item.sp_mode = sp_mode
                item.inverse_sp = 2 - sp_mode
                return

    def get_rate_fee(self, room_id):
        self.lock.acquire()
        try:
            for item in self.service_queue:
                if item.room_id == room_id:
                    return item.rate, self.fees[item.sp_mode]
        finally:
            self.lock.release()

    def is_room_work(self, room_id):
        self.lock.acquire()
        try:
            for item in self.service_queue:
                if item.room_id == room_id:
                    return True
            return False
        finally:
            self.lock.release()

    def contain_delete(self, room_id):
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
                self.add_wait(room_id, phone_num, req_time, sp_mode)
            else:
                self.add_wait(room_id, phone_num, req_time, sp_mode, timer=False)

    # 结束等待的请求，返回来处理
    def revive(self, room_id):
        # 风速最低，服务时间最长的拍第0
        self.set_wait_timer(room_id)
        self.service_queue.sort(key=attrgetter('sp_mode', 'req_time'))
        s = self.get_s(room_id)
        if self.service_queue[0].sp_mode <= s.sp_mode:
            self.move_to_wait(self.service_queue[0].room_id)
            self.move_to_service(room_id)

    def change_rate(self, room_id):
        for item in self.service_queue:
            if item.room_id == room_id:
                if item.sp_mode == 0:
                    item.rate *= 0.8
                elif item.sp_mode == 2:
                    item.rate *= 1.2
                print("room: ", room_id, " rate chang to: ", item.rate)
                return

    def get_is_work(self, room_id):
        for item in self.service_queue:
            if item.room_id == room_id:
                return item.is_run
        return None


machine = MainMachine()


def cost_temp(room_id, phone_num):
    state = State.objects.get(room_id=room_id)
    curr_temp = state.curr_temp
    goal_temp = state.goal_temp
    print("room_id: ", room_id, "服务中")
    rate, fee = machine.get_rate_fee(room_id=room_id)

    curr_temp = cal_curr_temp(curr_temp, goal_temp, rate)
    delta_fee = fee * CAL_INTERVAL / 60
    print("cal cost and temp: ", room_id, 'curr_temp is:', curr_temp)
    # 记录温度和费用
    state.curr_temp = curr_temp
    state.total_cost += delta_fee
    ticket = get_current_ticket(room_id, phone_num)
    ticket.cost += delta_fee
    ticket.service_duration += CAL_INTERVAL
    ticket.save()
    state.save()

    if math.isclose(goal_temp, curr_temp):
        machine.lock.acquire()
        try:
            # 将当前房间加入停止队列
            machine.move_to_pause(room_id)
            # 选择一个等待状态的放假加入服务队列
            machine.wait_to_service()
        finally:
            machine.lock.release()
    return


def rate_change(room_id):
    print("room_id: ", room_id, " change_rate")
    machine.lock.acquire()
    try:
        machine.change_rate(room_id)
    finally:
        machine.lock.release()
    return


# 等待时温度变化
def temp(room_id):
    state = State.objects.get(room_id=room_id)
    curr_temp = state.curr_temp
    env_temp = machine.env_temp
    off_rate = machine.off_rate
    if math.isclose(env_temp, curr_temp) is not True:
        curr_temp = cal_curr_temp(curr_temp, env_temp, off_rate)
        state.curr_temp = curr_temp
        print("room_id: ", room_id, "等待中, ", "curr_temp: ", curr_temp)
        state.save()
    return


def wait(room_id):
    print("room_id: ", room_id, " 等待超时")
    machine.lock.acquire()
    try:
        machine.revive(room_id)
    finally:
        machine.lock.release()
    return


# 达到目标温度后温度变化
def pause(room_id, phone_num):
    state = State.objects.get(room_id=room_id)
    curr_temp = state.curr_temp
    goal_temp = state.goal_temp
    env_temp = machine.env_temp
    off_rate = machine.off_rate
    #  和目标温度温差尚未达到1度
    if math.fabs(goal_temp - curr_temp) < 1:
        # 未回落到室温
        if math.isclose(env_temp, curr_temp) is not True:
            curr_temp = cal_curr_temp(curr_temp, env_temp, off_rate)
            state.curr_temp = curr_temp
            state.save()
            print("room_id :", room_id, "向室温回落", curr_temp)
    # 温差达到1度
    if math.fabs(goal_temp - curr_temp) >= 0.9999:
        print('room_id:' + room_id + " 服务苏醒")
        machine.lock.acquire()
        try:
            s = machine.delete_pause(room_id)
            machine.new_request(room_id=s.room_id, phone_num=phone_num, req_time=int(time.time()), sp_mode=s.sp_mode)
        finally:
            machine.lock.release()
    return


def cal_curr_temp(curr_temp, target_temp, rate):
    if target_temp > curr_temp:
        curr_temp += rate * CAL_INTERVAL / 60
        curr_temp = min(target_temp, curr_temp)
    else:
        curr_temp -= rate * CAL_INTERVAL / 60
        curr_temp = max(target_temp, curr_temp)
    return curr_temp
