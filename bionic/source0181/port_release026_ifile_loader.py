#!/usr/bin/env python3
"""Real Release 0.2.6/0.2.7 IFile-backed ELF/module loader for ARM64 FEX.

The actual 0.16.1-FEX host was retained by rebase_arm64.py even where
shadPS4 0.18.1 has replaced Core::Module and Core::Loader::Elf with a
SAF/overlay-friendly IFile constructor. This port restores the modern/
Release loading ABI WITHOUT replacing the original FEX guest execution,
relocation and TLS model, which are still required on Android ARM64.

The loader distinguishes guest "/app0/..." from app-private system library
paths; both use independent IFile handles so file descriptor ownership is
preserved throughout module load. No synthesized fake successful module.
"""
from pathlib import Path


def replace_once(text: str, old: str, new: str, label: str) -> str:
    n=text.count(old)
    if n != 1:
        raise RuntimeError(f"FEX loader source drift: {label}: found {n} anchors")
    return text.replace(old,new,1)


def apply(root: Path) -> dict:
    elf_h=root/"src/core/loader/elf.h"
    elf_c=root/"src/core/loader/elf.cpp"
    module_h=root/"src/core/module.h"
    module_c=root/"src/core/module.cpp"
    linker=root/"src/core/linker.cpp"
    h=elf_h.read_text();c=elf_c.read_text()
    mh=module_h.read_text();mc=module_c.read_text();li=linker.read_text()
    h=replace_once(h,
        "#include \"common/io_file.h\"\n",
        "#include \"common/io_file.h\"\n"
        "#include \"core/file_sys/ifile.h\"\n",
        "modern IFile Elf header")
    h=replace_once(h,
        "    void Open(const std::filesystem::path& file_name);\n",
        "    void Open(const std::filesystem::path& file_name);\n"
        "    void Open(std::unique_ptr<Core::FileSys::IFile> handle);\n",
        "Elf owning descriptor overload")
    h=replace_once(h,
        "    Common::FS::IOFile m_f{};",
        "    Core::FileSys::FileReader m_f{};",
        "modern bounded ELF FileReader")
    c=replace_once(c,
        "#include \"core/loader/elf.h\"\n",
        "#include \"core/file_sys/backends/host_fs.h\"\n"
        "#include \"core/loader/elf.h\"\n",
        "ELF host-file compatibility include")
    c=replace_once(c,
        """void Elf::Open(const std::filesystem::path& file_name) {
    m_f.Open(file_name, FileAccessMode::Read);
    if (!m_f.ReadObject(m_self)) {""",
        """void Elf::Open(const std::filesystem::path& file_name) {
    auto owned = std::make_unique<Core::FileSys::HostFile>(
        file_name, FileAccessMode::Read, /*read_only=*/true);
    if (!owned->IsOpen()) return;
    Open(std::move(owned));
}

void Elf::Open(std::unique_ptr<Core::FileSys::IFile> owned) {
    m_f.Reset(std::move(owned));
    if (!m_f.IsOpen()) return;
    if (!m_f.ReadObject(m_self)) {""",
        "Release IFile-based ELF parser")
    mh=replace_once(mh,
        """    explicit Module(Core::MemoryManager* memory, const std::filesystem::path& file,
                    u32& max_tls_index);""",
        """    // Release 0.2.6/0.2.7: ELF and SELF files are owned guest IFile
    // objects. Keep FEX-specific module initialization, relocations and TLS.
    Module(Core::MemoryManager* memory, const std::filesystem::path& file,
           std::unique_ptr<Core::FileSys::IFile> source, u32& max_tls_index);""",
        "Module Release IFile argument")
    # elf.h already includes IFile; add explicit header for public signature.
    mh=replace_once(mh,
        '#include "core/loader/elf.h"\n',
        '#include "core/loader/elf.h"\n#include "core/file_sys/ifile.h"\n',
        "Module public owning IFile header")
    mc=replace_once(mc,
        """Module::Module(Core::MemoryManager* memory_, const std::filesystem::path& file_, u32& max_tls_index)
    : memory{memory_}, file{file_}, name{file.filename().string()} {
    elf.Open(file);""",
        """Module::Module(Core::MemoryManager* memory_, const std::filesystem::path& file_,
               std::unique_ptr<Core::FileSys::IFile> source, u32& max_tls_index)
    : memory{memory_}, file{file_}, name{file.filename().string()} {
    // BACHATA_RELEASE026_MODULE_IFILE: never reopen a guest ELF via
    // host files after the Android/SAF broker has opened its descriptor.
    elf.Open(std::move(source));""",
        "actual Module constructor preserving FEX execution")
    li=replace_once(li,
        '#include "core/linker.h"\n',
        '#include "core/file_sys/fs.h"\n'
        '#include "core/file_sys/backends/host_fs.h"\n'
        '#include "core/linker.h"\n',
        "Linker to virtual mount and host system file")
    li=replace_once(li,
        """    if (!std::filesystem::exists(elf_name)) {
        LOG_ERROR(Core_Linker, "Provided file {} does not exist", elf_name.string());
        return -1;
    }

    auto module = std::make_unique<Module>(memory, elf_name, max_tls_index);""",
        """    // BACHATA_RELEASE026_LOADER_IFILE: guest file imports pass through
    // the mounted backend stack (including Android SAF and game updates).
    // App-private sysmodules are already real host files, not /app0 guests.
    const std::string path=elf_name.generic_string();
    const bool guest_path=path.starts_with("/app0/") ||
                          path.starts_with("app0/") ||
                          path.starts_with("/hostapp/") ||
                          path.starts_with("hostapp/");
    std::unique_ptr<Core::FileSys::IFile> source;
    if (guest_path) {
        source=Common::Singleton<Core::FileSys::MntPoints>::Instance()->Open(path);
    } else {
        auto host=std::make_unique<Core::FileSys::HostFile>(
            elf_name, Common::FS::FileAccessMode::Read, /*read_only=*/true);
        if(host->IsOpen())source=std::move(host);
    }
    if (!source || !source->IsOpen()) {
        LOG_ERROR(Core_Linker,
                  "BACHATA_RELEASE026_LOADER_IFILE_OPEN_FAILED path='{}' guest={}",
                  path,guest_path);
        return -1;
    }

    auto module=std::make_unique<Module>(memory,elf_name,std::move(source),max_tls_index);""",
        "IFile acquisition for PS4 guest modules")
    # Must not leave an accidental old Module construction.
    if "std::make_unique<Module>(memory, elf_name, max_tls_index)" in li:
        raise RuntimeError("Unsafe pathname-only FEX module constructor remains")
    for path,src in ((elf_h,h),(elf_c,c),(module_h,mh),(module_c,mc),(linker,li)):
        path.write_text(src)
    return {
        "ported": [
            "Core::Loader::Elf::Open(std::unique_ptr<IFile>)",
            "Core::Module::Module(memory,path,IFile,max_tls_index)",
            "Core::Linker::LoadModule guest mount IFile acquisition",
        ],
        "existingFex": "FEX module Start, relocation and TLS retained",
        "guest": "real SAF/MntPoints backend instead of host path reopening",
        "system": "real system-library file owned by HostFile IFile",
    }
