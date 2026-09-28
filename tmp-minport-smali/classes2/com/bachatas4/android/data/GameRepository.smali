.class public final Lcom/bachatas4/android/data/GameRepository;
.super Ljava/lang/Object;
.source "GameRepository.kt"


# annotations
.annotation system Ldalvik/annotation/SourceDebugExtension;
    value = "SMAP\nGameRepository.kt\nKotlin\n*S Kotlin\n*F\n+ 1 GameRepository.kt\ncom/bachatas4/android/data/GameRepository\n+ 2 Transform.kt\nkotlinx/coroutines/flow/FlowKt__TransformKt\n+ 3 Emitters.kt\nkotlinx/coroutines/flow/FlowKt__EmittersKt\n+ 4 SafeCollector.common.kt\nkotlinx/coroutines/flow/internal/SafeCollector_commonKt\n+ 5 _Collections.kt\nkotlin/collections/CollectionsKt___CollectionsKt\n+ 6 fake.kt\nkotlin/jvm/internal/FakeKt\n*L\n1#1,187:1\n49#2:188\n51#2:192\n45#3:189\n49#3:191\n105#4:190\n1739#5:193\n1814#5,3:194\n1373#5,2:198\n1402#5,4:200\n1739#5:204\n1814#5,3:205\n2068#5,2:208\n1#6:197\n*S KotlinDebug\n*F\n+ 1 GameRepository.kt\ncom/bachatas4/android/data/GameRepository\n*L\n18#1:188\n18#1:192\n18#1:189\n18#1:191\n18#1:190\n50#1:193\n50#1:194,3\n132#1:198,2\n132#1:200,4\n134#1:204\n134#1:205,3\n142#1:208,2\n*E\n"
.end annotation

