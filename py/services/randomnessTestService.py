import math
import numpy as np
from collections import Counter


class RandomnessTests:
    def __init__(self):
        pass

    def chi_square_test(self, bit_stream):
        """
        Perform the Chi-Square Test to compare observed and expected frequencies.
        A truly random sequence will have an observed frequency close to the expected frequency.
        good video tutorial: https://www.youtube.com/watch?v=qYOMO83Z1WU 
        """
        # Expected frequencies for a 50-50 bit distribution
        expected_frequency = len(bit_stream) / 2

        # Count observed frequencies
        observed_frequency = [bit_stream.count(0), bit_stream.count(1)]

        # Chi-square calculation
        chi_square = sum((observed - expected_frequency) ** 2 / expected_frequency for observed in observed_frequency)
        return chi_square

    def entropy(self, bit_stream):
        """
        Calculate Shannon entropy to measure the unpredictability of a bitstream.
        Higher entropy suggests better randomness.
        """
        counts = Counter(bit_stream)
        total = len(bit_stream)
        return -sum(count / total * math.log2(count / total) for count in counts.values())

    def autocorrelation_test(self, bit_stream):
        """
        Perform an autocorrelation test to check for patterns in the bitstream.
        For truly random sequences, the correlation should be close to zero.
        """
        correlations = []
        for lag in range(1, len(bit_stream) // 2):
            autocorrelation = sum(bit_stream[i] == bit_stream[i + lag] for i in range(len(bit_stream) - lag))
            correlations.append(autocorrelation / len(bit_stream))
        return correlations

    def monte_carlo_simulation(self, bit_stream, bins=10):
        """
        Perform a Monte Carlo simulation to check if the bits are uniformly distributed.
        A uniform distribution is expected for a random bitstream.
        """
        # Convert the bits to integers (0 or 1)
        hist, _ = np.histogram(bit_stream, bins=np.arange(0, bins + 1))

        # Calculate the expected frequency for a uniform distribution
        expected_frequency = len(bit_stream) / bins

        # Calculate the Chi-Square statistic for the histogram
        chi_square = sum((obs - expected_frequency) ** 2 / expected_frequency for obs in hist)
        return chi_square

    def check_unique(self, bit_stream):
        """
        Check if all integers in the bit stream are unique.
        For true randomness, each integer should appear only once.
        """
        unique_bits = set(bit_stream)
        return len(unique_bits) == len(bit_stream)

    def run_all_tests(self, bit_stream):
        """
        Run all the randomness tests and return the results as a dictionary.
        """
        results = {
            'Chi-Square Test': self.chi_square_test(bit_stream),
            'Entropy': self.entropy(bit_stream),
            'Autocorrelation': self.autocorrelation_test(bit_stream),
            'Monte Carlo Simulation': self.monte_carlo_simulation(bit_stream),
            'Uniqueness Check': self.check_unique(bit_stream)
        }
        return results


# Example usage:

if __name__ == "__main__":
    # Example random bitstream (you can replace this with your generated hotbits)
    bit_stream = [np.random.randint(0, 2) for _ in range(10000)]

    # Instantiate the RandomnessTests class
    tester = RandomnessTests()

    # Run all tests
    results = tester.run_all_tests(bit_stream)

    # Print the results
    print("Randomness Test Results:")
    for test, result in results.items():
        print(f"{test}: {result}")
