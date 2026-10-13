package com.bachatas4.android.bridge;
import android.app.Activity;
import android.app.AlertDialog;
import android.content.Context;
import android.content.SharedPreferences;
import android.view.View;
import android.widget.Button;
import android.widget.FrameLayout;
import android.widget.Toast;
import java.io.File;
import java.util.Map;

/** UI and launch configuration; the native worker reports actual temporal dispatch. */
public final class Fsr3Ui {
  private static final String[] MODES={"Native AA","Quality","Balanced","Performance","Ultra Performance"};
  private static volatile Context appContext;
  private static final String TAG="bachata.fsr31.control";
  private static int preset(SharedPreferences p){return Math.max(0,Math.min(4,p.getInt("preset",1)));}
  public static void attach(final Activity a){
    appContext=a.getApplicationContext();
    final View root=a.findViewById(android.R.id.content);
    if(!(root instanceof FrameLayout)||root.findViewWithTag(TAG)!=null)return;
    final SharedPreferences p=a.getSharedPreferences("bs4_fsr31",0);
    final Button button=new Button(a);button.setTag(TAG);button.setAllCaps(false);button.setTextSize(12);
    refresh(button,p);
    FrameLayout.LayoutParams lp=new FrameLayout.LayoutParams(-2,px(a,42),android.view.Gravity.TOP|android.view.Gravity.END);
    lp.setMargins(0,px(a,54),px(a,10),0);((FrameLayout)root).addView(button,lp);
    button.setOnClickListener(v->new AlertDialog.Builder(a).setTitle("Upscaler")
      .setSingleChoiceItems(new String[]{"FSR 1","FSR 3.1"},p.getBoolean("enabled",false)?1:0,(d,index)->{
        p.edit().putBoolean("enabled",index==1).commit();refresh(button,p);d.dismiss();
        if(index==1)modes(a,button,p);else notice(a);
      }).setNeutralButton("Modos FSR 3.1",(d,index)->modes(a,button,p))
      .setNegativeButton("Cancelar",null).show());
  }
  private static void modes(Activity a,Button b,SharedPreferences p){
    new AlertDialog.Builder(a).setTitle("FSR 3.1")
      .setSingleChoiceItems(MODES,preset(p),(d,index)->{
        p.edit().putInt("preset",index).putBoolean("enabled",true).commit();refresh(b,p);d.dismiss();notice(a);
      }).setNegativeButton("Cancelar",null).show();
  }
  private static void notice(Context a){Toast.makeText(a,"A seleção será aplicada ao iniciar o jogo.",Toast.LENGTH_SHORT).show();}
  private static void refresh(Button b,SharedPreferences p){b.setText(p.getBoolean("enabled",false)?"FSR 3.1 • "+MODES[preset(p)]:"FSR 1 • Configurar");}
  private static int px(Context a,int value){return Math.round(value*a.getResources().getDisplayMetrics().density);}
  public static void enrichProcessEnvironment(Map<String,String> env){enrichEnvironment(appContext,env);}
  public static void enrichEnvironment(Context context,Map<String,String> env){
    if(context==null||env==null)return;
    SharedPreferences p=context.getSharedPreferences("bs4_fsr31",0);
    boolean enabled=p.getBoolean("enabled",false);int mode=preset(p);
    env.put("BACHATA_FSR31_MODE",enabled?Integer.toString(mode):"-1");
    Fsr3Resolution.apply(context,enabled,mode);
    if(!enabled)return;
    env.put("BACHATA_FSR31_INPUT","port");env.put("BACHATA_FSR31_NATIVE_UI","1");
    String stage=new File(context.getApplicationInfo().nativeLibraryDir,"libbachata_fsr31_stage.so").getAbsolutePath();
    String old=env.get("LD_PRELOAD");
    if(old==null||old.isEmpty())env.put("LD_PRELOAD",stage);
    else if(!old.contains(stage))env.put("LD_PRELOAD",old+" "+stage);
  }
}
