.class final Lcom/bachatas4/android/data/ContentImporter$importGameTree$2;
.super Lkotlin/coroutines/jvm/internal/SuspendLambda;
.source "ContentImporter.kt"

# interfaces
.implements Lkotlin/jvm/functions/Function2;


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lcom/bachatas4/android/data/ContentImporter;->importGameTree(Lcom/bachatas4/android/data/ContentImportRequest;Ljava/util/List;Lkotlin/jvm/functions/Function3;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;
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

.annotation system Ldalvik/annotation/SourceDebugExtension;
    value = "SMAP\nContentImporter.kt\nKotlin\n*S Kotlin\n*F\n+ 1 ContentImporter.kt\ncom/bachatas4/android/data/ContentImporter$importGameTree$2\n+ 2 _Collections.kt\nkotlin/collections/CollectionsKt___CollectionsKt\n*L\n1#1,434:1\n2945#2,3:435\n2002#2,3:438\n1221#2:441\n2068#2,2:442\n*S KotlinDebug\n*F\n+ 1 ContentImporter.kt\ncom/bachatas4/android/data/ContentImporter$importGameTree$2\n*L\n85#1:435,3\n88#1:438,3\n111#1:441\n111#1:442,2\n*E\n"
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
    c = "com.bachatas4.android.data.ContentImporter$importGameTree$2"
    f = "ContentImporter.kt"
    i = {
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0
    }
    l = {
        0x73
    }
    m = "invokeSuspend"
    n = {
        "gamesDir",
        "destination",
        "staging",
        "digest",
        "bytesCopied",
        "$this$forEach$iv",
        "element$iv",
        "entry",
        "payload",
        "requiredBytes",
        "usableBytes",
        "completed"
    }
    nl = {
        0x74
    }
    s = {
        "L$0",
        "L$1",
        "L$2",
        "L$3",
        "L$4",
        "L$5",
        "L$9",
        "L$10",
        "L$11",
        "J$0",
        "J$1",
        "I$0"
    }
    v = 0x2
.end annotation


# instance fields
.field final synthetic $entries:Ljava/util/List;
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "Ljava/util/List<",
            "Lcom/bachatas4/android/data/ContentTreeEntry;",
            ">;"
        }
    .end annotation
.end field

.field final synthetic $onProgress:Lkotlin/jvm/functions/Function3;
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "Lkotlin/jvm/functions/Function3<",
            "Ljava/lang/Long;",
            "Ljava/lang/Long;",
            "Ljava/lang/String;",
            "Lkotlin/Unit;",
            ">;"
        }
    .end annotation
.end field

.field final synthetic $request:Lcom/bachatas4/android/data/ContentImportRequest;

.field I$0:I

.field J$0:J

.field J$1:J

.field J$2:J

.field L$0:Ljava/lang/Object;

.field L$1:Ljava/lang/Object;

.field L$10:Ljava/lang/Object;

.field L$11:Ljava/lang/Object;

.field L$12:Ljava/lang/Object;

.field L$2:Ljava/lang/Object;

.field L$3:Ljava/lang/Object;

.field L$4:Ljava/lang/Object;

.field L$5:Ljava/lang/Object;

.field L$6:Ljava/lang/Object;

.field L$7:Ljava/lang/Object;

.field L$8:Ljava/lang/Object;

.field L$9:Ljava/lang/Object;

.field label:I

.field final synthetic this$0:Lcom/bachatas4/android/data/ContentImporter;


# direct methods
.method constructor <init>(Lcom/bachatas4/android/data/ContentImporter;Lcom/bachatas4/android/data/ContentImportRequest;Ljava/util/List;Lkotlin/jvm/functions/Function3;Lkotlin/coroutines/Continuation;)V
    .locals 0
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "(",
            "Lcom/bachatas4/android/data/ContentImporter;",
            "Lcom/bachatas4/android/data/ContentImportRequest;",
            "Ljava/util/List<",
            "Lcom/bachatas4/android/data/ContentTreeEntry;",
            ">;",
            "Lkotlin/jvm/functions/Function3<",
            "-",
            "Ljava/lang/Long;",
            "-",
            "Ljava/lang/Long;",
            "-",
            "Ljava/lang/String;",
            "Lkotlin/Unit;",
            ">;",
            "Lkotlin/coroutines/Continuation<",
            "-",
            "Lcom/bachatas4/android/data/ContentImporter$importGameTree$2;",
            ">;)V"
        }
    .end annotation

    iput-object p1, p0, Lcom/bachatas4/android/data/ContentImporter$importGameTree$2;->this$0:Lcom/bachatas4/android/data/ContentImporter;

    iput-object p2, p0, Lcom/bachatas4/android/data/ContentImporter$importGameTree$2;->$request:Lcom/bachatas4/android/data/ContentImportRequest;

    iput-object p3, p0, Lcom/bachatas4/android/data/ContentImporter$importGameTree$2;->$entries:Ljava/util/List;

    iput-object p4, p0, Lcom/bachatas4/android/data/ContentImporter$importGameTree$2;->$onProgress:Lkotlin/jvm/functions/Function3;

    const/4 p1, 0x2

    invoke-direct {p0, p1, p5}, Lkotlin/coroutines/jvm/internal/SuspendLambda;-><init>(ILkotlin/coroutines/Continuation;)V

    return-void
.end method

