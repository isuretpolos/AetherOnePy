import sys, os, random, json

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from enum import Enum
from services.captureRandomnessFromWebCam import generate_hotbits

class HotbitsSource(Enum):
    RASPBERRY_PI = 'RASPBERRY_PI'
    WEBCAM = 'WEBCAM'
    ARDUINO = 'ARDUINO'
    ESP = 'ESP'


class HotbitsService:

    def __init__(self, hotbitsSource: HotbitsSource):
        self.source = hotbitsSource
        self.running = False

    def collectHotBits(self):
        if self.source == HotbitsSource.RASPBERRY_PI:
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

    def getHotbits(self, folder_path):
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
    #hotbitsService.collectHotBits()
    hotbits = hotbitsService.getHotbits("../../hotbits")
    print(len(hotbits))
    print(hotbits[1])
    print(hotbits[2])