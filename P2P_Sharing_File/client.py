import os
import pickle
import threading
import socket
from threading import *
from peerShare import *
from tkinter import filedialog as fd
import os, sys
import json as js

class peerServer:
    def __init__(self):
        print("Welcome to peer to peer file sharing system")
        self.file_path = ""
        self.file_name = ""
        self.peer_port = 0
        self.GetID()
    def start_server(self):
        if(self.flag == False):
            self.GetID()
        while True:
            choice = input("Menu \n(1) Register\n(2) Search\n(3) List all files\n(4) Download\n(5) Exit server\n")
            choice = int(choice)
            if choice == 1:
                self.peer_port = int(self.peer_id)
                self.register()
                start_sharing(self.peer_port, 'localhost')
            elif choice == 2:
                self.search()

            elif choice == 3:
                self.list_all()

            elif choice == 4:
                print(self.peer_id)
                peer_id = int(input('Enter peer id of file owner: '))
                file_name = input("Enter file name: ")
                start_sharing(peer_id, 'localhost')
                self.download(int(peer_id), file_name)

            elif choice == 5:
                break

            else:
                continue
    def register(self):
        client = socket.socket()
        client.connect(('localhost', 2182))
        self.file_path = fd.askopenfilename()
        self.file_name = os.path.basename(self.file_path)
        register_data = [1, self.peer_port, self.file_name]
        data_send = pickle.dumps(register_data)
        client.send(data_send)
        with open(self.file_path, 'rb') as myfile:
            data = myfile.read(2048)
            while data:
                client.send(data)
                data = myfile.read(2048)
            myfile.close()
        client.close()

    def search(self):
        client = socket.socket()
        client.connect(('localhost', 2182))
        file_name = input("Enter file name: ")
        register_data = [2, file_name]
        data = pickle.dumps(register_data)
        client.send(data)
        state = pickle.loads(client.recv(1024))
        self.print_list(state[0], state[1])
        client.close()

    def list_all(self):
        client = socket.socket()
        client.connect(('localhost', 2182))
        data = pickle.dumps([3])
        client.send(data)
        state = pickle.loads(client.recv(1024))
        self.print_list(state[0], state[1])
        client.close()

    def print_list(self, files, keys):
        myformat = "{:<10}{:<25}{}"
        if len(files) == 0:
            print("There is no file available")
        else:
            print(myformat.format('Peer ID', 'File Name', 'Date added'))
            for item in files:
                print(myformat.format(item[keys[0]], item[keys[1]], item[keys[2]]))
    def GetID(self):
        self.flag = False
        self.username = input("Enter username: ")
        with open("account.json", "r") as jf:
            data = js.load(jf)
            for elem in data:
                for key in elem:
                    if(self.username == key):
                        self.flag = True
                        self.peer_id = elem[key]
                        return
            print('This username is not registered, please enter another')

    def download(self, peerID, file_name):
        client = socket.socket()
        client.connect(('localhost', peerID))
        list_data = [4, str(file_name)]
        data = pickle.dumps(list_data)
        client.send(data)

        # file_path = os.path.join(, '..')
        file_path = os.path.join(os.getcwd(), self.username)
        # file_path = os.path.join(file_path, self.username)

        with open(os.path.join(file_path, file_name), 'wb') as myfile:
            # while True:
                data = client.recv(4096)
                while data:
                    myfile.write(data)
                    data = client.recv(4096)
                myfile.close()
        client.close()
        print('File is downloaded successfully.')
peer = peerServer()
peer.start_server()
