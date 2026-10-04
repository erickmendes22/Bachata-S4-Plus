package com.bachatas4.android.savelegacy;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.Context;
import android.content.DialogInterface;
import android.content.Intent;
import android.net.Uri;
import android.widget.Toast;
import java.io.*;
import java.text.SimpleDateFormat;
import java.util.*;
import java.util.zip.*;
import org.json.JSONObject;

public final class ReleaseSaveManager {
    private static final int REQ_EXPORT = 0x5341;
    private static final int REQ_IMPORT = 0x5342;
    private static final long MAX_ARCHIVE_BYTES = 8L * 1024L * 1024L * 1024L;
    private static final int MAX_ENTRIES = 100000;
    private static Activity pendingActivity;
    private static String pendingGameId;
    private static int pendingUserId = -1;
    private static File pendingGameDir;
    private ReleaseSaveManager() {}

    public static void open(Context context, String gameId) {
        if (!(context instanceof Activity)) {
            Toast.makeText(context, "Saves: activity context unavailable", Toast.LENGTH_LONG).show();
            return;
        }
        Activity a = (Activity) context;
        String id = normalizeTitleId(gameId);
        if (id == null) {
            Toast.makeText(a, "Invalid game ID: " + gameId, Toast.LENGTH_LONG).show();
            return;
        }
        showMain(a, id);
    }

    public static void onActivityResult(Activity activity, int requestCode, int resultCode, Intent data) {
        if ((requestCode != REQ_EXPORT && requestCode != REQ_IMPORT) || resultCode != Activity.RESULT_OK || data == null || data.getData() == null) return;
        final Uri uri = data.getData();
        final String gameId = pendingGameId;
        final int userId = pendingUserId;
        final File gameDir = pendingGameDir;
        pendingActivity = activity;
        if (gameId == null) return;
        if (requestCode == REQ_EXPORT) {
            if (gameDir == null || !gameDir.isDirectory()) {
                toast(activity, "Save folder no longer exists");
                return;
            }
            runBackground(activity, "Exporting save...", new Work() {
                public String run() throws Exception {
                    exportArchive(activity, uri, gameId, userId, gameDir);
                    return "Export completed";
                }
            });
        } else {
            if (isMutationBlocked()) {
                toast(activity, "A game or save operation is running. Close it before importing.");
                return;
            }
            runBackground(activity, "Importing save...", new Work() {
                public String run() throws Exception {
                    importArchive(activity, uri, gameId);
                    return "Import completed";
                }
            });
        }
    }

    private static void showMain(final Activity a, final String gameId) {
        final File home = findHome(a);
        final List<SaveRoot> roots = scanRoots(home, gameId);
        final List<String> items = new ArrayList<String>();
        for (SaveRoot r : roots) items.add("User " + r.userId + "  •  " + humanSize(sizeOf(r.dir)) + "  •  " + countFiles(r.dir) + " files");
        items.add("Import archive");
        items.add("Backups / Restore");
        String message = roots.isEmpty() ? "No saves found\n\n" + home.getAbsolutePath() : "Save location\n" + home.getAbsolutePath();
        new AlertDialog.Builder(a)
            .setTitle("Saves · " + gameId)
            .setMessage(message)
            .setItems(items.toArray(new String[0]), new DialogInterface.OnClickListener() {
                public void onClick(DialogInterface d, int which) {
                    if (which < roots.size()) showUserActions(a, gameId, roots.get(which));
                    else if (which == roots.size()) startImport(a, gameId);
                    else showBackups(a, gameId);
                }
            })
            .setNegativeButton("Close", null)
            .show();
    }

    private static void showUserActions(final Activity a, final String gameId, final SaveRoot root) {
        final String[] actions = new String[]{"Export", "Create backup", "Refresh"};
        new AlertDialog.Builder(a)
            .setTitle(gameId + " · User " + root.userId)
            .setMessage(root.dir.getAbsolutePath() + "\n" + humanSize(sizeOf(root.dir)))
            .setItems(actions, new DialogInterface.OnClickListener() {
                public void onClick(DialogInterface dialog, int which) {
                    if (which == 0) startExport(a, gameId, root);
                    else if (which == 1) {
                        if (isMutationBlocked()) { toast(a, "A game or save operation is running."); return; }
                        runBackground(a, "Creating backup...", new Work() {
                            public String run() throws Exception { createBackup(a, gameId, root.userId, root.dir); return "Backup created"; }
                        });
                    } else showMain(a, gameId);
                }
            })
            .setNegativeButton("Back", new DialogInterface.OnClickListener() { public void onClick(DialogInterface d, int w) { showMain(a, gameId); }})
            .show();
    }

