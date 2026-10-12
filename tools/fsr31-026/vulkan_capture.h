#pragma once
#include <vulkan/vulkan.h>
#include <cstdint>
extern "C" {
struct Bs4FsrCaptureImage {
    VkImage image;
    VkFormat format;
    VkExtent2D size;
    VkImageUsageFlags usage;
    VkImageLayout layout;
    VkImageAspectFlags aspects;
};
int bs4_fsr31_capture_image(VkImageView view, Bs4FsrCaptureImage* image);
int bs4_fsr31_capture_depth(VkExtent2D expected, Bs4FsrCaptureImage* depth);
}
