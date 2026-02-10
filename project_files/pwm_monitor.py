import RPi.GPIO as GPIO
import time
import signal
import sys

PWM_PIN = 12
GPIO.setmode(GPIO.BCM)
GPIO.setup(PWM_PIN, GPIO.OUT)

pwm = GPIO.PWM(PWM_PIN, 100) # 100Hz frequency
pwm.start(0)

# Safe Cleanup
def cleanup(signum, frame):
    pwm.stop()
    GPIO.cleanup()
    print("PWM Stopped.")
    sys.exit(0)

signal.signal(signal.SIGTERM, cleanup)

try:
    print("Starting Breathing LED...")
    while True:
        # Fade In
        for dc in range(0, 101, 5):
            pwm.ChangeDutyCycle(dc)
            time.sleep(0.05)
        # Fade Out
        for dc in range(100, -1, -5):
            pwm.ChangeDutyCycle(dc)
            time.sleep(0.05)
        
        print("Breathing Cycle Complete") # Sent to Logs

except Exception as e:
    print(f"Error: {e}")
finally:
    cleanup(None, None)
