.class public final synthetic Lcom/bachatas4/android/service/ImportService$$ExternalSyntheticLambda1;
.super Ljava/lang/Object;
.source "D8$$SyntheticClass"

# interfaces
.implements Lkotlin/jvm/functions/Function3;


# instance fields
.field public final synthetic f$0:Lcom/bachatas4/android/data/ResolvedGameMetadata;

.field public final synthetic f$1:Lcom/bachatas4/android/service/ImportService;


# direct methods
.method public synthetic constructor <init>(Lcom/bachatas4/android/data/ResolvedGameMetadata;Lcom/bachatas4/android/service/ImportService;)V
    .locals 0

    .line 0
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    iput-object p1, p0, Lcom/bachatas4/android/service/ImportService$$ExternalSyntheticLambda1;->f$0:Lcom/bachatas4/android/data/ResolvedGameMetadata;

    iput-object p2, p0, Lcom/bachatas4/android/service/ImportService$$ExternalSyntheticLambda1;->f$1:Lcom/bachatas4/android/service/ImportService;

    return-void
.end method


# virtual methods
.method public final invoke(Ljava/lang/Object;Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;
    .locals 7

    .line 0
    iget-object v0, p0, Lcom/bachatas4/android/service/ImportService$$ExternalSyntheticLambda1;->f$0:Lcom/bachatas4/android/data/ResolvedGameMetadata;

    iget-object v1, p0, Lcom/bachatas4/android/service/ImportService$$ExternalSyntheticLambda1;->f$1:Lcom/bachatas4/android/service/ImportService;

    check-cast p1, Ljava/lang/Long;

    invoke-virtual {p1}, Ljava/lang/Long;->longValue()J

    move-result-wide v2

    check-cast p2, Ljava/lang/Long;

    invoke-virtual {p2}, Ljava/lang/Long;->longValue()J

    move-result-wide v4

    move-object v6, p3

    check-cast v6, Ljava/lang/String;

    invoke-static/range {v0 .. v6}, Lcom/bachatas4/android/service/ImportService;->runFolderImport$lambda$8(Lcom/bachatas4/android/data/ResolvedGameMetadata;Lcom/bachatas4/android/service/ImportService;JJLjava/lang/String;)Lkotlin/Unit;

    move-result-object p0

    return-object p0
.end method
