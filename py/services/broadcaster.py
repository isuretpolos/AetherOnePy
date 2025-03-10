import multiprocessing
import time
import os,sys
import random
import hashlib
import numpy as np
from scipy.io.wavfile import write
from PIL import Image, ImageDraw

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from services.hotbitsService import generate_random_integer


class DigitalBroadcaster:
    def __init__(self, signature: str, output_path: str, duration: int = 10):
        """
        Initializes the broadcaster with a signature and duration.
        :param signature: The intent or message to broadcast.
        :param duration: Duration in seconds for broadcasting.
        """
        self.signature = signature
        self.output_path = os.path.join(output_path, "broadcasts")
        self.duration = duration
        self.parsed_signature = self._sigilize(signature)
        self.num_workers = max(1, os.cpu_count() // 4)
        self.resonance_events = []

    def _sigilize(self, text: str):
        """ Removes duplicate letters and spaces for sigilization. """
        text = text.upper().replace(" ", "")
        return list(dict.fromkeys(text))

    def _broadcast_worker(self, sigil_part: str):
        """ Dynamically modifies and broadcasts sigil fragments. """
        start_time = time.time()
        while time.time() - start_time < self.duration:
            transformation = self._deepen_sigilization(sigil_part)
            #print(f"[Worker-{os.getpid()}] Broadcasting: {transformation}")

    def _resonance_check_worker(self):
        """ Checks for resonance events during broadcasting. """
        start_time = time.time()
        while time.time() - start_time < self.duration:
            random.seed(generate_random_integer(32,1))
            eventEnergy = random.randint(0, 6765)
            if eventEnergy >= 6764:
                msg = f"Resonance detected! Random Event Energy: {eventEnergy} at {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())}"
                print(msg)
                self.resonance_events.append(msg)

    def _deepen_sigilization(self, sigil_part: str):
        """ Applies additional transformations to the sigil part. """
        random.seed(generate_random_integer(32,1))
        operations = [
            lambda x: x[::-1],
            lambda x: "-".join(x),
            lambda x: "".join(str(ord(c)) for c in x),
            lambda x: "".join(chr(ord(c) + 1) for c in x),
            lambda x: f"{x}{random.randint(1, 99)}",
        ]
        return random.choice(operations)(sigil_part)

    def start_broadcasting(self):
        """ Launches parallel workers to broadcast sigil parts. """
        print(f"Starting Digital Broadcaster with {self.num_workers} processes...")
        print(f"Sigilized Intent: {' '.join(self.parsed_signature)}")

        processes = []
        p = multiprocessing.Process(target=self._resonance_check_worker)
        p.daemon = True
        p.start()
        processes.append(p)

        for i in range(self.num_workers - 1):
            sigil_part = self.parsed_signature[i % len(self.parsed_signature)]
            p = multiprocessing.Process(target=self._broadcast_worker, args=(sigil_part,))
            p.start()
            processes.append(p)

        for p in processes:
            p.join()

        print("Broadcasting complete! Moving to coagulation...")
        self.coagulate_intent()

    def coagulate_intent(self):
        """ Finalizes the intent through quantum entropy & digital artifacts. """
        random.seed(generate_random_integer(32,1))
        final_state = hashlib.sha256((self.signature + str(random.randint(0, 1000000))).encode()).hexdigest()

        print(f"Finalized Quantum-Coagulated Intent: {final_state[:16]}")
        self._create_sigil_image(final_state[:16], random.randint(0, 1000000))
        self._create_coagulation_tone(final_state[:16], random.randint(0, 1000000))

    def _create_sigil_image(self, text, quantum_value):
        """ Creates a symbolic sigil image from the final intent hash & QRNG. """
        img = Image.new("RGB", (400, 400), "white")
        draw = ImageDraw.Draw(img)
        draw.text((150, 20), text, fill="black")

        # Determine number of shapes based on QRNG
        num_shapes = 3 + (quantum_value % 4)  # Between 3 and 6 shapes

        for i in range(num_shapes):
            shape_type = (quantum_value + i) % 3  # 0 = rectangle, 1 = circle, 2 = triangle
            random.seed(generate_random_integer(32,1))
            x1, y1 = random.randint(50, 350), random.randint(50, 350)
            x2, y2 = x1 + random.randint(10, 100), y1 + random.randint(10, 100)

            if shape_type == 0:
                draw.rectangle([x1, y1, x2, y2], outline="black", width=2)
            elif shape_type == 1:
                draw.ellipse([x1, y1, x2, y2], outline="black", width=2)
            elif shape_type == 2:
                draw.polygon([ (x1, y1), (x2, y2), (x1, y2) ], outline="black", width=2)

        file_name = f"sigil_{time.strftime('%Y%m%d_%H%M%S')}.png"
        output_file = os.path.join(self.output_path, file_name)
        img.save(output_file)
        print(f"Sigil saved as {file_name} with {num_shapes} symbols.")

    def _create_coagulation_tone(self, intent, quantum_value):
        """ Generates a dynamic frequency tone based on intent & QRNG entropy. """
        rate = 44100
        base_freq = sum(ord(char) for char in intent) % 1000
        mod_freq = 50 + (quantum_value % 50)
        duration = 5
        t = np.linspace(0, duration, int(rate * duration))

        # Dynamic frequency modulation
        carrier_wave = np.sin(2 * np.pi * base_freq * t)
        modulator_wave = np.sin(2 * np.pi * mod_freq * t)
        wave = (carrier_wave * modulator_wave * 32767).astype(np.int16)
        file_name = f"coagulation_tone_{time.strftime('%Y%m%d_%H%M%S')}.wav"
        output_file = os.path.join(self.output_path, file_name)
        write(output_file, rate, wave)
        print(f"Coagulated intent saved as {file_name} (Freq: {base_freq} Hz, Mod: {mod_freq} Hz)")

# Example Usage:
if __name__ == "__main__":
    PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
    if not os.path.isdir(os.path.join(PROJECT_ROOT, "broadcasts")):
        os.makedirs(os.path.join(PROJECT_ROOT, "broadcasts"))
    broadcaster = DigitalBroadcaster("Healing Energy for John Doe", PROJECT_ROOT, duration=10)
    broadcaster.start_broadcasting()
