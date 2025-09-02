import socket, time, random, crc

HOST = "127.0.0.1"
PORT = 3000
LOSS_PROB = 0.2   # 20% chance to drop a received frame or ack

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
            expected = 0
            buffer = {}
            data_buf = ""
            last_recieved = -1

            while True:
                data = conn.recv(1024)
                if not data: break
                data_buf += data.decode()

                while "\n" in data_buf:
                    msg, data_buf = data_buf.split("\n", 1)
                    if not msg: continue
                    try:
                        header = msg[:HEADER_SIZE]
                        src = header[:6*8]
                        dest = header[6*8:12*8]
                        fno = int(msg[12*8: HEADER_SIZE], 2)
                        payload = msg[HEADER_SIZE: HEADER_SIZE+PAYLOAD_SIZE]
                        tail = msg[CODEWORD_SIZE - TAILER_SIZE:]
                        time.sleep(1)
                        
                        check_tail = crc.generate_crc(header + payload, 'CRC-32')
                        if tail != check_tail:
                            print(f"Corrupted frame recieved: frame {fno} ignored")
                            continue

                        for no in range(last_recieved+1, fno):
                            conn.send(f"nak:{no}\n".encode())
                            print(f"Sent NAK for missing frame {no}")
                            
                        # Simulate frame loss
                        if random.random() < LOSS_PROB:
                            print(f"Simulated frame loss: frame {fno} dropped")
                            continue

                        if fno not in buffer:
                            buffer[fno] = payload
                            print(f"Frame {fno} buffered")

                            # Simulate ACK loss
                            if random.random() < LOSS_PROB:
                                print(f"Simulated ACK loss: ack {fno} not sent")
                            else:
                                last_recieved = fno
                                conn.send(f"ack:{fno}\n".encode())

                            # deliver in-order frames
                            while expected in buffer:
                                print(f"Delivered in order: {expected}")
                                buffer.pop(expected)
                                expected += 1
                    except ValueError:
                        print(f"Corrupted frame ignored: {msg}")

receiver()
