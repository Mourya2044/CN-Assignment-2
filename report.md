
# Computer Networks Lab Report

**Title**

*   **Name:** [Your Name]
*   **Class:** [Your Class]
*   **Group:** [Your Group]
*   **Assignment Number:** 2
*   **Problem Statement:** Implementation and analysis of reliable data transfer protocols (Go-Back-N/Stop-and-Wait and Selective Repeat) and error detection using CRC.
*   **Date:** 2025-09-07

**Design**

*   **Purpose of the program:**
    This project simulates two reliable data transfer protocols: a basic sliding window protocol (likely Go-Back-N or Stop-and-Wait) and Selective Repeat. It also includes error detection mechanisms using CRC (Cyclic Redundancy Check) and a simple checksum. The purpose is to send data from a sender to a receiver over an unreliable channel, which is simulated by introducing errors and packet loss. The project allows for a comparative analysis of the two protocols in terms of their efficiency and reliability in handling these errors.

*   **Structure Diagram:**
    The project is structured into several modules:
    *   **Sender (`sender.py`, `sender_sr.py`):** Reads data from a file, creates frames with headers (source/destination address, sequence number) and a CRC-32 checksum, and sends them to the receiver. It manages a sending window, timers, and retransmissions based on acknowledgements (ACKs) or timeouts.
    *   **Receiver (`reciever.py`, `reciever_sr.py`):** Receives frames from the sender, verifies the CRC-32 checksum, and sends ACKs for correctly received frames. The Selective Repeat receiver can buffer out-of-order frames and send negative acknowledgements (NAKs).
    *   **Error Detection (`crc.py`, `checksum.py`):** Provides functions to generate and verify CRC and checksums. `crc.py` is used in the main sender/receiver loops for robust error detection.
    *   **Error Injection (`injecterror.py`):** A testing module to simulate an unreliable channel by injecting various types of errors (single bit, burst, odd) into the data frames.
    *   **Data Files (`data.txt`, `test_data.txt`):** Text files containing the binary data to be transmitted.

*   **Input and Output Format:**
    *   **Input:** The input is a text file (`test_data.txt`) containing a binary string. The sender reads this data, and the user can configure parameters like window size and timeout values.
    *   **Output:** The sender and receiver print status messages to the console, showing the frames being sent, received, acknowledged, and retransmitted. The receiver, upon successful reception, would have the complete, error-free data.

**Implementation**

*   **Method Description:**
    *   **`sender.py` / `reciever.py` (Go-Back-N/Stop-and-Wait):**
        *   The sender sends a window of frames and waits for an ACK for the base of the window.
        *   If an ACK is received, the window slides forward.
        *   If a timeout occurs, the sender retransmits all frames from the last acknowledged frame onwards.
        *   The receiver only accepts frames in the expected order and discards any out-of-order frames.
    *   **`sender_sr.py` / `reciever_sr.py` (Selective Repeat):**
        *   The sender sends a window of frames, each with its own timer.
        *   The receiver ACKs each correctly received frame, even if it's out of order, and buffers it.
        *   If a frame is missing, the receiver sends a NAK.
        *   The sender only retransmits the specific frame that was lost or for which a NAK was received.
    *   **`crc.py`:**
        *   `generate_crc(data, polynomial)`: Takes data and a polynomial, and returns the CRC checksum.
        *   `verify_crc(data, polynomial)`: Takes data with an appended CRC and verifies its integrity. Returns `True` if the data is correct, `False` otherwise.

