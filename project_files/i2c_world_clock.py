import tm1637
from datetime import datetime
import time
import signal
import sys

# --- CONFIGURATION ---
CLK_PIN = 5
DIO_PIN = 4
BRIGHTNESS = 3

# Initialize Display
tm = tm1637.TM1637(clk=CLK_PIN, dio=DIO_PIN)
tm.brightness(BRIGHTNESS)

# --- CLEANUP HANDLER (Triggered by main_listener.py) ---
def cleanup(signum, frame):
    print("LOG:World Clock stopping...")
    tm.write([0, 0, 0, 0])  # Clear display
    tm.brightness(0)
    sys.exit(0)

# Listen for the "Kill" signal (SIGTERM)
signal.signal(signal.SIGTERM, cleanup)

print("LOG:World Clock Started on GPIO 5/4")

try:
    while True:
        now = datetime.now()
        hour = now.hour
        minute = now.minute
        second = now.second

        # Logic: We use 'colon=' inside numbers() to prevent overwriting
        # This fixes the flickering issue in your original code
        show_colon = (second % 2 == 0)
        tm.numbers(hour, minute, colon=show_colon)

        time.sleep(0.5)

except Exception as e:
    print(f"LOG:Error in Clock: {e}")
finally:
    tm.write([0, 0, 0, 0])
