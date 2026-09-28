.class final Lcom/bachatas4/android/service/ImportService$runPkgImport$7$result$1;
.super Lkotlin/coroutines/jvm/internal/SuspendLambda;
.source "ImportService.kt"

# interfaces
.implements Lkotlin/jvm/functions/Function2;


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lcom/bachatas4/android/service/ImportService;->runPkgImport(Ljava/lang/String;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;
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
        "Lcom/bachatas4/android/runtime/pkg/PkgExtractResult;",
        ">;",
        "Ljava/lang/Object;",
        ">;"
    }
.end annotation

.annotation runtime Lkotlin/Metadata;
    d1 = {
        "\u0000\n\n\u0000\n\u0002\u0018\u0002\n\u0002\u0018\u0002\u0010\u0000\u001a\u00020\u0001*\u00020\u0002H\n"
    }
    d2 = {
        "<anonymous>",
        "Lcom/bachatas4/android/runtime/pkg/PkgExtractResult;",
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
    c = "com.bachatas4.android.service.ImportService$runPkgImport$7$result$1"
    f = "ImportService.kt"
    i = {}
    l = {}
    m = "invokeSuspend"
    n = {}
    nl = {}
    s = {}
    v = 0x2
.end annotation


# instance fields
.field final synthetic $candidate:Ljava/lang/String;

.field final synthetic $displayName:Ljava/lang/String;

.field final synthetic $fd:I

.field final synthetic $staging:Lkotlin/jvm/internal/Ref$ObjectRef;
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "Lkotlin/jvm/internal/Ref$ObjectRef<",
            "Ljava/io/File;",
            ">;"
        }
    .end annotation
.end field

.field label:I

.field final synthetic this$0:Lcom/bachatas4/android/service/ImportService;


# direct methods
.method constructor <init>(Lcom/bachatas4/android/service/ImportService;ILkotlin/jvm/internal/Ref$ObjectRef;Ljava/lang/String;Ljava/lang/String;Lkotlin/coroutines/Continuation;)V
    .locals 0
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "(",
            "Lcom/bachatas4/android/service/ImportService;",
            "I",
            "Lkotlin/jvm/internal/Ref$ObjectRef<",
            "Ljava/io/File;",
            ">;",
            "Ljava/lang/String;",
            "Ljava/lang/String;",
            "Lkotlin/coroutines/Continuation<",
            "-",
            "Lcom/bachatas4/android/service/ImportService$runPkgImport$7$result$1;",
            ">;)V"
        }
    .end annotation

    iput-object p1, p0, Lcom/bachatas4/android/service/ImportService$runPkgImport$7$result$1;->this$0:Lcom/bachatas4/android/service/ImportService;

    iput p2, p0, Lcom/bachatas4/android/service/ImportService$runPkgImport$7$result$1;->$fd:I

    iput-object p3, p0, Lcom/bachatas4/android/service/ImportService$runPkgImport$7$result$1;->$staging:Lkotlin/jvm/internal/Ref$ObjectRef;

    iput-object p4, p0, Lcom/bachatas4/android/service/ImportService$runPkgImport$7$result$1;->$candidate:Ljava/lang/String;

    iput-object p5, p0, Lcom/bachatas4/android/service/ImportService$runPkgImport$7$result$1;->$displayName:Ljava/lang/String;

    const/4 p1, 0x2

    invoke-direct {p0, p1, p6}, Lkotlin/coroutines/jvm/internal/SuspendLambda;-><init>(ILkotlin/coroutines/Continuation;)V

    return-void
.end method


