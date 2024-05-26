import cv2
import numpy as np
import random
import json

def compare_images(image1, image2):
    # Convert images to grayscale
    gray1 = cv2.cvtColor(image1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(image2, cv2.COLOR_BGR2GRAY)

    # Compute absolute difference between the images
    diff = cv2.absdiff(gray1, gray2)

    return diff

def generate_random_numbers(diff):
    # Convert the difference matrix to binary
    binary_diff = (diff > 0).astype(int)

    # Flatten the binary difference matrix
    flattened_diff = binary_diff.flatten()

    # Take only the first 32 bits and convert to integer
    binary_string = ''.join(map(str, flattened_diff[:32]))
    num = int(binary_string, 2)

    return num

def main():
    consecutive_unchanged_frames = np.zeros((1080, 1920), dtype=int)  # Initialize array to keep track of consecutive unchanged frames
    integers = []
    # Open the default camera
    cap = cv2.VideoCapture(0)

    # Check if the camera is opened correctly
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return None

    while True:
        # Capture four images
        print("Capturing first image...")
        image1 = cap.read()
        print("Capturing second image...")
        image2 = cap.read()
        print("Capturing third image...")
        image3 = cap.read()
        print("Capturing fourth image...")
        image4 = cap.read()

        if image1 is None or image2 is None or image3 is None or image4 is None:
            return

        # Compare consecutive images
        print("Comparing images...")
        diff1 = compare_images(image1, image2)
        diff2 = compare_images(image2, image3)
        diff3 = compare_images(image3, image4)

        # Check for pixels that remain unchanged over the four images
        unchanged_pixels = np.logical_and.reduce((diff1 == 0, diff2 == 0, diff3 == 0))
        consecutive_unchanged_frames[unchanged_pixels] += 1

        # Generate random numbers from differences, excluding unchanged pixels
        invalid_pixels = consecutive_unchanged_frames >= 4
        diff1[invalid_pixels] = 0

        num = generate_random_numbers(diff1)
        integers.append(num)

        # Check if multiple integers are formed
        if len(set(integers)) > 1:
            # Save the integers to a JSON file
            with open('random_numbers.json', 'w') as f:
                json.dump(integers, f)
            print("Multiple integers formed. Saved to file.")
            break

    # Release the camera
    cap.release()

    if not ret:
        print("Error: Could not capture frame.")
        return None

if __name__ == "__main__":
    main()
