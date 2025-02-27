# Description: Example AetherOnePy app that uses Pygame to create a GUI
# Learn how to write your own AetherOnePy app
# Visit https://patr
from os import environ
environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'
import pygame
import requests

# Initialize pygame as a GUI
pygame.init()

hotbits = []

# Get hotbits from the server
#response = requests.get('http://localhost/hotbits')
#hotbits = response.json()['hotbits']

print(hotbits)

# Set up display
WIDTH, HEIGHT = 600, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Example AetherOnePy App")

# Define colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

# Circle properties
x, y = WIDTH // 2, HEIGHT // 2
radius = 20
speed_x, speed_y = 3, 3

# Main loop
running = True
while running:
    pygame.time.delay(10)  # Control frame rate

    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Draw everything
    screen.fill(BLACK)
    pygame.draw.rect(screen, WHITE, (10, 20, 300, 10), 1)
    pygame.draw.rect(screen, WHITE, (50, 15, 10, 30), 3)
    pygame.display.update()

if __name__ == '__main__':
    # Quit pygame
    pygame.quit()
