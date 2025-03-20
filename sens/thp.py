import time
import board
import busio
from adafruit_bme280 import basic as adafruit_bme280

i2c = busio.I2C(board.SCL, board.SDA, frequency=100000)  # Use standard 100kHz

bme280 = adafruit_bme280.Adafruit_BME280_I2C(i2c, address=0x76)

bme280.sea_level_pressure = 1013.25  

while True:
    print(f"Temperature: {bme280.temperature:.2f} C")
    print(f"Humidity: {bme280.relative_humidity:.2f} %")
    print(f"Pressure: {bme280.pressure:.2f} hPa")
    print(f"Altitude: {bme280.altitude:.2f} meters")
    print("-" * 30)
    time.sleep(2)
