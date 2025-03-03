import pygame
import io
from PIL import Image, ImageGrab

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 600, 400
MAX_WIDTH = 128
BG_COLOR = (30, 30, 30)

# Setup screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Image Paste and Resize")

def get_pasted_image():
    """Gets image from clipboard using Pillow and returns a resized pygame surface."""
    try:
        image = ImageGrab.grabclipboard()  # Get image from clipboard
        if image is None:
            print("No image found in clipboard.")
            return None

        # Maintain aspect ratio
        width_percent = MAX_WIDTH / float(image.size[0])
        new_height = int(float(image.size[1]) * width_percent)
        image = image.resize((MAX_WIDTH, new_height), Image.LANCZOS)

        return pygame.image.fromstring(image.tobytes(), image.size, image.mode)
    except Exception as e:
        print("Error pasting image:", e)
    return None

running = True
image_surface = None
while running:
    screen.fill(BG_COLOR)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_v and pygame.key.get_mods() & pygame.KMOD_CTRL:
                image_surface = get_pasted_image()

    if image_surface:
        screen.blit(image_surface, (WIDTH // 2 - image_surface.get_width() // 2, HEIGHT // 2 - image_surface.get_height() // 2))

    pygame.display.flip()

pygame.quit()
