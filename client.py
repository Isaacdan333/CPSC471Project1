import socket
import sys

def connect_to_server(server_addr, server_port):
    """Establish a connection to the FTP server."""
    try:
        conn_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn_sock.connect((server_addr, server_port))
        return conn_sock
    except Exception as e:
        print(f"Failed to connect to the server: {e}")
        sys.exit(1)

def send_command(conn_sock, command):
    """Send a command to the FTP server and print the response."""
    try:
        conn_sock.sendall((command.strip() + "\n").encode('utf-8'))
        response = conn_sock.recv(4096).decode('utf-8')
        print(f"Server response: {response}")
    except Exception as e:
        print(f"Error sending command to server or receiving response: {e}")
        sys.exit(1)

def send_file(conn_sock, file_name):
    """Send a file to the server using PUT command."""
    try:
        with open(file_name, 'rb') as file:
            while True:
                file_data = file.read(65536)
                if not file_data:
                    break
                data_size_str = f"{len(file_data):010d}"
                conn_sock.sendall(data_size_str.encode('utf-8') + file_data)
        print("File sent successfully.")
    except FileNotFoundError:
        print(f"File not found: {file_name}")
    except Exception as e:
        print(f"Error sending file: {e}")

def receive_file(conn_sock, file_name):
    """Receive a file from the server using GET command."""
    try:
        # Receive the data size string from the server
        data_size_str = b''
        while len(data_size_str) < 10:
            chunk = conn_sock.recv(10 - len(data_size_str))
            if not chunk:
                break
            data_size_str += chunk

        if len(data_size_str) == 10:
            data_size = int(data_size_str.decode('utf-8').strip())
            file_data = b''
            while len(file_data) < data_size:
                chunk = conn_sock.recv(min(65536, data_size - len(file_data)))
                if not chunk:
                    break
                file_data += chunk

            if len(file_data) == data_size:
                with open(file_name, 'wb') as file:
                    file.write(file_data)
                print(f"Received file '{file_name}' successfully.")
            else:
                print("Incomplete file data received.")
        else:
            print("Failed to receive data size from the server.")
    except Exception as e:
        print(f"Error receiving file: {e}")


def main():
    if len(sys.argv) < 3:
        print("USAGE: python client.py <SERVER ADDRESS> <SERVER PORT>")
        sys.exit(1)

    server_addr = sys.argv[1]
    server_port = int(sys.argv[2])
    conn_sock = connect_to_server(server_addr, server_port)

    try:
        while True:
            command = input("ftp> ")
            if command.lower().startswith("put"):
                _, file_name = command.split(maxsplit=1)
                send_file(conn_sock, file_name)
            elif command.lower().startswith("get"):
                _, file_name = command.split(maxsplit=1)
                receive_file(conn_sock, file_name)
            elif command.lower() == "quit":
                send_command(conn_sock, "QUIT")
                break
            else:
                send_command(conn_sock, command)
    finally:
        conn_sock.close()

if __name__ == "__main__":
    main()
