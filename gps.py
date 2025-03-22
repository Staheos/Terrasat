import serial
import time
import pynmea2

SERIAL_PORT = "/dev/serial0"
INITIAL_BAUD = 9600
TARGET_BAUD = 115200
UPDATE_RATE_HZ = 5

SET_BAUD_CMD = f"$PCAS01,5*19\r\n"
SET_UPDATE_RATE_CMD = "$PCAS02,200*1D\r\n"

def send_command(ser, command):
    """Send a command to the GPS module."""
    print(f"Sending command: {command.strip()}")
    ser.write(command.encode())
    time.sleep(0.5)

def parse_gps_data(data):
    """Parse NMEA sentence and extract GPS information."""
    try:
        msg = pynmea2.parse(data)
        if isinstance(msg, pynmea2.types.talker.GGA):
            print(f"\n--- GPS Data ---")
            print(f"Timestamp (UTC): {msg.timestamp}")
            print(f"Latitude: {msg.latitude} {msg.lat_dir}")
            print(f"Longitude: {msg.longitude} {msg.lon_dir}")
            print(f"Altitude: {msg.altitude} {msg.altitude_units}")
            print(f"Number of Satellites: {msg.num_sats}")
            print(f"Horizontal Dilution of Precision: {msg.horizontal_dil}")
            print(f"Geoid Separation: {msg.geo_sep} {msg.geo_sep_units}")
            print(f"----------------\n")
        elif isinstance(msg, pynmea2.types.talker.RMC):
            print(f"\n--- GPS Data ---")
            print(f"Timestamp (UTC): {msg.timestamp}")
            print(f"Status: {msg.status}")
            print(f"Latitude: {msg.latitude} {msg.lat_dir}")
            print(f"Longitude: {msg.longitude} {msg.lon_dir}")
            print(f"Speed Over Ground (knots): {msg.spd_over_grnd}")
            print(f"True Course: {msg.true_course}")
            print(f"Date: {msg.datestamp}")
            print(f"Magnetic Variation: {msg.mag_variation} {msg.mag_var_dir}")
            print(f"Mode Indicator: {msg.mode_indicator}")
            print(f"----------------\n")
    except pynmea2.ParseError as e:
        print(f"Failed to parse NMEA sentence: {e}")


with serial.Serial(SERIAL_PORT, INITIAL_BAUD, timeout=1) as ser:
    time.sleep(2)
    send_command(ser, SET_BAUD_CMD)
    time.sleep(1)

with serial.Serial(SERIAL_PORT, TARGET_BAUD, timeout=1) as ser:
    time.sleep(2)

    send_command(ser, SET_UPDATE_RATE_CMD)
    time.sleep(1)

    while True:
        line = ser.readline().decode(errors="replace").strip()
        if line.startswith("$GNRMC") or line.startswith("$GPGGA"):
            parse_gps_data(line)
