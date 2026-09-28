.class public final Lcom/bachatas4/android/service/SafBrokerSession;
.super Ljava/lang/Object;
.source "SafGameBroker.kt"

# interfaces
.implements Ljava/io/Closeable;


# annotations
.annotation system Ldalvik/annotation/MemberClasses;
    value = {
        Lcom/bachatas4/android/service/SafBrokerSession$Companion;
    }
.end annotation

.annotation system Ldalvik/annotation/SourceDebugExtension;
    value = "SMAP\nSafGameBroker.kt\nKotlin\n*S Kotlin\n*F\n+ 1 SafGameBroker.kt\ncom/bachatas4/android/service/SafBrokerSession\n+ 2 fake.kt\nkotlin/jvm/internal/FakeKt\n+ 3 _Collections.kt\nkotlin/collections/CollectionsKt___CollectionsKt\n*L\n1#1,224:1\n1#2:225\n2068#3,2:226\n2068#3,2:228\n*S KotlinDebug\n*F\n+ 1 SafGameBroker.kt\ncom/bachatas4/android/service/SafBrokerSession\n*L\n156#1:226,2\n191#1:228,2\n*E\n"
.end annotation

.annotation runtime Lkotlin/Metadata;
    d1 = {
        "\u0000r\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\u000e\n\u0002\u0008\u0002\n\u0002\u0018\u0002\n\u0002\u0008\u0006\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\u0008\u0003\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0010\u000b\n\u0000\n\u0002\u0010\u0002\n\u0002\u0008\u0004\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\u0008\n\u0000\n\u0002\u0010\u0012\n\u0002\u0008\u0003\n\u0002\u0010\t\n\u0002\u0008\u0003\n\u0002\u0010 \n\u0002\u0018\u0002\n\u0002\u0008\u0002\n\u0002\u0018\u0002\n\u0000\u0008\u0007\u0018\u0000 ,2\u00020\u0001:\u0001,B)\u0008\u0000\u0012\u0006\u0010\u0002\u001a\u00020\u0003\u0012\u0006\u0010\u0004\u001a\u00020\u0005\u0012\u0006\u0010\u0006\u001a\u00020\u0005\u0012\u0006\u0010\u0007\u001a\u00020\u0008\u00a2\u0006\u0004\u0008\t\u0010\nJ\u0010\u0010\u0018\u001a\u00020\u00192\u0006\u0010\u001a\u001a\u00020\u0016H\u0002J\u0008\u0010\u001b\u001a\u00020\u0019H\u0016J\"\u0010\u001c\u001a\u00020\u00192\u0006\u0010\u001d\u001a\u00020\u001e2\u0006\u0010\u001f\u001a\u00020 2\u0008\u0010!\u001a\u0004\u0018\u00010\"H\u0002J \u0010#\u001a\u00020\"2\u0006\u0010$\u001a\u00020\u00172\u0006\u0010%\u001a\u00020&2\u0006\u0010\'\u001a\u00020&H\u0002J\u0016\u0010(\u001a\u00020\"2\u000c\u0010)\u001a\u0008\u0012\u0004\u0012\u00020+0*H\u0002R\u000e\u0010\u0002\u001a\u00020\u0003X\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u0011\u0010\u0004\u001a\u00020\u0005\u00a2\u0006\u0008\n\u0000\u001a\u0004\u0008\u000b\u0010\u000cR\u0011\u0010\u0006\u001a\u00020\u0005\u00a2\u0006\u0008\n\u0000\u001a\u0004\u0008\r\u0010\u000cR\u000e\u0010\u0007\u001a\u00020\u0008X\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u000e\u0010\u000e\u001a\u00020\u000fX\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u0016\u0010\u0010\u001a\n \u0012*\u0004\u0018\u00010\u00110\u0011X\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u0016\u0010\u0013\u001a\n \u0012*\u0004\u0018\u00010\u00110\u0011X\u0082\u0004\u00a2\u0006\u0002\n\u0000RN\u0010\u0014\u001aB\u0012\u000c\u0012\n \u0012*\u0004\u0018\u00010\u00160\u0016\u0012\u000c\u0012\n \u0012*\u0004\u0018\u00010\u00170\u0017 \u0012* \u0012\u000c\u0012\n \u0012*\u0004\u0018\u00010\u00160\u0016\u0012\u000c\u0012\n \u0012*\u0004\u0018\u00010\u00170\u0017\u0018\u00010\u00150\u0015X\u0082\u0004\u00a2\u0006\u0002\n\u0000\u00ca\u0001\u000c\u0008.\u0012\u0008\u0008/\u0012\u0004\u0008\u0003\u0010\u0000\u00a8\u0006-"
    }
    d2 = {
        "Lcom/bachatas4/android/service/SafBrokerSession;",
        "Ljava/io/Closeable;",
        "server",
        "Landroid/net/LocalServerSocket;",
        "socketName",
        "",
        "token",
        "tree",
        "Lcom/bachatas4/android/data/AndroidGameDocumentTree;",
        "<init>",
        "(Landroid/net/LocalServerSocket;Ljava/lang/String;Ljava/lang/String;Lcom/bachatas4/android/data/AndroidGameDocumentTree;)V",
        "getSocketName",
        "()Ljava/lang/String;",
        "getToken",
        "closed",
        "Ljava/util/concurrent/atomic/AtomicBoolean;",
        "acceptor",
        "Ljava/util/concurrent/ExecutorService;",
        "kotlin.jvm.PlatformType",
        "workers",
        "activeSockets",
        "Ljava/util/concurrent/ConcurrentHashMap$KeySetView;",
        "Landroid/net/LocalSocket;",
        "",
        "serve",
        "",
        "socket",
        "close",
        "respond",
        "output",
        "Ljava/io/DataOutputStream;",
        "status",
        "",
        "payload",
        "",
        "encodeStat",
        "directory",
        "size",
        "",
        "modifiedAtMs",
        "encodeEntries",
        "entries",
        "",
        "Lcom/bachatas4/android/data/GameContentEntry;",
        "Companion",
        "app",
        "Landroidx/compose/runtime/internal/StabilityInferred;",
        "parameters"
    }
    k = 0x1
    mv = {
        0x2,
        0x4,
        0x0
    }
    xi = 0x30
.end annotation


# static fields
.field public static final $stable:I

.field private static final CLIENT_READ_TIMEOUT_MS:I = 0x7530

.field public static final Companion:Lcom/bachatas4/android/service/SafBrokerSession$Companion;

