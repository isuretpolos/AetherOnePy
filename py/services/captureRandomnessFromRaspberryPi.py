import os, sys
import struct

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class RandomNumberGenerator:
    def __init__(self, total_numbers=10000):
        """
        Initialize the generator.
        :param total_numbers: Number of random integers to generate
        """
        self.total_numbers = total_numbers
        self.numbers = set()  # Use a set to avoid duplicates

    def generate_numbers(self):
        """
        Retrieves randomness from /dev/random and generates integers.
        Stores the generated numbers in an array without duplicates.
        """
        self.numbers = set()  # Clear the set before generating
        try:
            with open("/dev/random", "rb") as random_source:
                while len(self.numbers) < self.total_numbers:
                    # Read 4 bytes of randomness to generate a 32-bit integer
                    random_bytes = random_source.read(4)
                    random_int = struct.unpack("I", random_bytes)[0]  # Convert to unsigned integer
                    self.numbers.add(random_int)
        except Exception as e:
            print(f"Error while generating numbers: {e}")

    def get_numbers(self):
        """
        Returns the generated array of numbers.
        :return: List of integers
        """
        return list(self.numbers)


# Example usage:
if __name__ == "__main__":
    rng = RandomNumberGenerator()
    rng.generate_numbers()
    print(f"Generated {len(rng.get_numbers())} random numbers.")
    print(rng.get_numbers()[:10])  # Print the first 10 numbers
