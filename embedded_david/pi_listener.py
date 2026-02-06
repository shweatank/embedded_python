import serial
import RPi.GPIO as GPIO

# --- CONFIGURATION ---
LED_PIN = 27
SERIAL_PORT = '/dev/serial0' 
BAUD_RATE = 9600

# --- SETUP ---
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.setwarnings(False)

try:
    # Open the serial port on the Pi
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    ser.flush()
    print("--- Pi Listening for Commands ---")

    while True:
        if ser.in_waiting > 0:
            # Read the incoming command
            data = ser.readline().decode('utf-8').strip()
            
            if data == 'on':
                GPIO.output(LED_PIN, GPIO.HIGH)
                print("Command: ON  | Status: LED turned ON")
                
            elif data == 'off':
                GPIO.output(LED_PIN, GPIO.LOW)
                print("Command: OFF | Status: LED turned OFF")
                
            else:
                print(f"Received unknown data: {data}")

except KeyboardInterrupt:
    print("\nExiting and cleaning up GPIO...")
    GPIO.cleanup()
    ser.close()
