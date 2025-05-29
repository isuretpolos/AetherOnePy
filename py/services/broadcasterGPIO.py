import RPi.GPIO as GPIO
import time
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.databaseService import CaseDAO


class GPIOBroadcaster:

    def __init__(self, aetherOneDB: CaseDAO):
        GPIO.setmode(GPIO.BCM)
        self.PIN_MAPPING = {
            aetherOneDB.get_setting("gpioRED"): [2, 6],
            aetherOneDB.get_setting("gpioBLUE"): [0, 3],
            aetherOneDB.get_setting("gpioGREEN"): [1, 4],
            aetherOneDB.get_setting("gpioLASER"): [9, 7],
            aetherOneDB.get_setting("gpioWHITE"): [8, 5]
        }
        self.PIN_MAPPING = {}
        for name, numbers in {
            "gpioRED": [2, 6],
            "gpioBLUE": [0, 3],
            "gpioGREEN": [1, 4],
            "gpioLASER": [9, 7],
            "gpioWHITE": [8, 5]
        }.items():
            pin_str = aetherOneDB.get_setting(name)
            if pin_str is None:
                print(f"[ERROR] Setting '{name}' is missing!")
                continue
            try:
                pin = int(pin_str)
                self.PIN_MAPPING[pin] = numbers
            except ValueError:
                print(f"[ERROR] Setting '{name}' is not a valid GPIO number: {pin_str}")
        for pin in self.PIN_MAPPING:
            GPIO.setup(pin, GPIO.OUT)
        print("GPIO setup complete.")

    def broadcast(self, signature: str, duration: float):
        """Translates a string into GPIO signals based on ASCII digits."""
        end_time = time.time() + duration
        print(f"Broadcasting '{signature}' for {duration} seconds...")

        while time.time() < end_time:
            for char in signature:
                ascii_value = str(ord(char))
                for digit in ascii_value:
                    num = int(digit)
                    for pin, assigned_numbers in self.PIN_MAPPING.items():
                        GPIO.output(pin, GPIO.HIGH if num in assigned_numbers else GPIO.LOW)
                    time.sleep(0.2)

        self.cleanup()

    def cleanup(self):
        """Clean up GPIO settings."""
        GPIO.cleanup()
        print("GPIO cleanup done.")

