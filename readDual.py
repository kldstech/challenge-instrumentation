import threading
import subprocess
import sys

# Default recording duration in seconds
RECORD_SECONDS = 5


# Function to execute a Python script with a specified argument using subprocess.
def execute_script(script_name, duration, serial_port):
    try:
        command = ["python3", script_name, str(duration), serial_port]
        subprocess.run(command, check=True)

    except subprocess.CalledProcessError as e:
        print(f"Error running the script {script_name}: {e}")
        exit(1)


if __name__ == "__main__":
    # Set the default recording duration
    record_duration = RECORD_SECONDS

    # Check if the user specified a custom recording duration as a command-line argument
    if len(sys.argv) > 1:
        record_duration = sys.argv[1]

    # Names of the Python scripts to execute
    script1_name = "readStream.py"
    script2_name = "readStream.py"

    # Create two threads, one for each script
    thread1 = threading.Thread(target=execute_script, args=(script1_name, record_duration, "/dev/ttyUSB0"))
    thread2 = threading.Thread(target=execute_script, args=(script2_name, record_duration, "/dev/ttyUSB1"))

    # Start the threads to run the scripts concurrently
    thread1.start()
    thread2.start()

    # Wait for both threads to finish before continuing
    thread1.join()
    thread2.join()
