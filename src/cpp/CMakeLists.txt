# Specify the minimum version for CMake
cmake_minimum_required(VERSION 2.8)

# Project's name
project(hello)

# Set the output folder where package will be created
set(CMAKE_BINARY_DIR ${CMAKE_SOURCE_DIR}/bin/)
set(EXECUTABLE_OUTPUT_PATH ${CMAKE_BINARY_DIR})
set(LIBRARY_OUTPUT_PATH ${CMAKE_BINARY_DIR})

file(GLOB MIRU_SRC
     "${PROJECT_SOURCE_DIR}/miru/basic/*.h"
     "${PROJECT_SOURCE_DIR}/miru/basic/*.cpp"
     "${PROJECT_SOURCE_DIR}/miru/engine/*.h"
     "${PROJECT_SOURCE_DIR}/miru/engine/*.cpp"
     "${PROJECT_SOURCE_DIR}/miru/imaging/image.h"
     "${PROJECT_SOURCE_DIR}/miru/imaging/image_lodepng.cpp"
     "${PROJECT_SOURCE_DIR}/miru/raymarching/*.h"
     "${PROJECT_SOURCE_DIR}/miru/raymarching/*.cpp"
     "${PROJECT_SOURCE_DIR}/miru/raymarching/*.cpp"
     "${PROJECT_SOURCE_DIR}/miru/test/test_raymarching.cpp"
     "${PROJECT_SOURCE_DIR}/dependencies/lodepng/lodepng.h"
     "${PROJECT_SOURCE_DIR}/dependencies/lodepng/lodepng.cpp"
)

# The following folder will be included
include_directories("${PROJECT_SOURCE_DIR}" "${PROJECT_SOURCE_DIR}/dependencies/")

add_executable(miru ${MIRU_SRC})