# virtual methods
.method public final create(Ljava/lang/Object;Lkotlin/coroutines/Continuation;)Lkotlin/coroutines/Continuation;
    .locals 7
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

    new-instance v0, Lcom/bachatas4/android/service/ImportService$runPkgImport$7$result$1;

    iget-object v1, p0, Lcom/bachatas4/android/service/ImportService$runPkgImport$7$result$1;->this$0:Lcom/bachatas4/android/service/ImportService;

    iget v2, p0, Lcom/bachatas4/android/service/ImportService$runPkgImport$7$result$1;->$fd:I

    iget-object v3, p0, Lcom/bachatas4/android/service/ImportService$runPkgImport$7$result$1;->$staging:Lkotlin/jvm/internal/Ref$ObjectRef;

    iget-object v4, p0, Lcom/bachatas4/android/service/ImportService$runPkgImport$7$result$1;->$candidate:Ljava/lang/String;

    iget-object v5, p0, Lcom/bachatas4/android/service/ImportService$runPkgImport$7$result$1;->$displayName:Ljava/lang/String;

    move-object v6, p2

    invoke-direct/range {v0 .. v6}, Lcom/bachatas4/android/service/ImportService$runPkgImport$7$result$1;-><init>(Lcom/bachatas4/android/service/ImportService;ILkotlin/jvm/internal/Ref$ObjectRef;Ljava/lang/String;Ljava/lang/String;Lkotlin/coroutines/Continuation;)V

    check-cast v0, Lkotlin/coroutines/Continuation;

    return-object v0
.end method

.method public bridge synthetic invoke(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;
    .locals 0

    check-cast p1, Lkotlinx/coroutines/CoroutineScope;

    check-cast p2, Lkotlin/coroutines/Continuation;

    invoke-virtual {p0, p1, p2}, Lcom/bachatas4/android/service/ImportService$runPkgImport$7$result$1;->invoke(Lkotlinx/coroutines/CoroutineScope;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;

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
            "Lcom/bachatas4/android/runtime/pkg/PkgExtractResult;",
            ">;)",
            "Ljava/lang/Object;"
        }
    .end annotation

    invoke-virtual {p0, p1, p2}, Lcom/bachatas4/android/service/ImportService$runPkgImport$7$result$1;->create(Ljava/lang/Object;Lkotlin/coroutines/Continuation;)Lkotlin/coroutines/Continuation;

    move-result-object p0

    check-cast p0, Lcom/bachatas4/android/service/ImportService$runPkgImport$7$result$1;

    sget-object p1, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;

    invoke-virtual {p0, p1}, Lcom/bachatas4/android/service/ImportService$runPkgImport$7$result$1;->invokeSuspend(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object p0

    return-object p0
.end method

.method public final invokeSuspend(Ljava/lang/Object;)Ljava/lang/Object;
    .locals 3

    invoke-static {}, Lkotlin/coroutines/intrinsics/IntrinsicsKt;->getCOROUTINE_SUSPENDED()Ljava/lang/Object;

    .line 535
    iget v0, p0, Lcom/bachatas4/android/service/ImportService$runPkgImport$7$result$1;->label:I

    if-nez v0, :cond_0

    invoke-static {p1}, Lkotlin/ResultKt;->throwOnFailure(Ljava/lang/Object;)V

    .line 536
    iget-object p1, p0, Lcom/bachatas4/android/service/ImportService$runPkgImport$7$result$1;->this$0:Lcom/bachatas4/android/service/ImportService;

    iget v0, p0, Lcom/bachatas4/android/service/ImportService$runPkgImport$7$result$1;->$fd:I

    iget-object v1, p0, Lcom/bachatas4/android/service/ImportService$runPkgImport$7$result$1;->$staging:Lkotlin/jvm/internal/Ref$ObjectRef;

    iget-object v1, v1, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    invoke-static {v1}, Lkotlin/jvm/internal/Intrinsics;->checkNotNull(Ljava/lang/Object;)V

    check-cast v1, Ljava/io/File;

    iget-object v2, p0, Lcom/bachatas4/android/service/ImportService$runPkgImport$7$result$1;->$candidate:Ljava/lang/String;

    iget-object p0, p0, Lcom/bachatas4/android/service/ImportService$runPkgImport$7$result$1;->$displayName:Ljava/lang/String;

    invoke-static {p1, v0, v1, v2, p0}, Lcom/bachatas4/android/service/ImportService;->access$extractWithProgress(Lcom/bachatas4/android/service/ImportService;ILjava/io/File;Ljava/lang/String;Ljava/lang/String;)Lcom/bachatas4/android/runtime/pkg/PkgExtractResult;

    move-result-object p0

    return-object p0

    .line 535
    :cond_0
    new-instance p0, Ljava/lang/IllegalStateException;

    const-string p1, "call to \'resume\' before \'invoke\' with coroutine"

    invoke-direct {p0, p1}, Ljava/lang/IllegalStateException;-><init>(Ljava/lang/String;)V

    throw p0
.end method
