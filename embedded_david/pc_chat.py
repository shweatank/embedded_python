import serial
import threading
import sys
import time

# --- CHECK YOUR COM PORT ---
# Windows: 'COM3', 'COM4' | Linux: '/dev/ttyUSB0'
PORT = '/dev/ttyUSB0' 
BAUD = 9600

try:
    ser = serial.Serial(PORT, BAUD, timeout=1)
    ser.flush()
    print(f"✅ PC Connected to {PORT}")
except Exception as e:
    print(f"❌ Error opening port: {e}")
    sys.exit()

def listen_for_data():
    while True:
        try:
            if ser.in_waiting > 0:
                # Read whatever is in the buffer (raw bytes)
                data = ser.read(ser.in_waiting)
                # Decode to text, replacing errors with '?'
                text = data.decode('utf-8', errors='replace').strip()
                if text:
                    print(f"\n[FROM PI]: {text}")
                    print("You: ", end="", flush=True)
            time.sleep(0.1) # reduce CPU usage
        except Exception as e:
            print(f"Read Error: {e}")
            break

# Start Listener in Background
t = threading.Thread(target=listen_for_data, daemon=True)
t.start()

# Main Sender Loop
try:
    print("--- CHAT STARTED ---")
    print("Type message and press ENTER.")
    print("You: ", end="", flush=True)
    
    while True:
        msg = input()
        if msg:
            # Send message + Newline (\n)
            full_msg = msg + "\n"
            ser.write(full_msg.encode('utf-8'))
            
except KeyboardInterrupt:
    print("\nClosing connection...")
    ser.close()
