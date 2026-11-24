// SPDX-License-Identifier: GPL-2.0-or-later
#include "driver_cache_file.h"
#include <cassert>
int main() {
    using namespace Vulkan::DriverCacheFile;
    Identity id{0x5143,0x830,123,{1,2,3}};
    std::vector<std::uint8_t> payload(64,0);
    const std::array<std::uint32_t,4> header{32,1,id.vendor,id.device};
    std::memcpy(payload.data(),header.data(),16);
    std::memcpy(payload.data()+16,id.uuid.data(),16);
    assert(ValidPayload(payload,id));
    const auto encoded=Encode(payload,id);
    assert(Decode(encoded,id)==payload);
    auto other=id; ++other.driver;
    assert(Decode(encoded,other).empty());
    other=id; ++other.uuid[0];
    assert(Decode(encoded,other).empty());
    auto corrupt=encoded; corrupt.back()^=1;
    assert(Decode(corrupt,id).empty());
    assert(Decode(std::span<const std::uint8_t>{encoded}.first(30),id).empty());
    auto path=std::filesystem::temp_directory_path()/"bachata-driver-cache-test"/"cache.bin";
    assert(Save(path,payload,id));
    assert(Load(path,id)==payload);
    payload.back()=42;
    assert(Save(path,payload,id));
    assert(Load(path,id)==payload);
    std::filesystem::remove_all(path.parent_path());
}
