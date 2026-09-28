.class final Lcom/bachatas4/android/data/ContentImporter$overlayStaging$2;
.super Lkotlin/coroutines/jvm/internal/SuspendLambda;
.source "ContentImporter.kt"

# interfaces
.implements Lkotlin/jvm/functions/Function2;


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lcom/bachatas4/android/data/ContentImporter;->overlayStaging(Ljava/lang/String;Ljava/io/File;Ljava/lang/String;Ljava/lang/String;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;
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
        "Lcom/bachatas4/android/data/OverlayResult;",
        ">;",
        "Ljava/lang/Object;",
        ">;"
    }
.end annotation

.annotation system Ldalvik/annotation/SourceDebugExtension;
    value = "SMAP\nContentImporter.kt\nKotlin\n*S Kotlin\n*F\n+ 1 ContentImporter.kt\ncom/bachatas4/android/data/ContentImporter$overlayStaging$2\n+ 2 _Sequences.kt\nkotlin/sequences/SequencesKt___SequencesKt\n*L\n1#1,434:1\n1505#2,2:435\n*S KotlinDebug\n*F\n+ 1 ContentImporter.kt\ncom/bachatas4/android/data/ContentImporter$overlayStaging$2\n*L\n344#1:435,2\n*E\n"
.end annotation

.annotation runtime Lkotlin/Metadata;
    d1 = {
        "\u0000\n\n\u0000\n\u0002\u0018\u0002\n\u0002\u0018\u0002\u0010\u0000\u001a\u00020\u0001*\u00020\u0002H\n"
    }
    d2 = {
        "<anonymous>",
        "Lcom/bachatas4/android/data/OverlayResult;",
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
    c = "com.bachatas4.android.data.ContentImporter$overlayStaging$2"
    f = "ContentImporter.kt"
    i = {}
    l = {}
    m = "invokeSuspend"
    n = {}
    nl = {}
    s = {}
    v = 0x2
.end annotation


# instance fields
.field final synthetic $gameId:Ljava/lang/String;

.field final synthetic $stagingDir:Ljava/io/File;

.field private synthetic L$0:Ljava/lang/Object;

.field label:I

.field final synthetic this$0:Lcom/bachatas4/android/data/ContentImporter;


# direct methods
.method constructor <init>(Lcom/bachatas4/android/data/ContentImporter;Ljava/lang/String;Ljava/io/File;Lkotlin/coroutines/Continuation;)V
    .locals 0
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "(",
            "Lcom/bachatas4/android/data/ContentImporter;",
            "Ljava/lang/String;",
            "Ljava/io/File;",
            "Lkotlin/coroutines/Continuation<",
            "-",
            "Lcom/bachatas4/android/data/ContentImporter$overlayStaging$2;",
            ">;)V"
        }
    .end annotation

    iput-object p1, p0, Lcom/bachatas4/android/data/ContentImporter$overlayStaging$2;->this$0:Lcom/bachatas4/android/data/ContentImporter;

    iput-object p2, p0, Lcom/bachatas4/android/data/ContentImporter$overlayStaging$2;->$gameId:Ljava/lang/String;

    iput-object p3, p0, Lcom/bachatas4/android/data/ContentImporter$overlayStaging$2;->$stagingDir:Ljava/io/File;

    const/4 p1, 0x2

    invoke-direct {p0, p1, p4}, Lkotlin/coroutines/jvm/internal/SuspendLambda;-><init>(ILkotlin/coroutines/Continuation;)V

    return-void
.end method


# virtual methods
.method public final create(Ljava/lang/Object;Lkotlin/coroutines/Continuation;)Lkotlin/coroutines/Continuation;
    .locals 3
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

    new-instance v0, Lcom/bachatas4/android/data/ContentImporter$overlayStaging$2;

    iget-object v1, p0, Lcom/bachatas4/android/data/ContentImporter$overlayStaging$2;->this$0:Lcom/bachatas4/android/data/ContentImporter;

    iget-object v2, p0, Lcom/bachatas4/android/data/ContentImporter$overlayStaging$2;->$gameId:Ljava/lang/String;

    iget-object p0, p0, Lcom/bachatas4/android/data/ContentImporter$overlayStaging$2;->$stagingDir:Ljava/io/File;

    invoke-direct {v0, v1, v2, p0, p2}, Lcom/bachatas4/android/data/ContentImporter$overlayStaging$2;-><init>(Lcom/bachatas4/android/data/ContentImporter;Ljava/lang/String;Ljava/io/File;Lkotlin/coroutines/Continuation;)V

    iput-object p1, v0, Lcom/bachatas4/android/data/ContentImporter$overlayStaging$2;->L$0:Ljava/lang/Object;

    check-cast v0, Lkotlin/coroutines/Continuation;

    return-object v0
.end method

