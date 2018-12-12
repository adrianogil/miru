from engine.transform import Transform
from engine.color import Color

class SDFCube:
    def __init__(self, size):
        self.size = size
        self.transform = Transform()
        self.color = Color.random()

    def pre_render(self):
        pass

    def distance(self, position):

        x = max(
            position.x - self.transform.position.x - self.size.x / 2.0,
            self.transform.position.x - position.x - self.size.x / 2.0
            )

        y = max(
            position.y - self.transform.position.y - self.size.y / 2.0,
            self.transform.position.y - position.y - self.size.y / 2.0
            )

        z = max(
            position.z - self.transform.position.z - self.size.z / 2.0,
            self.transform.position.z - position.z - self.size.z / 2.0
            )

        d = max(x, y)
        d = max(d, z)

        # print("SDFCube - distance - " + str(position) + " - " + str(d))

        return d

    def render(self, scene, position):
        return self.color;

