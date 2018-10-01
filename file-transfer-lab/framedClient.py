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
dirPath = os.path.dirname(os.path.realpath(__file__))
server, usage, debug  = paramMap["server"], paramMap["usage"], paramMap["debug"]
tryConnect = True 
while(tryConnect): 
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
                    fileNameProvided = raw_input('Please input file and or file path to transfer: ')
                    
                    print("File Name: "+ fileNameProvided)
                    realFile = False
                    try: # this will verify it is a file 
                        realFile = os.path.isfile(fileNameProvided)
                    except: 
                        try: 
                            realFile = os.path.isFile(dirPath + "\\" + fileNameProvided)
                            print("realFIle: ")
                        except: 
                            print("Error finding file. Please try again")
                    if(realFile): 
                        #then we need to check size and see if it is empty. 
                        if(os.stat(fileNameProvided).st_size == 0): 
                            print("You can only transfer files that contain something. Please try again.")
                        else: # we should transfer. 
                            
                            #FIRST CHECK THAT IT ISN"T ALREADY IN OUR SERVER 
                            
                            #ELSE TELL SERVER WHAT WE DOING.  
                            SendDet = "-StrFl "+ fileNameProvided.strip()
                            framedSend(s, SendDet.encode('utf-8') , debug)
                            print("received:", framedReceive(s, debug))
                            
                            
                            # we only want 100 bytes so lets loop through
                            f = open(fileNameProvided, "rb")
                            cnt = 0
                        
                            try:
                                lines = [line.rstrip('\n') for line in f] 
                                
                                for line in lines: 
                                   #loop through all lines if they are small enough send else split in two and tack detail to end. 
                                   if(sys.getsizeof(line) <= 100): 
                                       #send
                   
                                       framedSend(s, line.encode('utf-8'), debug)
                                       print("received:", framedReceive(s, debug)) 
                                   else: 
                                        totSizeLine = sys.getsizeof(line)
                                        notDone = True
                                        min = 0 
                                        max = 100
                                        while(notDone): 
                                            tosSizeLineRem = totSizeLine - (100*cnt)
                                            if(totSizeLineRem > 100): 
                                                lineSending = line[min:max] + "PL"
                                                framedSend(s, lineSending.encode('utf-8') , debug)
                                                print("received:", framedReceive(s, debug))
                                            else: 
                                                lineSending = line[min:totSizeLineRem] + "PL"
                                                framedSend(s, lineSending.encode('utf-8') , debug)
                                                print("received:", framedReceive(s, debug))
                                                notDone = False 
                                            min = max 
                                            max = max + 100 
                                                

                            except:
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
        
   
framedSend(s, b"hello world", debug)
print("received:", framedReceive(s, debug))

print("sending hello world")
framedSend(s, b"hello world", debug)
print("received:", framedReceive(s, debug))

