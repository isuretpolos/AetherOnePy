import pygame

# Initialize pygame
pygame.init()

# Set up display
WIDTH, HEIGHT = 500, 400
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Moving Graphic Example")

# Define colors
WHITE = (255, 255, 255)
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

    # Update circle position
    x += speed_x
    y += speed_y

    # Bounce off edges
    if x - radius <= 0 or x + radius >= WIDTH:
        speed_x = -speed_x
    if y - radius <= 0 or y + radius >= HEIGHT:
        speed_y = -speed_y

    # Draw everything
    screen.fill(WHITE)
    pygame.draw.circle(screen, RED, (x, y), radius)
    pygame.display.update()

# Quit pygame
pygame.quit()
