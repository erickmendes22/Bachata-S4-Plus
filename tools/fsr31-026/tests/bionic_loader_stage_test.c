#include <assert.h>
#include <stdlib.h>
#include <string.h>
int bs4_fsr31_bionic_loader_stage(void);
static void check(const char* input,const char* expected,int applied){
    assert(setenv("LD_PRELOAD",input,1)==0);
    assert(bs4_fsr31_bionic_loader_stage()==applied);
    assert(strcmp(getenv("LD_PRELOAD"),expected)==0);
}
int main(void){
    assert(setenv("BACHATA_FSR31_MODE","4",1)==0);
    check("/data/app/libbachata_fsr31_stage.so","$ORIGIN/libbachata_fsr31.so",1);
    check("libcompat.so /data/app/libbachata_fsr31_stage.so libgraphics.so",
          "libcompat.so libgraphics.so $ORIGIN/libbachata_fsr31.so",1);
    check("libcompat.so $ORIGIN/libbachata_fsr31.so /data/libbachata_fsr31_stage.so",
          "libcompat.so $ORIGIN/libbachata_fsr31.so",1);
    check("libcompat.so", "libcompat.so",0);
    assert(setenv("BACHATA_FSR31_MODE","-1",1)==0);
    check("libcompat.so /data/app/libbachata_fsr31_stage.so",
          "libcompat.so /data/app/libbachata_fsr31_stage.so",0);
    return 0;
}
