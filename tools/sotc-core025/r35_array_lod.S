// CUSA08809-only: count LOD bank from a verified texture-array TSharp.
// SHA-pinned target: R34 host/shadps4-arm64-025 2b76f3d27f3471b2159151c25afc5f42cd541b9537c26b62583f192972f4b290
// R34 site 0x12E4798, after array bindability check.
// Entry: original SP, TSharp u64[4] at SP+0x238.
// Replay original LDR X12,[SP,#0x68] and restore all displaced state.
.text
.p2align 4
.global r35_array_lod
r35_array_lod:
    stp x0, x1, [sp, #-96]!
    stp x8, x9, [sp, #16]
    stp x14, x15, [sp, #32]
    stp x16, x17, [sp, #48]
    str x30, [sp, #64]
r35_gate_call:
    .word 0x94000000 // BL to r34_check_game at 0x435F960
    cbz w0, r35_array_exit
r35_bank_bss_adrp:
    .inst 0x9000000e // ADRP X14, bank array at 0x5BE2000
    ldr x8, [sp, #0x2b0] // SP+96 + original TSharp fourth qword offset +0x250
    tbz x8, #20, r35_array_exit
    ubfx x9, x8, #12, #8
    ldr w15, [x14, x9, lsl #2]
    mov w17, #0xffff
    cmp w15, w17
    b.hs r35_array_exit
    add w15, w15, #1
    str w15, [x14, x9, lsl #2]
r35_array_exit:
    ldr x30, [sp, #64]
    ldp x16, x17, [sp, #48]
    ldp x14, x15, [sp, #32]
    ldp x8, x9, [sp, #16]
    ldp x0, x1, [sp], #96
    ldr x12, [sp, #0x68]
    ret
