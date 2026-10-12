SECTIONS {
    bs4_original_exec_dispatch = 0x12000;
    . = 0x12400;
    .entry : { *(.entry) *(.text*) *(.rodata*) }
}
