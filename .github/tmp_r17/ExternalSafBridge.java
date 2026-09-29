package com.bachatas4.android.bridge;

import java.io.File;

public final class ExternalSafBridge {
    private ExternalSafBridge() {}
    public static File iconPath(File filesDir, String relativePath) {
        return new File(filesDir, relativePath + "/sce_sys/icon0.png");
    }
}
