.class public final synthetic Lcom/bachatas4/android/service/SafBrokerSession$$ExternalSyntheticLambda3;
.super Ljava/lang/Object;
.source "D8$$SyntheticClass"

# interfaces
.implements Ljava/lang/Runnable;


# instance fields
.field public final synthetic f$0:Lcom/bachatas4/android/service/SafBrokerSession;

.field public final synthetic f$1:Landroid/net/LocalSocket;


# direct methods
.method public synthetic constructor <init>(Lcom/bachatas4/android/service/SafBrokerSession;Landroid/net/LocalSocket;)V
    .locals 0

    .line 0
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    iput-object p1, p0, Lcom/bachatas4/android/service/SafBrokerSession$$ExternalSyntheticLambda3;->f$0:Lcom/bachatas4/android/service/SafBrokerSession;

    iput-object p2, p0, Lcom/bachatas4/android/service/SafBrokerSession$$ExternalSyntheticLambda3;->f$1:Landroid/net/LocalSocket;

    return-void
.end method


# virtual methods
.method public final run()V
    .locals 1

    .line 0
    iget-object v0, p0, Lcom/bachatas4/android/service/SafBrokerSession$$ExternalSyntheticLambda3;->f$0:Lcom/bachatas4/android/service/SafBrokerSession;

    iget-object p0, p0, Lcom/bachatas4/android/service/SafBrokerSession$$ExternalSyntheticLambda3;->f$1:Landroid/net/LocalSocket;

    invoke-static {v0, p0}, Lcom/bachatas4/android/service/SafBrokerSession;->lambda$0$2(Lcom/bachatas4/android/service/SafBrokerSession;Landroid/net/LocalSocket;)V

    return-void
.end method
