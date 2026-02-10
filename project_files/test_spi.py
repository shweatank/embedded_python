import spidev
import time

# Use SPI Bus 0, Device 0 (Pin 24/CE0)
bus = 0
device = 0

spi = spidev.SpiDev()
spi.open(bus, device)
spi.max_speed_hz = 50000 # Start slow for initialization
spi.mode = 0

def test_connection():
    print("Wake up card...")
    # Send 80 dummy clock cycles (required to wake up SD cards)
    spi.xfer2([0xFF] * 10)

    print("Sending CMD0 (Reset)...")
    # CMD0: 0x40, Arg: 0x00000000, CRC: 0x95
    msg = [0x40, 0x00, 0x00, 0x00, 0x00, 0x95]
    spi.xfer2(msg)

    # Read response (look for 0x01)
    for i in range(10):
        resp = spi.xfer2([0xFF])[0]
        if resp == 0x01:
            return True, resp
        if resp != 0xFF:
            return False, resp # Received garbage data
            
    return False, 0xFF # Received nothing

try:
    success, code = test_connection()
    if success:
        print(f"✅ SUCCESS: SD Card Detected! (Response: 0x{code:02X})")
    elif code == 0xFF:
        print(f"❌ FAILURE: No response (0xFF). Check wiring, specifically MISO/MOSI.")
    else:
        print(f"⚠️  WARNING: Garbage data (0x{code:02X}). Wiring likely loose or power unstable.")
finally:
    spi.close()
