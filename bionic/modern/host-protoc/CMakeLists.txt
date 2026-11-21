cmake_minimum_required(VERSION 3.24)
project(bachata_pinned_host_protoc LANGUAGES C CXX)

# Build the host tool from the *identical* source revision used by the NDK
# runtime. The shadPS4 protobuf pin is an unreleased intermediate snapshot:
# neither official protoc 35.1 nor 36.0 generates ABI-compatible code.
if(NOT SHADPS4_SOURCE_ROOT)
  message(FATAL_ERROR "SHADPS4_SOURCE_ROOT must point to pinned modern-core")
endif()

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_POSITION_INDEPENDENT_CODE ON)
set(ABSL_ENABLE_INSTALL OFF CACHE BOOL "" FORCE)
set(ABSL_PROPAGATE_CXX_STD ON CACHE BOOL "" FORCE)
set(ABSL_BUILD_TESTING OFF CACHE BOOL "" FORCE)

add_subdirectory("${SHADPS4_SOURCE_ROOT}/externals/abseil-cpp" absl)
set(protobuf_BUILD_TESTS OFF CACHE BOOL "" FORCE)
set(protobuf_BUILD_EXAMPLES OFF CACHE BOOL "" FORCE)
set(protobuf_BUILD_CONFORMANCE OFF CACHE BOOL "" FORCE)
set(protobuf_INSTALL OFF CACHE BOOL "" FORCE)
set(protobuf_BUILD_SHARED_LIBS OFF CACHE BOOL "" FORCE)
set(protobuf_WITH_ZLIB OFF CACHE BOOL "" FORCE)
set(protobuf_FORCE_FETCH_DEPENDENCIES OFF CACHE BOOL "" FORCE)
set(protobuf_LOCAL_DEPENDENCIES_ONLY ON CACHE BOOL "" FORCE)
set(protobuf_BUILD_PROTOC_BINARIES ON CACHE BOOL "" FORCE)
add_subdirectory("${SHADPS4_SOURCE_ROOT}/externals/protobuf" protobuf)

if(NOT TARGET protoc)
  message(FATAL_ERROR "Pinned host protobuf did not define protoc")
endif()
