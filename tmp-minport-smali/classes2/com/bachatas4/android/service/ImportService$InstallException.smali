.class final Lcom/bachatas4/android/service/ImportService$InstallException;
.super Ljava/lang/Exception;
.source "ImportService.kt"


# annotations
.annotation system Ldalvik/annotation/EnclosingClass;
    value = Lcom/bachatas4/android/service/ImportService;
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x1a
    name = "InstallException"
.end annotation

.annotation runtime Lkotlin/Metadata;
    d1 = {
        "\u0000\u001c\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\u000e\n\u0002\u0008\u0005\u0008\u0002\u0018\u00002\u00060\u0001j\u0002`\u0002B\u0017\u0012\u0006\u0010\u0003\u001a\u00020\u0004\u0012\u0006\u0010\u0005\u001a\u00020\u0006\u00a2\u0006\u0004\u0008\u0007\u0010\u0008R\u0011\u0010\u0003\u001a\u00020\u0004\u00a2\u0006\u0008\n\u0000\u001a\u0004\u0008\t\u0010\n\u00a8\u0006\u000b"
    }
    d2 = {
        "Lcom/bachatas4/android/service/ImportService$InstallException;",
        "Ljava/lang/Exception;",
        "Lkotlin/Exception;",
        "code",
        "Lcom/bachatas4/android/data/InstallErrorCode;",
        "message",
        "",
        "<init>",
        "(Lcom/bachatas4/android/data/InstallErrorCode;Ljava/lang/String;)V",
        "getCode",
        "()Lcom/bachatas4/android/data/InstallErrorCode;",
        "app"
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
.field private final code:Lcom/bachatas4/android/data/InstallErrorCode;


# direct methods
.method public constructor <init>(Lcom/bachatas4/android/data/InstallErrorCode;Ljava/lang/String;)V
    .locals 1

    const-string v0, "code"

    invoke-static {p1, v0}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullParameter(Ljava/lang/Object;Ljava/lang/String;)V

    const-string v0, "message"

    invoke-static {p2, v0}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullParameter(Ljava/lang/Object;Ljava/lang/String;)V

    .line 1081
    invoke-direct {p0, p2}, Ljava/lang/Exception;-><init>(Ljava/lang/String;)V

    .line 1082
    iput-object p1, p0, Lcom/bachatas4/android/service/ImportService$InstallException;->code:Lcom/bachatas4/android/data/InstallErrorCode;

    return-void
.end method


# virtual methods
.method public final getCode()Lcom/bachatas4/android/data/InstallErrorCode;
    .locals 0

    .line 1082
    iget-object p0, p0, Lcom/bachatas4/android/service/ImportService$InstallException;->code:Lcom/bachatas4/android/data/InstallErrorCode;

    return-object p0
.end method
