.class public final Lcom/bachatas4/android/bridge/Fsr3Ui;
.super Ljava/lang/Object;
.source "Fsr3Ui.java"


# static fields
.field private static final MODES:[Ljava/lang/String;

.field private static final PREF:Ljava/lang/String; = "bs4_fsr31"

.field private static volatile appContext:Landroid/content/Context;


# direct methods
.method static constructor <clinit>()V
    .registers 5

    .line 41
    const-string v0, "Performance"

    const-string v1, "Ultra Performance"

    const-string v2, "Native AA"

    const-string v3, "Quality"

    const-string v4, "Balanced"

    filled-new-array {v2, v3, v4, v0, v1}, [Ljava/lang/String;

    move-result-object v0

    sput-object v0, Lcom/bachatas4/android/bridge/Fsr3Ui;->MODES:[Ljava/lang/String;

    return-void
.end method

.method public constructor <init>()V
    .registers 1

    .line 13
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method

.method public static attach(Landroid/app/Activity;)V
    .registers 9

    .line 50
    invoke-virtual {p0}, Landroid/app/Activity;->getApplicationContext()Landroid/content/Context;

    move-result-object v0

    sput-object v0, Lcom/bachatas4/android/bridge/Fsr3Ui;->appContext:Landroid/content/Context;

    .line 51
    invoke-virtual {p0}, Landroid/app/Activity;->getWindow()Landroid/view/Window;

    move-result-object v0

    invoke-virtual {v0}, Landroid/view/Window;->getDecorView()Landroid/view/View;

    move-result-object v0

    const v1, 0x1020002

    invoke-virtual {v0, v1}, Landroid/view/View;->findViewById(I)Landroid/view/View;

    move-result-object v0

    .line 52
    instance-of v1, v0, Landroid/widget/FrameLayout;

    if-nez v1, :cond_1a

    return-void

    .line 53
    :cond_1a
    check-cast v0, Landroid/widget/FrameLayout;

    .line 54
    const-string v1, "bs4_fsr31"

    const/4 v2, 0x0

    invoke-virtual {p0, v1, v2}, Landroid/app/Activity;->getSharedPreferences(Ljava/lang/String;I)Landroid/content/SharedPreferences;

    move-result-object v1

    .line 55
    new-instance v3, Landroid/widget/Button;

    invoke-direct {v3, p0}, Landroid/widget/Button;-><init>(Landroid/content/Context;)V

    .line 56
    invoke-virtual {v3, v2}, Landroid/widget/Button;->setAllCaps(Z)V

    .line 57
    const/4 v4, -0x1

    invoke-virtual {v3, v4}, Landroid/widget/Button;->setTextColor(I)V

    .line 58
    const/high16 v4, 0x41400000    # 12.0f

    invoke-virtual {v3, v4}, Landroid/widget/Button;->setTextSize(F)V

    .line 59
    invoke-static {v3, v1}, Lcom/bachatas4/android/bridge/Fsr3Ui;->refresh(Landroid/widget/Button;Landroid/content/SharedPreferences;)V

    .line 60
    new-instance v4, Landroid/widget/FrameLayout$LayoutParams;

    const/16 v5, 0x2a

    invoke-static {p0, v5}, Lcom/bachatas4/android/bridge/Fsr3Ui;->px(Landroid/app/Activity;I)I

    move-result v5

    const v6, 0x800035

    const/4 v7, -0x2

    invoke-direct {v4, v7, v5, v6}, Landroid/widget/FrameLayout$LayoutParams;-><init>(III)V

    .line 61
    const/16 v5, 0x36

    invoke-static {p0, v5}, Lcom/bachatas4/android/bridge/Fsr3Ui;->px(Landroid/app/Activity;I)I

    move-result v5

    const/16 v6, 0xa

    invoke-static {p0, v6}, Lcom/bachatas4/android/bridge/Fsr3Ui;->px(Landroid/app/Activity;I)I

    move-result v6

    invoke-virtual {v4, v2, v5, v6, v2}, Landroid/widget/FrameLayout$LayoutParams;->setMargins(IIII)V

    .line 62
    invoke-virtual {v0, v3, v4}, Landroid/widget/FrameLayout;->addView(Landroid/view/View;Landroid/view/ViewGroup$LayoutParams;)V

    .line 63
    new-instance v0, Lcom/bachatas4/android/bridge/Fsr3Ui$1;

    invoke-direct {v0, v1, p0, v3}, Lcom/bachatas4/android/bridge/Fsr3Ui$1;-><init>(Landroid/content/SharedPreferences;Landroid/app/Activity;Landroid/widget/Button;)V

    invoke-virtual {v3, v0}, Landroid/widget/Button;->setOnClickListener(Landroid/view/View$OnClickListener;)V

    .line 74
    return-void
.end method

.method public static enrichEnvironment(Landroid/content/Context;Ljava/util/Map;)V
    .registers 7
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "(",
            "Landroid/content/Context;",
            "Ljava/util/Map<",
            "Ljava/lang/String;",
            "Ljava/lang/String;",
            ">;)V"
        }
    .end annotation

    .line 17
    if-eqz p0, :cond_83

    if-nez p1, :cond_6

    goto/16 :goto_83

    .line 18
    :cond_6
    const-string v0, "bs4_fsr31"

    const/4 v1, 0x0

    invoke-virtual {p0, v0, v1}, Landroid/content/Context;->getSharedPreferences(Ljava/lang/String;I)Landroid/content/SharedPreferences;

    move-result-object v0

    .line 19
    const-string v2, "preset"

    const/4 v3, 0x1

    invoke-interface {v0, v2, v3}, Landroid/content/SharedPreferences;->getInt(Ljava/lang/String;I)I

    move-result v2

    .line 20
    if-ltz v2, :cond_1b

    const/4 v4, 0x4

    if-le v2, v4, :cond_1a

    goto :goto_1b

    :cond_1a
    move v3, v2

    .line 21
    :cond_1b
    :goto_1b
    const-string v2, "enabled"

    invoke-interface {v0, v2, v1}, Landroid/content/SharedPreferences;->getBoolean(Ljava/lang/String;Z)Z

    move-result v0

    .line 22
    if-eqz v0, :cond_28

    invoke-static {v3}, Ljava/lang/Integer;->toString(I)Ljava/lang/String;

    move-result-object v1

    goto :goto_2a

    :cond_28
    const-string v1, "-1"

    :goto_2a
    const-string v2, "BACHATA_FSR31_MODE"

    invoke-interface {p1, v2, v1}, Ljava/util/Map;->put(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;

    .line 26
    invoke-static {p0, v0, v3}, Lcom/bachatas4/android/bridge/Fsr3Resolution;->apply(Landroid/content/Context;ZI)V

    .line 30
    if-eqz v0, :cond_82

    .line 31
    const-string v0, "LD_PRELOAD"

    invoke-interface {p1, v0}, Ljava/util/Map;->get(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v1

    check-cast v1, Ljava/lang/String;

    .line 32
    new-instance v2, Ljava/lang/StringBuilder;

    invoke-direct {v2}, Ljava/lang/StringBuilder;-><init>()V

    invoke-virtual {p0}, Landroid/content/Context;->getApplicationInfo()Landroid/content/pm/ApplicationInfo;

    move-result-object p0

    iget-object p0, p0, Landroid/content/pm/ApplicationInfo;->nativeLibraryDir:Ljava/lang/String;

    invoke-virtual {v2, p0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p0

    const-string v2, "/libbachata_fsr31.so"

    invoke-virtual {p0, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p0

    invoke-virtual {p0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p0

    .line 33
    if-eqz v1, :cond_7f

    invoke-virtual {v1}, Ljava/lang/String;->isEmpty()Z

    move-result v2

    if-eqz v2, :cond_5e

    goto :goto_7f

    .line 34
    :cond_5e
    invoke-virtual {v1, p0}, Ljava/lang/String;->contains(Ljava/lang/CharSequence;)Z

    move-result v2

    if-nez v2, :cond_82

    new-instance v2, Ljava/lang/StringBuilder;

    invoke-direct {v2}, Ljava/lang/StringBuilder;-><init>()V

    invoke-virtual {v2, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    const-string v2, " "

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1, p0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p0

    invoke-virtual {p0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p0

    invoke-interface {p1, v0, p0}, Ljava/util/Map;->put(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;

    goto :goto_82

    .line 33
    :cond_7f
    :goto_7f
    invoke-interface {p1, v0, p0}, Ljava/util/Map;->put(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;

    .line 36
    :cond_82
    :goto_82
    return-void

    .line 17
    :cond_83
    :goto_83
    return-void
.end method

.method public static enrichProcessEnvironment(Ljava/util/Map;)V
    .registers 2
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "(",
            "Ljava/util/Map<",
            "Ljava/lang/String;",
            "Ljava/lang/String;",
            ">;)V"
        }
    .end annotation

    .line 38
    sget-object v0, Lcom/bachatas4/android/bridge/Fsr3Ui;->appContext:Landroid/content/Context;

    invoke-static {v0, p0}, Lcom/bachatas4/android/bridge/Fsr3Ui;->enrichEnvironment(Landroid/content/Context;Ljava/util/Map;)V

    .line 39
    return-void
.end method

.method static synthetic lambda$attach$0(Landroid/content/SharedPreferences;Landroid/widget/Button;Landroid/app/Activity;Landroid/content/DialogInterface;I)V
    .registers 9

    .line 67
    invoke-interface {p0}, Landroid/content/SharedPreferences;->edit()Landroid/content/SharedPreferences$Editor;

    move-result-object v0

    const/4 v1, 0x1

    if-ne p4, v1, :cond_9

    move v2, v1

    goto :goto_a

    :cond_9
    const/4 v2, 0x0

    :goto_a
    const-string v3, "enabled"

    invoke-interface {v0, v3, v2}, Landroid/content/SharedPreferences$Editor;->putBoolean(Ljava/lang/String;Z)Landroid/content/SharedPreferences$Editor;

    move-result-object v0

    invoke-interface {v0}, Landroid/content/SharedPreferences$Editor;->apply()V

    .line 68
    invoke-interface {p3}, Landroid/content/DialogInterface;->dismiss()V

    .line 69
    invoke-static {p1, p0}, Lcom/bachatas4/android/bridge/Fsr3Ui;->refresh(Landroid/widget/Button;Landroid/content/SharedPreferences;)V

    .line 70
    if-ne p4, v1, :cond_1e

    invoke-static {p2, p1, p0}, Lcom/bachatas4/android/bridge/Fsr3Ui;->showModes(Landroid/app/Activity;Landroid/widget/Button;Landroid/content/SharedPreferences;)V

    .line 71
    :cond_1e
    return-void
.end method

.method static synthetic lambda$attach$1(Landroid/app/Activity;Landroid/widget/Button;Landroid/content/SharedPreferences;Landroid/content/DialogInterface;I)V
    .registers 5

    .line 71
    invoke-static {p0, p1, p2}, Lcom/bachatas4/android/bridge/Fsr3Ui;->showModes(Landroid/app/Activity;Landroid/widget/Button;Landroid/content/SharedPreferences;)V

    return-void
.end method

.method static synthetic lambda$attach$2(Landroid/content/SharedPreferences;Landroid/app/Activity;Landroid/widget/Button;Landroid/view/View;)V
    .registers 8

    .line 64
    const-string p3, "enabled"

    const/4 v0, 0x0

    invoke-interface {p0, p3, v0}, Landroid/content/SharedPreferences;->getBoolean(Ljava/lang/String;Z)Z

    move-result p3

    .line 65
    new-instance v1, Landroid/app/AlertDialog$Builder;

    invoke-direct {v1, p1}, Landroid/app/AlertDialog$Builder;-><init>(Landroid/content/Context;)V

    const-string v2, "BACHATA S4+ \u2014 Upscaler"

    invoke-virtual {v1, v2}, Landroid/app/AlertDialog$Builder;->setTitle(Ljava/lang/CharSequence;)Landroid/app/AlertDialog$Builder;

    move-result-object v1

    const/4 v2, 0x2

    new-array v2, v2, [Ljava/lang/CharSequence;

    const-string v3, "FSR 1 (original)"

    aput-object v3, v2, v0

    const/4 v0, 0x1

    const-string v3, "FSR 3.1"

    aput-object v3, v2, v0

    new-instance v0, Lcom/bachatas4/android/bridge/Fsr3Ui$2;

    invoke-direct {v0, p0, p2, p1}, Lcom/bachatas4/android/bridge/Fsr3Ui$2;-><init>(Landroid/content/SharedPreferences;Landroid/widget/Button;Landroid/app/Activity;)V

    .line 66
    invoke-virtual {v1, v2, p3, v0}, Landroid/app/AlertDialog$Builder;->setSingleChoiceItems([Ljava/lang/CharSequence;ILandroid/content/DialogInterface$OnClickListener;)Landroid/app/AlertDialog$Builder;

    move-result-object p3

    new-instance v0, Lcom/bachatas4/android/bridge/Fsr3Ui$3;

    invoke-direct {v0, p1, p2, p0}, Lcom/bachatas4/android/bridge/Fsr3Ui$3;-><init>(Landroid/app/Activity;Landroid/widget/Button;Landroid/content/SharedPreferences;)V

    .line 71
    const-string p0, "Modos FSR 3.1"

    invoke-virtual {p3, p0, v0}, Landroid/app/AlertDialog$Builder;->setNeutralButton(Ljava/lang/CharSequence;Landroid/content/DialogInterface$OnClickListener;)Landroid/app/AlertDialog$Builder;

    move-result-object p0

    .line 72
    const-string p1, "Cancelar"

    const/4 p2, 0x0

    invoke-virtual {p0, p1, p2}, Landroid/app/AlertDialog$Builder;->setNegativeButton(Ljava/lang/CharSequence;Landroid/content/DialogInterface$OnClickListener;)Landroid/app/AlertDialog$Builder;

    move-result-object p0

    invoke-virtual {p0}, Landroid/app/AlertDialog$Builder;->show()Landroid/app/AlertDialog;

    .line 73
    return-void
.end method

.method static synthetic lambda$showModes$3(Landroid/content/SharedPreferences;Landroid/widget/Button;Landroid/content/DialogInterface;I)V
    .registers 6

    .line 80
    invoke-interface {p0}, Landroid/content/SharedPreferences;->edit()Landroid/content/SharedPreferences$Editor;

    move-result-object v0

    const-string v1, "preset"

    invoke-interface {v0, v1, p3}, Landroid/content/SharedPreferences$Editor;->putInt(Ljava/lang/String;I)Landroid/content/SharedPreferences$Editor;

    move-result-object p3

    invoke-interface {p3}, Landroid/content/SharedPreferences$Editor;->apply()V

    .line 81
    invoke-static {p1, p0}, Lcom/bachatas4/android/bridge/Fsr3Ui;->refresh(Landroid/widget/Button;Landroid/content/SharedPreferences;)V

    .line 82
    invoke-interface {p2}, Landroid/content/DialogInterface;->dismiss()V

    .line 83
    return-void
.end method

.method private static px(Landroid/app/Activity;I)I
    .registers 2

    .line 42
    int-to-float p1, p1

    invoke-virtual {p0}, Landroid/app/Activity;->getResources()Landroid/content/res/Resources;

    move-result-object p0

    invoke-virtual {p0}, Landroid/content/res/Resources;->getDisplayMetrics()Landroid/util/DisplayMetrics;

    move-result-object p0

    iget p0, p0, Landroid/util/DisplayMetrics;->density:F

    mul-float/2addr p1, p0

    const/high16 p0, 0x3f000000    # 0.5f

    add-float/2addr p1, p0

    float-to-int p0, p1

    return p0
.end method

.method private static refresh(Landroid/widget/Button;Landroid/content/SharedPreferences;)V
    .registers 5

    .line 44
    const-string v0, "enabled"

    const/4 v1, 0x0

    invoke-interface {p1, v0, v1}, Landroid/content/SharedPreferences;->getBoolean(Ljava/lang/String;Z)Z

    move-result v0

    .line 45
    const-string v1, "preset"

    const/4 v2, 0x1

    invoke-interface {p1, v1, v2}, Landroid/content/SharedPreferences;->getInt(Ljava/lang/String;I)I

    move-result p1

    .line 46
    if-ltz p1, :cond_17

    sget-object v1, Lcom/bachatas4/android/bridge/Fsr3Ui;->MODES:[Ljava/lang/String;

    array-length v1, v1

    if-lt p1, v1, :cond_16

    goto :goto_17

    :cond_16
    move v2, p1

    .line 47
    :cond_17
    :goto_17
    if-eqz v0, :cond_31

    new-instance p1, Ljava/lang/StringBuilder;

    invoke-direct {p1}, Ljava/lang/StringBuilder;-><init>()V

    const-string v0, "FSR 3.1 \u2022 "

    invoke-virtual {p1, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p1

    sget-object v0, Lcom/bachatas4/android/bridge/Fsr3Ui;->MODES:[Ljava/lang/String;

    aget-object v0, v0, v2

    invoke-virtual {p1, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p1

    invoke-virtual {p1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p1

    goto :goto_33

    :cond_31
    const-string p1, "FSR 1 \u2022 Configurar"

    :goto_33
    invoke-virtual {p0, p1}, Landroid/widget/Button;->setText(Ljava/lang/CharSequence;)V

    .line 48
    return-void
.end method

.method private static showModes(Landroid/app/Activity;Landroid/widget/Button;Landroid/content/SharedPreferences;)V
    .registers 6

    .line 76
    const-string v0, "preset"

    const/4 v1, 0x1

    invoke-interface {p2, v0, v1}, Landroid/content/SharedPreferences;->getInt(Ljava/lang/String;I)I

    move-result v0

    .line 77
    if-ltz v0, :cond_10

    sget-object v2, Lcom/bachatas4/android/bridge/Fsr3Ui;->MODES:[Ljava/lang/String;

    array-length v2, v2

    if-lt v0, v2, :cond_f

    goto :goto_10

    :cond_f
    move v1, v0

    .line 78
    :cond_10
    :goto_10
    new-instance v0, Landroid/app/AlertDialog$Builder;

    invoke-direct {v0, p0}, Landroid/app/AlertDialog$Builder;-><init>(Landroid/content/Context;)V

    const-string p0, "FSR 3.1 \u2014 Preset"

    invoke-virtual {v0, p0}, Landroid/app/AlertDialog$Builder;->setTitle(Ljava/lang/CharSequence;)Landroid/app/AlertDialog$Builder;

    move-result-object p0

    sget-object v0, Lcom/bachatas4/android/bridge/Fsr3Ui;->MODES:[Ljava/lang/String;

    new-instance v2, Lcom/bachatas4/android/bridge/Fsr3Ui$0;

    invoke-direct {v2, p2, p1}, Lcom/bachatas4/android/bridge/Fsr3Ui$0;-><init>(Landroid/content/SharedPreferences;Landroid/widget/Button;)V

    .line 79
    invoke-virtual {p0, v0, v1, v2}, Landroid/app/AlertDialog$Builder;->setSingleChoiceItems([Ljava/lang/CharSequence;ILandroid/content/DialogInterface$OnClickListener;)Landroid/app/AlertDialog$Builder;

    move-result-object p0

    .line 83
    const-string p1, "Cancelar"

    const/4 p2, 0x0

    invoke-virtual {p0, p1, p2}, Landroid/app/AlertDialog$Builder;->setNegativeButton(Ljava/lang/CharSequence;Landroid/content/DialogInterface$OnClickListener;)Landroid/app/AlertDialog$Builder;

    move-result-object p0

    invoke-virtual {p0}, Landroid/app/AlertDialog$Builder;->show()Landroid/app/AlertDialog;

    .line 84
    return-void
.end method

.method public static initialize(Landroid/content/Context;)V
    .registers 1
    invoke-virtual {p0}, Landroid/content/Context;->getApplicationContext()Landroid/content/Context;
    move-result-object p0
    sput-object p0, Lcom/bachatas4/android/bridge/Fsr3Ui;->appContext:Landroid/content/Context;
    return-void
.end method
