#!/usr/bin/env python3
"""Rebase Bachata's original AdrenoTools custom Turnip loader on full shadPS4 0.21.1."""
import argparse
from pathlib import Path
ORIGINAL = "    static vk::detail::DynamicLoader dl;\n    VULKAN_HPP_DEFAULT_DISPATCHER.init(\n        dl.getProcAddress<PFN_vkGetInstanceProcAddr>(\"vkGetInstanceProcAddr\"));"
PATCHED = "#if defined(__ANDROID__) && defined(__aarch64__)\n    // The signed Bachata APK already ships its own AdrenoTools bridge.\n    // An explicitly selected custom Turnip driver MUST NOT fall back to\n    // Android's stock Qualcomm Vulkan loader.\n    static PFN_vkGetInstanceProcAddr custom_proc = [] {\n        const char* dir = std::getenv(\"BACHATA_VULKAN_DRIVER_DIR\");\n        const char* name = std::getenv(\"BACHATA_VULKAN_DRIVER_NAME\");\n        const char* tmp = std::getenv(\"BACHATA_VULKAN_TMPDIR\");\n        const bool has_dir = dir && *dir, has_name = name && *name, has_tmp = tmp && *tmp;\n        if (has_dir || has_name || has_tmp) {\n            if (!has_dir || !has_name || !has_tmp) {\n                LOG_CRITICAL(Render_Vulkan, \"BIONIC_021_CUSTOM_DRIVER_ENV_INCOMPLETE\");\n                return static_cast<PFN_vkGetInstanceProcAddr>(nullptr);\n            }\n            void* helper = dlopen(\"libbachata_custom_vulkan.so\", RTLD_NOW | RTLD_LOCAL);\n            if (!helper) {\n                LOG_CRITICAL(Render_Vulkan, \"BIONIC_021_CUSTOM_DRIVER_BRIDGE_MISSING\");\n                return static_cast<PFN_vkGetInstanceProcAddr>(nullptr);\n            }\n            auto open_custom = reinterpret_cast<void* (*)()>(\n                dlsym(helper, \"bachata_open_custom_vulkan\"));\n            if (!open_custom) {\n                LOG_CRITICAL(Render_Vulkan, \"BIONIC_021_CUSTOM_DRIVER_EXPORT_MISSING\");\n                return static_cast<PFN_vkGetInstanceProcAddr>(nullptr);\n            }\n            void* driver = open_custom();\n            if (!driver) {\n                LOG_CRITICAL(Render_Vulkan, \"BIONIC_021_CUSTOM_DRIVER_OPEN_FAILED\");\n                return static_cast<PFN_vkGetInstanceProcAddr>(nullptr);\n            }\n            auto proc = reinterpret_cast<PFN_vkGetInstanceProcAddr>(\n                dlsym(driver, \"vkGetInstanceProcAddr\"));\n            if (!proc) {\n                LOG_CRITICAL(Render_Vulkan, \"BIONIC_021_CUSTOM_DRIVER_PROC_MISSING\");\n                return static_cast<PFN_vkGetInstanceProcAddr>(nullptr);\n            }\n            LOG_WARNING(Render_Vulkan, \"BIONIC_021_VULKAN_CUSTOM_READY\");\n            return proc;\n        }\n        void* system_driver = dlopen(\"libvulkan.so\", RTLD_NOW | RTLD_LOCAL);\n        if (!system_driver) return static_cast<PFN_vkGetInstanceProcAddr>(nullptr);\n        LOG_WARNING(Render_Vulkan, \"BIONIC_021_VULKAN_SYSTEM_SELECTED\");\n        return reinterpret_cast<PFN_vkGetInstanceProcAddr>(\n            dlsym(system_driver, \"vkGetInstanceProcAddr\"));\n    }();\n    ASSERT_MSG(custom_proc != nullptr,\n               \"Bionic 0.21.1: requested custom Vulkan driver is unavailable\");\n    VULKAN_HPP_DEFAULT_DISPATCHER.init(custom_proc);\n#else\n    static vk::detail::DynamicLoader dl;\n    VULKAN_HPP_DEFAULT_DISPATCHER.init(\n        dl.getProcAddress<PFN_vkGetInstanceProcAddr>(\"vkGetInstanceProcAddr\"));\n#endif"
def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--source",type=Path,required=True)
    source=parser.parse_args().source
    path=source/"src/video_core/renderer_vulkan/vk_platform.cpp"
    text=path.read_text()
    assert text.count(ORIGINAL)==1, "0.21.1 Vulkan dispatcher API changed: refuse partial patch"
    assert text.count("#include <vector>")==1, "Vulkan include layout changed"
    text=text.replace("#include <vector>",
       "#include <cstdlib>\n#if defined(__ANDROID__)\n#include <dlfcn.h>\n#endif\n#include <vector>",1)
    path.write_text(text.replace(ORIGINAL,PATCHED,1))
    print("BIONIC_021_ADRENOTOOLS_SOURCE_PATCHED")
if __name__=="__main__":
    main()
