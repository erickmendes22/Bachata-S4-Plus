.class final Lcom/bachatas4/android/feature/session/SessionViewModel$1;
.super Lkotlin/coroutines/jvm/internal/SuspendLambda;
.source "SessionViewModel.kt"

# interfaces
.implements Lkotlin/jvm/functions/Function2;


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lcom/bachatas4/android/feature/session/SessionViewModel;-><init>(Lcom/bachatas4/android/data/GameRepository;Landroid/content/Context;)V
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x18
    name = null
.end annotation

.annotation system Ldalvik/annotation/Signature;
    value = {
        "Lkotlin/coroutines/jvm/internal/SuspendLambda;",
        "Lkotlin/jvm/functions/Function2<",
        "Lkotlinx/coroutines/CoroutineScope;",
        "Lkotlin/coroutines/Continuation<",
        "-",
        "Lkotlin/Unit;",
        ">;",
        "Ljava/lang/Object;",
        ">;"
    }
.end annotation

.annotation system Ldalvik/annotation/SourceDebugExtension;
    value = "SMAP\nSessionViewModel.kt\nKotlin\n*S Kotlin\n*F\n+ 1 SessionViewModel.kt\ncom/bachatas4/android/feature/session/SessionViewModel$1\n+ 2 fake.kt\nkotlin/jvm/internal/FakeKt\n*L\n1#1,79:1\n1#2:80\n*E\n"
.end annotation

.annotation runtime Lkotlin/Metadata;
    d1 = {
        "\u0000\n\n\u0000\n\u0002\u0010\u0002\n\u0002\u0018\u0002\u0010\u0000\u001a\u00020\u0001*\u00020\u0002H\n"
    }
    d2 = {
        "<anonymous>",
        "",
        "Lkotlinx/coroutines/CoroutineScope;"
    }
    k = 0x3
    mv = {
        0x2,
        0x4,
        0x0
    }
    xi = 0x30
.end annotation

.annotation runtime Lkotlin/coroutines/jvm/internal/DebugMetadata;
    c = "com.bachatas4.android.feature.session.SessionViewModel$1"
    f = "SessionViewModel.kt"
    i = {
        0x0,
        0x0,
        0x0,
        0x0
    }
    l = {
        0x30
    }
    m = "invokeSuspend"
    n = {
        "$this$launch",
        "activityManager",
        "memory",
        "gpu"
    }
    nl = {
        -0x1
    }
    s = {
        "L$0",
        "L$1",
        "L$2",
        "L$3"
    }
    v = 0x2
.end annotation


# instance fields
.field private synthetic L$0:Ljava/lang/Object;

.field L$1:Ljava/lang/Object;

.field L$2:Ljava/lang/Object;

.field L$3:Ljava/lang/Object;

.field label:I

.field final synthetic this$0:Lcom/bachatas4/android/feature/session/SessionViewModel;


# direct methods
.method constructor <init>(Lcom/bachatas4/android/feature/session/SessionViewModel;Lkotlin/coroutines/Continuation;)V
    .locals 0
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "(",
            "Lcom/bachatas4/android/feature/session/SessionViewModel;",
            "Lkotlin/coroutines/Continuation<",
            "-",
            "Lcom/bachatas4/android/feature/session/SessionViewModel$1;",
            ">;)V"
        }
    .end annotation

    iput-object p1, p0, Lcom/bachatas4/android/feature/session/SessionViewModel$1;->this$0:Lcom/bachatas4/android/feature/session/SessionViewModel;

    const/4 p1, 0x2

    invoke-direct {p0, p1, p2}, Lkotlin/coroutines/jvm/internal/SuspendLambda;-><init>(ILkotlin/coroutines/Continuation;)V

    return-void
.end method


# virtual methods
.method public final create(Ljava/lang/Object;Lkotlin/coroutines/Continuation;)Lkotlin/coroutines/Continuation;
    .locals 1
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "(",
            "Ljava/lang/Object;",
            "Lkotlin/coroutines/Continuation<",
            "*>;)",
            "Lkotlin/coroutines/Continuation<",
            "Lkotlin/Unit;",
            ">;"
        }
    .end annotation

    new-instance v0, Lcom/bachatas4/android/feature/session/SessionViewModel$1;

    iget-object p0, p0, Lcom/bachatas4/android/feature/session/SessionViewModel$1;->this$0:Lcom/bachatas4/android/feature/session/SessionViewModel;

    invoke-direct {v0, p0, p2}, Lcom/bachatas4/android/feature/session/SessionViewModel$1;-><init>(Lcom/bachatas4/android/feature/session/SessionViewModel;Lkotlin/coroutines/Continuation;)V

    iput-object p1, v0, Lcom/bachatas4/android/feature/session/SessionViewModel$1;->L$0:Ljava/lang/Object;

    check-cast v0, Lkotlin/coroutines/Continuation;

    return-object v0
