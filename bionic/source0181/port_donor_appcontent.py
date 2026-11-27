"""Adapt the complete ISS/TLOU offline AppContent lifecycle to the Bachata VFS.
Sources: iss_android 879fe3c and tlou-remastered-android 62ea759,
src/runtime_content.c; ISS runtime_gr2.c/runtime_infamous.c.
Preserve installed DLC/license discovery and the existing FEX ABI adapters.
"""
from pathlib import Path


def apply(root: Path):
    src = Path(root) / 'src'
    cpp = src / 'core/libraries/app_content/app_content.cpp'
    h = cpp.with_suffix('.h')
    sys = src / 'core/libraries/sysmodule/sysmodule_internal.cpp'

    def replace(path, a, b, count=1):
        s = path.read_text()
        if s.count(a) != count:
            raise RuntimeError(f'{path}: AppContent anchor count {s.count(a)} != {count}: {a[:120]}')
        path.write_text(s.replace(a, b, count))

    replace(cpp, '#include <cmath>', '''#include <cmath>
#include <algorithm>
#include <cstring>
#include <mutex>
#include "core/libraries/playgo/bachata_installed_package.h"''')
    replace(cpp, 'static bool is_initialized = false;', '''static bool is_initialized = false;
static std::mutex donor_content_mutex;
static bool donor_module_loaded = false;

static bool DonorContent() {
    return BachataBoot::InstalledPackageTitle(Common::ElfInfo::Instance().GameSerial());
}

static auto LockDonorContent() {
    std::unique_lock lock{donor_content_mutex, std::defer_lock};
    if (DonorContent()) lock.lock();
    return lock;
}

void NotifyDonorAppContentLoaded() {
    if (!DonorContent()) return;
    auto lock = LockDonorContent();
    donor_module_loaded = true;
}

void ResetDonorAppContent() {
    if (!DonorContent()) return;
    auto lock = LockDonorContent();
    donor_module_loaded = false;
    is_initialized = false;
    addcont_count = 0;
    title_id.clear();
    addcont_info.fill({});
}

// Insert actual installed/license entries safely; preserve the installed entry
// when a license-only entitlement describes the same content.
static void StoreDonorEntitlement(std::string_view entitlement, OrbisAppContentAddcontDownloadStatus status) {
    if (entitlement.empty() || entitlement.size() >= ORBIS_NP_UNIFIED_ENTITLEMENT_LABEL_SIZE)
        return;
    for (s32 i = 0; i < addcont_count; ++i) {
        auto& info = addcont_info[i];
        if (entitlement == info.entitlement_label) {
            if (status == OrbisAppContentAddcontDownloadStatus::Installed) info.status = status;
            return;
        }
    }
    if (addcont_count >= static_cast<s32>(addcont_info.size())) return;
    auto& info = addcont_info[addcont_count++];
    info = {};
    entitlement.copy(info.entitlement_label, entitlement.size());
    info.status = status;
}

static int DonorContentSpace(const OrbisAppContentMountPoint* mount, u64* available) {
    if (!is_initialized || !mount || !available) return ORBIS_APP_CONTENT_ERROR_PARAMETER;
    const auto* end = static_cast<const char*>(std::memchr(mount->data, 0, sizeof(mount->data)));
    if (!end || end == mount->data) return ORBIS_APP_CONTENT_ERROR_PARAMETER;
    const std::string_view path(mount->data, static_cast<size_t>(end - mount->data));
    // Use the mounted host path, not the guest string or a fabricated quota.
    const auto host = Common::Singleton<Core::FileSys::MntPoints>::Instance()->GetHostPath(path);
    if (host.empty()) return ORBIS_APP_CONTENT_ERROR_PARAMETER;
    std::error_code ec;
    const auto space = std::filesystem::space(host, ec);
    if (ec || space.available == static_cast<std::uintmax_t>(-1)) return ORBIS_APP_CONTENT_ERROR_PARAMETER;
    *available = space.available / 1024;
    return ORBIS_OK;
}''')
    replace(h, 'int PS4_SYSV_ABI sceAppContentAddcontEnqueueDownload();', '''int PS4_SYSV_ABI sceAppContentAddcontEnqueueDownload(
    u32 service_label, const OrbisNpUnifiedEntitlementLabel* entitlement_label);
void NotifyDonorAppContentLoaded();
void ResetDonorAppContent();''')
    replace(cpp, '''int PS4_SYSV_ABI sceAppContentAddcontEnqueueDownload() {
    LOG_ERROR(Lib_AppContent, "(STUBBED) called");
    return ORBIS_OK;
}''', '''int PS4_SYSV_ABI sceAppContentAddcontEnqueueDownload(
    u32 service_label, const OrbisNpUnifiedEntitlementLabel* entitlement_label) {
    auto lock = LockDonorContent();
    if (DonorContent()) {
        if (!is_initialized || !entitlement_label) return ORBIS_APP_CONTENT_ERROR_PARAMETER;
        for (s32 i = 0; i < addcont_count; ++i) {
            if (std::strncmp(entitlement_label->data, addcont_info[i].entitlement_label,
                             ORBIS_NP_UNIFIED_ENTITLEMENT_LABEL_SIZE - 1) == 0) {
                // Already installed, or licensed content without extra data. No download needed.
                return ORBIS_OK;
            }
        }
        return ORBIS_APP_CONTENT_ERROR_NOT_FOUND;
    }
    LOG_ERROR(Lib_AppContent, "(STUBBED) called");
    return ORBIS_OK;
}''')
    replace(cpp, '''                                           OrbisAppContentMountPoint* mount_point) {
    LOG_INFO''', '''                                           OrbisAppContentMountPoint* mount_point) {
    auto lock = LockDonorContent();
    if (DonorContent() && (!is_initialized || !entitlement_label || !mount_point))
        return ORBIS_APP_CONTENT_ERROR_PARAMETER;
    LOG_INFO''')
    replace(cpp, '''    if (i == addcont_count) {''', '''    if (i == addcont_count || (DonorContent() &&
        addcont_info[i].status == OrbisAppContentAddcontDownloadStatus::NoExtraData)) {''')
    # Do not publish a mount point for absent or unmountable content.
    replace(cpp, '''            snprintf(mount_point->data, ORBIS_APP_CONTENT_MOUNTPOINT_DATA_MAXSIZE, "/addcont%d", i);''', '''            if (!DonorContent())
                snprintf(mount_point->data, ORBIS_APP_CONTENT_MOUNTPOINT_DATA_MAXSIZE, "/addcont%d", i);''')
    replace(cpp, '''    // Find which directory corresponds to this entitlement
    for (const auto& entry : std::filesystem::directory_iterator(addon_path)) {''', '''    // Find which directory corresponds to this entitlement.
    OrbisAppContentMountPoint candidate{};
    auto* result_mount = DonorContent() ? &candidate : mount_point;
    if (DonorContent())
        snprintf(candidate.data, sizeof(candidate.data), "/addcont%d", i);
    std::error_code addon_ec;
    if (DonorContent() && !std::filesystem::is_directory(addon_path, addon_ec))
        return ORBIS_APP_CONTENT_ERROR_NOT_FOUND;
    for (const auto& entry : std::filesystem::directory_iterator(addon_path)) {''')
    # Change only the mount function's use of the pending mount path.
    s = cpp.read_text()
    a = s.index('    // Find which directory corresponds to this entitlement.')
    b = s.index('int PS4_SYSV_ABI sceAppContentAddcontShrink()', a)
    segment = s[a:b].replace('mount_point->data', 'result_mount->data')
    segment = segment.replace('        // We\'ve located the correct folder.\n        return ORBIS_OK;', '''        // We've located the correct folder; publish only after successful validation.
        if (DonorContent()) *mount_point = candidate;
        return ORBIS_OK;''')
    segment = segment.replace('    UNREACHABLE_MSG(', '''    if (DonorContent()) return ORBIS_APP_CONTENT_ERROR_NOT_FOUND;
    UNREACHABLE_MSG(''')
    cpp.write_text(s[:a] + segment + s[b:])
    replace(cpp, '''    if (out_value == nullptr)
''', '''    auto lock = LockDonorContent();
    if (DonorContent() && !is_initialized) return ORBIS_APP_CONTENT_ERROR_PARAMETER;
    if (out_value == nullptr)
''')
    for signature in [
        'int PS4_SYSV_ABI sceAppContentDownloadDataGetAvailableSpaceKb(OrbisAppContentMountPoint* mountPoint,\n                                                              u64* availableSpaceKb) {',
        'int PS4_SYSV_ABI sceAppContentTemporaryDataGetAvailableSpaceKb(\n    const OrbisAppContentMountPoint* mountPoint, u64* availableSpaceKb) {',
    ]:
        replace(cpp, signature, signature + '''
    auto lock = LockDonorContent();
    if (DonorContent()) return DonorContentSpace(mountPoint, availableSpaceKb);''')
    # Existing ISS-only guards occur in both Initialize and GetAddcontInfo.
    replace(cpp, '''    const auto bachata_serial=Common::ElfInfo::Instance().GameSerial();
    const bool bachata_iss=bachata_serial=="CUSA00004"||bachata_serial=="CUSA00223";''', '''    auto lock = LockDonorContent();
    const bool bachata_iss = DonorContent();''', 2)
    replace(cpp, '''    if (entitlementLabel == nullptr || info == nullptr) {''', '''    if ((DonorContent() && !is_initialized) || entitlementLabel == nullptr || info == nullptr) {''')
    replace(cpp, '''                                                 u32* hit_num) {
    LOG_INFO''', '''                                                 u32* hit_num) {
    auto lock = LockDonorContent();
    if (DonorContent() && !is_initialized) return ORBIS_APP_CONTENT_ERROR_PARAMETER;
    LOG_INFO''')
    replace(cpp, '''    OrbisAppContentGetEntitlementKey* key) {
    LOG_INFO''', '''    OrbisAppContentGetEntitlementKey* key) {
    auto lock = LockDonorContent();
    LOG_INFO''')
    replace(cpp, '''    if (sdk_ver >= Common::ElfInfo::FW_150 && is_initialized) {''', '''    if ((bachata_iss || sdk_ver >= Common::ElfInfo::FW_150) && is_initialized) {''')
    replace(cpp, '''    if (bachata_iss && (!initParam || !bootParam)) {
        return ORBIS_APP_CONTENT_ERROR_PARAMETER;
    }''', '''    if (bachata_iss) {
        if (!donor_module_loaded || !initParam || std::ranges::any_of(initParam->reserved, [](char c) { return c != 0; }))
            return ORBIS_APP_CONTENT_ERROR_PARAMETER;
        addcont_count = 0;
        addcont_info.fill({});
    }''')
    replace(cpp, '''            auto& info = addcont_info[addcont_count++];
            entitlement_id.copy(info.entitlement_label, entitlement_id.length());
            info.status = OrbisAppContentAddcontDownloadStatus::Installed;''', '''            if (bachata_iss) {
                StoreDonorEntitlement(entitlement_id, OrbisAppContentAddcontDownloadStatus::Installed);
            } else {
                auto& info = addcont_info[addcont_count++];
                entitlement_id.copy(info.entitlement_label, entitlement_id.length());
                info.status = OrbisAppContentAddcontDownloadStatus::Installed;
            }''')
    replace(cpp, '''                    auto& info = addcont_info[addcont_count++];
                    entitlement_id.copy(info.entitlement_label, entitlement_id.length());
                    info.status = OrbisAppContentAddcontDownloadStatus::NoExtraData;''', '''                    if (bachata_iss) {
                        StoreDonorEntitlement(entitlement_id, OrbisAppContentAddcontDownloadStatus::NoExtraData);
                    } else {
                        auto& info = addcont_info[addcont_count++];
                        entitlement_id.copy(info.entitlement_label, entitlement_id.length());
                        info.status = OrbisAppContentAddcontDownloadStatus::NoExtraData;
                    }''')
    replace(cpp, '''    TmpMount.copy(mountPoint->data, TmpMount.size());''', '''    if (DonorContent()) std::memset(mountPoint->data, 0, sizeof(mountPoint->data));
    TmpMount.copy(mountPoint->data, TmpMount.size());''')
    # The existing Sysmodule unload decrements a copy. For the donor AppContent
    # provider only, publish the actual reference count and reset on final unload.
    replace(sys, '#include "core/libraries/fios2/fios2.h"', '''#include "core/libraries/app_content/app_content.h"
#include "core/libraries/fios2/fios2.h"''')
    s = sys.read_text()
    if '#include "core/libraries/playgo/bachata_installed_package.h"' not in s:
        replace(sys, '#include "core/libraries/fios2/fios2.h"', '#include "core/libraries/fios2/fios2.h"\n#include "core/libraries/playgo/bachata_installed_package.h"')
    replace(sys, '''    return ORBIS_OK;
}

s32 unloadModule(s32 id, s32 argc, const void* argv, s32* res_out, bool is_internal) {''', '''    if (id == 0xb4) Libraries::AppContent::NotifyDonorAppContentLoaded();
    return ORBIS_OK;
}

s32 unloadModule(s32 id, s32 argc, const void* argv, s32* res_out, bool is_internal) {''')
    replace(sys, '''        dep_mod.is_loaded--;
''', '''        dep_mod.is_loaded--;
        if (id == 0xb4 && dep_mod.id == id &&
            BachataBoot::InstalledPackageTitle(Common::ElfInfo::Instance().GameSerial())) {
            auto& live = g_modules_array[mod.to_load[i]];
            live.is_loaded = dep_mod.is_loaded;
            if (!live.is_loaded) Libraries::AppContent::ResetDonorAppContent();
        }
''')
