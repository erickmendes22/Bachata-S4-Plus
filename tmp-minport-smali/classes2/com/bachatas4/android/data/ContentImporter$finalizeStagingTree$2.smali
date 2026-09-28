.class final Lcom/bachatas4/android/data/ContentImporter$finalizeStagingTree$2;
.super Lkotlin/coroutines/jvm/internal/SuspendLambda;
.source "ContentImporter.kt"

# interfaces
.implements Lkotlin/jvm/functions/Function2;


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lcom/bachatas4/android/data/ContentImporter;->finalizeStagingTree(Lcom/bachatas4/android/data/ContentImportRequest;Ljava/io/File;Ljava/lang/String;Ljava/lang/String;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;
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
        "Lcom/bachatas4/android/data/ContentImportResult;",
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
        "Lcom/bachatas4/android/data/ContentImportResult;",
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
    c = "com.bachatas4.android.data.ContentImporter$finalizeStagingTree$2"
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
.field final synthetic $contentId:Ljava/lang/String;

.field final synthetic $mode:Ljava/lang/String;

.field final synthetic $request:Lcom/bachatas4/android/data/ContentImportRequest;

.field final synthetic $stagingDir:Ljava/io/File;

.field label:I

.field final synthetic this$0:Lcom/bachatas4/android/data/ContentImporter;


# direct methods
.method constructor <init>(Lcom/bachatas4/android/data/ContentImporter;Lcom/bachatas4/android/data/ContentImportRequest;Ljava/io/File;Ljava/lang/String;Ljava/lang/String;Lkotlin/coroutines/Continuation;)V
    .locals 0
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "(",
            "Lcom/bachatas4/android/data/ContentImporter;",
            "Lcom/bachatas4/android/data/ContentImportRequest;",
            "Ljava/io/File;",
            "Ljava/lang/String;",
            "Ljava/lang/String;",
            "Lkotlin/coroutines/Continuation<",
            "-",
            "Lcom/bachatas4/android/data/ContentImporter$finalizeStagingTree$2;",
            ">;)V"
        }
    .end annotation

    iput-object p1, p0, Lcom/bachatas4/android/data/ContentImporter$finalizeStagingTree$2;->this$0:Lcom/bachatas4/android/data/ContentImporter;

    iput-object p2, p0, Lcom/bachatas4/android/data/ContentImporter$finalizeStagingTree$2;->$request:Lcom/bachatas4/android/data/ContentImportRequest;

    iput-object p3, p0, Lcom/bachatas4/android/data/ContentImporter$finalizeStagingTree$2;->$stagingDir:Ljava/io/File;

    iput-object p4, p0, Lcom/bachatas4/android/data/ContentImporter$finalizeStagingTree$2;->$mode:Ljava/lang/String;

    iput-object p5, p0, Lcom/bachatas4/android/data/ContentImporter$finalizeStagingTree$2;->$contentId:Ljava/lang/String;

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

    new-instance v0, Lcom/bachatas4/android/data/ContentImporter$finalizeStagingTree$2;

    iget-object v1, p0, Lcom/bachatas4/android/data/ContentImporter$finalizeStagingTree$2;->this$0:Lcom/bachatas4/android/data/ContentImporter;

    iget-object v2, p0, Lcom/bachatas4/android/data/ContentImporter$finalizeStagingTree$2;->$request:Lcom/bachatas4/android/data/ContentImportRequest;

    iget-object v3, p0, Lcom/bachatas4/android/data/ContentImporter$finalizeStagingTree$2;->$stagingDir:Ljava/io/File;

    iget-object v4, p0, Lcom/bachatas4/android/data/ContentImporter$finalizeStagingTree$2;->$mode:Ljava/lang/String;

    iget-object v5, p0, Lcom/bachatas4/android/data/ContentImporter$finalizeStagingTree$2;->$contentId:Ljava/lang/String;

    move-object v6, p2

    invoke-direct/range {v0 .. v6}, Lcom/bachatas4/android/data/ContentImporter$finalizeStagingTree$2;-><init>(Lcom/bachatas4/android/data/ContentImporter;Lcom/bachatas4/android/data/ContentImportRequest;Ljava/io/File;Ljava/lang/String;Ljava/lang/String;Lkotlin/coroutines/Continuation;)V

    check-cast v0, Lkotlin/coroutines/Continuation;

    return-object v0
