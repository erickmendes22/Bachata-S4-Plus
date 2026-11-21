# Present-thread fix validation — BS4-20261121-FF5B7A1C

The user-provided diagnostic confirms the prior SAF work is functional:
the broker returns libc.prx, playgo-chunk.dat, archivemap.bin and shader
files; the game initializes PlayGo, audio and Gnm compute queues.

The current failure is a host access violation in shadPS4:Present at
PC 0x7580db6004 (read 0x4dc), before any recorded flip or presented frame.
The 9eb67b6 patch removes unneeded Vulkan blank-frame submits before the
VideoOut port opens and uses present_scheduler rather than draw_scheduler
when PresentThread prepares a blank frame. A fault-only ARM64 register
snapshot was added to distinguish future issues if the crash persists.

Build success proves only source compatibility. Do not claim first-frame
success without a new Android diagnostic. Preserve the working SAF bridge
and the original P36 app-signing secrets. This is a single opt-in full build
after the fast preflight passed in GitHub Actions 44847405348.
