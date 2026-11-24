// SPDX-License-Identifier: GPL-2.0-or-later
#pragma once
#include <string_view>
#include <vector>
namespace BachataDispatch {
inline bool SotcRoot(std::string_view path) {
    while (!path.empty() && path.back()=='/') path.remove_suffix(1);
    const auto slash=path.rfind('/');
    const auto name=slash==std::string_view::npos?path:path.substr(slash+1);
    return name=="CUSA08809" || name=="CUSA08034";
}
inline bool SotcArgs(const std::vector<std::string_view>& args) {
    // Actual service command: --override-root <root>/CUSA08809 -g eboot.bin.
    // Do not select by arbitrary substring in a filename or environment.
    for(size_t i=0;i+1<args.size();++i)
        if(args[i]=="--override-root")return SotcRoot(args[i+1]);
    return false;
}
}