.end method

.method public bridge synthetic invoke(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;
    .locals 0

    check-cast p1, Lkotlinx/coroutines/CoroutineScope;

    check-cast p2, Lkotlin/coroutines/Continuation;

    invoke-virtual {p0, p1, p2}, Lcom/bachatas4/android/data/ContentImporter$finalizeStagingTree$2;->invoke(Lkotlinx/coroutines/CoroutineScope;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;

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
            "Lcom/bachatas4/android/data/ContentImportResult;",
            ">;)",
            "Ljava/lang/Object;"
        }
    .end annotation

    invoke-virtual {p0, p1, p2}, Lcom/bachatas4/android/data/ContentImporter$finalizeStagingTree$2;->create(Ljava/lang/Object;Lkotlin/coroutines/Continuation;)Lkotlin/coroutines/Continuation;

    move-result-object p0

    check-cast p0, Lcom/bachatas4/android/data/ContentImporter$finalizeStagingTree$2;

    sget-object p1, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;

    invoke-virtual {p0, p1}, Lcom/bachatas4/android/data/ContentImporter$finalizeStagingTree$2;->invokeSuspend(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object p0

    return-object p0
.end method

.method public final invokeSuspend(Ljava/lang/Object;)Ljava/lang/Object;
    .locals 12

    invoke-static {}, Lkotlin/coroutines/intrinsics/IntrinsicsKt;->getCOROUTINE_SUSPENDED()Ljava/lang/Object;

    .line 163
    iget v0, p0, Lcom/bachatas4/android/data/ContentImporter$finalizeStagingTree$2;->label:I

    if-nez v0, :cond_2

    invoke-static {p1}, Lkotlin/ResultKt;->throwOnFailure(Ljava/lang/Object;)V

    .line 164
    iget-object p1, p0, Lcom/bachatas4/android/data/ContentImporter$finalizeStagingTree$2;->this$0:Lcom/bachatas4/android/data/ContentImporter;

    iget-object v0, p0, Lcom/bachatas4/android/data/ContentImporter$finalizeStagingTree$2;->$request:Lcom/bachatas4/android/data/ContentImportRequest;

    invoke-virtual {v0}, Lcom/bachatas4/android/data/ContentImportRequest;->getId()Ljava/lang/String;

    move-result-object v0

    invoke-static {p1, v0}, Lcom/bachatas4/android/data/ContentImporter;->access$validateGameId(Lcom/bachatas4/android/data/ContentImporter;Ljava/lang/String;)V

    .line 165
    new-instance p1, Ljava/io/File;

    iget-object v0, p0, Lcom/bachatas4/android/data/ContentImporter$finalizeStagingTree$2;->this$0:Lcom/bachatas4/android/data/ContentImporter;

    invoke-static {v0}, Lcom/bachatas4/android/data/ContentImporter;->access$getFilesDir$p(Lcom/bachatas4/android/data/ContentImporter;)Ljava/io/File;

    move-result-object v0

    const-string v1, "games"

    invoke-direct {p1, v0, v1}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    invoke-virtual {p1}, Ljava/io/File;->getCanonicalFile()Ljava/io/File;

    move-result-object p1

    .line 166
    invoke-virtual {p1}, Ljava/io/File;->mkdirs()Z

    .line 167
    new-instance v0, Ljava/io/File;

    iget-object v1, p0, Lcom/bachatas4/android/data/ContentImporter$finalizeStagingTree$2;->$request:Lcom/bachatas4/android/data/ContentImportRequest;

    invoke-virtual {v1}, Lcom/bachatas4/android/data/ContentImportRequest;->getId()Ljava/lang/String;

    move-result-object v1

    invoke-direct {v0, p1, v1}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    invoke-virtual {v0}, Ljava/io/File;->getCanonicalFile()Ljava/io/File;

    move-result-object v4

    .line 168
    iget-object v0, p0, Lcom/bachatas4/android/data/ContentImporter$finalizeStagingTree$2;->this$0:Lcom/bachatas4/android/data/ContentImporter;

    invoke-static {p1}, Lkotlin/jvm/internal/Intrinsics;->checkNotNull(Ljava/lang/Object;)V

    invoke-static {v4}, Lkotlin/jvm/internal/Intrinsics;->checkNotNull(Ljava/lang/Object;)V

    invoke-static {v0, p1, v4}, Lcom/bachatas4/android/data/ContentImporter;->access$requireInside(Lcom/bachatas4/android/data/ContentImporter;Ljava/io/File;Ljava/io/File;)V

    .line 169
    invoke-virtual {v4}, Ljava/io/File;->exists()Z

    move-result v0

    if-nez v0, :cond_1

    .line 172
    iget-object v0, p0, Lcom/bachatas4/android/data/ContentImporter$finalizeStagingTree$2;->$stagingDir:Ljava/io/File;

    invoke-virtual {v0}, Ljava/io/File;->getCanonicalFile()Ljava/io/File;

    move-result-object v3

    .line 173
    iget-object v0, p0, Lcom/bachatas4/android/data/ContentImporter$finalizeStagingTree$2;->this$0:Lcom/bachatas4/android/data/ContentImporter;

    invoke-static {v3}, Lkotlin/jvm/internal/Intrinsics;->checkNotNull(Ljava/lang/Object;)V

    invoke-static {v0, p1, v3}, Lcom/bachatas4/android/data/ContentImporter;->access$requireInside(Lcom/bachatas4/android/data/ContentImporter;Ljava/io/File;Ljava/io/File;)V

    .line 174
    invoke-virtual {v3}, Ljava/io/File;->isDirectory()Z

    move-result p1

    if-eqz p1, :cond_0

    .line 177
    iget-object v2, p0, Lcom/bachatas4/android/data/ContentImporter$finalizeStagingTree$2;->this$0:Lcom/bachatas4/android/data/ContentImporter;

    .line 180
    iget-object v5, p0, Lcom/bachatas4/android/data/ContentImporter$finalizeStagingTree$2;->$request:Lcom/bachatas4/android/data/ContentImportRequest;

    .line 181
    iget-object v6, p0, Lcom/bachatas4/android/data/ContentImporter$finalizeStagingTree$2;->$mode:Ljava/lang/String;

    .line 182
    iget-object v7, p0, Lcom/bachatas4/android/data/ContentImporter$finalizeStagingTree$2;->$contentId:Ljava/lang/String;

    const/4 v8, 0x1

    .line 177
    invoke-static/range {v2 .. v8}, Lcom/bachatas4/android/data/ContentImporter;->access$writeInstallManifestAndPromote(Lcom/bachatas4/android/data/ContentImporter;Ljava/io/File;Ljava/io/File;Lcom/bachatas4/android/data/ContentImportRequest;Ljava/lang/String;Ljava/lang/String;Z)J

    move-result-wide v0

    .line 185
    new-instance p1, Lcom/bachatas4/android/data/ContentImportResult;

    .line 186
    new-instance v2, Lcom/bachatas4/android/model/Game;

    .line 187
    iget-object v3, p0, Lcom/bachatas4/android/data/ContentImporter$finalizeStagingTree$2;->$request:Lcom/bachatas4/android/data/ContentImportRequest;

    invoke-virtual {v3}, Lcom/bachatas4/android/data/ContentImportRequest;->getId()Ljava/lang/String;

    move-result-object v3

    .line 188
    iget-object v4, p0, Lcom/bachatas4/android/data/ContentImporter$finalizeStagingTree$2;->$request:Lcom/bachatas4/android/data/ContentImportRequest;

    invoke-virtual {v4}, Lcom/bachatas4/android/data/ContentImportRequest;->getTitle()Ljava/lang/String;

    move-result-object v4

    .line 189
    iget-object v5, p0, Lcom/bachatas4/android/data/ContentImporter$finalizeStagingTree$2;->$request:Lcom/bachatas4/android/data/ContentImportRequest;

    invoke-virtual {v5}, Lcom/bachatas4/android/data/ContentImportRequest;->getId()Ljava/lang/String;

    move-result-object v5

    new-instance v6, Ljava/lang/StringBuilder;

    const-string v7, "games/"

    invoke-direct {v6, v7}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v6, v5}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v5

    invoke-virtual {v5}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v5

    .line 190
    iget-object v6, p0, Lcom/bachatas4/android/data/ContentImporter$finalizeStagingTree$2;->$request:Lcom/bachatas4/android/data/ContentImportRequest;

    invoke-virtual {v6}, Lcom/bachatas4/android/data/ContentImportRequest;->getSubtitle()Ljava/lang/String;

    move-result-object v6

    .line 191
    iget-object p0, p0, Lcom/bachatas4/android/data/ContentImporter$finalizeStagingTree$2;->$request:Lcom/bachatas4/android/data/ContentImportRequest;

    invoke-virtual {p0}, Lcom/bachatas4/android/data/ContentImportRequest;->getDetail()Ljava/lang/String;

    move-result-object v7

    const/16 v10, 0x20

    const/4 v11, 0x0

    const-wide/16 v8, 0x0

    .line 186
    invoke-direct/range {v2 .. v11}, Lcom/bachatas4/android/model/Game;-><init>(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;JILkotlin/jvm/internal/DefaultConstructorMarker;)V

    .line 194
    const-string p0, "pkg-extract"

    .line 185
    invoke-direct {p1, v2, v0, v1, p0}, Lcom/bachatas4/android/data/ContentImportResult;-><init>(Lcom/bachatas4/android/model/Game;JLjava/lang/String;)V

    return-object p1

    .line 175
    :cond_0
    new-instance v3, Lcom/bachatas4/android/data/ContentImportException;

    sget-object v4, Lcom/bachatas4/android/model/RuntimeErrorCode;->CONTENT_INVALID:Lcom/bachatas4/android/model/RuntimeErrorCode;

    const/4 v7, 0x4

    const/4 v8, 0x0

    const-string v5, "Staging directory missing"

    const/4 v6, 0x0

    invoke-direct/range {v3 .. v8}, Lcom/bachatas4/android/data/ContentImportException;-><init>(Lcom/bachatas4/android/model/RuntimeErrorCode;Ljava/lang/String;Ljava/lang/Throwable;ILkotlin/jvm/internal/DefaultConstructorMarker;)V

    throw v3

    .line 170
    :cond_1
    new-instance v4, Lcom/bachatas4/android/data/ContentImportException;

    sget-object v5, Lcom/bachatas4/android/model/RuntimeErrorCode;->CONTENT_INVALID:Lcom/bachatas4/android/model/RuntimeErrorCode;

    const/4 v8, 0x4

    const/4 v9, 0x0

    const-string v6, "Game already imported"

    const/4 v7, 0x0

    invoke-direct/range {v4 .. v9}, Lcom/bachatas4/android/data/ContentImportException;-><init>(Lcom/bachatas4/android/model/RuntimeErrorCode;Ljava/lang/String;Ljava/lang/Throwable;ILkotlin/jvm/internal/DefaultConstructorMarker;)V

    throw v4

    .line 163
    :cond_2
    new-instance p0, Ljava/lang/IllegalStateException;

    const-string p1, "call to \'resume\' before \'invoke\' with coroutine"

    invoke-direct {p0, p1}, Ljava/lang/IllegalStateException;-><init>(Ljava/lang/String;)V

    throw p0
.end method
