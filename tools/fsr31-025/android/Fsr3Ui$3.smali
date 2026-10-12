.class public final synthetic Lcom/bachatas4/android/bridge/Fsr3Ui$3;
.super Ljava/lang/Object;
.source "D8$$SyntheticClass"

# interfaces
.implements Landroid/content/DialogInterface$OnClickListener;


# annotations
.annotation runtime Lcom/android/tools/r8/annotations/LambdaMethod;
    holder = "Lcom/bachatas4/android/bridge/Fsr3Ui;"
    method = "lambda$attach$1"
    proto = "(Landroid/app/Activity;Landroid/widget/Button;Landroid/content/SharedPreferences;Landroid/content/DialogInterface;I)V"
.end annotation


# instance fields
.field public final synthetic f$0:Landroid/app/Activity;

.field public final synthetic f$1:Landroid/widget/Button;

.field public final synthetic f$2:Landroid/content/SharedPreferences;


# direct methods
.method public synthetic constructor <init>(Landroid/app/Activity;Landroid/widget/Button;Landroid/content/SharedPreferences;)V
    .registers 4

    .line 0
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    iput-object p1, p0, Lcom/bachatas4/android/bridge/Fsr3Ui$3;->f$0:Landroid/app/Activity;

    iput-object p2, p0, Lcom/bachatas4/android/bridge/Fsr3Ui$3;->f$1:Landroid/widget/Button;

    iput-object p3, p0, Lcom/bachatas4/android/bridge/Fsr3Ui$3;->f$2:Landroid/content/SharedPreferences;

    return-void
.end method


# virtual methods
.method public final onClick(Landroid/content/DialogInterface;I)V
    .registers 6

    .line 0
    iget-object v0, p0, Lcom/bachatas4/android/bridge/Fsr3Ui$3;->f$0:Landroid/app/Activity;

    iget-object v1, p0, Lcom/bachatas4/android/bridge/Fsr3Ui$3;->f$1:Landroid/widget/Button;

    iget-object v2, p0, Lcom/bachatas4/android/bridge/Fsr3Ui$3;->f$2:Landroid/content/SharedPreferences;

    invoke-static {v0, v1, v2, p1, p2}, Lcom/bachatas4/android/bridge/Fsr3Ui;->lambda$attach$1(Landroid/app/Activity;Landroid/widget/Button;Landroid/content/SharedPreferences;Landroid/content/DialogInterface;I)V

    return-void
.end method
