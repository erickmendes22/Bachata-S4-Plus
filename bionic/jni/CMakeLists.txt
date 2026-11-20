cmake_minimum_required(VERSION 3.22)
project(BachataNativeBridge LANGUAGES CXX)
# Exact JNI contract recovered from Bachata S4 Release 0.2.5.
# Generic Bionic core integration is a separate target, not an alias for the
# per-game libmain.so from Uncharted.
add_library(bachata_native_runtime SHARED bachata_native_bridge.cpp)
set_target_properties(bachata_native_runtime PROPERTIES
    CXX_STANDARD 17
    CXX_STANDARD_REQUIRED ON
    CXX_VISIBILITY_PRESET hidden
    VISIBILITY_INLINES_HIDDEN ON)
target_compile_options(bachata_native_runtime PRIVATE -Wall -Wextra -Werror -O2)
target_link_libraries(bachata_native_runtime PRIVATE android log dl)
