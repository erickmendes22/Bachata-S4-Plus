// SPDX-License-Identifier: GPL-2.0-or-later
.section .entry,"ax",@progbits
.global bs4_dispatch_preload_entry
bs4_dispatch_preload_entry:
    // Original dispatcher at VA 0x10758 has x0=ld.so path,
    // x1=argv, x2=envp and x8=__NR_execve.
    stp x0,x1,[sp,#-176]!
    stp x2,x3,[sp,#16]
    stp x4,x5,[sp,#32]
    stp x6,x7,[sp,#48]
    stp x8,x9,[sp,#64]
    stp x10,x11,[sp,#80]
    stp x12,x13,[sp,#96]
    stp x14,x15,[sp,#112]
    stp x16,x17,[sp,#128]
    stp x18,x30,[sp,#144]
    mov x0,x1
    bl bs4_r16_insert_preload
    ldp x18,x30,[sp,#144]
    ldp x16,x17,[sp,#128]
    ldp x14,x15,[sp,#112]
    ldp x12,x13,[sp,#96]
    ldp x10,x11,[sp,#80]
    ldp x8,x9,[sp,#64]
    ldp x6,x7,[sp,#48]
    ldp x4,x5,[sp,#32]
    ldp x2,x3,[sp,#16]
    ldp x0,x1,[sp],#176
    b bs4_original_exec_dispatch
