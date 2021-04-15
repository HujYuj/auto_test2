'''
Created on Feb 21, 2019

@author: hwiv
'''
from ctypes import *
import time,pyvisa,math,string,logging
try:
    from connection import _COM,_Shell
except:
    from .connection import _COM,_Shell

class Instrument(object):
    def __init__(self):
        nrpfile = '.\\DLL\\NRP_Z.dll'
        msfile = '.\\DLL\\MS2691A.dll'
        smufile = '.\\DLL\\SMU200.dll'
        self.dll = cdll.LoadLibrary(nrpfile)
        self.SA_Handlerdll = cdll.LoadLibrary(msfile)
        self.smudll = cdll.LoadLibrary(smufile)

    def Init_NRP(self,pID,sn):
        ''' sn should be string, eg: Init_NRP('103123'), '103123' is from NRP_Z21 power viewer
            Z11 productID: 0x000c, Z21 productID: 0x0003
        '''
        szPara = create_string_buffer('/0'*100)
        intPara = c_int()
        szPara.value = "USB::0x0aad::" + pID +"::" + sn   #
        self.dll.NRP_Init(byref(szPara), byref(intPara));
        nrpHandle = intPara.value
        if nrpHandle == 0:
            print("Power sensor init failed!")
        return nrpHandle

    def read_NRP_value(self,nrpHandle,freq,offset):
        ''' sn should be string, eg: read_NRP_value(handle,2925,0), handle is from Init_NRP(sn)
        '''
        doublePara = c_double(0.0)
        self.dll.NRP_Measure(nrpHandle,c_double(freq),c_double(offset),byref(doublePara))
    #   dll.NRP_Close(nrpHandle)
        return doublePara.value

    def Close_NRP(self,nrpHandle):
        ''' sn should be string, eg: read_NRP_value(handle,2925,0), handle is from Init_NRP(sn)
        '''
    #    dll = CDLL(".\\DLL\\NRP_Z.dll")
        self.dll.NRP_Close(nrpHandle)

    def Set_MS2691A_value(self,msHandle,freq,offset,power):
        ''' Set_MS2691A_value('192.168.1.103','FDD','20Mhz',2529,20) , freq should in [50Hz,6.0GHz], power is -70dBm
        '''
        self.SA_Handlerdll.MS_RFOFF(msHandle)
        time.sleep(1)
        self.SA_Handlerdll.MS_SetSignal(msHandle, c_double(freq), c_double(power), c_double(offset))
        self.SA_Handlerdll.MS_RFON(msHandle)
        print("Set MS2691A frequency to %f...... Cable loss is %f"%(freq,offset))
        time.sleep(1)

    def Close_MS2961A(self,msHandle):
    #    dll.MS_RFOFF(msHandle)
        self.SA_Handlerdll.MS_Close(msHandle)

    def RF_off_MS2961A(self,msHandle):
        self.SA_Handlerdll.MS_RFOFF(msHandle)

    def Init_SMU200(self,ipadd):
        szPara = create_string_buffer('/0'*100)
        szPara.value = ("TCPIP::" + ipadd + "::INSTR")
        re = self.smudll.SMU_Init(byref(szPara), c_short(0), c_short(0));
        if re < 0 :
            print('SMU200A initializing failed, please check your connection or address!!\n')

        else:
            print("SMU200A initializing...... ok.")
        return re

    def Set_SMU200A_and_RFon(self,freq,offset,power,bandwidth):
        self.smudll.SMU_RFOFF()
        time.sleep(0.2)
        self.smudll.SMU_SetLTETDDSignal(c_double(freq), c_double(power), c_double(bandwidth), c_double(offset))
        self.smudll.SMU_RFON()
        print("Set MSU200A freqency to %f...... Cable loss is %f"%(freq,offset))
        time.sleep(0.5)

    def SignalGen_Init(self,sgtype,ipadd,package,patten):
        if sgtype == 'RS':
            Handle = self.Init_SMU200(ipadd)
        elif sgtype == 'Anritsu':
            Handle = self.Init_MS2961A(ipadd,package,patten)
        else:
            print("\n############\nPlease check if the SG_type you input is right.\n##############\n")
        return Handle

    def SignalGen_RF_OFF(self,sgtype,msHandle):
        if sgtype == 'RS':
            self.smudll.SMU_RFOFF()
        elif sgtype == 'Anritsu':
            self.SA_Handlerdll.MS_RFOFF(msHandle)
        else:
            print("\n############\nPlease check if the SG_type you input is right.\n##############\n")

    def SignalGen_Set_Signal(self,sgtype,msHandle,freq,offset,power,bandwidth):
        if sgtype == 'RS':
            self.Set_SMU200A_and_RFon(freq,offset,power,bandwidth)
        elif sgtype == 'Anritsu':
            self.Set_MS2691A_value(msHandle,freq,offset,power)
        else:
            print("\n############\nPlease check if the SG_type you input is right.\n##############\n")

    def SignalGen_Close(self, sgtype,msHandle):
        if sgtype == 'RS':
    #        dll = cdll.LoadLibrary(".\\DLL\\SMU200.dll")
            self.smudll.SMU_Close()
        elif sgtype == 'Anritsu':
    #        dll = cdll.LoadLibrary(".\\DLL\\MS2691A.dll")
            self.SA_Handlerdll.MS_Close(msHandle)
        else:
            print("\n############\nPlease check if the SG_type you input is right.\n##############\n")


