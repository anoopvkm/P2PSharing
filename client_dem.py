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
    lines = data.split('\r\n')

    split = lines[0].split()
    if split[0] == 'GETLIST':
        if os.path.exists('.meta/'+split[1]):
           meta = json.load(open('.meta/'+split[1]))
           fname = meta['filename']
           if os.path.exists(fname):
                response = "200 OK\n" + json.dumps( meta['chunks'] )
           else:
               print 'File not at position'
               #TODO send it to server
               response = "404 Not found"

        else:
            response = "404 Not found"
def handle_socket(clientsocket):
    data = clientsocket.recv(8192)
    print data
    # custom_send(clientsocket,response)
    clientsocket.close()

def listen():
    serversocket = create_server_socket(socket.gethostname(), 8686, 5)
    print 'Starting client on ', socket.gethostname()
    while 1:
        (clientsocket, address) = serversocket.accept()
        print 'Connection request from ',address
        try:
            thread.start_new_thread(handle_socket,(clientsocket,))
        except:
            print 'Error in handling threads'


listen()

