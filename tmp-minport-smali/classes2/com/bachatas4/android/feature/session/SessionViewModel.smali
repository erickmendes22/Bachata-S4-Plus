.class public final Lcom/bachatas4/android/feature/session/SessionViewModel;
.super Landroidx/lifecycle/ViewModel;
.source "SessionViewModel.kt"


# annotations
.annotation runtime Lkotlin/Metadata;
    d1 = {
        "\u0000X\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0008\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0008\u0003\n\u0002\u0018\u0002\n\u0002\u0008\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0008\u0003\n\u0002\u0010\u0002\n\u0000\n\u0002\u0010\u000e\n\u0000\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\u0008\u0007\u0018\u00002\u00020\u0001B#\u0008\u0007\u0012\u0006\u0010\u0002\u001a\u00020\u0003\u0012\u000c\u0008\u0001\u0010\u0004\u001a\u00020\u0005:\u0002\u0008\u0006\u001a\u0002\u0008\t\u00a2\u0006\u0004\u0008\u0007\u0010\u0008J\u000e\u0010\u0017\u001a\u00020\u00182\u0006\u0010\u0019\u001a\u00020\u001aR\u000e\u0010\u0002\u001a\u00020\u0003X\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u0015\u0010\u0004\u001a\u00020\u00058\u0002X\u0083\u0004\u0092\u0002\u0002\u0008\u0006\u00a2\u0006\u0002\n\u0000R\u0017\u0010\n\u001a\u0008\u0012\u0004\u0012\u00020\u000c0\u000b\u00a2\u0006\u0008\n\u0000\u001a\u0004\u0008\r\u0010\u000eR\u0017\u0010\u000f\u001a\u0008\u0012\u0004\u0012\u00020\u00100\u000b\u00a2\u0006\u0008\n\u0000\u001a\u0004\u0008\u0011\u0010\u000eR\u0014\u0010\u0012\u001a\u0008\u0012\u0004\u0012\u00020\u00140\u0013X\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u0017\u0010\u0015\u001a\u0008\u0012\u0004\u0012\u00020\u00140\u000b\u00a2\u0006\u0008\n\u0000\u001a\u0004\u0008\u0016\u0010\u000e\u00ca\u0001\u0002\u0008\u001c\u00ca\u0001\u000c\u0008\u001d\u0012\u0008\u0008\u001e\u0012\u0004\u0008\u0003\u0010\u0000\u00a8\u0006\u001b"
    }
    d2 = {
        "Lcom/bachatas4/android/feature/session/SessionViewModel;",
        "Landroidx/lifecycle/ViewModel;",
        "repository",
        "Lcom/bachatas4/android/data/GameRepository;",
        "context",
        "Landroid/content/Context;",
        "Ldagger/hilt/android/qualifiers/ApplicationContext;",
        "<init>",
        "(Lcom/bachatas4/android/data/GameRepository;Landroid/content/Context;)V",
        "Ljavax/inject/Inject;",
        "state",
        "Lkotlinx/coroutines/flow/StateFlow;",
        "Lcom/bachatas4/android/runtime/session/ManagedSessionState;",
        "getState",
        "()Lkotlinx/coroutines/flow/StateFlow;",
        "frameTelemetry",
        "Lcom/bachatas4/android/runtime/session/FrameTelemetry;",
        "getFrameTelemetry",
        "mutableDeviceTelemetry",
        "Lkotlinx/coroutines/flow/MutableStateFlow;",
        "Lcom/bachatas4/android/feature/session/DeviceTelemetry;",
        "deviceTelemetry",
        "getDeviceTelemetry",
        "launch",
        "",
        "gameId",
        "",
        "session",
        "Ldagger/hilt/android/lifecycle/HiltViewModel;",
        "Landroidx/compose/runtime/internal/StabilityInferred;",
        "parameters"
    }
    k = 0x1
    mv = {
        0x2,
        0x4,
        0x0
    }
    xi = 0x30
