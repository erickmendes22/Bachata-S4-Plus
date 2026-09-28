.class public final Lcom/bachatas4/android/data/PkgTreePublisher;
.super Ljava/lang/Object;
.source "PkgTreePublisher.kt"


# annotations
.annotation system Ldalvik/annotation/SourceDebugExtension;
    value = "SMAP\nPkgTreePublisher.kt\nKotlin\n*S Kotlin\n*F\n+ 1 PkgTreePublisher.kt\ncom/bachatas4/android/data/PkgTreePublisher\n+ 2 fake.kt\nkotlin/jvm/internal/FakeKt\n+ 3 _Collections.kt\nkotlin/collections/CollectionsKt___CollectionsKt\n*L\n1#1,104:1\n1#2:105\n2068#3,2:106\n777#3:108\n873#3,2:109\n2002#3,3:111\n*S KotlinDebug\n*F\n+ 1 PkgTreePublisher.kt\ncom/bachatas4/android/data/PkgTreePublisher\n*L\n65#1:106,2\n72#1:108\n72#1:109,2\n73#1:111,3\n*E\n"
.end annotation

.annotation runtime Lkotlin/Metadata;
    d1 = {
        "\u0000>\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0000\n\u0002\u0018\u0002\n\u0002\u0008\u0003\n\u0002\u0010\u000e\n\u0000\n\u0002\u0018\u0002\n\u0002\u0008\u0002\n\u0002\u0018\u0002\n\u0002\u0010\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\u0010\t\n\u0002\u0008\u0006\n\u0002\u0010\u000b\n\u0002\u0008\u0002\u0018\u00002\u00020\u0001B\u000f\u0012\u0006\u0010\u0002\u001a\u00020\u0003\u00a2\u0006\u0004\u0008\u0004\u0010\u0005JV\u0010\u0006\u001a\u00020\u00072\u0006\u0010\u0008\u001a\u00020\t2\u0006\u0010\n\u001a\u00020\u00072\u0014\u0008\u0002\u0010\u000b\u001a\u000e\u0012\u0004\u0012\u00020\u0007\u0012\u0004\u0012\u00020\r0\u000c2 \u0008\u0002\u0010\u000e\u001a\u001a\u0012\u0004\u0012\u00020\u0010\u0012\u0004\u0012\u00020\u0010\u0012\u0004\u0012\u00020\u0007\u0012\u0004\u0012\u00020\r0\u000fH\u0086@\u00a2\u0006\u0002\u0010\u0011J8\u0010\u0012\u001a\u00020\r2\u0006\u0010\u0008\u001a\u00020\t2 \u0008\u0002\u0010\u000e\u001a\u001a\u0012\u0004\u0012\u00020\u0010\u0012\u0004\u0012\u00020\u0010\u0012\u0004\u0012\u00020\u0007\u0012\u0004\u0012\u00020\r0\u000fH\u0086@\u00a2\u0006\u0002\u0010\u0013JH\u0010\u0014\u001a\u00020\r2\u0006\u0010\u0008\u001a\u00020\t2\u0006\u0010\u0015\u001a\u00020\u00072\u001e\u0010\u000e\u001a\u001a\u0012\u0004\u0012\u00020\u0010\u0012\u0004\u0012\u00020\u0010\u0012\u0004\u0012\u00020\u0007\u0012\u0004\u0012\u00020\r0\u000f2\u0008\u0008\u0002\u0010\u0016\u001a\u00020\u0017H\u0082@\u00a2\u0006\u0002\u0010\u0018R\u000e\u0010\u0002\u001a\u00020\u0003X\u0082\u0004\u00a2\u0006\u0002\n\u0000\u00a8\u0006\u0019"
    }
    d2 = {
        "Lcom/bachatas4/android/data/PkgTreePublisher;",
        "",
        "target",
        "Lcom/bachatas4/android/data/PkgExportTarget;",
        "<init>",
        "(Lcom/bachatas4/android/data/PkgExportTarget;)V",
        "publish",
        "",
        "staging",
        "Ljava/io/File;",
        "gameId",
        "onStagingCreated",
        "Lkotlin/Function1;",
        "",
        "onProgress",
        "Lkotlin/Function3;",
        "",
        "(Ljava/io/File;Ljava/lang/String;Lkotlin/jvm/functions/Function1;Lkotlin/jvm/functions/Function3;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;",
        "overlay",
        "(Ljava/io/File;Lkotlin/jvm/functions/Function3;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;",
        "copyTree",
        "destination",
        "replaceExisting",
        "",
        "(Ljava/io/File;Ljava/lang/String;Lkotlin/jvm/functions/Function3;ZLkotlin/coroutines/Continuation;)Ljava/lang/Object;",
        "data"
    }
    k = 0x1
    mv = {
        0x2,
        0x4,
        0x0
    }
    xi = 0x30
.end annotation


# instance fields
.field private final target:Lcom/bachatas4/android/data/PkgExportTarget;


# direct methods
.method public constructor <init>(Lcom/bachatas4/android/data/PkgExportTarget;)V
    .locals 1

    const-string v0, "target"

    invoke-static {p1, v0}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullParameter(Ljava/lang/Object;Ljava/lang/String;)V

    .line 23
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    iput-object p1, p0, Lcom/bachatas4/android/data/PkgTreePublisher;->target:Lcom/bachatas4/android/data/PkgExportTarget;

    return-void
