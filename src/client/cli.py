import socket
import sys
import os

def connect_to_server(host, port):
    """ Establishes the control connection to the server. """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((host, port))
    return sock

def send_command(sock, command):
    """ Sends a command to the server through the control socket. """
    sock.sendall(command.encode())
    response = sock.recv(1024).decode()
    print("Server response:", response)
    return response

def handle_get(sock, filename):
    """ Handles downloading a file from the server. """
    response = send_command(sock, f'GET {filename}')
    if 'SUCCESS' in response:
        handle_data_transfer(sock, filename, mode='get')

def handle_put(sock, filename):
    """ Handles uploading a file to the server. """
    if not os.path.isfile(filename):
        print("File does not exist.")
        return
    response = send_command(sock, f'PUT {filename}')
    if 'SUCCESS' in response:
        handle_data_transfer(sock, filename, mode='put')

def handle_ls(sock):
    """ Lists files on the server. """
    response = send_command(sock, 'LS')
    if 'SUCCESS' in response:
        handle_data_transfer(sock, None, mode='ls')

def handle_quit(sock):
    """ Closes the connection to the server. """
    send_command(sock, 'QUIT')
    sock.close()
    sys.exit()

def handle_data_transfer(sock, filename, mode):
    """Handles data transfer setup based on the command."""
    port_info = sock.recv(1024).decode()
    _, port = port_info.split()
    port = int(port)

    data_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        data_sock.connect((sock.getpeername()[0], port))
    except socket.error as e:
        print(f"Connection failed: {e}")
        return

    if mode == 'get':
        receive_file(data_sock, filename)
    elif mode == 'put':
        send_file(data_sock, filename)
    elif mode == 'ls':
        receive_listing(data_sock)

    data_sock.close()
def send_file(data_sock, filename):
    """ Sends a file to the server. """
    with open(filename, 'rb') as f:
        content = f.read()
        data_sock.sendall(content)
    print(f"File sent: {filename}")


def receive_file(data_sock, filename):
    header = b''
    while True:
        chunk = data_sock.recv(1)
        if chunk == b'\n':  # Stop reading the header on a newline
            break
        header += chunk
    _, size = header.decode().split()
    size = int(size)

    with open(filename, 'wb') as f:
        received = 0
        while received < size:
            data = data_sock.recv(min(1024, size - received))
            if not data:
                break
            f.write(data)
            received += len(data)
    print(f"File received: {filename}, {received} bytes.")
def receive_listing(data_sock):
    """ Receives directory listing from the server. """
    listing = data_sock.recv(1024).decode()
    print("Directory listing:\n", listing)

def main():
    if len(sys.argv) != 3:
        print("Usage: python cli.py <server machine> <server port>")
        return

    host = sys.argv[1]
    port = int(sys.argv[2])

    sock = connect_to_server(host, port)
    print("ftp>", end=' ')

    while True:
        command = input()
        if command.startswith('get'):
            _, filename = command.split()
            handle_get(sock, filename)
        elif command.startswith('put'):
            _, filename = command.split()
            handle_put(sock, filename)
        elif command == 'ls':
            handle_ls(sock)
        elif command == 'quit':
            handle_quit(sock)
        else:
            print("Unknown command.")
        print("ftp>", end=' ')

if __name__ == "__main__":
    main()