.end annotation


# static fields
.field public static final $stable:I = 0x8


# instance fields
.field private final context:Landroid/content/Context;
    .annotation runtime Ldagger/hilt/android/qualifiers/ApplicationContext;
    .end annotation
.end field

.field private final deviceTelemetry:Lkotlinx/coroutines/flow/StateFlow;
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "Lkotlinx/coroutines/flow/StateFlow<",
            "Lcom/bachatas4/android/feature/session/DeviceTelemetry;",
            ">;"
        }
    .end annotation
.end field

.field private final frameTelemetry:Lkotlinx/coroutines/flow/StateFlow;
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "Lkotlinx/coroutines/flow/StateFlow<",
            "Lcom/bachatas4/android/runtime/session/FrameTelemetry;",
            ">;"
        }
    .end annotation
.end field

.field private final mutableDeviceTelemetry:Lkotlinx/coroutines/flow/MutableStateFlow;
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "Lkotlinx/coroutines/flow/MutableStateFlow<",
            "Lcom/bachatas4/android/feature/session/DeviceTelemetry;",
            ">;"
        }
    .end annotation
.end field

.field private final repository:Lcom/bachatas4/android/data/GameRepository;

.field private final state:Lkotlinx/coroutines/flow/StateFlow;
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "Lkotlinx/coroutines/flow/StateFlow<",
            "Lcom/bachatas4/android/runtime/session/ManagedSessionState;",
            ">;"
        }
    .end annotation
.end field


# direct methods
.method static constructor <clinit>()V
    .locals 0

    return-void
.end method

