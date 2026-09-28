package com.bachatas4.android.bridge;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.Intent;
import android.content.SharedPreferences;
import android.net.Uri;
import android.widget.Toast;
import kotlin.jvm.functions.Function1;

public final class ExternalStorageUi {
    private static final int REQUEST_TREE = 0x5341;
    private static Activity activity;
    private ExternalStorageUi() {}

    public static void attach(Activity a) { activity = a; }

    public static void dispatch(Function1 original, String label) {
        if ("Storage".equals(label)) { openDialog(); return; }
        original.invoke(label);
    }

    public static void openDialog() {
        final Activity a = activity;
        if (a == null) return;
        final SharedPreferences p = a.getSharedPreferences("pkg-extraction", 0);
        String current = p.getString("destination", null);
        String where = current == null || current.isEmpty() ? "App storage (default)" : current;
        new AlertDialog.Builder(a)
            .setTitle("PKG extraction location")
            .setMessage("Save newly extracted games to app storage or a folder on your device or SD card.\n\nCurrent: " + where)
            .setItems(new String[]{"Use app storage", "Choose folder"}, (d, which) -> {
                if (which == 0) {
                    p.edit().remove("destination").commit();
                    Toast.makeText(a, "PKG extraction: app storage", Toast.LENGTH_SHORT).show();
                } else {
                    Intent i = new Intent(Intent.ACTION_OPEN_DOCUMENT_TREE);
                    i.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION | Intent.FLAG_GRANT_WRITE_URI_PERMISSION |
                               Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION | Intent.FLAG_GRANT_PREFIX_URI_PERMISSION);
                    a.startActivityForResult(i, REQUEST_TREE);
                }
            }).show();
    }

    public static void onActivityResult(int requestCode, int resultCode, Intent data) {
        final Activity a = activity;
        if (a == null || requestCode != REQUEST_TREE || resultCode != Activity.RESULT_OK || data == null) return;
        Uri uri = data.getData();
        if (uri == null) return;
        int flags = data.getFlags() & (Intent.FLAG_GRANT_READ_URI_PERMISSION | Intent.FLAG_GRANT_WRITE_URI_PERMISSION);
        if (flags == 0) flags = Intent.FLAG_GRANT_READ_URI_PERMISSION | Intent.FLAG_GRANT_WRITE_URI_PERMISSION;
        try { a.getContentResolver().takePersistableUriPermission(uri, flags); } catch (Throwable ignored) {}
        a.getSharedPreferences("pkg-extraction", 0).edit().putString("destination", uri.toString()).commit();
        Toast.makeText(a, "PKG extraction folder selected", Toast.LENGTH_SHORT).show();
    }
}
