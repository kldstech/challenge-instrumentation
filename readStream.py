import serial
import time
import csv
import sys
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt

SERIAL_PORT = '/dev/ttyUSB0'    # Serial port to connect to the sensor
SCALE_FACTOR = 16/32768         # Scale factor to convert raw data to acceleration values (g)
RECORD_SECONDS = 5              # Default recording duration in seconds
RATE = 16000                    # Data rate of the sensor in samples per second

# User-specified recording duration (can be passed as a command-line argument)
record_duration = RECORD_SECONDS

# User-specified serial port (can be passed as a command-line argument)
serial_port = SERIAL_PORT


# Function to plot the data from a CSV file
def plotCSV(filename):
    t = []
    ax = []
    ay = []
    az = []

    # Read the data from the CSV file
    with open(filename, 'r') as file:
        reader = csv.reader(file)
        next(reader)  # bypass header

        for row in reader:
            t.append(float(row[0]))
            ax.append(float(row[1]))
            ay.append(float(row[2]))
            az.append(float(row[3]))

    # Plot the data using Matplotlib
    plt.plot(t, ax, label='Ax')
    plt.plot(t, ay, label='Ay')
    plt.plot(t, az, label='Az')

    plt.xlabel('Time (s)')
    plt.ylabel('Acceleration (g)')
    plt.title(filename)
    plt.legend()

    plt.show()
    

# Function to read data from the serial port and save it to a CSV file
def read_serial_data(ser, filename):
    data_buffer = []
    buffer_1s = []
    counter = 0
    t = 0
    lost = 0
    start_time = time.time()
    elapsed_time_count = 0

    # Open the CSV file for writing
    with open(filename, 'w', newline='') as csv_file:
        writer = csv.writer(csv_file)

        # Write the header row to the CSV file
        data_buffer = ["t", "ax", "ay", "az"]
        writer.writerow(data_buffer)
        data_buffer = []

        try:
            while True:
                byte = ser.read(1)

                # Frame format: S xx yy zz
                if byte == b'\x53':
                    counter += 1
                    lost = 0
                    data_buffer.append(t/RATE)
                    t += 1

                    for n in range(3):
                        data = ser.read(2)
                        value = int.from_bytes(data, byteorder='little', signed=True)
                        data_buffer.append(value * SCALE_FACTOR)

                    # Write the data to the CSV file
                    writer.writerow(data_buffer)
                    buffer_1s.append(data_buffer)
                    data_buffer = []

                else:
                    lost += 1
                    print(lost)
                
                # Check if 1 second has elapsed
                elapsed_time = time.time() - start_time
                if elapsed_time >= 1.0:
                    print("{} sps".format(counter))
                    buffer_1s = []
                    counter = 0
                    start_time = time.time()

                    # Check if the user-specified recording duration is reached
                    elapsed_time_count += 1
                    if elapsed_time_count >= record_duration:
                        break

        except KeyboardInterrupt:
            print("Program interrupted by keyboard")

    print("Serial close")
    ser.close()


# Main function
def main():
    # Connect to the sensor via the specified serial port
    ser = serial.Serial(serial_port, baudrate=3000000)

    # Get the current date and time to create a unique filename for the CSV file
    current_datetime = datetime.now()
    timestamp = current_datetime.strftime("%Y%d%m_%H%M%S")
    filename = f"data/{serial_port.replace('/dev/tty', '')}_{timestamp}.csv"

    # Read data from the MEMS sensor and save it to the CSV file
    read_serial_data(ser, filename)

    # Plot the recorded data from the CSV file
    plotCSV(filename)


if __name__ == '__main__':
    # Check if the user specified a custom recording duration as a command-line argument
    if len(sys.argv) > 1:
        record_duration = int(sys.argv[1])

    # Custom serial port command-line argument
    if len(sys.argv) > 2:
        serial_port = sys.argv[2]

    # Call the main function to start the data recording and plotting process
    main()
