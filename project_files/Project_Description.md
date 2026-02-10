# 🎛️ Micro-SCADA System: Web-to-Hardware Control via UART

**A robust, modular Supervisory Control and Data Acquisition (SCADA) system implementation that bridges a high-level Web Dashboard (Flask) with low-level Hardware Controllers (Raspberry Pi) using a physical UART Serial connection.**

---

## 📖 Project Abstract

This project demonstrates a full-stack IoT architecture where a central server (Master) controls remote hardware (Slave) without internet dependency, using a dedicated serial communication line.

* **The Master (PC):** Runs a Flask Web Server that provides a GUI for the user. It translates button clicks into serial command packets.
* **The Bridge:** A USB-to-TTL Serial connection transmits data between the PC and the Pi.
* **The Slave (Raspberry Pi):** Runs a custom "Kernel Listener" script that parses incoming commands and dynamically spawns/kills independent Python processes to control specific hardware modules (GPIO, PWM, I2C, SPI).

---

## 🏗️ System Architecture

### Data Flow Diagram

```mermaid
[User Interface] -> (HTTP/WebSocket) -> [Flask Server (PC)] 
                                              |
                                       (Serial/UART Packets)
                                              |
                                              v
                                     [USB-to-TTL Adapter]
                                              |
                                       (Physical Wires)
                                              |
                                              v
                                     [Raspberry Pi UART]
                                              |
                                     [Main Listener Script]
                                              |
                            +-----------------+------------------+
                            |                 |                  |
                       [GPIO Proc]       [I2C Proc]         [SPI Proc]
                            |                 |                  |
                       (Hardware)        (Hardware)         (Hardware)

```

---

## 🔌 Hardware Requirements & Wiring

### 1. Components

* **Master:** PC/Laptop (Windows, Linux, or Mac) with Python installed.
* **Slave:** Raspberry Pi (3B, 4, 5, or Zero W).
* **Bridge:** USB-to-TTL Serial Adapter (FTDI or CP2102).
* **Modules:**
* LEDs (x2) & Resistors (220Ω).
* TM1637 4-Digit 7-Segment Display.
* SD Card Module (SPI Interface) [Optional].



### 2. Pinout Configuration

#### **A. UART Bridge (PC to Pi)**

| USB Adapter Pin | Raspberry Pi Pin | Description |
| --- | --- | --- |
| **TX** | **Pin 10 (GPIO 15 - RX)** | PC sends, Pi receives. |
| **RX** | **Pin 8 (GPIO 14 - TX)** | Pi sends logs, PC receives. |
| **GND** | **Pin 6 (GND)** | Common Ground reference. |
| *VCC* | *DO NOT CONNECT* | Pi should be powered via its own USB-C. |

#### **B. Peripheral Connections**

| Module | Component Pin | Raspberry Pi Pin |
| --- | --- | --- |
| **GPIO LED** | Anode (+) | **GPIO 17** (Pin 11) |
| **PWM LED** | Anode (+) | **GPIO 18** (Pin 12) |
| **TM1637** | CLK | **GPIO 5** (Pin 29) |
| **TM1637** | DIO | **GPIO 4** (Pin 7) |
| **SD Card** | MOSI | **GPIO 10** (Pin 19) |
| **SD Card** | MISO | **GPIO 9** (Pin 21) |
| **SD Card** | SCLK | **GPIO 11** (Pin 23) |
| **SD Card** | CS | **GPIO 8** (Pin 24) |

---

## 🛠️ Software Installation

### Phase 1: Raspberry Pi Setup (Slave)

1. **Enable Serial Interface:**
* Run `sudo raspi-config`
* Go to **Interface Options** -> **Serial Port**.
* **Login Shell:** NO | **Hardware Enabled:** YES.
* Reboot: `sudo reboot`.


2. **Enable SPI (If using SD Card):**
* `sudo raspi-config` -> **Interface Options** -> **SPI** -> **Yes**.


