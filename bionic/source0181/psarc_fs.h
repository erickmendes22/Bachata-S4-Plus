// SPDX-FileCopyrightText: Copyright 2026 Bachata S4+ contributors
// SPDX-License-Identifier: GPL-2.0-or-later
#pragma once

// PSARC virtual filesystem for PS4 FIOS2 archives. The original Android FEX
// fallback mounted /app0 instead of the requested PSARC and reported success.
// This backend retains the real archive (which can itself come from SAF) and
// decompresses only requested blocks. No huge staging extraction or game
// title-specific paths.
#include <filesystem>
#include <memory>
#include <string_view>
#include "core/file_sys/ifile.h"

namespace Core::FileSys {
struct PsarcStorage;
class PsarcBackend final : public IBackend {
public:
    explicit PsarcBackend(std::unique_ptr<IFile> archive);
    ~PsarcBackend() override;
    bool IsOpen() const;
    bool Exists(std::string_view rel) override;
    bool IsDirectory(std::string_view rel) override;
    std::unique_ptr<IFile> Open(std::string_view rel, Common::FS::FileAccessMode mode) override;
    std::unique_ptr<IDirectory> OpenDir(std::string_view rel) override;
    bool IsReadOnly() const override { return true; }
    std::filesystem::path RootPath() const override { return {}; }
    std::optional<std::vector<u8>> ReadFile(std::string_view rel) const override;

private:
    std::shared_ptr<PsarcStorage> m_shared;
};
} // namespace Core::FileSys
