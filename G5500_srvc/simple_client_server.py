import socket
import threading
import datetime
import platform
import G5500

# Server configuration
HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)

CONFIG_FILE='G5500_config.txt'
CAL_FILE='rotator_cal.txt'

def handle_client(conn, addr, g5500 : G5500):
    """Handles individual client connections to the G5500 az/el rotator."""
    print(f"Connected by {addr}")
    conn.sendall(b"Welcome to the command server! Type 'HELP' for commands.\n")

    while True:
        try:
            data = conn.recv(1024)  # Receive up to 1024 bytes
            if not data:
                break  # Client disconnected

            args = data.decode('utf-8').strip().upper().split()
            command = args[0] if args else ""
            response = ""

            if command in ["STOP", "X"]:
                g5500.stop_motion()
                response = f"STOP command executed."
            elif command == "MOVETO":
                if len(args) != 3:
                    response = "Error: MOVETO command requires two arguments: az and el."
                else:
                    try:
                        az = float(args[1])
                        el = float(args[2])
                    except ValueError:
                        response = "Error: MOVETO command arguments must be numeric."
                    else:
                        g5500.move_to(az, el) # Blocking call
                        response = f"MOVETO {az},{el} command executed."
            elif command == "LEFT":
                g5500.move_az_left()
                response = f"LEFT command executed."
            elif command == "RIGHT":
                g5500.move_az_right()
                response = f"RIGHT command executed."
            elif command == "UP":
                g5500.move_el_up()
                response = f"UP command executed."
            elif command == "DOWN":
                g5500.move_el_down()
                response = f"DOWN command executed."
            elif command == "READ":
                g5500.read_sensors()
                response = f"READ command executed. {g5500}"
            elif command == "HELP":
                response = "Available commands: STOP, LEFT, RIGHT, UP, DOWN, READ, HELP, QUIT"
            elif command == "QUIT":
                g5500.stop_motion()
                response = "STOP command executed. Exiting."
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

    g5500.stop_motion()
    print(f"Client {addr} disconnected.")
    conn.close()

def start_server(g5500 : G5500, portnum : int = PORT):
    """Starts the main server loop."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, portnum))
        s.listen()
        print(f"Server listening on {HOST}:{portnum}")
        while True:
            conn, addr = s.accept()
            # Handle client in a new thread to allow multiple connections
            client_handler = threading.Thread(target=handle_client, args=(conn, addr, g5500))
            client_handler.start()

if __name__ == "__main__":
    import G5500_LabJackIF as G5500_IF
    g5500 = G5500_IF.G5500_LabJack(CAL_FILE)

    start_server(g5500)