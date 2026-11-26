"""Classify actual Order barrier closures and image-alias registration decisions.

No hazard, resource eligibility or command ordering decision changes. Pending
causes live with Runtime so recorder/owner handoffs do not lose provenance.
Windows are per owner/thread, with a clock only once per 1,024 events.
"""
from pathlib import Path


HEADER = r'''// SPDX-License-Identifier: GPL-2.0-or-later
#pragma once
#include <array>
#include <chrono>
#include <cstdint>
#include "common/types.h"
#ifndef LOG_INFO
#include "common/logging/log.h"
#endif

namespace Vulkan {
enum class OrderBarrierOrigin : u32 {
    Other, Buffer, ReadConst, Gds, Texture, Attachment, Vertex, Index, Indirect, Dispatch, Count
};
// The scope is lexical, including nested uploads/refreshes. It carries no
// pointer into a descriptor or an asynchronously consumed command.
class OrderBarrierScope {
public:
    OrderBarrierScope(const void* owner, OrderBarrierOrigin origin)
        : previous{current} { current = {owner, origin}; }
    ~OrderBarrierScope() { current = previous; }
    OrderBarrierScope(const OrderBarrierScope&) = delete;
    OrderBarrierScope& operator=(const OrderBarrierScope&) = delete;
    static OrderBarrierOrigin Origin(const void* owner) {
        return current.owner == owner ? current.origin : OrderBarrierOrigin::Other;
    }
private:
    struct Context { const void* owner; OrderBarrierOrigin origin; };
    inline static thread_local Context current{nullptr, OrderBarrierOrigin::Other};
    const Context previous;
};
enum class OrderBarrierKind : u32 { BufferRaw, BufferWaw, BufferWar, ImageLayout, ImageAccess, ImageWrite, Count };
struct OrderBarrierPending { u64 kinds{}, origins{}; };
inline void NoteOrderBarrier(OrderBarrierPending& pending, const void* owner, OrderBarrierKind kind) {
    pending.kinds |= u64{1} << static_cast<u32>(kind);
    pending.origins |= u64{1} << static_cast<u32>(OrderBarrierScope::Origin(owner));
}

inline void CountOrderBarrierFlush(const void* owner, OrderBarrierPending causes,
                                   bool open, bool memory, bool images) {
    if (!open) return;
    struct Window {
        const void* owner{};
        u64 total{}, memory_only{}, image_only{}, mixed{}, unknown{};
        std::array<u64, static_cast<u32>(OrderBarrierKind::Count)> kinds{};
        std::array<u64, static_cast<u32>(OrderBarrierOrigin::Count)> origins{};
        std::chrono::steady_clock::time_point start{};
        u32 unchecked{};
    };
    thread_local std::array<Window, 8> windows{};
    Window* selected{};
    for (auto& item : windows) {
        if (item.owner == owner) { selected = &item; break; }
        if (!item.owner && !selected) selected = &item;
    }
    if (!selected) selected = &windows[0];
    if (selected->owner != owner) {
        *selected = {}; selected->owner = owner; selected->start = std::chrono::steady_clock::now();
    }
    auto& w = *selected;
    ++w.total; w.memory_only += memory && !images; w.image_only += images && !memory;
    w.mixed += memory && images; w.unknown += causes.kinds == 0;
    for (u32 i=0; i<w.kinds.size(); ++i) w.kinds[i] += (causes.kinds >> i) & 1;
    for (u32 i=0; i<w.origins.size(); ++i) w.origins[i] += (causes.origins >> i) & 1;
    if (++w.unchecked < 1024) return;
    w.unchecked=0;
    const auto now=std::chrono::steady_clock::now();
    const auto us=std::chrono::duration_cast<std::chrono::microseconds>(now-w.start).count();
    if (us < 5'000'000) return;
    const auto wall=std::chrono::duration_cast<std::chrono::milliseconds>(
        std::chrono::system_clock::now().time_since_epoch()).count();
    LOG_INFO(Render_Vulkan,
        "BACHATA_ORDER_BARRIER_CAUSE owner={} wall_ms={} window_us={} closed={} "
        "memory_only={} image_only={} mixed={} unattributed={} buffer_raw={} buffer_waw={} buffer_war={} "
        "image_layout={} image_access={} image_write={} other={} buffers={} readconst={} gds={} "
        "textures={} attachments={} vertex={} index={} indirect={} dispatch={}",
        reinterpret_cast<std::uintptr_t>(owner),wall,us,w.total,w.memory_only,w.image_only,w.mixed,w.unknown,
        w.kinds[0],w.kinds[1],w.kinds[2],w.kinds[3],w.kinds[4],w.kinds[5],
        w.origins[0],w.origins[1],w.origins[2],w.origins[3],w.origins[4],w.origins[5],
        w.origins[6],w.origins[7],w.origins[8],w.origins[9]);
    const auto saved_owner=w.owner; w={};w.owner=saved_owner;w.start=now;
}

struct OrderAliasProbe { u64 same_base{}, eligible{}, layout{}, shape_format{}, one_way{}; };
enum class OrderAliasEvent { Registration, Write, Synchronize };
inline void CountOrderAliasProbe(const void* owner, OrderAliasEvent event, bool aliased,
                                 const OrderAliasProbe& probe = {}) {
    struct Window {
        const void* owner{};
        u64 registrations{},registered_aliases{},writes{},alias_writes{},syncs{},alias_syncs{};
        OrderAliasProbe probe;
        std::chrono::steady_clock::time_point start{};
        u32 unchecked{};
    };
    thread_local std::array<Window, 8> windows{};
    static thread_local Window* last_selected{};
    Window* selected=last_selected&&last_selected->owner==owner?last_selected:nullptr;
    if (!selected) {
        for (auto& item : windows) {
            if (item.owner==owner) {selected=&item;break;}
            if (!item.owner&&!selected) selected=&item;
        }
        if (!selected) selected=&windows[0];
        last_selected=selected;
    }
    if (selected->owner!=owner) {
        *selected={};selected->owner=owner;selected->start=std::chrono::steady_clock::now();
    }
    auto& w=*selected;
    if (event==OrderAliasEvent::Registration) {
        ++w.registrations;w.registered_aliases+=aliased;
        w.probe.same_base+=probe.same_base;w.probe.eligible+=probe.eligible;
        w.probe.layout+=probe.layout;w.probe.shape_format+=probe.shape_format;w.probe.one_way+=probe.one_way;
    } else if (event==OrderAliasEvent::Write) {++w.writes;w.alias_writes+=aliased;}
    else {++w.syncs;w.alias_syncs+=aliased;}
    if (++w.unchecked<1024) return;
    w.unchecked=0;
    const auto now=std::chrono::steady_clock::now();
    const auto us=std::chrono::duration_cast<std::chrono::microseconds>(now-w.start).count();
    if (us<5'000'000) return;
    const auto wall=std::chrono::duration_cast<std::chrono::milliseconds>(
        std::chrono::system_clock::now().time_since_epoch()).count();
    LOG_INFO(Render_Vulkan,
        "BACHATA_ORDER_ALIAS_CENSUS owner={} wall_ms={} window_us={} registrations={} registered_aliases={} "
        "same_base={} eligible={} layout_reject={} shape_format_reject={} one_way_reject={} "
        "writes={} alias_writes={} syncs={} alias_syncs={}",
        reinterpret_cast<std::uintptr_t>(owner),wall,us,w.registrations,w.registered_aliases,
        w.probe.same_base,w.probe.eligible,w.probe.layout,w.probe.shape_format,w.probe.one_way,
        w.writes,w.alias_writes,w.syncs,w.alias_syncs);
    const auto saved_owner=w.owner;w={};w.owner=saved_owner;w.start=now;
}
} // namespace Vulkan
'''


