from .transform import Transform


class Camera:
    ORTOGRAPHIC = 1
    PERSPECTIVE = 2

    def __init__(self):
        self.mode = Camera.PERSPECTIVE
        self.fov = 60

        self.near = 0.01
        self.far = 1000

        self.transform = Transform()

    @staticmethod
    def parse(data):

        c = Camera()

        if 'mode' in data:
            if data['mode'] == "perspective":
                c.mode = Camera.PERSPECTIVE
            else:
                c.mode = Camera.ORTOGRAPHIC

        if 'fov' in data:
            c.fov = int(data['fov'])

        if 'near' in data:
            c.near = float(data['near'])

        if 'far' in data:
            c.far = float(data['far'])

        if 'transform' in data:
            c.transform.parse(data['transform'])

        return c
