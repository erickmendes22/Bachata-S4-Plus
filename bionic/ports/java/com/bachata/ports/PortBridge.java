package com.bachata.ports;

import android.app.*;
import android.content.*;
import android.content.pm.*;
import android.content.res.*;
import android.os.*;
import android.widget.Toast;
import dalvik.system.DexClassLoader;
import java.io.*;
import java.nio.*;
import java.nio.file.*;
import java.security.MessageDigest;
import java.util.*;
import java.util.zip.*;

public final class PortBridge {
    static final String ORDER = "ro.cobrabm.fexdroid.Order1886Activity";
    static final String SOTC = "com.gow3.android.MainActivity";
    static final String SOTC_GAME = "ro.cobrabm.fexdroid.GameActivity";
    static final String GAME_PATH = "bachata.exact.port.game";
    static ApplicationInfo hostInfo;
    static ClassLoader hostLoader;
    static String active;
    static File module;
    static ClassLoader moduleLoader;
    static File privateRoot;
    static String moduleKind(String activity) {
        return ORDER.equals(activity) ? "order" :
               (SOTC.equals(activity) || SOTC_GAME.equals(activity) ? "sotc" : null);
    }
    static String hex(byte[] value) {
        StringBuilder s = new StringBuilder();
        for (byte b : value) s.append(String.format(Locale.ROOT, "%02x", b & 255));
        return s.toString();
    }
    static String hash(File file) throws Exception {
        MessageDigest d = MessageDigest.getInstance("SHA-256");
        try (InputStream in = new FileInputStream(file)) {
            byte[] buf = new byte[65536]; int n;
            while ((n = in.read(buf)) != -1) d.update(buf, 0, n);
        }
        return hex(d.digest());
    }
    static synchronized ClassLoader loader(String kind, ClassLoader host) throws Exception {
        if (moduleLoader != null) {
            if (!kind.equals(active)) throw new IllegalStateException("port process collision");
            return moduleLoader;
        }
        if (hostInfo == null) throw new IllegalStateException("missing host ApplicationInfo");
        active = kind;
        privateRoot = new File(hostInfo.dataDir, "files/exact-ports/" + kind);
        if (!privateRoot.isDirectory() && !privateRoot.mkdirs()) throw new IOException("port storage");
        File dir = new File(hostInfo.dataDir, "code_cache/exact-ports");
        if (!dir.isDirectory() && !dir.mkdirs()) throw new IOException("port module storage");
        try (ZipFile hostApk = new ZipFile(hostInfo.sourceDir)) {
            String prefix = "assets/exact-ports/" + kind;
            String expected;
            try (InputStream in = hostApk.getInputStream(hostApk.getEntry(prefix + ".sha256"))) {
                expected = new String(in.readAllBytes(), java.nio.charset.StandardCharsets.US_ASCII).trim();
            }
            if (!expected.matches("[0-9a-f]{64}")) throw new IOException("invalid port digest");
            module = new File(dir, kind + "-" + expected + ".apk");
            if (!module.isFile() || module.canWrite() || !expected.equals(hash(module))) {
                Files.deleteIfExists(module.toPath());
                File part = File.createTempFile(kind, ".part", dir);
                try {
                    try (InputStream in = hostApk.getInputStream(hostApk.getEntry(prefix + ".apk"));
                         FileOutputStream out = new FileOutputStream(part)) {
                        // Set read-only before copying code, per Android 14 dynamic-code rules.
                        if (!part.setReadOnly()) throw new IOException("module must be read-only");
                        in.transferTo(out);
                        out.getFD().sync();
                    }
                    if (!expected.equals(hash(part))) throw new IOException("port module digest mismatch");
                    Files.move(part.toPath(), module.toPath(), StandardCopyOption.ATOMIC_MOVE);
                } finally { Files.deleteIfExists(part.toPath()); }
            }
        }
        final ClassLoader bridgeLoader = PortBridge.class.getClassLoader();
        moduleLoader = new DexClassLoader(module.getAbsolutePath(), dir.getAbsolutePath(),
                                          hostInfo.nativeLibraryDir, host.getParent()) {
            @Override protected Class<?> loadClass(String name, boolean resolve) throws ClassNotFoundException {
                if (name.startsWith("com.bachata.ports.")) return bridgeLoader.loadClass(name);
                return super.loadClass(name, resolve);
            }
        };
        return moduleLoader;
    }
    static final class PortContext extends ContextWrapper {
        final Resources resources;
        final String kind;
        Resources.Theme theme;
        PortContext(Context base, String kind) {
            super(base); this.kind = kind;
            try {
                PackageManager pm = base.getPackageManager();
                PackageInfo pi = pm.getPackageArchiveInfo(module.getAbsolutePath(), 0);
                if (pi == null || pi.applicationInfo == null) throw new IOException("module metadata");
                pi.applicationInfo.sourceDir = module.getAbsolutePath();
                pi.applicationInfo.publicSourceDir = module.getAbsolutePath();
                resources = pm.getResourcesForApplication(pi.applicationInfo);
            } catch (Exception e) { throw new IllegalStateException("donor resources", e); }
        }
        @Override public Resources getResources() { return resources; }
        @Override public AssetManager getAssets() { return resources.getAssets(); }
        @Override public ClassLoader getClassLoader() { return moduleLoader; }
        @Override public File getFilesDir() { return privateRoot; }
        @Override public SharedPreferences getSharedPreferences(String n, int mode) {
            return super.getSharedPreferences("exact-port-" + kind + "-" + n, mode);
        }
        @Override public Context createConfigurationContext(Configuration config) {
            PortContext c = new PortContext(super.createConfigurationContext(config), kind);
            c.resources.updateConfiguration(config, c.resources.getDisplayMetrics());
            return c;
        }
        @Override public Resources.Theme getTheme() {
            if (theme == null) {
                theme = resources.newTheme();
                theme.applyStyle("sotc".equals(kind) ? 0x7f0a0004 : 0x0103022e, true);
            }
            return theme;
        }
        @Override public void setTheme(int id) { getTheme().applyStyle(id, true); }
    }
    public static Context wrap(Context context) {
        if (context instanceof PortContext) return context;
        if (active == null || moduleLoader == null) throw new IllegalStateException("port not loaded");
        return new PortContext(context, active);
    }
    public static int resourceIdentifier(Resources r, String n, String t, String p) {
        if ("sotc".equals(active) && "com.bachatas4.plusapp".equals(p))
            p = "com.sotc.android.daedalus";
        return r.getIdentifier(n,t,p);
    }
    public static void prepareActivity(Activity a) {
        String path = a.getIntent().getStringExtra(GAME_PATH);
        if (path != null) {
            File game = new File(path);
            if (!game.isDirectory() || !new File(game,"eboot.bin").isFile())
                throw new IllegalStateException("direct donor game path unavailable");
            if ("order".equals(active)) {
                a.getSharedPreferences("order1886",0).edit().putString("gameDir",path).apply();
            } else {
                a.getSharedPreferences("sotc",0).edit().putString("game_dir",path)
                    .putBoolean("sotc_auto_start",true).apply();
            }
        }
        if ("sotc".equals(active)) a.setTheme(0x7f0a0004);
    }
    public static boolean hasGameAccess(Activity a) {
        if (Environment.isExternalStorageManager()) return true;
        String path = a.getSharedPreferences("sotc",0).getString("game_dir",null);
        return path != null && new File(path,"eboot.bin").canRead()
            && new File(path,"sce_sys/param.sfo").canRead();
    }
    static final String[][] SOTC_EXE = {
        {"sotcport/arm64/bin/sotc-probe","libbachata_sotc_exec_sotc_probe.so"},
        {"sotcport/arm64/bin/gow3-prepare","libbachata_sotc_exec_gow3_prepare.so"},
        {"sotcport/arm64/bin/kgsl-chip-id","libbachata_sotc_exec_kgsl_chip_id.so"},
        {"sotcport/arm64/bin/orbis-pkg-util","libbachata_sotc_exec_orbis_pkg_util.so"},
        {"sotcport/arm64/python/bin/python3.13","libbachata_sotc_exec_python3_13.so"}
    };
    static void linkExact(File dest, File src) throws IOException {
        if (!src.isFile() || !src.canExecute()) throw new IOException("missing installed executable: "+src);
        Path d = dest.toPath(), s = src.toPath();
        if (Files.isSymbolicLink(d) && Files.readSymbolicLink(d).equals(s)) return;
        if (dest.isFile() && !Files.isSymbolicLink(d)) {
            try { if (!hash(dest).equals(hash(src))) throw new IOException("donor binary mismatch: "+dest); }
            catch (IOException e) { throw e; }
            catch (Exception e) { throw new IOException(e); }
        }
        Files.createDirectories(d.getParent());
        Path tmp = d.resolveSibling(d.getFileName()+".bachata-link");
        Files.deleteIfExists(tmp);
        Files.createSymbolicLink(tmp,s);
        try { Files.move(tmp,d,StandardCopyOption.ATOMIC_MOVE,StandardCopyOption.REPLACE_EXISTING); }
        finally { Files.deleteIfExists(tmp); }
    }
    public static synchronized Process start(ProcessBuilder p) throws IOException {
        if ("order".equals(active)) {
            File dir = new File(privateRoot,"native-deps");
            File alias = new File(hostInfo.nativeLibraryDir,"libbachata_order_cxx.so");
            linkExact(new File(dir,"libc++_shared.so"),alias);
            Map<String,String> env = p.environment();
            String old = env.get("LD_LIBRARY_PATH");
            env.put("LD_LIBRARY_PATH",dir.getAbsolutePath()+":"+hostInfo.nativeLibraryDir+
                    (old==null || old.isEmpty() ? "" : ":"+old));
        } else if ("sotc".equals(active)) {
            for (String[] pair : SOTC_EXE) {
                File dest = new File(privateRoot,pair[0]);
                if (dest.exists() || Files.isSymbolicLink(dest.toPath()))
                    linkExact(dest,new File(hostInfo.nativeLibraryDir,pair[1]));
            }
        } else throw new IOException("unidentified donor process");
        return p.start();
    }
    static String title(File game) throws IOException {
        byte[] b = Files.readAllBytes(new File(game,"sce_sys/param.sfo").toPath());
        ByteBuffer v = ByteBuffer.wrap(b).order(ByteOrder.LITTLE_ENDIAN);
        if (b.length < 20 || v.getInt(0) != 0x46535000) throw new IOException("bad SFO");
        int keys=v.getInt(8), data=v.getInt(12), count=v.getInt(16);
        if (keys<20 || data<keys || data>b.length || count<0 || count>(b.length-20)/16)
            throw new IOException("bad SFO layout");
        for (int i=0;i<count;i++) {
            int at=20+i*16, key=keys+Short.toUnsignedInt(v.getShort(at));
            int len=v.getInt(at+4), pos=data+v.getInt(at+12);
            if (key<keys || key>=data || len<0 || pos<data || pos>b.length-len) throw new IOException("bad SFO entry");
            int k=key; while(k<data && b[k]!=0) k++;
            String name=new String(b,key,k-key,java.nio.charset.StandardCharsets.UTF_8);
            if ("TITLE_ID".equals(name)) {
                int end=pos;while(end<pos+len && b[end]!=0)end++;
                return new String(b,pos,end-pos,java.nio.charset.StandardCharsets.US_ASCII);
            }
        }
        return "";
    }
    static String knownKind(String t) {
        if ("CUSA00785".equals(t)) return "order";
        if ("CUSA08809".equals(t) || "CUSA08034".equals(t)) return "sotc";
        return null;
    }
    public static boolean tryLaunch(Context context,Object game) {
        String hint = String.valueOf(game);
        String kind = null;
        try {
            String rel = (String)game.getClass().getMethod("getRelativePath").invoke(game);
            File root = new File(context.getFilesDir(),rel).getCanonicalFile();
            hint += " "+rel;
            for (String id : new String[]{"CUSA00785","CUSA08809","CUSA08034"})
                if (hint.contains(id)) kind=knownKind(id);
            String actual = title(root);
            String confirmed = knownKind(actual);
            if (confirmed==null) {
                if(kind!=null) throw new IOException("title identity mismatch");
                return false;
            }
            kind=confirmed;
            if (!new File(root,"eboot.bin").canRead()) throw new IOException("game file is not directly readable");
            Intent launch = new Intent();
            launch.setClassName(context.getPackageName(),"order".equals(kind)?ORDER:SOTC);
            launch.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            launch.putExtra(GAME_PATH,root.getAbsolutePath());
            context.startActivity(launch);
            return true;
        } catch (Exception e) {
            if (kind==null) {
                android.util.Log.w("BachataExactPorts","Game identity inspection failed; normal route",e);
                return false;
            }
            android.util.Log.e("BachataExactPorts","Dedicated launch rejected",e);
            Toast.makeText(context,"Port dedicado: "+e.getMessage(),Toast.LENGTH_LONG).show();
            return true;
        }
    }
}
