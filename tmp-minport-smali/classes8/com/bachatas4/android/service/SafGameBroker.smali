.class public final Lcom/bachatas4/android/service/SafGameBroker;
.super Ljava/lang/Object;
.source "SafGameBroker.kt"


# annotations
.annotation system Ldalvik/annotation/SourceDebugExtension;
    value = "SMAP\nSafGameBroker.kt\nKotlin\n*S Kotlin\n*F\n+ 1 SafGameBroker.kt\ncom/bachatas4/android/service/SafGameBroker\n+ 2 fake.kt\nkotlin/jvm/internal/FakeKt\n*L\n1#1,224:1\n1#2:225\n*E\n"
.end annotation

.annotation runtime Lkotlin/Metadata;
    d1 = {
        "\u0000$\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0000\n\u0002\u0018\u0002\n\u0002\u0008\u0003\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\u000e\n\u0000\n\u0002\u0018\u0002\n\u0000\u0008\u0007\u0018\u00002\u00020\u0001B\u000f\u0012\u0006\u0010\u0002\u001a\u00020\u0003\u00a2\u0006\u0004\u0008\u0004\u0010\u0005J\u000e\u0010\u0006\u001a\u00020\u00072\u0006\u0010\u0008\u001a\u00020\tR\u000e\u0010\u0002\u001a\u00020\u0003X\u0082\u0004\u00a2\u0006\u0002\n\u0000\u00ca\u0001\u000c\u0008\u000b\u0012\u0008\u0008\u000c\u0012\u0004\u0008\u0003\u0010\u0000\u00a8\u0006\n"
    }
    d2 = {
        "Lcom/bachatas4/android/service/SafGameBroker;",
        "",
        "contentResolver",
        "Landroid/content/ContentResolver;",
        "<init>",
        "(Landroid/content/ContentResolver;)V",
        "start",
        "Lcom/bachatas4/android/service/SafBrokerSession;",
        "sourceUri",
        "",
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
.field public static final $stable:I = 0x8


# instance fields
.field private final contentResolver:Landroid/content/ContentResolver;


# direct methods
.method static constructor <clinit>()V
    .locals 0

    return-void
.end method

.method public constructor <init>(Landroid/content/ContentResolver;)V
    .locals 1

    const-string v0, "contentResolver"

    invoke-static {p1, v0}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullParameter(Ljava/lang/Object;Ljava/lang/String;)V

    .line 24
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    .line 25
    iput-object p1, p0, Lcom/bachatas4/android/service/SafGameBroker;->contentResolver:Landroid/content/ContentResolver;

    return-void
.end method

.method static final start$lambda$0(B)Ljava/lang/CharSequence;
    .locals 1

    .line 30
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
.method public final start(Ljava/lang/String;)Lcom/bachatas4/android/service/SafBrokerSession;
    .locals 10

    const-string v0, "sourceUri"

    invoke-static {p1, v0}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullParameter(Ljava/lang/Object;Ljava/lang/String;)V

    .line 28
    new-instance v0, Lcom/bachatas4/android/data/AndroidGameDocumentTree;

    iget-object p0, p0, Lcom/bachatas4/android/service/SafGameBroker;->contentResolver:Landroid/content/ContentResolver;

    invoke-direct {v0, p0, p1}, Lcom/bachatas4/android/data/AndroidGameDocumentTree;-><init>(Landroid/content/ContentResolver;Ljava/lang/String;)V

    const/16 p0, 0x10

    .line 29
    new-array v1, p0, [B

    new-instance p1, Ljava/security/SecureRandom;

    invoke-direct {p1}, Ljava/security/SecureRandom;-><init>()V

    invoke-virtual {p1, v1}, Ljava/security/SecureRandom;->nextBytes([B)V

    .line 30
    const-string p1, ""

    move-object v2, p1

    check-cast v2, Ljava/lang/CharSequence;

    new-instance v7, Lcom/bachatas4/android/service/SafGameBroker$$ExternalSyntheticLambda0;

    invoke-direct {v7}, Lcom/bachatas4/android/service/SafGameBroker$$ExternalSyntheticLambda0;-><init>()V

    const/16 v8, 0x1e

    const/4 v9, 0x0

    const/4 v3, 0x0

    const/4 v4, 0x0

    const/4 v5, 0x0

    const/4 v6, 0x0

    invoke-static/range {v1 .. v9}, Lkotlin/collections/ArraysKt;->joinToString$default([BLjava/lang/CharSequence;Ljava/lang/CharSequence;Ljava/lang/CharSequence;ILjava/lang/CharSequence;Lkotlin/jvm/functions/Function1;ILjava/lang/Object;)Ljava/lang/String;

    move-result-object p1

    .line 31
    invoke-static {p1, p0}, Lkotlin/text/StringsKt;->take(Ljava/lang/String;I)Ljava/lang/String;

    move-result-object p0

    new-instance v1, Ljava/lang/StringBuilder;

    const-string v2, "bachata-saf-"

    invoke-direct {v1, v2}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v1, p0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p0

    invoke-virtual {p0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p0

    .line 32
    new-instance v1, Lcom/bachatas4/android/service/SafBrokerSession;

    new-instance v2, Landroid/net/LocalServerSocket;

    invoke-direct {v2, p0}, Landroid/net/LocalServerSocket;-><init>(Ljava/lang/String;)V

    invoke-direct {v1, v2, p0, p1, v0}, Lcom/bachatas4/android/service/SafBrokerSession;-><init>(Landroid/net/LocalServerSocket;Ljava/lang/String;Ljava/lang/String;Lcom/bachatas4/android/data/AndroidGameDocumentTree;)V

    return-object v1
.end method
