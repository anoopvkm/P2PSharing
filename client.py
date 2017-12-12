from __future__ import division
import os
import socket
import sys
import json as simplejson
import uuid
import math
import argparse

# Method to send a request to given port, host, file name etc
def send_request(host, port, request):

    # creating socket connection
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    print 'Sending Request: '
    print request
    print '========================================================================='
   # s.send(request)
    custom_send(s, request)

    # receiving response
    response = custom_recv(s)
    print 'Response......'
    response = ''.join(response)
    print response
    print '=========================================================================='
    s.close()
    return response

def custom_recv(s):
    response = []
    while 1:
        chunk = s.recv(1024)
        if chunk == "":
            break;
        response.append(chunk)

    return response

def custom_send(s, msg):
    totalsent = 0
    while totalsent < len(msg):
        sent = s.send(msg[totalsent:])
        if sent == 0:
            raise RuntimeError("Socket connection broken")
        totalsent = totalsent + sent

# extracts response code from response
def response_code(response):
    split = response.split('\n')
    split = split[0].split()
    return int(split[1])

# writes response to a file and print HEADERS
def write_to_file_and_print(response, method, filename):
    if method == 'HEAD':
        # writing header
        file = open('Download/'+filename+'_HEAD.txt', 'a')
        file.write(response)
        print response
        file.close()
        return


    # extracting content length
    split = response.split('\n')
    for i in range(1,len(split)):
        line = split[i]
        header_parsed = line.split(':')
        if header_parsed[0] == 'Content-Length':
            length = int(header_parsed[1])
            content = response[-length:]
            print response[:len(response)-length] # printing header
            break;
    # reading content
    file = open('Download/'+filename, 'w')
    file.write(content)
    file.close()
    return

# creating a new request
def create_request(filename, command):
    request = command+' '+filename+' HTTP/1.0\n\n'
    return request

def register_file(filename):
    fid = str(uuid.uuid4())
    if os.path.exists(filename):
        size = os.path.getsize(filename)
        print 'file size', size
        chunks = size/1000000.0
        chunks = math.ceil(chunks)
        chunks = int(chunks)
        with open('.meta/'+fid, "w+") as f:
            map = {}
            map['fid'] = fid
            map['filename'] = filename
            map['size'] = size
            map['chunks'] = range(chunks)
            map['server'] = "borg11.cs.purdue.edu"
            simplejson.dump(map,f) 
            f.close()
    
        request = "REG "+fid+" "+socket.gethostname()
        # TODO send to server
        send_request(map['server'], 8989, request)
    else:
        print 'File :' , filename, ' does not exist'

    return fid

def parse_server_response(response):
    lines = response.splitlines(True)
    print lines
    split = lines[0].split()
    code = int(split[0])
    if code != 200:
        return [code]
    l = simplejson.loads(lines[1])

    return[code, l]

def get_chunks(response):
    lines = response.splitlines(True)
    print lines
    split = lines[0].split()
    code = int(split[0])
    if code != 200:
        return [code]
    l = simplejson.loads(lines[1])

    return[code, l]

def create_dummy_file(file, size):
    with open(file, 'wb') as f:
        f.write(os.urandom(size))
        f.close()
 
def download_file(mfile, dloc):
    if os.path.exists(mfile):
        meta = simplejson.load(open(mfile))
        fname = meta['filename']
        print meta['chunks']
        request = "GET "+meta['fid']
        response = send_request(meta['server'], 8989, request)
        response = parse_server_response(response)
        if response[0] != 200:
            print "Unable to obtain file information from server, Quiting...."
            return
        clients = response[1]

        request = "GETLIST "+meta['fid']
        for client in clients:
            response = send_request(client, 8686, request)
            response = get_chunks(response)
            if response[0] != 200:
                print "Unable to get list from client ", client
            else:
                chunks = response[1]

                create_dummy_file(dloc, meta['size'])

    else:
        print 'Meta file ', mfile, " doesn't exist"
    

# main method parses command line arguments

def main():
  #  fid = register_file('foo')
    fid = '042c91eb-e47a-42cc-87bb-31c04ab5a9a6'
    download_file(fid, "./foo2")
main()