.method static final invokeSuspend$lambda$4(B)Ljava/lang/CharSequence;
    .locals 1

    .line 119
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
    .locals 6
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

    new-instance v0, Lcom/bachatas4/android/data/ContentImporter$importGameTree$2;

    iget-object v1, p0, Lcom/bachatas4/android/data/ContentImporter$importGameTree$2;->this$0:Lcom/bachatas4/android/data/ContentImporter;

    iget-object v2, p0, Lcom/bachatas4/android/data/ContentImporter$importGameTree$2;->$request:Lcom/bachatas4/android/data/ContentImportRequest;

    iget-object v3, p0, Lcom/bachatas4/android/data/ContentImporter$importGameTree$2;->$entries:Ljava/util/List;

    iget-object v4, p0, Lcom/bachatas4/android/data/ContentImporter$importGameTree$2;->$onProgress:Lkotlin/jvm/functions/Function3;

    move-object v5, p2

    invoke-direct/range {v0 .. v5}, Lcom/bachatas4/android/data/ContentImporter$importGameTree$2;-><init>(Lcom/bachatas4/android/data/ContentImporter;Lcom/bachatas4/android/data/ContentImportRequest;Ljava/util/List;Lkotlin/jvm/functions/Function3;Lkotlin/coroutines/Continuation;)V

    check-cast v0, Lkotlin/coroutines/Continuation;

    return-object v0
.end method

