import serial
import time

def open_serial_connection(port='COM3', baudrate=9600, timeout=1):
    """Opens a serial connection."""
    try:
        ser = serial.Serial(port, baudrate, timeout=timeout)
        print(f"Connected to {port} at {baudrate} baud.")
        return ser
    except serial.SerialException as e:
        print(f"Error opening serial port: {e}")
        return None

def send_message(ser, message):
    """Sends a message over the serial connection."""
    if ser and ser.is_open:
        ser.write(message.encode('utf-8'))
        print(f"Sent: {message}")

def receive_message(ser):
    """Receives a message from the serial connection."""
    if ser and ser.is_open:
        try:
            data = ser.readline().decode('utf-8').strip()
            if data:
                print(f"Received: {data}")
            return data
        except Exception as e:
            print(f"Error reading from serial: {e}")
            return None

def main():
    port = "/dev/ttyUSB0"
    baudrate = 9600

    ser = open_serial_connection(port, baudrate)

    if ser:
        try:
            while True:
                msg = input("Enter message to send (or 'exit' to quit): ")
                if msg.lower() == 'exit':
                    break
                send_message(ser, msg)
                time.sleep(1)  # Delay to allow response
                receive_message(ser)
        finally:
            ser.close()
            print("Serial connection closed.")

if __name__ == "__main__":
    main()