class visaInstrument(object):

    def __init__(self):
        self.visaDLL = 'c:/windows/system32/visa64.dll'
        self.resourceManager = pyvisa.ResourceManager(self.visaDLL)
    #SG related function
    def SignalGen_Init(self,pID):
        try:
            self.SG_Handler = self.resourceManager.open_resource("TCPIP0::%s::INSTR"%pID)
            self.SG_Handler.write("*RST")
            return True
        except Exception:
            logging.info('SG initializing failed, please check your connection or address!!\n')
            return False
    def MS2691A_SG_Init(self,frequency,ofsval,outlev,pat,wav):
        ofsval = -float(ofsval)
        time.sleep(0.11)
        self.SG_Handler.write("INST SG")
        time.sleep(0.11)
        self.SG_Handler.write("INST:DEF")
        time.sleep(0.11)
        if pat!="":
            self.SG_Handler.write("MMEM:LOAD:WAV \""+pat+"\",\""+wav+"\"")
            time.sleep(4)
            self.SG_Handler.write("RAD:ARB:WAV \""+pat+"\",\""+wav+"\"")
            time.sleep(2)
            self.SG_Handler.write("OUTP:MOD on")
            time.sleep(1)
        else:
            self.SG_Handler.write("MOD OFF")
            time.sleep(0.11)
        self.SG_Handler.write("freq " +str(float(frequency))+"MHz")

        time.sleep(0.11)
        self.SG_Handler.write("DISP:ANN:AMPL:UNIT DBM")
        time.sleep(0.11)
        self.SG_Handler.write("UNIT:POW DBM")
        time.sleep(0.11)
        self.SG_Handler.write("POW:OFFS " + str(ofsval))
        time.sleep(0.11)
        self.SG_Handler.write("POW:OFFS:STAT ON")
        time.sleep(0.11)
        self.SG_Handler.write("POW " + str(outlev))
        time.sleep(0.11)


    def MS2691A_RF_on(self):

        self.SG_Handler.write("INST SG")
        time.sleep(0.11)
        self.SG_Handler.write("outp on")
        time.sleep(0.11)

    def MS2691A_RF_off(self):
        self.SG_Handler.write("INST SG")
        time.sleep(0.11)
        self.SG_Handler.write("outp off")
        time.sleep(0.11)

    def MS2691A_Set_Signal(self,freq,ofsval,outlev):
        self.SG_Handler.write("freq "+str(float(freq))+'MHz')
        self.SG_Handler.write("POW:OFFS -" + str(ofsval))
        time.sleep(0.11)
        self.SG_Handler.write("POW:OFFS:STAT ON")
        time.sleep(0.11)
        self.SG_Handler.write("POW " + str(outlev))
        time.sleep(0.11)
        self.SG_Handler.write("outp on")
        time.sleep(0.11)

    def SMU200_SG_Init(self,frequency,ofsval,outlev,bw,source="A"):
        channel = str('1' if (source=='A') else '2')
        if bw == 0:
            pass
        else:
            self.SG_Handler.write("BB:EUTR:PRES")
            self.SG_Handler.write("BB:EUTR:STAT 1")
            self.SG_Handler.write("BB:EUTR:DUPL FDD")
            self.SG_Handler.write("BB:EUTR:LINK DOWN")
            time.sleep(1)
            if ( bw == 5 ):
                self.SG_Handler.write("BB:EUTR:SETT:TMOD:DL 'E-TM1_1__5MHz'")
            elif ( bw == 10 ):
                self.SG_Handler.write("BB:EUTR:SETT:TMOD:DL 'E-TM1_1__10Mhz'")
            elif ( bw == 15 ):
                self.SG_Handler.write("BB:EUTR:SETT:TMOD:DL 'E-TM1_1__15Mhz'")
            elif ( bw == 20 ):
                self.SG_Handler.write("BB:EUTR:SETT:TMOD:DL 'E-TM1_1__20MHz'")
        time.sleep(1)
        self.SG_Handler.write("SOURce%s:FREQ %sMhz"%(channel,frequency))
        time.sleep(1)
