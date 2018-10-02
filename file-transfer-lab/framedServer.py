#! /usr/bin/env python3
import sys
sys.path.append("../lib")       # for params
import re, socket, params,os


#start by creating a file for writing all transfered files. This will just reset for every different server. Essentially you lose them
#once you start a new server. 

curDir =os.path.dirname(os.path.abspath(__file__))
strPath = curDir + r'/serverStorage'
strNum = 0
notUnique = True
while(notUnique):
    if not os.path.exists(strPath):
        os.makedirs(strPath) 
        notUnique = False 
    else: 
        strPath = strPath + str(strNum)
        strNum = strNum + 1 
#should have storage folder now. 

switchesVarDefaults = (
    (('-l', '--listenPort') ,'listenPort', 50001),
    (('-d', '--debug'), "debug", False), # boolean (set if present)
    (('-?', '--usage'), "usage", False), # boolean (set if present)
    )

progname = "echoserver"
paramMap = params.parseParams(switchesVarDefaults)
fileDict = {}

debug, listenPort = paramMap['debug'], paramMap['listenPort']

if paramMap['usage']:
    params.usage()
dontProceed = True 
while(dontProceed): 
    try:
        listenPort = input("Please input the port you want the server to listen on: ")
        lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # listener socket
        bindAddr = ('127.0.0.1', listenPort)
        lsock.bind(bindAddr)
        lsock.listen(5)
        dontProceed = False 
    except: 
        dontProceed = True 
        print("Invalid.")
        
print("listening on:", bindAddr)
print("Writing all transfered files to:" + strPath)
while True:
    sock, addr = lsock.accept()
    try: 
        if not os.fork():
            print("new child process handling connection from", addr)    
        
            print("connection rec'd from", addr)


            from framedSock import framedSend, framedReceive
            notStarted = True 
            openFile = False 
            fileGiven = ""
            cmdEntered = False
            append = False 
            totAppend = ""
            display = False
            curAppend = ""
            addRest = False
            while True:
                payload = framedReceive(sock, debug)
                print("read: " + payload)
                cmds = payload.split()
                if(notStarted): 
                    for cmd in cmds: 
                        if(openFile): 
                            if cmd.strip() in fileDict: 
                                openFile = True
                                print("Overwrote file included due to request.")
                            else:    
                                fileGiven = open(strPath +"/"+cmd,'wb+') #open file in server area to write to. 
                                notStarted = False
                                fileDict[cmd] = True 
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
                                openFile = False
                        if(cmd == "-cmd"): 
                            #then next will be to close 
                            cmdEntered = True
                        else:
                            break 
                    
                    #then we write a line if we get here. 
                    if(notStarted == False): 
                        addRest = False
                        append = False 
                        
                        cnt = 0 
                        for cmd in cmds: 
                            if(cmd.strip() == "NEWLINE"):
                                curAppend= curAppend +'\n'
                                display = True
                                break
                            if(cmd.strip() == "DONELINE"): 
                                display = True
                                break
                            if(addRest): 
                                if((cmd != "PL" and cmd != "DONELINE")):
                                    curAppend = curAppend + cmd 
                            if((cmd.strip() == "PL") and (cnt == 0)):
                                append = True
                                addRest = True
                            
                        if(append): 
                            if(display): 
                                fileGiven.write(totAppend + curAppend + '\n')
                                append = False 
                                totAppend = ""
                                display = False
                                addRest = False
                                cnt = 0 
                            else:     
                                totAppend = totAppend + curAppend
                            

                        else: 
                            fileGiven.write(payload + '\n') 
                            
                if debug: print("rec'd: ", payload)
                
                if not payload:
                    break
                payload += b"!"             # make emphatic!
                framedSend(sock, payload, debug)
    except Exception as e: 
        print(e)
        print("Disconnected Client")
