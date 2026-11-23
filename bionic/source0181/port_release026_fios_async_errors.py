#!/usr/bin/env python3
"""Preserve FIOS2 asynchronous operation errors for all guest titles.

CUSA08809 (BS4-20261123-4C419457): failed async FHOpen returned op=-1;
OpIsDone(-1) replied true, OpGetError(-1) replied success, and the
guest then queried Fstat(handle=0), followed by an invalid -2 GiB
allocation. Never turn an unsuccessful open into a successful operation.
This does not synthesize missing game resources or bypass FEX callbacks.
"""
from pathlib import Path

def only(text: str, old: str, new: str, label: str) -> str:
    n = text.count(old)
    if n != 1:
        raise RuntimeError(f"FIOS2 async source drift {label}: {n}")
    return text.replace(old, new, 1)

def apply(root: Path) -> dict:
    path = root / "src/core/libraries/fios2/fios2.cpp"
    t = path.read_text()
    t = only(t,
        "s64 QueryOpActualCount(s32 op) {\n    std::scoped_lock lock{g_op_mutex};",
        "s64 QueryOpActualCount(s32 op) {\n"
        "    // Invalid submission is an error, not a successful 0-byte read.\n"
        "    if (op <= 0) return op < 0 ? op : -1;\n"
        "    std::scoped_lock lock{g_op_mutex};",
        "async operation byte count")
    t = only(t,
        '    LogOpAttr("FHOpen", op_attr);\n    if (out_handle == nullptr || path == nullptr) {',
        '    LogOpAttr("FHOpen", op_attr);\n'
        '    if (out_handle != nullptr) *out_handle = -1;\n'
        '    if (out_handle == nullptr || path == nullptr) {',
        "invalid file descriptor on failed async open")
    t = only(t,
        's32 PS4_SYSV_ABI sceFiosOpGetError(s32 op) {\n'
        '    // Ops store their outcome in the byte count: negative counts encode the errno.\n',
        's32 PS4_SYSV_ABI sceFiosOpGetError(s32 op) {\n'
        '    // BACHATA_RELEASE026_FIOS_ASYNC_INVALID_OP: never report success\n'
        '    // after the guest observed a negative FHOpen submission result.\n'
        '    if (op <= 0) {\n'
        '        LOG_ERROR(Lib_SysModule,\n'
        '                  "BACHATA_RELEASE026_FIOS_ASYNC_INVALID_OP op={}", op);\n'
        '        return op < 0 ? op : -1;\n'
        '    }\n'
        '    // Ops store their outcome in the byte count: negative counts encode the errno.\n',
        "negative operation error propagation")
    for name, signature in (
        ("sceFiosOpWait", "s32 PS4_SYSV_ABI sceFiosOpWait(s32 op) {"),
        ("sceFiosOpWaitUntil", "s32 PS4_SYSV_ABI sceFiosOpWaitUntil(s32 op, s64 deadline) {"),
        ("sceFiosOpSyncWait", "s32 PS4_SYSV_ABI sceFiosOpSyncWait(s32 op) {"),
    ):
        t = only(t, signature, signature + "\n    if (op <= 0) return op < 0 ? op : -1;",
                 name + " failure propagation")
    t = only(t,
        's32 PS4_SYSV_ABI sceFiosOpIsDone(s32 op) {\n',
        's32 PS4_SYSV_ABI sceFiosOpIsDone(s32 op) {\n'
        '    if (op <= 0) return op < 0 ? op : -1;\n',
        "is-done invalid operation")
    # The existing HLE casts requested byte counts to u64. A negative
    # signed size must not become an enormous read against guest memory.
    for name, signature, check in (
        ("sync sequential", 's64 PS4_SYSV_ABI sceFiosFHReadSync(const void* op_attr, s32 handle, void* buffer, s64 size) {',
         '    if (size < 0) return -1;'),
        ("sync positioned", 's64 PS4_SYSV_ABI sceFiosFHPreadSync(const void* op_attr, s32 handle, void* buffer, s64 size,\n                                    s64 offset) {',
         '    if (size < 0 || offset < 0) return -1;'),
        ("async sequential", 's32 PS4_SYSV_ABI sceFiosFHRead(const void* op_attr, s32 handle, void* buffer, s64 size) {',
         '    if (size < 0) return CompleteAsyncOp(op_attr, -1);'),
        ("async positioned", 's32 PS4_SYSV_ABI sceFiosFHPread(const void* op_attr, s32 handle, void* buffer, s64 size,\n                                s64 offset) {',
         '    if (size < 0 || offset < 0) return CompleteAsyncOp(op_attr, -1);'),
    ):
        t = only(t, signature, signature + "\n" + check, name + " size validation")
    path.write_text(t)
    return {"source": "real FIOS2 negative FHOpen op=-1 captured in CUSA08809",
            "changed": "preserve negative operation status and invalid fd; reject signed negative read sizes",
            "notClaimed": "guest assets exist or guest FEX callbacks are fixed"}
