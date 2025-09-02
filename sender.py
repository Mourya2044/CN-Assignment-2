import socket
import threading
import time
import random
import injecterror
import crc

HOST = '127.0.0.1'
PORT = 3000

buffer = {}
next_frame = 0
recieved_ack = -1
lock = threading.Lock()

timer_running = False
timer = None
ack_buffer = ""   # <-- buffer for partial/multiple ACKs

SRC_ADDR = "000000010000000100000001000000010000000100000001"
DEST_ADDR = "000000100000001000000010000000100000001000000010"
CODEWORD_SIZE = 64*8
HEADER_SIZE = 12*8 + 16
TAILER_SIZE = 4*8
PAYLOAD_SIZE = CODEWORD_SIZE - (HEADER_SIZE + TAILER_SIZE)

def start_timer():
    global timer, timer_running
    if not timer_running:
        timer_running = True
        timer = threading.Timer(5.0, timeout_handler)
        timer.start()

def stop_timer():
    global timer, timer_running
    if timer is not None:
        timer.cancel()
    timer_running = False

def timeout_handler():
    global next_frame, recieved_ack
    print("Timeout! Resending frames...")
    with lock:
        for f in range(recieved_ack+1, next_frame):
            frame = buffer[f]
            sock.send(f"{frame}\n".encode("utf-8"))
            print(f"Resent: {f}")
    start_timer()

def sender(n):
    global next_frame, buffer
    while True:
        with lock:
            if next_frame - recieved_ack < n:
                
                # prepping data
                data = f.read(PAYLOAD_SIZE)
                frame_no = bin(next_frame)[2:]
                payload = SRC_ADDR + DEST_ADDR + ('0'*(16-len(frame_no)) + frame_no) + data
                tailer = crc.generate_crc(payload, 'CRC-32')
                
                frame = payload + ('0'*(TAILER_SIZE - len(tailer)) + tailer)
                
                buffer[next_frame] = frame
                if random.random() < 0.1:
                    frame = injecterror.injectodderror(frame)
                
                sock.send(f"{frame}\n".encode("utf-8"))
                print(f"Sent: {next_frame}, len={len(frame)}")
                if not timer_running:
                    start_timer()
                next_frame += 1
        time.sleep(1)

def acknowledge():
    global recieved_ack, ack_buffer
    while True:
        data = sock.recv(1024)
        if not data:
            break

        ack_buffer += data.decode("utf-8")

        # process all complete ACKs separated by newline
        while "\n" in ack_buffer:
            msg, ack_buffer = ack_buffer.split("\n", 1)
            if not msg:
                continue
            try:
                ack_type, ack_no = msg.split(":", 1)
                ack_no = int(ack_no)
                with lock:
                    if ack_no > recieved_ack:
                        for i in range(recieved_ack+1, ack_no+1):
                            if i in buffer:
                                del buffer[i]
                        recieved_ack = ack_no
                        print(f"Acknowledged: frame {ack_no}")

                        # stop timer if all outstanding frames acked
                        if recieved_ack == next_frame-1:
                            stop_timer()
                        else:
                            # restart timer for next unacked frame
                            stop_timer()
                            start_timer()
            except ValueError:
                print(f"Corrupt ACK ignored: {msg}")

def send(n):
    threading.Thread(target=sender, args=(n,), daemon=True).start()
    threading.Thread(target=acknowledge, daemon=True).start()

with open('data.txt', 'r') as f, socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
    sock.connect((HOST, PORT))
    print(f"Connected to {HOST}:{PORT}")
    send(4)

    while True:
        time.sleep(1)
