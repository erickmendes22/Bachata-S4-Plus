// SPDX-License-Identifier: GPL-2.0-or-later
#include <assert.h>
#include <stdio.h>
#include <string.h>
extern int bs4_r16_insert_preload(char **);
static void check(const char* executable,int modified) {
    char* argv[500]={"ld-linux-aarch64.so.1","--library-path","host",
        (char*)executable,"--log-level","Info",0};
    int yes=bs4_r16_insert_preload(argv);
    assert(yes==modified);
    if(modified) {
        assert(!strcmp(argv[3],"--preload"));
        assert(!strcmp(argv[4],"libbachata_fsr31.so"));
        assert(!strcmp(argv[5],executable));
        assert(!strcmp(argv[6],"--log-level"));
        assert(!strcmp(argv[7],"Info"));
        assert(argv[8]==0);
    } else {
        assert(argv[3]==executable);
        assert(argv[6]==0);
    }
}
int main(void){
    check("shadps4-arm64-025",1);
    check("host/shadps4-arm64-025",1);
    check("host/shadps4-arm64-024",0);
    check("host/shadps4-arm64-023",0);
    check("host/shadps4-arm64-020",0);
    check("host/shadps4-arm64-fex",0);
    puts("PASS: GLIBC FSR preload restricted to core 025; argv & legacy cores preserved");
}
