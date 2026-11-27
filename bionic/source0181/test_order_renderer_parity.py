"""Verify the actual selective VRS geometry policy and set-path integration."""
import argparse,subprocess,tempfile
from pathlib import Path
from port_order_selective_vrs import add_vrs_query_feature, ensure_extension_capacity

# The failed revision matched three occurrences, including the unrelated
# get and unlink APIs. Reproduce the collision before building native code.
feature_fixture = """const vk::StructureChain feature_chain = physical_device.getFeatures2<
    vk::PhysicalDeviceFeatures2, vk::PhysicalDeviceShaderClockFeaturesKHR>();
    const auto x = feature_chain.get<vk::PhysicalDeviceShaderClockFeaturesKHR>();
    device_chain.unlink<vk::PhysicalDeviceShaderClockFeaturesKHR>();"""
assert feature_fixture.count("vk::PhysicalDeviceShaderClockFeaturesKHR>();")==3
feature_fixed = add_vrs_query_feature(feature_fixture)
assert feature_fixed.count("vk::PhysicalDeviceFragmentShadingRateFeaturesKHR")==1
assert "get<vk::PhysicalDeviceShaderClockFeaturesKHR>()" in feature_fixed
assert "unlink<vk::PhysicalDeviceShaderClockFeaturesKHR>()" in feature_fixed
assert "vk::PhysicalDeviceShaderClockFeaturesKHR, vk::PhysicalDeviceFragmentShadingRateFeaturesKHR>();" in feature_fixed
try:
    add_vrs_query_feature(feature_fixed)
except RuntimeError:
    pass
else:
    raise AssertionError("Duplicate feature insertion accepted")

for declaration in (
    "boost::container::static_vector<const char*, 32> enabled_extensions;",
    "boost::container::static_vector<const char *, 64> enabled_extensions;",
    "boost::container::static_vector<const char*, 128> enabled_extensions;",
    "std::vector<const char*> enabled_extensions{};",
):
    result=ensure_extension_capacity(declaration)
    assert result==declaration.replace(", 32>",", 64>")
p=argparse.ArgumentParser();p.add_argument("--source",type=Path,required=True)
root=p.parse_args().source/"src/video_core"
r=(root/"renderer_vulkan/vk_rasterizer.cpp").read_text()
rh=(root/"renderer_vulkan/vk_rasterizer.h").read_text()
view_family_start=rh.index("    struct ViewMemoToken {")
view_family_end=rh.index("ViewMemoToken token);",view_family_start)
assert view_family_end<rh.index("    struct OrderTextureSetKey {")
assert "OrderTextureSet" not in rh[view_family_start:view_family_end]
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
