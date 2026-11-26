"""Present patched Order frames between guest vblanks, as the active donor does."""
from pathlib import Path
import shutil


REFRESH = r'''// BACHATA_ORDER_FRAME_PACING: inspect mapped bytes after all launch patch paths.
void RefreshOrderFramePacing() {
    const auto version = CurrentAppVersion();
    std::array<std::uint8_t, 10> instruction{};
    bool readable = false;
#ifdef __ANDROID__
    constexpr auto rva = Common::OrderFramePacing::InstructionRva;
    if (g_game_serial == "CUSA00785" && version == "01.02" && g_eboot_address &&
        rva <= g_eboot_image_size && instruction.size() <= g_eboot_image_size - rva &&
        g_eboot_address <= UINTPTR_MAX - rva) {
        const auto address = g_eboot_address + rva;
        auto* memory = Common::Singleton<Core::MemoryManager>::Instance();
        // Never use ClampRangeSize's sub-1-GiB shortcut to inspect guest code.
        readable = memory->ClampGpuRangeSize(address, instruction.size()) == instruction.size() &&
                   memory->TryReadBacking(address, instruction.data(), instruction.size());
    }
#endif
    const bool enabled = Common::OrderFramePacing::Configure(
        g_game_serial, version,
        readable ? std::span<const std::uint8_t>{instruction} : std::span<const std::uint8_t>{});
    if (Common::OrderFramePacing::IsTarget()) {
        LOG_INFO(Loader,
            "BACHATA_ORDER_FRAME_PACING patch60_verified={} code_readable={} app={} presentation_limit={}",
            enabled, readable, version, Common::OrderFramePacing::FrameLimit());
    }
}

'''

TAIL = r'''        if (!frame_limit || main_port.flip_rate.load(std::memory_order_relaxed) != 0) {
            timer.End();
            continue;
        }

        // The guest vblank clock stays at its configured frequency. A finished
        // frame need not wait for its next tick: that quantized 17--33 ms work
        // to 30 FPS even with the 60-FPS instruction applied. Preserve the
        // donor's separate presentation deadline and FIFO request ownership.
        while (!token.stop_requested() && Common::OrderFramePacing::FrameLimit() &&
               main_port.flip_rate.load(std::memory_order_relaxed) == 0) {
            {
                std::unique_lock lk{mutex};
                if (!request_cv.wait_until(lk, tick_deadline,
                        [&] { return token.stop_requested() || !requests.empty(); })) {
                    break;
                }
            }
            if (token.stop_requested() || !Common::OrderFramePacing::FrameLimit() ||
                main_port.flip_rate.load(std::memory_order_relaxed) != 0) break;
            if (std::chrono::steady_clock::now() < next_flip) {
                if (next_flip >= tick_deadline) break;
                std::this_thread::sleep_until(next_flip);
            }
            if (token.stop_requested() || !Common::OrderFramePacing::FrameLimit() ||
                main_port.flip_rate.load(std::memory_order_relaxed) != 0) break;
            const auto now = std::chrono::steady_clock::now();
            // A queued request makes wait_until return even after its deadline.
            // Return to vblank publication when Present itself used this tick.
            if (now >= tick_deadline) break;
            const auto request = receive_request();
            if (request) {
                next_flip = std::max(next_flip + frame_period, now - frame_period);
                Flip(request);
                FRAME_END;
            }
        }
        std::this_thread::sleep_until(tick_deadline);
    }
}
'''


