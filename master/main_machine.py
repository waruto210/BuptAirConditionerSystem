import threading
from customer.slave import Slave
from operator import attrgetter
import time


class MainMachine:

    def __init__(self):
        self.wait_queue: list[Slave] = []
        self.max_run = 1
        self.lock = threading.RLock()
        self.env_temp = 25

    def get_temp(self):
        self.lock.acquire()
        try:
            return self.env_temp
        finally:
            self.lock.release()

    def set_temp(self, env):
        self.lock.acquire()
        try:
            self.env_temp = env
        finally:
            self.lock.release()

    def add_slave(self, room_id: str, req_time: int, sp_mode: int, is_pause: int):
        s = Slave(room_id=room_id, req_time=req_time, sp_mode=sp_mode, is_pause=is_pause)
        self.wait_queue.append(s)

    def delete_slave(self, room_id: str):
        for i in range(len(self.wait_queue)):
            if self.wait_queue[i].room_id == room_id:
                self.wait_queue.pop(i)
                return

    def change_sp(self, room_id, sp_mode):
        for item in self.wait_queue:
            if item.room_id == room_id:
                item.sp_mode = sp_mode
                item.inverse_sp = 2 - sp_mode
                return

    def set_pause(self, room_id: str, is_pause: int):
        for item in self.wait_queue:
            if item.room_id == room_id:
                item.is_pause = is_pause
                # 重新加入请求送风的队列中，修改开始等待的时间
                if is_pause == 0:
                    item.req_time = int(time.time())
                return

    def get_is_pause(self, room_id: str):
        for item in self.wait_queue:
            if item.room_id == room_id:
                return item.is_pause
        return None

    def schedule(self):
        self.wait_queue.sort(key=attrgetter('is_pause', 'inverse_sp', 'req_time'))

        count: int = 0
        for item in self.wait_queue:
            if count < self.max_run:
                if item.is_pause == 0:
                    if item.is_run is not True:
                        # 调度开始送风，更改等待时间
                        item.req_time = int(time.time())
                        item.is_run = True
                    count += 1
                elif item.is_pause == 1:
                    item.is_run = False
            else:
                if item.is_run is True:
                    item.is_run = False
                    # 被调度停止送风，更改开始等待时间
                    item.req_time = int(time.time())
        print('after schedule: ', self.wait_queue)

    def get_is_work(self, room_id):
        for item in self.wait_queue:
            if item.room_id == room_id:
                return item.is_run
        return None


machine = MainMachine()
