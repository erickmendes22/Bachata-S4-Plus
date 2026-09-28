.class public final synthetic Lcom/bachatas4/android/service/ImportService$$ExternalSyntheticLambda0;
.super Ljava/lang/Object;
.source "D8$$SyntheticClass"

# interfaces
.implements Lcom/bachatas4/android/runtime/pkg/PkgProgressListener;


# instance fields
.field public final synthetic f$0:Lkotlin/jvm/internal/Ref$LongRef;

.field public final synthetic f$1:Ljava/lang/String;

.field public final synthetic f$2:Lcom/bachatas4/android/service/ImportService;

.field public final synthetic f$3:Lkotlin/jvm/internal/Ref$LongRef;


# direct methods
.method public synthetic constructor <init>(Lkotlin/jvm/internal/Ref$LongRef;Ljava/lang/String;Lcom/bachatas4/android/service/ImportService;Lkotlin/jvm/internal/Ref$LongRef;)V
    .locals 0

    .line 0
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    iput-object p1, p0, Lcom/bachatas4/android/service/ImportService$$ExternalSyntheticLambda0;->f$0:Lkotlin/jvm/internal/Ref$LongRef;

    iput-object p2, p0, Lcom/bachatas4/android/service/ImportService$$ExternalSyntheticLambda0;->f$1:Ljava/lang/String;

    iput-object p3, p0, Lcom/bachatas4/android/service/ImportService$$ExternalSyntheticLambda0;->f$2:Lcom/bachatas4/android/service/ImportService;

    iput-object p4, p0, Lcom/bachatas4/android/service/ImportService$$ExternalSyntheticLambda0;->f$3:Lkotlin/jvm/internal/Ref$LongRef;

    return-void
.end method


# virtual methods
.method public final onProgress(JJLjava/lang/String;)V
    .locals 9

    .line 0
    iget-object v0, p0, Lcom/bachatas4/android/service/ImportService$$ExternalSyntheticLambda0;->f$0:Lkotlin/jvm/internal/Ref$LongRef;

    iget-object v1, p0, Lcom/bachatas4/android/service/ImportService$$ExternalSyntheticLambda0;->f$1:Ljava/lang/String;

    iget-object v2, p0, Lcom/bachatas4/android/service/ImportService$$ExternalSyntheticLambda0;->f$2:Lcom/bachatas4/android/service/ImportService;

    iget-object v3, p0, Lcom/bachatas4/android/service/ImportService$$ExternalSyntheticLambda0;->f$3:Lkotlin/jvm/internal/Ref$LongRef;

    move-wide v4, p1

    move-wide v6, p3

    move-object v8, p5

    invoke-static/range {v0 .. v8}, Lcom/bachatas4/android/service/ImportService;->extractWithProgress$lambda$0(Lkotlin/jvm/internal/Ref$LongRef;Ljava/lang/String;Lcom/bachatas4/android/service/ImportService;Lkotlin/jvm/internal/Ref$LongRef;JJLjava/lang/String;)V

    return-void
.end method
