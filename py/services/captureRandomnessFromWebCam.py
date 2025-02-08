import cv2
import numpy as np
import json
import time, os, sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))


class WebCamCollector:
    def __init__(self, main, countHotbits):
        self.stopCollectingHotbits: bool = False
        self.main = main
        self.countHotbits = countHotbits

    def bits_to_integer(self, bits):
        """Convert a list of bits into an integer."""
        bit_string = ''.join(map(str, bits))
        return int(bit_string, 2)

    def pixel_to_bit(self, img1, img2):
        """Compare two images pixel by pixel to generate bits."""
        bits = []
        for (pixel1, pixel2) in zip(img1.reshape(-1, 3), img2.reshape(-1, 3)):
            if sum(pixel1) > sum(pixel2):
                bits.append(1)
            else:
                bits.append(0)
        return bits

    def capture_image(self, cap):
        """Capture an image using the provided VideoCapture object."""
        ret, frame = cap.read()
        if not ret:
            raise Exception("Failed to capture image")
        return frame

    def sufficient_difference(self, img1, img2, threshold=500):
        """Check if there is sufficient difference between two images."""
        diff = np.abs(img1.astype(np.int32) - img2.astype(np.int32))
        total_diff = np.sum(diff)

        # Check if the generated bits are all zeros
        bits = self.pixel_to_bit(img1, img2)
        if bits[:9] == [0] * 9:
            print("Detected a series of 0s. Skipping one image and retrying...")
            return False

        return total_diff > threshold

    def stop_generate_hotbits(self):
        self.stopCollectingHotbits = True

    def checkIfWebCamIsAvailable(self):
        cap = cv2.VideoCapture(0)
        try:
            if not cap.isOpened():
                self.main.emitMessage('hotbits', 'Failed to open the camera!')
                return False
            ret, frame = cap.read()
            if not ret:
                self.main.emitMessage('hotbits', 'Failed to open the camera!')
                return False
        finally:
            cap.release()
        return True

    def generate_hotbits(self, hotbitsPath: str, amount: int):
        print("generate_hotbits with webCam")
        bit_array = []
        max_bits = 32  # Maximum number of bits for an integer

        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            self.main.emitMessage('hotbits', 'Failed to open the camera!')
            raise Exception("Failed to open the camera")
        ret, frame = cap.read()
        if not ret:
            self.main.emitMessage('hotbits', 'Failed to open the camera!')
            raise Exception("Failed to capture image")

        try:
            self.main.emitMessage('hotbits', 'Starting to collect ...')
            for _ in range(amount):
                integer_list = []
                unique_integers = set()

                while len(integer_list) < 10000:
                    if self.stopCollectingHotbits:
                        break

                    img1 = self.capture_image(cap)
                    img2 = self.capture_image(cap)

                    # Resize images to ensure they are the same dimensions
                    height, width = min(img1.shape[:2], img2.shape[:2])
                    img1 = cv2.resize(img1, (width, height))
                    img2 = cv2.resize(img2, (width, height))

                    # Wait until there is sufficient difference between images
                    if not self.sufficient_difference(img1, img2):
                        print("Insufficient difference between images. Retrying...")
                        continue

                    bits = self.pixel_to_bit(img1, img2)
                    bit_array.extend(bits)

                    while len(bit_array) >= max_bits:
                        integer = self.bits_to_integer(bit_array[:max_bits])
                        bit_array = bit_array[max_bits:]

                        # Ensure the integer is unique
                        if integer not in unique_integers:
                            integer_list.append(integer)
                            unique_integers.add(integer)

                        if len(integer_list) >= 10000:
                            break

                # Save the integers to a JSON file
                timestamp = int(time.time() * 1000)
                filename = f"{hotbitsPath}/hotbits_{timestamp}.json"
                with open(filename, 'w') as f:
                    json.dump({"integerList": integer_list, "source": "webCam"}, f)


                self.main.emitMessage('server_update', str(self.countHotbits()))
                print(f"Hotbits saved to {filename}")
        finally:
            cap.release()
            stopCollectingHotbits = False


if __name__ == "__main__":
    collector = WebCamCollector()
    collector.generate_hotbits(os.path.join(PROJECT_ROOT, "hotbits"), 10)
