import json

class SceneParser:
    def __init__(self, objects_parser):
        # objects_parser is a dictionary by type name
        self.objects_parser = objects_parser

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