.end method

.method public static final synthetic access$copyTree(Lcom/bachatas4/android/data/PkgTreePublisher;Ljava/io/File;Ljava/lang/String;Lkotlin/jvm/functions/Function3;ZLkotlin/coroutines/Continuation;)Ljava/lang/Object;
    .locals 0

    .line 23
    invoke-direct/range {p0 .. p5}, Lcom/bachatas4/android/data/PkgTreePublisher;->copyTree(Ljava/io/File;Ljava/lang/String;Lkotlin/jvm/functions/Function3;ZLkotlin/coroutines/Continuation;)Ljava/lang/Object;

    move-result-object p0

    return-object p0
.end method

.method private final copyTree(Ljava/io/File;Ljava/lang/String;Lkotlin/jvm/functions/Function3;ZLkotlin/coroutines/Continuation;)Ljava/lang/Object;
    .locals 22
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "(",
            "Ljava/io/File;",
            "Ljava/lang/String;",
            "Lkotlin/jvm/functions/Function3<",
            "-",
            "Ljava/lang/Long;",
            "-",
            "Ljava/lang/Long;",
            "-",
            "Ljava/lang/String;",
            "Lkotlin/Unit;",
            ">;Z",
            "Lkotlin/coroutines/Continuation<",
            "-",
            "Lkotlin/Unit;",
            ">;)",
            "Ljava/lang/Object;"
        }
    .end annotation

    move-object/from16 v0, p0

    move-object/from16 v1, p2

    .line 61
    invoke-virtual/range {p1 .. p1}, Ljava/io/File;->toPath()Ljava/nio/file/Path;

    move-result-object v2

    const/4 v3, 0x0

    new-array v4, v3, [Ljava/nio/file/LinkOption;

    invoke-interface {v2, v4}, Ljava/nio/file/Path;->toRealPath([Ljava/nio/file/LinkOption;)Ljava/nio/file/Path;

    move-result-object v2

    .line 62
    new-array v4, v3, [Ljava/nio/file/LinkOption;

    invoke-static {v2, v4}, Ljava/nio/file/Files;->isDirectory(Ljava/nio/file/Path;[Ljava/nio/file/LinkOption;)Z

    move-result v4

    if-eqz v4, :cond_f

    .line 63
    new-array v4, v3, [Ljava/nio/file/FileVisitOption;

    invoke-static {v2, v4}, Ljava/nio/file/Files;->walk(Ljava/nio/file/Path;[Ljava/nio/file/FileVisitOption;)Ljava/util/stream/Stream;

    move-result-object v4

    check-cast v4, Ljava/lang/AutoCloseable;

    :try_start_0
    move-object v5, v4

    check-cast v5, Ljava/util/stream/Stream;

    invoke-interface {v5}, Ljava/util/stream/Stream;->iterator()Ljava/util/Iterator;

    move-result-object v5

    const-string v6, "iterator(...)"

    invoke-static {v5, v6}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullExpressionValue(Ljava/lang/Object;Ljava/lang/String;)V

    invoke-static {v5}, Lkotlin/sequences/SequencesKt;->asSequence(Ljava/util/Iterator;)Lkotlin/sequences/Sequence;

    move-result-object v5

    invoke-static {v5}, Lkotlin/sequences/SequencesKt;->toList(Lkotlin/sequences/Sequence;)Ljava/util/List;

    move-result-object v5
    :try_end_0
    .catchall {:try_start_0 .. :try_end_0} :catchall_4

    const/4 v6, 0x0

    invoke-static {v4, v6}, Lkotlin/jdk7/AutoCloseableKt;->closeFinally(Ljava/lang/AutoCloseable;Ljava/lang/Throwable;)V

    .line 65
    move-object v4, v5

    check-cast v4, Ljava/lang/Iterable;

    .line 106
    invoke-interface {v4}, Ljava/lang/Iterable;->iterator()Ljava/util/Iterator;

    move-result-object v7

    :goto_0
    invoke-interface {v7}, Ljava/util/Iterator;->hasNext()Z

    move-result v8

    const/4 v9, 0x1

    if-eqz v8, :cond_3

    invoke-interface {v7}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v8

    check-cast v8, Ljava/nio/file/Path;

    .line 66
    invoke-static {v8}, Ljava/nio/file/Files;->isSymbolicLink(Ljava/nio/file/Path;)Z

    move-result v10

    if-nez v10, :cond_2

    .line 67
    new-array v10, v9, [Ljava/nio/file/LinkOption;

    sget-object v11, Ljava/nio/file/LinkOption;->NOFOLLOW_LINKS:Ljava/nio/file/LinkOption;

    aput-object v11, v10, v3

    invoke-static {v8, v10}, Ljava/nio/file/Files;->isDirectory(Ljava/nio/file/Path;[Ljava/nio/file/LinkOption;)Z

    move-result v10

    if-nez v10, :cond_0

    new-array v9, v9, [Ljava/nio/file/LinkOption;

    sget-object v10, Ljava/nio/file/LinkOption;->NOFOLLOW_LINKS:Ljava/nio/file/LinkOption;

    aput-object v10, v9, v3

    invoke-static {v8, v9}, Ljava/nio/file/Files;->isRegularFile(Ljava/nio/file/Path;[Ljava/nio/file/LinkOption;)Z

    move-result v9

    if-eqz v9, :cond_2

    .line 70
    :cond_0
    new-array v9, v3, [Ljava/nio/file/LinkOption;

    invoke-interface {v8, v9}, Ljava/nio/file/Path;->toRealPath([Ljava/nio/file/LinkOption;)Ljava/nio/file/Path;

    move-result-object v8

    invoke-interface {v8, v2}, Ljava/nio/file/Path;->startsWith(Ljava/nio/file/Path;)Z

    move-result v8

    if-eqz v8, :cond_1

    goto :goto_0

    :cond_1
    new-instance v0, Ljava/lang/IllegalStateException;

    const-string v1, "Extracted file escapes the game folder"

    invoke-virtual {v1}, Ljava/lang/Object;->toString()Ljava/lang/String;

    move-result-object v1

    invoke-direct {v0, v1}, Ljava/lang/IllegalStateException;-><init>(Ljava/lang/String;)V

    throw v0

    .line 66
    :cond_2
    new-instance v0, Ljava/lang/IllegalStateException;

    const-string v1, "Extracted package contains an unsupported file"

    invoke-virtual {v1}, Ljava/lang/Object;->toString()Ljava/lang/String;

    move-result-object v1

    invoke-direct {v0, v1}, Ljava/lang/IllegalStateException;-><init>(Ljava/lang/String;)V

    throw v0

    .line 108
    :cond_3
    new-instance v7, Ljava/util/ArrayList;

    invoke-direct {v7}, Ljava/util/ArrayList;-><init>()V

    check-cast v7, Ljava/util/Collection;

    .line 109
    invoke-interface {v4}, Ljava/lang/Iterable;->iterator()Ljava/util/Iterator;

    move-result-object v4

    :cond_4
    :goto_1
    invoke-interface {v4}, Ljava/util/Iterator;->hasNext()Z

    move-result v8

    if-eqz v8, :cond_5

    invoke-interface {v4}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v8

    move-object v10, v8

    check-cast v10, Ljava/nio/file/Path;

    .line 72
    new-array v11, v9, [Ljava/nio/file/LinkOption;

    sget-object v12, Ljava/nio/file/LinkOption;->NOFOLLOW_LINKS:Ljava/nio/file/LinkOption;

    aput-object v12, v11, v3

    invoke-static {v10, v11}, Ljava/nio/file/Files;->isRegularFile(Ljava/nio/file/Path;[Ljava/nio/file/LinkOption;)Z

    move-result v10

    if-eqz v10, :cond_4

    .line 109
    invoke-interface {v7, v8}, Ljava/util/Collection;->add(Ljava/lang/Object;)Z

    goto :goto_1

    .line 110
    :cond_5
    check-cast v7, Ljava/util/List;

    .line 108
    check-cast v7, Ljava/lang/Iterable;

    .line 112
    invoke-interface {v7}, Ljava/lang/Iterable;->iterator()Ljava/util/Iterator;

    move-result-object v4

    const-wide/16 v10, 0x0

    :goto_2
    invoke-interface {v4}, Ljava/util/Iterator;->hasNext()Z

    move-result v12

    if-eqz v12, :cond_6

    invoke-interface {v4}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v12

    check-cast v12, Ljava/nio/file/Path;

    .line 73
    invoke-static {v12}, Ljava/nio/file/Files;->size(Ljava/nio/file/Path;)J

    move-result-wide v12

    invoke-static {v10, v11, v12, v13}, Ljava/lang/Math;->addExact(JJ)J

    move-result-wide v10

    goto :goto_2

    :cond_6
    const/high16 v4, 0x40000

    .line 75
    new-array v4, v4, [B

    .line 76
    invoke-interface {v5}, Ljava/util/List;->iterator()Ljava/util/Iterator;

    move-result-object v5

    const-wide/16 v12, 0x0

    :goto_3
    invoke-interface {v5}, Ljava/util/Iterator;->hasNext()Z

    move-result v14

    if-eqz v14, :cond_e

    invoke-interface {v5}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v14

    check-cast v14, Ljava/nio/file/Path;

    .line 77
    invoke-interface/range {p5 .. p5}, Lkotlin/coroutines/Continuation;->getContext()Lkotlin/coroutines/CoroutineContext;

    move-result-object v15

    invoke-static {v15}, Lkotlinx/coroutines/JobKt;->ensureActive(Lkotlin/coroutines/CoroutineContext;)V

    .line 78
    invoke-static {v14, v2}, Lkotlin/jvm/internal/Intrinsics;->areEqual(Ljava/lang/Object;Ljava/lang/Object;)Z

    move-result v15

    if-nez v15, :cond_d

    .line 79
    invoke-interface {v2, v14}, Ljava/nio/file/Path;->relativize(Ljava/nio/file/Path;)Ljava/nio/file/Path;

    move-result-object v15

    invoke-virtual {v15}, Ljava/lang/Object;->toString()Ljava/lang/String;

    move-result-object v15

    const/4 v7, 0x2

    invoke-static {v15, v3, v7, v6}, Lcom/bachatas4/android/data/GameContentAccessKt;->normalizeGameContentPath$default(Ljava/lang/String;ZILjava/lang/Object;)Ljava/lang/String;

    move-result-object v7

    .line 80
    move-object v8, v1

    check-cast v8, Ljava/lang/CharSequence;

    invoke-interface {v8}, Ljava/lang/CharSequence;->length()I

    move-result v8

    if-nez v8, :cond_7

    move-object v8, v7

    goto :goto_4

    :cond_7
    new-instance v8, Ljava/lang/StringBuilder;

    invoke-direct {v8}, Ljava/lang/StringBuilder;-><init>()V

    invoke-virtual {v8, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v8

    const-string v15, "/"

    invoke-virtual {v8, v15}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v8

    invoke-virtual {v8, v7}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v8

    invoke-virtual {v8}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v8

    .line 81
    :goto_4
    new-array v15, v9, [Ljava/nio/file/LinkOption;

    sget-object v16, Ljava/nio/file/LinkOption;->NOFOLLOW_LINKS:Ljava/nio/file/LinkOption;

    aput-object v16, v15, v3

    invoke-static {v14, v15}, Ljava/nio/file/Files;->isDirectory(Ljava/nio/file/Path;[Ljava/nio/file/LinkOption;)Z

    move-result v15

    if-eqz v15, :cond_9

    if-eqz p4, :cond_8

    .line 82
    iget-object v7, v0, Lcom/bachatas4/android/data/PkgTreePublisher;->target:Lcom/bachatas4/android/data/PkgExportTarget;

    invoke-interface {v7, v8}, Lcom/bachatas4/android/data/PkgExportTarget;->exists(Ljava/lang/String;)Z

    move-result v7

    if-nez v7, :cond_d

    :cond_8
    iget-object v7, v0, Lcom/bachatas4/android/data/PkgTreePublisher;->target:Lcom/bachatas4/android/data/PkgExportTarget;

    invoke-interface {v7, v8}, Lcom/bachatas4/android/data/PkgExportTarget;->createDirectory(Ljava/lang/String;)V

    goto/16 :goto_7

    .line 84
    :cond_9
    invoke-static {v14}, Ljava/nio/file/Files;->size(Ljava/nio/file/Path;)J

    move-result-wide v16

    .line 86
    new-array v15, v3, [Ljava/nio/file/OpenOption;

    invoke-static {v14, v15}, Ljava/nio/file/Files;->newInputStream(Ljava/nio/file/Path;[Ljava/nio/file/OpenOption;)Ljava/io/InputStream;

    move-result-object v14

    check-cast v14, Ljava/io/Closeable;

    :try_start_1
    move-object v15, v14

    check-cast v15, Ljava/io/InputStream;
    :try_end_1
    .catchall {:try_start_1 .. :try_end_1} :catchall_2

    .line 87
    iget-object v9, v0, Lcom/bachatas4/android/data/PkgTreePublisher;->target:Lcom/bachatas4/android/data/PkgExportTarget;

    if-eqz p4, :cond_a

    :try_start_2
    invoke-interface {v9, v8}, Lcom/bachatas4/android/data/PkgExportTarget;->openReplacementFile(Ljava/lang/String;)Ljava/io/OutputStream;

    move-result-object v8

    goto :goto_5

    :cond_a
    invoke-interface {v9, v8}, Lcom/bachatas4/android/data/PkgExportTarget;->openNewFile(Ljava/lang/String;)Ljava/io/OutputStream;

    move-result-object v8

    :goto_5
    check-cast v8, Ljava/io/Closeable;
    :try_end_2
    .catchall {:try_start_2 .. :try_end_2} :catchall_2

    :try_start_3
    move-object v9, v8

    check-cast v9, Ljava/io/OutputStream;

    const-wide/16 v18, 0x0

    .line 89
    :goto_6
    invoke-interface/range {p5 .. p5}, Lkotlin/coroutines/Continuation;->getContext()Lkotlin/coroutines/CoroutineContext;

    move-result-object v20

    invoke-static/range {v20 .. v20}, Lkotlinx/coroutines/JobKt;->ensureActive(Lkotlin/coroutines/CoroutineContext;)V

    .line 90
    invoke-virtual {v15, v4}, Ljava/io/InputStream;->read([B)I

    move-result v6

    if-ltz v6, :cond_b

    .line 92
    invoke-virtual {v9, v4, v3, v6}, Ljava/io/OutputStream;->write([BII)V

    move-object/from16 v21, v4

    int-to-long v3, v6

    add-long v18, v18, v3

    add-long/2addr v12, v3

    .line 95
    invoke-static {v12, v13}, Lkotlin/coroutines/jvm/internal/Boxing;->boxLong(J)Ljava/lang/Long;

    move-result-object v3

    invoke-static {v10, v11}, Lkotlin/coroutines/jvm/internal/Boxing;->boxLong(J)Ljava/lang/Long;

    move-result-object v4

    move-object/from16 v6, p3

    invoke-interface {v6, v3, v4, v7}, Lkotlin/jvm/functions/Function3;->invoke(Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;

    move-object/from16 v4, v21

    const/4 v3, 0x0

    const/4 v6, 0x0

    goto :goto_6

    :cond_b
    move-object/from16 v6, p3

    move-object/from16 v21, v4

    .line 97
    sget-object v3, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;
    :try_end_3
    .catchall {:try_start_3 .. :try_end_3} :catchall_0

    const/4 v3, 0x0

    .line 87
    :try_start_4
    invoke-static {v8, v3}, Lkotlin/io/CloseableKt;->closeFinally(Ljava/io/Closeable;Ljava/lang/Throwable;)V

    .line 98
    sget-object v4, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;
    :try_end_4
    .catchall {:try_start_4 .. :try_end_4} :catchall_2

    .line 86
    invoke-static {v14, v3}, Lkotlin/io/CloseableKt;->closeFinally(Ljava/io/Closeable;Ljava/lang/Throwable;)V

    cmp-long v4, v18, v16

    if-nez v4, :cond_c

    goto :goto_8

    .line 99
    :cond_c
    new-instance v0, Ljava/lang/StringBuilder;

    const-string v1, "Extracted file changed while saving: "

    invoke-direct {v0, v1}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v0, v7}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    new-instance v1, Ljava/lang/IllegalStateException;

    invoke-virtual {v0}, Ljava/lang/Object;->toString()Ljava/lang/String;

    move-result-object v0

    invoke-direct {v1, v0}, Ljava/lang/IllegalStateException;-><init>(Ljava/lang/String;)V

    throw v1

    :catchall_0
    move-exception v0

    move-object v1, v0

    .line 87
    :try_start_5
    throw v1
    :try_end_5
    .catchall {:try_start_5 .. :try_end_5} :catchall_1

    :catchall_1
    move-exception v0

    :try_start_6
    invoke-static {v8, v1}, Lkotlin/io/CloseableKt;->closeFinally(Ljava/io/Closeable;Ljava/lang/Throwable;)V

    throw v0
    :try_end_6
    .catchall {:try_start_6 .. :try_end_6} :catchall_2

    :catchall_2
    move-exception v0

    move-object v1, v0

    .line 86
    :try_start_7
    throw v1
    :try_end_7
    .catchall {:try_start_7 .. :try_end_7} :catchall_3

    :catchall_3
    move-exception v0

    invoke-static {v14, v1}, Lkotlin/io/CloseableKt;->closeFinally(Ljava/io/Closeable;Ljava/lang/Throwable;)V

    throw v0

    :cond_d
    :goto_7
    move-object/from16 v21, v4

    move-object v3, v6

    move-object/from16 v6, p3

    :goto_8
    move-object v6, v3

    move-object/from16 v4, v21

    const/4 v3, 0x0

    const/4 v9, 0x1

    goto/16 :goto_3

    .line 102
    :cond_e
    sget-object v0, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;

    return-object v0

    :catchall_4
    move-exception v0

    move-object v1, v0

    .line 63
    :try_start_8
    throw v1
    :try_end_8
    .catchall {:try_start_8 .. :try_end_8} :catchall_5

    :catchall_5
    move-exception v0

    invoke-static {v4, v1}, Lkotlin/jdk7/AutoCloseableKt;->closeFinally(Ljava/lang/AutoCloseable;Ljava/lang/Throwable;)V

    throw v0

    .line 62
    :cond_f
    new-instance v0, Ljava/lang/IllegalStateException;

    const-string v1, "Extracted game folder is missing"

    invoke-virtual {v1}, Ljava/lang/Object;->toString()Ljava/lang/String;

    move-result-object v1

    invoke-direct {v0, v1}, Ljava/lang/IllegalStateException;-><init>(Ljava/lang/String;)V

    throw v0
.end method

.method static synthetic copyTree$default(Lcom/bachatas4/android/data/PkgTreePublisher;Ljava/io/File;Ljava/lang/String;Lkotlin/jvm/functions/Function3;ZLkotlin/coroutines/Continuation;ILjava/lang/Object;)Ljava/lang/Object;
    .locals 6

    and-int/lit8 p6, p6, 0x8

    if-eqz p6, :cond_0

    const/4 p4, 0x0

    :cond_0
    move-object v0, p0

    move-object v1, p1

    move-object v2, p2

    move-object v3, p3

    move v4, p4

    move-object v5, p5

    .line 55
    invoke-direct/range {v0 .. v5}, Lcom/bachatas4/android/data/PkgTreePublisher;->copyTree(Ljava/io/File;Ljava/lang/String;Lkotlin/jvm/functions/Function3;ZLkotlin/coroutines/Continuation;)Ljava/lang/Object;

    move-result-object p0

    return-object p0
.end method

.method public static synthetic overlay$default(Lcom/bachatas4/android/data/PkgTreePublisher;Ljava/io/File;Lkotlin/jvm/functions/Function3;Lkotlin/coroutines/Continuation;ILjava/lang/Object;)Ljava/lang/Object;
    .locals 0

    and-int/lit8 p4, p4, 0x2

    if-eqz p4, :cond_0

    .line 52
    new-instance p2, Lcom/bachatas4/android/data/PkgTreePublisher$$ExternalSyntheticLambda2;

    invoke-direct {p2}, Lcom/bachatas4/android/data/PkgTreePublisher$$ExternalSyntheticLambda2;-><init>()V

    .line 50
    :cond_0
    invoke-virtual {p0, p1, p2, p3}, Lcom/bachatas4/android/data/PkgTreePublisher;->overlay(Ljava/io/File;Lkotlin/jvm/functions/Function3;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;

    move-result-object p0

    return-object p0
.end method

.method static final overlay$lambda$0(JJLjava/lang/String;)Lkotlin/Unit;
    .locals 0

    const-string p0, "<unused var>"

    invoke-static {p4, p0}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullParameter(Ljava/lang/Object;Ljava/lang/String;)V

    .line 52
    sget-object p0, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;

    return-object p0
.end method

.method public static synthetic publish$default(Lcom/bachatas4/android/data/PkgTreePublisher;Ljava/io/File;Ljava/lang/String;Lkotlin/jvm/functions/Function1;Lkotlin/jvm/functions/Function3;Lkotlin/coroutines/Continuation;ILjava/lang/Object;)Ljava/lang/Object;
    .locals 6

    and-int/lit8 p7, p6, 0x4

    if-eqz p7, :cond_0

    .line 27
    new-instance p3, Lcom/bachatas4/android/data/PkgTreePublisher$$ExternalSyntheticLambda0;

    invoke-direct {p3}, Lcom/bachatas4/android/data/PkgTreePublisher$$ExternalSyntheticLambda0;-><init>()V

    :cond_0
    move-object v3, p3

    and-int/lit8 p3, p6, 0x8

    if-eqz p3, :cond_1

    .line 28
    new-instance p4, Lcom/bachatas4/android/data/PkgTreePublisher$$ExternalSyntheticLambda1;

    invoke-direct {p4}, Lcom/bachatas4/android/data/PkgTreePublisher$$ExternalSyntheticLambda1;-><init>()V

    :cond_1
    move-object v0, p0

    move-object v1, p1

    move-object v2, p2

    move-object v4, p4

    move-object v5, p5

    .line 24
    invoke-virtual/range {v0 .. v5}, Lcom/bachatas4/android/data/PkgTreePublisher;->publish(Ljava/io/File;Ljava/lang/String;Lkotlin/jvm/functions/Function1;Lkotlin/jvm/functions/Function3;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;

    move-result-object p0

    return-object p0
.end method

.method static final publish$lambda$0(Ljava/lang/String;)Lkotlin/Unit;
    .locals 1

    const-string v0, "it"

    invoke-static {p0, v0}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullParameter(Ljava/lang/Object;Ljava/lang/String;)V

    .line 27
    sget-object p0, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;

    return-object p0
.end method

.method static final publish$lambda$1(JJLjava/lang/String;)Lkotlin/Unit;
    .locals 0

    const-string p0, "<unused var>"

    invoke-static {p4, p0}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullParameter(Ljava/lang/Object;Ljava/lang/String;)V

    .line 28
    sget-object p0, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;

    return-object p0
.end method


# virtual methods
.method public final overlay(Ljava/io/File;Lkotlin/jvm/functions/Function3;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;
    .locals 6
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "(",
            "Ljava/io/File;",
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
            "Lkotlin/Unit;",
            ">;)",
            "Ljava/lang/Object;"
        }
    .end annotation

    .line 53
    const-string v2, ""

    const/4 v4, 0x1

    move-object v0, p0

    move-object v1, p1

    move-object v3, p2

    move-object v5, p3

    invoke-direct/range {v0 .. v5}, Lcom/bachatas4/android/data/PkgTreePublisher;->copyTree(Ljava/io/File;Ljava/lang/String;Lkotlin/jvm/functions/Function3;ZLkotlin/coroutines/Continuation;)Ljava/lang/Object;

    move-result-object p0

    return-object p0
.end method

.method public final publish(Ljava/io/File;Ljava/lang/String;Lkotlin/jvm/functions/Function1;Lkotlin/jvm/functions/Function3;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;
    .locals 14
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "(",
            "Ljava/io/File;",
            "Ljava/lang/String;",
            "Lkotlin/jvm/functions/Function1<",
            "-",
            "Ljava/lang/String;",
            "Lkotlin/Unit;",
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
            "Ljava/lang/String;",
            ">;)",
            "Ljava/lang/Object;"
        }
    .end annotation

    move-object/from16 v0, p2

    move-object/from16 v2, p5

    instance-of v3, v2, Lcom/bachatas4/android/data/PkgTreePublisher$publish$1;

    if-eqz v3, :cond_0

    move-object v3, v2

    check-cast v3, Lcom/bachatas4/android/data/PkgTreePublisher$publish$1;

    iget v4, v3, Lcom/bachatas4/android/data/PkgTreePublisher$publish$1;->label:I

    const/high16 v5, -0x80000000

    and-int/2addr v4, v5

    if-eqz v4, :cond_0

    iget v2, v3, Lcom/bachatas4/android/data/PkgTreePublisher$publish$1;->label:I

    sub-int/2addr v2, v5

    iput v2, v3, Lcom/bachatas4/android/data/PkgTreePublisher$publish$1;->label:I

    goto :goto_0

    :cond_0
    new-instance v3, Lcom/bachatas4/android/data/PkgTreePublisher$publish$1;

    invoke-direct {v3, p0, v2}, Lcom/bachatas4/android/data/PkgTreePublisher$publish$1;-><init>(Lcom/bachatas4/android/data/PkgTreePublisher;Lkotlin/coroutines/Continuation;)V

    :goto_0
    move-object v6, v3

    iget-object v2, v6, Lcom/bachatas4/android/data/PkgTreePublisher$publish$1;->result:Ljava/lang/Object;

    invoke-static {}, Lkotlin/coroutines/intrinsics/IntrinsicsKt;->getCOROUTINE_SUSPENDED()Ljava/lang/Object;

    move-result-object v9

    .line 24
    iget v3, v6, Lcom/bachatas4/android/data/PkgTreePublisher$publish$1;->label:I

    const-string v10, " already exists in the selected location"

    const/4 v11, 0x0

    const/4 v12, 0x1

    const-string v13, "A folder named "

    if-eqz v3, :cond_2

    if-ne v3, v12, :cond_1

    iget v12, v6, Lcom/bachatas4/android/data/PkgTreePublisher$publish$1;->I$0:I

    iget-object v0, v6, Lcom/bachatas4/android/data/PkgTreePublisher$publish$1;->L$4:Ljava/lang/Object;

    move-object v3, v0

    check-cast v3, Ljava/lang/String;

    iget-object v0, v6, Lcom/bachatas4/android/data/PkgTreePublisher$publish$1;->L$3:Ljava/lang/Object;

    check-cast v0, Lkotlin/jvm/functions/Function3;

    iget-object v0, v6, Lcom/bachatas4/android/data/PkgTreePublisher$publish$1;->L$2:Ljava/lang/Object;

    check-cast v0, Lkotlin/jvm/functions/Function1;

    iget-object v0, v6, Lcom/bachatas4/android/data/PkgTreePublisher$publish$1;->L$1:Ljava/lang/Object;

    check-cast v0, Ljava/lang/String;

    iget-object v4, v6, Lcom/bachatas4/android/data/PkgTreePublisher$publish$1;->L$0:Ljava/lang/Object;

    check-cast v4, Ljava/io/File;

    :try_start_0
    invoke-static {v2}, Lkotlin/ResultKt;->throwOnFailure(Ljava/lang/Object;)V
    :try_end_0
    .catchall {:try_start_0 .. :try_end_0} :catchall_0

    goto :goto_1

    :catchall_0
    move-exception v0

    move-object v2, v0

    move v11, v12

    goto/16 :goto_2

    :cond_1
    new-instance v0, Ljava/lang/IllegalStateException;

    const-string v1, "call to \'resume\' before \'invoke\' with coroutine"

    invoke-direct {v0, v1}, Ljava/lang/IllegalStateException;-><init>(Ljava/lang/String;)V

    throw v0

    :cond_2
    invoke-static {v2}, Lkotlin/ResultKt;->throwOnFailure(Ljava/lang/Object;)V

    .line 30
    move-object v2, v0

    check-cast v2, Ljava/lang/CharSequence;

    new-instance v3, Lkotlin/text/Regex;

    const-string v4, "[A-Za-z0-9_-]+"

    invoke-direct {v3, v4}, Lkotlin/text/Regex;-><init>(Ljava/lang/String;)V

    invoke-virtual {v3, v2}, Lkotlin/text/Regex;->matches(Ljava/lang/CharSequence;)Z

    move-result v2

    if-eqz v2, :cond_7

    .line 31
    iget-object v2, p0, Lcom/bachatas4/android/data/PkgTreePublisher;->target:Lcom/bachatas4/android/data/PkgExportTarget;

    invoke-interface {v2, v0}, Lcom/bachatas4/android/data/PkgExportTarget;->exists(Ljava/lang/String;)Z

    move-result v2

    if-nez v2, :cond_6

    .line 32
    invoke-static {}, Ljava/util/UUID;->randomUUID()Ljava/util/UUID;

    move-result-object v2

    new-instance v3, Ljava/lang/StringBuilder;

    const-string v4, ".bachata-import-"

    invoke-direct {v3, v4}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v3, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;

    move-result-object v2

    invoke-virtual {v2}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v3

    .line 35
    :try_start_1
    iget-object v2, p0, Lcom/bachatas4/android/data/PkgTreePublisher;->target:Lcom/bachatas4/android/data/PkgExportTarget;

    invoke-interface {v2, v3}, Lcom/bachatas4/android/data/PkgExportTarget;->createDirectory(Ljava/lang/String;)V
    :try_end_1
    .catchall {:try_start_1 .. :try_end_1} :catchall_1

    move-object/from16 v2, p3

    .line 37
    :try_start_2
    invoke-interface {v2, v3}, Lkotlin/jvm/functions/Function1;->invoke(Ljava/lang/Object;)Ljava/lang/Object;

    .line 38
    invoke-static {p1}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v4

    iput-object v4, v6, Lcom/bachatas4/android/data/PkgTreePublisher$publish$1;->L$0:Ljava/lang/Object;

    iput-object v0, v6, Lcom/bachatas4/android/data/PkgTreePublisher$publish$1;->L$1:Ljava/lang/Object;

    invoke-static {v2}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v2

    iput-object v2, v6, Lcom/bachatas4/android/data/PkgTreePublisher$publish$1;->L$2:Ljava/lang/Object;

    invoke-static/range {p4 .. p4}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v2

    iput-object v2, v6, Lcom/bachatas4/android/data/PkgTreePublisher$publish$1;->L$3:Ljava/lang/Object;

    iput-object v3, v6, Lcom/bachatas4/android/data/PkgTreePublisher$publish$1;->L$4:Ljava/lang/Object;

    iput v12, v6, Lcom/bachatas4/android/data/PkgTreePublisher$publish$1;->I$0:I

    iput v12, v6, Lcom/bachatas4/android/data/PkgTreePublisher$publish$1;->label:I

    const/4 v5, 0x0

    const/16 v7, 0x8

    const/4 v8, 0x0

    move-object v1, p0

    move-object v2, p1

    move-object/from16 v4, p4

    invoke-static/range {v1 .. v8}, Lcom/bachatas4/android/data/PkgTreePublisher;->copyTree$default(Lcom/bachatas4/android/data/PkgTreePublisher;Ljava/io/File;Ljava/lang/String;Lkotlin/jvm/functions/Function3;ZLkotlin/coroutines/Continuation;ILjava/lang/Object;)Ljava/lang/Object;

    move-result-object v2

    if-ne v2, v9, :cond_3

    return-object v9

    .line 39
    :cond_3
    :goto_1
    invoke-interface {v6}, Lkotlin/coroutines/Continuation;->getContext()Lkotlin/coroutines/CoroutineContext;

    move-result-object v2

    invoke-static {v2}, Lkotlinx/coroutines/JobKt;->ensureActive(Lkotlin/coroutines/CoroutineContext;)V

    .line 40
    iget-object v2, p0, Lcom/bachatas4/android/data/PkgTreePublisher;->target:Lcom/bachatas4/android/data/PkgExportTarget;

    invoke-interface {v2, v0}, Lcom/bachatas4/android/data/PkgExportTarget;->exists(Ljava/lang/String;)Z

    move-result v2

    if-nez v2, :cond_4

    .line 41
    iget-object v2, p0, Lcom/bachatas4/android/data/PkgTreePublisher;->target:Lcom/bachatas4/android/data/PkgExportTarget;

    invoke-interface {v2, v3, v0}, Lcom/bachatas4/android/data/PkgExportTarget;->rename(Ljava/lang/String;Ljava/lang/String;)Ljava/lang/String;

    move-result-object v0
    :try_end_2
    .catchall {:try_start_2 .. :try_end_2} :catchall_0

    .line 43
    :try_start_3
    iget-object v2, p0, Lcom/bachatas4/android/data/PkgTreePublisher;->target:Lcom/bachatas4/android/data/PkgExportTarget;

    invoke-interface {v2, v0}, Lcom/bachatas4/android/data/PkgExportTarget;->sourceUri(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v0
    :try_end_3
    .catchall {:try_start_3 .. :try_end_3} :catchall_1

    return-object v0

    .line 40
    :cond_4
    :try_start_4
    new-instance v2, Ljava/lang/StringBuilder;

    invoke-direct {v2, v13}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v2, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0, v10}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    new-instance v2, Ljava/lang/IllegalStateException;

    invoke-virtual {v0}, Ljava/lang/Object;->toString()Ljava/lang/String;

    move-result-object v0

    invoke-direct {v2, v0}, Ljava/lang/IllegalStateException;-><init>(Ljava/lang/String;)V

    throw v2
    :try_end_4
    .catchall {:try_start_4 .. :try_end_4} :catchall_0

    :catchall_1
    move-exception v0

    move-object v2, v0

    :goto_2
    if-eqz v11, :cond_5

    .line 45
    :try_start_5
    sget-object v0, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    iget-object v0, p0, Lcom/bachatas4/android/data/PkgTreePublisher;->target:Lcom/bachatas4/android/data/PkgExportTarget;

    invoke-interface {v0, v3}, Lcom/bachatas4/android/data/PkgExportTarget;->delete(Ljava/lang/String;)V

    sget-object v0, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;

    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;
    :try_end_5
    .catchall {:try_start_5 .. :try_end_5} :catchall_2

    goto :goto_3

    :catchall_2
    move-exception v0

    sget-object v1, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    invoke-static {v0}, Lkotlin/ResultKt;->createFailure(Ljava/lang/Throwable;)Ljava/lang/Object;

    move-result-object v0

    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;

    :cond_5
    :goto_3
    throw v2

    .line 31
    :cond_6
    new-instance v1, Ljava/lang/StringBuilder;

    invoke-direct {v1, v13}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v1, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0, v10}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    new-instance v1, Ljava/lang/IllegalStateException;

    invoke-virtual {v0}, Ljava/lang/Object;->toString()Ljava/lang/String;

    move-result-object v0

    invoke-direct {v1, v0}, Ljava/lang/IllegalStateException;-><init>(Ljava/lang/String;)V

    throw v1

    .line 30
    :cond_7
    new-instance v0, Ljava/lang/IllegalArgumentException;

    const-string v1, "Invalid game identifier"

    invoke-virtual {v1}, Ljava/lang/Object;->toString()Ljava/lang/String;

    move-result-object v1

    invoke-direct {v0, v1}, Ljava/lang/IllegalArgumentException;-><init>(Ljava/lang/String;)V

    throw v0
.end method
