package com.bachatas4.android.bridge;

import android.content.ContentResolver;
import android.net.Uri;
import android.provider.DocumentsContract;
import com.bachatas4.android.data.ContentImportRequest;
import com.bachatas4.android.data.ContentImportResult;
import com.bachatas4.android.data.ContentImporter;
import com.bachatas4.android.data.ContentTreeEntry;
import com.bachatas4.android.model.Game;
import java.io.File;
import java.io.InputStream;
import java.io.OutputStream;
import java.nio.file.Files;
import java.nio.file.StandardOpenOption;
import java.util.List;
import kotlin.coroutines.Continuation;
import kotlin.jvm.functions.Function3;

public final class ExternalFolderBridge {
    private ExternalFolderBridge() {}

    public static Object importGameTree(ContentImporter importer,
            ContentImportRequest request,
            List<ContentTreeEntry> entries,
            Function3<? super Long, ? super Long, ? super String, ?> progress,
            Continuation<? super ContentImportResult> continuation) {
        try {
            ContentResolver resolver = ExternalPkgBridge.contentResolver(importer);
            File filesDir = (File) ExternalPkgBridge.field(ContentImporter.class, "filesDir").get(importer);
            File localRoot = new File(filesDir, "games/" + request.getId());
            ExternalPkgBridge.deleteTree(localRoot);
            localRoot.mkdirs();

            long total = 0L;
            String treeUri = null;
            boolean hasEboot = false;
            for (ContentTreeEntry entry : entries) {
                Long expected = entry.getExpectedBytes();
                if (expected != null && expected.longValue() > 0L) total += expected.longValue();
                if (treeUri == null) treeUri = deriveTreeUri(entry.getSourceUri());
                String rel = normalize(entry.getRelativePath());
                if ("eboot.bin".equals(rel) || "sce_sys/param.sfo".equals(rel) || "sce_sys/icon0.png".equals(rel)) {
                    File dst = new File(localRoot, rel);
                    copyUri(resolver, entry.getSourceUri(), dst);
                    if ("eboot.bin".equals(rel)) hasEboot = dst.isFile() && dst.length() > 1L;
                }
            }
            if (!hasEboot) throw new IllegalStateException("Selected folder does not contain a readable eboot.bin");
            if (treeUri == null || treeUri.isEmpty()) throw new IllegalStateException("Could not resolve selected game folder URI");

            ExternalPkgBridge.saveDirectUri(request.getId(), treeUri);
            Game game = new Game(request.getId(), request.getTitle(), "games/" + request.getId(),
                    request.getSubtitle(), request.getDetail(), 0L);
            return new ContentImportResult(game, total, "");
        } catch (Throwable t) {
            try {
                File filesDir = (File) ExternalPkgBridge.field(ContentImporter.class, "filesDir").get(importer);
                ExternalPkgBridge.deleteTree(new File(filesDir, "games/" + request.getId()));
                ExternalPkgBridge.clearDirectUri(request.getId());
            } catch (Throwable ignored) {}
            if (t instanceof RuntimeException) throw (RuntimeException)t;
            throw new IllegalStateException("Could not register external game folder", t);
        }
    }

    private static String normalize(String s) {
        String r = s == null ? "" : s.replace('\\', '/');
        while (r.startsWith("/")) r = r.substring(1);
        return r;
    }

    private static String deriveTreeUri(String source) {
        try {
            Uri u = Uri.parse(source);
            String treeId = DocumentsContract.getTreeDocumentId(u);
            if (treeId != null && u.getAuthority() != null) {
                return DocumentsContract.buildTreeDocumentUri(u.getAuthority(), treeId).toString();
            }
        } catch (Throwable ignored) {}
        return null;
    }

    private static void copyUri(ContentResolver resolver, String source, File dst) throws Exception {
        File parent = dst.getParentFile();
        if (parent != null) parent.mkdirs();
        try (InputStream in = resolver.openInputStream(Uri.parse(source))) {
            if (in == null) throw new IllegalStateException("Could not open " + source);
            try (OutputStream out = Files.newOutputStream(dst.toPath(), StandardOpenOption.CREATE, StandardOpenOption.TRUNCATE_EXISTING, StandardOpenOption.WRITE)) {
                byte[] buf = new byte[1024 * 1024];
                int n;
                while ((n = in.read(buf)) >= 0) {
                    if (n > 0) out.write(buf, 0, n);
                }
            }
        }
    }
}
