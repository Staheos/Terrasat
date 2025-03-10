import serial
import time

# UART Configuration (Based on Documentation)
SERIAL_PORT = "/dev/ttyS0" 
BAUD_RATE = 115200  # Baud rate as per documentation

# Initialize serial connection
ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)

def calculate_checksum(command):
    """Calculate XOR checksum for a given command packet."""
    checksum = 0
    for byte in command:
        checksum ^= byte  # XOR all bytes
    return checksum

def send_command(command):
    """Send a command to the rangefinder."""
    command.append(calculate_checksum(command))  # Append checksum
    ser.write(bytes(command))  # Send as byte array
    time.sleep(0.1)  # Short delay before reading response

def receive_response(expected_length):
    """Read response from the rangefinder."""
    response = ser.read(expected_length)
    print(f"read: {response}")
    if len(response) == expected_length and response[0] == 0x55:  # Check start byte
        return response
    else:
        print("Invalid or no response received.")
        return None

def get_distance():
    """Send single ranging command and read distance response."""
    # Command to initiate single ranging: 55 01 02 20 00 CHK
    command = [0x55, 0x01, 0x02, 0x20, 0x00]
    send_command(command)

    # Read 11-byte response for distance measurement
    response = receive_response(11)

    if response:
        distance = (response[5] << 16) | (response[4] << 8) | response[3]  # Combine D5-D3 (High to Low bytes)
        distance = distance / 10.0  # Convert to meters
        voltage = response[1]  # APD High Voltage
        temperature = response[0]  # APD Temperature
        print(f"Distance: {distance:.1f} m | APD Voltage: {voltage}V | Temperature: {temperature} C")
    else:
        print("Failed to read distance.")

try:
    print("Powering on the module...")
    
    time.sleep(1)  # Allow the module to initialize

    while True:
        get_distance()
        time.sleep(1)  # Delay between readings

except KeyboardInterrupt:
    print("Shutting down...")
    ser.close()
    print("Serial connection closed.")
