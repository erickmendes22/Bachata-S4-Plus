// SPDX-FileCopyrightText: Copyright 2026 Bachata S4+ contributors
// SPDX-License-Identifier: GPL-2.0-or-later
#pragma once
#include <memory>
#include <string_view>
#include "core/file_sys/ifile.h"

namespace Core::FileSys {
// Working Bachata Release contains a real SafFsBackend/SafBrokerClient pair.
// The 0.18.1 port's symlink-backed MntPoints::Open fallback lacks their
// independent descriptor-backed IFile behavior. Return a read-only guest
// file that owns its own Android broker fd, never the shared symlink fd.
std::unique_ptr<IFile> OpenSafGuestFile(std::string_view guest_path);
} // namespace Core::FileSys
