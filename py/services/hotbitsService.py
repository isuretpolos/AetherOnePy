import sys, os, random, json
import platform as sys_platform

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from enum import Enum
from services.captureRandomnessFromWebCam import generate_hotbits
from services.captureRandomnessFromRaspberryPi import RandomNumberGenerator


class HotbitsSource(Enum):
    RASPBERRY_PI = 'RASPBERRY_PI'
    WEBCAM = 'WEBCAM'
    ARDUINO = 'ARDUINO'
    ESP = 'ESP'


class HotbitsService:

    def __init__(self, hotbitsSource: HotbitsSource):
        self.source = hotbitsSource
        self.running = False
        if self.is_raspberry_pi():
            print("This system is a Raspberry Pi.")
            self.source = HotbitsSource.RASPBERRY_PI

    def collectHotBits(self):
        if self.source == HotbitsSource.RASPBERRY_PI or self.is_raspberry_pi():
            self.raspberryPi = True
            print("Raspberry Pi source enabled.")
        elif self.source == HotbitsSource.WEBCAM:
            self.running = True
            generate_hotbits("../../hotbits", 1000)
        elif self.source == HotbitsSource.ARDUINO:
            self.useArduino = True
            print("Arduino source enabled.")
        elif self.source == HotbitsSource.ESP:
            self.useESP = True
            print("ESP source enabled.")
        else:
            print("Unknown Hotbits source selected. No changes made.")
        self.running = False

    def is_raspberry_pi(self):
        """Check if the computer is a Raspberry Pi."""
        try:
            # Check the platform
            print(sys.platform)
            if sys_platform.system() != "Linux":
                print("not a linux system")
                return False

            # Check for the presence of Raspberry Pi-specific files
            if os.path.exists('/sys/firmware/devicetree/base/model'):
                with open('/sys/firmware/devicetree/base/model', 'r') as model_file:
                    model_info = model_file.read().lower()
                    print(model_info)
                    if 'raspberry pi' in model_info:
                        return True

            # Check the CPU information for Raspberry Pi specific hardware
            with open('/proc/cpuinfo', 'r') as cpuinfo:
                for line in cpuinfo:
                    print(line)
                    if 'Hardware' in line and 'BCM' in line:
                        return True
                    if 'Model' in line and 'Raspberry Pi' in line:
                        return True
        except Exception as e:
            print(f"Error while checking Raspberry Pi: {e}")
        return False

    def getHotbits(self, folder_path):
        if self.source == HotbitsSource.RASPBERRY_PI:
            rng = RandomNumberGenerator()
            rng.generate_numbers()
        else:
            """Load integers from a random JSON file in a folder into an array."""
            json_files = [f for f in os.listdir(folder_path) if f.endswith('.json')]
            if not json_files:
                raise FileNotFoundError("No JSON files found in the folder")
            random_file = random.choice(json_files)
            json_file_path = os.path.join(folder_path, random_file)
            with open(json_file_path, 'r') as f:
                data = json.load(f)
            if "integerList" not in data:
                raise KeyError("The JSON file does not contain 'integerList'")
            print(f"Loaded integers from {random_file}")
            return data["integerList"]


if __name__ == "__main__":
    hotbitsService = HotbitsService(HotbitsSource.WEBCAM)
    if hotbitsService.is_raspberry_pi():
        print("Working from inside a RaspberryPi, great!")
    # hotbitsService.collectHotBits()
    hotbits = hotbitsService.getHotbits("../../hotbits")
    print(hotbits)
    print(len(hotbits))
    print(hotbits[1])
    print(hotbits[2])
