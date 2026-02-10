import RPi.GPIO as GPIO
import time
import sys
import signal

LED_PIN = 17
GPIO.setmode(GPIO.BCM)
GPIO.setup(LED_PIN, GPIO.OUT)

# Safe Cleanup on Kill
def cleanup(signum, frame):
    GPIO.output(LED_PIN, GPIO.LOW)
    GPIO.cleanup()
    print("GPIO Cleanup Complete.")
    sys.exit(0)

signal.signal(signal.SIGTERM, cleanup)

try:
    delay = float(sys.argv[1])
    
    if delay == 0:
        # Static ON
        GPIO.output(LED_PIN, GPIO.HIGH)
        print("LED Turned ON (Static)")
        while True:
            time.sleep(1) # Keep script alive
    else:
        # Blinking
        print(f"Blinking LED every {delay} seconds")
        while True:
            GPIO.output(LED_PIN, GPIO.HIGH)
            time.sleep(delay)
            GPIO.output(LED_PIN, GPIO.LOW)
            time.sleep(delay)

except Exception as e:
    print(f"Error: {e}")
finally:
    cleanup(None, None)
