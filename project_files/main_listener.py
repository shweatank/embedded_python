import serial
import subprocess
import time
import os
import signal
import sys

# --- CONFIGURATION ---
# Check your Pi's UART pins. Pi 3/4 usually use /dev/serial0
SERIAL_PORT = '/dev/serial0' 
BAUD_RATE = 115200

# Store the currently running process ID
current_process = None

def log_to_uart(message):
    """Sends a log message to the PC."""
    try:
        full_msg = f"LOG:{message}\n"
        ser.write(full_msg.encode('utf-8'))
        print(f"Sent: {message}")
    except Exception as e:
        print(f"UART Error: {e}")

def kill_current_process():
    """Stops the active micro-app."""
    global current_process
    if current_process:
        log_to_uart(f"Stopping active script (PID {current_process.pid})...")
        try:
            # Send SIGTERM to the entire process group
            os.killpg(os.getpgid(current_process.pid), signal.SIGTERM)
            current_process.wait(timeout=1) # Wait for it to die
        except Exception as e:
            log_to_uart(f"Error killing process: {e}")
        current_process = None

def run_script(script_name, args=[]):
    """Launches a new micro-app."""
    kill_current_process() # Ensure hardware is free
    
    cmd = ['python3', script_name] + args
    try:
        # start_new_session=True creates a new process group (crucial for clean kills)
        global current_process
        current_process = subprocess.Popen(
            cmd, 
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE, 
            preexec_fn=os.setsid,
            universal_newlines=True,
            bufsize=1  # Line buffered
        )
        log_to_uart(f"Started {script_name} with args {args}")
    except FileNotFoundError:
        log_to_uart(f"Error: Could not find {script_name}")

# --- MAIN LOOP ---
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
    print(f"Listening on {SERIAL_PORT}...")
    log_to_uart("Pi System Ready")

    while True:
        # 1. READ INCOMING COMMANDS
        if ser.in_waiting > 0:
            try:
                line = ser.readline().decode('utf-8').strip()
                if not line: continue
                
                parts = line.split(':')
                # Expected format: CMD:TYPE:ACTION:ARGS
                if len(parts) >= 3 and parts[0] == 'CMD':
                    module = parts[1]
                    action = parts[2]
                    
                    if module == 'GPIO':
                        if action == 'BLINK':
                            run_script('gpio_blink.py', [parts[3]])
                        elif action == 'ON':
                            run_script('gpio_blink.py', ['0']) # 0 delay = ON
                        elif action == 'OFF':
                            kill_current_process()
                            log_to_uart("GPIO Turned OFF")

                    elif module == 'PWM':
                        if action == 'START':
                            run_script('pwm_monitor.py') # Default args inside script
                        elif action == 'STOP':
                            kill_current_process()
                            log_to_uart("PWM Stopped")
                    
                    elif module == 'I2C':
                        if action == 'TIMER':
                            run_script('i2c_timer.py', [parts[3]])
                        elif action == 'CLOCK':
                            run_script('i2c_world_clock.py')

                    elif module == 'SPI':
                        # SPI is non-blocking (runs and finishes), so we wait for it
                        p3 = parts[3] if len(parts) > 3 else ""
                        p4 = parts[4] if len(parts) > 4 else ""
                        subprocess.run(['python3', 'spi_sd_card.py', action, p3, p4])
                        # The SPI script itself prints to stdout, which we capture below? 
                        # Actually, for non-blocking subprocess.run, we can't capture stdout easily in the loop below.
                        # Let's trust the SPI script to print, and we capture it via a Pipe if needed, 
                        # or just let it print to system console. 
                        # For better logs, we should read the output here:
                        result = subprocess.run(['python3', 'spi_sd_card.py', action, p3, p4], capture_output=True, text=True)
                        if result.stdout: log_to_uart(result.stdout.strip())
                        if result.stderr: log_to_uart(f"Error: {result.stderr.strip()}")

            except UnicodeDecodeError:
                pass # Ignore noise

        # 2. READ OUTPUT FROM RUNNING SCRIPT (LOGS)
        if current_process:
            # Non-blocking read of the sub-process output
            output = current_process.stdout.readline()
            if output:
                log_to_uart(f"[{current_process.args[1]}] {output.strip()}")
            
            # Check if process died
            if current_process.poll() is not None:
                current_process = None
                log_to_uart("Task finished.")

        time.sleep(0.05)

except KeyboardInterrupt:
    kill_current_process()
    print("Shutting down.")
