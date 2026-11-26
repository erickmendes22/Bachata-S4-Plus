#!/usr/bin/env python3
"""Execute effective ASC framing, PM4 predicates and the CP/VO wait graph.

The source prefix is copied verbatim from ProcessCompute, including split
assembly, Type-2 handling and read-pointer calls. Release/wait/IB packets use
the actual wire types and methods. The packet dispatch sink omits Vulkan and
coroutine scheduling. The companion gate then executes the actual CP/VO
methods. These gates prove framing, predicates and progress, not device
gameplay or the cause of a particular truncated diagnostic.
"""
import argparse
from pathlib import Path
import subprocess
import sys
import tempfile


def block(text, marker, semi=False):
    start = text.index(marker)
    opening = text.index("{", start)
    depth = 0
    for end in range(opening, len(text)):
        depth += (text[end] == "{") - (text[end] == "}")
        if not depth:
            return text[start:end + 1 + semi]
    raise AssertionError("unclosed source block: " + marker)


parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--source", required=True, type=Path)
args = parser.parse_args()
src = args.source.resolve() / "src"
cp = (src / "video_core/amdgpu/liverpool.cpp").read_text()
cp_header = (src / "video_core/amdgpu/liverpool.h").read_text()
wire_header = (src / "video_core/amdgpu/pm4_cmds.h").read_text()
asc = cp[cp.index("Liverpool::Task Liverpool::ProcessCompute("):]
prefix = asc[asc.index("        auto* header ="):asc.index("        const PM4ItOpcode opcode =")]
assert "BACHATA_SOTC_ASC_PACKET_BOUNDARY" in prefix
assert "header->type == 2 ? 1 : header->type3.NumWords() + 1" in prefix
assert prefix.index("header->type == 2 ?") < prefix.index("if (next_dw_off > acb.size())")
wire = wire_header[wire_header.index("enum class PM4ShaderType"):
                   wire_header.index("union ContextControlEnable")]
for name in ("DataSelect", "InterruptSelect"):
    wire += block(wire_header, "enum class " + name, True) + "\n"
for name in ("PM4CmdReleaseMem", "PM4CmdWaitRegMem", "PM4CmdIndirectBuffer", "PM4CmdRewind"):
    wire += block(wire_header, "struct " + name + " {", True) + "\n"
semaphore_signaled = block(wire_header, "    [[nodiscard]] bool Signaled(")
next_packet = block(cp, "static std::span<const u32> NextPacket(")
rptr = block(cp, "void Liverpool::AdvanceReadPointer(").replace("Liverpool::", "Probe::")
# This group must not reintroduce the separately reverted read-pointer policy.
assert "*read_addr=(*read_addr+dwords)%ring_size_dw;" in rptr
assert "InvalidateMemory" not in rptr and "TryWriteBacking" not in rptr
queue = block(cp_header, "    struct AscQueueInfo {", True)

