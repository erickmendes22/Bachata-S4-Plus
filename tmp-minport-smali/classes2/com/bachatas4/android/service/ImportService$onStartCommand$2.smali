.class final Lcom/bachatas4/android/service/ImportService$onStartCommand$2;
.super Lkotlin/coroutines/jvm/internal/SuspendLambda;
.source "ImportService.kt"

# interfaces
.implements Lkotlin/jvm/functions/Function2;


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lcom/bachatas4/android/service/ImportService;->onStartCommand(Landroid/content/Intent;II)I
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
    c = "com.bachatas4.android.service.ImportService$onStartCommand$2"
    f = "ImportService.kt"
    i = {}
    l = {
        0x9b,
        0x9c
    }
    m = "invokeSuspend"
    n = {}
    nl = {
        0x9c,
        0x9e
    }
    s = {}
    v = 0x2
.end annotation


# instance fields
.field final synthetic $mode:Ljava/lang/String;

.field final synthetic $uriString:Ljava/lang/String;

.field label:I

.field final synthetic this$0:Lcom/bachatas4/android/service/ImportService;


# direct methods
.method constructor <init>(Ljava/lang/String;Lcom/bachatas4/android/service/ImportService;Ljava/lang/String;Lkotlin/coroutines/Continuation;)V
    .locals 0
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "(",
            "Ljava/lang/String;",
            "Lcom/bachatas4/android/service/ImportService;",
            "Ljava/lang/String;",
            "Lkotlin/coroutines/Continuation<",
            "-",
            "Lcom/bachatas4/android/service/ImportService$onStartCommand$2;",
            ">;)V"
        }
    .end annotation

    iput-object p1, p0, Lcom/bachatas4/android/service/ImportService$onStartCommand$2;->$mode:Ljava/lang/String;

    iput-object p2, p0, Lcom/bachatas4/android/service/ImportService$onStartCommand$2;->this$0:Lcom/bachatas4/android/service/ImportService;

    iput-object p3, p0, Lcom/bachatas4/android/service/ImportService$onStartCommand$2;->$uriString:Ljava/lang/String;

    const/4 p1, 0x2

    invoke-direct {p0, p1, p4}, Lkotlin/coroutines/jvm/internal/SuspendLambda;-><init>(ILkotlin/coroutines/Continuation;)V

    return-void
.end method


# virtual methods
.method public final create(Ljava/lang/Object;Lkotlin/coroutines/Continuation;)Lkotlin/coroutines/Continuation;
    .locals 2
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

    new-instance p1, Lcom/bachatas4/android/service/ImportService$onStartCommand$2;

    iget-object v0, p0, Lcom/bachatas4/android/service/ImportService$onStartCommand$2;->$mode:Ljava/lang/String;

    iget-object v1, p0, Lcom/bachatas4/android/service/ImportService$onStartCommand$2;->this$0:Lcom/bachatas4/android/service/ImportService;

    iget-object p0, p0, Lcom/bachatas4/android/service/ImportService$onStartCommand$2;->$uriString:Ljava/lang/String;

    invoke-direct {p1, v0, v1, p0, p2}, Lcom/bachatas4/android/service/ImportService$onStartCommand$2;-><init>(Ljava/lang/String;Lcom/bachatas4/android/service/ImportService;Ljava/lang/String;Lkotlin/coroutines/Continuation;)V

    check-cast p1, Lkotlin/coroutines/Continuation;

    return-object p1
.end method

.method public bridge synthetic invoke(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;
    .locals 0

    check-cast p1, Lkotlinx/coroutines/CoroutineScope;

    check-cast p2, Lkotlin/coroutines/Continuation;

    invoke-virtual {p0, p1, p2}, Lcom/bachatas4/android/service/ImportService$onStartCommand$2;->invoke(Lkotlinx/coroutines/CoroutineScope;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;

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

    invoke-virtual {p0, p1, p2}, Lcom/bachatas4/android/service/ImportService$onStartCommand$2;->create(Ljava/lang/Object;Lkotlin/coroutines/Continuation;)Lkotlin/coroutines/Continuation;

    move-result-object p0

    check-cast p0, Lcom/bachatas4/android/service/ImportService$onStartCommand$2;

    sget-object p1, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;

    invoke-virtual {p0, p1}, Lcom/bachatas4/android/service/ImportService$onStartCommand$2;->invokeSuspend(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object p0

    return-object p0
.end method

.method public final invokeSuspend(Ljava/lang/Object;)Ljava/lang/Object;
    .locals 4

    invoke-static {}, Lkotlin/coroutines/intrinsics/IntrinsicsKt;->getCOROUTINE_SUSPENDED()Ljava/lang/Object;

    move-result-object v0

    .line 153
    iget v1, p0, Lcom/bachatas4/android/service/ImportService$onStartCommand$2;->label:I

    const/4 v2, 0x2

    const/4 v3, 0x1

    if-eqz v1, :cond_2

    if-eq v1, v3, :cond_1

    if-ne v1, v2, :cond_0

    goto :goto_0

    :cond_0
    new-instance p0, Ljava/lang/IllegalStateException;

    const-string p1, "call to \'resume\' before \'invoke\' with coroutine"

    invoke-direct {p0, p1}, Ljava/lang/IllegalStateException;-><init>(Ljava/lang/String;)V

    throw p0

    :cond_1
    :goto_0
    invoke-static {p1}, Lkotlin/ResultKt;->throwOnFailure(Ljava/lang/Object;)V

    goto :goto_2

    :cond_2
    invoke-static {p1}, Lkotlin/ResultKt;->throwOnFailure(Ljava/lang/Object;)V

    .line 154
    iget-object p1, p0, Lcom/bachatas4/android/service/ImportService$onStartCommand$2;->$mode:Ljava/lang/String;

    .line 155
    const-string v1, "pkg"

    invoke-static {p1, v1}, Lkotlin/jvm/internal/Intrinsics;->areEqual(Ljava/lang/Object;Ljava/lang/Object;)Z

    move-result p1

    .line 156
    iget-object v1, p0, Lcom/bachatas4/android/service/ImportService$onStartCommand$2;->this$0:Lcom/bachatas4/android/service/ImportService;

    if-eqz p1, :cond_3

    .line 155
    iget-object p1, p0, Lcom/bachatas4/android/service/ImportService$onStartCommand$2;->$uriString:Ljava/lang/String;

    move-object v2, p0

    check-cast v2, Lkotlin/coroutines/Continuation;

    iput v3, p0, Lcom/bachatas4/android/service/ImportService$onStartCommand$2;->label:I

    invoke-static {v1, p1, v2}, Lcom/bachatas4/android/service/ImportService;->access$runPkgImport(Lcom/bachatas4/android/service/ImportService;Ljava/lang/String;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;

    move-result-object p0

    if-ne p0, v0, :cond_4

    goto :goto_1

    .line 156
    :cond_3
    iget-object p1, p0, Lcom/bachatas4/android/service/ImportService$onStartCommand$2;->$uriString:Ljava/lang/String;

    move-object v3, p0

    check-cast v3, Lkotlin/coroutines/Continuation;

    iput v2, p0, Lcom/bachatas4/android/service/ImportService$onStartCommand$2;->label:I

    invoke-static {v1, p1, v3}, Lcom/bachatas4/android/service/ImportService;->access$runFolderImport(Lcom/bachatas4/android/service/ImportService;Ljava/lang/String;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;

    move-result-object p0

    if-ne p0, v0, :cond_4

    :goto_1
    return-object v0

    .line 158
    :cond_4
    :goto_2
    sget-object p0, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;

    return-object p0
.end method
