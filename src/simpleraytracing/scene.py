class Scene:
    def __init__(self):
        self.objects = []

    def add_objects(self, obj):
        self.objects.append(obj)

    def render(self, pixel_height, pixel_width, image_file):
        pass