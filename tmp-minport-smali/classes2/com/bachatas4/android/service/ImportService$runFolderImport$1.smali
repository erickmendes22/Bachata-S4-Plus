.class final Lcom/bachatas4/android/service/ImportService$runFolderImport$1;
.super Lkotlin/coroutines/jvm/internal/ContinuationImpl;
.source "ImportService.kt"


# annotations
.annotation system Ldalvik/annotation/EnclosingMethod;
    value = Lcom/bachatas4/android/service/ImportService;->runFolderImport(Ljava/lang/String;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;
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
    c = "com.bachatas4.android.service.ImportService"
    f = "ImportService.kt"
    i = {
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x0,
        0x1,
        0x1,
        0x1,
        0x1,
        0x1,
        0x1,
        0x1,
        0x1,
        0x1,
        0x1,
        0x2,
        0x2,
        0x2,
        0x2,
        0x2,
        0x2,
        0x2,
        0x2,
        0x2,
        0x2,
        0x2,
        0x2,
        0x2,
        0x3,
        0x3,
        0x3,
        0x3,
        0x3,
        0x3,
        0x3,
        0x3,
        0x3,
        0x3,
        0x3,
        0x3,
        0x3,
        0x3
    }
    l = {
        0xd4,
        0xee,
        0x10d,
        0x133
    }
    m = "runFolderImport"
    n = {
        "uriString",
        "jobId",
        "jobStore",
        "job",
        "uri",
        "persistable",
        "uriString",
        "jobId",
        "jobStore",
        "job",
        "uri",
        "folderName",
        "entries",
        "sfoEntry",
        "entry",
        "persistable",
        "uriString",
        "jobId",
        "jobStore",
        "job",
        "uri",
        "folderName",
        "entries",
        "sfoEntry",
        "sfoBytes",
        "sfo",
        "resolved",
        "dest",
        "persistable",
        "uriString",
        "jobId",
        "jobStore",
        "job",
        "uri",
        "folderName",
        "entries",
        "sfoEntry",
        "sfoBytes",
        "sfo",
        "resolved",
        "dest",
        "result",
        "persistable"
    }
    nl = {
        0xda,
        0xf3,
        0x12e,
        0x134
    }
    s = {
        "L$0",
        "L$1",
        "L$2",
        "L$3",
        "L$4",
        "Z$0",
        "L$0",
        "L$1",
        "L$2",
        "L$3",
        "L$4",
        "L$5",
        "L$6",
        "L$7",
        "L$8",
        "Z$0",
        "L$0",
        "L$1",
        "L$2",
        "L$3",
        "L$4",
        "L$5",
        "L$6",
        "L$7",
        "L$8",
        "L$9",
        "L$10",
        "L$11",
        "Z$0",
        "L$0",
        "L$1",
        "L$2",
        "L$3",
        "L$4",
        "L$5",
        "L$6",
        "L$7",
        "L$8",
        "L$9",
        "L$10",
        "L$11",
        "L$12",
        "Z$0"
    }
    v = 0x2
.end annotation


# instance fields
.field L$0:Ljava/lang/Object;

.field L$1:Ljava/lang/Object;

.field L$10:Ljava/lang/Object;

.field L$11:Ljava/lang/Object;

.field L$12:Ljava/lang/Object;

.field L$2:Ljava/lang/Object;

.field L$3:Ljava/lang/Object;

.field L$4:Ljava/lang/Object;

.field L$5:Ljava/lang/Object;

.field L$6:Ljava/lang/Object;

.field L$7:Ljava/lang/Object;

.field L$8:Ljava/lang/Object;

.field L$9:Ljava/lang/Object;

.field Z$0:Z

.field label:I

.field synthetic result:Ljava/lang/Object;

.field final synthetic this$0:Lcom/bachatas4/android/service/ImportService;


# direct methods
.method constructor <init>(Lcom/bachatas4/android/service/ImportService;Lkotlin/coroutines/Continuation;)V
    .locals 0
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "(",
            "Lcom/bachatas4/android/service/ImportService;",
            "Lkotlin/coroutines/Continuation<",
            "-",
            "Lcom/bachatas4/android/service/ImportService$runFolderImport$1;",
            ">;)V"
        }
    .end annotation

    iput-object p1, p0, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->this$0:Lcom/bachatas4/android/service/ImportService;

    invoke-direct {p0, p2}, Lkotlin/coroutines/jvm/internal/ContinuationImpl;-><init>(Lkotlin/coroutines/Continuation;)V

    return-void
.end method


# virtual methods
.method public final invokeSuspend(Ljava/lang/Object;)Ljava/lang/Object;
    .locals 1

    iput-object p1, p0, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->result:Ljava/lang/Object;

    iget p1, p0, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->label:I

    const/high16 v0, -0x80000000

    or-int/2addr p1, v0

    iput p1, p0, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->label:I

    iget-object p1, p0, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->this$0:Lcom/bachatas4/android/service/ImportService;

    const/4 v0, 0x0

    check-cast p0, Lkotlin/coroutines/Continuation;

    invoke-static {p1, v0, p0}, Lcom/bachatas4/android/service/ImportService;->access$runFolderImport(Lcom/bachatas4/android/service/ImportService;Ljava/lang/String;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;

    move-result-object p0

    return-object p0
.end method