.field public static final MAGIC:I = 0x42534631

.field private static final MAX_ACTIVE_CLIENTS:I = 0x10

.field private static final MAX_CLIENT_WORKERS:I = 0x4

.field private static final MAX_NAME:I = 0x1000

.field private static final MAX_PATH:I = 0x1000

.field private static final MAX_TOKEN:I = 0x80

.field public static final OP_CLOSE:I = 0x4

.field public static final OP_LIST:I = 0x2

.field public static final OP_OPEN:I = 0x3

.field public static final OP_STAT:I = 0x1

.field private static final RESPONSE_HEADER_SIZE:I = 0xa

.field public static final STATUS_AUTH:I = 0x4

.field public static final STATUS_DENIED:I = 0x3

.field public static final STATUS_INVALID:I = 0x2

.field public static final STATUS_NOT_FOUND:I = 0x1

.field public static final STATUS_OK:I = 0x0

.field public static final VERSION:I = 0x1


# instance fields
.field private final acceptor:Ljava/util/concurrent/ExecutorService;

.field private final activeSockets:Ljava/util/concurrent/ConcurrentHashMap$KeySetView;
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "Ljava/util/concurrent/ConcurrentHashMap$KeySetView<",
            "Landroid/net/LocalSocket;",
            "Ljava/lang/Boolean;",
            ">;"
        }
    .end annotation
.end field

.field private final closed:Ljava/util/concurrent/atomic/AtomicBoolean;

.field private final server:Landroid/net/LocalServerSocket;

.field private final socketName:Ljava/lang/String;

.field private final token:Ljava/lang/String;

.field private final tree:Lcom/bachatas4/android/data/AndroidGameDocumentTree;

.field private final workers:Ljava/util/concurrent/ExecutorService;


# direct methods
.method static constructor <clinit>()V
    .locals 2

    new-instance v0, Lcom/bachatas4/android/service/SafBrokerSession$Companion;

    const/4 v1, 0x0

    invoke-direct {v0, v1}, Lcom/bachatas4/android/service/SafBrokerSession$Companion;-><init>(Lkotlin/jvm/internal/DefaultConstructorMarker;)V

    sput-object v0, Lcom/bachatas4/android/service/SafBrokerSession;->Companion:Lcom/bachatas4/android/service/SafBrokerSession$Companion;

    const/16 v0, 0x8

    sput v0, Lcom/bachatas4/android/service/SafBrokerSession;->$stable:I

    return-void
.end method

.method public constructor <init>(Landroid/net/LocalServerSocket;Ljava/lang/String;Ljava/lang/String;Lcom/bachatas4/android/data/AndroidGameDocumentTree;)V
    .locals 1

    const-string v0, "server"

    invoke-static {p1, v0}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullParameter(Ljava/lang/Object;Ljava/lang/String;)V

    const-string v0, "socketName"

    invoke-static {p2, v0}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullParameter(Ljava/lang/Object;Ljava/lang/String;)V

    const-string v0, "token"

    invoke-static {p3, v0}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullParameter(Ljava/lang/Object;Ljava/lang/String;)V

    const-string v0, "tree"

    invoke-static {p4, v0}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullParameter(Ljava/lang/Object;Ljava/lang/String;)V

    .line 36
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    .line 37
    iput-object p1, p0, Lcom/bachatas4/android/service/SafBrokerSession;->server:Landroid/net/LocalServerSocket;

    .line 38
    iput-object p2, p0, Lcom/bachatas4/android/service/SafBrokerSession;->socketName:Ljava/lang/String;

    .line 39
    iput-object p3, p0, Lcom/bachatas4/android/service/SafBrokerSession;->token:Ljava/lang/String;

    .line 40
    iput-object p4, p0, Lcom/bachatas4/android/service/SafBrokerSession;->tree:Lcom/bachatas4/android/data/AndroidGameDocumentTree;

    .line 42
    new-instance p1, Ljava/util/concurrent/atomic/AtomicBoolean;

    const/4 p2, 0x0

    invoke-direct {p1, p2}, Ljava/util/concurrent/atomic/AtomicBoolean;-><init>(Z)V

    iput-object p1, p0, Lcom/bachatas4/android/service/SafBrokerSession;->closed:Ljava/util/concurrent/atomic/AtomicBoolean;

    .line 43
    new-instance p1, Lcom/bachatas4/android/service/SafBrokerSession$$ExternalSyntheticLambda0;

    invoke-direct {p1}, Lcom/bachatas4/android/service/SafBrokerSession$$ExternalSyntheticLambda0;-><init>()V

    invoke-static {p1}, Ljava/util/concurrent/Executors;->newSingleThreadExecutor(Ljava/util/concurrent/ThreadFactory;)Ljava/util/concurrent/ExecutorService;

    move-result-object p1

    iput-object p1, p0, Lcom/bachatas4/android/service/SafBrokerSession;->acceptor:Ljava/util/concurrent/ExecutorService;

    .line 46
    new-instance p2, Lcom/bachatas4/android/service/SafBrokerSession$$ExternalSyntheticLambda1;

    invoke-direct {p2}, Lcom/bachatas4/android/service/SafBrokerSession$$ExternalSyntheticLambda1;-><init>()V

    const/4 p3, 0x4

    invoke-static {p3, p2}, Ljava/util/concurrent/Executors;->newFixedThreadPool(ILjava/util/concurrent/ThreadFactory;)Ljava/util/concurrent/ExecutorService;

    move-result-object p2

    iput-object p2, p0, Lcom/bachatas4/android/service/SafBrokerSession;->workers:Ljava/util/concurrent/ExecutorService;

    .line 49
    invoke-static {}, Ljava/util/concurrent/ConcurrentHashMap;->newKeySet()Ljava/util/concurrent/ConcurrentHashMap$KeySetView;

    move-result-object p2

    iput-object p2, p0, Lcom/bachatas4/android/service/SafBrokerSession;->activeSockets:Ljava/util/concurrent/ConcurrentHashMap$KeySetView;

    .line 52
    new-instance p2, Lcom/bachatas4/android/service/SafBrokerSession$$ExternalSyntheticLambda2;

    invoke-direct {p2, p0}, Lcom/bachatas4/android/service/SafBrokerSession$$ExternalSyntheticLambda2;-><init>(Lcom/bachatas4/android/service/SafBrokerSession;)V

    invoke-interface {p1, p2}, Ljava/util/concurrent/ExecutorService;->execute(Ljava/lang/Runnable;)V

    return-void
