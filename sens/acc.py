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


def quaternion_to_euler(quat_i, quat_j, quat_k, quat_real):
    # Roll (x-axis rotation)
    sinr_cosp = 2 * (quat_real * quat_i + quat_j * quat_k)
    cosr_cosp = 1 - 2 * (quat_i * quat_i + quat_j * quat_j)
    roll = math.atan2(sinr_cosp, cosr_cosp)

    # Pitch (y-axis rotation)
    sinp = 2 * (quat_real * quat_j - quat_k * quat_i)
    if abs(sinp) >= 1:
        pitch = math.copysign(math.pi / 2, sinp)  # Use 90 degrees if out of range
    else:
        pitch = math.asin(sinp)

    # Yaw (z-axis rotation)
    siny_cosp = 2 * (quat_real * quat_k + quat_i * quat_j)
    cosy_cosp = 1 - 2 * (quat_j * quat_j + quat_k * quat_k)
    yaw = math.atan2(siny_cosp, cosy_cosp)

    return roll, pitch, yaw

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
        magnetometer_time = 100
        rotation_vector_time = 1

        acceleration_count = 0
        gyroscope_count = 0
        magnetometer_count = 0
        rotation_vector_count = 0

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
            quat_i, quat_j, quat_k, quat_real = bno.quaternion
            rotation_vector = f"ROTATION_VECTOR:{timestamp}&{quat_real:.6f}&{quat_i:.6f}&{quat_j:.6f}&{quat_k:.6f}"
            print(quaternion_to_euler(quat_i, quat_j, quat_k, quat_real))

            message = ""
            if acceleration_count == 0:
                message += "HEAD" + acceleration + "FOOT"
            if gyroscope_count == 0:
                message += "HEAD" + gyroscope + "FOOT"
            if magnetometer_count == 0:
                message += "HEAD" + magnetometer + "FOOT"
            if rotation_vector_count == 0:
                message += "HEAD" + rotation_vector + "FOOT"

            print(message)
            client_socket.sendall((message).encode(encoding="utf-8", errors="strict"))

            acceleration_count = (acceleration_count + 1) % acceleration_time
            gyroscope_count = (gyroscope_count + 1) % gyroscope_time
            magnetometer_count = (magnetometer_count + 1) % magnetometer_time
            rotation_vector_count = (rotation_vector_count + 1) % rotation_vector_time
            time.sleep(0.01)

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
