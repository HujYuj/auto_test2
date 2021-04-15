class DUT_keyup():

    def run_live_command(self,command):
        p = subprocess.Popen(command,
            stdout = subprocess.PIPE,
            stderr = subprocess.STDOUT)
        return iter(p.stdout.readline, b'')

    def run_L1_server(self):
        server_status = 'NOT started'
        command = [os.path.normcase(r'C:\L1_LIB_Hangzhou-master\venv\Scripts\python.exe'), os.path.normcase(r'C:\L1_LIB_Hangzhou-master\dut_control\dutControlServiceL1.py')]
        # command = shlex.split(command)
        for line in self.run_live_command(command):
            print(line.decode())
            if b'Running on http:' in line:
                print("server started")
                server_status = 'started'
                break
        print('Server is ' + server_status)



    def run_key_up(self):
        key_up_status = False
        command = [os.path.normcase(r'C:\T-GATE-5G-L1-DUT-CONTROL\venv\Scripts\python.exe'), os.path.normcase(r'C:\T-GATE-5G-L1-DUT-CONTROL\dut_control\nokia_5G_hwiv_configuration\run_python.py')]
        # command = shlex.split(command)
        for line in self.run_live_command(command):
            print(line.decode())
            if b'Test case < LibraryParametersExample_TM1_1_A1-5_100MHz_AEQV > passed' in line:
                print("key up finished")
                key_up_status = True
                break
        print('key up status is ', key_up_status)

    def library_setup_dut(self):
        LibraryCaller.activate_carriers()