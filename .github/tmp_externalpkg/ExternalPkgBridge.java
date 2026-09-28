package com.bachatas4.android.service;

import android.content.ContentResolver;
import com.bachatas4.android.data.AndroidPkgExportTarget;
import com.bachatas4.android.data.ContentImportRequest;
import com.bachatas4.android.data.ContentImportResult;
import com.bachatas4.android.data.ContentImporter;
import com.bachatas4.android.data.GameRepository;
import com.bachatas4.android.data.PkgTreePublisher;
import com.bachatas4.android.model.Game;
import com.bachatas4.android.model.GameStorageMode;
import java.io.File;
import java.lang.reflect.Field;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.util.Comparator;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import kotlin.coroutines.Continuation;
import kotlin.coroutines.EmptyCoroutineContext;
import kotlin.jvm.functions.Function2;
import kotlinx.coroutines.BuildersKt;
import kotlinx.coroutines.CoroutineScope;

/** Minimal bridge: only changes PKG finalization when an external extraction folder is selected. */
public final class ExternalPkgBridge {
    private ExternalPkgBridge() {}

    public static Object finalizeStagingTree(
            final ContentImporter importer,
            final ContentImportRequest request,
            final File staging,
            final String mode,
            final String contentId,
            final Continuation<? super ContentImportResult> continuation) {
        final String destination = readDestination(importer);
        if (destination == null || destination.isEmpty()) {
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
                        @Override
                        public Object invoke(CoroutineScope scope, Continuation<? super String> c) {
                            return PkgTreePublisher.publish$default(
                                    publisher, staging, request.getId(), null, null, c, 12, null);
                        }
                    });
            deleteTree(staging);
            Game game = new Game(
                    request.getId(),
                    request.getTitle(),
                    "",
                    request.getSubtitle(),
                    request.getDetail(),
                    0L,
                    GameStorageMode.DIRECT,
                    directUri,
                    0,
                    null);
            return new ContentImportResult(game, bytes, "");
        } catch (Throwable t) {
            if (t instanceof RuntimeException) throw (RuntimeException) t;
            throw new IllegalStateException("Could not publish extracted PKG to the selected folder", t);
        }
    }

    public static Object addImportedGame(
            GameRepository repository,
            ContentImportResult result,
            String sourceUri,
            long importedAtMs,
            Continuation<?> continuation) {
        Game game = result.getGame();
        if (game.getStorageMode() == GameStorageMode.DIRECT) {
            @SuppressWarnings("unchecked")
            Continuation<Object> c = (Continuation<Object>) continuation;
            return repository.addDirectGame(game, importedAtMs, c);
        }
        @SuppressWarnings("unchecked")
        Continuation<Object> c = (Continuation<Object>) continuation;
        return repository.addImportedGame(result, sourceUri, importedAtMs, c);
    }

    private static String readDestination(ContentImporter importer) {
        try {
            File filesDir = (File) field(ContentImporter.class, "filesDir").get(importer);
            File prefs = new File(filesDir.getParentFile(), "shared_prefs/pkg-extraction.xml");
            if (!prefs.isFile()) return null;
            String xml = new String(Files.readAllBytes(prefs.toPath()), StandardCharsets.UTF_8);
            Matcher m = Pattern.compile("<string\\s+name=\\\"destination\\\">(.*?)</string>", Pattern.DOTALL).matcher(xml);
            if (!m.find()) return null;
            String value = m.group(1).trim();
            if (value.isEmpty()) return null;
            return value.replace("&amp;", "&").replace("&lt;", "<").replace("&gt;", ">").replace("&quot;", "\\\"").replace("&#39;", "'");
        } catch (Throwable ignored) {
            return null;
        }
    }

    private static ContentResolver contentResolver(ContentImporter importer) throws Exception {
        Object source = field(ContentImporter.class, "source").get(importer);
        Field resolver = field(source.getClass(), "resolver");
        return (ContentResolver) resolver.get(source);
    }

    private static Field field(Class<?> type, String name) throws Exception {
        Field f = type.getDeclaredField(name);
        f.setAccessible(true);
        return f;
    }

    private static long treeSize(File root) throws Exception {
        final long[] total = {0L};
        try (java.util.stream.Stream<java.nio.file.Path> s = Files.walk(root.toPath())) {
            s.filter(Files::isRegularFile).forEach(p -> {
                try { total[0] = Math.addExact(total[0], Files.size(p)); } catch (Exception e) { throw new RuntimeException(e); }
            });
        }
        return total[0];
    }

    private static void deleteTree(File root) throws Exception {
        if (!root.exists()) return;
        try (java.util.stream.Stream<java.nio.file.Path> s = Files.walk(root.toPath())) {
            s.sorted(Comparator.reverseOrder()).forEach(p -> {
                try { Files.deleteIfExists(p); } catch (Exception e) { throw new RuntimeException(e); }
            });
        }
    }
}
