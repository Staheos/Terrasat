import socket
import threading

HOST = 'localhost'
PORT = 1769

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen()

print(f"Server is listening on {HOST}:{PORT}")

while True:
    client_socket, client_address = server_socket.accept()
    # client_thread = threading.Thread(target=client_handler, args=(client_socket,))
    # client_thread.start()

    while True:
        print(client_socket.recv(1024).decode("utf-8", errors="strict"))
        # client_socket.close()