#! /usr/bin/env python3

import sys

sys.path.append("../lib")       # for params

import re, socket, params,os

from framedSock import framedSend, framedReceive


switchesVarDefaults = (
    (('-s', '--server'), 'server', "127.0.0.1:50001"),
    (('-d', '--debug'), "debug", False), # boolean (set if present)
    (('-?', '--usage'), "usage", False), # boolean (set if present)
    )


progname = "framedClient"
paramMap = params.parseParams(switchesVarDefaults)

server, usage, debug  = paramMap["server"], paramMap["usage"], paramMap["debug"]

serverParse = str(input("Please input server socket you wish to connect to:"))

if(serverParse.strip() != ""): 
    server = "127.0.0.1:" + str(serverParse).strip()

if usage:
    params.usage()


try:
    serverHost, serverPort = re.split(":", server)
    serverPort = int(serverPort)
except:
    print("Can't parse server:port from '%s'" % server)
    sys.exit(1)

s = None
for res in socket.getaddrinfo(serverHost, serverPort, socket.AF_UNSPEC, socket.SOCK_STREAM):
    af, socktype, proto, canonname, sa = res
    
    try:
        print("creating sock: af=%d, type=%d, proto=%d" % (af, socktype, proto))
        s = socket.socket(af, socktype, proto)
    except socket.error as msg:
        print(" error: %s" % msg)
        s = None
        continue
    try:
        print(" attempting to connect to %s" % repr(sa))
        s.connect(sa)
    except socket.error as msg:
        print(" error: %s" % msg)
        s.close()
        s = None
        continue
    break

if s is None:
    print('could not open socket')
    sys.exit(1)

cont = True 
while(cont):
    print(" ")
    print("Please enter:")
    print("             0 to send a file to a server")
    print("             1 to display files on server")
    print("             2 to exit")
    try:
        cmd = input("Please input number corresponding to command.")
        if(str(cmd).strip() != ""):
            try: 
                if(cmd == 0): 
                    print("Sending a file to a server.")
                    print("Please input file to transfer")
                if(cmd == "1"): 
                    print("Displaying all files on a server. ")
                if(cmd == 2): 
                    cont = False
                if((cmd != 0) and (cmd != 1) and (cmd != 2)): 
                    print("Please enter 0, 1, or 2 ")
            except:
                print("Invalid input, please enter a number as a command.")

    except: 
        print("No number input, please try again. ")    
        
   
framedSend(s, b"hello world", debug)
print("received:", framedReceive(s, debug))

print("sending hello world")
framedSend(s, b"hello world", debug)
print("received:", framedReceive(s, debug))

