import socket
import threading
import datetime
import platform

# Server configuration
HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)

def handle_client(conn, addr):
    """Handles individual client connections."""
    print(f"Connected by {addr}")
    conn.sendall(b"Welcome to the command server! Type 'HELP' for commands.\n")

    while True:
        try:
            data = conn.recv(1024)  # Receive up to 1024 bytes
            if not data:
                break  # Client disconnected

            command = data.decode('utf-8').strip().upper()
            response = ""

            if command == "TIME":
                response = f"Current time: {datetime.datetime.now().strftime('%H:%M:%S')}"
            elif command == "DATE":
                response = f"Current date: {datetime.date.today().strftime('%Y-%m-%d')}"
            elif command == "OS":
                response = f"Server OS: {platform.system()} {platform.release()}"
            elif command == "HELP":
                response = "Available commands: TIME, DATE, OS, HELP, QUIT"
            elif command == "QUIT":
                response = "Goodbye!"
                conn.sendall(response.encode('utf-8') + b'\n')
                break
            else:
                response = f"Unknown command: '{command}'. Type 'HELP' for commands."

            conn.sendall(response.encode('utf-8') + b'\n')

        except ConnectionResetError:
            print(f"Client {addr} forcefully disconnected.")
            break
        except Exception as e:
            print(f"Error with client {addr}: {e}")
            break

    print(f"Client {addr} disconnected.")
    conn.close()

def start_server():
    """Starts the main server loop."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"Server listening on {HOST}:{PORT}")

        while True:
            conn, addr = s.accept()
            # Handle client in a new thread to allow multiple connections
            client_handler = threading.Thread(target=handle_client, args=(conn, addr))
            client_handler.start()

if __name__ == "__main__":
    start_server()