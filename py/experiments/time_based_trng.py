import time
import random

def generate_random_integer(bit_count=32):
    """
    Generates a random integer using time differences in loop execution.

    :param bit_count: The number of bits to generate for the random integer.
    :return: A randomly generated integer.
    """
    bits = []

    while len(bits) < bit_count:
        # Define two identical loops for timing comparison
        start_time_1 = time.perf_counter()
        for _ in range(1000):
            _ = random.randint(1, 10) * random.randint(1, 10)
        end_time_1 = time.perf_counter()

        start_time_2 = time.perf_counter()
        for _ in range(1000):
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

# Example usage
if __name__ == "__main__":
    random_int = generate_random_integer()
    print(f"Generated random integer: {random_int}")
