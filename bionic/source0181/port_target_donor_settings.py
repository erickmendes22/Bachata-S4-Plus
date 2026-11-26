"""Match the tested donor settings and GPU contracts on the retained 0.18.1 FEX cores."""
from pathlib import Path
def apply(root, sotc=False):
    def edit(rel,a,b,n=1):
        p=root/"src"/rel;s=p.read_text()
        if s.count(a)!=n:raise RuntimeError(f"parity anchor {rel}: {a[:100]} ({s.count(a)})")
        p.write_text(s.replace(a,b))
    v="video_core/renderer_vulkan/"
    # Resource keys: all declared binding counts and image types are checked.
    # A live descriptor must have matching shader semantics; a dormant input
    # may reuse a compiled variant without requiring identical presence bits.
    r="shader_recompiler/specialization.h"
    if sotc:
        edit(r,"static constexpr size_t MaxStageResources = 128;",
             "static constexpr size_t MaxStageResources = NUM_BUFFERS + NUM_IMAGES + NUM_FMASKS + NUM_SAMPLERS;")
        edit(r,"            bitset[binding++] = true;","            bitset.set(binding++);")
        edit(r,"        if (!Valid()) {","        if (!Valid() || !other.Valid()) {")
        edit(r,"if (buffers.empty() && images.empty() && samplers.empty())",
             "if (buffers.empty() && images.empty() && fmasks.empty() && samplers.empty() && other.buffers.empty() && other.images.empty() && other.fmasks.empty() && other.samplers.empty())")
    edit(r,"    bool is_srgb = false;","    bool is_srgb = false;\n    bool is_cube = false;\n    bool is_fmask = false;")
    edit(r,"                         spec.is_storage = desc.is_written;","""                         spec.is_storage = desc.is_written;
                         spec.is_cube = sharp.GetType()==AmdGpu::ImageType::Cube;
                         spec.is_fmask = AmdGpu::IsFmask(sharp.GetDataFmt());""")
    edit(r,"                         if (spec.is_storage) {","                         if (spec.is_storage || spec.is_fmask) {")
    # Current 0.18.1 Bindings has only buffer/unified (no donor user_data).
    # Keep strict start for resource-free shaders unless it truly has no
    # resources on either side; no invented field or cross-ABI push constants.
    edit(r,"samplers.size() != other.samplers.size() || bitset != other.bitset) {",
         "samplers.size() != other.samplers.size() || fmasks.size()!=other.fmasks.size()) {")
    # Don't allow a live resource to acquire a null-compiled binding; that
    # can change generated SPIR-V types. A live-compiled resource may become
    # null, as in the donor's directional compatibility.
    edit(r,"if (other.bitset[binding++] && buffers[i] != other.buffers[i]) {",
         "if (other.bitset[binding] && (!bitset[binding] || buffers[i] != other.buffers[i])) {\n                return false;\n            }\n            ++binding;\n            if (false) {")
    edit(r,"if (other.bitset[binding++] && images[i] != other.images[i]) {",
         "if (other.bitset[binding] && (!bitset[binding] || images[i] != other.images[i])) {\n                return false;\n            }\n            ++binding;\n            if (false) {")
    # Remove placeholder branches after transformation (two sites).
    edit(r,"            if (false) {\n                return false;\n            }\n","",2)
    # Metadata struct changed: cache reader checks ABI before decoding.
    ps=root/"src"/v/"vk_pipeline_serialization.cpp"
    s=ps.read_text()
    # Separate cache generation by the new serialization ABI; no APK SHA.
    # Keep assertion-compatible constant name while rejecting old structs.
    import re
    s,n=re.subn(r"(ShaderMetaVersion = )(\d+)u;",lambda m:m[1]+str(int(m[2])+1)+"u;",s)
    assert n==1;ps.write_text(s)
    if not sotc:
        # Latest port logs explicitly select precision mode, synchronous
        # first use with no draw drops. Do not queue/discard geometry.
        edit(v+"vk_pipeline_cache.cpp","    const bool can_queue=CanQueueGraphics(params);",
             "    const bool can_queue=!AmdGpu::BachataOrderNoMsaa()&&CanQueueGraphics(params);")
        edit(v+"vk_pipeline_cache.cpp","if (AmdGpu::BachataOrderNoMsaa() && info.sw_stage != SwStage::Compute &&",
             "if (false && AmdGpu::BachataOrderNoMsaa() && info.sw_stage != SwStage::Compute &&")
        # Exact donor guard already present but restricted to eight consecutive
        # load-mask words. Match the verified table offset contract only
        # when the first loaded word really refers to the table.
        edit("shader_recompiler/resource.h",'''            sharp_fetch.load_mask==0xff &&
            Order1886UnusedLightImage(info,sharp_fetch.offsets[0])) {
            bool contiguous=true;
            for (u32 i=1;i<8;++i)
                contiguous &= sharp_fetch.offsets[i]==sharp_fetch.offsets[0]+i;
            if (contiguous) return AmdGpu::Image::Null(false);
        }''',
             '''            (sharp_fetch.load_mask&1u) &&
            Order1886UnusedLightImage(info,sharp_fetch.offsets[0])) {
            return AmdGpu::Image::Null(false);
        }''')
        edit(v+"host_passes/pp_pass.cpp",'#include "core/emulator_settings.h"',
             '#include "core/emulator_settings.h"\n#include "common/elf_info.h"')
        edit(v+"host_passes/pp_pass.cpp","            .loadOp = vk::AttachmentLoadOp::eClear,",
             '''            .loadOp = Common::ElfInfo::Instance().GameSerial()=="CUSA00785"
                ? vk::AttachmentLoadOp::eDontCare : vk::AttachmentLoadOp::eClear,''')
        # Match actual guest argument list in reference logs, without
        # overriding explicit user arguments or other game's launch.
        edit("emulator.cpp","    std::filesystem::path mods_folder = game_folder;",
             '''    if(id=="CUSA00785") {
        if(args.size()<32 && std::ranges::find(args,"-disablecloth")==args.end())args.emplace_back("-disablecloth");
        if(args.size()<31&&std::ranges::find(args,"-msaa")==args.end()) {
            args.emplace_back("-msaa");args.emplace_back("1");
        }
        LOG_INFO(Loader,"BACHATA_ORDER_ENGINE_ARGS -disablecloth -msaa 1");
    }
    std::filesystem::path mods_folder = game_folder;''')
    # AHB buffers use the actual guest frame size; the physical window remains
    # the coordinate space for SDL and ImGui, with explicit framebuffer scale.
    edit(v+"vk_swapchain.h","    vk::Image Image() const;",
         "    void SetGameExtent(u32 w,u32 h);\n    vk::Image Image() const;")
    edit(v+"vk_swapchain.h","    bool ahb_disabled{};",
         "    bool ahb_disabled{};\n    u32 game_width{},game_height{};")
    edit(v+"vk_swapchain.cpp","        if(candidate->Create(native,extent.width,extent.height)){",
         """        const u32 bw=game_width?game_width:std::min<u32>(extent.width,1280);
        const u32 bh=game_height?game_height:std::min<u32>(extent.height,720);
        if(candidate->Create(native,bw,bh,extent.width,extent.height)){
            extent=vk::Extent2D{bw,bh};""")
    edit(v+"vk_swapchain.cpp",'LOG_INFO(Render_Vulkan,"BACHATA_AHB_SURFACECONTROL_ACTIVE {}x{}",width,height);',
         'LOG_INFO(Render_Vulkan,"BACHATA_AHB_SURFACECONTROL_ACTIVE {}x{} window={}x{}",extent.width,extent.height,width,height);')
    edit(v+"vk_swapchain.cpp","void Swapchain::Recreate(u32 width_, u32 height_) {",
         """void Swapchain::SetGameExtent(u32 w,u32 h) {
#ifdef __ANDROID__
    if(!w||!h||w>8192||h>8192||!ahb)return;
    if(game_width==w&&game_height==h)return;
    game_width=w;game_height=h;
    if(extent.width!=w||extent.height!=h)Recreate(width,height);
#endif
}
void Swapchain::Recreate(u32 width_, u32 height_) {""")
    ahb=root/"src"/v/"vk_ahb_present.h"
    s=ahb.read_text()
    if "ASurfaceTransaction_setGeometry(txn,control,rect,rect,0);" not in s:
        raise RuntimeError("NDK ARect patch missing")
    s=s.replace("bool Create(ANativeWindow* window,u32 w,u32 h) {",
                "bool Create(ANativeWindow* window,u32 w,u32 h,u32 output_w,u32 output_h) {").replace("width=w;height=h;","width=w;height=h;destination_width=output_w;destination_height=output_h;")
    s=s.replace("ASurfaceTransaction_setGeometry(txn,control,rect,rect,0);",
        "const ARect dst{0,0,static_cast<int32_t>(destination_width),static_cast<int32_t>(destination_height)};\n        ASurfaceTransaction_setGeometry(txn,control,rect,dst,0);")
    # Use an explicit independent field; existing width/height declaration varies.
    s=s.replace("    struct Callback {","    u32 destination_width{},destination_height{};\n    struct Callback {",1)
    ahb.write_text(s)
    edit(v+"vk_presenter.cpp","    // Recreate the swapchain if the window was resized.",
         "    if(is_game_frame)swapchain.SetGameExtent(frame->width,frame->height);\n    // Recreate the swapchain if the window was resized.")
    if sotc:
        edit(v+"vk_presenter.h","    Frame* GetRenderFrame();","    Frame* GetRenderFrame(u32 width=0,u32 height=0);")
        edit(v+"vk_presenter.cpp","Frame* Presenter::GetRenderFrame() {",
             "Frame* Presenter::GetRenderFrame(u32 width,u32 height) {\n    if(!width||!height){width=expected_frame_width;height=expected_frame_height;}")
        edit(v+"vk_presenter.cpp","if (frame->width != expected_frame_width || frame->height != expected_frame_height ||",
             "if (frame->width != width || frame->height != height ||")
        edit(v+"vk_presenter.cpp","RecreateFrame(frame, expected_frame_width, expected_frame_height);","RecreateFrame(frame, width, height);")
        edit(v+"vk_presenter.cpp","    texture_cache.UpdateImage(image_id);\n\n    Frame* frame = GetRenderFrame();",
             """    texture_cache.UpdateImage(image_id);

    const auto serial=Common::ElfInfo::Instance().GameSerial();
    const bool native=serial=="CUSA08809"||serial=="CUSA08034";
    Frame* frame=GetRenderFrame(native?attribute.attrib.width:0,native?attribute.attrib.height:0);""")
    # Fit content in AHB pixels, then transform back to ImGui coordinates.
    edit(v+"vk_presenter.cpp","[[nodiscard]] vk::ImageBlit MakeImageBlitFit(",
         """static std::pair<float,float> BachataFitAhbContent(float game_w,float game_h,
                                                     float content_w,float content_h,
                                                     float scale_x,float scale_y) {
    const float fit = std::min(content_w*scale_x/game_w,content_h*scale_y/game_h);
    return {std::min(content_w,game_w*fit/scale_x),
            std::min(content_h,game_h*fit/scale_y)};
}

[[nodiscard]] vk::ImageBlit MakeImageBlitFit(""")
    edit(v+"vk_presenter.cpp",'''                const auto imgRect =
                    FitImage(game_width, game_height, (s32)contentArea.x, (s32)contentArea.y);
                ImVec2 offset{
                    static_cast<float>(imgRect.offset.x),
                    static_cast<float>(imgRect.offset.y),
                };
                ImVec2 size{
                    static_cast<float>(imgRect.extent.width),
                    static_cast<float>(imgRect.extent.height),
                };''',
         '''                // BACHATA_AHB_CONTENT_FIT: fit in the actual framebuffer pixels.
                // SurfaceControl performs the one remaining fit to the output.
                ImVec2 offset{}, size{};
                const auto display_size = ImGui::GetIO().DisplaySize;
                const auto physical_extent = swapchain.GetExtent();
                if (swapchain.PresentLayout() == vk::ImageLayout::eGeneral &&
                    display_size.x > 0 && display_size.y > 0 &&
                    physical_extent.width && physical_extent.height &&
                    game_width && game_height && contentArea.x > 0 && contentArea.y > 0) {
                    const auto fitted = BachataFitAhbContent(
                        game_width,game_height,contentArea.x,contentArea.y,
                        physical_extent.width/display_size.x,
                        physical_extent.height/display_size.y);
                    size = ImVec2{fitted.first,fitted.second};
                    offset = ImVec2{(contentArea.x-size.x)*0.5f,(contentArea.y-size.y)*0.5f};
                } else {
                    const auto imgRect =
                        FitImage(game_width, game_height, (s32)contentArea.x, (s32)contentArea.y);
                    offset = ImVec2{static_cast<float>(imgRect.offset.x),
                                    static_cast<float>(imgRect.offset.y)};
                    size = ImVec2{static_cast<float>(imgRect.extent.width),
                                  static_cast<float>(imgRect.extent.height)};
                }''')
    edit("imgui/renderer/imgui_core.cpp","    ImDrawData* draw_data = GetDrawData();",
         """    ImDrawData* draw_data = GetDrawData();
    // Vulkan viewport/scissors must use the allocated AHB extent, while
    // SDL input and docking coordinates remain in the real window space.
    if(draw_data->DisplaySize.x>0&&draw_data->DisplaySize.y>0)
        draw_data->FramebufferScale=ImVec2(extent.width/draw_data->DisplaySize.x,
                                           extent.height/draw_data->DisplaySize.y);""")
    if not sotc:
        # Donor ISS uses this ABI and expects the local profile string, not a success-only stub.
        edit("core/libraries/system/systemservice.h","int PS4_SYSV_ABI sceSystemServiceParamGetString();",
             "int PS4_SYSV_ABI sceSystemServiceParamGetString(s32 id,char* value,u64 size);")
        edit("core/libraries/system/systemservice.cpp",'''int PS4_SYSV_ABI sceSystemServiceParamGetString() {
    LOG_ERROR(Lib_SystemService, "(STUBBED) called");
    return ORBIS_OK;
}''',r'''static int BachataIssParamString(s32 id,char* value,u64 size) {
    if(id!=6||!value||!size)return ORBIS_SYSTEM_SERVICE_ERROR_PARAMETER;
    constexpr char player[]="Player";
    u64 i=0;
    for(;i+1<size&&i<sizeof(player)-1;++i)value[i]=player[i];
    value[i]='\0';
    return ORBIS_OK;
}

int PS4_SYSV_ABI sceSystemServiceParamGetString(s32 id,char* value,u64 size) {
    const auto serial=Common::ElfInfo::Instance().GameSerial();
    if(serial=="CUSA00004"||serial=="CUSA00223")
        return BachataIssParamString(id,value,size);
    LOG_ERROR(Lib_SystemService, "(STUBBED) called");
    return ORBIS_OK;
}''')
    return {"specialization":"directional live binding compatibility, cube/FMask class, cache ABI increment",
            "presentation":"guest-sized AHB and scaled UI draw data, physical output geometry",
            "orderAccuracy":"synchronous no draw drops, exact light guard, opaque PP no-clear and verified engine arguments" if not sotc else None}
