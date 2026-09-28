.class public final Lcom/bachatas4/android/data/ContentImporter;
.super Ljava/lang/Object;
.source "ContentImporter.kt"


# annotations
.annotation system Ldalvik/annotation/SourceDebugExtension;
    value = "SMAP\nContentImporter.kt\nKotlin\n*S Kotlin\n*F\n+ 1 ContentImporter.kt\ncom/bachatas4/android/data/ContentImporter\n+ 2 _Sequences.kt\nkotlin/sequences/SequencesKt___SequencesKt\n*L\n1#1,434:1\n1505#2,2:435\n*S KotlinDebug\n*F\n+ 1 ContentImporter.kt\ncom/bachatas4/android/data/ContentImporter\n*L\n246#1:435,2\n*E\n"
.end annotation

.annotation runtime Lkotlin/Metadata;
    d1 = {
        "\u0000n\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\u0010\u000e\n\u0000\n\u0002\u0018\u0002\n\u0002\u0010\t\n\u0002\u0008\u0003\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010 \n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0008\u0004\n\u0002\u0010\u0002\n\u0002\u0008\u000c\n\u0002\u0010\u000b\n\u0002\u0008\u0007\n\u0002\u0018\u0002\n\u0002\u0008\u0002\n\u0002\u0018\u0002\n\u0002\u0008\u000f\u0018\u00002\u00020\u0001B=\u0012\u0006\u0010\u0002\u001a\u00020\u0003\u0012\u0006\u0010\u0004\u001a\u00020\u0005\u0012\u000e\u0008\u0002\u0010\u0006\u001a\u0008\u0012\u0004\u0012\u00020\u00080\u0007\u0012\u0014\u0008\u0002\u0010\t\u001a\u000e\u0012\u0004\u0012\u00020\u0003\u0012\u0004\u0012\u00020\u000b0\n\u00a2\u0006\u0004\u0008\u000c\u0010\rJu\u0010\u000e\u001a\u00020\u000f2\u0006\u0010\u0010\u001a\u00020\u00112\u000c\u0010\u0012\u001a\u0008\u0012\u0004\u0012\u00020\u00140\u00132O\u0008\u0002\u0010\u0015\u001aI\u0012\u0013\u0012\u00110\u000b\u00a2\u0006\u000c\u0008\u0017\u0012\u0008\u0008\u0018\u0012\u0004\u0008\u0008(\u0019\u0012\u0013\u0012\u00110\u000b\u00a2\u0006\u000c\u0008\u0017\u0012\u0008\u0008\u0018\u0012\u0004\u0008\u0008(\u001a\u0012\u0013\u0012\u00110\u0008\u00a2\u0006\u000c\u0008\u0017\u0012\u0008\u0008\u0018\u0012\u0004\u0008\u0008(\u001b\u0012\u0004\u0012\u00020\u001c\u0018\u00010\u0016H\u0086@\u00a2\u0006\u0002\u0010\u001dJ\u0010\u0010\u001e\u001a\u00020\u00082\u0006\u0010\u001f\u001a\u00020\u000bH\u0002J4\u0010 \u001a\u00020\u000f2\u0006\u0010\u0010\u001a\u00020\u00112\u0006\u0010!\u001a\u00020\u00032\u0008\u0008\u0002\u0010\"\u001a\u00020\u00082\n\u0008\u0002\u0010#\u001a\u0004\u0018\u00010\u0008H\u0086@\u00a2\u0006\u0002\u0010$J:\u0010%\u001a\u00020\u000b2\u0006\u0010&\u001a\u00020\u00032\u0006\u0010\'\u001a\u00020\u00032\u0006\u0010\u0010\u001a\u00020\u00112\u0006\u0010\"\u001a\u00020\u00082\u0008\u0010#\u001a\u0004\u0018\u00010\u00082\u0006\u0010(\u001a\u00020)H\u0002J\u0010\u0010*\u001a\u00020\u000b2\u0006\u0010+\u001a\u00020\u0003H\u0002J\u0016\u0010,\u001a\u00020\u000f2\u0006\u0010\u0010\u001a\u00020\u0011H\u0086@\u00a2\u0006\u0002\u0010-J&\u0010.\u001a\u00020\u000b2\u0006\u0010\u0010\u001a\u00020\u00112\u0006\u0010/\u001a\u00020\u00032\u0006\u00100\u001a\u000201H\u0082@\u00a2\u0006\u0002\u00102J0\u00103\u001a\u0002042\u0006\u00105\u001a\u00020\u00082\u0006\u0010!\u001a\u00020\u00032\u0008\u0010#\u001a\u0004\u0018\u00010\u00082\u0006\u00106\u001a\u00020\u0008H\u0086@\u00a2\u0006\u0002\u00107J&\u00108\u001a\u00020\u000b2\u0006\u00106\u001a\u00020\u00082\u0006\u0010/\u001a\u00020\u00032\u0006\u00100\u001a\u000201H\u0082@\u00a2\u0006\u0002\u00109J\u0018\u0010:\u001a\u00020\u001c2\u0006\u0010\u0010\u001a\u00020\u00112\u0006\u0010;\u001a\u00020\u000bH\u0002J\u0018\u0010<\u001a\u00020\u001c2\u0006\u0010\u0010\u001a\u00020\u00112\u0006\u0010=\u001a\u00020\u0008H\u0002J\u0018\u0010>\u001a\u00020\u001c2\u0006\u0010&\u001a\u00020\u00032\u0006\u0010\'\u001a\u00020\u0003H\u0002J\u0010\u0010?\u001a\u00020\u001c2\u0006\u0010@\u001a\u00020\u0008H\u0002J\u0018\u0010A\u001a\u00020\u001c2\u0006\u0010+\u001a\u00020\u00032\u0006\u0010B\u001a\u00020\u0003H\u0002R\u000e\u0010\u0002\u001a\u00020\u0003X\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u000e\u0010\u0004\u001a\u00020\u0005X\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u0014\u0010\u0006\u001a\u0008\u0012\u0004\u0012\u00020\u00080\u0007X\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u001a\u0010\t\u001a\u000e\u0012\u0004\u0012\u00020\u0003\u0012\u0004\u0012\u00020\u000b0\nX\u0082\u0004\u00a2\u0006\u0002\n\u0000\u00a8\u0006C"
    }
    d2 = {
        "Lcom/bachatas4/android/data/ContentImporter;",
        "",
        "filesDir",
        "Ljava/io/File;",
        "source",
        "Lcom/bachatas4/android/data/ImportSource;",
        "idFactory",
        "Lkotlin/Function0;",
        "",
        "availableBytes",
        "Lkotlin/Function1;",
        "",
        "<init>",
        "(Ljava/io/File;Lcom/bachatas4/android/data/ImportSource;Lkotlin/jvm/functions/Function0;Lkotlin/jvm/functions/Function1;)V",
        "importGameTree",
        "Lcom/bachatas4/android/data/ContentImportResult;",
        "request",
        "Lcom/bachatas4/android/data/ContentImportRequest;",
        "entries",
        "",
        "Lcom/bachatas4/android/data/ContentTreeEntry;",
        "onProgress",
        "Lkotlin/Function3;",
        "Lkotlin/ParameterName;",
        "name",
        "bytesCopied",
        "totalBytes",
        "currentFile",
        "",
        "(Lcom/bachatas4/android/data/ContentImportRequest;Ljava/util/List;Lkotlin/jvm/functions/Function3;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;",
        "formatGiB",
        "bytes",
        "finalizeStagingTree",
        "stagingDir",
        "mode",
        "contentId",
        "(Lcom/bachatas4/android/data/ContentImportRequest;Ljava/io/File;Ljava/lang/String;Ljava/lang/String;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;",
        "writeInstallManifestAndPromote",
        "staging",
        "destination",
        "requireFullTree",
        "",
        "walkFileSize",
        "root",
        "importGame",
        "(Lcom/bachatas4/android/data/ContentImportRequest;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;",
        "copySource",
        "payload",
        "digest",
        "Ljava/security/MessageDigest;",
        "(Lcom/bachatas4/android/data/ContentImportRequest;Ljava/io/File;Ljava/security/MessageDigest;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;",
        "overlayStaging",
        "Lcom/bachatas4/android/data/OverlayResult;",
        "gameId",
        "sourceUri",
        "(Ljava/lang/String;Ljava/io/File;Ljava/lang/String;Ljava/lang/String;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;",
        "copyUri",
        "(Ljava/lang/String;Ljava/io/File;Ljava/security/MessageDigest;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;",
        "validateBytes",
        "actualBytes",
        "validateDigest",
        "actualSha256",
        "moveAtomically",
        "validateGameId",
        "id",
        "requireInside",
        "child",
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
.field private final availableBytes:Lkotlin/jvm/functions/Function1;
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "Lkotlin/jvm/functions/Function1<",
            "Ljava/io/File;",
            "Ljava/lang/Long;",
            ">;"
        }
    .end annotation
