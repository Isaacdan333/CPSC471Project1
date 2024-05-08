import socket
import sys

def recv_all(sock, num_bytes):
    """ Helper function to receive the specified number of bytes from the socket. """
    recv_buff = b''
    while len(recv_buff) < num_bytes:
        packet = sock.recv(num_bytes - len(recv_buff))
        if not packet:
            return None
        recv_buff += packet
    return recv_buff

def main():
    if len(sys.argv) < 3:
        print(f"USAGE: python {sys.argv[0]} <SERVER ADDRESS> <SERVER PORT>")
        sys.exit(1)
    
    server_addr = sys.argv[1]
    server_port = int(sys.argv[2])

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as conn_sock:
        conn_sock.connect((server_addr, server_port))

        while True:
            user_input = input("ftp> ").strip()
            if not user_input:
                continue
            
            conn_sock.send(user_input.encode())

            if user_input.startswith("get"):
                file_name = user_input.split()[1]
                file_size = int(recv_all(conn_sock, 10).decode())
                if file_size == 0:
                    print("Server response: File does not exist!")
                else:
                    file_data = recv_all(conn_sock, file_size).decode()
                    print(f"Server response: Received '{file_name}' ({file_size} bytes).")
                    print(f"File content:\n{file_data}\n")
            elif user_input.startswith("put"):
                file_name = user_input.split()[1]
                try:
                    with open(file_name, 'rb') as f:
                        data = f.read()
                        size = f"{len(data):010d}"
                        conn_sock.send(size.encode() + data)
                    print("Server response: File sent successfully!")
                except FileNotFoundError:
                    print("Local error: File does not exist.")
            elif user_input.startswith("ls"):
                file_size = int(recv_all(conn_sock, 10).decode())
                directory_listing = recv_all(conn_sock, file_size).decode()
                print(f"Server response: List of documents:\n{directory_listing}")
            elif user_input == "quit":
                print("Server response: Session ended.")
                break
            else:
                print("Invalid command, try again.")

if __name__ == "__main__":
    main()