def apply(root: Path):
    root = Path(root)

    def edit(path, old, new, count=1):
        target = root / path
        text = target.read_text()
        if text.count(old) != count:
            raise RuntimeError(f'Order frame pacing anchor {path}: {text.count(old)} != {count}: {old[:90]}')
        target.write_text(text.replace(old, new))

    shutil.copyfile(Path(__file__).with_name('order_frame_pacing.h'),
                    root / 'src/common/order_frame_pacing.h')
    patcher = 'src/common/memory_patcher.cpp'
    edit(patcher, '#include "common/guarded_patch_group.h"',
         '#include "common/guarded_patch_group.h"\n#include "common/order_frame_pacing.h"')
    edit(patcher, 'bool IsMaskType(PatchLineType type) {', REFRESH + 'bool IsMaskType(PatchLineType type) {')
    edit(patcher, '    pending_patches.clear();\n}\n\nbool PatchMemory(',
         '    pending_patches.clear();\n    RefreshOrderFramePacing();\n}\n\nbool PatchMemory(')
    edit(patcher, '''            LOG_ERROR(Loader, "Failed to apply queued patch {}", patchToAdd.modNameStr);
        }
        return;''', '''            LOG_ERROR(Loader, "Failed to apply queued patch {}", patchToAdd.modNameStr);
        }
        RefreshOrderFramePacing();
        return;''')

    header = 'src/core/libraries/videoout/driver.h'
    edit(header, '#include <condition_variable>', '#include <atomic>\n#include <condition_variable>')
    edit(header, '    int flip_rate = 0;', '    std::atomic<int> flip_rate{0};')
    edit(header, '    std::mutex mutex;\n    VideoOutPort main_port{};',
         '    std::mutex mutex;\n    std::condition_variable request_cv;\n    VideoOutPort main_port{};')

    driver = 'src/core/libraries/videoout/driver.cpp'
    edit(driver, '#include "common/assert.h"',
         '#include "common/assert.h"\n#include "common/order_frame_pacing.h"')
    edit(driver, 'VideoOutDriver::~VideoOutDriver() = default;', '''VideoOutDriver::~VideoOutDriver() {
    // Join before requests, ports and the new condition variable are destroyed.
    present_thread.request_stop();
    request_cv.notify_all();
    if (present_thread.joinable()) present_thread.join();
}''')
    edit(driver, '''    std::scoped_lock lock{mutex};
    requests.push({
        .frame = frame,
        .port = port,
        .flip_arg = flip_arg,
        .index = index,
        .eop = is_eop,
    });''', '''    {
        std::scoped_lock lock{mutex};
        requests.push({
            .frame = frame,
            .port = port,
            .flip_arg = flip_arg,
            .index = index,
            .eop = is_eop,
        });
    }
    request_cv.notify_one();''')
    edit(driver, '    Common::AccurateTimer timer{vblank_period};', '''    Common::AccurateTimer timer{vblank_period};
    u32 frame_limit = Common::OrderFramePacing::FrameLimit();
    auto frame_period = frame_limit ? std::chrono::nanoseconds(1000000000 / frame_limit)
                                   : std::chrono::nanoseconds(0);
    auto next_flip = std::chrono::steady_clock::now();''')
    edit(driver, '''    while (!token.stop_requested()) {
        timer.Start();''', '''    while (!token.stop_requested()) {
        if (const u32 limit = Common::OrderFramePacing::FrameLimit(); limit != frame_limit) {
            frame_limit = limit;
            frame_period = limit ? std::chrono::nanoseconds(1000000000 / limit)
                                 : std::chrono::nanoseconds(0);
            next_flip = std::chrono::steady_clock::now();
        }
        timer.Start();
        const auto tick_deadline = std::chrono::steady_clock::now() + vblank_period;''')
    edit(driver, '''        if (vblank_status.count % (main_port.flip_rate + 1) == 0) {
            const auto request = receive_request();''', '''        const auto now = std::chrono::steady_clock::now();
        const bool flip_slot = !frame_limit || now >= next_flip;
        if (flip_slot && vblank_status.count %
                (main_port.flip_rate.load(std::memory_order_relaxed) + 1) == 0) {
            const auto request = receive_request();
            if (request && frame_limit) {
                next_flip = std::max(next_flip + frame_period, now - frame_period);
            }''')
    edit(driver, '        timer.End();\n    }\n}\n', TAIL)

    video_out = 'src/core/libraries/videoout/video_out.cpp'
    edit(video_out, '#include "common/elf_info.h"',
         '#include "common/elf_info.h"\n#include "common/order_frame_pacing.h"')
    edit(video_out, '''    driver->GetPort(handle)->flip_rate = rate;
    return ORBIS_OK;''', '''    const auto previous = driver->GetPort(handle)->flip_rate.exchange(rate, std::memory_order_relaxed);
    if (Common::OrderFramePacing::IsTarget()) {
        static std::atomic<bool> reported{false};
        if (!reported.exchange(true, std::memory_order_relaxed) || previous != rate) {
            LOG_INFO(Lib_VideoOut,
                "BACHATA_ORDER_FLIP_RATE guest_rate={} patch60_verified={} vblank_hz={} presentation_limit={}",
                rate, Common::OrderFramePacing::FrameLimit() == 60,
                EmulatorSettings.GetVblankFrequency(), Common::OrderFramePacing::FrameLimit());
        }
    }
    return ORBIS_OK;''')
    return {'scope': 'Android CUSA00785 01.02 with complete patched instruction verified',
            'pacing': 'notify on FIFO request; separate 60-FPS slots between guest vblanks',
            'guest': 'unchanged vblank clock, explicit nonzero flip rates respected',
            'lifetime': 'join presentation thread before queue/condition-variable destruction'}
