import datetime
import serial
import time
import RPi.GPIO as GPIO

def decode_distance(data: bytes):
    distance = int.from_bytes(data[5:7]) / 10 # convert to meters
    return distance

def initialize_uart():
    """Initialize the UART connection for the laser rangefinder module"""
    ser = serial.Serial(
        port='/dev/serial0',  # Use '/dev/serial0' or '/dev/ttyS0' depending on your setup
        baudrate=115200,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=1
    )
    return ser

def enable_module():
    """Enable the laser rangefinder module using GPIO 23 (Pin 16)."""
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(23, GPIO.OUT)
    GPIO.output(23, GPIO.HIGH)

def disable_module():
    """Disable the laser rangefinder module using GPIO 23 (Pin 16)."""
    GPIO.output(23, GPIO.LOW)
    GPIO.cleanup()

def send_command(ser, command):
    """Send a command to the laser rangefinder module."""
    ser.write(command)
    time.sleep(0.5)
    response = ser.read(ser.in_waiting)  # Read available data
    return response

def get_single_ranging(ser):
    """Send a command for single ranging measurement."""
    command = bytes([0x55, 0x01, 0x02, 0x20, 0x00, 0x76])  # Single ranging command
    response = send_command(ser, command)
    return response

def get_continuous_ranging(ser):
    """Send a command for continuous ranging measurement."""
    command = bytes([0x55, 0x02, 0x02, 0x20, 0x00, 0x75])  # Continuous ranging command
    response = send_command(ser, command)
    return response

def main():
    enable_module()
    ser = initialize_uart()
    if ser.is_open:
        print("UART connection established with laser rangefinder module.")

        while True:
            user_input = input("Enter command (single/continuous/stop/exit): ").lower()
            if user_input == 'single' or user_input == '' or user_input.isnumeric():
                response = get_single_ranging(ser)
            elif user_input == 'continuous':
                response = get_continuous_ranging(ser)
            elif user_input == 'stop':
                response = stop_continuous_ranging(ser)
            elif user_input == 'exit':
                break
            else:
                print("Invalid command. Try again.")
                continue

            print("Received:", response.hex())
            print("Distance:", decode_distance(response))
            open("measurements.txt", "a").write(f"{user_input}: [{datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')}]  {(decode_distance(response))}\n")

        ser.close()
        disable_module()
    else:
        print("Failed to open UART connection.")
        disable_module()

if __name__ == "__main__":
    main()

def stop_continuous_ranging(ser):
    """Stop continuous ranging measurement."""
    command = bytes([0x55, 0x00, 0x02, 0x00, 0x00, 0x57])  # Stop command
    response = send_command(ser, command)
    return response