PROGRAM = r'''
#include <algorithm>
#include <array>
#include <bit>
#include <cassert>
#include <cstring>
#include <iostream>
#include <span>
#include <stdexcept>
#include <vector>
#include "common/types.h"
#include "common/bit_field.h"
#include "video_core/amdgpu/pm4_opcodes.h"
#define ASSERT(x) assert(x)
#define LOG_ERROR(...) ((void)0)
#define UNREACHABLE() throw std::runtime_error("unreachable PM4 data selector")
#define UNREACHABLE_MSG(...) throw std::runtime_error("invalid PM4 type")
namespace AmdGpu {
u64 GetGpuClock64(){return 123;}
u64 GetGpuPerfCounter(){return 456;}
@WIRE@
@NEXT@
// Only the 40-bit guest-address mapping is a boundary substitute. The
// semaphore predicate and observation body below are the effective method.
struct SemaphoreProbe {
    u64 value{};
    template<class T> T Address() const {
        return reinterpret_cast<T>(const_cast<u64*>(&value));
    }
@SEMAPHORE_SIGNALED@
};
struct Probe {
@QUEUE@
    u32 read_pointer{};
    AscQueueInfo queue{.map_addr=0,.read_addr=&read_pointer,.ring_size_dw=4096,
                       .pipe_id=0,.tmp_packet={},.tmp_dwords=0};
    std::array<u32,16> registers{};
    u32 irq{},packets{},waits{},nops{},indirects{};
    void AdvanceReadPointer(u32*,u32,u32);
    template<bool is_indirect=false>void Feed(std::span<const u32> acb) {
      while(!acb.empty()) {
@PREFIX@
        switch(header->type3.opcode.Value()) {
        case PM4ItOpcode::ReleaseMem: {
            const auto* release=reinterpret_cast<const PM4CmdReleaseMem*>(header);
            release->SignalFence([&]{++irq;},[](VAddr,u16,u16){assert(false);});
            break;
        }
        case PM4ItOpcode::WaitRegMem: {
            const auto* wait=reinterpret_cast<const PM4CmdWaitRegMem*>(header);
            assert(wait->Test(registers));++waits;
            break;
        }
        case PM4ItOpcode::IndirectBuffer: {
            const auto* ib=reinterpret_cast<const PM4CmdIndirectBuffer*>(header);
            ++indirects;
            Feed<true>({ib->Address<const u32>(),ib->ib_size.Value()});
            break;
        }
        case PM4ItOpcode::Nop:++nops;break;
        default:throw std::runtime_error("unexpected PM4 opcode after framing");
        }
        ++packets;
        acb=NextPacket(acb,next_dw_off);
        if constexpr(!is_indirect)AdvanceReadPointer(queue.read_addr,next_dw_off,queue.ring_size_dw);
      }
    }
};
@RPTR@
template<class T> auto Encode(const T& packet) {
    static_assert(sizeof(T)%sizeof(u32)==0);
    return std::bit_cast<std::array<u32,sizeof(T)/sizeof(u32)>>(packet);
}
auto Release(u64& label,u32 value=1) {
    const auto address=reinterpret_cast<uintptr_t>(&label);
    PM4CmdReleaseMem packet{.header{PM4ItOpcode::ReleaseMem,5},.dw1=0,.dw2=0,
        .address_lo=u32(address),.address_hi=u32(address>>32),.data_lo=value,.data_hi=0};
    packet.data_sel.Assign(DataSelect::Data32Low);
    packet.int_sel.Assign(InterruptSelect::IrqWhenWriteConfirm);
    return Encode(packet);
}
auto Wait(u64& label,u32 value=1) {
    const auto address=reinterpret_cast<uintptr_t>(&label);
    PM4CmdWaitRegMem packet{.header{PM4ItOpcode::WaitRegMem,5},.raw=0,.poll_addr_lo_raw=0,
        .poll_addr_hi=u32(address>>32),.ref=value,.mask=~u32{},.poll_interval=0};
    packet.mem_space.Assign(PM4CmdWaitRegMem::MemSpace::Memory);
    packet.poll_addr_lo.Assign(u32(address)>>2);
    packet.function.Assign(PM4CmdWaitRegMem::Function::Equal);
    return Encode(packet);
}
void Append(std::vector<u32>& out,std::span<const u32> words) {
    out.insert(out.end(),words.begin(),words.end());
}
void TestAllPaddingCountBits() {
    u64 cases=0;
    for(u32 count=0;count<16384;++count)for(bool indirect:{false,true}) {
        alignas(8) u64 label=0;Probe cp;cp.read_pointer=4095;
        const std::array<u32,1> padding{0x80000000u|(count<<16)|(count*13u&0xffffu)};
        if(indirect)cp.Feed<true>(padding);else cp.Feed(padding);
        assert(cp.queue.tmp_dwords==0&&cp.read_pointer==(indirect?4095u:0u));
        const auto release=Release(label),wait=Wait(label);
        if(indirect){cp.Feed<true>(release);cp.Feed<true>(wait);}
        else {cp.Feed(release);cp.Feed(wait);}
        assert(label==1&&cp.irq==1&&cp.waits==1&&cp.packets==2);
        assert(cp.read_pointer==(indirect?4095u:14u)&&cp.queue.tmp_dwords==0);
        ++cases;
    }
    std::cout<<"SOTC_ASC_PADDING_ALL_COUNT_BITS cases="<<cases<<" direct/IB/RELEASE_MEM/WAIT=PASS\n";
}
void TestDoublePaddingAndIb() {
    u64 cases=0;
    for(u32 a:{0u,1u,17u,1023u,16382u,16383u})
    for(u32 b:{0u,2u,31u,16383u})for(bool separate:{false,true}) {
        alignas(8) u64 label=0;Probe cp;
        const std::array<u32,2> padding{0x80000000u|(a<<16),0x80000000u|(b<<16)};
        if(separate){cp.Feed(std::span(padding).first(1));cp.Feed(std::span(padding).last(1));}
        else cp.Feed(padding);
        assert(cp.queue.tmp_dwords==0&&cp.read_pointer==2);
        std::vector<u32> inner{padding.begin(),padding.end()};
        Append(inner,Release(label));Append(inner,Wait(label));
        inner.push_back(padding[0]);inner.push_back(padding[1]);
        const auto address=reinterpret_cast<uintptr_t>(inner.data());
        PM4CmdIndirectBuffer ib{.header{PM4ItOpcode::IndirectBuffer,2},
            .ibase_lo=u32(address),.dw1=0,.dw2=0};
        ib.ibase_hi.Assign(u32(address>>32));ib.ib_size.Assign(inner.size());
        cp.Feed(Encode(ib));
        assert(label==1&&cp.irq==1&&cp.waits==1&&cp.indirects==1&&cp.packets==3);
        assert(cp.queue.tmp_dwords==0&&cp.read_pointer==6);
        ++cases;
    }
    std::cout<<"SOTC_ASC_DOUBLE_PADDING_IB cases="<<cases<<" submit/IB/rptr=PASS\n";
}
void TestFragmentedType3() {
    u64 cases=0;
    for(bool indirect:{false,true})for(u32 cut=1;cut<7;++cut) {
        alignas(8) u64 label=0;Probe cp;cp.read_pointer=4094;
        const std::array<u32,1> padding{0x92340000u};
        const auto release=Release(label),wait=Wait(label);
        auto feed=[&](std::span<const u32> data) {
            if(indirect)cp.Feed<true>(data);else cp.Feed(data);
        };
        feed(padding);feed(std::span(release).first(cut));
        assert(label==0&&cp.irq==0&&cp.queue.tmp_dwords==cut);
        std::vector<u32> rest;Append(rest,std::span(release).subspan(cut));
        Append(rest,padding);Append(rest,std::span(wait).first(cut));feed(rest);
        assert(label==1&&cp.irq==1&&cp.waits==0&&cp.queue.tmp_dwords==cut);
        rest.clear();Append(rest,std::span(wait).subspan(cut));Append(rest,padding);feed(rest);
        assert(cp.irq==1&&cp.waits==1&&cp.packets==2&&cp.queue.tmp_dwords==0);
        assert(cp.read_pointer==(indirect?4094u:(4094u+17u)%4096u));++cases;
    }
    for(u32 words:{2u,7u,64u,1024u})for(u32 cut=1;cut<words;++cut) {
        Probe cp;std::vector<u32> packet(words,0);
        WriteHeader<PM4ItOpcode::Nop>(packet.data(),words-1);
        cp.Feed(std::span(packet).first(cut));
        assert(cp.queue.tmp_dwords==cut&&cp.nops==0);
        cp.Feed(std::span(packet).subspan(cut));
        assert(cp.queue.tmp_dwords==0&&cp.nops==1&&cp.read_pointer==words);++cases;
    }
    std::cout<<"SOTC_ASC_TYPE3_FRAGMENT cases="<<cases<<" ownership/length/read-pointer=PASS\n";
}
void TestObservedPredicates() {
    struct Case {u32 raw,mask,reference,expected_functions;};
    // Truth tables encode the expected result independently of the method:
    // bits 0..6 select Always, LT, LE, EQ, NE, GE and GT respectively.
    const std::array<Case,12> cases{{
        {0x800100a5u,0xffu,0xa6u,0x17u},
        {0x800100a5u,0xffu,0xa5u,0x2du},
        {0x800100a5u,0xffu,0xa4u,0x71u},
        {0xffffffffu,0u,0u,0x2du},
        {0xffffffffu,0u,1u,0x17u},
        {0xffffffffu,0x00ffffffu,0xffffffffu,0x17u},
        {0x80000000u,~u32{},0x7fffffffu,0x71u},
        {0x80000000u,~u32{},0x80000000u,0x2du},
        {0x80000000u,~u32{},0xffffffffu,0x17u},
        {0xffffffffu,~u32{},0xffffffffu,0x2du},
        {0u,~u32{},1u,0x17u},
        {0u,~u32{},0u,0x2du},
    }};
    u32 waits=0;
    for(const auto& sample:cases)for(bool memory:{false,true})for(u32 function=0;function<7;++function) {
        alignas(8) u64 label=sample.raw;
        const auto encoded=Wait(label,sample.reference);
        auto packet=std::bit_cast<PM4CmdWaitRegMem>(encoded);
        packet.mask=sample.mask;
        packet.function.Assign(static_cast<PM4CmdWaitRegMem::Function>(function));
        std::array<u32,16> registers{};
        if(!memory) {
            packet.mem_space.Assign(PM4CmdWaitRegMem::MemSpace::Register);
            packet.reg.Assign(9);registers[9]=sample.raw;
        }
        u32 observed=0xdeadbeefu;
        const bool expected=(sample.expected_functions&(1u<<function))!=0;
        assert(packet.Test(registers)==expected);
        assert(packet.Test(registers,&observed)==expected);
        assert(observed==sample.raw&&label==sample.raw);
        if(!memory)assert(registers[9]==sample.raw);
        ++waits;
    }
    const std::array<std::pair<u32,bool>,8> rewind_cases{{
        {0u,false},{1u,false},{0x00ffffffu,false},{0x7fffffffu,false},
        {0x80000000u,true},{0x80000001u,true},{0x81000000u,true},{0xffffffffu,true}
    }};
    for(const auto& [raw,expected]:rewind_cases) {
        PM4CmdRewind packet{.header{PM4ItOpcode::Rewind,0},.raw=raw};
        u32 observed=0xdeadbeefu;
        assert(packet.Valid()==expected&&packet.Valid(&observed)==expected);
        assert(observed==u32(expected)&&packet.raw==raw);
    }
    const std::array<std::pair<u64,bool>,7> semaphore_cases{{
        {0,false},{1,true},{2,true},{0xffffffffULL,true},
        {0x100000000ULL,true},{0x8000000000000000ULL,true},{~u64{},true}
    }};
    for(const auto& [value,expected]:semaphore_cases) {
        SemaphoreProbe packet{value};u64 observed=0xdeadbeefULL;
        assert(packet.Signaled()==expected&&packet.Signaled(&observed)==expected);
        assert(observed==value&&packet.value==value);
    }
    std::cout<<"SOTC_PM4_OBSERVED_PREDICATES waits="<<waits
             <<" rewind="<<rewind_cases.size()<<" semaphore="<<semaphore_cases.size()
             <<" default/capture/mask/unsigned=PASS\n";
}
}
int main() {
    AmdGpu::TestAllPaddingCountBits();
    AmdGpu::TestDoublePaddingAndIb();
    AmdGpu::TestFragmentedType3();
    AmdGpu::TestObservedPredicates();
}
'''
replacements = {"WIRE": wire, "NEXT": next_packet, "QUEUE": queue,
                "PREFIX": prefix, "RPTR": rptr, "SEMAPHORE_SIGNALED": semaphore_signaled}
