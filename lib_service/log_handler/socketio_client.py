# -*- coding: utf-8 -*-
"""
    :author: Wang, Fuqiang Q. (NSB - CN/Hangzhou) <fuqiang.q.wang@nokia-sbell.com>
"""

import socketio
import time

class SyncSocketIOClient:
    """T-Gate 5G L1 DUT control."""

    def __init__(self,  server_url: str, event: str):
        self.server_url = server_url
        self.event = event
        self.sio = socketio.Client(reconnection=False)

    def send(self, message: str):
        if self.sio.connected == False:
            self.sio.connect(self.server_url, transports=['websocket'])
        self.sio.emit(self.event, message)
        # self.sio.emit("runner message", message)


    def close(self):
        time.sleep(0.1)
        if self.sio.connected:
            self.sio.disconnect()

if __name__ == "__main__":
    message = "flask-sockeio client testing!!!!!!!!!"
    # server_url = "http://localhost:8031"
    server_url = "http://localhost:8032"
    event = "runner_message_event"
    # event = "ping_message_event"
    # namespace = "/ping"

    # cmd = "dir"
    client = SyncSocketIOClient(server_url, event)
    client.send(message)
    client.close()

    # import re
    # mac_re_str = "<re.Match object; span=(92964, 92991), match=', dst mac 02:40:43:80:12:31'>"
    # # re.search()
    # mac_re_str = re.search(", dst mac ([0-9a-fA-F-:]+)", mac_re_str)
    # address = re.search('..[:]..[:]..[:]..[:]([0-9a-fA-F]{2})[:]..', mac_re_str.group()).group(1)
    # print(f"address: {address}")