#        level = float(power)+float(offset)
        self.SG_Handler.write("SOURce%s:POW:OFFS -%s"%(channel,ofsval))
        time.sleep(0.2)
        self.SG_Handler.write("SOURce%s:POW %s"%(channel,outlev))
        time.sleep(0.2)

    def SMU200_Set_Signal(self,frequency,ofsval,outlev,bandwidth,source="A"):
        channel = str('1' if (source=='A') else '2')
        if frequency == None:
            pass
        else:
            self.SG_Handler.write("SOURce%s:FREQ %sMhz"%(channel,frequency))
            time.sleep(0.11)
        if ofsval == None:
            pass

        else:
            self.SG_Handler.write("SOURce%s:POW:OFFS -%s"%(channel,ofsval))
            time.sleep(0.2)
        if outlev == None:
            pass
        else:
            self.SG_Handler.write("SOURce%s:POW %s"%(channel,outlev))
            time.sleep(0.2)
        if bandwidth == 0:
            pass
        else:
            self.SMU_set_FDD(bandwidth)

    def SMU_set_FDD(self,bandwidth):
        self.SG_Handler.write("BB:EUTR:PRES")
        self.SG_Handler.write("BB:EUTR:STAT 1")
        self.SG_Handler.write("BB:EUTR:DUPL FDD")
        self.SG_Handler.write("BB:EUTR:LINK DOWN")
        time.sleep(1)
        if ( bandwidth == 5 ):
            self.SG_Handler.write("BB:EUTR:SETT:TMOD:DL 'E-TM1_1__5MHz'")
        elif ( bandwidth == 10 ):
            self.SG_Handler.write("BB:EUTR:SETT:TMOD:DL 'E-TM1_1__10Mhz'")
        elif ( bandwidth == 15 ):
            self.SG_Handler.write("BB:EUTR:SETT:TMOD:DL 'E-TM1_1__15Mhz'")
        elif ( bandwidth == 20 ):
            self.SG_Handler.write("BB:EUTR:SETT:TMOD:DL 'E-TM1_1__20MHz'")

    def SMU200_Power_Off(self):
        self.SG_Handler.write("OUTP OFF")

    def SMU200_Power_On(self):
        self.SG_Handler.write("OUTP ON")


    # SA related function
    def SignalAnalyzer_Init(self,pID):
        try:
            self.SA_Handler = self.resourceManager.open_resource("TCPIP0::%s::INSTR"%pID)
            self.SA_Handler.write("*RST")
            return True
        except Exception:
            logging.info('SA initializing failed, please check your connection or address!!\n')
            return False

    def set_sa_anritsu_scpi(self):
        self.SA_Handler.write("SYST:LANG SCPI")

    def set_sa_rs_scpi(self):
        self.SA_Handler.write("SYST:DISP:UPD ON")
        self.SA_Handler.write("CALC:MARK:FUNC:POW:SEL ACP")
        self.SA_Handler.write("CALC:MARK:FUNC:POW:PRES EUTRA")
        self.SA_Handler.write("sens:pow:ach:acp 2")

    def set_sa_ms_native(self):
        self.SA_Handler.write("SYST:LANG NAT")

    def check_id(self):
        return self.SA_Handler.ask("*IDN?")

    def anritsu_sa_set_marker(self,frequency):
        self.SA_Handler.write("SYS SPECT")
        self.SA_Handler.write("SWT")
        self.SA_Handler.write(":CALC:MARK:CENT %s"%frequency)
        self.SA_Handler.write("MKL?")

    def anritsu_initACP(self,freq,bandwidth,ofsval):
        bandwidth = float(bandwidth)
        self.SA_Handler.write("INST SPECT")
        time.sleep(1)
