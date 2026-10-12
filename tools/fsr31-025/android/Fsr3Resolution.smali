.class public final Lcom/bachatas4/android/bridge/Fsr3Resolution;
.super Ljava/lang/Object;
.source "Fsr3Resolution.java"


# static fields
.field private static final CONTROLLED:Ljava/lang/String; = "fsr31_bb_controls_resolution"

.field private static final ENABLED:Ljava/util/regex/Pattern;

.field private static final META:Ljava/util/regex/Pattern;

.field private static final NAME:Ljava/util/regex/Pattern;

.field private static final PREFIX:Ljava/lang/String; = "Decoupled 1080p UI ("

.field private static final SAVED:Ljava/lang/String; = "fsr31_bb_original_resolution"

.field private static final SIZES:[Ljava/lang/String;


# direct methods
.method static constructor <clinit>()V
    .registers 5

    .line 41
    const-string v0, "960x540"

    const-string v1, "640x360"

    const/4 v2, 0x0

    const-string v3, "1280x720"

    const-string v4, "1152x648"

    filled-new-array {v2, v3, v4, v0, v1}, [Ljava/lang/String;

    move-result-object v0

    sput-object v0, Lcom/bachatas4/android/bridge/Fsr3Resolution;->SIZES:[Ljava/lang/String;

    .line 42
    const-string v0, "<Metadata\\b[^>]*>"

    const/16 v1, 0x20

    invoke-static {v0, v1}, Ljava/util/regex/Pattern;->compile(Ljava/lang/String;I)Ljava/util/regex/Pattern;

    move-result-object v0

    sput-object v0, Lcom/bachatas4/android/bridge/Fsr3Resolution;->META:Ljava/util/regex/Pattern;

    .line 43
    const-string v0, "\\bName=\"([^\"]+)\""

    invoke-static {v0}, Ljava/util/regex/Pattern;->compile(Ljava/lang/String;)Ljava/util/regex/Pattern;

    move-result-object v0

    sput-object v0, Lcom/bachatas4/android/bridge/Fsr3Resolution;->NAME:Ljava/util/regex/Pattern;

    .line 44
    const-string v0, "\\bisEnabled=\"(?:true|false)\""

    invoke-static {v0}, Ljava/util/regex/Pattern;->compile(Ljava/lang/String;)Ljava/util/regex/Pattern;

    move-result-object v0

    sput-object v0, Lcom/bachatas4/android/bridge/Fsr3Resolution;->ENABLED:Ljava/util/regex/Pattern;

    return-void
.end method

.method public constructor <init>()V
    .registers 1

    .line 22
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method

.method public static declared-synchronized apply(Landroid/content/Context;ZI)V
    .registers 19

    move-object/from16 v0, p0

    move/from16 v1, p2

    const-class v2, Lcom/bachatas4/android/bridge/Fsr3Resolution;

    monitor-enter v2

    .line 58
    if-eqz v0, :cond_211

    if-ltz v1, :cond_211

    const/4 v3, 0x4

    if-le v1, v3, :cond_10

    goto/16 :goto_211

    .line 59
    :cond_10
    :try_start_10
    const-string v3, "bs4_fsr31"

    const/4 v4, 0x0

    invoke-virtual {v0, v3, v4}, Landroid/content/Context;->getSharedPreferences(Ljava/lang/String;I)Landroid/content/SharedPreferences;

    move-result-object v3
    :try_end_17
    .catchall {:try_start_10 .. :try_end_17} :catchall_20e

    .line 61
    :try_start_17
    new-instance v5, Ljava/io/File;

    invoke-virtual {v0}, Landroid/content/Context;->getFilesDir()Ljava/io/File;

    move-result-object v6

    new-instance v7, Ljava/lang/StringBuilder;

    invoke-direct {v7}, Ljava/lang/StringBuilder;-><init>()V

    const-string v8, "runtime/"

    invoke-virtual {v7, v8}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v7

    invoke-static {v0}, Lcom/bachatas4/android/bridge/Fsr3Resolution;->installedRuntimeName(Landroid/content/Context;)Ljava/lang/String;

    move-result-object v0

    invoke-virtual {v7, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    const-string v7, "/user/patches/bachata-official/Bloodborne.xml"

    invoke-virtual {v0, v7}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    invoke-direct {v5, v6, v0}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    .line 63
    invoke-virtual {v5}, Ljava/io/File;->isFile()Z

    move-result v0

    if-nez v0, :cond_5d

    .line 64
    const-string v0, "BS4_FSR31"

    new-instance v1, Ljava/lang/StringBuilder;

    invoke-direct {v1}, Ljava/lang/StringBuilder;-><init>()V

    const-string v3, "Installed runtime patch file is absent: "

    invoke-virtual {v1, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1, v5}, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v1

    invoke-static {v0, v1}, Landroid/util/Log;->e(Ljava/lang/String;Ljava/lang/String;)I
    :try_end_5b
    .catch Ljava/lang/Exception; {:try_start_17 .. :try_end_5b} :catch_204
    .catchall {:try_start_17 .. :try_end_5b} :catchall_20e

    .line 65
    monitor-exit v2

    return-void

    .line 67
    :cond_5d
    :try_start_5d
    new-instance v0, Ljava/lang/String;

    invoke-virtual {v5}, Ljava/io/File;->toPath()Ljava/nio/file/Path;

    move-result-object v6

    invoke-static {v6}, Ljava/nio/file/Files;->readAllBytes(Ljava/nio/file/Path;)[B

    move-result-object v6

    sget-object v7, Ljava/nio/charset/StandardCharsets;->UTF_8:Ljava/nio/charset/Charset;

    invoke-direct {v0, v6, v7}, Ljava/lang/String;-><init>([BLjava/nio/charset/Charset;)V

    .line 68
    const-string v6, "<ID>CUSA00900</ID>"

    invoke-virtual {v0, v6}, Ljava/lang/String;->contains(Ljava/lang/CharSequence;)Z

    move-result v6
    :try_end_72
    .catch Ljava/lang/Exception; {:try_start_5d .. :try_end_72} :catch_204
    .catchall {:try_start_5d .. :try_end_72} :catchall_20e

    if-nez v6, :cond_76

    monitor-exit v2

    return-void

    .line 69
    :cond_76
    :try_start_76
    const-string v6, "fsr31_bb_controls_resolution"

    invoke-interface {v3, v6, v4}, Landroid/content/SharedPreferences;->getBoolean(Ljava/lang/String;Z)Z

    move-result v6

    .line 70
    const/4 v7, 0x1

    if-eqz p1, :cond_bf

    if-nez v6, :cond_bf

    .line 71
    new-instance v8, Ljava/util/HashSet;

    invoke-direct {v8}, Ljava/util/HashSet;-><init>()V

    .line 72
    sget-object v9, Lcom/bachatas4/android/bridge/Fsr3Resolution;->META:Ljava/util/regex/Pattern;

    invoke-virtual {v9, v0}, Ljava/util/regex/Pattern;->matcher(Ljava/lang/CharSequence;)Ljava/util/regex/Matcher;

    move-result-object v9

    .line 73
    :goto_8c
    invoke-virtual {v9}, Ljava/util/regex/Matcher;->find()Z

    move-result v10

    if-eqz v10, :cond_ac

    .line 74
    invoke-virtual {v9}, Ljava/util/regex/Matcher;->group()Ljava/lang/String;

    move-result-object v10

    invoke-static {v10}, Lcom/bachatas4/android/bridge/Fsr3Resolution;->name(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v11

    .line 75
    const-string v12, "Resolution Patch "

    invoke-virtual {v11, v12}, Ljava/lang/String;->startsWith(Ljava/lang/String;)Z

    move-result v12

    if-eqz v12, :cond_ab

    invoke-static {v10}, Lcom/bachatas4/android/bridge/Fsr3Resolution;->isEnabled(Ljava/lang/String;)Z

    move-result v10

    if-eqz v10, :cond_ab

    invoke-interface {v8, v11}, Ljava/util/Set;->add(Ljava/lang/Object;)Z

    .line 76
    :cond_ab
    goto :goto_8c

    .line 77
    :cond_ac
    invoke-interface {v3}, Landroid/content/SharedPreferences;->edit()Landroid/content/SharedPreferences$Editor;

    move-result-object v9

    const-string v10, "fsr31_bb_original_resolution"

    invoke-interface {v9, v10, v8}, Landroid/content/SharedPreferences$Editor;->putStringSet(Ljava/lang/String;Ljava/util/Set;)Landroid/content/SharedPreferences$Editor;

    move-result-object v8

    const-string v9, "fsr31_bb_controls_resolution"

    invoke-interface {v8, v9, v7}, Landroid/content/SharedPreferences$Editor;->putBoolean(Ljava/lang/String;Z)Landroid/content/SharedPreferences$Editor;

    move-result-object v8

    invoke-interface {v8}, Landroid/content/SharedPreferences$Editor;->apply()V

    .line 79
    :cond_bf
    const-string v8, "fsr31_bb_original_resolution"

    invoke-static {}, Ljava/util/Collections;->emptySet()Ljava/util/Set;

    move-result-object v9

    invoke-interface {v3, v8, v9}, Landroid/content/SharedPreferences;->getStringSet(Ljava/lang/String;Ljava/util/Set;)Ljava/util/Set;

    move-result-object v8

    .line 80
    if-nez p1, :cond_cf

    if-eqz v6, :cond_cf

    move v6, v7

    goto :goto_d0

    :cond_cf
    move v6, v4

    .line 81
    :goto_d0
    if-eqz p1, :cond_f2

    if-lez v1, :cond_f2

    .line 82
    new-instance v9, Ljava/lang/StringBuilder;

    invoke-direct {v9}, Ljava/lang/StringBuilder;-><init>()V

    const-string v10, "Decoupled 1080p UI ("

    invoke-virtual {v9, v10}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v9

    sget-object v10, Lcom/bachatas4/android/bridge/Fsr3Resolution;->SIZES:[Ljava/lang/String;

    aget-object v10, v10, v1

    invoke-virtual {v9, v10}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v9

    const-string v10, " render res)"

    invoke-virtual {v9, v10}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v9

    invoke-virtual {v9}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v9

    goto :goto_f4

    :cond_f2
    const-string v9, ""

    .line 83
    :goto_f4
    new-instance v10, Ljava/lang/StringBuffer;

    invoke-virtual {v0}, Ljava/lang/String;->length()I

    move-result v11

    add-int/lit16 v11, v11, 0x100

    invoke-direct {v10, v11}, Ljava/lang/StringBuffer;-><init>(I)V

    .line 84
    sget-object v11, Lcom/bachatas4/android/bridge/Fsr3Resolution;->META:Ljava/util/regex/Pattern;

    invoke-virtual {v11, v0}, Ljava/util/regex/Pattern;->matcher(Ljava/lang/CharSequence;)Ljava/util/regex/Matcher;

    move-result-object v0

    .line 85
    move v11, v4

    move v12, v11

    .line 86
    :goto_107
    invoke-virtual {v0}, Ljava/util/regex/Matcher;->find()Z

    move-result v13

    if-eqz v13, :cond_164

    .line 87
    invoke-virtual {v0}, Ljava/util/regex/Matcher;->group()Ljava/lang/String;

    move-result-object v13

    invoke-static {v13}, Lcom/bachatas4/android/bridge/Fsr3Resolution;->name(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v14

    .line 88
    const-string v15, "Decoupled 1080p UI ("

    invoke-virtual {v14, v15}, Ljava/lang/String;->startsWith(Ljava/lang/String;)Z

    move-result v15

    if-eqz v15, :cond_139

    .line 89
    invoke-virtual {v14, v9}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v15

    if-eqz v15, :cond_125

    add-int/lit8 v11, v11, 0x1

    .line 90
    :cond_125
    invoke-virtual {v9}, Ljava/lang/String;->isEmpty()Z

    move-result v15

    if-nez v15, :cond_133

    invoke-virtual {v14, v9}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v14

    if-eqz v14, :cond_133

    move v14, v7

    goto :goto_134

    :cond_133
    move v14, v4

    :goto_134
    invoke-static {v13, v14}, Lcom/bachatas4/android/bridge/Fsr3Resolution;->toggle(Ljava/lang/String;Z)Ljava/lang/String;

    move-result-object v14

    goto :goto_154

    .line 91
    :cond_139
    const-string v15, "Resolution Patch "

    invoke-virtual {v14, v15}, Ljava/lang/String;->startsWith(Ljava/lang/String;)Z

    move-result v15

    if-eqz v15, :cond_153

    .line 92
    if-eqz p1, :cond_148

    invoke-static {v13, v4}, Lcom/bachatas4/android/bridge/Fsr3Resolution;->toggle(Ljava/lang/String;Z)Ljava/lang/String;

    move-result-object v14

    goto :goto_154

    .line 93
    :cond_148
    if-eqz v6, :cond_153

    invoke-interface {v8, v14}, Ljava/util/Set;->contains(Ljava/lang/Object;)Z

    move-result v14

    invoke-static {v13, v14}, Lcom/bachatas4/android/bridge/Fsr3Resolution;->toggle(Ljava/lang/String;Z)Ljava/lang/String;

    move-result-object v14

    goto :goto_154

    .line 95
    :cond_153
    move-object v14, v13

    :goto_154
    invoke-virtual {v14, v13}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result v13

    if-nez v13, :cond_15c

    add-int/lit8 v12, v12, 0x1

    .line 96
    :cond_15c
    invoke-static {v14}, Ljava/util/regex/Matcher;->quoteReplacement(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v13

    invoke-virtual {v0, v10, v13}, Ljava/util/regex/Matcher;->appendReplacement(Ljava/lang/StringBuffer;Ljava/lang/String;)Ljava/util/regex/Matcher;

    .line 97
    goto :goto_107

    .line 98
    :cond_164
    invoke-virtual {v0, v10}, Ljava/util/regex/Matcher;->appendTail(Ljava/lang/StringBuffer;)Ljava/lang/StringBuffer;

    .line 99
    invoke-virtual {v9}, Ljava/lang/String;->isEmpty()Z

    move-result v0

    if-nez v0, :cond_189

    if-eq v11, v7, :cond_189

    .line 100
    const-string v0, "BS4_FSR31"

    new-instance v1, Ljava/lang/StringBuilder;

    invoke-direct {v1}, Ljava/lang/StringBuilder;-><init>()V

    const-string v3, "Internal patch missing: "

    invoke-virtual {v1, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1, v9}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v1

    invoke-static {v0, v1}, Landroid/util/Log;->e(Ljava/lang/String;Ljava/lang/String;)I
    :try_end_187
    .catch Ljava/lang/Exception; {:try_start_76 .. :try_end_187} :catch_204
    .catchall {:try_start_76 .. :try_end_187} :catchall_20e

    monitor-exit v2

    return-void

    .line 102
    :cond_189
    if-lez v12, :cond_1bf

    .line 103
    :try_start_18b
    new-instance v0, Ljava/io/File;

    invoke-virtual {v5}, Ljava/io/File;->getParentFile()Ljava/io/File;

    move-result-object v8

    const-string v11, "Bloodborne.xml.fsr31.tmp"

    invoke-direct {v0, v8, v11}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    .line 104
    invoke-virtual {v0}, Ljava/io/File;->toPath()Ljava/nio/file/Path;

    move-result-object v8

    invoke-virtual {v10}, Ljava/lang/StringBuffer;->toString()Ljava/lang/String;

    move-result-object v10

    sget-object v11, Ljava/nio/charset/StandardCharsets;->UTF_8:Ljava/nio/charset/Charset;

    invoke-virtual {v10, v11}, Ljava/lang/String;->getBytes(Ljava/nio/charset/Charset;)[B

    move-result-object v10

    new-array v11, v4, [Ljava/nio/file/OpenOption;

    invoke-static {v8, v10, v11}, Ljava/nio/file/Files;->write(Ljava/nio/file/Path;[B[Ljava/nio/file/OpenOption;)Ljava/nio/file/Path;

    .line 105
    invoke-virtual {v0}, Ljava/io/File;->toPath()Ljava/nio/file/Path;

    move-result-object v0

    invoke-virtual {v5}, Ljava/io/File;->toPath()Ljava/nio/file/Path;

    move-result-object v5

    const/4 v8, 0x2

    new-array v8, v8, [Ljava/nio/file/CopyOption;

    sget-object v10, Ljava/nio/file/StandardCopyOption;->REPLACE_EXISTING:Ljava/nio/file/StandardCopyOption;

    aput-object v10, v8, v4

    sget-object v10, Ljava/nio/file/StandardCopyOption;->ATOMIC_MOVE:Ljava/nio/file/StandardCopyOption;

    aput-object v10, v8, v7

    invoke-static {v0, v5, v8}, Ljava/nio/file/Files;->move(Ljava/nio/file/Path;Ljava/nio/file/Path;[Ljava/nio/file/CopyOption;)Ljava/nio/file/Path;

    .line 108
    :cond_1bf
    if-eqz v6, :cond_1d4

    invoke-interface {v3}, Landroid/content/SharedPreferences;->edit()Landroid/content/SharedPreferences$Editor;

    move-result-object v0

    const-string v3, "fsr31_bb_original_resolution"

    invoke-interface {v0, v3}, Landroid/content/SharedPreferences$Editor;->remove(Ljava/lang/String;)Landroid/content/SharedPreferences$Editor;

    move-result-object v0

    const-string v3, "fsr31_bb_controls_resolution"

    invoke-interface {v0, v3, v4}, Landroid/content/SharedPreferences$Editor;->putBoolean(Ljava/lang/String;Z)Landroid/content/SharedPreferences$Editor;

    move-result-object v0

    invoke-interface {v0}, Landroid/content/SharedPreferences$Editor;->apply()V

    .line 109
    :cond_1d4
    const-string v0, "BS4_FSR31"

    new-instance v3, Ljava/lang/StringBuilder;

    invoke-direct {v3}, Ljava/lang/StringBuilder;-><init>()V

    const-string v4, "Bloodborne game-native scene="

    invoke-virtual {v3, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v3

    .line 110
    invoke-virtual {v9}, Ljava/lang/String;->isEmpty()Z

    move-result v4

    if-eqz v4, :cond_1ea

    const-string v1, "original"

    goto :goto_1ee

    :cond_1ea
    sget-object v4, Lcom/bachatas4/android/bridge/Fsr3Resolution;->SIZES:[Ljava/lang/String;

    aget-object v1, v4, v1

    :goto_1ee
    invoke-virtual {v3, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    const-string v3, " UI=1920x1080 edits="

    invoke-virtual {v1, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1, v12}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v1

    .line 109
    invoke-static {v0, v1}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I
    :try_end_203
    .catch Ljava/lang/Exception; {:try_start_18b .. :try_end_203} :catch_204
    .catchall {:try_start_18b .. :try_end_203} :catchall_20e

    .line 113
    goto :goto_20c

    .line 111
    :catch_204
    move-exception v0

    .line 112
    :try_start_205
    const-string v1, "BS4_FSR31"

    const-string v3, "Cannot set game-native render resolution"

    invoke-static {v1, v3, v0}, Landroid/util/Log;->e(Ljava/lang/String;Ljava/lang/String;Ljava/lang/Throwable;)I
    :try_end_20c
    .catchall {:try_start_205 .. :try_end_20c} :catchall_20e

    .line 114
    :goto_20c
    monitor-exit v2

    return-void

    .line 57
    :catchall_20e
    move-exception v0

    :try_start_20f
    monitor-exit v2
    :try_end_210
    .catchall {:try_start_20f .. :try_end_210} :catchall_20e

    throw v0

    .line 58
    :cond_211
    :goto_211
    monitor-exit v2

    return-void
.end method

.method private static installedRuntimeName(Landroid/content/Context;)Ljava/lang/String;
    .registers 6
    .annotation system Ldalvik/annotation/Throws;
        value = {
            Ljava/lang/Exception;
        }
    .end annotation

    .line 26
    invoke-virtual {p0}, Landroid/content/Context;->getAssets()Landroid/content/res/AssetManager;

    move-result-object p0

    const-string v0, "runtime/manifest.json"

    invoke-virtual {p0, v0}, Landroid/content/res/AssetManager;->open(Ljava/lang/String;)Ljava/io/InputStream;

    move-result-object p0

    .line 27
    :try_start_a
    new-instance v0, Ljava/io/ByteArrayOutputStream;

    invoke-direct {v0}, Ljava/io/ByteArrayOutputStream;-><init>()V
    :try_end_f
    .catchall {:try_start_a .. :try_end_f} :catchall_58

    .line 28
    const/16 v1, 0x2000

    :try_start_11
    new-array v1, v1, [B

    .line 29
    :goto_13
    invoke-virtual {p0, v1}, Ljava/io/InputStream;->read([B)I

    move-result v2

    if-lez v2, :cond_1e

    const/4 v3, 0x0

    invoke-virtual {v0, v1, v3, v2}, Ljava/io/ByteArrayOutputStream;->write([BII)V

    goto :goto_13

    .line 30
    :cond_1e
    new-instance v1, Lorg/json/JSONObject;

    new-instance v2, Ljava/lang/String;

    .line 31
    invoke-virtual {v0}, Ljava/io/ByteArrayOutputStream;->toByteArray()[B

    move-result-object v3

    sget-object v4, Ljava/nio/charset/StandardCharsets;->UTF_8:Ljava/nio/charset/Charset;

    invoke-direct {v2, v3, v4}, Ljava/lang/String;-><init>([BLjava/nio/charset/Charset;)V

    invoke-direct {v1, v2}, Lorg/json/JSONObject;-><init>(Ljava/lang/String;)V

    const-string v2, "runtimeVersion"

    .line 32
    invoke-virtual {v1, v2}, Lorg/json/JSONObject;->getString(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v1

    .line 33
    const-string v2, "bachata-s4-(?:plus|r[0-9]{3})-0\\.2\\.6-[a-zA-Z0-9]+"

    invoke-virtual {v1, v2}, Ljava/lang/String;->matches(Ljava/lang/String;)Z

    move-result v2
    :try_end_3a
    .catchall {:try_start_11 .. :try_end_3a} :catchall_4e

    if-eqz v2, :cond_46

    .line 35
    nop

    .line 36
    :try_start_3d
    invoke-virtual {v0}, Ljava/io/ByteArrayOutputStream;->close()V
    :try_end_40
    .catchall {:try_start_3d .. :try_end_40} :catchall_58

    if-eqz p0, :cond_45

    invoke-virtual {p0}, Ljava/io/InputStream;->close()V

    .line 35
    :cond_45
    return-object v1

    .line 34
    :cond_46
    :try_start_46
    new-instance v1, Ljava/lang/IllegalStateException;

    const-string v2, "Unrecognized BACHATA runtime name"

    invoke-direct {v1, v2}, Ljava/lang/IllegalStateException;-><init>(Ljava/lang/String;)V

    throw v1
    :try_end_4e
    .catchall {:try_start_46 .. :try_end_4e} :catchall_4e

    .line 26
    :catchall_4e
    move-exception v1

    :try_start_4f
    invoke-virtual {v0}, Ljava/io/ByteArrayOutputStream;->close()V
    :try_end_52
    .catchall {:try_start_4f .. :try_end_52} :catchall_53

    goto :goto_57

    :catchall_53
    move-exception v0

    :try_start_54
    invoke-virtual {v1, v0}, Ljava/lang/Throwable;->addSuppressed(Ljava/lang/Throwable;)V

    :goto_57
    throw v1
    :try_end_58
    .catchall {:try_start_54 .. :try_end_58} :catchall_58

    :catchall_58
    move-exception v0

    if-eqz p0, :cond_63

    :try_start_5b
    invoke-virtual {p0}, Ljava/io/InputStream;->close()V
    :try_end_5e
    .catchall {:try_start_5b .. :try_end_5e} :catchall_5f

    goto :goto_63

    :catchall_5f
    move-exception p0

    invoke-virtual {v0, p0}, Ljava/lang/Throwable;->addSuppressed(Ljava/lang/Throwable;)V

    :cond_63
    :goto_63
    throw v0
.end method

.method private static isEnabled(Ljava/lang/String;)Z
    .registers 2

    .line 50
    const-string v0, "isEnabled=\"true\""

    invoke-virtual {p0, v0}, Ljava/lang/String;->contains(Ljava/lang/CharSequence;)Z

    move-result p0

    return p0
.end method

.method private static name(Ljava/lang/String;)Ljava/lang/String;
    .registers 2

    .line 46
    sget-object v0, Lcom/bachatas4/android/bridge/Fsr3Resolution;->NAME:Ljava/util/regex/Pattern;

    invoke-virtual {v0, p0}, Ljava/util/regex/Pattern;->matcher(Ljava/lang/CharSequence;)Ljava/util/regex/Matcher;

    move-result-object p0

    .line 47
    invoke-virtual {p0}, Ljava/util/regex/Matcher;->find()Z

    move-result v0

    if-eqz v0, :cond_12

    const/4 v0, 0x1

    invoke-virtual {p0, v0}, Ljava/util/regex/Matcher;->group(I)Ljava/lang/String;

    move-result-object p0

    goto :goto_14

    :cond_12
    const-string p0, ""

    :goto_14
    return-object p0
.end method

.method private static toggle(Ljava/lang/String;Z)Ljava/lang/String;
    .registers 5

    .line 53
    sget-object v0, Lcom/bachatas4/android/bridge/Fsr3Resolution;->ENABLED:Ljava/util/regex/Pattern;

    invoke-virtual {v0, p0}, Ljava/util/regex/Pattern;->matcher(Ljava/lang/CharSequence;)Ljava/util/regex/Matcher;

    move-result-object v0

    .line 54
    invoke-virtual {v0}, Ljava/util/regex/Matcher;->find()Z

    move-result v1

    if-eqz v1, :cond_2a

    new-instance p0, Ljava/lang/StringBuilder;

    invoke-direct {p0}, Ljava/lang/StringBuilder;-><init>()V

    const-string v1, "isEnabled=\""

    invoke-virtual {p0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p0

    invoke-virtual {p0, p1}, Ljava/lang/StringBuilder;->append(Z)Ljava/lang/StringBuilder;

    move-result-object p0

    const-string p1, "\""

    invoke-virtual {p0, p1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p0

    invoke-virtual {p0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p0

    invoke-virtual {v0, p0}, Ljava/util/regex/Matcher;->replaceFirst(Ljava/lang/String;)Ljava/lang/String;

    move-result-object p0

    return-object p0

    .line 55
    :cond_2a
    new-instance v0, Ljava/lang/StringBuilder;

    invoke-direct {v0}, Ljava/lang/StringBuilder;-><init>()V

    invoke-virtual {p0}, Ljava/lang/String;->length()I

    move-result v1

    add-int/lit8 v1, v1, -0x1

    const/4 v2, 0x0

    invoke-virtual {p0, v2, v1}, Ljava/lang/String;->substring(II)Ljava/lang/String;

    move-result-object p0

    invoke-virtual {v0, p0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p0

    const-string v0, " isEnabled=\""

    invoke-virtual {p0, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p0

    invoke-virtual {p0, p1}, Ljava/lang/StringBuilder;->append(Z)Ljava/lang/StringBuilder;

    move-result-object p0

    const-string p1, "\">"

    invoke-virtual {p0, p1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p0

    invoke-virtual {p0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p0

    return-object p0
.end method
