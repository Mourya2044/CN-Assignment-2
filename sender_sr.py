import socket, threading, time, random, crc, injecterror

HOST = "127.0.0.1"
PORT = 3000
WINDOW_SIZE = 10
TIMEOUT = 5
LOSS_PROB = 0.1
retransmissions = 0

SRC_ADDR = "000000010000000100000001000000010000000100000001"
DEST_ADDR = "000000100000001000000010000000100000001000000010"
CODEWORD_SIZE = 64*8
HEADER_SIZE = 12*8 + 16
TAILER_SIZE = 4*8
PAYLOAD_SIZE = CODEWORD_SIZE - (HEADER_SIZE + TAILER_SIZE)

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
while True:
    try:
        print(f"Attempting to connect to {HOST}:{PORT}...")
        sock.connect((HOST, PORT))
        break
    except ConnectionRefusedError:
        print("Connection refused, retrying in 2 seconds...")
        time.sleep(2)
print(f"Connected to {HOST}:{PORT}")

buffer = {}       # frame_no -> data
timers = {}       # frame_no -> Timer
next_frame = 0
base = 0
lock = threading.Lock()
ack_buffer = ""
file_complete = False

def timeout_handler(frame_no):
    with lock:
        if frame_no in buffer:
            frame = buffer[frame_no]
            
            sock.send(f"{frame}\n".encode())
            print(f"Timeout! Resent frame {frame_no}")
            # restart timer
            t = threading.Timer(TIMEOUT, timeout_handler, args=(frame_no,))
            timers[frame_no] = t
            t.start()

def sender():
    global next_frame, file_complete, buffer
    with open('data.txt', 'r') as f:
        while True:
            with lock:
                if next_frame < base + WINDOW_SIZE:   # within window
                    # prepping data
                    data = f.read(PAYLOAD_SIZE)
                    if not data:
                        print("End of file reached")
                        file_complete = True
                        return
                    data = data + ('0'*(PAYLOAD_SIZE - len(data)))
                    frame_no = bin(next_frame)[2:]
                    payload = SRC_ADDR + DEST_ADDR + ('0'*(16-len(frame_no)) + frame_no) + data
                    tail = crc.generate_crc(payload, 'CRC-32')
                    
                    frame = payload + ('0'*(TAILER_SIZE - len(tail)) + tail)
                    buffer[next_frame] = frame
                    if random.random() < LOSS_PROB:
                        frame = injecterror.injectodderror(frame)

                    if random.random() < LOSS_PROB:
                        print(f"Simulated loss: frame {next_frame} not sent")
                    else:
                        sock.send(f"{frame}\n".encode())
                        print(f"Sent: {next_frame}")
                    # start per-frame timer
                    t = threading.Timer(TIMEOUT, timeout_handler, args=(next_frame,))
                    timers[next_frame] = t
                    t.start()
                    next_frame += 1
            # time.sleep(1)

def acknowledge():
    global base, ack_buffer, file_complete, buffer, retransmissions
    while True:
        data = sock.recv(1024)
        if not data: break
        ack_buffer += data.decode()
        while "\n" in ack_buffer:
            msg, ack_buffer = ack_buffer.split("\n", 1)
            if not msg: continue
            try:
                type, ack_no = msg.split(":", 1)
                ack_no = int(ack_no)

                with lock:
                    if type == "ack":
                        if ack_no in buffer:
                            buffer.pop(ack_no)
                            if ack_no in timers:
                                timers[ack_no].cancel()
                                timers.pop(ack_no)
                            print(f"ACK {ack_no} received -> frame removed")
                            if file_complete and not buffer:
                                return

                            # slide base forward if possible
                            while base not in buffer and base < next_frame:
                                base += 1
                    elif type == "nak":
                        if ack_no in timers and ack_no in buffer:
                            timers[ack_no].cancel()
                            timers.pop(ack_no)
                            frame = buffer[ack_no]
                            sock.send(f"{frame}\n".encode())
                            retransmissions += 1
                            t = threading.Timer(TIMEOUT, timeout_handler, args=(ack_no,))
                            timers[ack_no] = t
                            t.start()
                            print(f"NAK! Resent frame {ack_no}")

            except ValueError:
                print(f"Bad ACK ignored: {msg}")

def run():
    threading.Thread(target=sender, daemon=True).start()
    threading.Thread(target=acknowledge, daemon=True).start()

start_time = time.time()
run()
while True:
    if file_complete and not buffer:
        sock.close()
        end_time = time.time()
        elapsed_time = end_time - start_time
        with open('data.txt', 'r') as f:
            f.seek(0, 0)
            file_size_bits = len(f.read().strip())
        throughput = file_size_bits / elapsed_time
        print(f"Total time taken: {elapsed_time:.2f} seconds")
        print(f"Throughput: {throughput:.2f} bps")
        print(f"Total frames sent (including retransmissions): {next_frame +retransmissions}")
        print(f"Total retransmissions: {retransmissions}")
        print(f"Retransmission Rate: {(retransmissions / (next_frame +retransmissions))*100:.2f}%")
        print("Transfer complete. Closing program.")
        break
    time.sleep(1)
