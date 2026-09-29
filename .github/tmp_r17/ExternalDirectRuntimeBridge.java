package com.bachatas4.android.bridge;

import android.app.Application;
import android.content.Context;
import com.bachatas4.android.service.SafBrokerSession;
import com.bachatas4.android.service.SafGameBroker;
import java.io.File;
import java.util.ArrayList;
import java.util.List;

public final class ExternalDirectRuntimeBridge {
    private static SafBrokerSession session;
    private ExternalDirectRuntimeBridge() {}

    private static Context appContext() {
        try {
            return (Application)Class.forName("android.app.ActivityThread").getMethod("currentApplication").invoke(null);
        } catch (Throwable t) { return null; }
    }

    public static synchronized List<String> arguments(List<String> original, File overrideRoot) {
        Context c = appContext();
        if (c == null || overrideRoot == null) return original;
        String gameId = overrideRoot.getName();
        String uri = c.getSharedPreferences("direct-games", 0).getString(gameId, null);
        if (uri == null || uri.isEmpty()) {
            close();
            return original;
        }
        close();
        session = new SafGameBroker(c.getContentResolver()).start(uri);
        ArrayList<String> out = new ArrayList<>();
        boolean replacedGame = false;
        for (int i = 0; i < original.size(); i++) {
            String s = original.get(i);
            if ("-g".equals(s) && i + 1 < original.size()) {
                out.add("-g");
                out.add("eboot.bin");
                i++;
                replacedGame = true;
            } else {
                out.add(s);
            }
        }
        if (!replacedGame) {
            out.add("-g");
            out.add("eboot.bin");
        }
        out.add("--bachata-saf-socket");
        out.add(session.getSocketName());
        out.add("--bachata-saf-token");
        out.add(session.getToken());
        out.add("--ignore-game-patch");
        return out;
    }

    public static synchronized void close() {
        SafBrokerSession old = session;
        session = null;
        if (old != null) {
            try { old.close(); } catch (Throwable ignored) {}
        }
    }
}
