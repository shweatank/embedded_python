import sys
import os

# CONFIG: Where is the "SD Card"? 
# If real SPI card, use "/mnt/sdcard" or similar mount point.
SD_PATH = "sd_card_storage" 

if not os.path.exists(SD_PATH):
    os.makedirs(SD_PATH)

if len(sys.argv) < 2:
    print("Error: No action specified")
    sys.exit(1)

action = sys.argv[1] # CREATE, READ, WRITE, LIST

try:
    if action == "CREATE":
        fname = sys.argv[2]
        fpath = os.path.join(SD_PATH, fname)
        if os.path.exists(fpath):
            print(f"Error: {fname} already exists.")
        else:
            with open(fpath, 'w') as f:
                pass
            print(f"Success: Created {fname}")

    elif action == "WRITE":
        fname = sys.argv[2]
        data = sys.argv[3]
        fpath = os.path.join(SD_PATH, fname)
        with open(fpath, 'w') as f:
            f.write(data)
        print(f"Success: Wrote data to {fname}")

    elif action == "READ":
        fname = sys.argv[2]
        fpath = os.path.join(SD_PATH, fname)
        if os.path.exists(fpath):
            with open(fpath, 'r') as f:
                content = f.read()
            print(f"READ_DATA: {content}")
        else:
            print(f"Error: File {fname} not found")

    elif action == "LIST":
        files = os.listdir(SD_PATH)
        # Return as a simple comma-separated string for easier parsing
        print(f"FILE_LIST: {', '.join(files)}")

except Exception as e:
    print(f"SPI Error: {e}")
