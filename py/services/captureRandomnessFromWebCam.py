import cv2
import numpy as np
import json
import time,os,sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def bits_to_integer(bits):
    """Convert a list of bits into an integer."""
    bit_string = ''.join(map(str, bits))
    return int(bit_string, 2)


def pixel_to_bit(img1, img2):
    """Compare two images pixel by pixel to generate bits."""
    bits = []
    for (pixel1, pixel2) in zip(img1.reshape(-1, 3), img2.reshape(-1, 3)):
        if sum(pixel1) > sum(pixel2):
            bits.append(1)
        else:
            bits.append(0)
    return bits


def capture_image(cap):
    """Capture an image using the provided VideoCapture object."""
    ret, frame = cap.read()
    if not ret:
        raise Exception("Failed to capture image")
    return frame


def sufficient_difference(img1, img2, threshold=500):
    """Check if there is sufficient difference between two images."""
    diff = np.abs(img1.astype(np.int32) - img2.astype(np.int32))
    total_diff = np.sum(diff)

    # Check if the generated bits are all zeros
    bits = pixel_to_bit(img1, img2)
    if bits[:9] == [0] * 9:
        print("Detected a series of 0s. Skipping one image and retrying...")
        return False

    return total_diff > threshold


def generate_hotbits(hotbitsPath: str, amount: int):
    bit_array = []
    max_bits = 32  # Maximum number of bits for an integer

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise Exception("Failed to open the camera")

    try:
        for _ in range(amount):
            integer_list = []
            unique_integers = set()

            while len(integer_list) < 10000:
                img1 = capture_image(cap)
                img2 = capture_image(cap)

                # Resize images to ensure they are the same dimensions
                height, width = min(img1.shape[:2], img2.shape[:2])
                img1 = cv2.resize(img1, (width, height))
                img2 = cv2.resize(img2, (width, height))

                # Wait until there is sufficient difference between images
                if not sufficient_difference(img1, img2):
                    print("Insufficient difference between images. Retrying...")
                    continue

                bits = pixel_to_bit(img1, img2)
                bit_array.extend(bits)

                while len(bit_array) >= max_bits:
                    integer = bits_to_integer(bit_array[:max_bits])
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
                json.dump({"integerList": integer_list}, f)

            print(f"Hotbits saved to {filename}")
    finally:
        cap.release()


if __name__ == "__main__":
    generate_hotbits("../../hotbits", 10)