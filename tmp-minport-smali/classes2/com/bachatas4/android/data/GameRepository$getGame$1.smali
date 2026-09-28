.class final Lcom/bachatas4/android/data/GameRepository$getGame$1;
.super Lkotlin/coroutines/jvm/internal/ContinuationImpl;
.source "GameRepository.kt"


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lcom/bachatas4/android/data/GameRepository;->getGame(Ljava/lang/String;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x18
    name = null
.end annotation

.annotation runtime Lkotlin/Metadata;
    k = 0x3
    mv = {
        0x2,
        0x4,
        0x0
    }
    xi = 0x30
.end annotation

.annotation runtime Lkotlin/coroutines/jvm/internal/DebugMetadata;
    c = "com.bachatas4.android.data.GameRepository"
    f = "GameRepository.kt"
    i = {
        0x0
    }
    l = {
        0x14
    }
    m = "getGame"
    n = {
        "id"
    }
    nl = {
        -0x1
    }
    s = {
        "L$0"
    }
    v = 0x2
.end annotation


# instance fields
.field L$0:Ljava/lang/Object;

.field label:I

.field synthetic result:Ljava/lang/Object;

.field final synthetic this$0:Lcom/bachatas4/android/data/GameRepository;


# direct methods
.method constructor <init>(Lcom/bachatas4/android/data/GameRepository;Lkotlin/coroutines/Continuation;)V
    .locals 0
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "(",
            "Lcom/bachatas4/android/data/GameRepository;",
            "Lkotlin/coroutines/Continuation<",
            "-",
            "Lcom/bachatas4/android/data/GameRepository$getGame$1;",
            ">;)V"
        }
    .end annotation

    iput-object p1, p0, Lcom/bachatas4/android/data/GameRepository$getGame$1;->this$0:Lcom/bachatas4/android/data/GameRepository;

    invoke-direct {p0, p2}, Lkotlin/coroutines/jvm/internal/ContinuationImpl;-><init>(Lkotlin/coroutines/Continuation;)V

    return-void
.end method


# virtual methods
.method public final invokeSuspend(Ljava/lang/Object;)Ljava/lang/Object;
    .locals 1

    iput-object p1, p0, Lcom/bachatas4/android/data/GameRepository$getGame$1;->result:Ljava/lang/Object;

    iget p1, p0, Lcom/bachatas4/android/data/GameRepository$getGame$1;->label:I

    const/high16 v0, -0x80000000

    or-int/2addr p1, v0

    iput p1, p0, Lcom/bachatas4/android/data/GameRepository$getGame$1;->label:I

    iget-object p1, p0, Lcom/bachatas4/android/data/GameRepository$getGame$1;->this$0:Lcom/bachatas4/android/data/GameRepository;

    const/4 v0, 0x0

    check-cast p0, Lkotlin/coroutines/Continuation;

    invoke-virtual {p1, v0, p0}, Lcom/bachatas4/android/data/GameRepository;->getGame(Ljava/lang/String;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;

    move-result-object p0

    return-object p0
.end method
