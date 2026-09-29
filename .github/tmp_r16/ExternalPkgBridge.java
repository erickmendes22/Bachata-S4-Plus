package com.bachatas4.android.bridge;

import android.app.Application;
import android.content.ContentResolver;
import android.content.Context;
import com.bachatas4.android.data.AndroidPkgExportTarget;
import com.bachatas4.android.data.ContentImportRequest;
import com.bachatas4.android.data.ContentImportResult;
import com.bachatas4.android.data.ContentImporter;
import com.bachatas4.android.data.PkgTreePublisher;
import com.bachatas4.android.model.Game;
import java.io.File;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.StandardCopyOption;
import java.util.Comparator;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import kotlin.coroutines.Continuation;
import kotlin.coroutines.EmptyCoroutineContext;
import kotlin.jvm.functions.Function2;
import kotlinx.coroutines.BuildersKt;
import kotlinx.coroutines.CoroutineScope;

public final class ExternalPkgBridge {
    private ExternalPkgBridge() {}

    public static Object finalizeStagingTree(final ContentImporter importer, final ContentImportRequest request,
            final File staging, final String mode, final String contentId,
            final Continuation<? super ContentImportResult> continuation) {
        final String destination = readDestination(importer);
        if (destination == null || destination.isEmpty()) {
            clearDirectUri(request.getId());
            return importer.finalizeStagingTree(request, staging, mode, contentId, continuation);
        }
        try {
            final long bytes = treeSize(staging);
            final ContentResolver resolver = contentResolver(importer);
            final AndroidPkgExportTarget target = new AndroidPkgExportTarget(resolver, destination);
            target.checkWritable();
            final PkgTreePublisher publisher = new PkgTreePublisher(target);
            final String directUri = (String) BuildersKt.runBlocking(
                EmptyCoroutineContext.INSTANCE,
                new Function2<CoroutineScope, Continuation<? super String>, Object>() {
                    @Override public Object invoke(CoroutineScope scope, Continuation<? super String> c) {
                        return PkgTreePublisher.publish$default(publisher, staging, request.getId(), null, null, c, 12, null);
                    }
                });

            File filesDir = (File) field(ContentImporter.class, "filesDir").get(importer);
            File localRoot = new File(filesDir, "games/" + request.getId());
            deleteTree(localRoot);
            localRoot.mkdirs();
            copyIfFile(new File(staging, "eboot.bin"), new File(localRoot, "eboot.bin"));
            copyIfFile(new File(staging, "sce_sys/param.sfo"), new File(localRoot, "sce_sys/param.sfo"));
            copyIfFile(new File(staging, "sce_sys/icon0.png"), new File(localRoot, "sce_sys/icon0.png"));
            saveDirectUri(request.getId(), directUri);
            deleteTree(staging);

            Game game = new Game(request.getId(), request.getTitle(), "games/" + request.getId(),
                    request.getSubtitle(), request.getDetail(), 0L);
            return new ContentImportResult(game, bytes, "");
        } catch (Throwable t) {
            if (t instanceof RuntimeException) throw (RuntimeException)t;
            throw new IllegalStateException("Could not publish extracted PKG to the selected folder", t);
        }
    }

    private static Context appContext() {
        try {
            Application app = (Application)Class.forName("android.app.ActivityThread").getMethod("currentApplication").invoke(null);
            return app;
        } catch (Throwable t) { return null; }
    }
    private static void saveDirectUri(String id, String uri) {
        Context c = appContext();
        if (c != null) c.getSharedPreferences("direct-games", 0).edit().putString(id, uri).commit();
    }
    private static void clearDirectUri(String id) {
        Context c = appContext();
        if (c != null) c.getSharedPreferences("direct-games", 0).edit().remove(id).commit();
    }
    private static void copyIfFile(File src, File dst) throws Exception {
        if (!src.isFile()) return;
        File p = dst.getParentFile(); if (p != null) p.mkdirs();
        Files.copy(src.toPath(), dst.toPath(), StandardCopyOption.REPLACE_EXISTING);
    }
    private static String readDestination(ContentImporter importer) {
        try {
            File filesDir = (File)field(ContentImporter.class, "filesDir").get(importer);
            File prefs = new File(filesDir.getParentFile(), "shared_prefs/pkg-extraction.xml");
            if (!prefs.isFile()) return null;
            String xml = new String(Files.readAllBytes(prefs.toPath()), StandardCharsets.UTF_8);
            Matcher m = Pattern.compile("<string\\s+name=\\\"destination\\\">(.*?)</string>", Pattern.DOTALL).matcher(xml);
            if (!m.find()) return null;
            String v = m.group(1).trim();
            if (v.isEmpty()) return null;
            return v.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", "\"").replace("&#39;", "'");
        } catch (Throwable ignored) { return null; }
    }
    private static ContentResolver contentResolver(ContentImporter importer) throws Exception {
        Object source = field(ContentImporter.class, "source").get(importer);
        return (ContentResolver)field(source.getClass(), "contentResolver").get(source);
    }
    private static java.lang.reflect.Field field(Class<?> type, String name) throws Exception {
        java.lang.reflect.Field f = type.getDeclaredField(name); f.setAccessible(true); return f;
    }
    private static long treeSize(File root) throws Exception {
        final long[] total = {0L};
        try (java.util.stream.Stream<java.nio.file.Path> s = Files.walk(root.toPath())) {
            s.filter(Files::isRegularFile).forEach(p -> { try { total[0] = Math.addExact(total[0], Files.size(p)); } catch (Exception e) { throw new RuntimeException(e); } });
        }
        return total[0];
    }
    private static void deleteTree(File root) throws Exception {
        if (!root.exists()) return;
        try (java.util.stream.Stream<java.nio.file.Path> s = Files.walk(root.toPath())) {
            s.sorted(Comparator.reverseOrder()).forEach(p -> { try { Files.deleteIfExists(p); } catch (Exception e) { throw new RuntimeException(e); } });
        }
    }
}
