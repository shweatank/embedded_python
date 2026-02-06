from flask import Flask, render_template_string, request, jsonify
import serial
import time

app = Flask(__name__)

# --- CONFIGURATION ---
UART_PORT = '/dev/ttyUSB0'  # <--- CHANGE THIS
BAUD_RATE = 9600

# --- SERIAL CONNECTION ---
try:
    ser = serial.Serial(UART_PORT, BAUD_RATE, timeout=2)
    time.sleep(2) # Wait for connection to settle
    ser.reset_input_buffer()
    print(f"✅ Connected to {UART_PORT}")
except Exception as e:
    print(f"❌ Error connecting to UART: {e}")
    ser = None # Handle offline mode safely

# --- HTML TEMPLATE (Frontend) ---
# Keeping it inside the file for simplicity
HTML_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <title>UART LED Control</title>
    <style>
        body { font-family: sans-serif; text-align: center; padding: 50px; }
        .btn { padding: 20px 40px; font-size: 20px; margin: 10px; cursor: pointer; border: none; border-radius: 5px; color: white; }
        .on { background-color: #28a745; }
        .off { background-color: #dc3545; }
        #status { margin-top: 20px; font-weight: bold; font-size: 18px; color: #333; }
    </style>
</head>
<body>
    <h1>Raspberry Pi LED Controller</h1>
    
    <button class="btn on" onclick="sendCommand('LED_ON')">Turn ON</button>
    <button class="btn off" onclick="sendCommand('LED_OFF')">Turn OFF</button>
    
    <div id="status">Status: Ready</div>

    <script>
        function sendCommand(cmd) {
            document.getElementById('status').innerText = "Status: Sending...";
            
            // Send request to Flask backend
            fetch('/control', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({command: cmd})
            })
            .then(response => response.json())
            .then(data => {
                // Update text with response from Pi
                document.getElementById('status').innerText = "Status: " + data.reply;
            })
            .catch(error => {
                document.getElementById('status').innerText = "Status: Error communicating";
            });
        }
    </script>
</body>
</html>
"""

# --- ROUTES ---
@app.route('/')
def index():
    return render_template_string(HTML_PAGE)

@app.route('/control', methods=['POST'])
def control_led():
    if not ser:
        return jsonify({'reply': 'Error: UART not connected'})

    data = request.json
    command = data.get('command') # "LED_ON" or "LED_OFF"

    # 1. Send Command to Pi
    print(f"Sending to Pi: {command}")
    ser.write((command + "\n").encode('utf-8'))
    
    # 2. Wait for Reply from Pi
    # We strip whitespace so we get clean text like "LED is ON"
    response = ser.readline().decode('utf-8').strip()
    
    if not response:
        response = "No response from Pi"

    print(f"Reply from Pi: {response}")
    
    # 3. Send Reply to Frontend
    return jsonify({'reply': response})

if __name__ == '__main__':
    # Run server on localhost:5000
    app.run(debug=True, port=8001)