3. **Project Directory:**
```bash
mkdir ~/scada_project
cd ~/scada_project

```


4. **Install Dependencies:**
```bash
sudo apt update
sudo apt install python3-rpi.gpio python3-pip
pip3 install spidev

```


*(Note: Ensure you have `tm1637.py` driver file in this folder).*

### Phase 2: PC Setup (Master)

1. **Install Python Dependencies:**
```bash
pip install flask flask-socketio pyserial

```


2. **Determine COM Port:**
* **Windows:** Check Device Manager -> Ports (COM & LPT) -> e.g., `COM3`.
* **Linux/Mac:** Run `ls /dev/tty*` -> e.g., `/dev/ttyUSB0`.


3. **Configure App:**
* Open `app.py`.
* Edit line 12: `SERIAL_PORT = '/dev/ttyUSB0'` (Replace with your actual port).



---

## 🚀 Execution Guide

### Step 1: Start the Slave (Pi)

On the Raspberry Pi terminal:

```bash
cd ~/scada_project
python3 main_listener.py

```

*Output:* `Listening on /dev/serial0...`

### Step 2: Start the Master (PC)

On the PC terminal:

```bash
python app.py

```

*Output:* `Running on http://127.0.0.1:5000`

### Step 3: Control

Open your web browser and navigate to:
**`http://localhost:5000`**

---

## 📂 Project Structure

```text
Micro-SCADA/
├── Master_PC/
│   └── app.py                # FLASK SERVER: Web UI + UART Sender
│
└── Slave_Pi/
    ├── main_listener.py      # KERNEL: Manages UART & Subprocesses
    ├── gpio_blink.py         # WORKER: Handles LED On/Off/Blink
    ├── pwm_monitor.py        # WORKER: Handles Breathing LED (Speed Control)
    ├── i2c_timer.py          # WORKER: TM1637 Countdown Timer
    ├── i2c_world_clock.py    # WORKER: TM1637 Real-time Clock
    ├── spi_sd_card.py        # WORKER: SD Card File I/O
    └── tm1637.py             # DRIVER: Library for 7-Segment Display

```

---

## 📡 Communication Protocol

The system uses a custom text-based protocol.

### 1. Commands (PC -> Pi)

Format: `CMD:<MODULE>:<ACTION>:<ARGS>`

| Module | Command Example | Description |
| --- | --- | --- |
| **GPIO** | `CMD:GPIO:ON` | Turn LED on (Static). |
| **GPIO** | `CMD:GPIO:BLINK:0.5` | Blink LED every 0.5 seconds. |
| **PWM** | `CMD:PWM:START:0.05` | Start Breathing LED (Speed 0.05). |
| **I2C** | `CMD:I2C:CLOCK:START` | Display current system time. |
| **I2C** | `CMD:I2C:TIMER:01:30` | Start 1 min 30 sec countdown. |
| **SPI** | `CMD:SPI:CREATE:log.txt` | Create a file named log.txt. |

### 2. Logs (Pi -> PC)

Format: `LOG:<MESSAGE>`

* **Example:** `LOG:Timer Finished!`
* **Example:** `LOG:Breathing Cycle Complete`

---

## ⚠️ Troubleshooting

**1. "Serial Exception: Access Denied" on PC**

* Another program (Arduino IDE, Cura, PuTTY) is using the COM port. Close them.
* Unplug and replug the USB adapter.

**2. No Response from Pi (Dashboard logs empty)**

* **Check Wiring:** Is TX connected to RX? (They must cross over).
* **Check Baud Rate:** Ensure both `app.py` and `main_listener.py` use `115200`.

**3. "Permission Denied" on Pi**

* The user `pi` might not have dialout privileges.
* Fix: `sudo chmod 666 /dev/serial0`

**4. TM1637 Display Flickering**

* Ensure you are using the updated `i2c_world_clock.py` provided in the codebase, which combines digit and colon updates into a single transaction.

