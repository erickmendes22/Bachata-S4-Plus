.class public final synthetic Lcom/bachatas4/android/service/EmulationService$$ExternalSyntheticLambda6;
.super Ljava/lang/Object;
.source "D8$$SyntheticClass"

# interfaces
.implements Lkotlin/jvm/functions/Function1;


# instance fields
.field public final synthetic f$0:Ljava/util/concurrent/atomic/AtomicReference;


# direct methods
.method public synthetic constructor <init>(Ljava/util/concurrent/atomic/AtomicReference;)V
    .locals 0

    .line 0
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    iput-object p1, p0, Lcom/bachatas4/android/service/EmulationService$$ExternalSyntheticLambda6;->f$0:Ljava/util/concurrent/atomic/AtomicReference;

    return-void
.end method


# virtual methods
.method public final invoke(Ljava/lang/Object;)Ljava/lang/Object;
    .locals 0

    .line 0
    iget-object p0, p0, Lcom/bachatas4/android/service/EmulationService$$ExternalSyntheticLambda6;->f$0:Ljava/util/concurrent/atomic/AtomicReference;

    check-cast p1, Lcom/bachatas4/android/runtime/input/ControllerMotion;

    invoke-static {p0, p1}, Lcom/bachatas4/android/service/EmulationService;->$r8$lambda$BNirmT9VBt15wfCs4b8GaTodwdw(Ljava/util/concurrent/atomic/AtomicReference;Lcom/bachatas4/android/runtime/input/ControllerMotion;)Lkotlin/Unit;

    move-result-object p0

    return-object p0
.end method