.end method

.method public bridge synthetic invoke(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;
    .locals 0

    check-cast p1, Lkotlinx/coroutines/CoroutineScope;

    check-cast p2, Lkotlin/coroutines/Continuation;

    invoke-virtual {p0, p1, p2}, Lcom/bachatas4/android/feature/session/SessionViewModel$1;->invoke(Lkotlinx/coroutines/CoroutineScope;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;

    move-result-object p0

    return-object p0
.end method

.method public final invoke(Lkotlinx/coroutines/CoroutineScope;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;
    .locals 0
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "(",
            "Lkotlinx/coroutines/CoroutineScope;",
            "Lkotlin/coroutines/Continuation<",
            "-",
            "Lkotlin/Unit;",
            ">;)",
            "Ljava/lang/Object;"
        }
    .end annotation

    invoke-virtual {p0, p1, p2}, Lcom/bachatas4/android/feature/session/SessionViewModel$1;->create(Ljava/lang/Object;Lkotlin/coroutines/Continuation;)Lkotlin/coroutines/Continuation;

    move-result-object p0

    check-cast p0, Lcom/bachatas4/android/feature/session/SessionViewModel$1;

    sget-object p1, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;

    invoke-virtual {p0, p1}, Lcom/bachatas4/android/feature/session/SessionViewModel$1;->invokeSuspend(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object p0

    return-object p0
.end method

.method public final invokeSuspend(Ljava/lang/Object;)Ljava/lang/Object;
    .locals 13

    iget-object v0, p0, Lcom/bachatas4/android/feature/session/SessionViewModel$1;->L$0:Ljava/lang/Object;

    move-object v1, v0

    check-cast v1, Lkotlinx/coroutines/CoroutineScope;

    invoke-static {}, Lkotlin/coroutines/intrinsics/IntrinsicsKt;->getCOROUTINE_SUSPENDED()Ljava/lang/Object;

    move-result-object v2

    .line 35
    iget v0, p0, Lcom/bachatas4/android/feature/session/SessionViewModel$1;->label:I

    const/4 v3, 0x1

    if-eqz v0, :cond_1

    if-ne v0, v3, :cond_0

    iget-object v0, p0, Lcom/bachatas4/android/feature/session/SessionViewModel$1;->L$3:Ljava/lang/Object;

    check-cast v0, Ljava/lang/String;

    iget-object v0, p0, Lcom/bachatas4/android/feature/session/SessionViewModel$1;->L$2:Ljava/lang/Object;

    check-cast v0, Landroid/app/ActivityManager$MemoryInfo;

    iget-object v0, p0, Lcom/bachatas4/android/feature/session/SessionViewModel$1;->L$1:Ljava/lang/Object;

    check-cast v0, Landroid/app/ActivityManager;

    invoke-static {p1}, Lkotlin/ResultKt;->throwOnFailure(Ljava/lang/Object;)V

    move-object p1, v0

    goto :goto_0

    :cond_0
    new-instance p0, Ljava/lang/IllegalStateException;

    const-string p1, "call to \'resume\' before \'invoke\' with coroutine"

    invoke-direct {p0, p1}, Ljava/lang/IllegalStateException;-><init>(Ljava/lang/String;)V

    throw p0

    :cond_1
    invoke-static {p1}, Lkotlin/ResultKt;->throwOnFailure(Ljava/lang/Object;)V

    .line 36
    iget-object p1, p0, Lcom/bachatas4/android/feature/session/SessionViewModel$1;->this$0:Lcom/bachatas4/android/feature/session/SessionViewModel;

    invoke-static {p1}, Lcom/bachatas4/android/feature/session/SessionViewModel;->access$getContext$p(Lcom/bachatas4/android/feature/session/SessionViewModel;)Landroid/content/Context;

    move-result-object p1

    const-class v0, Landroid/app/ActivityManager;

    invoke-virtual {p1, v0}, Landroid/content/Context;->getSystemService(Ljava/lang/Class;)Ljava/lang/Object;

    move-result-object p1

    check-cast p1, Landroid/app/ActivityManager;

    .line 38
    :cond_2
    :goto_0
    sget-object v0, Lcom/bachatas4/android/runtime/session/ManagedSession;->INSTANCE:Lcom/bachatas4/android/runtime/session/ManagedSession;

    const-wide/16 v4, 0x0

    const/4 v6, 0x0

    invoke-static {v0, v4, v5, v3, v6}, Lcom/bachatas4/android/runtime/session/ManagedSession;->refreshFrameTelemetry$default(Lcom/bachatas4/android/runtime/session/ManagedSession;JILjava/lang/Object;)V

    .line 39
    new-instance v4, Landroid/app/ActivityManager$MemoryInfo;

    invoke-direct {v4}, Landroid/app/ActivityManager$MemoryInfo;-><init>()V

    invoke-virtual {p1, v4}, Landroid/app/ActivityManager;->getMemoryInfo(Landroid/app/ActivityManager$MemoryInfo;)V

    .line 40
    :try_start_0
    sget-object v0, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    .line 41
    new-instance v0, Ljava/io/File;

    const-string v5, "/sys/class/kgsl/kgsl-3d0/gpu_busy_percentage"

    invoke-direct {v0, v5}, Ljava/io/File;-><init>(Ljava/lang/String;)V

    invoke-static {v0, v6, v3, v6}, Lkotlin/io/FilesKt;->readText$default(Ljava/io/File;Ljava/nio/charset/Charset;ILjava/lang/Object;)Ljava/lang/String;

    move-result-object v0

    check-cast v0, Ljava/lang/CharSequence;

    invoke-static {v0}, Lkotlin/text/StringsKt;->trim(Ljava/lang/CharSequence;)Ljava/lang/CharSequence;

    move-result-object v0

    invoke-virtual {v0}, Ljava/lang/Object;->toString()Ljava/lang/String;

    move-result-object v0

    .line 40
    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v0
    :try_end_0
    .catchall {:try_start_0 .. :try_end_0} :catchall_0

    goto :goto_1

    :catchall_0
    move-exception v0

    sget-object v5, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    invoke-static {v0}, Lkotlin/ResultKt;->createFailure(Ljava/lang/Throwable;)Ljava/lang/Object;

    move-result-object v0

    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v0

    .line 42
    :goto_1
    invoke-static {v0}, Lkotlin/Result;->isFailure-impl(Ljava/lang/Object;)Z

    move-result v5

    if-eqz v5, :cond_3

    move-object v0, v6

    :cond_3
    check-cast v0, Ljava/lang/String;

    if-eqz v0, :cond_5

    move-object v5, v0

    check-cast v5, Ljava/lang/CharSequence;

    invoke-static {v5}, Lkotlin/text/StringsKt;->isBlank(Ljava/lang/CharSequence;)Z

    move-result v5

    if-nez v5, :cond_4

    move-object v6, v0

    :cond_4
    if-eqz v6, :cond_5

    goto :goto_2

    :cond_5
    const-string v6, "N/A"

    :goto_2
    move-object v12, v6

    .line 43
    iget-object v0, p0, Lcom/bachatas4/android/feature/session/SessionViewModel$1;->this$0:Lcom/bachatas4/android/feature/session/SessionViewModel;

    invoke-static {v0}, Lcom/bachatas4/android/feature/session/SessionViewModel;->access$getMutableDeviceTelemetry$p(Lcom/bachatas4/android/feature/session/SessionViewModel;)Lkotlinx/coroutines/flow/MutableStateFlow;

    move-result-object v0

    new-instance v7, Lcom/bachatas4/android/feature/session/DeviceTelemetry;

    .line 44
    iget-wide v5, v4, Landroid/app/ActivityManager$MemoryInfo;->totalMem:J

    iget-wide v8, v4, Landroid/app/ActivityManager$MemoryInfo;->availMem:J

    sub-long/2addr v5, v8

    const-wide/32 v8, 0x100000

    div-long/2addr v5, v8

    .line 45
    iget-wide v10, v4, Landroid/app/ActivityManager$MemoryInfo;->totalMem:J

    div-long/2addr v10, v8

    move-wide v8, v5

    .line 43
    invoke-direct/range {v7 .. v12}, Lcom/bachatas4/android/feature/session/DeviceTelemetry;-><init>(JJLjava/lang/String;)V

    invoke-interface {v0, v7}, Lkotlinx/coroutines/flow/MutableStateFlow;->setValue(Ljava/lang/Object;)V

    .line 48
    move-object v0, p0

    check-cast v0, Lkotlin/coroutines/Continuation;

    iput-object v1, p0, Lcom/bachatas4/android/feature/session/SessionViewModel$1;->L$0:Ljava/lang/Object;

    iput-object p1, p0, Lcom/bachatas4/android/feature/session/SessionViewModel$1;->L$1:Ljava/lang/Object;

    invoke-static {v4}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v4

    iput-object v4, p0, Lcom/bachatas4/android/feature/session/SessionViewModel$1;->L$2:Ljava/lang/Object;

    invoke-static {v12}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v4

    iput-object v4, p0, Lcom/bachatas4/android/feature/session/SessionViewModel$1;->L$3:Ljava/lang/Object;

    iput v3, p0, Lcom/bachatas4/android/feature/session/SessionViewModel$1;->label:I

    const-wide/16 v4, 0x1f4

    invoke-static {v4, v5, v0}, Lkotlinx/coroutines/DelayKt;->delay(JLkotlin/coroutines/Continuation;)Ljava/lang/Object;

    move-result-object v0

    if-ne v0, v2, :cond_2

    return-object v2
.end method
