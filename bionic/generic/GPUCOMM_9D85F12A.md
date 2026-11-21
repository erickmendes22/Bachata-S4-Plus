# GPUComm 9D85F12A — native driver selection test
- External SAF game files load correctly; the first frame was presented.
- Previous PresentThread fault is absent. New fatal SIGSEGV occurs on GpuComm,
  host read address 0x10 shortly after the Qualcomm qgpu atomic.umax LLVM IR.
- The process attempted libvulkan.so.1 and fell back to an Android loader even
  though the app profile reported Turnip. Driver provenance was not logged.
- Prefer a driver library declared in VK_ICD_FILENAMES/VK_DRIVER_FILES
  before trying the system loader. Log the actual physical device driver ID
  and its library, and the hosting shared object/offset on fatal signal.
- Fast native ICD manifest test passed in GitHub Actions 44852602895.
- This is a single deliberate complete core build; no assumption about
  Android boot or GPU crash recovery before device testing.
