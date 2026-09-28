.class final Lcom/bachatas4/android/data/ContentImporter$importGame$2;
.super Lkotlin/coroutines/jvm/internal/SuspendLambda;
.source "ContentImporter.kt"

# interfaces
.implements Lkotlin/jvm/functions/Function2;


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lcom/bachatas4/android/data/ContentImporter;->importGame(Lcom/bachatas4/android/data/ContentImportRequest;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;
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
    c = "com.bachatas4.android.data.ContentImporter$importGame$2"
    f = "ContentImporter.kt"
    i = {
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0
    }
    l = {
        0x113
    }
    m = "invokeSuspend"
    n = {
        "gamesDir",
        "destination",
        "staging",
        "payload",
        "digest",
        "completed"
    }
    nl = {
        0x114
    }
    s = {
        "L$0",
        "L$1",
        "L$2",
        "L$3",
        "L$4",
        "I$0"
    }
    v = 0x2
.end annotation


# instance fields
.field final synthetic $request:Lcom/bachatas4/android/data/ContentImportRequest;

.field I$0:I

.field L$0:Ljava/lang/Object;

.field L$1:Ljava/lang/Object;

.field L$2:Ljava/lang/Object;

.field L$3:Ljava/lang/Object;

.field L$4:Ljava/lang/Object;

.field label:I

.field final synthetic this$0:Lcom/bachatas4/android/data/ContentImporter;


# direct methods
.method constructor <init>(Lcom/bachatas4/android/data/ContentImporter;Lcom/bachatas4/android/data/ContentImportRequest;Lkotlin/coroutines/Continuation;)V
    .locals 0
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "(",
            "Lcom/bachatas4/android/data/ContentImporter;",
            "Lcom/bachatas4/android/data/ContentImportRequest;",
            "Lkotlin/coroutines/Continuation<",
            "-",
            "Lcom/bachatas4/android/data/ContentImporter$importGame$2;",
            ">;)V"
        }
    .end annotation

    iput-object p1, p0, Lcom/bachatas4/android/data/ContentImporter$importGame$2;->this$0:Lcom/bachatas4/android/data/ContentImporter;

    iput-object p2, p0, Lcom/bachatas4/android/data/ContentImporter$importGame$2;->$request:Lcom/bachatas4/android/data/ContentImportRequest;

    const/4 p1, 0x2

    invoke-direct {p0, p1, p3}, Lkotlin/coroutines/jvm/internal/SuspendLambda;-><init>(ILkotlin/coroutines/Continuation;)V

    return-void
.end method

