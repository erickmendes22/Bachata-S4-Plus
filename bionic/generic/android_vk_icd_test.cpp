// Minimal manifest resolver check; independent of Vulkan/Android build.
#include "android_vk_icd.h"
#include <cassert>
#include <cstdlib>
#include <filesystem>
#include <fstream>
#include <string>
#include <unistd.h>
namespace fs = std::filesystem;
int main() {
    const auto root=fs::temp_directory_path()/
                    ("bachata-icd-test-"+std::to_string(getpid()));
    fs::create_directories(root);
    const auto driver=root/"libvulkan_freedreno.so";
    const auto manifest=root/"turnip_icd.json";
    {std::ofstream out(driver);out<<"driver";}
    {std::ofstream out(manifest);
     out<<"{\"file_format_version\":\"1.0.0\", \"ICD\":"
           "{\"library_path\":\"libvulkan_freedreno.so\","
           "\"api_version\":\"1.3.0\"}}";}
    unsetenv("VK_DRIVER_FILES");
    unsetenv("VK_ICD_FILENAMES");
    assert(!BachataVulkan::ManifestWasRequested());
    assert(BachataVulkan::SelectedIcdLibrary().empty());
    setenv("VK_ICD_FILENAMES",manifest.c_str(),1);
    assert(BachataVulkan::ManifestWasRequested());
    assert(BachataVulkan::SelectedIcdLibrary()==driver.string());
    unsetenv("VK_ICD_FILENAMES");
    setenv("VK_DRIVER_FILES",manifest.c_str(),1);
    assert(BachataVulkan::SelectedIcdLibrary()==driver.string());
    unsetenv("VK_DRIVER_FILES");
    fs::remove_all(root);
}
