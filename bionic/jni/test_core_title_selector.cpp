#include "core_title_selector.h"
#include <cassert>
int main(){
    using namespace BachataDispatch;
    assert(SotcArgs({"shadps4-arm64-fex","--override-root","/storage/CUSA08809","-g","eboot.bin"}));
    assert(SotcArgs({"--override-root","/saf/CUSA08034/"}));
    assert(!SotcArgs({"--override-root","/CUSA00785","-g","CUSA08809"}));
    assert(!SotcArgs({"--override-root","/CUSA08809-other"}));
    assert(!SotcArgs({"--override-root"}));
    assert(!SotcArgs({"--other","CUSA08809"}));
}
