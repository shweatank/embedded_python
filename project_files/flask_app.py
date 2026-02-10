import serial
import threading
import time
from flask import Flask, render_template_string, request, jsonify
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app)

# --- CONFIGURATION ---
# CHANGE THIS to your USB-Serial port (e.g., 'COM3' on Windows, '/dev/ttyUSB0' on Linux)
SERIAL_PORT = 'COM3' 
BAUD_RATE = 115200

try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    print(f"✅ Connected to {SERIAL_PORT}")
except:
    print(f"❌ Could not connect to {SERIAL_PORT}. Running in simulation mode.")
    ser = None

# --- EMBEDDED FRONTEND (HTML/JS/CSS) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Micro-SCADA Controller</title>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/socket.io/4.0.1/socket.io.js"></script>
    <style>
        body { font-family: 'Courier New', monospace; background: #222; color: #0f0; padding: 20px; }
        .container { display: flex; flex-wrap: wrap; gap: 20px; }
        .card { border: 1px solid #0f0; padding: 15px; width: 300px; border-radius: 8px; background: #111; }
        h2 { border-bottom: 1px dashed #0f0; padding-bottom: 5px; margin-top: 0; }
        button { background: #0f0; color: #000; border: none; padding: 8px 15px; cursor: pointer; font-weight: bold; margin: 5px; }
        button:hover { background: #fff; }
        input[type="text"], input[type="number"] { background: #333; border: 1px solid #0f0; color: #fff; padding: 5px; width: 60%; }
        #logs { width: 100%; height: 200px; background: #000; border: 1px solid #0f0; overflow-y: scroll; padding: 10px; margin-top: 20px; white-space: pre-line; }
        .status { font-size: 0.8em; color: #888; }
    </style>
</head>
<body>
    <h1>📟 Micro-SCADA Dashboard</h1>
    
    <div class="container">
        <div class="card">
            <h2>GPIO: LED Control</h2>
            <button onclick="sendCommand('CMD:GPIO:ON')">Turn ON</button>
            <button onclick="sendCommand('CMD:GPIO:OFF')">Turn OFF</button>
            <br><br>
            <label>Blink Speed (sec):</label>
            <input type="number" id="blinkSpeed" value="1.0" step="0.1">
            <button onclick="sendCommand('CMD:GPIO:BLINK:' + document.getElementById('blinkSpeed').value)">Set Blink</button>
        </div>

        <div class="card">
            <h2>PWM: Breathing LED</h2>
            <label>Cycle Duration (sec):</label>
            <button onclick="sendCommand('CMD:PWM:FASTER')">Wait -</button>
            <button onclick="sendCommand('CMD:PWM:SLOWER')">Wait +</button>
            <br><br>
            <button onclick="sendCommand('CMD:PWM:START')">Start Breathing</button>
            <button onclick="sendCommand('CMD:PWM:STOP')">Stop</button>
        </div>

        <div class="card">
            <h2>I2C: TM1637 Display</h2>
            <button onclick="sendCommand('CMD:I2C:CLOCK:START')">Show World Clock</button>
            <hr>
            <label>Timer (MM:SS):</label><br>
            <input type="text" id="timerInput" placeholder="05:00">
            <button onclick="sendCommand('CMD:I2C:TIMER:' + document.getElementById('timerInput').value)">Start Timer</button>
        </div>

        <div class="card">
            <h2>SPI: SD Card</h2>
            <input type="text" id="fileName" placeholder="filename.txt">
            <button onclick="sendCommand('CMD:SPI:CREATE:' + document.getElementById('fileName').value)">Create File</button>
            <br>
            <input type="text" id="fileData" placeholder="Data to write...">
            <button onclick="sendCommand('CMD:SPI:WRITE:' + document.getElementById('fileName').value + ':' + document.getElementById('fileData').value)">Write Data</button>
            <br>
            <button onclick="sendCommand('CMD:SPI:READ:' + document.getElementById('fileName').value)">Read File</button>
            <button onclick="sendCommand('CMD:SPI:LIST')">List All Files</button>
        </div>
    </div>

    <h3>📡 System Logs (Real-time UART)</h3>
    <div id="logs">Waiting for system logs...</div>

    <script>
        var socket = io();

        // Send Command to Flask
        function sendCommand(cmd) {
            fetch('/send_command', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({command: cmd})
            });
            addLog(">> SENT: " + cmd);
        }

        // Receive Log from Flask
        socket.on('new_log', function(msg) {
            addLog("<< RECV: " + msg.data);
        });

        function addLog(text) {
            var logDiv = document.getElementById("logs");
            logDiv.innerHTML += "<div>" + text + "</div>";
            logDiv.scrollTop = logDiv.scrollHeight;
        }
    </script>
</body>
</html>
"""

# --- BACKEND ROUTES ---
@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/send_command', methods=['POST'])
def send_command():
    data = request.json
    cmd = data.get('command')
    if ser and ser.is_open:
        ser.write((cmd + '\n').encode('utf-8'))
        return jsonify({"status": "sent", "cmd": cmd})
    return jsonify({"status": "error", "msg": "Serial not connected"})

# --- SERIAL LISTENER THREAD ---
def read_from_serial():
    while True:
        if ser and ser.is_open:
            if ser.in_waiting > 0:
                try:
                    line = ser.readline().decode('utf-8').strip()
                    if line:
                        print(f"UART Received: {line}")
                        socketio.emit('new_log', {'data': line})
                except Exception as e:
                    print(f"Serial Error: {e}")
        time.sleep(0.1)

if __name__ == '__main__':
    # Start serial reading in background
    t = threading.Thread(target=read_from_serial)
    t.daemon = True
    t.start()
    
    socketio.run(app, debug=True, port=5000)
