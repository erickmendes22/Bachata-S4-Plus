#include "video_core/sotc_load_flush.h"
#include <cassert>
#include <iostream>
int main(){
 using namespace BachataSotcLoad;
 assert(!Notify("CUSA00785","st_gameflow() starting game"));
 assert(!Notify("CUSA08809","unrelated log"));
 assert(Notify("CUSA08809","[game] st_gameflow() starting game"));
 assert(pending.exchange(false));assert(!pending.load());
 assert(Notify("CUSA08034","st_gameflow() starting game"));assert(pending.exchange(false));
 struct Image{struct{bool is_bound{},is_target{},needs_rebind{};}binding;struct{bool storage{},render_target{},depth_target{},vo_surface{};}usage;};
 for(unsigned i=0;i<10;++i){Image a{};bool gpu=i==1,registered=i!=2;
 switch(i){case 3:a.binding.is_bound=true;break;case 4:a.binding.is_target=true;break;case 5:a.binding.needs_rebind=true;break;case 6:a.usage.storage=true;break;case 7:a.usage.render_target=true;break;case 8:a.usage.depth_target=true;break;case 9:a.usage.vo_surface=true;break;}
 assert(SafeToDrop(a,gpu,registered)==(i==0));}
 std::cout<<"SOTC_LOAD_FLUSH_POLICY_PASS\n";
}
