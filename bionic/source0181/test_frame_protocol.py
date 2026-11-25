#!/usr/bin/env python3
"""Run the actual native frame sender through a socket into the frontend protocol.

The v0.2.7 EmulationService compares the complete line exactly with
'BACHATA/1 EVENT Frame', then calls ManagedSession.recordPresentedFrame.
This test exercises the actual RuntimeClient, including serialization with
other events and a disconnected Android reader; no Vulkan or device mock FPS.
"""
import argparse
from pathlib import Path
import subprocess
import tempfile

p = argparse.ArgumentParser()
p.add_argument("--source", required=True, type=Path)
a = p.parse_args()
source = a.source.resolve() / "src"
code = r'''
#include "platform/bachata/runtime_client.h"
#include <cassert>
#include <string>
#include <thread>
#include <iostream>
#include <sys/socket.h>
#include <unistd.h>

int main() {
    using namespace Platform::Bachata;
    int pair[2];
    assert(socketpair(AF_UNIX,SOCK_STREAM,0,pair)==0);
    RuntimeClient sender(pair[0]);
    SetActiveRuntimeClient(&sender);
    unsigned frames=0;
    std::thread reader([&]{
        std::string line;
        char c;
        unsigned events=0;
        while (::recv(pair[1],&c,1,0)==1) {
            if (c!='\n') {line+=c;continue;}
            if (line=="BACHATA/1 EVENT Frame") ++frames;
            else if (line=="BACHATA/1 EVENT Running") ++events;
            else {assert(line=="BACHATA/1 EVENT Stopped exit_code=0");break;}
            line.clear();
        }
        assert(events==1);
    });
    assert(sender.SendRunning());
    for (unsigned i=0;i<120;++i) ReportPresentedFrame();
    assert(sender.SendStopped(0));
    reader.join();
    assert(frames==120);
    SetActiveRuntimeClient(nullptr);
    // A lost frontend must fail a send without delivering SIGPIPE.
    ::close(pair[1]);
    assert(!sender.SendFramePresented());
    ReportPresentedFrame();
    std::cout << "BACHATA_ORIGINAL_FPS_SOCKET_PROTOCOL_PASS frames=" << frames << '\n';
}
'''
with tempfile.TemporaryDirectory() as d:
    d = Path(d)
    (d / "frames.cpp").write_text(code)
    platform = source / "platform/bachata"
    subprocess.run(["c++", "-std=c++20", "-O2", "-pthread", "-I", str(source),
                    str(d / "frames.cpp"), str(platform / "runtime_client.cpp"),
                    str(platform / "controller_snapshot.cpp"), "-o", str(d / "frames")], check=True)
    subprocess.run([str(d / "frames")], check=True, timeout=10)
