import serial
import time

# Configure serial port
SERIAL_PORT = "/dev/serial0"  # Default UART on Raspberry Pi
BAUD_RATE = 115200   #Adjust if the sensor uses a different baud rate
print(f"     Baud: {BAUD_RATE}")
# Open the serial port
#ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
#ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=0)

ser = serial.Serial(
    port='/dev/ttyS0',      # Replace with your port name
    baudrate=BAUD_RATE,
    bytesize=serial.EIGHTBITS,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    timeout=1
)

def send_command(command):
    ser.write(command.encode('utf-8'))  # Convert to bytes and send

def read_response():
#    response = ser.readline().decode('utf-8').strip()  # Read and clean response
    response = ser.readline()  # Read and clean response
    return response

try:
    while True:
        # Send the command to measure distance (Replace 'M' with actual command)
        send_command('m')  # Change to correct command as per documentation
        
        # Read and display the response
        data = read_response()
        print(f"Distance: {data} meters")  # Modify parsing as needed
        
        print("loop")

except KeyboardInterrupt:
    print("Stopping...")
    ser.close()