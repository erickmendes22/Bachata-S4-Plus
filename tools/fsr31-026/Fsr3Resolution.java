package com.bachatas4.android.bridge;
import android.content.Context;
import android.content.SharedPreferences;
import android.util.Log;
import java.io.File;
import java.io.InputStream;
import java.io.ByteArrayOutputStream;
import org.json.JSONObject;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.StandardCopyOption;
import java.util.Collections;
import java.util.HashSet;
import java.util.Set;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

/** Bloodborne 01.09 game-native scene resolution with 1080p UI.
 *  Patch XML edits occur before launching the game, not during rendering.
 *  Existing non-FSR resolution selections are restored when disabling FSR3.
 */
public final class Fsr3Resolution {
  /** Read the runtime identity shipped with the APK. Do not hardcode the
   *  extraction suffix: the R13->R14 rename caused the 640x360 patch to vanish. */
  private static String activeRuntime(Context ctx) throws Exception {
    try (InputStream in=ctx.getAssets().open("runtime/manifest.json");
         ByteArrayOutputStream buffer=new ByteArrayOutputStream()) {
      byte[] chunk=new byte[8192];
      int n;
      while((n=in.read(chunk))!=-1) buffer.write(chunk,0,n);
      String version=new JSONObject(
          new String(buffer.toByteArray(),StandardCharsets.UTF_8))
          .getString("runtimeVersion");
      if(!version.matches("bachata-s4-plus-0\\.2\\.6-[a-zA-Z0-9]+"))
          throw new IllegalStateException("Invalid active runtime name");
      return version;
    }
  }
  private static final String SAVED = "fsr31_bb_original_resolution";
  private static final String CONTROLLED = "fsr31_bb_controls_resolution";
  private static final String PREFIX = "Decoupled 1080p UI (";
  private static final String[] SIZES = {null,"1280x720","1152x648","960x540","640x360"};
  private static final Pattern META = Pattern.compile("<Metadata\\b[^>]*>",Pattern.DOTALL);
  private static final Pattern NAME = Pattern.compile("\\bName=\"([^\"]+)\"");
  private static final Pattern ENABLED = Pattern.compile("\\bisEnabled=\"(?:true|false)\"");
  private static String name(String tag) {
    Matcher m = NAME.matcher(tag);
    return m.find() ? m.group(1) : "";
  }
  private static boolean isEnabled(String tag) {
    return tag.contains("isEnabled=\"true\"");
  }
  private static String toggle(String tag,boolean yes) {
    Matcher m = ENABLED.matcher(tag);
    if (m.find()) return m.replaceFirst("isEnabled=\"" + yes + "\"");
    return tag.substring(0,tag.length()-1) + " isEnabled=\"" + yes + "\">";
  }
  public static synchronized void apply(Context ctx,boolean enabled,int preset) {
    if(ctx==null||preset<0||preset>4)return;
    SharedPreferences preferences=ctx.getSharedPreferences("bs4_fsr31",Context.MODE_PRIVATE);
    try {
      final String currentRuntime=activeRuntime(ctx);
      final File xml=new File(ctx.getFilesDir(),"runtime/"+currentRuntime+
          "/user/patches/bachata-official/Bloodborne.xml");
      if(!xml.isFile()) {
        Log.e("BS4_FSR31","Active runtime resolution patch file missing: "+xml);
        return;
      }
      String before=new String(Files.readAllBytes(xml.toPath()),StandardCharsets.UTF_8);
      if(!before.contains("<ID>CUSA00900</ID>"))return;
      boolean controlled=preferences.getBoolean(CONTROLLED,false);
      if(enabled&&!controlled) {
        Set<String> prior=new HashSet<>();
        Matcher m=META.matcher(before);
        while(m.find()) {
          String tag=m.group(),title=name(tag);
          if(title.startsWith("Resolution Patch ")&&isEnabled(tag))prior.add(title);
        }
        preferences.edit().putStringSet(SAVED,prior).putBoolean(CONTROLLED,true).apply();
      }
      final Set<String> restore=preferences.getStringSet(SAVED,Collections.emptySet());
      final boolean restoring=!enabled&&controlled;
      final String selected=enabled&&preset>0 ?
          PREFIX+SIZES[preset]+" render res)" : "";
      StringBuffer out=new StringBuffer(before.length()+256);
      Matcher m=META.matcher(before);
      int count=0,changes=0;
      while(m.find()) {
        String tag=m.group(),title=name(tag),updated=tag;
        if(title.startsWith(PREFIX)) {
          if(title.equals(selected))count++;
          updated=toggle(tag,!selected.isEmpty()&&title.equals(selected));
        } else if(title.startsWith("Resolution Patch ")) {
          if(enabled)updated=toggle(tag,false);
          else if(restoring)updated=toggle(tag,restore.contains(title));
        }
        if(!updated.equals(tag))changes++;
        m.appendReplacement(out,Matcher.quoteReplacement(updated));
      }
      m.appendTail(out);
      if(!selected.isEmpty()&&count!=1){
        Log.e("BS4_FSR31","Internal patch missing: "+selected);return;
      }
      if(changes>0) {
        File tmp=new File(xml.getParentFile(),"Bloodborne.xml.fsr31.tmp");
        Files.write(tmp.toPath(),out.toString().getBytes(StandardCharsets.UTF_8));
        Files.move(tmp.toPath(),xml.toPath(),StandardCopyOption.REPLACE_EXISTING,
                   StandardCopyOption.ATOMIC_MOVE);
      }
      if(restoring)preferences.edit().remove(SAVED).putBoolean(CONTROLLED,false).apply();
      Log.i("BS4_FSR31","activeRuntime="+currentRuntime+" Bloodborne game-native scene="+
          (selected.isEmpty()?"original":SIZES[preset])+" UI=1920x1080 edits="+changes);
    } catch(Exception e) {
      Log.e("BS4_FSR31","Cannot set game-native render resolution",e);
    }
  }
}