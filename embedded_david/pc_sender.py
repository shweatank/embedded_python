import serial
import sys

# --- CONFIGURATION ---
# Windows: 'COM3', 'COM4', etc. | Linux/Mac: '/dev/ttyUSB0'
PC_PORT = '/dev/ttyUSB0'  
BAUD_RATE = 9600

try:
    ser = serial.Serial(PC_PORT, BAUD_RATE, timeout=1)
    print(f"Connected to {PC_PORT}. Type 'on' or 'off' to control Pi LED.")
    print("Press Ctrl+C to exit.")

    while True:
        command = input("Enter command: ").strip().lower()
        
        if command in ['on', 'off']:
            # Send command with a newline character so Pi knows it's finished
            ser.write((command + "\n").encode('utf-8'))
            print(f"Sent: {command}")
        else:
            print("Invalid command. Please type 'on' or 'off'.")

except KeyboardInterrupt:
    print("\nExiting...")
    ser.close()
except Exception as e:
    print(f"Error: {e}")
