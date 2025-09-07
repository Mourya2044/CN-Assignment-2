import socket
import random
import time
import crc

HOST = '127.0.0.1'
PORT = 3000

CODEWORD_SIZE = 64*8
HEADER_SIZE = 12*8 + 16
TAILER_SIZE = 4*8
PAYLOAD_SIZE = CODEWORD_SIZE - (HEADER_SIZE + TAILER_SIZE)

def receiver():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        print(f"Server listening on {HOST}:{PORT}")

        conn, addr = s.accept()
        with conn:
            print(f"Connected by {addr}")
            next_frame = 0
            buffer = ""

            while True:
                data = conn.recv(1024)
                if not data:
                    break

                buffer += data.decode("utf-8")

                # process all complete frames separated by newline
                while "\n" in buffer:
                    msg, buffer = buffer.split("\n", 1)
                    if not msg:
                        continue

                    try:                        
                        header = msg[:HEADER_SIZE]
                        src = header[:6*8]
                        dest = header[6*8:12*8]
                        frame_no = int(msg[12*8: HEADER_SIZE], 2)
                        payload = msg[HEADER_SIZE: HEADER_SIZE+PAYLOAD_SIZE]
                        tail = msg[CODEWORD_SIZE - TAILER_SIZE:]
                        
                        check_tail = crc.generate_crc(header + payload, 'CRC-32')
                        if tail != check_tail:
                            print(f"Corrupted frame recieved: frame {frame_no} ignored")
                            continue
                        

                        # time.sleep(random.uniform(1, 6))  # artificial delay

                        if frame_no <= next_frame:
                            print(f"Frame received: {frame_no}")
                            next_frame += 1
                            if random.random() < 0.5:
                                print("Simulated ACK loss")
                                continue
                            conn.send(f"ack:{frame_no}\n".encode("utf-8"))
                        # else:
                        #     # duplicate ACK for last in-order frame
                        #     if random.random() < 0.5:
                        #         print("Simulated ACK loss")
                        #         continue
                        #     conn.send(f"ack:{next_frame-1}\n".encode("utf-8"))

                    except ValueError:
                        print(f"Corrupted/partial frame ignored: {msg}")
            print("Transfer complete. Connection closed.")

receiver()
