.class public final synthetic Lcom/bachatas4/android/bridge/Fsr3Ui$0;
.super Ljava/lang/Object;
.source "D8$$SyntheticClass"

# interfaces
.implements Landroid/content/DialogInterface$OnClickListener;


# annotations
.annotation runtime Lcom/android/tools/r8/annotations/LambdaMethod;
    holder = "Lcom/bachatas4/android/bridge/Fsr3Ui;"
    method = "lambda$showModes$3"
    proto = "(Landroid/content/SharedPreferences;Landroid/widget/Button;Landroid/content/DialogInterface;I)V"
.end annotation


# instance fields
.field public final synthetic f$0:Landroid/content/SharedPreferences;

.field public final synthetic f$1:Landroid/widget/Button;


# direct methods
.method public synthetic constructor <init>(Landroid/content/SharedPreferences;Landroid/widget/Button;)V
    .registers 3

    .line 0
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    iput-object p1, p0, Lcom/bachatas4/android/bridge/Fsr3Ui$0;->f$0:Landroid/content/SharedPreferences;

    iput-object p2, p0, Lcom/bachatas4/android/bridge/Fsr3Ui$0;->f$1:Landroid/widget/Button;

    return-void
.end method


# virtual methods
.method public final onClick(Landroid/content/DialogInterface;I)V
    .registers 5

    .line 0
    iget-object v0, p0, Lcom/bachatas4/android/bridge/Fsr3Ui$0;->f$0:Landroid/content/SharedPreferences;

    iget-object v1, p0, Lcom/bachatas4/android/bridge/Fsr3Ui$0;->f$1:Landroid/widget/Button;

    invoke-static {v0, v1, p1, p2}, Lcom/bachatas4/android/bridge/Fsr3Ui;->lambda$showModes$3(Landroid/content/SharedPreferences;Landroid/widget/Button;Landroid/content/DialogInterface;I)V

    return-void
.end method
