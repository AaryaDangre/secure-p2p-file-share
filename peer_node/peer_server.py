import socket

import json

from file_transfer.file_receiver import receive_file



HOST = "0.0.0.0"

PORT = 5000



CHAT_FILE = "chat_messages.json"





def load_messages():

    try:

        with open(CHAT_FILE, "r") as f:

            return json.load(f)

    except:

        return []





def save_message(msg):

    data = load_messages()

    data.append(msg)



    with open(CHAT_FILE, "w") as f:

        json.dump(data, f)





def start_server():

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server.bind((HOST, PORT))

    server.listen(5)



    print(f"[SERVER] Listening on {HOST}:{PORT}")



    while True:

        conn, addr = server.accept()

        print(f"[CONNECTED] {addr}")



        try:

            data = conn.recv(1024)



            if not data:

                conn.close()

                continue



            message = data.decode(errors="ignore")



            if message.startswith("FILE"):

                receive_file(conn)



            elif message.startswith("MULT"):

                num_files_bytes = conn.recv(4)

                num_files = int.from_bytes(num_files_bytes, 'big')



                print(f"[RECEIVING {num_files} FILES]")



                for i in range(num_files):

                    receive_file(conn)



            elif message.startswith("CHAT"):

                chat_msg = message.replace("CHAT:", "").strip()



                print(f"[CHAT RECEIVED] {addr} → {chat_msg}")



                save_message({

                    "message": chat_msg,

                    "type": "received",

                    "sender_ip": addr[0],

                    "sender_port": 5000

                })



            else:

                print(f"[UNKNOWN MESSAGE] {message}")



        except Exception as e:

            print(f"[SERVER ERROR] {e}")



        finally:

            conn.close()

            print("[CONNECTION CLOSED]")





if __name__ == "__main__":

    start_server()