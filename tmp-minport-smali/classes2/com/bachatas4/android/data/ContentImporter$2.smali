.class final synthetic Lcom/bachatas4/android/data/ContentImporter$2;
.super Lkotlin/jvm/internal/FunctionReferenceImpl;
.source "ContentImporter.kt"

# interfaces
.implements Lkotlin/jvm/functions/Function1;


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lcom/bachatas4/android/data/ContentImporter;-><init>(Ljava/io/File;Lcom/bachatas4/android/data/ImportSource;Lkotlin/jvm/functions/Function0;Lkotlin/jvm/functions/Function1;ILkotlin/jvm/internal/DefaultConstructorMarker;)V
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x1018
    name = null
.end annotation

.annotation system Ldalvik/annotation/Signature;
    value = {
        "Lkotlin/jvm/internal/FunctionReferenceImpl;",
        "Lkotlin/jvm/functions/Function1<",
        "Ljava/io/File;",
        "Ljava/lang/Long;",
        ">;"
    }
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


# static fields
.field public static final INSTANCE:Lcom/bachatas4/android/data/ContentImporter$2;


# direct methods
.method static constructor <clinit>()V
    .locals 1

    new-instance v0, Lcom/bachatas4/android/data/ContentImporter$2;

    invoke-direct {v0}, Lcom/bachatas4/android/data/ContentImporter$2;-><init>()V

    sput-object v0, Lcom/bachatas4/android/data/ContentImporter$2;->INSTANCE:Lcom/bachatas4/android/data/ContentImporter$2;

    return-void
.end method

.method constructor <init>()V
    .locals 6

    const-class v2, Ljava/io/File;

    const-string v4, "getUsableSpace()J"

    const/4 v5, 0x0

    const/4 v1, 0x1

    const-string v3, "getUsableSpace"

    move-object v0, p0

    invoke-direct/range {v0 .. v5}, Lkotlin/jvm/internal/FunctionReferenceImpl;-><init>(ILjava/lang/Class;Ljava/lang/String;Ljava/lang/String;I)V

    return-void
.end method


# virtual methods
.method public final invoke(Ljava/io/File;)Ljava/lang/Long;
    .locals 0

    const-string p0, "p0"

    invoke-static {p1, p0}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullParameter(Ljava/lang/Object;Ljava/lang/String;)V

    .line 70
    invoke-virtual {p1}, Ljava/io/File;->getUsableSpace()J

    move-result-wide p0

    invoke-static {p0, p1}, Ljava/lang/Long;->valueOf(J)Ljava/lang/Long;

    move-result-object p0

    return-object p0
.end method

.method public bridge synthetic invoke(Ljava/lang/Object;)Ljava/lang/Object;
    .locals 0

    .line 70
    check-cast p1, Ljava/io/File;

    invoke-virtual {p0, p1}, Lcom/bachatas4/android/data/ContentImporter$2;->invoke(Ljava/io/File;)Ljava/lang/Long;

    move-result-object p0

    return-object p0
.end method
