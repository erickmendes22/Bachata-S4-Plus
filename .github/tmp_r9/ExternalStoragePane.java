package com.bachatas4.android.bridge;

import android.app.Activity;
import android.content.Context;
import android.content.ContextWrapper;
import android.content.Intent;
import android.content.SharedPreferences;
import android.graphics.Color;
import android.graphics.Typeface;
import android.graphics.drawable.GradientDrawable;
import android.net.Uri;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;
import androidx.compose.runtime.Composer;
import androidx.compose.ui.Modifier;
import androidx.compose.ui.viewinterop.AndroidView_androidKt;
import kotlin.Unit;
import kotlin.jvm.functions.Function1;

public final class ExternalStoragePane {
    private static final int REQUEST_TREE = 0x5341;
    private static Activity activity;
    private static TextView currentView;

    private ExternalStoragePane() {}

    public static void attach(Activity a) { activity = a; }

    public static void Render(Modifier modifier, Composer composer, int changed) {
        AndroidView_androidKt.AndroidView(new Function1<Context, View>() {
            @Override public View invoke(Context context) {
                return build(context);
            }
        }, modifier, null, composer, 0x30, 0x4);
    }

    private static View build(Context context) {
        Activity a = activity != null ? activity : findActivity(context);
        if (a != null) activity = a;
        float d = context.getResources().getDisplayMetrics().density;
        LinearLayout root = new LinearLayout(context);
        root.setOrientation(LinearLayout.VERTICAL);
        root.setPadding((int)(24*d), (int)(18*d), (int)(24*d), (int)(24*d));
        root.setGravity(Gravity.TOP);

        TextView title = text(context, "PKG extraction location", 22, Color.WHITE, true);
        root.addView(title, lp(-1, -2, 0, 0, 0, 10, d));

        TextView desc = text(context, "Save newly extracted games to app storage or a folder on your device or SD card.", 15, Color.rgb(180,180,185), false);
        root.addView(desc, lp(-1, -2, 0, 0, 0, 22, d));

        currentView = text(context, currentLabel(context), 16, Color.rgb(235,235,238), true);
        root.addView(currentView, lp(-1, -2, 0, 0, 0, 18, d));

        TextView choose = action(context, "Choose folder", d);
        choose.setOnClickListener(v -> chooseFolder());
        root.addView(choose, lp(-1, (int)(58*d), 0, 0, 0, 14, d));

        TextView internal = action(context, "Use app storage", d);
        internal.setOnClickListener(v -> {
            context.getSharedPreferences("pkg-extraction", 0).edit().remove("destination").commit();
            refresh(context);
            Toast.makeText(context, "PKG extraction: app storage", Toast.LENGTH_SHORT).show();
        });
        root.addView(internal, lp(-1, (int)(58*d), 0, 0, 0, 0, d));
        return root;
    }

    private static TextView action(Context c, String s, float d) {
        TextView v = text(c, s, 17, Color.WHITE, true);
        v.setGravity(Gravity.CENTER_VERTICAL);
        v.setPadding((int)(20*d), 0, (int)(20*d), 0);
        GradientDrawable bg = new GradientDrawable();
        bg.setColor(Color.rgb(32,32,37));
        bg.setCornerRadius(14*d);
        bg.setStroke((int)(2*d), Color.rgb(226,162,60));
        v.setBackground(bg);
        v.setClickable(true);
        v.setFocusable(true);
        return v;
    }

    private static TextView text(Context c, String s, int sp, int color, boolean bold) {
        TextView v = new TextView(c);
        v.setText(s);
        v.setTextSize(sp);
        v.setTextColor(color);
        if (bold) v.setTypeface(Typeface.DEFAULT, Typeface.BOLD);
        return v;
    }

    private static LinearLayout.LayoutParams lp(int w, int h, int l, int t, int r, int b, float d) {
        LinearLayout.LayoutParams p = new LinearLayout.LayoutParams(w, h);
        p.setMargins((int)(l*d),(int)(t*d),(int)(r*d),(int)(b*d));
        return p;
    }

    private static void chooseFolder() {
        Activity a = activity;
        if (a == null) return;
        Intent i = new Intent(Intent.ACTION_OPEN_DOCUMENT_TREE);
        i.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION | Intent.FLAG_GRANT_WRITE_URI_PERMISSION |
                Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION | Intent.FLAG_GRANT_PREFIX_URI_PERMISSION);
        a.startActivityForResult(i, REQUEST_TREE);
    }

    public static void onActivityResult(int requestCode, int resultCode, Intent data) {
        Activity a = activity;
        if (a == null || requestCode != REQUEST_TREE || resultCode != Activity.RESULT_OK || data == null) return;
        Uri uri = data.getData();
        if (uri == null) return;
        int flags = data.getFlags() & (Intent.FLAG_GRANT_READ_URI_PERMISSION | Intent.FLAG_GRANT_WRITE_URI_PERMISSION);
        if (flags == 0) flags = Intent.FLAG_GRANT_READ_URI_PERMISSION | Intent.FLAG_GRANT_WRITE_URI_PERMISSION;
        try { a.getContentResolver().takePersistableUriPermission(uri, flags); }
        catch (Throwable t) { Toast.makeText(a, "Could not keep folder permission", Toast.LENGTH_SHORT).show(); return; }
        a.getSharedPreferences("pkg-extraction", 0).edit().putString("destination", uri.toString()).commit();
        refresh(a);
        Toast.makeText(a, "PKG extraction folder selected", Toast.LENGTH_SHORT).show();
    }

    private static void refresh(Context c) {
        TextView v = currentView;
        if (v != null) v.setText(currentLabel(c));
    }

    private static String currentLabel(Context c) {
        String u = c.getSharedPreferences("pkg-extraction", 0).getString("destination", null);
        if (u == null || u.isEmpty()) return "Current: App storage (default)";
        try {
            String last = Uri.decode(Uri.parse(u).getLastPathSegment());
            if (last != null) {
                int slash = last.lastIndexOf('/');
                if (slash >= 0 && slash + 1 < last.length()) last = last.substring(slash + 1);
                int colon = last.lastIndexOf(':');
                if (colon >= 0 && colon + 1 < last.length()) last = last.substring(colon + 1);
                if (!last.isEmpty()) return "Current: " + last;
            }
        } catch (Throwable ignored) {}
        return "Current: External folder selected";
    }

    private static Activity findActivity(Context c) {
        while (c instanceof ContextWrapper) {
            if (c instanceof Activity) return (Activity)c;
            c = ((ContextWrapper)c).getBaseContext();
        }
        return c instanceof Activity ? (Activity)c : null;
    }
}
