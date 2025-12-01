import random

class ColorManager:
    def __init__(self):
        # Fixed palette as requested by the user
        self.palette = {
            'medium_orange': '#F39C12',  # Medium Orange
            'light_orange': '#F5CBA7',   # Light Orange
            'pink': '#F5B7B1',           # Pink
            'light_red': '#EC7063',      # Light Red
            'light_blue': '#AED6F1',     # Light Blue
            'white': '#FFFFFF'
        }
        
    def adjust_brightness(self, hex_color, factor):
        """
        Adjust the brightness of a hex color.
        factor > 1 lightens the color.
        factor < 1 darkens the color.
        """
        hex_color = hex_color.lstrip('#')
        
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        
        r = max(0, min(255, int(r * factor)))
        g = max(0, min(255, int(g * factor)))
        b = max(0, min(255, int(b * factor)))
        
        return f'#{r:02x}{g:02x}{b:02x}'

    def get_random_theme(self):
        """
        Returns the fixed color palette requested by the user.
        Kept the name 'get_random_theme' for compatibility with existing code.
        """
        # Mapping the fixed palette to the keys expected by the application
        return {
            'base': self.palette['medium_orange'],  # Used for buttons
            'dark': self.palette['light_red'],      # Used for dark backgrounds/borders
            'light': self.palette['pink'],          # Used for light backgrounds
            'lighter': self.palette['light_blue'],  # Used for very light backgrounds (replacing yellow)
            'white': self.palette['white'],
            
            # Additional colors available if needed
            'light_orange': self.palette['light_orange']
        }
