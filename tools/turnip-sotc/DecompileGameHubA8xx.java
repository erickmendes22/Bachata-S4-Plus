// @category GameHub
import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.listing.Function;
import ghidra.program.model.address.Address;
import java.nio.file.*;
import java.nio.charset.StandardCharsets;
public class DecompileGameHubA8xx extends GhidraScript {
  @Override public void run() throws Exception {
    long[] addresses = {0x96539cL,0xb57820L,0xca15b4L,0xca1320L};
    String[] names = {"use_sysmem_rendering","util_format_is_pure_integer",
                      "vk_format_aspects","vk_format_to_pipe_format"};
    DecompInterface d = new DecompInterface();
    d.toggleCCode(true);
    d.setSimplificationStyle("decompile");
    if (!d.openProgram(currentProgram)) throw new RuntimeException("Open program failed");
    StringBuilder out = new StringBuilder();
    out.append("// GameHub 26.10.22 ARM64 decompilation, Ghidra 12.2\n");
    out.append("// All source types/offsets must be verified against assembly.\n\n");
    for(int i=0;i<addresses.length;i++){
      Address a=toAddr(addresses[i]); Function f=getFunctionAt(a);
      out.append("/* ").append(names[i]).append(" at ").append(a).append(" */\n");
      if(f==null){out.append("// Missing from autoanalysis\n");continue;}
      DecompileResults r=d.decompileFunction(f,180,monitor);
      if(r!=null&&r.decompileCompleted()&&r.getDecompiledFunction()!=null)
         out.append(r.getDecompiledFunction().getC()).append("\n");
      else out.append("// Failed: ").append(r!=null?r.getErrorMessage():"null").append("\n");
    }
    String target=System.getenv("GHIDRA_DECOMPILE_OUT");
    if(target==null||target.isEmpty()) target="/tmp/gamehub_a8xx_decompiled.c";
    Files.writeString(Path.of(target),out.toString(),StandardCharsets.UTF_8);
    println("Wrote "+target+" bytes="+out.length());
    d.dispose();
  }
}