.method public constructor <init>(Lcom/bachatas4/android/data/GameRepository;Landroid/content/Context;)V
    .locals 8
    .param p2    # Landroid/content/Context;
        .annotation runtime Ldagger/hilt/android/qualifiers/ApplicationContext;
        .end annotation
    .end param
    .annotation runtime Ljavax/inject/Inject;
    .end annotation

    const-string v0, "repository"

    invoke-static {p1, v0}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullParameter(Ljava/lang/Object;Ljava/lang/String;)V

    const-string v0, "context"

    invoke-static {p2, v0}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullParameter(Ljava/lang/Object;Ljava/lang/String;)V

    .line 24
    invoke-direct {p0}, Landroidx/lifecycle/ViewModel;-><init>()V

    .line 26
    iput-object p1, p0, Lcom/bachatas4/android/feature/session/SessionViewModel;->repository:Lcom/bachatas4/android/data/GameRepository;

    .line 27
    iput-object p2, p0, Lcom/bachatas4/android/feature/session/SessionViewModel;->context:Landroid/content/Context;

    .line 29
    sget-object p1, Lcom/bachatas4/android/runtime/session/ManagedSession;->INSTANCE:Lcom/bachatas4/android/runtime/session/ManagedSession;

    invoke-virtual {p1}, Lcom/bachatas4/android/runtime/session/ManagedSession;->getState()Lkotlinx/coroutines/flow/StateFlow;

    move-result-object p1

    iput-object p1, p0, Lcom/bachatas4/android/feature/session/SessionViewModel;->state:Lkotlinx/coroutines/flow/StateFlow;

    .line 30
    sget-object p1, Lcom/bachatas4/android/runtime/session/ManagedSession;->INSTANCE:Lcom/bachatas4/android/runtime/session/ManagedSession;

    invoke-virtual {p1}, Lcom/bachatas4/android/runtime/session/ManagedSession;->getFrameTelemetry()Lkotlinx/coroutines/flow/StateFlow;

    move-result-object p1

    iput-object p1, p0, Lcom/bachatas4/android/feature/session/SessionViewModel;->frameTelemetry:Lkotlinx/coroutines/flow/StateFlow;

    .line 31
    new-instance v0, Lcom/bachatas4/android/feature/session/DeviceTelemetry;

    const/4 v6, 0x7

    const/4 v7, 0x0

    const-wide/16 v1, 0x0

    const-wide/16 v3, 0x0

    const/4 v5, 0x0

    invoke-direct/range {v0 .. v7}, Lcom/bachatas4/android/feature/session/DeviceTelemetry;-><init>(JJLjava/lang/String;ILkotlin/jvm/internal/DefaultConstructorMarker;)V

    invoke-static {v0}, Lkotlinx/coroutines/flow/StateFlowKt;->MutableStateFlow(Ljava/lang/Object;)Lkotlinx/coroutines/flow/MutableStateFlow;

    move-result-object p1

    iput-object p1, p0, Lcom/bachatas4/android/feature/session/SessionViewModel;->mutableDeviceTelemetry:Lkotlinx/coroutines/flow/MutableStateFlow;

    .line 32
    check-cast p1, Lkotlinx/coroutines/flow/StateFlow;

    iput-object p1, p0, Lcom/bachatas4/android/feature/session/SessionViewModel;->deviceTelemetry:Lkotlinx/coroutines/flow/StateFlow;

    .line 35
    move-object p1, p0

    check-cast p1, Landroidx/lifecycle/ViewModel;

    invoke-static {p1}, Landroidx/lifecycle/ViewModelKt;->getViewModelScope(Landroidx/lifecycle/ViewModel;)Lkotlinx/coroutines/CoroutineScope;

    move-result-object v0

    new-instance p1, Lcom/bachatas4/android/feature/session/SessionViewModel$1;

    const/4 p2, 0x0

    invoke-direct {p1, p0, p2}, Lcom/bachatas4/android/feature/session/SessionViewModel$1;-><init>(Lcom/bachatas4/android/feature/session/SessionViewModel;Lkotlin/coroutines/Continuation;)V

    move-object v3, p1

    check-cast v3, Lkotlin/jvm/functions/Function2;

    const/4 v4, 0x3

    const/4 v1, 0x0

    const/4 v2, 0x0

    invoke-static/range {v0 .. v5}, Lkotlinx/coroutines/BuildersKt;->launch$default(Lkotlinx/coroutines/CoroutineScope;Lkotlin/coroutines/CoroutineContext;Lkotlinx/coroutines/CoroutineStart;Lkotlin/jvm/functions/Function2;ILjava/lang/Object;)Lkotlinx/coroutines/Job;

    return-void
.end method

.method public static final synthetic access$getContext$p(Lcom/bachatas4/android/feature/session/SessionViewModel;)Landroid/content/Context;
    .locals 0

    .line 24
    iget-object p0, p0, Lcom/bachatas4/android/feature/session/SessionViewModel;->context:Landroid/content/Context;

    return-object p0
.end method

.method public static final synthetic access$getMutableDeviceTelemetry$p(Lcom/bachatas4/android/feature/session/SessionViewModel;)Lkotlinx/coroutines/flow/MutableStateFlow;
    .locals 0

    .line 24
    iget-object p0, p0, Lcom/bachatas4/android/feature/session/SessionViewModel;->mutableDeviceTelemetry:Lkotlinx/coroutines/flow/MutableStateFlow;

    return-object p0
.end method

.method public static final synthetic access$getRepository$p(Lcom/bachatas4/android/feature/session/SessionViewModel;)Lcom/bachatas4/android/data/GameRepository;
    .locals 0

    .line 24
    iget-object p0, p0, Lcom/bachatas4/android/feature/session/SessionViewModel;->repository:Lcom/bachatas4/android/data/GameRepository;

    return-object p0
.end method


