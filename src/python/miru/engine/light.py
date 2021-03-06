from .transform import Transform
from .color import Color


class Light:
    def __init__(self, color=None, intensity=1.0):
        if color is None:
            self.color = Color.white()
        else:
            self.color = color

        self.intensity = intensity
        self.transform = Transform()

    @staticmethod
    def parse(data):
        light = Light()

        if 'color' in data:
            light.color = Color.from_array(data['color'])

        if 'intensity' in data:
            light.intensity = float(data['intensity'])

        if 'transform' in data:
            light.transform.parse(data['transform'])

        return light
