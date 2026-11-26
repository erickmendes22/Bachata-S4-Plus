"""Verify the actual selective VRS geometry policy and set-path integration."""
import argparse,subprocess,tempfile
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument("--source",type=Path,required=True)
root=p.parse_args().source/"src/video_core"
r=(root/"renderer_vulkan/vk_rasterizer.cpp").read_text()
c=(root/"texture_cache/texture_cache.cpp").read_text()
i=(root/"renderer_vulkan/vk_instance.cpp").read_text()
g=(root/"renderer_vulkan/vk_graphics_pipeline.cpp").read_text()
assert "CheckOrderSampledSet(samples,order_set->generation,false)" in r
assert "order_set->key==order_set_key" in r and "memory->MappingGeneration()" in r
assert "needs_barrier|=runtime.Transit" in r
assert "ImageFlagBits::Dirty|ImageFlagBits::Aliased" in c
assert "view.view_uid!=v.view_uid" in c and "v.backing_uid!=image.backing->backing_uid" in c
assert "if(!remember) for(const auto& entry:entries)" in c
assert "order_vrs_supported=add_extension(VK_KHR_FRAGMENT_SHADING_RATE_EXTENSION_NAME)" in i
assert "rate.sampleCounts&vk::SampleCountFlagBits::e1" in i
assert "device_chain.unlink<vk::PhysicalDeviceFragmentShadingRateFeaturesKHR>()" in i
assert "dynamic_states.push_back(vk::DynamicState::eFragmentShadingRateKHR)" in g
assert "SetOrderVrs(pipeline,state,true,is_indexed)" in r and "SetOrderVrs(pipeline,state,false,is_indexed)" in r
assert "fs->has_discard" in r and "exports.mask_export_enable" in r and "image.is_depth || image.is_written" in r
assert "scheduler.RecordDeferred([rate]" in r and "real.setFragmentShadingRateKHR(rate,ops)" in r
cpp=r'''
#include "renderer_vulkan/order_vrs_parity.h"
#include <cassert>
using Vulkan::OrderVrsGeometry;
int main() {
    assert(OrderVrsGeometry(1280,720,2,false,false,false));
    assert(!OrderVrsGeometry(1280,720,1,true,true,false));
    assert(OrderVrsGeometry(640,360,1,true,true,false));
    assert(!OrderVrsGeometry(640,360,1,false,true,false));
    assert(!OrderVrsGeometry(640,360,1,true,false,false));
    assert(!OrderVrsGeometry(640,360,1,true,true,true));
    assert(!OrderVrsGeometry(640,360,2,true,true,false));
    assert(!OrderVrsGeometry(480,270,2,true,true,false));
}
'''
with tempfile.TemporaryDirectory() as d:
    source=Path(d)/"vrs.cpp";exe=Path(d)/"vrs"
    source.write_text(cpp)
    subprocess.run(["c++","-std=c++20","-Wall","-Wextra","-Werror","-I",str(root),str(source),"-o",str(exe)],check=True)
    subprocess.run([str(exe)],check=True)
print("BACHATA_ORDER_RENDERER_PARITY_PASS")
