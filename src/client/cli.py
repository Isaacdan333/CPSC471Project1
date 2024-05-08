import socket
import sys
import os

class FTPClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = self.connect_to_server()

    def connect_to_server(self):
        """ Establishes the control connection to the server. """
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect((self.host, self.port))
        return sock

    def send_command(self, command):
        """ Sends a command to the server through the control socket. """
        self.sock.sendall(command.encode())
        response = self.sock.recv(1024).decode()
        print("Server response:", response)
        return response

    def handle_get(self, filename):
        """ Handles downloading a file from the server. """
        response = self.send_command(f'GET {filename}')
        if 'SUCCESS' in response:
            self.handle_data_transfer(filename, mode='get')

    def handle_put(self, filename):
        """ Handles uploading a file to the server. """
        file_path = self.ensure_directory(filename)
        if not os.path.isfile(file_path):
            print("File does not exist.")
            return
        response = self.send_command(f'PUT {filename}')
        if 'SUCCESS' in response:
            self.handle_data_transfer(filename, mode='put')

    def handle_ls(self):
        """ Lists files on the server. """
        response = self.send_command('LS')
        if 'SUCCESS' in response:
            self.handle_data_transfer(None, mode='ls')

    def handle_quit(self):
        """ Closes the connection to the server. """
        self.send_command('QUIT')
        self.sock.close()
        sys.exit()

    def handle_data_transfer(self, filename, mode):
        """Handles data transfer setup based on the command."""
        port_info = self.sock.recv(1024).decode()
        _, port = port_info.split()
        port = int(port)

        data_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            data_sock.connect((self.sock.getpeername()[0], port))
        except socket.error as e:
            print(f"Connection failed: {e}")
            return

        if mode == 'get':
            self.receive_file(data_sock, filename)
        elif mode == 'put':
            self.send_file(data_sock, filename)
        elif mode == 'ls':
            self.receive_listing(data_sock)

        data_sock.close()

    def send_file(self, data_sock, filename):
        file_path = self.ensure_directory(filename)
        with open(file_path, 'rb') as f:
            content = f.read()
            header = f"SIZE {len(content)}\n".encode()
            data_sock.sendall(header)  # Send the size header
            data_sock.sendall(content)  # Then send the file content
        print(f"File sent: {filename}")

    def receive_file(self, data_sock, filename):
        header = b''
        while True:
            chunk = data_sock.recv(1)
            if chunk == b'\n':
                break
            header += chunk
        _, size = header.decode().split()
        size = int(size)

        file_path = self.ensure_directory(filename)
        with open(file_path, 'wb') as f:
            received = 0
            while received < size:
                data = data_sock.recv(min(1024, size - received))
                if not data:
                    break
                f.write(data)
                received += len(data)
        print(f"File received: {filename}, {received} bytes.")

    def receive_listing(self, data_sock):
        """ Receives directory listing from the server. """
        listing = data_sock.recv(1024).decode()
        print("Directory listing:\n", listing)

    def ensure_directory(self, filename):
        """ Ensure the client file directory exists and provide the full file path. """
        directory = './src/client/files'
        if not os.path.exists(directory):
            os.makedirs(directory)
        return os.path.join(directory, filename)

def main():
    if len(sys.argv) != 3:
        print("Usage: python cli.py <server machine> <server port>")
        return

    host = sys.argv[1]
    port = int(sys.argv[2])
    client = FTPClient(host, port)

    print("ftp>", end=' ')
    while True:
        command = input().strip()
        if not command:
            print("No command entered. Please try again.")
            print("ftp>", end=' ')
            continue

        command_parts = command.split()
        cmd = command_parts[0]

        if cmd == 'get' or cmd == 'put':
            if len(command_parts) < 2:
                print(f"Usage: {cmd} <filename>")
            else:
                filename = command_parts[1]
                if cmd == 'get':
                    client.handle_get(filename)
                elif cmd == 'put':
                    client.handle_put(filename)
        elif cmd == 'ls':
            client.handle_ls()
        elif cmd == 'quit':
            client.handle_quit()
        else:
            print("Unknown command.")

        print("ftp>", end=' ')

if __name__ == "__main__":
    main()