.method public bridge synthetic invoke(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;
    .locals 0

    check-cast p1, Lkotlinx/coroutines/CoroutineScope;

    check-cast p2, Lkotlin/coroutines/Continuation;

    invoke-virtual {p0, p1, p2}, Lcom/bachatas4/android/data/ContentImporter$overlayStaging$2;->invoke(Lkotlinx/coroutines/CoroutineScope;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;

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
            "Lcom/bachatas4/android/data/OverlayResult;",
            ">;)",
            "Ljava/lang/Object;"
        }
    .end annotation

    invoke-virtual {p0, p1, p2}, Lcom/bachatas4/android/data/ContentImporter$overlayStaging$2;->create(Ljava/lang/Object;Lkotlin/coroutines/Continuation;)Lkotlin/coroutines/Continuation;

    move-result-object p0

    check-cast p0, Lcom/bachatas4/android/data/ContentImporter$overlayStaging$2;

    sget-object p1, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;

    invoke-virtual {p0, p1}, Lcom/bachatas4/android/data/ContentImporter$overlayStaging$2;->invokeSuspend(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object p0

    return-object p0
.end method

.method public final invokeSuspend(Ljava/lang/Object;)Ljava/lang/Object;
    .locals 13

    iget-object v0, p0, Lcom/bachatas4/android/data/ContentImporter$overlayStaging$2;->L$0:Ljava/lang/Object;

    check-cast v0, Lkotlinx/coroutines/CoroutineScope;

    invoke-static {}, Lkotlin/coroutines/intrinsics/IntrinsicsKt;->getCOROUTINE_SUSPENDED()Ljava/lang/Object;

    .line 331
    iget v1, p0, Lcom/bachatas4/android/data/ContentImporter$overlayStaging$2;->label:I

    if-nez v1, :cond_4

    invoke-static {p1}, Lkotlin/ResultKt;->throwOnFailure(Ljava/lang/Object;)V

    .line 332
    iget-object p1, p0, Lcom/bachatas4/android/data/ContentImporter$overlayStaging$2;->this$0:Lcom/bachatas4/android/data/ContentImporter;

    iget-object v1, p0, Lcom/bachatas4/android/data/ContentImporter$overlayStaging$2;->$gameId:Ljava/lang/String;

    invoke-static {p1, v1}, Lcom/bachatas4/android/data/ContentImporter;->access$validateGameId(Lcom/bachatas4/android/data/ContentImporter;Ljava/lang/String;)V

    .line 333
    new-instance p1, Ljava/io/File;

    iget-object v1, p0, Lcom/bachatas4/android/data/ContentImporter$overlayStaging$2;->this$0:Lcom/bachatas4/android/data/ContentImporter;

    invoke-static {v1}, Lcom/bachatas4/android/data/ContentImporter;->access$getFilesDir$p(Lcom/bachatas4/android/data/ContentImporter;)Ljava/io/File;

    move-result-object v1

    const-string v2, "games"

    invoke-direct {p1, v1, v2}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    invoke-virtual {p1}, Ljava/io/File;->getCanonicalFile()Ljava/io/File;

    move-result-object p1

    .line 334
    new-instance v1, Ljava/io/File;

    iget-object v2, p0, Lcom/bachatas4/android/data/ContentImporter$overlayStaging$2;->$gameId:Ljava/lang/String;

    invoke-direct {v1, p1, v2}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    invoke-virtual {v1}, Ljava/io/File;->getCanonicalFile()Ljava/io/File;

    move-result-object v1

    .line 335
    iget-object v2, p0, Lcom/bachatas4/android/data/ContentImporter$overlayStaging$2;->$stagingDir:Ljava/io/File;

    invoke-virtual {v2}, Ljava/io/File;->getCanonicalFile()Ljava/io/File;

    move-result-object v2

    .line 336
    iget-object v3, p0, Lcom/bachatas4/android/data/ContentImporter$overlayStaging$2;->this$0:Lcom/bachatas4/android/data/ContentImporter;

    invoke-static {p1}, Lkotlin/jvm/internal/Intrinsics;->checkNotNull(Ljava/lang/Object;)V

    invoke-static {v1}, Lkotlin/jvm/internal/Intrinsics;->checkNotNull(Ljava/lang/Object;)V

    invoke-static {v3, p1, v1}, Lcom/bachatas4/android/data/ContentImporter;->access$requireInside(Lcom/bachatas4/android/data/ContentImporter;Ljava/io/File;Ljava/io/File;)V

    .line 337
    iget-object v3, p0, Lcom/bachatas4/android/data/ContentImporter$overlayStaging$2;->this$0:Lcom/bachatas4/android/data/ContentImporter;

    invoke-static {v2}, Lkotlin/jvm/internal/Intrinsics;->checkNotNull(Ljava/lang/Object;)V

    invoke-static {v3, p1, v2}, Lcom/bachatas4/android/data/ContentImporter;->access$requireInside(Lcom/bachatas4/android/data/ContentImporter;Ljava/io/File;Ljava/io/File;)V

    .line 338
    invoke-virtual {v1}, Ljava/io/File;->isDirectory()Z

    move-result p1

    if-eqz p1, :cond_3

    .line 344
    invoke-static {v2}, Lkotlin/io/FilesKt;->walkTopDown(Ljava/io/File;)Lkotlin/io/FileTreeWalk;

    move-result-object p1

    check-cast p1, Lkotlin/sequences/Sequence;

    iget-object p0, p0, Lcom/bachatas4/android/data/ContentImporter$overlayStaging$2;->this$0:Lcom/bachatas4/android/data/ContentImporter;

    .line 435
    invoke-interface {p1}, Lkotlin/sequences/Sequence;->iterator()Ljava/util/Iterator;

    move-result-object p1

    const/4 v3, 0x0

    const-wide/16 v4, 0x0

    :cond_0
    :goto_0
    invoke-interface {p1}, Ljava/util/Iterator;->hasNext()Z

    move-result v6

    if-eqz v6, :cond_2

    invoke-interface {p1}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v6

    move-object v7, v6

    check-cast v7, Ljava/io/File;

    .line 345
    invoke-virtual {v7}, Ljava/io/File;->isFile()Z

    move-result v6

    if-eqz v6, :cond_0

    .line 346
    invoke-static {v7, v2}, Lkotlin/io/FilesKt;->relativeTo(Ljava/io/File;Ljava/io/File;)Ljava/io/File;

    move-result-object v6

    invoke-virtual {v6}, Ljava/io/File;->getPath()Ljava/lang/String;

    move-result-object v6

    .line 347
    new-instance v8, Ljava/io/File;

    invoke-direct {v8, v1, v6}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    invoke-virtual {v8}, Ljava/io/File;->getCanonicalFile()Ljava/io/File;

    move-result-object v8

    .line 348
    invoke-static {v8}, Lkotlin/jvm/internal/Intrinsics;->checkNotNull(Ljava/lang/Object;)V

    invoke-static {p0, v1, v8}, Lcom/bachatas4/android/data/ContentImporter;->access$requireInside(Lcom/bachatas4/android/data/ContentImporter;Ljava/io/File;Ljava/io/File;)V

    .line 349
    invoke-virtual {v8}, Ljava/io/File;->getParentFile()Ljava/io/File;

    move-result-object v6

    if-eqz v6, :cond_1

    invoke-virtual {v6}, Ljava/io/File;->mkdirs()Z

    move-result v6

    invoke-static {v6}, Lkotlin/coroutines/jvm/internal/Boxing;->boxBoolean(Z)Ljava/lang/Boolean;

    .line 350
    :cond_1
    invoke-interface {v0}, Lkotlinx/coroutines/CoroutineScope;->getCoroutineContext()Lkotlin/coroutines/CoroutineContext;

    move-result-object v6

    invoke-static {v6}, Lkotlinx/coroutines/JobKt;->ensureActive(Lkotlin/coroutines/CoroutineContext;)V

    const/4 v11, 0x4

    const/4 v12, 0x0

    const/4 v9, 0x1

    const/4 v10, 0x0

    .line 351
    invoke-static/range {v7 .. v12}, Lkotlin/io/FilesKt;->copyTo$default(Ljava/io/File;Ljava/io/File;ZIILjava/lang/Object;)Ljava/io/File;

    add-int/lit8 v3, v3, 0x1

    .line 353
    invoke-virtual {v7}, Ljava/io/File;->length()J

    move-result-wide v6

    add-long/2addr v4, v6

    goto :goto_0

    .line 355
    :cond_2
    new-instance p0, Lcom/bachatas4/android/data/OverlayResult;

    invoke-direct {p0, v3, v4, v5}, Lcom/bachatas4/android/data/OverlayResult;-><init>(IJ)V

    return-object p0

    .line 339
    :cond_3
    new-instance v6, Lcom/bachatas4/android/data/ContentImportException;

    sget-object v7, Lcom/bachatas4/android/model/RuntimeErrorCode;->CONTENT_INVALID:Lcom/bachatas4/android/model/RuntimeErrorCode;

    const/4 v10, 0x4

    const/4 v11, 0x0

    const-string v8, "Base game not installed"

    const/4 v9, 0x0

    invoke-direct/range {v6 .. v11}, Lcom/bachatas4/android/data/ContentImportException;-><init>(Lcom/bachatas4/android/model/RuntimeErrorCode;Ljava/lang/String;Ljava/lang/Throwable;ILkotlin/jvm/internal/DefaultConstructorMarker;)V

    throw v6

    .line 331
    :cond_4
    new-instance p0, Ljava/lang/IllegalStateException;

    const-string p1, "call to \'resume\' before \'invoke\' with coroutine"

    invoke-direct {p0, p1}, Ljava/lang/IllegalStateException;-><init>(Ljava/lang/String;)V

    throw p0
.end method
