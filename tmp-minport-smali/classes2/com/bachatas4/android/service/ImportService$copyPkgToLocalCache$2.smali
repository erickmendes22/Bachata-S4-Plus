.class final Lcom/bachatas4/android/service/ImportService$copyPkgToLocalCache$2;
.super Lkotlin/coroutines/jvm/internal/SuspendLambda;
.source "ImportService.kt"

# interfaces
.implements Lkotlin/jvm/functions/Function2;


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lcom/bachatas4/android/service/ImportService;->copyPkgToLocalCache(Landroid/net/Uri;Ljava/io/File;Ljava/lang/String;JLkotlin/coroutines/Continuation;)Ljava/lang/Object;
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
    c = "com.bachatas4.android.service.ImportService$copyPkgToLocalCache$2"
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
.field final synthetic $dest:Ljava/io/File;

.field final synthetic $displayName:Ljava/lang/String;

.field final synthetic $totalHint:J

.field final synthetic $uri:Landroid/net/Uri;

.field private synthetic L$0:Ljava/lang/Object;

.field label:I

.field final synthetic this$0:Lcom/bachatas4/android/service/ImportService;


# direct methods
.method constructor <init>(Lcom/bachatas4/android/service/ImportService;Landroid/net/Uri;Ljava/io/File;JLjava/lang/String;Lkotlin/coroutines/Continuation;)V
    .locals 0
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "(",
            "Lcom/bachatas4/android/service/ImportService;",
            "Landroid/net/Uri;",
            "Ljava/io/File;",
            "J",
            "Ljava/lang/String;",
            "Lkotlin/coroutines/Continuation<",
            "-",
            "Lcom/bachatas4/android/service/ImportService$copyPkgToLocalCache$2;",
            ">;)V"
        }
    .end annotation

    iput-object p1, p0, Lcom/bachatas4/android/service/ImportService$copyPkgToLocalCache$2;->this$0:Lcom/bachatas4/android/service/ImportService;

    iput-object p2, p0, Lcom/bachatas4/android/service/ImportService$copyPkgToLocalCache$2;->$uri:Landroid/net/Uri;

    iput-object p3, p0, Lcom/bachatas4/android/service/ImportService$copyPkgToLocalCache$2;->$dest:Ljava/io/File;

    iput-wide p4, p0, Lcom/bachatas4/android/service/ImportService$copyPkgToLocalCache$2;->$totalHint:J

    iput-object p6, p0, Lcom/bachatas4/android/service/ImportService$copyPkgToLocalCache$2;->$displayName:Ljava/lang/String;

    const/4 p1, 0x2

    invoke-direct {p0, p1, p7}, Lkotlin/coroutines/jvm/internal/SuspendLambda;-><init>(ILkotlin/coroutines/Continuation;)V

    return-void
.end method


# virtual methods
.method public final create(Ljava/lang/Object;Lkotlin/coroutines/Continuation;)Lkotlin/coroutines/Continuation;
    .locals 8
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

    new-instance v0, Lcom/bachatas4/android/service/ImportService$copyPkgToLocalCache$2;

    iget-object v1, p0, Lcom/bachatas4/android/service/ImportService$copyPkgToLocalCache$2;->this$0:Lcom/bachatas4/android/service/ImportService;

    iget-object v2, p0, Lcom/bachatas4/android/service/ImportService$copyPkgToLocalCache$2;->$uri:Landroid/net/Uri;

    iget-object v3, p0, Lcom/bachatas4/android/service/ImportService$copyPkgToLocalCache$2;->$dest:Ljava/io/File;

    iget-wide v4, p0, Lcom/bachatas4/android/service/ImportService$copyPkgToLocalCache$2;->$totalHint:J

    iget-object v6, p0, Lcom/bachatas4/android/service/ImportService$copyPkgToLocalCache$2;->$displayName:Ljava/lang/String;

    move-object v7, p2

    invoke-direct/range {v0 .. v7}, Lcom/bachatas4/android/service/ImportService$copyPkgToLocalCache$2;-><init>(Lcom/bachatas4/android/service/ImportService;Landroid/net/Uri;Ljava/io/File;JLjava/lang/String;Lkotlin/coroutines/Continuation;)V

    iput-object p1, v0, Lcom/bachatas4/android/service/ImportService$copyPkgToLocalCache$2;->L$0:Ljava/lang/Object;

    check-cast v0, Lkotlin/coroutines/Continuation;

    return-object v0
.end method

