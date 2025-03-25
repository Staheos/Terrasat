import serial
import time
import pynmea2

SERIAL_PORT = "/dev/ttyAMA0"
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

def parse_gps_data(data, file):
    """Parse NMEA sentence and extract GPS information."""
    try:
        msg = pynmea2.parse(data)
        if isinstance(msg, pynmea2.types.talker.GGA):
            file.write(f"\n--- GPS Data ---\n")
            file.write(f"Timestamp (UTC): {msg.timestamp}\n")
            file.write(f"Latitude: {msg.latitude} {msg.lat_dir}\n")
            file.write(f"Longitude: {msg.longitude} {msg.lon_dir}\n")
            file.write(f"Altitude: {msg.altitude} {msg.altitude_units}\n")
            file.write(f"Number of Satellites: {msg.num_sats}\n")
            file.write(f"Horizontal Dilution of Precision: {msg.horizontal_dil}\n")
            file.write(f"Geoid Separation: {msg.geo_sep} {msg.geo_sep_units}\n")
            file.write(f"----------------\n")
        elif isinstance(msg, pynmea2.types.talker.RMC):
            file.write(f"\n--- GPS Data ---\n")
            file.write(f"Timestamp (UTC): {msg.timestamp}\n")
            file.write(f"Status: {msg.status}\n")
            file.write(f"Latitude: {msg.latitude} {msg.lat_dir}\n")
            file.write(f"Longitude: {msg.longitude} {msg.lon_dir}\n")
            file.write(f"Speed Over Ground (knots): {msg.spd_over_grnd}\n")
            file.write(f"True Course: {msg.true_course}\n")
            file.write(f"Date: {msg.datestamp}\n")
            file.write(f"Magnetic Variation: {msg.mag_variation} {msg.mag_var_dir}\n")
            file.write(f"Mode Indicator: {msg.mode_indicator}\n")
            file.write(f"----------------\n")
    except pynmea2.ParseError as e:
        file.write(f"Failed to parse NMEA sentence: {e}\n")

def main():
    with serial.Serial(SERIAL_PORT, INITIAL_BAUD, timeout=1) as ser:
        time.sleep(2)
        send_command(ser, SET_BAUD_CMD)
        time.sleep(1)

    with serial.Serial(SERIAL_PORT, TARGET_BAUD, timeout=1) as ser:
        time.sleep(2)
        send_command(ser, SET_UPDATE_RATE_CMD)
        time.sleep(1)

        with open("gps_data.txt", "w") as file:
            while True:
                line = ser.readline().decode(errors="replace").strip()
                if line.startswith("$GNRMC") or line.startswith("$GPGGA"):
                    parse_gps_data(line, file)

if __name__ == "__main__":
    main()
