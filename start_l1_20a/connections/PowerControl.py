import select
import socket


class PowerControl():
    def power_on(self):

        #create an INET, STRENMING socket
        #IPv4, TCP protocol
        try:
            s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        except socket.error:
            print("failed to create socket")

        print("socket created")

        remote_ip = '192.168.2.112'
        port = 8462

        #conenct to remote server
        s.connect((remote_ip,port))
        print("socket connected to " + remote_ip)

        #message = "*IDN?"

        try:
            s.send(b"*IDN?")
            s.send(b"\r\n")
            print("HAH", s.recv(1024))
            s.send(b"SYST:REM:CV?")
            s.send(b"\r\n")
            print("HAH",s.recv(1024))
        except socket.error:
            print('send failed')

        print("send successfully")


        try:
            s.send(b"SOUR:VOL:MAX 50")
            s.send(b"\t\n")
            # print("HAH", s.recv(1024))
        except:
            print("set volatge and current falied")


        s.send(b"MEAS:VOL?")
        s.send(b"\t\n")
        #print("HAH", s.recv(1024))

        ready = select.select([s], [], [], 10)
        if ready[0]:
            reply = s.recv(1024)
            print(reply)

        try:
            s.send(b"OUTP 1")
            s.send(b"\t\n")
        except:
            print("power on failed")

        # #reply = s.recv(1024)
        # #print(reply)

        # try:
        #     s.send(b"MEASure:VOLtage?")
        #     s.send(b"\t\n")
        # except:
        #     print("measure failed")

        # reply = s.recv(1024)
        # print(reply)

        s.close()

    def power_off(self):
        pass

if __name__ == "__main__":
    handler = PowerControl()
    handler.power_on()