'''I2C: smbus2 (simple + reliable)

SPI: spidev (kernel-native /dev/spidev*)

0) One-time enable + verify

Enable interfaces:

sudo raspi-config
# Interface Options -> I2C -> Enable
# Interface Options -> SPI -> Enable
sudo reboot


Verify device nodes:

ls -l /dev/i2c-1
ls -l /dev/spidev0.0


Scan I2C bus:

sudo apt install -y i2c-tools
i2cdetect -y 1

1) Install Python packages
pip3 install smbus2 spidev

✅ I2C Sample Program (smbus2)
Example A: Detect + read common registers (generic template)

This is a template you can adapt to any sensor after you know its address + register map.

i2c_read_write_template.py'''
from smbus2 import SMBus, i2c_msg
import time

I2C_BUS = 1
DEV_ADDR = 0x71   # change after i2cdetect (example: MPU6050 is often 0x68)

def i2c_write_reg(bus: SMBus, addr: int, reg: int, val: int) -> None:
    bus.write_byte_data(addr, reg, val & 0xFF)

def i2c_read_reg(bus: SMBus, addr: int, reg: int) -> int:
    return bus.read_byte_data(addr, reg)

def i2c_read_bytes(bus: SMBus, addr: int, start_reg: int, length: int) -> bytes:
    # repeated-start safe read using i2c_msg
    write = i2c_msg.write(addr, [start_reg & 0xFF])
    read = i2c_msg.read(addr, length)
    bus.i2c_rdwr(write, read)
    return bytes(list(read))

def main():
    with SMBus(I2C_BUS) as bus:
        print(f"[OK] Opened I2C bus {I2C_BUS}, device 0x{DEV_ADDR:02X}")

        # Example: try reading "WHO_AM_I" style register often used by sensors
        # Replace 0x75 with your sensor's ID register.
        try:
            who = i2c_read_reg(bus, DEV_ADDR, 0x75)
            print(f"Reg 0x75 = 0x{who:02X}")
        except OSError as e:
            print(f"[ERR] I2C read failed: {e}")
            return

        # Example: read 6 bytes from some data block (replace reg)
        try:
            data = i2c_read_bytes(bus, DEV_ADDR, 0x3B, 6)
            print("Data bytes:", data.hex(" "))
        except OSError as e:
            print(f"[ERR] Block read failed: {e}")

if __name__ == "__main__":
    main()
'''
✅ SPI Sample Program (spidev)
Example B: SPI loopback test (best first test)

Wire MOSI to MISO physically for loopback:

MOSI (GPIO10, pin 19) → MISO (GPIO9, pin 21)

GND shared

spi_loopback.py'''
import spidev
import time

SPI_BUS = 0
SPI_DEV = 0       # /dev/spidev0.0
HZ = 1_000_000     # 1 MHz

def main():
    spi = spidev.SpiDev()
    spi.open(SPI_BUS, SPI_DEV)
    spi.max_speed_hz = HZ
    spi.mode = 0b00

    print(f"[OK] Opened SPI /dev/spidev{SPI_BUS}.{SPI_DEV} @ {HZ} Hz, mode {spi.mode}")

    try:
        for i in range(10):
            tx = [0xAA, 0x55, i & 0xFF, 0x00, 0xFF]
            rx = spi.xfer2(tx)   # full-duplex transfer
            print(f"TX: {tx}  RX: {rx}")
            time.sleep(0.5)
    finally:
        spi.close()

if __name__ == "__main__":
    main()


'''If loopback is correct, RX should equal TX.

✅ Combined “Embedded Python Stack” Example

LED blink + UART + I2C scan + SPI transfer in one script (good lab driver).

embedded_bus_demo.py'''
from gpiozero import LED
import serial
import time
from smbus2 import SMBus
import spidev

LED_GPIO = 17
UART_DEV = "/dev/serial0"
BAUD = 115200

I2C_BUS = 1
SPI_BUS, SPI_DEV = 0, 0

def i2c_scan(busno: int):
    found = []
    with SMBus(busno) as bus:
        for addr in range(0x03, 0x78):
            try:
                bus.write_quick(addr)
                found.append(addr)
            except OSError:
                pass
    return found

def spi_demo():
    spi = spidev.SpiDev()
    spi.open(SPI_BUS, SPI_DEV)
    spi.max_speed_hz = 1_000_000
    spi.mode = 0
    tx = [0x9F, 0x00, 0x00, 0x00]  # common "read ID" command for SPI flash (works only if you have one connected)
    rx = spi.xfer2(tx)
    spi.close()
    return tx, rx

def main():
    led = LED(LED_GPIO)

    ser = serial.Serial(UART_DEV, BAUD, timeout=0.1, write_timeout=1.0)
    print("[OK] UART opened")

    # I2C scan
    devs = i2c_scan(I2C_BUS)
    msg = "I2C devices: " + (" ".join([f"0x{x:02X}" for x in devs]) if devs else "NONE")
    print(msg)
    ser.write((msg + "\r\n").encode())

    # SPI demo (may return garbage if no SPI target connected)
    tx, rx = spi_demo()
    msg = f"SPI TX={tx} RX={rx}"
    print(msg)
    ser.write((msg + "\r\n").encode())

    # Blink + UART message
    try:
        state = False
        while True:
            state = not state
            led.value = 1 if state else 0
            ser.write((f"LED={'ON' if state else 'OFF'}\r\n").encode())

            r = ser.read(128)
            if r:
                print("[RX]", r.decode(errors="replace").rstrip())

            time.sleep(0.5)

    except KeyboardInterrupt:
        pass
    finally:
        led.off()
        ser.close()

if __name__ == "__main__":
    main()

'''🔥 Practice Use-Cases (hands-on assignments)
I2C practice (progressive)

Bus scanner

Scan bus 1 and print addresses

Add --json output option (address list)

Register read/write CLI tool

read <addr> <reg>

write <addr> <reg> <val>

Add retries + error decode

Sensor bring-up

Pick a common module:

BMP280/BME280 (0x76/0x77)

MPU6050 (0x68)

SSD1306 OLED (0x3C)

Tasks:

read chip-ID register

configure mode

read data and print

I2C logging daemon

poll sensor every 1s

log to CSV + rotate daily

SPI practice (progressive)

SPI loopback test

verify xfer2 full-duplex correctness

print pass/fail

SPI “protocol framing”

implement frame: [SOF=0xA5][LEN][PAYLOAD][CRC8]

send frame over SPI and validate loopback CRC

SPI device ID read

if using SPI flash (W25Qxx):

send 0x9F and parse manufacturer/device ID

if using MCP3008 ADC:

read channel values and print

Performance test

send 4KB blocks 1000 times

measure throughput (bytes/sec) + jitter

Combined use-cases (real embedded feel)

UART command console

commands:

I2C_SCAN

I2C_READ addr reg

SPI_XFER bytes...

LED ON/OFF/BLINK ms

respond with structured text

Fault-injection

unplug sensor / wrong address

program must:

retry

report error

keep running'''