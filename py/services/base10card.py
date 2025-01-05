import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
import os

def draw_radionic_chart(rates, output_file=None):
    """
    Draws a radionic chart based on the provided rates and optionally saves it as an image.
    """
    fig, ax = plt.subplots(figsize=(6, 6))
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
            plt.plot([0, x], [0, y], color='black', linewidth=0.2)

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
        plt.plot([x_inner, x_outer], [y_inner, y_outer], color='red', linewidth=0.5)

    # Set axis limits
    ax.set_xlim(-radius - 0.5, radius + 0.5)
    ax.set_ylim(-radius - 0.5, radius + 0.5)
    ax.set_aspect('equal', adjustable='box')
    plt.axis('off')

    if output_file:
        plt.savefig(output_file, dpi=300, bbox_inches='tight', pad_inches=0, transparent=True)

        # Resize to exact dimensions
        img = Image.open(output_file)
        img_resized = img.resize((755, 755), Image.LANCZOS)
        img_resized.save(output_file)
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
    while True:
        input_string = input("Enter Rates (space-separated, 0-10, or 'q' to quit): ")
        if input_string.lower() == 'q':
            print("Exiting...")
            break

        rates = parse_input(input_string)

        if rates:
            output_file = f"radionic_chart_{input_string.replace(' ', '_')}.png"
            draw_radionic_chart(rates, output_file)

if __name__ == "__main__":
    main()
