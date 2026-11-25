#!/usr/bin/env python3
"""Regression tests for production Order metadata state and dispatch selection."""
import argparse
from pathlib import Path
import subprocess
import tempfile


parser = argparse.ArgumentParser()
parser.add_argument("--source", required=True, type=Path)
args = parser.parse_args()
source = args.source.resolve() / "src"
rasterizer = (source / "video_core/renderer_vulkan/vk_rasterizer.cpp").read_text()
begin = rasterizer.index("bool Rasterizer::IsComputeMetaClear(")
end = rasterizer.index("bool Rasterizer::IsComputeImageCopy(", begin)
production_dispatch = rasterizer[begin:end]

code = r'''
#include "video_core/texture_cache/surface_metadata.h"
#include <array>
#include <cassert>
#include <cstddef>
#include <cstdint>
#include <iostream>
#include <limits>
#include <vector>

using u32 = std::uint32_t;
using u64 = std::uint64_t;
using VAddr = std::uintptr_t;
using Metadata = VideoCore::SurfaceMetadata;
using Type = Metadata::Type;
namespace boost::container {
template<class T, std::size_t> using small_vector = std::vector<T>;
}
namespace Shader {
enum class SwStage { Compute };
}
#define LOG_TRACE(...) do {} while (false)

struct Sharp {
    VAddr base_address : 44;
    u32 size;
    u32 GetSize() const { return size; }
};
struct BufferDesc {
    bool is_written;
    bool special;
    Sharp sharp;
    bool IsSpecial() const { return special; }
    Sharp GetSharp(const auto&) const {
        assert(!special); // Special resources do not carry guest buffer descriptors.
        return sharp;
    }
};
struct ImageDesc { bool is_written; };
struct Stage {
    bool has_bitwise_xor{};
    std::vector<BufferDesc> buffers;
    std::vector<ImageDesc> images;
};
struct Pipeline {
    bool compute{true};
    Stage stage;
    bool IsCompute() const { return compute; }
    const Stage& GetStage(Shader::SwStage) const { return stage; }
};
struct Memory {
    VAddr short_address{};
    u64 ClampRangeSize(VAddr address, u64 size) const {
        return address == short_address && size ? size - 1 : size;
    }
};
struct TextureCache {
    Metadata metadata;
    auto IsMeta(VAddr address) const { return metadata.TypeAt(address); }
    bool ClearMetaBatch(std::span<const Metadata::ClearRange> ranges) {
        return metadata.ClearBatch(ranges);
    }
};
struct Rasterizer {
    TextureCache texture_cache;
    Memory* memory;
    bool IsComputeMetaClear(const Pipeline* pipeline);
};
'''
code += production_dispatch
code += r'''

void StateTests() {
    Metadata meta;
    constexpr VAddr a = 0x10000, b = 0x20000, c = 0x30000;
    meta.Register(a, 1, Type::CMask);
    assert(meta.TypeAt(a) == Type::CMask && meta.IsCleared(a, 0));
    assert(meta.Touch(a, 0, false));
    assert(!meta.Touch(a, 0, false));
    // The same image rebound must retain dirty slices; slot reuse must not.
    meta.Register(a, 1, Type::CMask);
    assert(!meta.IsCleared(a, 0));
    meta.Register(a, 2, Type::CMask);
    assert(meta.IsCleared(a, 0));
    meta.Erase(a, 1);
    assert(meta.TypeAt(a));
    meta.Erase(a, 2);
    assert(!meta.TypeAt(a));

    meta.Register(a, 3, Type::HTile, 0);
    meta.Fill(a, 64, 0xfffff3ff);
    assert(!meta.IsCleared(a, 0)); // expanded stencil HTILE is not a clear
    meta.Fill(a, 64, 0xfffff3f0);
    assert(meta.IsCleared(a, 0));
    meta.Write(a + 64, 1);
    assert(meta.IsCleared(a, 0)); // adjacent, not overlapping
    meta.Write(a + 60, 4);
    assert(!meta.IsCleared(a, 0)); // interior write invalidates a known extent
    meta.Fill(a, 64, 0xfffc0000);
    assert(meta.IsCleared(a, 0));
    meta.Fill(a, 64, 0xfffc000f);
    assert(!meta.IsCleared(a, 0)); // expanded depth HTILE is not a clear
    assert(meta.Clear(a, 64));
    assert(meta.IsCleared(a, 0));
    assert(!meta.Touch(a, 32, false));
    assert(!meta.IsCleared(a, 0) && !meta.IsCleared(a, 32));
    assert(!meta.Clear(a, 0) && !meta.Clear(a, 62) && !meta.Clear(a + 1, 64));
    assert(!meta.IsCleared(a, 0));
    assert(!meta.Clear(a, std::numeric_limits<u64>::max() - 3));
    assert(!meta.IsCleared(a, 0));
    assert(meta.Clear(a, 64));
    meta.Unmap(a + 64, 4);
    assert(meta.TypeAt(a));
    meta.Unmap(a + 63, 1);
    assert(!meta.TypeAt(a));

    meta.Register(a, 4, Type::CMask, 0);
    meta.Register(b, 5, Type::HTile, 0, 2);
    const std::array ranges{Metadata::ClearRange{a, 64}, Metadata::ClearRange{b, 64}};
    assert(!meta.ClearBatch(ranges)); // no partial commit before an unsupported output
    assert(!meta.IsCleared(a, 0) && !meta.IsCleared(b, 0));
    meta.Register(b, 5, Type::HTile, 0, 1);
    assert(meta.ClearBatch(ranges));
    assert(meta.IsCleared(a, 0) && meta.IsCleared(b, 0));
    // The entire extent of the first clear invalidates another registered alias.
    meta.Register(c, 6, Type::FMask, 0);
    meta.Register(c + 4, 7, Type::CMask);
    assert(meta.Clear(c, 16));
    assert(meta.IsCleared(c, 0) && !meta.IsCleared(c + 4, 0));
    meta.Fill(c, 16, 0xffffffff);
    assert(meta.IsCleared(c, 0)); // CMask/FMask retain donor fill behavior
    meta.Write(c, 16);
    assert(!meta.IsCleared(c, 0));
    meta.Register(c, 6, Type::FMask, ~0u);
    assert(!meta.IsCleared(c, 0));
    meta.Register(c, 6, Type::CMask, ~0u);
    assert(meta.IsCleared(c, 0)); // changing type resets the association
}

void DispatchTests() {
    Memory memory;
    Rasterizer r{{}, &memory};
    auto& meta = r.texture_cache.metadata;
    constexpr VAddr a = 0x10000, b = 0x20000, unknown = 0x30000;
    meta.Register(a, 1, Type::HTile, 0);
    meta.Register(b, 2, Type::CMask, 0);
    Pipeline p;
    p.stage.buffers = {{true, false, {a, 64}}, {true, false, {unknown, 64}}};
    assert(!r.IsComputeMetaClear(&p));
    assert(!meta.IsCleared(a, 0)); // old code skipped the real second buffer write
    p.stage.buffers[1].sharp.base_address = b;
    assert(r.IsComputeMetaClear(&p));
    assert(meta.IsCleared(a, 0) && meta.IsCleared(b, 0));

    meta.Write(a, 64);
    meta.Write(b, 64);
    memory.short_address = b;
    assert(!r.IsComputeMetaClear(&p));
    assert(!meta.IsCleared(a, 0) && !meta.IsCleared(b, 0));
    memory.short_address = 0;
    p.stage.images = {{true}};
    assert(!r.IsComputeMetaClear(&p)); // storage-image work must execute
    assert(!meta.IsCleared(a, 0));
    p.stage.images.clear();
    p.stage.buffers.push_back({false, false, {a, 64}});
    assert(!r.IsComputeMetaClear(&p)); // metadata inspection/copy must execute
    p.stage.buffers.back() = {true, true, {unknown, 64}};
    assert(!r.IsComputeMetaClear(&p)); // a special output must execute
    assert(!meta.IsCleared(a, 0));
    p.stage.buffers.back().is_written = false;
    p.stage.has_bitwise_xor = true;
    assert(!r.IsComputeMetaClear(&p));
    p.stage.has_bitwise_xor = false;
    p.compute = false;
    assert(!r.IsComputeMetaClear(&p));
    p.compute = true;
    assert(r.IsComputeMetaClear(&p)); // special read needs no buffer sharp fetch
    p.stage.buffers.clear();
    assert(!r.IsComputeMetaClear(&p));
    p.stage.buffers = {{false, false, {unknown, 64}}};
    assert(!r.IsComputeMetaClear(&p)); // no output is not a metadata clear
}

int main() {
    StateTests();
    DispatchTests();
    std::cout << "BACHATA_ORDER_METADATA_PROTOCOL_PASS\n";
}
'''

with tempfile.TemporaryDirectory() as directory:
    directory = Path(directory)
    cpp = directory / "metadata.cpp"
    binary = directory / "metadata"
    cpp.write_text(code)
    subprocess.run(["c++", "-std=c++20", "-O2", "-Wall", "-Wextra", "-Werror",
                    "-I", str(source), str(cpp), "-o", str(binary)], check=True)
    subprocess.run([str(binary)], check=True)
