#!/usr/bin/env python3
"""Correct the common FIOS2 completion ABI without bypassing the FEX guest.

The callback is int(context, op, uint8 event, int error), not
void(context, op, error, int64 byte_count). COMPLETE is event 1. Bytes remain
available through OpGetActualCount. All existing async wrappers must publish
their completion through the same helper; their synchronous I/O stays intact.
"""
from pathlib import Path


def once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"FIOS callback ABI source drift {label}: {count}")
    return text.replace(old, new, 1)


def apply(root: Path) -> dict:
    path = root / "src/core/libraries/fios2/fios2.cpp"
    text = path.read_text()
    text = once(text,
        "// typedef void (*SceFiosOpCallback)(void* pContext, s32 op, s32 err, s64 result);\n"
        "using FiosOpCallback = void PS4_SYSV_ABI (*)(void* context, s32 op, s32 err, s64 result);",
        "// FIOS2 callback ABI: context, operation, event, error. Transfer bytes\n"
        "// belong to OpGetActualCount, never the callback's error argument.\n"
        "using FiosOpCallback = s32 PS4_SYSV_ABI (*)(void* context, s32 op, u8 event, s32 error);\n"
        "constexpr u8 FiosOpEventComplete = 1;",
        "four callback argument types")
    begin = text.index("// Fire SceFiosOpAttr completion callback")
    end = text.index("// Allocate op handle and complete", begin)
    old = text[begin:end]
    if '"sceFiosOpCallback"' not in old or old.count("cb(attr->p_callback_context, op, err, result);") != 1:
        raise RuntimeError("FIOS callback original bridge drift")
    text = once(text, old, '''// Complete event is delivered outside g_op_mutex, after the result is
// queryable. Snapshot the pointers before running guest code: a callback may
// query/delete this op, submit a nested operation, or release its own attributes.
void MaybeInvokeOpCallback(const void* op_attr, s32 op, s32 err, s64 result) {
    if (op_attr == nullptr) return;
    const auto* attr = static_cast<const FiosOpAttr*>(op_attr);
    const auto callback = attr->p_callback;
    void* const context = attr->p_callback_context;
    if (callback == nullptr) return;
    LOG_INFO(Lib_SysModule,
             "BACHATA_FIOS_COMPLETION event={} op={} error={} actual={} callback={}",
             FiosOpEventComplete, op, err, result, callback);
#ifdef SHADPS4_ENABLE_FEX_GUEST_CPU
    if (Core::GuestCpu::IsGuestFunctionAddress(callback)) {
        // Keep the original PS4 function on FEX, including reentrant calls.
        static_cast<void>(Core::GuestCpu::RunGuestFunctionOrAbort(
            callback, "sceFiosOpCallback", context, op, FiosOpEventComplete, err));
        return;
    }
#endif
    auto* cb = reinterpret_cast<FiosOpCallback>(callback);
    static_cast<void>(cb(context, op, FiosOpEventComplete, err));
}

''', "native and FEX callback dispatch")
    text = once(text,
        '''    *out_handle = fd;
    const s32 op = CompleteAsyncOp(op_attr, 0);
    LOG_INFO(Lib_SysModule,
             "[FIOS-HLE][FHOpen] path='{}' handle={} op={} op_attr={} open_params={}", path, fd, op,
             op_attr, open_params);
    return op;''',
        '''    *out_handle = fd;
    // A completion callback may release the caller's path/attributes. Format
    // borrowed inputs before dispatch; the common helper logs the operation.
    LOG_INFO(Lib_SysModule,
             "[FIOS-HLE][FHOpen] path='{}' handle={} op_attr={} open_params={}", path, fd,
             op_attr, open_params);
    return CompleteAsyncOp(op_attr, 0);''', "open inputs must outlive only the I/O, not its callback")
    # These wrappers allocated a queryable op but silently omitted its callback.
    old = "    return result >= 0 ? AllocateOpHandle(0) : result;"
    if text.count(old) != 4:
        raise RuntimeError("FIOS Delete/ArchiveMount/DirectoryCreate/Stat wrapper drift")
    text = text.replace(old, "    return CompleteAsyncOp(op_attr, result < 0 ? result : 0);")
    text = once(text,
        "    const s32 op = written >= 0 ? AllocateOpHandle(written) : static_cast<s32>(written);",
        "    const s32 op = CompleteAsyncOp(op_attr, written);",
        "positioned write completion")
    signature = "s32 PS4_SYSV_ABI sceFiosFHPwrite(const void* op_attr, s32 handle, const void* buffer, s64 size,\n                                 s64 offset) {\n    static_cast<void>(op_attr);"
    text = once(text, signature,
        signature.replace("    static_cast<void>(op_attr);",
                          "    if (size < 0 || offset < 0) return CompleteAsyncOp(op_attr, -1);"),
        "positioned write invalid range")
    text = once(text, "            return static_cast<s32>(pos);",
        "            return CompleteAsyncOp(op_attr, pos);", "positioned write fallback error")
    text = once(text,
        "    return sceFiosDHOpenSync(op_attr, handle, path, open_params);",
        "    const s32 result = sceFiosDHOpenSync(op_attr, handle, path, open_params);\n"
        "    return CompleteAsyncOp(op_attr, result < 0 ? result : 0);",
        "directory open failure completion")
    text = once(text,
        "s64 PS4_SYSV_ABI sceFiosArchiveGetMountBufferSize(const void* op_attr, const char* path,\n"
        "                                                  const void* params) {\n"
        "    return sceFiosArchiveGetMountBufferSizeSync(op_attr, path, params);\n}",
        "s32 PS4_SYSV_ABI sceFiosArchiveGetMountBufferSize(const void* op_attr, const char* path,\n"
        "                                                  const void* params) {\n"
        "    const s64 result = sceFiosArchiveGetMountBufferSizeSync(op_attr, path, params);\n"
        "    return CompleteAsyncOp(op_attr, result);\n}",
        "archive size asynchronous operation handle")
    text = once(text,
        '''s32 PS4_SYSV_ABI sceFiosArchiveUnmount(const void* op_attr, s32 handle) {
    static_cast<void>(op_attr);
    static_cast<void>(handle);
    LOG_INFO(Lib_SysModule, "[FIOS-HLE][ArchiveUnmount] handle={} (no-op)", handle);
    return 0;
}

s32 PS4_SYSV_ABI sceFiosArchiveUnmountSync(const void* op_attr, s32 handle) {
    return sceFiosArchiveUnmount(op_attr, handle);
}''',
        '''s32 PS4_SYSV_ABI sceFiosArchiveUnmountSync(const void* op_attr, s32 handle) {
    static_cast<void>(op_attr);
    static_cast<void>(handle);
    LOG_INFO(Lib_SysModule, "[FIOS-HLE][ArchiveUnmount] handle={} (no-op)", handle);
    return 0;
}

s32 PS4_SYSV_ABI sceFiosArchiveUnmount(const void* op_attr, s32 handle) {
    const s32 result = sceFiosArchiveUnmountSync(op_attr, handle);
    return CompleteAsyncOp(op_attr, result < 0 ? result : 0);
}''', "unmount sync status versus async operation")
    path.write_text(text)
    return {
        "evidence": "BS4-20261126-80C69C93 FHOpen callback used event0/error0; no first frame",
        "callbackAbi": "int(context, op, uint8 COMPLETE=1, int error); count stays in OpGetActualCount",
        "scope": "common FIOS2 HLE across all titles, native and existing FEX callback bridge",
        "completionFamilies": ["open", "read", "pread", "close", "pwrite", "archive size",
                               "archive mount", "archive unmount", "directory create",
                               "directory open", "delete", "stat"],
        "preserved": ["negative submission errors", "SAF backend", "synchronous I/O execution",
                      "guest callback execution through FEX", "mount alias behavior"],
        "notClaimed": "inFAMOUS gameplay boot verified on Android or all FIOS APIs implemented",
    }