    private static void showBackups(final Activity a, final String gameId) {
        final List<Backup> backups = scanBackups(a, gameId);
        if (backups.isEmpty()) { toast(a, "No backups for " + gameId); return; }
        String[] labels = new String[backups.size()];
        for (int i=0;i<backups.size();i++) {
            Backup b=backups.get(i);
            labels[i]="User " + b.userId + " · " + b.dir.getName() + " · " + humanSize(sizeOf(b.dir));
        }
        new AlertDialog.Builder(a)
            .setTitle("Backups · " + gameId)
            .setItems(labels, new DialogInterface.OnClickListener() {
                public void onClick(DialogInterface d, int which) { confirmRestore(a, gameId, backups.get(which)); }
            })
            .setNegativeButton("Back", new DialogInterface.OnClickListener(){ public void onClick(DialogInterface d,int w){ showMain(a, gameId); }})
            .show();
    }

    private static void confirmRestore(final Activity a, final String gameId, final Backup backup) {
        new AlertDialog.Builder(a)
            .setTitle("Restore backup?")
            .setMessage("User " + backup.userId + "\n" + backup.dir.getName() + "\n\nCurrent save will be backed up first.")
            .setPositiveButton("Restore", new DialogInterface.OnClickListener() {
                public void onClick(DialogInterface d, int w) {
                    if (isMutationBlocked()) { toast(a, "A game or save operation is running."); return; }
                    runBackground(a, "Restoring backup...", new Work() {
                        public String run() throws Exception {
                            File target = new File(new File(new File(findHome(a), String.valueOf(backup.userId)), "savedata"), gameId);
                            if (target.isDirectory()) createBackup(a, gameId, backup.userId, target);
                            replaceTree(backup.dir, target);
                            return "Backup restored";
                        }
                    });
                }
            })
            .setNegativeButton("Cancel", null).show();
    }

    private static void startExport(Activity a, String gameId, SaveRoot root) {
        pendingActivity = a; pendingGameId = gameId; pendingUserId = root.userId; pendingGameDir = root.dir;
        Intent i = new Intent(Intent.ACTION_CREATE_DOCUMENT);
        i.addCategory(Intent.CATEGORY_OPENABLE);
        i.setType("application/zip");
        i.putExtra(Intent.EXTRA_TITLE, gameId + "-user" + root.userId + "-" + stamp() + ".zip");
        a.startActivityForResult(i, REQ_EXPORT);
    }

    private static void startImport(Activity a, String gameId) {
        pendingActivity = a; pendingGameId = gameId; pendingUserId = -1; pendingGameDir = null;
        Intent i = new Intent(Intent.ACTION_OPEN_DOCUMENT);
        i.addCategory(Intent.CATEGORY_OPENABLE);
        i.setType("application/zip");
        a.startActivityForResult(i, REQ_IMPORT);
    }

    private static void exportArchive(Context c, Uri uri, String gameId, int userId, File gameDir) throws Exception {
        OutputStream raw = c.getContentResolver().openOutputStream(uri, "w");
        if (raw == null) throw new IOException("Unable to open export destination");
        ZipOutputStream out = new ZipOutputStream(new BufferedOutputStream(raw));
        try {
            JSONObject m = new JSONObject();
            m.put("format", "Bachata S4 Save Manager");
            m.put("version", 1);
            m.put("titleId", gameId);
            m.put("userId", userId);
            m.put("createdAt", System.currentTimeMillis());
            byte[] meta = m.toString(2).getBytes("UTF-8");
            out.putNextEntry(new ZipEntry("manifest.json")); out.write(meta); out.closeEntry();
            zipTree(out, gameDir, "saves/" + gameId + "/");
        } finally { out.close(); }
    }

