.class final Lcom/bachatas4/android/feature/session/SessionViewModel$launch$1;
.super Lkotlin/coroutines/jvm/internal/SuspendLambda;
.source "SessionViewModel.kt"

# interfaces
.implements Lkotlin/jvm/functions/Function2;


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lcom/bachatas4/android/feature/session/SessionViewModel;->launch(Ljava/lang/String;)V
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
    c = "com.bachatas4.android.feature.session.SessionViewModel$launch$1"
    f = "SessionViewModel.kt"
    i = {}
    l = {
        0x38
    }
    m = "invokeSuspend"
    n = {}
    nl = {
        0x39
    }
    s = {}
    v = 0x2
.end annotation


# instance fields
.field final synthetic $gameId:Ljava/lang/String;

.field label:I

.field final synthetic this$0:Lcom/bachatas4/android/feature/session/SessionViewModel;


# direct methods
.method constructor <init>(Lcom/bachatas4/android/feature/session/SessionViewModel;Ljava/lang/String;Lkotlin/coroutines/Continuation;)V
    .locals 0
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "(",
            "Lcom/bachatas4/android/feature/session/SessionViewModel;",
            "Ljava/lang/String;",
            "Lkotlin/coroutines/Continuation<",
            "-",
            "Lcom/bachatas4/android/feature/session/SessionViewModel$launch$1;",
            ">;)V"
        }
    .end annotation

    iput-object p1, p0, Lcom/bachatas4/android/feature/session/SessionViewModel$launch$1;->this$0:Lcom/bachatas4/android/feature/session/SessionViewModel;

    iput-object p2, p0, Lcom/bachatas4/android/feature/session/SessionViewModel$launch$1;->$gameId:Ljava/lang/String;

    const/4 p1, 0x2

    invoke-direct {p0, p1, p3}, Lkotlin/coroutines/jvm/internal/SuspendLambda;-><init>(ILkotlin/coroutines/Continuation;)V

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

    new-instance p1, Lcom/bachatas4/android/feature/session/SessionViewModel$launch$1;

    iget-object v0, p0, Lcom/bachatas4/android/feature/session/SessionViewModel$launch$1;->this$0:Lcom/bachatas4/android/feature/session/SessionViewModel;

    iget-object p0, p0, Lcom/bachatas4/android/feature/session/SessionViewModel$launch$1;->$gameId:Ljava/lang/String;

    invoke-direct {p1, v0, p0, p2}, Lcom/bachatas4/android/feature/session/SessionViewModel$launch$1;-><init>(Lcom/bachatas4/android/feature/session/SessionViewModel;Ljava/lang/String;Lkotlin/coroutines/Continuation;)V

    check-cast p1, Lkotlin/coroutines/Continuation;

    return-object p1
.end method