.end method

.method static final _init_$lambda$0(Lcom/bachatas4/android/service/SafBrokerSession;)V
    .locals 3

    .line 53
    :goto_0
    iget-object v0, p0, Lcom/bachatas4/android/service/SafBrokerSession;->closed:Ljava/util/concurrent/atomic/AtomicBoolean;

    invoke-virtual {v0}, Ljava/util/concurrent/atomic/AtomicBoolean;->get()Z

    move-result v0

    if-nez v0, :cond_2

    .line 55
    :try_start_0
    iget-object v0, p0, Lcom/bachatas4/android/service/SafBrokerSession;->server:Landroid/net/LocalServerSocket;

    invoke-virtual {v0}, Landroid/net/LocalServerSocket;->accept()Landroid/net/LocalSocket;

    move-result-object v0
    :try_end_0
    .catch Ljava/io/IOException; {:try_start_0 .. :try_end_0} :catch_2

    .line 59
    iget-object v1, p0, Lcom/bachatas4/android/service/SafBrokerSession;->closed:Ljava/util/concurrent/atomic/AtomicBoolean;

    invoke-virtual {v1}, Ljava/util/concurrent/atomic/AtomicBoolean;->get()Z

    move-result v1

    if-nez v1, :cond_1

    iget-object v1, p0, Lcom/bachatas4/android/service/SafBrokerSession;->activeSockets:Ljava/util/concurrent/ConcurrentHashMap$KeySetView;

    invoke-virtual {v1}, Ljava/util/concurrent/ConcurrentHashMap$KeySetView;->size()I

    move-result v1

    const/16 v2, 0x10

    if-lt v1, v2, :cond_0

    goto :goto_1

    :cond_0
    const/16 v1, 0x7530

    .line 64
    :try_start_1
    invoke-virtual {v0, v1}, Landroid/net/LocalSocket;->setSoTimeout(I)V
    :try_end_1
    .catch Ljava/io/IOException; {:try_start_1 .. :try_end_1} :catch_1

    .line 69
    iget-object v1, p0, Lcom/bachatas4/android/service/SafBrokerSession;->activeSockets:Ljava/util/concurrent/ConcurrentHashMap$KeySetView;

    invoke-virtual {v1, v0}, Ljava/util/concurrent/ConcurrentHashMap$KeySetView;->add(Ljava/lang/Object;)Z

    .line 71
    :try_start_2
    iget-object v1, p0, Lcom/bachatas4/android/service/SafBrokerSession;->workers:Ljava/util/concurrent/ExecutorService;

    new-instance v2, Lcom/bachatas4/android/service/SafBrokerSession$$ExternalSyntheticLambda3;

    invoke-direct {v2, p0, v0}, Lcom/bachatas4/android/service/SafBrokerSession$$ExternalSyntheticLambda3;-><init>(Lcom/bachatas4/android/service/SafBrokerSession;Landroid/net/LocalSocket;)V

    invoke-interface {v1, v2}, Ljava/util/concurrent/ExecutorService;->execute(Ljava/lang/Runnable;)V
    :try_end_2
    .catch Ljava/util/concurrent/RejectedExecutionException; {:try_start_2 .. :try_end_2} :catch_0

    goto :goto_0

    .line 79
    :catch_0
    iget-object v1, p0, Lcom/bachatas4/android/service/SafBrokerSession;->activeSockets:Ljava/util/concurrent/ConcurrentHashMap$KeySetView;

    invoke-virtual {v1, v0}, Ljava/util/concurrent/ConcurrentHashMap$KeySetView;->remove(Ljava/lang/Object;)Z

    .line 80
    :try_start_3
    sget-object v1, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    invoke-virtual {v0}, Landroid/net/LocalSocket;->close()V

    sget-object v0, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;

    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;
    :try_end_3
    .catchall {:try_start_3 .. :try_end_3} :catchall_0

    goto :goto_0

    :catchall_0
    move-exception v0

    sget-object v1, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    invoke-static {v0}, Lkotlin/ResultKt;->createFailure(Ljava/lang/Throwable;)Ljava/lang/Object;

    move-result-object v0

    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;

    goto :goto_0

    .line 66
    :catch_1
    :try_start_4
    sget-object v1, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    invoke-virtual {v0}, Landroid/net/LocalSocket;->close()V

    sget-object v0, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;

    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;
    :try_end_4
    .catchall {:try_start_4 .. :try_end_4} :catchall_1

    goto :goto_0

    :catchall_1
    move-exception v0

    sget-object v1, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    invoke-static {v0}, Lkotlin/ResultKt;->createFailure(Ljava/lang/Throwable;)Ljava/lang/Object;

    move-result-object v0

    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;

    goto :goto_0

    .line 60
    :cond_1
    :goto_1
    :try_start_5
    sget-object v1, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    invoke-virtual {v0}, Landroid/net/LocalSocket;->close()V

    sget-object v0, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;

    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;
    :try_end_5
    .catchall {:try_start_5 .. :try_end_5} :catchall_2

    goto :goto_0

    :catchall_2
    move-exception v0

    sget-object v1, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    invoke-static {v0}, Lkotlin/ResultKt;->createFailure(Ljava/lang/Throwable;)Ljava/lang/Object;

    move-result-object v0

    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;

    goto :goto_0

    :catch_2
    :cond_2
    return-void
.end method

.method static final acceptor$lambda$0(Ljava/lang/Runnable;)Ljava/lang/Thread;
    .locals 2

    .line 44
    new-instance v0, Ljava/lang/Thread;

    const-string v1, "BachataSafBroker"

    invoke-direct {v0, p0, v1}, Ljava/lang/Thread;-><init>(Ljava/lang/Runnable;Ljava/lang/String;)V

    const/4 p0, 0x1

    invoke-virtual {v0, p0}, Ljava/lang/Thread;->setDaemon(Z)V

    return-object v0
.end method

