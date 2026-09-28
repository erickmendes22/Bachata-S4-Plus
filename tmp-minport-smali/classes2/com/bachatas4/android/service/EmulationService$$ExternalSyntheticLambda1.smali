.class public final synthetic Lcom/bachatas4/android/service/EmulationService$$ExternalSyntheticLambda1;
.super Ljava/lang/Object;
.source "D8$$SyntheticClass"

# interfaces
.implements Lkotlin/jvm/functions/Function2;


# instance fields
.field public final synthetic f$0:Lcom/bachatas4/android/runtime/diagnostics/SessionLog;


# direct methods
.method public synthetic constructor <init>(Lcom/bachatas4/android/runtime/diagnostics/SessionLog;)V
    .locals 0

    .line 0
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    iput-object p1, p0, Lcom/bachatas4/android/service/EmulationService$$ExternalSyntheticLambda1;->f$0:Lcom/bachatas4/android/runtime/diagnostics/SessionLog;

    return-void
.end method


# virtual methods
.method public final invoke(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;
    .locals 0

    .line 0
    iget-object p0, p0, Lcom/bachatas4/android/service/EmulationService$$ExternalSyntheticLambda1;->f$0:Lcom/bachatas4/android/runtime/diagnostics/SessionLog;

    check-cast p1, Ljava/lang/String;

    check-cast p2, Ljava/lang/String;

    invoke-static {p0, p1, p2}, Lcom/bachatas4/android/service/EmulationService;->runSession$lambda$6(Lcom/bachatas4/android/runtime/diagnostics/SessionLog;Ljava/lang/String;Ljava/lang/String;)Lkotlin/Unit;

    move-result-object p0

    return-object p0
.end method