program = PROGRAM
for key, value in replacements.items():
    program = program.replace("@" + key + "@", value)

variants = [("actual", program, True)]
mutations = {
    "old_type3_size_for_padding": (
        "header->type == 2 ? 1 : header->type3.NumWords() + 1",
        "header->type3.NumWords() + 1"),
    "lost_type2_read_pointer": (
        "                AdvanceReadPointer(queue.read_addr, next_dw_off, queue.ring_size_dw);",
        "                /* lost Type-2 read-pointer update */"),
    "lost_fragment_copy": (
        "            std::memcpy(queue.tmp_packet.data() + queue.tmp_dwords, acb.data(),\n"
        "                        next_dw_off * sizeof(u32));",
        "            /* lost continuation payload */"),
    "indirect_pointer_pollution": (
        "            if constexpr (!is_indirect) {\n"
        "                AdvanceReadPointer(queue.read_addr, next_dw_off, queue.ring_size_dw);",
        "            if constexpr (true) {\n"
        "                AdvanceReadPointer(queue.read_addr, next_dw_off, queue.ring_size_dw);"),
}
for label, (old, new) in mutations.items():
    assert prefix.count(old) == 1, (label, prefix.count(old))
    variants.append((label, program.replace(prefix, prefix.replace(old, new, 1), 1), False))
