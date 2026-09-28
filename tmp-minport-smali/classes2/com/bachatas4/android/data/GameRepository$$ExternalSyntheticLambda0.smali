.class public final synthetic Lcom/bachatas4/android/data/GameRepository$$ExternalSyntheticLambda0;
.super Ljava/lang/Object;
.source "D8$$SyntheticClass"

# interfaces
.implements Lkotlin/jvm/functions/Function1;


# instance fields
.field public final synthetic f$0:Ljava/util/Map;

.field public final synthetic f$1:Lcom/bachatas4/android/data/GameRepository;


# direct methods
.method public synthetic constructor <init>(Ljava/util/Map;Lcom/bachatas4/android/data/GameRepository;)V
    .locals 0

    .line 0
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    iput-object p1, p0, Lcom/bachatas4/android/data/GameRepository$$ExternalSyntheticLambda0;->f$0:Ljava/util/Map;

    iput-object p2, p0, Lcom/bachatas4/android/data/GameRepository$$ExternalSyntheticLambda0;->f$1:Lcom/bachatas4/android/data/GameRepository;

    return-void
.end method


# virtual methods
.method public final invoke(Ljava/lang/Object;)Ljava/lang/Object;
    .locals 1

    .line 0
    iget-object v0, p0, Lcom/bachatas4/android/data/GameRepository$$ExternalSyntheticLambda0;->f$0:Ljava/util/Map;

    iget-object p0, p0, Lcom/bachatas4/android/data/GameRepository$$ExternalSyntheticLambda0;->f$1:Lcom/bachatas4/android/data/GameRepository;

    check-cast p1, Ljava/lang/String;

    invoke-static {v0, p0, p1}, Lcom/bachatas4/android/data/GameRepository;->backfillTitlesFromSfo$lambda$2(Ljava/util/Map;Lcom/bachatas4/android/data/GameRepository;Ljava/lang/String;)Ljava/lang/String;

    move-result-object p0

    return-object p0
.end method
