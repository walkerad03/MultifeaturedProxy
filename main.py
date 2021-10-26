#!/usr/bin/python

# Built-ins
from threading import Thread
import socket
import sys

#Owned
import config as cfg
__author__ = 'Walker Davis'
__version__ = '0.0.2'


class ClientToProxy(Thread):
    def __init__(self, host, port):
        super(ClientToProxy, self).__init__()
        self.client = None
        self.host = host
        self.port = port
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.connect((host, port))

    def run(self):
        while True:
            data = self.server.recv(4096)
            if data:
                print('[client] {}'.format(data))
                self.client.sendall(data)

class ProxyToServer(Thread):
    def __init__(self, host, port):
        super(ProxyToServer, self).__init__()
        self.server = None
        self.host = host
        self.port = port
        
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((host, port))
        sock.listen(1)

        self.client, addr = sock.accept()
    
    def run(self):
        while True:
            data = self.client.recv(4096)
            if data:
                print('[server] {}'.format(data))
                self.server.sendall(data)

class Proxy(Thread):
    def __init__(self, client_host, server_host, port):
        super(Proxy, self).__init__()
        self.client_host = client_host
        self.server_host = server_host
        self.port = port
        self.running = False
    
    def run(self):
        while True:
            print("[Proxy({})] starting...".format(self.port))
            self.c2p = ClientToProxy(self.client_host, self.port)
            self.p2s = ProxyToServer(self.server_host, self.port)
            print("[Proxy({})] connection established.".format(self.port))
            self.c2p.client = self.p2s.client
            self.p2s.server = self.c2p.server
            self.running = True

            self.c2p.start()
            self.p2s.start()

def main():
    if len(sys.argv) == 4:
        proxy_server = Proxy(sys.argv[1], sys.argv[2], int(sys.argv[3]))
        proxy_server.start()
    else:
        print('Incorrect number of arguments provided.')
        print('Using default values from config.py')
        print('\tServer IP: {}'.format(cfg.default['server_ip']))
        print('\tClient IP: {}'.format(cfg.default['client_ip']))
        print('\tPort:      {}'.format(cfg.default['port']))
        proxy_server = Proxy(cfg.default['server_ip'], cfg.default['client_ip'], cfg.default['port'])
        proxy_server.start()
    
if __name__ == '__main__':
    main()