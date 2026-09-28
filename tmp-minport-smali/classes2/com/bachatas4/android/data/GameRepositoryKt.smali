.class public final Lcom/bachatas4/android/data/GameRepositoryKt;
.super Ljava/lang/Object;
.source "GameRepository.kt"


# annotations
.annotation runtime Lkotlin/Metadata;
    d1 = {
        "\u0000\u000c\n\u0000\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\u001a\u000c\u0010\u0000\u001a\u00020\u0001*\u00020\u0002H\u0002\u00a8\u0006\u0003"
    }
    d2 = {
        "toModel",
        "Lcom/bachatas4/android/model/Game;",
        "Lcom/bachatas4/android/database/GameEntity;",
        "data"
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
.method public static final synthetic access$toModel(Lcom/bachatas4/android/database/GameEntity;)Lcom/bachatas4/android/model/Game;
    .locals 0

    .line 1
    invoke-static {p0}, Lcom/bachatas4/android/data/GameRepositoryKt;->toModel(Lcom/bachatas4/android/database/GameEntity;)Lcom/bachatas4/android/model/Game;

    move-result-object p0

    return-object p0
.end method

.method private static final toModel(Lcom/bachatas4/android/database/GameEntity;)Lcom/bachatas4/android/model/Game;
    .locals 8

    .line 179
    new-instance v0, Lcom/bachatas4/android/model/Game;

    .line 180
    invoke-virtual {p0}, Lcom/bachatas4/android/database/GameEntity;->getId()Ljava/lang/String;

    move-result-object v1

    .line 181
    invoke-virtual {p0}, Lcom/bachatas4/android/database/GameEntity;->getTitle()Ljava/lang/String;

    move-result-object v2

    .line 182
    invoke-virtual {p0}, Lcom/bachatas4/android/database/GameEntity;->getRelativePath()Ljava/lang/String;

    move-result-object v3

    .line 183
    invoke-virtual {p0}, Lcom/bachatas4/android/database/GameEntity;->getSubtitle()Ljava/lang/String;

    move-result-object v4

    .line 184
    invoke-virtual {p0}, Lcom/bachatas4/android/database/GameEntity;->getDetail()Ljava/lang/String;

    move-result-object v5

    .line 185
    invoke-virtual {p0}, Lcom/bachatas4/android/database/GameEntity;->getLastLaunchedAtMs()J

    move-result-wide v6

    .line 179
    invoke-direct/range {v0 .. v7}, Lcom/bachatas4/android/model/Game;-><init>(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;J)V

    return-object v0
.end method
