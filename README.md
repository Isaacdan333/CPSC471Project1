# CPSC471Project1

The goal of this project is to utilize sockets programming API to Implement a basic FTP 
system that allows users to 
```
Upload files: send files from the client to the server using 'put' command
Download Files: Retrieve files from the server to the client using 'get' command
List Directory Contents: View files and directories on the server with 'ls' command
Session Managing: Connect and disconnect from the server properly.
```


## Names and emails
- Isaac Koczwara - isaackoz@csu.fullerton.edu
- Isaac Perez - isaacdan@csu.fullerton.edu
- Ulysses Carbajal - Ulysses@csu.fullerton.edu

## Programming language
Python

## Program Requirements
Python 3.XX installed on both server and client machines/terminals.

## Server Setup
The `server.py` script is designed to listen for incoming FTP commands on a 
specified port number. It can handle multiple client connections and supports
basic file operations such as `ls` to list files stored in the current directory,
`get` to download files from the server  `put` to upload files to the server
You can run the file with `python serv.py <PORTNUMBER>` or `python3 serv.py <PORTNUMBER>` For example `python serv.py 1234`

## Client Setup

The `client.py` connects the client to the server by specifying the server's domain name or IP address and the port number.
It supports commands to upload and download files, list files, and quit the server. To list files, simply type `ls` 
in the terminal would work. Downloading files can be done in the format `ftp> get <file name> (downloads file <file name> from the server) `
Uploading files can be done  in the format `ftp> put <filename> (uploads file <file name> to the server) `. To quit
simply typing `quit` will disconnect you from the server.
You can run the file with `python cli.py <server machine> <server port>` or with `python3 cli.py <server machine> <server port>`
For example python3 client.py localhost 1234

## Example
In client
```
python3 client.py localhost 1234
ftp> ls
Server response: List of documents:
client.py
server.py
small.txt
test.txt
test2.txt
ftp> get test.txt
Server response: Received 'test.txt' (4 bytes).
File content:
test

ftp> get test2.txt
Server response: Received 'test2.txt' (450 bytes).
File content:
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nam ex ante, pellentesque et dapibus ac, egestas sed lacus. Curabitur tincidunt, tellus convallis facilisis commodo, diam urna gravida quam, sed vulputate erat lacus ac lorem. Nullam convallis ligula quis tellus lobortis iaculis. Proin auctor erat vel consequat placerat. Morbi lacus sapien, imperdiet quis justo eu, iaculis lobortis dui. In nec felis eleifend, dapibus odio a, ultricies eros.

ftp> put test.txt
Server response: File sent successfully!
ftp> quit
Server response: Session ended.
```
In Server
```
python3 server.py 1234
[2024-05-07 22:18:10.580574] - Server is running...
[2024-05-07 22:18:10.581221] - Server listening on port 1234
[2024-05-07 22:18:26.781745] - Accepted connection from ('127.0.0.1', 59400)
[2024-05-07 22:18:29.025256] - Command received from ('127.0.0.1', 59400): ls
[2024-05-07 22:18:29.030384] - Sent directory listing to ('127.0.0.1', 59400). Success!
[2024-05-07 22:18:41.407070] - Command received from ('127.0.0.1', 59400): get test.txt
[2024-05-07 22:18:41.418556] - Sent 'test.txt' (4 bytes) to ('127.0.0.1', 59400). Success!
[2024-05-07 22:18:46.339589] - Command received from ('127.0.0.1', 59400): get test2.txt
[2024-05-07 22:18:46.351987] - Sent 'test2.txt' (450 bytes) to ('127.0.0.1', 59400). Success!
[2024-05-07 22:18:50.774649] - Command received from ('127.0.0.1', 59400): put test.txt
[2024-05-07 22:18:50.833196] - Received and saved 'test.txt' (4 bytes) from ('127.0.0.1', 59400). Success!
[2024-05-07 22:18:52.618749] - Command received from ('127.0.0.1', 59400): quit
[2024-05-07 22:18:52.618822] - ('127.0.0.1', 59400) requested to end the session. Quitting.
[2024-05-07 22:18:52.619211] - Connection with ('127.0.0.1', 59400) closed.
```