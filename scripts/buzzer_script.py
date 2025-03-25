import RPi.GPIO as GPIO
import time

# Disable warnings (optional)
GPIO.setwarnings(False)

# Select GPIO mode
GPIO.setmode(GPIO.BCM)

# Set buzzer - pin 18 as output
buzzer = 18
GPIO.setup(buzzer, GPIO.OUT)

try:
    # Run forever loop
    while True:
        GPIO.output(buzzer, GPIO.LOW)  # Activate buzzer
        print("Beep")
        time.sleep(0.5)  # Delay in seconds
        GPIO.output(buzzer, GPIO.HIGH)  # Deactivate buzzer
        print("No Beep")
        time.sleep(0.5)
except KeyboardInterrupt:
    # Ensure buzzer is off before cleanup
    GPIO.output(buzzer, GPIO.HIGH)
    GPIO.cleanup()
    print("Program terminated and GPIO cleaned up.")
