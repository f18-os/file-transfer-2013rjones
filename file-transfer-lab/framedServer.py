#! /usr/bin/env python3
import sys
sys.path.append("../lib")       # for params
import re, socket, params


switchesVarDefaults = (
    (('-l', '--listenPort') ,'listenPort', 50001),
    (('-d', '--debug'), "debug", False), # boolean (set if present)
    (('-?', '--usage'), "usage", False), # boolean (set if present)
    )

progname = "echoserver"
paramMap = params.parseParams(switchesVarDefaults)

debug, listenPort = paramMap['debug'], paramMap['listenPort']

if paramMap['usage']:
    params.usage()
dontProceed = True 
while(dontProceed): 
    listenPort = input("Please input the port you want the server to listen on: ")
    try: 
        lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # listener socket
        bindAddr = ('127.0.0.1', listenPort)
        lsock.bind(bindAddr)
        lsock.listen(5)
        dontProceed = False 
    except: 
        dontProceed = True 
        
print("listening on:", bindAddr)

while True:
    try: 
            
        sock, addr = lsock.accept()
        print("connection rec'd from", addr)


        from framedSock import framedSend, framedReceive
        notStarted = True 
        openFile = False 
        fileGiven = ""
        cmdEntered = False
        
        while True:
            payload = framedReceive(sock, debug)
            print("read: " + payload)
            cmds = payload.split()
            if(notStarted): 
                for cmd in cmds: 
                    if(openFile): 
                        fileGiven = open(cmd+"ServerVers", 'w') #open file in server Area appending ServerVers
                        notStarted = False 
                    if(cmd == "-StrFl"):
                        #then we have a file to open. 
                        openFile = True 
            
            else: 
                for cmd in cmds:
                    if(cmdEntered): 
                        if(cmd == "CloseFileWritingChunks"):
                            fileGiven.close()
                            cmdEntered = False 
                            notStarted = True
                    if(cmd == "-cmd"): 
                        #then next will be to close 
                        cmdEntered = True
                    else:
                        break 
                
                #then we write a line if we get here. 
                if(notStarted == False): 
                    fileGiven.write(payload + '\n') #modify this to take the parts of a same line.  
            if debug: print("rec'd: ", payload)
            
            if not payload:
                break
            payload += b"!"             # make emphatic!
            framedSend(sock, payload, debug)
    except:
        print("Disconnected Client")