.annotation runtime Lkotlin/Metadata;
    d1 = {
        "\u0000V\n\u0002\u0018\u0002\n\u0002\u0010\u0000\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0008\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\u0010 \n\u0002\u0018\u0002\n\u0002\u0008\u0002\n\u0002\u0010\u000e\n\u0002\u0008\u0002\n\u0002\u0010\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\u0008\u0002\n\u0002\u0010\t\n\u0002\u0008\t\n\u0002\u0010\u000b\n\u0000\u0018\u00002\u00020\u0001B#\u0008\u0007\u0012\u0006\u0010\u0002\u001a\u00020\u0003\u0012\u000c\u0008\u0001\u0010\u0004\u001a\u00020\u0005:\u0002\u0008\u0006\u001a\u0002\u0008\t\u00a2\u0006\u0004\u0008\u0007\u0010\u0008J\u0012\u0010\n\u001a\u000e\u0012\n\u0012\u0008\u0012\u0004\u0012\u00020\r0\u000c0\u000bJ\u0018\u0010\u000e\u001a\u0004\u0018\u00010\r2\u0006\u0010\u000f\u001a\u00020\u0010H\u0086@\u00a2\u0006\u0002\u0010\u0011J&\u0010\u0012\u001a\u00020\u00132\u0006\u0010\u0014\u001a\u00020\u00152\u0006\u0010\u0016\u001a\u00020\u00102\u0006\u0010\u0017\u001a\u00020\u0018H\u0086@\u00a2\u0006\u0002\u0010\u0019J\u000e\u0010\u001a\u001a\u00020\u0013H\u0086@\u00a2\u0006\u0002\u0010\u001bJ\u000e\u0010\u001c\u001a\u00020\u0013H\u0086@\u00a2\u0006\u0002\u0010\u001bJ\u000e\u0010\u001d\u001a\u00020\u0013H\u0086@\u00a2\u0006\u0002\u0010\u001bJ\u0016\u0010\u001e\u001a\u00020\u00132\u0006\u0010\u000f\u001a\u00020\u0010H\u0086@\u00a2\u0006\u0002\u0010\u0011J\u0016\u0010\u001f\u001a\u00020\u00132\u0006\u0010 \u001a\u00020\u0010H\u0086@\u00a2\u0006\u0002\u0010\u0011J\u0016\u0010!\u001a\u00020\"2\u0006\u0010\u000f\u001a\u00020\u0010H\u0086@\u00a2\u0006\u0002\u0010\u0011R\u000e\u0010\u0002\u001a\u00020\u0003X\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u0015\u0010\u0004\u001a\u00020\u00058\u0002X\u0083\u0004\u0092\u0002\u0002\u0008\u0006\u00a2\u0006\u0002\n\u0000\u00a8\u0006#"
    }
    d2 = {
        "Lcom/bachatas4/android/data/GameRepository;",
        "",
        "gameDao",
        "Lcom/bachatas4/android/database/GameDao;",
        "context",
        "Landroid/content/Context;",
        "Ldagger/hilt/android/qualifiers/ApplicationContext;",
        "<init>",
        "(Lcom/bachatas4/android/database/GameDao;Landroid/content/Context;)V",
        "Ljavax/inject/Inject;",
        "observeGames",
        "Lkotlinx/coroutines/flow/Flow;",
        "",
        "Lcom/bachatas4/android/model/Game;",
        "getGame",
        "id",
        "",
        "(Ljava/lang/String;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;",
        "addImportedGame",
        "",
        "result",
        "Lcom/bachatas4/android/data/ContentImportResult;",
        "sourceUri",
        "importedAtMs",
        "",
        "(Lcom/bachatas4/android/data/ContentImportResult;Ljava/lang/String;JLkotlin/coroutines/Continuation;)Ljava/lang/Object;",
        "syncLibrary",
        "(Lkotlin/coroutines/Continuation;)Ljava/lang/Object;",
        "syncOrphanedFolders",
        "backfillTitlesFromSfo",
        "updateLastLaunched",
        "touchGame",
        "gameId",
        "deleteGame",
        "",
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
.field private final context:Landroid/content/Context;
    .annotation runtime Ldagger/hilt/android/qualifiers/ApplicationContext;
    .end annotation
.end field

.field private final gameDao:Lcom/bachatas4/android/database/GameDao;


# direct methods
.method public constructor <init>(Lcom/bachatas4/android/database/GameDao;Landroid/content/Context;)V
    .locals 1
    .param p2    # Landroid/content/Context;
        .annotation runtime Ldagger/hilt/android/qualifiers/ApplicationContext;
        .end annotation
    .end param
    .annotation runtime Ljavax/inject/Inject;
    .end annotation

    const-string v0, "gameDao"

    invoke-static {p1, v0}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullParameter(Ljava/lang/Object;Ljava/lang/String;)V

    const-string v0, "context"

    invoke-static {p2, v0}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullParameter(Ljava/lang/Object;Ljava/lang/String;)V

    .line 13
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    .line 14
    iput-object p1, p0, Lcom/bachatas4/android/data/GameRepository;->gameDao:Lcom/bachatas4/android/database/GameDao;

    .line 15
    iput-object p2, p0, Lcom/bachatas4/android/data/GameRepository;->context:Landroid/content/Context;

    return-void
.end method

.method static final backfillTitlesFromSfo$lambda$2(Ljava/util/Map;Lcom/bachatas4/android/data/GameRepository;Ljava/lang/String;)Ljava/lang/String;
    .locals 2

    const-string v0, "id"

    invoke-static {p2, v0}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullParameter(Ljava/lang/Object;Ljava/lang/String;)V

    .line 136
    invoke-interface {p0, p2}, Ljava/util/Map;->get(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object p0

    check-cast p0, Lcom/bachatas4/android/database/GameEntity;

    const/4 p2, 0x0

    if-nez p0, :cond_0

    return-object p2

    .line 137
    :cond_0
    sget-object v0, Lcom/bachatas4/android/data/GameIconPaths;->INSTANCE:Lcom/bachatas4/android/data/GameIconPaths;

    iget-object p1, p1, Lcom/bachatas4/android/data/GameRepository;->context:Landroid/content/Context;

    invoke-virtual {p1}, Landroid/content/Context;->getFilesDir()Ljava/io/File;

    move-result-object p1

    const-string v1, "getFilesDir(...)"

    invoke-static {p1, v1}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullExpressionValue(Ljava/lang/Object;Ljava/lang/String;)V

    invoke-virtual {p0}, Lcom/bachatas4/android/database/GameEntity;->getRelativePath()Ljava/lang/String;

    move-result-object p0

    invoke-virtual {v0, p1, p0}, Lcom/bachatas4/android/data/GameIconPaths;->paramSfo(Ljava/io/File;Ljava/lang/String;)Ljava/io/File;

    move-result-object p0

    .line 138
    invoke-virtual {p0}, Ljava/io/File;->isFile()Z

    move-result p1

    if-nez p1, :cond_1

    return-object p2

    .line 139
    :cond_1
    :try_start_0
    sget-object p1, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    sget-object p1, Lcom/bachatas4/android/data/ParamSfoReader;->INSTANCE:Lcom/bachatas4/android/data/ParamSfoReader;

    invoke-static {p0}, Lkotlin/io/FilesKt;->readBytes(Ljava/io/File;)[B

    move-result-object p0

    invoke-virtual {p1, p0}, Lcom/bachatas4/android/data/ParamSfoReader;->parse([B)Lcom/bachatas4/android/data/ParamSfoMetadata;

    move-result-object p0

    invoke-virtual {p0}, Lcom/bachatas4/android/data/ParamSfoMetadata;->getTitle()Ljava/lang/String;

    move-result-object p0

    invoke-static {p0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object p0
    :try_end_0
    .catchall {:try_start_0 .. :try_end_0} :catchall_0

    goto :goto_0

    :catchall_0
    move-exception p0

    sget-object p1, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    invoke-static {p0}, Lkotlin/ResultKt;->createFailure(Ljava/lang/Throwable;)Ljava/lang/Object;

    move-result-object p0

    invoke-static {p0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object p0

    :goto_0
    invoke-static {p0}, Lkotlin/Result;->isFailure-impl(Ljava/lang/Object;)Z

    move-result p1

    if-eqz p1, :cond_2

    goto :goto_1

    :cond_2
    move-object p2, p0

    :goto_1
    check-cast p2, Ljava/lang/String;

    return-object p2
.end method


# virtual methods
.method public final addImportedGame(Lcom/bachatas4/android/data/ContentImportResult;Ljava/lang/String;JLkotlin/coroutines/Continuation;)Ljava/lang/Object;
    .locals 11
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "(",
            "Lcom/bachatas4/android/data/ContentImportResult;",
            "Ljava/lang/String;",
            "J",
            "Lkotlin/coroutines/Continuation<",
            "-",
            "Lkotlin/Unit;",
            ">;)",
            "Ljava/lang/Object;"
        }
    .end annotation

    .line 27
    iget-object p0, p0, Lcom/bachatas4/android/data/GameRepository;->gameDao:Lcom/bachatas4/android/database/GameDao;

    .line 28
    new-instance v0, Lcom/bachatas4/android/database/GameEntity;

    .line 29
    invoke-virtual {p1}, Lcom/bachatas4/android/data/ContentImportResult;->getGame()Lcom/bachatas4/android/model/Game;

    move-result-object v1

    invoke-virtual {v1}, Lcom/bachatas4/android/model/Game;->getId()Ljava/lang/String;

    move-result-object v1

    .line 30
    invoke-virtual {p1}, Lcom/bachatas4/android/data/ContentImportResult;->getGame()Lcom/bachatas4/android/model/Game;

    move-result-object v2

    invoke-virtual {v2}, Lcom/bachatas4/android/model/Game;->getTitle()Ljava/lang/String;

    move-result-object v2

    .line 31
    invoke-virtual {p1}, Lcom/bachatas4/android/data/ContentImportResult;->getGame()Lcom/bachatas4/android/model/Game;

    move-result-object v3

    invoke-virtual {v3}, Lcom/bachatas4/android/model/Game;->getRelativePath()Ljava/lang/String;

    move-result-object v3

    .line 34
    invoke-virtual {p1}, Lcom/bachatas4/android/data/ContentImportResult;->getGame()Lcom/bachatas4/android/model/Game;

    move-result-object v4

    invoke-virtual {v4}, Lcom/bachatas4/android/model/Game;->getSubtitle()Ljava/lang/String;

    move-result-object v7

    .line 35
    invoke-virtual {p1}, Lcom/bachatas4/android/data/ContentImportResult;->getGame()Lcom/bachatas4/android/model/Game;

    move-result-object p1

    invoke-virtual {p1}, Lcom/bachatas4/android/model/Game;->getDetail()Ljava/lang/String;

    move-result-object v8

    const-wide/16 v9, 0x0

    move-object v4, p2

    move-wide v5, p3

    .line 28
    invoke-direct/range {v0 .. v10}, Lcom/bachatas4/android/database/GameEntity;-><init>(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;JLjava/lang/String;Ljava/lang/String;J)V

    move-object/from16 p1, p5

    .line 27
    invoke-interface {p0, v0, p1}, Lcom/bachatas4/android/database/GameDao;->insert(Lcom/bachatas4/android/database/GameEntity;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;

    move-result-object p0

    return-object p0
.end method

.method public final backfillTitlesFromSfo(Lkotlin/coroutines/Continuation;)Ljava/lang/Object;
    .locals 12
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "(",
            "Lkotlin/coroutines/Continuation<",
            "-",
            "Lkotlin/Unit;",
            ">;)",
            "Ljava/lang/Object;"
        }
    .end annotation

    instance-of v0, p1, Lcom/bachatas4/android/data/GameRepository$backfillTitlesFromSfo$1;

    if-eqz v0, :cond_0

    move-object v0, p1

    check-cast v0, Lcom/bachatas4/android/data/GameRepository$backfillTitlesFromSfo$1;

    iget v1, v0, Lcom/bachatas4/android/data/GameRepository$backfillTitlesFromSfo$1;->label:I

    const/high16 v2, -0x80000000

    and-int/2addr v1, v2

    if-eqz v1, :cond_0

    iget p1, v0, Lcom/bachatas4/android/data/GameRepository$backfillTitlesFromSfo$1;->label:I

    sub-int/2addr p1, v2

    iput p1, v0, Lcom/bachatas4/android/data/GameRepository$backfillTitlesFromSfo$1;->label:I

    goto :goto_0

    :cond_0
    new-instance v0, Lcom/bachatas4/android/data/GameRepository$backfillTitlesFromSfo$1;

    invoke-direct {v0, p0, p1}, Lcom/bachatas4/android/data/GameRepository$backfillTitlesFromSfo$1;-><init>(Lcom/bachatas4/android/data/GameRepository;Lkotlin/coroutines/Continuation;)V

    :goto_0
    iget-object p1, v0, Lcom/bachatas4/android/data/GameRepository$backfillTitlesFromSfo$1;->result:Ljava/lang/Object;

    invoke-static {}, Lkotlin/coroutines/intrinsics/IntrinsicsKt;->getCOROUTINE_SUSPENDED()Ljava/lang/Object;

    move-result-object v1

    .line 130
    iget v2, v0, Lcom/bachatas4/android/data/GameRepository$backfillTitlesFromSfo$1;->label:I

    const/4 v3, 0x2

    const/4 v4, 0x1

    if-eqz v2, :cond_3

    if-eq v2, v4, :cond_2

    if-ne v2, v3, :cond_1

    iget-object v2, v0, Lcom/bachatas4/android/data/GameRepository$backfillTitlesFromSfo$1;->L$7:Ljava/lang/Object;

    check-cast v2, Ljava/lang/String;

    iget-object v2, v0, Lcom/bachatas4/android/data/GameRepository$backfillTitlesFromSfo$1;->L$6:Ljava/lang/Object;

    check-cast v2, Ljava/lang/String;

    iget-object v2, v0, Lcom/bachatas4/android/data/GameRepository$backfillTitlesFromSfo$1;->L$5:Ljava/lang/Object;

    iget-object v2, v0, Lcom/bachatas4/android/data/GameRepository$backfillTitlesFromSfo$1;->L$4:Ljava/lang/Object;

    check-cast v2, Ljava/util/Iterator;

    iget-object v4, v0, Lcom/bachatas4/android/data/GameRepository$backfillTitlesFromSfo$1;->L$3:Ljava/lang/Object;

    check-cast v4, Ljava/lang/Iterable;

    iget-object v5, v0, Lcom/bachatas4/android/data/GameRepository$backfillTitlesFromSfo$1;->L$2:Ljava/lang/Object;

    check-cast v5, Ljava/util/List;

    iget-object v6, v0, Lcom/bachatas4/android/data/GameRepository$backfillTitlesFromSfo$1;->L$1:Ljava/lang/Object;

    check-cast v6, Ljava/util/Map;

    iget-object v7, v0, Lcom/bachatas4/android/data/GameRepository$backfillTitlesFromSfo$1;->L$0:Ljava/lang/Object;

    check-cast v7, Ljava/util/List;

    invoke-static {p1}, Lkotlin/ResultKt;->throwOnFailure(Ljava/lang/Object;)V

    goto/16 :goto_4

    :cond_1
    new-instance p0, Ljava/lang/IllegalStateException;

    const-string p1, "call to \'resume\' before \'invoke\' with coroutine"

    invoke-direct {p0, p1}, Ljava/lang/IllegalStateException;-><init>(Ljava/lang/String;)V

    throw p0

    :cond_2
    invoke-static {p1}, Lkotlin/ResultKt;->throwOnFailure(Ljava/lang/Object;)V

    goto :goto_1

    :cond_3
    invoke-static {p1}, Lkotlin/ResultKt;->throwOnFailure(Ljava/lang/Object;)V

    .line 131
    iget-object p1, p0, Lcom/bachatas4/android/data/GameRepository;->gameDao:Lcom/bachatas4/android/database/GameDao;

    iput v4, v0, Lcom/bachatas4/android/data/GameRepository$backfillTitlesFromSfo$1;->label:I

    invoke-interface {p1, v0}, Lcom/bachatas4/android/database/GameDao;->getAll(Lkotlin/coroutines/Continuation;)Ljava/lang/Object;

    move-result-object p1

    if-ne p1, v1, :cond_4

    goto/16 :goto_5

    .line 130
    :cond_4
    :goto_1
    check-cast p1, Ljava/util/List;

    .line 132
    move-object v2, p1

    check-cast v2, Ljava/lang/Iterable;

    const/16 v4, 0xa

    .line 198
    invoke-static {v2, v4}, Lkotlin/collections/CollectionsKt;->collectionSizeOrDefault(Ljava/lang/Iterable;I)I

    move-result v5

    invoke-static {v5}, Lkotlin/collections/MapsKt;->mapCapacity(I)I

    move-result v5

    const/16 v6, 0x10

    invoke-static {v5, v6}, Lkotlin/ranges/RangesKt;->coerceAtLeast(II)I

    move-result v5

    .line 199
    new-instance v6, Ljava/util/LinkedHashMap;

    invoke-direct {v6, v5}, Ljava/util/LinkedHashMap;-><init>(I)V

    check-cast v6, Ljava/util/Map;

    .line 200
    invoke-interface {v2}, Ljava/lang/Iterable;->iterator()Ljava/util/Iterator;

    move-result-object v5

    :goto_2
    invoke-interface {v5}, Ljava/util/Iterator;->hasNext()Z

    move-result v7

    if-eqz v7, :cond_5

    invoke-interface {v5}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v7

    .line 201
    move-object v8, v7

    check-cast v8, Lcom/bachatas4/android/database/GameEntity;

    .line 132
    invoke-virtual {v8}, Lcom/bachatas4/android/database/GameEntity;->getId()Ljava/lang/String;

    move-result-object v8

    .line 201
    invoke-interface {v6, v8, v7}, Ljava/util/Map;->put(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;

    goto :goto_2

    .line 204
    :cond_5
    new-instance v5, Ljava/util/ArrayList;

    invoke-static {v2, v4}, Lkotlin/collections/CollectionsKt;->collectionSizeOrDefault(Ljava/lang/Iterable;I)I

    move-result v4

    invoke-direct {v5, v4}, Ljava/util/ArrayList;-><init>(I)V

    check-cast v5, Ljava/util/Collection;

    .line 205
    invoke-interface {v2}, Ljava/lang/Iterable;->iterator()Ljava/util/Iterator;

    move-result-object v2

    :goto_3
    invoke-interface {v2}, Ljava/util/Iterator;->hasNext()Z

    move-result v4

    if-eqz v4, :cond_6

    invoke-interface {v2}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v4

    .line 206
    check-cast v4, Lcom/bachatas4/android/database/GameEntity;

    .line 134
    invoke-virtual {v4}, Lcom/bachatas4/android/database/GameEntity;->getId()Ljava/lang/String;

    move-result-object v7

    invoke-virtual {v4}, Lcom/bachatas4/android/database/GameEntity;->getTitle()Ljava/lang/String;

    move-result-object v4

    invoke-static {v7, v4}, Lkotlin/TuplesKt;->to(Ljava/lang/Object;Ljava/lang/Object;)Lkotlin/Pair;

    move-result-object v4

    .line 206
    invoke-interface {v5, v4}, Ljava/util/Collection;->add(Ljava/lang/Object;)Z

    goto :goto_3

    .line 207
    :cond_6
    check-cast v5, Ljava/util/List;

    .line 133
    new-instance v2, Lcom/bachatas4/android/data/GameRepository$$ExternalSyntheticLambda0;

    invoke-direct {v2, v6, p0}, Lcom/bachatas4/android/data/GameRepository$$ExternalSyntheticLambda0;-><init>(Ljava/util/Map;Lcom/bachatas4/android/data/GameRepository;)V

    invoke-static {v5, v2}, Lcom/bachatas4/android/data/GameTitleBackfillKt;->titlesToUpdate(Ljava/util/List;Lkotlin/jvm/functions/Function1;)Ljava/util/List;

    move-result-object v2

    .line 142
    move-object v4, v2

    check-cast v4, Ljava/lang/Iterable;

    .line 208
    invoke-interface {v4}, Ljava/lang/Iterable;->iterator()Ljava/util/Iterator;

    move-result-object v5

    move-object v7, v5

    move-object v5, v2

    move-object v2, v7

    move-object v7, p1

    :cond_7
    :goto_4
    invoke-interface {v2}, Ljava/util/Iterator;->hasNext()Z

    move-result p1

    if-eqz p1, :cond_8

    invoke-interface {v2}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object p1

    move-object v8, p1

    check-cast v8, Lkotlin/Pair;

    invoke-virtual {v8}, Lkotlin/Pair;->component1()Ljava/lang/Object;

    move-result-object v9

    check-cast v9, Ljava/lang/String;

    invoke-virtual {v8}, Lkotlin/Pair;->component2()Ljava/lang/Object;

    move-result-object v8

    check-cast v8, Ljava/lang/String;

    .line 142
    iget-object v10, p0, Lcom/bachatas4/android/data/GameRepository;->gameDao:Lcom/bachatas4/android/database/GameDao;

    invoke-static {v7}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v11

    iput-object v11, v0, Lcom/bachatas4/android/data/GameRepository$backfillTitlesFromSfo$1;->L$0:Ljava/lang/Object;

    invoke-static {v6}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v11

    iput-object v11, v0, Lcom/bachatas4/android/data/GameRepository$backfillTitlesFromSfo$1;->L$1:Ljava/lang/Object;

    invoke-static {v5}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v11

    iput-object v11, v0, Lcom/bachatas4/android/data/GameRepository$backfillTitlesFromSfo$1;->L$2:Ljava/lang/Object;

    invoke-static {v4}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v11

    iput-object v11, v0, Lcom/bachatas4/android/data/GameRepository$backfillTitlesFromSfo$1;->L$3:Ljava/lang/Object;

    iput-object v2, v0, Lcom/bachatas4/android/data/GameRepository$backfillTitlesFromSfo$1;->L$4:Ljava/lang/Object;

    invoke-static {p1}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object p1

    iput-object p1, v0, Lcom/bachatas4/android/data/GameRepository$backfillTitlesFromSfo$1;->L$5:Ljava/lang/Object;

    invoke-static {v9}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object p1

    iput-object p1, v0, Lcom/bachatas4/android/data/GameRepository$backfillTitlesFromSfo$1;->L$6:Ljava/lang/Object;

    invoke-static {v8}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object p1

    iput-object p1, v0, Lcom/bachatas4/android/data/GameRepository$backfillTitlesFromSfo$1;->L$7:Ljava/lang/Object;

    iput v3, v0, Lcom/bachatas4/android/data/GameRepository$backfillTitlesFromSfo$1;->label:I

    invoke-interface {v10, v9, v8, v0}, Lcom/bachatas4/android/database/GameDao;->updateTitle(Ljava/lang/String;Ljava/lang/String;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;

    move-result-object p1

    if-ne p1, v1, :cond_7

    :goto_5
    return-object v1

    .line 143
    :cond_8
    sget-object p0, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;

    return-object p0
.end method

.method public final deleteGame(Ljava/lang/String;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;
    .locals 9
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "(",
            "Ljava/lang/String;",
            "Lkotlin/coroutines/Continuation<",
            "-",
            "Ljava/lang/Boolean;",
            ">;)",
            "Ljava/lang/Object;"
        }
    .end annotation

    instance-of v0, p2, Lcom/bachatas4/android/data/GameRepository$deleteGame$1;

    if-eqz v0, :cond_0

    move-object v0, p2

    check-cast v0, Lcom/bachatas4/android/data/GameRepository$deleteGame$1;

    iget v1, v0, Lcom/bachatas4/android/data/GameRepository$deleteGame$1;->label:I

    const/high16 v2, -0x80000000

    and-int/2addr v1, v2

    if-eqz v1, :cond_0

    iget p2, v0, Lcom/bachatas4/android/data/GameRepository$deleteGame$1;->label:I

    sub-int/2addr p2, v2

    iput p2, v0, Lcom/bachatas4/android/data/GameRepository$deleteGame$1;->label:I

    goto :goto_0

    :cond_0
    new-instance v0, Lcom/bachatas4/android/data/GameRepository$deleteGame$1;

    invoke-direct {v0, p0, p2}, Lcom/bachatas4/android/data/GameRepository$deleteGame$1;-><init>(Lcom/bachatas4/android/data/GameRepository;Lkotlin/coroutines/Continuation;)V

    :goto_0
    iget-object p2, v0, Lcom/bachatas4/android/data/GameRepository$deleteGame$1;->result:Ljava/lang/Object;

    invoke-static {}, Lkotlin/coroutines/intrinsics/IntrinsicsKt;->getCOROUTINE_SUSPENDED()Ljava/lang/Object;

    move-result-object v1

    .line 168
    iget v2, v0, Lcom/bachatas4/android/data/GameRepository$deleteGame$1;->label:I

    const/4 v3, 0x2

    const/4 v4, 0x0

    const/4 v5, 0x1

    if-eqz v2, :cond_3

    if-eq v2, v5, :cond_2

    if-ne v2, v3, :cond_1

    iget-object p0, v0, Lcom/bachatas4/android/data/GameRepository$deleteGame$1;->L$3:Ljava/lang/Object;

    check-cast p0, Ljava/io/File;

    iget-object p0, v0, Lcom/bachatas4/android/data/GameRepository$deleteGame$1;->L$2:Ljava/lang/Object;

    check-cast p0, Ljava/io/File;

    iget-object p0, v0, Lcom/bachatas4/android/data/GameRepository$deleteGame$1;->L$1:Ljava/lang/Object;

    check-cast p0, Lcom/bachatas4/android/database/GameEntity;

    iget-object p0, v0, Lcom/bachatas4/android/data/GameRepository$deleteGame$1;->L$0:Ljava/lang/Object;

    check-cast p0, Ljava/lang/String;

    invoke-static {p2}, Lkotlin/ResultKt;->throwOnFailure(Ljava/lang/Object;)V

    goto/16 :goto_3

    :cond_1
    new-instance p0, Ljava/lang/IllegalStateException;

    const-string p1, "call to \'resume\' before \'invoke\' with coroutine"

    invoke-direct {p0, p1}, Ljava/lang/IllegalStateException;-><init>(Ljava/lang/String;)V

    throw p0

    :cond_2
    iget-object p1, v0, Lcom/bachatas4/android/data/GameRepository$deleteGame$1;->L$0:Ljava/lang/Object;

    check-cast p1, Ljava/lang/String;

    invoke-static {p2}, Lkotlin/ResultKt;->throwOnFailure(Ljava/lang/Object;)V

    goto :goto_1

    :cond_3
    invoke-static {p2}, Lkotlin/ResultKt;->throwOnFailure(Ljava/lang/Object;)V

    .line 169
    iget-object p2, p0, Lcom/bachatas4/android/data/GameRepository;->gameDao:Lcom/bachatas4/android/database/GameDao;

    iput-object p1, v0, Lcom/bachatas4/android/data/GameRepository$deleteGame$1;->L$0:Ljava/lang/Object;

    iput v5, v0, Lcom/bachatas4/android/data/GameRepository$deleteGame$1;->label:I

    invoke-interface {p2, p1, v0}, Lcom/bachatas4/android/database/GameDao;->getById(Ljava/lang/String;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;

    move-result-object p2

    if-ne p2, v1, :cond_4

    goto :goto_2

    :cond_4
    :goto_1
    check-cast p2, Lcom/bachatas4/android/database/GameEntity;

    if-nez p2, :cond_5

    invoke-static {v4}, Lkotlin/coroutines/jvm/internal/Boxing;->boxBoolean(Z)Ljava/lang/Boolean;

    move-result-object p0

    return-object p0

    .line 170
    :cond_5
    iget-object v2, p0, Lcom/bachatas4/android/data/GameRepository;->context:Landroid/content/Context;

    invoke-virtual {v2}, Landroid/content/Context;->getFilesDir()Ljava/io/File;

    move-result-object v2

    const-string v6, "getFilesDir(...)"

    invoke-static {v2, v6}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullExpressionValue(Ljava/lang/Object;Ljava/lang/String;)V

    const-string v7, "games"

    invoke-static {v2, v7}, Lkotlin/io/FilesKt;->resolve(Ljava/io/File;Ljava/lang/String;)Ljava/io/File;

    move-result-object v2

    invoke-virtual {v2}, Ljava/io/File;->getCanonicalFile()Ljava/io/File;

    move-result-object v2

    .line 171
    iget-object v7, p0, Lcom/bachatas4/android/data/GameRepository;->context:Landroid/content/Context;

    invoke-virtual {v7}, Landroid/content/Context;->getFilesDir()Ljava/io/File;

    move-result-object v7

    invoke-static {v7, v6}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullExpressionValue(Ljava/lang/Object;Ljava/lang/String;)V

    invoke-virtual {p2}, Lcom/bachatas4/android/database/GameEntity;->getRelativePath()Ljava/lang/String;

    move-result-object v6

    invoke-static {v7, v6}, Lkotlin/io/FilesKt;->resolve(Ljava/io/File;Ljava/lang/String;)Ljava/io/File;

    move-result-object v6

    invoke-virtual {v6}, Ljava/io/File;->getCanonicalFile()Ljava/io/File;

    move-result-object v6

    .line 172
    invoke-virtual {v6}, Ljava/io/File;->toPath()Ljava/nio/file/Path;

    move-result-object v7

    invoke-virtual {v2}, Ljava/io/File;->toPath()Ljava/nio/file/Path;

    move-result-object v8

    invoke-interface {v7, v8}, Ljava/nio/file/Path;->startsWith(Ljava/nio/file/Path;)Z

    move-result v7

    if-eqz v7, :cond_9

    .line 173
    invoke-virtual {v6}, Ljava/io/File;->exists()Z

    move-result v7

    if-eqz v7, :cond_6

    invoke-static {v6}, Lkotlin/jvm/internal/Intrinsics;->checkNotNull(Ljava/lang/Object;)V

    invoke-static {v6}, Lkotlin/io/FilesKt;->deleteRecursively(Ljava/io/File;)Z

    move-result v7

    if-nez v7, :cond_6

    invoke-static {v4}, Lkotlin/coroutines/jvm/internal/Boxing;->boxBoolean(Z)Ljava/lang/Boolean;

    move-result-object p0

    return-object p0

    .line 174
    :cond_6
    iget-object p0, p0, Lcom/bachatas4/android/data/GameRepository;->gameDao:Lcom/bachatas4/android/database/GameDao;

    invoke-static {p1}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v7

    iput-object v7, v0, Lcom/bachatas4/android/data/GameRepository$deleteGame$1;->L$0:Ljava/lang/Object;

    invoke-static {p2}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object p2

    iput-object p2, v0, Lcom/bachatas4/android/data/GameRepository$deleteGame$1;->L$1:Ljava/lang/Object;

    invoke-static {v2}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object p2

    iput-object p2, v0, Lcom/bachatas4/android/data/GameRepository$deleteGame$1;->L$2:Ljava/lang/Object;

    invoke-static {v6}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object p2

    iput-object p2, v0, Lcom/bachatas4/android/data/GameRepository$deleteGame$1;->L$3:Ljava/lang/Object;

    iput v3, v0, Lcom/bachatas4/android/data/GameRepository$deleteGame$1;->label:I

    invoke-interface {p0, p1, v0}, Lcom/bachatas4/android/database/GameDao;->deleteById(Ljava/lang/String;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;

    move-result-object p2

    if-ne p2, v1, :cond_7

    :goto_2
    return-object v1

    :cond_7
    :goto_3
    check-cast p2, Ljava/lang/Number;

    invoke-virtual {p2}, Ljava/lang/Number;->intValue()I

    move-result p0

    if-lez p0, :cond_8

    move v4, v5

    :cond_8
    invoke-static {v4}, Lkotlin/coroutines/jvm/internal/Boxing;->boxBoolean(Z)Ljava/lang/Boolean;

    move-result-object p0

    return-object p0

    .line 172
    :cond_9
    new-instance p0, Ljava/lang/IllegalArgumentException;

    const-string p1, "Game path escapes app-owned storage"

    invoke-virtual {p1}, Ljava/lang/Object;->toString()Ljava/lang/String;

    move-result-object p1

    invoke-direct {p0, p1}, Ljava/lang/IllegalArgumentException;-><init>(Ljava/lang/String;)V

    throw p0
.end method

.method public final getGame(Ljava/lang/String;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;
    .locals 4
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "(",
            "Ljava/lang/String;",
            "Lkotlin/coroutines/Continuation<",
            "-",
            "Lcom/bachatas4/android/model/Game;",
            ">;)",
            "Ljava/lang/Object;"
        }
    .end annotation

    instance-of v0, p2, Lcom/bachatas4/android/data/GameRepository$getGame$1;

    if-eqz v0, :cond_0

    move-object v0, p2

    check-cast v0, Lcom/bachatas4/android/data/GameRepository$getGame$1;

    iget v1, v0, Lcom/bachatas4/android/data/GameRepository$getGame$1;->label:I

    const/high16 v2, -0x80000000

    and-int/2addr v1, v2

    if-eqz v1, :cond_0

    iget p2, v0, Lcom/bachatas4/android/data/GameRepository$getGame$1;->label:I

    sub-int/2addr p2, v2

    iput p2, v0, Lcom/bachatas4/android/data/GameRepository$getGame$1;->label:I

    goto :goto_0

    :cond_0
    new-instance v0, Lcom/bachatas4/android/data/GameRepository$getGame$1;

    invoke-direct {v0, p0, p2}, Lcom/bachatas4/android/data/GameRepository$getGame$1;-><init>(Lcom/bachatas4/android/data/GameRepository;Lkotlin/coroutines/Continuation;)V

    :goto_0
    iget-object p2, v0, Lcom/bachatas4/android/data/GameRepository$getGame$1;->result:Ljava/lang/Object;

    invoke-static {}, Lkotlin/coroutines/intrinsics/IntrinsicsKt;->getCOROUTINE_SUSPENDED()Ljava/lang/Object;

    move-result-object v1

    .line 20
    iget v2, v0, Lcom/bachatas4/android/data/GameRepository$getGame$1;->label:I

    const/4 v3, 0x1

    if-eqz v2, :cond_2

    if-ne v2, v3, :cond_1

    iget-object p0, v0, Lcom/bachatas4/android/data/GameRepository$getGame$1;->L$0:Ljava/lang/Object;

    check-cast p0, Ljava/lang/String;

    invoke-static {p2}, Lkotlin/ResultKt;->throwOnFailure(Ljava/lang/Object;)V

    goto :goto_1

    :cond_1
    new-instance p0, Ljava/lang/IllegalStateException;

    const-string p1, "call to \'resume\' before \'invoke\' with coroutine"

    invoke-direct {p0, p1}, Ljava/lang/IllegalStateException;-><init>(Ljava/lang/String;)V

    throw p0

    :cond_2
    invoke-static {p2}, Lkotlin/ResultKt;->throwOnFailure(Ljava/lang/Object;)V

    iget-object p0, p0, Lcom/bachatas4/android/data/GameRepository;->gameDao:Lcom/bachatas4/android/database/GameDao;

    invoke-static {p1}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object p2

    iput-object p2, v0, Lcom/bachatas4/android/data/GameRepository$getGame$1;->L$0:Ljava/lang/Object;

    iput v3, v0, Lcom/bachatas4/android/data/GameRepository$getGame$1;->label:I

    invoke-interface {p0, p1, v0}, Lcom/bachatas4/android/database/GameDao;->getById(Ljava/lang/String;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;

    move-result-object p2

    if-ne p2, v1, :cond_3

    return-object v1

    :cond_3
    :goto_1
    check-cast p2, Lcom/bachatas4/android/database/GameEntity;

    if-eqz p2, :cond_4

    invoke-static {p2}, Lcom/bachatas4/android/data/GameRepositoryKt;->access$toModel(Lcom/bachatas4/android/database/GameEntity;)Lcom/bachatas4/android/model/Game;

    move-result-object p0

    return-object p0

    :cond_4
    const/4 p0, 0x0

    return-object p0
.end method

.method public final observeGames()Lkotlinx/coroutines/flow/Flow;
    .locals 1
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "()",
            "Lkotlinx/coroutines/flow/Flow<",
            "Ljava/util/List<",
            "Lcom/bachatas4/android/model/Game;",
            ">;>;"
        }
    .end annotation

    .line 18
    iget-object p0, p0, Lcom/bachatas4/android/data/GameRepository;->gameDao:Lcom/bachatas4/android/database/GameDao;

    invoke-interface {p0}, Lcom/bachatas4/android/database/GameDao;->observeAll()Lkotlinx/coroutines/flow/Flow;

    move-result-object p0

    .line 190
    new-instance v0, Lcom/bachatas4/android/data/GameRepository$observeGames$$inlined$map$1;

    invoke-direct {v0, p0}, Lcom/bachatas4/android/data/GameRepository$observeGames$$inlined$map$1;-><init>(Lkotlinx/coroutines/flow/Flow;)V

    check-cast v0, Lkotlinx/coroutines/flow/Flow;

    return-object v0
.end method

.method public final syncLibrary(Lkotlin/coroutines/Continuation;)Ljava/lang/Object;
    .locals 30
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "(",
            "Lkotlin/coroutines/Continuation<",
            "-",
            "Lkotlin/Unit;",
            ">;)",
            "Ljava/lang/Object;"
        }
    .end annotation

    move-object/from16 v1, p0

    move-object/from16 v0, p1

    instance-of v2, v0, Lcom/bachatas4/android/data/GameRepository$syncLibrary$1;

    if-eqz v2, :cond_0

    move-object v2, v0

    check-cast v2, Lcom/bachatas4/android/data/GameRepository$syncLibrary$1;

    iget v3, v2, Lcom/bachatas4/android/data/GameRepository$syncLibrary$1;->label:I

    const/high16 v4, -0x80000000

    and-int/2addr v3, v4

    if-eqz v3, :cond_0

    iget v0, v2, Lcom/bachatas4/android/data/GameRepository$syncLibrary$1;->label:I

    sub-int/2addr v0, v4

    iput v0, v2, Lcom/bachatas4/android/data/GameRepository$syncLibrary$1;->label:I

    goto :goto_0

    :cond_0
    new-instance v2, Lcom/bachatas4/android/data/GameRepository$syncLibrary$1;

    invoke-direct {v2, v1, v0}, Lcom/bachatas4/android/data/GameRepository$syncLibrary$1;-><init>(Lcom/bachatas4/android/data/GameRepository;Lkotlin/coroutines/Continuation;)V

    :goto_0
    iget-object v0, v2, Lcom/bachatas4/android/data/GameRepository$syncLibrary$1;->result:Ljava/lang/Object;

    invoke-static {}, Lkotlin/coroutines/intrinsics/IntrinsicsKt;->getCOROUTINE_SUSPENDED()Ljava/lang/Object;

    move-result-object v3

    .line 45
    iget v4, v2, Lcom/bachatas4/android/data/GameRepository$syncLibrary$1;->label:I

    const/4 v5, 0x3

    const/4 v6, 0x2

    const/4 v7, 0x1

    const-string v8, "getFilesDir(...)"

    if-eqz v4, :cond_4

    if-eq v4, v7, :cond_3

    if-eq v4, v6, :cond_2

    if-ne v4, v5, :cond_1

    iget-object v4, v2, Lcom/bachatas4/android/data/GameRepository$syncLibrary$1;->L$7:Ljava/lang/Object;

    check-cast v4, Lcom/bachatas4/android/data/GameRepository;

    iget-object v4, v2, Lcom/bachatas4/android/data/GameRepository$syncLibrary$1;->L$6:Ljava/lang/Object;

    check-cast v4, Ljava/io/File;

    iget-object v4, v2, Lcom/bachatas4/android/data/GameRepository$syncLibrary$1;->L$5:Ljava/lang/Object;

    check-cast v4, Ljava/lang/String;

    iget-object v4, v2, Lcom/bachatas4/android/data/GameRepository$syncLibrary$1;->L$4:Ljava/lang/Object;

    check-cast v4, Ljava/util/Iterator;

    iget-object v6, v2, Lcom/bachatas4/android/data/GameRepository$syncLibrary$1;->L$3:Ljava/lang/Object;

    check-cast v6, Lcom/bachatas4/android/data/LibrarySyncPlan;

    iget-object v7, v2, Lcom/bachatas4/android/data/GameRepository$syncLibrary$1;->L$2:Ljava/lang/Object;

    check-cast v7, Ljava/util/Set;

    iget-object v9, v2, Lcom/bachatas4/android/data/GameRepository$syncLibrary$1;->L$1:Ljava/lang/Object;

    check-cast v9, Ljava/util/List;

    iget-object v10, v2, Lcom/bachatas4/android/data/GameRepository$syncLibrary$1;->L$0:Ljava/lang/Object;

    check-cast v10, Ljava/io/File;

    :try_start_0
    invoke-static {v0}, Lkotlin/ResultKt;->throwOnFailure(Ljava/lang/Object;)V
    :try_end_0
    .catchall {:try_start_0 .. :try_end_0} :catchall_0

    goto/16 :goto_6

    :catchall_0
    move-exception v0

    goto/16 :goto_7

    :cond_1
    new-instance v0, Ljava/lang/IllegalStateException;

    const-string v1, "call to \'resume\' before \'invoke\' with coroutine"

    invoke-direct {v0, v1}, Ljava/lang/IllegalStateException;-><init>(Ljava/lang/String;)V

    throw v0

    :cond_2
    iget-object v4, v2, Lcom/bachatas4/android/data/GameRepository$syncLibrary$1;->L$6:Ljava/lang/Object;

    check-cast v4, Ljava/io/File;

    iget-object v4, v2, Lcom/bachatas4/android/data/GameRepository$syncLibrary$1;->L$5:Ljava/lang/Object;

    check-cast v4, Lcom/bachatas4/android/data/LibraryInsert;

    iget-object v4, v2, Lcom/bachatas4/android/data/GameRepository$syncLibrary$1;->L$4:Ljava/lang/Object;

    check-cast v4, Ljava/util/Iterator;

    iget-object v7, v2, Lcom/bachatas4/android/data/GameRepository$syncLibrary$1;->L$3:Ljava/lang/Object;

    check-cast v7, Lcom/bachatas4/android/data/LibrarySyncPlan;

    iget-object v9, v2, Lcom/bachatas4/android/data/GameRepository$syncLibrary$1;->L$2:Ljava/lang/Object;

    check-cast v9, Ljava/util/Set;

    iget-object v10, v2, Lcom/bachatas4/android/data/GameRepository$syncLibrary$1;->L$1:Ljava/lang/Object;

    check-cast v10, Ljava/util/List;

    iget-object v11, v2, Lcom/bachatas4/android/data/GameRepository$syncLibrary$1;->L$0:Ljava/lang/Object;

    check-cast v11, Ljava/io/File;

    invoke-static {v0}, Lkotlin/ResultKt;->throwOnFailure(Ljava/lang/Object;)V

    goto/16 :goto_3

    :cond_3
    iget-object v4, v2, Lcom/bachatas4/android/data/GameRepository$syncLibrary$1;->L$0:Ljava/lang/Object;

    check-cast v4, Ljava/io/File;

    invoke-static {v0}, Lkotlin/ResultKt;->throwOnFailure(Ljava/lang/Object;)V

    goto :goto_1

    :cond_4
    invoke-static {v0}, Lkotlin/ResultKt;->throwOnFailure(Ljava/lang/Object;)V

    .line 46
    iget-object v0, v1, Lcom/bachatas4/android/data/GameRepository;->context:Landroid/content/Context;

    invoke-virtual {v0}, Landroid/content/Context;->getFilesDir()Ljava/io/File;

    move-result-object v0

    invoke-static {v0, v8}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullExpressionValue(Ljava/lang/Object;Ljava/lang/String;)V

    const-string v4, "games"

    invoke-static {v0, v4}, Lkotlin/io/FilesKt;->resolve(Ljava/io/File;Ljava/lang/String;)Ljava/io/File;

    move-result-object v4

    .line 47
    invoke-virtual {v4}, Ljava/io/File;->isDirectory()Z

    move-result v0

    if-nez v0, :cond_5

    sget-object v0, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;

    return-object v0

    .line 49
    :cond_5
    iget-object v0, v1, Lcom/bachatas4/android/data/GameRepository;->gameDao:Lcom/bachatas4/android/database/GameDao;

    iput-object v4, v2, Lcom/bachatas4/android/data/GameRepository$syncLibrary$1;->L$0:Ljava/lang/Object;

    iput v7, v2, Lcom/bachatas4/android/data/GameRepository$syncLibrary$1;->label:I

    invoke-interface {v0, v2}, Lcom/bachatas4/android/database/GameDao;->getAll(Lkotlin/coroutines/Continuation;)Ljava/lang/Object;

    move-result-object v0

    if-ne v0, v3, :cond_6

    goto/16 :goto_5

    .line 45
    :cond_6
    :goto_1
    check-cast v0, Ljava/util/List;

    .line 50
    move-object v9, v0

    check-cast v9, Ljava/lang/Iterable;

    .line 193
    new-instance v10, Ljava/util/ArrayList;

    const/16 v11, 0xa

    invoke-static {v9, v11}, Lkotlin/collections/CollectionsKt;->collectionSizeOrDefault(Ljava/lang/Iterable;I)I

    move-result v11

    invoke-direct {v10, v11}, Ljava/util/ArrayList;-><init>(I)V

    check-cast v10, Ljava/util/Collection;

    .line 194
    invoke-interface {v9}, Ljava/lang/Iterable;->iterator()Ljava/util/Iterator;

    move-result-object v9

    :goto_2
    invoke-interface {v9}, Ljava/util/Iterator;->hasNext()Z

    move-result v11

    if-eqz v11, :cond_7

    invoke-interface {v9}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v11

    .line 195
    check-cast v11, Lcom/bachatas4/android/database/GameEntity;

    .line 50
    invoke-virtual {v11}, Lcom/bachatas4/android/database/GameEntity;->getId()Ljava/lang/String;

    move-result-object v11

    .line 195
    invoke-interface {v10, v11}, Ljava/util/Collection;->add(Ljava/lang/Object;)Z

    goto :goto_2

    .line 196
    :cond_7
    check-cast v10, Ljava/util/List;

    .line 193
    check-cast v10, Ljava/lang/Iterable;

    .line 50
    invoke-static {v10}, Lkotlin/collections/CollectionsKt;->toSet(Ljava/lang/Iterable;)Ljava/util/Set;

    move-result-object v9

    .line 51
    sget-object v10, Lcom/bachatas4/android/data/LibrarySync;->INSTANCE:Lcom/bachatas4/android/data/LibrarySync;

    .line 54
    sget-object v11, Lcom/bachatas4/android/data/ImportManager;->INSTANCE:Lcom/bachatas4/android/data/ImportManager;

    const/4 v12, 0x0

    invoke-static {v11, v12, v7, v12}, Lcom/bachatas4/android/data/ImportManager;->isBusy$default(Lcom/bachatas4/android/data/ImportManager;Lcom/bachatas4/android/data/ImportProgress;ILjava/lang/Object;)Z

    move-result v7

    .line 55
    iget-object v11, v1, Lcom/bachatas4/android/data/GameRepository;->context:Landroid/content/Context;

    invoke-virtual {v11}, Landroid/content/Context;->getFilesDir()Ljava/io/File;

    move-result-object v11

    invoke-static {v11, v8}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullExpressionValue(Ljava/lang/Object;Ljava/lang/String;)V

    .line 51
    invoke-virtual {v10, v4, v9, v7, v11}, Lcom/bachatas4/android/data/LibrarySync;->planSync(Ljava/io/File;Ljava/util/Set;ZLjava/io/File;)Lcom/bachatas4/android/data/LibrarySyncPlan;

    move-result-object v7

    .line 57
    sget-object v10, Lcom/bachatas4/android/data/LibrarySync;->INSTANCE:Lcom/bachatas4/android/data/LibrarySync;

    invoke-virtual {v10, v7}, Lcom/bachatas4/android/data/LibrarySync;->applyHeals(Lcom/bachatas4/android/data/LibrarySyncPlan;)V

    .line 58
    invoke-virtual {v7}, Lcom/bachatas4/android/data/LibrarySyncPlan;->getInserts()Ljava/util/List;

    move-result-object v10

    invoke-interface {v10}, Ljava/util/List;->iterator()Ljava/util/Iterator;

    move-result-object v10

    move-object v11, v4

    move-object v4, v10

    move-object v10, v0

    :cond_8
    :goto_3
    invoke-interface {v4}, Ljava/util/Iterator;->hasNext()Z

    move-result v0

    if-eqz v0, :cond_c

    invoke-interface {v4}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v0

    check-cast v0, Lcom/bachatas4/android/data/LibraryInsert;

    .line 60
    sget-object v12, Lcom/bachatas4/android/data/GameInstallVerifier;->INSTANCE:Lcom/bachatas4/android/data/GameInstallVerifier;

    iget-object v13, v1, Lcom/bachatas4/android/data/GameRepository;->context:Landroid/content/Context;

    invoke-virtual {v13}, Landroid/content/Context;->getFilesDir()Ljava/io/File;

    move-result-object v13

    invoke-static {v13, v8}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullExpressionValue(Ljava/lang/Object;Ljava/lang/String;)V

    invoke-virtual {v0}, Lcom/bachatas4/android/data/LibraryInsert;->getRelativePath()Ljava/lang/String;

    move-result-object v14

    invoke-virtual {v12, v13, v14}, Lcom/bachatas4/android/data/GameInstallVerifier;->canLaunch(Ljava/io/File;Ljava/lang/String;)Z

    move-result v12

    if-nez v12, :cond_9

    .line 61
    sget-object v12, Lcom/bachatas4/android/data/GameInstallVerifier;->INSTANCE:Lcom/bachatas4/android/data/GameInstallVerifier;

    .line 62
    new-instance v13, Ljava/io/File;

    iget-object v14, v1, Lcom/bachatas4/android/data/GameRepository;->context:Landroid/content/Context;

    invoke-virtual {v14}, Landroid/content/Context;->getFilesDir()Ljava/io/File;

    move-result-object v14

    invoke-virtual {v0}, Lcom/bachatas4/android/data/LibraryInsert;->getRelativePath()Ljava/lang/String;

    move-result-object v15

    invoke-direct {v13, v14, v15}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    .line 63
    invoke-virtual {v0}, Lcom/bachatas4/android/data/LibraryInsert;->getId()Ljava/lang/String;

    move-result-object v14

    .line 61
    invoke-virtual {v12, v13, v14}, Lcom/bachatas4/android/data/GameInstallVerifier;->verifyTreeForRegistration(Ljava/io/File;Ljava/lang/String;)Lcom/bachatas4/android/data/GameInstallVerifier$VerifyResult;

    move-result-object v12

    instance-of v12, v12, Lcom/bachatas4/android/data/GameInstallVerifier$VerifyResult$Ok;

    .line 68
    :cond_9
    sget-object v12, Lcom/bachatas4/android/data/GameInstallVerifier;->INSTANCE:Lcom/bachatas4/android/data/GameInstallVerifier;

    iget-object v13, v1, Lcom/bachatas4/android/data/GameRepository;->context:Landroid/content/Context;

    invoke-virtual {v13}, Landroid/content/Context;->getFilesDir()Ljava/io/File;

    move-result-object v13

    invoke-static {v13, v8}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullExpressionValue(Ljava/lang/Object;Ljava/lang/String;)V

    invoke-virtual {v0}, Lcom/bachatas4/android/data/LibraryInsert;->getRelativePath()Ljava/lang/String;

    move-result-object v14

    invoke-virtual {v12, v13, v14}, Lcom/bachatas4/android/data/GameInstallVerifier;->canLaunch(Ljava/io/File;Ljava/lang/String;)Z

    move-result v12

    if-nez v12, :cond_a

    .line 69
    sget-object v12, Lcom/bachatas4/android/data/GameInstallVerifier;->INSTANCE:Lcom/bachatas4/android/data/GameInstallVerifier;

    new-instance v13, Ljava/io/File;

    iget-object v14, v1, Lcom/bachatas4/android/data/GameRepository;->context:Landroid/content/Context;

    invoke-virtual {v14}, Landroid/content/Context;->getFilesDir()Ljava/io/File;

    move-result-object v14

    invoke-virtual {v0}, Lcom/bachatas4/android/data/LibraryInsert;->getRelativePath()Ljava/lang/String;

    move-result-object v15

    invoke-direct {v13, v14, v15}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    invoke-virtual {v12, v13}, Lcom/bachatas4/android/data/GameInstallVerifier;->requiredFilesPresent(Ljava/io/File;)Z

    move-result v12

    if-eqz v12, :cond_8

    .line 72
    :cond_a
    new-instance v12, Ljava/io/File;

    iget-object v13, v1, Lcom/bachatas4/android/data/GameRepository;->context:Landroid/content/Context;

    invoke-virtual {v13}, Landroid/content/Context;->getFilesDir()Ljava/io/File;

    move-result-object v13

    invoke-virtual {v0}, Lcom/bachatas4/android/data/LibraryInsert;->getRelativePath()Ljava/lang/String;

    move-result-object v14

    invoke-direct {v12, v13, v14}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    .line 73
    sget-object v13, Lcom/bachatas4/android/data/InstallManifestIo;->INSTANCE:Lcom/bachatas4/android/data/InstallManifestIo;

    invoke-virtual {v13, v12}, Lcom/bachatas4/android/data/InstallManifestIo;->read(Ljava/io/File;)Lcom/bachatas4/android/data/InstallManifest;

    move-result-object v13

    if-nez v13, :cond_b

    .line 74
    sget-object v13, Lcom/bachatas4/android/data/GameInstallVerifier;->INSTANCE:Lcom/bachatas4/android/data/GameInstallVerifier;

    invoke-virtual {v0}, Lcom/bachatas4/android/data/LibraryInsert;->getId()Ljava/lang/String;

    move-result-object v14

    invoke-virtual {v13, v12, v14}, Lcom/bachatas4/android/data/GameInstallVerifier;->verifyTreeForRegistration(Ljava/io/File;Ljava/lang/String;)Lcom/bachatas4/android/data/GameInstallVerifier$VerifyResult;

    move-result-object v13

    .line 75
    instance-of v14, v13, Lcom/bachatas4/android/data/GameInstallVerifier$VerifyResult$Ok;

    if-eqz v14, :cond_8

    .line 76
    sget-object v14, Lcom/bachatas4/android/data/InstallManifestIo;->INSTANCE:Lcom/bachatas4/android/data/InstallManifestIo;

    .line 78
    new-instance v15, Lcom/bachatas4/android/data/InstallManifest;

    .line 80
    invoke-virtual {v0}, Lcom/bachatas4/android/data/LibraryInsert;->getId()Ljava/lang/String;

    move-result-object v18

    .line 83
    invoke-virtual {v0}, Lcom/bachatas4/android/data/LibraryInsert;->getSourceUri()Ljava/lang/String;

    move-result-object v21

    .line 84
    invoke-static {}, Ljava/lang/System;->currentTimeMillis()J

    move-result-wide v22

    .line 85
    sget-object v16, Lcom/bachatas4/android/data/GameInstallVerifier;->INSTANCE:Lcom/bachatas4/android/data/GameInstallVerifier;

    invoke-virtual/range {v16 .. v16}, Lcom/bachatas4/android/data/GameInstallVerifier;->getREQUIRED_FILES()Ljava/util/List;

    move-result-object v24

    .line 86
    check-cast v13, Lcom/bachatas4/android/data/GameInstallVerifier$VerifyResult$Ok;

    invoke-virtual {v13}, Lcom/bachatas4/android/data/GameInstallVerifier$VerifyResult$Ok;->getBytesTotal()J

    move-result-wide v25

    const/16 v28, 0x201

    const/16 v29, 0x0

    const/16 v16, 0x0

    .line 78
    const-string v17, "INSTALLED"

    const/16 v19, 0x0

    const-string v20, "folder"

    const/16 v27, 0x0

    invoke-direct/range {v15 .. v29}, Lcom/bachatas4/android/data/InstallManifest;-><init>(ILjava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;JLjava/util/List;JLjava/util/List;ILkotlin/jvm/internal/DefaultConstructorMarker;)V

    .line 76
    invoke-virtual {v14, v12, v15}, Lcom/bachatas4/android/data/InstallManifestIo;->write(Ljava/io/File;Lcom/bachatas4/android/data/InstallManifest;)V

    .line 93
    :cond_b
    invoke-virtual {v0}, Lcom/bachatas4/android/data/LibraryInsert;->getId()Ljava/lang/String;

    move-result-object v13

    invoke-interface {v9, v13}, Ljava/util/Set;->contains(Ljava/lang/Object;)Z

    move-result v13

    if-nez v13, :cond_8

    .line 94
    iget-object v13, v1, Lcom/bachatas4/android/data/GameRepository;->gameDao:Lcom/bachatas4/android/database/GameDao;

    .line 95
    new-instance v14, Lcom/bachatas4/android/database/GameEntity;

    .line 96
    invoke-virtual {v0}, Lcom/bachatas4/android/data/LibraryInsert;->getId()Ljava/lang/String;

    move-result-object v15

    .line 97
    invoke-virtual {v0}, Lcom/bachatas4/android/data/LibraryInsert;->getTitle()Ljava/lang/String;

    move-result-object v16

    .line 98
    invoke-virtual {v0}, Lcom/bachatas4/android/data/LibraryInsert;->getRelativePath()Ljava/lang/String;

    move-result-object v17

    .line 99
    invoke-virtual {v0}, Lcom/bachatas4/android/data/LibraryInsert;->getSourceUri()Ljava/lang/String;

    move-result-object v18

    .line 100
    invoke-static {}, Ljava/lang/System;->currentTimeMillis()J

    move-result-wide v19

    .line 101
    invoke-virtual {v0}, Lcom/bachatas4/android/data/LibraryInsert;->getSubtitle()Ljava/lang/String;

    move-result-object v21

    .line 102
    invoke-virtual {v0}, Lcom/bachatas4/android/data/LibraryInsert;->getDetail()Ljava/lang/String;

    move-result-object v22

    const-wide/16 v23, 0x0

    .line 95
    invoke-direct/range {v14 .. v24}, Lcom/bachatas4/android/database/GameEntity;-><init>(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;JLjava/lang/String;Ljava/lang/String;J)V

    .line 94
    iput-object v11, v2, Lcom/bachatas4/android/data/GameRepository$syncLibrary$1;->L$0:Ljava/lang/Object;

    invoke-static {v10}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v15

    iput-object v15, v2, Lcom/bachatas4/android/data/GameRepository$syncLibrary$1;->L$1:Ljava/lang/Object;

    iput-object v9, v2, Lcom/bachatas4/android/data/GameRepository$syncLibrary$1;->L$2:Ljava/lang/Object;

    iput-object v7, v2, Lcom/bachatas4/android/data/GameRepository$syncLibrary$1;->L$3:Ljava/lang/Object;

    iput-object v4, v2, Lcom/bachatas4/android/data/GameRepository$syncLibrary$1;->L$4:Ljava/lang/Object;

    invoke-static {v0}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v0

    iput-object v0, v2, Lcom/bachatas4/android/data/GameRepository$syncLibrary$1;->L$5:Ljava/lang/Object;

    invoke-static {v12}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v0

    iput-object v0, v2, Lcom/bachatas4/android/data/GameRepository$syncLibrary$1;->L$6:Ljava/lang/Object;

    iput v6, v2, Lcom/bachatas4/android/data/GameRepository$syncLibrary$1;->label:I

    invoke-interface {v13, v14, v2}, Lcom/bachatas4/android/database/GameDao;->insert(Lcom/bachatas4/android/database/GameEntity;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;

    move-result-object v0

    if-ne v0, v3, :cond_8

    goto/16 :goto_5

    .line 109
    :cond_c
    invoke-virtual {v7}, Lcom/bachatas4/android/data/LibrarySyncPlan;->getDbIdsToDrop()Ljava/util/List;

    move-result-object v0

    invoke-interface {v0}, Ljava/util/List;->iterator()Ljava/util/Iterator;

    move-result-object v0

    move-object v4, v0

    move-object v6, v7

    move-object v7, v9

    move-object v9, v10

    move-object v10, v11

    :cond_d
    :goto_4
    invoke-interface {v4}, Ljava/util/Iterator;->hasNext()Z

    move-result v0

    if-eqz v0, :cond_11

    invoke-interface {v4}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v0

    check-cast v0, Ljava/lang/String;

    .line 111
    new-instance v11, Ljava/io/File;

    invoke-direct {v11, v10, v0}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    .line 112
    invoke-virtual {v11}, Ljava/io/File;->isDirectory()Z

    move-result v12

    if-eqz v12, :cond_e

    sget-object v12, Lcom/bachatas4/android/data/GameInstallVerifier;->INSTANCE:Lcom/bachatas4/android/data/GameInstallVerifier;

    iget-object v13, v1, Lcom/bachatas4/android/data/GameRepository;->context:Landroid/content/Context;

    invoke-virtual {v13}, Landroid/content/Context;->getFilesDir()Ljava/io/File;

    move-result-object v13

    invoke-static {v13, v8}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullExpressionValue(Ljava/lang/Object;Ljava/lang/String;)V

    new-instance v14, Ljava/lang/StringBuilder;

    const-string v15, "games/"

    invoke-direct {v14, v15}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v14, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v14

    invoke-virtual {v14}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v14

    invoke-virtual {v12, v13, v14}, Lcom/bachatas4/android/data/GameInstallVerifier;->canLaunch(Ljava/io/File;Ljava/lang/String;)Z

    move-result v12

    if-nez v12, :cond_d

    .line 113
    :cond_e
    invoke-virtual {v11}, Ljava/io/File;->isDirectory()Z

    move-result v12

    if-eqz v12, :cond_f

    .line 114
    sget-object v12, Lcom/bachatas4/android/data/GameInstallVerifier;->INSTANCE:Lcom/bachatas4/android/data/GameInstallVerifier;

    invoke-virtual {v12, v11, v0}, Lcom/bachatas4/android/data/GameInstallVerifier;->verifyTreeForRegistration(Ljava/io/File;Ljava/lang/String;)Lcom/bachatas4/android/data/GameInstallVerifier$VerifyResult;

    move-result-object v12

    instance-of v12, v12, Lcom/bachatas4/android/data/GameInstallVerifier$VerifyResult$Fail;

    if-eqz v12, :cond_d

    .line 117
    :cond_f
    :try_start_1
    sget-object v12, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    move-object v12, v1

    check-cast v12, Lcom/bachatas4/android/data/GameRepository;

    iget-object v12, v1, Lcom/bachatas4/android/data/GameRepository;->gameDao:Lcom/bachatas4/android/database/GameDao;

    iput-object v10, v2, Lcom/bachatas4/android/data/GameRepository$syncLibrary$1;->L$0:Ljava/lang/Object;

    invoke-static {v9}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v13

    iput-object v13, v2, Lcom/bachatas4/android/data/GameRepository$syncLibrary$1;->L$1:Ljava/lang/Object;

    invoke-static {v7}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v13

    iput-object v13, v2, Lcom/bachatas4/android/data/GameRepository$syncLibrary$1;->L$2:Ljava/lang/Object;

    invoke-static {v6}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v13

    iput-object v13, v2, Lcom/bachatas4/android/data/GameRepository$syncLibrary$1;->L$3:Ljava/lang/Object;

    iput-object v4, v2, Lcom/bachatas4/android/data/GameRepository$syncLibrary$1;->L$4:Ljava/lang/Object;

    invoke-static {v0}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v13

    iput-object v13, v2, Lcom/bachatas4/android/data/GameRepository$syncLibrary$1;->L$5:Ljava/lang/Object;

    invoke-static {v11}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v11

    iput-object v11, v2, Lcom/bachatas4/android/data/GameRepository$syncLibrary$1;->L$6:Ljava/lang/Object;

    invoke-static {v1}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v11

    iput-object v11, v2, Lcom/bachatas4/android/data/GameRepository$syncLibrary$1;->L$7:Ljava/lang/Object;

    iput v5, v2, Lcom/bachatas4/android/data/GameRepository$syncLibrary$1;->label:I

    invoke-interface {v12, v0, v2}, Lcom/bachatas4/android/database/GameDao;->deleteById(Ljava/lang/String;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;

    move-result-object v0

    if-ne v0, v3, :cond_10

    :goto_5
    return-object v3

    :cond_10
    :goto_6
    check-cast v0, Ljava/lang/Number;

    invoke-virtual {v0}, Ljava/lang/Number;->intValue()I

    move-result v0

    invoke-static {v0}, Lkotlin/coroutines/jvm/internal/Boxing;->boxInt(I)Ljava/lang/Integer;

    move-result-object v0

    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;
    :try_end_1
    .catchall {:try_start_1 .. :try_end_1} :catchall_0

    goto/16 :goto_4

    :goto_7
    sget-object v11, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    invoke-static {v0}, Lkotlin/ResultKt;->createFailure(Ljava/lang/Throwable;)Ljava/lang/Object;

    move-result-object v0

    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;

    goto/16 :goto_4

    .line 121
    :cond_11
    sget-object v0, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;

    return-object v0
.end method

.method public final syncOrphanedFolders(Lkotlin/coroutines/Continuation;)Ljava/lang/Object;
    .locals 0
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "(",
            "Lkotlin/coroutines/Continuation<",
            "-",
            "Lkotlin/Unit;",
            ">;)",
            "Ljava/lang/Object;"
        }
    .end annotation

    .line 124
    invoke-virtual {p0, p1}, Lcom/bachatas4/android/data/GameRepository;->syncLibrary(Lkotlin/coroutines/Continuation;)Ljava/lang/Object;

    move-result-object p0

    return-object p0
.end method

.method public final touchGame(Ljava/lang/String;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;
    .locals 11
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "(",
            "Ljava/lang/String;",
            "Lkotlin/coroutines/Continuation<",
            "-",
            "Lkotlin/Unit;",
            ">;)",
            "Ljava/lang/Object;"
        }
    .end annotation

    instance-of v0, p2, Lcom/bachatas4/android/data/GameRepository$touchGame$1;

    if-eqz v0, :cond_0

    move-object v0, p2

    check-cast v0, Lcom/bachatas4/android/data/GameRepository$touchGame$1;

    iget v1, v0, Lcom/bachatas4/android/data/GameRepository$touchGame$1;->label:I

    const/high16 v2, -0x80000000

    and-int/2addr v1, v2

    if-eqz v1, :cond_0

    iget p2, v0, Lcom/bachatas4/android/data/GameRepository$touchGame$1;->label:I

    sub-int/2addr p2, v2

    iput p2, v0, Lcom/bachatas4/android/data/GameRepository$touchGame$1;->label:I

    goto :goto_0

    :cond_0
    new-instance v0, Lcom/bachatas4/android/data/GameRepository$touchGame$1;

    invoke-direct {v0, p0, p2}, Lcom/bachatas4/android/data/GameRepository$touchGame$1;-><init>(Lcom/bachatas4/android/data/GameRepository;Lkotlin/coroutines/Continuation;)V

    :goto_0
    move-object v8, v0

    iget-object p2, v8, Lcom/bachatas4/android/data/GameRepository$touchGame$1;->result:Ljava/lang/Object;

    invoke-static {}, Lkotlin/coroutines/intrinsics/IntrinsicsKt;->getCOROUTINE_SUSPENDED()Ljava/lang/Object;

    move-result-object v9

    .line 153
    iget v0, v8, Lcom/bachatas4/android/data/GameRepository$touchGame$1;->label:I

    const/4 v1, 0x2

    const/4 v2, 0x1

    if-eqz v0, :cond_3

    if-eq v0, v2, :cond_2

    if-ne v0, v1, :cond_1

    iget-object p0, v8, Lcom/bachatas4/android/data/GameRepository$touchGame$1;->L$3:Ljava/lang/Object;

    check-cast p0, Lcom/bachatas4/android/data/ParamSfoMetadata;

    iget-object p0, v8, Lcom/bachatas4/android/data/GameRepository$touchGame$1;->L$2:Ljava/lang/Object;

    check-cast p0, Ljava/io/File;

    iget-object p0, v8, Lcom/bachatas4/android/data/GameRepository$touchGame$1;->L$1:Ljava/lang/Object;

    check-cast p0, Lcom/bachatas4/android/database/GameEntity;

    iget-object p0, v8, Lcom/bachatas4/android/data/GameRepository$touchGame$1;->L$0:Ljava/lang/Object;

    check-cast p0, Ljava/lang/String;

    invoke-static {p2}, Lkotlin/ResultKt;->throwOnFailure(Ljava/lang/Object;)V

    goto/16 :goto_5

    :cond_1
    new-instance p0, Ljava/lang/IllegalStateException;

    const-string p1, "call to \'resume\' before \'invoke\' with coroutine"

    invoke-direct {p0, p1}, Ljava/lang/IllegalStateException;-><init>(Ljava/lang/String;)V

    throw p0

    :cond_2
    iget-object p1, v8, Lcom/bachatas4/android/data/GameRepository$touchGame$1;->L$0:Ljava/lang/Object;

    check-cast p1, Ljava/lang/String;

    invoke-static {p2}, Lkotlin/ResultKt;->throwOnFailure(Ljava/lang/Object;)V

    goto :goto_1

    :cond_3
    invoke-static {p2}, Lkotlin/ResultKt;->throwOnFailure(Ljava/lang/Object;)V

    .line 154
    iget-object p2, p0, Lcom/bachatas4/android/data/GameRepository;->gameDao:Lcom/bachatas4/android/database/GameDao;

    iput-object p1, v8, Lcom/bachatas4/android/data/GameRepository$touchGame$1;->L$0:Ljava/lang/Object;

    iput v2, v8, Lcom/bachatas4/android/data/GameRepository$touchGame$1;->label:I

    invoke-interface {p2, p1, v8}, Lcom/bachatas4/android/database/GameDao;->getById(Ljava/lang/String;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;

    move-result-object p2

    if-ne p2, v9, :cond_4

    goto/16 :goto_4

    :cond_4
    :goto_1
    move-object v2, p1

    check-cast p2, Lcom/bachatas4/android/database/GameEntity;

    if-nez p2, :cond_5

    sget-object p0, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;

    return-object p0

    .line 155
    :cond_5
    sget-object p1, Lcom/bachatas4/android/data/GameIconPaths;->INSTANCE:Lcom/bachatas4/android/data/GameIconPaths;

    iget-object v0, p0, Lcom/bachatas4/android/data/GameRepository;->context:Landroid/content/Context;

    invoke-virtual {v0}, Landroid/content/Context;->getFilesDir()Ljava/io/File;

    move-result-object v0

    const-string v3, "getFilesDir(...)"

    invoke-static {v0, v3}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullExpressionValue(Ljava/lang/Object;Ljava/lang/String;)V

    invoke-virtual {p2}, Lcom/bachatas4/android/database/GameEntity;->getRelativePath()Ljava/lang/String;

    move-result-object v3

    invoke-virtual {p1, v0, v3}, Lcom/bachatas4/android/data/GameIconPaths;->paramSfo(Ljava/io/File;Ljava/lang/String;)Ljava/io/File;

    move-result-object p1

    .line 156
    invoke-virtual {p1}, Ljava/io/File;->isFile()Z

    move-result v0

    const/4 v3, 0x0

    if-eqz v0, :cond_7

    .line 157
    :try_start_0
    sget-object v0, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    move-object v0, p0

    check-cast v0, Lcom/bachatas4/android/data/GameRepository;

    sget-object v0, Lcom/bachatas4/android/data/ParamSfoReader;->INSTANCE:Lcom/bachatas4/android/data/ParamSfoReader;

    invoke-static {p1}, Lkotlin/io/FilesKt;->readBytes(Ljava/io/File;)[B

    move-result-object v4

    invoke-virtual {v0, v4}, Lcom/bachatas4/android/data/ParamSfoReader;->parse([B)Lcom/bachatas4/android/data/ParamSfoMetadata;

    move-result-object v0

    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v0
    :try_end_0
    .catchall {:try_start_0 .. :try_end_0} :catchall_0

    goto :goto_2

    :catchall_0
    move-exception v0

    sget-object v4, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    invoke-static {v0}, Lkotlin/ResultKt;->createFailure(Ljava/lang/Throwable;)Ljava/lang/Object;

    move-result-object v0

    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v0

    :goto_2
    invoke-static {v0}, Lkotlin/Result;->isFailure-impl(Ljava/lang/Object;)Z

    move-result v4

    if-eqz v4, :cond_6

    move-object v0, v3

    :cond_6
    check-cast v0, Lcom/bachatas4/android/data/ParamSfoMetadata;

    goto :goto_3

    :cond_7
    move-object v0, v3

    .line 159
    :goto_3
    iget-object p0, p0, Lcom/bachatas4/android/data/GameRepository;->gameDao:Lcom/bachatas4/android/database/GameDao;

    if-eqz v0, :cond_9

    .line 161
    invoke-virtual {v0}, Lcom/bachatas4/android/data/ParamSfoMetadata;->getTitle()Ljava/lang/String;

    move-result-object v4

    if-eqz v4, :cond_9

    move-object v5, v4

    check-cast v5, Ljava/lang/CharSequence;

    invoke-static {v5}, Lkotlin/text/StringsKt;->isBlank(Ljava/lang/CharSequence;)Z

    move-result v5

    if-nez v5, :cond_8

    move-object v3, v4

    :cond_8
    if-nez v3, :cond_a

    :cond_9
    invoke-virtual {p2}, Lcom/bachatas4/android/database/GameEntity;->getTitle()Ljava/lang/String;

    move-result-object v3

    :cond_a
    if-eqz v0, :cond_b

    .line 162
    invoke-virtual {v0}, Lcom/bachatas4/android/data/ParamSfoMetadata;->getSubtitle()Ljava/lang/String;

    move-result-object v4

    if-nez v4, :cond_c

    :cond_b
    invoke-virtual {p2}, Lcom/bachatas4/android/database/GameEntity;->getSubtitle()Ljava/lang/String;

    move-result-object v4

    :cond_c
    if-eqz v0, :cond_d

    .line 163
    invoke-virtual {v0}, Lcom/bachatas4/android/data/ParamSfoMetadata;->getDetail()Ljava/lang/String;

    move-result-object v5

    if-nez v5, :cond_e

    :cond_d
    invoke-virtual {p2}, Lcom/bachatas4/android/database/GameEntity;->getDetail()Ljava/lang/String;

    move-result-object v5

    .line 164
    :cond_e
    invoke-static {}, Ljava/lang/System;->currentTimeMillis()J

    move-result-wide v6

    .line 159
    invoke-static {v2}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v10

    iput-object v10, v8, Lcom/bachatas4/android/data/GameRepository$touchGame$1;->L$0:Ljava/lang/Object;

    invoke-static {p2}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object p2

    iput-object p2, v8, Lcom/bachatas4/android/data/GameRepository$touchGame$1;->L$1:Ljava/lang/Object;

    invoke-static {p1}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object p1

    iput-object p1, v8, Lcom/bachatas4/android/data/GameRepository$touchGame$1;->L$2:Ljava/lang/Object;

    invoke-static {v0}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object p1

    iput-object p1, v8, Lcom/bachatas4/android/data/GameRepository$touchGame$1;->L$3:Ljava/lang/Object;

    iput v1, v8, Lcom/bachatas4/android/data/GameRepository$touchGame$1;->label:I

    move-object v1, p0

    invoke-interface/range {v1 .. v8}, Lcom/bachatas4/android/database/GameDao;->updateMetadata(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;JLkotlin/coroutines/Continuation;)Ljava/lang/Object;

    move-result-object p0

    if-ne p0, v9, :cond_f

    :goto_4
    return-object v9

    .line 166
    :cond_f
    :goto_5
    sget-object p0, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;

    return-object p0
.end method

.method public final updateLastLaunched(Ljava/lang/String;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;
    .locals 6
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "(",
            "Ljava/lang/String;",
            "Lkotlin/coroutines/Continuation<",
            "-",
            "Lkotlin/Unit;",
            ">;)",
            "Ljava/lang/Object;"
        }
    .end annotation

    instance-of v0, p2, Lcom/bachatas4/android/data/GameRepository$updateLastLaunched$1;

    if-eqz v0, :cond_0

    move-object v0, p2

    check-cast v0, Lcom/bachatas4/android/data/GameRepository$updateLastLaunched$1;

    iget v1, v0, Lcom/bachatas4/android/data/GameRepository$updateLastLaunched$1;->label:I

    const/high16 v2, -0x80000000

    and-int/2addr v1, v2

    if-eqz v1, :cond_0

    iget p2, v0, Lcom/bachatas4/android/data/GameRepository$updateLastLaunched$1;->label:I

    sub-int/2addr p2, v2

    iput p2, v0, Lcom/bachatas4/android/data/GameRepository$updateLastLaunched$1;->label:I

    goto :goto_0

    :cond_0
    new-instance v0, Lcom/bachatas4/android/data/GameRepository$updateLastLaunched$1;

    invoke-direct {v0, p0, p2}, Lcom/bachatas4/android/data/GameRepository$updateLastLaunched$1;-><init>(Lcom/bachatas4/android/data/GameRepository;Lkotlin/coroutines/Continuation;)V

    :goto_0
    iget-object p2, v0, Lcom/bachatas4/android/data/GameRepository$updateLastLaunched$1;->result:Ljava/lang/Object;

    invoke-static {}, Lkotlin/coroutines/intrinsics/IntrinsicsKt;->getCOROUTINE_SUSPENDED()Ljava/lang/Object;

    move-result-object v1

    .line 145
    iget v2, v0, Lcom/bachatas4/android/data/GameRepository$updateLastLaunched$1;->label:I

    const/4 v3, 0x1

    if-eqz v2, :cond_2

    if-ne v2, v3, :cond_1

    iget-object p0, v0, Lcom/bachatas4/android/data/GameRepository$updateLastLaunched$1;->L$0:Ljava/lang/Object;

    check-cast p0, Ljava/lang/String;

    invoke-static {p2}, Lkotlin/ResultKt;->throwOnFailure(Ljava/lang/Object;)V

    goto :goto_1

    :cond_1
    new-instance p0, Ljava/lang/IllegalStateException;

    const-string p1, "call to \'resume\' before \'invoke\' with coroutine"

    invoke-direct {p0, p1}, Ljava/lang/IllegalStateException;-><init>(Ljava/lang/String;)V

    throw p0

    :cond_2
    invoke-static {p2}, Lkotlin/ResultKt;->throwOnFailure(Ljava/lang/Object;)V

    .line 146
    iget-object p0, p0, Lcom/bachatas4/android/data/GameRepository;->gameDao:Lcom/bachatas4/android/database/GameDao;

    invoke-static {}, Ljava/lang/System;->currentTimeMillis()J

    move-result-wide v4

    invoke-static {p1}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object p2

    iput-object p2, v0, Lcom/bachatas4/android/data/GameRepository$updateLastLaunched$1;->L$0:Ljava/lang/Object;

    iput v3, v0, Lcom/bachatas4/android/data/GameRepository$updateLastLaunched$1;->label:I

    invoke-interface {p0, p1, v4, v5, v0}, Lcom/bachatas4/android/database/GameDao;->updateLastLaunched(Ljava/lang/String;JLkotlin/coroutines/Continuation;)Ljava/lang/Object;

    move-result-object p0

    if-ne p0, v1, :cond_3

    return-object v1

    .line 147
    :cond_3
    :goto_1
    sget-object p0, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;

    return-object p0
.end method
