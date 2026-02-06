import serial
import RPi.GPIO as GPIO
import time

# --- CONFIGURATION ---
# Note: On Pi, the built-in UART is usually '/dev/ttyS0' or '/dev/ttyAMA0'
# If using a USB adapter on the Pi side, it's likely '/dev/ttyUSB0'
UART_PORT = '/dev/ttyUSB0' 
BAUD_RATE = 9600
LED_PIN = 18

# --- SETUP ---
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)

try:
    ser = serial.Serial(UART_PORT, BAUD_RATE, timeout=1)
    ser.reset_input_buffer()
    print(f"🚀 Pi Listener Ready on {UART_PORT}...")
except Exception as e:
    print(f"❌ Connection Error: {e}")
    exit()

# --- MAIN LOOP ---
try:
    while True:
        if ser.in_waiting > 0:
            # 1. Read the command from Flask
            command = ser.readline().decode('utf-8').strip()
            print(f"📩 Received: {command}")

            # 2. Execute Hardware Action
            if command == "LED_ON":
                GPIO.output(LED_PIN, GPIO.HIGH)
                reply = "LED is now ON"
            elif command == "LED_OFF":
                GPIO.output(LED_PIN, GPIO.LOW)
                reply = "LED is now OFF"
            else:
                reply = f"Unknown command: {command}"

            # 3. Send Confirmation back to Flask
            print(f"📤 Replying: {reply}")
            ser.write((reply + "\n").encode('utf-8'))
            
        time.sleep(0.1)  # Save CPU power

except KeyboardInterrupt:
    print("\nStopping...")
finally:
    GPIO.cleanup()
    ser.close()
