.class public final Lcom/bachatas4/android/service/ImportServiceKt;
.super Ljava/lang/Object;
.source "ImportService.kt"


# annotations
.annotation system Ldalvik/annotation/SourceDebugExtension;
    value = "SMAP\nImportService.kt\nKotlin\n*S Kotlin\n*F\n+ 1 ImportService.kt\ncom/bachatas4/android/service/ImportServiceKt\n+ 2 _Arrays.kt\nkotlin/collections/ArraysKt___ArraysKt\n*L\n1#1,1201:1\n15101#2,2:1202\n*S KotlinDebug\n*F\n+ 1 ImportService.kt\ncom/bachatas4/android/service/ImportServiceKt\n*L\n1188#1:1202,2\n*E\n"
.end annotation

.annotation runtime Lkotlin/Metadata;
    d1 = {
        "\u0000\u0010\n\u0000\n\u0002\u0010 \n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\u001a\u0012\u0010\u0000\u001a\u0008\u0012\u0004\u0012\u00020\u00020\u0001*\u00020\u0003H\u0002\u00a8\u0006\u0004"
    }
    d2 = {
        "toImportEntries",
        "",
        "Lcom/bachatas4/android/data/ContentTreeEntry;",
        "Landroidx/documentfile/provider/DocumentFile;",
        "app"
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
.method public static final synthetic access$toImportEntries(Landroidx/documentfile/provider/DocumentFile;)Ljava/util/List;
    .locals 0

    .line 1
    invoke-static {p0}, Lcom/bachatas4/android/service/ImportServiceKt;->toImportEntries(Landroidx/documentfile/provider/DocumentFile;)Ljava/util/List;

    move-result-object p0

    return-object p0
.end method

.method private static final toImportEntries(Landroidx/documentfile/provider/DocumentFile;)Ljava/util/List;
    .locals 13
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "(",
            "Landroidx/documentfile/provider/DocumentFile;",
            ")",
            "Ljava/util/List<",
            "Lcom/bachatas4/android/data/ContentTreeEntry;",
            ">;"
        }
    .end annotation

    .line 1183
    new-instance v0, Ljava/util/ArrayList;

    invoke-direct {v0}, Ljava/util/ArrayList;-><init>()V

    check-cast v0, Ljava/util/List;

    .line 1184
    new-instance v1, Lkotlin/collections/ArrayDeque;

    invoke-direct {v1}, Lkotlin/collections/ArrayDeque;-><init>()V

    .line 1185
    const-string v2, ""

    invoke-static {p0, v2}, Lkotlin/TuplesKt;->to(Ljava/lang/Object;Ljava/lang/Object;)Lkotlin/Pair;

    move-result-object p0

    invoke-virtual {v1, p0}, Lkotlin/collections/ArrayDeque;->add(Ljava/lang/Object;)Z

    .line 1186
    :cond_0
    move-object p0, v1

    check-cast p0, Ljava/util/Collection;

    invoke-interface {p0}, Ljava/util/Collection;->isEmpty()Z

    move-result p0

    if-nez p0, :cond_5

    .line 1187
    invoke-virtual {v1}, Lkotlin/collections/ArrayDeque;->removeLast()Ljava/lang/Object;

    move-result-object p0

    check-cast p0, Lkotlin/Pair;

    invoke-virtual {p0}, Lkotlin/Pair;->component1()Ljava/lang/Object;

    move-result-object v2

    check-cast v2, Landroidx/documentfile/provider/DocumentFile;

    invoke-virtual {p0}, Lkotlin/Pair;->component2()Ljava/lang/Object;

    move-result-object p0

    check-cast p0, Ljava/lang/String;

    .line 1188
    invoke-virtual {v2}, Landroidx/documentfile/provider/DocumentFile;->listFiles()[Landroidx/documentfile/provider/DocumentFile;

    move-result-object v2

    const-string v3, "listFiles(...)"

    invoke-static {v2, v3}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullExpressionValue(Ljava/lang/Object;Ljava/lang/String;)V

    check-cast v2, [Ljava/lang/Object;

    .line 1202
    array-length v3, v2

    const/4 v4, 0x0

    :goto_0
    if-ge v4, v3, :cond_0

    aget-object v5, v2, v4

    check-cast v5, Landroidx/documentfile/provider/DocumentFile;

    .line 1189
    invoke-virtual {v5}, Landroidx/documentfile/provider/DocumentFile;->getName()Ljava/lang/String;

    move-result-object v6

    if-nez v6, :cond_1

    goto :goto_2

    .line 1190
    :cond_1
    move-object v7, p0

    check-cast v7, Ljava/lang/CharSequence;

    invoke-interface {v7}, Ljava/lang/CharSequence;->length()I

    move-result v7

    if-nez v7, :cond_2

    goto :goto_1

    :cond_2
    new-instance v7, Ljava/lang/StringBuilder;

    invoke-direct {v7}, Ljava/lang/StringBuilder;-><init>()V

    invoke-virtual {v7, p0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v7

    const-string v8, "/"

    invoke-virtual {v7, v8}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v7

    invoke-virtual {v7, v6}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v6

    invoke-virtual {v6}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v6

    .line 1192
    :goto_1
    invoke-virtual {v5}, Landroidx/documentfile/provider/DocumentFile;->isDirectory()Z

    move-result v7

    if-eqz v7, :cond_3

    invoke-static {v5, v6}, Lkotlin/TuplesKt;->to(Ljava/lang/Object;Ljava/lang/Object;)Lkotlin/Pair;

    move-result-object v5

    invoke-virtual {v1, v5}, Lkotlin/collections/ArrayDeque;->add(Ljava/lang/Object;)Z

    goto :goto_2

    .line 1193
    :cond_3
    invoke-virtual {v5}, Landroidx/documentfile/provider/DocumentFile;->isFile()Z

    move-result v7

    if-eqz v7, :cond_4

    .line 1194
    new-instance v7, Lcom/bachatas4/android/data/ContentTreeEntry;

    invoke-virtual {v5}, Landroidx/documentfile/provider/DocumentFile;->getUri()Landroid/net/Uri;

    move-result-object v8

    invoke-virtual {v8}, Landroid/net/Uri;->toString()Ljava/lang/String;

    move-result-object v8

    const-string v9, "toString(...)"

    invoke-static {v8, v9}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullExpressionValue(Ljava/lang/Object;Ljava/lang/String;)V

    invoke-virtual {v5}, Landroidx/documentfile/provider/DocumentFile;->length()J

    move-result-wide v9

    const-wide/16 v11, 0x0

    invoke-static {v9, v10, v11, v12}, Lkotlin/ranges/RangesKt;->coerceAtLeast(JJ)J

    move-result-wide v9

    invoke-static {v9, v10}, Ljava/lang/Long;->valueOf(J)Ljava/lang/Long;

    move-result-object v5

    invoke-direct {v7, v6, v8, v5}, Lcom/bachatas4/android/data/ContentTreeEntry;-><init>(Ljava/lang/String;Ljava/lang/String;Ljava/lang/Long;)V

    .line 1193
    invoke-interface {v0, v7}, Ljava/util/List;->add(Ljava/lang/Object;)Z

    :cond_4
    :goto_2
    add-int/lit8 v4, v4, 0x1

    goto :goto_0

    :cond_5
    return-object v0
.end method
