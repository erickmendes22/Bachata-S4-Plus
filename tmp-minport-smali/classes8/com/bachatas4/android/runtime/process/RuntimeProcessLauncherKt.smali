.class public final Lcom/bachatas4/android/runtime/process/RuntimeProcessLauncherKt;
.super Ljava/lang/Object;
.source "RuntimeProcessLauncher.kt"


# annotations
.annotation system Ldalvik/annotation/SourceDebugExtension;
    value = "SMAP\nRuntimeProcessLauncher.kt\nKotlin\n*S Kotlin\n*F\n+ 1 RuntimeProcessLauncher.kt\ncom/bachatas4/android/runtime/process/RuntimeProcessLauncherKt\n+ 2 fake.kt\nkotlin/jvm/internal/FakeKt\n*L\n1#1,251:1\n1#2:252\n*E\n"
.end annotation

.annotation runtime Lkotlin/Metadata;
    d1 = {
        "\u0000\u0012\n\u0000\n\u0002\u0010 \n\u0002\u0010\u000e\n\u0000\n\u0002\u0018\u0002\n\u0000\u001a\u0018\u0010\u0000\u001a\u0008\u0012\u0004\u0012\u00020\u00020\u00012\u0008\u0010\u0003\u001a\u0004\u0018\u00010\u0004H\u0000\u00a8\u0006\u0005"
    }
    d2 = {
        "safRuntimeArguments",
        "",
        "",
        "mount",
        "Lcom/bachatas4/android/runtime/process/SafRuntimeMount;",
        "runtime"
    }
    k = 0x2
    mv = {
        0x2,
        0x4,
        0x0
    }
    xi = 0x30
.end annotation


# direct methods
.method public static final safRuntimeArguments(Lcom/bachatas4/android/runtime/process/SafRuntimeMount;)Ljava/util/List;
    .locals 4
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "(",
            "Lcom/bachatas4/android/runtime/process/SafRuntimeMount;",
            ")",
            "Ljava/util/List<",
            "Ljava/lang/String;",
            ">;"
        }
    .end annotation

    const/4 v0, 0x0

    if-eqz p0, :cond_2

    .line 30
    invoke-virtual {p0}, Lcom/bachatas4/android/runtime/process/SafRuntimeMount;->getSocketName()Ljava/lang/String;

    move-result-object v1

    check-cast v1, Ljava/lang/CharSequence;

    invoke-static {v1}, Lkotlin/text/StringsKt;->isBlank(Ljava/lang/CharSequence;)Z

    move-result v1

    if-nez v1, :cond_1

    invoke-virtual {p0}, Lcom/bachatas4/android/runtime/process/SafRuntimeMount;->getSocketName()Ljava/lang/String;

    move-result-object v1

    check-cast v1, Ljava/lang/CharSequence;

    const/4 v2, 0x0

    const/4 v3, 0x2

    invoke-static {v1, v2, v2, v3, v0}, Lkotlin/text/StringsKt;->contains$default(Ljava/lang/CharSequence;CZILjava/lang/Object;)Z

    move-result v1

    if-nez v1, :cond_1

    .line 31
    invoke-virtual {p0}, Lcom/bachatas4/android/runtime/process/SafRuntimeMount;->getToken()Ljava/lang/String;

    move-result-object v1

    check-cast v1, Ljava/lang/CharSequence;

    invoke-static {v1}, Lkotlin/text/StringsKt;->isBlank(Ljava/lang/CharSequence;)Z

    move-result v1

    if-nez v1, :cond_0

    invoke-virtual {p0}, Lcom/bachatas4/android/runtime/process/SafRuntimeMount;->getToken()Ljava/lang/String;

    move-result-object v1

    check-cast v1, Ljava/lang/CharSequence;

    invoke-static {v1, v2, v2, v3, v0}, Lkotlin/text/StringsKt;->contains$default(Ljava/lang/CharSequence;CZILjava/lang/Object;)Z

    move-result v0

    if-nez v0, :cond_0

    const/4 v0, 0x4

    .line 32
    new-array v0, v0, [Ljava/lang/String;

    const-string v1, "--bachata-saf-socket"

    aput-object v1, v0, v2

    const/4 v1, 0x1

    invoke-virtual {p0}, Lcom/bachatas4/android/runtime/process/SafRuntimeMount;->getSocketName()Ljava/lang/String;

    move-result-object v2

    aput-object v2, v0, v1

    const-string v1, "--bachata-saf-token"

    aput-object v1, v0, v3

    const/4 v1, 0x3

    invoke-virtual {p0}, Lcom/bachatas4/android/runtime/process/SafRuntimeMount;->getToken()Ljava/lang/String;

    move-result-object p0

    aput-object p0, v0, v1

    invoke-static {v0}, Lkotlin/collections/CollectionsKt;->listOf([Ljava/lang/Object;)Ljava/util/List;

    move-result-object v0

    goto :goto_0

    .line 31
    :cond_0
    new-instance p0, Ljava/lang/IllegalArgumentException;

    const-string v0, "Invalid SAF token"

    invoke-virtual {v0}, Ljava/lang/Object;->toString()Ljava/lang/String;

    move-result-object v0

    invoke-direct {p0, v0}, Ljava/lang/IllegalArgumentException;-><init>(Ljava/lang/String;)V

    throw p0

    .line 30
    :cond_1
    new-instance p0, Ljava/lang/IllegalArgumentException;

    const-string v0, "Invalid SAF socket"

    invoke-virtual {v0}, Ljava/lang/Object;->toString()Ljava/lang/String;

    move-result-object v0

    invoke-direct {p0, v0}, Ljava/lang/IllegalArgumentException;-><init>(Ljava/lang/String;)V

    throw p0

    :cond_2
    :goto_0
    if-nez v0, :cond_3

    .line 33
    invoke-static {}, Lkotlin/collections/CollectionsKt;->emptyList()Ljava/util/List;

    move-result-object p0

    return-object p0

    :cond_3
    return-object v0
.end method
