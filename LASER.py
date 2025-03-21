import datetime
import serial
import time
import RPi.GPIO as GPIO
import socket
import Framer


client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect(('localhost', 1769))

data_in: bytearray = bytearray()

def decode_distance(data: bytes):
    distance = int.from_bytes(data[5:7]) / 10 # convert to meters
    return distance

def initialize_uart() -> serial.Serial:
    """Initialize the UART connection for the laser rangefinder module"""
    ser = serial.Serial(
        #port='/dev/serial0',  # Use '/dev/serial0' or '/dev/ttyS0' depending on your setup
        port='/dev/ttyUSB0',
        baudrate=115200,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=1
    )
    return ser

def enable_module():
    """Enable the laser rangefinder module using GPIO 26 (Pin 37)."""
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(26, GPIO.OUT)
    GPIO.output(26, GPIO.HIGH)

def disable_module():
    """Disable the laser rangefinder module using GPIO 26 (Pin 37)."""
    GPIO.output(26, GPIO.LOW)
    GPIO.cleanup()

def send_command(ser, command):
    """Send a command to the laser rangefinder module."""
    ser.write(command)
    # time.sleep(0.1)
    response = ser.read(ser.in_waiting)  # Read available data
    return response

def get_single_ranging(ser):
    """Send a command for single ranging measurement."""
    command = bytes([0x55, 0x01, 0x02, 0x20, 0x00, 0x76])  # Single ranging command
    response = send_command(ser, command)
    return response

def start_continuous_ranging(ser):
    """Send a command for continuous ranging measurement."""
    command = bytes([0x55, 0x02, 0x02, 0x20, 0x00, 0x75])  # Continuous ranging command
    response = send_command(ser, command)
    return response

def stop_continuous_ranging(ser):
    """Stop continuous ranging measurement."""
    command = bytes([0x55, 0x00, 0x02, 0x00, 0x00, 0x57])  # Stop ranging command
    response = send_command(ser, command)
    return response

enable_module()
ser = initialize_uart()

try:
    if ser.is_open:
        print("UART connection established with laser rangefinder module.")
        start_continuous_ranging(ser)

        while True:
            serial_waiting = ser.in_waiting
            if serial_waiting > 0:
                data_in.extend(ser.read(serial_waiting))

            if len(data_in) >= 14:
                packet = data_in[0:14]
                data_in = data_in[14:]
                print(packet.hex())
                print(decode_distance(packet))
                timestamp = int(time.time() * 1000)
                message = "LASER:" + str(decode_distance(packet)) + "&" + str(timestamp) + "&" + str(packet.hex())
                client_socket.sendall(("HEAD" + message + "FOOT").encode(encoding="utf-8", errors="strict"))


        # user_input = input("Enter command (single/continuous/stop/exit): ").lower()
        # if user_input == 'single' or user_input == '' or user_input.isnumeric():
        #     response = get_single_ranging(ser)
        # elif user_input == 'continuous':
        #     response = get_continuous_ranging(ser)
        # elif user_input == 'stop':
        #     response = stop_continuous_ranging(ser)
        # elif user_input == 'exit':
        #     break
        # else:
        #     print("Invalid command. Try again.")
        #     continue

        # print("Received:", response.hex())
        # print("Distance:", decode_distance(response))
        #client_socket.sendall(str(decode_distance(response)).encode("utf-8", errors="strict"))
        # open("measurements.txt", "a").write(f"{user_input}: [{datetime.datetime.now().strftime('%Y-%m-%d_%H:%M:%S')}]  {(decode_distance(response))}\n")

        ser.close()
        disable_module()
    else:
        print("Failed to open UART connection.")
        disable_module()
except KeyboardInterrupt:
    stop_continuous_ranging(ser)
    disable_module()
    ser.close()
    print("Exiting...")