#        self.SA_Handler.write("INST:DEF")
        time.sleep(1)
        self.SA_Handler.write("RAD:STAN 3GLTE_DL")
        time.sleep(2)
        if bandwidth ==1.4:
            self.SA_Handler.write("RAD:STAN:LOAD ADJ,1.4MBW_EUTRA1.4MHZ")
        elif bandwidth == 3:
            self.SA_Handler.write("RAD:STAN:LOAD ADJ,3MBW_EUTRA3MHZ")
        elif bandwidth == 5:
            self.SA_Handler.write("RAD:STAN:LOAD ADJ,5MBW_EUTRA5MHZ")
        elif bandwidth == 10:
            self.SA_Handler.write("RAD:STAN:LOAD ADJ,10MBW_EUTRA10MHZ")
        elif bandwidth == 15:
            self.SA_Handler.write("RAD:STAN:LOAD ADJ,15MBW_EUTRA15MHZ")
        elif bandwidth == 20:
            self.SA_Handler.write("RAD:STAN:LOAD ADJ,20MBW_EUTRA20MHZ")
        else:
            print("Invalid bandwith: %s"%bandwidth)
            return False
        time.sleep(5)
        self.SA_Handler.write("FREQ:CENT %sMHz"%freq)
        self.SA_Handler.write("SWE:TIME 0.5")
        self.SA_Handler.write("DISP:WIND:TRAC:Y:RLEV:OFFS %s"%ofsval)    #To set the reference level offset
        self.SA_Handler.write("DISP:WIND:TRAC:Y:RLEV:OFFS:STAT ON")

    def rs_msinitACP(self,freq,bandwidth,ofsval):
        bandwidth = float(bandwidth)
        #self.SA_Handler.write("INST SPECT")

