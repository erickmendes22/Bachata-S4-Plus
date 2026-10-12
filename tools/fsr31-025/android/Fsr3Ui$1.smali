.class public final synthetic Lcom/bachatas4/android/bridge/Fsr3Ui$1;
.super Ljava/lang/Object;
.source "D8$$SyntheticClass"

# interfaces
.implements Landroid/view/View$OnClickListener;


# annotations
.annotation runtime Lcom/android/tools/r8/annotations/LambdaMethod;
    holder = "Lcom/bachatas4/android/bridge/Fsr3Ui;"
    method = "lambda$attach$2"
    proto = "(Landroid/content/SharedPreferences;Landroid/app/Activity;Landroid/widget/Button;Landroid/view/View;)V"
.end annotation


# instance fields
.field public final synthetic f$0:Landroid/content/SharedPreferences;

.field public final synthetic f$1:Landroid/app/Activity;

.field public final synthetic f$2:Landroid/widget/Button;


# direct methods
.method public synthetic constructor <init>(Landroid/content/SharedPreferences;Landroid/app/Activity;Landroid/widget/Button;)V
    .registers 4

    .line 0
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    iput-object p1, p0, Lcom/bachatas4/android/bridge/Fsr3Ui$1;->f$0:Landroid/content/SharedPreferences;

    iput-object p2, p0, Lcom/bachatas4/android/bridge/Fsr3Ui$1;->f$1:Landroid/app/Activity;

    iput-object p3, p0, Lcom/bachatas4/android/bridge/Fsr3Ui$1;->f$2:Landroid/widget/Button;

    return-void
.end method


# virtual methods
.method public final onClick(Landroid/view/View;)V
    .registers 5

    .line 0
    iget-object v0, p0, Lcom/bachatas4/android/bridge/Fsr3Ui$1;->f$0:Landroid/content/SharedPreferences;

    iget-object v1, p0, Lcom/bachatas4/android/bridge/Fsr3Ui$1;->f$1:Landroid/app/Activity;

    iget-object v2, p0, Lcom/bachatas4/android/bridge/Fsr3Ui$1;->f$2:Landroid/widget/Button;

    invoke-static {v0, v1, v2, p1}, Lcom/bachatas4/android/bridge/Fsr3Ui;->lambda$attach$2(Landroid/content/SharedPreferences;Landroid/app/Activity;Landroid/widget/Button;Landroid/view/View;)V

    return-void
.end method
