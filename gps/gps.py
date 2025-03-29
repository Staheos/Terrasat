import serial
import time
import pynmea2
import time
import datetime
import sys
import socket


def is_debug() -> bool:
    return len(sys.argv) >= 2 and sys.argv[1] == "-d"

def log(data: any) -> None:
    with open("gps_log.txt", "a") as f:
        f.write(str(data) + "\n")
    if is_debug():
        log(data)

def coord_to_int(coord: float) -> int:
    return int(coord * 10000000)

def send_command(ser, command):
    """Send a command to the GPS module."""
    log(f"Sending command: {command.strip()}")
    ser.write(command.encode())
    time.sleep(0.5)

def parse_gsv(line) -> str:
    ret = f"{line[0:8]}"
    try:
        parts = line.split(',')
        total_sats = int(parts[3])
        ret += f"\n🛰️ Total Satellites in View: {total_sats}"
        sats = []
        for i in range(4, len(parts) - 4, 4):
            prn = parts[i]
            elev = parts[i+1]
            az = parts[i+2]
            snr = parts[i+3].split('*')[0] if '*' in parts[i+3] else parts[i+3]
            if prn:
                sats.append((prn, elev, az, snr if snr else "N/A"))

        for s in sats:
            ret += f" - PRN: {s[0]} | Elevation: {s[1]}° | Azimuth: {s[2]}° | SNR: {s[3]} dBHz"
    except Exception as e:
        ret += f"⚠️ Failed to parse GSV: {e}"
    return ret


def parse_gps_data(data) -> any:
    """Parse NMEA sentence and extract GPS information."""
    try:
        msg = pynmea2.parse(data)
        if isinstance(msg, pynmea2.types.talker.GGA):
            log(f"\n--- GPS Data ---")
            log(f"Timestamp (UTC): {msg.timestamp}")
            log(f"Latitude: {msg.latitude} {msg.lat_dir}")
            log(f"Longitude: {msg.longitude} {msg.lon_dir}")
            log(f"Altitude: {msg.altitude} {msg.altitude_units}")
            log(f"Number of Satellites: {msg.num_sats}")
            log(f"Horizontal Dilution of Precision: {msg.horizontal_dil}")
            log(f"Geoid Separation: {msg.geo_sep} {msg.geo_sep_units}")
            log(f"----------------\n")
            return msg
        elif isinstance(msg, pynmea2.types.talker.RMC):
            log(f"\n--- GPS Data ---")
            log(f"Timestamp (UTC): {msg.timestamp}")
            log(f"Status: {msg.status}")
            log(f"Latitude: {msg.latitude} {msg.lat_dir}")
            log(f"Longitude: {msg.longitude} {msg.lon_dir}")
            log(f"Speed Over Ground (knots): {msg.spd_over_grnd}")
            log(f"True Course: {msg.true_course}")
            log(f"Date: {msg.datestamp}")
            log(f"Magnetic Variation: {msg.mag_variation} {msg.mag_var_dir}")
            log(f"Mode Indicator: {msg.mode_indicator}")
            log(f"----------------\n")
            return msg
    except pynmea2.ParseError as e:
        log(f"Failed to parse NMEA sentence: {e}")
    return None

while True:
    try:
        SERIAL_PORT = "/dev/serial0"
        INITIAL_BAUD = 9600
        TARGET_BAUD = 115200
        UPDATE_RATE_HZ = 5

        SET_BAUD_CMD = f"$PCAS01,5*19\r\n"
        SET_UPDATE_RATE_CMD = "$PCAS02,200*1D\r\n"
        ENABLE_GGA_CMD = "$PGKC115,0,1,0,1,0,0,0,0*2B\r\n"
        ENABLE_ALL = "$PGKC110,7*2F\r\n"

        SENDING_PERIOD = 10
        sending_count = 0

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('localhost', 1769))

        with serial.Serial(SERIAL_PORT, INITIAL_BAUD, timeout=1) as ser:
            time.sleep(2)
            send_command(ser, SET_BAUD_CMD)
            time.sleep(1)

        with serial.Serial(SERIAL_PORT, TARGET_BAUD, timeout=1) as ser:
            time.sleep(2)

            send_command(ser, SET_UPDATE_RATE_CMD)
            time.sleep(1)

            send_command(ser, ENABLE_GGA_CMD)
            time.sleep(1)

            send_command(ser, ENABLE_ALL)
            time.sleep(1)

            while True:
                message = ""
                to_send = False

                receiving_altitude = 0

                line = ser.readline().decode(errors="replace").strip()
                open("gps_serial.txt", "a").write(f"[{datetime.datetime.now()}]  {line}\n")

                if line.startswith("$GPGSV") or line.startswith("$GLGSV") or line.startswith("$BDGSV") or line.startswith("$GAGSV") or line.startswith("$GNGSV"):
                    open("gps_satellites.txt", "a").write(f"[{datetime.datetime.now()}]  {parse_gsv(line)}\n")
                elif line.startswith("$GNRMC") or line.startswith("$GPGGA") or line.startswith("$GNGGA"):
                    msg = parse_gps_data(line)
                    if msg == "" or msg is None or msg.latitude == 0 or msg.longitude == 0 or msg.latitude is None or msg.longitude is None:
                        continue
                    message = f"{coord_to_int(msg.latitude)}&{msg.lat_dir}&{coord_to_int(msg.longitude)}&{msg.lon_dir}"
                    if hasattr(msg, "altitude") and hasattr(msg, "altitude_units"):
                        message += f"&{coord_to_int(msg.altitude)}&{msg.altitude_units}"
                        receiving_altitude = 0
                        to_send = True
                    else:
                        receiving_altitude += 1
                        if receiving_altitude > 10:
                            to_send = True
                if message == "":
                    continue

                timestamp = int(time.time() * 1000)
                message = "GPS:" + str(timestamp) + "&" + message
                log(message)
                if to_send and sending_count == 0:
                    client_socket.sendall(("HEAD" + message + "FOOT").encode(encoding="utf-8", errors="strict"))
                sending_count = (sending_count + 1) % SENDING_PERIOD
                open("gps_data.txt", 'a').write(message + '\n')

    except KeyboardInterrupt:
        log("Exiting...")
        break
    except Exception as e:
        log(f"Error: {e}")
        try:
            open("gps_errors.txt", "a").write(f"[{datetime.datetime.now()}]  {e}\n")
            time.sleep(3)
        except Exception as e2:
            log(f"Fatal: {e2}")
