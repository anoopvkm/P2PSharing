import socket
import re
import time
import sys
import os
import thread
import json
def create_server_socket(host, port, max_connections):
    serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serversocket.bind((host, port))
    serversocket.listen(max_connections)
    return serversocket

def handle_request(data):
    print data

    split = data.split()
    response = "500 Server Error"
    if split[0] == 'REG':
        fname = ".smeta/"+split[1]
       
        if os.path.exists(fname):
            flist = json.load(open(fname))
        else:
            flist = []

    
        flist.append(split[2])
        flist = set(flist)
        flist = list(flist)

        with open(fname, "w+") as f:
            json.dump(flist,f)
            f.close()

    elif split[0] == 'GET':
        fname = ".smeta/"+split[1]
        if os.path.exists(fname):
            flist = json.load(open(fname))
            response = "200 OK" + "\n" + json.dumps(flist)

        else:
            response = "404 Not found"
    return response
    
def custom_send(s, msg):
    totalsent = 0
    while totalsent < len(msg):
        sent = s.send(msg[totalsent:])
        if sent == 0:
            raise RuntimeError("Socket connection broken")
        totalsent = totalsent + sent


def handle_socket(clientsocket):
    data = clientsocket.recv(8192)
    response = handle_request(data);

    custom_send(clientsocket,response)
    clientsocket.close()

def listen():
    serversocket = create_server_socket(socket.gethostname(), 8989, 5)
    print 'Starting server on ', socket.gethostname()
    while 1:
        (clientsocket, address) = serversocket.accept()
        print 'Connection request from ',address
        try:
            thread.start_new_thread(handle_socket,(clientsocket,))
        except:
            print 'Error in handling threads'


listen()

