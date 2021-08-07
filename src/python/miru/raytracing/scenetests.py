from miru.raytracing.scene import render_scene

import os


def run_scenes_tests():
	test_folder = "miru_test_results"

	miru_folder = os.environ["MIRU_PROJ_PATH"]
	
	if not os.path.exists(test_folder):
		os.makedirs(test_folder)

	# 1o Test: scenes/test/four_spheres_in_corners.scene
	scene_file = os.path.join(miru_folder, "scenes/test/four_spheres_in_corners.scene")
	image_path = os.path.join(test_folder, "four_spheres_in_corners.png")
	
	render_scene(scene_file, image_path)


if __name__ == '__main__':
	run_scenes_tests()
