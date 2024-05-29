import cv2  # For WebCam
import json
import os
import numpy as np

class WebcamRandomService:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.data_dir = 'hotbits'  # Folder with Hotbits
            os.makedirs(cls._instance.data_dir, exist_ok=True)
        return cls._instance

    def capture_random_data(self, num_samples=10):
        cap = cv2.VideoCapture(0)  # Zugriff auf die Webcam
        random_data = []

        for _ in range(num_samples):
            ret, frame = cap.read()
            if not ret:
                break
            # Hier könnten Sie den Frame analysieren, um echte Zufallszahlen zu generieren
            random_numbers = np.random.randint(0, 255, size=(10,), dtype=np.uint8).tolist()
            random_data.append(random_numbers)

        cap.release()

        # Daten als JSON-Datei speichern
        file_path = os.path.join(self.data_dir, 'random_data.json')
        with open(file_path, 'w') as file:
            json.dump(random_data, file)

        return file_path

    def get_random_data(self):
        file_path = os.path.join(self.data_dir, 'random_data.json')
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                random_data = json.load(file)
            return random_data
        else:
            return None

    def get_random_numbers(self, start, end):
        random_data = self.get_random_data()
        if random_data:
            random_numbers = [number for data in random_data for number in data]
            return random_numbers[start:end]
        else:
            return []

# Beispiel für die Verwendung:
webcam_service = WebcamRandomService()
webcam_service.capture_random_data(num_samples=100)  # Daten erfassen
random_numbers = webcam_service.get_random_numbers(start=10, end=20)  # Zufallszahlen abrufen
print(random_numbers)
