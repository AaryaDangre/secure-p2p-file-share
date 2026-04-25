import socket
from file_transfer.file_sender import send_file

PORT = 5000

def connect_to_peer(ip):
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    client.connect((ip, PORT))

    print("[CONNECTED TO PEER]")

    while True:
        msg = input("Enter message (or 'send' to transfer file): ")

        if msg == "send":
            # Ask for single or multiple file transfer
            transfer_type = input("Single file (s) or multiple files (m)? ").lower()
            
            if transfer_type == 'm':
                # Multiple file transfer
                try:
                    num_files = int(input("Enter number of files: "))
                    if num_files <= 0:
                        print("Number of files must be positive.")
                        continue
                    
                    file_paths = []
                    for i in range(num_files):
                        file_path = input(f"Enter file path {i+1}: ")
                        file_paths.append(file_path)
                    
                    # Send multi-file protocol header
                    client.send(b"MULTI")
                    client.send(num_files.to_bytes(4, 'big'))
                    print(f"[SENDING {num_files} FILES]")
                    
                    # Send each file
                    for i, file_path in enumerate(file_paths):
                        print(f"[FILE {i+1}/{num_files}]")
                        send_file(client, file_path)
                    
                    print("[ALL FILES SENT]")
                    
                except ValueError:
                    print("Invalid number. Please enter a valid integer.")
            else:
                # Single file transfer (existing logic)
                client.send(b"FILE")
                file_path = input("Enter file path: ")
                send_file(client, file_path)
        else:
            client.send(msg.encode())

if __name__ == "__main__":
    ip = input("Enter peer IP: ")
    connect_to_peer(ip)
