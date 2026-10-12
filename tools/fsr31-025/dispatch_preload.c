// SPDX-License-Identifier: GPL-2.0-or-later
// Extend the original R15 GLIBC dispatcher argv only for core 025.
// Inactive unless caller chooses core 025; never switches the selected core.
static const char kPreload[] = "--preload";
static const char kLibrary[] = "libbachata_fsr31.so";
static const char kCore[] = "shadps4-arm64-025";
static int equals(const char* a,const char* b) {
    if(!a || !b)return 0;
    for(;*a && *b;a++,b++)if(*a!=*b)return 0;
    return !*a && !*b;
}
__attribute__((visibility("hidden"))) int bs4_r16_insert_preload(char** argv) {
    if(!argv || !argv[3])return 0;
    const char* base=argv[3];
    for(const char* p=base;*p;p++)if(*p=='/')base=p+1;
    if(!equals(base,kCore))return 0;
    unsigned n=0;
    while(n<496 && argv[n])n++;
    if(n>=496)return 0;
    // Includes NULL terminator. Two new loader-only arguments go BEFORE
    // the actual core executable; this keeps all game arguments unmodified.
    for(unsigned j=n+1;j>3;j--)argv[j+1]=argv[j-1];
    argv[3]=(char*)kPreload;
    argv[4]=(char*)kLibrary;
    return 1;
}