    private static void importArchive(Context c, Uri uri, String expectedGameId) throws Exception {
        File temp = File.createTempFile("save-import-", ".zip", c.getCacheDir());
        try {
            InputStream in = c.getContentResolver().openInputStream(uri);
            if (in == null) throw new IOException("Unable to open import document");
            copyStream(in, new FileOutputStream(temp), MAX_ARCHIVE_BYTES);
            ZipFile z = new ZipFile(temp);
            try {
                ZipEntry me = z.getEntry("manifest.json");
                if (me == null) throw new IOException("Archive manifest is missing");
                String manifest = readString(z.getInputStream(me), 1024 * 1024);
                JSONObject obj = new JSONObject(manifest);
                String format = obj.optString("format", "");
                if (!format.contains("Bachata")) throw new IOException("Unsupported save archive");
                String gameId = normalizeTitleId(obj.optString("titleId", ""));
                if (gameId == null || !gameId.equals(expectedGameId)) throw new IOException("Archive is for " + obj.optString("titleId", "another game"));
                int userId = obj.optInt("userId", -1);
                if (userId < 0) throw new IOException("Invalid user ID in archive");
                File stage = new File(c.getCacheDir(), "save-stage-" + System.nanoTime());
                if (!stage.mkdirs()) throw new IOException("Unable to create staging folder");
                long total = 0; int count = 0;
                String prefix = "saves/" + gameId + "/";
                Enumeration<? extends ZipEntry> en = z.entries();
                while (en.hasMoreElements()) {
                    ZipEntry e = en.nextElement();
                    String name = e.getName();
                    if (!name.startsWith(prefix) || name.equals(prefix)) continue;
                    if (++count > MAX_ENTRIES) throw new IOException("Too many archive entries");
                    String rel = name.substring(prefix.length());
                    File out = safeChild(stage, rel);
                    if (e.isDirectory()) { if (!out.isDirectory() && !out.mkdirs()) throw new IOException("Unable to create " + rel); continue; }
                    File par = out.getParentFile(); if (!par.isDirectory() && !par.mkdirs()) throw new IOException("Unable to create folder");
                    InputStream zin = z.getInputStream(e); FileOutputStream fout = new FileOutputStream(out);
                    total += copyStream(zin, fout, MAX_ARCHIVE_BYTES - total);
                    if (total > MAX_ARCHIVE_BYTES) throw new IOException("Archive exceeds size limit");
                }
                if (count == 0) throw new IOException("Archive contains no save files");
                File target = new File(new File(new File(findHome(c), String.valueOf(userId)), "savedata"), gameId);
                if (target.isDirectory()) createBackup(c, gameId, userId, target);
                replaceTree(stage, target);
                deleteTree(stage);
            } finally { z.close(); }
        } finally { temp.delete(); }
    }

    private static File createBackup(Context c, String gameId, int userId, File source) throws Exception {
        File root = new File(new File(new File(c.getFilesDir(), "save-manager-backups"), gameId), String.valueOf(userId));
        File dst = new File(root, stamp());
        copyTree(source, dst);
        return dst;
    }

    private static List<Backup> scanBackups(Context c, String gameId) {
        List<Backup> out = new ArrayList<Backup>();
        File root = new File(new File(c.getFilesDir(), "save-manager-backups"), gameId);
        File[] users = root.listFiles(); if (users == null) return out;
        for (File u : users) {
            if (!u.isDirectory()) continue;
            int uid; try { uid = Integer.parseInt(u.getName()); } catch (Exception e) { continue; }
            File[] bs = u.listFiles(); if (bs == null) continue;
            Arrays.sort(bs, Collections.reverseOrder());
            for (File b : bs) if (b.isDirectory()) out.add(new Backup(uid,b));
        }
        Collections.sort(out, new Comparator<Backup>() { public int compare(Backup a, Backup b) { return b.dir.getName().compareTo(a.dir.getName()); }});
        return out;
    }

    private static List<SaveRoot> scanRoots(File home, String gameId) {
        List<SaveRoot> out = new ArrayList<SaveRoot>();
        File[] users = home.listFiles(); if (users == null) return out;
        Arrays.sort(users, new Comparator<File>() { public int compare(File a, File b){ return a.getName().compareTo(b.getName()); }});
        for (File u : users) {
            if (!u.isDirectory()) continue;
            int uid; try { uid = Integer.parseInt(u.getName()); } catch (Exception e) { continue; }
            File dir = new File(new File(u, "savedata"), gameId);
            if (dir.isDirectory()) out.add(new SaveRoot(uid, dir));
        }
        return out;
    }

    private static File findHome(Context c) {
        File base = c.getFilesDir();
        File[] candidates = new File[]{
            new File(base, "runtime-home/.local/share/shadPS4/home"),
            new File(base, "runtime/.local/share/shadPS4/home"),
            new File(base, ".local/share/shadPS4/home")
        };
        for (File f : candidates) if (f.isDirectory()) return f;
        return candidates[0];
    }

    private static boolean isMutationBlocked() {
        try {
            Class<?> c = Class.forName("com.bachatas4.android.data.GameMutationGuard");
            Object inst = c.getField("INSTANCE").get(null);
            boolean runtime = ((Boolean)c.getMethod("getRuntimeReserved").invoke(inst)).booleanValue();
            boolean save = ((Boolean)c.getMethod("getSaveReserved").invoke(inst)).booleanValue();
            Object readiness = c.getMethod("recoveryReadiness").invoke(inst);
            boolean recovery = false;
            try { recovery = ((Boolean)readiness.getClass().getMethod("getRequired").invoke(readiness)).booleanValue(); } catch (Throwable ignored) {}
            return runtime || save || recovery;
        } catch (Throwable ignored) { return false; }
    }

    private static void replaceTree(File src, File dst) throws Exception {
        File parent = dst.getParentFile(); if (!parent.isDirectory() && !parent.mkdirs()) throw new IOException("Unable to create save parent");
        File tmp = new File(parent, dst.getName() + ".importing");
        deleteTree(tmp); copyTree(src, tmp);
        File old = new File(parent, dst.getName() + ".old"); deleteTree(old);
        if (dst.exists() && !dst.renameTo(old)) { deleteTree(dst); }
        if (!tmp.renameTo(dst)) { copyTree(tmp, dst); deleteTree(tmp); }
        deleteTree(old);
    }

