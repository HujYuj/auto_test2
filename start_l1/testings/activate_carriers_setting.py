class ActivateCarriersSetting:
    def __init__(self, ABIL_SLOT_NUMBER, RRU, TDD_SWITCH, CASE_TYPE, DL_TM, UL_TM, BANDWIDTH:list, FREQUENCY:list, POWER:list):
        self.ABIL_SLOT_NUMBER = ABIL_SLOT_NUMBER
        self.RRU = RRU
        self.TDD_SWITCH = TDD_SWITCH
        self.CASE_TYPE = CASE_TYPE
        self.DL_TM = DL_TM
        self.BANDWIDTH = BANDWIDTH
        self.FREQUENCY = FREQUENCY
        self.POWER = POWER
        self.UL_TM = UL_TM

    def get_abil_slot_number(self):
        return self.ABIL_SLOT_NUMBER

    def get_rru(self):
        return self.RRU

    def get_tdd_switch(self):
        return self.TDD_SWITCH

    def get_case_type(self):
        return self.CASE_TYPE

    def get_dl_tm(self):
        return self.DL_TM

    def get_ul_tm(self):
        return self.UL_TM

    def get_bandwidth(self):
        return self.BANDWIDTH

    def get_single_bandwidth(self):
        return self.BANDWIDTH[0]

    def get_frequency(self):
        return self.FREQUENCY

    def get_single_frequency(self):
        return self.FREQUENCY[0]

    def get_power(self):
        return self.POWER

    def get_single_power(self):
        return self.POWER[0]

    def get_made_num(self):
        return 8 if self.get_rru() == "AEQE" else 4

    def get_mades(self):
        return ['192.168.101.2', '192.168.101.3', '192.168.101.4', '192.168.101.5'] if self.get_made_num() == 4 else \
            ['192.168.101.2', '192.168.101.3', '192.168.101.4', '192.168.101.5',
             '192.168.101.6', '192.168.101.7', '192.168.101.8', '192.168.101.9']
