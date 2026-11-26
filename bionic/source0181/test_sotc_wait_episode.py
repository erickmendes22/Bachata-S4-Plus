#!/usr/bin/env python3
"""Run actual CP/predicate methods with callbacks and coroutine-owned wait age.

The monotonic clock has a deterministic forward offset. GPU/VO boundaries are
the existing CP graph mocks; actual predicates, Process, ProcessCommands,
NoteCommandWait, reset, backoff and coroutine scopes come from --source.
"""
import argparse
import pathlib
import subprocess
import tempfile

from test_sotc_cp_wait_graph import block, build_fixture


CASES = r'''
struct WaitRecord {
    std::string reason;
    u32 qid;
    VAddr address;
    u64 reference,mask,observed;
    u32 function;
    u64 elapsed_ms;
};
std::vector<WaitRecord> records;

void CoroutineAndCallbackEpisodes() {
    Liverpool cp;
    VideoOutPort port;
    cp.vo_port=&port;
    PM4CmdWaitRegMem packet;
    packet.address=reinterpret_cast<u32*>(&port.buffer_labels[0]);
    std::atomic<unsigned> callbacks{0};
    std::jthread worker([&](std::stop_token stop){cp.Process(stop);});
    const auto initial_reports=warning_count.load();
    for(unsigned phase=0;phase<3;++phase) {
        const bool long_episode=phase!=1;
        const unsigned end_poll=long_episode?35:3;
        const unsigned reports_before=warning_count.load();
        const unsigned reads_before=diagnostic_clock_reads.load();
        const unsigned callbacks_before=callbacks.load();
        packet.calls=0;
        port.buffer_labels[0]=1;
        packet.on_poll=[&] {
            if(packet.calls>end_poll)return;
            const bool finish=packet.calls==end_poll;
            std::scoped_lock lock{cp.submit_mutex};
            cp.command_queue.emplace([&,finish]{
                ++callbacks;
                // Each unrelated callback marks cp_progress in the real
                // dispatcher. It does not satisfy the predicate until finish.
                if(long_episode)diagnostic_clock_offset_ns.fetch_add(200'000'000ULL);
                if(finish)port.buffer_labels[0]=0;
            });
            ++cp.num_commands;
        };
        auto task=cp.WaitTask(&packet);
        {
            std::scoped_lock lock{cp.submit_mutex,cp.mapped_queues[0].m_access};
            cp.mapped_queues[0].submits.push(task.handle);
            ++cp.num_submits;
            cp.submit_cv.notify_one();
        }
        Until([&]{return cp.num_submits==0;});
        assert(port.buffer_labels[0]==0);
        assert(callbacks-callbacks_before==end_poll);
        assert(packet.calls==end_poll+1);
        assert(warning_count==reports_before+(long_episode?1:0));
        // Entry + the 32nd false reentry; no clock reads in other polls or
        // after reporting. The passing predicate never enters the observer.
        assert(diagnostic_clock_reads-reads_before==(long_episode?2:1));
        assert(cp.submit_cv.timed_waits==0);
    }
    Stop(cp,worker);
    assert(warning_count==initial_reports+2);
    diagnostic_clock_offset_ns=0;
    std::cout<<"CALLBACK_EPISODES_PASS callbacks="<<callbacks
             <<" same-key long/short/long, real coroutine completion, no backoff report\n";
}

struct WaitKey {
    const char* reason="wait_reg_mem_memory";
    VAddr address=0x1234;
    u64 reference=9,mask=0xff;
    u32 function=3,qid=0;
};
void Observe(Liverpool& cp,Liverpool::CommandWaitEpisode& episode,
             bool& first,const WaitKey& key,u64 observed=1) {
    cp.NoteCommandWait(key.reason,key.address,key.reference,key.mask,observed,
                       key.function,first,key.qid,episode);
}
void Poll32(Liverpool& cp,Liverpool::CommandWaitEpisode& episode,
            bool& first,const WaitKey& key,u64 observed=1) {
    for(unsigned i=0;i<32;++i)Observe(cp,episode,first,key,observed);
}
void IdentityAndObservation() {
    Liverpool cp;
    const WaitKey original;
    for(unsigned field=0;field<6;++field) {
        Liverpool::CommandWaitEpisode episode{};
        bool first=true;
        Observe(cp,episode,first,original);
        assert(cp.cp_progress && !first);
        cp.cp_progress=false;
        diagnostic_clock_offset_ns.fetch_add(2'001'000'000ULL);
        auto changed=original;
        switch(field) {
        case 0:changed.reason="wait_reg_mem_register";break;
        case 1:changed.address+=4;break;
        case 2:++changed.reference;break;
        case 3:changed.mask=0xffff;break;
        case 4:changed.function=4;break;
        case 5:changed.qid=1;break;
        }
        const auto reports=warning_count.load();
        Observe(cp,episode,first,changed);
        Poll32(cp,episode,first,changed);
        assert(warning_count==reports && !cp.cp_progress);
        diagnostic_clock_offset_ns.fetch_add(2'001'000'000ULL);
        Poll32(cp,episode,first,changed);
        assert(warning_count==reports+1);
        const auto& record=records.back();
        assert(record.reason==changed.reason && record.qid==changed.qid);
        assert(record.address==changed.address && record.reference==changed.reference);
        assert(record.mask==changed.mask && record.function==changed.function);
    }
    Liverpool::CommandWaitEpisode episode{};
    bool first=true;
    Observe(cp,episode,first,original);
    const auto reports=warning_count.load();
    diagnostic_clock_offset_ns.fetch_add(2'001'000'000ULL);
    for(u64 value=2;value<34;++value) {
        cp.ResetCommandWaitProgress();
        Observe(cp,episode,first,original,value);
    }
    assert(warning_count==reports+1 && records.back().observed==33);
    assert(records.back().elapsed_ms>=2001);
    const auto clock_reads=diagnostic_clock_reads.load();
    Poll32(cp,episode,first,original,44);
    assert(warning_count==reports+1 && diagnostic_clock_reads==clock_reads);
    diagnostic_clock_offset_ns=0;
    std::cout<<"WAIT_IDENTITY_PASS all6fields, observed-only changes, exactly-once, sampled clock\n";
}

void IndependentQueuesAndOptOut() {
    Liverpool cp;
    Liverpool::CommandWaitEpisode a{},b{};
    WaitKey ka,kb;kb.qid=1;
    bool first_a=true,first_b=true;
    Observe(cp,a,first_a,ka);Observe(cp,b,first_b,kb);
    const auto reports=warning_count.load();
    diagnostic_clock_offset_ns.fetch_add(2'001'000'000ULL);
    for(unsigned i=0;i<32;++i) {
        cp.ResetCommandWaitProgress();Observe(cp,a,first_a,ka);
        cp.ResetCommandWaitProgress();Observe(cp,b,first_b,kb);
    }
    assert(warning_count==reports+2);
    assert(records[records.size()-2].qid==0 && records.back().qid==1);
    for(const char* serial:{"CUSA00785","OTHER"}) {
        Common::ElfInfo::Instance().serial=serial;
        Liverpool::CommandWaitEpisode off{};bool first=true;
        const auto clocks=diagnostic_clock_reads.load(),warnings=warning_count.load();
        Observe(cp,off,first,ka);Poll32(cp,off,first,ka);
        assert(!off.state.active && first);
        assert(diagnostic_clock_reads==clocks && warning_count==warnings);
    }
    diagnostic_clock_offset_ns=0;
    std::cout<<"WAIT_QUEUE_SCOPE_PASS independent episodes, other titles do not sample\n";
}

int main() {
    for(const char* serial:{"CUSA08809","CUSA08034"}) {
        Common::ElfInfo::Instance().serial=serial;
        CoroutineAndCallbackEpisodes();IdentityAndObservation();IndependentQueuesAndOptOut();
    }
}
'''


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", type=pathlib.Path, required=True)
    args = parser.parse_args()
    cp = (args.source / "src/video_core/amdgpu/liverpool.cpp").read_text()
    assert "BACHATA_SOTC_WAIT_EPISODE" in cp, "Apply the local wait episode overlay first"
    assert cp.count("CommandWaitEpisode wait_episode{};") == 8
    src, _ = build_fixture(args.source)
    # Only the predicate-call arrival hook and clock are boundary mocks. The
    # case still invokes the actual Test and actual coroutine-owned episode.
    src = src.replace("mutable unsigned calls=0;",
                      "std::function<void()> on_poll;\n    mutable unsigned calls=0;")
    src = src.replace("        ++calls;\n", "        ++calls;\n        if(on_poll)on_poll();\n", 1)
    src = src.replace(block(src, "int main()"), CASES)
    capture = block(src, "void CaptureWarning(")
    new_capture = r'''void CaptureWarning(const char*,const char* reason,u32 qid,VAddr address,
        u64 reference,u64 mask,u64 observed,u32 function,u32,u32,u64,u64,u64,u64 elapsed_ms) {
    records.push_back({reason,qid,address,reference,mask,observed,function,elapsed_ms});
    warning_qid=qid;
    ++warning_count;
}'''
    record_def = CASES[:CASES.index("void CoroutineAndCallbackEpisodes()")]
    src = src.replace(record_def, "", 1)
    src = src.replace(capture, record_def + new_capture, 1)
    controls = {
        "callbacks_restart_wait_age": (
            "const bool same = old.active &&", "const bool same = old.active && !cp_progress &&"),
        "identity_fields_ignored": (
            "old.qid == qid && old.address == address &&\n"
            "                      old.reference == reference && old.mask == mask && old.function == function",
            "true"),
        "observation_restarts_age": (
            "const bool same = old.active &&", "const bool same = old.active && old.observed == observed &&"),
        "static_episode_reused_after_completion": (
            "CommandWaitEpisode wait_episode{};", "static CommandWaitEpisode wait_episode{};"),
        "clock_sampled_every_poll": (
            "if (episode.reported || (++episode.polls & 31u) != 0) return;",
            "if (episode.reported) return;"),
        "repeated_report_for_same_episode": (
            "if (episode.reported || (++episode.polls & 31u) != 0) return;",
            "if ((++episode.polls & 31u) != 0) return;"),
    }
    with tempfile.TemporaryDirectory(prefix="sotc-wait-episode-") as temporary:
        output = pathlib.Path(temporary)
        def run(name, code, negative=False):
            path = output / (name + ".cpp")
            path.write_text(code)
            binary = path.with_suffix("")
            subprocess.run(["g++", "-std=c++20", "-O1", "-g", "-pthread", "-fsanitize=undefined",
                            "-fno-sanitize-recover=all", str(path), "-o", str(binary)], check=True)
            try:
                result = subprocess.run([str(binary)], text=True, capture_output=True, timeout=12)
                failed = result.returncode != 0
            except subprocess.TimeoutExpired:
                if not negative:
                    raise
                failed = True
            if negative:
                assert failed, f"Negative control survived: {name}"
                print("NEGATIVE_REJECTED", name)
            else:
                assert not failed, result.stdout + result.stderr
                print(result.stdout, end="")
        run("effective", src)
        for name, (before, after) in controls.items():
            assert src.count(before) == 1, (name, src.count(before))
            run(name, src.replace(before, after, 1), True)
    print("SOTC_WAIT_EPISODE_PASS actual CP/predicate/coroutine methods and 6 negatives")


if __name__ == "__main__":
    main()
