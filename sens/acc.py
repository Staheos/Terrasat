import time
import board
import busio
from adafruit_bno08x.i2c import BNO08X_I2C
from adafruit_bno08x import (
    BNO_REPORT_ACCELEROMETER,
    BNO_REPORT_GYROSCOPE,
    BNO_REPORT_MAGNETOMETER,
    BNO_REPORT_ROTATION_VECTOR,
)

i2c = busio.I2C(board.SCL, board.SDA, frequency=400000) 

bno = BNO08X_I2C(i2c)

bno.enable_feature(BNO_REPORT_ACCELEROMETER)
bno.enable_feature(BNO_REPORT_GYROSCOPE)

bno.enable_feature(BNO_REPORT_MAGNETOMETER)
bno.enable_feature(BNO_REPORT_ROTATION_VECTOR)

print("BNO08X IMU Sensor Initialized!")
print("Reading sensor data...\n")

while True:
    try:
        accel_x, accel_y, accel_z = bno.acceleration
        print(f"Acceleration - X: {accel_x:.6f} m/s^2, Y: {accel_y:.6f} m/s^2")

        gyro_x, gyro_y, gyro_z = bno.gyro
        print(f"Gyroscope - X: {gyro_x:.6f} rad/s, Y: {gyro_y:.6f} rad/s, Z:")

        mag_x, mag_y, mag_z = bno.magnetic
        print(f"Magnetometer - X: {mag_x:.6f} uT, Y: {mag_y:.6f} uT, Z:")
       
        quat_i, quat_j, quat_k, quat_real = bno.quaternion
        print(f"Rotation Vector - i: {quat_i:.6f}, j: {quat_j:.6f}, k:")

        print("\n")
        time.sleep(1.0) 

    except Exception as e:
        print(f"Error reading sensor: {e}")
        time.sleep(1.0)