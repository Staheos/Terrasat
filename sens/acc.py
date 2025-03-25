import time
import board
import time
import datetime
import socket
import board
import math
import adafruit_bmp280
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

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('localhost', 1769))

        acceleration_time = 100
        gyroscope_time = 100
        magnetometer_time = 1000
        rotation_vector_time = 1

        acceleration_count = 0
        gyroscope_count = 0
        magnetometer_count = 0
        rotation_vector_count = 0

        time.sleep(1)
        bno.begin_calibration()
        time.sleep(1)

        while True:
            timestamp = int(time.time() * 1000)
            accel_x, accel_y, accel_z = bno.acceleration
            acceleration = f"ACCELERATION:{timestamp}&{accel_x:.6f}&{accel_y:.6f}&{accel_z:.6f}"

            timestamp = int(time.time() * 1000)
            gyro_x, gyro_y, gyro_z = bno.gyro
            gyroscope = f"GYROSCOPE:{timestamp}&{gyro_x:.6f}&{gyro_y:.6f}&{gyro_z:.6f}"

            timestamp = int(time.time() * 1000)
            mag_x, mag_y, mag_z = bno.magnetic
            magnetometer = f"MAGNETOMETER:{timestamp}&{mag_x:.6f}&{mag_y:.6f}&{mag_z:.6f}"

            timestamp = int(time.time() * 1000)
            # quat_real, quat_i, quat_j, quat_k = bno.quaternion
            quat_real, quat_j, quat_i, quat_k = bno.quaternion
            rotation_vector = f"ROTATION_VECTOR:{timestamp}&{quat_real:.6f}&{quat_i:.6f}&{quat_j:.6f}&{quat_k:.6f}"

            # roll, pitch, yaw = quaternion_to_euler(quat_i, quat_j, quat_k, quat_real)
            distance = 1

            # x = distance * math.sin(pitch) * math.cos(roll)
            # y = distance * math.cos(pitch) * math.cos(roll)
            # z = distance * math.sin(roll) #* math.cos(pitch)

            azimuth, elevation = quaternion_to_azimuth_elevation(quat_real, quat_i, quat_j, quat_k)
            x, z, y, = compute_3d_coordinates(distance, azimuth, elevation)

            # print(f"{datetime.datetime.now().isoformat()}  {(quat_real, quat_i, quat_j, quat_k)}")
            print(f"{datetime.datetime.now().isoformat()}  {x:.6f},{y:.6f},{z:.6f}")
            open("imu_data.txt", "a").write(f"{datetime.datetime.now().isoformat()}  {x:.6f},{y:.6f},{z:.6f}\n")

            # result = get_global_coordinates_from_sensor(quat_real, quat_i, quat_j, quat_k, distance, axis='x')
            # print(f"{datetime.datetime.now().isoformat()}  {result}")

            # print(f"{datetime.datetime.now().isoformat()}  {roll:.6f},{pitch:.6f},{yaw:.6f}")
            # open("imu_data.txt", "a").write(f"{datetime.datetime.now().isoformat()}  {roll:.6f},{pitch:.6f},{yaw:.6f}\n")
            # print(f"{datetime.datetime.now().isoformat()}  {x:.6f},{y:.6f},{z:.6f}")
            # open("imu_data.txt", "a").write(f"{datetime.datetime.now().isoformat()}  {x:.6f},{y:.6f},{z:.6f}\n")

            message = ""
            if acceleration_count == 0:
                message += "HEAD" + acceleration + "FOOT"
            if gyroscope_count == 0:
                message += "HEAD" + gyroscope + "FOOT"
            if magnetometer_count == 0:
                message += "HEAD" + magnetometer + "FOOT"
            if rotation_vector_count == 0:
                message += "HEAD" + rotation_vector + "FOOT"

            # print(message)
            open("bno_data.txt", 'a').write(message + '\n')
            client_socket.sendall((message).encode(encoding="utf-8", errors="strict"))

            acceleration_count = (acceleration_count + 1) % acceleration_time
            gyroscope_count = (gyroscope_count + 1) % gyroscope_time
            magnetometer_count = (magnetometer_count + 1) % magnetometer_time
            rotation_vector_count = (rotation_vector_count + 1) % rotation_vector_time
            time.sleep(0.0025)

    except KeyboardInterrupt:
        print("Exiting...")
        break
    except Exception as e:
        print(f"Error: {e}")
        try:
            open("bno_errors.txt", "a").write(f"[{datetime.datetime.now()}]  {e}\n")
            time.sleep(3)
        except Exception as e2:
            print(f"Fatal: {e2}")