ALIAS_PROBE = r'''
Vulkan::OrderAliasProbe TextureCache::ProbeOrderAliasRegistration(const Image& image) const {
    Vulkan::OrderAliasProbe probe;
    const auto page=page_table.find(image.info.guest_address >> Traits::PAGE_BITS);
    if (!page) return probe;
    for (const ImageId id : *page) {
        const auto& candidate=slot_images[id];
        const auto& a=candidate.info;const auto& b=image.info;
        if (&candidate==&image || a.guest_address!=b.guest_address) continue;
        ++probe.same_base;
        const bool forward=GetOrderAliasCopyExtent(a,b).has_value();
        const bool reverse=GetOrderAliasCopyExtent(b,a).has_value();
        if (forward&&reverse) {++probe.eligible;continue;}
        if (forward!=reverse) {++probe.one_way;continue;}
        if (a.num_bits!=b.num_bits || a.num_samples!=b.num_samples || a.props.is_depth || b.props.is_depth ||
            a.props.is_block!=b.props.is_block || a.props.is_pow2!=b.props.is_pow2 || a.type!=b.type ||
            a.pitch!=b.pitch || a.tile_mode!=b.tile_mode || a.array_mode!=b.array_mode ||
            a.bank_swizzle!=b.bank_swizzle || a.alt_tile!=b.alt_tile) ++probe.layout;
        else ++probe.shape_format;
    }
    return probe;
}

'''


