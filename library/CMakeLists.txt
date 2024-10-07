cmake_minimum_required(VERSION 3.5)
project(dibidab-header)

file(GLOB_RECURSE source source/*)
add_library(dibidab-header ${source})

target_include_directories(dibidab-header PUBLIC include/)

set_property(TARGET dibidab-header PROPERTY LINKER_LANGUAGE CXX)
set_property(TARGET dibidab-header PROPERTY CXX_STANDARD 17)
set_property(TARGET dibidab-header PROPERTY CXX_STANDARD_REQUIRED ON)

if (MSVC)
    set(CMAKE_CXX_FLAGS  "/Ox /EHsc /bigobj /D NDEBUG")
else()
    set(CMAKE_CXX_FLAGS  "-B /usr/libexec/mold")
endif()
