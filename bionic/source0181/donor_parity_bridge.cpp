// SPDX-License-Identifier: GPL-2.0-or-later
// Donor: ShadowOfTheColossus-Android-Aot@6556a9f15747395c13b48a058394b00866989b6e.
#include <cstdint>
#include <span>
#include <variant>
#include "common/logging/log.h"
#include "common/singleton.h"
#include "core/linker.h"
#include "core/libraries/libs.h"
#include "core/memory.h"

extern "C" {
int32_t BachataNgs2SystemCreateWithAllocator(const void* option, const void* allocator, uintptr_t* out);
int32_t BachataNgs2SystemDestroy(uintptr_t handle, void* out);
int32_t BachataNgs2SystemRender(uintptr_t handle, const void* buffers, uint32_t count);
int32_t BachataNgs2RackQueryBufferSize(uint32_t rack_id, const void* option, void* out);
int32_t BachataNgs2RackCreate(uintptr_t system, uint32_t rack_id, const void* option, const void* buffer, uintptr_t* out);
int32_t BachataNgs2RackCreateWithAllocator(uintptr_t system, uint32_t rack_id, const void* option, const void* allocator, uintptr_t* out);
int32_t BachataNgs2RackDestroy(uintptr_t handle, void* out);
int32_t BachataNgs2RackGetVoiceHandle(uintptr_t rack, uint32_t index, uintptr_t* out);
int32_t BachataNgs2VoiceControl(uintptr_t handle, const void* params);
int32_t BachataNgs2VoiceGetState(uintptr_t handle, void* out, uint64_t size);
int32_t BachataNgs2VoiceGetStateFlags(uintptr_t handle, uint32_t* out);
uint64_t BachataNgs2GuestCall(uintptr_t function, unsigned count, const uint64_t* args) {
    if (!function || count != 1 || !args) return static_cast<uint64_t>(-1);
    auto* linker = Common::Singleton<Core::Linker>::Instance();
    const auto result = linker->RunGuestFunction(function, std::span<const u64>{args, count}, 0);
    if (const auto* failed = std::get_if<Core::GuestExecutionFailure>(&result)) {
        LOG_ERROR(Core_Linker, "BACHATA_SOTC_NGS2_CALLBACK_FAILED entry={:#x} stage={} error={}",
                  function, static_cast<int>(failed->Stage), failed->Error);
        return static_cast<uint64_t>(-1);
    }
    return std::get<u64>(result);
}
}

namespace Libraries {
void RegisterBachataSotcNgs2(Core::Loader::SymbolsResolver* sym) {
    LIB_FUNCTION("mPYgU4oYpuY", "libSceNgs2", 1, "libSceNgs2", BachataNgs2SystemCreateWithAllocator);
    LIB_FUNCTION("u-WrYDaJA3k", "libSceNgs2", 1, "libSceNgs2", BachataNgs2SystemDestroy);
    LIB_FUNCTION("i0VnXM-C9fc", "libSceNgs2", 1, "libSceNgs2", BachataNgs2SystemRender);
    LIB_FUNCTION("0eFLVCfWVds", "libSceNgs2", 1, "libSceNgs2", BachataNgs2RackQueryBufferSize);
    LIB_FUNCTION("cLV4aiT9JpA", "libSceNgs2", 1, "libSceNgs2", BachataNgs2RackCreate);
    LIB_FUNCTION("U546k6orxQo", "libSceNgs2", 1, "libSceNgs2", BachataNgs2RackCreateWithAllocator);
    LIB_FUNCTION("lCqD7oycmIM", "libSceNgs2", 1, "libSceNgs2", BachataNgs2RackDestroy);
    LIB_FUNCTION("MwmHz8pAdAo", "libSceNgs2", 1, "libSceNgs2", BachataNgs2RackGetVoiceHandle);
    LIB_FUNCTION("uu94irFOGpA", "libSceNgs2", 1, "libSceNgs2", BachataNgs2VoiceControl);
    LIB_FUNCTION("-TOuuAQ-buE", "libSceNgs2", 1, "libSceNgs2", BachataNgs2VoiceGetState);
    LIB_FUNCTION("rEh728kXk3w", "libSceNgs2", 1, "libSceNgs2", BachataNgs2VoiceGetStateFlags);
    LOG_INFO(Core_Linker, "BACHATA_SOTC_NGS2_DONOR_MIXER_READY");
}
}

namespace Shader {
bool IsBachataMappedImageBase(u64 address) {
    if (!address || address >= 0x10000000000ULL) return false;
    auto* memory = Core::Memory::Instance();
    return memory->IsValidGpuMapping(address, 0) && memory->ClampGpuRangeSize(address, 1) == 1;
}
}