.method static final invokeSuspend$lambda$0(B)Ljava/lang/CharSequence;
    .locals 1

    .line 276
    invoke-static {p0}, Ljava/lang/Byte;->valueOf(B)Ljava/lang/Byte;

    move-result-object p0

    filled-new-array {p0}, [Ljava/lang/Object;

    move-result-object p0

    const/4 v0, 0x1

    invoke-static {p0, v0}, Ljava/util/Arrays;->copyOf([Ljava/lang/Object;I)[Ljava/lang/Object;

    move-result-object p0

    const-string v0, "%02x"

    invoke-static {v0, p0}, Ljava/lang/String;->format(Ljava/lang/String;[Ljava/lang/Object;)Ljava/lang/String;

    move-result-object p0

    const-string v0, "format(...)"

    invoke-static {p0, v0}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullExpressionValue(Ljava/lang/Object;Ljava/lang/String;)V

    check-cast p0, Ljava/lang/CharSequence;

    return-object p0
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

    new-instance p1, Lcom/bachatas4/android/data/ContentImporter$importGame$2;

    iget-object v0, p0, Lcom/bachatas4/android/data/ContentImporter$importGame$2;->this$0:Lcom/bachatas4/android/data/ContentImporter;

    iget-object p0, p0, Lcom/bachatas4/android/data/ContentImporter$importGame$2;->$request:Lcom/bachatas4/android/data/ContentImportRequest;

    invoke-direct {p1, v0, p0, p2}, Lcom/bachatas4/android/data/ContentImporter$importGame$2;-><init>(Lcom/bachatas4/android/data/ContentImporter;Lcom/bachatas4/android/data/ContentImportRequest;Lkotlin/coroutines/Continuation;)V

    check-cast p1, Lkotlin/coroutines/Continuation;

    return-object p1
.end method

.method public bridge synthetic invoke(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;
    .locals 0

    check-cast p1, Lkotlinx/coroutines/CoroutineScope;

    check-cast p2, Lkotlin/coroutines/Continuation;

    invoke-virtual {p0, p1, p2}, Lcom/bachatas4/android/data/ContentImporter$importGame$2;->invoke(Lkotlinx/coroutines/CoroutineScope;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;

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

    invoke-virtual {p0, p1, p2}, Lcom/bachatas4/android/data/ContentImporter$importGame$2;->create(Ljava/lang/Object;Lkotlin/coroutines/Continuation;)Lkotlin/coroutines/Continuation;

    move-result-object p0

    check-cast p0, Lcom/bachatas4/android/data/ContentImporter$importGame$2;

    sget-object p1, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;

    invoke-virtual {p0, p1}, Lcom/bachatas4/android/data/ContentImporter$importGame$2;->invokeSuspend(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object p0

    return-object p0
.end method

.method public final invokeSuspend(Ljava/lang/Object;)Ljava/lang/Object;
    .locals 22

    move-object/from16 v0, p0

    const-string v1, "games/"

    invoke-static {}, Lkotlin/coroutines/intrinsics/IntrinsicsKt;->getCOROUTINE_SUSPENDED()Ljava/lang/Object;

    move-result-object v2

    .line 255
    iget v3, v0, Lcom/bachatas4/android/data/ContentImporter$importGame$2;->label:I

    const/4 v4, 0x1

    if-eqz v3, :cond_1

    if-ne v3, v4, :cond_0

    iget v2, v0, Lcom/bachatas4/android/data/ContentImporter$importGame$2;->I$0:I

    iget-object v3, v0, Lcom/bachatas4/android/data/ContentImporter$importGame$2;->L$4:Ljava/lang/Object;

    check-cast v3, Ljava/security/MessageDigest;

    iget-object v5, v0, Lcom/bachatas4/android/data/ContentImporter$importGame$2;->L$3:Ljava/lang/Object;

    check-cast v5, Ljava/io/File;

    iget-object v5, v0, Lcom/bachatas4/android/data/ContentImporter$importGame$2;->L$2:Ljava/lang/Object;

    check-cast v5, Ljava/io/File;

    iget-object v6, v0, Lcom/bachatas4/android/data/ContentImporter$importGame$2;->L$1:Ljava/lang/Object;

    check-cast v6, Ljava/io/File;

    iget-object v7, v0, Lcom/bachatas4/android/data/ContentImporter$importGame$2;->L$0:Ljava/lang/Object;

    check-cast v7, Ljava/io/File;

    :try_start_0
    invoke-static/range {p1 .. p1}, Lkotlin/ResultKt;->throwOnFailure(Ljava/lang/Object;)V
    :try_end_0
    .catch Ljava/lang/SecurityException; {:try_start_0 .. :try_end_0} :catch_0
    .catchall {:try_start_0 .. :try_end_0} :catchall_0

    move-object v9, v3

    move-object/from16 v3, p1

    :goto_0
    move-object v11, v5

    move-object v12, v6

    goto/16 :goto_1

    :catchall_0
    move-exception v0

    move v4, v2

    goto/16 :goto_5

    :catch_0
    move-exception v0

    move v4, v2

    goto/16 :goto_4

    :cond_0
    new-instance v0, Ljava/lang/IllegalStateException;

    const-string v1, "call to \'resume\' before \'invoke\' with coroutine"

    invoke-direct {v0, v1}, Ljava/lang/IllegalStateException;-><init>(Ljava/lang/String;)V

    throw v0

    :cond_1
    invoke-static/range {p1 .. p1}, Lkotlin/ResultKt;->throwOnFailure(Ljava/lang/Object;)V

    .line 256
    iget-object v3, v0, Lcom/bachatas4/android/data/ContentImporter$importGame$2;->this$0:Lcom/bachatas4/android/data/ContentImporter;

    iget-object v5, v0, Lcom/bachatas4/android/data/ContentImporter$importGame$2;->$request:Lcom/bachatas4/android/data/ContentImportRequest;

    invoke-virtual {v5}, Lcom/bachatas4/android/data/ContentImportRequest;->getId()Ljava/lang/String;

    move-result-object v5

    invoke-static {v3, v5}, Lcom/bachatas4/android/data/ContentImporter;->access$validateGameId(Lcom/bachatas4/android/data/ContentImporter;Ljava/lang/String;)V

    .line 257
    new-instance v3, Ljava/io/File;

    iget-object v5, v0, Lcom/bachatas4/android/data/ContentImporter$importGame$2;->this$0:Lcom/bachatas4/android/data/ContentImporter;

    invoke-static {v5}, Lcom/bachatas4/android/data/ContentImporter;->access$getFilesDir$p(Lcom/bachatas4/android/data/ContentImporter;)Ljava/io/File;

    move-result-object v5

    const-string v6, "games"

    invoke-direct {v3, v5, v6}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    invoke-virtual {v3}, Ljava/io/File;->getCanonicalFile()Ljava/io/File;

    move-result-object v3

    .line 258
    invoke-virtual {v3}, Ljava/io/File;->mkdirs()Z

    .line 259
    new-instance v5, Ljava/io/File;

    iget-object v6, v0, Lcom/bachatas4/android/data/ContentImporter$importGame$2;->$request:Lcom/bachatas4/android/data/ContentImportRequest;

    invoke-virtual {v6}, Lcom/bachatas4/android/data/ContentImportRequest;->getId()Ljava/lang/String;

    move-result-object v6

    invoke-direct {v5, v3, v6}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    invoke-virtual {v5}, Ljava/io/File;->getCanonicalFile()Ljava/io/File;

    move-result-object v6

    .line 260
    iget-object v5, v0, Lcom/bachatas4/android/data/ContentImporter$importGame$2;->this$0:Lcom/bachatas4/android/data/ContentImporter;

    invoke-static {v3}, Lkotlin/jvm/internal/Intrinsics;->checkNotNull(Ljava/lang/Object;)V

    invoke-static {v6}, Lkotlin/jvm/internal/Intrinsics;->checkNotNull(Ljava/lang/Object;)V

    invoke-static {v5, v3, v6}, Lcom/bachatas4/android/data/ContentImporter;->access$requireInside(Lcom/bachatas4/android/data/ContentImporter;Ljava/io/File;Ljava/io/File;)V

    .line 261
    invoke-virtual {v6}, Ljava/io/File;->exists()Z

    move-result v5

    if-nez v5, :cond_5

    .line 265
    new-instance v5, Ljava/io/File;

    iget-object v7, v0, Lcom/bachatas4/android/data/ContentImporter$importGame$2;->this$0:Lcom/bachatas4/android/data/ContentImporter;

    invoke-static {v7}, Lcom/bachatas4/android/data/ContentImporter;->access$getIdFactory$p(Lcom/bachatas4/android/data/ContentImporter;)Lkotlin/jvm/functions/Function0;

    move-result-object v7

    invoke-interface {v7}, Lkotlin/jvm/functions/Function0;->invoke()Ljava/lang/Object;

    move-result-object v7

    new-instance v8, Ljava/lang/StringBuilder;

    const-string v9, ".import-"

    invoke-direct {v8, v9}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v8, v7}, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;

    move-result-object v7

    invoke-virtual {v7}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v7

    invoke-direct {v5, v3, v7}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    invoke-virtual {v5}, Ljava/io/File;->getCanonicalFile()Ljava/io/File;

    move-result-object v5

    .line 266
    iget-object v7, v0, Lcom/bachatas4/android/data/ContentImporter$importGame$2;->this$0:Lcom/bachatas4/android/data/ContentImporter;

    invoke-static {v5}, Lkotlin/jvm/internal/Intrinsics;->checkNotNull(Ljava/lang/Object;)V

    invoke-static {v7, v3, v5}, Lcom/bachatas4/android/data/ContentImporter;->access$requireInside(Lcom/bachatas4/android/data/ContentImporter;Ljava/io/File;Ljava/io/File;)V

    const/4 v7, 0x0

    .line 269
    :try_start_1
    invoke-virtual {v5}, Ljava/io/File;->exists()Z

    move-result v8

    if-eqz v8, :cond_2

    .line 270
    invoke-static {v5}, Lkotlin/io/FilesKt;->deleteRecursively(Ljava/io/File;)Z

    .line 272
    :cond_2
    invoke-virtual {v5}, Ljava/io/File;->mkdirs()Z

    .line 273
    new-instance v8, Ljava/io/File;

    const-string v9, "eboot.bin"

    invoke-direct {v8, v5, v9}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    .line 274
    const-string v9, "SHA-256"

    invoke-static {v9}, Ljava/security/MessageDigest;->getInstance(Ljava/lang/String;)Ljava/security/MessageDigest;

    move-result-object v9

    .line 275
    iget-object v10, v0, Lcom/bachatas4/android/data/ContentImporter$importGame$2;->this$0:Lcom/bachatas4/android/data/ContentImporter;

    iget-object v11, v0, Lcom/bachatas4/android/data/ContentImporter$importGame$2;->$request:Lcom/bachatas4/android/data/ContentImportRequest;

    invoke-static {v9}, Lkotlin/jvm/internal/Intrinsics;->checkNotNull(Ljava/lang/Object;)V

    move-object v12, v0

    check-cast v12, Lkotlin/coroutines/Continuation;

    invoke-static {v3}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v3

    iput-object v3, v0, Lcom/bachatas4/android/data/ContentImporter$importGame$2;->L$0:Ljava/lang/Object;

    iput-object v6, v0, Lcom/bachatas4/android/data/ContentImporter$importGame$2;->L$1:Ljava/lang/Object;

    iput-object v5, v0, Lcom/bachatas4/android/data/ContentImporter$importGame$2;->L$2:Ljava/lang/Object;

    invoke-static {v8}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v3

    iput-object v3, v0, Lcom/bachatas4/android/data/ContentImporter$importGame$2;->L$3:Ljava/lang/Object;

    iput-object v9, v0, Lcom/bachatas4/android/data/ContentImporter$importGame$2;->L$4:Ljava/lang/Object;

    iput v7, v0, Lcom/bachatas4/android/data/ContentImporter$importGame$2;->I$0:I

    iput v4, v0, Lcom/bachatas4/android/data/ContentImporter$importGame$2;->label:I

    invoke-static {v10, v11, v8, v9, v12}, Lcom/bachatas4/android/data/ContentImporter;->access$copySource(Lcom/bachatas4/android/data/ContentImporter;Lcom/bachatas4/android/data/ContentImportRequest;Ljava/io/File;Ljava/security/MessageDigest;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;

    move-result-object v3
    :try_end_1
    .catch Ljava/lang/SecurityException; {:try_start_1 .. :try_end_1} :catch_3
    .catchall {:try_start_1 .. :try_end_1} :catchall_3

    if-ne v3, v2, :cond_3

    return-object v2

    :cond_3
    move v2, v7

    goto/16 :goto_0

    :goto_1
    :try_start_2
    check-cast v3, Ljava/lang/Number;

    invoke-virtual {v3}, Ljava/lang/Number;->longValue()J

    move-result-wide v5

    .line 276
    invoke-virtual {v9}, Ljava/security/MessageDigest;->digest()[B

    move-result-object v13

    const-string v3, "digest(...)"

    invoke-static {v13, v3}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullExpressionValue(Ljava/lang/Object;Ljava/lang/String;)V

    const-string v3, ""

    move-object v14, v3

    check-cast v14, Ljava/lang/CharSequence;

    new-instance v19, Lcom/bachatas4/android/data/ContentImporter$importGame$2$$ExternalSyntheticLambda0;

    invoke-direct/range {v19 .. v19}, Lcom/bachatas4/android/data/ContentImporter$importGame$2$$ExternalSyntheticLambda0;-><init>()V

    const/16 v20, 0x1e

    const/16 v21, 0x0

    const/4 v15, 0x0

    const/16 v16, 0x0

    const/16 v17, 0x0

    const/16 v18, 0x0

    invoke-static/range {v13 .. v21}, Lkotlin/collections/ArraysKt;->joinToString$default([BLjava/lang/CharSequence;Ljava/lang/CharSequence;Ljava/lang/CharSequence;ILjava/lang/CharSequence;Lkotlin/jvm/functions/Function1;ILjava/lang/Object;)Ljava/lang/String;

    move-result-object v3

    .line 277
    iget-object v7, v0, Lcom/bachatas4/android/data/ContentImporter$importGame$2;->this$0:Lcom/bachatas4/android/data/ContentImporter;

    iget-object v8, v0, Lcom/bachatas4/android/data/ContentImporter$importGame$2;->$request:Lcom/bachatas4/android/data/ContentImportRequest;

    invoke-static {v7, v8, v5, v6}, Lcom/bachatas4/android/data/ContentImporter;->access$validateBytes(Lcom/bachatas4/android/data/ContentImporter;Lcom/bachatas4/android/data/ContentImportRequest;J)V

    .line 278
    iget-object v7, v0, Lcom/bachatas4/android/data/ContentImporter$importGame$2;->this$0:Lcom/bachatas4/android/data/ContentImporter;

    iget-object v8, v0, Lcom/bachatas4/android/data/ContentImporter$importGame$2;->$request:Lcom/bachatas4/android/data/ContentImportRequest;

    invoke-static {v7, v8, v3}, Lcom/bachatas4/android/data/ContentImporter;->access$validateDigest(Lcom/bachatas4/android/data/ContentImporter;Lcom/bachatas4/android/data/ContentImportRequest;Ljava/lang/String;)V

    .line 279
    iget-object v10, v0, Lcom/bachatas4/android/data/ContentImporter$importGame$2;->this$0:Lcom/bachatas4/android/data/ContentImporter;

    .line 280
    invoke-static {v11}, Lkotlin/jvm/internal/Intrinsics;->checkNotNull(Ljava/lang/Object;)V

    .line 281
    invoke-static {v12}, Lkotlin/jvm/internal/Intrinsics;->checkNotNull(Ljava/lang/Object;)V

    .line 282
    iget-object v13, v0, Lcom/bachatas4/android/data/ContentImporter$importGame$2;->$request:Lcom/bachatas4/android/data/ContentImportRequest;

    .line 283
    const-string v14, "folder"

    const/4 v15, 0x0

    const/16 v16, 0x0

    .line 279
    invoke-static/range {v10 .. v16}, Lcom/bachatas4/android/data/ContentImporter;->access$writeInstallManifestAndPromote(Lcom/bachatas4/android/data/ContentImporter;Ljava/io/File;Ljava/io/File;Lcom/bachatas4/android/data/ContentImportRequest;Ljava/lang/String;Ljava/lang/String;Z)J
    :try_end_2
    .catch Ljava/lang/SecurityException; {:try_start_2 .. :try_end_2} :catch_2
    .catchall {:try_start_2 .. :try_end_2} :catchall_2

    .line 288
    :try_start_3
    new-instance v2, Lcom/bachatas4/android/data/ContentImportResult;

    .line 289
    new-instance v12, Lcom/bachatas4/android/model/Game;

    .line 290
    iget-object v7, v0, Lcom/bachatas4/android/data/ContentImporter$importGame$2;->$request:Lcom/bachatas4/android/data/ContentImportRequest;

    invoke-virtual {v7}, Lcom/bachatas4/android/data/ContentImportRequest;->getId()Ljava/lang/String;

    move-result-object v13

    .line 291
    iget-object v7, v0, Lcom/bachatas4/android/data/ContentImporter$importGame$2;->$request:Lcom/bachatas4/android/data/ContentImportRequest;

    invoke-virtual {v7}, Lcom/bachatas4/android/data/ContentImportRequest;->getTitle()Ljava/lang/String;

    move-result-object v14

    .line 292
    iget-object v7, v0, Lcom/bachatas4/android/data/ContentImporter$importGame$2;->$request:Lcom/bachatas4/android/data/ContentImportRequest;

    invoke-virtual {v7}, Lcom/bachatas4/android/data/ContentImportRequest;->getId()Ljava/lang/String;

    move-result-object v7

    new-instance v8, Ljava/lang/StringBuilder;

    invoke-direct {v8, v1}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v8, v7}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v15

    .line 293
    iget-object v1, v0, Lcom/bachatas4/android/data/ContentImporter$importGame$2;->$request:Lcom/bachatas4/android/data/ContentImportRequest;

    invoke-virtual {v1}, Lcom/bachatas4/android/data/ContentImportRequest;->getSubtitle()Ljava/lang/String;

    move-result-object v16

    .line 294
    iget-object v0, v0, Lcom/bachatas4/android/data/ContentImporter$importGame$2;->$request:Lcom/bachatas4/android/data/ContentImportRequest;

    invoke-virtual {v0}, Lcom/bachatas4/android/data/ContentImportRequest;->getDetail()Ljava/lang/String;

    move-result-object v17

    const/16 v20, 0x20

    const/16 v21, 0x0

    const-wide/16 v18, 0x0

    .line 289
    invoke-direct/range {v12 .. v21}, Lcom/bachatas4/android/model/Game;-><init>(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;JILkotlin/jvm/internal/DefaultConstructorMarker;)V

    .line 288
    invoke-direct {v2, v12, v5, v6, v3}, Lcom/bachatas4/android/data/ContentImportResult;-><init>(Lcom/bachatas4/android/model/Game;JLjava/lang/String;)V
    :try_end_3
    .catch Ljava/lang/SecurityException; {:try_start_3 .. :try_end_3} :catch_1
    .catchall {:try_start_3 .. :try_end_3} :catchall_1

    return-object v2

    :catchall_1
    move-exception v0

    goto :goto_2

    :catch_1
    move-exception v0

    goto :goto_3

    :catchall_2
    move-exception v0

    move v4, v2

    :goto_2
    move-object v5, v11

    goto :goto_5

    :catch_2
    move-exception v0

    move v4, v2

    :goto_3
    move-object v5, v11

    goto :goto_4

    :catchall_3
    move-exception v0

    move v4, v7

    goto :goto_5

    :catch_3
    move-exception v0

    move v4, v7

    .line 300
    :goto_4
    :try_start_4
    new-instance v1, Lcom/bachatas4/android/data/ContentImportException;

    .line 301
    sget-object v2, Lcom/bachatas4/android/model/RuntimeErrorCode;->CONTENT_PERMISSION_LOST:Lcom/bachatas4/android/model/RuntimeErrorCode;

    .line 302
    const-string v3, "Source permission lost"

    .line 303
    check-cast v0, Ljava/lang/Throwable;

    .line 300
    invoke-direct {v1, v2, v3, v0}, Lcom/bachatas4/android/data/ContentImportException;-><init>(Lcom/bachatas4/android/model/RuntimeErrorCode;Ljava/lang/String;Ljava/lang/Throwable;)V

    throw v1
    :try_end_4
    .catchall {:try_start_4 .. :try_end_4} :catchall_4

    :catchall_4
    move-exception v0

    :goto_5
    if-nez v4, :cond_4

    .line 307
    invoke-static {v5}, Lkotlin/jvm/internal/Intrinsics;->checkNotNull(Ljava/lang/Object;)V

    invoke-static {v5}, Lkotlin/io/FilesKt;->deleteRecursively(Ljava/io/File;)Z

    :cond_4
    throw v0

    .line 262
    :cond_5
    new-instance v6, Lcom/bachatas4/android/data/ContentImportException;

    sget-object v7, Lcom/bachatas4/android/model/RuntimeErrorCode;->CONTENT_INVALID:Lcom/bachatas4/android/model/RuntimeErrorCode;

    const/4 v10, 0x4

    const/4 v11, 0x0

    const-string v8, "Game already imported"

    const/4 v9, 0x0

    invoke-direct/range {v6 .. v11}, Lcom/bachatas4/android/data/ContentImportException;-><init>(Lcom/bachatas4/android/model/RuntimeErrorCode;Ljava/lang/String;Ljava/lang/Throwable;ILkotlin/jvm/internal/DefaultConstructorMarker;)V

    throw v6
.end method
