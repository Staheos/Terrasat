import time
import board
import adafruit_bmp280

i2c = board.I2C()  # Uses board.SCL (GPIO3) and board.SDA (GPIO2)

bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(i2c)

bmp280.sea_level_pressure = 1013.25

while True:
    print(f"Temperature: {bmp280.temperature:.2f} °C")
    print(f"Pressure: {bmp280.pressure:.2f} hPa")
    print(f"Altitude: {bmp280.altitude:.2f} meters")
    print("-" * 30)
    time.sleep(2)  # Wait for 2 seconds before the next reading
