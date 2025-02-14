import math
import numpy as np
import random,sys,os
import matplotlib.pyplot as plt


sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from collections import Counter
from hotbitsService import generate_random_integer

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

        Chi-Square Test: This test checks if the distribution of bits in the stream matches the expected distribution. A low p-value (typically less than 0.05) indicates that the bit stream significantly deviates from the expected distribution, suggesting it may not be random. A high p-value suggests the bit stream is likely random.
        Entropy: Entropy measures the unpredictability or randomness of the bit stream. Higher entropy values indicate higher randomness. For a truly random bit stream, the entropy should be close to the maximum possible value for the given length.
        Autocorrelation: This test checks for patterns or correlations within the bit stream. A low autocorrelation value indicates that the bits are not correlated and are likely random. High autocorrelation suggests patterns, indicating non-randomness.
        Monte Carlo Simulation: This test uses random sampling to estimate mathematical properties. In the context of randomness tests, it might be used to estimate the value of π or other constants. If the estimated value is close to the actual value, it suggests the bit stream is random.
        Uniqueness Check: This test checks if each integer in the bit stream appears only once. If all integers are unique, it suggests randomness. If there are duplicates, it indicates non-randomness.
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
    #bit_stream = [np.random.randint(0, 2) for _ in range(10000)]
    bit_stream = []
    for _ in range(10000):
        random.seed(generate_random_integer(32,100))
        bit_stream.append(random.randint(0, 1))

    # Instantiate the RandomnessTests class
    tester = RandomnessTests()

    # Run all tests
    results = tester.run_all_tests(bit_stream)
    print(f"Chi-Square Test: {results['Chi-Square Test']} # Expected: Low p-value for randomness")
    print(f"Entropy: {results['Entropy']} # Expected: High entropy for randomness") 
    #print(f"Autocorrelation: {results['Autocorrelation']} # Expected: Low autocorrelation for randomness")
    print(f"Monte Carlo Simulation: {results['Monte Carlo Simulation']}# Expected: Low Chi-Square for randomness")  
    print(f"Uniqueness Check: {results['Uniqueness Check']} # Expected: True for randomness") 
    # Make a PNG image of the bitstream
    bit_array = np.array(bit_stream).reshape((100, 100))  # Reshape to 100x100 for visualization
    plt.figure(figsize=(10, 10))
    plt.imshow(bit_array, cmap='gray', aspect='auto')
    plt.axis('off')
    plt.savefig('bitstream.png', bbox_inches='tight', pad_inches=0)
    plt.close()