.method private final encodeEntries(Ljava/util/List;)[B
    .locals 6
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "(",
            "Ljava/util/List<",
            "Lcom/bachatas4/android/data/GameContentEntry;",
            ">;)[B"
        }
    .end annotation

    .line 188
    new-instance p0, Ljava/io/ByteArrayOutputStream;

    invoke-direct {p0}, Ljava/io/ByteArrayOutputStream;-><init>()V

    .line 189
    new-instance v0, Ljava/io/DataOutputStream;

    move-object v1, p0

    check-cast v1, Ljava/io/OutputStream;

    invoke-direct {v0, v1}, Ljava/io/DataOutputStream;-><init>(Ljava/io/OutputStream;)V

    check-cast v0, Ljava/io/Closeable;

    :try_start_0
    move-object v1, v0

    check-cast v1, Ljava/io/DataOutputStream;

    .line 190
    invoke-interface {p1}, Ljava/util/List;->size()I

    move-result v2

    invoke-virtual {v1, v2}, Ljava/io/DataOutputStream;->writeInt(I)V

    .line 191
    check-cast p1, Ljava/lang/Iterable;

    .line 228
    invoke-interface {p1}, Ljava/lang/Iterable;->iterator()Ljava/util/Iterator;

    move-result-object p1

    :goto_0
    invoke-interface {p1}, Ljava/util/Iterator;->hasNext()Z

    move-result v2

    if-eqz v2, :cond_1

    invoke-interface {p1}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v2

    check-cast v2, Lcom/bachatas4/android/data/GameContentEntry;

    .line 192
    invoke-virtual {v2}, Lcom/bachatas4/android/data/GameContentEntry;->getName()Ljava/lang/String;

    move-result-object v3

    sget-object v4, Lkotlin/text/Charsets;->UTF_8:Ljava/nio/charset/Charset;

    invoke-virtual {v3, v4}, Ljava/lang/String;->getBytes(Ljava/nio/charset/Charset;)[B

    move-result-object v3

    const-string v4, "getBytes(...)"

    invoke-static {v3, v4}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullExpressionValue(Ljava/lang/Object;Ljava/lang/String;)V

    .line 193
    array-length v4, v3

    const/16 v5, 0x1000

    if-gt v4, v5, :cond_0

    .line 194
    array-length v4, v3

    invoke-virtual {v1, v4}, Ljava/io/DataOutputStream;->writeShort(I)V

    .line 195
    invoke-virtual {v1, v3}, Ljava/io/DataOutputStream;->write([B)V

    .line 196
    invoke-virtual {v2}, Lcom/bachatas4/android/data/GameContentEntry;->getStat()Lcom/bachatas4/android/data/GameContentStat;

    move-result-object v3

    invoke-virtual {v3}, Lcom/bachatas4/android/data/GameContentStat;->isDirectory()Z

    move-result v3

    invoke-virtual {v1, v3}, Ljava/io/DataOutputStream;->writeBoolean(Z)V

    .line 197
    invoke-virtual {v2}, Lcom/bachatas4/android/data/GameContentEntry;->getStat()Lcom/bachatas4/android/data/GameContentStat;

    move-result-object v3

    invoke-virtual {v3}, Lcom/bachatas4/android/data/GameContentStat;->getSize()J

    move-result-wide v3

    invoke-virtual {v1, v3, v4}, Ljava/io/DataOutputStream;->writeLong(J)V

    .line 198
    invoke-virtual {v2}, Lcom/bachatas4/android/data/GameContentEntry;->getStat()Lcom/bachatas4/android/data/GameContentStat;

    move-result-object v2

    invoke-virtual {v2}, Lcom/bachatas4/android/data/GameContentStat;->getModifiedAtMs()J

    move-result-wide v2

    invoke-virtual {v1, v2, v3}, Ljava/io/DataOutputStream;->writeLong(J)V

    goto :goto_0

    .line 193
    :cond_0
    const-string p0, "Failed requirement."

    new-instance p1, Ljava/lang/IllegalArgumentException;

    invoke-virtual {p0}, Ljava/lang/Object;->toString()Ljava/lang/String;

    move-result-object p0

    invoke-direct {p1, p0}, Ljava/lang/IllegalArgumentException;-><init>(Ljava/lang/String;)V

    throw p1

    .line 200
    :cond_1
    sget-object p1, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;
    :try_end_0
    .catchall {:try_start_0 .. :try_end_0} :catchall_0

    const/4 p1, 0x0

    .line 189
    invoke-static {v0, p1}, Lkotlin/io/CloseableKt;->closeFinally(Ljava/io/Closeable;Ljava/lang/Throwable;)V

    .line 201
    invoke-virtual {p0}, Ljava/io/ByteArrayOutputStream;->toByteArray()[B

    move-result-object p0

    const-string p1, "toByteArray(...)"

    invoke-static {p0, p1}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullExpressionValue(Ljava/lang/Object;Ljava/lang/String;)V

    return-object p0

    :catchall_0
    move-exception p0

    .line 189
    :try_start_1
    throw p0
    :try_end_1
    .catchall {:try_start_1 .. :try_end_1} :catchall_1

    :catchall_1
    move-exception p1

    invoke-static {v0, p0}, Lkotlin/io/CloseableKt;->closeFinally(Ljava/io/Closeable;Ljava/lang/Throwable;)V

    throw p1
.end method

.method private final encodeStat(ZJJ)[B
    .locals 2

    .line 179
    new-instance p0, Ljava/io/ByteArrayOutputStream;

    invoke-direct {p0}, Ljava/io/ByteArrayOutputStream;-><init>()V

    .line 180
    new-instance v0, Ljava/io/DataOutputStream;

    move-object v1, p0

    check-cast v1, Ljava/io/OutputStream;

    invoke-direct {v0, v1}, Ljava/io/DataOutputStream;-><init>(Ljava/io/OutputStream;)V

    check-cast v0, Ljava/io/Closeable;

    :try_start_0
    move-object v1, v0

    check-cast v1, Ljava/io/DataOutputStream;

    .line 181
    invoke-virtual {v1, p1}, Ljava/io/DataOutputStream;->writeBoolean(Z)V

    .line 182
    invoke-virtual {v1, p2, p3}, Ljava/io/DataOutputStream;->writeLong(J)V

    .line 183
    invoke-virtual {v1, p4, p5}, Ljava/io/DataOutputStream;->writeLong(J)V

    .line 184
    sget-object p1, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;
    :try_end_0
    .catchall {:try_start_0 .. :try_end_0} :catchall_0

    const/4 p1, 0x0

    .line 180
    invoke-static {v0, p1}, Lkotlin/io/CloseableKt;->closeFinally(Ljava/io/Closeable;Ljava/lang/Throwable;)V

    .line 185
    invoke-virtual {p0}, Ljava/io/ByteArrayOutputStream;->toByteArray()[B

    move-result-object p0

    const-string p1, "toByteArray(...)"

    invoke-static {p0, p1}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullExpressionValue(Ljava/lang/Object;Ljava/lang/String;)V

    return-object p0

    :catchall_0
    move-exception p0

    .line 180
    :try_start_1
    throw p0
    :try_end_1
    .catchall {:try_start_1 .. :try_end_1} :catchall_1

    :catchall_1
    move-exception p1

    invoke-static {v0, p0}, Lkotlin/io/CloseableKt;->closeFinally(Ljava/io/Closeable;Ljava/lang/Throwable;)V

    throw p1
.end method

.method static final lambda$0$2(Lcom/bachatas4/android/service/SafBrokerSession;Landroid/net/LocalSocket;)V
    .locals 3

    .line 73
    :try_start_0
    sget-object v0, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    move-object v0, p1

    check-cast v0, Ljava/io/Closeable;
    :try_end_0
    .catchall {:try_start_0 .. :try_end_0} :catchall_2

    :try_start_1
    move-object v1, v0

    check-cast v1, Landroid/net/LocalSocket;

    invoke-direct {p0, v1}, Lcom/bachatas4/android/service/SafBrokerSession;->serve(Landroid/net/LocalSocket;)V

    sget-object v1, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;
    :try_end_1
    .catchall {:try_start_1 .. :try_end_1} :catchall_0

    const/4 v1, 0x0

    :try_start_2
    invoke-static {v0, v1}, Lkotlin/io/CloseableKt;->closeFinally(Ljava/io/Closeable;Ljava/lang/Throwable;)V

    sget-object v0, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;

    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;
    :try_end_2
    .catchall {:try_start_2 .. :try_end_2} :catchall_2

    goto :goto_0

    :catchall_0
    move-exception v1

    :try_start_3
    throw v1
    :try_end_3
    .catchall {:try_start_3 .. :try_end_3} :catchall_1

    :catchall_1
    move-exception v2

    :try_start_4
    invoke-static {v0, v1}, Lkotlin/io/CloseableKt;->closeFinally(Ljava/io/Closeable;Ljava/lang/Throwable;)V

    throw v2
    :try_end_4
    .catchall {:try_start_4 .. :try_end_4} :catchall_2

    :catchall_2
    move-exception v0

    :try_start_5
    sget-object v1, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    invoke-static {v0}, Lkotlin/ResultKt;->createFailure(Ljava/lang/Throwable;)Ljava/lang/Object;

    move-result-object v0

    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;
    :try_end_5
    .catchall {:try_start_5 .. :try_end_5} :catchall_3

    .line 75
    :goto_0
    iget-object p0, p0, Lcom/bachatas4/android/service/SafBrokerSession;->activeSockets:Ljava/util/concurrent/ConcurrentHashMap$KeySetView;

    invoke-virtual {p0, p1}, Ljava/util/concurrent/ConcurrentHashMap$KeySetView;->remove(Ljava/lang/Object;)Z

    return-void

    :catchall_3
    move-exception v0

    iget-object p0, p0, Lcom/bachatas4/android/service/SafBrokerSession;->activeSockets:Ljava/util/concurrent/ConcurrentHashMap$KeySetView;

    invoke-virtual {p0, p1}, Ljava/util/concurrent/ConcurrentHashMap$KeySetView;->remove(Ljava/lang/Object;)Z

    throw v0
.end method

.method private final respond(Ljava/io/DataOutputStream;I[B)V
    .locals 4

    .line 163
    new-instance p0, Ljava/io/ByteArrayOutputStream;

    const/4 v0, 0x0

    if-eqz p3, :cond_0

    array-length v1, p3

    goto :goto_0

    :cond_0
    move v1, v0

    :goto_0
    add-int/lit8 v1, v1, 0xa

    invoke-direct {p0, v1}, Ljava/io/ByteArrayOutputStream;-><init>(I)V

    .line 164
    new-instance v1, Ljava/io/DataOutputStream;

    move-object v2, p0

    check-cast v2, Ljava/io/OutputStream;

    invoke-direct {v1, v2}, Ljava/io/DataOutputStream;-><init>(Ljava/io/OutputStream;)V

    check-cast v1, Ljava/io/Closeable;

    :try_start_0
    move-object v2, v1

    check-cast v2, Ljava/io/DataOutputStream;

    const v3, 0x42534631

    .line 165
    invoke-virtual {v2, v3}, Ljava/io/DataOutputStream;->writeInt(I)V

    const/4 v3, 0x1

    .line 166
    invoke-virtual {v2, v3}, Ljava/io/DataOutputStream;->writeByte(I)V

    .line 167
    invoke-virtual {v2, p2}, Ljava/io/DataOutputStream;->writeByte(I)V

    if-eqz p3, :cond_1

    .line 168
    array-length v0, p3

    :cond_1
    invoke-virtual {v2, v0}, Ljava/io/DataOutputStream;->writeInt(I)V

    if-eqz p3, :cond_2

    .line 169
    invoke-virtual {v2, p3}, Ljava/io/DataOutputStream;->write([B)V

    .line 170
    :cond_2
    sget-object p2, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;
    :try_end_0
    .catchall {:try_start_0 .. :try_end_0} :catchall_0

    const/4 p2, 0x0

    .line 164
    invoke-static {v1, p2}, Lkotlin/io/CloseableKt;->closeFinally(Ljava/io/Closeable;Ljava/lang/Throwable;)V

    .line 171
    invoke-virtual {p0}, Ljava/io/ByteArrayOutputStream;->toByteArray()[B

    move-result-object p0

    .line 174
    invoke-virtual {p1, p0}, Ljava/io/DataOutputStream;->write([B)V

    .line 175
    invoke-virtual {p1}, Ljava/io/DataOutputStream;->flush()V

    return-void

    :catchall_0
    move-exception p0

    .line 164
    :try_start_1
    throw p0
    :try_end_1
    .catchall {:try_start_1 .. :try_end_1} :catchall_1

    :catchall_1
    move-exception p1

    invoke-static {v1, p0}, Lkotlin/io/CloseableKt;->closeFinally(Ljava/io/Closeable;Ljava/lang/Throwable;)V

    throw p1
.end method

.method private final serve(Landroid/net/LocalSocket;)V
    .locals 13

    .line 87
    new-instance v7, Ljava/io/DataInputStream;

    invoke-virtual {p1}, Landroid/net/LocalSocket;->getInputStream()Ljava/io/InputStream;

    move-result-object v2

    invoke-direct {v7, v2}, Ljava/io/DataInputStream;-><init>(Ljava/io/InputStream;)V

    .line 88
    new-instance v8, Ljava/io/DataOutputStream;

    invoke-virtual {p1}, Landroid/net/LocalSocket;->getOutputStream()Ljava/io/OutputStream;

    move-result-object v2

    invoke-direct {v8, v2}, Ljava/io/DataOutputStream;-><init>(Ljava/io/OutputStream;)V

    .line 89
    :goto_0
    iget-object v2, p0, Lcom/bachatas4/android/service/SafBrokerSession;->closed:Ljava/util/concurrent/atomic/AtomicBoolean;

    invoke-virtual {v2}, Ljava/util/concurrent/atomic/AtomicBoolean;->get()Z

    move-result v2

    if-nez v2, :cond_b

    const/4 v9, 0x3

    const/4 v10, 0x2

    const/4 v11, 0x0

    .line 91
    :try_start_0
    invoke-virtual {v7}, Ljava/io/DataInputStream;->readInt()I

    move-result v2

    const v3, 0x42534631

    if-ne v2, v3, :cond_b

    invoke-virtual {v7}, Ljava/io/DataInputStream;->readUnsignedByte()I

    move-result v2

    const/4 v3, 0x1

    if-eq v2, v3, :cond_0

    goto/16 :goto_4

    .line 92
    :cond_0
    invoke-virtual {v7}, Ljava/io/DataInputStream;->readUnsignedByte()I

    move-result v2

    .line 93
    invoke-virtual {v7}, Ljava/io/DataInputStream;->readUnsignedShort()I

    move-result v4

    .line 94
    invoke-virtual {v7}, Ljava/io/DataInputStream;->readInt()I

    move-result v5

    if-gt v3, v4, :cond_9

    const/16 v6, 0x81

    if-ge v4, v6, :cond_9

    if-ltz v5, :cond_9

    const/16 v6, 0x1001

    if-ge v5, v6, :cond_9

    .line 96
    new-array v4, v4, [B

    invoke-virtual {v7, v4}, Ljava/io/DataInputStream;->readFully([B)V

    .line 97
    new-array v5, v5, [B

    invoke-virtual {v7, v5}, Ljava/io/DataInputStream;->readFully([B)V

    .line 98
    iget-object v6, p0, Lcom/bachatas4/android/service/SafBrokerSession;->token:Ljava/lang/String;

    sget-object v12, Lkotlin/text/Charsets;->UTF_8:Ljava/nio/charset/Charset;

    invoke-virtual {v6, v12}, Ljava/lang/String;->getBytes(Ljava/nio/charset/Charset;)[B

    move-result-object v6

    const-string v12, "getBytes(...)"

    invoke-static {v6, v12}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullExpressionValue(Ljava/lang/Object;Ljava/lang/String;)V

    invoke-static {v6, v4}, Ljava/security/MessageDigest;->isEqual([B[B)Z

    move-result v4

    if-nez v4, :cond_1

    const/4 v0, 0x4

    .line 99
    invoke-direct {p0, v8, v0, v11}, Lcom/bachatas4/android/service/SafBrokerSession;->respond(Ljava/io/DataOutputStream;I[B)V

    return-void

    .line 100
    :cond_1
    new-instance v4, Ljava/lang/String;

    .line 102
    sget-object v6, Lkotlin/text/Charsets;->UTF_8:Ljava/nio/charset/Charset;

    invoke-direct {v4, v5, v6}, Ljava/lang/String;-><init>([BLjava/nio/charset/Charset;)V
    :try_end_0
    .catch Ljava/io/EOFException; {:try_start_0 .. :try_end_0} :catch_4
    .catch Lcom/bachatas4/android/data/GamePathResolutionException; {:try_start_0 .. :try_end_0} :catch_3
    .catch Ljava/lang/SecurityException; {:try_start_0 .. :try_end_0} :catch_2
    .catch Ljava/io/IOException; {:try_start_0 .. :try_end_0} :catch_4
    .catch Ljava/lang/Exception; {:try_start_0 .. :try_end_0} :catch_1

    const/4 v12, 0x0

    if-eq v2, v10, :cond_3

    if-ne v2, v3, :cond_2

    goto :goto_1

    :cond_2
    move v5, v12

    goto :goto_2

    :cond_3
    :goto_1
    move v5, v3

    .line 104
    :goto_2
    :try_start_1
    invoke-static {v4, v5}, Lcom/bachatas4/android/data/GameContentAccessKt;->normalizeGameContentPath(Ljava/lang/String;Z)Ljava/lang/String;

    move-result-object v4
    :try_end_1
    .catch Lcom/bachatas4/android/data/GamePathResolutionException; {:try_start_1 .. :try_end_1} :catch_0
    .catch Ljava/io/EOFException; {:try_start_1 .. :try_end_1} :catch_4
    .catch Ljava/lang/SecurityException; {:try_start_1 .. :try_end_1} :catch_2
    .catch Ljava/io/IOException; {:try_start_1 .. :try_end_1} :catch_4
    .catch Ljava/lang/Exception; {:try_start_1 .. :try_end_1} :catch_1

    if-eq v2, v3, :cond_7

    if-eq v2, v10, :cond_6

    if-eq v2, v9, :cond_4

    goto/16 :goto_4

    .line 117
    :cond_4
    :try_start_2
    iget-object v2, p0, Lcom/bachatas4/android/service/SafBrokerSession;->tree:Lcom/bachatas4/android/data/AndroidGameDocumentTree;

    invoke-virtual {v2, v4}, Lcom/bachatas4/android/data/AndroidGameDocumentTree;->openDescriptor(Ljava/lang/String;)Landroid/os/ParcelFileDescriptor;

    move-result-object v2

    if-nez v2, :cond_5

    .line 119
    invoke-direct {p0, v8, v3, v11}, Lcom/bachatas4/android/service/SafBrokerSession;->respond(Ljava/io/DataOutputStream;I[B)V

    goto :goto_0

    .line 121
    :cond_5
    check-cast v2, Ljava/io/Closeable;
    :try_end_2
    .catch Ljava/io/EOFException; {:try_start_2 .. :try_end_2} :catch_4
    .catch Lcom/bachatas4/android/data/GamePathResolutionException; {:try_start_2 .. :try_end_2} :catch_3
    .catch Ljava/lang/SecurityException; {:try_start_2 .. :try_end_2} :catch_2
    .catch Ljava/io/IOException; {:try_start_2 .. :try_end_2} :catch_4
    .catch Ljava/lang/Exception; {:try_start_2 .. :try_end_2} :catch_1

    :try_start_3
    move-object v4, v2

    check-cast v4, Landroid/os/ParcelFileDescriptor;

    .line 122
    new-array v3, v3, [Ljava/io/FileDescriptor;

    invoke-virtual {v4}, Landroid/os/ParcelFileDescriptor;->getFileDescriptor()Ljava/io/FileDescriptor;

    move-result-object v4

    aput-object v4, v3, v12

    invoke-virtual {p1, v3}, Landroid/net/LocalSocket;->setFileDescriptorsForSend([Ljava/io/FileDescriptor;)V

    .line 123
    invoke-direct {p0, v8, v12, v11}, Lcom/bachatas4/android/service/SafBrokerSession;->respond(Ljava/io/DataOutputStream;I[B)V

    .line 124
    invoke-virtual {p1, v11}, Landroid/net/LocalSocket;->setFileDescriptorsForSend([Ljava/io/FileDescriptor;)V

    .line 125
    sget-object v3, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;
    :try_end_3
    .catchall {:try_start_3 .. :try_end_3} :catchall_0

    .line 121
    :try_start_4
    invoke-static {v2, v11}, Lkotlin/io/CloseableKt;->closeFinally(Ljava/io/Closeable;Ljava/lang/Throwable;)V
    :try_end_4
    .catch Ljava/io/EOFException; {:try_start_4 .. :try_end_4} :catch_4
    .catch Lcom/bachatas4/android/data/GamePathResolutionException; {:try_start_4 .. :try_end_4} :catch_3
    .catch Ljava/lang/SecurityException; {:try_start_4 .. :try_end_4} :catch_2
    .catch Ljava/io/IOException; {:try_start_4 .. :try_end_4} :catch_4
    .catch Ljava/lang/Exception; {:try_start_4 .. :try_end_4} :catch_1

    goto/16 :goto_0

    :catchall_0
    move-exception v0

    move-object v3, v0

    :try_start_5
    throw v3
    :try_end_5
    .catchall {:try_start_5 .. :try_end_5} :catchall_1

    :catchall_1
    move-exception v0

    :try_start_6
    invoke-static {v2, v3}, Lkotlin/io/CloseableKt;->closeFinally(Ljava/io/Closeable;Ljava/lang/Throwable;)V

    throw v0

    .line 115
    :cond_6
    iget-object v2, p0, Lcom/bachatas4/android/service/SafBrokerSession;->tree:Lcom/bachatas4/android/data/AndroidGameDocumentTree;

    invoke-virtual {v2, v4}, Lcom/bachatas4/android/data/AndroidGameDocumentTree;->list(Ljava/lang/String;)Ljava/util/List;

    move-result-object v2

    invoke-direct {p0, v2}, Lcom/bachatas4/android/service/SafBrokerSession;->encodeEntries(Ljava/util/List;)[B

    move-result-object v2

    invoke-direct {p0, v8, v12, v2}, Lcom/bachatas4/android/service/SafBrokerSession;->respond(Ljava/io/DataOutputStream;I[B)V

    goto/16 :goto_0

    .line 111
    :cond_7
    iget-object v2, p0, Lcom/bachatas4/android/service/SafBrokerSession;->tree:Lcom/bachatas4/android/data/AndroidGameDocumentTree;

    invoke-virtual {v2, v4}, Lcom/bachatas4/android/data/AndroidGameDocumentTree;->stat(Ljava/lang/String;)Lcom/bachatas4/android/data/GameContentStat;

    move-result-object v2

    if-nez v2, :cond_8

    .line 112
    invoke-direct {p0, v8, v3, v11}, Lcom/bachatas4/android/service/SafBrokerSession;->respond(Ljava/io/DataOutputStream;I[B)V

    goto/16 :goto_0

    :cond_8
    move-object v3, v2

    .line 113
    invoke-virtual {v3}, Lcom/bachatas4/android/data/GameContentStat;->isDirectory()Z

    move-result v2

    move-object v5, v3

    invoke-virtual {v5}, Lcom/bachatas4/android/data/GameContentStat;->getSize()J

    move-result-wide v3

    invoke-virtual {v5}, Lcom/bachatas4/android/data/GameContentStat;->getModifiedAtMs()J

    move-result-wide v5

    move-object v1, p0

    invoke-direct/range {v1 .. v6}, Lcom/bachatas4/android/service/SafBrokerSession;->encodeStat(ZJJ)[B

    move-result-object v2

    invoke-direct {p0, v8, v12, v2}, Lcom/bachatas4/android/service/SafBrokerSession;->respond(Ljava/io/DataOutputStream;I[B)V

    goto/16 :goto_0

    .line 106
    :catch_0
    invoke-direct {p0, v8, v10, v11}, Lcom/bachatas4/android/service/SafBrokerSession;->respond(Ljava/io/DataOutputStream;I[B)V
    :try_end_6
    .catch Ljava/io/EOFException; {:try_start_6 .. :try_end_6} :catch_4
    .catch Lcom/bachatas4/android/data/GamePathResolutionException; {:try_start_6 .. :try_end_6} :catch_3
    .catch Ljava/lang/SecurityException; {:try_start_6 .. :try_end_6} :catch_2
    .catch Ljava/io/IOException; {:try_start_6 .. :try_end_6} :catch_4
    .catch Ljava/lang/Exception; {:try_start_6 .. :try_end_6} :catch_1

    goto :goto_4

    :cond_9
    return-void

    .line 147
    :catch_1
    :try_start_7
    sget-object v0, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    invoke-direct {p0, v8, v10, v11}, Lcom/bachatas4/android/service/SafBrokerSession;->respond(Ljava/io/DataOutputStream;I[B)V

    sget-object v0, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;

    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;
    :try_end_7
    .catchall {:try_start_7 .. :try_end_7} :catchall_2

    goto :goto_4

    :catchall_2
    move-exception v0

    sget-object v1, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    invoke-static {v0}, Lkotlin/ResultKt;->createFailure(Ljava/lang/Throwable;)Ljava/lang/Object;

    move-result-object v0

    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;

    goto :goto_4

    .line 142
    :catch_2
    :try_start_8
    sget-object v0, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    invoke-direct {p0, v8, v9, v11}, Lcom/bachatas4/android/service/SafBrokerSession;->respond(Ljava/io/DataOutputStream;I[B)V

    sget-object v0, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;

    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;
    :try_end_8
    .catchall {:try_start_8 .. :try_end_8} :catchall_3

    goto :goto_4

    :catchall_3
    move-exception v0

    sget-object v1, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    invoke-static {v0}, Lkotlin/ResultKt;->createFailure(Ljava/lang/Throwable;)Ljava/lang/Object;

    move-result-object v0

    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;

    goto :goto_4

    :catch_3
    move-exception v0

    .line 134
    invoke-virtual {v0}, Lcom/bachatas4/android/data/GamePathResolutionException;->getCode()Lcom/bachatas4/android/model/RuntimeErrorCode;

    move-result-object v0

    sget-object v2, Lcom/bachatas4/android/model/RuntimeErrorCode;->CONTENT_PERMISSION_LOST:Lcom/bachatas4/android/model/RuntimeErrorCode;

    if-ne v0, v2, :cond_a

    goto :goto_3

    :cond_a
    move v9, v10

    .line 139
    :goto_3
    :try_start_9
    sget-object v0, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    invoke-direct {p0, v8, v9, v11}, Lcom/bachatas4/android/service/SafBrokerSession;->respond(Ljava/io/DataOutputStream;I[B)V

    sget-object v0, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;

    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;
    :try_end_9
    .catchall {:try_start_9 .. :try_end_9} :catchall_4

    goto :goto_4

    :catchall_4
    move-exception v0

    sget-object v1, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    invoke-static {v0}, Lkotlin/ResultKt;->createFailure(Ljava/lang/Throwable;)Ljava/lang/Object;

    move-result-object v0

    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;

    :catch_4
    :cond_b
    :goto_4
    return-void
.end method

.method static final workers$lambda$0(Ljava/lang/Runnable;)Ljava/lang/Thread;
    .locals 2

    .line 47
    new-instance v0, Ljava/lang/Thread;

    const-string v1, "BachataSafClient"

    invoke-direct {v0, p0, v1}, Ljava/lang/Thread;-><init>(Ljava/lang/Runnable;Ljava/lang/String;)V

    const/4 p0, 0x1

    invoke-virtual {v0, p0}, Ljava/lang/Thread;->setDaemon(Z)V

    return-object v0
.end method


# virtual methods
.method public close()V
    .locals 3

    .line 154
    iget-object v0, p0, Lcom/bachatas4/android/service/SafBrokerSession;->closed:Ljava/util/concurrent/atomic/AtomicBoolean;

    const/4 v1, 0x0

    const/4 v2, 0x1

    invoke-virtual {v0, v1, v2}, Ljava/util/concurrent/atomic/AtomicBoolean;->compareAndSet(ZZ)Z

    move-result v0

    if-nez v0, :cond_0

    return-void

    .line 155
    :cond_0
    :try_start_0
    sget-object v0, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    move-object v0, p0

    check-cast v0, Lcom/bachatas4/android/service/SafBrokerSession;

    iget-object v0, p0, Lcom/bachatas4/android/service/SafBrokerSession;->server:Landroid/net/LocalServerSocket;

    invoke-virtual {v0}, Landroid/net/LocalServerSocket;->close()V

    sget-object v0, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;

    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;
    :try_end_0
    .catchall {:try_start_0 .. :try_end_0} :catchall_0

    goto :goto_0

    :catchall_0
    move-exception v0

    sget-object v1, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    invoke-static {v0}, Lkotlin/ResultKt;->createFailure(Ljava/lang/Throwable;)Ljava/lang/Object;

    move-result-object v0

    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;

    .line 156
    :goto_0
    iget-object v0, p0, Lcom/bachatas4/android/service/SafBrokerSession;->activeSockets:Ljava/util/concurrent/ConcurrentHashMap$KeySetView;

    const-string v1, "activeSockets"

    invoke-static {v0, v1}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullExpressionValue(Ljava/lang/Object;Ljava/lang/String;)V

    check-cast v0, Ljava/lang/Iterable;

    .line 226
    invoke-interface {v0}, Ljava/lang/Iterable;->iterator()Ljava/util/Iterator;

    move-result-object v0

    :goto_1
    invoke-interface {v0}, Ljava/util/Iterator;->hasNext()Z

    move-result v1

    if-eqz v1, :cond_1

    invoke-interface {v0}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v1

    check-cast v1, Landroid/net/LocalSocket;

    .line 156
    :try_start_1
    sget-object v2, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    move-object v2, p0

    check-cast v2, Lcom/bachatas4/android/service/SafBrokerSession;

    invoke-virtual {v1}, Landroid/net/LocalSocket;->close()V

    sget-object v1, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;

    invoke-static {v1}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;
    :try_end_1
    .catchall {:try_start_1 .. :try_end_1} :catchall_1

    goto :goto_1

    :catchall_1
    move-exception v1

    sget-object v2, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    invoke-static {v1}, Lkotlin/ResultKt;->createFailure(Ljava/lang/Throwable;)Ljava/lang/Object;

    move-result-object v1

    invoke-static {v1}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;

    goto :goto_1

    .line 157
    :cond_1
    iget-object v0, p0, Lcom/bachatas4/android/service/SafBrokerSession;->activeSockets:Ljava/util/concurrent/ConcurrentHashMap$KeySetView;

    invoke-virtual {v0}, Ljava/util/concurrent/ConcurrentHashMap$KeySetView;->clear()V

    .line 158
    iget-object v0, p0, Lcom/bachatas4/android/service/SafBrokerSession;->acceptor:Ljava/util/concurrent/ExecutorService;

    invoke-interface {v0}, Ljava/util/concurrent/ExecutorService;->shutdownNow()Ljava/util/List;

    .line 159
    iget-object p0, p0, Lcom/bachatas4/android/service/SafBrokerSession;->workers:Ljava/util/concurrent/ExecutorService;

    invoke-interface {p0}, Ljava/util/concurrent/ExecutorService;->shutdownNow()Ljava/util/List;

    return-void
.end method

.method public final getSocketName()Ljava/lang/String;
    .locals 0

    .line 38
    iget-object p0, p0, Lcom/bachatas4/android/service/SafBrokerSession;->socketName:Ljava/lang/String;

    return-object p0
.end method

.method public final getToken()Ljava/lang/String;
    .locals 0

    .line 39
    iget-object p0, p0, Lcom/bachatas4/android/service/SafBrokerSession;->token:Ljava/lang/String;

    return-object p0
.end method
