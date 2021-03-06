cpp_flags = -std=c++0x

miru_path = ../miru/
lodepng_path = ../dependencies/lodepng
oneweekend_path=$(miru_path)/oneweekend/

miru_includes = -I../ -I../dependencies/
lodepng_includes=-
oneweekend_includes=-I${oneweekend_path}

png_libconfig = `libpng-config --ldflags`

build-tests: build-test-vector build-test-matrix build-test-image build-test-scene

build-test-vector:
	g++ -c $(cpp_flags) $(miru_path)/engine/vector.cpp $(miru_path)/test/test_vector.cpp $(miru_includes)
	g++ -o test_vector vector.o test_vector.o

build-test-matrix:
	g++ -c $(cpp_flags) $(miru_path)/engine/matrix.cpp $(miru_path)/test/test_matrix.cpp $(miru_includes)
	g++ -o test_matrix matrix.o test_matrix.o

build-test-image:
	g++ -c $(cpp_flags) $(miru_path)/imaging/image_pngpp.cpp $(miru_path)/test/test_image.cpp $(miru_includes)
	g++ -o test_image image_pngpp.o test_image.o $(png_libconfig)

build-test-scene:
	g++ -c $(cpp_flags) $(miru_path)/imaging/*.cpp $(miru_path)/engine/*.cpp $(miru_path)/test/test_scene.cpp $(miru_includes)
	g++ -o test_scene *.o $(png_libconfig)

build-test-raymarching-sphere: build-image-lodepng
	g++ -c $(cpp_flags) $(miru_path)/engine/*.cpp $(miru_path)/raymarching/*.cpp $(miru_path)/test/test_raymarching_sphere.cpp $(miru_includes)
	g++ -o test_raymarching_sphere *.o $(png_libconfig)

build-test-raymarching: build-image-lodepng
	g++ -c $(cpp_flags) $(miru_path)/engine/*.cpp $(miru_path)/raymarching/*.cpp $(miru_path)/test/test_raymarching.cpp $(miru_includes)
	g++ -o test_raymarching *.o $(png_libconfig)

build-image-pngpp:
	g++ -c  $(cpp_flags) $(miru_includes) $(miru_path)/imaging/image_pngpp.cpp

build-image-lodepng:
	g++ -c  $(cpp_flags) $(miru_includes) $(miru_path)/imaging/image_lodepng.cpp $(lodepng_path)/lodepng.cpp

build-wknd:
	g++ -c ${oneweekend_path}/test_ppm.cpp ${oneweekend_includes}
	g++ -o test_wknd_ppm test_ppm.o
	g++ -c ${oneweekend_path}/main.cpp ${oneweekend_includes}
	g++ -o main main.o

clean: clean-objs clean-tests

clean-tests:
	rm test_*

clean-objs:
	rm -rf *.o