.end field

.field private final filesDir:Ljava/io/File;

.field private final idFactory:Lkotlin/jvm/functions/Function0;
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "Lkotlin/jvm/functions/Function0<",
            "Ljava/lang/String;",
            ">;"
        }
    .end annotation
.end field

.field private final source:Lcom/bachatas4/android/data/ImportSource;


# direct methods
.method public constructor <init>(Ljava/io/File;Lcom/bachatas4/android/data/ImportSource;Lkotlin/jvm/functions/Function0;Lkotlin/jvm/functions/Function1;)V
    .locals 1
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "(",
            "Ljava/io/File;",
            "Lcom/bachatas4/android/data/ImportSource;",
            "Lkotlin/jvm/functions/Function0<",
            "Ljava/lang/String;",
            ">;",
            "Lkotlin/jvm/functions/Function1<",
            "-",
            "Ljava/io/File;",
            "Ljava/lang/Long;",
            ">;)V"
        }
    .end annotation

    const-string v0, "filesDir"

    invoke-static {p1, v0}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullParameter(Ljava/lang/Object;Ljava/lang/String;)V

    const-string v0, "source"

    invoke-static {p2, v0}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullParameter(Ljava/lang/Object;Ljava/lang/String;)V

    const-string v0, "idFactory"

    invoke-static {p3, v0}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullParameter(Ljava/lang/Object;Ljava/lang/String;)V

    const-string v0, "availableBytes"

    invoke-static {p4, v0}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullParameter(Ljava/lang/Object;Ljava/lang/String;)V

    .line 66
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    .line 67
    iput-object p1, p0, Lcom/bachatas4/android/data/ContentImporter;->filesDir:Ljava/io/File;

    .line 68
    iput-object p2, p0, Lcom/bachatas4/android/data/ContentImporter;->source:Lcom/bachatas4/android/data/ImportSource;

    .line 69
    iput-object p3, p0, Lcom/bachatas4/android/data/ContentImporter;->idFactory:Lkotlin/jvm/functions/Function0;

    .line 70
    iput-object p4, p0, Lcom/bachatas4/android/data/ContentImporter;->availableBytes:Lkotlin/jvm/functions/Function1;

    return-void
.end method

.method public synthetic constructor <init>(Ljava/io/File;Lcom/bachatas4/android/data/ImportSource;Lkotlin/jvm/functions/Function0;Lkotlin/jvm/functions/Function1;ILkotlin/jvm/internal/DefaultConstructorMarker;)V
    .locals 0

    and-int/lit8 p6, p5, 0x4

    if-eqz p6, :cond_0

    .line 69
    new-instance p3, Lcom/bachatas4/android/data/ContentImporter$$ExternalSyntheticLambda0;

    invoke-direct {p3}, Lcom/bachatas4/android/data/ContentImporter$$ExternalSyntheticLambda0;-><init>()V

    :cond_0
    and-int/lit8 p5, p5, 0x8

    if-eqz p5, :cond_1

    .line 70
    sget-object p4, Lcom/bachatas4/android/data/ContentImporter$2;->INSTANCE:Lcom/bachatas4/android/data/ContentImporter$2;

    check-cast p4, Lkotlin/jvm/functions/Function1;

    .line 66
    :cond_1
    invoke-direct {p0, p1, p2, p3, p4}, Lcom/bachatas4/android/data/ContentImporter;-><init>(Ljava/io/File;Lcom/bachatas4/android/data/ImportSource;Lkotlin/jvm/functions/Function0;Lkotlin/jvm/functions/Function1;)V

    return-void
