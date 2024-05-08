import socket
import os
import threading
import sys


class SocketServer:
    """
    A server that uses separate control and data connections for FTP-like file operations with a defined protocol.
    """

    def __init__(self, server_port):
        self.control_port = server_port
        self.control_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.control_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.control_socket.bind(('0.0.0.0', self.control_port))
        self.control_socket.listen(5)
        print(f"Server started on control port {self.control_port}")

    def accept_connections(self):
        try:
            while True:
                client_socket, address = self.control_socket.accept()
                print(f"Control connection established with {address}")
                threading.Thread(target=self.handle_client, args=(client_socket, address)).start()
        except KeyboardInterrupt:
            print("Server is closing")
            self.control_socket.close()

    def handle_client(self, control_socket, address):
        try:
            while True:
                data = control_socket.recv(1024).decode()
                if not data:
                    break
                print(f"Received command: {data}")
                command, *args = data.split()

                if command == 'GET' and args:
                    self.handle_get(control_socket, address, args[0])
                elif command == 'PUT' and args:
                    self.handle_put(control_socket, address, args[0])
                elif command == 'LS':
                    self.handle_ls(control_socket, address)
                elif command == 'QUIT':
                    control_socket.sendall(b"SUCCESS: Quitting session.")
                    break
                else:
                    control_socket.sendall(b"ERROR: Invalid command")
        finally:
            control_socket.close()
            print("Control connection closed.")

    def handle_get(self, control_socket, address, filename):
        if os.path.isfile('./src/server/files/'+filename):
            control_socket.sendall(b"SUCCESS: Starting file transfer.")
            self.setup_data_connection(control_socket, address, filename, 'send')
        else:
            control_socket.sendall(b"ERROR: File not found")

    def handle_put(self, control_socket, address, filename):
        control_socket.sendall(b"SUCCESS: Ready to receive file.")
        self.setup_data_connection(control_socket, address, filename, 'receive')

    def handle_ls(self, control_socket, address):
        control_socket.sendall(b"SUCCESS: Listing files.")
        files = '\n'.join(os.listdir('./src/server/files'))
        self.setup_data_connection(control_socket, address, None, 'ls', files)

    def setup_data_connection(self, control_socket, client_address, filename, mode, directory_listing=None):
        """Sets up a data connection to handle file transfer or directory listing."""
        if filename is not None:
            filepath = "./src/server/files/" + filename
        else:
            filepath = None
        data_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        ephemeral_port = self.generate_ephemeral_port()
        data_socket.bind(('0.0.0.0', ephemeral_port))
        data_socket.listen(1)

        # Inform client about the data port
        control_socket.sendall(f"CONNECT {ephemeral_port}".encode())

        # Accept the data connection from the client
        client_data_socket, _ = data_socket.accept()
        if mode == 'send':
            self.send_file(client_data_socket, filepath)
        elif mode == 'receive':
            self.receive_file(client_data_socket, filepath)
        elif mode == 'ls':
            self.send_data(client_data_socket, directory_listing.encode())

        client_data_socket.close()
        data_socket.close()

    def send_file(self, data_socket, filename):
        with open(filename, 'rb') as file:
            content = file.read()
            header = f"SIZE {len(content)}\n".encode()  # Ensure there is a newline character
            data_socket.sendall(header)
            data_socket.sendall(content)
        print(f"File sent: {filename}")

    def receive_file(self, data_socket, filename):
        try:
            header = b''
            # Read byte by byte until we get a newline, which indicates the end of the header
            while True:
                part = data_socket.recv(1)
                if part == b'\n':
                    break
                header += part
            _, size = header.decode().split()
            size = int(size)
        except ValueError:
            print("Error parsing size header")
            return

        with open(filename, 'wb') as file:
            received = 0
            while received < size:
                chunk = data_socket.recv(min(1024, size - received))
                if not chunk:
                    break
                file.write(chunk)
                received += len(chunk)
        print(f"File received: {filename}")

    def send_data(self, data_socket, data):
        data_socket.sendall(f"SIZE {len(data)}".encode() + b'\n' + data)

    def generate_ephemeral_port(self):
        """Generate an ephemeral port for data connection."""
        return 49152  # Typically, the range is 49152 to 65535 for ephemeral ports


def start_server(port):
    server = SocketServer(port)
    server.accept_connections()


def main():
    if len(sys.argv) < 2:
        raise RuntimeError("Missing args. USAGE: python server.py <PORT>")

    if not sys.argv[1].isdigit():
        raise RuntimeError(sys.argv[1], "is not a valid port number.")

    server_port = int(sys.argv[1])
    start_server(server_port)


if __name__ == "__main__":
    main()