    private static void copyTree(File src, File dst) throws Exception {
        if (src.isDirectory()) {
            if (!dst.isDirectory() && !dst.mkdirs()) throw new IOException("Unable to create " + dst);
            File[] fs=src.listFiles(); if (fs==null) return;
            for(File f:fs) copyTree(f,new File(dst,f.getName()));
        } else {
            File p=dst.getParentFile(); if(!p.isDirectory()&&!p.mkdirs()) throw new IOException("Unable to create folder");
            copyStream(new FileInputStream(src),new FileOutputStream(dst),MAX_ARCHIVE_BYTES);
        }
    }

    private static void zipTree(ZipOutputStream out, File src, String prefix) throws Exception {
        File[] fs=src.listFiles(); if(fs==null) return;
        byte[] buf=new byte[131072];
        for(File f:fs){
            String name=prefix+f.getName();
            if(f.isDirectory()){ out.putNextEntry(new ZipEntry(name+"/")); out.closeEntry(); zipTree(out,f,name+"/"); }
            else { out.putNextEntry(new ZipEntry(name)); FileInputStream in=new FileInputStream(f); try { int n; while((n=in.read(buf))!=-1) out.write(buf,0,n); } finally { in.close(); } out.closeEntry(); }
        }
    }

    private static long copyStream(InputStream in, OutputStream out, long max) throws Exception {
        byte[] b=new byte[131072]; long total=0; try { int n; while((n=in.read(b))!=-1){ total+=n; if(total>max) throw new IOException("Data exceeds allowed size"); out.write(b,0,n);} out.flush(); return total; } finally { try{in.close();}catch(Throwable ignored){} try{out.close();}catch(Throwable ignored){} }
    }
    private static String readString(InputStream in, long max) throws Exception { ByteArrayOutputStream b=new ByteArrayOutputStream(); byte[] x=new byte[8192]; long total=0; try { int n; while((n=in.read(x))!=-1){ total+=n; if(total>max) throw new IOException("Data exceeds allowed size"); b.write(x,0,n);} return b.toString("UTF-8"); } finally { try{in.close();}catch(Throwable ignored){} } }
    private static File safeChild(File root,String rel)throws Exception{ File f=new File(root,rel); String rp=root.getCanonicalPath()+File.separator; String fp=f.getCanonicalPath(); if(!fp.startsWith(rp)) throw new IOException("Unsafe archive path"); return f; }
    private static void deleteTree(File f){ if(f==null||!f.exists())return; if(f.isDirectory()){File[] a=f.listFiles();if(a!=null)for(File x:a)deleteTree(x);} f.delete(); }
    private static long sizeOf(File f){ if(f==null||!f.exists())return 0; if(f.isFile())return f.length(); long n=0;File[] a=f.listFiles();if(a!=null)for(File x:a)n+=sizeOf(x);return n; }
    private static int countFiles(File f){ if(f==null||!f.exists())return 0;if(f.isFile())return 1;int n=0;File[]a=f.listFiles();if(a!=null)for(File x:a)n+=countFiles(x);return n; }
    private static String humanSize(long n){ if(n<1024)return n+" B"; double v=n;String[]u={"KB","MB","GB","TB"};int i=-1;do{v/=1024.0;i++;}while(v>=1024&&i<u.length-1);return String.format(Locale.US,"%.1f %s",v,u[i]); }
    private static String stamp(){ return new SimpleDateFormat("yyyyMMdd-HHmmss",Locale.US).format(new Date()); }
    private static String normalizeTitleId(String s){ if(s==null)return null;String x=s.trim().toUpperCase(Locale.US);return x.matches("[A-Z]{4}[0-9]{5}")?x:null; }
    private static void toast(final Activity a, final String s){ a.runOnUiThread(new Runnable(){public void run(){Toast.makeText(a,s,Toast.LENGTH_LONG).show();}}); }
    private static void runBackground(final Activity a, final String start, final Work work){ toast(a,start); new Thread(new Runnable(){public void run(){ try{ final String done=work.run(); toast(a,done); }catch(final Throwable t){ toast(a,"Save Manager: "+(t.getMessage()==null?t.getClass().getSimpleName():t.getMessage())); }}},"BachataSaveManager").start(); }
    private interface Work{ String run() throws Exception; }
    private static final class SaveRoot{ final int userId;final File dir;SaveRoot(int u,File d){userId=u;dir=d;} }
    private static final class Backup{ final int userId;final File dir;Backup(int u,File d){userId=u;dir=d;} }
}
