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
from urlparse import urlparse

def help():
    print "httpclient.py [GET/POST] [URL]\n"

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body

class HTTPRequest(object):
    def __init__(self, method, path, protocol, hostname, body = ""):
        self.method = method
        self.path = path
        self.protocol = protocol
        self.hostname = hostname
        self.body = body

    def build(self):
        if self.hostname == None:
            self.hostname = ""
        else:
            self.hostname = "\nHost: " + self.hostname
        return self.method+" "+self.path+" "+self.protocol+self.hostname+"\r\n\r\n" + self.body

class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        # use sockets!
        outgoing = socket.socket()
        try:
            outgoing.connect((host,port))
            outgoing.setblocking(0)
        except socket.error, ex:
            if ex.errno == -5 or ex.errno == 111:
                outgoing = None
            else:
                raise
        return outgoing

    def get_code(self, data):
        reg_ex_format = "(HTTP/1.[0,1]) ([1-5][0-9][0-9]) (.*)\n"
        match = re.search(reg_ex_format, data)
        code = 0
        if match == None or len(match.groups()) != 3:
            code = 404
        else:
            code = int(match.group(2))
        return code

    def get_headers(self,data):
        return None

    def get_body(self, data):
        return data.split("\r\n\r\n", 1)[1]

    # read everything from the socket
    def recvall(self, sock):
        buffer = bytearray()
        done = False
        while not done:
            try:
                part = sock.recv(1024)
            except socket.error, ex:
                if ex.errno == 11:
                    continue
            if (part):
                buffer.extend(part)
            else:
                done = not part
        return str(buffer)

    def sendall(self, socket, request):
        socket.sendall(request.build())

    def prepend_http(self, url):
        if not url.startswith("http://"):
            url = "http://" + url
        return url

    def parse_url(self, url):
        url =  self.prepend_http(url)
        parsed_url = urlparse(url)
        host = parsed_url.hostname
        port = parsed_url.port
        path = parsed_url.path
        if(host == None):
            host = port = path = None
        if port != None:
            port = int(port)
            if port >= 65535:
                host, port = None, None
        if port == None and host != None:
            port = 80
        if path == None or path == "":
            path = "/"
        return host, port, path

    def GET(self, url, args=None):
        host, port, path = self.parse_url(url)
        # Check host and port for None
        connection_socket = self.connect(host, port)
        if connection_socket == None:
            return HTTPResponse(404)
        self.sendall(connection_socket, HTTPRequest("GET", path, " HTTP/1.1", host))
        data = self.recvall(connection_socket)
        if (data == None):
            return HTTPResponse(404)
        code = self.get_code(data)
        body = self.get_body(data)
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