*   **Code Snippets:**

    *   **Selective Repeat Sender (`sender_sr.py`):**
        ```python
        def sender():
            global next_frame, file_complete, buffer
            with open('test_data.txt', 'r') as f:
                while True:
                    with lock:
                        if next_frame < base + WINDOW_SIZE:   # within window
                            # prepping data
                            data = f.read(PAYLOAD_SIZE)
                            if not data:
                                print("End of file reached")
                                file_complete = True
                                return
                            # ... (frame creation)
                            buffer[next_frame] = frame
                            # ... (send frame and start timer)
                            next_frame += 1
                    time.sleep(1)
        ```

    *   **Selective Repeat Receiver (`reciever_sr.py`):**
        ```python
        while "
" in data_buf:
            msg, data_buf = data_buf.split("
", 1)
            # ... (frame parsing and CRC check)
            if fno not in buffer:
                buffer[fno] = payload
                print(f"Frame {fno} buffered")
                last_recieved = fno
                conn.send(f"ack:{fno}
".encode())

            # deliver in-order frames
            while expected in buffer:
                print(f"Delivered in order: {expected}")
                buffer.pop(expected)
                expected += 1
        ```

**Test cases**

*   **Error-free transmission:** Run the sender and receiver without any error injection to verify that the data is transmitted correctly.
*   **Single bit errors:** Use `injecterror.injecterror()` to introduce single bit flips in the frames. The receiver should detect these errors using the CRC check and discard the frames. The sender should then retransmit the frames.
*   **Burst errors:** Use `injecterror.injectbursterror()` to simulate burst errors. The CRC-32 should be effective in detecting these.
*   **Odd number of errors:** Use `injecterror.injectodderror()` to test the error detection capabilities.
*   **Frame loss:** The sender and receiver scripts include a `LOSS_PROB` variable to simulate frame and ACK loss. This tests the timeout and retransmission mechanisms of the protocols.
*   **ACK loss:** Similar to frame loss, the loss of ACK packets is simulated to test the sender's timeout and retransmission logic.
*   **Out-of-order delivery:** By introducing delays, the out-of-order arrival of frames can be simulated to test the receiver's buffering mechanism (especially in Selective Repeat).

**Results**

*   **Performance Metrics:**
    *   **Throughput:** The rate of successful data transfer (bits per second). This can be calculated by measuring the total data sent and the time taken.
    *   **Error Detection Rate:** The percentage of injected errors that are successfully detected by the receiver.
    *   **Retransmission Rate:** The number of retransmitted frames as a percentage of the total frames sent.

*   **Expected Results:**
    *   Selective Repeat is expected to have a higher throughput than Go-Back-N, especially in a high-error-rate environment, because it retransmits only the lost frames, not the entire window.
    *   CRC-32 should detect all single-bit errors, all burst errors up to 32 bits, and a very high percentage of other errors.
    *   The retransmission rate will increase with the error and loss probability.

**Analysis**

*   **Protocol Comparison:**
    *   **Go-Back-N/Stop-and-Wait:** Simpler to implement, but inefficient if the bandwidth-delay product is large or the error rate is high. A single lost frame causes the retransmission of many subsequent frames.
    *   **Selective Repeat:** More complex to implement due to the need for individual timers and buffering at the receiver. However, it is much more efficient on unreliable links as it minimizes retransmissions.
*   **Error Detection:**
    *   CRC is a powerful error detection mechanism and is much more robust than a simple checksum. The choice of the polynomial is crucial for its effectiveness. CRC-32 is a standard for Ethernet and other protocols due to its excellent error detection capabilities.
*   **Bugs and Improvements:**
    *   The current implementation uses a fixed timeout value. A dynamic timeout, based on the round-trip time (RTT), would make the protocols more adaptive to network conditions.
    *   The file reading and sending loop could be made more efficient.

**Comments**

*   **Evaluation of the Lab:**
    This assignment provides a practical understanding of the challenges of reliable data transfer over unreliable networks. It demonstrates the core principles of sliding window protocols and the importance of error detection.
*   **What was learned:**
    *   The implementation details of Go-Back-N and Selective Repeat protocols.
    *   The working of CRC and its superiority over simple checksums.
    *   The complexities of handling timeouts, retransmissions, and duplicate packets.
*   **Suggestions for Improvements:**
    *   Visualize the sending and receiving windows and the movement of frames.
    *   Implement a graphical user interface (GUI) to control the simulation parameters and visualize the results.
    *   Compare the performance of different CRC polynomials.
