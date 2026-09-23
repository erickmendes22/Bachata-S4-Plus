cmake_minimum_required(VERSION 3.22)
project(bachata_reverse_source LANGUAGES CXX)

# Reconstructed source layer for the validated Bachata S4+ Box64 runtime.
# Public shadPS4 interfaces are used as architectural contracts where noted.

add_library(bachata_reverse_patches STATIC
    src/order1886_patches.cpp
    src/srt_duplicate_table.cpp
    src/per_vertex_aux_gs.cpp
)

target_include_directories(bachata_reverse_patches PUBLIC include)
target_compile_features(bachata_reverse_patches PUBLIC cxx_std_20)
