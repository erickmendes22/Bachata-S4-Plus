package com.bachatas4.android.bridge;

import android.content.Context;
import com.bachatas4.android.service.SafBrokerSession;
import com.bachatas4.android.service.SafGameBroker;
import java.io.File;
import java.io.FileOutputStream;
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
        File eboot = new File(root, "eboot.bin");
        if (!eboot.isFile()) {
            try (FileOutputStream out = new FileOutputStream(eboot)) { out.write(0); }
            catch (Exception e) { throw new IllegalStateException("Could not create direct runtime stub", e); }
        }
        return "direct-runtime/" + gameId;
    }

    public static synchronized List<String> buildGameArguments(File eboot) {
        if (session == null) return Arrays.asList("-g", eboot.getPath());
        return Arrays.asList("--bachata-saf-socket", session.getSocketName(),
                "--bachata-saf-token", session.getToken(),
                "--ignore-game-patch", "-g", "eboot.bin");
    }

    public static synchronized void close() {
        SafBrokerSession old = session;
        session = null;
        if (old != null) {
            try { old.close(); } catch (Throwable ignored) {}
        }
    }
}
