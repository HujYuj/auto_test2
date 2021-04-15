# -*- coding: utf-8 -*-
"""
    :author: Wang, Fuqiang Q. (NSB - CN/Hangzhou) <fuqiang.q.wang@nokia-sbell.com>
"""
from logging import Handler
from auto_test.lib_service.log_handler.socketio_client import SyncSocketIOClient

class SocketIOHandler(Handler):

    def __init__(self,  server_url: str, event: str):
        Handler.__init__(self)
        self.socketio_client = SyncSocketIOClient(server_url, event)
        print("SocketIOHandler init called!")

    def emit(self, record):
        msg = self.format(record)
        self.socketio_client.send(msg)
        # print(msg)
        # with open("SocketIOHandler.txt", "a+") as f:
        #     f.write(msg)
        #     f.write("\n")

    def close(self):
        print("SocketIOHandler close called!")
        Handler.close(self)
        self.socketio_client.close()

