import socket
import os
import sys
import threading
import time
from datetime import datetime, timezone, timedelta

def handle_client(conn_sock, client_address):
    try:
        while True:
            command = conn_sock.recv(1024).decode('utf-8').strip()
            if not command:
                break  # If no command, exit the loop

            print(f"Received command: '{command}' from {client_address}")

            if command.lower() == "ls":
                list_directory(conn_sock)
            elif command.lower().startswith("put "):
                _, file_name = command.split(maxsplit=1)
                receive_file(conn_sock, file_name.strip())
            elif command.lower().startswith("get "):
                _, file_name = command.split(maxsplit=1)
                send_file(conn_sock, file_name.strip())
            elif command.lower() == "quit":
                print(f"Client {client_address} has quit the session.")
                break  # End the session if 'quit' command is received
            else:
                print("Unsupported command received.")
    except Exception as e:
        print(f"Error handling client {client_address}: {e}")
    finally:
        conn_sock.close()

def list_directory(conn_sock):
    try:
        directory_contents = os.listdir('.')
        directory_response = "\n".join(directory_contents) + "\n"
        conn_sock.sendall(directory_response.encode('utf-8'))
    except Exception as e:
        print("Failed to list directory:", e)
        conn_sock.sendall("Failed to list directory.\n".encode('utf-8'))

def receive_file(conn_sock, file_name):
    try:
        data_size = int(conn_sock.recv(10).decode().strip())
        file_data = b''
        while len(file_data) < data_size:
            file_data += conn_sock.recv(data_size - len(file_data))
        with open(file_name, 'wb') as file:
            file.write(file_data)
        print(f"Received file '{file_name}' from client.")
    except Exception as e:
        print(f"Error receiving file: {e}")

def send_file(conn_sock, file_name):
    try:
        with open(file_name, 'rb') as file:
            file_data = file.read()
            data_size_str = f"{len(file_data):010d}"
            conn_sock.sendall(data_size_str.encode('utf-8') + file_data)
            print(f"Sent file '{file_name}' to client.")
    except FileNotFoundError:
        print(f"File not found: {file_name}")
        conn_sock.sendall(b'0000000000')
    except Exception as e:
        print(f"Error sending file: {e}")

def server_status():
    while True:
        print(f"{datetime.now().isoformat()} - Server is running...")
        time.sleep(60)

def start_server(port):
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind(('', port))
    server_sock.listen(5)
    print(f"Server listening on port {port}")
    
    threading.Thread(target=server_status, daemon=True).start()

    try:
        while True:
            conn_sock, client_address = server_sock.accept()
            print(f"Accepted connection from {client_address}")
            threading.Thread(target=handle_client, args=(conn_sock, client_address)).start()
    except KeyboardInterrupt:
        print('Server shutdown requested.')
    finally:
        server_sock.close()
        print("Server has been shut down.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("USAGE: python server.py <PORT>")
        sys.exit(1)

    server_port = int(sys.argv[1])
    start_server(server_port)