.method public bridge synthetic invoke(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;
    .locals 0

    check-cast p1, Lkotlinx/coroutines/CoroutineScope;

    check-cast p2, Lkotlin/coroutines/Continuation;

    invoke-virtual {p0, p1, p2}, Lcom/bachatas4/android/feature/session/SessionViewModel$launch$1;->invoke(Lkotlinx/coroutines/CoroutineScope;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;

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

    invoke-virtual {p0, p1, p2}, Lcom/bachatas4/android/feature/session/SessionViewModel$launch$1;->create(Ljava/lang/Object;Lkotlin/coroutines/Continuation;)Lkotlin/coroutines/Continuation;

    move-result-object p0

    check-cast p0, Lcom/bachatas4/android/feature/session/SessionViewModel$launch$1;

    sget-object p1, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;

    invoke-virtual {p0, p1}, Lcom/bachatas4/android/feature/session/SessionViewModel$launch$1;->invokeSuspend(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object p0

    return-object p0
.end method

.method public final invokeSuspend(Ljava/lang/Object;)Ljava/lang/Object;
    .locals 6

    invoke-static {}, Lkotlin/coroutines/intrinsics/IntrinsicsKt;->getCOROUTINE_SUSPENDED()Ljava/lang/Object;

    move-result-object v0

    .line 55
    iget v1, p0, Lcom/bachatas4/android/feature/session/SessionViewModel$launch$1;->label:I

    const/4 v2, 0x1

    if-eqz v1, :cond_1

    if-ne v1, v2, :cond_0

    invoke-static {p1}, Lkotlin/ResultKt;->throwOnFailure(Ljava/lang/Object;)V

    goto :goto_0

    :cond_0
    new-instance p0, Ljava/lang/IllegalStateException;

    const-string p1, "call to \'resume\' before \'invoke\' with coroutine"

    invoke-direct {p0, p1}, Ljava/lang/IllegalStateException;-><init>(Ljava/lang/String;)V

    throw p0

    :cond_1
    invoke-static {p1}, Lkotlin/ResultKt;->throwOnFailure(Ljava/lang/Object;)V

    .line 56
    iget-object p1, p0, Lcom/bachatas4/android/feature/session/SessionViewModel$launch$1;->this$0:Lcom/bachatas4/android/feature/session/SessionViewModel;

    invoke-static {p1}, Lcom/bachatas4/android/feature/session/SessionViewModel;->access$getRepository$p(Lcom/bachatas4/android/feature/session/SessionViewModel;)Lcom/bachatas4/android/data/GameRepository;

    move-result-object p1

    iget-object v1, p0, Lcom/bachatas4/android/feature/session/SessionViewModel$launch$1;->$gameId:Ljava/lang/String;

    move-object v3, p0

    check-cast v3, Lkotlin/coroutines/Continuation;

    iput v2, p0, Lcom/bachatas4/android/feature/session/SessionViewModel$launch$1;->label:I

    invoke-virtual {p1, v1, v3}, Lcom/bachatas4/android/data/GameRepository;->getGame(Ljava/lang/String;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;

    move-result-object p1

    if-ne p1, v0, :cond_2

    return-object v0

    .line 55
    :cond_2
    :goto_0
    check-cast p1, Lcom/bachatas4/android/model/Game;

    if-nez p1, :cond_3

    .line 58
    sget-object p0, Lcom/bachatas4/android/runtime/session/ManagedSession;->INSTANCE:Lcom/bachatas4/android/runtime/session/ManagedSession;

    new-instance v0, Lcom/bachatas4/android/runtime/session/ManagedSessionState$Failed;

    sget-object v1, Lcom/bachatas4/android/model/RuntimeErrorCode;->CONTENT_INVALID:Lcom/bachatas4/android/model/RuntimeErrorCode;

    const/4 v4, 0x4

    const/4 v5, 0x0

    const-string v2, "Game not found"

    const/4 v3, 0x0

    invoke-direct/range {v0 .. v5}, Lcom/bachatas4/android/runtime/session/ManagedSessionState$Failed;-><init>(Lcom/bachatas4/android/model/RuntimeErrorCode;Ljava/lang/String;Lcom/bachatas4/android/runtime/diagnostics/DiagnosticReportContext;ILkotlin/jvm/internal/DefaultConstructorMarker;)V

    check-cast v0, Lcom/bachatas4/android/runtime/session/ManagedSessionState;

    invoke-virtual {p0, v0}, Lcom/bachatas4/android/runtime/session/ManagedSession;->update(Lcom/bachatas4/android/runtime/session/ManagedSessionState;)V

    .line 59
    sget-object p0, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;

    return-object p0

    .line 61
    :cond_3
    iget-object v0, p0, Lcom/bachatas4/android/feature/session/SessionViewModel$launch$1;->this$0:Lcom/bachatas4/android/feature/session/SessionViewModel;

    invoke-static {v0}, Lcom/bachatas4/android/feature/session/SessionViewModel;->access$getContext$p(Lcom/bachatas4/android/feature/session/SessionViewModel;)Landroid/content/Context;

    move-result-object v0

    .line 63
    new-instance v1, Landroid/content/Intent;

    const-string v2, "com.bachatas4.android.action.START_EMULATION"

    invoke-direct {v1, v2}, Landroid/content/Intent;-><init>(Ljava/lang/String;)V

    iget-object v2, p0, Lcom/bachatas4/android/feature/session/SessionViewModel$launch$1;->this$0:Lcom/bachatas4/android/feature/session/SessionViewModel;

    invoke-static {v2}, Lcom/bachatas4/android/feature/session/SessionViewModel;->access$getContext$p(Lcom/bachatas4/android/feature/session/SessionViewModel;)Landroid/content/Context;

    move-result-object v2

    invoke-virtual {v2}, Landroid/content/Context;->getPackageName()Ljava/lang/String;

    move-result-object v2

    const-string v3, "com.bachatas4.android.service.EmulationService"

    invoke-virtual {v1, v2, v3}, Landroid/content/Intent;->setClassName(Ljava/lang/String;Ljava/lang/String;)Landroid/content/Intent;

    move-result-object v1

    .line 64
    const-string v2, "game_id"

    invoke-virtual {p1}, Lcom/bachatas4/android/model/Game;->getId()Ljava/lang/String;

    move-result-object v3

    invoke-virtual {v1, v2, v3}, Landroid/content/Intent;->putExtra(Ljava/lang/String;Ljava/lang/String;)Landroid/content/Intent;

    move-result-object v1

    .line 65
    const-string v2, "game_path"

    invoke-virtual {p1}, Lcom/bachatas4/android/model/Game;->getRelativePath()Ljava/lang/String;

    move-result-object p1

    invoke-virtual {v1, v2, p1}, Landroid/content/Intent;->putExtra(Ljava/lang/String;Ljava/lang/String;)Landroid/content/Intent;

    move-result-object p1

    .line 68
    sget-object v1, Lcom/bachatas4/android/runtime/process/RuntimeVulkanDriverPreference;->INSTANCE:Lcom/bachatas4/android/runtime/process/RuntimeVulkanDriverPreference;

    .line 69
    iget-object p0, p0, Lcom/bachatas4/android/feature/session/SessionViewModel$launch$1;->this$0:Lcom/bachatas4/android/feature/session/SessionViewModel;

    invoke-static {p0}, Lcom/bachatas4/android/feature/session/SessionViewModel;->access$getContext$p(Lcom/bachatas4/android/feature/session/SessionViewModel;)Landroid/content/Context;

    move-result-object p0

    .line 70
    const-string v2, "emulator_settings"

    const/4 v3, 0x0

    .line 69
    invoke-virtual {p0, v2, v3}, Landroid/content/Context;->getSharedPreferences(Ljava/lang/String;I)Landroid/content/SharedPreferences;

    move-result-object p0

    const/4 v2, 0x0

    .line 72
    const-string v3, "vulkan_driver"

    invoke-interface {p0, v3, v2}, Landroid/content/SharedPreferences;->getString(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;

    move-result-object p0

    .line 68
    invoke-virtual {v1, p0}, Lcom/bachatas4/android/runtime/process/RuntimeVulkanDriverPreference;->decode(Ljava/lang/String;)Lcom/bachatas4/android/runtime/process/RuntimeVulkanDriver;

    move-result-object p0

    .line 73
    invoke-virtual {p0}, Lcom/bachatas4/android/runtime/process/RuntimeVulkanDriver;->name()Ljava/lang/String;

    move-result-object p0

    .line 66
    invoke-virtual {p1, v3, p0}, Landroid/content/Intent;->putExtra(Ljava/lang/String;Ljava/lang/String;)Landroid/content/Intent;

    move-result-object p0

    .line 61
    invoke-virtual {v0, p0}, Landroid/content/Context;->startService(Landroid/content/Intent;)Landroid/content/ComponentName;

    .line 76
    sget-object p0, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;

    return-object p0
.end method
