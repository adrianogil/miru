cpp_flags = -std=c++0x

build:
	g++ -c $(cpp_flags) vector.cpp test_vector.cpp 
	g++ -o test_vector vector.o test_vector.o 
	g++ -c $(cpp_flags) matrix.cpp test_matrix.cpp 
	g++ -o test_matrix matrix.o test_matrix.o 

clean:
	rm -rf *.o