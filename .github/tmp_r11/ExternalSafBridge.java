package com.bachatas4.android.bridge;

import android.content.Context;
import com.bachatas4.android.service.SafBrokerSession;
import com.bachatas4.android.service.SafGameBroker;
import java.io.File;
import java.io.FileOutputStream;
import java.nio.file.Files;
import java.nio.file.StandardCopyOption;
import java.util.Arrays;
import java.util.List;

public final class ExternalSafBridge {
    private static SafBrokerSession session;
    private ExternalSafBridge() {}

    public static synchronized String preparePath(Context context, String gameId, String relativePath) {
        close();
        if (relativePath == null || !relativePath.startsWith("saf:")) return relativePath;
        String uri = relativePath.substring(4);
        SafBrokerSession s = new SafGameBroker(context.getContentResolver()).start(uri);
        session = s;
        File root = new File(context.getFilesDir(), "direct-runtime/" + gameId);
        if (!root.exists() && !root.mkdirs()) throw new IllegalStateException("Could not create direct runtime directory");
        copyCachedParam(context.getFilesDir(), uri, root);
        File eboot = new File(root, "eboot.bin");
        if (!eboot.isFile()) {
            try (FileOutputStream out = new FileOutputStream(eboot)) { out.write(0); }
            catch (Exception e) { throw new IllegalStateException("Could not create direct runtime stub", e); }
        }
        return "direct-runtime/" + gameId;
    }

    private static void copyCachedParam(File filesDir, String uri, File root) {
        try {
            File src = new File(filesDir, "direct-meta/" + ExternalPkgBridge.hash(uri) + "/sce_sys/param.sfo");
            if (!src.isFile()) return;
            File dst = new File(root, "sce_sys/param.sfo");
            File p = dst.getParentFile(); if (p != null) p.mkdirs();
            Files.copy(src.toPath(), dst.toPath(), StandardCopyOption.REPLACE_EXISTING);
        } catch (Throwable ignored) {}
    }

    public static File iconPath(File filesDir, String relativePath) {
        if (relativePath == null || !relativePath.startsWith("saf:")) {
            return new File(filesDir, relativePath + "/sce_sys/icon0.png");
        }
        try {
            String uri = relativePath.substring(4);
            return new File(filesDir, "direct-meta/" + ExternalPkgBridge.hash(uri) + "/sce_sys/icon0.png");
        } catch (Throwable t) {
            return new File(filesDir, "__missing__/icon0.png");
        }
    }

    public static synchronized List<String> buildGameArguments(File eboot) {
        if (session == null) return Arrays.asList("-g", eboot.getPath());
        // The 1-byte file exists only to pass the old managed-path validation.
        // Remove it before launching so the runtime resolves eboot.bin through SAF.
        try { if (eboot.isFile()) eboot.delete(); } catch (Throwable ignored) {}
        return Arrays.asList("--bachata-saf-socket", session.getSocketName(),
                "--bachata-saf-token", session.getToken(),
                "--ignore-game-patch", "-g", "eboot.bin");
    }

    public static synchronized void close() {
        SafBrokerSession old = session;
        session = null;
        if (old != null) { try { old.close(); } catch (Throwable ignored) {} }
    }
}
