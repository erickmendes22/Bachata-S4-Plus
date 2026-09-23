cmake_minimum_required(VERSION 3.22)
project(bachata_reverse_source LANGUAGES CXX)

# Reconstructed source layer for the validated Bachata S4+ Box64 runtime.
# Public shadPS4 interfaces may be supplied as a compile-time reference SDK.
# This does not make the reference tree the Bachata runtime source.

set(BACHATA_REFERENCE_ROOT "" CACHE PATH "Optional shadPS4 reference tree used only for headers")

add_library(bachata_reverse_patches STATIC
    src/order1886_patches.cpp
    src/srt_duplicate_table.cpp
    src/per_vertex_aux_gs.cpp
    src/per_vertex_integration.cpp
    src/fragment_input_layout.cpp
    src/aux_gs_cache.cpp
    src/pipeline_aux_gs.cpp
)

target_include_directories(bachata_reverse_patches PUBLIC include)
target_compile_features(bachata_reverse_patches PUBLIC cxx_std_20)

if(BACHATA_REFERENCE_ROOT)
    target_include_directories(bachata_reverse_patches PRIVATE
        "${BACHATA_REFERENCE_ROOT}/src"
        "${BACHATA_REFERENCE_ROOT}/externals/sirit/include"
        "${BACHATA_REFERENCE_ROOT}/externals/Vulkan-Headers/include"
        "${BACHATA_REFERENCE_ROOT}/externals/magic_enum/include"
        "${BACHATA_REFERENCE_ROOT}/externals/fmt/include"
    )
    target_compile_definitions(bachata_reverse_patches PRIVATE
        BACHATA_REFERENCE_COMPILE=1
    )
endif()

if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
    target_compile_options(bachata_reverse_patches PRIVATE
        -Wall -Wextra -Wpedantic
    )
endif()
