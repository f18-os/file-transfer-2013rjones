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
    sock, addr = lsock.accept()
    try: 
        if not os.fork():
            print("new child process handling connection from", addr)    
        
            print("connection rec'd from", addr)


            from framedSock import framedSend, framedReceive
            
            while True:
                payload = framedReceive(sock, debug)
                print("read: " + payload)
                cmds = payload.split()
                if(notStarted): 
                    for cmd in cmds: #All logic inside a loop should flow from bottom up. IE bottom if implements first then upper if. This forces the if statements to be executed in certain order. Since i want to get vals after seeing certain vals. 
                        if(openFile): 
                            if cmd.strip() in fileDict: 
                                print("Overwrote file included due to request.") 
                            fileGiven = open(strPath +"/"+cmd,'wb+') #open file in server area to write to. 
                            notStarted = False #reset vars for next time and turn off notStarted to force next logic
                            fileDict[cmd] = True 
                            openFile = False 
                            
                        if(cmd == "-StrFl"):
                            #then we have a file to open. 
                            openFile = True 
                
                else: 
                    for cmd in cmds: #this bit of logic is used to catch if we need to stop writing and close the file. Could extend this to execute other commands during running. 
                        if(cmdEntered): 
                            if(cmd == "CloseFileWritingChunks"):
                                fileGiven.close()
                                cmdEntered = False #Reset all for next time. 
                                notStarted = True
                                openFile = False
                        if(cmd == "-cmd"): 
                            #then next will be to close 
                            cmdEntered = True
                        else:
                            break #no sense in looping through all words if first isn't what we are looking for. 
                    
                    #then we need to write a line since our file is open and we didn't close the file. 
                    if(notStarted == False): 
                        
                        addRest = False
                        append = False 
                        
                        for cmd in cmds: 
                            if(cmd.strip() == "NEWLINE"): #errors with new line passing so I just put special newlines to denote when newlines happen. This could be erased when sending files back. 
                                curAppend= curAppend +'\n'
                                display = True
                                break
                            if(cmd.strip() == "DONELINE"): #needed endlines to ensure we had the ends of lines 
                                display = True
                                break
                            if(addRest): 
                                if((cmd != "PL" and cmd != "DONELINE")): #PL denotes that the line is larger than 100 bytes and we need to append lines together before putting in file. 
                                    curAppend = curAppend + cmd 
                            if(cmd.strip() == "PL"):
                                append = True
                                addRest = True
                            
                        if(append): 
                            if(display): #This will actually write our line when we know we have the end. 
                                fileGiven.write(totAppend + curAppend + '\n')
                                append = False 
                                totAppend = ""
                                display = False
                                addRest = False
                            else:     
                                totAppend = totAppend + curAppend
                            

                        else: #This writes our line if it is under 100 bytes. 
                            fileGiven.write(payload + '\n') 
                            
                if debug: print("rec'd: ", payload)
                
                if not payload:
                    break
                payload += b"!"             # make emphatic!
                framedSend(sock, payload, debug)
    except Exception as e: 
        print(e)
        print("Disconnected Client")
