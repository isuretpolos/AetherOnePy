import csv
import random
import time

current_time_ms = int(time.time() * 1000)
random.seed(current_time_ms)

# Load data from CSV file
filename = "../../data/remoteViewingCategories.csv"
categories = []
targets = []

with open(filename, 'r', encoding='utf-8') as file:
    reader = csv.reader(file)
    next(reader)  # Skip the header
    for row in reader:
        categories.append(row[0])
        targets.append(row[1].split(', '))

# Flatten the list of targets
all_targets = [item for sublist in targets for item in sublist]

correct_count = 0
incorrect_count = 0

while True:
    # Randomly select a target example
    selected_target = random.choice(all_targets)

    # Generate a list of 10 options including the selected target
    options = random.sample(all_targets, 9)
    if selected_target not in options:
        options.append(selected_target)
    else:
        options[random.randint(0, 8)] = selected_target

    # Ensure no duplicate entries
    options = list(set(options))

    # If fewer than 10 options due to duplicate removal, add more unique options
    while len(options) < 10:
        extra_option = random.choice(all_targets)
        if extra_option not in options:
            options.append(extra_option)

    # Shuffle the options
    random.shuffle(options)

    # Prompt the user to guess the target
    print("Guess the true target from the following options:")
    for i, option in enumerate(options, start=1):
        print(f"{i}. {option}")

    # Get the user's guess
    user_guess = int(input("Enter the number of your guess (1-10): "))

    # Check if the user's guess was correct
    if options[user_guess - 1] == selected_target:
        print("Congratulations! You guessed the correct target.")
        correct_count += 1
    else:
        print(f"Sorry, the correct target was: {selected_target}")
        incorrect_count += 1

    # Display the current score
    print(f"Correct guesses: {correct_count}, Incorrect guesses: {incorrect_count}")

    # Ask if the user wants to play again
    play_again = input("Do you want to play again? (yes/no): ").strip().lower()
    if play_again == 'no':
        break

print("Thank you for playing!")