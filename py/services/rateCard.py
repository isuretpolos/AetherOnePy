import matplotlib.pyplot as plt
import numpy as np
from PIL import Image, ImageFont, ImageDraw

# Thanks to Benjamin Ludwig!!!

def draw_radionic_chart(rate_text:str,rates, base:str, output_file=None):
    """
    Draws a radionic chart based on the provided rates and optionally saves it as an image.
    """
    fig, ax = plt.subplots(figsize=(6, 6))
    fig.patch.set_facecolor('white')

    # Add the title using suptitle with better spacing
    fig.suptitle(rate_text, fontsize=14)  # Adjust 'y' to move it away from the top border

    # Adjust the layout to create space for the title
    plt.subplots_adjust(top=1.0)

    radius = 5
    inner_radius = radius * 2 / 3
    outer_radius = radius - 0.2

    # Draw circles
    circle_outer = plt.Circle((0, 0), radius, color='black', fill=False, linewidth=2)
    circle_inner = plt.Circle((0, 0), inner_radius, color='black', fill=False, linewidth=0.5)
    ax.add_artist(circle_outer)
    ax.add_artist(circle_inner)

    n_sectors = 11
    angle_step = 360 / n_sectors
    sub_angle_step = angle_step / 9

    if base == 'base44':
        n_sectors = 44
        angle_step = 360 / n_sectors
        sub_angle_step = angle_step / 8

    if base == 'base336':
        n_sectors = 10
        angle_step = 360 / n_sectors
        sub_angle_step = angle_step / 9

    # Sector lines and subsegments
    for i in range(n_sectors):
        angle = np.radians(90 - (i * angle_step))
        x = radius * np.cos(angle)
        y = radius * np.sin(angle)
        plt.plot([0, x], [0, y], color='black', linewidth=0.5)

    for i in range(n_sectors):
        for j in range(9):
            angle = np.radians(90 - (i * angle_step + j * sub_angle_step))
            x = radius * np.cos(angle)
            y = radius * np.sin(angle)
            plt.plot([0, x], [0, y], color='grey', linewidth=0.1)

    # Sector labels
    for i in range(n_sectors):
        angle = np.radians(90 - (i * angle_step + angle_step / 2))
        x = (radius - 0.5) * np.cos(angle)
        y = (radius - 0.5) * np.sin(angle)
        plt.text(x, y, str(i), fontsize=8, ha='center', va='center', color='black')

    # Draw rates
    for sector, position in rates:
        base_angle = 90 - (sector * angle_step)
        angle = np.radians(base_angle - (position - 1) * sub_angle_step)
        x_inner = inner_radius * np.cos(angle)
        y_inner = inner_radius * np.sin(angle)
        x_outer = outer_radius * np.cos(angle)
        y_outer = outer_radius * np.sin(angle)
        plt.plot([x_inner, x_outer], [y_inner, y_outer], color='red', linewidth=2)

    # Set axis limits
    ax.set_xlim(-radius - 0.5, radius + 0.5)
    ax.set_ylim(-radius - 0.5, radius + 0.5)
    ax.set_aspect('equal', adjustable='box')
    plt.axis('off')

    if output_file:
        plt.savefig(output_file, dpi=300, bbox_inches='tight', pad_inches=0, transparent=False)

        # Resize to exact dimensions
        img = Image.open(output_file)
        img_resized = img.resize((755, 755), Image.LANCZOS)

        # Define the top border size (e.g., 50 pixels)
        top_border_size = 50

        # Create a new white background image with the same width and additional height for the top border
        new_height = img_resized.height + top_border_size
        background_adjusted = Image.new("RGB", (img_resized.width, new_height), "white")

        # Paste the original image onto the white background, leaving space at the top
        background_adjusted.paste(img_resized, (0, top_border_size))

        # Create a drawing object
        draw = ImageDraw.Draw(background_adjusted)

        try:
            # Try to load a truetype font dynamically
            font = ImageFont.truetype("arial.ttf", 20)  # Common font name
        except IOError:
            # Fallback to the default Pillow font if no truetype font is available
            font = ImageFont.load_default()

        draw.text((10, 770), 'AetherOnePy', font=font, fill=(211, 211, 211))
        draw.text((560, 770), 'Radionics Rate Card', font=font, fill=(211, 211, 211))

        rates_text = ""
        pos = 0

        for rate in rates:
            rates_text += str(rate[0])
            pos += 1
            if pos < len(rates):
                rates_text += " - "

        text_width = font.getlength(rates_text)
        print(text_width)
        draw.text(((755/2) - (text_width/2), 80), rates_text, font=font, fill="red")

        background_adjusted.save(output_file)

        print(f"Chart saved as {output_file}")


def parse_input(input_string):
    """
    Parses the input string into a list of (sector, position) tuples.
    """
    rates = []
    try:
        for position, num in enumerate(input_string.split(), 1):
            sector = float(num)
            if 0.0 <= sector <= 10.999:
                rates.append((sector, position))
            else:
                raise ValueError(f"Sector {num} out of range (0-10)")
    except ValueError as e:
        print(f"Input Error: {e}")
        return []
    return rates

def main():
    print("Radionic Chart Generator (Command Line Version)")
    input_string = '10.34 5.75 1.5 4.65'
    rates = parse_input(input_string)
    draw_radionic_chart('ChelidoniumBase10', rates, 'base10', f"../../data/rate-cards/ChelidoniumBase10.png")
    draw_radionic_chart('ChelidoniumBase44', rates, 'base44', f"../../data/rate-cards/ChelidoniumBase44.png")
    draw_radionic_chart('ChelidoniumBase336', rates, 'base336', f"../../data/rate-cards/ChelidoniumBase336.png")

if __name__ == "__main__":
    main()
