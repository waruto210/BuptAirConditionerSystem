import threading

class MainMachine:

    def __init__(self):
        self.wait_list = []
        self.run_list = []
        self.lock = threading.RLock()
        self.env_temp = 25

    def get_list(self):
        self.lock.acquire()
        try:
            return self.wait_list, self.run_list
        finally:
            self.lock.release()

    def get_temp(self):
        self.lock.acquire()
        try:
            return self.env_temp
        finally:
            self.lock.release()
    def set_temp(self, env=None):
        self.lock.acquire()
        try:
            if env != None:
                self.env_temp = env
        finally:
            self.lock.release()

machine = MainMachine()