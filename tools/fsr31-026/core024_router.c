// SPDX-License-Identifier: GPL-2.0-or-later
// Optional 0.2.6 FSR 3.1 routing, preserving the exact working core024 ELF.
// Only mode 0..4 chooses the new reconstructed source renderer; FSR=off
// execs the original unchanged 024. No /bin/sh or runtime symlinks needed.
#define _GNU_SOURCE
#include <errno.h>
#include <limits.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
extern char **environ;
int main(int argc,char** argv) {
    char self[PATH_MAX], executable[PATH_MAX];
    ssize_t n=readlink("/proc/self/exe",self,sizeof(self)-1);
    if(n<1 || (size_t)n>=sizeof(self)-1) {
        fputs("[BS4_FSR31] cannot locate core024 router\n",stderr);
        return 126;
    }
    self[n]=0;
    char* slash=strrchr(self,'/');
    if(!slash)return 126;
    slash[1]=0;
    const char* mode=getenv("BACHATA_FSR31_MODE");
    const int enabled=mode && mode[0]>='0' && mode[0]<='4' && !mode[1];
    const char* name=enabled?"shadps4-arm64-fsr31":"shadps4-arm64-024-stable";
    const int total=snprintf(executable,sizeof(executable),"%s%s",self,name);
    if(total<0 || total>=(int)sizeof(executable))return 126;
    if(access(executable,X_OK)!=0) {
        fprintf(stderr,"[BS4_FSR31] target unavailable: %s errno=%d\n",name,errno);
        return 126;
    }
    char** forwarded=calloc((size_t)argc+1,sizeof(char*));
    if(!forwarded)return 126;
    forwarded[0]=executable;
    for(int i=1;i<argc;++i)forwarded[i]=argv[i];
    execve(executable,forwarded,environ);
    fprintf(stderr,"[BS4_FSR31] exec failed: %s errno=%d\n",name,errno);
    return 126;
}
