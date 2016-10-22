#!/usr/bin/env python
# encoding: utf-8

import re
from socket import socket, AF_INET, SOCK_STREAM
import time
from threading import Thread

class Douyu:

    def __init__(self):
        self.sock = socket(AF_INET, SOCK_STREAM)
        HOST = '218.205.114.210'
        PORT = 12602
        self.sock.connect((HOST,PORT))


    #包的结构
    def convert(self,msg):
        length = bytearray([len(msg) + 9, 0x00, 0x00, 0x00])
        code = length
        magic = bytearray([0xb1,0x02,0x00,0x00])
        end = bytearray([0x00])
        msg = bytes(msg.encode('utf-8'))
        return bytes(length+code+magic+msg+end)

    def keepalive(self):
        while 1:
            msg = 'type@=mrkl/'
            msg = self.convert(msg)
            self.sock.send(msg)
            time.sleep(10)

    def login(self):
        HOST = '218.205.114.210'
        PORT = 12602
        msg_login = 'type@=loginreq/username@=password@=/roomid@=6324/'
        msg_login = self.convert(msg_login)
        self.sock.send(msg_login)
        response = self.sock.recv(4000)
        if response:   #需要正则判断
            print('>>>>>>>>>>>>>>>connect successful<<<<<<<<<<<<\n')
            print('============getting danmu=============')
            msg_joingroup = 'type@=joingroup/rid=@6324/gid@=16/'
            msg_joingroup = self.convert(msg_joingroup)
            self.sock.send(msg_joingroup)
        else:
            print('>>>>>>>>>>>>>>>conncet error<<<<<<<<<<<<<<<')
            exit(1)

    def getdanmu(self):
        msg_danmu = 'type@=ocmreq/ts_range@=90/'
        msg_danmu = self.convert(msg_danmu)
        while 1:
            self.sock.send(msg_danmu)  #与抓包的情况不同(抓包时只需发送一次）
            response = self.sock.recv(4000)
            danmu = re.findall(b'txt@AA=(.*?)@',response)
            name = re.findall(b'nn@AA=(.*?)@',response)
            time.sleep(1)
            try:
                danmu = danmu[0].decode()
                name = name[0].decode()
                print(name+':   '+danmu)
            except:
                print('解析弹幕出错')
                print(response)

if __name__ == '__main__':
    douyu = Douyu()
    douyu.login()
    Thread(target=douyu.keepalive).start()
    Thread(target=douyu.getdanmu()).start()