.end method

.method static final _init_$lambda$0()Ljava/lang/String;
    .locals 2

    .line 69
    invoke-static {}, Ljava/util/UUID;->randomUUID()Ljava/util/UUID;

    move-result-object v0

    invoke-virtual {v0}, Ljava/util/UUID;->toString()Ljava/lang/String;

    move-result-object v0

    const-string v1, "toString(...)"

    invoke-static {v0, v1}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullExpressionValue(Ljava/lang/Object;Ljava/lang/String;)V

    return-object v0
.end method

.method public static final synthetic access$copySource(Lcom/bachatas4/android/data/ContentImporter;Lcom/bachatas4/android/data/ContentImportRequest;Ljava/io/File;Ljava/security/MessageDigest;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;
    .locals 0

    .line 66
    invoke-direct {p0, p1, p2, p3, p4}, Lcom/bachatas4/android/data/ContentImporter;->copySource(Lcom/bachatas4/android/data/ContentImportRequest;Ljava/io/File;Ljava/security/MessageDigest;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;

    move-result-object p0

    return-object p0
.end method

.method public static final synthetic access$copyUri(Lcom/bachatas4/android/data/ContentImporter;Ljava/lang/String;Ljava/io/File;Ljava/security/MessageDigest;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;
    .locals 0

    .line 66
    invoke-direct {p0, p1, p2, p3, p4}, Lcom/bachatas4/android/data/ContentImporter;->copyUri(Ljava/lang/String;Ljava/io/File;Ljava/security/MessageDigest;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;

    move-result-object p0

    return-object p0
.end method

.method public static final synthetic access$formatGiB(Lcom/bachatas4/android/data/ContentImporter;J)Ljava/lang/String;
    .locals 0

    .line 66
    invoke-direct {p0, p1, p2}, Lcom/bachatas4/android/data/ContentImporter;->formatGiB(J)Ljava/lang/String;

    move-result-object p0

    return-object p0
.end method

.method public static final synthetic access$getAvailableBytes$p(Lcom/bachatas4/android/data/ContentImporter;)Lkotlin/jvm/functions/Function1;
    .locals 0

    .line 66
    iget-object p0, p0, Lcom/bachatas4/android/data/ContentImporter;->availableBytes:Lkotlin/jvm/functions/Function1;

    return-object p0
.end method

.method public static final synthetic access$getFilesDir$p(Lcom/bachatas4/android/data/ContentImporter;)Ljava/io/File;
    .locals 0

    .line 66
    iget-object p0, p0, Lcom/bachatas4/android/data/ContentImporter;->filesDir:Ljava/io/File;

    return-object p0
.end method

.method public static final synthetic access$getIdFactory$p(Lcom/bachatas4/android/data/ContentImporter;)Lkotlin/jvm/functions/Function0;
    .locals 0

    .line 66
    iget-object p0, p0, Lcom/bachatas4/android/data/ContentImporter;->idFactory:Lkotlin/jvm/functions/Function0;

    return-object p0
.end method

.method public static final synthetic access$requireInside(Lcom/bachatas4/android/data/ContentImporter;Ljava/io/File;Ljava/io/File;)V
    .locals 0

    .line 66
    invoke-direct {p0, p1, p2}, Lcom/bachatas4/android/data/ContentImporter;->requireInside(Ljava/io/File;Ljava/io/File;)V

    return-void
.end method

.method public static final synthetic access$validateBytes(Lcom/bachatas4/android/data/ContentImporter;Lcom/bachatas4/android/data/ContentImportRequest;J)V
    .locals 0

    .line 66
    invoke-direct {p0, p1, p2, p3}, Lcom/bachatas4/android/data/ContentImporter;->validateBytes(Lcom/bachatas4/android/data/ContentImportRequest;J)V

    return-void
.end method

.method public static final synthetic access$validateDigest(Lcom/bachatas4/android/data/ContentImporter;Lcom/bachatas4/android/data/ContentImportRequest;Ljava/lang/String;)V
    .locals 0

    .line 66
    invoke-direct {p0, p1, p2}, Lcom/bachatas4/android/data/ContentImporter;->validateDigest(Lcom/bachatas4/android/data/ContentImportRequest;Ljava/lang/String;)V

    return-void
.end method

.method public static final synthetic access$validateGameId(Lcom/bachatas4/android/data/ContentImporter;Ljava/lang/String;)V
    .locals 0

    .line 66
    invoke-direct {p0, p1}, Lcom/bachatas4/android/data/ContentImporter;->validateGameId(Ljava/lang/String;)V

    return-void
.end method

.method public static final synthetic access$writeInstallManifestAndPromote(Lcom/bachatas4/android/data/ContentImporter;Ljava/io/File;Ljava/io/File;Lcom/bachatas4/android/data/ContentImportRequest;Ljava/lang/String;Ljava/lang/String;Z)J
    .locals 0

    .line 66
    invoke-direct/range {p0 .. p6}, Lcom/bachatas4/android/data/ContentImporter;->writeInstallManifestAndPromote(Ljava/io/File;Ljava/io/File;Lcom/bachatas4/android/data/ContentImportRequest;Ljava/lang/String;Ljava/lang/String;Z)J

    move-result-wide p0

    return-wide p0
.end method

.method private final copySource(Lcom/bachatas4/android/data/ContentImportRequest;Ljava/io/File;Ljava/security/MessageDigest;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;
    .locals 0
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "(",
            "Lcom/bachatas4/android/data/ContentImportRequest;",
            "Ljava/io/File;",
            "Ljava/security/MessageDigest;",
            "Lkotlin/coroutines/Continuation<",
            "-",
            "Ljava/lang/Long;",
            ">;)",
            "Ljava/lang/Object;"
        }
    .end annotation

    .line 317
    invoke-virtual {p1}, Lcom/bachatas4/android/data/ContentImportRequest;->getSourceUri()Ljava/lang/String;

    move-result-object p1

    invoke-direct {p0, p1, p2, p3, p4}, Lcom/bachatas4/android/data/ContentImporter;->copyUri(Ljava/lang/String;Ljava/io/File;Ljava/security/MessageDigest;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;

    move-result-object p0

    return-object p0
.end method

.method private final copyUri(Ljava/lang/String;Ljava/io/File;Ljava/security/MessageDigest;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;
    .locals 6
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "(",
            "Ljava/lang/String;",
            "Ljava/io/File;",
            "Ljava/security/MessageDigest;",
            "Lkotlin/coroutines/Continuation<",
            "-",
            "Ljava/lang/Long;",
            ">;)",
            "Ljava/lang/Object;"
        }
    .end annotation

    .line 364
    iget-object p0, p0, Lcom/bachatas4/android/data/ContentImporter;->source:Lcom/bachatas4/android/data/ImportSource;

    invoke-interface {p0, p1}, Lcom/bachatas4/android/data/ImportSource;->open(Ljava/lang/String;)Ljava/io/InputStream;

    move-result-object p0

    check-cast p0, Ljava/io/Closeable;

    :try_start_0
    move-object p1, p0

    check-cast p1, Ljava/io/InputStream;

    .line 365
    new-instance v0, Ljava/io/FileOutputStream;

    invoke-direct {v0, p2}, Ljava/io/FileOutputStream;-><init>(Ljava/io/File;)V

    check-cast v0, Ljava/io/Closeable;
    :try_end_0
    .catchall {:try_start_0 .. :try_end_0} :catchall_2

    :try_start_1
    move-object p2, v0

    check-cast p2, Ljava/io/FileOutputStream;

    const/16 v1, 0x2000

    .line 366
    new-array v1, v1, [B

    const-wide/16 v2, 0x0

    .line 368
    :goto_0
    invoke-interface {p4}, Lkotlin/coroutines/Continuation;->getContext()Lkotlin/coroutines/CoroutineContext;

    move-result-object v4

    invoke-static {v4}, Lkotlinx/coroutines/JobKt;->ensureActive(Lkotlin/coroutines/CoroutineContext;)V

    .line 369
    invoke-virtual {p1, v1}, Ljava/io/InputStream;->read([B)I

    move-result v4

    if-gez v4, :cond_0

    .line 377
    invoke-virtual {p2}, Ljava/io/FileOutputStream;->getFD()Ljava/io/FileDescriptor;

    move-result-object p1

    invoke-virtual {p1}, Ljava/io/FileDescriptor;->sync()V

    .line 378
    sget-object p1, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;
    :try_end_1
    .catchall {:try_start_1 .. :try_end_1} :catchall_0

    const/4 p1, 0x0

    .line 365
    :try_start_2
    invoke-static {v0, p1}, Lkotlin/io/CloseableKt;->closeFinally(Ljava/io/Closeable;Ljava/lang/Throwable;)V

    .line 379
    sget-object p2, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;
    :try_end_2
    .catchall {:try_start_2 .. :try_end_2} :catchall_2

    .line 364
    invoke-static {p0, p1}, Lkotlin/io/CloseableKt;->closeFinally(Ljava/io/Closeable;Ljava/lang/Throwable;)V

    .line 380
    invoke-static {v2, v3}, Lkotlin/coroutines/jvm/internal/Boxing;->boxLong(J)Ljava/lang/Long;

    move-result-object p0

    return-object p0

    :cond_0
    const/4 v5, 0x0

    .line 373
    :try_start_3
    invoke-virtual {p2, v1, v5, v4}, Ljava/io/FileOutputStream;->write([BII)V

    .line 374
    invoke-virtual {p3, v1, v5, v4}, Ljava/security/MessageDigest;->update([BII)V
    :try_end_3
    .catchall {:try_start_3 .. :try_end_3} :catchall_0

    int-to-long v4, v4

    add-long/2addr v2, v4

    goto :goto_0

    :catchall_0
    move-exception p1

    .line 365
    :try_start_4
    throw p1
    :try_end_4
    .catchall {:try_start_4 .. :try_end_4} :catchall_1

    :catchall_1
    move-exception p2

    :try_start_5
    invoke-static {v0, p1}, Lkotlin/io/CloseableKt;->closeFinally(Ljava/io/Closeable;Ljava/lang/Throwable;)V

    throw p2
    :try_end_5
    .catchall {:try_start_5 .. :try_end_5} :catchall_2

    :catchall_2
    move-exception p1

    .line 364
    :try_start_6
    throw p1
    :try_end_6
    .catchall {:try_start_6 .. :try_end_6} :catchall_3

    :catchall_3
    move-exception p2

    invoke-static {p0, p1}, Lkotlin/io/CloseableKt;->closeFinally(Ljava/io/Closeable;Ljava/lang/Throwable;)V

    throw p2
.end method

.method public static synthetic finalizeStagingTree$default(Lcom/bachatas4/android/data/ContentImporter;Lcom/bachatas4/android/data/ContentImportRequest;Ljava/io/File;Ljava/lang/String;Ljava/lang/String;Lkotlin/coroutines/Continuation;ILjava/lang/Object;)Ljava/lang/Object;
    .locals 6

    and-int/lit8 p7, p6, 0x4

    if-eqz p7, :cond_0

    .line 161
    const-string p3, "pkg"

    :cond_0
    move-object v3, p3

    and-int/lit8 p3, p6, 0x8

    if-eqz p3, :cond_1

    const/4 p4, 0x0

    :cond_1
    move-object v0, p0

    move-object v1, p1

    move-object v2, p2

    move-object v4, p4

    move-object v5, p5

    .line 158
    invoke-virtual/range {v0 .. v5}, Lcom/bachatas4/android/data/ContentImporter;->finalizeStagingTree(Lcom/bachatas4/android/data/ContentImportRequest;Ljava/io/File;Ljava/lang/String;Ljava/lang/String;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;

    move-result-object p0

    return-object p0
.end method

.method private final formatGiB(J)Ljava/lang/String;
    .locals 2

    long-to-double p0, p1

    const-wide/high16 v0, 0x41d0000000000000L    # 1.073741824E9

    div-double/2addr p0, v0

    .line 152
    invoke-static {p0, p1}, Ljava/lang/Double;->valueOf(D)Ljava/lang/Double;

    move-result-object p0

    filled-new-array {p0}, [Ljava/lang/Object;

    move-result-object p0

    const/4 p1, 0x1

    invoke-static {p0, p1}, Ljava/util/Arrays;->copyOf([Ljava/lang/Object;I)[Ljava/lang/Object;

    move-result-object p0

    const-string p1, "%.1f"

    invoke-static {p1, p0}, Ljava/lang/String;->format(Ljava/lang/String;[Ljava/lang/Object;)Ljava/lang/String;

    move-result-object p0

    const-string p1, "format(...)"

    invoke-static {p0, p1}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullExpressionValue(Ljava/lang/Object;Ljava/lang/String;)V

    return-object p0
.end method

.method public static synthetic importGameTree$default(Lcom/bachatas4/android/data/ContentImporter;Lcom/bachatas4/android/data/ContentImportRequest;Ljava/util/List;Lkotlin/jvm/functions/Function3;Lkotlin/coroutines/Continuation;ILjava/lang/Object;)Ljava/lang/Object;
    .locals 0

    and-int/lit8 p5, p5, 0x4

    if-eqz p5, :cond_0

    const/4 p3, 0x0

    .line 72
    :cond_0
    invoke-virtual {p0, p1, p2, p3, p4}, Lcom/bachatas4/android/data/ContentImporter;->importGameTree(Lcom/bachatas4/android/data/ContentImportRequest;Ljava/util/List;Lkotlin/jvm/functions/Function3;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;

    move-result-object p0

    return-object p0
.end method

.method private final moveAtomically(Ljava/io/File;Ljava/io/File;)V
    .locals 2

    .line 411
    :try_start_0
    invoke-virtual {p1}, Ljava/io/File;->toPath()Ljava/nio/file/Path;

    move-result-object p0

    invoke-virtual {p2}, Ljava/io/File;->toPath()Ljava/nio/file/Path;

    move-result-object p1

    const/4 p2, 0x1

    new-array p2, p2, [Ljava/nio/file/CopyOption;

    sget-object v0, Ljava/nio/file/StandardCopyOption;->ATOMIC_MOVE:Ljava/nio/file/StandardCopyOption;

    const/4 v1, 0x0

    aput-object v0, p2, v1

    invoke-static {p0, p1, p2}, Ljava/nio/file/Files;->move(Ljava/nio/file/Path;Ljava/nio/file/Path;[Ljava/nio/file/CopyOption;)Ljava/nio/file/Path;
    :try_end_0
    .catch Ljava/nio/file/AtomicMoveNotSupportedException; {:try_start_0 .. :try_end_0} :catch_0

    return-void

    :catch_0
    move-exception p0

    .line 413
    new-instance p1, Lcom/bachatas4/android/data/ContentImportException;

    sget-object p2, Lcom/bachatas4/android/model/RuntimeErrorCode;->CONTENT_INVALID:Lcom/bachatas4/android/model/RuntimeErrorCode;

    const-string v0, "Atomic rename unavailable"

    check-cast p0, Ljava/lang/Throwable;

    invoke-direct {p1, p2, v0, p0}, Lcom/bachatas4/android/data/ContentImportException;-><init>(Lcom/bachatas4/android/model/RuntimeErrorCode;Ljava/lang/String;Ljava/lang/Throwable;)V

    throw p1
.end method

.method private final requireInside(Ljava/io/File;Ljava/io/File;)V
    .locals 6

    .line 427
    invoke-virtual {p1}, Ljava/io/File;->toPath()Ljava/nio/file/Path;

    move-result-object p0

    .line 428
    invoke-virtual {p2}, Ljava/io/File;->toPath()Ljava/nio/file/Path;

    move-result-object p1

    .line 429
    invoke-interface {p1, p0}, Ljava/nio/file/Path;->startsWith(Ljava/nio/file/Path;)Z

    move-result p0

    if-eqz p0, :cond_0

    return-void

    .line 430
    :cond_0
    new-instance v0, Lcom/bachatas4/android/data/ContentImportException;

    sget-object v1, Lcom/bachatas4/android/model/RuntimeErrorCode;->CONTENT_INVALID:Lcom/bachatas4/android/model/RuntimeErrorCode;

    const/4 v4, 0x4

    const/4 v5, 0x0

    const-string v2, "Import path escapes games dir"

    const/4 v3, 0x0

    invoke-direct/range {v0 .. v5}, Lcom/bachatas4/android/data/ContentImportException;-><init>(Lcom/bachatas4/android/model/RuntimeErrorCode;Ljava/lang/String;Ljava/lang/Throwable;ILkotlin/jvm/internal/DefaultConstructorMarker;)V

    throw v0
.end method

.method private final validateBytes(Lcom/bachatas4/android/data/ContentImportRequest;J)V
    .locals 6

    .line 387
    invoke-virtual {p1}, Lcom/bachatas4/android/data/ContentImportRequest;->getExpectedBytes()Ljava/lang/Long;

    move-result-object p0

    if-eqz p0, :cond_1

    invoke-virtual {p1}, Lcom/bachatas4/android/data/ContentImportRequest;->getExpectedBytes()Ljava/lang/Long;

    move-result-object p0

    if-eqz p0, :cond_0

    invoke-virtual {p0}, Ljava/lang/Long;->longValue()J

    move-result-wide v0

    cmp-long p0, v0, p2

    if-nez p0, :cond_0

    goto :goto_0

    .line 388
    :cond_0
    new-instance v0, Lcom/bachatas4/android/data/ContentImportException;

    .line 389
    sget-object v1, Lcom/bachatas4/android/model/RuntimeErrorCode;->CONTENT_INVALID:Lcom/bachatas4/android/model/RuntimeErrorCode;

    .line 390
    invoke-virtual {p1}, Lcom/bachatas4/android/data/ContentImportRequest;->getExpectedBytes()Ljava/lang/Long;

    move-result-object p0

    new-instance p1, Ljava/lang/StringBuilder;

    const-string v2, "Byte count mismatch: expected "

    invoke-direct {p1, v2}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {p1, p0}, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;

    move-result-object p0

    const-string p1, ", got "

    invoke-virtual {p0, p1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p0

    invoke-virtual {p0, p2, p3}, Ljava/lang/StringBuilder;->append(J)Ljava/lang/StringBuilder;

    move-result-object p0

    invoke-virtual {p0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v2

    const/4 v4, 0x4

    const/4 v5, 0x0

    const/4 v3, 0x0

    .line 388
    invoke-direct/range {v0 .. v5}, Lcom/bachatas4/android/data/ContentImportException;-><init>(Lcom/bachatas4/android/model/RuntimeErrorCode;Ljava/lang/String;Ljava/lang/Throwable;ILkotlin/jvm/internal/DefaultConstructorMarker;)V

    throw v0

    :cond_1
    :goto_0
    return-void
.end method

.method private final validateDigest(Lcom/bachatas4/android/data/ContentImportRequest;Ljava/lang/String;)V
    .locals 6

    .line 399
    invoke-virtual {p1}, Lcom/bachatas4/android/data/ContentImportRequest;->getExpectedSha256()Ljava/lang/String;

    move-result-object p0

    if-eqz p0, :cond_1

    .line 400
    invoke-virtual {p1}, Lcom/bachatas4/android/data/ContentImportRequest;->getExpectedSha256()Ljava/lang/String;

    move-result-object p0

    const/4 p1, 0x1

    invoke-static {p0, p2, p1}, Lkotlin/text/StringsKt;->equals(Ljava/lang/String;Ljava/lang/String;Z)Z

    move-result p0

    if-eqz p0, :cond_0

    goto :goto_0

    .line 402
    :cond_0
    new-instance v0, Lcom/bachatas4/android/data/ContentImportException;

    sget-object v1, Lcom/bachatas4/android/model/RuntimeErrorCode;->CONTENT_INVALID:Lcom/bachatas4/android/model/RuntimeErrorCode;

    const/4 v4, 0x4

    const/4 v5, 0x0

    const-string v2, "SHA-256 mismatch"

    const/4 v3, 0x0

    invoke-direct/range {v0 .. v5}, Lcom/bachatas4/android/data/ContentImportException;-><init>(Lcom/bachatas4/android/model/RuntimeErrorCode;Ljava/lang/String;Ljava/lang/Throwable;ILkotlin/jvm/internal/DefaultConstructorMarker;)V

    throw v0

    :cond_1
    :goto_0
    return-void
.end method

.method private final validateGameId(Ljava/lang/String;)V
    .locals 6

    .line 418
    check-cast p1, Ljava/lang/CharSequence;

    new-instance p0, Lkotlin/text/Regex;

    const-string v0, "[A-Za-z0-9._-]+"

    invoke-direct {p0, v0}, Lkotlin/text/Regex;-><init>(Ljava/lang/String;)V

    invoke-virtual {p0, p1}, Lkotlin/text/Regex;->matches(Ljava/lang/CharSequence;)Z

    move-result p0

    if-eqz p0, :cond_0

    return-void

    .line 419
    :cond_0
    new-instance v0, Lcom/bachatas4/android/data/ContentImportException;

    sget-object v1, Lcom/bachatas4/android/model/RuntimeErrorCode;->CONTENT_INVALID:Lcom/bachatas4/android/model/RuntimeErrorCode;

    const/4 v4, 0x4

    const/4 v5, 0x0

    const-string v2, "Invalid game id"

    const/4 v3, 0x0

    invoke-direct/range {v0 .. v5}, Lcom/bachatas4/android/data/ContentImportException;-><init>(Lcom/bachatas4/android/model/RuntimeErrorCode;Ljava/lang/String;Ljava/lang/Throwable;ILkotlin/jvm/internal/DefaultConstructorMarker;)V

    throw v0
.end method

.method private final walkFileSize(Ljava/io/File;)J
    .locals 6

    .line 246
    invoke-static {p1}, Lkotlin/io/FilesKt;->walkTopDown(Ljava/io/File;)Lkotlin/io/FileTreeWalk;

    move-result-object p0

    check-cast p0, Lkotlin/sequences/Sequence;

    .line 435
    invoke-interface {p0}, Lkotlin/sequences/Sequence;->iterator()Ljava/util/Iterator;

    move-result-object p0

    const-wide/16 v0, 0x0

    move-wide v2, v0

    :cond_0
    :goto_0
    invoke-interface {p0}, Ljava/util/Iterator;->hasNext()Z

    move-result p1

    if-eqz p1, :cond_1

    invoke-interface {p0}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object p1

    check-cast p1, Ljava/io/File;

    .line 247
    invoke-virtual {p1}, Ljava/io/File;->isFile()Z

    move-result v4

    if-eqz v4, :cond_0

    .line 248
    invoke-virtual {p1}, Ljava/io/File;->length()J

    move-result-wide v4

    invoke-static {v4, v5, v0, v1}, Lkotlin/ranges/RangesKt;->coerceAtLeast(JJ)J

    move-result-wide v4

    add-long/2addr v2, v4

    goto :goto_0

    :cond_1
    return-wide v2
.end method

.method private final writeInstallManifestAndPromote(Ljava/io/File;Ljava/io/File;Lcom/bachatas4/android/data/ContentImportRequest;Ljava/lang/String;Ljava/lang/String;Z)J
    .locals 19

    move-object/from16 v0, p1

    .line 210
    const-string v1, "eboot.bin"

    if-eqz p6, :cond_2

    .line 211
    sget-object v2, Lcom/bachatas4/android/data/GameInstallVerifier;->INSTANCE:Lcom/bachatas4/android/data/GameInstallVerifier;

    invoke-virtual/range {p3 .. p3}, Lcom/bachatas4/android/data/ContentImportRequest;->getId()Ljava/lang/String;

    move-result-object v3

    invoke-virtual {v2, v0, v3}, Lcom/bachatas4/android/data/GameInstallVerifier;->verifyTreeForRegistration(Ljava/io/File;Ljava/lang/String;)Lcom/bachatas4/android/data/GameInstallVerifier$VerifyResult;

    move-result-object v2

    .line 212
    instance-of v3, v2, Lcom/bachatas4/android/data/GameInstallVerifier$VerifyResult$Fail;

    if-nez v3, :cond_1

    .line 214
    instance-of v3, v2, Lcom/bachatas4/android/data/GameInstallVerifier$VerifyResult$Ok;

    if-eqz v3, :cond_0

    check-cast v2, Lcom/bachatas4/android/data/GameInstallVerifier$VerifyResult$Ok;

    invoke-virtual {v2}, Lcom/bachatas4/android/data/GameInstallVerifier$VerifyResult$Ok;->getBytesTotal()J

    move-result-wide v2

    goto :goto_0

    .line 211
    :cond_0
    new-instance v0, Lkotlin/NoWhenBranchMatchedException;

    invoke-direct {v0}, Lkotlin/NoWhenBranchMatchedException;-><init>()V

    throw v0

    .line 213
    :cond_1
    new-instance v0, Lcom/bachatas4/android/data/ContentImportException;

    sget-object v1, Lcom/bachatas4/android/model/RuntimeErrorCode;->CONTENT_INVALID:Lcom/bachatas4/android/model/RuntimeErrorCode;

    check-cast v2, Lcom/bachatas4/android/data/GameInstallVerifier$VerifyResult$Fail;

    invoke-virtual {v2}, Lcom/bachatas4/android/data/GameInstallVerifier$VerifyResult$Fail;->getMessage()Ljava/lang/String;

    move-result-object v2

    const/4 v3, 0x4

    const/4 v4, 0x0

    const/4 v5, 0x0

    move-object/from16 p0, v0

    move-object/from16 p1, v1

    move-object/from16 p2, v2

    move/from16 p4, v3

    move-object/from16 p5, v4

    move-object/from16 p3, v5

    invoke-direct/range {p0 .. p5}, Lcom/bachatas4/android/data/ContentImportException;-><init>(Lcom/bachatas4/android/model/RuntimeErrorCode;Ljava/lang/String;Ljava/lang/Throwable;ILkotlin/jvm/internal/DefaultConstructorMarker;)V

    throw v0

    .line 217
    :cond_2
    new-instance v2, Ljava/io/File;

    invoke-direct {v2, v0, v1}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    .line 218
    invoke-virtual {v2}, Ljava/io/File;->isFile()Z

    move-result v3

    if-eqz v3, :cond_4

    invoke-virtual {v2}, Ljava/io/File;->length()J

    move-result-wide v2

    const-wide/16 v4, 0x0

    cmp-long v2, v2, v4

    if-lez v2, :cond_4

    .line 221
    invoke-direct/range {p0 .. p1}, Lcom/bachatas4/android/data/ContentImporter;->walkFileSize(Ljava/io/File;)J

    move-result-wide v2

    :goto_0
    move-wide v14, v2

    .line 223
    sget-object v2, Lcom/bachatas4/android/data/InstallManifestIo;->INSTANCE:Lcom/bachatas4/android/data/InstallManifestIo;

    .line 225
    new-instance v4, Lcom/bachatas4/android/data/InstallManifest;

    .line 227
    invoke-virtual/range {p3 .. p3}, Lcom/bachatas4/android/data/ContentImportRequest;->getId()Ljava/lang/String;

    move-result-object v7

    .line 230
    invoke-virtual/range {p3 .. p3}, Lcom/bachatas4/android/data/ContentImportRequest;->getSourceUri()Ljava/lang/String;

    move-result-object v10

    .line 231
    invoke-static {}, Ljava/lang/System;->currentTimeMillis()J

    move-result-wide v11

    if-eqz p6, :cond_3

    .line 233
    sget-object v1, Lcom/bachatas4/android/data/GameInstallVerifier;->INSTANCE:Lcom/bachatas4/android/data/GameInstallVerifier;

    invoke-virtual {v1}, Lcom/bachatas4/android/data/GameInstallVerifier;->getREQUIRED_FILES()Ljava/util/List;

    move-result-object v1

    goto :goto_1

    .line 235
    :cond_3
    invoke-static {v1}, Lkotlin/collections/CollectionsKt;->listOf(Ljava/lang/Object;)Ljava/util/List;

    move-result-object v1

    :goto_1
    move-object v13, v1

    const/16 v17, 0x201

    const/16 v18, 0x0

    const/4 v5, 0x0

    .line 225
    const-string v6, "INSTALLED"

    const/16 v16, 0x0

    move-object/from16 v9, p4

    move-object/from16 v8, p5

    invoke-direct/range {v4 .. v18}, Lcom/bachatas4/android/data/InstallManifest;-><init>(ILjava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;JLjava/util/List;JLjava/util/List;ILkotlin/jvm/internal/DefaultConstructorMarker;)V

    .line 223
    invoke-virtual {v2, v0, v4}, Lcom/bachatas4/android/data/InstallManifestIo;->write(Ljava/io/File;Lcom/bachatas4/android/data/InstallManifest;)V

    .line 240
    invoke-direct/range {p0 .. p2}, Lcom/bachatas4/android/data/ContentImporter;->moveAtomically(Ljava/io/File;Ljava/io/File;)V

    return-wide v14

    .line 219
    :cond_4
    new-instance v0, Lcom/bachatas4/android/data/ContentImportException;

    sget-object v1, Lcom/bachatas4/android/model/RuntimeErrorCode;->CONTENT_INVALID:Lcom/bachatas4/android/model/RuntimeErrorCode;

    const/4 v2, 0x4

    const/4 v3, 0x0

    const-string v4, "missing eboot.bin"

    const/4 v5, 0x0

    move-object/from16 p0, v0

    move-object/from16 p1, v1

    move/from16 p4, v2

    move-object/from16 p5, v3

    move-object/from16 p2, v4

    move-object/from16 p3, v5

    invoke-direct/range {p0 .. p5}, Lcom/bachatas4/android/data/ContentImportException;-><init>(Lcom/bachatas4/android/model/RuntimeErrorCode;Ljava/lang/String;Ljava/lang/Throwable;ILkotlin/jvm/internal/DefaultConstructorMarker;)V

    throw v0
.end method


# virtual methods
.method public final finalizeStagingTree(Lcom/bachatas4/android/data/ContentImportRequest;Ljava/io/File;Ljava/lang/String;Ljava/lang/String;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;
    .locals 8
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "(",
            "Lcom/bachatas4/android/data/ContentImportRequest;",
            "Ljava/io/File;",
            "Ljava/lang/String;",
            "Ljava/lang/String;",
            "Lkotlin/coroutines/Continuation<",
            "-",
            "Lcom/bachatas4/android/data/ContentImportResult;",
            ">;)",
            "Ljava/lang/Object;"
        }
    .end annotation

    .line 163
    invoke-static {}, Lkotlinx/coroutines/Dispatchers;->getIO()Lkotlinx/coroutines/CoroutineDispatcher;

    move-result-object v0

    check-cast v0, Lkotlin/coroutines/CoroutineContext;

    new-instance v1, Lcom/bachatas4/android/data/ContentImporter$finalizeStagingTree$2;

    const/4 v7, 0x0

    move-object v2, p0

    move-object v3, p1

    move-object v4, p2

    move-object v5, p3

    move-object v6, p4

    invoke-direct/range {v1 .. v7}, Lcom/bachatas4/android/data/ContentImporter$finalizeStagingTree$2;-><init>(Lcom/bachatas4/android/data/ContentImporter;Lcom/bachatas4/android/data/ContentImportRequest;Ljava/io/File;Ljava/lang/String;Ljava/lang/String;Lkotlin/coroutines/Continuation;)V

    check-cast v1, Lkotlin/jvm/functions/Function2;

    invoke-static {v0, v1, p5}, Lkotlinx/coroutines/BuildersKt;->withContext(Lkotlin/coroutines/CoroutineContext;Lkotlin/jvm/functions/Function2;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;

    move-result-object p0

    return-object p0
.end method

.method public final importGame(Lcom/bachatas4/android/data/ContentImportRequest;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;
    .locals 3
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "(",
            "Lcom/bachatas4/android/data/ContentImportRequest;",
            "Lkotlin/coroutines/Continuation<",
            "-",
            "Lcom/bachatas4/android/data/ContentImportResult;",
            ">;)",
            "Ljava/lang/Object;"
        }
    .end annotation

    .line 255
    invoke-static {}, Lkotlinx/coroutines/Dispatchers;->getIO()Lkotlinx/coroutines/CoroutineDispatcher;

    move-result-object v0

    check-cast v0, Lkotlin/coroutines/CoroutineContext;

    new-instance v1, Lcom/bachatas4/android/data/ContentImporter$importGame$2;

    const/4 v2, 0x0

    invoke-direct {v1, p0, p1, v2}, Lcom/bachatas4/android/data/ContentImporter$importGame$2;-><init>(Lcom/bachatas4/android/data/ContentImporter;Lcom/bachatas4/android/data/ContentImportRequest;Lkotlin/coroutines/Continuation;)V

    check-cast v1, Lkotlin/jvm/functions/Function2;

    invoke-static {v0, v1, p2}, Lkotlinx/coroutines/BuildersKt;->withContext(Lkotlin/coroutines/CoroutineContext;Lkotlin/jvm/functions/Function2;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;

    move-result-object p0

    return-object p0
.end method

.method public final importGameTree(Lcom/bachatas4/android/data/ContentImportRequest;Ljava/util/List;Lkotlin/jvm/functions/Function3;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;
    .locals 7
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "(",
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
            "Lcom/bachatas4/android/data/ContentImportResult;",
            ">;)",
            "Ljava/lang/Object;"
        }
    .end annotation

    .line 76
    invoke-static {}, Lkotlinx/coroutines/Dispatchers;->getIO()Lkotlinx/coroutines/CoroutineDispatcher;

    move-result-object v0

    check-cast v0, Lkotlin/coroutines/CoroutineContext;

    new-instance v1, Lcom/bachatas4/android/data/ContentImporter$importGameTree$2;

    const/4 v6, 0x0

    move-object v2, p0

    move-object v3, p1

    move-object v4, p2

    move-object v5, p3

    invoke-direct/range {v1 .. v6}, Lcom/bachatas4/android/data/ContentImporter$importGameTree$2;-><init>(Lcom/bachatas4/android/data/ContentImporter;Lcom/bachatas4/android/data/ContentImportRequest;Ljava/util/List;Lkotlin/jvm/functions/Function3;Lkotlin/coroutines/Continuation;)V

    check-cast v1, Lkotlin/jvm/functions/Function2;

    invoke-static {v0, v1, p4}, Lkotlinx/coroutines/BuildersKt;->withContext(Lkotlin/coroutines/CoroutineContext;Lkotlin/jvm/functions/Function2;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;

    move-result-object p0

    return-object p0
.end method

.method public final overlayStaging(Ljava/lang/String;Ljava/io/File;Ljava/lang/String;Ljava/lang/String;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;
    .locals 1
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "(",
            "Ljava/lang/String;",
            "Ljava/io/File;",
            "Ljava/lang/String;",
            "Ljava/lang/String;",
            "Lkotlin/coroutines/Continuation<",
            "-",
            "Lcom/bachatas4/android/data/OverlayResult;",
            ">;)",
            "Ljava/lang/Object;"
        }
    .end annotation

    .line 331
    invoke-static {}, Lkotlinx/coroutines/Dispatchers;->getIO()Lkotlinx/coroutines/CoroutineDispatcher;

    move-result-object p3

    check-cast p3, Lkotlin/coroutines/CoroutineContext;

    new-instance p4, Lcom/bachatas4/android/data/ContentImporter$overlayStaging$2;

    const/4 v0, 0x0

    invoke-direct {p4, p0, p1, p2, v0}, Lcom/bachatas4/android/data/ContentImporter$overlayStaging$2;-><init>(Lcom/bachatas4/android/data/ContentImporter;Ljava/lang/String;Ljava/io/File;Lkotlin/coroutines/Continuation;)V

    check-cast p4, Lkotlin/jvm/functions/Function2;

    invoke-static {p3, p4, p5}, Lkotlinx/coroutines/BuildersKt;->withContext(Lkotlin/coroutines/CoroutineContext;Lkotlin/jvm/functions/Function2;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;

    move-result-object p0

    return-object p0
.end method