def once(text: str, old: str, new: str, label: str) -> str:
    if text.count(old) != 1: raise RuntimeError(f"Order barrier census anchor drift: {label}")
    return text.replace(old, new, 1)


def span(text: str, marker: str) -> tuple[int, int]:
    if text.count(marker) != 1: raise RuntimeError(f"Order barrier census function drift: {marker}")
    begin=text.index(marker);opening=text.index("{",begin);depth=1;end=opening+1
    while depth:
        depth+=(text[end]=="{")-(text[end]=="}");end+=1
    return begin,end


def edit_function(text: str, marker: str, transform) -> str:
    begin,end=span(text,marker)
    return text[:begin]+transform(text[begin:end])+text[end:]


def apply(root):
    root=Path(root)/"src"
    names=("video_core/renderer_vulkan/vk_runtime.h","video_core/renderer_vulkan/vk_runtime.cpp",
           "video_core/renderer_vulkan/vk_rasterizer.cpp","video_core/renderer_vulkan/vk_scheduler.h",
           "video_core/texture_cache/texture_cache.h","video_core/texture_cache/texture_cache.cpp")
    files={name:(root/name).read_text() for name in names}
    rh,rc,rr,sh,th,tc=names
    include='#include "video_core/renderer_vulkan/order_resource_census.h"\n'
    if (root/"video_core/renderer_vulkan/order_resource_census.h").exists():
        raise RuntimeError("Order resource census already applied")
    files[rh]=include+files[rh]
    files[th]=include+files[th]
    files[rh]=once(files[rh],"    bool donor_range_tracking{};",
        "    bool donor_range_tracking{};\n    bool order_resource_census{};\n    OrderBarrierPending order_barrier_pending{};", "runtime pending causes")
    files[rc]=once(files[rc], '    donor_range_tracking=serial=="CUSA00785"||serial=="CUSA08809"||serial=="CUSA08034";',
        '    donor_range_tracking=serial=="CUSA00785"||serial=="CUSA08809"||serial=="CUSA08034";\n#ifdef __ANDROID__\n    order_resource_census=serial=="CUSA00785";\n#endif', "runtime policy")
    files[sh]=once(files[sh], "    [[nodiscard]] u64 RenderingSerial() const noexcept { return rendering_serial; }",
        "    [[nodiscard]] u64 RenderingSerial() const noexcept { return rendering_serial; }\n    [[nodiscard]] bool RenderingActive() const noexcept { return is_rendering; }", "open scope query")

    def access(body):
        body=once(body, "        return donor_barriers.FindRange(range,Access::Write) ||\n            (check_read_access && donor_barriers.FindRange(range,Access::Read));", r'''        const bool prior_write=donor_barriers.FindRange(range,Access::Write);
        const bool prior_read=!prior_write && check_read_access && donor_barriers.FindRange(range,Access::Read);
        if (order_resource_census && (prior_write || prior_read))
            NoteOrderBarrier(order_barrier_pending,this,prior_read ? OrderBarrierKind::BufferWar :
                check_read_access ? OrderBarrierKind::BufferWaw : OrderBarrierKind::BufferRaw);
        return prior_write || prior_read;''', "range tracker result")

        return body
    files[rc]=edit_function(files[rc],"bool Runtime::IsBufferAccessed(",access)

    def transit(body):
        return once(body,"    return image_barriers.size() != prev_num_barriers;",r'''    if (order_resource_census) for (size_t i=prev_num_barriers; i<image_barriers.size(); ++i) {
        const auto& barrier=image_barriers[i];
        constexpr auto writes=vk::AccessFlagBits2::eTransferWrite | vk::AccessFlagBits2::eShaderWrite |
                              vk::AccessFlagBits2::eMemoryWrite;
        NoteOrderBarrier(order_barrier_pending,this,barrier.oldLayout!=barrier.newLayout
            ? OrderBarrierKind::ImageLayout : (barrier.srcAccessMask & writes)
            ? OrderBarrierKind::ImageWrite : OrderBarrierKind::ImageAccess);
    }
    return image_barriers.size() != prev_num_barriers;''',"image transition results")
    files[rc]=edit_function(files[rc],"bool Runtime::Transit(",transit)

    def flush(body):
        return once(body,"    scheduler.EndRendering(Vulkan::OrderPassEndReason::Barrier);",r'''    if (order_resource_census) {
        CountOrderBarrierFlush(this,order_barrier_pending,scheduler.RenderingActive(),
                               dep_info.memoryBarrierCount!=0,dep_info.imageMemoryBarrierCount!=0);
        order_barrier_pending={};
    }
    scheduler.EndRendering(Vulkan::OrderPassEndReason::Barrier);''',"actual barrier closure")
    files[rc]=edit_function(files[rc],"void Runtime::FlushBarriers()",flush)

    scopes={"void Rasterizer::BindBuffers(":"Buffer", "void Rasterizer::BindTextures(":"Texture",
            "RenderState Rasterizer::BeginRenderingFull(":"Attachment", "void Rasterizer::BindVertexBuffers(":"Vertex",
            "void Rasterizer::BindIndexBuffer(":"Index", "void Rasterizer::DrawIndirect(":"Indirect",
            "void Rasterizer::DispatchDirect(":"Dispatch", "void Rasterizer::DispatchIndirect(":"Indirect"}
    for marker,origin in scopes.items():
        files[rr]=edit_function(files[rr],marker,lambda body,origin=origin:body.replace("{", "{\n    const OrderBarrierScope order_barrier_scope{&runtime,OrderBarrierOrigin::"+origin+"};",1))
    files[rr]=once(files[rr], "            if (desc.buffer_type == Shader::BufferType::GdsBuffer) {",
        "            if (desc.buffer_type == Shader::BufferType::GdsBuffer) {\n                const OrderBarrierScope gds_scope{&runtime,OrderBarrierOrigin::Gds};", "GDS source")
    files[rr]=once(files[rr], "            const auto vsharp = desc.GetSharp(stage);",
        "            const OrderBarrierScope buffer_scope{&runtime,desc.used_as_readconst ? OrderBarrierOrigin::ReadConst : OrderBarrierOrigin::Buffer};\n            const auto vsharp = desc.GetSharp(stage);", "ReadConst source")

    files[th]=once(files[th],"    void RegisterAlias(ImageId image_id);",
        "    Vulkan::OrderAliasProbe ProbeOrderAliasRegistration(const Image& image) const;\n    void RegisterAlias(ImageId image_id);", "alias registration probe API")
    files[tc]=once(files[tc],"void TextureCache::RegisterAlias(ImageId image_id) {",ALIAS_PROBE+"void TextureCache::RegisterAlias(ImageId image_id) {", "alias probe")
    def registration(body):
        # The extra scan occurs only at registration. Existing CanAlias and the
        # authority selection below remain exactly as in the verified overlay.
        return body[:-1]+r'''    if (ImageAliasesEnabled())
        Vulkan::CountOrderAliasProbe(this,Vulkan::OrderAliasEvent::Registration,
            True(slot_images[image_id].flags & ImageFlagBits::Aliased),
            ProbeOrderAliasRegistration(slot_images[image_id]));
}'''
    files[tc]=edit_function(files[tc],"void TextureCache::RegisterAlias(",registration)
    for marker,event in (("void TextureCache::PublishAliasWrite(","Write"),
                         ("void TextureCache::SynchronizeAlias(","Synchronize")):
        files[tc]=edit_function(files[tc],marker,lambda body,event=event:body.replace("{", "{\n    if (ImageAliasesEnabled()) Vulkan::CountOrderAliasProbe(this,Vulkan::OrderAliasEvent::"+event+",\n        True(slot_images[image_id].flags & ImageFlagBits::Aliased));",1))
    for name in names:(root/name).write_text(files[name])
    (root/"video_core/renderer_vulkan/order_resource_census.h").write_text(HEADER)
    print("BACHATA_ORDER_BARRIER_CAUSE / ALIAS_CENSUS overlay applied")
    return {"marker":"BACHATA_ORDER_BARRIER_CAUSE", "alias_marker":"BACHATA_ORDER_ALIAS_CENSUS",
            "files":list(names)+["video_core/renderer_vulkan/order_resource_census.h"],
            "policy":"Android CUSA00785", "clock":"1024 events / >=5 seconds", "behavior":"observational"}


if __name__=="__main__":
    import sys
    apply(sys.argv[1])
