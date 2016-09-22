#!/usr/bin/env python
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import re
# you may use urllib to encode data appropriately
import urllib

def help():
    print "httpclient.py [GET/POST] [URL]\n"

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        # use sockets!
        outgoing = socket.socket()
        try:
            outgoing.connect((host,port))
        except socket.error, ex:
            # If no address associated with hostname
            if ex.errno == -5:
                outgoing = None
            else:
                raise
        return outgoing

    def get_code(self, data):
        reg_ex_format = "(HTTP/1.[0,1]) ([1-5][0-9][0-9]) (.*)\n"
        match = re.search(reg_ex_format, data)
        code = 0
        if len(match.groups()) != 3:
            code = 400        
        return match.group(2)

    def get_headers(self,data):
        return None

    def get_body(self, data):
        return None

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            part = sock.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return str(buffer)

    def get_host_and_port(self, url):
        reg_ex_format = "(.*?)(?::|$)(\d{1,5})?"
        match = re.search(reg_ex_format, url)
        host, port = match.group(1), match.group(2)
        if port != None:
            port = int(port)
        if port == None and host != None:
            port = 80
        return host, port

    def GET(self, url, args=None):
        host, port = self.get_host_and_port(url)
        print "host: ", host
        print "port: ", port
        connection_socket = self.connect(host, port)
        data = self.recvall(connection_socket)
        print "data: ", data
        code = self.get_code(data)
        body = ""
        return HTTPResponse(code, body)

    def POST(self, url, args=None):
        code = 500
        body = ""
        return HTTPResponse(code, body)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print client.command( sys.argv[2], sys.argv[1] )
    else:
        print client.command( sys.argv[1] )   
