cmake_minimum_required(VERSION 3.22)
project(bachata_reverse_source LANGUAGES CXX)

# This target is intentionally a reconstruction layer, not yet a standalone
# shadPS4 replacement. It is linked into the reconstructed runtime tree once
# the public-interface-compatible headers are populated.

add_library(bachata_reverse_patches STATIC
    src/order1886_patches.cpp
    src/srt_duplicate_table.cpp
)

target_include_directories(bachata_reverse_patches PUBLIC include)
target_compile_features(bachata_reverse_patches PUBLIC cxx_std_20)
