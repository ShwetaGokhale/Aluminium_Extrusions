# receiver.py
import serial
import time
from datetime import datetime

# ------------------------------------------------------------
# Configuration
# ------------------------------------------------------------
REC_PORT = '72.60.201.184'       # COM connected to Reyax LoRa Receiver
REC_BAUD = 115200       # Must match sender baud
NETWORK_ID = 5

# ------------------------------------------------------------
# Function to send AT command and read response
# ------------------------------------------------------------
def send_at_command(ser, cmd, delay=0.5):
    print(f"[AT CMD] Sending: {cmd}")
    ser.write((cmd + '\r\n').encode())
    time.sleep(delay)
    response = ser.read_all().decode(errors='ignore').strip()
    if response:
        print(f"[AT RESP] {response}")
    return response

# ------------------------------------------------------------
# Configure Reyax module as Receiver
# ------------------------------------------------------------
def setup_receiver(ser):
    print("[SETUP] Configuring LoRa Receiver...")
    send_at_command(ser, 'AT')
    send_at_command(ser, 'AT+ADDRESS=2')
    send_at_command(ser, f'AT+NETWORKID={NETWORK_ID}')
    send_at_command(ser, 'AT+BAND=433000000')
    send_at_command(ser, 'AT+PARAMETER=9,7,1,12')
    print("[SETUP] LoRa Receiver ready.")

# ------------------------------------------------------------
# Main Logic: Receive from LoRa
# ------------------------------------------------------------
if __name__ == "__main__":
    print("[INFO] Opening COM port for Receiver...")
    rec = serial.Serial(REC_PORT, REC_BAUD, timeout=1)
    time.sleep(2)
    setup_receiver(rec)

    print("[INFO] LoRa Receiver running. Press Ctrl+C to stop.")
    try:
        while True:
            if rec.in_waiting > 0:
                data = rec.readline().decode('utf-8', errors='ignore').strip()
                if data.startswith("+RCV="):
                    try:
                        raw = data.replace("+RCV=", "")
                        src_addr, rest = raw.split(',', 1)
                        length_str, message_and_extra = rest.split(',', 1)
                        length = int(length_str)
                        message = message_and_extra[:length]
                        print(f"[ RECEIVED ] {message}")
                    except Exception as e:
                        print(f"[{datetime.now()}] Parsing error: {data} | {e}")
            time.sleep(0.05)
    except KeyboardInterrupt:
        print("\n[INFO] Stopped by user.")
    finally:
        rec.close()
        print("[INFO] COM port closed.")
