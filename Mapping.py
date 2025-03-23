import datetime
import serial
import time
import RPi.GPIO as GPIO
import socket
import Framer

import time
import board
import time
import datetime
import socket
import board
import math
import busio
from adafruit_bno08x.i2c import BNO08X_I2C
from adafruit_bno08x import (
    BNO_REPORT_ACCELEROMETER,
    BNO_REPORT_GYROSCOPE,
    BNO_REPORT_MAGNETOMETER,
    BNO_REPORT_ROTATION_VECTOR,
)

import numpy as np

def compute_3d_coordinates(distance, azimuth_deg, elevation_deg):
    """
    distance     = scalar distance measured along the laser's local forward axis
    azimuth_deg  = rotation around global Z (0-360 degrees typically)
    elevation_deg= tilt above/below horizontal (e.g. -90 to +90 degrees)
    returns (x, y, z) in global coordinates
    """
    az_rad = math.radians(azimuth_deg)
    el_rad = math.radians(elevation_deg)

    x = distance * math.cos(el_rad) * math.cos(az_rad)
    y = distance * math.cos(el_rad) * math.sin(az_rad)
    z = distance * math.sin(el_rad)
    return x, y, z

def quaternion_to_azimuth_elevation(w, x, y, z):
    """
    Convert a quaternion (w, x, y, z) into azimuth (yaw) and elevation (pitch).
    Rolls about the forward axis are ignored here.

    Returns: (azimuth_degrees, elevation_degrees)
    """
    # Normalize the quaternion just to be safe
    mag = math.sqrt(w*w + x*x + y*y + z*z)
    if mag < 1e-12:
        # Degenerate quaternion - return zeros or handle error
        return 0.0, 0.0
    w, x, y, z = w/mag, x/mag, y/mag, z/mag

    # Standard formula for yaw, pitch, roll (Tait-Bryan angles, Z-Y-X sequence):
    #   yaw   = atan2(2(qw qz + qx qy), 1 - 2(qy^2 + qz^2))
    #   pitch = asin( 2(qw qy - qz qx) )
    #   roll  = atan2(2(qw qx + qy qz), 1 - 2(qx^2 + qy^2))
    #
    # We'll define:
    #   azimuth   = yaw   (rotation around global Z)
    #   elevation = pitch (rotation around global Y, up/down)

    # Yaw (Z-axis rotation)
    yaw = math.atan2(2.0 * (w*z + x*y), 1.0 - 2.0 * (y*y + z*z))
    # Pitch (Y-axis rotation)
    pitch = math.asin(2.0 * (w*y - z*x))
    # Roll is ignored in this scenario.

    # Convert to degrees for convenience
    azimuth_deg = math.degrees(yaw)
    elevation_deg = math.degrees(pitch)

    # OPTIONAL: You might want to force azimuth into [0, 360) or [-180, 180], etc.
    # For example, to keep azimuth in [0, 360):
    if azimuth_deg < 0:
        azimuth_deg += 360.0

    return azimuth_deg, elevation_deg


def decode_distance(data: bytes):
    distance = int.from_bytes(data[5:7]) / 10 # convert to meters
    return distance

def initialize_uart() -> serial.Serial:
    """Initialize the UART connection for the laser rangefinder module"""
    new_serial = serial.Serial(
        #port='/dev/serial0',  # Use '/dev/serial0' or '/dev/ttyS0' depending on your setup
        port='/dev/ttyUSB0',
        baudrate=115200,
        bytesize=serial.EIGHTBITS,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        timeout=1
    )
    return new_serial

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


while True:
    try:
        i2c = busio.I2C(board.SCL, board.SDA, frequency=400000)

        bno = BNO08X_I2C(i2c)

        bno.enable_feature(BNO_REPORT_ACCELEROMETER)
        bno.enable_feature(BNO_REPORT_GYROSCOPE)

        bno.enable_feature(BNO_REPORT_MAGNETOMETER)
        bno.enable_feature(BNO_REPORT_ROTATION_VECTOR)

        print("BNO08X IMU Sensor Initialized!")
        print("Reading sensor data...\n")

        time.sleep(1)
        bno.begin_calibration()
        time.sleep(1)

        data_in: bytearray = bytearray()

        enable_module()
        ser = initialize_uart()
        date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

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

                    distance = decode_distance(packet)
                    print(distance)
                    timestamp = int(time.time() * 1000)

                    quat_real, quat_j, quat_i, quat_k = bno.quaternion
                    rotation_vector = f"ROTATION_VECTOR:{timestamp}&{quat_real:.6f}&{quat_i:.6f}&{quat_j:.6f}&{quat_k:.6f}"

                    azimuth, elevation = quaternion_to_azimuth_elevation(quat_real, quat_i, quat_j, quat_k)
                    x, z, y, = compute_3d_coordinates(distance, azimuth, elevation)

                    print(f"{x:.6f},{y:.6f},{z:.6f}")
                    open(f"mapping_{date}.txt", "a").write(f"{datetime.datetime.now().isoformat()}  {x:.6f},{y:.6f},{z:.6f}\n")
                    open(f"points_{date}.txt", "a").write(f"{x:.6f}\t{y:.6f}\t{z:.6f}\n")

        else:
            print("Failed to open UART connection.")
            disable_module()
            ser.close()
    except KeyboardInterrupt:
        stop_continuous_ranging(ser)
        disable_module()
        ser.close()
        print("Exiting...")
        break
    except Exception as e:
        print(f"Error: {e}")
        try:
            open("laser_errors.txt", "a").write(f"[{datetime.datetime.now()}]  {e}\n")
            if ser != None and ser.is_open:
                stop_continuous_ranging(ser)
            disable_module()
            # ser.close()
            time.sleep(3)
        except Exception as e2:
            print(f"Fatal: {e2}")