#        self.SA_Handler.write("INST:DEF")

        #self.SA_Handler.write("RAD:STAN 3GLTE_DL")

        if bandwidth == 5:
            self.SA_Handler.write("sens:pow:ach:spac 5 Mhz")
            self.SA_Handler.write("sens:pow:ach:band 4.515 Mhz")
            self.SA_Handler.write("sens:pow:ach:band:ach 4.515 Mhz")
        elif bandwidth == 10:
            self.SA_Handler.write("sens:pow:ach:spac 10 Mhz")
            self.SA_Handler.write("sens:pow:ach:band 9.015 Mhz")
            self.SA_Handler.write("sens:pow:ach:band:ach 9.015 Mhz")
        elif bandwidth == 15:
            self.SA_Handler.write("sens:pow:ach:spac 15 Mhz")
            self.SA_Handler.write("sens:pow:ach:band 13.515 Mhz")
            self.SA_Handler.write("sens:pow:ach:band:ach 13.515 Mhz")
        elif bandwidth == 20:
            self.SA_Handler.write("sens:pow:ach:spac 20 Mhz")
            self.SA_Handler.write("sens:pow:ach:band 18.015 Mhz")
            self.SA_Handler.write("sens:pow:ach:band:ach 18.015 Mhz")
        else:
            print("Invalid bandwith: %s"%bandwidth)
            return False
        time.sleep(5)
        self.SA_Handler.write("FREQ:CENT %sMHz"%freq)
        self.SA_Handler.write("SWE:TIME 0.2s")
        self.SA_Handler.write("DISP:TRAC:Y:RLEV:OFFS %s"%ofsval)    #To set the reference level offset
        self.SA_Handler.write("DISP:TRAC:Y:RLEV:OFFS:STAT ON")
        self.SA_Handler.write("")

    def anritsu_setSpFreq(self,freq):
        self.SA_Handler.write("FREQ:CENT %sMHz"%freq)

    def anritsu_SetSpOfs(self,ofsval):
        self.SA_Handler.write("DISP:WIND:TRAC:Y:RLEV:OFFS:STAT ON")
        self.SA_Handler.write("DISP:WIND:TRAC:Y:RLEV:OFFS %s"%ofsval)

    def anritsu_SetSpAtt(self,atten):
        self.SA_Handler.write("POW:ATT:AUTO OFF")
        self.SA_Handler.write("POW:ATT %s"%atten)

    def rs_SetSpAtt(self,atten):
        self.SA_Handler.write("INP:ATT %s"%atten)
    def rs_setSpFreq(self,freq):
        self.SA_Handler.write("FREQ:CENT %sMHz"%freq)

    def rs_SetSpOfs(self,ofsval):
        self.SA_Handler.write("DISP:TRAC:Y:RLEV:OFFS %s"%ofsval)

    def anritsu_get_aclr_max(self):
        data = self.SA_Handler.ask("MEAS:ACP?")
        data = data.split(",")
        return max(float(data[1]),float(data[3]),float(data[5]),float(data[7]))
    def rs_ms_get_aclr_max(self):
        data = self.SA_Handler.ask("calc:mark:func:pow:res? ACP")

        data = data.split(",")
        return max(float(data[1]),float(data[2]),float(data[3]),float(data[4]))
    def rs_capture_window(self,name):
        self.SA_handler.write("HCOP: DEV: LANG BMP")
        time.sleep(0.5)
        self.SA_handler.write("HCOP: DEST 'MMEM'")
        time.sleep(0.5)
        self.SA_handler.write("MMEM: NAME 'C:/%s.bmp'"%name)
        time.sleep(0.5)
    def anritsu_get_pow(self):
        data = self.SA_Handler.ask("MEAS:ACP?")
        data = data.split(",")
        return float(data[0])

    def rs_get_pow(self):
        data = self.SA_Handler.ask("calc:mark:func:pow:res? ACP")

        data = data.split(",")
        return float(data[0])


    # power sensor related function
    def Init_NRP(self,pID,sn):
        ''' sn should be string, eg: Init_NRP('103123'), '103123' is from NRP_Z21 power viewer
            Z11 productID: 0x000c, Z21 productID: 0x0003
        '''
        logging.info("PowerSensor id:"+pID+", sn:"+sn)
        try:
            self.NRP01 = self.resourceManager.open_resource("RSNRP::%s::%s::INSTR"%(pID,sn))
            logging.info("NRP-Z21 initializing ok." )
            self.config_NRP()
            return self.NRP01
        except Exception:
            logging.info('NRP-Z21 initializing failed, please check your connection or address!!\n')
            return False
    def config_NRP(self):
        self.NRP01.write("INIT:CONT OFF")
        self.NRP01.write("SENS:FUNC \"POW:AVG\"")

        self.NRP01.write("SENS:AVER:COUN:AUTO OFF")
        self.NRP01.write("SENS:AVER:COUN 16")
        self.NRP01.write("SENS:AVER:STAT ON")
        self.NRP01.write("SENS:AVER:TCON REP")
        self.NRP01.write("SENS:POW:AVG:APER 5e-3")

        self.NRP01.write("SENSe:CORRection:OFFSet:STATe ON")
        self.NRP01.write("FORMAT ASCII")
        self.NRP01.write("INIT:IMM")
        time.sleep(1.21)
    def read_NRP_value(self,freq,offset):
        ''' sn should be string, eg: read_NRP_value(handle,2925,0), handle is from Init_NRP(sn)
        '''
        #print 'freq is:' , freq
