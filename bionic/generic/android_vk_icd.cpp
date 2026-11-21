// PS4/Bionic: explicitly select Mesa/Turnip ICD JSON on Android.
// The system libvulkan.so does not honor Linux VK_ICD_FILENAMES.
#include "android_vk_icd.h"
#include <cstdlib>
#include <filesystem>
#include <fstream>
#include <string>
#include <string_view>
namespace BachataVulkan {
namespace {
std::string ResolveOne(const std::filesystem::path& manifest) {
    std::ifstream in(manifest, std::ios::binary);
    if (!in) return {};
    std::string json(262144, '\0');
    in.read(json.data(), json.size());
    json.resize(static_cast<std::size_t>(in.gcount()));
    auto k = json.find("\"library_path\"");
    if (k == std::string::npos) return {};
    k = json.find(':', k + 14);
    if (k == std::string::npos) return {};
    k = json.find('"', k + 1);
    if (k == std::string::npos) return {};
    std::string library;
    bool closed = false;
    for (++k; k < json.size(); ++k) {
        char ch = json[k];
        if (ch == '"') { closed = true; break; }
        if (ch == '\\') {
            if (++k == json.size()) return {};
            ch = json[k];
            if (ch != '/' && ch != '\\' && ch != '"') return {};
        }
        library.push_back(ch);
        if (library.size() > 4096) return {};
    }
    if (!closed || library.empty()) return {};
    std::filesystem::path path(library);
    if (path.is_absolute()) return path.string();
    auto adjacent = manifest.parent_path() / path;
    if (std::filesystem::exists(adjacent)) return adjacent.string();
    // Bare sonames may be visible in the app's native linker namespace.
    return path.has_parent_path() ? std::string{} : library;
}
}
std::string SelectedIcdLibrary() {
    for (auto key : {"VK_DRIVER_FILES", "VK_ICD_FILENAMES"}) {
        const char* env = std::getenv(key);
        if (!env || !*env) continue;
        std::string_view files(env);
        std::size_t at = 0;
        while (at < files.size()) {
            const auto end = files.find(':', at);
            const auto name = files.substr(at, end == files.npos ? files.size() - at : end - at);
            if (!name.empty()) {
                auto result = ResolveOne(std::filesystem::path(name));
                if (!result.empty()) return result;
            }
            if (end == files.npos) break;
            at = end + 1;
        }
    }
    return {};
}
bool ManifestWasRequested() {
    const char* a = std::getenv("VK_DRIVER_FILES");
    const char* b = std::getenv("VK_ICD_FILENAMES");
    return (a && *a) || (b && *b);
}
}
