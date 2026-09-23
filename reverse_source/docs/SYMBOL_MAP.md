# Binary-to-source symbol map

This map records locations observed in the validated x86-64 runtime family. Addresses are documentation only and must not be used as ABI in reconstructed C++.

| Binary symbol / area | Reconstructed source responsibility |
|---|---|
| `Vulkan::Rasterizer::BindTextures` | image descriptor acquisition / null-image path |
| `Vulkan::Rasterizer::BindResources` | PushData and shader resource binding |
| `Shader::Backend::SPIRV::EmitImageRead` | image fetch and MSAA sample operand handling |
| `Vulkan::TextureCache::ResolveDepthOverlap` | color/depth alias recreation and copies |
| `Shader::Optimization::FlattenExtendedUserdataPass` | SRT flattening and duplicate ReadConst flags |
| Pipeline cache fragment compilation | future AUX-GS generation and module insertion |

## Layout facts recovered from the current source-equivalent model

`Shader::PushData`:
- 4 floats first: xoffset, yoffset, xscale, yscale
- then `ud_regs[16]`
- therefore `ud_regs[1]` is source-level field access, not a stable binary offset

`IR::Inst`:
- ReadConst has two logical arguments
- historical V11 used storage corresponding to the otherwise unused third value slot
- reconstructed code must not depend on unused-object-layout storage
