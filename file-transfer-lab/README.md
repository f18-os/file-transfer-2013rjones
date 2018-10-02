This folder consists of several programs. One of which is a framedClient.py and a framedServer.py. These when ran and attached to the same socket can transfer files from the client to the server. 

To run the program type: 

    python framedServer.py
    
In another terminal/buffer type 

    python framedClient.py

Then by typing in the corresponding sockets and ip addresses these two can be linked together to transfer files. 

The server program works by taking in input from a socket. It also echos back information to the client that tries to store files in the server. This allows easy communication between the two. The server program also does it's own processing of files on it's side. 

The client program works by taking in user input to determine which files the user wants to transfer to a server. This also helps to do all initial validation of the files, and keeps track of what it is connected to server wise. This program works to fix any issues and errors with the communication between the server and the cient. 
