import socket
import os
import threading
from datetime import datetime

def recv_all(sock, num_bytes):
    """ Helper function to receive the specified number of bytes from the socket. """
    recv_buff = b''
    while len(recv_buff) < num_bytes:
        packet = sock.recv(num_bytes - len(recv_buff))
        if not packet:
            return None
        recv_buff += packet
    return recv_buff

def handle_client(client_sock, addr):
    try:
        while True:
            command = client_sock.recv(1024).decode().strip()
            if not command:
                continue
            
            print(f"[{datetime.now()}] - Command received from {addr}: {command}")

            if command.startswith('get'):
                file_name = command[4:]
                if os.path.isfile(file_name):
                    with open(file_name, 'rb') as file:
                        file_data = file.read()
                        file_size = len(file_data)
                        size_header = f"{file_size:010d}".encode() + file_data
                        client_sock.sendall(size_header)
                        print(f"[{datetime.now()}] - Sent '{file_name}' ({file_size} bytes) to {addr}. Success!")
                else:
                    client_sock.sendall(b'0000000000')
                    print(f"[{datetime.now()}] - File not found: '{file_name}'. Failure!")

            elif command.startswith('put'):
                file_size = int(client_sock.recv(10).decode())
                file_data = recv_all(client_sock, file_size)
                file_name = command[4:]
                with open(file_name, 'wb') as file:
                    file.write(file_data)
                print(f"[{datetime.now()}] - Received and saved '{file_name}' ({file_size} bytes) from {addr}. Success!")

            elif command.startswith('ls'):
                directory_listing = "\n".join(os.listdir('.'))
                size_str = f"{len(directory_listing):010d}".encode() + directory_listing.encode()
                client_sock.sendall(size_str)
                print(f"[{datetime.now()}] - Sent directory listing to {addr}. Success!")

            elif command == 'quit':
                print(f"[{datetime.now()}] - {addr} requested to end the session. Quitting.")
                break

    except Exception as e:
        print(f"[{datetime.now()}] - Error handling client {addr}: {str(e)}")
    finally:
        client_sock.close()
        print(f"[{datetime.now()}] - Connection with {addr} closed.")

def server_status():
    while True:
        print(f"[{datetime.now()}] - Server is running...")
        threading.Event().wait(60)

def start_server(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
        server_sock.bind(('', port))
        server_sock.listen()
        print(f"[{datetime.now()}] - Server listening on port {port}")

        while True:
            client_sock, addr = server_sock.accept()
            print(f"[{datetime.now()}] - Accepted connection from {addr}")
            threading.Thread(target=handle_client, args=(client_sock, addr)).start()

if __name__ == "__main__":
    import sys
    if len(sys.argv) != 2:
        print(f"USAGE: python {sys.argv[0]} <PORT>")
        sys.exit(1)
    port = int(sys.argv[1])
    threading.Thread(target=server_status, daemon=True).start()
    start_server(port)