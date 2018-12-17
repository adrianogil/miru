import json

from miru.engine.material import Material


class SceneParser:
    def __init__(self, objects_parser):
        # objects_parser is a dictionary by type name
        self.objects_parser = objects_parser
        self.target_scene = None

    def parse(self, scene_file, target_scene):
        print("SceneParser - parsing - " + str(scene_file))
        with open(scene_file, 'r') as f:
            scene_data = json.load(f)

        if 'camera' in scene_data:
            c = self.objects_parser["camera"](scene_data["camera"])
            target_scene.set_camera(c)

        for o in scene_data["objects"]:
            print(o['type'])
            if o['type'] in self.objects_parser:
                new_obj = self.objects_parser[o['type']](o)
                if new_obj is not None:
                    target_scene.add_objects(new_obj)

                    if 'material' in o:
                        new_obj.material = Material.parse(o['material'])

        if 'render' in scene_data:
            render_data = scene_data['render']
            if 'height' in render_data:
                target_scene.render_height = render_data['height']

            if 'width' in render_data:
                target_scene.render_width = render_data['width']

            if 'to_image' in render_data:
                target_scene.target_image_file = render_data['to_image']