#        doubleParav = c_double(0.0)
        # p002=raw_input('p002 doublePara pause: '), doublePara.value
        self.NRP01.write("INIT:CONT OFF")
        self.NRP01.write("SENS:FUNC \"POW:AVG\"")
        self.NRP01.write("SENS:FREQ " + str(int(freq * 1e6)))
        self.NRP01.write("SENS:AVER:COUN:AUTO OFF")
        self.NRP01.write("SENS:AVER:COUN 16")
        self.NRP01.write("SENS:AVER:STAT ON")
        self.NRP01.write("SENS:AVER:TCON REP")
        self.NRP01.write("SENS:POW:AVG:APER 5e-3")
        self.NRP01.write("SENSe:CORRection:OFFSet "+str(offset))
        self.NRP01.write("SENSe:CORRection:OFFSet:STATe ON")
        self.NRP01.write("FORMAT ASCII")
        self.NRP01.write("INIT:IMM")
        time.sleep(1.21)
        temp01 = self.NRP01.ask("FETCH?")
        temp02 = temp01[0:13]
        temp03 = float(temp02)
        doubleParav = 10 * math.log(abs(temp03), math.e) / math.log(10, math.e) + 30.0
        return doubleParav

    #powersupply related function
    def PowerSuppy_Init(self,interface,address):
        ''' sn should be string, eg: Init_NRP('103123'), '103123' is from NRP_Z21 power viewer
            Z11 productID: 0x000c, Z21 productID: 0x0003
        '''
        if interface == "GPIB":
            logging.info("PowerSupply remote mode is:"+ interface+", GPIB Address is:"+address)
            try:
                PS_handler = self.resourceManager.open_resource("GPIB1::%s::INSTR"%(address))
                return PS_handler
            except Exception:
                return False
        elif interface == "TCPIP_VISA":
            logging.info("PowerSupply remote mode is:"+ interface+", IP Address is:"+address)
            try:
                PS_handler = self.resourceManager.open_resource("TCPIP0::%s::INSTR"%(address))
                return PS_handler
            except Exception:
                return False
        elif interface == "TCPIP_VISA_RAWSOCKET":
            logging.info("PowerSupply remote mode is:"+ interface+", IP Address is:"+address)
            try:
                PS_handler = self.resourceManager.open_resource("TCPIP0::%s::8462::SOCKET"%address)
                return PS_handler
            except Exception:
                return False
        elif interface == "TCPIP":
            logging.info("PowerSupply remote mode is:"+ interface+", IP Address is:"+address)
            try:

                PS_handler = _Shell(address,8462,"Power","")
                return PS_handler
            except Exception:
                return False
        else:
            logging.info("Not Supply this remote mode now")
            return False
    def PowerSuppy_ON(self,PSHandler):
        PSHandler.write("OUTPUT:STAT ON")

    def PowerSuppy_ON_DELTA(self,PSHandler):
        PSHandler.write("OUTPUT 1\n")
    def PowerSuppy_OFF_DELTA(self,PSHandler):
        PSHandler.write("OUTPUT 0\n")
    def PowerSuppy_OFF(self,PSHandler):
        PSHandler.write("OUTPUT:STAT OFF")

    def Init_switch_64X(self,interface,address,port):
        if interface =="TCPIP":
            try:
                self.Switch_Handler = _Shell(address,int(port),"64X",b"")
                return self.Switch_Handler
            except Exception:
                logging.info('64X switch initializing failed, please check your connection or address!!\n')
                return False
        elif interface == "VISA":
            try:
                self.Switch_Handler = self.resourceManager.open_resource("TCPIP0::%s::inst0::INSTR"%(address))
                return self.Switch_Handler
            except:
                return False

    def send_cmd_64X(self,Switch_Handler,cmd):
        res = Switch_Handler.write(cmd)

    def Switch_path_to(self,path,item,con,switch_handler):
        logging.info("###################################\nSwitch path to %s\n####################################\n"%path)
        if path <1 or path >64:
            print("input port erroe!")
            return False
        n = path-1
        n = n/8
        n=int(n+1)

        m = path-1
        m=m%8
        m=int(m+1)

        k=n+8
        print("SWIT:CLOS %s,%s"%(n,m))
        switch_handler.write("*RST")
        time.sleep(6)
        switch_handler.write("SWIT:CLOS %s,%s"%(n,m))
        time.sleep(3)
        print("SWIT:CLOS %s,1"%(k))
        switch_handler.write("SWIT:CLOS %s,1"%(k))
        time.sleep(6)
        print("SWIT:CLOS 18,%s"%(n))
        switch_handler.write("SWIT:CLOS 18,%s"%(n))
        time.sleep(6)
        print("SWIT:CLOS 20,1")
        switch_handler.write("SWIT:CLOS 20,1")
        time.sleep(6)
        return True

if __name__=="__main__":
    intr = visaInstrument()
    power_handler = intr.PowerSuppy_Init("GPIB", "7")
    # print(power_handler)
    intr.PowerSuppy_OFF(power_handler)
#
