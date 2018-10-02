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

tosSizeLineRem = 0
progname = "framedClient"
paramMap = params.parseParams(switchesVarDefaults)
dirPath = os.path.dirname(os.path.realpath(__file__))
server, usage, debug  = paramMap["server"], paramMap["usage"], paramMap["debug"]

tryConnect = True 
while(tryConnect): 
    
    serverParse1 = raw_input("Please input server ip address you wish to connect to: ")

        
    serverParse = str(input("Please input server socket you wish to connect to: "))

    if(serverParse.strip() != ""): 
        server = serverParse1.strip() + ":" + str(serverParse).strip()

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
            tryConnect = False
        except socket.error as msg:
            print(" error: %s" % msg)
            s.close()
            s = None
            continue
        break

    if s is None:
        print('could not open socket')
        print("")
            
totSizeLineRem = 0
cont = True 
while(cont):
    #try: 
    #    framedSend(s, "CheckAlive".encode('utf-8') , debug)
    #except: 
        #then it is dead thus reprompt to connect.
    #    setUpSocket()
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
                    fileNameProvided = raw_input('Please input file and or file path to transfer: ')
                    
                    print("File Name: "+ fileNameProvided)
                    realFile = False
                    try: # this will verify it is a file 
                        realFile = os.path.isfile(fileNameProvided)
                    except: 
                        try: 
                            realFile = os.path.isFile(dirPath + "\\" + fileNameProvided)
                            #print("realFile: ")
                        except: 
                            print("Error finding file. Please try again")
                    if(realFile): 
                        proceedToSend = True 
                        #then we need to check size and see if it is empty. 
                        if(os.stat(fileNameProvided).st_size == 0): 
                            print("You can only transfer files that contain something. Please try again.")
                        else: # we should transfer. 
                            
                            #FIRST CHECK THAT IT ISN"T ALREADY IN OUR SERVER 
                            
                            #ELSE TELL SERVER WHAT WE DOING.  
                            SendDet = "-StrFl "+ fileNameProvided.strip()
                            framedSend(s, SendDet.encode('utf-8') , debug)
                            print("received:", framedReceive(s, debug))
                            
                            
                            
                            if(proceedToSend): 
                                
                                # we only want 100 bytes so lets loop through
                                #f = open(fileNameProvided, "rb")
                                cnt = 0
                            
                                try:
                                    with open(fileNameProvided) as f:
                                        for line in f:#loop through all lines if they are small enough send else split in two and tack detail to end. 
                                            if(sys.getsizeof(line) <= 100): 
                                            #send
                                                print("Sending line. " + line)
                                                framedSend(s, line.strip().encode('utf-8'), debug)
                                                print("received:", framedReceive(s, debug)) 
                                            else:
                                                totSizeLine = sys.getsizeof(line)
                                                print("Total line size: "+ str(totSizeLine))
                                                notDone = True
                                                cnt = 0
                                                while(notDone):
                                                    totSizeLineRem = totSizeLine - (98*cnt)
                                                    if(totSizeLineRem > 98): 
                                                        cnt = cnt + 1 
                                                        valLoop = totSizeLineRem / 98 
                                                        looping = True
                                                        totLoop = 0 
                                                        while(looping): 
                                                            if(valLoop <= totLoop):
                                                                looping = False
                                                                
                                                                framedSend(s, "NEWLINE".encode('utf-8') , debug)
                                                                print("received:", framedReceive(s, debug))
                                                                
                                                                framedSend(s, "DONELINE".encode('utf-8') , debug)
                                                                print("received:", framedReceive(s, debug))
                                                                notDone = False 
                                                            else:    
                                                                lineSending = "PL "+ line[(0+(98*totLoop)):(98 + (98*totLoop))]
                                                                print("LineSending: "+ lineSending)
                                                                framedSend(s, lineSending.encode('utf-8') , debug)
                                                                print("received:", framedReceive(s, debug))
                                                                totLoop = totLoop + 1 


                                except Exception as e:
                                    print(e)
                                    print("Error during byte writing.")
                            
                                f.close()
                                #tell server we are done writing 
                                SendDet = "-cmd CloseFileWritingChunks"
                                framedSend(s, SendDet.encode('utf-8') , debug)
                                print("received:", framedReceive(s, debug))
                    else: 
                        print("Invalid file, please try again.")
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
 
SendDet = "-cmd Exiting"
framedSend(s, SendDet.encode('utf-8') , debug) 
print("Exited")        

