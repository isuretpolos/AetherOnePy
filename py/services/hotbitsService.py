import sys, os, random, json
import platform as sys_platform
import threading, time,multiprocessing

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from enum import Enum
from services.captureRandomnessFromWebCam import WebCamCollector
from services.captureRandomnessFromRaspberryPi import RandomNumberGenerator
from services.databaseService import CaseDAO, get_case_dao

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))


class HotbitsSource(Enum):
    RASPBERRY_PI = 'RASPBERRY_PI'
    WEBCAM = 'WEBCAM'
    ARDUINO = 'ARDUINO'
    ESP = 'ESP'


def generate_random_integer(bit_count: int = 32):
    """
    Generates a random integer using time differences in loop execution.

    :param bit_count: The number of bits to generate for the random integer.
    :return: A randomly generated integer.
    """
    maxCount = 50
    bits = []

    while len(bits) < bit_count:
        # Define two identical loops for timing comparison
        start_time_1 = time.perf_counter()
        for _ in range(maxCount):
            _ = random.randint(1, 10) * random.randint(1, 10)
        end_time_1 = time.perf_counter()

        start_time_2 = time.perf_counter()
        for _ in range(maxCount):
            _ = random.randint(1, 10) * random.randint(1, 10)
        end_time_2 = time.perf_counter()

        # Compare the durations and store a bit based on the result
        if (end_time_1 - start_time_1) < (end_time_2 - start_time_2):
            bits.append(1)
        else:
            bits.append(0)

    # Convert the collected bits into an integer
    random_integer = int("".join(map(str, bits)), 2)
    return random_integer


class HotbitsService:

    def __init__(self, hotbitsSource: HotbitsSource, folder_path: str, aetherOneDB: CaseDAO, main):
        self.source = hotbitsSource
        self.main = main
        self.running = False
        self.aetherOneDB = aetherOneDB
        self.hotbits: [int] = []
        self.folder_path = folder_path
        self.webCamCollector = WebCamCollector(main, self.countHotbits)
        if self.is_raspberry_pi():
            print("This system is a Raspberry Pi.")
            self.source = HotbitsSource.RASPBERRY_PI
        # always start collecting some hotbits
        #thread = threading.Thread(target=self.initHotbits)
        #thread.daemon = True
        #thread.start()


    def initHotbits(self):
        count = self.countHotbits()
        amount = 1000 - count
        for _ in range(amount):
            if count > 500:
                time.sleep(5)
            elif count > 250:
                time.sleep(2)
            elif count > 20:
                time.sleep(1)
            
            timeLoopedHotbits: [int] = []
            for i in range(10000):
                timeLoopedHotbits.append(generate_random_integer())
            # Save the integers to a JSON file
            timestamp = int(time.time() * 1000)
            filename = f"{self.folder_path}/hotbits_{timestamp}.json"
            with open(filename, 'w') as f:
                json.dump({"integerList": timeLoopedHotbits, "source": "timeLoop"}, f)

    def countHotbits(self):
        return len([file for file in os.listdir(self.folder_path) if file.endswith(".json")])

    def stopCollectingHotbits(self):
        self.webCamCollector.stopCollectingHotbits = True
        self.running = False

    def collectWebCamHotBits(self):
        self.main.emitMessage('server_update', 'running webCam')
        if self.webCamCollector.checkIfWebCamIsAvailable():
            self.running = True
            thread = threading.Thread(target=self.webCamCollector.generate_hotbits, args=[self.folder_path, 100])
            thread.daemon = True
            thread.start()
            return True
        else:
            return False

    def collectHotBits(self):
        if self.source == HotbitsSource.RASPBERRY_PI:
            self.raspberryPi = True
            print("Raspberry Pi source enabled.")
        elif self.source == HotbitsSource.WEBCAM:
            self.running = True
            self.webCamCollector.generate_hotbits(self.folder_path, 10000)
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
            if sys_platform.system() != "Linux":
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

    def getHotbits(self):
        if self.source == HotbitsSource.RASPBERRY_PI:
            rng = RandomNumberGenerator()
            rng.generate_numbers()
            return rng.get_numbers()
        else:
            if self.countHotbits() < 10 and self.running is False:
                # TODO make this as a SETTING
                if self.aetherOneDB.get_setting('hotbits_use_WebCam'):
                    thread = threading.Thread(target=self.collectHotBits)
                    thread.daemon = True
                    thread.start()
                    print("collect webcam hotbits")
                    #asyncio.run(self.collectHotBits())
            if self.countHotbits() < 1:
                # SIMULATION MODE
                timeLoopedHotbits: [int] = []
                for i in range(250):
                    timeLoopedHotbits.append(generate_random_integer())
                print("time loop generated random number ...")
                return timeLoopedHotbits
            """Load integers from a random JSON file in a folder into an array."""
            json_files = [f for f in os.listdir(self.folder_path) if f.endswith('.json')]
            if not json_files:
                raise FileNotFoundError("No JSON files found in the folder")
            random_file = random.choice(json_files)
            json_file_path = os.path.join(self.folder_path, random_file)
            with open(json_file_path, 'r') as f:
                data = json.load(f)
            if "integerList" not in data:
                raise KeyError("The JSON file does not contain 'integerList'")
            os.remove(json_file_path)  # Delete the hotbits file after loading
            print(f"Loaded integers from {random_file}")
            return data["integerList"]

    def getInt(self, min: int = 0, max: int = 1):
        if len(self.hotbits) < 1:
            self.hotbits = self.getHotbits()
        # BUGFIX: IndexError: pop from empty list
        if len(self.hotbits) < 1:
            print("Hotbits list is empty, generating a pseudo random number.")
            return random.randint(min, max)
        random.seed(self.hotbits.pop(0))
        return random.randint(min, max)

if __name__ == "__main__":
    aetherOneDB = get_case_dao(os.path.join(PROJECT_ROOT, 'data/aetherone.db'))
    hotbitsService = HotbitsService(HotbitsSource.WEBCAM, os.path.join(PROJECT_ROOT, "hotbits"),aetherOneDB)
    if hotbitsService.is_raspberry_pi():
        print("Working from inside a RaspberryPi, great!")
    # hotbitsService.collectHotBits()
    hotbits = hotbitsService.getHotbits()
    print(hotbits)
    print(len(hotbits))
    print(hotbits[1])
    print(hotbits[2])