.method public bridge synthetic invoke(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;
    .locals 0

    check-cast p1, Lkotlinx/coroutines/CoroutineScope;

    check-cast p2, Lkotlin/coroutines/Continuation;

    invoke-virtual {p0, p1, p2}, Lcom/bachatas4/android/data/ContentImporter$importGameTree$2;->invoke(Lkotlinx/coroutines/CoroutineScope;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;

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

    invoke-virtual {p0, p1, p2}, Lcom/bachatas4/android/data/ContentImporter$importGameTree$2;->create(Ljava/lang/Object;Lkotlin/coroutines/Continuation;)Lkotlin/coroutines/Continuation;

    move-result-object p0

    check-cast p0, Lcom/bachatas4/android/data/ContentImporter$importGameTree$2;

    sget-object p1, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;

    invoke-virtual {p0, p1}, Lcom/bachatas4/android/data/ContentImporter$importGameTree$2;->invokeSuspend(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object p0

    return-object p0
.end method

.method public final invokeSuspend(Ljava/lang/Object;)Ljava/lang/Object;
    .locals 30

    move-object/from16 v0, p0

    invoke-static {}, Lkotlin/coroutines/intrinsics/IntrinsicsKt;->getCOROUTINE_SUSPENDED()Ljava/lang/Object;

    move-result-object v1

    .line 76
    iget v2, v0, Lcom/bachatas4/android/data/ContentImporter$importGameTree$2;->label:I

    const/4 v3, 0x1

    if-eqz v2, :cond_1

    if-ne v2, v3, :cond_0

    iget-wide v4, v0, Lcom/bachatas4/android/data/ContentImporter$importGameTree$2;->J$2:J

    iget v2, v0, Lcom/bachatas4/android/data/ContentImporter$importGameTree$2;->I$0:I

    iget-wide v6, v0, Lcom/bachatas4/android/data/ContentImporter$importGameTree$2;->J$1:J

    iget-wide v8, v0, Lcom/bachatas4/android/data/ContentImporter$importGameTree$2;->J$0:J

    iget-object v10, v0, Lcom/bachatas4/android/data/ContentImporter$importGameTree$2;->L$12:Ljava/lang/Object;

    check-cast v10, Lkotlin/jvm/internal/Ref$LongRef;

    iget-object v11, v0, Lcom/bachatas4/android/data/ContentImporter$importGameTree$2;->L$11:Ljava/lang/Object;

    check-cast v11, Ljava/io/File;

    iget-object v11, v0, Lcom/bachatas4/android/data/ContentImporter$importGameTree$2;->L$10:Ljava/lang/Object;

    check-cast v11, Lcom/bachatas4/android/data/ContentTreeEntry;

    iget-object v12, v0, Lcom/bachatas4/android/data/ContentImporter$importGameTree$2;->L$8:Ljava/lang/Object;

    check-cast v12, Ljava/util/Iterator;

    iget-object v13, v0, Lcom/bachatas4/android/data/ContentImporter$importGameTree$2;->L$7:Ljava/lang/Object;

    check-cast v13, Lkotlin/jvm/functions/Function3;

    iget-object v14, v0, Lcom/bachatas4/android/data/ContentImporter$importGameTree$2;->L$6:Ljava/lang/Object;

    check-cast v14, Lcom/bachatas4/android/data/ContentImporter;

    iget-object v15, v0, Lcom/bachatas4/android/data/ContentImporter$importGameTree$2;->L$5:Ljava/lang/Object;

    check-cast v15, Ljava/lang/Iterable;

    iget-object v3, v0, Lcom/bachatas4/android/data/ContentImporter$importGameTree$2;->L$4:Ljava/lang/Object;

    check-cast v3, Lkotlin/jvm/internal/Ref$LongRef;

    move/from16 v16, v2

    iget-object v2, v0, Lcom/bachatas4/android/data/ContentImporter$importGameTree$2;->L$3:Ljava/lang/Object;

    check-cast v2, Ljava/security/MessageDigest;

    move-object/from16 v17, v2

    iget-object v2, v0, Lcom/bachatas4/android/data/ContentImporter$importGameTree$2;->L$2:Ljava/lang/Object;

    check-cast v2, Ljava/io/File;

    move-object/from16 v18, v2

    iget-object v2, v0, Lcom/bachatas4/android/data/ContentImporter$importGameTree$2;->L$1:Ljava/lang/Object;

    check-cast v2, Ljava/io/File;

    move-object/from16 v19, v2

    iget-object v2, v0, Lcom/bachatas4/android/data/ContentImporter$importGameTree$2;->L$0:Ljava/lang/Object;

    check-cast v2, Ljava/io/File;

    :try_start_0
    invoke-static/range {p1 .. p1}, Lkotlin/ResultKt;->throwOnFailure(Ljava/lang/Object;)V
    :try_end_0
    .catch Ljava/lang/SecurityException; {:try_start_0 .. :try_end_0} :catch_0
    .catchall {:try_start_0 .. :try_end_0} :catchall_0

    move-object/from16 v20, v15

    move-object v15, v1

    move-object v1, v13

    move-object v13, v11

    move-object v11, v10

    move-object/from16 v27, v2

    move-object/from16 v2, p1

    move-object/from16 v28, v3

    move-object/from16 v3, v27

    move-object/from16 v27, v12

    move-object/from16 v12, v28

    move-object/from16 v28, v14

    move-object/from16 v14, v27

    move-object/from16 v27, v18

    move-object/from16 v18, v28

    move-wide/from16 v28, v6

    move/from16 v6, v16

    move-wide v7, v8

    move-object/from16 v16, v27

    move-wide/from16 v9, v28

    goto/16 :goto_4

    :catchall_0
    move-exception v0

    move/from16 v3, v16

    move-object/from16 v2, v18

    goto/16 :goto_c

    :catch_0
    move-exception v0

    move/from16 v3, v16

    move-object/from16 v2, v18

    goto/16 :goto_b

    :cond_0
    new-instance v0, Ljava/lang/IllegalStateException;

    const-string v1, "call to \'resume\' before \'invoke\' with coroutine"

    invoke-direct {v0, v1}, Ljava/lang/IllegalStateException;-><init>(Ljava/lang/String;)V

    throw v0

    :cond_1
    invoke-static/range {p1 .. p1}, Lkotlin/ResultKt;->throwOnFailure(Ljava/lang/Object;)V

    .line 77
    iget-object v2, v0, Lcom/bachatas4/android/data/ContentImporter$importGameTree$2;->this$0:Lcom/bachatas4/android/data/ContentImporter;

    iget-object v3, v0, Lcom/bachatas4/android/data/ContentImporter$importGameTree$2;->$request:Lcom/bachatas4/android/data/ContentImportRequest;

    invoke-virtual {v3}, Lcom/bachatas4/android/data/ContentImportRequest;->getId()Ljava/lang/String;

    move-result-object v3

    invoke-static {v2, v3}, Lcom/bachatas4/android/data/ContentImporter;->access$validateGameId(Lcom/bachatas4/android/data/ContentImporter;Ljava/lang/String;)V

    .line 78
    new-instance v2, Ljava/io/File;

    iget-object v3, v0, Lcom/bachatas4/android/data/ContentImporter$importGameTree$2;->this$0:Lcom/bachatas4/android/data/ContentImporter;

    invoke-static {v3}, Lcom/bachatas4/android/data/ContentImporter;->access$getFilesDir$p(Lcom/bachatas4/android/data/ContentImporter;)Ljava/io/File;

    move-result-object v3

    const-string v4, "games"

    invoke-direct {v2, v3, v4}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    invoke-virtual {v2}, Ljava/io/File;->getCanonicalFile()Ljava/io/File;

    move-result-object v2

    .line 79
    invoke-virtual {v2}, Ljava/io/File;->mkdirs()Z

    .line 80
    new-instance v3, Ljava/io/File;

    iget-object v4, v0, Lcom/bachatas4/android/data/ContentImporter$importGameTree$2;->$request:Lcom/bachatas4/android/data/ContentImportRequest;

    invoke-virtual {v4}, Lcom/bachatas4/android/data/ContentImportRequest;->getId()Ljava/lang/String;

    move-result-object v4

    invoke-direct {v3, v2, v4}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    invoke-virtual {v3}, Ljava/io/File;->getCanonicalFile()Ljava/io/File;

    move-result-object v3

    .line 81
    iget-object v4, v0, Lcom/bachatas4/android/data/ContentImporter$importGameTree$2;->this$0:Lcom/bachatas4/android/data/ContentImporter;

    invoke-static {v2}, Lkotlin/jvm/internal/Intrinsics;->checkNotNull(Ljava/lang/Object;)V

    invoke-static {v3}, Lkotlin/jvm/internal/Intrinsics;->checkNotNull(Ljava/lang/Object;)V

    invoke-static {v4, v2, v3}, Lcom/bachatas4/android/data/ContentImporter;->access$requireInside(Lcom/bachatas4/android/data/ContentImporter;Ljava/io/File;Ljava/io/File;)V

    .line 82
    invoke-virtual {v3}, Ljava/io/File;->exists()Z

    move-result v4

    if-nez v4, :cond_f

    .line 85
    iget-object v4, v0, Lcom/bachatas4/android/data/ContentImporter$importGameTree$2;->$entries:Ljava/util/List;

    check-cast v4, Ljava/lang/Iterable;

    .line 435
    instance-of v5, v4, Ljava/util/Collection;

    if-eqz v5, :cond_2

    move-object v5, v4

    check-cast v5, Ljava/util/Collection;

    invoke-interface {v5}, Ljava/util/Collection;->isEmpty()Z

    move-result v5

    if-nez v5, :cond_e

    .line 436
    :cond_2
    invoke-interface {v4}, Ljava/lang/Iterable;->iterator()Ljava/util/Iterator;

    move-result-object v4

    :cond_3
    invoke-interface {v4}, Ljava/util/Iterator;->hasNext()Z

    move-result v5

    if-eqz v5, :cond_e

    invoke-interface {v4}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v5

    check-cast v5, Lcom/bachatas4/android/data/ContentTreeEntry;

    .line 85
    invoke-virtual {v5}, Lcom/bachatas4/android/data/ContentTreeEntry;->getRelativePath()Ljava/lang/String;

    move-result-object v5

    const-string v6, "eboot.bin"

    invoke-static {v5, v6}, Lkotlin/jvm/internal/Intrinsics;->areEqual(Ljava/lang/Object;Ljava/lang/Object;)Z

    move-result v5

    if-eqz v5, :cond_3

    .line 88
    iget-object v4, v0, Lcom/bachatas4/android/data/ContentImporter$importGameTree$2;->$entries:Ljava/util/List;

    check-cast v4, Ljava/lang/Iterable;

    .line 439
    invoke-interface {v4}, Ljava/lang/Iterable;->iterator()Ljava/util/Iterator;

    move-result-object v4

    const-wide/16 v5, 0x0

    move-wide v7, v5

    :cond_4
    :goto_0
    invoke-interface {v4}, Ljava/util/Iterator;->hasNext()Z

    move-result v9

    if-eqz v9, :cond_6

    invoke-interface {v4}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v9

    check-cast v9, Lcom/bachatas4/android/data/ContentTreeEntry;

    .line 89
    invoke-virtual {v9}, Lcom/bachatas4/android/data/ContentTreeEntry;->getExpectedBytes()Ljava/lang/Long;

    move-result-object v9

    if-eqz v9, :cond_4

    invoke-virtual {v9}, Ljava/lang/Long;->longValue()J

    move-result-wide v9

    cmp-long v11, v9, v5

    if-ltz v11, :cond_5

    const-wide v11, 0x7fffffffffffffffL

    sub-long/2addr v11, v7

    cmp-long v11, v11, v9

    if-ltz v11, :cond_5

    add-long/2addr v7, v9

    goto :goto_0

    .line 91
    :cond_5
    new-instance v9, Lcom/bachatas4/android/data/ContentImportException;

    sget-object v10, Lcom/bachatas4/android/model/RuntimeErrorCode;->CONTENT_INVALID:Lcom/bachatas4/android/model/RuntimeErrorCode;

    const/4 v13, 0x4

    const/4 v14, 0x0

    const-string v11, "Selected folder size is invalid"

    const/4 v12, 0x0

    invoke-direct/range {v9 .. v14}, Lcom/bachatas4/android/data/ContentImportException;-><init>(Lcom/bachatas4/android/model/RuntimeErrorCode;Ljava/lang/String;Ljava/lang/Throwable;ILkotlin/jvm/internal/DefaultConstructorMarker;)V

    throw v9

    .line 95
    :cond_6
    iget-object v4, v0, Lcom/bachatas4/android/data/ContentImporter$importGameTree$2;->this$0:Lcom/bachatas4/android/data/ContentImporter;

    invoke-static {v4}, Lcom/bachatas4/android/data/ContentImporter;->access$getAvailableBytes$p(Lcom/bachatas4/android/data/ContentImporter;)Lkotlin/jvm/functions/Function1;

    move-result-object v4

    invoke-interface {v4, v2}, Lkotlin/jvm/functions/Function1;->invoke(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v4

    check-cast v4, Ljava/lang/Number;

    invoke-virtual {v4}, Ljava/lang/Number;->longValue()J

    move-result-wide v9

    cmp-long v4, v7, v5

    if-lez v4, :cond_8

    cmp-long v4, v7, v9

    if-gtz v4, :cond_7

    goto :goto_1

    .line 97
    :cond_7
    new-instance v16, Lcom/bachatas4/android/data/ContentImportException;

    .line 98
    sget-object v17, Lcom/bachatas4/android/model/RuntimeErrorCode;->CONTENT_INVALID:Lcom/bachatas4/android/model/RuntimeErrorCode;

    .line 99
    iget-object v1, v0, Lcom/bachatas4/android/data/ContentImporter$importGameTree$2;->this$0:Lcom/bachatas4/android/data/ContentImporter;

    invoke-static {v1, v7, v8}, Lcom/bachatas4/android/data/ContentImporter;->access$formatGiB(Lcom/bachatas4/android/data/ContentImporter;J)Ljava/lang/String;

    move-result-object v1

    iget-object v0, v0, Lcom/bachatas4/android/data/ContentImporter$importGameTree$2;->this$0:Lcom/bachatas4/android/data/ContentImporter;

    invoke-static {v0, v9, v10}, Lcom/bachatas4/android/data/ContentImporter;->access$formatGiB(Lcom/bachatas4/android/data/ContentImporter;J)Ljava/lang/String;

    move-result-object v0

    new-instance v2, Ljava/lang/StringBuilder;

    const-string v3, "Import requires "

    invoke-direct {v2, v3}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v2, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    const-string v2, " GiB but only "

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    const-string v1, " GiB is available"

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v18

    const/16 v20, 0x4

    const/16 v21, 0x0

    const/16 v19, 0x0

    .line 97
    invoke-direct/range {v16 .. v21}, Lcom/bachatas4/android/data/ContentImportException;-><init>(Lcom/bachatas4/android/model/RuntimeErrorCode;Ljava/lang/String;Ljava/lang/Throwable;ILkotlin/jvm/internal/DefaultConstructorMarker;)V

    throw v16

    .line 103
    :cond_8
    :goto_1
    new-instance v4, Ljava/io/File;

    iget-object v5, v0, Lcom/bachatas4/android/data/ContentImporter$importGameTree$2;->this$0:Lcom/bachatas4/android/data/ContentImporter;

    invoke-static {v5}, Lcom/bachatas4/android/data/ContentImporter;->access$getIdFactory$p(Lcom/bachatas4/android/data/ContentImporter;)Lkotlin/jvm/functions/Function0;

    move-result-object v5

    invoke-interface {v5}, Lkotlin/jvm/functions/Function0;->invoke()Ljava/lang/Object;

    move-result-object v5

    new-instance v6, Ljava/lang/StringBuilder;

    const-string v11, ".import-"

    invoke-direct {v6, v11}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v6, v5}, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;

    move-result-object v5

    invoke-virtual {v5}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v5

    invoke-direct {v4, v2, v5}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    invoke-virtual {v4}, Ljava/io/File;->getCanonicalFile()Ljava/io/File;

    move-result-object v4

    .line 104
    iget-object v5, v0, Lcom/bachatas4/android/data/ContentImporter$importGameTree$2;->this$0:Lcom/bachatas4/android/data/ContentImporter;

    invoke-static {v4}, Lkotlin/jvm/internal/Intrinsics;->checkNotNull(Ljava/lang/Object;)V

    invoke-static {v5, v2, v4}, Lcom/bachatas4/android/data/ContentImporter;->access$requireInside(Lcom/bachatas4/android/data/ContentImporter;Ljava/io/File;Ljava/io/File;)V

    const/4 v5, 0x0

    .line 107
    :try_start_1
    invoke-static {v4}, Lkotlin/io/FilesKt;->deleteRecursively(Ljava/io/File;)Z

    .line 108
    invoke-virtual {v4}, Ljava/io/File;->mkdirs()Z

    .line 109
    const-string v6, "SHA-256"

    invoke-static {v6}, Ljava/security/MessageDigest;->getInstance(Ljava/lang/String;)Ljava/security/MessageDigest;

    move-result-object v6

    .line 110
    new-instance v11, Lkotlin/jvm/internal/Ref$LongRef;

    invoke-direct {v11}, Lkotlin/jvm/internal/Ref$LongRef;-><init>()V

    .line 111
    iget-object v12, v0, Lcom/bachatas4/android/data/ContentImporter$importGameTree$2;->$entries:Ljava/util/List;

    check-cast v12, Ljava/lang/Iterable;

    .line 441
    new-instance v13, Lcom/bachatas4/android/data/ContentImporter$importGameTree$2$invokeSuspend$$inlined$sortedBy$1;

    invoke-direct {v13}, Lcom/bachatas4/android/data/ContentImporter$importGameTree$2$invokeSuspend$$inlined$sortedBy$1;-><init>()V

    check-cast v13, Ljava/util/Comparator;

    invoke-static {v12, v13}, Lkotlin/collections/CollectionsKt;->sortedWith(Ljava/lang/Iterable;Ljava/util/Comparator;)Ljava/util/List;

    move-result-object v12

    check-cast v12, Ljava/lang/Iterable;

    iget-object v13, v0, Lcom/bachatas4/android/data/ContentImporter$importGameTree$2;->this$0:Lcom/bachatas4/android/data/ContentImporter;

    iget-object v14, v0, Lcom/bachatas4/android/data/ContentImporter$importGameTree$2;->$onProgress:Lkotlin/jvm/functions/Function3;

    .line 442
    invoke-interface {v12}, Ljava/lang/Iterable;->iterator()Ljava/util/Iterator;

    move-result-object v15
    :try_end_1
    .catch Ljava/lang/SecurityException; {:try_start_1 .. :try_end_1} :catch_7
    .catchall {:try_start_1 .. :try_end_1} :catchall_7

    move-object/from16 v27, v3

    move-object v3, v2

    move-object v2, v4

    move-object/from16 v4, v27

    move-object/from16 v27, v15

    move-object v15, v12

    move-object/from16 v12, v27

    move-object/from16 v27, v14

    move-object v14, v13

    move-object/from16 v13, v27

    :goto_2
    :try_start_2
    invoke-interface {v12}, Ljava/util/Iterator;->hasNext()Z

    move-result v16

    if-eqz v16, :cond_c

    invoke-interface {v12}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v16

    move-object/from16 p1, v3

    move-object/from16 v3, v16

    check-cast v3, Lcom/bachatas4/android/data/ContentTreeEntry;

    move-object/from16 v17, v15

    .line 112
    new-instance v15, Ljava/io/File;

    move-object/from16 v18, v1

    invoke-virtual {v3}, Lcom/bachatas4/android/data/ContentTreeEntry;->getRelativePath()Ljava/lang/String;

    move-result-object v1

    invoke-direct {v15, v2, v1}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    invoke-virtual {v15}, Ljava/io/File;->getCanonicalFile()Ljava/io/File;

    move-result-object v1

    .line 113
    invoke-static {v2}, Lkotlin/jvm/internal/Intrinsics;->checkNotNull(Ljava/lang/Object;)V

    invoke-static {v1}, Lkotlin/jvm/internal/Intrinsics;->checkNotNull(Ljava/lang/Object;)V

    invoke-static {v14, v2, v1}, Lcom/bachatas4/android/data/ContentImporter;->access$requireInside(Lcom/bachatas4/android/data/ContentImporter;Ljava/io/File;Ljava/io/File;)V

    .line 114
    invoke-virtual {v1}, Ljava/io/File;->getParentFile()Ljava/io/File;

    move-result-object v15
    :try_end_2
    .catch Ljava/lang/SecurityException; {:try_start_2 .. :try_end_2} :catch_6
    .catchall {:try_start_2 .. :try_end_2} :catchall_6

    if-eqz v15, :cond_9

    :try_start_3
    invoke-virtual {v15}, Ljava/io/File;->mkdirs()Z

    move-result v15

    invoke-static {v15}, Lkotlin/coroutines/jvm/internal/Boxing;->boxBoolean(Z)Ljava/lang/Boolean;
    :try_end_3
    .catch Ljava/lang/SecurityException; {:try_start_3 .. :try_end_3} :catch_1
    .catchall {:try_start_3 .. :try_end_3} :catchall_1

    goto :goto_3

    :catchall_1
    move-exception v0

    goto/16 :goto_9

    :catch_1
    move-exception v0

    goto/16 :goto_a

    :cond_9
    :goto_3
    move-wide/from16 v19, v9

    .line 115
    :try_start_4
    iget-wide v9, v11, Lkotlin/jvm/internal/Ref$LongRef;->element:J

    invoke-virtual {v3}, Lcom/bachatas4/android/data/ContentTreeEntry;->getSourceUri()Ljava/lang/String;

    move-result-object v15

    invoke-static {v6}, Lkotlin/jvm/internal/Intrinsics;->checkNotNull(Ljava/lang/Object;)V

    move-object/from16 v21, v1

    invoke-static/range {p1 .. p1}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v1

    iput-object v1, v0, Lcom/bachatas4/android/data/ContentImporter$importGameTree$2;->L$0:Ljava/lang/Object;

    iput-object v4, v0, Lcom/bachatas4/android/data/ContentImporter$importGameTree$2;->L$1:Ljava/lang/Object;

    iput-object v2, v0, Lcom/bachatas4/android/data/ContentImporter$importGameTree$2;->L$2:Ljava/lang/Object;

    iput-object v6, v0, Lcom/bachatas4/android/data/ContentImporter$importGameTree$2;->L$3:Ljava/lang/Object;

    iput-object v11, v0, Lcom/bachatas4/android/data/ContentImporter$importGameTree$2;->L$4:Ljava/lang/Object;

    invoke-static/range {v17 .. v17}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v1

    iput-object v1, v0, Lcom/bachatas4/android/data/ContentImporter$importGameTree$2;->L$5:Ljava/lang/Object;

    iput-object v14, v0, Lcom/bachatas4/android/data/ContentImporter$importGameTree$2;->L$6:Ljava/lang/Object;

    iput-object v13, v0, Lcom/bachatas4/android/data/ContentImporter$importGameTree$2;->L$7:Ljava/lang/Object;

    iput-object v12, v0, Lcom/bachatas4/android/data/ContentImporter$importGameTree$2;->L$8:Ljava/lang/Object;

    invoke-static/range {v16 .. v16}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v1

    iput-object v1, v0, Lcom/bachatas4/android/data/ContentImporter$importGameTree$2;->L$9:Ljava/lang/Object;

    iput-object v3, v0, Lcom/bachatas4/android/data/ContentImporter$importGameTree$2;->L$10:Ljava/lang/Object;

    invoke-static/range {v21 .. v21}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v1

    iput-object v1, v0, Lcom/bachatas4/android/data/ContentImporter$importGameTree$2;->L$11:Ljava/lang/Object;

    iput-object v11, v0, Lcom/bachatas4/android/data/ContentImporter$importGameTree$2;->L$12:Ljava/lang/Object;

    iput-wide v7, v0, Lcom/bachatas4/android/data/ContentImporter$importGameTree$2;->J$0:J
    :try_end_4
    .catch Ljava/lang/SecurityException; {:try_start_4 .. :try_end_4} :catch_6
    .catchall {:try_start_4 .. :try_end_4} :catchall_6

    move-object/from16 v16, v2

    move-wide/from16 v1, v19

    :try_start_5
    iput-wide v1, v0, Lcom/bachatas4/android/data/ContentImporter$importGameTree$2;->J$1:J

    iput v5, v0, Lcom/bachatas4/android/data/ContentImporter$importGameTree$2;->I$0:I

    iput-wide v9, v0, Lcom/bachatas4/android/data/ContentImporter$importGameTree$2;->J$2:J

    move-wide/from16 v19, v1

    const/4 v1, 0x1

    iput v1, v0, Lcom/bachatas4/android/data/ContentImporter$importGameTree$2;->label:I

    move-object/from16 v2, v21

    invoke-static {v14, v15, v2, v6, v0}, Lcom/bachatas4/android/data/ContentImporter;->access$copyUri(Lcom/bachatas4/android/data/ContentImporter;Ljava/lang/String;Ljava/io/File;Ljava/security/MessageDigest;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;

    move-result-object v2
    :try_end_5
    .catch Ljava/lang/SecurityException; {:try_start_5 .. :try_end_5} :catch_5
    .catchall {:try_start_5 .. :try_end_5} :catchall_5

    move-object/from16 v15, v18

    if-ne v2, v15, :cond_a

    return-object v15

    :cond_a
    move-object v1, v13

    move-object/from16 v18, v14

    move-object v13, v3

    move-object v14, v12

    move-object/from16 v3, p1

    move-object v12, v11

    move-wide/from16 v27, v19

    move-object/from16 v19, v4

    move-object/from16 v20, v17

    move-object/from16 v17, v6

    move v6, v5

    move-wide v4, v9

    move-wide/from16 v9, v27

    :goto_4
    :try_start_6
    check-cast v2, Ljava/lang/Number;

    invoke-virtual {v2}, Ljava/lang/Number;->longValue()J

    move-result-wide v21

    add-long v4, v4, v21

    iput-wide v4, v11, Lkotlin/jvm/internal/Ref$LongRef;->element:J

    if-eqz v1, :cond_b

    .line 116
    iget-wide v4, v12, Lkotlin/jvm/internal/Ref$LongRef;->element:J

    invoke-static {v4, v5}, Lkotlin/coroutines/jvm/internal/Boxing;->boxLong(J)Ljava/lang/Long;

    move-result-object v2

    invoke-static {v7, v8}, Lkotlin/coroutines/jvm/internal/Boxing;->boxLong(J)Ljava/lang/Long;

    move-result-object v4

    invoke-virtual {v13}, Lcom/bachatas4/android/data/ContentTreeEntry;->getRelativePath()Ljava/lang/String;

    move-result-object v5

    invoke-interface {v1, v2, v4, v5}, Lkotlin/jvm/functions/Function3;->invoke(Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;
    :try_end_6
    .catch Ljava/lang/SecurityException; {:try_start_6 .. :try_end_6} :catch_2
    .catchall {:try_start_6 .. :try_end_6} :catchall_2

    :cond_b
    move-object v13, v1

    move v5, v6

    move-object v11, v12

    move-object v12, v14

    move-object v1, v15

    move-object/from16 v2, v16

    move-object/from16 v6, v17

    move-object/from16 v14, v18

    move-object/from16 v4, v19

    move-object/from16 v15, v20

    goto/16 :goto_2

    :catchall_2
    move-exception v0

    move v3, v6

    :goto_5
    move-object/from16 v2, v16

    goto/16 :goto_c

    :catch_2
    move-exception v0

    move v3, v6

    :goto_6
    move-object/from16 v2, v16

    goto/16 :goto_b

    :cond_c
    move-object/from16 v16, v2

    .line 118
    :try_start_7
    iget-object v1, v0, Lcom/bachatas4/android/data/ContentImporter$importGameTree$2;->this$0:Lcom/bachatas4/android/data/ContentImporter;

    iget-object v2, v0, Lcom/bachatas4/android/data/ContentImporter$importGameTree$2;->$request:Lcom/bachatas4/android/data/ContentImportRequest;

    iget-wide v7, v11, Lkotlin/jvm/internal/Ref$LongRef;->element:J

    invoke-static {v1, v2, v7, v8}, Lcom/bachatas4/android/data/ContentImporter;->access$validateBytes(Lcom/bachatas4/android/data/ContentImporter;Lcom/bachatas4/android/data/ContentImportRequest;J)V

    .line 119
    invoke-virtual {v6}, Ljava/security/MessageDigest;->digest()[B

    move-result-object v1

    const-string v2, "digest(...)"

    invoke-static {v1, v2}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullExpressionValue(Ljava/lang/Object;Ljava/lang/String;)V

    const-string v2, ""

    move-object/from16 v18, v2

    check-cast v18, Ljava/lang/CharSequence;

    new-instance v23, Lcom/bachatas4/android/data/ContentImporter$importGameTree$2$$ExternalSyntheticLambda0;

    invoke-direct/range {v23 .. v23}, Lcom/bachatas4/android/data/ContentImporter$importGameTree$2$$ExternalSyntheticLambda0;-><init>()V

    const/16 v24, 0x1e

    const/16 v25, 0x0

    const/16 v19, 0x0

    const/16 v20, 0x0

    const/16 v21, 0x0

    const/16 v22, 0x0

    move-object/from16 v17, v1

    invoke-static/range {v17 .. v25}, Lkotlin/collections/ArraysKt;->joinToString$default([BLjava/lang/CharSequence;Ljava/lang/CharSequence;Ljava/lang/CharSequence;ILjava/lang/CharSequence;Lkotlin/jvm/functions/Function1;ILjava/lang/Object;)Ljava/lang/String;

    move-result-object v1

    .line 120
    iget-object v2, v0, Lcom/bachatas4/android/data/ContentImporter$importGameTree$2;->this$0:Lcom/bachatas4/android/data/ContentImporter;

    iget-object v3, v0, Lcom/bachatas4/android/data/ContentImporter$importGameTree$2;->$request:Lcom/bachatas4/android/data/ContentImportRequest;

    invoke-static {v2, v3, v1}, Lcom/bachatas4/android/data/ContentImporter;->access$validateDigest(Lcom/bachatas4/android/data/ContentImporter;Lcom/bachatas4/android/data/ContentImportRequest;Ljava/lang/String;)V

    .line 121
    iget-object v2, v0, Lcom/bachatas4/android/data/ContentImporter$importGameTree$2;->this$0:Lcom/bachatas4/android/data/ContentImporter;

    .line 122
    invoke-static/range {v16 .. v16}, Lkotlin/jvm/internal/Intrinsics;->checkNotNull(Ljava/lang/Object;)V

    .line 123
    invoke-static {v4}, Lkotlin/jvm/internal/Intrinsics;->checkNotNull(Ljava/lang/Object;)V

    .line 124
    iget-object v3, v0, Lcom/bachatas4/android/data/ContentImporter$importGameTree$2;->$request:Lcom/bachatas4/android/data/ContentImportRequest;

    .line 125
    const-string v20, "folder"
    :try_end_7
    .catch Ljava/lang/SecurityException; {:try_start_7 .. :try_end_7} :catch_5
    .catchall {:try_start_7 .. :try_end_7} :catchall_5

    const/16 v21, 0x0

    const/16 v22, 0x1

    move-object/from16 v19, v3

    move-object/from16 v18, v4

    move-object/from16 v17, v16

    move-object/from16 v16, v2

    .line 121
    :try_start_8
    invoke-static/range {v16 .. v22}, Lcom/bachatas4/android/data/ContentImporter;->access$writeInstallManifestAndPromote(Lcom/bachatas4/android/data/ContentImporter;Ljava/io/File;Ljava/io/File;Lcom/bachatas4/android/data/ContentImportRequest;Ljava/lang/String;Ljava/lang/String;Z)J
    :try_end_8
    .catch Ljava/lang/SecurityException; {:try_start_8 .. :try_end_8} :catch_4
    .catchall {:try_start_8 .. :try_end_8} :catchall_4

    move-object/from16 v16, v17

    .line 130
    :try_start_9
    new-instance v2, Lcom/bachatas4/android/data/ContentImportResult;

    .line 131
    new-instance v17, Lcom/bachatas4/android/model/Game;

    .line 132
    iget-object v3, v0, Lcom/bachatas4/android/data/ContentImporter$importGameTree$2;->$request:Lcom/bachatas4/android/data/ContentImportRequest;

    invoke-virtual {v3}, Lcom/bachatas4/android/data/ContentImportRequest;->getId()Ljava/lang/String;

    move-result-object v18

    .line 133
    iget-object v3, v0, Lcom/bachatas4/android/data/ContentImporter$importGameTree$2;->$request:Lcom/bachatas4/android/data/ContentImportRequest;

    invoke-virtual {v3}, Lcom/bachatas4/android/data/ContentImportRequest;->getTitle()Ljava/lang/String;

    move-result-object v19

    .line 134
    iget-object v3, v0, Lcom/bachatas4/android/data/ContentImporter$importGameTree$2;->$request:Lcom/bachatas4/android/data/ContentImportRequest;

    invoke-virtual {v3}, Lcom/bachatas4/android/data/ContentImportRequest;->getId()Ljava/lang/String;

    move-result-object v3

    new-instance v4, Ljava/lang/StringBuilder;

    invoke-direct {v4}, Ljava/lang/StringBuilder;-><init>()V

    const-string v5, "games/"

    invoke-virtual {v4, v5}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v4

    invoke-virtual {v4, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v3

    invoke-virtual {v3}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v20

    .line 135
    iget-object v3, v0, Lcom/bachatas4/android/data/ContentImporter$importGameTree$2;->$request:Lcom/bachatas4/android/data/ContentImportRequest;

    invoke-virtual {v3}, Lcom/bachatas4/android/data/ContentImportRequest;->getSubtitle()Ljava/lang/String;

    move-result-object v21

    .line 136
    iget-object v0, v0, Lcom/bachatas4/android/data/ContentImporter$importGameTree$2;->$request:Lcom/bachatas4/android/data/ContentImportRequest;

    invoke-virtual {v0}, Lcom/bachatas4/android/data/ContentImportRequest;->getDetail()Ljava/lang/String;

    move-result-object v22

    const/16 v25, 0x20

    const/16 v26, 0x0

    const-wide/16 v23, 0x0

    .line 131
    invoke-direct/range {v17 .. v26}, Lcom/bachatas4/android/model/Game;-><init>(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;JILkotlin/jvm/internal/DefaultConstructorMarker;)V

    move-object/from16 v0, v17

    .line 138
    iget-wide v3, v11, Lkotlin/jvm/internal/Ref$LongRef;->element:J

    .line 130
    invoke-direct {v2, v0, v3, v4, v1}, Lcom/bachatas4/android/data/ContentImportResult;-><init>(Lcom/bachatas4/android/model/Game;JLjava/lang/String;)V
    :try_end_9
    .catch Ljava/lang/SecurityException; {:try_start_9 .. :try_end_9} :catch_3
    .catchall {:try_start_9 .. :try_end_9} :catchall_3

    return-object v2

    :catchall_3
    move-exception v0

    move-object/from16 v2, v16

    const/4 v3, 0x1

    goto :goto_c

    :catch_3
    move-exception v0

    move-object/from16 v2, v16

    const/4 v3, 0x1

    goto :goto_b

    :catchall_4
    move-exception v0

    move-object/from16 v16, v17

    goto :goto_7

    :catch_4
    move-exception v0

    move-object/from16 v16, v17

    goto :goto_8

    :catchall_5
    move-exception v0

    :goto_7
    move v3, v5

    goto/16 :goto_5

    :catch_5
    move-exception v0

    :goto_8
    move v3, v5

    goto/16 :goto_6

    :catchall_6
    move-exception v0

    move-object/from16 v16, v2

    goto :goto_9

    :catch_6
    move-exception v0

    move-object/from16 v16, v2

    goto :goto_a

    :catchall_7
    move-exception v0

    move-object v2, v4

    :goto_9
    move v3, v5

    goto :goto_c

    :catch_7
    move-exception v0

    move-object v2, v4

    :goto_a
    move v3, v5

    .line 142
    :goto_b
    :try_start_a
    new-instance v1, Lcom/bachatas4/android/data/ContentImportException;

    .line 143
    sget-object v4, Lcom/bachatas4/android/model/RuntimeErrorCode;->CONTENT_PERMISSION_LOST:Lcom/bachatas4/android/model/RuntimeErrorCode;

    .line 144
    const-string v5, "Source permission lost"

    .line 145
    check-cast v0, Ljava/lang/Throwable;

    .line 142
    invoke-direct {v1, v4, v5, v0}, Lcom/bachatas4/android/data/ContentImportException;-><init>(Lcom/bachatas4/android/model/RuntimeErrorCode;Ljava/lang/String;Ljava/lang/Throwable;)V

    throw v1
    :try_end_a
    .catchall {:try_start_a .. :try_end_a} :catchall_8

    :catchall_8
    move-exception v0

    :goto_c
    if-nez v3, :cond_d

    .line 148
    invoke-static {v2}, Lkotlin/jvm/internal/Intrinsics;->checkNotNull(Ljava/lang/Object;)V

    invoke-static {v2}, Lkotlin/io/FilesKt;->deleteRecursively(Ljava/io/File;)Z

    :cond_d
    throw v0

    .line 86
    :cond_e
    new-instance v4, Lcom/bachatas4/android/data/ContentImportException;

    sget-object v5, Lcom/bachatas4/android/model/RuntimeErrorCode;->CONTENT_INVALID:Lcom/bachatas4/android/model/RuntimeErrorCode;

    const/4 v8, 0x4

    const/4 v9, 0x0

    const-string v6, "Selected folder has no eboot.bin"

    const/4 v7, 0x0

    invoke-direct/range {v4 .. v9}, Lcom/bachatas4/android/data/ContentImportException;-><init>(Lcom/bachatas4/android/model/RuntimeErrorCode;Ljava/lang/String;Ljava/lang/Throwable;ILkotlin/jvm/internal/DefaultConstructorMarker;)V

    throw v4

    .line 83
    :cond_f
    new-instance v5, Lcom/bachatas4/android/data/ContentImportException;

    sget-object v6, Lcom/bachatas4/android/model/RuntimeErrorCode;->CONTENT_INVALID:Lcom/bachatas4/android/model/RuntimeErrorCode;

    const/4 v9, 0x4

    const/4 v10, 0x0

    const-string v7, "Game already imported"

    const/4 v8, 0x0

    invoke-direct/range {v5 .. v10}, Lcom/bachatas4/android/data/ContentImportException;-><init>(Lcom/bachatas4/android/model/RuntimeErrorCode;Ljava/lang/String;Ljava/lang/Throwable;ILkotlin/jvm/internal/DefaultConstructorMarker;)V

    throw v5
.end method
