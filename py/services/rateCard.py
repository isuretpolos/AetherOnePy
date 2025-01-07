import matplotlib.pyplot as plt
import numpy as np
from io import BytesIO
from PIL import Image, ImageFont, ImageDraw

# Thanks to Benjamin Ludwig!!!

class RadionicChart:
    def __init__(self, rate_text, base='base10'):
        """
        Initialize the RadionicChart class.
        """
        self.rate_text = rate_text
        self.base = base
        self.radius = 5
        self.inner_radius = self.radius * 2 / 3
        self.outer_radius = self.radius - 0.2
        self.n_sectors, self.angle_step, self.sub_angle_step = self._configure_base()

    def _configure_base(self):
        """
        Configure the chart base parameters based on the base type.
        """
        if self.base == 'base44':
            n_sectors = 44
            angle_step = 360 / n_sectors
            sub_angle_step = angle_step / 8
        elif self.base == 'base336':
            n_sectors = 10
            angle_step = 360 / n_sectors
            sub_angle_step = angle_step / 9
        else:  # Default is base10
            n_sectors = 11
            angle_step = 360 / n_sectors
            sub_angle_step = angle_step / 9
        return n_sectors, angle_step, sub_angle_step

    def draw_chart(self, rates):
        """
        Draw the radionic chart with the provided rates.
        """
        fig, ax = plt.subplots(figsize=(6, 6))
        fig.patch.set_facecolor('white')
        fig.suptitle(self.rate_text, fontsize=14)
        plt.subplots_adjust(top=1.0)

        # Draw circles
        circle_outer = plt.Circle((0, 0), self.radius, color='black', fill=False, linewidth=2)
        circle_inner = plt.Circle((0, 0), self.inner_radius, color='black', fill=False, linewidth=0.5)
        ax.add_artist(circle_outer)
        ax.add_artist(circle_inner)

        # Draw sector lines and subsegments
        self._draw_sectors(ax)

        # Add rates
        self._draw_rates(ax, rates)

        # Set axis properties
        ax.set_xlim(-self.radius - 0.5, self.radius + 0.5)
        ax.set_ylim(-self.radius - 0.5, self.radius + 0.5)
        ax.set_aspect('equal', adjustable='box')
        plt.axis('off')

        # Render the chart to an Image object
        return self._render_to_image(fig, rates)

    def _draw_sectors(self, ax):
        """
        Draw sectors and subsegments for the chart.
        """
        for i in range(self.n_sectors):
            angle = np.radians(90 - (i * self.angle_step))
            x = self.radius * np.cos(angle)
            y = self.radius * np.sin(angle)
            plt.plot([0, x], [0, y], color='black', linewidth=0.5)

            for j in range(9):
                angle = np.radians(90 - (i * self.angle_step + j * self.sub_angle_step))
                x = self.radius * np.cos(angle)
                y = self.radius * np.sin(angle)
                plt.plot([0, x], [0, y], color='grey', linewidth=0.1)

        for i in range(self.n_sectors):
            angle = np.radians(90 - (i * self.angle_step + self.angle_step / 2))
            x = (self.radius - 0.5) * np.cos(angle)
            y = (self.radius - 0.5) * np.sin(angle)
            plt.text(x, y, str(i), fontsize=8, ha='center', va='center', color='black')

    def _draw_rates(self, ax, rates):
        """
        Draw the rates on the chart.
        """
        for sector, position in rates:
            base_angle = 90 - (sector * self.angle_step)
            angle = np.radians(base_angle - (position - 1) * self.sub_angle_step)
            x_inner = self.inner_radius * np.cos(angle)
            y_inner = self.inner_radius * np.sin(angle)
            x_outer = self.outer_radius * np.cos(angle)
            y_outer = self.outer_radius * np.sin(angle)
            plt.plot([x_inner, x_outer], [y_inner, y_outer], color='red', linewidth=2)

    def _render_to_image(self, fig, rates):
        """
        Render the chart to an in-memory Image object and return it.
        """
        # Save figure to a BytesIO buffer
        buf = BytesIO()
        fig.savefig(buf, format='png', dpi=300, bbox_inches='tight', pad_inches=0, transparent=False)
        buf.seek(0)
        plt.close(fig)

        # Open the image from the buffer
        img = Image.open(buf)

        # Resize and add additional details
        img_resized = img.resize((755, 755), Image.LANCZOS)
        new_height = img_resized.height + 50
        background_adjusted = Image.new("RGB", (img_resized.width, new_height), "white")
        background_adjusted.paste(img_resized, (0, 50))
        draw = ImageDraw.Draw(background_adjusted)

        try:
            font = ImageFont.truetype("arial.ttf", 20)
        except IOError:
            font = ImageFont.load_default()

        draw.text((10, 770), 'AetherOnePy', font=font, fill=(211, 211, 211))
        draw.text((560, 770), 'Radionics Rate Card', font=font, fill=(211, 211, 211))
        rates_text = " - ".join(str(rate[0]) for rate in rates)
        text_width = font.getlength(rates_text)
        draw.text(((755 / 2) - (text_width / 2), 80), rates_text, font=font, fill="red")

        return background_adjusted

    @staticmethod
    def parse_input(input_string):
        """
        Parses the input string into a list of (sector, position) tuples.
        """
        rates = []
        try:
            for position, num in enumerate(input_string.split(), 1):
                sector = float(num)
                rates.append((sector, position))
        except ValueError as e:
            print(f"Input Error: {e}")
            return []
        return rates


# Example Usage
if __name__ == "__main__":
    input_string = '10.34 5.75 1.5 4.65'
    rates = RadionicChart.parse_input(input_string)

    chart = RadionicChart('ChelidoniumBase10', 'base10')
    image = chart.draw_chart(rates)

    # Show the image (for testing)
    image.show()
