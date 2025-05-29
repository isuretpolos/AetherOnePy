from gpiozero import LED
import time
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.databaseService import CaseDAO


class GPIOBroadcaster:

    def __init__(self, aetherOneDB: CaseDAO):
        self.led_map = {}

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
                self.led_map[pin] = {
                    "led": LED(pin),
                    "numbers": numbers
                }
            except ValueError:
                print(f"[ERROR] Setting '{name}' is not a valid GPIO number: {pin_str}")

        print(f"GPIOZero LEDs mapped: {list(self.led_map.keys())}")

    def broadcast(self, signature: str, duration: float):
        end_time = time.time() + duration
        print(f"Broadcasting '{signature}' for {duration} seconds...")

        while time.time() < end_time:
            for char in signature:
                ascii_value = str(ord(char))
                for digit in ascii_value:
                    num = int(digit)
                    for pin, obj in self.led_map.items():
                        if num in obj["numbers"]:
                            obj["led"].on()
                        else:
                            obj["led"].off()
                    time.sleep(0.2)

        self.cleanup()

    def cleanup(self):
        for obj in self.led_map.values():
            obj["led"].off()
        print("GPIOZero LEDs turned off.")