for label, old, new in (
    ("lost_wait_mask", "return (value & mask) == ref;", "return value == ref;"),
    ("masked_wait_observation", "if (observed) *observed = value;\n        switch (function.Value())",
     "if (observed) *observed = value & mask;\n        switch (function.Value())"),
):
    assert program.count(old) == 1, (label, program.count(old))
    variants.append((label, program.replace(old, new, 1), False))

with tempfile.TemporaryDirectory(prefix="sotc-stall-progress-") as directory:
    directory = Path(directory)
    for label, source, positive in variants:
        path, executable = directory / (label + ".cpp"), directory / label
        path.write_text(source)
        subprocess.run(["c++", "-std=c++23", "-O1", "-Wall", "-Wextra", "-Werror",
                        "-fsanitize=undefined", "-fno-sanitize-recover=all", "-I", str(src),
                        str(path), "-o", str(executable)], check=True)
        result = subprocess.run([str(executable)], capture_output=True, text=True, timeout=20)
        if positive:
            assert result.returncode == 0, result.stdout + result.stderr
            print(result.stdout, end="")
        else:
            assert result.returncode != 0, "Negative control accepted: " + label
            assert any(x in result.stderr for x in ("Assertion", "runtime_error", "runtime error:")), result.stderr
            print("SOTC_STALL_PROGRESS_NEGATIVE_PASS", label)

subprocess.run([sys.executable, str(Path(__file__).with_name("test_sotc_cp_wait_graph.py")),
                "--source", str(args.source.resolve())], check=True)
print("SOTC_STALL_PROGRESS_PASS ASC framing, real predicates and CP/VO progress", flush=True)
