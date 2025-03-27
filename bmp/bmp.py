import time
import datetime
import socket
import board
import adafruit_bmp280

while True:
    try:
        i2c = board.I2C()

        # Specify the correct I2C address (0x76)
        bmp280 = adafruit_bmp280.Adafruit_BMP280_I2C(i2c, address=0x76)

        bmp280.sea_level_pressure = 1013.25

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('localhost', 1769))

        while True:
            temperature = str(int(bmp280.temperature * 100))
            pressure = str(int(bmp280.pressure * 100))
            altitude = str(int(bmp280.altitude * 100))

            timestamp = int(time.time() * 1000)

            message = "BMP:" + str(timestamp) + "&" + temperature + "&" + pressure + "&" + altitude
            print(message)
            client_socket.sendall(("HEAD" + message + "FOOT").encode(encoding="utf-8", errors="strict"))
            open("bmp_data.txt", 'a').write(message + '\n')

            time.sleep(0.8)

    except KeyboardInterrupt:
        print("Exiting...")
        break
    except Exception as e:
        print(f"Error: {e}")
        try:
            open("bmp_errors.txt", "a").write(f"[{datetime.datetime.now()}]  {e}\n")
            time.sleep(3)
        except Exception as e2:
            print(f"Fatal: {e2}")
