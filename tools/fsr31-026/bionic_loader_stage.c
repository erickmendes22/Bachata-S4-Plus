// SPDX-License-Identifier: GPL-2.0-or-later
// Android/Bionic launch stage for an existing core025 FSR module.
// Keep pre-existing LD_PRELOAD entries (native hooks and other launch fixes).
// Never preload an Android/Bionic library into the Linux/glibc guest process.
#include <stdlib.h>
#include <string.h>
#include <ctype.h>

static const char stage_name[]="libbachata_fsr31_stage.so";
static const char target_name[]="$ORIGIN/libbachata_fsr31.so";

static int matches_name(const char* start,size_t len,const char* suffix) {
    const size_t slen=strlen(suffix);
    return len>=slen && !memcmp(start+len-slen,suffix,slen) &&
        (len==slen || start[len-slen-1]=='/');
}
static int configured(void) {
    const char* mode=getenv("BACHATA_FSR31_MODE");
    return mode && mode[0]>='0' && mode[0]<='4' && mode[1]==0;
}
// Intentionally exported for a test harness; constructor uses the same path.
__attribute__((visibility("default"))) int bs4_fsr31_bionic_loader_stage(void) {
    if(!configured())return 0;
    const char* original=getenv("LD_PRELOAD");
    if(!original)return 0;
    size_t retained=0;
    int found_stage=0,found_target=0;
    for(const char* p=original;*p;) {
        while(*p && isspace((unsigned char)*p))++p;
        const char* start=p;
        while(*p && !isspace((unsigned char)*p))++p;
        const size_t len=(size_t)(p-start);
        if(!len)continue;
        if(matches_name(start,len,stage_name)) {found_stage=1;continue;}
        if(len==strlen(target_name)&&!memcmp(start,target_name,len)) {
            found_target=1;
        }
        retained+=len+1;
    }
    if(!found_stage)return 0;
    const size_t target_size=found_target?0:sizeof(target_name);
    if(retained > (size_t)-1 - target_size - 1)return 0;
    char* rewritten=(char*)malloc(retained+target_size+1);
    if(!rewritten)return 0;
    size_t used=0;
    for(const char* p=original;*p;) {
        while(*p&&isspace((unsigned char)*p))++p;
        const char* start=p;
        while(*p&&!isspace((unsigned char)*p))++p;
        const size_t len=(size_t)(p-start);
        if(!len||matches_name(start,len,stage_name))continue;
        if(used)rewritten[used++]=' ';
        memcpy(rewritten+used,start,len);used+=len;
    }
    if(!found_target) {
        if(used)rewritten[used++]=' ';
        memcpy(rewritten+used,target_name,sizeof(target_name)-1);
        used+=sizeof(target_name)-1;
    }
    rewritten[used]=0;
    const int success=setenv("LD_PRELOAD",rewritten,1)==0;
    free(rewritten);
    return success;
}
__attribute__((constructor)) static void forward(void) {
    (void)bs4_fsr31_bionic_loader_stage();
}
