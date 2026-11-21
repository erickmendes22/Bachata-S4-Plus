# Diagnosis 7E78AC2F — native Vulkan driver selection

Android application profile: turnip-2bbb279a3da76805.
Actual Bionic loader: libvulkan.so (Android system fallback).
Actual physical driver: Qualcomm Technologies Inc. Adreno Vulkan Driver, ID 8.
Actual crash module: /vendor/lib64/libllvm-qgl.so, offset 0x91f470.
Signal: SIGSEGV, attempted read 0x10, GpuComm after FIRST_FRAME_PRESENTED.

Not a missing game-file problem: external SAF game content and first flip
complete successfully. This is not proven to be a shader IR defect either:
the LLVM qgpu intrinsic and crash occur in Qualcomm's native compiler.

Root fix implemented: generic Bionic Vulkan loader invokes original signed
Bachata 0.2.7 libbachata_custom_vulkan.so::bachata_open_custom_vulkan()
first when BACHATA_VULKAN_DRIVER_DIR/NAME/TMPDIR are provided by the APK
frontend. That bridge itself uses adrenotools_open_libvulkan and the original
hook libraries to load selected Turnip. Do not silently fall back to Qualcomm
when a custom driver is requested. Report booleans for the 3 env settings.
Keep the existing manifest-only resolution path for other environments.

Preflight #44882470765 passed. Packaging also requires custom Vulkan bridge
and both hook libraries in the signed output (original P36 key).
A successful native build does not prove the Android driver is Turnip;
the subsequent device log must show BIONIC_VULKAN_CUSTOM_BRIDGE_READY and
BIONIC_VULKAN_DEVICE showing a Mesa driver, followed by gameplay testing.
