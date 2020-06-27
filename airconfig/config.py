class AirConfig:
    def __init__(self):
        self.room_list = ['101', '102', '103', '104', '105', '201', '202', '203', '204', '205']
        self.cal_interval = 10
        self.wait_interval = 60
        self.temp_rate = 0.5
        self.room_temp = {'101': 32,
                          '102': 28,
                          '103': 30,
                          '104': 29,
                          '105': 35,
                          '106': 25,
                          '107': 25,
                          '108': 25,
                          '109': 25,
                          '110': 25}


config = AirConfig()
