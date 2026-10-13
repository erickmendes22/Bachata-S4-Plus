// SPDX-License-Identifier: GPL-2.0-or-later
// Bionic-stage LD_PRELOAD trampoline: the BACHATA Android host-loader cannot
// load the glibc FSR3 library, and Android's linker does not expand $ORIGIN.
// The Android launcher points LD_PRELOAD at this tiny Bionic .so via an
// absolute path. Its constructor replaces the value with the correct glibc
// module name before the real ELF loader launches shadps4-arm64-024.
extern char **environ;
extern int setenv(const char*, const char*, int);
static int prefix(const char* a,const char* b) {
    while(*b) if(*a++!=*b++)return 0;
    return 1;
}
static unsigned long length(const char* s) {
    unsigned long i=0;while(s[i])i++;return i;
}
__attribute__((constructor)) static void forward(void) {
    static const char name[]="LD_PRELOAD=";
    static const char value[]="$ORIGIN/libbachata_fsr31.so";
    for(char** entry=environ;entry && *entry;entry++) {
        char* pair=*entry;
        if(!prefix(pair,name))continue;
        char* current=pair+sizeof(name)-1;
        if(length(current)>=sizeof(value)-1)
            for(unsigned long i=0;i<sizeof(value);i++)current[i]=value[i];
        break;
    }
    setenv("LD_PRELOAD",value,1);
}
__attribute__((visibility("default"))) int bs4_fsr31_bionic_loader_stage(void) {
    return 1;
}
