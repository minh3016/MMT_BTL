import socket
import threading
import pickle as pk
from datetime import datetime
from threading import *
import os
import json as js


class mainServer(threading.Thread):
    def __init__(self, max_connection):
        threading.Thread.__init__(self)
        self.host = 'localhost'
        self.semaphore = Semaphore(max_connection)
        self.port = 2182
        self.serv = socket.socket()
        print("Central server is live")
        self.serv.bind((self.host, self.port))
        self.serv.listen(max_connection)
        self.files = []
        self.keys = ['peer_id', 'file_name', 'date_added']
        print("Get connected at", self.host, "on port number", self.port)

    def run(self):
        while True:
            client, addr = self.serv.accept()
            print("Connected to", addr[0], "Port at", addr[1])

            request = pk.loads(client.recv(1024))
            file_path = os.path.join(os.getcwd(), 'SharingFiles')
            if request[0] == 1:
                print("Peer", addr[1], "Add new file")
                file_path = os.path.join(file_path, str(request[2]))
                with open(file_path, 'wb') as f:
                    data = client.recv(2048)
                    while data:
                        f.write(data)
                        data = client.recv(2048)
                    f.close()
                self.semaphore.acquire()
                self.register(request[1], request[2], str(datetime.now()))
                ret = "File Registered Successfully."
                client.send(bytes(ret, 'utf-8'))
                self.semaphore.release()
                client.close()
            elif request[0] == 2:
                print("Peer", addr[1], "Searching for a file")
                self.semaphore.acquire()
                ret_data = pk.dumps(self.search_data(request[1]))
                client.send(ret_data)
                self.semaphore.release()
                client.close()
            elif request[0] == 3:
                print("Peer", addr[1], "Listing all files")
                self.semaphore.acquire()
                ret_data = pk.dumps(self.all_data())
                client.send(ret_data)
                self.semaphore.release()
                client.close()
            else:
                continue

    def register(self, peer_id, file_name, date):
        entry = [str(peer_id), file_name, str(date)]
        self.files.insert(0, dict(zip(self.keys, entry)))
        infor = dict(zip(self.keys, entry))
        with open('SharingFiles/Sharing.json', 'r+') as jf:
            data = js.load(jf)
            if not any(item['peer_id'] == infor['peer_id'] and item['file_name'] == infor['file_name'] for item in data):
                data.append(infor)
            else:
                for item in data:
                    if(item['peer_id'] == infor['peer_id'] and item['file_name'] == infor['file_name'] and item['date_added'] != infor['date_added']):
                        data.remove(item)
                        data.append(infor)
            jf.seek(0)
            js.dump(data, jf, indent = 4) 
    def search_data(self, file_name):
        ret = []
        for item in self.files:
            if item['file_name'] == file_name:
                entry = [item['peer_id'], item['file_name'], item['date_added']]
                ret.insert(0, dict(zip(self.keys, entry)))
        return ret, self.keys

    def all_data(self):
        with open('SharingFiles/Sharing.json', 'r+') as jf:
            data = js.load(jf)
        return data, self.keys


# Main
print("Welcome. Server is about to go live")
server = mainServer(2)
server.start()
