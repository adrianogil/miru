cpp_flags = -std=c++0x
miru_path = ../miru/
miru_includes = -I../
png_libconfig = `libpng-config --ldflags` 

build-tests:
	g++ -c $(cpp_flags) $(miru_path)/engine/vector.cpp $(miru_path)/test/test_vector.cpp $(miru_includes)
	g++ -o test_vector vector.o test_vector.o 
	g++ -c $(cpp_flags) $(miru_path)/engine/matrix.cpp $(miru_path)/test/test_matrix.cpp $(miru_includes)
	g++ -o test_matrix matrix.o test_matrix.o 
	g++ -c $(cpp_flags) $(miru_path)/imaging/image_pngpp.cpp $(miru_path)/test/test_image.cpp $(miru_includes)
	g++ -o test_image image_pngpp.o test_image.o $(png_libconfig)

clean: clean-objs clean-tests

clean-tests:
	rm test_*

clean-objs:	
	rm -rf *.o