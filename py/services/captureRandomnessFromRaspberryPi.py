import os
import struct

class RandomNumberGenerator:
    def __init__(self, total_numbers=10000):
        """
        Initialize the generator.
        :param total_numbers: Number of random integers to generate
        """
        self.total_numbers = total_numbers
        self.numbers = []

    def generate_numbers(self):
        """
        Retrieves randomness from /dev/random and generates integers.
        Stores the generated numbers in an array.
        """
        self.numbers = []  # Clear the array before generating
        try:
            with open("/dev/random", "rb") as random_source:
                for _ in range(self.total_numbers):
                    # Read 4 bytes of randomness to generate a 32-bit integer
                    random_bytes = random_source.read(4)
                    random_int = struct.unpack("I", random_bytes)[0]  # Convert to unsigned integer
                    self.numbers.append(random_int)
        except Exception as e:
            print(f"Error while generating numbers: {e}")

    def get_numbers(self):
        """
        Returns the generated array of numbers.
        :return: List of integers
        """
        return self.numbers

# Example usage:
if __name__ == "__main__":
    rng = RandomNumberGenerator()
    rng.generate_numbers()
    print(f"Generated {len(rng.get_numbers())} random numbers.")
    print(rng.get_numbers()[:10])  # Print the first 10 numbers