.method public bridge synthetic invoke(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;
    .locals 0

    check-cast p1, Lkotlinx/coroutines/CoroutineScope;

    check-cast p2, Lkotlin/coroutines/Continuation;

    invoke-virtual {p0, p1, p2}, Lcom/bachatas4/android/service/ImportService$copyPkgToLocalCache$2;->invoke(Lkotlinx/coroutines/CoroutineScope;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;

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

    invoke-virtual {p0, p1, p2}, Lcom/bachatas4/android/service/ImportService$copyPkgToLocalCache$2;->create(Ljava/lang/Object;Lkotlin/coroutines/Continuation;)Lkotlin/coroutines/Continuation;

    move-result-object p0

    check-cast p0, Lcom/bachatas4/android/service/ImportService$copyPkgToLocalCache$2;

    sget-object p1, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;

    invoke-virtual {p0, p1}, Lcom/bachatas4/android/service/ImportService$copyPkgToLocalCache$2;->invokeSuspend(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object p0

    return-object p0
.end method

.method public final invokeSuspend(Ljava/lang/Object;)Ljava/lang/Object;
    .locals 24

    move-object/from16 v0, p0

    iget-object v1, v0, Lcom/bachatas4/android/service/ImportService$copyPkgToLocalCache$2;->L$0:Ljava/lang/Object;

    check-cast v1, Lkotlinx/coroutines/CoroutineScope;

    invoke-static {}, Lkotlin/coroutines/intrinsics/IntrinsicsKt;->getCOROUTINE_SUSPENDED()Ljava/lang/Object;

    .line 937
    iget v2, v0, Lcom/bachatas4/android/service/ImportService$copyPkgToLocalCache$2;->label:I

    if-nez v2, :cond_6

    invoke-static/range {p1 .. p1}, Lkotlin/ResultKt;->throwOnFailure(Ljava/lang/Object;)V

    .line 938
    iget-object v2, v0, Lcom/bachatas4/android/service/ImportService$copyPkgToLocalCache$2;->this$0:Lcom/bachatas4/android/service/ImportService;

    invoke-virtual {v2}, Lcom/bachatas4/android/service/ImportService;->getContentResolver()Landroid/content/ContentResolver;

    move-result-object v2

    iget-object v3, v0, Lcom/bachatas4/android/service/ImportService$copyPkgToLocalCache$2;->$uri:Landroid/net/Uri;

    invoke-virtual {v2, v3}, Landroid/content/ContentResolver;->openInputStream(Landroid/net/Uri;)Ljava/io/InputStream;

    move-result-object v2

    if-eqz v2, :cond_5

    .line 940
    check-cast v2, Ljava/io/Closeable;

    iget-object v3, v0, Lcom/bachatas4/android/service/ImportService$copyPkgToLocalCache$2;->$dest:Ljava/io/File;

    iget-wide v7, v0, Lcom/bachatas4/android/service/ImportService$copyPkgToLocalCache$2;->$totalHint:J

    iget-object v15, v0, Lcom/bachatas4/android/service/ImportService$copyPkgToLocalCache$2;->$displayName:Ljava/lang/String;

    iget-object v0, v0, Lcom/bachatas4/android/service/ImportService$copyPkgToLocalCache$2;->this$0:Lcom/bachatas4/android/service/ImportService;

    :try_start_0
    move-object v11, v2

    check-cast v11, Ljava/io/InputStream;

    .line 941
    new-instance v4, Ljava/io/FileOutputStream;

    invoke-direct {v4, v3}, Ljava/io/FileOutputStream;-><init>(Ljava/io/File;)V

    move-object v3, v4

    check-cast v3, Ljava/io/Closeable;
    :try_end_0
    .catchall {:try_start_0 .. :try_end_0} :catchall_2

    :try_start_1
    move-object v12, v3

    check-cast v12, Ljava/io/FileOutputStream;

    const/high16 v4, 0x100000

    .line 942
    new-array v13, v4, [B

    const-wide/16 v16, 0x0

    move-wide/from16 v4, v16

    move-wide v9, v4

    .line 946
    :goto_0
    invoke-interface {v1}, Lkotlinx/coroutines/CoroutineScope;->getCoroutineContext()Lkotlin/coroutines/CoroutineContext;

    move-result-object v6

    invoke-static {v6}, Lkotlinx/coroutines/JobKt;->ensureActive(Lkotlin/coroutines/CoroutineContext;)V

    .line 947
    invoke-virtual {v11, v13}, Ljava/io/InputStream;->read([B)I

    move-result v6

    if-ltz v6, :cond_3

    const/4 v14, 0x0

    .line 949
    invoke-virtual {v12, v13, v14, v6}, Ljava/io/FileOutputStream;->write([BII)V

    move-object/from16 p1, v15

    int-to-long v14, v6

    add-long v5, v4, v14

    .line 951
    invoke-static {}, Ljava/lang/System;->currentTimeMillis()J

    move-result-wide v14

    sub-long v18, v14, v9

    const-wide/16 v20, 0xfa

    cmp-long v4, v18, v20

    if-ltz v4, :cond_2

    .line 954
    sget-object v4, Lcom/bachatas4/android/data/ImportManager;->INSTANCE:Lcom/bachatas4/android/data/ImportManager;

    move-object v9, v4

    .line 955
    new-instance v4, Lcom/bachatas4/android/data/ImportProgress$Copying;

    move-object v10, v9

    .line 958
    const-string v9, "Local PKG cache"

    move-object/from16 v18, v1

    move-object v1, v10

    move-object/from16 v10, p1

    .line 955
    invoke-direct/range {v4 .. v10}, Lcom/bachatas4/android/data/ImportProgress$Copying;-><init>(JJLjava/lang/String;Ljava/lang/String;)V

    move-wide/from16 v22, v14

    move-object v15, v10

    move-wide/from16 v9, v22

    check-cast v4, Lcom/bachatas4/android/data/ImportProgress;

    .line 954
    invoke-virtual {v1, v4}, Lcom/bachatas4/android/data/ImportManager;->update(Lcom/bachatas4/android/data/ImportProgress;)V

    .line 962
    invoke-static {}, Lcom/bachatas4/android/service/ImportService;->access$getCompanion$p()Lcom/bachatas4/android/service/ImportService$Companion;

    move-result-object v1

    invoke-virtual {v1, v5, v6, v7, v8}, Lcom/bachatas4/android/service/ImportService$Companion;->scaledProgress(JJ)Lkotlin/Pair;

    move-result-object v1

    invoke-virtual {v1}, Lkotlin/Pair;->component1()Ljava/lang/Object;

    move-result-object v4

    check-cast v4, Ljava/lang/Number;

    invoke-virtual {v4}, Ljava/lang/Number;->intValue()I

    move-result v4

    invoke-virtual {v1}, Lkotlin/Pair;->component2()Ljava/lang/Object;

    move-result-object v1

    check-cast v1, Ljava/lang/Number;

    invoke-virtual {v1}, Ljava/lang/Number;->intValue()I

    move-result v1

    cmp-long v14, v7, v16

    if-lez v14, :cond_0

    .line 964
    invoke-static {}, Lcom/bachatas4/android/service/ImportService;->access$getCompanion$p()Lcom/bachatas4/android/service/ImportService$Companion;

    move-result-object v14

    invoke-virtual {v14, v5, v6}, Lcom/bachatas4/android/service/ImportService$Companion;->formatBytes(J)Ljava/lang/String;

    move-result-object v14

    move-wide/from16 v19, v9

    invoke-static {}, Lcom/bachatas4/android/service/ImportService;->access$getCompanion$p()Lcom/bachatas4/android/service/ImportService$Companion;

    move-result-object v9

    invoke-virtual {v9, v7, v8}, Lcom/bachatas4/android/service/ImportService$Companion;->formatBytes(J)Ljava/lang/String;

    move-result-object v9

    new-instance v10, Ljava/lang/StringBuilder;

    invoke-direct {v10}, Ljava/lang/StringBuilder;-><init>()V

    invoke-virtual {v10, v14}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v10

    const-string v14, " / "

    invoke-virtual {v10, v14}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v10

    invoke-virtual {v10, v9}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v9

    invoke-virtual {v9}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v9

    goto :goto_1

    :cond_0
    move-wide/from16 v19, v9

    .line 966
    invoke-static {}, Lcom/bachatas4/android/service/ImportService;->access$getCompanion$p()Lcom/bachatas4/android/service/ImportService$Companion;

    move-result-object v9

    invoke-virtual {v9, v5, v6}, Lcom/bachatas4/android/service/ImportService$Companion;->formatBytes(J)Ljava/lang/String;

    move-result-object v9

    .line 969
    :goto_1
    new-instance v10, Ljava/lang/StringBuilder;

    invoke-direct {v10}, Ljava/lang/StringBuilder;-><init>()V

    const-string v14, "Copying PKG to device \u00b7 "

    invoke-virtual {v10, v14}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v10

    invoke-virtual {v10, v9}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v9

    invoke-virtual {v9}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v9

    if-nez v4, :cond_1

    const/4 v14, 0x1

    goto :goto_2

    :cond_1
    const/4 v14, 0x0

    .line 968
    :goto_2
    invoke-static {v0, v9, v4, v1, v14}, Lcom/bachatas4/android/service/ImportService;->access$updateNotification(Lcom/bachatas4/android/service/ImportService;Ljava/lang/String;IIZ)V

    move-wide v4, v5

    move-object/from16 v1, v18

    move-wide/from16 v9, v19

    goto/16 :goto_0

    :cond_2
    move-object/from16 v15, p1

    move-wide v4, v5

    goto/16 :goto_0

    .line 976
    :cond_3
    invoke-virtual {v12}, Ljava/io/FileOutputStream;->getFD()Ljava/io/FileDescriptor;

    move-result-object v0

    invoke-virtual {v0}, Ljava/io/FileDescriptor;->sync()V

    .line 977
    sget-object v0, Lcom/bachatas4/android/data/ImportManager;->INSTANCE:Lcom/bachatas4/android/data/ImportManager;

    .line 978
    new-instance v9, Lcom/bachatas4/android/data/ImportProgress$Copying;

    cmp-long v1, v7, v16

    if-lez v1, :cond_4

    move-wide v12, v7

    goto :goto_3

    :cond_4
    move-wide v12, v4

    .line 981
    :goto_3
    const-string v14, "Local PKG cache"

    move-wide v10, v4

    .line 978
    invoke-direct/range {v9 .. v15}, Lcom/bachatas4/android/data/ImportProgress$Copying;-><init>(JJLjava/lang/String;Ljava/lang/String;)V

    check-cast v9, Lcom/bachatas4/android/data/ImportProgress;

    .line 977
    invoke-virtual {v0, v9}, Lcom/bachatas4/android/data/ImportManager;->update(Lcom/bachatas4/android/data/ImportProgress;)V

    .line 985
    sget-object v0, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;
    :try_end_1
    .catchall {:try_start_1 .. :try_end_1} :catchall_0

    const/4 v0, 0x0

    .line 941
    :try_start_2
    invoke-static {v3, v0}, Lkotlin/io/CloseableKt;->closeFinally(Ljava/io/Closeable;Ljava/lang/Throwable;)V

    .line 986
    sget-object v1, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;
    :try_end_2
    .catchall {:try_start_2 .. :try_end_2} :catchall_2

    .line 940
    invoke-static {v2, v0}, Lkotlin/io/CloseableKt;->closeFinally(Ljava/io/Closeable;Ljava/lang/Throwable;)V

    .line 987
    sget-object v0, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;

    return-object v0

    :catchall_0
    move-exception v0

    move-object v1, v0

    .line 941
    :try_start_3
    throw v1
    :try_end_3
    .catchall {:try_start_3 .. :try_end_3} :catchall_1

    :catchall_1
    move-exception v0

    :try_start_4
    invoke-static {v3, v1}, Lkotlin/io/CloseableKt;->closeFinally(Ljava/io/Closeable;Ljava/lang/Throwable;)V

    throw v0
    :try_end_4
    .catchall {:try_start_4 .. :try_end_4} :catchall_2

    :catchall_2
    move-exception v0

    move-object v1, v0

    .line 940
    :try_start_5
    throw v1
    :try_end_5
    .catchall {:try_start_5 .. :try_end_5} :catchall_3

    :catchall_3
    move-exception v0

    invoke-static {v2, v1}, Lkotlin/io/CloseableKt;->closeFinally(Ljava/io/Closeable;Ljava/lang/Throwable;)V

    throw v0

    .line 938
    :cond_5
    new-instance v0, Ljava/lang/IllegalStateException;

    .line 939
    const-string v1, "Cannot open PKG stream for local cache"

    invoke-virtual {v1}, Ljava/lang/Object;->toString()Ljava/lang/String;

    move-result-object v1

    invoke-direct {v0, v1}, Ljava/lang/IllegalStateException;-><init>(Ljava/lang/String;)V

    throw v0

    .line 937
    :cond_6
    new-instance v0, Ljava/lang/IllegalStateException;

    const-string v1, "call to \'resume\' before \'invoke\' with coroutine"

    invoke-direct {v0, v1}, Ljava/lang/IllegalStateException;-><init>(Ljava/lang/String;)V

    throw v0
.end method
