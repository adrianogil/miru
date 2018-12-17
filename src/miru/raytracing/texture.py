from PIL import Image

from color import Color

import numpy as np

class Texture:
    def __init__(self, image_path):
        self.image_path = image_path
        self.load()

    def load(self):
        self.image = Image.open(self.image_path)
        image_size = self.image.size
        self.width = image_size[0]
        self.height = image_size[1]
        self.pixels = self.image.load()
        self.aspect_ratio = self.width * 1.0 / self.height

    def tex2D(self, uv):
        px = int(uv.x * (self.width-1)) 
        py = int(uv.y * (self.height-1))

        # Adjust py (UV.y is inverted)
        py = self.height - py - 1

        px = np.mod(px + self.width, self.width)
        py = np.mod(py + self.height, self.height)

        # print("px: " + str(px))
        # print("py: " + str(py))

        color = self.pixels[px,py]

        return Color(color[0]*1.0/255,color[1]*1.0/255,color[2]*1.0/255,1.0)