# virtual methods
.method public final getDeviceTelemetry()Lkotlinx/coroutines/flow/StateFlow;
    .locals 0
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "()",
            "Lkotlinx/coroutines/flow/StateFlow<",
            "Lcom/bachatas4/android/feature/session/DeviceTelemetry;",
            ">;"
        }
    .end annotation

    .line 32
    iget-object p0, p0, Lcom/bachatas4/android/feature/session/SessionViewModel;->deviceTelemetry:Lkotlinx/coroutines/flow/StateFlow;

    return-object p0
.end method

.method public final getFrameTelemetry()Lkotlinx/coroutines/flow/StateFlow;
    .locals 0
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "()",
            "Lkotlinx/coroutines/flow/StateFlow<",
            "Lcom/bachatas4/android/runtime/session/FrameTelemetry;",
            ">;"
        }
    .end annotation

    .line 30
    iget-object p0, p0, Lcom/bachatas4/android/feature/session/SessionViewModel;->frameTelemetry:Lkotlinx/coroutines/flow/StateFlow;

    return-object p0
.end method

.method public final getState()Lkotlinx/coroutines/flow/StateFlow;
    .locals 0
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "()",
            "Lkotlinx/coroutines/flow/StateFlow<",
            "Lcom/bachatas4/android/runtime/session/ManagedSessionState;",
            ">;"
        }
    .end annotation

    .line 29
    iget-object p0, p0, Lcom/bachatas4/android/feature/session/SessionViewModel;->state:Lkotlinx/coroutines/flow/StateFlow;

    return-object p0
.end method

.method public final launch(Ljava/lang/String;)V
    .locals 7

    const-string v0, "gameId"

    invoke-static {p1, v0}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullParameter(Ljava/lang/Object;Ljava/lang/String;)V

    .line 54
    iget-object v0, p0, Lcom/bachatas4/android/feature/session/SessionViewModel;->state:Lkotlinx/coroutines/flow/StateFlow;

    invoke-interface {v0}, Lkotlinx/coroutines/flow/StateFlow;->getValue()Ljava/lang/Object;

    move-result-object v0

    instance-of v0, v0, Lcom/bachatas4/android/runtime/session/ManagedSessionState$Running;

    if-nez v0, :cond_1

    iget-object v0, p0, Lcom/bachatas4/android/feature/session/SessionViewModel;->state:Lkotlinx/coroutines/flow/StateFlow;

    invoke-interface {v0}, Lkotlinx/coroutines/flow/StateFlow;->getValue()Ljava/lang/Object;

    move-result-object v0

    instance-of v0, v0, Lcom/bachatas4/android/runtime/session/ManagedSessionState$Preparing;

    if-eqz v0, :cond_0

    goto :goto_0

    .line 55
    :cond_0
    move-object v0, p0

    check-cast v0, Landroidx/lifecycle/ViewModel;

    invoke-static {v0}, Landroidx/lifecycle/ViewModelKt;->getViewModelScope(Landroidx/lifecycle/ViewModel;)Lkotlinx/coroutines/CoroutineScope;

    move-result-object v1

    new-instance v0, Lcom/bachatas4/android/feature/session/SessionViewModel$launch$1;

    const/4 v2, 0x0

    invoke-direct {v0, p0, p1, v2}, Lcom/bachatas4/android/feature/session/SessionViewModel$launch$1;-><init>(Lcom/bachatas4/android/feature/session/SessionViewModel;Ljava/lang/String;Lkotlin/coroutines/Continuation;)V

    move-object v4, v0

    check-cast v4, Lkotlin/jvm/functions/Function2;

    const/4 v5, 0x3

    const/4 v6, 0x0

    const/4 v3, 0x0

    invoke-static/range {v1 .. v6}, Lkotlinx/coroutines/BuildersKt;->launch$default(Lkotlinx/coroutines/CoroutineScope;Lkotlin/coroutines/CoroutineContext;Lkotlinx/coroutines/CoroutineStart;Lkotlin/jvm/functions/Function2;ILjava/lang/Object;)Lkotlinx/coroutines/Job;

    :cond_1
    :goto_0
    return-void
.end method
