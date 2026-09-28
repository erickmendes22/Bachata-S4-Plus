.class public final Lcom/bachatas4/android/service/ImportService;
.super Lcom/bachatas4/android/service/Hilt_ImportService;
.source "ImportService.kt"


# annotations
.annotation runtime Ldagger/hilt/android/AndroidEntryPoint;
.end annotation

.annotation system Ldalvik/annotation/MemberClasses;
    value = {
        Lcom/bachatas4/android/service/ImportService$Companion;,
        Lcom/bachatas4/android/service/ImportService$InstallException;,
        Lcom/bachatas4/android/service/ImportService$WhenMappings;
    }
.end annotation

.annotation system Ldalvik/annotation/SourceDebugExtension;
    value = "SMAP\nImportService.kt\nKotlin\n*S Kotlin\n*F\n+ 1 ImportService.kt\ncom/bachatas4/android/service/ImportService\n+ 2 _Collections.kt\nkotlin/collections/CollectionsKt___CollectionsKt\n+ 3 fake.kt\nkotlin/jvm/internal/FakeKt\n*L\n1#1,1201:1\n2945#2,3:1202\n2945#2,3:1205\n296#2,2:1208\n2068#2,2:1211\n2068#2,2:1213\n2069#2:1215\n2068#2,2:1216\n2069#2:1218\n2068#2,2:1219\n2069#2:1221\n2068#2,2:1222\n2069#2:1224\n2068#2,2:1225\n2069#2:1227\n2068#2,2:1228\n2069#2:1230\n2068#2,2:1231\n2069#2:1233\n2068#2,2:1234\n1#3:1210\n*S KotlinDebug\n*F\n+ 1 ImportService.kt\ncom/bachatas4/android/service/ImportService\n*L\n220#1:1202,3\n223#1:1205,3\n236#1:1208,2\n903#1:1211,2\n904#1:1213,2\n903#1:1215\n904#1:1216,2\n903#1:1218\n904#1:1219,2\n903#1:1221\n904#1:1222,2\n903#1:1224\n904#1:1225,2\n903#1:1227\n904#1:1228,2\n903#1:1230\n904#1:1231,2\n903#1:1233\n904#1:1234,2\n*E\n"
.end annotation

.annotation runtime Lkotlin/Metadata;
    d1 = {
        "\u0000\u00b8\u0001\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0008\u0003\n\u0002\u0018\u0002\n\u0002\u0008\u0004\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\u0008\u0005\n\u0002\u0018\u0002\n\u0002\u0008\u0005\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\u0010\u000e\n\u0000\n\u0002\u0010\u000b\n\u0000\n\u0002\u0010\u0002\n\u0000\n\u0002\u0010\u0008\n\u0000\n\u0002\u0018\u0002\n\u0002\u0008\u0003\n\u0002\u0018\u0002\n\u0002\u0008\u0008\n\u0002\u0010 \n\u0002\u0008\u0003\n\u0002\u0018\u0002\n\u0002\u0008\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\u0008\u0002\n\u0002\u0010\t\n\u0002\u0008\u0002\n\u0002\u0018\u0002\n\u0002\u0008\u0004\n\u0002\u0010\u0001\n\u0000\n\u0002\u0018\u0002\n\u0002\u0008\u0003\n\u0002\u0010\u0003\n\u0002\u0008\u0005\n\u0002\u0018\u0002\n\u0002\u0008\u0007\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\u0008\u0007\u0018\u0000 X2\u00020\u0001:\u0002WXB\u0007\u00a2\u0006\u0004\u0008\u0002\u0010\u0003J\u0008\u0010 \u001a\u00020!H\u0016J\"\u0010\"\u001a\u00020#2\u0008\u0010$\u001a\u0004\u0018\u00010%2\u0006\u0010&\u001a\u00020#2\u0006\u0010\'\u001a\u00020#H\u0016J\u0014\u0010(\u001a\u0004\u0018\u00010)2\u0008\u0010$\u001a\u0004\u0018\u00010%H\u0016J\u0008\u0010*\u001a\u00020!H\u0016J\u0016\u0010+\u001a\u00020!2\u0006\u0010,\u001a\u00020\u001dH\u0082@\u00a2\u0006\u0002\u0010-J\u0016\u0010.\u001a\u00020!2\u0006\u0010,\u001a\u00020\u001dH\u0082@\u00a2\u0006\u0002\u0010-J$\u0010/\u001a\u00020!2\u0006\u00100\u001a\u00020\u001d2\u000c\u00101\u001a\u0008\u0012\u0004\u0012\u00020\u001d02H\u0082@\u00a2\u0006\u0002\u00103J\u0010\u00104\u001a\u00020\u001f2\u0006\u00105\u001a\u000206H\u0002J.\u00107\u001a\u00020!2\u0006\u00108\u001a\u0002092\u0006\u0010:\u001a\u00020;2\u0006\u0010<\u001a\u00020\u001d2\u0006\u0010=\u001a\u00020>H\u0082@\u00a2\u0006\u0002\u0010?J*\u0010@\u001a\u00020A2\u0006\u0010B\u001a\u00020#2\u0006\u0010C\u001a\u00020;2\u0008\u0010D\u001a\u0004\u0018\u00010\u001d2\u0006\u0010<\u001a\u00020\u001dH\u0002J\u0018\u0010E\u001a\u00020F2\u0006\u0010G\u001a\u00020H2\u0006\u0010I\u001a\u00020\u001dH\u0002J\u0010\u0010J\u001a\u00020!2\u0006\u0010K\u001a\u00020LH\u0002J\u001a\u0010M\u001a\u00020!2\u0006\u0010N\u001a\u00020\u001d2\u0008\u0008\u0002\u0010O\u001a\u00020\u001fH\u0002J\u0008\u0010P\u001a\u00020!H\u0002J2\u0010Q\u001a\u00020R2\u0006\u0010N\u001a\u00020\u001d2\u0006\u0010S\u001a\u00020#2\u0006\u0010T\u001a\u00020#2\u0006\u0010O\u001a\u00020\u001f2\u0008\u0008\u0002\u0010U\u001a\u00020\u001fH\u0002J.\u0010V\u001a\u00020!2\u0006\u0010N\u001a\u00020\u001d2\u0008\u0008\u0002\u0010S\u001a\u00020#2\u0008\u0008\u0002\u0010T\u001a\u00020#2\u0008\u0008\u0002\u0010U\u001a\u00020\u001fH\u0002R#\u0010\u0004\u001a\u00020\u00058\u0006@\u0006X\u0087.\u0092\u0002\u0002\u0008\n\u00a2\u0006\u000e\n\u0000\u001a\u0004\u0008\u0006\u0010\u0007\"\u0004\u0008\u0008\u0010\tR#\u0010\u000b\u001a\u00020\u000c8\u0006@\u0006X\u0087.\u0092\u0002\u0002\u0008\n\u00a2\u0006\u000e\n\u0000\u001a\u0004\u0008\r\u0010\u000e\"\u0004\u0008\u000f\u0010\u0010R#\u0010\u0011\u001a\u00020\u00128\u0006@\u0006X\u0087.\u0092\u0002\u0002\u0008\n\u00a2\u0006\u000e\n\u0000\u001a\u0004\u0008\u0013\u0010\u0014\"\u0004\u0008\u0015\u0010\u0016R\u000e\u0010\u0017\u001a\u00020\u0018X\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u0010\u0010\u0019\u001a\u0004\u0018\u00010\u001aX\u0082\u000e\u00a2\u0006\u0002\n\u0000R\u0018\u0010\u001b\u001a\u000c\u0012\u0006\u0012\u0004\u0018\u00010\u001d\u0018\u00010\u001cX\u0082\u000e\u00a2\u0006\u0002\n\u0000R\u0016\u0010\u001e\u001a\n\u0012\u0004\u0012\u00020\u001f\u0018\u00010\u001cX\u0082\u000e\u00a2\u0006\u0002\n\u0000\u00ca\u0001\u0002\u0008Z\u00ca\u0001\u000c\u0008[\u0012\u0008\u0008\\\u0012\u0004\u0008\u0003\u0010\u0000\u00a8\u0006Y"
    }
    d2 = {
        "Lcom/bachatas4/android/service/ImportService;",
        "Landroid/app/Service;",
        "<init>",
        "()V",
        "contentImporter",
        "Lcom/bachatas4/android/data/ContentImporter;",
        "getContentImporter",
        "()Lcom/bachatas4/android/data/ContentImporter;",
        "setContentImporter",
        "(Lcom/bachatas4/android/data/ContentImporter;)V",
        "Ljavax/inject/Inject;",
        "gameRepository",
        "Lcom/bachatas4/android/data/GameRepository;",
        "getGameRepository",
        "()Lcom/bachatas4/android/data/GameRepository;",
        "setGameRepository",
        "(Lcom/bachatas4/android/data/GameRepository;)V",
        "pkgKeyStore",
        "Lcom/bachatas4/android/data/PkgKeyStore;",
        "getPkgKeyStore",
        "()Lcom/bachatas4/android/data/PkgKeyStore;",
        "setPkgKeyStore",
        "(Lcom/bachatas4/android/data/PkgKeyStore;)V",
        "scope",
        "Lkotlinx/coroutines/CoroutineScope;",
        "importJob",
        "Lkotlinx/coroutines/Job;",
        "passcodeWaiter",
        "Lkotlinx/coroutines/CompletableDeferred;",
        "",
        "copyConfirmWaiter",
        "",
        "onCreate",
        "",
        "onStartCommand",
        "",
        "intent",
        "Landroid/content/Intent;",
        "flags",
        "startId",
        "onBind",
        "Landroid/os/IBinder;",
        "onDestroy",
        "runFolderImport",
        "uriString",
        "(Ljava/lang/String;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;",
        "runPkgImport",
        "runPkgBatchImport",
        "gameId",
        "uris",
        "",
        "(Ljava/lang/String;Ljava/util/List;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;",
        "isOpenFdSeekable",
        "pfd",
        "Landroid/os/ParcelFileDescriptor;",
        "copyPkgToLocalCache",
        "uri",
        "Landroid/net/Uri;",
        "dest",
        "Ljava/io/File;",
        "displayName",
        "totalHint",
        "",
        "(Landroid/net/Uri;Ljava/io/File;Ljava/lang/String;JLkotlin/coroutines/Continuation;)Ljava/lang/Object;",
        "extractWithProgress",
        "Lcom/bachatas4/android/runtime/pkg/PkgExtractResult;",
        "fd",
        "staging",
        "passcode",
        "failInstall",
        "",
        "code",
        "Lcom/bachatas4/android/data/InstallErrorCode;",
        "message",
        "handleFailure",
        "failure",
        "",
        "notifyDone",
        "text",
        "ongoing",
        "createNotificationChannel",
        "buildNotification",
        "Landroid/app/Notification;",
        "maxProgress",
        "progress",
        "indeterminate",
        "updateNotification",
        "InstallException",
        "Companion",
        "app",
        "Ldagger/hilt/android/AndroidEntryPoint;",
        "Landroidx/compose/runtime/internal/StabilityInferred;",
        "parameters"
    }
    k = 0x1
    mv = {
        0x2,
        0x4,
        0x0
    }
    xi = 0x30
.end annotation


# static fields
.field public static final $stable:I

.field public static final CHANNEL_ID:Ljava/lang/String; = "import"
    .annotation runtime Ljava/lang/Deprecated;
    .end annotation
.end field

.field public static final COPY_BUFFER_BYTES:I = 0x100000
    .annotation runtime Ljava/lang/Deprecated;
    .end annotation
.end field

.field private static final Companion:Lcom/bachatas4/android/service/ImportService$Companion;

.field public static final NOTIFICATION_ID:I = 0x2a
    .annotation runtime Ljava/lang/Deprecated;
    .end annotation
.end field

.field public static final PROGRESS_SCALE:I = 0x3e8
    .annotation runtime Ljava/lang/Deprecated;
    .end annotation
.end field

.field public static final STORAGE_MARGIN_BYTES:J = 0x10000000L
    .annotation runtime Ljava/lang/Deprecated;
    .end annotation
.end field

.field public static final TAG:Ljava/lang/String; = "BachataImport"
    .annotation runtime Ljava/lang/Deprecated;
    .end annotation
.end field


# instance fields
.field public contentImporter:Lcom/bachatas4/android/data/ContentImporter;
    .annotation runtime Ljavax/inject/Inject;
    .end annotation
.end field

.field private copyConfirmWaiter:Lkotlinx/coroutines/CompletableDeferred;
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "Lkotlinx/coroutines/CompletableDeferred<",
            "Ljava/lang/Boolean;",
            ">;"
        }
    .end annotation
.end field

.field public gameRepository:Lcom/bachatas4/android/data/GameRepository;
    .annotation runtime Ljavax/inject/Inject;
    .end annotation
.end field

.field private importJob:Lkotlinx/coroutines/Job;

.field private passcodeWaiter:Lkotlinx/coroutines/CompletableDeferred;
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "Lkotlinx/coroutines/CompletableDeferred<",
            "Ljava/lang/String;",
            ">;"
        }
    .end annotation
.end field

.field public pkgKeyStore:Lcom/bachatas4/android/data/PkgKeyStore;
    .annotation runtime Ljavax/inject/Inject;
    .end annotation
.end field

.field private final scope:Lkotlinx/coroutines/CoroutineScope;


# direct methods
.method static constructor <clinit>()V
    .locals 2

    new-instance v0, Lcom/bachatas4/android/service/ImportService$Companion;

    const/4 v1, 0x0

    invoke-direct {v0, v1}, Lcom/bachatas4/android/service/ImportService$Companion;-><init>(Lkotlin/jvm/internal/DefaultConstructorMarker;)V

    sput-object v0, Lcom/bachatas4/android/service/ImportService;->Companion:Lcom/bachatas4/android/service/ImportService$Companion;

    const/16 v0, 0x8

    sput v0, Lcom/bachatas4/android/service/ImportService;->$stable:I

    return-void
.end method

.method public constructor <init>()V
    .locals 2

    .line 64
    invoke-direct {p0}, Lcom/bachatas4/android/service/Hilt_ImportService;-><init>()V

    const/4 v0, 0x0

    const/4 v1, 0x1

    .line 70
    invoke-static {v0, v1, v0}, Lkotlinx/coroutines/SupervisorKt;->SupervisorJob$default(Lkotlinx/coroutines/Job;ILjava/lang/Object;)Lkotlinx/coroutines/CompletableJob;

    move-result-object v0

    invoke-static {}, Lkotlinx/coroutines/Dispatchers;->getIO()Lkotlinx/coroutines/CoroutineDispatcher;

    move-result-object v1

    check-cast v1, Lkotlin/coroutines/CoroutineContext;

    invoke-interface {v0, v1}, Lkotlinx/coroutines/CompletableJob;->plus(Lkotlin/coroutines/CoroutineContext;)Lkotlin/coroutines/CoroutineContext;

    move-result-object v0

    invoke-static {v0}, Lkotlinx/coroutines/CoroutineScopeKt;->CoroutineScope(Lkotlin/coroutines/CoroutineContext;)Lkotlinx/coroutines/CoroutineScope;

    move-result-object v0

    iput-object v0, p0, Lcom/bachatas4/android/service/ImportService;->scope:Lkotlinx/coroutines/CoroutineScope;

    return-void
.end method

.method public static final synthetic access$copyPkgToLocalCache(Lcom/bachatas4/android/service/ImportService;Landroid/net/Uri;Ljava/io/File;Ljava/lang/String;JLkotlin/coroutines/Continuation;)Ljava/lang/Object;
    .locals 0

    .line 64
    invoke-direct/range {p0 .. p6}, Lcom/bachatas4/android/service/ImportService;->copyPkgToLocalCache(Landroid/net/Uri;Ljava/io/File;Ljava/lang/String;JLkotlin/coroutines/Continuation;)Ljava/lang/Object;

    move-result-object p0

    return-object p0
.end method

.method public static final synthetic access$extractWithProgress(Lcom/bachatas4/android/service/ImportService;ILjava/io/File;Ljava/lang/String;Ljava/lang/String;)Lcom/bachatas4/android/runtime/pkg/PkgExtractResult;
    .locals 0

    .line 64
    invoke-direct {p0, p1, p2, p3, p4}, Lcom/bachatas4/android/service/ImportService;->extractWithProgress(ILjava/io/File;Ljava/lang/String;Ljava/lang/String;)Lcom/bachatas4/android/runtime/pkg/PkgExtractResult;

    move-result-object p0

    return-object p0
.end method

.method public static final synthetic access$getCompanion$p()Lcom/bachatas4/android/service/ImportService$Companion;
    .locals 1

    .line 64
    sget-object v0, Lcom/bachatas4/android/service/ImportService;->Companion:Lcom/bachatas4/android/service/ImportService$Companion;

    return-object v0
.end method

.method public static final synthetic access$runFolderImport(Lcom/bachatas4/android/service/ImportService;Ljava/lang/String;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;
    .locals 0

    .line 64
    invoke-direct {p0, p1, p2}, Lcom/bachatas4/android/service/ImportService;->runFolderImport(Ljava/lang/String;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;

    move-result-object p0

    return-object p0
.end method

.method public static final synthetic access$runPkgBatchImport(Lcom/bachatas4/android/service/ImportService;Ljava/lang/String;Ljava/util/List;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;
    .locals 0

    .line 64
    invoke-direct {p0, p1, p2, p3}, Lcom/bachatas4/android/service/ImportService;->runPkgBatchImport(Ljava/lang/String;Ljava/util/List;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;

    move-result-object p0

    return-object p0
.end method

.method public static final synthetic access$runPkgImport(Lcom/bachatas4/android/service/ImportService;Ljava/lang/String;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;
    .locals 0

    .line 64
    invoke-direct {p0, p1, p2}, Lcom/bachatas4/android/service/ImportService;->runPkgImport(Ljava/lang/String;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;

    move-result-object p0

    return-object p0
.end method

.method public static final synthetic access$updateNotification(Lcom/bachatas4/android/service/ImportService;Ljava/lang/String;IIZ)V
    .locals 0

    .line 64
    invoke-direct {p0, p1, p2, p3, p4}, Lcom/bachatas4/android/service/ImportService;->updateNotification(Ljava/lang/String;IIZ)V

    return-void
.end method

.method private final buildNotification(Ljava/lang/String;IIZZ)Landroid/app/Notification;
    .locals 6

    .line 1107
    move-object v0, p0

    check-cast v0, Landroid/content/Context;

    .line 1109
    new-instance v1, Landroid/content/Intent;

    const-class v2, Lcom/bachatas4/android/MainActivity;

    invoke-direct {v1, v0, v2}, Landroid/content/Intent;-><init>(Landroid/content/Context;Ljava/lang/Class;)V

    const/4 v2, 0x0

    const/high16 v3, 0xc000000

    .line 1106
    invoke-static {v0, v2, v1, v3}, Landroid/app/PendingIntent;->getActivity(Landroid/content/Context;ILandroid/content/Intent;I)Landroid/app/PendingIntent;

    move-result-object v1

    .line 1115
    new-instance v4, Landroid/content/Intent;

    const-string v5, "com.bachatas4.android.action.CANCEL_IMPORT"

    invoke-direct {v4, v5}, Landroid/content/Intent;-><init>(Ljava/lang/String;)V

    invoke-virtual {p0}, Lcom/bachatas4/android/service/ImportService;->getPackageName()Ljava/lang/String;

    move-result-object p0

    const-string v5, "com.bachatas4.android.service.ImportService"

    invoke-virtual {v4, p0, v5}, Landroid/content/Intent;->setClassName(Ljava/lang/String;Ljava/lang/String;)Landroid/content/Intent;

    move-result-object p0

    const/4 v4, 0x1

    .line 1112
    invoke-static {v0, v4, p0, v3}, Landroid/app/PendingIntent;->getService(Landroid/content/Context;ILandroid/content/Intent;I)Landroid/app/PendingIntent;

    move-result-object p0

    .line 1118
    new-instance v3, Landroidx/core/app/NotificationCompat$Builder;

    const-string v5, "import"

    invoke-direct {v3, v0, v5}, Landroidx/core/app/NotificationCompat$Builder;-><init>(Landroid/content/Context;Ljava/lang/String;)V

    const v0, 0x1080081

    .line 1119
    invoke-virtual {v3, v0}, Landroidx/core/app/NotificationCompat$Builder;->setSmallIcon(I)Landroidx/core/app/NotificationCompat$Builder;

    move-result-object v0

    .line 1120
    const-string v3, "Bachata S4"

    check-cast v3, Ljava/lang/CharSequence;

    invoke-virtual {v0, v3}, Landroidx/core/app/NotificationCompat$Builder;->setContentTitle(Ljava/lang/CharSequence;)Landroidx/core/app/NotificationCompat$Builder;

    move-result-object v0

    .line 1121
    check-cast p1, Ljava/lang/CharSequence;

    invoke-virtual {v0, p1}, Landroidx/core/app/NotificationCompat$Builder;->setContentText(Ljava/lang/CharSequence;)Landroidx/core/app/NotificationCompat$Builder;

    move-result-object p1

    .line 1122
    invoke-virtual {p1, v1}, Landroidx/core/app/NotificationCompat$Builder;->setContentIntent(Landroid/app/PendingIntent;)Landroidx/core/app/NotificationCompat$Builder;

    move-result-object p1

    .line 1123
    invoke-virtual {p1, p4}, Landroidx/core/app/NotificationCompat$Builder;->setOngoing(Z)Landroidx/core/app/NotificationCompat$Builder;

    move-result-object p1

    .line 1124
    invoke-virtual {p1, v4}, Landroidx/core/app/NotificationCompat$Builder;->setOnlyAlertOnce(Z)Landroidx/core/app/NotificationCompat$Builder;

    move-result-object p1

    const-string v0, "setOnlyAlertOnce(...)"

    invoke-static {p1, v0}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullExpressionValue(Ljava/lang/Object;Ljava/lang/String;)V

    if-eqz p4, :cond_2

    .line 1126
    const-string p4, "Cancel"

    check-cast p4, Ljava/lang/CharSequence;

    invoke-virtual {p1, v2, p4, p0}, Landroidx/core/app/NotificationCompat$Builder;->addAction(ILjava/lang/CharSequence;Landroid/app/PendingIntent;)Landroidx/core/app/NotificationCompat$Builder;

    if-nez p5, :cond_1

    if-gtz p2, :cond_0

    goto :goto_0

    .line 1130
    :cond_0
    invoke-static {p3, v2, p2}, Lkotlin/ranges/RangesKt;->coerceIn(III)I

    move-result p0

    invoke-virtual {p1, p2, p0, v2}, Landroidx/core/app/NotificationCompat$Builder;->setProgress(IIZ)Landroidx/core/app/NotificationCompat$Builder;

    goto :goto_1

    .line 1128
    :cond_1
    :goto_0
    invoke-virtual {p1, v2, v2, v4}, Landroidx/core/app/NotificationCompat$Builder;->setProgress(IIZ)Landroidx/core/app/NotificationCompat$Builder;

    .line 1133
    :cond_2
    :goto_1
    invoke-virtual {p1}, Landroidx/core/app/NotificationCompat$Builder;->build()Landroid/app/Notification;

    move-result-object p0

    const-string p1, "build(...)"

    invoke-static {p0, p1}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullExpressionValue(Ljava/lang/Object;Ljava/lang/String;)V

    return-object p0
.end method

.method static synthetic buildNotification$default(Lcom/bachatas4/android/service/ImportService;Ljava/lang/String;IIZZILjava/lang/Object;)Landroid/app/Notification;
    .locals 6

    and-int/lit8 p6, p6, 0x10

    if-eqz p6, :cond_0

    const/4 p5, 0x0

    :cond_0
    move-object v0, p0

    move-object v1, p1

    move v2, p2

    move v3, p3

    move v4, p4

    move v5, p5

    .line 1099
    invoke-direct/range {v0 .. v5}, Lcom/bachatas4/android/service/ImportService;->buildNotification(Ljava/lang/String;IIZZ)Landroid/app/Notification;

    move-result-object p0

    return-object p0
.end method

.method private final copyPkgToLocalCache(Landroid/net/Uri;Ljava/io/File;Ljava/lang/String;JLkotlin/coroutines/Continuation;)Ljava/lang/Object;
    .locals 9
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "(",
            "Landroid/net/Uri;",
            "Ljava/io/File;",
            "Ljava/lang/String;",
            "J",
            "Lkotlin/coroutines/Continuation<",
            "-",
            "Lkotlin/Unit;",
            ">;)",
            "Ljava/lang/Object;"
        }
    .end annotation

    .line 937
    invoke-static {}, Lkotlinx/coroutines/Dispatchers;->getIO()Lkotlinx/coroutines/CoroutineDispatcher;

    move-result-object v0

    check-cast v0, Lkotlin/coroutines/CoroutineContext;

    new-instance v1, Lcom/bachatas4/android/service/ImportService$copyPkgToLocalCache$2;

    const/4 v8, 0x0

    move-object v2, p0

    move-object v3, p1

    move-object v4, p2

    move-object v7, p3

    move-wide v5, p4

    invoke-direct/range {v1 .. v8}, Lcom/bachatas4/android/service/ImportService$copyPkgToLocalCache$2;-><init>(Lcom/bachatas4/android/service/ImportService;Landroid/net/Uri;Ljava/io/File;JLjava/lang/String;Lkotlin/coroutines/Continuation;)V

    check-cast v1, Lkotlin/jvm/functions/Function2;

    invoke-static {v0, v1, p6}, Lkotlinx/coroutines/BuildersKt;->withContext(Lkotlin/coroutines/CoroutineContext;Lkotlin/jvm/functions/Function2;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;

    move-result-object p0

    invoke-static {}, Lkotlin/coroutines/intrinsics/IntrinsicsKt;->getCOROUTINE_SUSPENDED()Ljava/lang/Object;

    move-result-object p1

    if-ne p0, p1, :cond_0

    return-object p0

    :cond_0
    sget-object p0, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;

    return-object p0
.end method

.method private final createNotificationChannel()V
    .locals 4

    .line 1094
    const-class v0, Landroid/app/NotificationManager;

    invoke-virtual {p0, v0}, Lcom/bachatas4/android/service/ImportService;->getSystemService(Ljava/lang/Class;)Ljava/lang/Object;

    move-result-object p0

    check-cast p0, Landroid/app/NotificationManager;

    .line 1095
    new-instance v0, Landroid/app/NotificationChannel;

    const-string v1, "Game Imports"

    check-cast v1, Ljava/lang/CharSequence;

    const/4 v2, 0x2

    const-string v3, "import"

    invoke-direct {v0, v3, v1, v2}, Landroid/app/NotificationChannel;-><init>(Ljava/lang/String;Ljava/lang/CharSequence;I)V

    .line 1094
    invoke-virtual {p0, v0}, Landroid/app/NotificationManager;->createNotificationChannel(Landroid/app/NotificationChannel;)V

    return-void
.end method

.method private final extractWithProgress(ILjava/io/File;Ljava/lang/String;Ljava/lang/String;)Lcom/bachatas4/android/runtime/pkg/PkgExtractResult;
    .locals 11

    .line 996
    new-instance v0, Lkotlin/jvm/internal/Ref$LongRef;

    invoke-direct {v0}, Lkotlin/jvm/internal/Ref$LongRef;-><init>()V

    .line 997
    new-instance v1, Lkotlin/jvm/internal/Ref$LongRef;

    invoke-direct {v1}, Lkotlin/jvm/internal/Ref$LongRef;-><init>()V

    .line 999
    sget-object v2, Lcom/bachatas4/android/data/ImportManager;->INSTANCE:Lcom/bachatas4/android/data/ImportManager;

    .line 1000
    new-instance v3, Lcom/bachatas4/android/data/ImportProgress$Extracting;

    const-wide/16 v6, 0x0

    .line 1003
    const-string v8, "Preparing extract\u2026"

    const-wide/16 v4, 0x0

    move-object v9, p4

    .line 1000
    invoke-direct/range {v3 .. v9}, Lcom/bachatas4/android/data/ImportProgress$Extracting;-><init>(JJLjava/lang/String;Ljava/lang/String;)V

    check-cast v3, Lcom/bachatas4/android/data/ImportProgress;

    .line 999
    invoke-virtual {v2, v3}, Lcom/bachatas4/android/data/ImportManager;->update(Lcom/bachatas4/android/data/ImportProgress;)V

    const/4 v9, 0x6

    const/4 v10, 0x0

    .line 1007
    const-string v5, "Extracting PKG\u2026"

    const/4 v6, 0x0

    const/4 v7, 0x0

    const/4 v8, 0x1

    move-object v4, p0

    invoke-static/range {v4 .. v10}, Lcom/bachatas4/android/service/ImportService;->updateNotification$default(Lcom/bachatas4/android/service/ImportService;Ljava/lang/String;IIZILjava/lang/Object;)V

    .line 1008
    invoke-virtual {p2}, Ljava/io/File;->getAbsolutePath()Ljava/lang/String;

    move-result-object v2

    new-instance v3, Ljava/lang/StringBuilder;

    const-string v5, "nativeExtract enter fd="

    invoke-direct {v3, v5}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v3, p1}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    move-result-object v3

    const-string v5, " out="

    invoke-virtual {v3, v5}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v3

    invoke-virtual {v3, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v2

    invoke-virtual {v2}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v2

    const-string v3, "BachataImport"

    invoke-static {v3, v2}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    .line 1011
    invoke-virtual {p2}, Ljava/io/File;->getAbsolutePath()Ljava/lang/String;

    move-result-object p2

    const-string v2, "getAbsolutePath(...)"

    invoke-static {p2, v2}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullExpressionValue(Ljava/lang/Object;Ljava/lang/String;)V

    .line 1013
    new-instance v2, Lcom/bachatas4/android/service/ImportService$$ExternalSyntheticLambda0;

    invoke-direct {v2, v1, p4, p0, v0}, Lcom/bachatas4/android/service/ImportService$$ExternalSyntheticLambda0;-><init>(Lkotlin/jvm/internal/Ref$LongRef;Ljava/lang/String;Lcom/bachatas4/android/service/ImportService;Lkotlin/jvm/internal/Ref$LongRef;)V

    .line 1009
    invoke-static {p1, p2, p3, v2}, Lcom/bachatas4/android/runtime/pkg/PkgExtractor;->nativeExtract(ILjava/lang/String;Ljava/lang/String;Lcom/bachatas4/android/runtime/pkg/PkgProgressListener;)Lcom/bachatas4/android/runtime/pkg/PkgExtractResult;

    move-result-object p0

    .line 1047
    invoke-virtual {p0}, Lcom/bachatas4/android/runtime/pkg/PkgExtractResult;->getStatus()Lcom/bachatas4/android/runtime/pkg/PkgStatus;

    move-result-object p1

    invoke-virtual {p0}, Lcom/bachatas4/android/runtime/pkg/PkgExtractResult;->getMessage()Ljava/lang/String;

    move-result-object p2

    new-instance p3, Ljava/lang/StringBuilder;

    const-string v0, "nativeExtract exit status="

    invoke-direct {p3, v0}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {p3, p1}, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;

    move-result-object p1

    const-string p3, " msg="

    invoke-virtual {p1, p3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p1

    invoke-virtual {p1, p2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p1

    invoke-virtual {p1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p1

    invoke-static {v3, p1}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    return-object p0
.end method

.method static final extractWithProgress$lambda$0(Lkotlin/jvm/internal/Ref$LongRef;Ljava/lang/String;Lcom/bachatas4/android/service/ImportService;Lkotlin/jvm/internal/Ref$LongRef;JJLjava/lang/String;)V
    .locals 11

    move-object/from16 v0, p8

    const-string v1, "currentFile"

    invoke-static {v0, v1}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullParameter(Ljava/lang/Object;Ljava/lang/String;)V

    .line 1014
    invoke-static {}, Ljava/lang/System;->currentTimeMillis()J

    move-result-wide v7

    .line 1016
    iget-wide v1, p0, Lkotlin/jvm/internal/Ref$LongRef;->element:J

    const-wide/16 v9, 0x0

    cmp-long v1, v1, v9

    if-eqz v1, :cond_0

    iget-wide v1, p0, Lkotlin/jvm/internal/Ref$LongRef;->element:J

    sub-long v1, v7, v1

    const-wide/16 v3, 0xc8

    cmp-long v1, v1, v3

    if-gez v1, :cond_0

    goto/16 :goto_2

    .line 1019
    :cond_0
    iput-wide v7, p0, Lkotlin/jvm/internal/Ref$LongRef;->element:J

    .line 1020
    move-object p0, v0

    check-cast p0, Ljava/lang/CharSequence;

    invoke-static {p0}, Lkotlin/text/StringsKt;->isBlank(Ljava/lang/CharSequence;)Z

    move-result v0

    if-eqz v0, :cond_1

    const-string p0, "\u2026"

    :cond_1
    move-object v5, p0

    check-cast v5, Ljava/lang/String;

    .line 1021
    sget-object p0, Lcom/bachatas4/android/data/ImportManager;->INSTANCE:Lcom/bachatas4/android/data/ImportManager;

    .line 1022
    new-instance v0, Lcom/bachatas4/android/data/ImportProgress$Extracting;

    move-object v6, p1

    move-wide v1, p4

    move-wide/from16 v3, p6

    invoke-direct/range {v0 .. v6}, Lcom/bachatas4/android/data/ImportProgress$Extracting;-><init>(JJLjava/lang/String;Ljava/lang/String;)V

    check-cast v0, Lcom/bachatas4/android/data/ImportProgress;

    .line 1021
    invoke-virtual {p0, v0}, Lcom/bachatas4/android/data/ImportManager;->update(Lcom/bachatas4/android/data/ImportProgress;)V

    .line 1029
    sget-object p0, Lcom/bachatas4/android/service/ImportService;->Companion:Lcom/bachatas4/android/service/ImportService$Companion;

    invoke-virtual {p0, v1, v2, v3, v4}, Lcom/bachatas4/android/service/ImportService$Companion;->scaledProgress(JJ)Lkotlin/Pair;

    move-result-object p1

    invoke-virtual {p1}, Lkotlin/Pair;->component1()Ljava/lang/Object;

    move-result-object v0

    check-cast v0, Ljava/lang/Number;

    invoke-virtual {v0}, Ljava/lang/Number;->intValue()I

    move-result v0

    invoke-virtual {p1}, Lkotlin/Pair;->component2()Ljava/lang/Object;

    move-result-object p1

    check-cast p1, Ljava/lang/Number;

    invoke-virtual {p1}, Ljava/lang/Number;->intValue()I

    move-result p1

    cmp-long v6, v3, v9

    if-lez v6, :cond_2

    .line 1031
    invoke-virtual {p0, v1, v2}, Lcom/bachatas4/android/service/ImportService$Companion;->formatBytes(J)Ljava/lang/String;

    move-result-object v1

    invoke-virtual {p0, v3, v4}, Lcom/bachatas4/android/service/ImportService$Companion;->formatBytes(J)Ljava/lang/String;

    move-result-object p0

    new-instance v2, Ljava/lang/StringBuilder;

    invoke-direct {v2}, Ljava/lang/StringBuilder;-><init>()V

    invoke-virtual {v2, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    const-string v2, " / "

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1, p0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p0

    invoke-virtual {p0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p0

    goto :goto_0

    .line 1033
    :cond_2
    invoke-virtual {p0, v1, v2}, Lcom/bachatas4/android/service/ImportService$Companion;->formatBytes(J)Ljava/lang/String;

    move-result-object p0

    .line 1036
    :goto_0
    new-instance v1, Ljava/lang/StringBuilder;

    const-string v2, "Extracting PKG \u00b7 "

    invoke-direct {v1, v2}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v1, p0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    const-string v2, " \u00b7 "

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1, v5}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v1

    if-nez v0, :cond_3

    const/4 v2, 0x1

    goto :goto_1

    :cond_3
    const/4 v2, 0x0

    .line 1035
    :goto_1
    invoke-direct {p2, v1, v0, p1, v2}, Lcom/bachatas4/android/service/ImportService;->updateNotification(Ljava/lang/String;IIZ)V

    .line 1041
    iget-wide p1, p3, Lkotlin/jvm/internal/Ref$LongRef;->element:J

    sub-long p1, v7, p1

    const-wide/16 v0, 0x7d0

    cmp-long p1, p1, v0

    if-ltz p1, :cond_4

    .line 1042
    iput-wide v7, p3, Lkotlin/jvm/internal/Ref$LongRef;->element:J

    .line 1043
    new-instance p1, Ljava/lang/StringBuilder;

    const-string p2, "nativeExtract progress "

    invoke-direct {p1, p2}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {p1, p0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p0

    const-string p1, " file="

    invoke-virtual {p0, p1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p0

    invoke-virtual {p0, v5}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p0

    invoke-virtual {p0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p0

    const-string p1, "BachataImport"

    invoke-static {p1, p0}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    :cond_4
    :goto_2
    return-void
.end method

.method private final failInstall(Lcom/bachatas4/android/data/InstallErrorCode;Ljava/lang/String;)Ljava/lang/Void;
    .locals 0

    .line 1052
    new-instance p0, Lcom/bachatas4/android/service/ImportService$InstallException;

    invoke-direct {p0, p1, p2}, Lcom/bachatas4/android/service/ImportService$InstallException;-><init>(Lcom/bachatas4/android/data/InstallErrorCode;Ljava/lang/String;)V

    throw p0
.end method

.method private final handleFailure(Ljava/lang/Throwable;)V
    .locals 5

    .line 1056
    instance-of v0, p1, Ljava/util/concurrent/CancellationException;

    const-string v1, "BachataImport"

    if-nez v0, :cond_8

    .line 1057
    instance-of v0, p1, Lcom/bachatas4/android/service/ImportService$InstallException;

    if-eqz v0, :cond_0

    move-object v2, p1

    check-cast v2, Lcom/bachatas4/android/service/ImportService$InstallException;

    invoke-virtual {v2}, Lcom/bachatas4/android/service/ImportService$InstallException;->getCode()Lcom/bachatas4/android/data/InstallErrorCode;

    move-result-object v2

    sget-object v3, Lcom/bachatas4/android/data/InstallErrorCode;->CANCELLED:Lcom/bachatas4/android/data/InstallErrorCode;

    if-ne v2, v3, :cond_0

    goto/16 :goto_2

    :cond_0
    if-eqz v0, :cond_2

    .line 1065
    move-object v0, p1

    check-cast v0, Lcom/bachatas4/android/service/ImportService$InstallException;

    invoke-virtual {v0}, Lcom/bachatas4/android/service/ImportService$InstallException;->getCode()Lcom/bachatas4/android/data/InstallErrorCode;

    move-result-object v0

    invoke-virtual {p1}, Ljava/lang/Throwable;->getMessage()Ljava/lang/String;

    move-result-object v2

    if-nez v2, :cond_1

    const-string v2, ""

    :cond_1
    invoke-static {v0, v2}, Lkotlin/TuplesKt;->to(Ljava/lang/Object;Ljava/lang/Object;)Lkotlin/Pair;

    move-result-object v0

    goto :goto_1

    .line 1066
    :cond_2
    instance-of v0, p1, Lcom/bachatas4/android/data/ContentImportException;

    if-eqz v0, :cond_6

    .line 1067
    move-object v0, p1

    check-cast v0, Lcom/bachatas4/android/data/ContentImportException;

    invoke-virtual {v0}, Lcom/bachatas4/android/data/ContentImportException;->getCode()Lcom/bachatas4/android/model/RuntimeErrorCode;

    move-result-object v2

    sget-object v3, Lcom/bachatas4/android/service/ImportService$WhenMappings;->$EnumSwitchMapping$0:[I

    invoke-virtual {v2}, Lcom/bachatas4/android/model/RuntimeErrorCode;->ordinal()I

    move-result v2

    aget v2, v3, v2

    const/4 v3, 0x2

    if-eq v2, v3, :cond_4

    const/4 v3, 0x3

    if-eq v2, v3, :cond_3

    .line 1070
    sget-object v2, Lcom/bachatas4/android/data/InstallErrorCode;->VERIFY_FAILED:Lcom/bachatas4/android/data/InstallErrorCode;

    goto :goto_0

    .line 1068
    :cond_3
    sget-object v2, Lcom/bachatas4/android/data/InstallErrorCode;->INSUFFICIENT_STORAGE:Lcom/bachatas4/android/data/InstallErrorCode;

    goto :goto_0

    .line 1069
    :cond_4
    sget-object v2, Lcom/bachatas4/android/data/InstallErrorCode;->PERMISSION_LOST:Lcom/bachatas4/android/data/InstallErrorCode;

    .line 1072
    :goto_0
    invoke-virtual {p1}, Ljava/lang/Throwable;->getMessage()Ljava/lang/String;

    move-result-object v3

    if-nez v3, :cond_5

    invoke-virtual {v0}, Lcom/bachatas4/android/data/ContentImportException;->getCode()Lcom/bachatas4/android/model/RuntimeErrorCode;

    move-result-object v0

    invoke-virtual {v0}, Lcom/bachatas4/android/model/RuntimeErrorCode;->name()Ljava/lang/String;

    move-result-object v3

    :cond_5
    invoke-static {v2, v3}, Lkotlin/TuplesKt;->to(Ljava/lang/Object;Ljava/lang/Object;)Lkotlin/Pair;

    move-result-object v0

    goto :goto_1

    .line 1074
    :cond_6
    sget-object v0, Lcom/bachatas4/android/data/InstallErrorCode;->UNKNOWN:Lcom/bachatas4/android/data/InstallErrorCode;

    invoke-virtual {p1}, Ljava/lang/Throwable;->getMessage()Ljava/lang/String;

    move-result-object v2

    if-nez v2, :cond_7

    invoke-virtual {p1}, Ljava/lang/Object;->getClass()Ljava/lang/Class;

    move-result-object v2

    invoke-virtual {v2}, Ljava/lang/Class;->getSimpleName()Ljava/lang/String;

    move-result-object v2

    :cond_7
    invoke-static {v0, v2}, Lkotlin/TuplesKt;->to(Ljava/lang/Object;Ljava/lang/Object;)Lkotlin/Pair;

    move-result-object v0

    .line 1064
    :goto_1
    invoke-virtual {v0}, Lkotlin/Pair;->component1()Ljava/lang/Object;

    move-result-object v2

    check-cast v2, Lcom/bachatas4/android/data/InstallErrorCode;

    invoke-virtual {v0}, Lkotlin/Pair;->component2()Ljava/lang/Object;

    move-result-object v0

    check-cast v0, Ljava/lang/String;

    .line 1076
    new-instance v3, Ljava/lang/StringBuilder;

    const-string v4, "install failed: "

    invoke-direct {v3, v4}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v3, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;

    move-result-object v3

    const-string v4, " "

    invoke-virtual {v3, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v3

    invoke-virtual {v3, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v3

    invoke-virtual {v3}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v3

    invoke-static {v1, v3, p1}, Landroid/util/Log;->e(Ljava/lang/String;Ljava/lang/String;Ljava/lang/Throwable;)I

    .line 1077
    sget-object p1, Lcom/bachatas4/android/data/ImportManager;->INSTANCE:Lcom/bachatas4/android/data/ImportManager;

    new-instance v1, Lcom/bachatas4/android/data/ImportProgress$Failed;

    invoke-direct {v1, v2, v0}, Lcom/bachatas4/android/data/ImportProgress$Failed;-><init>(Lcom/bachatas4/android/data/InstallErrorCode;Ljava/lang/String;)V

    check-cast v1, Lcom/bachatas4/android/data/ImportProgress;

    invoke-virtual {p1, v1}, Lcom/bachatas4/android/data/ImportManager;->update(Lcom/bachatas4/android/data/ImportProgress;)V

    .line 1078
    new-instance p1, Ljava/lang/StringBuilder;

    const-string v1, "Install failed: "

    invoke-direct {p1, v1}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {p1, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p1

    invoke-virtual {p1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p1

    const/4 v0, 0x0

    invoke-direct {p0, p1, v0}, Lcom/bachatas4/android/service/ImportService;->notifyDone(Ljava/lang/String;Z)V

    return-void

    .line 1059
    :cond_8
    :goto_2
    const-string p1, "import cancelled"

    invoke-static {v1, p1}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    .line 1060
    sget-object p1, Lcom/bachatas4/android/data/ImportManager;->INSTANCE:Lcom/bachatas4/android/data/ImportManager;

    new-instance v0, Lcom/bachatas4/android/data/ImportProgress$Failed;

    sget-object v1, Lcom/bachatas4/android/data/InstallErrorCode;->CANCELLED:Lcom/bachatas4/android/data/InstallErrorCode;

    const-string v2, "cancelled"

    invoke-direct {v0, v1, v2}, Lcom/bachatas4/android/data/ImportProgress$Failed;-><init>(Lcom/bachatas4/android/data/InstallErrorCode;Ljava/lang/String;)V

    check-cast v0, Lcom/bachatas4/android/data/ImportProgress;

    invoke-virtual {p1, v0}, Lcom/bachatas4/android/data/ImportManager;->update(Lcom/bachatas4/android/data/ImportProgress;)V

    .line 1061
    const-class p1, Landroid/app/NotificationManager;

    invoke-virtual {p0, p1}, Lcom/bachatas4/android/service/ImportService;->getSystemService(Ljava/lang/Class;)Ljava/lang/Object;

    move-result-object p0

    check-cast p0, Landroid/app/NotificationManager;

    const/16 p1, 0x2a

    invoke-virtual {p0, p1}, Landroid/app/NotificationManager;->cancel(I)V

    return-void
.end method

.method private final isOpenFdSeekable(Landroid/os/ParcelFileDescriptor;)Z
    .locals 2

    .line 919
    :try_start_0
    invoke-virtual {p1}, Landroid/os/ParcelFileDescriptor;->getFileDescriptor()Ljava/io/FileDescriptor;

    move-result-object p0

    sget p1, Landroid/system/OsConstants;->SEEK_CUR:I

    const-wide/16 v0, 0x0

    invoke-static {p0, v0, v1, p1}, Landroid/system/Os;->lseek(Ljava/io/FileDescriptor;JI)J
    :try_end_0
    .catch Ljava/lang/Exception; {:try_start_0 .. :try_end_0} :catch_0

    const/4 p0, 0x1

    return p0

    :catch_0
    const/4 p0, 0x0

    return p0
.end method

.method private final notifyDone(Ljava/lang/String;Z)V
    .locals 9

    .line 1087
    const-class v0, Landroid/app/NotificationManager;

    invoke-virtual {p0, v0}, Lcom/bachatas4/android/service/ImportService;->getSystemService(Ljava/lang/Class;)Ljava/lang/Object;

    move-result-object v0

    check-cast v0, Landroid/app/NotificationManager;

    const/16 v7, 0x10

    const/4 v8, 0x0

    const/4 v3, 0x0

    const/4 v4, 0x0

    const/4 v6, 0x0

    move-object v1, p0

    move-object v2, p1

    move v5, p2

    .line 1089
    invoke-static/range {v1 .. v8}, Lcom/bachatas4/android/service/ImportService;->buildNotification$default(Lcom/bachatas4/android/service/ImportService;Ljava/lang/String;IIZZILjava/lang/Object;)Landroid/app/Notification;

    move-result-object p0

    const/16 p1, 0x2a

    .line 1087
    invoke-virtual {v0, p1, p0}, Landroid/app/NotificationManager;->notify(ILandroid/app/Notification;)V

    return-void
.end method

.method static synthetic notifyDone$default(Lcom/bachatas4/android/service/ImportService;Ljava/lang/String;ZILjava/lang/Object;)V
    .locals 0

    and-int/lit8 p3, p3, 0x2

    if-eqz p3, :cond_0

    const/4 p2, 0x0

    .line 1086
    :cond_0
    invoke-direct {p0, p1, p2}, Lcom/bachatas4/android/service/ImportService;->notifyDone(Ljava/lang/String;Z)V

    return-void
.end method

.method private final runFolderImport(Ljava/lang/String;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;
    .locals 94
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

    move-object/from16 v1, p0

    move-object/from16 v8, p1

    move-object/from16 v0, p2

    const-string v9, "sce_sys/param.sfo"

    const-string v10, "games/"

    const-string v11, "folder persistable permission: "

    const-string v12, "folder tree scan done name="

    instance-of v2, v0, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;

    if-eqz v2, :cond_0

    move-object v2, v0

    check-cast v2, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;

    iget v3, v2, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->label:I

    const/high16 v4, -0x80000000

    and-int/2addr v3, v4

    if-eqz v3, :cond_0

    iget v0, v2, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->label:I

    sub-int/2addr v0, v4

    iput v0, v2, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->label:I

    goto :goto_0

    :cond_0
    new-instance v2, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;

    invoke-direct {v2, v1, v0}, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;-><init>(Lcom/bachatas4/android/service/ImportService;Lkotlin/coroutines/Continuation;)V

    :goto_0
    move-object v13, v2

    iget-object v0, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->result:Ljava/lang/Object;

    invoke-static {}, Lkotlin/coroutines/intrinsics/IntrinsicsKt;->getCOROUTINE_SUSPENDED()Ljava/lang/Object;

    move-result-object v14

    .line 177
    iget v2, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->label:I

    const-string v3, " files="

    const/4 v4, 0x4

    const/4 v5, 0x3

    const-string v6, "folder import finished (stopSelf)"

    const/4 v7, 0x2

    move-object/from16 v16, v9

    const-string v9, "getFilesDir(...)"

    move-object/from16 v17, v10

    const/4 v10, 0x1

    move-object/from16 v18, v11

    const-string v11, "BachataImport"

    if-eqz v2, :cond_5

    if-eq v2, v10, :cond_4

    if-eq v2, v7, :cond_3

    if-eq v2, v5, :cond_2

    if-ne v2, v4, :cond_1

    iget-boolean v2, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->Z$0:Z

    iget-object v2, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->L$12:Ljava/lang/Object;

    check-cast v2, Lcom/bachatas4/android/data/ContentImportResult;

    iget-object v2, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->L$11:Ljava/lang/Object;

    check-cast v2, Ljava/io/File;

    iget-object v2, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->L$10:Ljava/lang/Object;

    check-cast v2, Lcom/bachatas4/android/data/ResolvedGameMetadata;

    iget-object v3, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->L$9:Ljava/lang/Object;

    check-cast v3, Lcom/bachatas4/android/data/ParamSfoMetadata;

    iget-object v3, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->L$8:Ljava/lang/Object;

    check-cast v3, [B

    iget-object v3, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->L$7:Ljava/lang/Object;

    check-cast v3, Lcom/bachatas4/android/data/ContentTreeEntry;

    iget-object v3, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->L$6:Ljava/lang/Object;

    check-cast v3, Ljava/util/List;

    iget-object v3, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->L$5:Ljava/lang/Object;

    check-cast v3, Ljava/lang/String;

    iget-object v3, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->L$4:Ljava/lang/Object;

    check-cast v3, Landroid/net/Uri;

    iget-object v3, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->L$3:Ljava/lang/Object;

    check-cast v3, Lcom/bachatas4/android/data/InstallJob;

    iget-object v3, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->L$2:Ljava/lang/Object;

    check-cast v3, Lcom/bachatas4/android/data/InstallJobStore;

    iget-object v4, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->L$1:Ljava/lang/Object;

    check-cast v4, Ljava/lang/String;

    iget-object v5, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->L$0:Ljava/lang/Object;

    check-cast v5, Ljava/lang/String;

    :try_start_0
    invoke-static {v0}, Lkotlin/ResultKt;->throwOnFailure(Ljava/lang/Object;)V
    :try_end_0
    .catchall {:try_start_0 .. :try_end_0} :catchall_0

    move-object/from16 v61, v6

    move-object v12, v9

    move-object v10, v11

    const/16 p2, 0x0

    goto/16 :goto_15

    :catchall_0
    move-exception v0

    move-object v15, v4

    move-object v4, v6

    goto/16 :goto_1

    :cond_1
    new-instance v0, Ljava/lang/IllegalStateException;

    const-string v1, "call to \'resume\' before \'invoke\' with coroutine"

    invoke-direct {v0, v1}, Ljava/lang/IllegalStateException;-><init>(Ljava/lang/String;)V

    throw v0

    :cond_2
    iget-boolean v2, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->Z$0:Z

    iget-object v3, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->L$11:Ljava/lang/Object;

    check-cast v3, Ljava/io/File;

    iget-object v5, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->L$10:Ljava/lang/Object;

    check-cast v5, Lcom/bachatas4/android/data/ResolvedGameMetadata;

    iget-object v8, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->L$9:Ljava/lang/Object;

    check-cast v8, Lcom/bachatas4/android/data/ParamSfoMetadata;

    iget-object v10, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->L$8:Ljava/lang/Object;

    check-cast v10, [B

    iget-object v12, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->L$7:Ljava/lang/Object;

    check-cast v12, Lcom/bachatas4/android/data/ContentTreeEntry;

    iget-object v4, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->L$6:Ljava/lang/Object;

    check-cast v4, Ljava/util/List;

    iget-object v7, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->L$5:Ljava/lang/Object;

    check-cast v7, Ljava/lang/String;

    iget-object v15, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->L$4:Ljava/lang/Object;

    check-cast v15, Landroid/net/Uri;

    move-object/from16 v22, v0

    iget-object v0, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->L$3:Ljava/lang/Object;

    check-cast v0, Lcom/bachatas4/android/data/InstallJob;

    move-object/from16 p1, v0

    iget-object v0, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->L$2:Ljava/lang/Object;

    move-object/from16 v16, v0

    check-cast v16, Lcom/bachatas4/android/data/InstallJobStore;

    iget-object v0, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->L$1:Ljava/lang/Object;

    move-object/from16 v17, v0

    check-cast v17, Ljava/lang/String;

    iget-object v0, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->L$0:Ljava/lang/Object;

    check-cast v0, Ljava/lang/String;

    :try_start_1
    invoke-static/range {v22 .. v22}, Lkotlin/ResultKt;->throwOnFailure(Ljava/lang/Object;)V
    :try_end_1
    .catchall {:try_start_1 .. :try_end_1} :catchall_1

    move-object/from16 p2, v12

    move-object v12, v9

    move-object/from16 v9, v16

    move-object/from16 v16, p2

    move-object/from16 v62, p1

    move-object/from16 v30, v3

    move-object/from16 v61, v6

    move-object v6, v10

    move-object v10, v11

    move-object v11, v14

    move-object/from16 v29, v15

    move-object/from16 v15, v17

    const/16 p2, 0x0

    move v3, v2

    move-object v2, v5

    move-object v5, v0

    move-object/from16 v0, v22

    goto/16 :goto_13

    :catchall_1
    move-exception v0

    move-object v4, v6

    move-object v2, v9

    move-object v10, v11

    move-object/from16 v3, v16

    move-object/from16 v15, v17

    goto/16 :goto_22

    :cond_3
    move-object/from16 v22, v0

    iget-boolean v0, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->Z$0:Z

    iget-object v2, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->L$8:Ljava/lang/Object;

    check-cast v2, Lcom/bachatas4/android/data/ContentTreeEntry;

    iget-object v2, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->L$7:Ljava/lang/Object;

    check-cast v2, Lcom/bachatas4/android/data/ContentTreeEntry;

    iget-object v4, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->L$6:Ljava/lang/Object;

    check-cast v4, Ljava/util/List;

    iget-object v7, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->L$5:Ljava/lang/Object;

    check-cast v7, Ljava/lang/String;

    iget-object v8, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->L$4:Ljava/lang/Object;

    check-cast v8, Landroid/net/Uri;

    iget-object v10, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->L$3:Ljava/lang/Object;

    check-cast v10, Lcom/bachatas4/android/data/InstallJob;

    iget-object v12, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->L$2:Ljava/lang/Object;

    check-cast v12, Lcom/bachatas4/android/data/InstallJobStore;

    iget-object v15, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->L$1:Ljava/lang/Object;

    check-cast v15, Ljava/lang/String;

    iget-object v5, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->L$0:Ljava/lang/Object;

    check-cast v5, Ljava/lang/String;

    :try_start_2
    invoke-static/range {v22 .. v22}, Lkotlin/ResultKt;->throwOnFailure(Ljava/lang/Object;)V
    :try_end_2
    .catchall {:try_start_2 .. :try_end_2} :catchall_2

    move-object/from16 v61, v6

    move-object/from16 v30, v9

    move-object v6, v10

    move-object v10, v11

    move-object v11, v14

    move-object/from16 v58, v17

    const/16 p2, 0x0

    move v14, v0

    move-object v9, v3

    move-object v3, v12

    move-object/from16 v0, v22

    const/4 v12, 0x2

    goto/16 :goto_b

    :catchall_2
    move-exception v0

    move-object v4, v6

    move-object v2, v9

    move-object v10, v11

    move-object v3, v12

    goto/16 :goto_22

    :cond_4
    move-object/from16 v22, v0

    iget-boolean v0, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->Z$0:Z

    iget-object v2, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->L$4:Ljava/lang/Object;

    check-cast v2, Landroid/net/Uri;

    iget-object v4, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->L$3:Ljava/lang/Object;

    check-cast v4, Lcom/bachatas4/android/data/InstallJob;

    iget-object v5, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->L$2:Ljava/lang/Object;

    check-cast v5, Lcom/bachatas4/android/data/InstallJobStore;

    iget-object v7, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->L$1:Ljava/lang/Object;

    check-cast v7, Ljava/lang/String;

    iget-object v8, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->L$0:Ljava/lang/Object;

    check-cast v8, Ljava/lang/String;

    :try_start_3
    invoke-static/range {v22 .. v22}, Lkotlin/ResultKt;->throwOnFailure(Ljava/lang/Object;)V
    :try_end_3
    .catchall {:try_start_3 .. :try_end_3} :catchall_3

    move-object/from16 v60, v3

    move-object/from16 v27, v4

    move-object v15, v5

    move-object/from16 v61, v6

    move-object v10, v11

    move-object/from16 v56, v12

    move-object v11, v14

    move-object/from16 v59, v16

    move-object/from16 v58, v17

    const/16 p2, 0x0

    const/4 v12, 0x0

    move v14, v0

    move-object v4, v1

    move-object/from16 v16, v2

    move-object v2, v7

    move-object/from16 v0, v22

    goto/16 :goto_5

    :catchall_3
    move-exception v0

    move-object v3, v5

    move-object v4, v6

    move-object v15, v7

    :goto_1
    move-object v2, v9

    move-object v10, v11

    goto/16 :goto_22

    :cond_5
    move-object/from16 v22, v0

    invoke-static/range {v22 .. v22}, Lkotlin/ResultKt;->throwOnFailure(Ljava/lang/Object;)V

    .line 178
    new-instance v0, Ljava/lang/StringBuilder;

    const-string v2, "folder import prepare uri="

    invoke-direct {v0, v2}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v0, v8}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    invoke-static {v11, v0}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    move-object v2, v6

    const/4 v6, 0x6

    const/4 v7, 0x0

    move-object v4, v2

    .line 179
    const-string v2, "Validating folder\u2026"

    move-object v5, v3

    const/4 v3, 0x0

    move-object v15, v4

    const/4 v4, 0x0

    move-object/from16 v22, v5

    const/4 v5, 0x1

    const/16 v19, 0x4

    const/16 v23, 0x3

    invoke-static/range {v1 .. v7}, Lcom/bachatas4/android/service/ImportService;->updateNotification$default(Lcom/bachatas4/android/service/ImportService;Ljava/lang/String;IIZILjava/lang/Object;)V

    .line 180
    invoke-static {}, Ljava/util/UUID;->randomUUID()Ljava/util/UUID;

    move-result-object v0

    invoke-virtual {v0}, Ljava/util/UUID;->toString()Ljava/lang/String;

    move-result-object v2

    const-string v0, "toString(...)"

    invoke-static {v2, v0}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullExpressionValue(Ljava/lang/Object;Ljava/lang/String;)V

    .line 181
    new-instance v1, Lcom/bachatas4/android/data/InstallJobStore;

    invoke-virtual/range {p0 .. p0}, Lcom/bachatas4/android/service/ImportService;->getFilesDir()Ljava/io/File;

    move-result-object v0

    invoke-static {v0, v9}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullExpressionValue(Ljava/lang/Object;Ljava/lang/String;)V

    invoke-direct {v1, v0}, Lcom/bachatas4/android/data/InstallJobStore;-><init>(Ljava/io/File;)V

    .line 182
    new-instance v0, Lcom/bachatas4/android/data/InstallJob;

    move-object/from16 v3, v18

    move/from16 v4, v19

    .line 187
    invoke-static {}, Ljava/lang/System;->currentTimeMillis()J

    move-result-wide v18

    const/4 v5, 0x0

    .line 188
    invoke-static {}, Ljava/lang/System;->currentTimeMillis()J

    move-result-wide v20

    const v24, 0x33fe1

    const/16 v25, 0x0

    move-object v6, v1

    const/4 v1, 0x0

    move-object v7, v3

    .line 182
    const-string v3, "SELECTED"

    move/from16 v27, v4

    const-string v4, "folder"

    move-object/from16 v28, v6

    const/4 v6, 0x0

    move-object/from16 v29, v7

    const/4 v7, 0x0

    const/4 v8, 0x0

    move-object/from16 v30, v9

    const/4 v9, 0x0

    move/from16 v31, v10

    const/4 v10, 0x0

    move-object/from16 v32, v11

    const/4 v11, 0x0

    move-object/from16 v34, v12

    move-object/from16 v33, v13

    const-wide/16 v12, 0x0

    move-object/from16 v35, v14

    move-object/from16 v36, v15

    const-wide/16 v14, 0x0

    move-object/from16 v38, v16

    move-object/from16 v37, v17

    const-wide/16 v16, 0x0

    move-object/from16 v39, v22

    const/16 v22, 0x0

    move/from16 v40, v23

    const/16 v23, 0x0

    move/from16 p2, v5

    move-object/from16 v55, v28

    move-object/from16 v57, v29

    move-object/from16 v62, v30

    move-object/from16 v64, v32

    move-object/from16 v53, v33

    move-object/from16 v56, v34

    move-object/from16 v54, v35

    move-object/from16 v61, v36

    move-object/from16 v58, v37

    move-object/from16 v59, v38

    move-object/from16 v60, v39

    move-object/from16 v5, p1

    invoke-direct/range {v0 .. v25}, Lcom/bachatas4/android/data/InstallJob;-><init>(ILjava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;ZLjava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;JJJJJLjava/lang/String;Ljava/lang/String;ILkotlin/jvm/internal/DefaultConstructorMarker;)V

    move-object/from16 v6, v55

    .line 190
    invoke-virtual {v6, v0}, Lcom/bachatas4/android/data/InstallJobStore;->create(Lcom/bachatas4/android/data/InstallJob;)V

    .line 192
    :try_start_4
    sget-object v1, Lcom/bachatas4/android/data/ImportManager;->INSTANCE:Lcom/bachatas4/android/data/ImportManager;

    new-instance v3, Lcom/bachatas4/android/data/ImportProgress$Validating;

    const-string v4, "folder"

    invoke-direct {v3, v5, v4}, Lcom/bachatas4/android/data/ImportProgress$Validating;-><init>(Ljava/lang/String;Ljava/lang/String;)V

    check-cast v3, Lcom/bachatas4/android/data/ImportProgress;

    invoke-virtual {v1, v3}, Lcom/bachatas4/android/data/ImportManager;->update(Lcom/bachatas4/android/data/ImportProgress;)V

    .line 193
    const-string v30, "VALIDATING"

    invoke-static {}, Ljava/lang/System;->currentTimeMillis()J

    move-result-wide v47

    const v51, 0x37ffb

    const/16 v52, 0x0

    const/16 v28, 0x0

    const/16 v29, 0x0

    const/16 v31, 0x0

    const/16 v32, 0x0

    const/16 v33, 0x0

    const/16 v34, 0x0

    const/16 v35, 0x0

    const/16 v36, 0x0

    const/16 v37, 0x0

    const/16 v38, 0x0

    const-wide/16 v39, 0x0

    const-wide/16 v41, 0x0

    const-wide/16 v43, 0x0

    const-wide/16 v45, 0x0

    const/16 v49, 0x0

    const/16 v50, 0x0

    move-object/from16 v27, v0

    invoke-static/range {v27 .. v52}, Lcom/bachatas4/android/data/InstallJob;->copy$default(Lcom/bachatas4/android/data/InstallJob;ILjava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;ZLjava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;JJJJJLjava/lang/String;Ljava/lang/String;ILjava/lang/Object;)Lcom/bachatas4/android/data/InstallJob;

    move-result-object v1

    .line 194
    invoke-virtual {v6, v1}, Lcom/bachatas4/android/data/InstallJobStore;->update(Lcom/bachatas4/android/data/InstallJob;)V

    .line 196
    sget-object v0, Lcom/bachatas4/android/data/InstallValidator;->INSTANCE:Lcom/bachatas4/android/data/InstallValidator;

    invoke-virtual/range {p0 .. p0}, Lcom/bachatas4/android/service/ImportService;->getFilesDir()Ljava/io/File;

    move-result-object v3
    :try_end_4
    .catchall {:try_start_4 .. :try_end_4} :catchall_1c

    move-object/from16 v9, v62

    :try_start_5
    invoke-static {v3, v9}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullExpressionValue(Ljava/lang/Object;Ljava/lang/String;)V

    invoke-virtual {v0, v3}, Lcom/bachatas4/android/data/InstallValidator;->checkWritableGamesDir(Ljava/io/File;)Lcom/bachatas4/android/data/InstallErrorCode;

    move-result-object v0

    if-nez v0, :cond_18

    .line 200
    invoke-static {v5}, Landroid/net/Uri;->parse(Ljava/lang/String;)Landroid/net/Uri;

    move-result-object v3
    :try_end_5
    .catchall {:try_start_5 .. :try_end_5} :catchall_1b

    .line 201
    :try_start_6
    sget-object v0, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;
    :try_end_6
    .catchall {:try_start_6 .. :try_end_6} :catchall_6

    move-object/from16 v4, p0

    :try_start_7
    move-object v0, v4

    check-cast v0, Lcom/bachatas4/android/service/ImportService;

    .line 202
    invoke-virtual {v4}, Lcom/bachatas4/android/service/ImportService;->getContentResolver()Landroid/content/ContentResolver;

    move-result-object v0
    :try_end_7
    .catchall {:try_start_7 .. :try_end_7} :catchall_5

    const/4 v7, 0x1

    :try_start_8
    invoke-virtual {v0, v3, v7}, Landroid/content/ContentResolver;->takePersistableUriPermission(Landroid/net/Uri;I)V

    .line 203
    invoke-static {v7}, Lkotlin/coroutines/jvm/internal/Boxing;->boxBoolean(Z)Ljava/lang/Boolean;

    move-result-object v0

    .line 201
    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v0
    :try_end_8
    .catchall {:try_start_8 .. :try_end_8} :catchall_4

    goto :goto_3

    :catchall_4
    move-exception v0

    goto :goto_2

    :catchall_5
    move-exception v0

    const/4 v7, 0x1

    goto :goto_2

    :catchall_6
    move-exception v0

    const/4 v7, 0x1

    move-object/from16 v4, p0

    :goto_2
    :try_start_9
    sget-object v8, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    invoke-static {v0}, Lkotlin/ResultKt;->createFailure(Ljava/lang/Throwable;)Ljava/lang/Object;

    move-result-object v0

    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v0

    .line 204
    :goto_3
    invoke-static {v0}, Lkotlin/Result;->exceptionOrNull-impl(Ljava/lang/Object;)Ljava/lang/Throwable;

    move-result-object v8

    if-nez v8, :cond_6

    move-object/from16 v10, v64

    goto :goto_4

    .line 205
    :cond_6
    invoke-virtual {v8}, Ljava/lang/Throwable;->getMessage()Ljava/lang/String;

    move-result-object v0

    new-instance v8, Ljava/lang/StringBuilder;

    move-object/from16 v10, v57

    invoke-direct {v8, v10}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v8, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0
    :try_end_9
    .catchall {:try_start_9 .. :try_end_9} :catchall_19

    move-object/from16 v10, v64

    :try_start_a
    invoke-static {v10, v0}, Landroid/util/Log;->w(Ljava/lang/String;Ljava/lang/String;)I

    .line 206
    invoke-static/range {p2 .. p2}, Lkotlin/coroutines/jvm/internal/Boxing;->boxBoolean(Z)Ljava/lang/Boolean;

    move-result-object v0

    .line 204
    :goto_4
    check-cast v0, Ljava/lang/Boolean;

    invoke-virtual {v0}, Ljava/lang/Boolean;->booleanValue()Z

    move-result v71

    .line 208
    invoke-static {}, Ljava/lang/System;->currentTimeMillis()J

    move-result-wide v85

    const v89, 0x37fdf

    const/16 v90, 0x0

    const/16 v66, 0x0

    const/16 v67, 0x0

    const/16 v68, 0x0

    const/16 v69, 0x0

    const/16 v70, 0x0

    const/16 v72, 0x0

    const/16 v73, 0x0

    const/16 v74, 0x0

    const/16 v75, 0x0

    const/16 v76, 0x0

    const-wide/16 v77, 0x0

    const-wide/16 v79, 0x0

    const-wide/16 v81, 0x0

    const-wide/16 v83, 0x0

    const/16 v87, 0x0

    const/16 v88, 0x0

    move-object/from16 v65, v1

    invoke-static/range {v65 .. v90}, Lcom/bachatas4/android/data/InstallJob;->copy$default(Lcom/bachatas4/android/data/InstallJob;ILjava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;ZLjava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;JJJJJLjava/lang/String;Ljava/lang/String;ILjava/lang/Object;)Lcom/bachatas4/android/data/InstallJob;

    move-result-object v0

    move/from16 v1, v71

    .line 209
    invoke-virtual {v6, v0}, Lcom/bachatas4/android/data/InstallJobStore;->update(Lcom/bachatas4/android/data/InstallJob;)V

    .line 211
    const-string v8, "folder tree scan start"

    invoke-static {v10, v8}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    .line 212
    invoke-static {}, Lkotlinx/coroutines/Dispatchers;->getIO()Lkotlinx/coroutines/CoroutineDispatcher;

    move-result-object v8

    check-cast v8, Lkotlin/coroutines/CoroutineContext;

    new-instance v11, Lcom/bachatas4/android/service/ImportService$runFolderImport$3;

    const/4 v12, 0x0

    invoke-direct {v11, v4, v3, v12}, Lcom/bachatas4/android/service/ImportService$runFolderImport$3;-><init>(Lcom/bachatas4/android/service/ImportService;Landroid/net/Uri;Lkotlin/coroutines/Continuation;)V

    check-cast v11, Lkotlin/jvm/functions/Function2;

    move-object/from16 v13, v53

    iput-object v5, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->L$0:Ljava/lang/Object;

    iput-object v2, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->L$1:Ljava/lang/Object;

    iput-object v6, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->L$2:Ljava/lang/Object;

    iput-object v0, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->L$3:Ljava/lang/Object;

    invoke-static {v3}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v14

    iput-object v14, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->L$4:Ljava/lang/Object;

    iput-boolean v1, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->Z$0:Z

    iput v7, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->label:I

    invoke-static {v8, v11, v13}, Lkotlinx/coroutines/BuildersKt;->withContext(Lkotlin/coroutines/CoroutineContext;Lkotlin/jvm/functions/Function2;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;

    move-result-object v7
    :try_end_a
    .catchall {:try_start_a .. :try_end_a} :catchall_18

    move-object/from16 v11, v54

    if-ne v7, v11, :cond_7

    goto/16 :goto_14

    :cond_7
    move-object/from16 v27, v0

    move v14, v1

    move-object/from16 v16, v3

    move-object v8, v5

    move-object v15, v6

    move-object v0, v7

    :goto_5
    :try_start_b
    check-cast v0, Lkotlin/Pair;

    invoke-virtual {v0}, Lkotlin/Pair;->component1()Ljava/lang/Object;

    move-result-object v1

    check-cast v1, Ljava/lang/String;

    invoke-virtual {v0}, Lkotlin/Pair;->component2()Ljava/lang/Object;

    move-result-object v0

    check-cast v0, Ljava/util/List;

    .line 218
    invoke-interface {v0}, Ljava/util/List;->size()I

    move-result v3

    new-instance v5, Ljava/lang/StringBuilder;

    move-object/from16 v6, v56

    invoke-direct {v5, v6}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v5, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v5

    move-object/from16 v6, v60

    invoke-virtual {v5, v6}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v5

    invoke-virtual {v5, v3}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    move-result-object v3

    invoke-virtual {v3}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v3

    invoke-static {v10, v3}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    .line 220
    move-object v3, v0

    check-cast v3, Ljava/lang/Iterable;

    .line 1202
    instance-of v5, v3, Ljava/util/Collection;
    :try_end_b
    .catchall {:try_start_b .. :try_end_b} :catchall_17

    if-eqz v5, :cond_9

    :try_start_c
    move-object v5, v3

    check-cast v5, Ljava/util/Collection;

    invoke-interface {v5}, Ljava/util/Collection;->isEmpty()Z

    move-result v5
    :try_end_c
    .catchall {:try_start_c .. :try_end_c} :catchall_7

    if-nez v5, :cond_8

    goto :goto_6

    :cond_8
    move-object v5, v2

    move-object v1, v4

    move-object v2, v9

    move-object/from16 v4, v61

    goto/16 :goto_1c

    :catchall_7
    move-exception v0

    move-object v1, v4

    move-object v3, v15

    move-object/from16 v4, v61

    move-object v15, v2

    move-object v2, v9

    goto/16 :goto_22

    .line 1203
    :cond_9
    :goto_6
    :try_start_d
    invoke-interface {v3}, Ljava/lang/Iterable;->iterator()Ljava/util/Iterator;

    move-result-object v3

    :goto_7
    invoke-interface {v3}, Ljava/util/Iterator;->hasNext()Z

    move-result v5

    if-eqz v5, :cond_8

    invoke-interface {v3}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v5

    check-cast v5, Lcom/bachatas4/android/data/ContentTreeEntry;

    .line 220
    invoke-virtual {v5}, Lcom/bachatas4/android/data/ContentTreeEntry;->getRelativePath()Ljava/lang/String;

    move-result-object v5

    const-string v7, "eboot.bin"

    invoke-static {v5, v7}, Lkotlin/jvm/internal/Intrinsics;->areEqual(Ljava/lang/Object;Ljava/lang/Object;)Z

    move-result v5

    if-eqz v5, :cond_17

    .line 223
    move-object v3, v0

    check-cast v3, Ljava/lang/Iterable;

    .line 1205
    instance-of v5, v3, Ljava/util/Collection;
    :try_end_d
    .catchall {:try_start_d .. :try_end_d} :catchall_17

    if-eqz v5, :cond_b

    :try_start_e
    move-object v5, v3

    check-cast v5, Ljava/util/Collection;

    invoke-interface {v5}, Ljava/util/Collection;->isEmpty()Z

    move-result v5
    :try_end_e
    .catchall {:try_start_e .. :try_end_e} :catchall_7

    if-nez v5, :cond_a

    goto :goto_8

    :cond_a
    move-object v5, v2

    move-object v1, v4

    move-object v2, v9

    move-object/from16 v4, v61

    goto/16 :goto_1b

    .line 1206
    :cond_b
    :goto_8
    :try_start_f
    invoke-interface {v3}, Ljava/lang/Iterable;->iterator()Ljava/util/Iterator;

    move-result-object v3

    :goto_9
    invoke-interface {v3}, Ljava/util/Iterator;->hasNext()Z

    move-result v5

    if-eqz v5, :cond_a

    invoke-interface {v3}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v5

    check-cast v5, Lcom/bachatas4/android/data/ContentTreeEntry;

    .line 223
    invoke-virtual {v5}, Lcom/bachatas4/android/data/ContentTreeEntry;->getRelativePath()Ljava/lang/String;

    move-result-object v5

    move-object/from16 v7, v59

    invoke-static {v5, v7}, Lkotlin/jvm/internal/Intrinsics;->areEqual(Ljava/lang/Object;Ljava/lang/Object;)Z

    move-result v5
    :try_end_f
    .catchall {:try_start_f .. :try_end_f} :catchall_17

    if-eqz v5, :cond_16

    .line 227
    :try_start_10
    sget-object v3, Lcom/bachatas4/android/data/ImportManager;->INSTANCE:Lcom/bachatas4/android/data/ImportManager;

    new-instance v5, Lcom/bachatas4/android/data/ImportProgress$ReadingMetadata;

    invoke-direct {v5, v1, v12}, Lcom/bachatas4/android/data/ImportProgress$ReadingMetadata;-><init>(Ljava/lang/String;Ljava/lang/String;)V

    check-cast v5, Lcom/bachatas4/android/data/ImportProgress;

    invoke-virtual {v3, v5}, Lcom/bachatas4/android/data/ImportManager;->update(Lcom/bachatas4/android/data/ImportProgress;)V

    .line 229
    const-string v30, "READING_METADATA"

    .line 231
    invoke-static {}, Ljava/lang/System;->currentTimeMillis()J

    move-result-wide v47

    const v51, 0x37fbb

    const/16 v52, 0x0

    const/16 v28, 0x0

    const/16 v29, 0x0

    const/16 v31, 0x0

    const/16 v32, 0x0

    const/16 v33, 0x0

    const/16 v35, 0x0

    const/16 v36, 0x0

    const/16 v37, 0x0

    const/16 v38, 0x0

    const-wide/16 v39, 0x0

    const-wide/16 v41, 0x0

    const-wide/16 v43, 0x0

    const-wide/16 v45, 0x0

    const/16 v49, 0x0

    const/16 v50, 0x0

    move-object/from16 v34, v1

    .line 228
    invoke-static/range {v27 .. v52}, Lcom/bachatas4/android/data/InstallJob;->copy$default(Lcom/bachatas4/android/data/InstallJob;ILjava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;ZLjava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;JJJJJLjava/lang/String;Ljava/lang/String;ILjava/lang/Object;)Lcom/bachatas4/android/data/InstallJob;

    move-result-object v1

    .line 233
    invoke-virtual {v15, v1}, Lcom/bachatas4/android/data/InstallJobStore;->update(Lcom/bachatas4/android/data/InstallJob;)V
    :try_end_10
    .catchall {:try_start_10 .. :try_end_10} :catchall_15

    move-object v3, v2

    .line 234
    :try_start_11
    const-string v2, "Reading metadata\u2026"
    :try_end_11
    .catchall {:try_start_11 .. :try_end_11} :catchall_14

    move-object/from16 v22, v6

    const/4 v6, 0x6

    move-object/from16 v38, v7

    const/4 v7, 0x0

    move-object v5, v3

    const/4 v3, 0x0

    const/4 v4, 0x0

    move-object/from16 v17, v5

    const/4 v5, 0x1

    move-object/from16 v91, v1

    move-object/from16 v30, v9

    move-object/from16 v93, v17

    move-object/from16 v9, v22

    move-object/from16 v92, v34

    move-object/from16 v12, v38

    move-object/from16 v1, p0

    :try_start_12
    invoke-static/range {v1 .. v7}, Lcom/bachatas4/android/service/ImportService;->updateNotification$default(Lcom/bachatas4/android/service/ImportService;Ljava/lang/String;IIZILjava/lang/Object;)V

    .line 236
    move-object v2, v0

    check-cast v2, Ljava/lang/Iterable;

    .line 1208
    invoke-interface {v2}, Ljava/lang/Iterable;->iterator()Ljava/util/Iterator;

    move-result-object v2

    :cond_c
    invoke-interface {v2}, Ljava/util/Iterator;->hasNext()Z

    move-result v3
    :try_end_12
    .catchall {:try_start_12 .. :try_end_12} :catchall_13

    if-eqz v3, :cond_d

    :try_start_13
    invoke-interface {v2}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v3

    move-object v4, v3

    check-cast v4, Lcom/bachatas4/android/data/ContentTreeEntry;

    .line 236
    invoke-virtual {v4}, Lcom/bachatas4/android/data/ContentTreeEntry;->getRelativePath()Ljava/lang/String;

    move-result-object v4

    invoke-static {v4, v12}, Lkotlin/jvm/internal/Intrinsics;->areEqual(Ljava/lang/Object;Ljava/lang/Object;)Z

    move-result v4
    :try_end_13
    .catchall {:try_start_13 .. :try_end_13} :catchall_8

    if-eqz v4, :cond_c

    goto :goto_a

    :catchall_8
    move-exception v0

    move-object v3, v15

    move-object/from16 v2, v30

    move-object/from16 v4, v61

    move-object/from16 v15, v93

    goto/16 :goto_22

    :cond_d
    const/4 v3, 0x0

    :goto_a
    :try_start_14
    move-object v2, v3

    check-cast v2, Lcom/bachatas4/android/data/ContentTreeEntry;
    :try_end_14
    .catchall {:try_start_14 .. :try_end_14} :catchall_13

    if-eqz v2, :cond_f

    .line 238
    :try_start_15
    invoke-static {}, Lkotlinx/coroutines/Dispatchers;->getIO()Lkotlinx/coroutines/CoroutineDispatcher;

    move-result-object v3

    check-cast v3, Lkotlin/coroutines/CoroutineContext;

    new-instance v4, Lcom/bachatas4/android/service/ImportService$runFolderImport$sfoBytes$1$1;

    const/4 v12, 0x0

    invoke-direct {v4, v1, v2, v12}, Lcom/bachatas4/android/service/ImportService$runFolderImport$sfoBytes$1$1;-><init>(Lcom/bachatas4/android/service/ImportService;Lcom/bachatas4/android/data/ContentTreeEntry;Lkotlin/coroutines/Continuation;)V

    check-cast v4, Lkotlin/jvm/functions/Function2;

    iput-object v8, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->L$0:Ljava/lang/Object;
    :try_end_15
    .catchall {:try_start_15 .. :try_end_15} :catchall_b

    move-object/from16 v5, v93

    :try_start_16
    iput-object v5, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->L$1:Ljava/lang/Object;

    iput-object v15, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->L$2:Ljava/lang/Object;

    move-object/from16 v6, v91

    iput-object v6, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->L$3:Ljava/lang/Object;

    invoke-static/range {v16 .. v16}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v7

    iput-object v7, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->L$4:Ljava/lang/Object;

    move-object/from16 v7, v92

    iput-object v7, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->L$5:Ljava/lang/Object;

    iput-object v0, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->L$6:Ljava/lang/Object;

    invoke-static {v2}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v12

    iput-object v12, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->L$7:Ljava/lang/Object;

    invoke-static {v2}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v12

    iput-object v12, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->L$8:Ljava/lang/Object;

    iput-boolean v14, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->Z$0:Z

    const/4 v12, 0x2

    iput v12, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->label:I

    invoke-static {v3, v4, v13}, Lkotlinx/coroutines/BuildersKt;->withContext(Lkotlin/coroutines/CoroutineContext;Lkotlin/jvm/functions/Function2;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;

    move-result-object v3
    :try_end_16
    .catchall {:try_start_16 .. :try_end_16} :catchall_a

    if-ne v3, v11, :cond_e

    goto/16 :goto_14

    :cond_e
    move-object v4, v0

    move-object v0, v3

    move-object v3, v15

    move-object v15, v5

    move-object v5, v8

    move-object/from16 v8, v16

    .line 177
    :goto_b
    :try_start_17
    check-cast v0, [B

    move-object/from16 v62, v6

    move-object v6, v8

    move-object v8, v5

    :goto_c
    move-object/from16 v17, v7

    move-object v5, v2

    move v2, v14

    goto :goto_f

    :catchall_9
    move-exception v0

    move-object/from16 v2, v30

    :goto_d
    move-object/from16 v4, v61

    goto/16 :goto_22

    :catchall_a
    move-exception v0

    goto :goto_e

    :catchall_b
    move-exception v0

    move-object/from16 v5, v93

    :goto_e
    move-object v3, v15

    move-object/from16 v2, v30

    move-object/from16 v4, v61

    goto/16 :goto_1e

    :cond_f
    move-object/from16 v6, v91

    move-object/from16 v7, v92

    move-object/from16 v5, v93

    const/4 v12, 0x2

    move-object v4, v0

    move-object/from16 v62, v6

    move-object v3, v15

    move-object/from16 v6, v16

    const/4 v0, 0x0

    move-object v15, v5

    goto :goto_c

    :goto_f
    if-eqz v0, :cond_10

    .line 245
    sget-object v7, Lcom/bachatas4/android/data/ParamSfoReader;->INSTANCE:Lcom/bachatas4/android/data/ParamSfoReader;

    invoke-virtual {v7, v0}, Lcom/bachatas4/android/data/ParamSfoReader;->parse([B)Lcom/bachatas4/android/data/ParamSfoMetadata;

    move-result-object v7
    :try_end_17
    .catchall {:try_start_17 .. :try_end_17} :catchall_9

    move-object/from16 v18, v7

    goto :goto_10

    :cond_10
    const/16 v18, 0x0

    .line 246
    :goto_10
    :try_start_18
    sget-object v16, Lcom/bachatas4/android/data/GameMetadataResolver;->INSTANCE:Lcom/bachatas4/android/data/GameMetadataResolver;

    const/16 v20, 0x4

    const/16 v21, 0x0

    const/16 v19, 0x0

    invoke-static/range {v16 .. v21}, Lcom/bachatas4/android/data/GameMetadataResolver;->resolve$default(Lcom/bachatas4/android/data/GameMetadataResolver;Ljava/lang/String;Lcom/bachatas4/android/data/ParamSfoMetadata;Lkotlin/jvm/functions/Function0;ILjava/lang/Object;)Lcom/bachatas4/android/data/ResolvedGameMetadata;

    move-result-object v7

    move-object/from16 v14, v18

    .line 247
    invoke-virtual {v7}, Lcom/bachatas4/android/data/ResolvedGameMetadata;->getId()Ljava/lang/String;

    move-result-object v16

    check-cast v16, Ljava/lang/CharSequence;

    invoke-static/range {v16 .. v16}, Lkotlin/text/StringsKt;->isBlank(Ljava/lang/CharSequence;)Z

    move-result v16

    if-nez v16, :cond_15

    .line 250
    invoke-virtual {v7}, Lcom/bachatas4/android/data/ResolvedGameMetadata;->getId()Ljava/lang/String;

    move-result-object v12

    move-object/from16 p1, v0

    invoke-virtual {v7}, Lcom/bachatas4/android/data/ResolvedGameMetadata;->getTitle()Ljava/lang/String;

    move-result-object v0

    move-object/from16 v16, v5

    invoke-interface {v4}, Ljava/util/List;->size()I

    move-result v5

    move-object/from16 v29, v6

    new-instance v6, Ljava/lang/StringBuilder;

    invoke-direct {v6}, Ljava/lang/StringBuilder;-><init>()V

    move-object/from16 v21, v8

    const-string v8, "folder copy start id="

    invoke-virtual {v6, v8}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v6

    invoke-virtual {v6, v12}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v6

    const-string v8, " title="

    invoke-virtual {v6, v8}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v6

    invoke-virtual {v6, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0, v9}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0, v5}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    invoke-static {v10, v0}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    .line 252
    new-instance v0, Ljava/io/File;

    invoke-virtual {v1}, Lcom/bachatas4/android/service/ImportService;->getFilesDir()Ljava/io/File;

    move-result-object v5

    invoke-virtual {v7}, Lcom/bachatas4/android/data/ResolvedGameMetadata;->getId()Ljava/lang/String;

    move-result-object v6

    new-instance v8, Ljava/lang/StringBuilder;

    invoke-direct {v8}, Ljava/lang/StringBuilder;-><init>()V

    move-object/from16 v9, v58

    invoke-virtual {v8, v9}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v8

    invoke-virtual {v8, v6}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v6

    invoke-virtual {v6}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v6

    invoke-direct {v0, v5, v6}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    .line 253
    invoke-virtual {v0}, Ljava/io/File;->exists()Z

    move-result v5
    :try_end_18
    .catchall {:try_start_18 .. :try_end_18} :catchall_12

    if-eqz v5, :cond_12

    .line 254
    :try_start_19
    sget-object v5, Lcom/bachatas4/android/data/GameInstallVerifier;->INSTANCE:Lcom/bachatas4/android/data/GameInstallVerifier;

    invoke-virtual {v1}, Lcom/bachatas4/android/service/ImportService;->getFilesDir()Ljava/io/File;

    move-result-object v6
    :try_end_19
    .catchall {:try_start_19 .. :try_end_19} :catchall_d

    move-object/from16 v12, v30

    :try_start_1a
    invoke-static {v6, v12}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullExpressionValue(Ljava/lang/Object;Ljava/lang/String;)V

    invoke-virtual {v7}, Lcom/bachatas4/android/data/ResolvedGameMetadata;->getId()Ljava/lang/String;

    move-result-object v8

    move-object/from16 v30, v0

    new-instance v0, Ljava/lang/StringBuilder;

    invoke-direct {v0}, Ljava/lang/StringBuilder;-><init>()V

    invoke-virtual {v0, v9}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0, v8}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    invoke-virtual {v5, v6, v0}, Lcom/bachatas4/android/data/GameInstallVerifier;->canLaunch(Ljava/io/File;Ljava/lang/String;)Z

    move-result v0

    if-nez v0, :cond_11

    .line 258
    invoke-static/range {v30 .. v30}, Lkotlin/io/FilesKt;->deleteRecursively(Ljava/io/File;)Z

    goto :goto_12

    .line 255
    :cond_11
    sget-object v0, Lcom/bachatas4/android/data/InstallErrorCode;->ALREADY_INSTALLED:Lcom/bachatas4/android/data/InstallErrorCode;

    const-string v2, "Game already installed"

    invoke-direct {v1, v0, v2}, Lcom/bachatas4/android/service/ImportService;->failInstall(Lcom/bachatas4/android/data/InstallErrorCode;Ljava/lang/String;)Ljava/lang/Void;

    new-instance v0, Lkotlin/KotlinNothingValueException;

    invoke-direct {v0}, Lkotlin/KotlinNothingValueException;-><init>()V

    throw v0
    :try_end_1a
    .catchall {:try_start_1a .. :try_end_1a} :catchall_c

    :catchall_c
    move-exception v0

    goto :goto_11

    :catchall_d
    move-exception v0

    move-object/from16 v12, v30

    :goto_11
    move-object v2, v12

    goto/16 :goto_d

    :cond_12
    move-object/from16 v12, v30

    move-object/from16 v30, v0

    .line 262
    :goto_12
    :try_start_1b
    const-string v65, "COPYING"

    .line 263
    invoke-virtual {v7}, Lcom/bachatas4/android/data/ResolvedGameMetadata;->getId()Ljava/lang/String;

    move-result-object v71

    .line 264
    new-instance v0, Ljava/lang/StringBuilder;

    invoke-direct {v0}, Ljava/lang/StringBuilder;-><init>()V

    const-string v5, "games/.import-"

    invoke-virtual {v0, v5}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0, v15}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v72

    .line 265
    invoke-static {}, Ljava/lang/System;->currentTimeMillis()J

    move-result-wide v82

    const v86, 0x37cfb

    const/16 v87, 0x0

    const/16 v63, 0x0

    const/16 v64, 0x0

    const/16 v66, 0x0

    const/16 v67, 0x0

    const/16 v68, 0x0

    const/16 v69, 0x0

    const/16 v70, 0x0

    const/16 v73, 0x0

    const-wide/16 v74, 0x0

    const-wide/16 v76, 0x0

    const-wide/16 v78, 0x0

    const-wide/16 v80, 0x0

    const/16 v84, 0x0

    const/16 v85, 0x0

    .line 261
    invoke-static/range {v62 .. v87}, Lcom/bachatas4/android/data/InstallJob;->copy$default(Lcom/bachatas4/android/data/InstallJob;ILjava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;ZLjava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;JJJJJLjava/lang/String;Ljava/lang/String;ILjava/lang/Object;)Lcom/bachatas4/android/data/InstallJob;

    move-result-object v0

    .line 267
    invoke-virtual {v3, v0}, Lcom/bachatas4/android/data/InstallJobStore;->update(Lcom/bachatas4/android/data/InstallJob;)V

    .line 269
    invoke-virtual {v1}, Lcom/bachatas4/android/service/ImportService;->getContentImporter()Lcom/bachatas4/android/data/ContentImporter;

    move-result-object v5

    .line 270
    new-instance v18, Lcom/bachatas4/android/data/ContentImportRequest;

    .line 271
    invoke-virtual {v7}, Lcom/bachatas4/android/data/ResolvedGameMetadata;->getId()Ljava/lang/String;

    move-result-object v19

    .line 272
    invoke-virtual {v7}, Lcom/bachatas4/android/data/ResolvedGameMetadata;->getTitle()Ljava/lang/String;

    move-result-object v20

    .line 274
    invoke-virtual {v7}, Lcom/bachatas4/android/data/ResolvedGameMetadata;->getSubtitle()Ljava/lang/String;

    move-result-object v24

    .line 275
    invoke-virtual {v7}, Lcom/bachatas4/android/data/ResolvedGameMetadata;->getDetail()Ljava/lang/String;

    move-result-object v25

    const/16 v26, 0x18

    const/16 v27, 0x0

    const/16 v22, 0x0

    const/16 v23, 0x0

    .line 270
    invoke-direct/range {v18 .. v27}, Lcom/bachatas4/android/data/ContentImportRequest;-><init>(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/Long;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;ILkotlin/jvm/internal/DefaultConstructorMarker;)V

    move-object/from16 v6, v18

    move-object/from16 v8, v21

    .line 269
    new-instance v9, Lcom/bachatas4/android/service/ImportService$$ExternalSyntheticLambda1;

    invoke-direct {v9, v7, v1}, Lcom/bachatas4/android/service/ImportService$$ExternalSyntheticLambda1;-><init>(Lcom/bachatas4/android/data/ResolvedGameMetadata;Lcom/bachatas4/android/service/ImportService;)V

    iput-object v8, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->L$0:Ljava/lang/Object;

    iput-object v15, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->L$1:Ljava/lang/Object;

    iput-object v3, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->L$2:Ljava/lang/Object;

    iput-object v0, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->L$3:Ljava/lang/Object;

    move-object/from16 v18, v0

    invoke-static/range {v29 .. v29}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v0

    iput-object v0, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->L$4:Ljava/lang/Object;

    invoke-static/range {v17 .. v17}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v0

    iput-object v0, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->L$5:Ljava/lang/Object;

    invoke-static {v4}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v0

    iput-object v0, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->L$6:Ljava/lang/Object;

    invoke-static/range {v16 .. v16}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v0

    iput-object v0, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->L$7:Ljava/lang/Object;

    invoke-static/range {p1 .. p1}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v0

    iput-object v0, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->L$8:Ljava/lang/Object;

    invoke-static {v14}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v0

    iput-object v0, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->L$9:Ljava/lang/Object;

    iput-object v7, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->L$10:Ljava/lang/Object;

    invoke-static/range {v30 .. v30}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v0

    iput-object v0, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->L$11:Ljava/lang/Object;

    iput-boolean v2, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->Z$0:Z

    move v0, v2

    const/4 v2, 0x3

    iput v2, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->label:I

    invoke-virtual {v5, v6, v4, v9, v13}, Lcom/bachatas4/android/data/ContentImporter;->importGameTree(Lcom/bachatas4/android/data/ContentImportRequest;Ljava/util/List;Lkotlin/jvm/functions/Function3;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;

    move-result-object v2
    :try_end_1b
    .catchall {:try_start_1b .. :try_end_1b} :catchall_10

    if-ne v2, v11, :cond_13

    goto/16 :goto_14

    :cond_13
    move-object/from16 v6, p1

    move-object v9, v3

    move-object v5, v8

    move-object v8, v14

    move-object/from16 v62, v18

    move v3, v0

    move-object v0, v2

    move-object v2, v7

    move-object/from16 v7, v17

    .line 177
    :goto_13
    :try_start_1c
    check-cast v0, Lcom/bachatas4/android/data/ContentImportResult;

    .line 302
    sget-object v14, Lcom/bachatas4/android/data/ImportManager;->INSTANCE:Lcom/bachatas4/android/data/ImportManager;

    move-object/from16 p1, v0

    new-instance v0, Lcom/bachatas4/android/data/ImportProgress$Verifying;

    move-object/from16 v17, v4

    invoke-virtual {v2}, Lcom/bachatas4/android/data/ResolvedGameMetadata;->getTitle()Ljava/lang/String;

    move-result-object v4

    invoke-direct {v0, v4}, Lcom/bachatas4/android/data/ImportProgress$Verifying;-><init>(Ljava/lang/String;)V

    check-cast v0, Lcom/bachatas4/android/data/ImportProgress;

    invoke-virtual {v14, v0}, Lcom/bachatas4/android/data/ImportManager;->update(Lcom/bachatas4/android/data/ImportProgress;)V

    .line 303
    sget-object v0, Lcom/bachatas4/android/data/ImportManager;->INSTANCE:Lcom/bachatas4/android/data/ImportManager;

    new-instance v4, Lcom/bachatas4/android/data/ImportProgress$Registering;

    invoke-virtual {v2}, Lcom/bachatas4/android/data/ResolvedGameMetadata;->getTitle()Ljava/lang/String;

    move-result-object v14

    invoke-direct {v4, v14}, Lcom/bachatas4/android/data/ImportProgress$Registering;-><init>(Ljava/lang/String;)V

    check-cast v4, Lcom/bachatas4/android/data/ImportProgress;

    invoke-virtual {v0, v4}, Lcom/bachatas4/android/data/ImportManager;->update(Lcom/bachatas4/android/data/ImportProgress;)V

    .line 304
    const-string v65, "REGISTERING"

    invoke-static {}, Ljava/lang/System;->currentTimeMillis()J

    move-result-wide v82

    const v86, 0x37ffb

    const/16 v87, 0x0

    const/16 v63, 0x0

    const/16 v64, 0x0

    const/16 v66, 0x0

    const/16 v67, 0x0

    const/16 v68, 0x0

    const/16 v69, 0x0

    const/16 v70, 0x0

    const/16 v71, 0x0

    const/16 v72, 0x0

    const/16 v73, 0x0

    const-wide/16 v74, 0x0

    const-wide/16 v76, 0x0

    const-wide/16 v78, 0x0

    const-wide/16 v80, 0x0

    const/16 v84, 0x0

    const/16 v85, 0x0

    invoke-static/range {v62 .. v87}, Lcom/bachatas4/android/data/InstallJob;->copy$default(Lcom/bachatas4/android/data/InstallJob;ILjava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;ZLjava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;JJJJJLjava/lang/String;Ljava/lang/String;ILjava/lang/Object;)Lcom/bachatas4/android/data/InstallJob;

    move-result-object v0

    .line 305
    invoke-virtual {v9, v0}, Lcom/bachatas4/android/data/InstallJobStore;->update(Lcom/bachatas4/android/data/InstallJob;)V

    .line 307
    invoke-virtual {v1}, Lcom/bachatas4/android/service/ImportService;->getGameRepository()Lcom/bachatas4/android/data/GameRepository;

    move-result-object v4

    move-object/from16 v18, v6

    move-object v14, v7

    invoke-static {}, Ljava/lang/System;->currentTimeMillis()J

    move-result-wide v6

    move-object/from16 v19, v0

    invoke-static {v5}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v0

    iput-object v0, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->L$0:Ljava/lang/Object;

    iput-object v15, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->L$1:Ljava/lang/Object;

    iput-object v9, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->L$2:Ljava/lang/Object;

    invoke-static/range {v19 .. v19}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v0

    iput-object v0, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->L$3:Ljava/lang/Object;

    invoke-static/range {v29 .. v29}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v0

    iput-object v0, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->L$4:Ljava/lang/Object;

    invoke-static {v14}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v0

    iput-object v0, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->L$5:Ljava/lang/Object;

    invoke-static/range {v17 .. v17}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v0

    iput-object v0, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->L$6:Ljava/lang/Object;

    invoke-static/range {v16 .. v16}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v0

    iput-object v0, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->L$7:Ljava/lang/Object;

    invoke-static/range {v18 .. v18}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v0

    iput-object v0, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->L$8:Ljava/lang/Object;

    invoke-static {v8}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v0

    iput-object v0, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->L$9:Ljava/lang/Object;

    iput-object v2, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->L$10:Ljava/lang/Object;

    invoke-static/range {v30 .. v30}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v0

    iput-object v0, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->L$11:Ljava/lang/Object;

    invoke-static/range {p1 .. p1}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v0

    iput-object v0, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->L$12:Ljava/lang/Object;

    iput-boolean v3, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->Z$0:Z

    const/4 v3, 0x4

    iput v3, v13, Lcom/bachatas4/android/service/ImportService$runFolderImport$1;->label:I

    move-object v3, v4

    move-object v8, v13

    move-object/from16 v4, p1

    invoke-virtual/range {v3 .. v8}, Lcom/bachatas4/android/data/GameRepository;->addImportedGame(Lcom/bachatas4/android/data/ContentImportResult;Ljava/lang/String;JLkotlin/coroutines/Continuation;)Ljava/lang/Object;

    move-result-object v0
    :try_end_1c
    .catchall {:try_start_1c .. :try_end_1c} :catchall_f

    if-ne v0, v11, :cond_14

    :goto_14
    return-object v11

    :cond_14
    move-object v3, v9

    move-object v4, v15

    .line 308
    :goto_15
    :try_start_1d
    invoke-virtual {v3, v4}, Lcom/bachatas4/android/data/InstallJobStore;->delete(Ljava/lang/String;)V

    .line 309
    sget-object v0, Lcom/bachatas4/android/data/ImportManager;->INSTANCE:Lcom/bachatas4/android/data/ImportManager;

    new-instance v5, Lcom/bachatas4/android/data/ImportProgress$Installed;

    invoke-virtual {v2}, Lcom/bachatas4/android/data/ResolvedGameMetadata;->getId()Ljava/lang/String;

    move-result-object v6

    invoke-virtual {v2}, Lcom/bachatas4/android/data/ResolvedGameMetadata;->getTitle()Ljava/lang/String;

    move-result-object v7

    invoke-direct {v5, v6, v7}, Lcom/bachatas4/android/data/ImportProgress$Installed;-><init>(Ljava/lang/String;Ljava/lang/String;)V

    check-cast v5, Lcom/bachatas4/android/data/ImportProgress;

    invoke-virtual {v0, v5}, Lcom/bachatas4/android/data/ImportManager;->update(Lcom/bachatas4/android/data/ImportProgress;)V

    .line 310
    invoke-virtual {v2}, Lcom/bachatas4/android/data/ResolvedGameMetadata;->getId()Ljava/lang/String;

    move-result-object v0

    new-instance v5, Ljava/lang/StringBuilder;

    invoke-direct {v5}, Ljava/lang/StringBuilder;-><init>()V

    const-string v6, "folder import success id="

    invoke-virtual {v5, v6}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v5

    invoke-virtual {v5, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    invoke-static {v10, v0}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    .line 311
    invoke-virtual {v2}, Lcom/bachatas4/android/data/ResolvedGameMetadata;->getTitle()Ljava/lang/String;

    move-result-object v0

    new-instance v2, Ljava/lang/StringBuilder;

    invoke-direct {v2}, Ljava/lang/StringBuilder;-><init>()V

    invoke-virtual {v2, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    const-string v2, " installed"

    invoke-virtual {v0, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    move/from16 v6, p2

    const/4 v2, 0x2

    const/4 v13, 0x0

    invoke-static {v1, v0, v6, v2, v13}, Lcom/bachatas4/android/service/ImportService;->notifyDone$default(Lcom/bachatas4/android/service/ImportService;Ljava/lang/String;ZILjava/lang/Object;)V
    :try_end_1d
    .catchall {:try_start_1d .. :try_end_1d} :catchall_e

    move-object/from16 v2, v61

    .line 316
    invoke-static {v10, v2}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    goto/16 :goto_23

    :catchall_e
    move-exception v0

    move-object/from16 v2, v61

    move-object v15, v4

    :goto_16
    move-object v4, v2

    goto :goto_17

    :catchall_f
    move-exception v0

    move-object/from16 v2, v61

    move-object v4, v2

    move-object v3, v9

    :goto_17
    move-object v2, v12

    goto/16 :goto_22

    :catchall_10
    move-exception v0

    goto :goto_18

    :cond_15
    move-object/from16 v12, v30

    move-object/from16 v2, v61

    .line 248
    :try_start_1e
    sget-object v0, Lcom/bachatas4/android/data/InstallErrorCode;->NO_TITLE_ID:Lcom/bachatas4/android/data/InstallErrorCode;

    const-string v4, "Could not determine game title id"

    invoke-direct {v1, v0, v4}, Lcom/bachatas4/android/service/ImportService;->failInstall(Lcom/bachatas4/android/data/InstallErrorCode;Ljava/lang/String;)Ljava/lang/Void;

    new-instance v0, Lkotlin/KotlinNothingValueException;

    invoke-direct {v0}, Lkotlin/KotlinNothingValueException;-><init>()V

    throw v0
    :try_end_1e
    .catchall {:try_start_1e .. :try_end_1e} :catchall_11

    :catchall_11
    move-exception v0

    goto :goto_16

    :catchall_12
    move-exception v0

    move-object/from16 v12, v30

    :goto_18
    move-object/from16 v2, v61

    goto :goto_16

    :catchall_13
    move-exception v0

    move-object/from16 v12, v30

    move-object/from16 v2, v61

    move-object/from16 v5, v93

    goto :goto_1a

    :catchall_14
    move-exception v0

    move-object v5, v3

    goto :goto_19

    :catchall_15
    move-exception v0

    move-object v5, v2

    :goto_19
    move-object v1, v4

    move-object v12, v9

    move-object/from16 v2, v61

    :goto_1a
    move-object v4, v2

    move-object v2, v12

    goto :goto_1d

    :cond_16
    move-object v5, v2

    move-object v2, v9

    move-object/from16 v33, v13

    move-object v13, v12

    move-object v12, v7

    move-object v7, v1

    move-object v1, v4

    move-object v2, v5

    move-object v1, v7

    move-object/from16 v59, v12

    move-object v12, v13

    move-object/from16 v13, v33

    goto/16 :goto_9

    .line 224
    :goto_1b
    :try_start_1f
    sget-object v0, Lcom/bachatas4/android/data/InstallErrorCode;->VERIFY_FAILED:Lcom/bachatas4/android/data/InstallErrorCode;

    const-string v3, "Selected folder has no sce_sys/param.sfo"

    invoke-direct {v1, v0, v3}, Lcom/bachatas4/android/service/ImportService;->failInstall(Lcom/bachatas4/android/data/InstallErrorCode;Ljava/lang/String;)Ljava/lang/Void;

    new-instance v0, Lkotlin/KotlinNothingValueException;

    invoke-direct {v0}, Lkotlin/KotlinNothingValueException;-><init>()V

    throw v0

    :cond_17
    move-object v7, v1

    move-object v5, v2

    move-object v1, v4

    move-object v2, v9

    move-object/from16 v33, v13

    move-object v13, v12

    move-object v2, v5

    move-object v1, v7

    move-object/from16 v13, v33

    goto/16 :goto_7

    .line 221
    :goto_1c
    sget-object v0, Lcom/bachatas4/android/data/InstallErrorCode;->VERIFY_FAILED:Lcom/bachatas4/android/data/InstallErrorCode;

    const-string v3, "Selected folder has no eboot.bin"

    invoke-direct {v1, v0, v3}, Lcom/bachatas4/android/service/ImportService;->failInstall(Lcom/bachatas4/android/data/InstallErrorCode;Ljava/lang/String;)Ljava/lang/Void;

    new-instance v0, Lkotlin/KotlinNothingValueException;

    invoke-direct {v0}, Lkotlin/KotlinNothingValueException;-><init>()V

    throw v0
    :try_end_1f
    .catchall {:try_start_1f .. :try_end_1f} :catchall_16

    :catchall_16
    move-exception v0

    goto :goto_1d

    :catchall_17
    move-exception v0

    move-object v5, v2

    move-object v1, v4

    move-object v2, v9

    move-object/from16 v4, v61

    :goto_1d
    move-object v3, v15

    :goto_1e
    move-object v15, v5

    goto :goto_22

    :catchall_18
    move-exception v0

    move-object v3, v2

    move-object v1, v4

    move-object v2, v9

    move-object/from16 v4, v61

    goto :goto_21

    :catchall_19
    move-exception v0

    move-object v3, v2

    move-object v1, v4

    goto :goto_1f

    :cond_18
    move-object/from16 v1, p0

    move-object v3, v2

    move-object v2, v9

    move-object/from16 v4, v61

    move-object/from16 v10, v64

    .line 197
    :try_start_20
    const-string v5, "Games directory is not writable"

    invoke-direct {v1, v0, v5}, Lcom/bachatas4/android/service/ImportService;->failInstall(Lcom/bachatas4/android/data/InstallErrorCode;Ljava/lang/String;)Ljava/lang/Void;

    new-instance v0, Lkotlin/KotlinNothingValueException;

    invoke-direct {v0}, Lkotlin/KotlinNothingValueException;-><init>()V

    throw v0
    :try_end_20
    .catchall {:try_start_20 .. :try_end_20} :catchall_1a

    :catchall_1a
    move-exception v0

    goto :goto_21

    :catchall_1b
    move-exception v0

    move-object/from16 v1, p0

    move-object v3, v2

    :goto_1f
    move-object v2, v9

    move-object/from16 v4, v61

    goto :goto_20

    :catchall_1c
    move-exception v0

    move-object/from16 v1, p0

    move-object v3, v2

    move-object/from16 v4, v61

    move-object/from16 v2, v62

    :goto_20
    move-object/from16 v10, v64

    :goto_21
    move-object v15, v3

    move-object v3, v6

    .line 313
    :goto_22
    :try_start_21
    new-instance v5, Lcom/bachatas4/android/data/InstallCleanup;

    invoke-virtual {v1}, Lcom/bachatas4/android/service/ImportService;->getFilesDir()Ljava/io/File;

    move-result-object v6

    invoke-static {v6, v2}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullExpressionValue(Ljava/lang/Object;Ljava/lang/String;)V

    invoke-direct {v5, v6, v3}, Lcom/bachatas4/android/data/InstallCleanup;-><init>(Ljava/io/File;Lcom/bachatas4/android/data/InstallJobStore;)V

    invoke-virtual {v5, v15}, Lcom/bachatas4/android/data/InstallCleanup;->cleanupJob(Ljava/lang/String;)V

    .line 314
    invoke-direct {v1, v0}, Lcom/bachatas4/android/service/ImportService;->handleFailure(Ljava/lang/Throwable;)V
    :try_end_21
    .catchall {:try_start_21 .. :try_end_21} :catchall_1d

    .line 316
    invoke-static {v10, v4}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    .line 317
    :goto_23
    invoke-virtual {v1}, Lcom/bachatas4/android/service/ImportService;->stopSelf()V

    .line 319
    sget-object v0, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;

    return-object v0

    :catchall_1d
    move-exception v0

    .line 316
    invoke-static {v10, v4}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    .line 317
    invoke-virtual {v1}, Lcom/bachatas4/android/service/ImportService;->stopSelf()V

    throw v0
.end method

.method static final runFolderImport$lambda$8(Lcom/bachatas4/android/data/ResolvedGameMetadata;Lcom/bachatas4/android/service/ImportService;JJLjava/lang/String;)Lkotlin/Unit;
    .locals 8

    const-string v0, "currentFile"

    invoke-static {p6, v0}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullParameter(Ljava/lang/Object;Ljava/lang/String;)V

    .line 279
    sget-object v0, Lcom/bachatas4/android/data/ImportManager;->INSTANCE:Lcom/bachatas4/android/data/ImportManager;

    .line 280
    new-instance v1, Lcom/bachatas4/android/data/ImportProgress$Copying;

    .line 284
    invoke-virtual {p0}, Lcom/bachatas4/android/data/ResolvedGameMetadata;->getTitle()Ljava/lang/String;

    move-result-object v7

    move-wide v2, p2

    move-wide v4, p4

    move-object v6, p6

    .line 280
    invoke-direct/range {v1 .. v7}, Lcom/bachatas4/android/data/ImportProgress$Copying;-><init>(JJLjava/lang/String;Ljava/lang/String;)V

    check-cast v1, Lcom/bachatas4/android/data/ImportProgress;

    .line 279
    invoke-virtual {v0, v1}, Lcom/bachatas4/android/data/ImportManager;->update(Lcom/bachatas4/android/data/ImportProgress;)V

    .line 287
    sget-object p2, Lcom/bachatas4/android/service/ImportService;->Companion:Lcom/bachatas4/android/service/ImportService$Companion;

    invoke-virtual {p2, v2, v3, v4, v5}, Lcom/bachatas4/android/service/ImportService$Companion;->scaledProgress(JJ)Lkotlin/Pair;

    move-result-object p3

    invoke-virtual {p3}, Lkotlin/Pair;->component1()Ljava/lang/Object;

    move-result-object p4

    check-cast p4, Ljava/lang/Number;

    invoke-virtual {p4}, Ljava/lang/Number;->intValue()I

    move-result p4

    invoke-virtual {p3}, Lkotlin/Pair;->component2()Ljava/lang/Object;

    move-result-object p3

    check-cast p3, Ljava/lang/Number;

    invoke-virtual {p3}, Ljava/lang/Number;->intValue()I

    move-result p3

    const-wide/16 p5, 0x0

    cmp-long p5, v4, p5

    if-lez p5, :cond_0

    .line 289
    invoke-virtual {p2, v2, v3}, Lcom/bachatas4/android/service/ImportService$Companion;->formatBytes(J)Ljava/lang/String;

    move-result-object p5

    invoke-virtual {p2, v4, v5}, Lcom/bachatas4/android/service/ImportService$Companion;->formatBytes(J)Ljava/lang/String;

    move-result-object p2

    new-instance p6, Ljava/lang/StringBuilder;

    invoke-direct {p6}, Ljava/lang/StringBuilder;-><init>()V

    invoke-virtual {p6, p5}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p5

    const-string p6, " / "

    invoke-virtual {p5, p6}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p5

    invoke-virtual {p5, p2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p2

    invoke-virtual {p2}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p2

    goto :goto_0

    .line 291
    :cond_0
    invoke-virtual {p2, v2, v3}, Lcom/bachatas4/android/service/ImportService$Companion;->formatBytes(J)Ljava/lang/String;

    move-result-object p2

    .line 294
    :goto_0
    invoke-virtual {p0}, Lcom/bachatas4/android/data/ResolvedGameMetadata;->getTitle()Ljava/lang/String;

    move-result-object p0

    new-instance p5, Ljava/lang/StringBuilder;

    const-string p6, "Importing "

    invoke-direct {p5, p6}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {p5, p0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p0

    const-string p5, " \u00b7 "

    invoke-virtual {p0, p5}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p0

    invoke-virtual {p0, p2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p0

    invoke-virtual {p0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p0

    if-nez p4, :cond_1

    const/4 p2, 0x1

    goto :goto_1

    :cond_1
    const/4 p2, 0x0

    .line 293
    :goto_1
    invoke-direct {p1, p0, p4, p3, p2}, Lcom/bachatas4/android/service/ImportService;->updateNotification(Ljava/lang/String;IIZ)V

    .line 299
    sget-object p0, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;

    return-object p0
.end method

.method private final runPkgBatchImport(Ljava/lang/String;Ljava/util/List;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;
    .locals 141
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "(",
            "Ljava/lang/String;",
            "Ljava/util/List<",
            "Ljava/lang/String;",
            ">;",
            "Lkotlin/coroutines/Continuation<",
            "-",
            "Lkotlin/Unit;",
            ">;)",
            "Ljava/lang/Object;"
        }
    .end annotation

    move-object/from16 v1, p0

    move-object/from16 v0, p1

    move-object/from16 v2, p3

    const-string v8, "-"

    const-string v9, "games/"

    instance-of v3, v2, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;

    if-eqz v3, :cond_0

    move-object v3, v2

    check-cast v3, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;

    iget v4, v3, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->label:I

    const/high16 v5, -0x80000000

    and-int/2addr v4, v5

    if-eqz v4, :cond_0

    iget v2, v3, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->label:I

    sub-int/2addr v2, v5

    iput v2, v3, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->label:I

    goto :goto_0

    :cond_0
    new-instance v3, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;

    invoke-direct {v3, v1, v2}, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;-><init>(Lcom/bachatas4/android/service/ImportService;Lkotlin/coroutines/Continuation;)V

    :goto_0
    move-object v10, v3

    iget-object v2, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->result:Ljava/lang/Object;

    invoke-static {}, Lkotlin/coroutines/intrinsics/IntrinsicsKt;->getCOROUTINE_SUSPENDED()Ljava/lang/Object;

    move-result-object v11

    .line 675
    iget v3, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->label:I

    const-string v12, "00000000000000000000000000000000"

    const-string v13, "r"

    const-string v15, "cancelled"

    const-string v6, "/"

    const-string v7, "pkg batch finished completed="

    const-string v14, "BachataImport"

    move/from16 v16, v3

    packed-switch v16, :pswitch_data_0

    new-instance v0, Ljava/lang/IllegalStateException;

    const-string v1, "call to \'resume\' before \'invoke\' with coroutine"

    invoke-direct {v0, v1}, Ljava/lang/IllegalStateException;-><init>(Ljava/lang/String;)V

    throw v0

    :pswitch_0
    iget-wide v4, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->J$3:J

    iget-wide v4, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->J$2:J

    iget-wide v4, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->J$1:J

    iget-wide v4, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->J$0:J

    iget v4, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->I$0:I

    iget-object v0, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$11:Ljava/lang/Object;

    check-cast v0, Lcom/bachatas4/android/data/InstallManifest;

    iget-object v0, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$10:Ljava/lang/Object;

    check-cast v0, Ljava/util/List;

    iget-object v0, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$9:Ljava/lang/Object;

    check-cast v0, Ljava/lang/String;

    iget-object v5, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$8:Ljava/lang/Object;

    check-cast v5, Lcom/bachatas4/android/model/Game;

    iget-object v5, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$7:Ljava/lang/Object;

    check-cast v5, Ljava/util/List;

    iget-object v8, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$6:Ljava/lang/Object;

    check-cast v8, Ljava/util/List;

    iget-object v9, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$5:Ljava/lang/Object;

    check-cast v9, Ljava/util/List;

    iget-object v11, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$4:Ljava/lang/Object;

    check-cast v11, Ljava/io/File;

    iget-object v11, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$3:Ljava/lang/Object;

    check-cast v11, Ljava/io/File;

    iget-object v11, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$2:Ljava/lang/Object;

    check-cast v11, Ljava/lang/String;

    iget-object v11, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$1:Ljava/lang/Object;

    check-cast v11, Ljava/util/List;

    iget-object v10, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$0:Ljava/lang/Object;

    check-cast v10, Ljava/lang/String;

    :try_start_0
    invoke-static {v2}, Lkotlin/ResultKt;->throwOnFailure(Ljava/lang/Object;)V
    :try_end_0
    .catchall {:try_start_0 .. :try_end_0} :catchall_0

    move-object/from16 v53, v11

    move-object v11, v9

    move-object/from16 v9, v53

    move-object/from16 v53, v6

    move-object/from16 v64, v7

    move-object/from16 v106, v14

    goto/16 :goto_49

    :catchall_0
    move-exception v0

    move-object v3, v7

    move-object v9, v11

    move-object v12, v14

    move v14, v4

    move-object v11, v6

    goto/16 :goto_58

    :pswitch_1
    iget v0, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->I$3:I

    iget-wide v3, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->J$4:J

    iget v0, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->I$2:I

    iget v0, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->I$1:I

    iget-wide v3, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->J$3:J

    move-object v5, v2

    iget-wide v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->J$2:J

    move-wide/from16 p1, v1

    iget-wide v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->J$1:J

    move-wide/from16 v19, v1

    iget-wide v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->J$0:J

    iget v9, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->I$0:I

    move-wide/from16 v21, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$20:Ljava/lang/Object;

    check-cast v1, Ljava/util/List;

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$19:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$ObjectRef;

    iget-object v2, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$18:Ljava/lang/Object;

    check-cast v2, Landroid/os/ParcelFileDescriptor;

    iget-object v2, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$17:Ljava/lang/Object;

    check-cast v2, Landroid/net/Uri;

    iget-object v2, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$16:Ljava/lang/Object;

    check-cast v2, Ljava/io/File;

    move-object/from16 v23, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$15:Ljava/lang/Object;

    check-cast v1, Ljava/lang/String;

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$14:Ljava/lang/Object;

    check-cast v1, Lcom/bachatas4/android/runtime/pkg/PkgProbeResult;

    move-object/from16 v24, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$13:Ljava/lang/Object;

    check-cast v1, Ljava/lang/String;

    move-object/from16 v25, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$12:Ljava/lang/Object;

    check-cast v1, Lkotlin/Pair;

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$11:Ljava/lang/Object;

    check-cast v1, Ljava/util/Iterator;

    move-object/from16 v26, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$10:Ljava/lang/Object;

    check-cast v1, Ljava/util/List;

    move-object/from16 v27, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$9:Ljava/lang/Object;

    check-cast v1, Ljava/lang/String;

    move-object/from16 v28, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$8:Ljava/lang/Object;

    check-cast v1, Lcom/bachatas4/android/model/Game;

    move-object/from16 v29, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$7:Ljava/lang/Object;

    check-cast v1, Ljava/util/List;

    move-object/from16 v30, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$6:Ljava/lang/Object;

    check-cast v1, Ljava/util/List;

    move-object/from16 v31, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$5:Ljava/lang/Object;

    check-cast v1, Ljava/util/List;

    move-object/from16 v32, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$4:Ljava/lang/Object;

    check-cast v1, Ljava/io/File;

    move-object/from16 v33, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$3:Ljava/lang/Object;

    check-cast v1, Ljava/io/File;

    move-object/from16 v34, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$2:Ljava/lang/Object;

    check-cast v1, Ljava/lang/String;

    move-object/from16 v35, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$1:Ljava/lang/Object;

    check-cast v1, Ljava/util/List;

    move-object/from16 v36, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$0:Ljava/lang/Object;

    check-cast v1, Ljava/lang/String;

    :try_start_1
    invoke-static {v5}, Lkotlin/ResultKt;->throwOnFailure(Ljava/lang/Object;)V
    :try_end_1
    .catchall {:try_start_1 .. :try_end_1} :catchall_1

    move-wide/from16 v57, p1

    move v5, v0

    move-wide/from16 v59, v3

    move-object/from16 v53, v6

    move-object/from16 v64, v7

    move-object/from16 v42, v10

    move-object v6, v11

    move-object/from16 v84, v12

    move-object/from16 v106, v14

    move-object/from16 v4, v23

    move-object/from16 v0, v28

    move-object/from16 v7, v31

    move-object/from16 v12, v34

    move-object/from16 v10, v36

    const-wide/16 v51, 0x0

    move-object v3, v2

    move-object/from16 v36, v13

    move-object/from16 v2, v25

    move-object/from16 v13, v33

    move-object/from16 v25, v8

    move-object/from16 v8, v32

    move-object/from16 v138, v15

    move-object v15, v1

    move-object/from16 v1, v24

    move-wide/from16 v23, v19

    move-object/from16 v19, v29

    move-object/from16 v20, v138

    goto/16 :goto_34

    :catchall_1
    move-exception v0

    move-object/from16 v1, p0

    move-object v11, v6

    move-object v3, v7

    move-object v12, v14

    move-object/from16 v5, v30

    move-object/from16 v8, v31

    move v14, v9

    move-object/from16 v9, v36

    goto/16 :goto_58

    :pswitch_2
    move-object v5, v2

    iget v0, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->I$4:I

    iget v0, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->I$3:I

    iget-wide v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->J$4:J

    iget v3, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->I$2:I

    iget v4, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->I$1:I

    move-wide/from16 v19, v1

    iget-wide v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->J$3:J

    move-wide/from16 v21, v1

    iget-wide v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->J$2:J

    move-wide/from16 v23, v1

    iget-wide v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->J$1:J

    move-wide/from16 v25, v1

    iget-wide v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->J$0:J

    iget v9, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->I$0:I

    move-wide/from16 v27, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$25:Ljava/lang/Object;

    check-cast v1, Ljava/lang/String;

    iget-object v2, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$24:Ljava/lang/Object;

    check-cast v2, Lkotlinx/coroutines/CompletableDeferred;

    iget-object v2, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$23:Ljava/lang/Object;

    check-cast v2, Lcom/bachatas4/android/runtime/pkg/PkgStatus;

    iget-object v2, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$22:Ljava/lang/Object;

    check-cast v2, Landroid/os/ParcelFileDescriptor;

    iget-object v2, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$21:Ljava/lang/Object;

    check-cast v2, Ljava/io/Closeable;

    move-object/from16 p1, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$20:Ljava/lang/Object;

    check-cast v1, Ljava/util/List;

    move-object/from16 p2, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$19:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$ObjectRef;

    move-object/from16 v29, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$18:Ljava/lang/Object;

    check-cast v1, Landroid/os/ParcelFileDescriptor;

    move-object/from16 v30, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$17:Ljava/lang/Object;

    check-cast v1, Landroid/net/Uri;

    move-object/from16 v31, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$16:Ljava/lang/Object;

    check-cast v1, Ljava/io/File;

    move-object/from16 v32, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$15:Ljava/lang/Object;

    check-cast v1, Ljava/lang/String;

    move-object/from16 v33, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$14:Ljava/lang/Object;

    check-cast v1, Lcom/bachatas4/android/runtime/pkg/PkgProbeResult;

    move-object/from16 v34, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$13:Ljava/lang/Object;

    check-cast v1, Ljava/lang/String;

    move-object/from16 v35, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$12:Ljava/lang/Object;

    check-cast v1, Lkotlin/Pair;

    move-object/from16 v36, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$11:Ljava/lang/Object;

    check-cast v1, Ljava/util/Iterator;

    move-object/from16 v37, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$10:Ljava/lang/Object;

    check-cast v1, Ljava/util/List;

    move-object/from16 v38, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$9:Ljava/lang/Object;

    check-cast v1, Ljava/lang/String;

    move-object/from16 v39, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$8:Ljava/lang/Object;

    check-cast v1, Lcom/bachatas4/android/model/Game;

    move-object/from16 v40, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$7:Ljava/lang/Object;

    check-cast v1, Ljava/util/List;

    move-object/from16 v41, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$6:Ljava/lang/Object;

    check-cast v1, Ljava/util/List;

    move-object/from16 v42, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$5:Ljava/lang/Object;

    check-cast v1, Ljava/util/List;

    move-object/from16 v43, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$4:Ljava/lang/Object;

    check-cast v1, Ljava/io/File;

    move-object/from16 v44, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$3:Ljava/lang/Object;

    check-cast v1, Ljava/io/File;

    move-object/from16 v45, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$2:Ljava/lang/Object;

    check-cast v1, Ljava/lang/String;

    move-object/from16 v46, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$1:Ljava/lang/Object;

    check-cast v1, Ljava/util/List;

    move-object/from16 v47, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$0:Ljava/lang/Object;

    check-cast v1, Ljava/lang/String;

    :try_start_2
    invoke-static {v5}, Lkotlin/ResultKt;->throwOnFailure(Ljava/lang/Object;)V
    :try_end_2
    .catchall {:try_start_2 .. :try_end_2} :catchall_2

    move-object/from16 v18, p2

    move-object/from16 v126, v2

    move/from16 v128, v3

    move/from16 v127, v4

    move-object/from16 v53, v6

    move-object/from16 v64, v7

    move-object v4, v11

    move-object/from16 v84, v12

    move-object/from16 v106, v14

    move-object/from16 v105, v15

    move-object/from16 v2, v29

    move-object/from16 v123, v35

    move-object/from16 v122, v37

    move-object/from16 v15, v41

    move-object/from16 v12, v45

    const-wide/16 v51, 0x0

    move-object/from16 v3, p1

    move-object v11, v5

    move-object v14, v10

    move-wide/from16 v5, v27

    move-object/from16 v28, v36

    move-object/from16 v36, v13

    const/4 v13, 0x0

    move-wide/from16 v138, v21

    move-object/from16 v22, v1

    move/from16 v21, v9

    move-wide/from16 v9, v138

    move-wide/from16 v138, v25

    move-object/from16 v25, v8

    move-wide/from16 v7, v138

    move-object/from16 v26, v32

    goto/16 :goto_2d

    :catchall_2
    move-exception v0

    move-object v1, v0

    move-object/from16 v53, v6

    move-object/from16 v64, v7

    move-object/from16 v106, v14

    move-object/from16 v5, v41

    move-object/from16 v8, v42

    move-object/from16 v10, v47

    move v14, v9

    goto/16 :goto_3f

    :pswitch_3
    move-object v5, v2

    iget v0, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->I$4:I

    iget v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->I$3:I

    iget-wide v2, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->J$4:J

    iget v4, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->I$2:I

    iget v9, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->I$1:I

    move/from16 v19, v1

    move-wide/from16 v20, v2

    iget-wide v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->J$3:J

    move-wide/from16 v22, v1

    iget-wide v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->J$2:J

    move-wide/from16 v24, v1

    iget-wide v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->J$1:J

    move-wide/from16 v26, v1

    iget-wide v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->J$0:J

    iget v3, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->I$0:I

    move-wide/from16 v28, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$24:Ljava/lang/Object;

    check-cast v1, Lkotlinx/coroutines/CompletableDeferred;

    iget-object v2, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$23:Ljava/lang/Object;

    check-cast v2, Lcom/bachatas4/android/runtime/pkg/PkgStatus;

    move-object/from16 p1, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$22:Ljava/lang/Object;

    check-cast v1, Landroid/os/ParcelFileDescriptor;

    move-object/from16 p2, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$21:Ljava/lang/Object;

    check-cast v1, Ljava/io/Closeable;

    move-object/from16 v30, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$20:Ljava/lang/Object;

    check-cast v1, Ljava/util/List;

    move-object/from16 v31, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$19:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$ObjectRef;

    move-object/from16 v32, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$18:Ljava/lang/Object;

    check-cast v1, Landroid/os/ParcelFileDescriptor;

    move-object/from16 v33, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$17:Ljava/lang/Object;

    check-cast v1, Landroid/net/Uri;

    move-object/from16 v34, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$16:Ljava/lang/Object;

    check-cast v1, Ljava/io/File;

    move-object/from16 v35, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$15:Ljava/lang/Object;

    check-cast v1, Ljava/lang/String;

    move-object/from16 v36, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$14:Ljava/lang/Object;

    check-cast v1, Lcom/bachatas4/android/runtime/pkg/PkgProbeResult;

    move-object/from16 v37, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$13:Ljava/lang/Object;

    check-cast v1, Ljava/lang/String;

    move-object/from16 v38, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$12:Ljava/lang/Object;

    check-cast v1, Lkotlin/Pair;

    move-object/from16 v39, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$11:Ljava/lang/Object;

    check-cast v1, Ljava/util/Iterator;

    move-object/from16 v40, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$10:Ljava/lang/Object;

    check-cast v1, Ljava/util/List;

    move-object/from16 v41, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$9:Ljava/lang/Object;

    check-cast v1, Ljava/lang/String;

    move-object/from16 v42, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$8:Ljava/lang/Object;

    check-cast v1, Lcom/bachatas4/android/model/Game;

    move-object/from16 v43, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$7:Ljava/lang/Object;

    check-cast v1, Ljava/util/List;

    move-object/from16 v44, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$6:Ljava/lang/Object;

    check-cast v1, Ljava/util/List;

    move-object/from16 v45, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$5:Ljava/lang/Object;

    check-cast v1, Ljava/util/List;

    move-object/from16 v46, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$4:Ljava/lang/Object;

    check-cast v1, Ljava/io/File;

    move-object/from16 v47, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$3:Ljava/lang/Object;

    check-cast v1, Ljava/io/File;

    move-object/from16 v48, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$2:Ljava/lang/Object;

    check-cast v1, Ljava/lang/String;

    move-object/from16 v49, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$1:Ljava/lang/Object;

    check-cast v1, Ljava/util/List;

    move-object/from16 v50, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$0:Ljava/lang/Object;

    check-cast v1, Ljava/lang/String;

    :try_start_3
    invoke-static {v5}, Lkotlin/ResultKt;->throwOnFailure(Ljava/lang/Object;)V
    :try_end_3
    .catchall {:try_start_3 .. :try_end_3} :catchall_3

    move/from16 v117, v3

    move-object/from16 v53, v6

    move-object/from16 v64, v7

    move-object/from16 v118, v10

    move-object v6, v11

    move-object/from16 v84, v12

    move-object/from16 v106, v14

    move-object/from16 v105, v15

    move/from16 v7, v19

    move-wide/from16 v115, v20

    move-wide/from16 v113, v22

    move-wide/from16 v111, v24

    move-wide/from16 v109, v26

    move-wide/from16 v107, v28

    move-object/from16 v26, v30

    move-object/from16 v18, v31

    move-object/from16 v31, v32

    move-object/from16 v17, v34

    move-object/from16 v3, v35

    move-object/from16 v28, v39

    move-object/from16 v34, v40

    move-object/from16 v15, v44

    move-object/from16 v14, v45

    move-object/from16 v11, v47

    move-object/from16 v12, v48

    move-object/from16 v10, v50

    const/16 v24, 0x0

    const-wide/16 v51, 0x0

    move-object/from16 v19, p1

    move-object/from16 v21, p2

    move-object/from16 v32, v2

    move-object/from16 v25, v8

    move v2, v0

    move-object v8, v1

    move-object v0, v5

    move-object/from16 v5, v36

    move-object/from16 v1, p0

    move-object/from16 v36, v13

    move-object/from16 v13, v46

    move/from16 v46, v4

    move v4, v9

    move-object/from16 v9, v49

    goto/16 :goto_2c

    :pswitch_4
    move-object v5, v2

    iget v0, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->I$4:I

    iget v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->I$3:I

    iget-wide v2, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->J$4:J

    iget v4, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->I$2:I

    iget v9, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->I$1:I

    move/from16 v19, v1

    move-wide/from16 v20, v2

    iget-wide v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->J$3:J

    move-wide/from16 v22, v1

    iget-wide v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->J$2:J

    move-wide/from16 v24, v1

    iget-wide v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->J$1:J

    move-wide/from16 v26, v1

    iget-wide v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->J$0:J

    iget v3, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->I$0:I

    move-wide/from16 v28, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$25:Ljava/lang/Object;

    check-cast v1, Ljava/lang/String;

    iget-object v2, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$24:Ljava/lang/Object;

    check-cast v2, Ljava/util/Iterator;

    move-object/from16 p1, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$23:Ljava/lang/Object;

    check-cast v1, Lcom/bachatas4/android/runtime/pkg/PkgStatus;

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$22:Ljava/lang/Object;

    check-cast v1, Landroid/os/ParcelFileDescriptor;

    move-object/from16 p2, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$21:Ljava/lang/Object;

    check-cast v1, Ljava/io/Closeable;

    move-object/from16 v30, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$20:Ljava/lang/Object;

    check-cast v1, Ljava/util/List;

    move-object/from16 v31, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$19:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$ObjectRef;

    move-object/from16 v32, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$18:Ljava/lang/Object;

    check-cast v1, Landroid/os/ParcelFileDescriptor;

    move-object/from16 v33, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$17:Ljava/lang/Object;

    check-cast v1, Landroid/net/Uri;

    move-object/from16 v34, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$16:Ljava/lang/Object;

    check-cast v1, Ljava/io/File;

    move-object/from16 v35, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$15:Ljava/lang/Object;

    check-cast v1, Ljava/lang/String;

    move-object/from16 v36, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$14:Ljava/lang/Object;

    check-cast v1, Lcom/bachatas4/android/runtime/pkg/PkgProbeResult;

    move-object/from16 v37, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$13:Ljava/lang/Object;

    check-cast v1, Ljava/lang/String;

    move-object/from16 v38, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$12:Ljava/lang/Object;

    check-cast v1, Lkotlin/Pair;

    move-object/from16 v39, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$11:Ljava/lang/Object;

    check-cast v1, Ljava/util/Iterator;

    move-object/from16 v40, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$10:Ljava/lang/Object;

    check-cast v1, Ljava/util/List;

    move-object/from16 v41, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$9:Ljava/lang/Object;

    check-cast v1, Ljava/lang/String;

    move-object/from16 v42, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$8:Ljava/lang/Object;

    check-cast v1, Lcom/bachatas4/android/model/Game;

    move-object/from16 v43, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$7:Ljava/lang/Object;

    check-cast v1, Ljava/util/List;

    move-object/from16 v44, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$6:Ljava/lang/Object;

    check-cast v1, Ljava/util/List;

    move-object/from16 v45, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$5:Ljava/lang/Object;

    check-cast v1, Ljava/util/List;

    move-object/from16 v46, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$4:Ljava/lang/Object;

    check-cast v1, Ljava/io/File;

    move-object/from16 v47, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$3:Ljava/lang/Object;

    check-cast v1, Ljava/io/File;

    move-object/from16 v48, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$2:Ljava/lang/Object;

    check-cast v1, Ljava/lang/String;

    move-object/from16 v49, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$1:Ljava/lang/Object;

    check-cast v1, Ljava/util/List;

    move-object/from16 v50, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$0:Ljava/lang/Object;

    check-cast v1, Ljava/lang/String;

    :try_start_4
    invoke-static {v5}, Lkotlin/ResultKt;->throwOnFailure(Ljava/lang/Object;)V
    :try_end_4
    .catchall {:try_start_4 .. :try_end_4} :catchall_3

    move/from16 v65, v3

    move/from16 v66, v4

    move-object/from16 v53, v6

    move-object/from16 v64, v7

    move/from16 v67, v9

    move-object/from16 v68, v10

    move-object/from16 v84, v12

    move-wide/from16 v6, v20

    move-wide/from16 v59, v22

    move-wide/from16 v57, v24

    move-wide/from16 v62, v26

    move-wide/from16 v26, v28

    move-object/from16 v4, v30

    move-object/from16 v18, v31

    move-object/from16 v23, v33

    move-object/from16 v17, v34

    move-object/from16 v29, v35

    move-object/from16 v61, v36

    move-object/from16 v10, v37

    move-object/from16 v28, v39

    move-object/from16 v30, v41

    move-object/from16 v34, v45

    move-object/from16 v39, v46

    move-object/from16 v12, v48

    move-object/from16 v9, v50

    const/16 v24, 0x0

    const-wide/16 v51, 0x0

    move-object/from16 v21, p2

    move v3, v0

    move-object/from16 v35, v2

    move-object/from16 v25, v8

    move-object/from16 v36, v13

    move-object/from16 v20, v15

    move-object/from16 v8, v42

    move-object/from16 v0, v47

    move-object/from16 v13, v49

    move-object/from16 v2, p1

    move-object v15, v1

    move-object v1, v11

    move-object/from16 v49, v14

    move-object/from16 v14, v32

    move-object/from16 v11, v38

    move-object/from16 v32, v44

    goto/16 :goto_27

    :catchall_3
    move-exception v0

    move-object v1, v0

    move-object/from16 v53, v6

    move-object/from16 v64, v7

    move-object/from16 v106, v14

    move-object/from16 v2, v30

    move-object/from16 v5, v44

    move-object/from16 v8, v45

    move-object/from16 v10, v50

    move v14, v3

    goto/16 :goto_3f

    :pswitch_5
    move-object v5, v2

    iget v0, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->I$3:I

    iget-wide v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->J$4:J

    iget v3, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->I$2:I

    iget v4, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->I$1:I

    move-wide/from16 v19, v1

    iget-wide v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->J$3:J

    move-wide/from16 v21, v1

    iget-wide v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->J$2:J

    move-wide/from16 v23, v1

    iget-wide v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->J$1:J

    move-wide/from16 v25, v1

    iget-wide v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->J$0:J

    iget v9, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->I$0:I

    move-wide/from16 v27, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$19:Ljava/lang/Object;

    check-cast v1, Ljava/io/File;

    iget-object v2, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$18:Ljava/lang/Object;

    check-cast v2, Ljava/io/File;

    iget-object v2, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$17:Ljava/lang/Object;

    check-cast v2, Landroid/net/Uri;

    move-object/from16 p1, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$16:Ljava/lang/Object;

    check-cast v1, Ljava/io/File;

    move-object/from16 p2, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$15:Ljava/lang/Object;

    check-cast v1, Ljava/lang/String;

    move-object/from16 v29, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$14:Ljava/lang/Object;

    check-cast v1, Lcom/bachatas4/android/runtime/pkg/PkgProbeResult;

    move-object/from16 v30, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$13:Ljava/lang/Object;

    check-cast v1, Ljava/lang/String;

    move-object/from16 v31, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$12:Ljava/lang/Object;

    check-cast v1, Lkotlin/Pair;

    move-object/from16 v32, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$11:Ljava/lang/Object;

    check-cast v1, Ljava/util/Iterator;

    move-object/from16 v33, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$10:Ljava/lang/Object;

    check-cast v1, Ljava/util/List;

    move-object/from16 v34, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$9:Ljava/lang/Object;

    check-cast v1, Ljava/lang/String;

    move-object/from16 v35, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$8:Ljava/lang/Object;

    check-cast v1, Lcom/bachatas4/android/model/Game;

    move-object/from16 v36, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$7:Ljava/lang/Object;

    check-cast v1, Ljava/util/List;

    move-object/from16 v37, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$6:Ljava/lang/Object;

    check-cast v1, Ljava/util/List;

    move-object/from16 v38, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$5:Ljava/lang/Object;

    check-cast v1, Ljava/util/List;

    move-object/from16 v39, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$4:Ljava/lang/Object;

    check-cast v1, Ljava/io/File;

    move-object/from16 v40, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$3:Ljava/lang/Object;

    check-cast v1, Ljava/io/File;

    move-object/from16 v41, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$2:Ljava/lang/Object;

    check-cast v1, Ljava/lang/String;

    move-object/from16 v42, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$1:Ljava/lang/Object;

    check-cast v1, Ljava/util/List;

    move-object/from16 v43, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$0:Ljava/lang/Object;

    check-cast v1, Ljava/lang/String;

    :try_start_5
    invoke-static {v5}, Lkotlin/ResultKt;->throwOnFailure(Ljava/lang/Object;)V
    :try_end_5
    .catchall {:try_start_5 .. :try_end_5} :catchall_4

    move-object/from16 v53, v6

    move-object/from16 v64, v7

    move-object/from16 v17, v12

    move-wide/from16 v5, v19

    move-wide/from16 v45, v21

    move-wide/from16 v62, v25

    move-object/from16 v44, v34

    move-object/from16 v19, v36

    const-wide/16 v51, 0x0

    move v7, v3

    move/from16 v26, v4

    move-object/from16 v25, v8

    move-object v12, v11

    move-object/from16 v36, v13

    move-object/from16 v20, v15

    move-object/from16 v8, v38

    move-object/from16 v13, v40

    move-object/from16 v3, p2

    move-object v4, v2

    move-object v11, v10

    move-object/from16 v2, v29

    move-object/from16 v29, v30

    move-object/from16 v30, v33

    move-object/from16 v10, v37

    move-object/from16 v37, v1

    move-object/from16 v1, p1

    goto/16 :goto_23

    :catchall_4
    move-exception v0

    move-object/from16 v1, p0

    move-object v11, v6

    move-object v3, v7

    move-object v12, v14

    move-object/from16 v5, v37

    move-object/from16 v8, v38

    move v14, v9

    move-object/from16 v9, v43

    goto/16 :goto_58

    :pswitch_6
    move-object v5, v2

    iget-boolean v0, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->Z$0:Z

    iget-wide v0, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->J$0:J

    iget v2, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->I$0:I

    iget-object v3, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$15:Ljava/lang/Object;

    check-cast v3, Landroid/os/ParcelFileDescriptor;

    iget-object v3, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$14:Ljava/lang/Object;

    check-cast v3, Ljava/io/Closeable;

    iget-object v4, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$13:Ljava/lang/Object;

    check-cast v4, Landroid/net/Uri;

    iget-object v4, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$12:Ljava/lang/Object;

    check-cast v4, Ljava/lang/String;

    iget-object v9, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$11:Ljava/lang/Object;

    check-cast v9, Ljava/util/Iterator;

    move-wide/from16 v19, v0

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$10:Ljava/lang/Object;

    check-cast v1, Ljava/util/List;

    iget-object v0, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$9:Ljava/lang/Object;

    check-cast v0, Ljava/lang/String;

    move-object/from16 p1, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$8:Ljava/lang/Object;

    check-cast v1, Lcom/bachatas4/android/model/Game;

    move-object/from16 p2, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$7:Ljava/lang/Object;

    check-cast v1, Ljava/util/List;

    move-object/from16 v21, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$6:Ljava/lang/Object;

    check-cast v1, Ljava/util/List;

    move-object/from16 v22, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$5:Ljava/lang/Object;

    check-cast v1, Ljava/util/List;

    move-object/from16 v23, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$4:Ljava/lang/Object;

    check-cast v1, Ljava/io/File;

    move-object/from16 v24, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$3:Ljava/lang/Object;

    check-cast v1, Ljava/io/File;

    move-object/from16 v25, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$2:Ljava/lang/Object;

    check-cast v1, Ljava/lang/String;

    move-object/from16 v26, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$1:Ljava/lang/Object;

    check-cast v1, Ljava/util/List;

    move-object/from16 v27, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$0:Ljava/lang/Object;

    check-cast v1, Ljava/lang/String;

    :try_start_6
    invoke-static {v5}, Lkotlin/ResultKt;->throwOnFailure(Ljava/lang/Object;)V
    :try_end_6
    .catchall {:try_start_6 .. :try_end_6} :catchall_5

    move-object/from16 v53, v6

    move-object/from16 v54, v7

    move-object/from16 v18, v8

    move-object/from16 v17, v12

    move-object/from16 v8, v25

    move-object v12, v0

    move-object v6, v1

    move-object v7, v4

    move-object/from16 v25, v13

    move-object/from16 v1, p1

    move-object/from16 v0, p2

    move-object/from16 v138, v11

    move v11, v2

    move-object v2, v5

    move-object v5, v3

    move-wide/from16 v3, v19

    move-object/from16 v19, v10

    move-object/from16 v10, v138

    move-object/from16 v20, v15

    move-object/from16 v15, v21

    goto/16 :goto_9

    :catchall_5
    move-exception v0

    move-object/from16 v13, p0

    move v4, v2

    move-object v8, v6

    move-object v1, v7

    move-object/from16 v5, v21

    move-object/from16 v21, v22

    move-object/from16 v9, v27

    :goto_1
    move-object v2, v0

    goto/16 :goto_19

    :pswitch_7
    move-object v5, v2

    iget v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->I$0:I

    iget-object v0, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$7:Ljava/lang/Object;

    move-object v2, v0

    check-cast v2, Ljava/util/List;

    iget-object v0, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$6:Ljava/lang/Object;

    move-object v3, v0

    check-cast v3, Ljava/util/List;

    iget-object v0, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$5:Ljava/lang/Object;

    check-cast v0, Ljava/util/List;

    iget-object v4, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$4:Ljava/lang/Object;

    check-cast v4, Ljava/io/File;

    iget-object v9, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$3:Ljava/lang/Object;

    check-cast v9, Ljava/io/File;

    move/from16 v19, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$2:Ljava/lang/Object;

    check-cast v1, Ljava/lang/String;

    move-object/from16 p1, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$1:Ljava/lang/Object;

    check-cast v1, Ljava/util/List;

    move-object/from16 p2, v1

    iget-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$0:Ljava/lang/Object;

    check-cast v1, Ljava/lang/String;

    :try_start_7
    invoke-static {v5}, Lkotlin/ResultKt;->throwOnFailure(Ljava/lang/Object;)V
    :try_end_7
    .catchall {:try_start_7 .. :try_end_7} :catchall_6

    move-object/from16 v53, v6

    move-object/from16 v54, v7

    move-object/from16 v18, v8

    move-object v6, v9

    move-object/from16 v17, v12

    move-object/from16 v20, v15

    move-object/from16 v9, p2

    move-object v7, v2

    move-object v8, v5

    move-object/from16 v2, p1

    move-object v5, v0

    move-object v0, v1

    move-object/from16 v1, p0

    goto/16 :goto_3

    :catchall_6
    move-exception v0

    move-object/from16 v1, p0

    move-object/from16 v9, p2

    move-object v5, v2

    move-object v8, v3

    move-object v11, v6

    move-object v3, v7

    move-object v12, v14

    :goto_2
    move/from16 v14, v19

    goto/16 :goto_58

    :pswitch_8
    move-object v5, v2

    invoke-static {v5}, Lkotlin/ResultKt;->throwOnFailure(Ljava/lang/Object;)V

    .line 676
    invoke-interface/range {p2 .. p2}, Ljava/util/List;->size()I

    move-result v1

    new-instance v2, Ljava/lang/StringBuilder;

    const-string v3, "pkg batch start gameId="

    invoke-direct {v2, v3}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v2, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v2

    const-string v3, " count="

    invoke-virtual {v2, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v2

    invoke-virtual {v2, v1}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v1

    invoke-static {v14, v1}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    move-object v1, v6

    const/4 v6, 0x6

    move-object v2, v7

    const/4 v7, 0x0

    move-object v3, v2

    .line 677
    const-string v2, "Preparing batch install\u2026"

    move-object v4, v3

    const/4 v3, 0x0

    move-object v5, v4

    const/4 v4, 0x0

    move-object/from16 v19, v5

    const/4 v5, 0x1

    move-object/from16 v53, v1

    move-object/from16 v20, v15

    move-object/from16 v54, v19

    const/4 v15, 0x0

    move-object/from16 v1, p0

    invoke-static/range {v1 .. v7}, Lcom/bachatas4/android/service/ImportService;->updateNotification$default(Lcom/bachatas4/android/service/ImportService;Ljava/lang/String;IIZILjava/lang/Object;)V

    .line 678
    invoke-static {}, Ljava/util/UUID;->randomUUID()Ljava/util/UUID;

    move-result-object v2

    invoke-virtual {v2}, Ljava/util/UUID;->toString()Ljava/lang/String;

    move-result-object v2

    const-string v3, "toString(...)"

    invoke-static {v2, v3}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullExpressionValue(Ljava/lang/Object;Ljava/lang/String;)V

    .line 679
    new-instance v3, Ljava/io/File;

    invoke-virtual {v1}, Lcom/bachatas4/android/service/ImportService;->getFilesDir()Ljava/io/File;

    move-result-object v4

    const-string v5, "games"

    invoke-direct {v3, v4, v5}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    invoke-virtual {v3}, Ljava/io/File;->getCanonicalFile()Ljava/io/File;

    move-result-object v3

    .line 680
    new-instance v4, Ljava/io/File;

    invoke-direct {v4, v3, v0}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    invoke-virtual {v4}, Ljava/io/File;->getCanonicalFile()Ljava/io/File;

    move-result-object v4

    .line 683
    new-instance v5, Ljava/util/ArrayList;

    invoke-direct {v5}, Ljava/util/ArrayList;-><init>()V

    check-cast v5, Ljava/util/List;

    .line 684
    new-instance v6, Ljava/util/ArrayList;

    invoke-direct {v6}, Ljava/util/ArrayList;-><init>()V

    check-cast v6, Ljava/util/List;

    .line 685
    new-instance v7, Ljava/util/ArrayList;

    invoke-direct {v7}, Ljava/util/ArrayList;-><init>()V

    check-cast v7, Ljava/util/List;

    .line 688
    :try_start_8
    invoke-virtual {v4}, Ljava/io/File;->isDirectory()Z

    move-result v16
    :try_end_8
    .catchall {:try_start_8 .. :try_end_8} :catchall_61

    if-eqz v16, :cond_3d

    :try_start_9
    sget-object v15, Lcom/bachatas4/android/data/GameInstallVerifier;->INSTANCE:Lcom/bachatas4/android/data/GameInstallVerifier;

    move-object/from16 v17, v12

    invoke-virtual {v1}, Lcom/bachatas4/android/service/ImportService;->getFilesDir()Ljava/io/File;

    move-result-object v12

    move-object/from16 v18, v8

    const-string v8, "getFilesDir(...)"

    invoke-static {v12, v8}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullExpressionValue(Ljava/lang/Object;Ljava/lang/String;)V

    new-instance v8, Ljava/lang/StringBuilder;

    invoke-direct {v8, v9}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v8, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v8

    invoke-virtual {v8}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v8

    invoke-virtual {v15, v12, v8}, Lcom/bachatas4/android/data/GameInstallVerifier;->canLaunch(Ljava/io/File;Ljava/lang/String;)Z

    move-result v8

    if-nez v8, :cond_1

    goto/16 :goto_52

    .line 694
    :cond_1
    invoke-virtual {v1}, Lcom/bachatas4/android/service/ImportService;->getGameRepository()Lcom/bachatas4/android/data/GameRepository;

    move-result-object v8

    iput-object v0, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$0:Ljava/lang/Object;
    :try_end_9
    .catchall {:try_start_9 .. :try_end_9} :catchall_5c

    move-object/from16 v9, p2

    :try_start_a
    iput-object v9, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$1:Ljava/lang/Object;

    iput-object v2, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$2:Ljava/lang/Object;

    iput-object v3, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$3:Ljava/lang/Object;

    iput-object v4, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$4:Ljava/lang/Object;

    iput-object v5, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$5:Ljava/lang/Object;

    iput-object v6, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$6:Ljava/lang/Object;

    iput-object v7, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$7:Ljava/lang/Object;

    const/4 v12, 0x0

    iput v12, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->I$0:I

    const/4 v12, 0x1

    iput v12, v10, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->label:I

    invoke-virtual {v8, v0, v10}, Lcom/bachatas4/android/data/GameRepository;->getGame(Ljava/lang/String;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;

    move-result-object v8
    :try_end_a
    .catchall {:try_start_a .. :try_end_a} :catchall_5b

    if-ne v8, v11, :cond_2

    move-object v6, v11

    goto/16 :goto_48

    :cond_2
    move-object/from16 v19, v6

    move-object v6, v3

    move-object/from16 v3, v19

    const/16 v19, 0x0

    .line 675
    :goto_3
    :try_start_b
    check-cast v8, Lcom/bachatas4/android/model/Game;
    :try_end_b
    .catchall {:try_start_b .. :try_end_b} :catchall_5a

    if-eqz v8, :cond_3

    .line 695
    :try_start_c
    invoke-virtual {v8}, Lcom/bachatas4/android/model/Game;->getTitle()Ljava/lang/String;

    move-result-object v12
    :try_end_c
    .catchall {:try_start_c .. :try_end_c} :catchall_7

    if-nez v12, :cond_4

    goto :goto_5

    :catchall_7
    move-exception v0

    move-object v8, v3

    move-object v5, v7

    move-object v12, v14

    move/from16 v14, v19

    :goto_4
    move-object/from16 v11, v53

    move-object/from16 v3, v54

    goto/16 :goto_58

    :cond_3
    :goto_5
    move-object v12, v0

    .line 696
    :cond_4
    :try_start_d
    sget-object v15, Lcom/bachatas4/android/data/ImportManager;->INSTANCE:Lcom/bachatas4/android/data/ImportManager;

    move-object/from16 p1, v2

    .line 697
    new-instance v2, Lcom/bachatas4/android/data/ImportProgress$BatchSelected;
    :try_end_d
    .catchall {:try_start_d .. :try_end_d} :catchall_5a

    move-object/from16 p2, v3

    :try_start_e
    invoke-interface {v9}, Ljava/util/List;->size()I

    move-result v3

    invoke-direct {v2, v0, v12, v3}, Lcom/bachatas4/android/data/ImportProgress$BatchSelected;-><init>(Ljava/lang/String;Ljava/lang/String;I)V

    check-cast v2, Lcom/bachatas4/android/data/ImportProgress;

    .line 696
    invoke-virtual {v15, v2}, Lcom/bachatas4/android/data/ImportManager;->update(Lcom/bachatas4/android/data/ImportProgress;)V

    .line 701
    new-instance v2, Ljava/util/ArrayList;

    invoke-direct {v2}, Ljava/util/ArrayList;-><init>()V

    check-cast v2, Ljava/util/List;

    .line 703
    invoke-interface {v9}, Ljava/util/List;->iterator()Ljava/util/Iterator;

    move-result-object v3
    :try_end_e
    .catchall {:try_start_e .. :try_end_e} :catchall_59

    move/from16 v15, v19

    move-object/from16 v19, v10

    move v10, v15

    move-object v15, v7

    const-wide/16 v55, 0x0

    move-object v7, v5

    move-object v5, v4

    move-object/from16 v4, p1

    move-object/from16 p1, v8

    move-object/from16 v8, p2

    move-object/from16 p2, v3

    move-object v3, v0

    :goto_6
    :try_start_f
    invoke-interface/range {p2 .. p2}, Ljava/util/Iterator;->hasNext()Z

    move-result v0
    :try_end_f
    .catchall {:try_start_f .. :try_end_f} :catchall_58

    if-eqz v0, :cond_18

    :try_start_10
    invoke-interface/range {p2 .. p2}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v0

    move-object/from16 v21, v11

    move-object v11, v0

    check-cast v11, Ljava/lang/String;

    .line 704
    invoke-interface/range {v19 .. v19}, Lkotlin/coroutines/Continuation;->getContext()Lkotlin/coroutines/CoroutineContext;

    move-result-object v0

    invoke-static {v0}, Lkotlinx/coroutines/JobKt;->ensureActive(Lkotlin/coroutines/CoroutineContext;)V
    :try_end_10
    .catchall {:try_start_10 .. :try_end_10} :catchall_1e

    move/from16 v22, v10

    .line 705
    :try_start_11
    invoke-static {v11}, Landroid/net/Uri;->parse(Ljava/lang/String;)Landroid/net/Uri;

    move-result-object v10
    :try_end_11
    .catchall {:try_start_11 .. :try_end_11} :catchall_1d

    .line 706
    :try_start_12
    sget-object v0, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    move-object v0, v1

    check-cast v0, Lcom/bachatas4/android/service/ImportService;

    .line 707
    invoke-virtual {v1}, Lcom/bachatas4/android/service/ImportService;->getContentResolver()Landroid/content/ContentResolver;

    move-result-object v0
    :try_end_12
    .catchall {:try_start_12 .. :try_end_12} :catchall_9

    move-object/from16 v23, v11

    const/4 v11, 0x1

    :try_start_13
    invoke-virtual {v0, v10, v11}, Landroid/content/ContentResolver;->takePersistableUriPermission(Landroid/net/Uri;I)V

    .line 708
    sget-object v0, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;

    .line 706
    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;
    :try_end_13
    .catchall {:try_start_13 .. :try_end_13} :catchall_8

    goto :goto_8

    :catchall_8
    move-exception v0

    goto :goto_7

    :catchall_9
    move-exception v0

    move-object/from16 v23, v11

    :goto_7
    :try_start_14
    sget-object v11, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    invoke-static {v0}, Lkotlin/ResultKt;->createFailure(Ljava/lang/Throwable;)Ljava/lang/Object;

    move-result-object v0

    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;

    .line 709
    :goto_8
    invoke-virtual {v1}, Lcom/bachatas4/android/service/ImportService;->getContentResolver()Landroid/content/ContentResolver;

    move-result-object v0

    invoke-virtual {v0, v10, v13}, Landroid/content/ContentResolver;->openFileDescriptor(Landroid/net/Uri;Ljava/lang/String;)Landroid/os/ParcelFileDescriptor;

    move-result-object v0

    if-eqz v0, :cond_14

    move-object v11, v0

    check-cast v11, Ljava/io/Closeable;
    :try_end_14
    .catchall {:try_start_14 .. :try_end_14} :catchall_1d

    :try_start_15
    move-object v0, v11

    check-cast v0, Landroid/os/ParcelFileDescriptor;

    move-object/from16 v24, v10

    .line 710
    invoke-direct {v1, v0}, Lcom/bachatas4/android/service/ImportService;->isOpenFdSeekable(Landroid/os/ParcelFileDescriptor;)Z

    move-result v10

    move-object/from16 v25, v13

    .line 711
    invoke-virtual {v0}, Landroid/os/ParcelFileDescriptor;->getFd()I

    move-result v13
    :try_end_15
    .catchall {:try_start_15 .. :try_end_15} :catchall_19

    :try_start_16
    new-instance v1, Ljava/lang/StringBuilder;

    invoke-direct {v1}, Ljava/lang/StringBuilder;-><init>()V
    :try_end_16
    .catchall {:try_start_16 .. :try_end_16} :catchall_18

    move-object/from16 v26, v11

    :try_start_17
    const-string v11, "batch probe fd="

    invoke-virtual {v1, v11}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1, v13}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    move-result-object v1

    const-string v11, " seekable="

    invoke-virtual {v1, v11}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1, v10}, Ljava/lang/StringBuilder;->append(Z)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v1

    invoke-static {v14, v1}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    .line 712
    invoke-static {}, Lkotlinx/coroutines/Dispatchers;->getIO()Lkotlinx/coroutines/CoroutineDispatcher;

    move-result-object v1

    check-cast v1, Lkotlin/coroutines/CoroutineContext;

    new-instance v11, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$probe$1$1;

    const/4 v13, 0x0

    invoke-direct {v11, v0, v13}, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$probe$1$1;-><init>(Landroid/os/ParcelFileDescriptor;Lkotlin/coroutines/Continuation;)V

    check-cast v11, Lkotlin/jvm/functions/Function2;

    move-object/from16 v13, v19

    iput-object v3, v13, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$0:Ljava/lang/Object;

    iput-object v9, v13, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$1:Ljava/lang/Object;

    iput-object v4, v13, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$2:Ljava/lang/Object;

    iput-object v6, v13, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$3:Ljava/lang/Object;

    iput-object v5, v13, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$4:Ljava/lang/Object;

    iput-object v7, v13, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$5:Ljava/lang/Object;

    iput-object v8, v13, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$6:Ljava/lang/Object;

    iput-object v15, v13, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$7:Ljava/lang/Object;

    move-object/from16 v19, v3

    invoke-static/range {p1 .. p1}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v3

    iput-object v3, v13, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$8:Ljava/lang/Object;

    iput-object v12, v13, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$9:Ljava/lang/Object;

    iput-object v2, v13, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$10:Ljava/lang/Object;

    move-object/from16 v3, p2

    iput-object v3, v13, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$11:Ljava/lang/Object;

    move-object/from16 v27, v2

    move-object/from16 v2, v23

    iput-object v2, v13, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$12:Ljava/lang/Object;

    move-object/from16 v23, v2

    invoke-static/range {v24 .. v24}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v2

    iput-object v2, v13, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$13:Ljava/lang/Object;
    :try_end_17
    .catchall {:try_start_17 .. :try_end_17} :catchall_17

    move-object/from16 v2, v26

    :try_start_18
    iput-object v2, v13, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$14:Ljava/lang/Object;

    invoke-static {v0}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v0

    iput-object v0, v13, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$15:Ljava/lang/Object;
    :try_end_18
    .catchall {:try_start_18 .. :try_end_18} :catchall_16

    move-object/from16 v26, v2

    move/from16 v2, v22

    :try_start_19
    iput v2, v13, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->I$0:I

    move-object/from16 v24, v3

    move-object/from16 v22, v4

    move-wide/from16 v3, v55

    iput-wide v3, v13, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->J$0:J

    iput-boolean v10, v13, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->Z$0:Z

    const/4 v10, 0x2

    iput v10, v13, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->label:I

    invoke-static {v1, v11, v13}, Lkotlinx/coroutines/BuildersKt;->withContext(Lkotlin/coroutines/CoroutineContext;Lkotlin/jvm/functions/Function2;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;

    move-result-object v0
    :try_end_19
    .catchall {:try_start_19 .. :try_end_19} :catchall_15

    move-object/from16 v10, v21

    if-ne v0, v10, :cond_5

    move-object v6, v10

    goto/16 :goto_48

    :cond_5
    move-object/from16 v1, v23

    move-object/from16 v23, v7

    move-object v7, v1

    move v11, v2

    move-object/from16 v1, v27

    move-object v2, v0

    move-object/from16 v27, v9

    move-object/from16 v9, v24

    move-object/from16 v0, p1

    move-object/from16 v24, v5

    move-object/from16 v5, v26

    move-object/from16 v26, v22

    move-object/from16 v22, v8

    move-object v8, v6

    move-object/from16 v6, v19

    move-object/from16 v19, v13

    :goto_9
    :try_start_1a
    check-cast v2, Lcom/bachatas4/android/runtime/pkg/PkgProbeResult;
    :try_end_1a
    .catchall {:try_start_1a .. :try_end_1a} :catchall_14

    const/4 v13, 0x0

    .line 709
    :try_start_1b
    invoke-static {v5, v13}, Lkotlin/io/CloseableKt;->closeFinally(Ljava/io/Closeable;Ljava/lang/Throwable;)V

    if-nez v2, :cond_6

    move-object/from16 v13, p0

    move v10, v11

    move-object/from16 v21, v22

    move-object v11, v7

    move-object v5, v15

    move-object/from16 v8, v53

    move-object/from16 v1, v54

    goto/16 :goto_1a

    .line 719
    :cond_6
    invoke-virtual {v2}, Lcom/bachatas4/android/runtime/pkg/PkgProbeResult;->getStatus()Lcom/bachatas4/android/runtime/pkg/PkgStatus;

    move-result-object v5

    sget-object v13, Lcom/bachatas4/android/runtime/pkg/PkgStatus;->ERROR:Lcom/bachatas4/android/runtime/pkg/PkgStatus;
    :try_end_1b
    .catchall {:try_start_1b .. :try_end_1b} :catchall_13

    if-ne v5, v13, :cond_b

    .line 720
    :try_start_1c
    sget-object v0, Lcom/bachatas4/android/data/ImportManager;->INSTANCE:Lcom/bachatas4/android/data/ImportManager;

    .line 721
    new-instance v1, Lcom/bachatas4/android/data/ImportProgress$BatchFailed;

    .line 722
    sget-object v3, Lcom/bachatas4/android/data/InstallValidator;->INSTANCE:Lcom/bachatas4/android/data/InstallValidator;

    invoke-virtual {v2}, Lcom/bachatas4/android/runtime/pkg/PkgProbeResult;->getMessage()Ljava/lang/String;

    move-result-object v4

    invoke-virtual {v3, v4}, Lcom/bachatas4/android/data/InstallValidator;->mapProbeError(Ljava/lang/String;)Lcom/bachatas4/android/data/InstallErrorCode;

    move-result-object v3

    .line 723
    invoke-virtual {v2}, Lcom/bachatas4/android/runtime/pkg/PkgProbeResult;->getMessage()Ljava/lang/String;

    move-result-object v2
    :try_end_1c
    .catchall {:try_start_1c .. :try_end_1c} :catchall_d

    if-nez v2, :cond_7

    :try_start_1d
    const-string v2, "Invalid package"
    :try_end_1d
    .catchall {:try_start_1d .. :try_end_1d} :catchall_a

    goto :goto_a

    :catchall_a
    move-exception v0

    move-object/from16 v1, p0

    move-object v12, v14

    move-object v5, v15

    move-object/from16 v8, v22

    move-object/from16 v9, v27

    move-object/from16 v3, v54

    move v14, v11

    move-object/from16 v11, v53

    goto/16 :goto_58

    .line 725
    :cond_7
    :goto_a
    :try_start_1e
    invoke-interface/range {v27 .. v27}, Ljava/util/List;->size()I

    move-result v4

    const/4 v12, 0x0

    .line 721
    invoke-direct {v1, v3, v2, v12, v4}, Lcom/bachatas4/android/data/ImportProgress$BatchFailed;-><init>(Lcom/bachatas4/android/data/InstallErrorCode;Ljava/lang/String;II)V

    check-cast v1, Lcom/bachatas4/android/data/ImportProgress;

    .line 720
    invoke-virtual {v0, v1}, Lcom/bachatas4/android/data/ImportManager;->update(Lcom/bachatas4/android/data/ImportProgress;)V

    .line 728
    sget-object v1, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;
    :try_end_1e
    .catchall {:try_start_1e .. :try_end_1e} :catchall_d

    .line 903
    check-cast v22, Ljava/lang/Iterable;

    .line 1211
    invoke-interface/range {v22 .. v22}, Ljava/lang/Iterable;->iterator()Ljava/util/Iterator;

    move-result-object v2

    :goto_b
    invoke-interface {v2}, Ljava/util/Iterator;->hasNext()Z

    move-result v0

    if-eqz v0, :cond_8

    invoke-interface {v2}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v0

    check-cast v0, Ljava/io/File;

    .line 903
    :try_start_1f
    sget-object v3, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    move-object/from16 v3, p0

    check-cast v3, Lcom/bachatas4/android/service/ImportService;

    invoke-static {v0}, Lkotlin/io/FilesKt;->deleteRecursively(Ljava/io/File;)Z

    move-result v0

    invoke-static {v0}, Lkotlin/coroutines/jvm/internal/Boxing;->boxBoolean(Z)Ljava/lang/Boolean;

    move-result-object v0

    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;
    :try_end_1f
    .catchall {:try_start_1f .. :try_end_1f} :catchall_b

    goto :goto_b

    :catchall_b
    move-exception v0

    sget-object v3, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    invoke-static {v0}, Lkotlin/ResultKt;->createFailure(Ljava/lang/Throwable;)Ljava/lang/Object;

    move-result-object v0

    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;

    goto :goto_b

    .line 904
    :cond_8
    check-cast v15, Ljava/lang/Iterable;

    .line 1219
    invoke-interface {v15}, Ljava/lang/Iterable;->iterator()Ljava/util/Iterator;

    move-result-object v2

    :goto_c
    invoke-interface {v2}, Ljava/util/Iterator;->hasNext()Z

    move-result v0

    if-eqz v0, :cond_9

    invoke-interface {v2}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v0

    check-cast v0, Ljava/io/File;

    .line 904
    :try_start_20
    sget-object v3, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    move-object/from16 v3, p0

    check-cast v3, Lcom/bachatas4/android/service/ImportService;

    invoke-virtual {v0}, Ljava/io/File;->delete()Z

    move-result v0

    invoke-static {v0}, Lkotlin/coroutines/jvm/internal/Boxing;->boxBoolean(Z)Ljava/lang/Boolean;

    move-result-object v0

    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;
    :try_end_20
    .catchall {:try_start_20 .. :try_end_20} :catchall_c

    goto :goto_c

    :catchall_c
    move-exception v0

    sget-object v3, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    invoke-static {v0}, Lkotlin/ResultKt;->createFailure(Ljava/lang/Throwable;)Ljava/lang/Object;

    move-result-object v0

    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;

    goto :goto_c

    :cond_9
    const/4 v15, 0x0

    move-object/from16 v13, p0

    .line 905
    iput-object v15, v13, Lcom/bachatas4/android/service/ImportService;->passcodeWaiter:Lkotlinx/coroutines/CompletableDeferred;

    .line 906
    iput-object v15, v13, Lcom/bachatas4/android/service/ImportService;->copyConfirmWaiter:Lkotlinx/coroutines/CompletableDeferred;

    .line 907
    sget-object v0, Lcom/bachatas4/android/data/ImportManager;->INSTANCE:Lcom/bachatas4/android/data/ImportManager;

    const/4 v12, 0x1

    invoke-static {v0, v15, v12, v15}, Lcom/bachatas4/android/data/ImportManager;->isBusy$default(Lcom/bachatas4/android/data/ImportManager;Lcom/bachatas4/android/data/ImportProgress;ILjava/lang/Object;)Z

    move-result v0

    if-eqz v0, :cond_a

    sget-object v0, Lcom/bachatas4/android/data/ImportManager;->INSTANCE:Lcom/bachatas4/android/data/ImportManager;

    invoke-virtual {v0}, Lcom/bachatas4/android/data/ImportManager;->reset()V

    .line 908
    :cond_a
    invoke-interface/range {v27 .. v27}, Ljava/util/List;->size()I

    move-result v0

    new-instance v2, Ljava/lang/StringBuilder;

    move-object/from16 v5, v54

    invoke-direct {v2, v5}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v2, v11}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    move-result-object v2

    move-object/from16 v3, v53

    invoke-virtual {v2, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v2

    :goto_d
    invoke-virtual {v2, v0}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    invoke-static {v14, v0}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    .line 909
    invoke-virtual {v13}, Lcom/bachatas4/android/service/ImportService;->stopSelf()V

    return-object v1

    :catchall_d
    move-exception v0

    move-object/from16 v13, p0

    move-object/from16 v3, v53

    move-object/from16 v5, v54

    move-object v1, v13

    move-object v12, v14

    move-object/from16 v8, v22

    move-object/from16 v9, v27

    move v14, v11

    move-object v11, v3

    move-object v3, v5

    :goto_e
    move-object v5, v15

    goto/16 :goto_58

    :cond_b
    move-object/from16 v13, p0

    move-object/from16 p1, v8

    move-object/from16 v8, v53

    move-object/from16 v5, v54

    .line 730
    :try_start_21
    invoke-virtual {v2}, Lcom/bachatas4/android/runtime/pkg/PkgProbeResult;->getTitleHint()Ljava/lang/String;

    move-result-object v21
    :try_end_21
    .catchall {:try_start_21 .. :try_end_21} :catchall_12

    if-eqz v21, :cond_c

    :try_start_22
    check-cast v21, Ljava/lang/CharSequence;

    invoke-static/range {v21 .. v21}, Lkotlin/text/StringsKt;->trim(Ljava/lang/CharSequence;)Ljava/lang/CharSequence;

    move-result-object v21

    invoke-virtual/range {v21 .. v21}, Ljava/lang/Object;->toString()Ljava/lang/String;

    move-result-object v21

    goto :goto_f

    :catchall_e
    move-exception v0

    move-object v3, v5

    move-object v1, v13

    move-object v12, v14

    move-object v5, v15

    move-object/from16 v9, v27

    move v14, v11

    move-object v11, v8

    move-object/from16 v8, v22

    goto/16 :goto_58

    :cond_c
    const/16 v21, 0x0

    :goto_f
    if-nez v21, :cond_d

    const-string v21, ""
    :try_end_22
    .catchall {:try_start_22 .. :try_end_22} :catchall_e

    :cond_d
    move-wide/from16 v28, v3

    move-object/from16 v3, v21

    const/4 v4, 0x1

    .line 731
    :try_start_23
    invoke-static {v3, v6, v4}, Lkotlin/text/StringsKt;->equals(Ljava/lang/String;Ljava/lang/String;Z)Z

    move-result v21
    :try_end_23
    .catchall {:try_start_23 .. :try_end_23} :catchall_12

    if-nez v21, :cond_11

    .line 732
    :try_start_24
    sget-object v0, Lcom/bachatas4/android/data/ImportManager;->INSTANCE:Lcom/bachatas4/android/data/ImportManager;

    .line 733
    new-instance v1, Lcom/bachatas4/android/data/ImportProgress$BatchFailed;

    .line 734
    sget-object v2, Lcom/bachatas4/android/data/InstallErrorCode;->MALFORMED_PACKAGE:Lcom/bachatas4/android/data/InstallErrorCode;

    .line 735
    new-instance v4, Ljava/lang/StringBuilder;

    invoke-direct {v4}, Ljava/lang/StringBuilder;-><init>()V

    const-string v7, "PKG TITLE_ID \'"

    invoke-virtual {v4, v7}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v4

    invoke-virtual {v4, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v3

    const-string v4, "\' does not match \'"

    invoke-virtual {v3, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v3

    invoke-virtual {v3, v6}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v3

    const-string v4, "\'"

    invoke-virtual {v3, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v3

    invoke-virtual {v3}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v3

    .line 737
    invoke-interface/range {v27 .. v27}, Ljava/util/List;->size()I

    move-result v4

    const/4 v12, 0x0

    .line 733
    invoke-direct {v1, v2, v3, v12, v4}, Lcom/bachatas4/android/data/ImportProgress$BatchFailed;-><init>(Lcom/bachatas4/android/data/InstallErrorCode;Ljava/lang/String;II)V

    check-cast v1, Lcom/bachatas4/android/data/ImportProgress;

    .line 732
    invoke-virtual {v0, v1}, Lcom/bachatas4/android/data/ImportManager;->update(Lcom/bachatas4/android/data/ImportProgress;)V

    .line 740
    sget-object v1, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;
    :try_end_24
    .catchall {:try_start_24 .. :try_end_24} :catchall_e

    .line 903
    check-cast v22, Ljava/lang/Iterable;

    .line 1211
    invoke-interface/range {v22 .. v22}, Ljava/lang/Iterable;->iterator()Ljava/util/Iterator;

    move-result-object v2

    :goto_10
    invoke-interface {v2}, Ljava/util/Iterator;->hasNext()Z

    move-result v0

    if-eqz v0, :cond_e

    invoke-interface {v2}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v0

    check-cast v0, Ljava/io/File;

    .line 903
    :try_start_25
    sget-object v3, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    move-object v3, v13

    check-cast v3, Lcom/bachatas4/android/service/ImportService;

    invoke-static {v0}, Lkotlin/io/FilesKt;->deleteRecursively(Ljava/io/File;)Z

    move-result v0

    invoke-static {v0}, Lkotlin/coroutines/jvm/internal/Boxing;->boxBoolean(Z)Ljava/lang/Boolean;

    move-result-object v0

    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;
    :try_end_25
    .catchall {:try_start_25 .. :try_end_25} :catchall_f

    goto :goto_10

    :catchall_f
    move-exception v0

    sget-object v3, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    invoke-static {v0}, Lkotlin/ResultKt;->createFailure(Ljava/lang/Throwable;)Ljava/lang/Object;

    move-result-object v0

    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;

    goto :goto_10

    .line 904
    :cond_e
    check-cast v15, Ljava/lang/Iterable;

    .line 1222
    invoke-interface {v15}, Ljava/lang/Iterable;->iterator()Ljava/util/Iterator;

    move-result-object v2

    :goto_11
    invoke-interface {v2}, Ljava/util/Iterator;->hasNext()Z

    move-result v0

    if-eqz v0, :cond_f

    invoke-interface {v2}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v0

    check-cast v0, Ljava/io/File;

    .line 904
    :try_start_26
    sget-object v3, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    move-object v3, v13

    check-cast v3, Lcom/bachatas4/android/service/ImportService;

    invoke-virtual {v0}, Ljava/io/File;->delete()Z

    move-result v0

    invoke-static {v0}, Lkotlin/coroutines/jvm/internal/Boxing;->boxBoolean(Z)Ljava/lang/Boolean;

    move-result-object v0

    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;
    :try_end_26
    .catchall {:try_start_26 .. :try_end_26} :catchall_10

    goto :goto_11

    :catchall_10
    move-exception v0

    sget-object v3, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    invoke-static {v0}, Lkotlin/ResultKt;->createFailure(Ljava/lang/Throwable;)Ljava/lang/Object;

    move-result-object v0

    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;

    goto :goto_11

    :cond_f
    const/4 v15, 0x0

    .line 905
    iput-object v15, v13, Lcom/bachatas4/android/service/ImportService;->passcodeWaiter:Lkotlinx/coroutines/CompletableDeferred;

    .line 906
    iput-object v15, v13, Lcom/bachatas4/android/service/ImportService;->copyConfirmWaiter:Lkotlinx/coroutines/CompletableDeferred;

    .line 907
    sget-object v0, Lcom/bachatas4/android/data/ImportManager;->INSTANCE:Lcom/bachatas4/android/data/ImportManager;

    const/4 v12, 0x1

    invoke-static {v0, v15, v12, v15}, Lcom/bachatas4/android/data/ImportManager;->isBusy$default(Lcom/bachatas4/android/data/ImportManager;Lcom/bachatas4/android/data/ImportProgress;ILjava/lang/Object;)Z

    move-result v0

    if-eqz v0, :cond_10

    sget-object v0, Lcom/bachatas4/android/data/ImportManager;->INSTANCE:Lcom/bachatas4/android/data/ImportManager;

    invoke-virtual {v0}, Lcom/bachatas4/android/data/ImportManager;->reset()V

    .line 908
    :cond_10
    invoke-interface/range {v27 .. v27}, Ljava/util/List;->size()I

    move-result v0

    new-instance v2, Ljava/lang/StringBuilder;

    invoke-direct {v2, v5}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v2, v11}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    move-result-object v2

    invoke-virtual {v2, v8}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v2

    goto/16 :goto_d

    .line 742
    :cond_11
    :try_start_27
    invoke-static {v7, v2}, Lkotlin/TuplesKt;->to(Ljava/lang/Object;Ljava/lang/Object;)Lkotlin/Pair;

    move-result-object v3

    invoke-interface {v1, v3}, Ljava/util/List;->add(Ljava/lang/Object;)Z

    .line 743
    invoke-virtual {v2}, Lcom/bachatas4/android/runtime/pkg/PkgProbeResult;->getPfsImageSize()J

    move-result-wide v3

    invoke-static {v3, v4}, Lkotlin/coroutines/jvm/internal/Boxing;->boxLong(J)Ljava/lang/Long;

    move-result-object v3

    move-object v4, v3

    check-cast v4, Ljava/lang/Number;

    invoke-virtual {v4}, Ljava/lang/Number;->longValue()J

    move-result-wide v30
    :try_end_27
    .catchall {:try_start_27 .. :try_end_27} :catchall_12

    move v4, v11

    move-object/from16 p2, v12

    const-wide/16 v11, 0x0

    cmp-long v7, v30, v11

    if-lez v7, :cond_12

    goto :goto_12

    :cond_12
    const/4 v3, 0x0

    :goto_12
    if-eqz v3, :cond_13

    :try_start_28
    invoke-virtual {v3}, Ljava/lang/Long;->longValue()J

    move-result-wide v2

    goto :goto_13

    :cond_13
    invoke-virtual {v2}, Lcom/bachatas4/android/runtime/pkg/PkgProbeResult;->getPackageSize()J

    move-result-wide v2

    :goto_13
    invoke-static {v2, v3, v11, v12}, Lkotlin/ranges/RangesKt;->coerceAtLeast(JJ)J

    move-result-wide v2
    :try_end_28
    .catchall {:try_start_28 .. :try_end_28} :catchall_11

    add-long v55, v28, v2

    move-object/from16 v12, p2

    move-object v2, v1

    move-object/from16 v54, v5

    move-object v3, v6

    move-object/from16 v53, v8

    move-object/from16 p2, v9

    move-object v11, v10

    move-object v1, v13

    move-object/from16 v8, v22

    move-object/from16 v7, v23

    move-object/from16 v5, v24

    move-object/from16 v13, v25

    move-object/from16 v9, v27

    move-object/from16 v6, p1

    move-object/from16 p1, v0

    move v10, v4

    move-object/from16 v4, v26

    goto/16 :goto_6

    :catchall_11
    move-exception v0

    goto :goto_14

    :catchall_12
    move-exception v0

    move v4, v11

    goto :goto_14

    :catchall_13
    move-exception v0

    move-object/from16 v13, p0

    move v4, v11

    move-object/from16 v8, v53

    move-object/from16 v5, v54

    :goto_14
    move-object v3, v5

    move-object v11, v8

    move-object v1, v13

    move-object v12, v14

    move-object v5, v15

    move-object/from16 v8, v22

    move-object/from16 v9, v27

    goto/16 :goto_4d

    :catchall_14
    move-exception v0

    move-object/from16 v13, p0

    move v4, v11

    move-object/from16 v8, v53

    move-object/from16 v1, v54

    move-object v2, v0

    move-object v3, v5

    move-object v5, v15

    move-object/from16 v21, v22

    move-object/from16 v9, v27

    goto :goto_19

    :catchall_15
    move-exception v0

    move-object/from16 v13, p0

    move-object/from16 v21, v8

    goto :goto_18

    :catchall_16
    move-exception v0

    move-object/from16 v13, p0

    move-object/from16 v26, v2

    goto :goto_15

    :catchall_17
    move-exception v0

    move-object/from16 v13, p0

    :goto_15
    move-object/from16 v21, v8

    goto :goto_17

    :catchall_18
    move-exception v0

    move-object/from16 v13, p0

    goto :goto_16

    :catchall_19
    move-exception v0

    move-object v13, v1

    :goto_16
    move-object/from16 v21, v8

    move-object/from16 v26, v11

    :goto_17
    move/from16 v2, v22

    :goto_18
    move-object/from16 v8, v53

    move-object/from16 v1, v54

    move v4, v2

    move-object v5, v15

    move-object/from16 v3, v26

    goto/16 :goto_1

    .line 709
    :goto_19
    :try_start_29
    throw v2
    :try_end_29
    .catchall {:try_start_29 .. :try_end_29} :catchall_1a

    :catchall_1a
    move-exception v0

    :try_start_2a
    invoke-static {v3, v2}, Lkotlin/io/CloseableKt;->closeFinally(Ljava/io/Closeable;Ljava/lang/Throwable;)V

    throw v0
    :try_end_2a
    .catchall {:try_start_2a .. :try_end_2a} :catchall_1b

    :catchall_1b
    move-exception v0

    move-object v3, v1

    move-object v11, v8

    move-object v1, v13

    move-object v12, v14

    move-object/from16 v8, v21

    goto/16 :goto_4d

    :cond_14
    move-object v13, v1

    move-object/from16 v21, v8

    move/from16 v2, v22

    move v10, v2

    move-object/from16 v27, v9

    move-object/from16 v11, v23

    move-object/from16 v8, v53

    move-object/from16 v1, v54

    move-object v5, v15

    .line 713
    :goto_1a
    :try_start_2b
    move-object v0, v13

    check-cast v0, Lcom/bachatas4/android/service/ImportService;

    .line 714
    sget-object v0, Lcom/bachatas4/android/data/ImportManager;->INSTANCE:Lcom/bachatas4/android/data/ImportManager;

    .line 715
    new-instance v2, Lcom/bachatas4/android/data/ImportProgress$BatchFailed;

    sget-object v3, Lcom/bachatas4/android/data/InstallErrorCode;->SOURCE_INACCESSIBLE:Lcom/bachatas4/android/data/InstallErrorCode;

    new-instance v4, Ljava/lang/StringBuilder;

    invoke-direct {v4}, Ljava/lang/StringBuilder;-><init>()V

    const-string v6, "Cannot open "

    invoke-virtual {v4, v6}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v4

    invoke-virtual {v4, v11}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v4

    invoke-virtual {v4}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v4

    invoke-interface/range {v27 .. v27}, Ljava/util/List;->size()I

    move-result v6

    const/4 v12, 0x0

    invoke-direct {v2, v3, v4, v12, v6}, Lcom/bachatas4/android/data/ImportProgress$BatchFailed;-><init>(Lcom/bachatas4/android/data/InstallErrorCode;Ljava/lang/String;II)V

    check-cast v2, Lcom/bachatas4/android/data/ImportProgress;

    .line 714
    invoke-virtual {v0, v2}, Lcom/bachatas4/android/data/ImportManager;->update(Lcom/bachatas4/android/data/ImportProgress;)V

    .line 717
    sget-object v0, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;
    :try_end_2b
    .catchall {:try_start_2b .. :try_end_2b} :catchall_1c

    .line 903
    check-cast v21, Ljava/lang/Iterable;

    .line 1211
    invoke-interface/range {v21 .. v21}, Ljava/lang/Iterable;->iterator()Ljava/util/Iterator;

    move-result-object v2

    :goto_1b
    invoke-interface {v2}, Ljava/util/Iterator;->hasNext()Z

    move-result v3

    if-eqz v3, :cond_15

    invoke-interface {v2}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v3

    check-cast v3, Ljava/io/File;

    .line 903
    sget-object v4, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    move-object v4, v13

    check-cast v4, Lcom/bachatas4/android/service/ImportService;

    invoke-static {v3}, Lkotlin/io/FilesKt;->deleteRecursively(Ljava/io/File;)Z

    move-result v3

    invoke-static {v3}, Lkotlin/coroutines/jvm/internal/Boxing;->boxBoolean(Z)Ljava/lang/Boolean;

    move-result-object v3

    invoke-static {v3}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;

    goto :goto_1b

    .line 904
    :cond_15
    check-cast v5, Ljava/lang/Iterable;

    .line 1216
    invoke-interface {v5}, Ljava/lang/Iterable;->iterator()Ljava/util/Iterator;

    move-result-object v2

    :goto_1c
    invoke-interface {v2}, Ljava/util/Iterator;->hasNext()Z

    move-result v3

    if-eqz v3, :cond_16

    invoke-interface {v2}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v3

    check-cast v3, Ljava/io/File;

    .line 904
    sget-object v4, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    move-object v4, v13

    check-cast v4, Lcom/bachatas4/android/service/ImportService;

    invoke-virtual {v3}, Ljava/io/File;->delete()Z

    move-result v3

    invoke-static {v3}, Lkotlin/coroutines/jvm/internal/Boxing;->boxBoolean(Z)Ljava/lang/Boolean;

    move-result-object v3

    invoke-static {v3}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;

    goto :goto_1c

    :cond_16
    const/4 v15, 0x0

    .line 905
    iput-object v15, v13, Lcom/bachatas4/android/service/ImportService;->passcodeWaiter:Lkotlinx/coroutines/CompletableDeferred;

    .line 906
    iput-object v15, v13, Lcom/bachatas4/android/service/ImportService;->copyConfirmWaiter:Lkotlinx/coroutines/CompletableDeferred;

    .line 907
    sget-object v2, Lcom/bachatas4/android/data/ImportManager;->INSTANCE:Lcom/bachatas4/android/data/ImportManager;

    const/4 v12, 0x1

    invoke-static {v2, v15, v12, v15}, Lcom/bachatas4/android/data/ImportManager;->isBusy$default(Lcom/bachatas4/android/data/ImportManager;Lcom/bachatas4/android/data/ImportProgress;ILjava/lang/Object;)Z

    move-result v2

    if-eqz v2, :cond_17

    sget-object v2, Lcom/bachatas4/android/data/ImportManager;->INSTANCE:Lcom/bachatas4/android/data/ImportManager;

    invoke-virtual {v2}, Lcom/bachatas4/android/data/ImportManager;->reset()V

    .line 908
    :cond_17
    invoke-interface/range {v27 .. v27}, Ljava/util/List;->size()I

    move-result v2

    new-instance v3, Ljava/lang/StringBuilder;

    invoke-direct {v3, v1}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v3, v10}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1, v8}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v1

    invoke-static {v14, v1}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    .line 909
    invoke-virtual {v13}, Lcom/bachatas4/android/service/ImportService;->stopSelf()V

    return-object v0

    :catchall_1c
    move-exception v0

    move-object v3, v1

    move-object v11, v8

    move-object v1, v13

    move-object v12, v14

    move-object/from16 v8, v21

    move-object/from16 v9, v27

    goto/16 :goto_57

    :catchall_1d
    move-exception v0

    move-object v13, v1

    move-object/from16 v21, v8

    move/from16 v2, v22

    goto :goto_1d

    :catchall_1e
    move-exception v0

    move-object v13, v1

    move-object/from16 v21, v8

    move v2, v10

    :goto_1d
    move-object/from16 v8, v53

    move-object/from16 v1, v54

    move-object v3, v1

    move-object v11, v8

    move-object v1, v13

    move-object v12, v14

    move-object v5, v15

    move-object/from16 v8, v21

    move v14, v2

    goto/16 :goto_58

    :cond_18
    move-object/from16 v27, v2

    move-object/from16 v22, v4

    move-object/from16 v21, v8

    move v2, v10

    move-object v10, v11

    move-object/from16 v25, v13

    move-object/from16 v13, v19

    move-object/from16 v8, v53

    move-object v11, v1

    move-object/from16 v19, v3

    move-object/from16 v1, v54

    move-wide/from16 v3, v55

    const-wide/16 v23, 0x14

    move-wide/from16 v28, v3

    .line 747
    :try_start_2c
    div-long v3, v28, v23

    move-object/from16 v24, v5

    move-object/from16 v23, v6

    const-wide/32 v5, 0x10000000

    invoke-static {v5, v6, v3, v4}, Ljava/lang/Math;->max(JJ)J

    move-result-wide v3

    add-long v5, v28, v3

    .line 749
    invoke-virtual {v11}, Lcom/bachatas4/android/service/ImportService;->getFilesDir()Ljava/io/File;

    move-result-object v0

    move-wide/from16 v30, v3

    invoke-virtual {v0}, Ljava/io/File;->getUsableSpace()J

    move-result-wide v3

    .line 750
    new-instance v0, Ljava/lang/StringBuilder;

    invoke-direct {v0}, Ljava/lang/StringBuilder;-><init>()V

    move-object/from16 v26, v7

    const-string v7, "pkg batch storage required="

    invoke-virtual {v0, v7}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0, v5, v6}, Ljava/lang/StringBuilder;->append(J)Ljava/lang/StringBuilder;

    move-result-object v0

    const-string v7, " free="

    invoke-virtual {v0, v7}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0, v3, v4}, Ljava/lang/StringBuilder;->append(J)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    invoke-static {v14, v0}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    .line 751
    sget-object v0, Lcom/bachatas4/android/data/InstallValidator;->INSTANCE:Lcom/bachatas4/android/data/InstallValidator;

    invoke-virtual {v0, v5, v6, v3, v4}, Lcom/bachatas4/android/data/InstallValidator;->checkStorage(JJ)Lcom/bachatas4/android/data/InstallErrorCode;

    move-result-object v0
    :try_end_2c
    .catchall {:try_start_2c .. :try_end_2c} :catchall_57

    if-eqz v0, :cond_1c

    .line 752
    :try_start_2d
    sget-object v7, Lcom/bachatas4/android/data/ImportManager;->INSTANCE:Lcom/bachatas4/android/data/ImportManager;

    .line 753
    new-instance v10, Lcom/bachatas4/android/data/ImportProgress$BatchFailed;

    sget-object v12, Lcom/bachatas4/android/service/ImportService;->Companion:Lcom/bachatas4/android/service/ImportService$Companion;

    invoke-virtual {v12, v5, v6}, Lcom/bachatas4/android/service/ImportService$Companion;->formatBytes(J)Ljava/lang/String;

    move-result-object v5

    invoke-virtual {v12, v3, v4}, Lcom/bachatas4/android/service/ImportService$Companion;->formatBytes(J)Ljava/lang/String;

    move-result-object v3

    new-instance v4, Ljava/lang/StringBuilder;

    invoke-direct {v4}, Ljava/lang/StringBuilder;-><init>()V

    const-string v6, "Need "

    invoke-virtual {v4, v6}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v4

    invoke-virtual {v4, v5}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v4

    const-string v5, " free, have "

    invoke-virtual {v4, v5}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v4

    invoke-virtual {v4, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v3

    invoke-virtual {v3}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v3

    invoke-interface {v9}, Ljava/util/List;->size()I

    move-result v4

    const/4 v12, 0x0

    invoke-direct {v10, v0, v3, v12, v4}, Lcom/bachatas4/android/data/ImportProgress$BatchFailed;-><init>(Lcom/bachatas4/android/data/InstallErrorCode;Ljava/lang/String;II)V

    check-cast v10, Lcom/bachatas4/android/data/ImportProgress;

    .line 752
    invoke-virtual {v7, v10}, Lcom/bachatas4/android/data/ImportManager;->update(Lcom/bachatas4/android/data/ImportProgress;)V

    .line 755
    sget-object v0, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;
    :try_end_2d
    .catchall {:try_start_2d .. :try_end_2d} :catchall_1f

    .line 903
    move-object/from16 v3, v21

    check-cast v3, Ljava/lang/Iterable;

    .line 1211
    invoke-interface {v3}, Ljava/lang/Iterable;->iterator()Ljava/util/Iterator;

    move-result-object v3

    :goto_1e
    invoke-interface {v3}, Ljava/util/Iterator;->hasNext()Z

    move-result v4

    if-eqz v4, :cond_19

    invoke-interface {v3}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v4

    check-cast v4, Ljava/io/File;

    .line 903
    sget-object v5, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    move-object v5, v11

    check-cast v5, Lcom/bachatas4/android/service/ImportService;

    invoke-static {v4}, Lkotlin/io/FilesKt;->deleteRecursively(Ljava/io/File;)Z

    move-result v4

    invoke-static {v4}, Lkotlin/coroutines/jvm/internal/Boxing;->boxBoolean(Z)Ljava/lang/Boolean;

    move-result-object v4

    invoke-static {v4}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;

    goto :goto_1e

    .line 904
    :cond_19
    check-cast v15, Ljava/lang/Iterable;

    .line 1225
    invoke-interface {v15}, Ljava/lang/Iterable;->iterator()Ljava/util/Iterator;

    move-result-object v3

    :goto_1f
    invoke-interface {v3}, Ljava/util/Iterator;->hasNext()Z

    move-result v4

    if-eqz v4, :cond_1a

    invoke-interface {v3}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v4

    check-cast v4, Ljava/io/File;

    .line 904
    sget-object v5, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    move-object v5, v11

    check-cast v5, Lcom/bachatas4/android/service/ImportService;

    invoke-virtual {v4}, Ljava/io/File;->delete()Z

    move-result v4

    invoke-static {v4}, Lkotlin/coroutines/jvm/internal/Boxing;->boxBoolean(Z)Ljava/lang/Boolean;

    move-result-object v4

    invoke-static {v4}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;

    goto :goto_1f

    :cond_1a
    const/4 v15, 0x0

    .line 905
    iput-object v15, v11, Lcom/bachatas4/android/service/ImportService;->passcodeWaiter:Lkotlinx/coroutines/CompletableDeferred;

    .line 906
    iput-object v15, v11, Lcom/bachatas4/android/service/ImportService;->copyConfirmWaiter:Lkotlinx/coroutines/CompletableDeferred;

    .line 907
    sget-object v3, Lcom/bachatas4/android/data/ImportManager;->INSTANCE:Lcom/bachatas4/android/data/ImportManager;

    const/4 v12, 0x1

    invoke-static {v3, v15, v12, v15}, Lcom/bachatas4/android/data/ImportManager;->isBusy$default(Lcom/bachatas4/android/data/ImportManager;Lcom/bachatas4/android/data/ImportProgress;ILjava/lang/Object;)Z

    move-result v3

    if-eqz v3, :cond_1b

    sget-object v3, Lcom/bachatas4/android/data/ImportManager;->INSTANCE:Lcom/bachatas4/android/data/ImportManager;

    invoke-virtual {v3}, Lcom/bachatas4/android/data/ImportManager;->reset()V

    .line 908
    :cond_1b
    invoke-interface {v9}, Ljava/util/List;->size()I

    move-result v3

    new-instance v4, Ljava/lang/StringBuilder;

    invoke-direct {v4, v1}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v4, v2}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1, v8}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1, v3}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v1

    invoke-static {v14, v1}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    .line 909
    invoke-virtual {v11}, Lcom/bachatas4/android/service/ImportService;->stopSelf()V

    return-object v0

    :catchall_1f
    move-exception v0

    move-object v3, v1

    move-object v1, v11

    move-object v12, v14

    move-object v5, v15

    move v14, v2

    move-object v11, v8

    goto/16 :goto_4f

    .line 759
    :cond_1c
    :try_start_2e
    move-object/from16 v0, v27

    check-cast v0, Ljava/lang/Iterable;

    invoke-interface {v0}, Ljava/lang/Iterable;->iterator()Ljava/util/Iterator;

    move-result-object v0
    :try_end_2e
    .catchall {:try_start_2e .. :try_end_2e} :catchall_57

    move-object v7, v12

    move-object v12, v0

    move-object v0, v7

    move-object v7, v10

    move v10, v2

    move-object/from16 v2, v22

    move-object/from16 v22, v7

    move-object/from16 v54, v1

    move-wide/from16 v59, v3

    move-wide/from16 v57, v5

    move-object/from16 v53, v8

    move-object v6, v13

    move-object v1, v15

    move-object/from16 v15, v19

    move-object/from16 v7, v21

    move-object/from16 v3, v23

    move-object/from16 v13, v24

    move-object/from16 v8, v26

    move-object/from16 v4, v27

    move-wide/from16 v26, v28

    move-wide/from16 v23, v30

    const/4 v5, 0x0

    move-object/from16 v19, p1

    :goto_20
    :try_start_2f
    invoke-interface {v12}, Ljava/util/Iterator;->hasNext()Z

    move-result v21
    :try_end_2f
    .catchall {:try_start_2f .. :try_end_2f} :catchall_56

    if-eqz v21, :cond_37

    move/from16 v21, v10

    add-int/lit8 v10, v5, 0x1

    :try_start_30
    invoke-interface {v12}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v28

    check-cast v28, Lkotlin/Pair;

    .line 760
    invoke-virtual/range {v28 .. v28}, Lkotlin/Pair;->component1()Ljava/lang/Object;

    move-result-object v29

    move/from16 p1, v10

    move-object/from16 v10, v29

    check-cast v10, Ljava/lang/String;

    invoke-virtual/range {v28 .. v28}, Lkotlin/Pair;->component2()Ljava/lang/Object;

    move-result-object v29

    move-object/from16 p2, v10

    move-object/from16 v10, v29

    check-cast v10, Lcom/bachatas4/android/runtime/pkg/PkgProbeResult;

    .line 761
    invoke-interface {v6}, Lkotlin/coroutines/Continuation;->getContext()Lkotlin/coroutines/CoroutineContext;

    move-result-object v29

    invoke-static/range {v29 .. v29}, Lkotlinx/coroutines/JobKt;->ensureActive(Lkotlin/coroutines/CoroutineContext;)V

    .line 762
    invoke-virtual {v10}, Lcom/bachatas4/android/runtime/pkg/PkgProbeResult;->getTitleHint()Ljava/lang/String;

    move-result-object v29
    :try_end_30
    .catchall {:try_start_30 .. :try_end_30} :catchall_4f

    if-eqz v29, :cond_1e

    :try_start_31
    check-cast v29, Ljava/lang/CharSequence;

    invoke-static/range {v29 .. v29}, Lkotlin/text/StringsKt;->isBlank(Ljava/lang/CharSequence;)Z

    move-result v30

    if-eqz v30, :cond_1d

    const/16 v29, 0x0

    :cond_1d
    check-cast v29, Ljava/lang/String;
    :try_end_31
    .catchall {:try_start_31 .. :try_end_31} :catchall_20

    if-nez v29, :cond_20

    goto :goto_21

    :catchall_20
    move-exception v0

    move-object v5, v1

    move-object v8, v7

    move-object v1, v11

    move-object v12, v14

    move/from16 v14, v21

    goto/16 :goto_4

    :cond_1e
    :goto_21
    :try_start_32
    invoke-virtual {v10}, Lcom/bachatas4/android/runtime/pkg/PkgProbeResult;->getContentId()Ljava/lang/String;

    move-result-object v29

    check-cast v29, Ljava/lang/CharSequence;

    invoke-static/range {v29 .. v29}, Lkotlin/text/StringsKt;->isBlank(Ljava/lang/CharSequence;)Z

    move-result v30
    :try_end_32
    .catchall {:try_start_32 .. :try_end_32} :catchall_4f

    if-eqz v30, :cond_1f

    :try_start_33
    const-string v29, "PKG"
    :try_end_33
    .catchall {:try_start_33 .. :try_end_33} :catchall_20

    :cond_1f
    :try_start_34
    check-cast v29, Ljava/lang/String;

    :cond_20
    move-object/from16 v61, v29

    move-object/from16 v29, v10

    .line 763
    new-instance v10, Ljava/io/File;

    move-object/from16 v30, v12

    new-instance v12, Ljava/lang/StringBuilder;

    invoke-direct {v12}, Ljava/lang/StringBuilder;-><init>()V

    move-object/from16 v31, v4

    const-string v4, ".import-batch-"

    invoke-virtual {v12, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v4

    invoke-virtual {v4, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v4

    move-object/from16 v12, v18

    invoke-virtual {v4, v12}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v4

    invoke-virtual {v4, v5}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    move-result-object v4

    invoke-virtual {v4}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v4

    invoke-direct {v10, v3, v4}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    invoke-virtual {v10}, Ljava/io/File;->getCanonicalFile()Ljava/io/File;

    move-result-object v10

    .line 764
    move-object v4, v7

    check-cast v4, Ljava/util/Collection;

    invoke-interface {v4, v10}, Ljava/util/Collection;->add(Ljava/lang/Object;)Z

    .line 765
    invoke-virtual {v10}, Ljava/io/File;->mkdirs()Z

    .line 766
    invoke-virtual {v10}, Ljava/io/File;->getAbsolutePath()Ljava/lang/String;

    move-result-object v4

    move-object/from16 v18, v10

    new-instance v10, Ljava/lang/StringBuilder;

    invoke-direct {v10}, Ljava/lang/StringBuilder;-><init>()V
    :try_end_34
    .catchall {:try_start_34 .. :try_end_34} :catchall_4f

    move-object/from16 v32, v1

    :try_start_35
    const-string v1, "pkg batch staging="

    invoke-virtual {v10, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v1

    invoke-static {v14, v1}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    .line 769
    invoke-static/range {p2 .. p2}, Landroid/net/Uri;->parse(Ljava/lang/String;)Landroid/net/Uri;

    move-result-object v1
    :try_end_35
    .catchall {:try_start_35 .. :try_end_35} :catchall_4e

    move-object v4, v7

    move-object v10, v8

    .line 770
    :try_start_36
    invoke-virtual/range {v29 .. v29}, Lcom/bachatas4/android/runtime/pkg/PkgProbeResult;->getPackageSize()J

    move-result-wide v7
    :try_end_36
    .catchall {:try_start_36 .. :try_end_36} :catchall_4d

    move-object/from16 v33, v3

    move-object/from16 v34, v4

    const-wide/16 v3, 0x0

    :try_start_37
    invoke-static {v7, v8, v3, v4}, Lkotlin/ranges/RangesKt;->coerceAtLeast(JJ)J

    move-result-wide v7

    .line 771
    invoke-virtual {v11}, Lcom/bachatas4/android/service/ImportService;->getContentResolver()Landroid/content/ContentResolver;

    move-result-object v3

    move-object/from16 v4, v25

    invoke-virtual {v3, v1, v4}, Landroid/content/ContentResolver;->openFileDescriptor(Landroid/net/Uri;Ljava/lang/String;)Landroid/os/ParcelFileDescriptor;

    move-result-object v3
    :try_end_37
    .catchall {:try_start_37 .. :try_end_37} :catchall_4c

    if-eqz v3, :cond_21

    :try_start_38
    check-cast v3, Ljava/io/Closeable;
    :try_end_38
    .catchall {:try_start_38 .. :try_end_38} :catchall_23

    move-object/from16 v25, v10

    :try_start_39
    move-object v10, v3

    check-cast v10, Landroid/os/ParcelFileDescriptor;

    invoke-direct {v11, v10}, Lcom/bachatas4/android/service/ImportService;->isOpenFdSeekable(Landroid/os/ParcelFileDescriptor;)Z

    move-result v10
    :try_end_39
    .catchall {:try_start_39 .. :try_end_39} :catchall_21

    move/from16 v35, v10

    const/4 v10, 0x0

    :try_start_3a
    invoke-static {v3, v10}, Lkotlin/io/CloseableKt;->closeFinally(Ljava/io/Closeable;Ljava/lang/Throwable;)V
    :try_end_3a
    .catchall {:try_start_3a .. :try_end_3a} :catchall_23

    move/from16 v10, v35

    goto :goto_22

    :catchall_21
    move-exception v0

    move-object v1, v0

    :try_start_3b
    throw v1
    :try_end_3b
    .catchall {:try_start_3b .. :try_end_3b} :catchall_22

    :catchall_22
    move-exception v0

    :try_start_3c
    invoke-static {v3, v1}, Lkotlin/io/CloseableKt;->closeFinally(Ljava/io/Closeable;Ljava/lang/Throwable;)V

    throw v0

    :catchall_23
    move-exception v0

    move-object v1, v11

    move-object v12, v14

    move/from16 v14, v21

    move-object/from16 v5, v32

    move-object/from16 v8, v34

    goto/16 :goto_4

    :cond_21
    move-object/from16 v25, v10

    const/4 v10, 0x0

    :goto_22
    if-eqz v10, :cond_23

    .line 773
    invoke-virtual {v11}, Lcom/bachatas4/android/service/ImportService;->getContentResolver()Landroid/content/ContentResolver;

    move-result-object v3

    invoke-virtual {v3, v1, v4}, Landroid/content/ContentResolver;->openFileDescriptor(Landroid/net/Uri;Ljava/lang/String;)Landroid/os/ParcelFileDescriptor;

    move-result-object v3

    if-eqz v3, :cond_22

    move-object/from16 v36, v4

    move-object/from16 v43, v9

    move v11, v10

    move-wide/from16 v62, v23

    move-object/from16 v39, v25

    move-object/from16 v4, v31

    move-object/from16 v64, v54

    const-wide/16 v51, 0x0

    move/from16 v9, p1

    move-object/from16 v31, p2

    move-object/from16 v25, v12

    move-object/from16 v12, v22

    goto/16 :goto_24

    :cond_22
    new-instance v0, Ljava/lang/IllegalStateException;

    const-string v1, "Cannot reopen PKG for batch extract"

    invoke-virtual {v1}, Ljava/lang/Object;->toString()Ljava/lang/String;

    move-result-object v1

    invoke-direct {v0, v1}, Ljava/lang/IllegalStateException;-><init>(Ljava/lang/String;)V

    throw v0
    :try_end_3c
    .catchall {:try_start_3c .. :try_end_3c} :catchall_23

    .line 775
    :cond_23
    :try_start_3d
    new-instance v3, Ljava/io/File;

    move-object/from16 v35, v1

    invoke-virtual {v11}, Lcom/bachatas4/android/service/ImportService;->getFilesDir()Ljava/io/File;

    move-result-object v1

    move-object/from16 v36, v4

    const-string v4, "pkg-cache"

    invoke-direct {v3, v1, v4}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    invoke-virtual {v3}, Ljava/io/File;->getCanonicalFile()Ljava/io/File;

    move-result-object v1

    .line 776
    invoke-virtual {v1}, Ljava/io/File;->mkdirs()Z

    .line 777
    new-instance v3, Ljava/io/File;

    new-instance v4, Ljava/lang/StringBuilder;

    invoke-direct {v4}, Ljava/lang/StringBuilder;-><init>()V

    const-string v11, "batch-"

    invoke-virtual {v4, v11}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v4

    invoke-virtual {v4, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v4

    invoke-virtual {v4, v12}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v4

    invoke-virtual {v4, v5}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    move-result-object v4

    const-string v11, ".pkg"

    invoke-virtual {v4, v11}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v4

    invoke-virtual {v4}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v4

    invoke-direct {v3, v1, v4}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    invoke-virtual {v3}, Ljava/io/File;->getCanonicalFile()Ljava/io/File;

    move-result-object v3

    .line 778
    move-object/from16 v4, v32

    check-cast v4, Ljava/util/Collection;

    invoke-interface {v4, v3}, Ljava/util/Collection;->add(Ljava/lang/Object;)Z

    .line 779
    invoke-virtual {v3}, Ljava/io/File;->getAbsolutePath()Ljava/lang/String;

    move-result-object v4

    new-instance v11, Ljava/lang/StringBuilder;

    invoke-direct {v11}, Ljava/lang/StringBuilder;-><init>()V

    move-object/from16 v37, v1

    const-string v1, "pkg batch cache copy dest="

    invoke-virtual {v11, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    const-string v4, " size="

    invoke-virtual {v1, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1, v7, v8}, Ljava/lang/StringBuilder;->append(J)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v1

    invoke-static {v14, v1}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    .line 780
    invoke-static/range {v35 .. v35}, Lkotlin/jvm/internal/Intrinsics;->checkNotNull(Ljava/lang/Object;)V

    invoke-static {v3}, Lkotlin/jvm/internal/Intrinsics;->checkNotNull(Ljava/lang/Object;)V

    iput-object v15, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$0:Ljava/lang/Object;

    iput-object v9, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$1:Ljava/lang/Object;

    iput-object v2, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$2:Ljava/lang/Object;

    move-object/from16 v1, v33

    iput-object v1, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$3:Ljava/lang/Object;

    iput-object v13, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$4:Ljava/lang/Object;

    move-object/from16 v11, v25

    iput-object v11, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$5:Ljava/lang/Object;
    :try_end_3d
    .catchall {:try_start_3d .. :try_end_3d} :catchall_4c

    move-object/from16 v4, v34

    :try_start_3e
    iput-object v4, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$6:Ljava/lang/Object;
    :try_end_3e
    .catchall {:try_start_3e .. :try_end_3e} :catchall_4d

    move-object/from16 v33, v1

    move-object/from16 v1, v32

    :try_start_3f
    iput-object v1, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$7:Ljava/lang/Object;
    :try_end_3f
    .catchall {:try_start_3f .. :try_end_3f} :catchall_4b

    move-object/from16 v32, v1

    :try_start_40
    invoke-static/range {v19 .. v19}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v1

    iput-object v1, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$8:Ljava/lang/Object;

    iput-object v0, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$9:Ljava/lang/Object;

    move-object/from16 v1, v31

    iput-object v1, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$10:Ljava/lang/Object;

    move-object/from16 v25, v12

    move-object/from16 v12, v30

    iput-object v12, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$11:Ljava/lang/Object;

    move-object/from16 v31, v1

    invoke-static/range {v28 .. v28}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v1

    iput-object v1, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$12:Ljava/lang/Object;

    move-object/from16 v1, p2

    iput-object v1, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$13:Ljava/lang/Object;

    move-object/from16 v30, v12

    move-object/from16 v12, v29

    iput-object v12, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$14:Ljava/lang/Object;

    move-object/from16 p2, v1

    move-object/from16 v1, v61

    iput-object v1, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$15:Ljava/lang/Object;

    move-object/from16 v29, v12

    move-object/from16 v12, v18

    iput-object v12, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$16:Ljava/lang/Object;

    move-object/from16 v18, v1

    invoke-static/range {v35 .. v35}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v1

    iput-object v1, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$17:Ljava/lang/Object;

    invoke-static/range {v37 .. v37}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v1

    iput-object v1, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$18:Ljava/lang/Object;

    iput-object v3, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$19:Ljava/lang/Object;

    const/4 v1, 0x0

    iput-object v1, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$20:Ljava/lang/Object;
    :try_end_40
    .catchall {:try_start_40 .. :try_end_40} :catchall_4d

    move/from16 v1, v21

    :try_start_41
    iput v1, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->I$0:I
    :try_end_41
    .catchall {:try_start_41 .. :try_end_41} :catchall_4a

    move/from16 v34, v1

    move-object/from16 v21, v2

    move-wide/from16 v1, v26

    :try_start_42
    iput-wide v1, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->J$0:J

    move-wide/from16 v26, v1

    move-wide/from16 v1, v23

    iput-wide v1, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->J$1:J

    move-object/from16 v23, v11

    move-object/from16 v24, v12

    move-wide/from16 v11, v57

    iput-wide v11, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->J$2:J

    move-wide/from16 v41, v11

    move-wide/from16 v11, v59

    iput-wide v11, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->J$3:J

    move-object/from16 v37, v15

    move/from16 v15, p1

    iput v15, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->I$1:I

    iput v5, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->I$2:I

    iput-wide v7, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->J$4:J

    iput v10, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->I$3:I

    move-wide/from16 v38, v1

    const/4 v1, 0x3

    iput v1, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->label:I
    :try_end_42
    .catchall {:try_start_42 .. :try_end_42} :catchall_49

    move-object/from16 v1, p0

    move/from16 p1, v5

    move-wide/from16 v45, v11

    move-wide/from16 v47, v26

    move-object/from16 v44, v31

    move-object/from16 v43, v33

    move-object/from16 v2, v35

    move-wide/from16 v62, v38

    move-object/from16 v64, v54

    const-wide/16 v51, 0x0

    move/from16 v26, v15

    move/from16 v15, v34

    move-object/from16 v138, v18

    move-object/from16 v18, p2

    move/from16 p2, v10

    move-object/from16 v10, v32

    move-wide/from16 v139, v7

    move-object v8, v4

    move-object v7, v6

    move-wide/from16 v5, v139

    move-object/from16 v4, v138

    :try_start_43
    invoke-direct/range {v1 .. v7}, Lcom/bachatas4/android/service/ImportService;->copyPkgToLocalCache(Landroid/net/Uri;Ljava/io/File;Ljava/lang/String;JLkotlin/coroutines/Continuation;)Ljava/lang/Object;

    move-result-object v11
    :try_end_43
    .catchall {:try_start_43 .. :try_end_43} :catchall_48

    move-object v1, v4

    move-object/from16 v12, v22

    if-ne v11, v12, :cond_24

    move-object v6, v12

    goto/16 :goto_48

    :cond_24
    move-object/from16 v35, v0

    move-object v4, v2

    move-object v11, v7

    move-object/from16 v31, v18

    move-object/from16 v39, v23

    move-object/from16 v32, v28

    move-wide/from16 v27, v47

    move/from16 v7, p1

    move/from16 v0, p2

    move-object v2, v1

    move-object v1, v3

    move-object/from16 v3, v24

    move-wide/from16 v23, v41

    move-object/from16 v41, v43

    move-object/from16 v43, v9

    move v9, v15

    move-object/from16 v42, v21

    :goto_23
    const/high16 v15, 0x10000000

    .line 781
    :try_start_44
    invoke-static {v1, v15}, Landroid/os/ParcelFileDescriptor;->open(Ljava/io/File;I)Landroid/os/ParcelFileDescriptor;

    move-result-object v1

    .line 780
    invoke-static {v1}, Lkotlin/jvm/internal/Intrinsics;->checkNotNull(Ljava/lang/Object;)V
    :try_end_44
    .catchall {:try_start_44 .. :try_end_44} :catchall_47

    move-object/from16 v61, v2

    move-object/from16 v18, v3

    move-object/from16 v34, v8

    move/from16 v21, v9

    move-wide/from16 v57, v23

    move/from16 v9, v26

    move-wide/from16 v26, v27

    move-object/from16 v28, v32

    move-object/from16 v15, v37

    move-object/from16 v33, v41

    move-object/from16 v2, v42

    move-wide/from16 v59, v45

    move-object v3, v1

    move-object v1, v4

    move-object/from16 v32, v10

    move-object/from16 v4, v44

    move-object/from16 v138, v11

    move v11, v0

    move-object/from16 v0, v35

    move-wide/from16 v139, v5

    move v5, v7

    move-wide/from16 v7, v139

    move-object/from16 v6, v138

    :goto_24
    move-object/from16 v10, v29

    .line 784
    :try_start_45
    new-instance v22, Lkotlin/jvm/internal/Ref$ObjectRef;

    invoke-direct/range {v22 .. v22}, Lkotlin/jvm/internal/Ref$ObjectRef;-><init>()V

    move-object/from16 p1, v1

    .line 785
    invoke-static {}, Lkotlin/collections/CollectionsKt;->createListBuilder()Ljava/util/List;

    move-result-object v1

    move-object/from16 p2, v2

    const/4 v2, 0x0

    .line 786
    invoke-interface {v1, v2}, Ljava/util/List;->add(Ljava/lang/Object;)Z

    .line 787
    invoke-virtual/range {p0 .. p0}, Lcom/bachatas4/android/service/ImportService;->getPkgKeyStore()Lcom/bachatas4/android/data/PkgKeyStore;

    move-result-object v2

    move-object/from16 v23, v3

    invoke-virtual {v10}, Lcom/bachatas4/android/runtime/pkg/PkgProbeResult;->getContentId()Ljava/lang/String;

    move-result-object v3

    invoke-virtual {v2, v3}, Lcom/bachatas4/android/data/PkgKeyStore;->getPasscode(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v2
    :try_end_45
    .catchall {:try_start_45 .. :try_end_45} :catchall_46

    if-eqz v2, :cond_25

    :try_start_46
    invoke-interface {v1, v2}, Ljava/util/List;->add(Ljava/lang/Object;)Z

    move-result v2

    invoke-static {v2}, Lkotlin/coroutines/jvm/internal/Boxing;->boxBoolean(Z)Ljava/lang/Boolean;
    :try_end_46
    .catchall {:try_start_46 .. :try_end_46} :catchall_24

    goto :goto_25

    :catchall_24
    move-exception v0

    move-object/from16 v1, p0

    move-object v12, v14

    move/from16 v14, v21

    move-object/from16 v5, v32

    move-object/from16 v8, v34

    move-object/from16 v9, v43

    move-object/from16 v11, v53

    move-object/from16 v3, v64

    goto/16 :goto_58

    :cond_25
    :goto_25
    move-object/from16 v2, v17

    .line 788
    :try_start_47
    invoke-interface {v1, v2}, Ljava/util/List;->add(Ljava/lang/Object;)Z

    .line 785
    invoke-static {v1}, Lkotlin/collections/CollectionsKt;->build(Ljava/util/List;)Ljava/util/List;

    move-result-object v1

    check-cast v1, Ljava/lang/Iterable;

    .line 789
    invoke-static {v1}, Lkotlin/collections/CollectionsKt;->distinct(Ljava/lang/Iterable;)Ljava/util/List;

    move-result-object v1

    .line 791
    move-object/from16 v3, v23

    check-cast v3, Ljava/io/Closeable;
    :try_end_47
    .catchall {:try_start_47 .. :try_end_47} :catchall_46

    :try_start_48
    move-object/from16 v17, v3

    check-cast v17, Landroid/os/ParcelFileDescriptor;

    .line 792
    invoke-virtual/range {v17 .. v17}, Landroid/os/ParcelFileDescriptor;->getFd()I

    move-result v24

    .line 793
    sget-object v29, Lcom/bachatas4/android/runtime/pkg/PkgStatus;->ERROR:Lcom/bachatas4/android/runtime/pkg/PkgStatus;

    .line 794
    invoke-interface {v1}, Ljava/util/List;->iterator()Ljava/util/Iterator;

    move-result-object v35
    :try_end_48
    .catchall {:try_start_48 .. :try_end_48} :catchall_43

    move/from16 v66, v5

    move-object/from16 v68, v6

    move-wide v5, v7

    move/from16 v67, v9

    move/from16 v65, v21

    move-object/from16 v9, v43

    move-object v8, v0

    move-object v7, v4

    move-object v0, v13

    move-object/from16 v21, v17

    move-object/from16 v17, p1

    move-object/from16 v13, p2

    move-object v4, v3

    move v3, v11

    move-object/from16 v11, v31

    move-object/from16 v31, v29

    move-object/from16 v29, v18

    move-object/from16 v18, v1

    move-object/from16 v1, v33

    move-object/from16 v33, v2

    move/from16 v2, v24

    const/16 v24, 0x0

    :goto_26
    :try_start_49
    invoke-interface/range {v35 .. v35}, Ljava/util/Iterator;->hasNext()Z

    move-result v37
    :try_end_49
    .catchall {:try_start_49 .. :try_end_49} :catchall_42

    if-eqz v37, :cond_2b

    :try_start_4a
    invoke-interface/range {v35 .. v35}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v37

    check-cast v37, Ljava/lang/String;

    .line 795
    invoke-static {}, Lkotlinx/coroutines/Dispatchers;->getIO()Lkotlinx/coroutines/CoroutineDispatcher;

    move-result-object v38

    move-wide/from16 p1, v5

    move-object/from16 v6, v38

    check-cast v6, Lkotlin/coroutines/CoroutineContext;

    move-object v5, v0

    new-instance v0, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$5$result$1;
    :try_end_4a
    .catchall {:try_start_4a .. :try_end_4a} :catchall_2a

    move-object/from16 v38, v6

    const/4 v6, 0x0

    move-wide/from16 v70, p1

    move/from16 v69, v3

    move-object/from16 v82, v4

    move-object/from16 v49, v14

    move-object/from16 v72, v22

    move-wide/from16 v73, v26

    move-object/from16 v3, v29

    move-object/from16 v29, v30

    move-object/from16 v84, v33

    move-object/from16 v81, v35

    move-object/from16 v4, v37

    move-object/from16 v83, v38

    move-wide/from16 v75, v57

    move-wide/from16 v77, v59

    move-wide/from16 v79, v62

    move-object v14, v5

    move-object/from16 v30, v7

    move-object/from16 v26, v10

    move-object/from16 v27, v11

    move-object/from16 v22, v12

    move-object/from16 v11, v32

    move-object/from16 v10, v34

    move-object/from16 v7, v39

    move-object/from16 v5, v61

    move-object v12, v1

    move-object/from16 v1, p0

    :try_start_4b
    invoke-direct/range {v0 .. v6}, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$5$result$1;-><init>(Lcom/bachatas4/android/service/ImportService;ILjava/io/File;Ljava/lang/String;Ljava/lang/String;Lkotlin/coroutines/Continuation;)V

    check-cast v0, Lkotlin/jvm/functions/Function2;

    move-object/from16 v6, v68

    iput-object v15, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$0:Ljava/lang/Object;

    iput-object v9, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$1:Ljava/lang/Object;

    iput-object v13, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$2:Ljava/lang/Object;

    iput-object v12, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$3:Ljava/lang/Object;

    iput-object v14, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$4:Ljava/lang/Object;

    iput-object v7, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$5:Ljava/lang/Object;

    iput-object v10, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$6:Ljava/lang/Object;

    iput-object v11, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$7:Ljava/lang/Object;

    invoke-static/range {v19 .. v19}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v1

    iput-object v1, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$8:Ljava/lang/Object;

    iput-object v8, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$9:Ljava/lang/Object;

    move-object/from16 v1, v30

    iput-object v1, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$10:Ljava/lang/Object;

    move-object/from16 v30, v1

    move-object/from16 v1, v29

    iput-object v1, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$11:Ljava/lang/Object;

    move-object/from16 v29, v1

    invoke-static/range {v28 .. v28}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v1

    iput-object v1, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$12:Ljava/lang/Object;

    move-object/from16 v1, v27

    iput-object v1, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$13:Ljava/lang/Object;

    move-object/from16 v27, v1

    move-object/from16 v1, v26

    iput-object v1, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$14:Ljava/lang/Object;

    iput-object v5, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$15:Ljava/lang/Object;

    iput-object v3, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$16:Ljava/lang/Object;

    move-object/from16 v26, v1

    invoke-static/range {v17 .. v17}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v1

    iput-object v1, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$17:Ljava/lang/Object;

    invoke-static/range {v23 .. v23}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v1

    iput-object v1, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$18:Ljava/lang/Object;

    move-object/from16 v1, v72

    iput-object v1, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$19:Ljava/lang/Object;

    move-object/from16 v72, v1

    invoke-static/range {v18 .. v18}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v1

    iput-object v1, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$20:Ljava/lang/Object;
    :try_end_4b
    .catchall {:try_start_4b .. :try_end_4b} :catchall_29

    move-object/from16 v1, v82

    :try_start_4c
    iput-object v1, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$21:Ljava/lang/Object;
    :try_end_4c
    .catchall {:try_start_4c .. :try_end_4c} :catchall_28

    move-object/from16 v82, v1

    :try_start_4d
    invoke-static/range {v21 .. v21}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v1

    iput-object v1, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$22:Ljava/lang/Object;

    invoke-static/range {v31 .. v31}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v1

    iput-object v1, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$23:Ljava/lang/Object;

    move-object/from16 v1, v81

    iput-object v1, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$24:Ljava/lang/Object;

    iput-object v4, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$25:Ljava/lang/Object;
    :try_end_4d
    .catchall {:try_start_4d .. :try_end_4d} :catchall_29

    move-object/from16 v81, v1

    move/from16 v1, v65

    :try_start_4e
    iput v1, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->I$0:I

    move-object/from16 v33, v3

    move-object/from16 v32, v4

    move-wide/from16 v3, v73

    iput-wide v3, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->J$0:J

    move-wide/from16 v73, v3

    move-wide/from16 v3, v79

    iput-wide v3, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->J$1:J

    move-wide/from16 v79, v3

    move-wide/from16 v3, v75

    iput-wide v3, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->J$2:J

    move-wide/from16 v75, v3

    move-wide/from16 v3, v77

    iput-wide v3, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->J$3:J
    :try_end_4e
    .catchall {:try_start_4e .. :try_end_4e} :catchall_27

    move/from16 v34, v1

    move/from16 v1, v67

    :try_start_4f
    iput v1, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->I$1:I

    move/from16 v35, v1

    move/from16 v1, v66

    iput v1, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->I$2:I

    move-wide/from16 v77, v3

    move-wide/from16 v3, v70

    iput-wide v3, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->J$4:J

    move/from16 v37, v1

    move/from16 v1, v69

    iput v1, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->I$3:I

    iput v2, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->I$4:I

    move/from16 v69, v1

    const/4 v1, 0x4

    iput v1, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->label:I

    move-object/from16 v1, v83

    invoke-static {v1, v0, v6}, Lkotlinx/coroutines/BuildersKt;->withContext(Lkotlin/coroutines/CoroutineContext;Lkotlin/jvm/functions/Function2;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;

    move-result-object v0
    :try_end_4f
    .catchall {:try_start_4f .. :try_end_4f} :catchall_26

    move-object/from16 v1, v22

    if-ne v0, v1, :cond_26

    move-object v6, v1

    goto/16 :goto_48

    :cond_26
    move-object/from16 v61, v5

    move-object/from16 v68, v6

    move-object/from16 v39, v7

    move-object/from16 v43, v19

    move-object/from16 v40, v29

    move-object/from16 v29, v33

    move/from16 v65, v34

    move/from16 v67, v35

    move/from16 v66, v37

    move/from16 v19, v69

    move-wide/from16 v57, v75

    move-wide/from16 v59, v77

    move-wide/from16 v62, v79

    move-object/from16 v35, v81

    move-object v5, v0

    move-wide v6, v3

    move-object/from16 v34, v10

    move-object v0, v14

    move-object/from16 v10, v26

    move-object/from16 v14, v72

    move-object/from16 v4, v82

    move v3, v2

    move-object/from16 v2, v32

    move-object/from16 v32, v11

    move-object/from16 v11, v27

    move-wide/from16 v26, v73

    .line 675
    :goto_27
    :try_start_50
    check-cast v5, Lcom/bachatas4/android/runtime/pkg/PkgExtractResult;

    .line 798
    invoke-virtual {v5}, Lcom/bachatas4/android/runtime/pkg/PkgExtractResult;->getStatus()Lcom/bachatas4/android/runtime/pkg/PkgStatus;

    move-result-object v31

    move-object/from16 v22, v1

    .line 799
    invoke-virtual {v5}, Lcom/bachatas4/android/runtime/pkg/PkgExtractResult;->getStatus()Lcom/bachatas4/android/runtime/pkg/PkgStatus;

    move-result-object v1

    move/from16 p1, v3

    sget-object v3, Lcom/bachatas4/android/runtime/pkg/PkgStatus;->OK:Lcom/bachatas4/android/runtime/pkg/PkgStatus;

    if-ne v1, v3, :cond_27

    .line 800
    iput-object v2, v14, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    move-object v2, v13

    move-object v13, v4

    move-object v4, v2

    move-wide v5, v6

    move-object v2, v8

    move-object v3, v9

    move-object/from16 v85, v14

    move/from16 v14, v19

    move-wide/from16 v86, v26

    move-object/from16 v89, v32

    move-object/from16 v90, v34

    move-object/from16 v91, v39

    move-object/from16 v88, v40

    move-object/from16 v19, v43

    move-wide/from16 v92, v57

    move-wide/from16 v94, v59

    move-object/from16 v9, v61

    move-wide/from16 v96, v62

    move/from16 v98, v65

    move/from16 v99, v66

    move/from16 v100, v67

    move-object/from16 v101, v68

    move/from16 v8, p1

    move-object/from16 v26, v10

    move-object/from16 v27, v11

    move-object/from16 v10, v29

    :goto_28
    move-object v7, v15

    move-object/from16 v15, v30

    move-object/from16 v11, v31

    goto/16 :goto_2b

    .line 803
    :cond_27
    invoke-virtual {v5}, Lcom/bachatas4/android/runtime/pkg/PkgExtractResult;->getStatus()Lcom/bachatas4/android/runtime/pkg/PkgStatus;

    move-result-object v1

    sget-object v2, Lcom/bachatas4/android/runtime/pkg/PkgStatus;->CANCELLED:Lcom/bachatas4/android/runtime/pkg/PkgStatus;

    if-eq v1, v2, :cond_2a

    .line 804
    invoke-virtual {v5}, Lcom/bachatas4/android/runtime/pkg/PkgExtractResult;->getStatus()Lcom/bachatas4/android/runtime/pkg/PkgStatus;

    move-result-object v1

    sget-object v2, Lcom/bachatas4/android/runtime/pkg/PkgStatus;->NEED_PASSCODE:Lcom/bachatas4/android/runtime/pkg/PkgStatus;

    if-eq v1, v2, :cond_29

    .line 805
    invoke-virtual {v5}, Lcom/bachatas4/android/runtime/pkg/PkgExtractResult;->getMessage()Ljava/lang/String;

    move-result-object v0

    if-nez v0, :cond_28

    const-string v0, "PKG extract failed"

    :cond_28
    new-instance v1, Ljava/lang/IllegalStateException;

    invoke-virtual {v0}, Ljava/lang/Object;->toString()Ljava/lang/String;

    move-result-object v0

    invoke-direct {v1, v0}, Ljava/lang/IllegalStateException;-><init>(Ljava/lang/String;)V

    throw v1

    :cond_29
    move/from16 v2, p1

    move-wide v5, v6

    move-object v1, v12

    move/from16 v3, v19

    move-object/from16 v12, v22

    move-object/from16 v7, v30

    move-object/from16 v30, v40

    move-object/from16 v19, v43

    move-object/from16 v33, v84

    move-object/from16 v22, v14

    move-object/from16 v14, v49

    goto/16 :goto_26

    .line 803
    :cond_2a
    new-instance v0, Ljava/util/concurrent/CancellationException;

    move-object/from16 v1, v20

    invoke-direct {v0, v1}, Ljava/util/concurrent/CancellationException;-><init>(Ljava/lang/String;)V

    throw v0
    :try_end_50
    .catchall {:try_start_50 .. :try_end_50} :catchall_25

    :catchall_25
    move-exception v0

    move-object v1, v0

    move-object v2, v4

    move-object v10, v9

    move-object/from16 v5, v32

    move-object/from16 v8, v34

    move-object/from16 v106, v49

    move/from16 v14, v65

    goto/16 :goto_3f

    :catchall_26
    move-exception v0

    goto :goto_2a

    :catchall_27
    move-exception v0

    move/from16 v34, v1

    goto :goto_2a

    :catchall_28
    move-exception v0

    move-object/from16 v82, v1

    goto :goto_29

    :catchall_29
    move-exception v0

    goto :goto_29

    :catchall_2a
    move-exception v0

    move-object/from16 v82, v4

    move-object/from16 v49, v14

    move-object/from16 v11, v32

    move-object/from16 v10, v34

    :goto_29
    move/from16 v34, v65

    :goto_2a
    move-object v1, v0

    move-object v8, v10

    move-object v5, v11

    move/from16 v14, v34

    move-object/from16 v106, v49

    goto/16 :goto_3e

    :cond_2b
    move/from16 v69, v3

    move-object/from16 v82, v4

    move-wide v3, v5

    move-object/from16 v49, v14

    move-object/from16 v72, v22

    move-wide/from16 v73, v26

    move-object/from16 v84, v33

    move-wide/from16 v75, v57

    move-wide/from16 v77, v59

    move-object/from16 v5, v61

    move-wide/from16 v79, v62

    move/from16 v37, v66

    move/from16 v35, v67

    move-object/from16 v6, v68

    move-object v14, v0

    move-object/from16 v26, v10

    move-object/from16 v27, v11

    move-object/from16 v22, v12

    move-object/from16 v33, v29

    move-object/from16 v29, v30

    move-object/from16 v11, v32

    move-object/from16 v10, v34

    move/from16 v34, v65

    move-object v12, v1

    move-object/from16 v30, v7

    move-object/from16 v7, v39

    move-object v0, v8

    move v8, v2

    move-object v2, v0

    move-object/from16 v101, v6

    move-object/from16 v91, v7

    move-object/from16 v90, v10

    move-object/from16 v89, v11

    move-object v0, v14

    move-object/from16 v88, v29

    move-object/from16 v10, v33

    move/from16 v98, v34

    move/from16 v100, v35

    move/from16 v99, v37

    move/from16 v14, v69

    move-object/from16 v85, v72

    move-wide/from16 v86, v73

    move-wide/from16 v92, v75

    move-wide/from16 v94, v77

    move-wide/from16 v96, v79

    move-object/from16 v138, v9

    move-object v9, v5

    move-wide v5, v3

    move-object/from16 v3, v138

    move-object v4, v13

    move-object/from16 v13, v82

    goto/16 :goto_28

    .line 808
    :goto_2b
    :try_start_51
    sget-object v1, Lcom/bachatas4/android/runtime/pkg/PkgStatus;->OK:Lcom/bachatas4/android/runtime/pkg/PkgStatus;

    if-eq v11, v1, :cond_32

    .line 809
    invoke-virtual/range {v26 .. v26}, Lcom/bachatas4/android/runtime/pkg/PkgProbeResult;->getContentId()Ljava/lang/String;

    move-result-object v1

    move-object/from16 p1, v2

    new-instance v2, Ljava/lang/StringBuilder;

    invoke-direct {v2}, Ljava/lang/StringBuilder;-><init>()V
    :try_end_51
    .catchall {:try_start_51 .. :try_end_51} :catchall_41

    move-object/from16 p2, v3

    :try_start_52
    const-string v3, "pkg batch need user passcode contentId="

    invoke-virtual {v2, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v2

    invoke-virtual {v2, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v1
    :try_end_52
    .catchall {:try_start_52 .. :try_end_52} :catchall_3a

    move-object/from16 v2, v49

    :try_start_53
    invoke-static {v2, v1}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    .line 810
    sget-object v1, Lcom/bachatas4/android/data/ImportManager;->INSTANCE:Lcom/bachatas4/android/data/ImportManager;

    new-instance v3, Lcom/bachatas4/android/data/ImportProgress$NeedPasscode;
    :try_end_53
    .catchall {:try_start_53 .. :try_end_53} :catchall_39

    move-object/from16 v49, v2

    :try_start_54
    invoke-virtual/range {v26 .. v26}, Lcom/bachatas4/android/runtime/pkg/PkgProbeResult;->getContentId()Ljava/lang/String;

    move-result-object v2

    move-object/from16 v29, v4

    invoke-virtual/range {v26 .. v26}, Lcom/bachatas4/android/runtime/pkg/PkgProbeResult;->getTitleHint()Ljava/lang/String;

    move-result-object v4

    invoke-direct {v3, v2, v4}, Lcom/bachatas4/android/data/ImportProgress$NeedPasscode;-><init>(Ljava/lang/String;Ljava/lang/String;)V

    check-cast v3, Lcom/bachatas4/android/data/ImportProgress;

    invoke-virtual {v1, v3}, Lcom/bachatas4/android/data/ImportManager;->update(Lcom/bachatas4/android/data/ImportProgress;)V

    .line 811
    const-string v2, "Passcode required"
    :try_end_54
    .catchall {:try_start_54 .. :try_end_54} :catchall_3a

    move-wide v3, v5

    const/4 v6, 0x6

    move-object v1, v7

    const/4 v7, 0x0

    move-wide v4, v3

    const/4 v3, 0x0

    move-wide/from16 v30, v4

    const/4 v4, 0x0

    const/4 v5, 0x1

    move-object/from16 v32, v29

    move-object/from16 v29, v9

    move-object/from16 v9, v32

    move-object/from16 v32, v26

    move-object/from16 v26, v13

    move-object/from16 v13, v32

    move-object/from16 v32, v11

    move-object/from16 v105, v20

    move-object/from16 v104, v22

    move-wide/from16 v102, v30

    move-object/from16 v106, v49

    move-object/from16 v11, p1

    move/from16 v20, v8

    move/from16 v22, v14

    move-object/from16 v14, v27

    move-object v8, v1

    move-object/from16 v27, v10

    move-object/from16 v1, p0

    move-object/from16 v10, p2

    :try_start_55
    invoke-static/range {v1 .. v7}, Lcom/bachatas4/android/service/ImportService;->updateNotification$default(Lcom/bachatas4/android/service/ImportService;Ljava/lang/String;IIZILjava/lang/Object;)V

    const/4 v2, 0x0

    const/4 v4, 0x1

    .line 812
    invoke-static {v2, v4, v2}, Lkotlinx/coroutines/CompletableDeferredKt;->CompletableDeferred$default(Lkotlinx/coroutines/Job;ILjava/lang/Object;)Lkotlinx/coroutines/CompletableDeferred;

    move-result-object v3

    .line 813
    iput-object v3, v1, Lcom/bachatas4/android/service/ImportService;->passcodeWaiter:Lkotlinx/coroutines/CompletableDeferred;

    move-object/from16 v6, v101

    .line 814
    iput-object v8, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$0:Ljava/lang/Object;

    iput-object v10, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$1:Ljava/lang/Object;

    iput-object v9, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$2:Ljava/lang/Object;

    iput-object v12, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$3:Ljava/lang/Object;

    iput-object v0, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$4:Ljava/lang/Object;

    move-object/from16 v7, v91

    iput-object v7, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$5:Ljava/lang/Object;
    :try_end_55
    .catchall {:try_start_55 .. :try_end_55} :catchall_38

    move-object/from16 v2, v90

    :try_start_56
    iput-object v2, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$6:Ljava/lang/Object;
    :try_end_56
    .catchall {:try_start_56 .. :try_end_56} :catchall_37

    move-object/from16 v4, v89

    :try_start_57
    iput-object v4, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$7:Ljava/lang/Object;

    invoke-static/range {v19 .. v19}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v5

    iput-object v5, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$8:Ljava/lang/Object;

    iput-object v11, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$9:Ljava/lang/Object;

    iput-object v15, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$10:Ljava/lang/Object;

    move-object/from16 v5, v88

    iput-object v5, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$11:Ljava/lang/Object;
    :try_end_57
    .catchall {:try_start_57 .. :try_end_57} :catchall_36

    move-object/from16 v30, v2

    :try_start_58
    invoke-static/range {v28 .. v28}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v2

    iput-object v2, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$12:Ljava/lang/Object;

    iput-object v14, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$13:Ljava/lang/Object;

    iput-object v13, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$14:Ljava/lang/Object;

    move-object/from16 v2, v29

    iput-object v2, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$15:Ljava/lang/Object;

    move-object/from16 v29, v2

    move-object/from16 v2, v27

    iput-object v2, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$16:Ljava/lang/Object;

    move-object/from16 v27, v2

    invoke-static/range {v17 .. v17}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v2

    iput-object v2, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$17:Ljava/lang/Object;

    invoke-static/range {v23 .. v23}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v2

    iput-object v2, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$18:Ljava/lang/Object;

    move-object/from16 v2, v85

    iput-object v2, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$19:Ljava/lang/Object;

    move-object/from16 v31, v2

    invoke-static/range {v18 .. v18}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v2

    iput-object v2, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$20:Ljava/lang/Object;
    :try_end_58
    .catchall {:try_start_58 .. :try_end_58} :catchall_35

    move-object/from16 v2, v26

    :try_start_59
    iput-object v2, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$21:Ljava/lang/Object;
    :try_end_59
    .catchall {:try_start_59 .. :try_end_59} :catchall_34

    move-object/from16 v26, v2

    :try_start_5a
    invoke-static/range {v21 .. v21}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v2

    iput-object v2, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$22:Ljava/lang/Object;

    invoke-static/range {v32 .. v32}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v2

    iput-object v2, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$23:Ljava/lang/Object;

    invoke-static {v3}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v2

    iput-object v2, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$24:Ljava/lang/Object;

    const/4 v2, 0x0

    iput-object v2, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$25:Ljava/lang/Object;
    :try_end_5a
    .catchall {:try_start_5a .. :try_end_5a} :catchall_35

    move/from16 v2, v98

    :try_start_5b
    iput v2, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->I$0:I
    :try_end_5b
    .catchall {:try_start_5b .. :try_end_5b} :catchall_33

    move-object/from16 v33, v4

    move-object/from16 v34, v5

    move-wide/from16 v4, v86

    :try_start_5c
    iput-wide v4, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->J$0:J

    move-wide/from16 v37, v4

    move-wide/from16 v4, v96

    iput-wide v4, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->J$1:J

    move-wide/from16 v39, v4

    move-wide/from16 v4, v92

    iput-wide v4, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->J$2:J

    move-wide/from16 v41, v4

    move-wide/from16 v4, v94

    iput-wide v4, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->J$3:J
    :try_end_5c
    .catchall {:try_start_5c .. :try_end_5c} :catchall_32

    move/from16 v35, v2

    move/from16 v2, v100

    :try_start_5d
    iput v2, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->I$1:I

    move/from16 v43, v2

    move/from16 v2, v99

    iput v2, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->I$2:I

    move-wide/from16 v44, v4

    move-wide/from16 v4, v102

    iput-wide v4, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->J$4:J

    move/from16 v46, v2

    move/from16 v2, v22

    iput v2, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->I$3:I

    move/from16 v22, v2

    move/from16 v2, v20

    iput v2, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->I$4:I

    move/from16 v20, v2

    const/4 v2, 0x5

    iput v2, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->label:I

    invoke-interface {v3, v6}, Lkotlinx/coroutines/CompletableDeferred;->await(Lkotlin/coroutines/Continuation;)Ljava/lang/Object;

    move-result-object v2
    :try_end_5d
    .catchall {:try_start_5d .. :try_end_5d} :catchall_31

    move-object/from16 v47, v6

    move-object/from16 v6, v104

    if-ne v2, v6, :cond_2c

    goto/16 :goto_48

    :cond_2c
    move-wide/from16 v115, v4

    move-object/from16 v5, v29

    move/from16 v117, v35

    move-wide/from16 v107, v37

    move-wide/from16 v109, v39

    move-wide/from16 v111, v41

    move/from16 v4, v43

    move-wide/from16 v113, v44

    move-object/from16 v118, v47

    move-object/from16 v42, v11

    move-object/from16 v37, v13

    move-object/from16 v38, v14

    move-object/from16 v41, v15

    move-object/from16 v43, v19

    move-object/from16 v14, v30

    move-object/from16 v15, v33

    move-object v11, v0

    move-object v0, v2

    move-object/from16 v19, v3

    move-object v13, v7

    move/from16 v2, v20

    move/from16 v7, v22

    move-object/from16 v33, v23

    move-object/from16 v3, v27

    .line 675
    :goto_2c
    :try_start_5e
    check-cast v0, Ljava/lang/String;

    move/from16 p1, v2

    const/4 v2, 0x0

    .line 815
    iput-object v2, v1, Lcom/bachatas4/android/service/ImportService;->passcodeWaiter:Lkotlinx/coroutines/CompletableDeferred;

    .line 816
    move-object v2, v0

    check-cast v2, Ljava/lang/CharSequence;

    if-eqz v2, :cond_31

    invoke-static {v2}, Lkotlin/text/StringsKt;->isBlank(Ljava/lang/CharSequence;)Z

    move-result v2

    if-nez v2, :cond_31

    .line 817
    invoke-static {}, Lkotlinx/coroutines/Dispatchers;->getIO()Lkotlinx/coroutines/CoroutineDispatcher;

    move-result-object v2

    check-cast v2, Lkotlin/coroutines/CoroutineContext;

    move/from16 v20, v4

    move-object v4, v0

    new-instance v0, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$5$result$2;
    :try_end_5e
    .catchall {:try_start_5e .. :try_end_5e} :catchall_30

    move-object/from16 v22, v6

    const/4 v6, 0x0

    move-object/from16 v120, v2

    move/from16 v127, v20

    move-object/from16 v119, v22

    move-object/from16 v126, v26

    move-object/from16 v125, v31

    move-object/from16 v122, v34

    move-object/from16 v124, v37

    move-object/from16 v123, v38

    move-object/from16 v121, v41

    move/from16 v128, v46

    move/from16 v2, p1

    move/from16 v20, v7

    move-object/from16 v7, v42

    :try_start_5f
    invoke-direct/range {v0 .. v6}, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$5$result$2;-><init>(Lcom/bachatas4/android/service/ImportService;ILjava/io/File;Ljava/lang/String;Ljava/lang/String;Lkotlin/coroutines/Continuation;)V

    check-cast v0, Lkotlin/jvm/functions/Function2;

    move-object/from16 v6, v118

    iput-object v8, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$0:Ljava/lang/Object;

    iput-object v10, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$1:Ljava/lang/Object;

    iput-object v9, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$2:Ljava/lang/Object;

    iput-object v12, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$3:Ljava/lang/Object;

    iput-object v11, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$4:Ljava/lang/Object;

    iput-object v13, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$5:Ljava/lang/Object;

    iput-object v14, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$6:Ljava/lang/Object;

    iput-object v15, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$7:Ljava/lang/Object;

    move-object/from16 v22, v8

    invoke-static/range {v43 .. v43}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v8

    iput-object v8, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$8:Ljava/lang/Object;

    iput-object v7, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$9:Ljava/lang/Object;

    move-object/from16 v8, v121

    iput-object v8, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$10:Ljava/lang/Object;

    move-object/from16 v23, v7

    move-object/from16 v7, v122

    iput-object v7, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$11:Ljava/lang/Object;

    move-object/from16 v122, v7

    invoke-static/range {v28 .. v28}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v7

    iput-object v7, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$12:Ljava/lang/Object;

    move-object/from16 v7, v123

    iput-object v7, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$13:Ljava/lang/Object;

    move-object/from16 v123, v7

    move-object/from16 v7, v124

    iput-object v7, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$14:Ljava/lang/Object;

    iput-object v5, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$15:Ljava/lang/Object;

    iput-object v3, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$16:Ljava/lang/Object;

    move-object/from16 v26, v3

    invoke-static/range {v17 .. v17}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v3

    iput-object v3, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$17:Ljava/lang/Object;

    invoke-static/range {v33 .. v33}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v3

    iput-object v3, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$18:Ljava/lang/Object;

    move-object/from16 v3, v125

    iput-object v3, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$19:Ljava/lang/Object;

    move-object/from16 v125, v3

    invoke-static/range {v18 .. v18}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v3

    iput-object v3, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$20:Ljava/lang/Object;
    :try_end_5f
    .catchall {:try_start_5f .. :try_end_5f} :catchall_2e

    move-object/from16 v3, v126

    :try_start_60
    iput-object v3, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$21:Ljava/lang/Object;
    :try_end_60
    .catchall {:try_start_60 .. :try_end_60} :catchall_2d

    move-object/from16 v126, v3

    :try_start_61
    invoke-static/range {v21 .. v21}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v3

    iput-object v3, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$22:Ljava/lang/Object;

    invoke-static/range {v32 .. v32}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v3

    iput-object v3, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$23:Ljava/lang/Object;

    invoke-static/range {v19 .. v19}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v3

    iput-object v3, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$24:Ljava/lang/Object;

    iput-object v4, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$25:Ljava/lang/Object;
    :try_end_61
    .catchall {:try_start_61 .. :try_end_61} :catchall_2e

    move/from16 v3, v117

    :try_start_62
    iput v3, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->I$0:I
    :try_end_62
    .catchall {:try_start_62 .. :try_end_62} :catchall_2c

    move/from16 v21, v3

    move-object/from16 v19, v4

    move-wide/from16 v3, v107

    :try_start_63
    iput-wide v3, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->J$0:J

    move-wide/from16 v29, v3

    move-wide/from16 v3, v109

    iput-wide v3, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->J$1:J

    move-wide/from16 v31, v3

    move-wide/from16 v3, v111

    iput-wide v3, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->J$2:J

    move-wide/from16 v34, v3

    move-wide/from16 v3, v113

    iput-wide v3, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->J$3:J

    move-wide/from16 v37, v3

    move/from16 v3, v127

    iput v3, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->I$1:I

    move/from16 v4, v128

    iput v4, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->I$2:I

    move/from16 v127, v3

    move/from16 v128, v4

    move-wide/from16 v3, v115

    iput-wide v3, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->J$4:J

    move-wide/from16 v39, v3

    move/from16 v3, v20

    iput v3, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->I$3:I

    iput v2, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->I$4:I

    const/4 v2, 0x6

    iput v2, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->label:I

    move-object/from16 v2, v120

    invoke-static {v2, v0, v6}, Lkotlinx/coroutines/BuildersKt;->withContext(Lkotlin/coroutines/CoroutineContext;Lkotlin/jvm/functions/Function2;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;

    move-result-object v2
    :try_end_63
    .catchall {:try_start_63 .. :try_end_63} :catchall_2f

    move-object/from16 v4, v119

    if-ne v2, v4, :cond_2d

    move-object v6, v4

    goto/16 :goto_48

    :cond_2d
    move v0, v3

    move-object/from16 v46, v9

    move-object/from16 v47, v10

    move-object/from16 v44, v11

    move-object/from16 v42, v14

    move-object/from16 v3, v19

    move-wide/from16 v9, v37

    move-wide/from16 v19, v39

    move-object/from16 v40, v43

    move-object v11, v2

    move-object v14, v6

    move-object/from16 v38, v8

    move-object/from16 v43, v13

    move-object/from16 v39, v23

    move-object/from16 v13, v24

    move-wide/from16 v23, v34

    move-object/from16 v2, v125

    move-object/from16 v34, v7

    move-wide/from16 v7, v31

    move-object/from16 v31, v17

    move-object/from16 v138, v33

    move-object/from16 v33, v5

    move-wide/from16 v5, v29

    move-object/from16 v30, v138

    .line 675
    :goto_2d
    :try_start_64
    check-cast v11, Lcom/bachatas4/android/runtime/pkg/PkgExtractResult;

    move-object/from16 v104, v4

    .line 820
    invoke-virtual {v11}, Lcom/bachatas4/android/runtime/pkg/PkgExtractResult;->getStatus()Lcom/bachatas4/android/runtime/pkg/PkgStatus;

    move-result-object v4

    move-wide/from16 p1, v5

    sget-object v5, Lcom/bachatas4/android/runtime/pkg/PkgStatus;->CANCELLED:Lcom/bachatas4/android/runtime/pkg/PkgStatus;

    if-eq v4, v5, :cond_30

    .line 821
    invoke-virtual {v11}, Lcom/bachatas4/android/runtime/pkg/PkgExtractResult;->getStatus()Lcom/bachatas4/android/runtime/pkg/PkgStatus;

    move-result-object v4

    sget-object v5, Lcom/bachatas4/android/runtime/pkg/PkgStatus;->OK:Lcom/bachatas4/android/runtime/pkg/PkgStatus;

    if-eq v4, v5, :cond_2f

    .line 822
    invoke-virtual {v11}, Lcom/bachatas4/android/runtime/pkg/PkgExtractResult;->getMessage()Ljava/lang/String;

    move-result-object v0

    if-nez v0, :cond_2e

    const-string v0, "Wrong passcode or extract failed"

    :cond_2e
    new-instance v2, Ljava/lang/IllegalStateException;

    invoke-virtual {v0}, Ljava/lang/Object;->toString()Ljava/lang/String;

    move-result-object v0

    invoke-direct {v2, v0}, Ljava/lang/IllegalStateException;-><init>(Ljava/lang/String;)V

    throw v2

    .line 824
    :cond_2f
    iput-object v3, v2, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    move/from16 v133, v0

    move-object v4, v2

    move-wide/from16 v131, v9

    move-object v1, v13

    move-object v6, v14

    move-object v11, v15

    move/from16 v45, v21

    move-object/from16 v14, v22

    move-wide/from16 v129, v23

    move-object/from16 v24, v30

    move-object/from16 v21, v31

    move-object/from16 v13, v34

    move-object/from16 v15, v38

    move-object/from16 v34, v39

    move-object/from16 v5, v42

    move-object/from16 v0, v44

    move-object/from16 v9, v46

    move-object/from16 v10, v47

    move-object/from16 v22, v104

    move-object/from16 v3, v122

    move-object/from16 v2, v123

    move/from16 v134, v127

    move/from16 v27, v128

    move-object/from16 v23, v18

    move-wide/from16 v31, v19

    move-object/from16 v39, v26

    move-object/from16 v19, v40

    move-object/from16 v20, v105

    move-wide/from16 v17, v7

    move-object/from16 v7, v43

    move-object/from16 v8, v126

    move-wide/from16 v43, p1

    :goto_2e
    move-object/from16 v35, v28

    goto/16 :goto_33

    .line 820
    :cond_30
    new-instance v0, Ljava/util/concurrent/CancellationException;

    move-object/from16 v2, v105

    invoke-direct {v0, v2}, Ljava/util/concurrent/CancellationException;-><init>(Ljava/lang/String;)V

    throw v0
    :try_end_64
    .catchall {:try_start_64 .. :try_end_64} :catchall_2b

    :catchall_2b
    move-exception v0

    move-object v1, v0

    move-object v5, v15

    move/from16 v14, v21

    move-object/from16 v8, v42

    move-object/from16 v10, v47

    goto :goto_31

    :catchall_2c
    move-exception v0

    move/from16 v21, v3

    goto :goto_30

    :catchall_2d
    move-exception v0

    move-object/from16 v126, v3

    goto :goto_2f

    :catchall_2e
    move-exception v0

    goto :goto_2f

    :cond_31
    move-object/from16 v126, v26

    move-object/from16 v2, v105

    move/from16 v21, v117

    .line 816
    :try_start_65
    new-instance v0, Ljava/util/concurrent/CancellationException;

    invoke-direct {v0, v2}, Ljava/util/concurrent/CancellationException;-><init>(Ljava/lang/String;)V

    throw v0
    :try_end_65
    .catchall {:try_start_65 .. :try_end_65} :catchall_2f

    :catchall_2f
    move-exception v0

    goto :goto_30

    :catchall_30
    move-exception v0

    move-object/from16 v126, v26

    :goto_2f
    move/from16 v21, v117

    :goto_30
    move-object v1, v0

    move-object v8, v14

    move-object v5, v15

    move/from16 v14, v21

    :goto_31
    move-object/from16 v2, v126

    goto/16 :goto_3f

    :catchall_31
    move-exception v0

    goto/16 :goto_3c

    :catchall_32
    move-exception v0

    move/from16 v35, v2

    goto/16 :goto_3c

    :catchall_33
    move-exception v0

    move/from16 v35, v2

    move-object/from16 v33, v4

    goto/16 :goto_3c

    :catchall_34
    move-exception v0

    move-object/from16 v26, v2

    move-object/from16 v33, v4

    move/from16 v35, v98

    move-object v1, v0

    goto/16 :goto_3d

    :catchall_35
    move-exception v0

    goto :goto_32

    :catchall_36
    move-exception v0

    move-object/from16 v30, v2

    :goto_32
    move-object/from16 v33, v4

    goto/16 :goto_3b

    :catchall_37
    move-exception v0

    move-object/from16 v30, v2

    move-object/from16 v33, v89

    goto/16 :goto_3b

    :catchall_38
    move-exception v0

    goto/16 :goto_3a

    :catchall_39
    move-exception v0

    move-object/from16 v10, p2

    move-object/from16 v106, v2

    move-object/from16 v26, v13

    goto/16 :goto_3a

    :catchall_3a
    move-exception v0

    move-object/from16 v10, p2

    goto/16 :goto_39

    :cond_32
    move-object/from16 v8, v26

    move-object/from16 v26, v13

    move-object v13, v8

    move-object v11, v2

    move-object v8, v7

    move-object/from16 v29, v9

    move-object/from16 v106, v49

    move-object/from16 v31, v85

    move-wide/from16 v37, v86

    move-object/from16 v34, v88

    move-object/from16 v33, v89

    move-object/from16 v30, v90

    move-object/from16 v7, v91

    move-wide/from16 v41, v92

    move-wide/from16 v44, v94

    move-wide/from16 v39, v96

    move/from16 v35, v98

    move/from16 v46, v99

    move/from16 v43, v100

    move-object/from16 v47, v101

    move-object v9, v4

    move-wide v4, v5

    move-object/from16 v6, v22

    move/from16 v22, v14

    move-object/from16 v14, v27

    move-object/from16 v27, v10

    move-object v10, v3

    move-wide v1, v4

    move-object/from16 v4, v31

    move-wide/from16 v31, v1

    move-object v2, v14

    move-object/from16 v21, v17

    move/from16 v133, v22

    move-object/from16 v1, v24

    move-object/from16 v5, v30

    move-object/from16 v3, v34

    move-wide/from16 v129, v41

    move/from16 v134, v43

    move-wide/from16 v131, v44

    move-object/from16 v22, v6

    move-object v14, v8

    move-object/from16 v34, v11

    move-object/from16 v24, v23

    move-object/from16 v8, v26

    move-object/from16 v11, v33

    move/from16 v45, v35

    move-wide/from16 v43, v37

    move-object/from16 v6, v47

    move-object/from16 v23, v18

    move-object/from16 v33, v29

    move-wide/from16 v17, v39

    move-object/from16 v39, v27

    move/from16 v27, v46

    goto/16 :goto_2e

    .line 826
    :goto_33
    :try_start_66
    sget-object v26, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;
    :try_end_66
    .catchall {:try_start_66 .. :try_end_66} :catchall_40

    .line 791
    :try_start_67
    invoke-static {v8, v1}, Lkotlin/io/CloseableKt;->closeFinally(Ljava/io/Closeable;Ljava/lang/Throwable;)V

    .line 828
    sget-object v1, Lcom/bachatas4/android/data/ImportManager;->INSTANCE:Lcom/bachatas4/android/data/ImportManager;

    .line 829
    new-instance v26, Lcom/bachatas4/android/data/ImportProgress$BatchExtracting;

    .line 831
    invoke-interface {v15}, Ljava/util/List;->size()I

    move-result v28

    const-wide/16 v29, 0x0

    .line 829
    invoke-direct/range {v26 .. v34}, Lcom/bachatas4/android/data/ImportProgress$BatchExtracting;-><init>(IIJJLjava/lang/String;Ljava/lang/String;)V

    move/from16 v135, v27

    move-wide/from16 v136, v31

    move-object/from16 v8, v34

    move-object/from16 v27, v4

    move-object/from16 v4, v26

    check-cast v4, Lcom/bachatas4/android/data/ImportProgress;

    .line 828
    invoke-virtual {v1, v4}, Lcom/bachatas4/android/data/ImportManager;->update(Lcom/bachatas4/android/data/ImportProgress;)V

    .line 839
    invoke-virtual/range {p0 .. p0}, Lcom/bachatas4/android/service/ImportService;->getContentImporter()Lcom/bachatas4/android/data/ContentImporter;

    move-result-object v37

    .line 841
    invoke-static/range {v39 .. v39}, Lkotlin/jvm/internal/Intrinsics;->checkNotNull(Ljava/lang/Object;)V

    .line 842
    invoke-virtual {v13}, Lcom/bachatas4/android/runtime/pkg/PkgProbeResult;->getContentId()Ljava/lang/String;

    move-result-object v40

    .line 839
    iput-object v14, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$0:Ljava/lang/Object;

    iput-object v10, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$1:Ljava/lang/Object;

    iput-object v9, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$2:Ljava/lang/Object;

    iput-object v12, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$3:Ljava/lang/Object;

    iput-object v0, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$4:Ljava/lang/Object;

    iput-object v7, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$5:Ljava/lang/Object;

    iput-object v5, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$6:Ljava/lang/Object;

    iput-object v11, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$7:Ljava/lang/Object;

    invoke-static/range {v19 .. v19}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v1

    iput-object v1, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$8:Ljava/lang/Object;

    iput-object v8, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$9:Ljava/lang/Object;

    iput-object v15, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$10:Ljava/lang/Object;

    iput-object v3, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$11:Ljava/lang/Object;

    invoke-static/range {v35 .. v35}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v1

    iput-object v1, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$12:Ljava/lang/Object;

    iput-object v2, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$13:Ljava/lang/Object;

    iput-object v13, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$14:Ljava/lang/Object;

    invoke-static/range {v33 .. v33}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v1

    iput-object v1, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$15:Ljava/lang/Object;

    move-object/from16 v1, v39

    iput-object v1, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$16:Ljava/lang/Object;

    invoke-static/range {v21 .. v21}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v4

    iput-object v4, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$17:Ljava/lang/Object;

    invoke-static/range {v24 .. v24}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v4

    iput-object v4, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$18:Ljava/lang/Object;

    move-object/from16 v4, v27

    iput-object v4, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$19:Ljava/lang/Object;

    move-object/from16 v39, v1

    invoke-static/range {v23 .. v23}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v1

    iput-object v1, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$20:Ljava/lang/Object;

    const/4 v1, 0x0

    iput-object v1, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$21:Ljava/lang/Object;

    iput-object v1, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$22:Ljava/lang/Object;

    iput-object v1, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$23:Ljava/lang/Object;

    iput-object v1, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$24:Ljava/lang/Object;

    iput-object v1, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$25:Ljava/lang/Object;
    :try_end_67
    .catchall {:try_start_67 .. :try_end_67} :catchall_3f

    move/from16 v1, v45

    :try_start_68
    iput v1, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->I$0:I
    :try_end_68
    .catchall {:try_start_68 .. :try_end_68} :catchall_3e

    move/from16 v21, v1

    move-object/from16 v41, v2

    move-wide/from16 v1, v43

    :try_start_69
    iput-wide v1, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->J$0:J

    move-wide/from16 v23, v1

    move-wide/from16 v1, v17

    iput-wide v1, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->J$1:J

    move-wide/from16 v17, v1

    move-wide/from16 v1, v129

    iput-wide v1, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->J$2:J

    move-wide/from16 v26, v1

    move-wide/from16 v1, v131

    iput-wide v1, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->J$3:J

    move-wide/from16 v28, v1

    move/from16 v1, v134

    iput v1, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->I$1:I

    move/from16 v2, v135

    iput v2, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->I$2:I

    move/from16 v30, v1

    move-wide/from16 v1, v136

    iput-wide v1, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->J$4:J

    move/from16 v1, v133

    iput v1, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->I$3:I

    const/4 v1, 0x7

    iput v1, v6, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->label:I

    move-object/from16 v42, v6

    move-object/from16 v38, v14

    invoke-virtual/range {v37 .. v42}, Lcom/bachatas4/android/data/ContentImporter;->overlayStaging(Ljava/lang/String;Ljava/io/File;Ljava/lang/String;Ljava/lang/String;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;

    move-result-object v1
    :try_end_69
    .catchall {:try_start_69 .. :try_end_69} :catchall_3d

    move-object/from16 v6, v22

    if-ne v1, v6, :cond_33

    goto/16 :goto_48

    :cond_33
    move-object/from16 v35, v9

    move-object v1, v13

    move/from16 v9, v21

    move-wide/from16 v21, v23

    move-wide/from16 v57, v26

    move-wide/from16 v59, v28

    move-object/from16 v2, v41

    move-object v13, v0

    move-object/from16 v26, v3

    move-object v0, v8

    move-object/from16 v27, v15

    move-wide/from16 v23, v17

    move-object/from16 v15, v38

    move-object/from16 v3, v39

    move-object v8, v7

    move-object v7, v5

    move/from16 v5, v30

    move-object/from16 v30, v11

    .line 845
    :goto_34
    :try_start_6a
    move-object v11, v8

    check-cast v11, Ljava/util/Collection;

    new-instance v14, Lcom/bachatas4/android/data/OverlayRecord;

    move-object/from16 p1, v1

    invoke-virtual/range {p1 .. p1}, Lcom/bachatas4/android/runtime/pkg/PkgProbeResult;->getContentId()Ljava/lang/String;

    move-result-object v1
    :try_end_6a
    .catchall {:try_start_6a .. :try_end_6a} :catchall_3c

    move-object/from16 p2, v7

    move-object/from16 v17, v8

    :try_start_6b
    invoke-static {}, Ljava/lang/System;->currentTimeMillis()J

    move-result-wide v7

    invoke-direct {v14, v1, v2, v7, v8}, Lcom/bachatas4/android/data/OverlayRecord;-><init>(Ljava/lang/String;Ljava/lang/String;J)V

    invoke-interface {v11, v14}, Ljava/util/Collection;->add(Ljava/lang/Object;)Z

    .line 847
    iget-object v1, v4, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v1, Ljava/lang/CharSequence;

    if-eqz v1, :cond_35

    invoke-static {v1}, Lkotlin/text/StringsKt;->isBlank(Ljava/lang/CharSequence;)Z

    move-result v1

    if-eqz v1, :cond_34

    goto :goto_35

    .line 848
    :cond_34
    iget-object v1, v4, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    move-object/from16 v2, v84

    invoke-static {v1, v2}, Lkotlin/jvm/internal/Intrinsics;->areEqual(Ljava/lang/Object;Ljava/lang/Object;)Z

    move-result v1

    if-nez v1, :cond_36

    .line 849
    invoke-virtual/range {p1 .. p1}, Lcom/bachatas4/android/runtime/pkg/PkgProbeResult;->getContentId()Ljava/lang/String;

    move-result-object v1

    check-cast v1, Ljava/lang/CharSequence;

    invoke-static {v1}, Lkotlin/text/StringsKt;->isBlank(Ljava/lang/CharSequence;)Z

    move-result v1

    if-nez v1, :cond_36

    .line 851
    invoke-virtual/range {p0 .. p0}, Lcom/bachatas4/android/service/ImportService;->getPkgKeyStore()Lcom/bachatas4/android/data/PkgKeyStore;

    move-result-object v1

    invoke-virtual/range {p1 .. p1}, Lcom/bachatas4/android/runtime/pkg/PkgProbeResult;->getContentId()Ljava/lang/String;

    move-result-object v7

    iget-object v4, v4, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v4, Ljava/lang/String;

    invoke-virtual {v1, v7, v4}, Lcom/bachatas4/android/data/PkgKeyStore;->putPasscode(Ljava/lang/String;Ljava/lang/String;)V

    goto :goto_36

    :cond_35
    :goto_35
    move-object/from16 v2, v84

    .line 854
    :cond_36
    :goto_36
    invoke-static {v3}, Lkotlin/jvm/internal/Intrinsics;->checkNotNull(Ljava/lang/Object;)V

    invoke-static {v3}, Lkotlin/io/FilesKt;->deleteRecursively(Ljava/io/File;)Z

    .line 855
    move-object/from16 v7, p2

    check-cast v7, Ljava/util/Collection;

    invoke-interface {v7, v3}, Ljava/util/Collection;->remove(Ljava/lang/Object;)Z
    :try_end_6b
    .catchall {:try_start_6b .. :try_end_6b} :catchall_3b

    add-int/lit8 v1, v9, 0x1

    move-object/from16 v11, p0

    move-object/from16 v7, p2

    move-object v9, v10

    move-object v3, v12

    move-object/from16 v8, v17

    move-object/from16 v18, v25

    move-object/from16 v12, v26

    move-object/from16 v4, v27

    move-object/from16 v25, v36

    move-object/from16 v54, v64

    move-object/from16 v14, v106

    move v10, v1

    move-object/from16 v17, v2

    move-wide/from16 v26, v21

    move-object/from16 v1, v30

    move-object/from16 v2, v35

    move-object/from16 v22, v6

    move-object/from16 v6, v42

    goto/16 :goto_20

    :catchall_3b
    move-exception v0

    goto :goto_37

    :catchall_3c
    move-exception v0

    move-object/from16 p2, v7

    :goto_37
    move-object/from16 v1, p0

    move-object/from16 v8, p2

    move v14, v9

    move-object v9, v10

    move-object/from16 v5, v30

    goto/16 :goto_41

    :catchall_3d
    move-exception v0

    goto :goto_38

    :catchall_3e
    move-exception v0

    move/from16 v21, v1

    goto :goto_38

    :catchall_3f
    move-exception v0

    move/from16 v21, v45

    :goto_38
    move-object/from16 v1, p0

    move-object v8, v5

    move-object v9, v10

    move-object v5, v11

    move/from16 v14, v21

    goto/16 :goto_41

    :catchall_40
    move-exception v0

    move/from16 v21, v45

    move-object v1, v0

    move-object v2, v8

    move/from16 v14, v21

    move-object v8, v5

    move-object v5, v11

    goto :goto_3f

    :catchall_41
    move-exception v0

    move-object v10, v3

    :goto_39
    move-object/from16 v26, v13

    move-object/from16 v106, v49

    :goto_3a
    move-object/from16 v33, v89

    move-object/from16 v30, v90

    :goto_3b
    move/from16 v35, v98

    :goto_3c
    move-object v1, v0

    move-object/from16 v2, v26

    :goto_3d
    move-object/from16 v8, v30

    move-object/from16 v5, v33

    move/from16 v14, v35

    goto :goto_3f

    :catchall_42
    move-exception v0

    move-object/from16 v82, v4

    move-object/from16 v106, v14

    move-object/from16 v11, v32

    move-object/from16 v10, v34

    move/from16 v34, v65

    move-object v1, v0

    move-object v8, v10

    move-object v5, v11

    move/from16 v14, v34

    :goto_3e
    move-object/from16 v2, v82

    move-object v10, v9

    goto :goto_3f

    :catchall_43
    move-exception v0

    move-object/from16 v106, v14

    move-object v1, v0

    move-object v2, v3

    move/from16 v14, v21

    move-object/from16 v5, v32

    move-object/from16 v8, v34

    move-object/from16 v10, v43

    .line 791
    :goto_3f
    :try_start_6c
    throw v1
    :try_end_6c
    .catchall {:try_start_6c .. :try_end_6c} :catchall_44

    :catchall_44
    move-exception v0

    :try_start_6d
    invoke-static {v2, v1}, Lkotlin/io/CloseableKt;->closeFinally(Ljava/io/Closeable;Ljava/lang/Throwable;)V

    throw v0
    :try_end_6d
    .catchall {:try_start_6d .. :try_end_6d} :catchall_45

    :catchall_45
    move-exception v0

    move-object/from16 v1, p0

    move-object v9, v10

    goto :goto_41

    :catchall_46
    move-exception v0

    move-object/from16 v106, v14

    move-object/from16 v1, p0

    move/from16 v14, v21

    move-object/from16 v5, v32

    move-object/from16 v8, v34

    goto :goto_40

    :catchall_47
    move-exception v0

    move-object/from16 v106, v14

    move-object/from16 v1, p0

    move v14, v9

    move-object v5, v10

    :goto_40
    move-object/from16 v9, v43

    :goto_41
    move-object/from16 v11, v53

    move-object/from16 v3, v64

    move-object/from16 v12, v106

    goto/16 :goto_58

    :catchall_48
    move-exception v0

    move-object/from16 v106, v14

    goto :goto_46

    :catchall_49
    move-exception v0

    move-object v8, v4

    move-object/from16 v106, v14

    move-object/from16 v10, v32

    move/from16 v15, v34

    goto :goto_45

    :catchall_4a
    move-exception v0

    move v15, v1

    move-object v8, v4

    move-object/from16 v106, v14

    goto :goto_43

    :catchall_4b
    move-exception v0

    move-object v10, v1

    move-object v8, v4

    goto :goto_44

    :catchall_4c
    move-exception v0

    move-object/from16 v106, v14

    move/from16 v15, v21

    move-object/from16 v10, v32

    move-object/from16 v8, v34

    goto :goto_45

    :catchall_4d
    move-exception v0

    move-object v8, v4

    goto :goto_42

    :catchall_4e
    move-exception v0

    move-object v8, v7

    :goto_42
    move-object/from16 v106, v14

    move/from16 v15, v21

    :goto_43
    move-object/from16 v10, v32

    goto :goto_45

    :catchall_4f
    move-exception v0

    move-object v10, v1

    move-object v8, v7

    :goto_44
    move-object/from16 v106, v14

    move/from16 v15, v21

    :goto_45
    move-object/from16 v64, v54

    :goto_46
    move-object/from16 v1, p0

    move-object v5, v10

    move v14, v15

    goto :goto_41

    :cond_37
    move-object/from16 v21, v2

    move-object/from16 v43, v3

    move-object/from16 v44, v4

    move-object/from16 v106, v14

    move-object/from16 v37, v15

    move-wide/from16 v62, v23

    move-wide/from16 v47, v26

    move-object/from16 v64, v54

    move-wide/from16 v41, v57

    move-wide/from16 v45, v59

    move-object/from16 v23, v8

    move v15, v10

    move-object v10, v1

    move-object v8, v7

    move-object v7, v6

    move-object/from16 v6, v22

    .line 860
    :try_start_6e
    sget-object v1, Lcom/bachatas4/android/data/InstallManifestIo;->INSTANCE:Lcom/bachatas4/android/data/InstallManifestIo;

    invoke-static {v13}, Lkotlin/jvm/internal/Intrinsics;->checkNotNull(Ljava/lang/Object;)V

    invoke-virtual {v1, v13}, Lcom/bachatas4/android/data/InstallManifestIo;->read(Ljava/io/File;)Lcom/bachatas4/android/data/InstallManifest;

    move-result-object v1
    :try_end_6e
    .catchall {:try_start_6e .. :try_end_6e} :catchall_55

    if-nez v1, :cond_38

    :try_start_6f
    new-instance v26, Lcom/bachatas4/android/data/InstallManifest;

    .line 861
    const-string v28, "INSTALLED"

    .line 864
    const-string v31, "pkg"

    .line 865
    const-string v32, ""

    .line 866
    invoke-static {}, Ljava/lang/System;->currentTimeMillis()J

    move-result-wide v33

    .line 867
    sget-object v1, Lcom/bachatas4/android/data/GameInstallVerifier;->INSTANCE:Lcom/bachatas4/android/data/GameInstallVerifier;

    invoke-virtual {v1}, Lcom/bachatas4/android/data/GameInstallVerifier;->getREQUIRED_FILES()Ljava/util/List;

    move-result-object v35

    const/16 v39, 0x201

    const/16 v40, 0x0

    const/16 v27, 0x0

    const/16 v30, 0x0

    move-object/from16 v29, v37

    const-wide/16 v36, 0x0

    const/16 v38, 0x0

    .line 860
    invoke-direct/range {v26 .. v40}, Lcom/bachatas4/android/data/InstallManifest;-><init>(ILjava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;JLjava/util/List;JLjava/util/List;ILkotlin/jvm/internal/DefaultConstructorMarker;)V
    :try_end_6f
    .catchall {:try_start_6f .. :try_end_6f} :catchall_50

    move-object/from16 v2, v29

    move-object/from16 v24, v26

    goto :goto_47

    :catchall_50
    move-exception v0

    goto :goto_46

    :cond_38
    move-object/from16 v2, v37

    move-object/from16 v24, v1

    .line 870
    :goto_47
    :try_start_70
    sget-object v1, Lcom/bachatas4/android/data/InstallManifestIo;->INSTANCE:Lcom/bachatas4/android/data/InstallManifestIo;

    .line 874
    invoke-virtual/range {v24 .. v24}, Lcom/bachatas4/android/data/InstallManifest;->getOverlays()Ljava/util/List;

    move-result-object v3

    check-cast v3, Ljava/util/Collection;

    move-object/from16 v4, v23

    check-cast v4, Ljava/lang/Iterable;

    invoke-static {v3, v4}, Lkotlin/collections/CollectionsKt;->plus(Ljava/util/Collection;Ljava/lang/Iterable;)Ljava/util/List;

    move-result-object v36

    .line 875
    invoke-static {}, Ljava/lang/System;->currentTimeMillis()J

    move-result-wide v31

    const/16 v37, 0x1be

    const/16 v38, 0x0

    const/16 v25, 0x2

    const/16 v26, 0x0

    const/16 v27, 0x0

    const/16 v28, 0x0

    const/16 v29, 0x0

    const/16 v30, 0x0

    const/16 v33, 0x0

    const-wide/16 v34, 0x0

    .line 872
    invoke-static/range {v24 .. v38}, Lcom/bachatas4/android/data/InstallManifest;->copy$default(Lcom/bachatas4/android/data/InstallManifest;ILjava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;JLjava/util/List;JLjava/util/List;ILjava/lang/Object;)Lcom/bachatas4/android/data/InstallManifest;

    move-result-object v3

    .line 870
    invoke-virtual {v1, v13, v3}, Lcom/bachatas4/android/data/InstallManifestIo;->write(Ljava/io/File;Lcom/bachatas4/android/data/InstallManifest;)V

    .line 879
    invoke-virtual/range {p0 .. p0}, Lcom/bachatas4/android/service/ImportService;->getGameRepository()Lcom/bachatas4/android/data/GameRepository;

    move-result-object v1

    iput-object v2, v7, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$0:Ljava/lang/Object;

    iput-object v9, v7, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$1:Ljava/lang/Object;

    invoke-static/range {v21 .. v21}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v3

    iput-object v3, v7, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$2:Ljava/lang/Object;

    invoke-static/range {v43 .. v43}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v3

    iput-object v3, v7, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$3:Ljava/lang/Object;

    invoke-static {v13}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v3

    iput-object v3, v7, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$4:Ljava/lang/Object;

    move-object/from16 v11, v23

    iput-object v11, v7, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$5:Ljava/lang/Object;

    iput-object v8, v7, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$6:Ljava/lang/Object;

    iput-object v10, v7, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$7:Ljava/lang/Object;

    invoke-static/range {v19 .. v19}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v3

    iput-object v3, v7, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$8:Ljava/lang/Object;

    iput-object v0, v7, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$9:Ljava/lang/Object;

    invoke-static/range {v44 .. v44}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v3

    iput-object v3, v7, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$10:Ljava/lang/Object;

    invoke-static/range {v24 .. v24}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v3

    iput-object v3, v7, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$11:Ljava/lang/Object;

    const/4 v13, 0x0

    iput-object v13, v7, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$12:Ljava/lang/Object;

    iput-object v13, v7, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$13:Ljava/lang/Object;

    iput-object v13, v7, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$14:Ljava/lang/Object;

    iput-object v13, v7, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$15:Ljava/lang/Object;

    iput-object v13, v7, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$16:Ljava/lang/Object;

    iput-object v13, v7, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$17:Ljava/lang/Object;

    iput-object v13, v7, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$18:Ljava/lang/Object;

    iput-object v13, v7, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$19:Ljava/lang/Object;

    iput-object v13, v7, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->L$20:Ljava/lang/Object;

    iput v15, v7, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->I$0:I

    move-wide/from16 v3, v47

    iput-wide v3, v7, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->J$0:J

    move-wide/from16 v3, v62

    iput-wide v3, v7, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->J$1:J

    move-wide/from16 v3, v41

    iput-wide v3, v7, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->J$2:J

    move-wide/from16 v3, v45

    iput-wide v3, v7, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->J$3:J

    const/16 v3, 0x8

    iput v3, v7, Lcom/bachatas4/android/service/ImportService$runPkgBatchImport$1;->label:I

    invoke-virtual {v1, v2, v7}, Lcom/bachatas4/android/data/GameRepository;->touchGame(Ljava/lang/String;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;

    move-result-object v1
    :try_end_70
    .catchall {:try_start_70 .. :try_end_70} :catchall_55

    if-ne v1, v6, :cond_39

    :goto_48
    return-object v6

    :cond_39
    move-object v5, v10

    move v4, v15

    move-object v10, v2

    .line 880
    :goto_49
    :try_start_71
    sget-object v1, Lcom/bachatas4/android/data/ImportManager;->INSTANCE:Lcom/bachatas4/android/data/ImportManager;

    .line 881
    new-instance v2, Lcom/bachatas4/android/data/ImportProgress$BatchInstalled;

    invoke-interface {v11}, Ljava/util/List;->size()I

    move-result v3

    invoke-direct {v2, v10, v0, v3}, Lcom/bachatas4/android/data/ImportProgress$BatchInstalled;-><init>(Ljava/lang/String;Ljava/lang/String;I)V

    check-cast v2, Lcom/bachatas4/android/data/ImportProgress;

    .line 880
    invoke-virtual {v1, v2}, Lcom/bachatas4/android/data/ImportManager;->update(Lcom/bachatas4/android/data/ImportProgress;)V

    .line 883
    invoke-interface {v11}, Ljava/util/List;->size()I

    move-result v1

    new-instance v2, Ljava/lang/StringBuilder;

    invoke-direct {v2}, Ljava/lang/StringBuilder;-><init>()V

    invoke-virtual {v2, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    const-string v2, ": "

    invoke-virtual {v0, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    move-result-object v0

    const-string v1, " package(s) installed"

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0
    :try_end_71
    .catchall {:try_start_71 .. :try_end_71} :catchall_54

    const/4 v10, 0x2

    const/4 v12, 0x0

    const/4 v15, 0x0

    move-object/from16 v1, p0

    :try_start_72
    invoke-static {v1, v0, v12, v10, v15}, Lcom/bachatas4/android/service/ImportService;->notifyDone$default(Lcom/bachatas4/android/service/ImportService;Ljava/lang/String;ZILjava/lang/Object;)V
    :try_end_72
    .catchall {:try_start_72 .. :try_end_72} :catchall_53

    .line 903
    check-cast v8, Ljava/lang/Iterable;

    .line 1211
    invoke-interface {v8}, Ljava/lang/Iterable;->iterator()Ljava/util/Iterator;

    move-result-object v2

    :goto_4a
    invoke-interface {v2}, Ljava/util/Iterator;->hasNext()Z

    move-result v0

    if-eqz v0, :cond_3a

    invoke-interface {v2}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v0

    check-cast v0, Ljava/io/File;

    .line 903
    :try_start_73
    sget-object v3, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    move-object v3, v1

    check-cast v3, Lcom/bachatas4/android/service/ImportService;

    invoke-static {v0}, Lkotlin/io/FilesKt;->deleteRecursively(Ljava/io/File;)Z

    move-result v0

    invoke-static {v0}, Lkotlin/coroutines/jvm/internal/Boxing;->boxBoolean(Z)Ljava/lang/Boolean;

    move-result-object v0

    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;
    :try_end_73
    .catchall {:try_start_73 .. :try_end_73} :catchall_51

    goto :goto_4a

    :catchall_51
    move-exception v0

    sget-object v3, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    invoke-static {v0}, Lkotlin/ResultKt;->createFailure(Ljava/lang/Throwable;)Ljava/lang/Object;

    move-result-object v0

    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;

    goto :goto_4a

    .line 904
    :cond_3a
    check-cast v5, Ljava/lang/Iterable;

    .line 1228
    invoke-interface {v5}, Ljava/lang/Iterable;->iterator()Ljava/util/Iterator;

    move-result-object v2

    :goto_4b
    invoke-interface {v2}, Ljava/util/Iterator;->hasNext()Z

    move-result v0

    if-eqz v0, :cond_3b

    invoke-interface {v2}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v0

    check-cast v0, Ljava/io/File;

    .line 904
    :try_start_74
    sget-object v3, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    move-object v3, v1

    check-cast v3, Lcom/bachatas4/android/service/ImportService;

    invoke-virtual {v0}, Ljava/io/File;->delete()Z

    move-result v0

    invoke-static {v0}, Lkotlin/coroutines/jvm/internal/Boxing;->boxBoolean(Z)Ljava/lang/Boolean;

    move-result-object v0

    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;
    :try_end_74
    .catchall {:try_start_74 .. :try_end_74} :catchall_52

    goto :goto_4b

    :catchall_52
    move-exception v0

    sget-object v3, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    invoke-static {v0}, Lkotlin/ResultKt;->createFailure(Ljava/lang/Throwable;)Ljava/lang/Object;

    move-result-object v0

    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;

    goto :goto_4b

    :cond_3b
    const/4 v15, 0x0

    .line 905
    iput-object v15, v1, Lcom/bachatas4/android/service/ImportService;->passcodeWaiter:Lkotlinx/coroutines/CompletableDeferred;

    .line 906
    iput-object v15, v1, Lcom/bachatas4/android/service/ImportService;->copyConfirmWaiter:Lkotlinx/coroutines/CompletableDeferred;

    .line 907
    sget-object v0, Lcom/bachatas4/android/data/ImportManager;->INSTANCE:Lcom/bachatas4/android/data/ImportManager;

    const/4 v12, 0x1

    invoke-static {v0, v15, v12, v15}, Lcom/bachatas4/android/data/ImportManager;->isBusy$default(Lcom/bachatas4/android/data/ImportManager;Lcom/bachatas4/android/data/ImportProgress;ILjava/lang/Object;)Z

    move-result v0

    if-eqz v0, :cond_3c

    sget-object v0, Lcom/bachatas4/android/data/ImportManager;->INSTANCE:Lcom/bachatas4/android/data/ImportManager;

    invoke-virtual {v0}, Lcom/bachatas4/android/data/ImportManager;->reset()V

    .line 908
    :cond_3c
    invoke-interface {v9}, Ljava/util/List;->size()I

    move-result v0

    new-instance v2, Ljava/lang/StringBuilder;

    move-object/from16 v3, v64

    invoke-direct {v2, v3}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v2, v4}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    move-result-object v2

    move-object/from16 v11, v53

    invoke-virtual {v2, v11}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v2

    invoke-virtual {v2, v0}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    move-object/from16 v12, v106

    goto/16 :goto_5c

    :catchall_53
    move-exception v0

    goto :goto_4c

    :catchall_54
    move-exception v0

    move-object/from16 v1, p0

    :goto_4c
    move-object/from16 v11, v53

    move-object/from16 v3, v64

    move-object/from16 v12, v106

    :goto_4d
    move v14, v4

    goto/16 :goto_58

    :catchall_55
    move-exception v0

    move-object/from16 v1, p0

    move-object/from16 v11, v53

    move-object/from16 v3, v64

    move-object/from16 v12, v106

    goto :goto_4e

    :catchall_56
    move-exception v0

    move-object v8, v7

    move v15, v10

    move-object v12, v14

    move-object/from16 v3, v54

    move-object v10, v1

    move-object v1, v11

    move-object/from16 v11, v53

    :goto_4e
    move-object v5, v10

    move v14, v15

    goto/16 :goto_58

    :catchall_57
    move-exception v0

    move-object v3, v1

    move-object v1, v11

    move-object v12, v14

    move-object v11, v8

    move v14, v2

    move-object v5, v15

    :goto_4f
    move-object/from16 v8, v21

    goto/16 :goto_58

    :catchall_58
    move-exception v0

    move-object/from16 v21, v8

    move v2, v10

    move-object v12, v14

    move-object/from16 v11, v53

    move-object/from16 v3, v54

    move v14, v2

    goto/16 :goto_e

    :catchall_59
    move-exception v0

    goto :goto_50

    :catchall_5a
    move-exception v0

    move-object/from16 p2, v3

    :goto_50
    move-object v12, v14

    move-object/from16 v11, v53

    move-object/from16 v3, v54

    move-object/from16 v8, p2

    move-object v5, v7

    goto/16 :goto_2

    :catchall_5b
    move-exception v0

    goto :goto_51

    :catchall_5c
    move-exception v0

    move-object/from16 v9, p2

    :goto_51
    move-object v12, v14

    move-object/from16 v11, v53

    move-object/from16 v3, v54

    move-object v8, v6

    move-object v5, v7

    const/4 v14, 0x0

    goto/16 :goto_58

    :cond_3d
    :goto_52
    move-object/from16 v9, p2

    move-object v12, v14

    move-object/from16 v11, v53

    move-object/from16 v3, v54

    .line 689
    :try_start_75
    sget-object v0, Lcom/bachatas4/android/data/ImportManager;->INSTANCE:Lcom/bachatas4/android/data/ImportManager;

    .line 690
    new-instance v2, Lcom/bachatas4/android/data/ImportProgress$BatchFailed;

    sget-object v4, Lcom/bachatas4/android/data/InstallErrorCode;->BASE_MISSING:Lcom/bachatas4/android/data/InstallErrorCode;

    const-string v5, "Base game not installed"

    invoke-interface {v9}, Ljava/util/List;->size()I

    move-result v8
    :try_end_75
    .catchall {:try_start_75 .. :try_end_75} :catchall_60

    const/4 v10, 0x0

    :try_start_76
    invoke-direct {v2, v4, v5, v10, v8}, Lcom/bachatas4/android/data/ImportProgress$BatchFailed;-><init>(Lcom/bachatas4/android/data/InstallErrorCode;Ljava/lang/String;II)V

    check-cast v2, Lcom/bachatas4/android/data/ImportProgress;

    .line 689
    invoke-virtual {v0, v2}, Lcom/bachatas4/android/data/ImportManager;->update(Lcom/bachatas4/android/data/ImportProgress;)V

    .line 692
    sget-object v2, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;
    :try_end_76
    .catchall {:try_start_76 .. :try_end_76} :catchall_5f

    .line 903
    check-cast v6, Ljava/lang/Iterable;

    .line 1211
    invoke-interface {v6}, Ljava/lang/Iterable;->iterator()Ljava/util/Iterator;

    move-result-object v3

    :goto_53
    invoke-interface {v3}, Ljava/util/Iterator;->hasNext()Z

    move-result v0

    if-eqz v0, :cond_3e

    invoke-interface {v3}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v0

    check-cast v0, Ljava/io/File;

    .line 903
    :try_start_77
    sget-object v4, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    move-object v4, v1

    check-cast v4, Lcom/bachatas4/android/service/ImportService;

    invoke-static {v0}, Lkotlin/io/FilesKt;->deleteRecursively(Ljava/io/File;)Z

    move-result v0

    invoke-static {v0}, Lkotlin/coroutines/jvm/internal/Boxing;->boxBoolean(Z)Ljava/lang/Boolean;

    move-result-object v0

    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;
    :try_end_77
    .catchall {:try_start_77 .. :try_end_77} :catchall_5d

    goto :goto_53

    :catchall_5d
    move-exception v0

    sget-object v4, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    invoke-static {v0}, Lkotlin/ResultKt;->createFailure(Ljava/lang/Throwable;)Ljava/lang/Object;

    move-result-object v0

    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;

    goto :goto_53

    .line 904
    :cond_3e
    check-cast v7, Ljava/lang/Iterable;

    .line 1213
    invoke-interface {v7}, Ljava/lang/Iterable;->iterator()Ljava/util/Iterator;

    move-result-object v3

    :goto_54
    invoke-interface {v3}, Ljava/util/Iterator;->hasNext()Z

    move-result v0

    if-eqz v0, :cond_3f

    invoke-interface {v3}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v0

    check-cast v0, Ljava/io/File;

    .line 904
    :try_start_78
    sget-object v4, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    move-object v4, v1

    check-cast v4, Lcom/bachatas4/android/service/ImportService;

    invoke-virtual {v0}, Ljava/io/File;->delete()Z

    move-result v0

    invoke-static {v0}, Lkotlin/coroutines/jvm/internal/Boxing;->boxBoolean(Z)Ljava/lang/Boolean;

    move-result-object v0

    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;
    :try_end_78
    .catchall {:try_start_78 .. :try_end_78} :catchall_5e

    goto :goto_54

    :catchall_5e
    move-exception v0

    sget-object v4, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    invoke-static {v0}, Lkotlin/ResultKt;->createFailure(Ljava/lang/Throwable;)Ljava/lang/Object;

    move-result-object v0

    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;

    goto :goto_54

    :cond_3f
    const/4 v15, 0x0

    .line 905
    iput-object v15, v1, Lcom/bachatas4/android/service/ImportService;->passcodeWaiter:Lkotlinx/coroutines/CompletableDeferred;

    .line 906
    iput-object v15, v1, Lcom/bachatas4/android/service/ImportService;->copyConfirmWaiter:Lkotlinx/coroutines/CompletableDeferred;

    .line 907
    sget-object v0, Lcom/bachatas4/android/data/ImportManager;->INSTANCE:Lcom/bachatas4/android/data/ImportManager;

    const/4 v4, 0x1

    invoke-static {v0, v15, v4, v15}, Lcom/bachatas4/android/data/ImportManager;->isBusy$default(Lcom/bachatas4/android/data/ImportManager;Lcom/bachatas4/android/data/ImportProgress;ILjava/lang/Object;)Z

    move-result v0

    if-eqz v0, :cond_40

    sget-object v0, Lcom/bachatas4/android/data/ImportManager;->INSTANCE:Lcom/bachatas4/android/data/ImportManager;

    invoke-virtual {v0}, Lcom/bachatas4/android/data/ImportManager;->reset()V

    .line 908
    :cond_40
    invoke-interface {v9}, Ljava/util/List;->size()I

    move-result v0

    new-instance v3, Ljava/lang/StringBuilder;

    const-string v4, "pkg batch finished completed=0/"

    invoke-direct {v3, v4}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v3, v0}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    invoke-static {v12, v0}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    .line 909
    invoke-virtual {v1}, Lcom/bachatas4/android/service/ImportService;->stopSelf()V

    return-object v2

    :catchall_5f
    move-exception v0

    goto :goto_56

    :catchall_60
    move-exception v0

    goto :goto_55

    :catchall_61
    move-exception v0

    move-object/from16 v9, p2

    move-object v12, v14

    move-object/from16 v11, v53

    move-object/from16 v3, v54

    :goto_55
    const/4 v10, 0x0

    :goto_56
    move-object v8, v6

    move-object v5, v7

    :goto_57
    move v14, v10

    .line 885
    :goto_58
    :try_start_79
    instance-of v2, v0, Ljava/util/concurrent/CancellationException;

    if-nez v2, :cond_48

    .line 886
    const-string v2, "pkg batch failed"

    invoke-static {v12, v2, v0}, Landroid/util/Log;->e(Ljava/lang/String;Ljava/lang/String;Ljava/lang/Throwable;)I

    .line 887
    sget-object v2, Lcom/bachatas4/android/data/ImportManager;->INSTANCE:Lcom/bachatas4/android/data/ImportManager;

    .line 888
    new-instance v4, Lcom/bachatas4/android/data/ImportProgress$BatchFailed;

    .line 890
    instance-of v6, v0, Lcom/bachatas4/android/data/ContentImportException;

    if-eqz v6, :cond_43

    move-object v6, v0

    check-cast v6, Lcom/bachatas4/android/data/ContentImportException;

    invoke-virtual {v6}, Lcom/bachatas4/android/data/ContentImportException;->getCode()Lcom/bachatas4/android/model/RuntimeErrorCode;

    move-result-object v6

    sget-object v7, Lcom/bachatas4/android/service/ImportService$WhenMappings;->$EnumSwitchMapping$0:[I

    invoke-virtual {v6}, Lcom/bachatas4/android/model/RuntimeErrorCode;->ordinal()I

    move-result v6

    aget v6, v7, v6

    const/4 v7, 0x1

    if-eq v6, v7, :cond_42

    const/4 v10, 0x2

    if-eq v6, v10, :cond_41

    .line 893
    sget-object v6, Lcom/bachatas4/android/data/InstallErrorCode;->UNKNOWN:Lcom/bachatas4/android/data/InstallErrorCode;

    goto :goto_59

    .line 892
    :cond_41
    sget-object v6, Lcom/bachatas4/android/data/InstallErrorCode;->PERMISSION_LOST:Lcom/bachatas4/android/data/InstallErrorCode;

    goto :goto_59

    .line 891
    :cond_42
    sget-object v6, Lcom/bachatas4/android/data/InstallErrorCode;->MALFORMED_PACKAGE:Lcom/bachatas4/android/data/InstallErrorCode;

    goto :goto_59

    .line 895
    :cond_43
    sget-object v6, Lcom/bachatas4/android/data/InstallErrorCode;->UNKNOWN:Lcom/bachatas4/android/data/InstallErrorCode;

    .line 897
    :goto_59
    invoke-virtual {v0}, Ljava/lang/Throwable;->getMessage()Ljava/lang/String;

    move-result-object v0

    if-nez v0, :cond_44

    const-string v0, "Batch install failed"

    .line 899
    :cond_44
    invoke-interface {v9}, Ljava/util/List;->size()I

    move-result v7

    .line 888
    invoke-direct {v4, v6, v0, v14, v7}, Lcom/bachatas4/android/data/ImportProgress$BatchFailed;-><init>(Lcom/bachatas4/android/data/InstallErrorCode;Ljava/lang/String;II)V

    check-cast v4, Lcom/bachatas4/android/data/ImportProgress;

    .line 887
    invoke-virtual {v2, v4}, Lcom/bachatas4/android/data/ImportManager;->update(Lcom/bachatas4/android/data/ImportProgress;)V
    :try_end_79
    .catchall {:try_start_79 .. :try_end_79} :catchall_64

    .line 903
    check-cast v8, Ljava/lang/Iterable;

    .line 1211
    invoke-interface {v8}, Ljava/lang/Iterable;->iterator()Ljava/util/Iterator;

    move-result-object v2

    :goto_5a
    invoke-interface {v2}, Ljava/util/Iterator;->hasNext()Z

    move-result v0

    if-eqz v0, :cond_45

    invoke-interface {v2}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v0

    check-cast v0, Ljava/io/File;

    .line 903
    :try_start_7a
    sget-object v4, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    invoke-static {v0}, Lkotlin/io/FilesKt;->deleteRecursively(Ljava/io/File;)Z

    move-result v0

    invoke-static {v0}, Lkotlin/coroutines/jvm/internal/Boxing;->boxBoolean(Z)Ljava/lang/Boolean;

    move-result-object v0

    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;
    :try_end_7a
    .catchall {:try_start_7a .. :try_end_7a} :catchall_62

    goto :goto_5a

    :catchall_62
    move-exception v0

    sget-object v4, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    invoke-static {v0}, Lkotlin/ResultKt;->createFailure(Ljava/lang/Throwable;)Ljava/lang/Object;

    move-result-object v0

    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;

    goto :goto_5a

    .line 904
    :cond_45
    check-cast v5, Ljava/lang/Iterable;

    .line 1231
    invoke-interface {v5}, Ljava/lang/Iterable;->iterator()Ljava/util/Iterator;

    move-result-object v2

    :goto_5b
    invoke-interface {v2}, Ljava/util/Iterator;->hasNext()Z

    move-result v0

    if-eqz v0, :cond_46

    invoke-interface {v2}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v0

    check-cast v0, Ljava/io/File;

    .line 904
    :try_start_7b
    sget-object v4, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    invoke-virtual {v0}, Ljava/io/File;->delete()Z

    move-result v0

    invoke-static {v0}, Lkotlin/coroutines/jvm/internal/Boxing;->boxBoolean(Z)Ljava/lang/Boolean;

    move-result-object v0

    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;
    :try_end_7b
    .catchall {:try_start_7b .. :try_end_7b} :catchall_63

    goto :goto_5b

    :catchall_63
    move-exception v0

    sget-object v4, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    invoke-static {v0}, Lkotlin/ResultKt;->createFailure(Ljava/lang/Throwable;)Ljava/lang/Object;

    move-result-object v0

    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;

    goto :goto_5b

    :cond_46
    const/4 v15, 0x0

    .line 905
    iput-object v15, v1, Lcom/bachatas4/android/service/ImportService;->passcodeWaiter:Lkotlinx/coroutines/CompletableDeferred;

    .line 906
    iput-object v15, v1, Lcom/bachatas4/android/service/ImportService;->copyConfirmWaiter:Lkotlinx/coroutines/CompletableDeferred;

    .line 907
    sget-object v0, Lcom/bachatas4/android/data/ImportManager;->INSTANCE:Lcom/bachatas4/android/data/ImportManager;

    const/4 v4, 0x1

    invoke-static {v0, v15, v4, v15}, Lcom/bachatas4/android/data/ImportManager;->isBusy$default(Lcom/bachatas4/android/data/ImportManager;Lcom/bachatas4/android/data/ImportProgress;ILjava/lang/Object;)Z

    move-result v0

    if-eqz v0, :cond_47

    sget-object v0, Lcom/bachatas4/android/data/ImportManager;->INSTANCE:Lcom/bachatas4/android/data/ImportManager;

    invoke-virtual {v0}, Lcom/bachatas4/android/data/ImportManager;->reset()V

    .line 908
    :cond_47
    invoke-interface {v9}, Ljava/util/List;->size()I

    move-result v0

    new-instance v2, Ljava/lang/StringBuilder;

    invoke-direct {v2, v3}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v2, v14}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    move-result-object v2

    invoke-virtual {v2, v11}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v2

    invoke-virtual {v2, v0}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    :goto_5c
    invoke-static {v12, v0}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    .line 909
    invoke-virtual {v1}, Lcom/bachatas4/android/service/ImportService;->stopSelf()V

    .line 911
    sget-object v0, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;

    return-object v0

    .line 885
    :cond_48
    :try_start_7c
    throw v0
    :try_end_7c
    .catchall {:try_start_7c .. :try_end_7c} :catchall_64

    :catchall_64
    move-exception v0

    move-object v2, v0

    .line 903
    check-cast v8, Ljava/lang/Iterable;

    .line 1211
    invoke-interface {v8}, Ljava/lang/Iterable;->iterator()Ljava/util/Iterator;

    move-result-object v4

    :goto_5d
    invoke-interface {v4}, Ljava/util/Iterator;->hasNext()Z

    move-result v0

    if-eqz v0, :cond_49

    invoke-interface {v4}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v0

    check-cast v0, Ljava/io/File;

    .line 903
    :try_start_7d
    sget-object v6, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    invoke-static {v0}, Lkotlin/io/FilesKt;->deleteRecursively(Ljava/io/File;)Z

    move-result v0

    invoke-static {v0}, Lkotlin/coroutines/jvm/internal/Boxing;->boxBoolean(Z)Ljava/lang/Boolean;

    move-result-object v0

    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;
    :try_end_7d
    .catchall {:try_start_7d .. :try_end_7d} :catchall_65

    goto :goto_5d

    :catchall_65
    move-exception v0

    sget-object v6, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    invoke-static {v0}, Lkotlin/ResultKt;->createFailure(Ljava/lang/Throwable;)Ljava/lang/Object;

    move-result-object v0

    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;

    goto :goto_5d

    .line 904
    :cond_49
    check-cast v5, Ljava/lang/Iterable;

    .line 1234
    invoke-interface {v5}, Ljava/lang/Iterable;->iterator()Ljava/util/Iterator;

    move-result-object v4

    :goto_5e
    invoke-interface {v4}, Ljava/util/Iterator;->hasNext()Z

    move-result v0

    if-eqz v0, :cond_4a

    invoke-interface {v4}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v0

    check-cast v0, Ljava/io/File;

    .line 904
    :try_start_7e
    sget-object v5, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    invoke-virtual {v0}, Ljava/io/File;->delete()Z

    move-result v0

    invoke-static {v0}, Lkotlin/coroutines/jvm/internal/Boxing;->boxBoolean(Z)Ljava/lang/Boolean;

    move-result-object v0

    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;
    :try_end_7e
    .catchall {:try_start_7e .. :try_end_7e} :catchall_66

    goto :goto_5e

    :catchall_66
    move-exception v0

    sget-object v5, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    invoke-static {v0}, Lkotlin/ResultKt;->createFailure(Ljava/lang/Throwable;)Ljava/lang/Object;

    move-result-object v0

    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;

    goto :goto_5e

    :cond_4a
    const/4 v15, 0x0

    .line 905
    iput-object v15, v1, Lcom/bachatas4/android/service/ImportService;->passcodeWaiter:Lkotlinx/coroutines/CompletableDeferred;

    .line 906
    iput-object v15, v1, Lcom/bachatas4/android/service/ImportService;->copyConfirmWaiter:Lkotlinx/coroutines/CompletableDeferred;

    .line 907
    sget-object v0, Lcom/bachatas4/android/data/ImportManager;->INSTANCE:Lcom/bachatas4/android/data/ImportManager;

    const/4 v4, 0x1

    invoke-static {v0, v15, v4, v15}, Lcom/bachatas4/android/data/ImportManager;->isBusy$default(Lcom/bachatas4/android/data/ImportManager;Lcom/bachatas4/android/data/ImportProgress;ILjava/lang/Object;)Z

    move-result v0

    if-eqz v0, :cond_4b

    sget-object v0, Lcom/bachatas4/android/data/ImportManager;->INSTANCE:Lcom/bachatas4/android/data/ImportManager;

    invoke-virtual {v0}, Lcom/bachatas4/android/data/ImportManager;->reset()V

    .line 908
    :cond_4b
    invoke-interface {v9}, Ljava/util/List;->size()I

    move-result v0

    new-instance v4, Ljava/lang/StringBuilder;

    invoke-direct {v4, v3}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v4, v14}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    move-result-object v3

    invoke-virtual {v3, v11}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v3

    invoke-virtual {v3, v0}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    invoke-static {v12, v0}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    .line 909
    invoke-virtual {v1}, Lcom/bachatas4/android/service/ImportService;->stopSelf()V

    throw v2

    :pswitch_data_0
    .packed-switch 0x0
        :pswitch_8
        :pswitch_7
        :pswitch_6
        :pswitch_5
        :pswitch_4
        :pswitch_3
        :pswitch_2
        :pswitch_1
        :pswitch_0
    .end packed-switch
.end method

.method private final runPkgImport(Ljava/lang/String;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;
    .locals 259
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

    move-object/from16 v1, p0

    move-object/from16 v8, p1

    move-object/from16 v0, p2

    const-string v9, "pkg space package="

    const-string v10, "pkg cache copy start dest="

    const-string v11, "pkg-cache/"

    const-string v12, "pkg direct saf fd (skip cache) uri="

    const-string v13, "pkg extract candidates="

    const-string v14, "pkg staging="

    const-string v15, "pkg persistable permission: "

    const-string v2, "pkg nativeProbe done status="

    const-string v3, "pkg nativeProbe start fd="

    const-string v4, ".import-"

    const-string v5, "pkg extract fd="

    const-string v6, "pkg saf fd seekable="

    const-string v7, "pkg copy confirmed; free="

    move-object/from16 v16, v9

    const-string v9, "pkg openFileDescriptor ok sizeHint="

    move-object/from16 v17, v9

    const-string v9, "pkg cache copy done size="

    move-object/from16 v18, v2

    instance-of v2, v0, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;

    if-eqz v2, :cond_0

    move-object v2, v0

    check-cast v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;

    move-object/from16 v19, v3

    iget v3, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->label:I

    const/high16 v20, -0x80000000

    and-int v3, v3, v20

    if-eqz v3, :cond_1

    iget v0, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->label:I

    sub-int v0, v0, v20

    iput v0, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->label:I

    goto :goto_0

    :cond_0
    move-object/from16 v19, v3

    :cond_1
    new-instance v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;

    invoke-direct {v2, v1, v0}, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;-><init>(Lcom/bachatas4/android/service/ImportService;Lkotlin/coroutines/Continuation;)V

    :goto_0
    iget-object v0, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->result:Ljava/lang/Object;

    invoke-static {}, Lkotlin/coroutines/intrinsics/IntrinsicsKt;->getCOROUTINE_SUSPENDED()Ljava/lang/Object;

    move-result-object v3

    .line 321
    iget v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->label:I

    move-object/from16 v20, v9

    const-string v9, " is available"

    move-object/16 p2, v9

    const-string v9, " direct="

    move-object/from16 v22, v9

    const-string v9, " size="

    move-object/from16 v23, v9

    const-string v9, " required="

    move-object/from16 v24, v9

    const-string v9, "00000000000000000000000000000000"

    move-object/from16 v25, v9

    const-string v9, "pkg extract attempt #"

    move-object/from16 v26, v9

    const-string v9, " msg="

    move-object/from16 v27, v9

    const-string v9, " (stopSelf)"

    move-object/from16 v28, v9

    const-string v9, "pkg import finished completed="

    move-object/from16 v29, v9

    const-string v9, "pkg import cleanup staging="

    move-object/from16 v30, v9

    const-string v9, "pkg cache delete path="

    move-object/from16 v31, v9

    const-string v9, "cancelled"

    move-object/from16 v33, v9

    const-string v9, "getFilesDir(...)"

    move-object/from16 v34, v10

    const-string v10, "BachataImport"

    move-object/from16 v36, v11

    const-string v11, "Import needs about "

    packed-switch v1, :pswitch_data_0

    new-instance v0, Ljava/lang/IllegalStateException;

    const-string v1, "call to \'resume\' before \'invoke\' with coroutine"

    invoke-direct {v0, v1}, Ljava/lang/IllegalStateException;-><init>(Ljava/lang/String;)V

    throw v0

    :pswitch_0
    iget v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->I$0:I

    iget-wide v3, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$6:J

    iget-boolean v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->Z$1:Z

    iget-wide v3, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$5:J

    iget-wide v3, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$4:J

    iget-wide v3, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$3:J

    iget-wide v3, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$2:J

    iget-wide v3, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$1:J

    iget-wide v3, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$0:J

    iget-boolean v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->Z$0:Z

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$23:Ljava/lang/Object;

    check-cast v1, Lcom/bachatas4/android/data/ContentImportResult;

    iget-object v3, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$22:Ljava/lang/Object;

    check-cast v3, Ljava/io/File;

    iget-object v3, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$21:Ljava/lang/Object;

    check-cast v3, Lcom/bachatas4/android/data/ResolvedGameMetadata;

    iget-object v4, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$20:Ljava/lang/Object;

    check-cast v4, Lcom/bachatas4/android/data/ParamSfoMetadata;

    iget-object v4, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$19:Ljava/lang/Object;

    check-cast v4, Ljava/io/File;

    iget-object v4, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$18:Ljava/lang/Object;

    check-cast v4, Landroid/os/ParcelFileDescriptor;

    iget-object v4, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$17:Ljava/lang/Object;

    check-cast v4, Ljava/io/Closeable;

    iget-object v5, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$16:Ljava/lang/Object;

    check-cast v5, Landroid/os/ParcelFileDescriptor;

    iget-object v5, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$15:Ljava/lang/Object;

    check-cast v5, Ljava/util/List;

    iget-object v5, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$14:Ljava/lang/Object;

    check-cast v5, Lkotlin/jvm/internal/Ref$ObjectRef;

    iget-object v5, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$13:Ljava/lang/Object;

    check-cast v5, Lkotlin/jvm/internal/Ref$ObjectRef;

    iget-object v5, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$12:Ljava/lang/Object;

    check-cast v5, Lkotlinx/coroutines/CompletableDeferred;

    iget-object v5, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$11:Ljava/lang/Object;

    check-cast v5, Ljava/io/File;

    iget-object v5, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$10:Ljava/lang/Object;

    check-cast v5, Ljava/lang/String;

    iget-object v5, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$9:Ljava/lang/Object;

    check-cast v5, Lkotlin/jvm/internal/Ref$BooleanRef;

    iget-object v5, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$8:Ljava/lang/Object;

    check-cast v5, Lkotlin/jvm/internal/Ref$ObjectRef;

    iget-object v5, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$7:Ljava/lang/Object;

    check-cast v5, Landroid/net/Uri;

    iget-object v5, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$6:Ljava/lang/Object;

    check-cast v5, Lkotlin/jvm/internal/Ref$BooleanRef;

    iget-object v6, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$5:Ljava/lang/Object;

    check-cast v6, Ljava/io/File;

    iget-object v7, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$4:Ljava/lang/Object;

    check-cast v7, Lkotlin/jvm/internal/Ref$ObjectRef;

    iget-object v8, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$3:Ljava/lang/Object;

    check-cast v8, Lkotlin/jvm/internal/Ref$ObjectRef;

    iget-object v8, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$2:Ljava/lang/Object;

    check-cast v8, Lcom/bachatas4/android/data/InstallJobStore;

    iget-object v11, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$1:Ljava/lang/Object;

    check-cast v11, Ljava/lang/String;

    iget-object v2, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$0:Ljava/lang/Object;

    check-cast v2, Ljava/lang/String;

    :try_start_0
    invoke-static {v0}, Lkotlin/ResultKt;->throwOnFailure(Ljava/lang/Object;)V
    :try_end_0
    .catchall {:try_start_0 .. :try_end_0} :catchall_0

    move-object/from16 v43, v9

    move-object v12, v10

    move-object/from16 v82, v28

    move-object/from16 v83, v29

    move-object/from16 v84, v30

    move-object/from16 v85, v31

    const/4 v0, 0x0

    const/16 v54, 0x0

    goto/16 :goto_36

    :catchall_0
    move-exception v0

    move-object/from16 v2, p0

    move-object v3, v0

    move-object/from16 v43, v9

    move-object v12, v10

    move-object/from16 v82, v28

    move-object/from16 v15, v29

    move-object/from16 v1, v30

    :goto_1
    move-object v9, v6

    goto/16 :goto_46

    :pswitch_1
    iget v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->I$0:I

    iget-wide v4, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$6:J

    iget-boolean v6, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->Z$1:Z

    iget-wide v7, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$5:J

    iget-wide v11, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$4:J

    iget-wide v13, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$3:J

    move-object/from16 v38, v3

    move-wide v15, v4

    iget-wide v3, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$2:J

    move-wide/from16 v17, v3

    iget-wide v3, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$1:J

    move-wide/from16 v19, v3

    iget-wide v3, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$0:J

    iget-boolean v5, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->Z$0:Z

    move/from16 v22, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$22:Ljava/lang/Object;

    check-cast v1, Ljava/io/File;

    move-object/16 p1, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$21:Ljava/lang/Object;

    check-cast v1, Lcom/bachatas4/android/data/ResolvedGameMetadata;

    move-object/16 p2, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$20:Ljava/lang/Object;

    check-cast v1, Lcom/bachatas4/android/data/ParamSfoMetadata;

    move-object/from16 v23, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$19:Ljava/lang/Object;

    check-cast v1, Ljava/io/File;

    move-object/from16 v24, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$18:Ljava/lang/Object;

    check-cast v1, Landroid/os/ParcelFileDescriptor;

    move-object/from16 v26, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$17:Ljava/lang/Object;

    check-cast v1, Ljava/io/Closeable;

    move-object/from16 v27, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$16:Ljava/lang/Object;

    check-cast v1, Landroid/os/ParcelFileDescriptor;

    move-object/from16 v33, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$15:Ljava/lang/Object;

    check-cast v1, Ljava/util/List;

    move-object/from16 v34, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$14:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$ObjectRef;

    move-object/from16 v36, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$13:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$ObjectRef;

    move-object/from16 v39, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$12:Ljava/lang/Object;

    check-cast v1, Lkotlinx/coroutines/CompletableDeferred;

    move-object/from16 v40, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$11:Ljava/lang/Object;

    check-cast v1, Ljava/io/File;

    move-object/from16 v41, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$10:Ljava/lang/Object;

    check-cast v1, Ljava/lang/String;

    move-object/from16 v42, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$9:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$BooleanRef;

    move-object/from16 v43, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$8:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$ObjectRef;

    move-object/from16 v44, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$7:Ljava/lang/Object;

    check-cast v1, Landroid/net/Uri;

    move-object/from16 v45, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$6:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$BooleanRef;

    move-object/from16 v46, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$5:Ljava/lang/Object;

    check-cast v1, Ljava/io/File;

    move-object/from16 v47, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$4:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$ObjectRef;

    move-object/from16 v48, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$3:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$ObjectRef;

    move-object/from16 v49, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$2:Ljava/lang/Object;

    check-cast v1, Lcom/bachatas4/android/data/InstallJobStore;

    move-object/from16 v50, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$1:Ljava/lang/Object;

    check-cast v1, Ljava/lang/String;

    move-object/from16 v51, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$0:Ljava/lang/Object;

    check-cast v1, Ljava/lang/String;

    :try_start_1
    invoke-static {v0}, Lkotlin/ResultKt;->throwOnFailure(Ljava/lang/Object;)V
    :try_end_1
    .catchall {:try_start_1 .. :try_end_1} :catchall_1

    move/from16 v249, v6

    move-wide/from16 v250, v7

    move-wide/from16 v252, v11

    move-wide/from16 v254, v13

    move-object/from16 v82, v28

    move-object/from16 v83, v29

    move-object/from16 v84, v30

    move-object/from16 v85, v31

    move-object/from16 v11, v44

    move-object/from16 v14, v48

    move-object/from16 v32, v49

    move-object/from16 v7, v51

    const/16 v54, 0x0

    move-object/from16 v31, p1

    move-object/from16 v13, p2

    move-object/16 p1, v1

    move-object v12, v10

    move-object/from16 v29, v23

    move-object/from16 v30, v24

    move-object/from16 v23, v26

    move-object/from16 v1, v39

    move-object/16 p2, v41

    move-object/from16 v10, v47

    move-object/16 v256, v9

    move-object v9, v2

    move-object/from16 v2, v27

    move-wide/from16 v26, v17

    move-object/from16 v18, v34

    move-object/from16 v34, v36

    move-object/from16 v17, v40

    move-wide/from16 v39, v19

    move/from16 v19, v22

    const/16 v22, 0x0

    move-wide/from16 v20, v15

    move-object/from16 v16, v43

    move-object/from16 v15, v50

    move-object/from16 v43, v256

    move-wide/16 v256, v3

    move v4, v5

    move-wide/from16 v5, v256

    move-object/from16 v3, v46

    goto/16 :goto_32

    :catchall_1
    move-exception v0

    move-object/from16 v2, p0

    move-object v3, v0

    move-object/from16 v43, v9

    move-object v12, v10

    move-object/from16 v4, v27

    move-object/from16 v82, v28

    move-object/from16 v15, v29

    move-object/from16 v1, v30

    move-object/from16 v5, v46

    move-object/from16 v9, v47

    move-object/from16 v7, v48

    move-object/from16 v8, v50

    move-object/from16 v11, v51

    goto/16 :goto_46

    :pswitch_2
    move-object/from16 v38, v3

    iget v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->I$0:I

    iget-wide v3, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$6:J

    iget-boolean v5, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->Z$1:Z

    iget-wide v6, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$5:J

    iget-wide v11, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$4:J

    iget-wide v13, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$3:J

    move-wide v15, v3

    iget-wide v3, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$2:J

    move-wide/from16 v17, v3

    iget-wide v3, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$1:J

    move-wide/from16 v19, v3

    iget-wide v3, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$0:J

    iget-boolean v8, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->Z$0:Z

    move/from16 v22, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$20:Ljava/lang/Object;

    check-cast v1, Ljava/lang/String;

    move-object/16 p1, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$19:Ljava/lang/Object;

    check-cast v1, Lkotlinx/coroutines/CompletableDeferred;

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$18:Ljava/lang/Object;

    check-cast v1, Landroid/os/ParcelFileDescriptor;

    move-object/16 p2, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$17:Ljava/lang/Object;

    check-cast v1, Ljava/io/Closeable;

    move-object/from16 v23, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$16:Ljava/lang/Object;

    check-cast v1, Landroid/os/ParcelFileDescriptor;

    move-object/from16 v24, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$15:Ljava/lang/Object;

    check-cast v1, Ljava/util/List;

    move-object/from16 v26, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$14:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$ObjectRef;

    move-object/from16 v34, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$13:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$ObjectRef;

    move-object/from16 v36, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$12:Ljava/lang/Object;

    check-cast v1, Lkotlinx/coroutines/CompletableDeferred;

    move-object/from16 v39, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$11:Ljava/lang/Object;

    check-cast v1, Ljava/io/File;

    move-object/from16 v40, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$10:Ljava/lang/Object;

    check-cast v1, Ljava/lang/String;

    move-object/from16 v41, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$9:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$BooleanRef;

    move-object/from16 v42, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$8:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$ObjectRef;

    move-object/from16 v43, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$7:Ljava/lang/Object;

    check-cast v1, Landroid/net/Uri;

    move-object/from16 v44, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$6:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$BooleanRef;

    move-object/from16 v45, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$5:Ljava/lang/Object;

    check-cast v1, Ljava/io/File;

    move-object/from16 v46, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$4:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$ObjectRef;

    move-object/from16 v47, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$3:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$ObjectRef;

    move-object/from16 v48, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$2:Ljava/lang/Object;

    check-cast v1, Lcom/bachatas4/android/data/InstallJobStore;

    move-object/from16 v49, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$1:Ljava/lang/Object;

    check-cast v1, Ljava/lang/String;

    move-object/from16 v50, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$0:Ljava/lang/Object;

    check-cast v1, Ljava/lang/String;

    :try_start_2
    invoke-static {v0}, Lkotlin/ResultKt;->throwOnFailure(Ljava/lang/Object;)V
    :try_end_2
    .catchall {:try_start_2 .. :try_end_2} :catchall_2

    move/from16 v229, v5

    move-object/from16 v230, v10

    move-object/from16 v192, v27

    move-object/from16 v82, v28

    move-object/from16 v83, v29

    move-object/from16 v84, v30

    move-object/from16 v85, v31

    move-object/from16 v210, v33

    move-object/from16 v5, v41

    const/16 v21, 0x0

    const/16 v54, 0x0

    move/from16 v33, v8

    move-wide/from16 v31, v17

    move-wide/from16 v29, v19

    move-object/from16 v18, v26

    move-object/from16 v17, v39

    move-object/from16 v26, v44

    move-object v8, v1

    move-wide/from16 v19, v11

    move-object/from16 v12, v36

    move-object/from16 v1, v38

    move-object/from16 v11, v43

    move-object/from16 v43, v9

    move-wide/from16 v38, v13

    move-object/from16 v13, v23

    move-object/from16 v23, p2

    move-object v14, v2

    move-wide v9, v6

    move-wide v6, v15

    move-object/from16 v16, v42

    move-object/from16 v15, v48

    move-object/from16 v2, p1

    goto/16 :goto_1f

    :pswitch_3
    move-object/from16 v38, v3

    iget v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->I$0:I

    iget-wide v3, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$6:J

    iget-boolean v5, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->Z$1:Z

    iget-wide v6, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$5:J

    iget-wide v11, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$4:J

    iget-wide v13, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$3:J

    move-wide v15, v3

    iget-wide v3, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$2:J

    move-wide/from16 v17, v3

    iget-wide v3, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$1:J

    move-wide/from16 v19, v3

    iget-wide v3, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$0:J

    iget-boolean v8, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->Z$0:Z

    move/from16 v22, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$19:Ljava/lang/Object;

    check-cast v1, Lkotlinx/coroutines/CompletableDeferred;

    move-object/16 p1, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$18:Ljava/lang/Object;

    check-cast v1, Landroid/os/ParcelFileDescriptor;

    move-object/16 p2, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$17:Ljava/lang/Object;

    check-cast v1, Ljava/io/Closeable;

    move-object/from16 v23, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$16:Ljava/lang/Object;

    check-cast v1, Landroid/os/ParcelFileDescriptor;

    move-object/from16 v24, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$15:Ljava/lang/Object;

    check-cast v1, Ljava/util/List;

    move-object/from16 v26, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$14:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$ObjectRef;

    move-object/from16 v34, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$13:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$ObjectRef;

    move-object/from16 v36, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$12:Ljava/lang/Object;

    check-cast v1, Lkotlinx/coroutines/CompletableDeferred;

    move-object/from16 v39, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$11:Ljava/lang/Object;

    check-cast v1, Ljava/io/File;

    move-object/from16 v40, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$10:Ljava/lang/Object;

    check-cast v1, Ljava/lang/String;

    move-object/from16 v41, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$9:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$BooleanRef;

    move-object/from16 v42, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$8:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$ObjectRef;

    move-object/from16 v43, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$7:Ljava/lang/Object;

    check-cast v1, Landroid/net/Uri;

    move-object/from16 v44, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$6:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$BooleanRef;

    move-object/from16 v45, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$5:Ljava/lang/Object;

    check-cast v1, Ljava/io/File;

    move-object/from16 v46, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$4:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$ObjectRef;

    move-object/from16 v47, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$3:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$ObjectRef;

    move-object/from16 v48, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$2:Ljava/lang/Object;

    check-cast v1, Lcom/bachatas4/android/data/InstallJobStore;

    move-object/from16 v49, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$1:Ljava/lang/Object;

    check-cast v1, Ljava/lang/String;

    move-object/from16 v50, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$0:Ljava/lang/Object;

    check-cast v1, Ljava/lang/String;

    :try_start_3
    invoke-static {v0}, Lkotlin/ResultKt;->throwOnFailure(Ljava/lang/Object;)V
    :try_end_3
    .catchall {:try_start_3 .. :try_end_3} :catchall_2

    move-wide/from16 v212, v3

    move-wide/from16 v220, v6

    move/from16 v223, v8

    move-object/from16 v211, v10

    move-wide/from16 v225, v11

    move-wide/from16 v227, v13

    move-wide/from16 v218, v15

    move-wide/from16 v216, v17

    move-wide/from16 v214, v19

    move-object/from16 v4, v23

    move-object/from16 v18, v26

    move-object/from16 v192, v27

    move-object/from16 v82, v28

    move-object/from16 v83, v29

    move-object/from16 v84, v30

    move-object/from16 v85, v31

    move-object/from16 v210, v33

    move-object/from16 v12, v36

    move-object/from16 v7, v38

    move-object/from16 v17, v39

    move-object/from16 v10, v40

    move-object/from16 v16, v42

    move-object/from16 v11, v43

    move-object/from16 v26, v44

    move-object/from16 v3, v47

    move-object/from16 v15, v48

    move-object/from16 v222, v49

    move-object/from16 v224, v50

    const/16 v19, 0x0

    const/16 v54, 0x0

    move-object/from16 v13, p1

    move-object/from16 v23, p2

    move-object v8, v1

    move-object v14, v2

    move v6, v5

    move-object/from16 v43, v9

    move/from16 v2, v22

    move-object/from16 v5, v41

    move-object/from16 v9, v46

    move-object/from16 v1, p0

    goto/16 :goto_1d

    :catchall_2
    move-exception v0

    move-object/from16 v2, p0

    move-object v3, v0

    move-object/from16 v43, v9

    move-object v12, v10

    move-object/from16 v4, v23

    move-object/from16 v82, v28

    move-object/from16 v15, v29

    move-object/from16 v1, v30

    move-object/from16 v5, v45

    move-object/from16 v9, v46

    move-object/from16 v7, v47

    move-object/from16 v8, v49

    move-object/from16 v11, v50

    goto/16 :goto_46

    :pswitch_4
    move-object/from16 v38, v3

    iget v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->I$2:I

    iget v3, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->I$1:I

    iget v4, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->I$0:I

    iget-wide v5, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$6:J

    iget-boolean v7, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->Z$1:Z

    iget-wide v11, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$5:J

    iget-wide v13, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$4:J

    move v8, v3

    move v15, v4

    iget-wide v3, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$3:J

    move-wide/from16 v16, v3

    iget-wide v3, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$2:J

    move-wide/from16 v18, v3

    iget-wide v3, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$1:J

    move-wide/from16 v22, v3

    iget-wide v3, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$0:J

    move/from16 v20, v1

    iget-boolean v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->Z$0:Z

    move/from16 v24, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$20:Ljava/lang/Object;

    check-cast v1, Ljava/lang/String;

    move-object/16 p1, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$19:Ljava/lang/Object;

    check-cast v1, Ljava/util/Iterator;

    move-object/16 p2, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$18:Ljava/lang/Object;

    check-cast v1, Landroid/os/ParcelFileDescriptor;

    move-object/from16 v34, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$17:Ljava/lang/Object;

    check-cast v1, Ljava/io/Closeable;

    move-object/from16 v36, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$16:Ljava/lang/Object;

    check-cast v1, Landroid/os/ParcelFileDescriptor;

    move-object/from16 v39, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$15:Ljava/lang/Object;

    check-cast v1, Ljava/util/List;

    move-object/from16 v40, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$14:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$ObjectRef;

    move-object/from16 v41, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$13:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$ObjectRef;

    move-object/from16 v42, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$12:Ljava/lang/Object;

    check-cast v1, Lkotlinx/coroutines/CompletableDeferred;

    move-object/from16 v43, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$11:Ljava/lang/Object;

    check-cast v1, Ljava/io/File;

    move-object/from16 v44, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$10:Ljava/lang/Object;

    check-cast v1, Ljava/lang/String;

    move-object/from16 v45, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$9:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$BooleanRef;

    move-object/from16 v46, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$8:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$ObjectRef;

    move-object/from16 v47, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$7:Ljava/lang/Object;

    check-cast v1, Landroid/net/Uri;

    move-object/from16 v48, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$6:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$BooleanRef;

    move-object/from16 v49, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$5:Ljava/lang/Object;

    check-cast v1, Ljava/io/File;

    move-object/from16 v50, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$4:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$ObjectRef;

    move-object/from16 v51, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$3:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$ObjectRef;

    move-object/from16 v52, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$2:Ljava/lang/Object;

    check-cast v1, Lcom/bachatas4/android/data/InstallJobStore;

    move-object/from16 v53, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$1:Ljava/lang/Object;

    check-cast v1, Ljava/lang/String;

    move-object/from16 v54, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$0:Ljava/lang/Object;

    check-cast v1, Ljava/lang/String;

    :try_start_4
    invoke-static {v0}, Lkotlin/ResultKt;->throwOnFailure(Ljava/lang/Object;)V
    :try_end_4
    .catchall {:try_start_4 .. :try_end_4} :catchall_3

    move-wide/from16 v180, v3

    move-wide/from16 v174, v5

    move v6, v8

    move-wide/from16 v176, v11

    move-wide/from16 v178, v13

    move-wide/from16 v172, v16

    move-wide/from16 v170, v18

    move-wide/from16 v168, v22

    move/from16 v117, v24

    move-object/from16 v80, v26

    move-object/from16 v82, v28

    move-object/from16 v83, v29

    move-object/from16 v84, v30

    move-object/from16 v85, v31

    move-object/from16 v86, v33

    move-object/from16 v23, v34

    move-object/from16 v21, v36

    move-object/from16 v28, v39

    move-object/from16 v18, v40

    move-object/from16 v4, v42

    move-object/from16 v17, v43

    move-object/from16 v16, v46

    move-object/from16 v12, v47

    move-object/from16 v26, v48

    move-object/from16 v5, v49

    move-object/from16 v29, v51

    move-object/from16 v11, v52

    move-object/from16 v49, v53

    move-object/from16 v14, v54

    const/16 v19, 0x0

    const/16 v54, 0x0

    move-object/from16 v3, p1

    move-object/from16 v8, p2

    move-object v13, v1

    move-object/from16 v40, v2

    move-object/from16 v43, v9

    move/from16 v2, v20

    move-object/from16 v1, v38

    move/from16 v20, v7

    move-object/from16 v7, v44

    move-object/from16 v44, v10

    move-object/from16 v10, v41

    move-object/from16 v41, v45

    goto/16 :goto_13

    :catchall_3
    move-exception v0

    move-object/from16 v2, p0

    move-object v3, v0

    move-object/from16 v43, v9

    move-object v12, v10

    move-object/from16 v82, v28

    move-object/from16 v15, v29

    move-object/from16 v1, v30

    move-object/from16 v4, v36

    move-object/from16 v5, v49

    move-object/from16 v9, v50

    move-object/from16 v7, v51

    move-object/from16 v8, v53

    move-object/from16 v11, v54

    goto/16 :goto_46

    :pswitch_5
    move-object/from16 v38, v3

    iget-wide v3, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$6:J

    iget-boolean v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->Z$1:Z

    iget-wide v6, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$5:J

    iget-wide v11, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$4:J

    iget-wide v13, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$3:J

    move-wide v15, v3

    iget-wide v3, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$2:J

    move-wide/from16 v17, v3

    iget-wide v3, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$1:J

    move-wide/from16 v39, v3

    iget-wide v3, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$0:J

    iget-boolean v8, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->Z$0:Z

    move/from16 v19, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$16:Ljava/lang/Object;

    check-cast v1, Ljava/io/File;

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$15:Ljava/lang/Object;

    check-cast v1, Ljava/util/List;

    move-object/16 p1, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$14:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$ObjectRef;

    move-object/16 p2, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$13:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$ObjectRef;

    move-object/from16 v24, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$12:Ljava/lang/Object;

    check-cast v1, Lkotlinx/coroutines/CompletableDeferred;

    move-object/from16 v34, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$11:Ljava/lang/Object;

    check-cast v1, Ljava/io/File;

    move-object/from16 v36, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$10:Ljava/lang/Object;

    check-cast v1, Ljava/lang/String;

    move-object/from16 v41, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$9:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$BooleanRef;

    move-object/from16 v42, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$8:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$ObjectRef;

    move-object/from16 v43, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$7:Ljava/lang/Object;

    check-cast v1, Landroid/net/Uri;

    move-object/from16 v44, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$6:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$BooleanRef;

    move-object/from16 v45, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$5:Ljava/lang/Object;

    check-cast v1, Ljava/io/File;

    move-object/from16 v46, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$4:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$ObjectRef;

    move-object/from16 v47, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$3:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$ObjectRef;

    move-object/from16 v48, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$2:Ljava/lang/Object;

    check-cast v1, Lcom/bachatas4/android/data/InstallJobStore;

    move-object/from16 v49, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$1:Ljava/lang/Object;

    check-cast v1, Ljava/lang/String;

    move-object/from16 v50, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$0:Ljava/lang/Object;

    check-cast v1, Ljava/lang/String;

    :try_start_5
    invoke-static {v0}, Lkotlin/ResultKt;->throwOnFailure(Ljava/lang/Object;)V
    :try_end_5
    .catchall {:try_start_5 .. :try_end_5} :catchall_4

    move-object/from16 v59, v5

    move/from16 v117, v8

    move/from16 v0, v19

    move-object/from16 v66, v20

    move-object/from16 v8, v23

    move-object/from16 v23, v24

    move-object/from16 v80, v26

    move-object/from16 v82, v28

    move-object/from16 v83, v29

    move-object/from16 v84, v30

    move-object/from16 v85, v31

    move-object/from16 v86, v33

    move-object/from16 v19, v42

    move-object/from16 v31, v43

    move-object/from16 v29, v47

    const/16 v54, 0x0

    move-object/from16 v30, p2

    move-object/from16 v43, v9

    move-object v9, v10

    move-wide/from16 v20, v13

    move-wide/from16 v32, v17

    move-object/from16 v14, v25

    move-wide/from16 v24, v6

    move-wide/from16 v17, v11

    move-wide v12, v15

    move-object/from16 v16, v34

    move-object/from16 v7, v38

    move-wide/from16 v10, v39

    move-object/from16 v40, v2

    move-wide v5, v3

    move-object/from16 v2, v44

    move-object/from16 v4, v46

    move-object/from16 v3, p1

    goto/16 :goto_f

    :catchall_4
    move-exception v0

    move-object/from16 v1, p0

    move-object/from16 v43, v9

    move-object v12, v10

    move-object/from16 v11, v28

    move-object/from16 v15, v29

    move-object/from16 v9, v30

    move-object/from16 v13, v31

    move-object/from16 v4, v45

    move-object/from16 v8, v47

    move-object/from16 v3, v49

    move-object/from16 v2, v50

    goto/16 :goto_67

    :pswitch_6
    move-object/from16 v38, v3

    move-object v1, v4

    iget-wide v3, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$5:J

    move-wide v15, v3

    iget-wide v3, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$4:J

    move-wide/from16 v17, v3

    iget-wide v3, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$3:J

    move-wide/from16 v39, v3

    iget-wide v3, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$2:J

    move-wide/from16 v41, v3

    iget-wide v3, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$1:J

    move-wide/from16 v43, v3

    iget-wide v3, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$0:J

    iget-boolean v6, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->Z$0:Z

    iget-object v8, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$11:Ljava/lang/Object;

    check-cast v8, Lkotlinx/coroutines/CompletableDeferred;

    move-object/from16 v45, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$10:Ljava/lang/Object;

    check-cast v1, Ljava/io/File;

    move-object/16 p1, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$9:Ljava/lang/Object;

    check-cast v1, Ljava/lang/String;

    move-object/from16 v19, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$8:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$BooleanRef;

    move-object/from16 v46, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$7:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$ObjectRef;

    move-object/from16 v47, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$6:Ljava/lang/Object;

    check-cast v1, Landroid/net/Uri;

    move-object/from16 v48, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$5:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$BooleanRef;

    move-object/from16 v49, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$4:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$ObjectRef;

    move-object/from16 v50, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$3:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$ObjectRef;

    move-object/from16 v51, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$2:Ljava/lang/Object;

    check-cast v1, Lcom/bachatas4/android/data/InstallJobStore;

    move-object/from16 v52, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$1:Ljava/lang/Object;

    check-cast v1, Ljava/lang/String;

    move-object/from16 v53, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$0:Ljava/lang/Object;

    check-cast v1, Ljava/lang/String;

    :try_start_6
    invoke-static {v0}, Lkotlin/ResultKt;->throwOnFailure(Ljava/lang/Object;)V
    :try_end_6
    .catchall {:try_start_6 .. :try_end_6} :catchall_5

    move-object/from16 v75, p2

    move-object/from16 v59, v5

    move-object/from16 v57, v7

    move-object/from16 v90, v11

    move-object/from16 v71, v12

    move-object/from16 v70, v13

    move-object/from16 v69, v14

    move-object/from16 v66, v20

    move-object/from16 v77, v23

    move-object/from16 v79, v25

    move-object/from16 v80, v26

    move-object/from16 v82, v28

    move-object/from16 v83, v29

    move-object/from16 v84, v30

    move-object/from16 v85, v31

    move-object/from16 v86, v33

    move-object/from16 v73, v34

    move-object/from16 v72, v36

    move-wide/from16 v172, v39

    move-wide/from16 v170, v41

    move-wide/from16 v168, v43

    move-object/from16 v60, v45

    move-object/from16 v14, v46

    move-object/from16 v12, v47

    move-object/from16 v21, v48

    move-object/from16 v11, v53

    const/16 v54, 0x0

    move-object/from16 v13, p1

    move-object/from16 v40, v2

    move-object/from16 v43, v9

    move-object/from16 v44, v10

    move-object/from16 v9, v24

    move-object/from16 v2, v52

    move v10, v6

    move-wide v6, v15

    move-object/from16 v15, v51

    move-object/from16 v16, v8

    move-object/from16 v8, v50

    move-object/16 v256, v1

    move-object/from16 v1, p0

    move-wide/16 v257, v3

    move-object/from16 v3, v256

    move-wide/from16 v4, v17

    move-object/from16 v18, v19

    move-object/from16 v17, v49

    move-wide/from16 v19, v257

    goto/16 :goto_d

    :catchall_5
    move-exception v0

    move-object/from16 v1, p0

    move-object/from16 v43, v9

    move-object v12, v10

    move-object/from16 v11, v28

    move-object/from16 v15, v29

    move-object/from16 v9, v30

    move-object/from16 v13, v31

    move-object/from16 v4, v49

    move-object/from16 v8, v50

    move-object/from16 v3, v52

    move-object/from16 v2, v53

    goto/16 :goto_66

    :pswitch_7
    move-object/from16 v38, v3

    move-object/from16 v45, v4

    iget-boolean v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->Z$0:Z

    iget-object v3, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$11:Ljava/lang/Object;

    check-cast v3, Lkotlin/jvm/internal/Ref$ObjectRef;

    iget-object v4, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$10:Ljava/lang/Object;

    check-cast v4, Landroid/os/ParcelFileDescriptor;

    iget-object v4, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$9:Ljava/lang/Object;

    check-cast v4, Ljava/io/Closeable;

    iget-object v6, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$8:Ljava/lang/Object;

    check-cast v6, Lkotlin/jvm/internal/Ref$BooleanRef;

    iget-object v8, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$7:Ljava/lang/Object;

    check-cast v8, Lkotlin/jvm/internal/Ref$ObjectRef;

    iget-object v15, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$6:Ljava/lang/Object;

    check-cast v15, Landroid/net/Uri;

    move/from16 v17, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$5:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$BooleanRef;

    move-object/16 p1, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$4:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$ObjectRef;

    move-object/from16 v19, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$3:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$ObjectRef;

    move-object/from16 v39, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$2:Ljava/lang/Object;

    check-cast v1, Lcom/bachatas4/android/data/InstallJobStore;

    move-object/from16 v40, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$1:Ljava/lang/Object;

    check-cast v1, Ljava/lang/String;

    move-object/from16 v41, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$0:Ljava/lang/Object;

    check-cast v1, Ljava/lang/String;

    :try_start_7
    invoke-static {v0}, Lkotlin/ResultKt;->throwOnFailure(Ljava/lang/Object;)V
    :try_end_7
    .catchall {:try_start_7 .. :try_end_7} :catchall_6

    move-object/from16 v75, p2

    move-object/from16 v59, v5

    move-object/from16 v57, v7

    move-object/from16 v43, v9

    move-object/from16 v90, v11

    move-object/from16 v71, v12

    move-object/from16 v70, v13

    move-object/from16 v69, v14

    move-object/from16 v74, v16

    move-object/from16 v62, v18

    move-object/from16 v66, v20

    move-object/from16 v76, v22

    move-object/from16 v77, v23

    move-object/from16 v78, v24

    move-object/from16 v79, v25

    move-object/from16 v80, v26

    move-object/from16 v81, v27

    move-object/from16 v82, v28

    move-object/from16 v83, v29

    move-object/from16 v84, v30

    move-object/from16 v85, v31

    move-object/from16 v86, v33

    move-object/from16 v73, v34

    move-object/from16 v72, v36

    move-object/from16 v7, v38

    move-object/from16 v12, v40

    move-object/from16 v14, v41

    move-object/from16 v60, v45

    const/16 v54, 0x0

    move-object/from16 v9, p0

    move-object v13, v1

    move-object v5, v4

    move-object v11, v10

    move-object/from16 v1, p1

    move-object v10, v2

    move-object v4, v3

    move-object v3, v8

    move-object v2, v15

    move-object/from16 v15, v19

    move-object/from16 v8, v39

    goto/16 :goto_6

    :catchall_6
    move-exception v0

    move-object/from16 v1, p0

    move-object/from16 v6, p1

    move-object v2, v0

    move-object/from16 v43, v9

    move-object v12, v10

    move-object/from16 v5, v19

    move-object/from16 v11, v28

    move-object/from16 v15, v29

    move-object/from16 v9, v30

    move-object/from16 v13, v31

    move-object/from16 v16, v40

    move-object/from16 v19, v41

    goto/16 :goto_5c

    :pswitch_8
    move-object/from16 v38, v3

    move-object/from16 v45, v4

    iget-boolean v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->Z$0:Z

    iget-object v3, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$8:Ljava/lang/Object;

    check-cast v3, Lkotlin/jvm/internal/Ref$BooleanRef;

    iget-object v4, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$7:Ljava/lang/Object;

    check-cast v4, Lkotlin/jvm/internal/Ref$ObjectRef;

    iget-object v8, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$6:Ljava/lang/Object;

    check-cast v8, Landroid/net/Uri;

    iget-object v15, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$5:Ljava/lang/Object;

    check-cast v15, Lkotlin/jvm/internal/Ref$BooleanRef;

    move/from16 v39, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$4:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$ObjectRef;

    move-object/16 p1, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$3:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$ObjectRef;

    move-object/from16 v40, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$2:Ljava/lang/Object;

    check-cast v1, Lcom/bachatas4/android/data/InstallJobStore;

    move-object/from16 v41, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$1:Ljava/lang/Object;

    check-cast v1, Ljava/lang/String;

    move-object/from16 v42, v1

    iget-object v1, v2, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$0:Ljava/lang/Object;

    check-cast v1, Ljava/lang/String;

    :try_start_8
    invoke-static {v0}, Lkotlin/ResultKt;->throwOnFailure(Ljava/lang/Object;)V
    :try_end_8
    .catch Ljava/lang/SecurityException; {:try_start_8 .. :try_end_8} :catch_1
    .catch Ljava/lang/Exception; {:try_start_8 .. :try_end_8} :catch_0
    .catchall {:try_start_8 .. :try_end_8} :catchall_7

    move-object/from16 v75, p2

    move-object/from16 v59, v5

    move-object/from16 v58, v6

    move-object/from16 v57, v7

    move-object v7, v8

    move-object/from16 v43, v9

    move-object/from16 v90, v11

    move-object/from16 v71, v12

    move-object/from16 v70, v13

    move-object/from16 v69, v14

    move-object/from16 v74, v16

    move-object/from16 v67, v17

    move-object/from16 v62, v18

    move-object/from16 v61, v19

    move-object/from16 v66, v20

    move-object/from16 v76, v22

    move-object/from16 v77, v23

    move-object/from16 v78, v24

    move-object/from16 v79, v25

    move-object/from16 v80, v26

    move-object/from16 v81, v27

    move-object/from16 v82, v28

    move-object/from16 v83, v29

    move-object/from16 v84, v30

    move-object/from16 v85, v31

    move-object/from16 v86, v33

    move-object/from16 v73, v34

    move-object/from16 v72, v36

    move-object/from16 v14, v38

    move/from16 v12, v39

    move-object/from16 v60, v45

    const/16 v54, 0x0

    move-object/from16 v9, p0

    move-object/from16 v5, p1

    move-object v13, v3

    move-object v6, v4

    move-object v11, v10

    move-object/from16 v4, v40

    move-object/from16 v3, v41

    move-object v10, v2

    move-object/from16 v2, v42

    goto/16 :goto_5

    :catchall_7
    move-exception v0

    move-object/from16 v1, p0

    move-object/from16 v8, p1

    move-object/from16 v43, v9

    move-object v12, v10

    move-object v4, v15

    move-object/from16 v11, v28

    move-object/from16 v15, v29

    move-object/from16 v9, v30

    move-object/from16 v13, v31

    move-object/from16 v3, v41

    move-object/from16 v2, v42

    goto/16 :goto_66

    :catch_0
    move-exception v0

    move-object/from16 v1, p0

    move-object/from16 v4, p1

    move-object/from16 v43, v9

    move-object v12, v10

    move-object v6, v15

    move-object/from16 v11, v28

    move-object/from16 v15, v29

    move-object/from16 v9, v30

    move-object/from16 v13, v31

    move-object/from16 v3, v41

    move-object/from16 v2, v42

    goto/16 :goto_60

    :catch_1
    move-exception v0

    move-object/from16 v1, p0

    move-object/from16 v4, p1

    move-object/from16 v43, v9

    move-object v12, v10

    move-object v6, v15

    move-object/from16 v11, v28

    move-object/from16 v15, v29

    move-object/from16 v9, v30

    move-object/from16 v13, v31

    move-object/from16 v3, v41

    move-object/from16 v2, v42

    goto/16 :goto_61

    :pswitch_9
    move-object/from16 v38, v3

    move-object/from16 v45, v4

    invoke-static {v0}, Lkotlin/ResultKt;->throwOnFailure(Ljava/lang/Object;)V

    .line 322
    new-instance v0, Ljava/lang/StringBuilder;

    const-string v1, "pkg import prepare uri="

    invoke-direct {v0, v1}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v0, v8}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    invoke-static {v10, v0}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    move-object v1, v6

    const/4 v6, 0x6

    move-object v3, v7

    const/4 v7, 0x0

    move-object v4, v2

    .line 323
    const-string v2, "Validating package\u2026"

    move-object/from16 v39, v3

    const/4 v3, 0x0

    move-object/from16 v40, v4

    const/4 v4, 0x0

    move-object/from16 v41, v5

    const/4 v5, 0x1

    move-object/from16 v58, v1

    move-object/from16 v62, v18

    move-object/from16 v61, v19

    move-object/from16 v56, v38

    move-object/from16 v57, v39

    move-object/from16 v55, v40

    move-object/from16 v59, v41

    move-object/from16 v60, v45

    move-object/from16 v1, p0

    invoke-static/range {v1 .. v7}, Lcom/bachatas4/android/service/ImportService;->updateNotification$default(Lcom/bachatas4/android/service/ImportService;Ljava/lang/String;IIZILjava/lang/Object;)V

    .line 324
    invoke-static {}, Ljava/util/UUID;->randomUUID()Ljava/util/UUID;

    move-result-object v0

    invoke-virtual {v0}, Ljava/util/UUID;->toString()Ljava/lang/String;

    move-result-object v2

    const-string v0, "toString(...)"

    invoke-static {v2, v0}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullExpressionValue(Ljava/lang/Object;Ljava/lang/String;)V

    .line 325
    new-instance v1, Lcom/bachatas4/android/data/InstallJobStore;

    invoke-virtual/range {p0 .. p0}, Lcom/bachatas4/android/service/ImportService;->getFilesDir()Ljava/io/File;

    move-result-object v0

    invoke-static {v0, v9}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullExpressionValue(Ljava/lang/Object;Ljava/lang/String;)V

    invoke-direct {v1, v0}, Lcom/bachatas4/android/data/InstallJobStore;-><init>(Ljava/io/File;)V

    .line 326
    new-instance v3, Lkotlin/jvm/internal/Ref$ObjectRef;

    invoke-direct {v3}, Lkotlin/jvm/internal/Ref$ObjectRef;-><init>()V

    new-instance v0, Lcom/bachatas4/android/data/InstallJob;

    .line 331
    invoke-static {}, Ljava/lang/System;->currentTimeMillis()J

    move-result-wide v18

    move-object/from16 v4, v20

    const/4 v5, 0x2

    .line 332
    invoke-static {}, Ljava/lang/System;->currentTimeMillis()J

    move-result-wide v20

    move-object/from16 v6, v24

    const v24, 0x33fe1

    move-object/from16 v7, v25

    const/16 v25, 0x0

    move-object/from16 v38, v1

    const/4 v1, 0x0

    move-object/from16 v39, v3

    .line 326
    const-string v3, "SELECTED"

    move-object/from16 v40, v4

    const-string v4, "pkg"

    move-object/from16 v41, v6

    const/4 v6, 0x0

    move-object/from16 v42, v7

    const/4 v7, 0x0

    const/4 v8, 0x0

    move-object/from16 v43, v9

    const/4 v9, 0x0

    move-object/from16 v44, v10

    const/4 v10, 0x0

    move-object/from16 v45, v11

    const/4 v11, 0x0

    move-object/from16 v47, v12

    move-object/from16 v46, v13

    const-wide/16 v12, 0x0

    move-object/from16 v49, v14

    move-object/from16 v48, v15

    const-wide/16 v14, 0x0

    move-object/from16 v51, v16

    move-object/from16 v50, v17

    const-wide/16 v16, 0x0

    move-object/from16 v52, v22

    const/16 v22, 0x0

    move-object/from16 v53, v23

    const/16 v23, 0x0

    move-object/from16 v5, p1

    move-object/from16 v75, p2

    move-object/from16 v80, v26

    move-object/from16 v81, v27

    move-object/from16 v82, v28

    move-object/from16 v83, v29

    move-object/from16 v84, v30

    move-object/from16 v85, v31

    move-object/from16 v86, v33

    move-object/from16 v73, v34

    move-object/from16 v72, v36

    move-object/from16 v64, v38

    move-object/from16 v65, v39

    move-object/from16 v66, v40

    move-object/from16 v78, v41

    move-object/from16 v79, v42

    move-object/from16 v87, v43

    move-object/from16 v89, v44

    move-object/from16 v90, v45

    move-object/from16 v70, v46

    move-object/from16 v71, v47

    move-object/from16 v68, v48

    move-object/from16 v69, v49

    move-object/from16 v67, v50

    move-object/from16 v74, v51

    move-object/from16 v76, v52

    move-object/from16 v77, v53

    const/16 v54, 0x0

    invoke-direct/range {v0 .. v25}, Lcom/bachatas4/android/data/InstallJob;-><init>(ILjava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;ZLjava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;JJJJJLjava/lang/String;Ljava/lang/String;ILkotlin/jvm/internal/DefaultConstructorMarker;)V

    move-object/from16 v1, v65

    iput-object v0, v1, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    .line 334
    iget-object v0, v1, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v0, Lcom/bachatas4/android/data/InstallJob;

    move-object/from16 v3, v64

    invoke-virtual {v3, v0}, Lcom/bachatas4/android/data/InstallJobStore;->create(Lcom/bachatas4/android/data/InstallJob;)V

    .line 335
    new-instance v4, Lkotlin/jvm/internal/Ref$ObjectRef;

    invoke-direct {v4}, Lkotlin/jvm/internal/Ref$ObjectRef;-><init>()V

    .line 337
    new-instance v6, Lkotlin/jvm/internal/Ref$BooleanRef;

    invoke-direct {v6}, Lkotlin/jvm/internal/Ref$BooleanRef;-><init>()V

    .line 339
    :try_start_9
    sget-object v0, Lcom/bachatas4/android/data/ImportManager;->INSTANCE:Lcom/bachatas4/android/data/ImportManager;

    new-instance v7, Lcom/bachatas4/android/data/ImportProgress$Validating;

    const-string v8, "pkg"

    invoke-direct {v7, v5, v8}, Lcom/bachatas4/android/data/ImportProgress$Validating;-><init>(Ljava/lang/String;Ljava/lang/String;)V

    check-cast v7, Lcom/bachatas4/android/data/ImportProgress;

    invoke-virtual {v0, v7}, Lcom/bachatas4/android/data/ImportManager;->update(Lcom/bachatas4/android/data/ImportProgress;)V

    .line 340
    iget-object v0, v1, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    move-object v7, v0

    check-cast v7, Lcom/bachatas4/android/data/InstallJob;

    const-string v10, "VALIDATING"

    invoke-static {}, Ljava/lang/System;->currentTimeMillis()J

    move-result-wide v27

    const v31, 0x37ffb

    const/16 v32, 0x0

    const/4 v8, 0x0

    const/4 v9, 0x0

    const/4 v11, 0x0

    const/4 v12, 0x0

    const/4 v13, 0x0

    const/4 v14, 0x0

    const/4 v15, 0x0

    const/16 v16, 0x0

    const/16 v17, 0x0

    const/16 v18, 0x0

    const-wide/16 v19, 0x0

    const-wide/16 v21, 0x0

    const-wide/16 v23, 0x0

    const-wide/16 v25, 0x0

    const/16 v29, 0x0

    const/16 v30, 0x0

    invoke-static/range {v7 .. v32}, Lcom/bachatas4/android/data/InstallJob;->copy$default(Lcom/bachatas4/android/data/InstallJob;ILjava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;ZLjava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;JJJJJLjava/lang/String;Ljava/lang/String;ILjava/lang/Object;)Lcom/bachatas4/android/data/InstallJob;

    move-result-object v0

    iput-object v0, v1, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    .line 341
    iget-object v0, v1, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v0, Lcom/bachatas4/android/data/InstallJob;

    invoke-virtual {v3, v0}, Lcom/bachatas4/android/data/InstallJobStore;->update(Lcom/bachatas4/android/data/InstallJob;)V

    .line 343
    sget-object v0, Lcom/bachatas4/android/data/InstallValidator;->INSTANCE:Lcom/bachatas4/android/data/InstallValidator;

    invoke-virtual/range {p0 .. p0}, Lcom/bachatas4/android/service/ImportService;->getFilesDir()Ljava/io/File;

    move-result-object v7
    :try_end_9
    .catchall {:try_start_9 .. :try_end_9} :catchall_69

    move-object/from16 v8, v87

    :try_start_a
    invoke-static {v7, v8}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullExpressionValue(Ljava/lang/Object;Ljava/lang/String;)V

    invoke-virtual {v0, v7}, Lcom/bachatas4/android/data/InstallValidator;->checkWritableGamesDir(Ljava/io/File;)Lcom/bachatas4/android/data/InstallErrorCode;

    move-result-object v0

    if-nez v0, :cond_35

    .line 347
    invoke-static {v5}, Landroid/net/Uri;->parse(Ljava/lang/String;)Landroid/net/Uri;

    move-result-object v7
    :try_end_a
    .catchall {:try_start_a .. :try_end_a} :catchall_68

    .line 348
    :try_start_b
    sget-object v0, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;
    :try_end_b
    .catchall {:try_start_b .. :try_end_b} :catchall_a

    move-object/from16 v9, p0

    :try_start_c
    move-object v0, v9

    check-cast v0, Lcom/bachatas4/android/service/ImportService;

    .line 349
    invoke-virtual {v9}, Lcom/bachatas4/android/service/ImportService;->getContentResolver()Landroid/content/ContentResolver;

    move-result-object v0
    :try_end_c
    .catchall {:try_start_c .. :try_end_c} :catchall_9

    const/4 v10, 0x1

    :try_start_d
    invoke-virtual {v0, v7, v10}, Landroid/content/ContentResolver;->takePersistableUriPermission(Landroid/net/Uri;I)V

    .line 350
    invoke-static {v10}, Lkotlin/coroutines/jvm/internal/Boxing;->boxBoolean(Z)Ljava/lang/Boolean;

    move-result-object v0

    .line 348
    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v0
    :try_end_d
    .catchall {:try_start_d .. :try_end_d} :catchall_8

    goto :goto_3

    :catchall_8
    move-exception v0

    goto :goto_2

    :catchall_9
    move-exception v0

    const/4 v10, 0x1

    goto :goto_2

    :catchall_a
    move-exception v0

    const/4 v10, 0x1

    move-object/from16 v9, p0

    :goto_2
    :try_start_e
    sget-object v11, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    invoke-static {v0}, Lkotlin/ResultKt;->createFailure(Ljava/lang/Throwable;)Ljava/lang/Object;

    move-result-object v0

    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v0

    .line 351
    :goto_3
    invoke-static {v0}, Lkotlin/Result;->exceptionOrNull-impl(Ljava/lang/Object;)Ljava/lang/Throwable;

    move-result-object v11

    if-nez v11, :cond_2

    move-object/from16 v11, v89

    goto :goto_4

    .line 352
    :cond_2
    invoke-virtual {v11}, Ljava/lang/Throwable;->getMessage()Ljava/lang/String;

    move-result-object v0

    new-instance v11, Ljava/lang/StringBuilder;

    move-object/from16 v12, v68

    invoke-direct {v11, v12}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v11, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0
    :try_end_e
    .catchall {:try_start_e .. :try_end_e} :catchall_67

    move-object/from16 v11, v89

    :try_start_f
    invoke-static {v11, v0}, Landroid/util/Log;->w(Ljava/lang/String;Ljava/lang/String;)I

    .line 353
    invoke-static/range {v54 .. v54}, Lkotlin/coroutines/jvm/internal/Boxing;->boxBoolean(Z)Ljava/lang/Boolean;

    move-result-object v0

    .line 351
    :goto_4
    check-cast v0, Ljava/lang/Boolean;

    invoke-virtual {v0}, Ljava/lang/Boolean;->booleanValue()Z

    move-result v18

    .line 355
    iget-object v0, v1, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    move-object v12, v0

    check-cast v12, Lcom/bachatas4/android/data/InstallJob;

    invoke-static {}, Ljava/lang/System;->currentTimeMillis()J

    move-result-wide v32

    const v36, 0x37fdf

    const/16 v37, 0x0

    const/4 v13, 0x0

    const/4 v14, 0x0

    const/4 v15, 0x0

    const/16 v16, 0x0

    const/16 v17, 0x0

    const/16 v19, 0x0

    const/16 v20, 0x0

    const/16 v21, 0x0

    const/16 v22, 0x0

    const/16 v23, 0x0

    const-wide/16 v24, 0x0

    const-wide/16 v26, 0x0

    const-wide/16 v28, 0x0

    const-wide/16 v30, 0x0

    const/16 v34, 0x0

    const/16 v35, 0x0

    invoke-static/range {v12 .. v37}, Lcom/bachatas4/android/data/InstallJob;->copy$default(Lcom/bachatas4/android/data/InstallJob;ILjava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;ZLjava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;JJJJJLjava/lang/String;Ljava/lang/String;ILjava/lang/Object;)Lcom/bachatas4/android/data/InstallJob;

    move-result-object v0

    move/from16 v12, v18

    iput-object v0, v1, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    .line 356
    iget-object v0, v1, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v0, Lcom/bachatas4/android/data/InstallJob;

    invoke-virtual {v3, v0}, Lcom/bachatas4/android/data/InstallJobStore;->update(Lcom/bachatas4/android/data/InstallJob;)V

    .line 362
    new-instance v0, Lkotlin/jvm/internal/Ref$ObjectRef;

    invoke-direct {v0}, Lkotlin/jvm/internal/Ref$ObjectRef;-><init>()V

    .line 363
    new-instance v13, Lkotlin/jvm/internal/Ref$BooleanRef;

    invoke-direct {v13}, Lkotlin/jvm/internal/Ref$BooleanRef;-><init>()V
    :try_end_f
    .catchall {:try_start_f .. :try_end_f} :catchall_66

    .line 365
    :try_start_10
    invoke-static {}, Lkotlinx/coroutines/Dispatchers;->getIO()Lkotlinx/coroutines/CoroutineDispatcher;

    move-result-object v14

    check-cast v14, Lkotlin/coroutines/CoroutineContext;

    new-instance v15, Lcom/bachatas4/android/service/ImportService$runPkgImport$3;

    const/4 v10, 0x0

    invoke-direct {v15, v9, v7, v10}, Lcom/bachatas4/android/service/ImportService$runPkgImport$3;-><init>(Lcom/bachatas4/android/service/ImportService;Landroid/net/Uri;Lkotlin/coroutines/Continuation;)V

    check-cast v15, Lkotlin/jvm/functions/Function2;

    move-object/from16 v10, v55

    iput-object v5, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$0:Ljava/lang/Object;

    iput-object v2, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$1:Ljava/lang/Object;

    iput-object v3, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$2:Ljava/lang/Object;

    iput-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$3:Ljava/lang/Object;

    iput-object v4, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$4:Ljava/lang/Object;

    iput-object v6, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$5:Ljava/lang/Object;

    iput-object v7, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$6:Ljava/lang/Object;

    iput-object v0, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$7:Ljava/lang/Object;

    iput-object v13, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$8:Ljava/lang/Object;

    iput-boolean v12, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->Z$0:Z

    move-object/from16 v39, v1

    const/4 v1, 0x1

    iput v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->label:I

    invoke-static {v14, v15, v10}, Lkotlinx/coroutines/BuildersKt;->withContext(Lkotlin/coroutines/CoroutineContext;Lkotlin/jvm/functions/Function2;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;

    move-result-object v1
    :try_end_10
    .catch Ljava/lang/SecurityException; {:try_start_10 .. :try_end_10} :catch_9
    .catch Ljava/lang/Exception; {:try_start_10 .. :try_end_10} :catch_8
    .catchall {:try_start_10 .. :try_end_10} :catchall_66

    move-object/from16 v14, v56

    if-ne v1, v14, :cond_3

    move-object v7, v14

    goto/16 :goto_35

    :cond_3
    move-object v15, v6

    move-object/from16 v43, v8

    move-object v6, v0

    move-object v0, v1

    move-object v1, v5

    move-object v5, v4

    move-object/from16 v4, v39

    .line 321
    :goto_5
    :try_start_11
    move-object v8, v0

    check-cast v8, Ljava/io/Closeable;
    :try_end_11
    .catch Ljava/lang/SecurityException; {:try_start_11 .. :try_end_11} :catch_7
    .catch Ljava/lang/Exception; {:try_start_11 .. :try_end_11} :catch_6
    .catchall {:try_start_11 .. :try_end_11} :catchall_64

    .line 368
    :try_start_12
    move-object v0, v8

    check-cast v0, Landroid/os/ParcelFileDescriptor;

    move-object/from16 v16, v6

    move-object/from16 v17, v7

    .line 369
    invoke-virtual {v0}, Landroid/os/ParcelFileDescriptor;->getStatSize()J

    move-result-wide v6

    move-object/from16 v38, v14

    new-instance v14, Ljava/lang/StringBuilder;

    move/from16 v18, v12

    move-object/from16 v12, v67

    invoke-direct {v14, v12}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v14, v6, v7}, Ljava/lang/StringBuilder;->append(J)Ljava/lang/StringBuilder;

    move-result-object v6

    invoke-virtual {v6}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v6

    invoke-static {v11, v6}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    .line 370
    invoke-direct {v9, v0}, Lcom/bachatas4/android/service/ImportService;->isOpenFdSeekable(Landroid/os/ParcelFileDescriptor;)Z

    move-result v6

    iput-boolean v6, v13, Lkotlin/jvm/internal/Ref$BooleanRef;->element:Z

    .line 371
    iget-boolean v6, v13, Lkotlin/jvm/internal/Ref$BooleanRef;->element:Z

    new-instance v7, Ljava/lang/StringBuilder;

    move-object/from16 v12, v58

    invoke-direct {v7, v12}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v7, v6}, Ljava/lang/StringBuilder;->append(Z)Ljava/lang/StringBuilder;

    move-result-object v6

    invoke-virtual {v6}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v6

    invoke-static {v11, v6}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    .line 372
    invoke-virtual {v0}, Landroid/os/ParcelFileDescriptor;->getFd()I

    move-result v6

    new-instance v7, Ljava/lang/StringBuilder;

    move-object/from16 v12, v61

    invoke-direct {v7, v12}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v7, v6}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    move-result-object v6

    invoke-virtual {v6}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v6

    invoke-static {v11, v6}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    .line 373
    invoke-static {}, Lkotlinx/coroutines/Dispatchers;->getIO()Lkotlinx/coroutines/CoroutineDispatcher;

    move-result-object v6

    check-cast v6, Lkotlin/coroutines/CoroutineContext;

    new-instance v7, Lcom/bachatas4/android/service/ImportService$runPkgImport$4$1;

    const/4 v12, 0x0

    invoke-direct {v7, v0, v12}, Lcom/bachatas4/android/service/ImportService$runPkgImport$4$1;-><init>(Landroid/os/ParcelFileDescriptor;Lkotlin/coroutines/Continuation;)V

    check-cast v7, Lkotlin/jvm/functions/Function2;

    iput-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$0:Ljava/lang/Object;

    iput-object v2, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$1:Ljava/lang/Object;

    iput-object v3, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$2:Ljava/lang/Object;

    iput-object v4, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$3:Ljava/lang/Object;

    iput-object v5, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$4:Ljava/lang/Object;

    iput-object v15, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$5:Ljava/lang/Object;

    move-object/from16 v12, v17

    iput-object v12, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$6:Ljava/lang/Object;

    move-object/from16 v14, v16

    iput-object v14, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$7:Ljava/lang/Object;

    iput-object v13, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$8:Ljava/lang/Object;

    iput-object v8, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$9:Ljava/lang/Object;

    invoke-static {v0}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v0

    iput-object v0, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$10:Ljava/lang/Object;

    iput-object v14, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$11:Ljava/lang/Object;

    move/from16 v0, v18

    iput-boolean v0, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->Z$0:Z
    :try_end_12
    .catchall {:try_start_12 .. :try_end_12} :catchall_61

    move-object/from16 v16, v3

    const/4 v3, 0x2

    :try_start_13
    iput v3, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->label:I

    invoke-static {v6, v7, v10}, Lkotlinx/coroutines/BuildersKt;->withContext(Lkotlin/coroutines/CoroutineContext;Lkotlin/jvm/functions/Function2;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;

    move-result-object v6
    :try_end_13
    .catchall {:try_start_13 .. :try_end_13} :catchall_60

    move-object/from16 v7, v38

    if-ne v6, v7, :cond_4

    goto/16 :goto_35

    :cond_4
    move/from16 v17, v0

    move-object v0, v6

    move-object v6, v13

    move-object v3, v14

    move-object v13, v1

    move-object v14, v2

    move-object v2, v12

    move-object v1, v15

    move-object/from16 v12, v16

    move-object v15, v5

    move-object v5, v8

    move-object v8, v4

    move-object v4, v3

    .line 321
    :goto_6
    :try_start_14
    iput-object v0, v4, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    .line 374
    sget-object v0, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;
    :try_end_14
    .catchall {:try_start_14 .. :try_end_14} :catchall_5f

    const/4 v4, 0x0

    .line 368
    :try_start_15
    invoke-static {v5, v4}, Lkotlin/io/CloseableKt;->closeFinally(Ljava/io/Closeable;Ljava/lang/Throwable;)V
    :try_end_15
    .catch Ljava/lang/SecurityException; {:try_start_15 .. :try_end_15} :catch_3
    .catch Ljava/lang/Exception; {:try_start_15 .. :try_end_15} :catch_2
    .catchall {:try_start_15 .. :try_end_15} :catchall_5e

    .line 382
    :try_start_16
    iget-object v0, v3, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v0, Lcom/bachatas4/android/runtime/pkg/PkgProbeResult;

    invoke-virtual {v0}, Lcom/bachatas4/android/runtime/pkg/PkgProbeResult;->getStatus()Lcom/bachatas4/android/runtime/pkg/PkgStatus;

    move-result-object v0

    iget-object v4, v3, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v4, Lcom/bachatas4/android/runtime/pkg/PkgProbeResult;

    invoke-virtual {v4}, Lcom/bachatas4/android/runtime/pkg/PkgProbeResult;->getContentId()Ljava/lang/String;

    move-result-object v4

    .line 383
    iget-object v5, v3, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v5, Lcom/bachatas4/android/runtime/pkg/PkgProbeResult;
    :try_end_16
    .catchall {:try_start_16 .. :try_end_16} :catchall_5e

    move-object/16 p1, v1

    move-object/16 p2, v2

    :try_start_17
    invoke-virtual {v5}, Lcom/bachatas4/android/runtime/pkg/PkgProbeResult;->getPackageSize()J

    move-result-wide v1

    iget-object v5, v3, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v5, Lcom/bachatas4/android/runtime/pkg/PkgProbeResult;

    move-object/from16 v16, v6

    invoke-virtual {v5}, Lcom/bachatas4/android/runtime/pkg/PkgProbeResult;->getPfsImageSize()J

    move-result-wide v5

    move-object/from16 v38, v7

    .line 384
    iget-object v7, v3, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v7, Lcom/bachatas4/android/runtime/pkg/PkgProbeResult;

    invoke-virtual {v7}, Lcom/bachatas4/android/runtime/pkg/PkgProbeResult;->getTitleHint()Ljava/lang/String;

    move-result-object v7
    :try_end_17
    .catchall {:try_start_17 .. :try_end_17} :catchall_5d

    :try_start_18
    iget-object v9, v3, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v9, Lcom/bachatas4/android/runtime/pkg/PkgProbeResult;

    invoke-virtual {v9}, Lcom/bachatas4/android/runtime/pkg/PkgProbeResult;->getMessage()Ljava/lang/String;

    move-result-object v9
    :try_end_18
    .catchall {:try_start_18 .. :try_end_18} :catchall_5c

    move-object/from16 v18, v15

    :try_start_19
    new-instance v15, Ljava/lang/StringBuilder;
    :try_end_19
    .catchall {:try_start_19 .. :try_end_19} :catchall_5b

    move-object/from16 v19, v14

    move-object/from16 v14, v62

    :try_start_1a
    invoke-direct {v15, v14}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v15, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;

    move-result-object v0

    const-string v14, " contentId="

    invoke-virtual {v0, v14}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    const-string v4, " pkgSize="

    invoke-virtual {v0, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0, v1, v2}, Ljava/lang/StringBuilder;->append(J)Ljava/lang/StringBuilder;

    move-result-object v0

    const-string v1, " pfsSize="

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0, v5, v6}, Ljava/lang/StringBuilder;->append(J)Ljava/lang/StringBuilder;

    move-result-object v0

    const-string v1, " hint="

    invoke-virtual {v0, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0, v7}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    move-object/from16 v14, v81

    invoke-virtual {v0, v14}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0, v9}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    .line 380
    invoke-static {v11, v0}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    .line 386
    iget-object v0, v3, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v0, Lcom/bachatas4/android/runtime/pkg/PkgProbeResult;

    invoke-virtual {v0}, Lcom/bachatas4/android/runtime/pkg/PkgProbeResult;->getTitleHint()Ljava/lang/String;

    move-result-object v0
    :try_end_1a
    .catchall {:try_start_1a .. :try_end_1a} :catchall_5a

    if-eqz v0, :cond_6

    :try_start_1b
    check-cast v0, Ljava/lang/CharSequence;

    invoke-static {v0}, Lkotlin/text/StringsKt;->isBlank(Ljava/lang/CharSequence;)Z

    move-result v1

    if-eqz v1, :cond_5

    const/4 v0, 0x0

    :cond_5
    check-cast v0, Ljava/lang/String;
    :try_end_1b
    .catchall {:try_start_1b .. :try_end_1b} :catchall_b

    if-nez v0, :cond_8

    goto :goto_8

    :catchall_b
    move-exception v0

    move-object/from16 v1, p0

    move-object/from16 v4, p1

    move-object v3, v12

    :goto_7
    move-object/from16 v8, v18

    move-object/from16 v2, v19

    move-object/from16 v15, v83

    move-object/from16 v9, v84

    move-object/from16 v13, v85

    const/16 v46, 0x0

    move-object v12, v11

    goto/16 :goto_47

    .line 387
    :cond_6
    :goto_8
    :try_start_1c
    iget-object v0, v3, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v0, Lcom/bachatas4/android/runtime/pkg/PkgProbeResult;

    invoke-virtual {v0}, Lcom/bachatas4/android/runtime/pkg/PkgProbeResult;->getContentId()Ljava/lang/String;

    move-result-object v0

    check-cast v0, Ljava/lang/CharSequence;

    invoke-static {v0}, Lkotlin/text/StringsKt;->isBlank(Ljava/lang/CharSequence;)Z

    move-result v1
    :try_end_1c
    .catchall {:try_start_1c .. :try_end_1c} :catchall_5a

    if-eqz v1, :cond_7

    :try_start_1d
    const-string v0, "PKG"
    :try_end_1d
    .catchall {:try_start_1d .. :try_end_1d} :catchall_b

    :cond_7
    :try_start_1e
    check-cast v0, Ljava/lang/String;

    .line 388
    :cond_8
    sget-object v1, Lcom/bachatas4/android/data/ImportManager;->INSTANCE:Lcom/bachatas4/android/data/ImportManager;

    new-instance v2, Lcom/bachatas4/android/data/ImportProgress$ReadingMetadata;

    iget-object v4, v3, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v4, Lcom/bachatas4/android/runtime/pkg/PkgProbeResult;

    invoke-virtual {v4}, Lcom/bachatas4/android/runtime/pkg/PkgProbeResult;->getContentId()Ljava/lang/String;

    move-result-object v4

    invoke-direct {v2, v0, v4}, Lcom/bachatas4/android/data/ImportProgress$ReadingMetadata;-><init>(Ljava/lang/String;Ljava/lang/String;)V

    check-cast v2, Lcom/bachatas4/android/data/ImportProgress;

    invoke-virtual {v1, v2}, Lcom/bachatas4/android/data/ImportManager;->update(Lcom/bachatas4/android/data/ImportProgress;)V

    .line 389
    iget-object v1, v8, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    move-object/from16 v91, v1

    check-cast v91, Lcom/bachatas4/android/data/InstallJob;

    .line 390
    const-string v94, "READING_METADATA"

    .line 392
    iget-object v1, v3, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v1, Lcom/bachatas4/android/runtime/pkg/PkgProbeResult;

    invoke-virtual {v1}, Lcom/bachatas4/android/runtime/pkg/PkgProbeResult;->getContentId()Ljava/lang/String;

    move-result-object v99

    .line 393
    invoke-static {}, Ljava/lang/System;->currentTimeMillis()J

    move-result-wide v111

    const v115, 0x37f3b

    const/16 v116, 0x0

    const/16 v92, 0x0

    const/16 v93, 0x0

    const/16 v95, 0x0

    const/16 v96, 0x0

    const/16 v97, 0x0

    const/16 v100, 0x0

    const/16 v101, 0x0

    const/16 v102, 0x0

    const-wide/16 v103, 0x0

    const-wide/16 v105, 0x0

    const-wide/16 v107, 0x0

    const-wide/16 v109, 0x0

    const/16 v113, 0x0

    const/16 v114, 0x0

    move-object/from16 v98, v0

    .line 389
    invoke-static/range {v91 .. v116}, Lcom/bachatas4/android/data/InstallJob;->copy$default(Lcom/bachatas4/android/data/InstallJob;ILjava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;ZLjava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;JJJJJLjava/lang/String;Ljava/lang/String;ILjava/lang/Object;)Lcom/bachatas4/android/data/InstallJob;

    move-result-object v0

    move-object/from16 v9, v98

    iput-object v0, v8, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    .line 395
    iget-object v0, v8, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v0, Lcom/bachatas4/android/data/InstallJob;

    invoke-virtual {v12, v0}, Lcom/bachatas4/android/data/InstallJobStore;->update(Lcom/bachatas4/android/data/InstallJob;)V

    .line 396
    const-string v2, "Reading metadata\u2026"
    :try_end_1e
    .catchall {:try_start_1e .. :try_end_1e} :catchall_5a

    const/4 v6, 0x6

    const/4 v7, 0x0

    move-object v0, v3

    const/4 v3, 0x0

    const/4 v4, 0x0

    const/4 v5, 0x1

    move-object/from16 v1, p0

    move-object/from16 v15, p1

    move-object/from16 v98, v9

    move-object/from16 v27, v14

    move-object/from16 v14, v16

    move/from16 v117, v17

    move-object/from16 v9, p2

    :try_start_1f
    invoke-static/range {v1 .. v7}, Lcom/bachatas4/android/service/ImportService;->updateNotification$default(Lcom/bachatas4/android/service/ImportService;Ljava/lang/String;IIZILjava/lang/Object;)V

    .line 398
    iget-object v2, v0, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v2, Lcom/bachatas4/android/runtime/pkg/PkgProbeResult;

    invoke-virtual {v2}, Lcom/bachatas4/android/runtime/pkg/PkgProbeResult;->getStatus()Lcom/bachatas4/android/runtime/pkg/PkgStatus;

    move-result-object v2

    sget-object v3, Lcom/bachatas4/android/runtime/pkg/PkgStatus;->ERROR:Lcom/bachatas4/android/runtime/pkg/PkgStatus;
    :try_end_1f
    .catchall {:try_start_1f .. :try_end_1f} :catchall_59

    if-ne v2, v3, :cond_a

    .line 400
    :try_start_20
    sget-object v2, Lcom/bachatas4/android/data/InstallValidator;->INSTANCE:Lcom/bachatas4/android/data/InstallValidator;

    iget-object v3, v0, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v3, Lcom/bachatas4/android/runtime/pkg/PkgProbeResult;

    invoke-virtual {v3}, Lcom/bachatas4/android/runtime/pkg/PkgProbeResult;->getMessage()Ljava/lang/String;

    move-result-object v3

    invoke-virtual {v2, v3}, Lcom/bachatas4/android/data/InstallValidator;->mapProbeError(Ljava/lang/String;)Lcom/bachatas4/android/data/InstallErrorCode;

    move-result-object v2

    .line 401
    iget-object v0, v0, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v0, Lcom/bachatas4/android/runtime/pkg/PkgProbeResult;

    invoke-virtual {v0}, Lcom/bachatas4/android/runtime/pkg/PkgProbeResult;->getMessage()Ljava/lang/String;

    move-result-object v0

    if-nez v0, :cond_9

    const-string v0, "Invalid package"

    .line 399
    :cond_9
    invoke-direct {v1, v2, v0}, Lcom/bachatas4/android/service/ImportService;->failInstall(Lcom/bachatas4/android/data/InstallErrorCode;Ljava/lang/String;)Ljava/lang/Void;

    new-instance v0, Lkotlin/KotlinNothingValueException;

    invoke-direct {v0}, Lkotlin/KotlinNothingValueException;-><init>()V

    throw v0
    :try_end_20
    .catchall {:try_start_20 .. :try_end_20} :catchall_c

    :catchall_c
    move-exception v0

    move-object v3, v12

    move-object v4, v15

    goto/16 :goto_7

    .line 404
    :cond_a
    :try_start_21
    iget-object v2, v0, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v2, Lcom/bachatas4/android/runtime/pkg/PkgProbeResult;

    invoke-virtual {v2}, Lcom/bachatas4/android/runtime/pkg/PkgProbeResult;->getContentId()Ljava/lang/String;

    move-result-object v2

    check-cast v2, Ljava/lang/CharSequence;

    invoke-static {v2}, Lkotlin/text/StringsKt;->isBlank(Ljava/lang/CharSequence;)Z

    move-result v2
    :try_end_21
    .catchall {:try_start_21 .. :try_end_21} :catchall_59

    if-eqz v2, :cond_c

    :try_start_22
    iget-object v2, v0, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v2, Lcom/bachatas4/android/runtime/pkg/PkgProbeResult;

    invoke-virtual {v2}, Lcom/bachatas4/android/runtime/pkg/PkgProbeResult;->getTitleHint()Ljava/lang/String;

    move-result-object v2

    check-cast v2, Ljava/lang/CharSequence;

    if-eqz v2, :cond_b

    invoke-static {v2}, Lkotlin/text/StringsKt;->isBlank(Ljava/lang/CharSequence;)Z

    move-result v2

    if-nez v2, :cond_b

    goto :goto_9

    .line 405
    :cond_b
    sget-object v0, Lcom/bachatas4/android/data/InstallErrorCode;->NO_TITLE_ID:Lcom/bachatas4/android/data/InstallErrorCode;

    const-string v2, "Package has no title identifier"

    invoke-direct {v1, v0, v2}, Lcom/bachatas4/android/service/ImportService;->failInstall(Lcom/bachatas4/android/data/InstallErrorCode;Ljava/lang/String;)Ljava/lang/Void;

    new-instance v0, Lkotlin/KotlinNothingValueException;

    invoke-direct {v0}, Lkotlin/KotlinNothingValueException;-><init>()V

    throw v0
    :try_end_22
    .catchall {:try_start_22 .. :try_end_22} :catchall_c

    .line 408
    :cond_c
    :goto_9
    :try_start_23
    new-instance v2, Ljava/io/File;

    invoke-virtual {v1}, Lcom/bachatas4/android/service/ImportService;->getFilesDir()Ljava/io/File;

    move-result-object v3

    const-string v4, "games"

    invoke-direct {v2, v3, v4}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    invoke-virtual {v2}, Ljava/io/File;->getCanonicalFile()Ljava/io/File;

    move-result-object v2

    .line 409
    invoke-virtual {v2}, Ljava/io/File;->mkdirs()Z

    .line 410
    iget-object v3, v0, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v3, Lcom/bachatas4/android/runtime/pkg/PkgProbeResult;

    invoke-virtual {v3}, Lcom/bachatas4/android/runtime/pkg/PkgProbeResult;->getPackageSize()J

    move-result-wide v3

    const-wide/16 v5, 0x0

    invoke-static {v3, v4, v5, v6}, Lkotlin/ranges/RangesKt;->coerceAtLeast(JJ)J

    move-result-wide v3

    .line 411
    iget-object v7, v0, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v7, Lcom/bachatas4/android/runtime/pkg/PkgProbeResult;

    invoke-virtual {v7}, Lcom/bachatas4/android/runtime/pkg/PkgProbeResult;->getPfsImageSize()J

    move-result-wide v16

    invoke-static/range {v16 .. v17}, Lkotlin/coroutines/jvm/internal/Boxing;->boxLong(J)Ljava/lang/Long;

    move-result-object v7

    move-object/from16 v16, v7

    check-cast v16, Ljava/lang/Number;

    invoke-virtual/range {v16 .. v16}, Ljava/lang/Number;->longValue()J

    move-result-wide v16
    :try_end_23
    .catchall {:try_start_23 .. :try_end_23} :catchall_59

    cmp-long v16, v16, v5

    if-lez v16, :cond_d

    goto :goto_a

    :cond_d
    const/4 v7, 0x0

    :goto_a
    if-eqz v7, :cond_e

    :try_start_24
    invoke-virtual {v7}, Ljava/lang/Long;->longValue()J

    move-result-wide v16
    :try_end_24
    .catchall {:try_start_24 .. :try_end_24} :catchall_c

    move-object/16 p1, v2

    move-wide/from16 v1, v16

    goto :goto_b

    :cond_e
    move-object/16 p1, v2

    move-wide v1, v3

    :goto_b
    :try_start_25
    invoke-static {v1, v2, v5, v6}, Lkotlin/ranges/RangesKt;->coerceAtLeast(JJ)J

    move-result-wide v1

    .line 414
    iget-boolean v5, v14, Lkotlin/jvm/internal/Ref$BooleanRef;->element:Z

    if-eqz v5, :cond_f

    move-wide v5, v1

    goto :goto_c

    :cond_f
    add-long v5, v3, v1

    :goto_c
    const-wide/16 v16, 0x14

    move-object/16 p2, v9

    move-object/from16 v40, v10

    .line 415
    div-long v9, v5, v16
    :try_end_25
    .catchall {:try_start_25 .. :try_end_25} :catchall_58

    move-object/from16 v16, v12

    move-object/from16 v17, v13

    const-wide/32 v12, 0x10000000

    :try_start_26
    invoke-static {v12, v13, v9, v10}, Ljava/lang/Math;->max(JJ)J

    move-result-wide v9

    add-long v12, v5, v9

    .line 417
    invoke-virtual/range {p0 .. p0}, Lcom/bachatas4/android/service/ImportService;->getFilesDir()Ljava/io/File;

    move-result-object v7

    move-wide/from16 v28, v5

    invoke-virtual {v7}, Ljava/io/File;->getUsableSpace()J

    move-result-wide v5

    .line 421
    iget-boolean v7, v14, Lkotlin/jvm/internal/Ref$BooleanRef;->element:Z

    move-wide/from16 v30, v9

    new-instance v9, Ljava/lang/StringBuilder;

    move-object/from16 v10, v74

    invoke-direct {v9, v10}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v9, v3, v4}, Ljava/lang/StringBuilder;->append(J)Ljava/lang/StringBuilder;

    move-result-object v9

    const-string v10, " extract="

    invoke-virtual {v9, v10}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v9

    invoke-virtual {v9, v1, v2}, Ljava/lang/StringBuilder;->append(J)Ljava/lang/StringBuilder;

    move-result-object v9

    move-object/from16 v10, v76

    invoke-virtual {v9, v10}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v9

    invoke-virtual {v9, v7}, Ljava/lang/StringBuilder;->append(Z)Ljava/lang/StringBuilder;

    move-result-object v7

    move-object/from16 v9, v78

    invoke-virtual {v7, v9}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v7

    invoke-virtual {v7, v12, v13}, Ljava/lang/StringBuilder;->append(J)Ljava/lang/StringBuilder;

    move-result-object v7

    move-wide/from16 v132, v1

    const-string v1, " free="

    invoke-virtual {v7, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1, v5, v6}, Ljava/lang/StringBuilder;->append(J)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v1

    .line 418
    invoke-static {v11, v1}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    .line 424
    sget-object v1, Lcom/bachatas4/android/data/ImportManager;->INSTANCE:Lcom/bachatas4/android/data/ImportManager;

    .line 425
    new-instance v20, Lcom/bachatas4/android/data/ImportProgress$CheckingStorage;

    iget-object v2, v0, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v2, Lcom/bachatas4/android/runtime/pkg/PkgProbeResult;

    invoke-virtual {v2}, Lcom/bachatas4/android/runtime/pkg/PkgProbeResult;->getContentId()Ljava/lang/String;

    move-result-object v21

    move-wide/from16 v24, v5

    move-wide/from16 v22, v12

    invoke-direct/range {v20 .. v25}, Lcom/bachatas4/android/data/ImportProgress$CheckingStorage;-><init>(Ljava/lang/String;JJ)V

    move-wide/from16 v5, v24

    move-object/from16 v2, v20

    check-cast v2, Lcom/bachatas4/android/data/ImportProgress;

    .line 424
    invoke-virtual {v1, v2}, Lcom/bachatas4/android/data/ImportManager;->update(Lcom/bachatas4/android/data/ImportProgress;)V

    .line 427
    iget-object v1, v8, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    move-object/from16 v118, v1

    check-cast v118, Lcom/bachatas4/android/data/InstallJob;

    .line 428
    const-string v121, "CHECKING_STORAGE"

    .line 432
    invoke-static {}, Ljava/lang/System;->currentTimeMillis()J

    move-result-wide v138

    const v142, 0x347fb

    const/16 v143, 0x0

    const/16 v119, 0x0

    const/16 v120, 0x0

    const/16 v122, 0x0

    const/16 v123, 0x0

    const/16 v124, 0x0

    const/16 v125, 0x0

    const/16 v126, 0x0

    const/16 v127, 0x0

    const/16 v128, 0x0

    const/16 v129, 0x0

    const-wide/16 v136, 0x0

    const/16 v140, 0x0

    const/16 v141, 0x0

    move-wide/from16 v130, v3

    move-wide/from16 v134, v22

    .line 427
    invoke-static/range {v118 .. v143}, Lcom/bachatas4/android/data/InstallJob;->copy$default(Lcom/bachatas4/android/data/InstallJob;ILjava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;ZLjava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;JJJJJLjava/lang/String;Ljava/lang/String;ILjava/lang/Object;)Lcom/bachatas4/android/data/InstallJob;

    move-result-object v1

    move-wide/from16 v2, v134

    iput-object v1, v8, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    .line 434
    iget-object v1, v8, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v1, Lcom/bachatas4/android/data/InstallJob;
    :try_end_26
    .catchall {:try_start_26 .. :try_end_26} :catchall_57

    move-object/from16 v12, v16

    :try_start_27
    invoke-virtual {v12, v1}, Lcom/bachatas4/android/data/InstallJobStore;->update(Lcom/bachatas4/android/data/InstallJob;)V

    .line 436
    sget-object v1, Lcom/bachatas4/android/data/InstallValidator;->INSTANCE:Lcom/bachatas4/android/data/InstallValidator;

    invoke-virtual {v1, v2, v3, v5, v6}, Lcom/bachatas4/android/data/InstallValidator;->checkStorage(JJ)Lcom/bachatas4/android/data/InstallErrorCode;

    move-result-object v1
    :try_end_27
    .catchall {:try_start_27 .. :try_end_27} :catchall_58

    if-nez v1, :cond_32

    .line 444
    :try_start_28
    sget-object v1, Lcom/bachatas4/android/data/ImportManager;->INSTANCE:Lcom/bachatas4/android/data/ImportManager;

    .line 445
    new-instance v99, Lcom/bachatas4/android/data/ImportProgress$NeedCopyConfirm;

    .line 446
    iget-object v4, v0, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v4, Lcom/bachatas4/android/runtime/pkg/PkgProbeResult;

    invoke-virtual {v4}, Lcom/bachatas4/android/runtime/pkg/PkgProbeResult;->getContentId()Ljava/lang/String;

    move-result-object v100

    .line 447
    iget-object v4, v0, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v4, Lcom/bachatas4/android/runtime/pkg/PkgProbeResult;

    invoke-virtual {v4}, Lcom/bachatas4/android/runtime/pkg/PkgProbeResult;->getTitleHint()Ljava/lang/String;

    move-result-object v101

    move-wide/from16 v106, v2

    move-wide/from16 v108, v5

    move-wide/from16 v102, v130

    move-wide/from16 v104, v132

    .line 445
    invoke-direct/range {v99 .. v109}, Lcom/bachatas4/android/data/ImportProgress$NeedCopyConfirm;-><init>(Ljava/lang/String;Ljava/lang/String;JJJJ)V

    move-wide/from16 v130, v102

    move-wide/from16 v132, v104

    move-wide/from16 v22, v106

    move-object/from16 v2, v99

    check-cast v2, Lcom/bachatas4/android/data/ImportProgress;

    .line 444
    invoke-virtual {v1, v2}, Lcom/bachatas4/android/data/ImportManager;->update(Lcom/bachatas4/android/data/ImportProgress;)V

    .line 454
    iget-object v1, v8, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    move-object/from16 v134, v1

    check-cast v134, Lcom/bachatas4/android/data/InstallJob;

    .line 455
    const-string v137, "NEED_COPY_CONFIRM"

    .line 456
    invoke-static {}, Ljava/lang/System;->currentTimeMillis()J

    move-result-wide v154

    const v158, 0x37ffb

    const/16 v159, 0x0

    const/16 v135, 0x0

    const/16 v136, 0x0

    const/16 v138, 0x0

    const/16 v139, 0x0

    const/16 v140, 0x0

    const/16 v141, 0x0

    const/16 v142, 0x0

    const/16 v143, 0x0

    const/16 v144, 0x0

    const/16 v145, 0x0

    const-wide/16 v146, 0x0

    const-wide/16 v148, 0x0

    const-wide/16 v150, 0x0

    const-wide/16 v152, 0x0

    const/16 v156, 0x0

    const/16 v157, 0x0

    .line 454
    invoke-static/range {v134 .. v159}, Lcom/bachatas4/android/data/InstallJob;->copy$default(Lcom/bachatas4/android/data/InstallJob;ILjava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;ZLjava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;JJJJJLjava/lang/String;Ljava/lang/String;ILjava/lang/Object;)Lcom/bachatas4/android/data/InstallJob;

    move-result-object v1

    iput-object v1, v8, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    .line 458
    iget-object v1, v8, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v1, Lcom/bachatas4/android/data/InstallJob;

    invoke-virtual {v12, v1}, Lcom/bachatas4/android/data/InstallJobStore;->update(Lcom/bachatas4/android/data/InstallJob;)V

    .line 459
    const-string v2, "Confirm storage for PKG import"
    :try_end_28
    .catchall {:try_start_28 .. :try_end_28} :catchall_55

    const/4 v6, 0x6

    const/4 v7, 0x0

    const/4 v3, 0x0

    const/4 v4, 0x0

    const/4 v5, 0x1

    move-object/from16 v1, p0

    move-object/from16 v13, p1

    move-object/from16 v44, v11

    move-wide/from16 v164, v22

    move-wide/from16 v162, v28

    move-wide/from16 v166, v108

    move-wide/from16 v160, v132

    move-object/from16 v22, v10

    move-wide/from16 v10, v130

    :try_start_29
    invoke-static/range {v1 .. v7}, Lcom/bachatas4/android/service/ImportService;->updateNotification$default(Lcom/bachatas4/android/service/ImportService;Ljava/lang/String;IIZILjava/lang/Object;)V

    const/4 v2, 0x1

    const/4 v4, 0x0

    .line 460
    invoke-static {v4, v2, v4}, Lkotlinx/coroutines/CompletableDeferredKt;->CompletableDeferred$default(Lkotlinx/coroutines/Job;ILjava/lang/Object;)Lkotlinx/coroutines/CompletableDeferred;

    move-result-object v3

    .line 461
    iput-object v3, v1, Lcom/bachatas4/android/service/ImportService;->copyConfirmWaiter:Lkotlinx/coroutines/CompletableDeferred;

    move-object/from16 v2, v17

    move-object/from16 v4, v40

    .line 462
    iput-object v2, v4, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$0:Ljava/lang/Object;
    :try_end_29
    .catchall {:try_start_29 .. :try_end_29} :catchall_54

    move-object/from16 v6, v19

    :try_start_2a
    iput-object v6, v4, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$1:Ljava/lang/Object;

    iput-object v12, v4, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$2:Ljava/lang/Object;

    iput-object v8, v4, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$3:Ljava/lang/Object;
    :try_end_2a
    .catchall {:try_start_2a .. :try_end_2a} :catchall_53

    move-object/from16 v7, v18

    :try_start_2b
    iput-object v7, v4, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$4:Ljava/lang/Object;

    iput-object v15, v4, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$5:Ljava/lang/Object;

    move-object/from16 v5, p2

    iput-object v5, v4, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$6:Ljava/lang/Object;

    iput-object v0, v4, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$7:Ljava/lang/Object;

    iput-object v14, v4, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$8:Ljava/lang/Object;

    move-object/from16 v17, v2

    move-object/from16 v2, v98

    iput-object v2, v4, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$9:Ljava/lang/Object;

    iput-object v13, v4, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$10:Ljava/lang/Object;

    move-object/from16 v98, v2

    invoke-static {v3}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v2

    iput-object v2, v4, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$11:Ljava/lang/Object;

    move/from16 v2, v117

    iput-boolean v2, v4, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->Z$0:Z

    iput-wide v10, v4, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$0:J
    :try_end_2b
    .catchall {:try_start_2b .. :try_end_2b} :catchall_52

    move-object/16 p2, v5

    move-object/from16 v19, v6

    move-wide/from16 v5, v160

    :try_start_2c
    iput-wide v5, v4, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$1:J

    move-wide/from16 v132, v5

    move-wide/from16 v5, v162

    iput-wide v5, v4, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$2:J

    move-wide/from16 v28, v5

    move-wide/from16 v5, v30

    iput-wide v5, v4, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$3:J

    move-wide/from16 v30, v5

    move-wide/from16 v5, v164

    iput-wide v5, v4, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$4:J
    :try_end_2c
    .catchall {:try_start_2c .. :try_end_2c} :catchall_51

    move-object/from16 v18, v7

    move-object/from16 v16, v8

    move-wide/from16 v7, v166

    :try_start_2d
    iput-wide v7, v4, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$5:J

    move/from16 v117, v2

    const/4 v2, 0x3

    iput v2, v4, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->label:I

    invoke-interface {v3, v4}, Lkotlinx/coroutines/CompletableDeferred;->await(Lkotlin/coroutines/Continuation;)Ljava/lang/Object;

    move-result-object v2
    :try_end_2d
    .catchall {:try_start_2d .. :try_end_2d} :catchall_54

    move-wide/from16 v130, v10

    move-object/from16 v10, v38

    if-ne v2, v10, :cond_10

    move-object v7, v10

    goto/16 :goto_35

    :cond_10
    move-object v11, v12

    move-object v12, v0

    move-object v0, v2

    move-object v2, v11

    move-object/from16 v11, v16

    move-object/from16 v16, v3

    move-object/from16 v3, v17

    move-object/from16 v17, v15

    move-object v15, v11

    move-object/from16 v21, p2

    move-object/from16 v40, v4

    move-wide v4, v5

    move-wide v6, v7

    move-object/from16 v38, v10

    move-object/from16 v8, v18

    move-object/from16 v11, v19

    move-wide/from16 v170, v28

    move-wide/from16 v172, v30

    move-object/from16 v18, v98

    move/from16 v10, v117

    move-wide/from16 v19, v130

    move-wide/from16 v168, v132

    :goto_d
    :try_start_2e
    check-cast v0, Ljava/lang/Boolean;

    invoke-virtual {v0}, Ljava/lang/Boolean;->booleanValue()Z

    move-result v0

    move/from16 v23, v10

    const/4 v10, 0x0

    .line 463
    iput-object v10, v1, Lcom/bachatas4/android/service/ImportService;->copyConfirmWaiter:Lkotlinx/coroutines/CompletableDeferred;

    if-eqz v0, :cond_31

    .line 467
    new-instance v10, Ljava/lang/StringBuilder;
    :try_end_2e
    .catchall {:try_start_2e .. :try_end_2e} :catchall_50

    move-object/from16 v1, v57

    :try_start_2f
    invoke-direct {v10, v1}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v10, v6, v7}, Ljava/lang/StringBuilder;->append(J)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1, v9}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1, v4, v5}, Ljava/lang/StringBuilder;->append(J)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v1
    :try_end_2f
    .catchall {:try_start_2f .. :try_end_2f} :catchall_4e

    move-object/from16 v9, v44

    :try_start_30
    invoke-static {v9, v1}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    .line 470
    invoke-virtual/range {p0 .. p0}, Lcom/bachatas4/android/service/ImportService;->getFilesDir()Ljava/io/File;

    move-result-object v1

    move-wide/from16 v24, v6

    invoke-virtual {v1}, Ljava/io/File;->getUsableSpace()J

    move-result-wide v6

    .line 471
    sget-object v1, Lcom/bachatas4/android/data/InstallValidator;->INSTANCE:Lcom/bachatas4/android/data/InstallValidator;

    invoke-virtual {v1, v4, v5, v6, v7}, Lcom/bachatas4/android/data/InstallValidator;->checkStorage(JJ)Lcom/bachatas4/android/data/InstallErrorCode;

    move-result-object v1
    :try_end_30
    .catchall {:try_start_30 .. :try_end_30} :catchall_4d

    if-nez v1, :cond_30

    .line 480
    :try_start_31
    new-instance v1, Ljava/io/File;

    new-instance v10, Ljava/lang/StringBuilder;

    move-wide/16 p1, v6

    move-object/from16 v6, v60

    invoke-direct {v10, v6}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v10, v11}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v6

    invoke-virtual {v6}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v6

    invoke-direct {v1, v13, v6}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    invoke-virtual {v1}, Ljava/io/File;->getCanonicalFile()Ljava/io/File;

    move-result-object v1

    iput-object v1, v8, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    .line 481
    iget-object v1, v8, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    invoke-static {v1}, Lkotlin/jvm/internal/Intrinsics;->checkNotNull(Ljava/lang/Object;)V

    check-cast v1, Ljava/io/File;

    invoke-virtual {v1}, Ljava/io/File;->mkdirs()Z

    .line 482
    iget-object v1, v8, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    invoke-static {v1}, Lkotlin/jvm/internal/Intrinsics;->checkNotNull(Ljava/lang/Object;)V

    check-cast v1, Ljava/io/File;

    invoke-virtual {v1}, Ljava/io/File;->getAbsolutePath()Ljava/lang/String;

    move-result-object v1

    new-instance v6, Ljava/lang/StringBuilder;

    move-object/from16 v7, v69

    invoke-direct {v6, v7}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v6, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v1

    invoke-static {v9, v1}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    .line 484
    new-instance v10, Lkotlin/jvm/internal/Ref$ObjectRef;

    invoke-direct {v10}, Lkotlin/jvm/internal/Ref$ObjectRef;-><init>()V

    .line 485
    new-instance v1, Lkotlin/jvm/internal/Ref$ObjectRef;

    invoke-direct {v1}, Lkotlin/jvm/internal/Ref$ObjectRef;-><init>()V

    sget-object v6, Lcom/bachatas4/android/runtime/pkg/PkgStatus;->ERROR:Lcom/bachatas4/android/runtime/pkg/PkgStatus;

    iput-object v6, v1, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    .line 487
    invoke-static {}, Lkotlin/collections/CollectionsKt;->createListBuilder()Ljava/util/List;

    move-result-object v6

    const/4 v7, 0x0

    .line 488
    invoke-interface {v6, v7}, Ljava/util/List;->add(Ljava/lang/Object;)Z

    .line 489
    invoke-virtual/range {p0 .. p0}, Lcom/bachatas4/android/service/ImportService;->getPkgKeyStore()Lcom/bachatas4/android/data/PkgKeyStore;

    move-result-object v7

    move-wide/from16 v28, v4

    iget-object v4, v12, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v4, Lcom/bachatas4/android/runtime/pkg/PkgProbeResult;

    invoke-virtual {v4}, Lcom/bachatas4/android/runtime/pkg/PkgProbeResult;->getContentId()Ljava/lang/String;

    move-result-object v4

    invoke-virtual {v7, v4}, Lcom/bachatas4/android/data/PkgKeyStore;->getPasscode(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v4
    :try_end_31
    .catchall {:try_start_31 .. :try_end_31} :catchall_4c

    if-eqz v4, :cond_11

    :try_start_32
    invoke-interface {v6, v4}, Ljava/util/List;->add(Ljava/lang/Object;)Z

    move-result v4

    invoke-static {v4}, Lkotlin/coroutines/jvm/internal/Boxing;->boxBoolean(Z)Ljava/lang/Boolean;
    :try_end_32
    .catchall {:try_start_32 .. :try_end_32} :catchall_d

    goto :goto_e

    :catchall_d
    move-exception v0

    move-object/from16 v1, p0

    move-object v3, v2

    move-object v12, v9

    move-object v2, v11

    move-object/from16 v4, v17

    move-object/from16 v11, v82

    move-object/from16 v15, v83

    move-object/from16 v9, v84

    move-object/from16 v13, v85

    goto/16 :goto_66

    :cond_11
    :goto_e
    move-object/from16 v4, v79

    .line 490
    :try_start_33
    invoke-interface {v6, v4}, Ljava/util/List;->add(Ljava/lang/Object;)Z

    .line 487
    invoke-static {v6}, Lkotlin/collections/CollectionsKt;->build(Ljava/util/List;)Ljava/util/List;

    move-result-object v5

    check-cast v5, Ljava/lang/Iterable;

    .line 491
    invoke-static {v5}, Lkotlin/collections/CollectionsKt;->distinct(Ljava/lang/Iterable;)Ljava/util/List;

    move-result-object v5

    .line 492
    invoke-interface {v5}, Ljava/util/List;->size()I

    move-result v6

    new-instance v7, Ljava/lang/StringBuilder;

    move-object/from16 v42, v4

    move-object/from16 v4, v70

    invoke-direct {v7, v4}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v7, v6}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    move-result-object v4

    const-string v6, " (passcodes redacted)"

    invoke-virtual {v4, v6}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v4

    invoke-virtual {v4}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v4

    invoke-static {v9, v4}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    .line 498
    iget-boolean v4, v14, Lkotlin/jvm/internal/Ref$BooleanRef;->element:Z
    :try_end_33
    .catchall {:try_start_33 .. :try_end_33} :catchall_4c

    const-string v6, "games/.import-"

    if-eqz v4, :cond_13

    .line 499
    :try_start_34
    iget-object v4, v15, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    move-object/from16 v87, v4

    check-cast v87, Lcom/bachatas4/android/data/InstallJob;

    .line 500
    new-instance v4, Ljava/lang/StringBuilder;

    invoke-direct {v4, v6}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v4, v11}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v4

    invoke-virtual {v4}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v97

    .line 502
    invoke-static {}, Ljava/lang/System;->currentTimeMillis()J

    move-result-wide v107

    .line 501
    const-string v90, "EXTRACTING"

    const v111, 0x37dfb

    const/16 v112, 0x0

    const/16 v88, 0x0

    const/16 v89, 0x0

    const/16 v91, 0x0

    const/16 v92, 0x0

    const/16 v93, 0x0

    const/16 v94, 0x0

    const/16 v95, 0x0

    const/16 v96, 0x0

    const/16 v98, 0x0

    const-wide/16 v99, 0x0

    const-wide/16 v101, 0x0

    const-wide/16 v103, 0x0

    const-wide/16 v105, 0x0

    const/16 v109, 0x0

    const/16 v110, 0x0

    .line 499
    invoke-static/range {v87 .. v112}, Lcom/bachatas4/android/data/InstallJob;->copy$default(Lcom/bachatas4/android/data/InstallJob;ILjava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;ZLjava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;JJJJJLjava/lang/String;Ljava/lang/String;ILjava/lang/Object;)Lcom/bachatas4/android/data/InstallJob;

    move-result-object v4

    iput-object v4, v15, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    .line 504
    iget-object v4, v15, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v4, Lcom/bachatas4/android/data/InstallJob;

    invoke-virtual {v2, v4}, Lcom/bachatas4/android/data/InstallJobStore;->update(Lcom/bachatas4/android/data/InstallJob;)V

    .line 505
    new-instance v4, Ljava/lang/StringBuilder;

    move-object/from16 v6, v71

    invoke-direct {v4, v6}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v4, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v4

    invoke-virtual {v4}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v4

    invoke-static {v9, v4}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    .line 506
    invoke-virtual/range {p0 .. p0}, Lcom/bachatas4/android/service/ImportService;->getContentResolver()Landroid/content/ContentResolver;

    move-result-object v4

    const-string v6, "r"

    move-object/from16 v7, v21

    invoke-virtual {v4, v7, v6}, Landroid/content/ContentResolver;->openFileDescriptor(Landroid/net/Uri;Ljava/lang/String;)Landroid/os/ParcelFileDescriptor;

    move-result-object v4

    if-eqz v4, :cond_12

    move-object/from16 v49, v2

    move-object v2, v7

    move-object/from16 v31, v12

    move-object/from16 v36, v13

    move-object/from16 v48, v15

    move-object/from16 v45, v17

    move-object/from16 v41, v18

    move/from16 v117, v23

    move-wide/from16 v17, v28

    move-object/from16 v7, v38

    const/4 v6, 0x0

    move-wide/from16 v12, p1

    move-object/from16 v29, v8

    move-object v15, v14

    move-object/from16 v14, v42

    move-object/from16 v8, v77

    goto/16 :goto_10

    :cond_12
    new-instance v0, Ljava/lang/IllegalStateException;

    .line 507
    const-string v1, "Cannot reopen PKG for extract"

    invoke-virtual {v1}, Ljava/lang/Object;->toString()Ljava/lang/String;

    move-result-object v1

    invoke-direct {v0, v1}, Ljava/lang/IllegalStateException;-><init>(Ljava/lang/String;)V

    throw v0
    :try_end_34
    .catchall {:try_start_34 .. :try_end_34} :catchall_d

    :cond_13
    move-object/from16 v7, v21

    .line 509
    :try_start_35
    new-instance v4, Ljava/io/File;

    invoke-virtual/range {p0 .. p0}, Lcom/bachatas4/android/service/ImportService;->getFilesDir()Ljava/io/File;

    move-result-object v7

    move-object/from16 v26, v5

    const-string v5, "pkg-cache"

    invoke-direct {v4, v7, v5}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    invoke-virtual {v4}, Ljava/io/File;->getCanonicalFile()Ljava/io/File;

    move-result-object v4

    .line 510
    invoke-virtual {v4}, Ljava/io/File;->mkdirs()Z

    .line 511
    new-instance v5, Ljava/io/File;

    new-instance v7, Ljava/lang/StringBuilder;

    invoke-direct {v7}, Ljava/lang/StringBuilder;-><init>()V

    invoke-virtual {v7, v11}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v7

    move-object/from16 v30, v1

    const-string v1, ".pkg"

    invoke-virtual {v7, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v1

    invoke-direct {v5, v4, v1}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    invoke-virtual {v5}, Ljava/io/File;->getCanonicalFile()Ljava/io/File;

    move-result-object v1
    :try_end_35
    .catchall {:try_start_35 .. :try_end_35} :catchall_4c

    .line 512
    :try_start_36
    iget-object v5, v15, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    move-object/from16 v87, v5

    check-cast v87, Lcom/bachatas4/android/data/InstallJob;

    .line 513
    new-instance v5, Ljava/lang/StringBuilder;

    move-object/from16 v7, v72

    invoke-direct {v5, v7}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v5, v11}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v5

    const-string v7, ".pkg"

    invoke-virtual {v5, v7}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v5

    invoke-virtual {v5}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v98

    .line 514
    new-instance v5, Ljava/lang/StringBuilder;

    invoke-direct {v5, v6}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v5, v11}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v5

    invoke-virtual {v5}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v97

    .line 516
    invoke-static {}, Ljava/lang/System;->currentTimeMillis()J

    move-result-wide v107

    .line 515
    const-string v90, "EXTRACTING"

    const v111, 0x379fb

    const/16 v112, 0x0

    const/16 v88, 0x0

    const/16 v89, 0x0

    const/16 v91, 0x0

    const/16 v92, 0x0

    const/16 v93, 0x0

    const/16 v94, 0x0

    const/16 v95, 0x0

    const/16 v96, 0x0

    const-wide/16 v99, 0x0

    const-wide/16 v101, 0x0

    const-wide/16 v103, 0x0

    const-wide/16 v105, 0x0

    const/16 v109, 0x0

    const/16 v110, 0x0

    .line 512
    invoke-static/range {v87 .. v112}, Lcom/bachatas4/android/data/InstallJob;->copy$default(Lcom/bachatas4/android/data/InstallJob;ILjava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;ZLjava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;JJJJJLjava/lang/String;Ljava/lang/String;ILjava/lang/Object;)Lcom/bachatas4/android/data/InstallJob;

    move-result-object v5

    iput-object v5, v15, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    .line 518
    iget-object v5, v15, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v5, Lcom/bachatas4/android/data/InstallJob;

    invoke-virtual {v2, v5}, Lcom/bachatas4/android/data/InstallJobStore;->update(Lcom/bachatas4/android/data/InstallJob;)V

    .line 519
    invoke-static {v1}, Lkotlin/jvm/internal/Intrinsics;->checkNotNull(Ljava/lang/Object;)V

    invoke-virtual {v1}, Ljava/io/File;->getAbsolutePath()Ljava/lang/String;

    move-result-object v5

    new-instance v6, Ljava/lang/StringBuilder;

    move-object/from16 v7, v73

    invoke-direct {v6, v7}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v6, v5}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v5

    move-object/from16 v6, v77

    invoke-virtual {v5, v6}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v5

    move-object/from16 v53, v6

    move-wide/from16 v6, v19

    invoke-virtual {v5, v6, v7}, Ljava/lang/StringBuilder;->append(J)Ljava/lang/StringBuilder;

    move-result-object v5

    invoke-virtual {v5}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v5

    invoke-static {v9, v5}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    .line 520
    invoke-static/range {v21 .. v21}, Lkotlin/jvm/internal/Intrinsics;->checkNotNull(Ljava/lang/Object;)V

    move-object/from16 v5, v40

    iput-object v3, v5, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$0:Ljava/lang/Object;

    iput-object v11, v5, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$1:Ljava/lang/Object;

    iput-object v2, v5, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$2:Ljava/lang/Object;

    iput-object v15, v5, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$3:Ljava/lang/Object;

    iput-object v8, v5, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$4:Ljava/lang/Object;

    iput-object v1, v5, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$5:Ljava/lang/Object;
    :try_end_36
    .catchall {:try_start_36 .. :try_end_36} :catchall_4b

    move-object/from16 v19, v1

    move-object/from16 v1, v17

    :try_start_37
    iput-object v1, v5, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$6:Ljava/lang/Object;
    :try_end_37
    .catchall {:try_start_37 .. :try_end_37} :catchall_4a

    move-object/from16 v17, v1

    :try_start_38
    invoke-static/range {v21 .. v21}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v1

    iput-object v1, v5, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$7:Ljava/lang/Object;

    iput-object v12, v5, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$8:Ljava/lang/Object;

    iput-object v14, v5, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$9:Ljava/lang/Object;

    move-object/from16 v1, v18

    iput-object v1, v5, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$10:Ljava/lang/Object;

    iput-object v13, v5, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$11:Ljava/lang/Object;

    move-object/from16 v18, v1

    invoke-static/range {v16 .. v16}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v1

    iput-object v1, v5, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$12:Ljava/lang/Object;

    iput-object v10, v5, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$13:Ljava/lang/Object;

    move-object/from16 v1, v30

    iput-object v1, v5, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$14:Ljava/lang/Object;

    move-object/from16 v30, v1

    move-object/from16 v1, v26

    iput-object v1, v5, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$15:Ljava/lang/Object;

    invoke-static {v4}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v4

    iput-object v4, v5, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$16:Ljava/lang/Object;

    move/from16 v4, v23

    iput-boolean v4, v5, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->Z$0:Z

    iput-wide v6, v5, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$0:J
    :try_end_38
    .catchall {:try_start_38 .. :try_end_38} :catchall_49

    move-object/from16 v23, v10

    move-object/from16 v20, v11

    move-wide/from16 v10, v168

    :try_start_39
    iput-wide v10, v5, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$1:J

    move-object/from16 v31, v12

    move-object/from16 v26, v13

    move-wide/from16 v12, v170

    iput-wide v12, v5, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$2:J

    move-wide/from16 v32, v12

    move-wide/from16 v12, v172

    iput-wide v12, v5, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$3:J
    :try_end_39
    .catchall {:try_start_39 .. :try_end_39} :catchall_48

    move-object/from16 v36, v1

    move-object/from16 v34, v2

    move-wide/from16 v1, v28

    :try_start_3a
    iput-wide v1, v5, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$4:J

    move-wide/from16 v28, v1

    move-wide/from16 v1, v24

    iput-wide v1, v5, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$5:J

    iput-boolean v0, v5, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->Z$1:Z

    move-wide/from16 v24, v1

    move-wide/from16 v1, p1

    iput-wide v1, v5, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$6:J

    move-wide/16 p1, v1

    const/4 v1, 0x4

    iput v1, v5, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->label:I
    :try_end_3a
    .catchall {:try_start_3a .. :try_end_3a} :catchall_47

    move-wide v1, v6

    move-object v7, v5

    move-wide v5, v1

    move-object/from16 v1, p0

    move/from16 v117, v4

    move-object/from16 v49, v17

    move-object/from16 v4, v18

    move-object/from16 v2, v21

    move-wide/from16 v17, v12

    move-object/from16 v21, v15

    move-wide/from16 v12, v28

    move-object/from16 v28, v3

    move-object/from16 v29, v8

    move-object/from16 v3, v19

    move-object/from16 v8, v53

    move-object/from16 v19, v14

    move-object/from16 v14, v42

    :try_start_3b
    invoke-direct/range {v1 .. v7}, Lcom/bachatas4/android/service/ImportService;->copyPkgToLocalCache(Landroid/net/Uri;Ljava/io/File;Ljava/lang/String;JLkotlin/coroutines/Continuation;)Ljava/lang/Object;

    move-result-object v15
    :try_end_3b
    .catchall {:try_start_3b .. :try_end_3b} :catchall_46

    move-object v1, v4

    move-object/from16 v40, v7

    move-object/from16 v7, v38

    if-ne v15, v7, :cond_14

    goto/16 :goto_35

    :cond_14
    move-object/from16 v41, v1

    move-object v4, v3

    move-object/from16 v50, v20

    move-object/from16 v48, v21

    move-object/from16 v1, v28

    move-object/from16 v3, v36

    move-object/from16 v45, v49

    move-wide/from16 v20, v17

    move-object/from16 v36, v26

    move-object/from16 v49, v34

    move-wide/from16 v17, v12

    move-wide/from16 v12, p1

    .line 521
    :goto_f
    :try_start_3c
    invoke-static {v4}, Lkotlin/jvm/internal/Intrinsics;->checkNotNull(Ljava/lang/Object;)V

    move-object/16 p1, v1

    move-object/16 p2, v2

    invoke-virtual {v4}, Ljava/io/File;->length()J

    move-result-wide v1

    new-instance v15, Ljava/lang/StringBuilder;

    move-object/from16 v26, v3

    move-object/from16 v3, v66

    invoke-direct {v15, v3}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v15, v1, v2}, Ljava/lang/StringBuilder;->append(J)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v1

    invoke-static {v9, v1}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    const/high16 v1, 0x10000000

    .line 522
    invoke-static {v4, v1}, Landroid/os/ParcelFileDescriptor;->open(Ljava/io/File;I)Landroid/os/ParcelFileDescriptor;

    move-result-object v1

    invoke-static {v1}, Lkotlin/jvm/internal/Intrinsics;->checkNotNull(Ljava/lang/Object;)V
    :try_end_3c
    .catchall {:try_start_3c .. :try_end_3c} :catchall_45

    move-object/from16 v3, p1

    move-object/from16 v2, p2

    move-wide/from16 v168, v10

    move-object/from16 v15, v19

    move-wide/from16 v172, v20

    move-object/from16 v10, v23

    move-wide/from16 v170, v32

    move-object/from16 v11, v50

    move-wide/from16 v19, v5

    move-object/from16 v5, v26

    move-object v6, v4

    move-object v4, v1

    move-object/from16 v1, v30

    .line 525
    :goto_10
    :try_start_3d
    move-object/from16 v21, v4

    check-cast v21, Ljava/io/Closeable;
    :try_end_3d
    .catchall {:try_start_3d .. :try_end_3d} :catchall_44

    :try_start_3e
    move-object/from16 v23, v21

    check-cast v23, Landroid/os/ParcelFileDescriptor;

    move-object/16 p1, v1

    .line 526
    invoke-virtual/range {v23 .. v23}, Landroid/os/ParcelFileDescriptor;->getFd()I

    move-result v1

    move-object/from16 v26, v2

    move-object/16 p2, v3

    .line 527
    invoke-virtual/range {v23 .. v23}, Landroid/os/ParcelFileDescriptor;->getStatSize()J

    move-result-wide v2

    move-object/from16 v28, v4

    iget-boolean v4, v15, Lkotlin/jvm/internal/Ref$BooleanRef;->element:Z
    :try_end_3e
    .catchall {:try_start_3e .. :try_end_3e} :catchall_41

    move-object/from16 v30, v6

    :try_start_3f
    new-instance v6, Ljava/lang/StringBuilder;

    move-object/from16 v32, v10

    move-object/from16 v10, v59

    invoke-direct {v6, v10}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v6, v1}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    move-result-object v6

    invoke-virtual {v6, v8}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v6

    invoke-virtual {v6, v2, v3}, Ljava/lang/StringBuilder;->append(J)Ljava/lang/StringBuilder;

    move-result-object v2

    move-object/from16 v10, v22

    invoke-virtual {v2, v10}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v2

    invoke-virtual {v2, v4}, Ljava/lang/StringBuilder;->append(Z)Ljava/lang/StringBuilder;

    move-result-object v2

    invoke-virtual {v2}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v2

    invoke-static {v9, v2}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    .line 529
    move-object v2, v5

    check-cast v2, Ljava/lang/Iterable;

    invoke-interface {v2}, Ljava/lang/Iterable;->iterator()Ljava/util/Iterator;

    move-result-object v2
    :try_end_3f
    .catchall {:try_start_3f .. :try_end_3f} :catchall_40

    move-object/from16 v10, p1

    move-object v8, v2

    move-wide/from16 v174, v12

    move-wide/from16 v178, v17

    move-wide/from16 v3, v19

    move-wide/from16 v176, v24

    move-object/from16 v12, v31

    move-object/16 p1, v36

    move/from16 v6, v54

    const/16 v19, 0x0

    move-object/from16 v13, p2

    move v2, v1

    move-object/from16 v18, v5

    move-object/from16 v25, v14

    move-object/from16 v17, v16

    move-object/from16 v5, v45

    move-object v14, v11

    move-object/from16 v16, v15

    move-object/from16 v15, v30

    move-object/from16 v11, v48

    goto/16 :goto_14

    :goto_11
    :try_start_40
    invoke-interface {v8}, Ljava/util/Iterator;->hasNext()Z

    move-result v20
    :try_end_40
    .catchall {:try_start_40 .. :try_end_40} :catchall_3f

    if-eqz v20, :cond_1b

    move-object/from16 v38, v7

    add-int/lit8 v7, v6, 0x1

    :try_start_41
    invoke-interface {v8}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v20

    check-cast v20, Ljava/lang/String;

    move/16 p2, v2

    if-eqz v20, :cond_15

    const/4 v2, 0x1

    goto :goto_12

    :cond_15
    move/from16 v2, v54

    :goto_12
    move-wide/from16 v29, v3

    .line 533
    iget-object v3, v1, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    invoke-static {v3}, Lkotlin/jvm/internal/Intrinsics;->checkNotNull(Ljava/lang/Object;)V

    check-cast v3, Ljava/io/File;

    invoke-virtual {v3}, Ljava/io/File;->getAbsolutePath()Ljava/lang/String;

    move-result-object v3

    new-instance v4, Ljava/lang/StringBuilder;

    invoke-direct {v4}, Ljava/lang/StringBuilder;-><init>()V

    move/from16 v22, v7

    move-object/from16 v7, v80

    invoke-virtual {v4, v7}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v4

    invoke-virtual {v4, v6}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    move-result-object v4
    :try_end_41
    .catchall {:try_start_41 .. :try_end_41} :catchall_15

    move-object/from16 v24, v1

    :try_start_42
    const-string v1, " hasPasscode="

    invoke-virtual {v4, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Z)Ljava/lang/StringBuilder;

    move-result-object v1

    const-string v2, " staging="

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v1

    .line 530
    invoke-static {v9, v1}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    .line 535
    invoke-static {}, Lkotlinx/coroutines/Dispatchers;->getIO()Lkotlinx/coroutines/CoroutineDispatcher;

    move-result-object v1

    check-cast v1, Lkotlin/coroutines/CoroutineContext;

    move v2, v0

    new-instance v0, Lcom/bachatas4/android/service/ImportService$runPkgImport$7$result$1;
    :try_end_42
    .catchall {:try_start_42 .. :try_end_42} :catchall_14

    move v3, v6

    const/4 v6, 0x0

    move-object/from16 v190, v1

    move/from16 v189, v3

    move-object/from16 v80, v7

    move-object/from16 v44, v9

    move-object/from16 v4, v20

    move-object/from16 v191, v21

    move-object/from16 v3, v24

    move-wide/from16 v180, v29

    move-object/from16 v24, v32

    move/from16 v182, v117

    move-wide/from16 v183, v168

    move-wide/from16 v185, v170

    move-wide/from16 v187, v172

    move-object/from16 v1, p0

    move-object/from16 v7, p1

    move/from16 v20, v2

    move-object v9, v5

    move-object/16 p1, v8

    move-object/from16 v21, v10

    move-object/from16 v10, v40

    move-object/from16 v5, v41

    move-object/from16 v8, v49

    move/from16 v2, p2

    :try_start_43
    invoke-direct/range {v0 .. v6}, Lcom/bachatas4/android/service/ImportService$runPkgImport$7$result$1;-><init>(Lcom/bachatas4/android/service/ImportService;ILkotlin/jvm/internal/Ref$ObjectRef;Ljava/lang/String;Ljava/lang/String;Lkotlin/coroutines/Continuation;)V

    check-cast v0, Lkotlin/jvm/functions/Function2;

    iput-object v13, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$0:Ljava/lang/Object;

    iput-object v14, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$1:Ljava/lang/Object;

    iput-object v8, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$2:Ljava/lang/Object;

    iput-object v11, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$3:Ljava/lang/Object;

    iput-object v3, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$4:Ljava/lang/Object;

    iput-object v15, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$5:Ljava/lang/Object;

    iput-object v9, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$6:Ljava/lang/Object;

    invoke-static/range {v26 .. v26}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v1

    iput-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$7:Ljava/lang/Object;

    iput-object v12, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$8:Ljava/lang/Object;

    invoke-static/range {v16 .. v16}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v1

    iput-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$9:Ljava/lang/Object;

    iput-object v5, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$10:Ljava/lang/Object;

    iput-object v7, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$11:Ljava/lang/Object;

    invoke-static/range {v17 .. v17}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v1

    iput-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$12:Ljava/lang/Object;

    move-object/from16 v1, v24

    iput-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$13:Ljava/lang/Object;

    move-object/from16 v6, v21

    iput-object v6, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$14:Ljava/lang/Object;

    move-object/from16 v24, v1

    invoke-static/range {v18 .. v18}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v1

    iput-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$15:Ljava/lang/Object;

    invoke-static/range {v28 .. v28}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v1

    iput-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$16:Ljava/lang/Object;
    :try_end_43
    .catchall {:try_start_43 .. :try_end_43} :catchall_13

    move-object/from16 v1, v191

    :try_start_44
    iput-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$17:Ljava/lang/Object;
    :try_end_44
    .catchall {:try_start_44 .. :try_end_44} :catchall_12

    move-object/from16 v191, v1

    :try_start_45
    invoke-static/range {v23 .. v23}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v1

    iput-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$18:Ljava/lang/Object;

    move-object/from16 v1, p1

    iput-object v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$19:Ljava/lang/Object;

    iput-object v4, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$20:Ljava/lang/Object;

    move-object/16 p1, v1

    move/from16 v1, v182

    iput-boolean v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->Z$0:Z
    :try_end_45
    .catchall {:try_start_45 .. :try_end_45} :catchall_13

    move-object/from16 v29, v3

    move-object/from16 v21, v4

    move-wide/from16 v3, v180

    :try_start_46
    iput-wide v3, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$0:J

    move-wide/from16 v180, v3

    move-wide/from16 v3, v183

    iput-wide v3, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$1:J

    move-wide/from16 v183, v3

    move-wide/from16 v3, v185

    iput-wide v3, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$2:J

    move-wide/from16 v185, v3

    move-wide/from16 v3, v187

    iput-wide v3, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$3:J

    move-wide/from16 v187, v3

    move-wide/from16 v3, v178

    iput-wide v3, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$4:J

    move-wide/from16 v30, v3

    move-wide/from16 v3, v176

    iput-wide v3, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$5:J

    move/from16 v182, v1

    move/from16 v1, v20

    iput-boolean v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->Z$1:Z

    move-wide/from16 v32, v3

    move-wide/from16 v3, v174

    iput-wide v3, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$6:J

    iput v2, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->I$0:I

    move/from16 v20, v1

    move/from16 v1, v22

    iput v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->I$1:I

    move/from16 v22, v1

    move/from16 v1, v189

    iput v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->I$2:I

    move/from16 v189, v1

    const/4 v1, 0x5

    iput v1, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->label:I

    move-object/from16 v1, v190

    invoke-static {v1, v0, v10}, Lkotlinx/coroutines/BuildersKt;->withContext(Lkotlin/coroutines/CoroutineContext;Lkotlin/jvm/functions/Function2;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;

    move-result-object v0
    :try_end_46
    .catchall {:try_start_46 .. :try_end_46} :catchall_11

    move-object/from16 v1, v38

    if-ne v0, v1, :cond_16

    goto/16 :goto_1e

    :cond_16
    move-wide/from16 v174, v3

    move-object/from16 v41, v5

    move-object/from16 v49, v8

    move-object v5, v9

    move-object/from16 v40, v10

    move-object/from16 v50, v15

    move-object/from16 v3, v21

    move-object/from16 v4, v24

    move-wide/from16 v178, v30

    move-wide/from16 v176, v32

    move/from16 v117, v182

    move-wide/from16 v168, v183

    move-wide/from16 v170, v185

    move-wide/from16 v172, v187

    move-object/from16 v21, v191

    move-object/from16 v8, p1

    move v15, v2

    move-object v10, v6

    move/from16 v6, v22

    move/from16 v2, v189

    .line 321
    :goto_13
    :try_start_47
    check-cast v0, Lcom/bachatas4/android/runtime/pkg/PkgExtractResult;

    .line 538
    invoke-virtual {v0}, Lcom/bachatas4/android/runtime/pkg/PkgExtractResult;->getStatus()Lcom/bachatas4/android/runtime/pkg/PkgStatus;

    move-result-object v9

    iput-object v9, v10, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    .line 539
    invoke-virtual {v0}, Lcom/bachatas4/android/runtime/pkg/PkgExtractResult;->getStatus()Lcom/bachatas4/android/runtime/pkg/PkgStatus;

    move-result-object v9

    move-object/from16 v38, v1

    invoke-virtual {v0}, Lcom/bachatas4/android/runtime/pkg/PkgExtractResult;->getMessage()Ljava/lang/String;

    move-result-object v1
    :try_end_47
    .catchall {:try_start_47 .. :try_end_47} :catchall_10

    move-object/16 p1, v5

    :try_start_48
    new-instance v5, Ljava/lang/StringBuilder;

    invoke-direct {v5}, Ljava/lang/StringBuilder;-><init>()V

    move/16 p2, v6

    move-object/from16 v6, v80

    invoke-virtual {v5, v6}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v5

    invoke-virtual {v5, v2}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    move-result-object v2

    const-string v5, " result="

    invoke-virtual {v2, v5}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v2

    invoke-virtual {v2, v9}, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;

    move-result-object v2

    move-object/from16 v5, v27

    invoke-virtual {v2, v5}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v2

    invoke-virtual {v2, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v1
    :try_end_48
    .catchall {:try_start_48 .. :try_end_48} :catchall_f

    move-object/from16 v2, v44

    :try_start_49
    invoke-static {v2, v1}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    .line 540
    invoke-virtual {v0}, Lcom/bachatas4/android/runtime/pkg/PkgExtractResult;->getStatus()Lcom/bachatas4/android/runtime/pkg/PkgStatus;

    move-result-object v1

    sget-object v9, Lcom/bachatas4/android/runtime/pkg/PkgStatus;->OK:Lcom/bachatas4/android/runtime/pkg/PkgStatus;

    if-ne v1, v9, :cond_17

    .line 541
    iput-object v3, v4, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    move-object v3, v2

    move-object/from16 v195, v4

    move-object/from16 v192, v5

    move-object v2, v10

    move-object/from16 v193, v13

    move-object v5, v14

    move-object/from16 v13, v21

    move-object/from16 v8, v41

    move-object/from16 v194, v50

    move/from16 v196, v117

    move-wide/from16 v197, v168

    move-wide/from16 v199, v170

    move-wide/from16 v201, v172

    move-wide/from16 v203, v174

    move-wide/from16 v205, v176

    move-wide/from16 v207, v178

    move-object/from16 v14, p1

    move-object v9, v7

    move-object v4, v11

    move-object v6, v12

    move/from16 v0, v20

    move-object/from16 v7, v29

    move-object/from16 v10, v40

    move-object/from16 v33, v86

    move-wide/from16 v11, v180

    goto/16 :goto_1c

    .line 544
    :cond_17
    invoke-virtual {v0}, Lcom/bachatas4/android/runtime/pkg/PkgExtractResult;->getStatus()Lcom/bachatas4/android/runtime/pkg/PkgStatus;

    move-result-object v1

    sget-object v3, Lcom/bachatas4/android/runtime/pkg/PkgStatus;->CANCELLED:Lcom/bachatas4/android/runtime/pkg/PkgStatus;

    if-eq v1, v3, :cond_1a

    .line 545
    invoke-virtual {v0}, Lcom/bachatas4/android/runtime/pkg/PkgExtractResult;->getStatus()Lcom/bachatas4/android/runtime/pkg/PkgStatus;

    move-result-object v1

    sget-object v3, Lcom/bachatas4/android/runtime/pkg/PkgStatus;->NEED_PASSCODE:Lcom/bachatas4/android/runtime/pkg/PkgStatus;

    if-eq v1, v3, :cond_19

    .line 546
    invoke-virtual {v0}, Lcom/bachatas4/android/runtime/pkg/PkgExtractResult;->getMessage()Ljava/lang/String;

    move-result-object v0

    if-nez v0, :cond_18

    const-string v0, "PKG extract failed"

    :cond_18
    new-instance v1, Ljava/lang/IllegalStateException;

    invoke-virtual {v0}, Ljava/lang/Object;->toString()Ljava/lang/String;

    move-result-object v0

    invoke-direct {v1, v0}, Ljava/lang/IllegalStateException;-><init>(Ljava/lang/String;)V

    throw v1

    :cond_19
    move-object v9, v2

    move-object/from16 v32, v4

    move-object/from16 v27, v5

    move-object/from16 v80, v6

    move v2, v15

    move/from16 v0, v20

    move-object/from16 v15, v50

    move-wide/from16 v3, v180

    move-object/from16 v5, p1

    move/from16 v6, p2

    move-object/16 p1, v7

    move-object/from16 v7, v38

    :goto_14
    move-object/from16 v1, v29

    goto/16 :goto_11

    .line 544
    :cond_1a
    new-instance v0, Ljava/util/concurrent/CancellationException;

    move-object/from16 v1, v86

    invoke-direct {v0, v1}, Ljava/util/concurrent/CancellationException;-><init>(Ljava/lang/String;)V

    throw v0
    :try_end_49
    .catchall {:try_start_49 .. :try_end_49} :catchall_e

    :catchall_e
    move-exception v0

    goto :goto_15

    :catchall_f
    move-exception v0

    move-object/from16 v2, v44

    :goto_15
    move-object/from16 v5, p1

    goto :goto_16

    :catchall_10
    move-exception v0

    move-object/16 p1, v5

    move-object/from16 v2, v44

    :goto_16
    move-object v3, v0

    move-object v12, v2

    move-object v11, v14

    move-object/from16 v4, v21

    move-object/from16 v7, v29

    move-object/from16 v8, v49

    move-object/from16 v9, v50

    move-object/from16 v15, v83

    move-object/from16 v1, v84

    move-object/from16 v31, v85

    :goto_17
    move-object/from16 v2, p0

    goto/16 :goto_46

    :catchall_11
    move-exception v0

    goto :goto_19

    :catchall_12
    move-exception v0

    move-object/from16 v191, v1

    goto :goto_18

    :catchall_13
    move-exception v0

    :goto_18
    move-object/from16 v29, v3

    :goto_19
    move-object/from16 v2, v44

    move-object v3, v0

    move-object v12, v2

    move-object v5, v9

    goto :goto_1b

    :catchall_14
    move-exception v0

    move-object v2, v9

    move-object/from16 v191, v21

    move-object/from16 v29, v24

    goto :goto_1a

    :catchall_15
    move-exception v0

    move-object/from16 v29, v1

    move-object v2, v9

    move-object/from16 v191, v21

    :goto_1a
    move-object/from16 v8, v49

    move-object v9, v5

    move-object v3, v0

    move-object v12, v2

    :goto_1b
    move-object v11, v14

    move-object v9, v15

    move-object/from16 v7, v29

    move-object/from16 v15, v83

    move-object/from16 v1, v84

    move-object/from16 v31, v85

    move-object/from16 v4, v191

    goto :goto_17

    :cond_1b
    move/from16 v20, v0

    move-object/from16 v29, v1

    move-wide/from16 v180, v3

    move-object/from16 v38, v7

    move-object v3, v9

    move-object v6, v10

    move-object/from16 v191, v21

    move-object/from16 v192, v27

    move-object/from16 v24, v32

    move-object/from16 v8, v49

    move/from16 v182, v117

    move-wide/from16 v183, v168

    move-wide/from16 v185, v170

    move-wide/from16 v187, v172

    move-wide/from16 v21, v174

    move-wide/from16 v32, v176

    move-wide/from16 v30, v178

    move-object/from16 v7, p1

    move-object v9, v5

    move-object/from16 v5, v41

    move-object/from16 v193, v13

    move-object/from16 v194, v15

    move-wide/from16 v203, v21

    move-object/from16 v195, v24

    move-wide/from16 v207, v30

    move-wide/from16 v205, v32

    move/from16 v196, v182

    move-wide/from16 v197, v183

    move-wide/from16 v199, v185

    move-wide/from16 v201, v187

    move-object/from16 v13, v191

    move v15, v2

    move-object v8, v5

    move-object v2, v6

    move-object v5, v14

    move-object v14, v9

    move-object/from16 v10, v40

    move-object v4, v11

    move-object/from16 v33, v86

    move-object v6, v12

    move-wide/from16 v11, v180

    move-object v9, v7

    move-object/from16 v7, v29

    .line 550
    :goto_1c
    :try_start_4a
    iget-object v1, v2, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    move-object/from16 v20, v2

    sget-object v2, Lcom/bachatas4/android/runtime/pkg/PkgStatus;->OK:Lcom/bachatas4/android/runtime/pkg/PkgStatus;
    :try_end_4a
    .catchall {:try_start_4a .. :try_end_4a} :catchall_3e

    if-eq v1, v2, :cond_22

    .line 551
    :try_start_4b
    iget-object v1, v6, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v1, Lcom/bachatas4/android/runtime/pkg/PkgProbeResult;

    invoke-virtual {v1}, Lcom/bachatas4/android/runtime/pkg/PkgProbeResult;->getContentId()Ljava/lang/String;

    move-result-object v1

    new-instance v2, Ljava/lang/StringBuilder;

    invoke-direct {v2}, Ljava/lang/StringBuilder;-><init>()V

    move-object/16 p1, v4

    const-string v4, "pkg need user passcode contentId="

    invoke-virtual {v2, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v2

    invoke-virtual {v2, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v1

    invoke-static {v3, v1}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    .line 552
    sget-object v1, Lcom/bachatas4/android/data/ImportManager;->INSTANCE:Lcom/bachatas4/android/data/ImportManager;

    .line 553
    new-instance v2, Lcom/bachatas4/android/data/ImportProgress$NeedPasscode;

    iget-object v4, v6, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v4, Lcom/bachatas4/android/runtime/pkg/PkgProbeResult;

    invoke-virtual {v4}, Lcom/bachatas4/android/runtime/pkg/PkgProbeResult;->getContentId()Ljava/lang/String;

    move-result-object v4
    :try_end_4b
    .catchall {:try_start_4b .. :try_end_4b} :catchall_27

    move-object/from16 v44, v3

    :try_start_4c
    iget-object v3, v6, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v3, Lcom/bachatas4/android/runtime/pkg/PkgProbeResult;

    invoke-virtual {v3}, Lcom/bachatas4/android/runtime/pkg/PkgProbeResult;->getTitleHint()Ljava/lang/String;

    move-result-object v3

    invoke-direct {v2, v4, v3}, Lcom/bachatas4/android/data/ImportProgress$NeedPasscode;-><init>(Ljava/lang/String;Ljava/lang/String;)V

    check-cast v2, Lcom/bachatas4/android/data/ImportProgress;

    .line 552
    invoke-virtual {v1, v2}, Lcom/bachatas4/android/data/ImportManager;->update(Lcom/bachatas4/android/data/ImportProgress;)V

    .line 555
    const-string v2, "Passcode required"
    :try_end_4c
    .catchall {:try_start_4c .. :try_end_4c} :catchall_26

    move-object v1, v6

    const/4 v6, 0x6

    move-object/from16 v29, v7

    const/4 v7, 0x0

    const/4 v3, 0x0

    const/4 v4, 0x0

    move-object/from16 v21, v5

    const/4 v5, 0x1

    move-object/from16 v24, v9

    move-object/from16 v22, v13

    move-object/from16 v9, v21

    move-object/from16 v13, v29

    move-object/from16 v210, v33

    move-object/from16 v209, v38

    move-object/from16 v211, v44

    move-wide/from16 v29, v11

    move/from16 v21, v15

    move-object/from16 v12, v49

    move-object/from16 v15, p1

    move-object v11, v1

    move-object/from16 v1, p0

    :try_start_4d
    invoke-static/range {v1 .. v7}, Lcom/bachatas4/android/service/ImportService;->updateNotification$default(Lcom/bachatas4/android/service/ImportService;Ljava/lang/String;IIZILjava/lang/Object;)V

    const/4 v2, 0x1

    const/4 v4, 0x0

    .line 556
    invoke-static {v4, v2, v4}, Lkotlinx/coroutines/CompletableDeferredKt;->CompletableDeferred$default(Lkotlinx/coroutines/Job;ILjava/lang/Object;)Lkotlinx/coroutines/CompletableDeferred;

    move-result-object v3

    .line 557
    iput-object v3, v1, Lcom/bachatas4/android/service/ImportService;->passcodeWaiter:Lkotlinx/coroutines/CompletableDeferred;

    move-object/from16 v2, v193

    .line 558
    iput-object v2, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$0:Ljava/lang/Object;

    iput-object v9, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$1:Ljava/lang/Object;

    iput-object v12, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$2:Ljava/lang/Object;

    iput-object v15, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$3:Ljava/lang/Object;

    iput-object v13, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$4:Ljava/lang/Object;
    :try_end_4d
    .catchall {:try_start_4d .. :try_end_4d} :catchall_25

    move-object/from16 v4, v194

    :try_start_4e
    iput-object v4, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$5:Ljava/lang/Object;

    iput-object v14, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$6:Ljava/lang/Object;

    invoke-static/range {v26 .. v26}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v5

    iput-object v5, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$7:Ljava/lang/Object;

    iput-object v11, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$8:Ljava/lang/Object;

    invoke-static/range {v16 .. v16}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v5

    iput-object v5, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$9:Ljava/lang/Object;

    iput-object v8, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$10:Ljava/lang/Object;

    move-object/from16 v7, v24

    iput-object v7, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$11:Ljava/lang/Object;

    invoke-static/range {v17 .. v17}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v5

    iput-object v5, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$12:Ljava/lang/Object;

    move-object/from16 v5, v195

    iput-object v5, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$13:Ljava/lang/Object;

    invoke-static/range {v20 .. v20}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v6

    iput-object v6, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$14:Ljava/lang/Object;

    invoke-static/range {v18 .. v18}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v6

    iput-object v6, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$15:Ljava/lang/Object;

    invoke-static/range {v28 .. v28}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v6

    iput-object v6, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$16:Ljava/lang/Object;
    :try_end_4e
    .catchall {:try_start_4e .. :try_end_4e} :catchall_24

    move-object/from16 v6, v22

    :try_start_4f
    iput-object v6, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$17:Ljava/lang/Object;

    move-object/from16 v22, v2

    invoke-static/range {v23 .. v23}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v2

    iput-object v2, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$18:Ljava/lang/Object;

    invoke-static {v3}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v2

    iput-object v2, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$19:Ljava/lang/Object;

    const/4 v2, 0x0

    iput-object v2, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$20:Ljava/lang/Object;

    move/from16 v2, v196

    iput-boolean v2, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->Z$0:Z
    :try_end_4f
    .catchall {:try_start_4f .. :try_end_4f} :catchall_23

    move-object/from16 v24, v4

    move-object/from16 v27, v5

    move-wide/from16 v4, v29

    :try_start_50
    iput-wide v4, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$0:J

    move-wide/from16 v29, v4

    move-wide/from16 v4, v197

    iput-wide v4, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$1:J

    move-wide/from16 v31, v4

    move-wide/from16 v4, v199

    iput-wide v4, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$2:J

    move-wide/from16 v33, v4

    move-wide/from16 v4, v201

    iput-wide v4, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$3:J

    move-wide/from16 v38, v4

    move-wide/from16 v4, v207

    iput-wide v4, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$4:J

    move-wide/from16 v40, v4

    move-wide/from16 v4, v205

    iput-wide v4, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$5:J

    iput-boolean v0, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->Z$1:Z

    move-wide/from16 v44, v4

    move-wide/from16 v4, v203

    iput-wide v4, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$6:J

    move/from16 v36, v2

    move/from16 v2, v21

    iput v2, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->I$0:I

    move/from16 v21, v2

    const/4 v2, 0x6

    iput v2, v10, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->label:I

    invoke-interface {v3, v10}, Lkotlinx/coroutines/CompletableDeferred;->await(Lkotlin/coroutines/Continuation;)Ljava/lang/Object;

    move-result-object v2
    :try_end_50
    .catchall {:try_start_50 .. :try_end_50} :catchall_22

    move-object/from16 v42, v7

    move-object/from16 v7, v209

    if-ne v2, v7, :cond_1c

    goto/16 :goto_35

    :cond_1c
    move-object/from16 v212, v13

    move-object v13, v3

    move-object/from16 v3, v212

    move-wide/from16 v218, v4

    move-object v4, v6

    move-object v5, v8

    move-object/from16 v224, v9

    move-object/from16 v222, v12

    move-object/from16 v8, v22

    move-object/from16 v9, v24

    move-object/from16 v12, v27

    move-object/from16 v24, v28

    move-wide/from16 v212, v29

    move-wide/from16 v214, v31

    move-wide/from16 v216, v33

    move/from16 v223, v36

    move-wide/from16 v227, v38

    move-wide/from16 v225, v40

    move-wide/from16 v220, v44

    move v6, v0

    move-object v0, v2

    move-object/from16 v45, v14

    move-object/from16 v34, v20

    move/from16 v2, v21

    move-object v14, v10

    move-object/from16 v10, v42

    .line 321
    :goto_1d
    :try_start_51
    check-cast v0, Ljava/lang/String;

    move/16 p1, v2

    const/4 v2, 0x0

    .line 559
    iput-object v2, v1, Lcom/bachatas4/android/service/ImportService;->passcodeWaiter:Lkotlinx/coroutines/CompletableDeferred;

    .line 560
    move-object v2, v0

    check-cast v2, Ljava/lang/CharSequence;

    if-eqz v2, :cond_21

    invoke-static {v2}, Lkotlin/text/StringsKt;->isBlank(Ljava/lang/CharSequence;)Z

    move-result v2

    if-nez v2, :cond_21

    .line 563
    invoke-virtual {v0}, Ljava/lang/String;->length()I

    move-result v2

    new-instance v1, Ljava/lang/StringBuilder;

    invoke-direct {v1}, Ljava/lang/StringBuilder;-><init>()V
    :try_end_51
    .catchall {:try_start_51 .. :try_end_51} :catchall_21

    move-object/16 p2, v3

    :try_start_52
    const-string v3, "pkg user passcode received len="

    invoke-virtual {v1, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v1
    :try_end_52
    .catchall {:try_start_52 .. :try_end_52} :catchall_1f

    move-object/from16 v2, v211

    :try_start_53
    invoke-static {v2, v1}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    .line 564
    invoke-static {}, Lkotlinx/coroutines/Dispatchers;->getIO()Lkotlinx/coroutines/CoroutineDispatcher;

    move-result-object v1

    check-cast v1, Lkotlin/coroutines/CoroutineContext;
    :try_end_53
    .catchall {:try_start_53 .. :try_end_53} :catchall_1e

    move-object v3, v4

    move-object v4, v0

    :try_start_54
    new-instance v0, Lcom/bachatas4/android/service/ImportService$runPkgImport$7$result$2;
    :try_end_54
    .catchall {:try_start_54 .. :try_end_54} :catchall_1d

    move/from16 v20, v6

    const/4 v6, 0x0

    move-object/from16 v230, v2

    move-object/from16 v56, v7

    move-object/from16 v21, v13

    move/from16 v229, v20

    move-object/from16 v7, v45

    move/from16 v2, p1

    move-object/from16 v20, v1

    move-object v13, v3

    move-object/from16 v1, p0

    move-object/from16 v3, p2

    :try_start_55
    invoke-direct/range {v0 .. v6}, Lcom/bachatas4/android/service/ImportService$runPkgImport$7$result$2;-><init>(Lcom/bachatas4/android/service/ImportService;ILkotlin/jvm/internal/Ref$ObjectRef;Ljava/lang/String;Ljava/lang/String;Lkotlin/coroutines/Continuation;)V

    check-cast v0, Lkotlin/jvm/functions/Function2;

    iput-object v8, v14, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$0:Ljava/lang/Object;
    :try_end_55
    .catchall {:try_start_55 .. :try_end_55} :catchall_1c

    move-object/from16 v1, v224

    :try_start_56
    iput-object v1, v14, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$1:Ljava/lang/Object;
    :try_end_56
    .catchall {:try_start_56 .. :try_end_56} :catchall_1b

    move-object/from16 v6, v222

    :try_start_57
    iput-object v6, v14, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$2:Ljava/lang/Object;

    iput-object v15, v14, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$3:Ljava/lang/Object;

    iput-object v3, v14, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$4:Ljava/lang/Object;

    iput-object v9, v14, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$5:Ljava/lang/Object;

    iput-object v7, v14, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$6:Ljava/lang/Object;
    :try_end_57
    .catchall {:try_start_57 .. :try_end_57} :catchall_1a

    move-object/from16 v22, v1

    :try_start_58
    invoke-static/range {v26 .. v26}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v1

    iput-object v1, v14, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$7:Ljava/lang/Object;

    iput-object v11, v14, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$8:Ljava/lang/Object;

    invoke-static/range {v16 .. v16}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v1

    iput-object v1, v14, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$9:Ljava/lang/Object;

    iput-object v5, v14, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$10:Ljava/lang/Object;

    iput-object v10, v14, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$11:Ljava/lang/Object;

    invoke-static/range {v17 .. v17}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v1

    iput-object v1, v14, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$12:Ljava/lang/Object;

    iput-object v12, v14, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$13:Ljava/lang/Object;

    invoke-static/range {v34 .. v34}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v1

    iput-object v1, v14, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$14:Ljava/lang/Object;

    invoke-static/range {v18 .. v18}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v1

    iput-object v1, v14, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$15:Ljava/lang/Object;

    invoke-static/range {v24 .. v24}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v1

    iput-object v1, v14, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$16:Ljava/lang/Object;

    iput-object v13, v14, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$17:Ljava/lang/Object;

    invoke-static/range {v23 .. v23}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v1

    iput-object v1, v14, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$18:Ljava/lang/Object;

    invoke-static/range {v21 .. v21}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v1

    iput-object v1, v14, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$19:Ljava/lang/Object;

    iput-object v4, v14, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$20:Ljava/lang/Object;

    move/from16 v1, v223

    iput-boolean v1, v14, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->Z$0:Z
    :try_end_58
    .catchall {:try_start_58 .. :try_end_58} :catchall_19

    move-object/16 p2, v3

    move-object/from16 v21, v4

    move-wide/from16 v3, v212

    :try_start_59
    iput-wide v3, v14, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$0:J

    move-wide/from16 v27, v3

    move-wide/from16 v3, v214

    iput-wide v3, v14, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$1:J

    move-wide/from16 v29, v3

    move-wide/from16 v3, v216

    iput-wide v3, v14, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$2:J

    move-wide/from16 v31, v3

    move-wide/from16 v3, v227

    iput-wide v3, v14, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$3:J

    move-wide/from16 v38, v3

    move-wide/from16 v3, v225

    iput-wide v3, v14, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$4:J

    move-wide/from16 v40, v3

    move-wide/from16 v3, v220

    iput-wide v3, v14, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$5:J

    move/from16 v33, v1

    move/from16 v1, v229

    iput-boolean v1, v14, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->Z$1:Z

    move-wide/from16 v44, v3

    move-wide/from16 v3, v218

    iput-wide v3, v14, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$6:J

    iput v2, v14, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->I$0:I

    move/from16 v229, v1

    const/4 v1, 0x7

    iput v1, v14, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->label:I

    move-object/from16 v1, v20

    invoke-static {v1, v0, v14}, Lkotlinx/coroutines/BuildersKt;->withContext(Lkotlin/coroutines/CoroutineContext;Lkotlin/jvm/functions/Function2;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;

    move-result-object v0
    :try_end_59
    .catchall {:try_start_59 .. :try_end_59} :catchall_18

    move-object/from16 v1, v56

    if-ne v0, v1, :cond_1d

    :goto_1e
    move-object v7, v1

    goto/16 :goto_35

    :cond_1d
    move-object/from16 v47, p2

    move-object/from16 v49, v6

    move-object/from16 v46, v9

    move-object/from16 v50, v22

    move/from16 v22, v2

    move-object/from16 v2, v21

    move-object/from16 v21, v19

    move-wide/from16 v19, v40

    move-object/from16 v40, v10

    move-wide/from16 v9, v44

    move-object/from16 v45, v7

    move-wide v6, v3

    move-wide/from16 v3, v27

    .line 321
    :goto_1f
    :try_start_5a
    check-cast v0, Lcom/bachatas4/android/runtime/pkg/PkgExtractResult;

    move-object/from16 v56, v1

    .line 567
    invoke-virtual {v0}, Lcom/bachatas4/android/runtime/pkg/PkgExtractResult;->getStatus()Lcom/bachatas4/android/runtime/pkg/PkgStatus;

    move-result-object v1

    move-wide/16 p1, v3

    invoke-virtual {v0}, Lcom/bachatas4/android/runtime/pkg/PkgExtractResult;->getMessage()Ljava/lang/String;

    move-result-object v3

    new-instance v4, Ljava/lang/StringBuilder;

    invoke-direct {v4}, Ljava/lang/StringBuilder;-><init>()V

    move-object/from16 v27, v5

    const-string v5, "pkg extract with user passcode result="

    invoke-virtual {v4, v5}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v4

    invoke-virtual {v4, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;

    move-result-object v1

    move-object/from16 v5, v192

    invoke-virtual {v1, v5}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v1
    :try_end_5a
    .catchall {:try_start_5a .. :try_end_5a} :catchall_17

    move-object/from16 v3, v230

    :try_start_5b
    invoke-static {v3, v1}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    .line 568
    invoke-virtual {v0}, Lcom/bachatas4/android/runtime/pkg/PkgExtractResult;->getStatus()Lcom/bachatas4/android/runtime/pkg/PkgStatus;

    move-result-object v1

    sget-object v4, Lcom/bachatas4/android/runtime/pkg/PkgStatus;->CANCELLED:Lcom/bachatas4/android/runtime/pkg/PkgStatus;

    if-eq v1, v4, :cond_20

    .line 569
    invoke-virtual {v0}, Lcom/bachatas4/android/runtime/pkg/PkgExtractResult;->getStatus()Lcom/bachatas4/android/runtime/pkg/PkgStatus;

    move-result-object v1

    sget-object v4, Lcom/bachatas4/android/runtime/pkg/PkgStatus;->OK:Lcom/bachatas4/android/runtime/pkg/PkgStatus;

    if-eq v1, v4, :cond_1f

    .line 570
    invoke-virtual {v0}, Lcom/bachatas4/android/runtime/pkg/PkgExtractResult;->getMessage()Ljava/lang/String;

    move-result-object v0

    if-nez v0, :cond_1e

    const-string v0, "Wrong passcode or extract failed"

    :cond_1e
    new-instance v1, Ljava/lang/IllegalStateException;

    invoke-virtual {v0}, Ljava/lang/Object;->toString()Ljava/lang/String;

    move-result-object v0

    invoke-direct {v1, v0}, Ljava/lang/IllegalStateException;-><init>(Ljava/lang/String;)V

    throw v1

    .line 572
    :cond_1f
    iput-object v2, v12, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    move-object/from16 v60, v8

    move-object v4, v13

    move-object/from16 v231, v14

    move-wide/from16 v233, v19

    move-object/from16 v19, v21

    move-object/from16 v1, v27

    move-object/from16 v8, v40

    move-object/from16 v5, v45

    move-object/from16 v2, v49

    move-object/from16 v232, v50

    move-wide/from16 v13, p1

    move-wide/from16 v44, v9

    move/from16 v10, v22

    move-object/from16 v9, v46

    :goto_20
    move-wide/from16 v235, v38

    goto/16 :goto_2c

    .line 568
    :cond_20
    new-instance v0, Ljava/util/concurrent/CancellationException;

    move-object/from16 v1, v210

    invoke-direct {v0, v1}, Ljava/util/concurrent/CancellationException;-><init>(Ljava/lang/String;)V

    throw v0
    :try_end_5b
    .catchall {:try_start_5b .. :try_end_5b} :catchall_16

    :catchall_16
    move-exception v0

    goto :goto_21

    :catchall_17
    move-exception v0

    move-object/from16 v3, v230

    :goto_21
    move-object/from16 v2, p0

    move-object v12, v3

    move-object v4, v13

    move-object/from16 v5, v45

    move-object/from16 v9, v46

    move-object/from16 v7, v47

    move-object/from16 v8, v49

    move-object/from16 v11, v50

    move-object/from16 v15, v83

    move-object/from16 v1, v84

    move-object/from16 v31, v85

    goto/16 :goto_28

    :catchall_18
    move-exception v0

    goto :goto_23

    :catchall_19
    move-exception v0

    goto :goto_22

    :catchall_1a
    move-exception v0

    move-object/from16 v22, v1

    :goto_22
    move-object/16 p2, v3

    goto :goto_23

    :catchall_1b
    move-exception v0

    move-object/from16 v22, v1

    move-object/16 p2, v3

    move-object/from16 v6, v222

    goto :goto_23

    :catchall_1c
    move-exception v0

    move-object/16 p2, v3

    move-object/from16 v6, v222

    move-object/from16 v22, v224

    :goto_23
    move-object/from16 v3, v230

    goto :goto_24

    :catchall_1d
    move-exception v0

    move-object v13, v3

    move-object/from16 v7, v45

    move-object/from16 v6, v222

    move-object/from16 v22, v224

    move-object v3, v2

    goto :goto_24

    :catchall_1e
    move-exception v0

    move-object v3, v2

    move-object v13, v4

    move-object/from16 v7, v45

    goto :goto_26

    :catchall_1f
    move-exception v0

    goto :goto_25

    :cond_21
    move-object/16 p2, v3

    move-object v13, v4

    move-object/from16 v7, v45

    move-object/from16 v1, v210

    move-object/from16 v3, v211

    move-object/from16 v6, v222

    move-object/from16 v22, v224

    .line 561
    :try_start_5c
    new-instance v0, Ljava/util/concurrent/CancellationException;

    invoke-direct {v0, v1}, Ljava/util/concurrent/CancellationException;-><init>(Ljava/lang/String;)V

    throw v0
    :try_end_5c
    .catchall {:try_start_5c .. :try_end_5c} :catchall_20

    :catchall_20
    move-exception v0

    :goto_24
    move-object/from16 v2, p0

    move-object v12, v3

    move-object v8, v6

    move-object v5, v7

    move-object v4, v13

    goto :goto_27

    :catchall_21
    move-exception v0

    move-object/16 p2, v3

    :goto_25
    move-object v13, v4

    move-object/from16 v7, v45

    move-object/from16 v3, v211

    :goto_26
    move-object/from16 v6, v222

    move-object/from16 v22, v224

    move-object/from16 v2, p0

    move-object v12, v3

    move-object v8, v6

    move-object v5, v7

    :goto_27
    move-object/from16 v11, v22

    move-object/from16 v15, v83

    move-object/from16 v1, v84

    move-object/from16 v31, v85

    move-object/from16 v7, p2

    :goto_28
    move-object v3, v0

    goto/16 :goto_46

    :catchall_22
    move-exception v0

    goto :goto_29

    :catchall_23
    move-exception v0

    move-object/from16 v24, v4

    goto :goto_29

    :catchall_24
    move-exception v0

    move-object/from16 v24, v4

    move-object/from16 v6, v22

    goto :goto_29

    :catchall_25
    move-exception v0

    move-object/from16 v6, v22

    move-object/from16 v24, v194

    :goto_29
    move-object/from16 v3, v211

    move-object/from16 v2, p0

    move-object v4, v6

    move-object v11, v9

    move-object v8, v12

    move-object v7, v13

    goto :goto_2b

    :catchall_26
    move-exception v0

    move-object v9, v5

    move-object v6, v13

    move-object/from16 v3, v44

    goto :goto_2a

    :catchall_27
    move-exception v0

    move-object v9, v5

    move-object v6, v13

    :goto_2a
    move-object/from16 v12, v49

    move-object/from16 v24, v194

    move-object v13, v7

    move-object/from16 v2, p0

    move-object v4, v6

    move-object v11, v9

    move-object v8, v12

    :goto_2b
    move-object v5, v14

    move-object/from16 v9, v24

    move-object/from16 v15, v83

    move-object/from16 v1, v84

    move-object/from16 v31, v85

    move-object v12, v3

    goto :goto_28

    :cond_22
    move-object/from16 v42, v9

    move-wide/from16 v29, v11

    move/from16 v21, v15

    move-object/from16 v56, v38

    move-object/from16 v12, v49

    move-object/from16 v22, v193

    move-object/from16 v24, v194

    move-object/from16 v27, v195

    move/from16 v36, v196

    move-wide/from16 v31, v197

    move-wide/from16 v33, v199

    move-wide/from16 v38, v201

    move-wide/from16 v44, v205

    move-wide/from16 v40, v207

    move-object v15, v4

    move-object v9, v5

    move-object v11, v6

    move-object v6, v13

    move-wide/from16 v4, v203

    move-object v13, v7

    move-wide v1, v4

    move-object v4, v6

    move-wide v6, v1

    move/from16 v229, v0

    move-object v1, v8

    move-object/from16 v232, v9

    move-object/from16 v231, v10

    move-object v2, v12

    move-object/from16 v47, v13

    move-object v5, v14

    move/from16 v10, v21

    move-object/from16 v60, v22

    move-object/from16 v9, v24

    move-object/from16 v12, v27

    move-object/from16 v24, v28

    move-wide/from16 v13, v29

    move-wide/from16 v29, v31

    move-wide/from16 v31, v33

    move/from16 v33, v36

    move-wide/from16 v233, v40

    move-object/from16 v8, v42

    move-object/from16 v34, v20

    goto/16 :goto_20

    .line 575
    :goto_2c
    :try_start_5d
    sget-object v0, Lcom/bachatas4/android/data/ImportManager;->INSTANCE:Lcom/bachatas4/android/data/ImportManager;
    :try_end_5d
    .catchall {:try_start_5d .. :try_end_5d} :catchall_3d

    move-object/from16 v89, v3

    :try_start_5e
    new-instance v3, Lcom/bachatas4/android/data/ImportProgress$Verifying;

    invoke-direct {v3, v1}, Lcom/bachatas4/android/data/ImportProgress$Verifying;-><init>(Ljava/lang/String;)V

    check-cast v3, Lcom/bachatas4/android/data/ImportProgress;

    invoke-virtual {v0, v3}, Lcom/bachatas4/android/data/ImportManager;->update(Lcom/bachatas4/android/data/ImportProgress;)V

    .line 576
    iget-object v0, v15, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    move-object/from16 v90, v0

    check-cast v90, Lcom/bachatas4/android/data/InstallJob;

    const-string v93, "VERIFYING"

    invoke-static {}, Ljava/lang/System;->currentTimeMillis()J

    move-result-wide v110

    const v114, 0x37ffb

    const/16 v115, 0x0

    const/16 v91, 0x0

    const/16 v92, 0x0

    const/16 v94, 0x0

    const/16 v95, 0x0

    const/16 v96, 0x0

    const/16 v97, 0x0

    const/16 v98, 0x0

    const/16 v99, 0x0

    const/16 v100, 0x0

    const/16 v101, 0x0

    const-wide/16 v102, 0x0

    const-wide/16 v104, 0x0

    const-wide/16 v106, 0x0

    const-wide/16 v108, 0x0

    const/16 v112, 0x0

    const/16 v113, 0x0

    invoke-static/range {v90 .. v115}, Lcom/bachatas4/android/data/InstallJob;->copy$default(Lcom/bachatas4/android/data/InstallJob;ILjava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;ZLjava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;JJJJJLjava/lang/String;Ljava/lang/String;ILjava/lang/Object;)Lcom/bachatas4/android/data/InstallJob;

    move-result-object v0

    iput-object v0, v15, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    .line 577
    iget-object v0, v15, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v0, Lcom/bachatas4/android/data/InstallJob;

    invoke-virtual {v2, v0}, Lcom/bachatas4/android/data/InstallJobStore;->update(Lcom/bachatas4/android/data/InstallJob;)V
    :try_end_5e
    .catchall {:try_start_5e .. :try_end_5e} :catchall_3c

    move-object/from16 v49, v2

    .line 578
    :try_start_5f
    const-string v2, "Verifying install\u2026"
    :try_end_5f
    .catchall {:try_start_5f .. :try_end_5f} :catchall_3b

    move-wide/from16 v20, v6

    const/4 v6, 0x6

    const/4 v7, 0x0

    const/4 v3, 0x0

    move-object/from16 v22, v4

    const/4 v4, 0x0

    move-object/from16 v27, v5

    const/4 v5, 0x1

    move-wide/from16 v247, v20

    move-object/from16 v238, v22

    move-wide/from16 v240, v29

    move-wide/from16 v242, v31

    move/from16 v239, v33

    move-wide/from16 v244, v44

    move-object/from16 v237, v56

    move/from16 v246, v229

    move/from16 v20, v10

    move-wide/from16 v21, v13

    move-object/from16 v14, v27

    move-object/from16 v13, v47

    move-object/from16 v10, v49

    move-object/from16 v49, v1

    move-object/from16 v27, v12

    move-object/from16 v12, v89

    move-object/from16 v1, p0

    :try_start_60
    invoke-static/range {v1 .. v7}, Lcom/bachatas4/android/service/ImportService;->updateNotification$default(Lcom/bachatas4/android/service/ImportService;Ljava/lang/String;IIZILjava/lang/Object;)V

    .line 579
    const-string v0, "pkg finalize start"

    invoke-static {v12, v0}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    .line 581
    new-instance v2, Ljava/io/File;

    iget-object v0, v13, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v0, Ljava/io/File;

    const-string v3, "sce_sys/param.sfo"

    invoke-direct {v2, v0, v3}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    .line 582
    invoke-virtual {v2}, Ljava/io/File;->isFile()Z

    move-result v0
    :try_end_60
    .catchall {:try_start_60 .. :try_end_60} :catchall_3a

    if-eqz v0, :cond_24

    .line 583
    :try_start_61
    sget-object v0, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    move-object v0, v1

    check-cast v0, Lcom/bachatas4/android/service/ImportService;

    sget-object v0, Lcom/bachatas4/android/data/ParamSfoReader;->INSTANCE:Lcom/bachatas4/android/data/ParamSfoReader;

    invoke-static {v2}, Lkotlin/io/FilesKt;->readBytes(Ljava/io/File;)[B

    move-result-object v3

    invoke-virtual {v0, v3}, Lcom/bachatas4/android/data/ParamSfoReader;->parse([B)Lcom/bachatas4/android/data/ParamSfoMetadata;

    move-result-object v0

    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v0
    :try_end_61
    .catchall {:try_start_61 .. :try_end_61} :catchall_28

    goto :goto_2d

    :catchall_28
    move-exception v0

    :try_start_62
    sget-object v3, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    invoke-static {v0}, Lkotlin/ResultKt;->createFailure(Ljava/lang/Throwable;)Ljava/lang/Object;

    move-result-object v0

    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v0

    :goto_2d
    invoke-static {v0}, Lkotlin/Result;->isFailure-impl(Ljava/lang/Object;)Z

    move-result v3

    if-eqz v3, :cond_23

    const/4 v0, 0x0

    :cond_23
    check-cast v0, Lcom/bachatas4/android/data/ParamSfoMetadata;
    :try_end_62
    .catchall {:try_start_62 .. :try_end_62} :catchall_29

    move-object/from16 v50, v0

    goto :goto_30

    :catchall_29
    move-exception v0

    :goto_2e
    move-object v3, v0

    move-object v2, v1

    :goto_2f
    move-object v8, v10

    move-object v7, v13

    move-object v5, v14

    move-object/from16 v15, v83

    move-object/from16 v1, v84

    move-object/from16 v31, v85

    move-object/from16 v11, v232

    move-object/from16 v4, v238

    goto/16 :goto_46

    :cond_24
    const/16 v50, 0x0

    .line 587
    :goto_30
    :try_start_63
    sget-object v48, Lcom/bachatas4/android/data/GameMetadataResolver;->INSTANCE:Lcom/bachatas4/android/data/GameMetadataResolver;

    const/16 v52, 0x4

    const/16 v53, 0x0

    const/16 v51, 0x0

    invoke-static/range {v48 .. v53}, Lcom/bachatas4/android/data/GameMetadataResolver;->resolve$default(Lcom/bachatas4/android/data/GameMetadataResolver;Ljava/lang/String;Lcom/bachatas4/android/data/ParamSfoMetadata;Lkotlin/jvm/functions/Function0;ILjava/lang/Object;)Lcom/bachatas4/android/data/ResolvedGameMetadata;

    move-result-object v0

    move-object/from16 v28, v49

    move-object/from16 v29, v50

    .line 591
    invoke-virtual {v0}, Lcom/bachatas4/android/data/ResolvedGameMetadata;->getId()Ljava/lang/String;

    move-result-object v3

    invoke-virtual {v0}, Lcom/bachatas4/android/data/ResolvedGameMetadata;->getTitle()Ljava/lang/String;

    move-result-object v4

    new-instance v5, Ljava/lang/StringBuilder;

    invoke-direct {v5}, Ljava/lang/StringBuilder;-><init>()V

    const-string v6, "pkg metadata id="

    invoke-virtual {v5, v6}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v5

    invoke-virtual {v5, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v3

    const-string v5, " title="

    invoke-virtual {v3, v5}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v3

    invoke-virtual {v3, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v3

    invoke-virtual {v3}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v3

    invoke-static {v12, v3}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    .line 593
    new-instance v3, Ljava/io/File;

    invoke-virtual {v0}, Lcom/bachatas4/android/data/ResolvedGameMetadata;->getId()Ljava/lang/String;

    move-result-object v4

    invoke-direct {v3, v8, v4}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    .line 594
    invoke-virtual {v3}, Ljava/io/File;->exists()Z

    move-result v4
    :try_end_63
    .catchall {:try_start_63 .. :try_end_63} :catchall_3a

    if-eqz v4, :cond_26

    .line 595
    :try_start_64
    sget-object v4, Lcom/bachatas4/android/data/GameInstallVerifier;->INSTANCE:Lcom/bachatas4/android/data/GameInstallVerifier;

    invoke-virtual {v1}, Lcom/bachatas4/android/service/ImportService;->getFilesDir()Ljava/io/File;

    move-result-object v5
    :try_end_64
    .catchall {:try_start_64 .. :try_end_64} :catchall_2b

    move-object/from16 v6, v43

    :try_start_65
    invoke-static {v5, v6}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullExpressionValue(Ljava/lang/Object;Ljava/lang/String;)V

    invoke-virtual {v0}, Lcom/bachatas4/android/data/ResolvedGameMetadata;->getId()Ljava/lang/String;

    move-result-object v7

    move-object/16 p1, v2

    new-instance v2, Ljava/lang/StringBuilder;

    invoke-direct {v2}, Ljava/lang/StringBuilder;-><init>()V

    move-object/16 p2, v3

    const-string v3, "games/"

    invoke-virtual {v2, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v2

    invoke-virtual {v2, v7}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v2

    invoke-virtual {v2}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v2

    invoke-virtual {v4, v5, v2}, Lcom/bachatas4/android/data/GameInstallVerifier;->canLaunch(Ljava/io/File;Ljava/lang/String;)Z

    move-result v2

    if-nez v2, :cond_25

    .line 598
    invoke-static/range {p2 .. p2}, Lkotlin/io/FilesKt;->deleteRecursively(Ljava/io/File;)Z

    goto :goto_31

    .line 596
    :cond_25
    sget-object v0, Lcom/bachatas4/android/data/InstallErrorCode;->ALREADY_INSTALLED:Lcom/bachatas4/android/data/InstallErrorCode;

    const-string v2, "Game already installed"

    invoke-direct {v1, v0, v2}, Lcom/bachatas4/android/service/ImportService;->failInstall(Lcom/bachatas4/android/data/InstallErrorCode;Ljava/lang/String;)Ljava/lang/Void;

    new-instance v0, Lkotlin/KotlinNothingValueException;

    invoke-direct {v0}, Lkotlin/KotlinNothingValueException;-><init>()V

    throw v0
    :try_end_65
    .catchall {:try_start_65 .. :try_end_65} :catchall_2a

    :catchall_2a
    move-exception v0

    move-object v3, v0

    move-object v2, v1

    move-object/from16 v43, v6

    goto/16 :goto_2f

    :catchall_2b
    move-exception v0

    move-object/from16 v6, v43

    goto/16 :goto_2e

    :cond_26
    move-object/16 p1, v2

    move-object/16 p2, v3

    move-object/from16 v6, v43

    .line 601
    :goto_31
    :try_start_66
    sget-object v2, Lcom/bachatas4/android/data/ImportManager;->INSTANCE:Lcom/bachatas4/android/data/ImportManager;

    new-instance v3, Lcom/bachatas4/android/data/ImportProgress$Registering;

    invoke-virtual {v0}, Lcom/bachatas4/android/data/ResolvedGameMetadata;->getTitle()Ljava/lang/String;

    move-result-object v4

    invoke-direct {v3, v4}, Lcom/bachatas4/android/data/ImportProgress$Registering;-><init>(Ljava/lang/String;)V

    check-cast v3, Lcom/bachatas4/android/data/ImportProgress;

    invoke-virtual {v2, v3}, Lcom/bachatas4/android/data/ImportManager;->update(Lcom/bachatas4/android/data/ImportProgress;)V

    .line 602
    iget-object v2, v15, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    move-object/from16 v86, v2

    check-cast v86, Lcom/bachatas4/android/data/InstallJob;

    .line 603
    const-string v89, "REGISTERING"

    .line 604
    invoke-virtual {v0}, Lcom/bachatas4/android/data/ResolvedGameMetadata;->getId()Ljava/lang/String;

    move-result-object v95

    .line 605
    invoke-static {}, Ljava/lang/System;->currentTimeMillis()J

    move-result-wide v106

    const v110, 0x37efb

    const/16 v111, 0x0

    const/16 v87, 0x0

    const/16 v88, 0x0

    const/16 v90, 0x0

    const/16 v91, 0x0

    const/16 v92, 0x0

    const/16 v93, 0x0

    const/16 v94, 0x0

    const/16 v96, 0x0

    const/16 v97, 0x0

    const-wide/16 v98, 0x0

    const-wide/16 v100, 0x0

    const-wide/16 v102, 0x0

    const-wide/16 v104, 0x0

    const/16 v108, 0x0

    const/16 v109, 0x0

    .line 602
    invoke-static/range {v86 .. v111}, Lcom/bachatas4/android/data/InstallJob;->copy$default(Lcom/bachatas4/android/data/InstallJob;ILjava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;ZLjava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;JJJJJLjava/lang/String;Ljava/lang/String;ILjava/lang/Object;)Lcom/bachatas4/android/data/InstallJob;

    move-result-object v2

    iput-object v2, v15, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    .line 607
    iget-object v2, v15, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v2, Lcom/bachatas4/android/data/InstallJob;

    invoke-virtual {v10, v2}, Lcom/bachatas4/android/data/InstallJobStore;->update(Lcom/bachatas4/android/data/InstallJob;)V

    .line 608
    const-string v2, "Registering game\u2026"
    :try_end_66
    .catchall {:try_start_66 .. :try_end_66} :catchall_39

    move-object/from16 v43, v6

    const/4 v6, 0x6

    const/4 v7, 0x0

    const/4 v3, 0x0

    const/4 v4, 0x0

    const/4 v5, 0x1

    move-object/from16 v30, p1

    move-object/from16 v31, p2

    move-object/from16 v32, v15

    move-object/from16 v15, v43

    :try_start_67
    invoke-static/range {v1 .. v7}, Lcom/bachatas4/android/service/ImportService;->updateNotification$default(Lcom/bachatas4/android/service/ImportService;Ljava/lang/String;IIZILjava/lang/Object;)V
    :try_end_67
    .catchall {:try_start_67 .. :try_end_67} :catchall_38

    .line 610
    :try_start_68
    invoke-virtual/range {p0 .. p0}, Lcom/bachatas4/android/service/ImportService;->getContentImporter()Lcom/bachatas4/android/data/ContentImporter;

    move-result-object v48

    .line 611
    new-instance v49, Lcom/bachatas4/android/data/ContentImportRequest;

    .line 612
    invoke-virtual {v0}, Lcom/bachatas4/android/data/ResolvedGameMetadata;->getId()Ljava/lang/String;

    move-result-object v58

    .line 613
    invoke-virtual {v0}, Lcom/bachatas4/android/data/ResolvedGameMetadata;->getTitle()Ljava/lang/String;

    move-result-object v59

    .line 615
    invoke-virtual {v0}, Lcom/bachatas4/android/data/ResolvedGameMetadata;->getSubtitle()Ljava/lang/String;

    move-result-object v63

    .line 616
    invoke-virtual {v0}, Lcom/bachatas4/android/data/ResolvedGameMetadata;->getDetail()Ljava/lang/String;

    move-result-object v64

    const/16 v65, 0x18

    const/16 v66, 0x0

    const/16 v61, 0x0

    const/16 v62, 0x0

    move-object/from16 v57, v49

    .line 611
    invoke-direct/range {v57 .. v66}, Lcom/bachatas4/android/data/ContentImportRequest;-><init>(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/Long;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;ILkotlin/jvm/internal/DefaultConstructorMarker;)V

    move-object/from16 v1, v60

    .line 618
    iget-object v3, v13, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    invoke-static {v3}, Lkotlin/jvm/internal/Intrinsics;->checkNotNull(Ljava/lang/Object;)V

    move-object/from16 v50, v3

    check-cast v50, Ljava/io/File;

    .line 619
    const-string v51, "pkg"

    .line 620
    iget-object v3, v11, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v3, Lcom/bachatas4/android/runtime/pkg/PkgProbeResult;

    invoke-virtual {v3}, Lcom/bachatas4/android/runtime/pkg/PkgProbeResult;->getContentId()Ljava/lang/String;

    move-result-object v52

    move-object/from16 v3, v231

    .line 610
    iput-object v1, v3, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$0:Ljava/lang/Object;
    :try_end_68
    .catchall {:try_start_68 .. :try_end_68} :catchall_37

    move-object/from16 v4, v232

    :try_start_69
    iput-object v4, v3, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$1:Ljava/lang/Object;

    iput-object v10, v3, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$2:Ljava/lang/Object;

    invoke-static/range {v32 .. v32}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v5

    iput-object v5, v3, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$3:Ljava/lang/Object;

    iput-object v13, v3, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$4:Ljava/lang/Object;

    iput-object v9, v3, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$5:Ljava/lang/Object;

    iput-object v14, v3, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$6:Ljava/lang/Object;

    invoke-static/range {v26 .. v26}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v5

    iput-object v5, v3, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$7:Ljava/lang/Object;

    iput-object v11, v3, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$8:Ljava/lang/Object;

    invoke-static/range {v16 .. v16}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v5

    iput-object v5, v3, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$9:Ljava/lang/Object;

    invoke-static/range {v28 .. v28}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v5

    iput-object v5, v3, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$10:Ljava/lang/Object;

    invoke-static {v8}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v5

    iput-object v5, v3, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$11:Ljava/lang/Object;

    invoke-static/range {v17 .. v17}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v5

    iput-object v5, v3, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$12:Ljava/lang/Object;

    move-object/from16 v5, v27

    iput-object v5, v3, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$13:Ljava/lang/Object;

    invoke-static/range {v34 .. v34}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v6

    iput-object v6, v3, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$14:Ljava/lang/Object;

    invoke-static/range {v18 .. v18}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v6

    iput-object v6, v3, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$15:Ljava/lang/Object;

    invoke-static/range {v24 .. v24}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v6

    iput-object v6, v3, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$16:Ljava/lang/Object;
    :try_end_69
    .catchall {:try_start_69 .. :try_end_69} :catchall_36

    move-object/from16 v6, v238

    :try_start_6a
    iput-object v6, v3, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$17:Ljava/lang/Object;

    invoke-static/range {v23 .. v23}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v7

    iput-object v7, v3, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$18:Ljava/lang/Object;

    invoke-static/range {v30 .. v30}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v7

    iput-object v7, v3, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$19:Ljava/lang/Object;

    invoke-static/range {v29 .. v29}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v7

    iput-object v7, v3, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$20:Ljava/lang/Object;

    iput-object v0, v3, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$21:Ljava/lang/Object;

    invoke-static/range {v31 .. v31}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v7

    iput-object v7, v3, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$22:Ljava/lang/Object;

    move/from16 v7, v239

    iput-boolean v7, v3, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->Z$0:Z
    :try_end_6a
    .catchall {:try_start_6a .. :try_end_6a} :catchall_35

    move-object/from16 v27, v4

    move-object/from16 v33, v5

    move-wide/from16 v4, v21

    :try_start_6b
    iput-wide v4, v3, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$0:J

    move-wide/from16 v21, v4

    move-wide/from16 v4, v240

    iput-wide v4, v3, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$1:J

    move-wide/from16 v240, v4

    move-wide/from16 v4, v242

    iput-wide v4, v3, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$2:J

    move-wide/from16 v242, v4

    move-wide/from16 v4, v235

    iput-wide v4, v3, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$3:J

    move-wide/from16 v38, v4

    move-wide/from16 v4, v233

    iput-wide v4, v3, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$4:J

    move-wide/from16 v40, v4

    move-wide/from16 v4, v244

    iput-wide v4, v3, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$5:J

    move-object/from16 v60, v1

    move/from16 v1, v246

    iput-boolean v1, v3, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->Z$1:Z

    move-wide/from16 v244, v4

    move-wide/from16 v4, v247

    iput-wide v4, v3, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$6:J

    move/from16 v246, v1

    move/from16 v1, v20

    iput v1, v3, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->I$0:I

    move/from16 v20, v1

    const/16 v1, 0x8

    iput v1, v3, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->label:I

    move-object/from16 v53, v3

    invoke-virtual/range {v48 .. v53}, Lcom/bachatas4/android/data/ContentImporter;->finalizeStagingTree(Lcom/bachatas4/android/data/ContentImportRequest;Ljava/io/File;Ljava/lang/String;Ljava/lang/String;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;

    move-result-object v1
    :try_end_6b
    .catchall {:try_start_6b .. :try_end_6b} :catchall_34

    move-object/from16 v3, v237

    if-ne v1, v3, :cond_27

    move-object v7, v3

    goto/16 :goto_35

    :cond_27
    move-object v2, v6

    move-object/16 p2, v8

    move-object/from16 v43, v15

    move-object/from16 v45, v26

    move-object/from16 v42, v28

    move-wide/from16 v254, v38

    move-wide/from16 v252, v40

    move-object/16 p1, v60

    move-wide/from16 v39, v240

    move-wide/from16 v250, v244

    move/from16 v249, v246

    move-object/from16 v38, v3

    move-object v15, v10

    move-object v3, v14

    move-object v10, v9

    move-object v14, v13

    move-object/from16 v9, v53

    move-object v13, v0

    move-object v0, v1

    move-object/from16 v1, v33

    move-object/from16 v33, v24

    move-wide/16 v256, v4

    move v4, v7

    move-wide/from16 v5, v21

    move-object/from16 v7, v27

    move-wide/from16 v26, v242

    move-object/from16 v22, v19

    move/from16 v19, v20

    move-wide/from16 v20, v256

    .line 321
    :goto_32
    :try_start_6c
    check-cast v0, Lcom/bachatas4/android/data/ContentImportResult;

    const/4 v8, 0x0

    .line 623
    iput-object v8, v14, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    const/4 v8, 0x1

    .line 624
    iput-boolean v8, v3, Lkotlin/jvm/internal/Ref$BooleanRef;->element:Z

    .line 626
    iget-object v8, v1, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v8, Ljava/lang/CharSequence;
    :try_end_6c
    .catchall {:try_start_6c .. :try_end_6c} :catchall_33

    if-eqz v8, :cond_29

    :try_start_6d
    invoke-static {v8}, Lkotlin/text/StringsKt;->isBlank(Ljava/lang/CharSequence;)Z

    move-result v8

    if-eqz v8, :cond_28

    goto :goto_33

    .line 627
    :cond_28
    iget-object v8, v1, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    move-wide/from16 v46, v5

    move-object/from16 v5, v25

    invoke-static {v8, v5}, Lkotlin/jvm/internal/Intrinsics;->areEqual(Ljava/lang/Object;Ljava/lang/Object;)Z

    move-result v5

    if-nez v5, :cond_2a

    .line 628
    iget-object v5, v11, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v5, Lcom/bachatas4/android/runtime/pkg/PkgProbeResult;

    invoke-virtual {v5}, Lcom/bachatas4/android/runtime/pkg/PkgProbeResult;->getContentId()Ljava/lang/String;

    move-result-object v5

    check-cast v5, Ljava/lang/CharSequence;

    invoke-static {v5}, Lkotlin/text/StringsKt;->isBlank(Ljava/lang/CharSequence;)Z

    move-result v5

    if-nez v5, :cond_2a

    .line 630
    invoke-virtual/range {p0 .. p0}, Lcom/bachatas4/android/service/ImportService;->getPkgKeyStore()Lcom/bachatas4/android/data/PkgKeyStore;

    move-result-object v5

    iget-object v6, v11, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v6, Lcom/bachatas4/android/runtime/pkg/PkgProbeResult;

    invoke-virtual {v6}, Lcom/bachatas4/android/runtime/pkg/PkgProbeResult;->getContentId()Ljava/lang/String;

    move-result-object v6

    iget-object v8, v1, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v8, Ljava/lang/String;

    invoke-virtual {v5, v6, v8}, Lcom/bachatas4/android/data/PkgKeyStore;->putPasscode(Ljava/lang/String;Ljava/lang/String;)V

    .line 631
    iget-object v5, v11, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v5, Lcom/bachatas4/android/runtime/pkg/PkgProbeResult;

    invoke-virtual {v5}, Lcom/bachatas4/android/runtime/pkg/PkgProbeResult;->getContentId()Ljava/lang/String;

    move-result-object v5

    new-instance v6, Ljava/lang/StringBuilder;

    invoke-direct {v6}, Ljava/lang/StringBuilder;-><init>()V

    const-string v8, "pkg keydb saved for contentId="

    invoke-virtual {v6, v8}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v6

    invoke-virtual {v6, v5}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v5

    invoke-virtual {v5}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v5

    invoke-static {v12, v5}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I
    :try_end_6d
    .catchall {:try_start_6d .. :try_end_6d} :catchall_2c

    goto :goto_34

    :catchall_2c
    move-exception v0

    move-object v4, v2

    move-object v5, v3

    move-object v11, v7

    move-object v9, v10

    move-object v7, v14

    move-object v8, v15

    move-object/from16 v15, v83

    move-object/from16 v1, v84

    move-object/from16 v31, v85

    move-object/from16 v2, p0

    goto/16 :goto_28

    :cond_29
    :goto_33
    move-wide/from16 v46, v5

    .line 634
    :cond_2a
    :goto_34
    :try_start_6e
    invoke-virtual/range {p0 .. p0}, Lcom/bachatas4/android/service/ImportService;->getGameRepository()Lcom/bachatas4/android/data/GameRepository;

    move-result-object v5

    invoke-static {}, Ljava/lang/System;->currentTimeMillis()J

    move-result-wide v24

    invoke-static/range {p1 .. p1}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v6

    iput-object v6, v9, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$0:Ljava/lang/Object;

    iput-object v7, v9, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$1:Ljava/lang/Object;

    iput-object v15, v9, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$2:Ljava/lang/Object;

    invoke-static/range {v32 .. v32}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v6

    iput-object v6, v9, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$3:Ljava/lang/Object;

    iput-object v14, v9, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$4:Ljava/lang/Object;

    iput-object v10, v9, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$5:Ljava/lang/Object;

    iput-object v3, v9, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$6:Ljava/lang/Object;

    invoke-static/range {v45 .. v45}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v6

    iput-object v6, v9, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$7:Ljava/lang/Object;

    invoke-static {v11}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v6

    iput-object v6, v9, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$8:Ljava/lang/Object;

    invoke-static/range {v16 .. v16}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v6

    iput-object v6, v9, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$9:Ljava/lang/Object;

    invoke-static/range {v42 .. v42}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v6

    iput-object v6, v9, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$10:Ljava/lang/Object;

    invoke-static/range {p2 .. p2}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v6

    iput-object v6, v9, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$11:Ljava/lang/Object;

    invoke-static/range {v17 .. v17}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v6

    iput-object v6, v9, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$12:Ljava/lang/Object;

    invoke-static {v1}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v1

    iput-object v1, v9, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$13:Ljava/lang/Object;

    invoke-static/range {v34 .. v34}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v1

    iput-object v1, v9, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$14:Ljava/lang/Object;

    invoke-static/range {v18 .. v18}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v1

    iput-object v1, v9, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$15:Ljava/lang/Object;

    invoke-static/range {v33 .. v33}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v1

    iput-object v1, v9, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$16:Ljava/lang/Object;

    iput-object v2, v9, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$17:Ljava/lang/Object;

    invoke-static/range {v23 .. v23}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v1

    iput-object v1, v9, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$18:Ljava/lang/Object;

    invoke-static/range {v30 .. v30}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v1

    iput-object v1, v9, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$19:Ljava/lang/Object;

    invoke-static/range {v29 .. v29}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v1

    iput-object v1, v9, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$20:Ljava/lang/Object;

    iput-object v13, v9, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$21:Ljava/lang/Object;

    invoke-static/range {v31 .. v31}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v1

    iput-object v1, v9, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$22:Ljava/lang/Object;

    iput-object v0, v9, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->L$23:Ljava/lang/Object;

    iput-boolean v4, v9, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->Z$0:Z
    :try_end_6e
    .catchall {:try_start_6e .. :try_end_6e} :catchall_33

    move-object v11, v2

    move-wide/from16 v1, v46

    :try_start_6f
    iput-wide v1, v9, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$0:J

    move-wide/from16 v1, v39

    iput-wide v1, v9, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$1:J

    move-wide/from16 v1, v26

    iput-wide v1, v9, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$2:J

    move-wide/from16 v1, v254

    iput-wide v1, v9, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$3:J

    move-wide/from16 v1, v252

    iput-wide v1, v9, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$4:J

    move-wide/from16 v1, v250

    iput-wide v1, v9, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$5:J

    move/from16 v6, v249

    iput-boolean v6, v9, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->Z$1:Z

    move-wide/from16 v1, v20

    iput-wide v1, v9, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->J$6:J

    move/from16 v1, v19

    iput v1, v9, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->I$0:I

    const/16 v1, 0x9

    iput v1, v9, Lcom/bachatas4/android/service/ImportService$runPkgImport$1;->label:I
    :try_end_6f
    .catchall {:try_start_6f .. :try_end_6f} :catchall_32

    move-object/from16 v6, p1

    move-object v4, v5

    move-object/from16 v51, v7

    move-wide/from16 v7, v24

    move-object v5, v0

    :try_start_70
    invoke-virtual/range {v4 .. v9}, Lcom/bachatas4/android/data/GameRepository;->addImportedGame(Lcom/bachatas4/android/data/ContentImportResult;Ljava/lang/String;JLkotlin/coroutines/Continuation;)Ljava/lang/Object;

    move-result-object v0
    :try_end_70
    .catchall {:try_start_70 .. :try_end_70} :catchall_31

    move-object/from16 v7, v38

    if-ne v0, v7, :cond_2b

    :goto_35
    return-object v7

    :cond_2b
    move-object v1, v5

    move-object v6, v10

    move-object v4, v11

    move-object v7, v14

    move-object v8, v15

    move-object/from16 v0, v22

    move-object/from16 v11, v51

    move-object v5, v3

    move-object v3, v13

    .line 635
    :goto_36
    :try_start_71
    invoke-virtual {v8, v11}, Lcom/bachatas4/android/data/InstallJobStore;->delete(Ljava/lang/String;)V

    .line 636
    sget-object v2, Lcom/bachatas4/android/data/ImportManager;->INSTANCE:Lcom/bachatas4/android/data/ImportManager;

    new-instance v9, Lcom/bachatas4/android/data/ImportProgress$Installed;

    invoke-virtual {v3}, Lcom/bachatas4/android/data/ResolvedGameMetadata;->getId()Ljava/lang/String;

    move-result-object v10

    invoke-virtual {v3}, Lcom/bachatas4/android/data/ResolvedGameMetadata;->getTitle()Ljava/lang/String;

    move-result-object v13

    invoke-direct {v9, v10, v13}, Lcom/bachatas4/android/data/ImportProgress$Installed;-><init>(Ljava/lang/String;Ljava/lang/String;)V

    check-cast v9, Lcom/bachatas4/android/data/ImportProgress;

    invoke-virtual {v2, v9}, Lcom/bachatas4/android/data/ImportManager;->update(Lcom/bachatas4/android/data/ImportProgress;)V

    .line 637
    invoke-virtual {v3}, Lcom/bachatas4/android/data/ResolvedGameMetadata;->getId()Ljava/lang/String;

    move-result-object v2

    invoke-virtual {v1}, Lcom/bachatas4/android/data/ContentImportResult;->getBytesCopied()J

    move-result-wide v9

    new-instance v1, Ljava/lang/StringBuilder;

    invoke-direct {v1}, Ljava/lang/StringBuilder;-><init>()V

    const-string v13, "pkg import success id="

    invoke-virtual {v1, v13}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    const-string v2, " bytes="

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1, v9, v10}, Ljava/lang/StringBuilder;->append(J)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v1

    invoke-static {v12, v1}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    .line 638
    invoke-virtual {v3}, Lcom/bachatas4/android/data/ResolvedGameMetadata;->getTitle()Ljava/lang/String;

    move-result-object v1

    new-instance v2, Ljava/lang/StringBuilder;

    invoke-direct {v2}, Ljava/lang/StringBuilder;-><init>()V

    invoke-virtual {v2, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    const-string v2, " installed"

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v1
    :try_end_71
    .catchall {:try_start_71 .. :try_end_71} :catchall_30

    const/4 v3, 0x2

    const/4 v10, 0x0

    move-object/from16 v2, p0

    move/from16 v9, v54

    :try_start_72
    invoke-static {v2, v1, v9, v3, v10}, Lcom/bachatas4/android/service/ImportService;->notifyDone$default(Lcom/bachatas4/android/service/ImportService;Ljava/lang/String;ZILjava/lang/Object;)V

    .line 639
    sget-object v1, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;
    :try_end_72
    .catchall {:try_start_72 .. :try_end_72} :catchall_2f

    .line 525
    :try_start_73
    invoke-static {v4, v0}, Lkotlin/io/CloseableKt;->closeFinally(Ljava/io/Closeable;Ljava/lang/Throwable;)V
    :try_end_73
    .catchall {:try_start_73 .. :try_end_73} :catchall_2e

    .line 646
    iget-boolean v0, v5, Lkotlin/jvm/internal/Ref$BooleanRef;->element:Z

    if-nez v0, :cond_2d

    .line 647
    iget-object v0, v7, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v0, Ljava/io/File;

    if-eqz v0, :cond_2c

    invoke-virtual {v0}, Ljava/io/File;->getAbsolutePath()Ljava/lang/String;

    move-result-object v11

    goto :goto_37

    :cond_2c
    const/4 v11, 0x0

    :goto_37
    new-instance v0, Ljava/lang/StringBuilder;

    move-object/from16 v1, v84

    invoke-direct {v0, v1}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v0, v11}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    invoke-static {v12, v0}, Landroid/util/Log;->w(Ljava/lang/String;Ljava/lang/String;)I

    .line 648
    iget-object v0, v7, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v0, Ljava/io/File;

    if-eqz v0, :cond_2d

    invoke-static {v0}, Lkotlin/io/FilesKt;->deleteRecursively(Ljava/io/File;)Z

    move-result v0

    invoke-static {v0}, Lkotlin/coroutines/jvm/internal/Boxing;->boxBoolean(Z)Ljava/lang/Boolean;

    :cond_2d
    if-eqz v6, :cond_2e

    .line 651
    invoke-virtual {v6}, Ljava/io/File;->getAbsolutePath()Ljava/lang/String;

    move-result-object v0

    new-instance v1, Ljava/lang/StringBuilder;

    move-object/from16 v9, v85

    invoke-direct {v1, v9}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v1, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    invoke-static {v12, v0}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    .line 652
    :try_start_74
    sget-object v0, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    move-object v0, v2

    check-cast v0, Lcom/bachatas4/android/service/ImportService;

    invoke-virtual {v6}, Ljava/io/File;->delete()Z

    move-result v0

    invoke-static {v0}, Lkotlin/coroutines/jvm/internal/Boxing;->boxBoolean(Z)Ljava/lang/Boolean;

    move-result-object v0

    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v0
    :try_end_74
    .catchall {:try_start_74 .. :try_end_74} :catchall_2d

    goto :goto_38

    :catchall_2d
    move-exception v0

    sget-object v1, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    invoke-static {v0}, Lkotlin/ResultKt;->createFailure(Ljava/lang/Throwable;)Ljava/lang/Object;

    move-result-object v0

    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v0

    :goto_38
    invoke-static {v0}, Lkotlin/Result;->box-impl(Ljava/lang/Object;)Lkotlin/Result;

    :cond_2e
    const/4 v4, 0x0

    .line 654
    iput-object v4, v2, Lcom/bachatas4/android/service/ImportService;->passcodeWaiter:Lkotlinx/coroutines/CompletableDeferred;

    .line 655
    iput-object v4, v2, Lcom/bachatas4/android/service/ImportService;->copyConfirmWaiter:Lkotlinx/coroutines/CompletableDeferred;

    .line 656
    sget-object v0, Lcom/bachatas4/android/data/ImportManager;->INSTANCE:Lcom/bachatas4/android/data/ImportManager;

    const/4 v1, 0x1

    invoke-static {v0, v4, v1, v4}, Lcom/bachatas4/android/data/ImportManager;->isBusy$default(Lcom/bachatas4/android/data/ImportManager;Lcom/bachatas4/android/data/ImportProgress;ILjava/lang/Object;)Z

    move-result v0

    if-eqz v0, :cond_2f

    sget-object v0, Lcom/bachatas4/android/data/ImportManager;->INSTANCE:Lcom/bachatas4/android/data/ImportManager;

    invoke-virtual {v0}, Lcom/bachatas4/android/data/ImportManager;->reset()V

    .line 657
    :cond_2f
    iget-boolean v0, v5, Lkotlin/jvm/internal/Ref$BooleanRef;->element:Z

    new-instance v1, Ljava/lang/StringBuilder;

    move-object/from16 v13, v83

    invoke-direct {v1, v13}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v1, v0}, Ljava/lang/StringBuilder;->append(Z)Ljava/lang/StringBuilder;

    move-result-object v0

    move-object/from16 v3, v82

    invoke-virtual {v0, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    invoke-static {v12, v0}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    .line 658
    invoke-virtual {v2}, Lcom/bachatas4/android/service/ImportService;->stopSelf()V

    goto/16 :goto_6a

    :catchall_2e
    move-exception v0

    move-object/from16 v3, v82

    move-object/from16 v13, v83

    move-object/from16 v1, v84

    move-object/from16 v9, v85

    move-object v4, v5

    move-object/from16 v46, v6

    move-object v15, v13

    move-object v13, v9

    move-object v9, v1

    move-object v1, v2

    move-object v2, v11

    move-object v11, v3

    move-object v3, v8

    move-object v8, v7

    goto/16 :goto_67

    :catchall_2f
    move-exception v0

    goto :goto_39

    :catchall_30
    move-exception v0

    move-object/from16 v2, p0

    :goto_39
    move-object/from16 v3, v82

    move-object/from16 v13, v83

    move-object/from16 v1, v84

    move-object/from16 v9, v85

    move-object/from16 v31, v9

    move-object v15, v13

    move-object v3, v0

    goto/16 :goto_1

    :catchall_31
    move-exception v0

    move-object/from16 v2, p0

    goto :goto_3a

    :catchall_32
    move-exception v0

    move-object/from16 v2, p0

    move-object/from16 v51, v7

    :goto_3a
    move-object/from16 v13, v83

    move-object/from16 v1, v84

    move-object/from16 v9, v85

    goto :goto_3b

    :catchall_33
    move-exception v0

    move-object v11, v2

    move-object/from16 v51, v7

    move-object/from16 v13, v83

    move-object/from16 v1, v84

    move-object/from16 v9, v85

    move-object/from16 v2, p0

    :goto_3b
    move-object v5, v3

    move-object/from16 v31, v9

    move-object v9, v10

    move-object v4, v11

    move-object v7, v14

    move-object v8, v15

    move-object/from16 v11, v51

    move-object v3, v0

    move-object v15, v13

    goto/16 :goto_46

    :catchall_34
    move-exception v0

    move-object/from16 v2, p0

    goto :goto_3c

    :catchall_35
    move-exception v0

    move-object/from16 v2, p0

    move-object/from16 v27, v4

    :goto_3c
    move-object/from16 v43, v15

    move-object/from16 v15, v83

    move-object/from16 v1, v84

    move-object/from16 v31, v85

    goto :goto_40

    :catchall_36
    move-exception v0

    move-object/from16 v2, p0

    move-object/from16 v27, v4

    move-object/from16 v43, v15

    move-object/from16 v15, v83

    move-object/from16 v1, v84

    move-object/from16 v31, v85

    goto :goto_3f

    :catchall_37
    move-exception v0

    move-object/from16 v2, p0

    goto :goto_3d

    :catchall_38
    move-exception v0

    move-object v2, v1

    :goto_3d
    move-object/from16 v43, v15

    goto :goto_3e

    :catchall_39
    move-exception v0

    move-object v2, v1

    move-object/from16 v43, v6

    goto :goto_3e

    :catchall_3a
    move-exception v0

    move-object v2, v1

    :goto_3e
    move-object/from16 v15, v83

    move-object/from16 v1, v84

    move-object/from16 v31, v85

    move-object/from16 v27, v232

    :goto_3f
    move-object/from16 v6, v238

    :goto_40
    move-object v3, v0

    move-object v4, v6

    move-object v8, v10

    move-object v7, v13

    move-object v5, v14

    goto :goto_43

    :catchall_3b
    move-exception v0

    move-object/from16 v2, p0

    move-object v6, v4

    move-object v14, v5

    move-object/from16 v13, v47

    move-object/from16 v10, v49

    move-object/from16 v15, v83

    move-object/from16 v1, v84

    move-object/from16 v31, v85

    move-object/from16 v12, v89

    move-object/from16 v27, v232

    goto :goto_42

    :catchall_3c
    move-exception v0

    move-object v10, v2

    move-object v6, v4

    move-object v14, v5

    move-object/from16 v13, v47

    move-object/from16 v15, v83

    move-object/from16 v1, v84

    move-object/from16 v31, v85

    move-object/from16 v12, v89

    goto :goto_41

    :catchall_3d
    move-exception v0

    move-object v10, v2

    move-object v12, v3

    move-object v6, v4

    move-object v14, v5

    move-object/from16 v13, v47

    move-object/from16 v15, v83

    move-object/from16 v1, v84

    move-object/from16 v31, v85

    :goto_41
    move-object/from16 v27, v232

    move-object/from16 v2, p0

    :goto_42
    move-object v3, v0

    move-object v8, v10

    move-object v7, v13

    :goto_43
    move-object/from16 v11, v27

    goto/16 :goto_46

    :catchall_3e
    move-exception v0

    move-object/from16 v2, p0

    move-object v12, v3

    move-object v9, v5

    move-object v6, v13

    move-object/from16 v15, v83

    move-object/from16 v1, v84

    move-object/from16 v31, v85

    move-object/from16 v24, v194

    move-object v13, v7

    move-object v3, v0

    move-object v4, v6

    move-object v11, v9

    move-object v5, v14

    move-object/from16 v9, v24

    goto :goto_45

    :catchall_3f
    move-exception v0

    move-object/from16 v2, p0

    move-object/from16 v29, v1

    move-object v12, v9

    move-object/from16 v30, v15

    move-object/from16 v191, v21

    move-object/from16 v8, v49

    move-object/from16 v15, v83

    move-object/from16 v1, v84

    move-object/from16 v31, v85

    move-object v9, v5

    move-object v3, v0

    move-object v11, v14

    move-object/from16 v7, v29

    move-object/from16 v9, v30

    move-object/from16 v4, v191

    goto :goto_46

    :catchall_40
    move-exception v0

    move-object/from16 v2, p0

    goto :goto_44

    :catchall_41
    move-exception v0

    move-object/from16 v2, p0

    move-object/from16 v30, v6

    :goto_44
    move-object v12, v9

    move-object/from16 v15, v83

    move-object/from16 v1, v84

    move-object/from16 v31, v85

    move-object v3, v0

    move-object/from16 v4, v21

    move-object/from16 v7, v29

    move-object/from16 v9, v30

    move-object/from16 v5, v45

    :goto_45
    move-object/from16 v8, v49

    .line 525
    :goto_46
    :try_start_75
    throw v3
    :try_end_75
    .catchall {:try_start_75 .. :try_end_75} :catchall_42

    :catchall_42
    move-exception v0

    :try_start_76
    invoke-static {v4, v3}, Lkotlin/io/CloseableKt;->closeFinally(Ljava/io/Closeable;Ljava/lang/Throwable;)V

    throw v0
    :try_end_76
    .catchall {:try_start_76 .. :try_end_76} :catchall_43

    :catchall_43
    move-exception v0

    move-object v4, v5

    move-object v3, v8

    move-object/from16 v46, v9

    move-object/from16 v13, v31

    move-object v9, v1

    move-object v1, v2

    move-object v8, v7

    move-object v2, v11

    goto :goto_47

    :catchall_44
    move-exception v0

    move-object/from16 v2, p0

    move-object/from16 v30, v6

    move-object v12, v9

    move-object/from16 v15, v83

    move-object/from16 v1, v84

    move-object/from16 v31, v85

    move-object v9, v1

    move-object v1, v2

    move-object v2, v11

    move-object/from16 v8, v29

    move-object/from16 v46, v30

    move-object/from16 v13, v31

    move-object/from16 v4, v45

    move-object/from16 v3, v49

    goto :goto_47

    :catchall_45
    move-exception v0

    move-object/from16 v2, p0

    move-object v12, v9

    move-object/from16 v15, v83

    move-object/from16 v1, v84

    move-object/from16 v31, v85

    move-object v9, v1

    move-object v1, v2

    move-object/from16 v46, v4

    move-object/from16 v8, v29

    move-object/from16 v13, v31

    move-object/from16 v4, v45

    move-object/from16 v3, v49

    move-object/from16 v2, v50

    :goto_47
    move-object/from16 v11, v82

    goto/16 :goto_67

    :catchall_46
    move-exception v0

    move-object v2, v1

    move-object v12, v9

    move-object/from16 v15, v83

    move-object/from16 v1, v84

    move-object/from16 v31, v85

    move-object v9, v1

    move-object v1, v2

    move-object/from16 v46, v3

    move-object/from16 v2, v20

    move-object/from16 v8, v29

    goto/16 :goto_4c

    :catchall_47
    move-exception v0

    move-object/from16 v2, p0

    move-object/from16 v29, v8

    move-object v12, v9

    move-object/from16 v49, v17

    move-object/from16 v3, v19

    move-object/from16 v15, v83

    move-object/from16 v1, v84

    move-object/from16 v31, v85

    goto :goto_4b

    :catchall_48
    move-exception v0

    move-object/from16 v34, v2

    move-object/from16 v29, v8

    move-object v12, v9

    goto :goto_48

    :catchall_49
    move-exception v0

    move-object/from16 v34, v2

    move-object/from16 v29, v8

    move-object v12, v9

    move-object/from16 v20, v11

    :goto_48
    move-object/from16 v49, v17

    goto :goto_49

    :catchall_4a
    move-exception v0

    move-object/from16 v49, v1

    move-object/from16 v34, v2

    move-object/from16 v29, v8

    move-object v12, v9

    move-object/from16 v20, v11

    :goto_49
    move-object/from16 v3, v19

    goto :goto_4a

    :catchall_4b
    move-exception v0

    move-object v3, v1

    move-object/from16 v34, v2

    move-object/from16 v29, v8

    move-object v12, v9

    move-object/from16 v20, v11

    move-object/from16 v49, v17

    :goto_4a
    move-object/from16 v15, v83

    move-object/from16 v1, v84

    move-object/from16 v31, v85

    move-object/from16 v2, p0

    :goto_4b
    move-object v9, v1

    move-object v1, v2

    move-object/from16 v46, v3

    move-object/from16 v2, v20

    :goto_4c
    move-object/from16 v13, v31

    move-object/from16 v3, v34

    move-object/from16 v4, v49

    goto :goto_47

    :catchall_4c
    move-exception v0

    move-object/from16 v34, v2

    move-object/from16 v29, v8

    move-object v12, v9

    move-object/from16 v20, v11

    move-object/from16 v49, v17

    move-object/from16 v15, v83

    move-object/from16 v1, v84

    move-object/from16 v31, v85

    move-object/from16 v2, p0

    move-object v9, v1

    goto/16 :goto_4e

    :cond_30
    move-object/from16 v34, v2

    move-wide v3, v4

    move-wide/16 p1, v6

    move-object/from16 v29, v8

    move-object v12, v9

    move-object/from16 v49, v17

    move-wide/from16 v5, v19

    move-object/from16 v15, v83

    move-object/from16 v9, v84

    move-object/from16 v31, v85

    move-object/from16 v2, p0

    move-object/from16 v20, v11

    move-wide/from16 v10, v168

    .line 474
    :try_start_77
    sget-object v0, Lcom/bachatas4/android/service/ImportService;->Companion:Lcom/bachatas4/android/service/ImportService$Companion;

    invoke-virtual {v0, v3, v4}, Lcom/bachatas4/android/service/ImportService$Companion;->formatBytes(J)Ljava/lang/String;

    move-result-object v3

    .line 475
    invoke-virtual {v0, v5, v6}, Lcom/bachatas4/android/service/ImportService$Companion;->formatBytes(J)Ljava/lang/String;

    move-result-object v4

    invoke-virtual {v0, v10, v11}, Lcom/bachatas4/android/service/ImportService$Companion;->formatBytes(J)Ljava/lang/String;

    move-result-object v5

    move-wide/from16 v6, p1

    .line 476
    invoke-virtual {v0, v6, v7}, Lcom/bachatas4/android/service/ImportService$Companion;->formatBytes(J)Ljava/lang/String;

    move-result-object v0

    new-instance v6, Ljava/lang/StringBuilder;

    move-object/from16 v10, v90

    invoke-direct {v6, v10}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v6, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v3

    const-string v6, " free (package "

    invoke-virtual {v3, v6}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v3

    invoke-virtual {v3, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v3

    const-string v4, " + extract "

    invoke-virtual {v3, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v3

    invoke-virtual {v3, v5}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v3

    const-string v4, ") but only "

    invoke-virtual {v3, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v3

    invoke-virtual {v3, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    move-object/from16 v3, v75

    invoke-virtual {v0, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    .line 472
    invoke-direct {v2, v1, v0}, Lcom/bachatas4/android/service/ImportService;->failInstall(Lcom/bachatas4/android/data/InstallErrorCode;Ljava/lang/String;)Ljava/lang/Void;

    new-instance v0, Lkotlin/KotlinNothingValueException;

    invoke-direct {v0}, Lkotlin/KotlinNothingValueException;-><init>()V

    throw v0

    :catchall_4d
    move-exception v0

    move-object/from16 v34, v2

    move-object/from16 v29, v8

    move-object v12, v9

    move-object/from16 v20, v11

    move-object/from16 v49, v17

    goto :goto_4d

    :catchall_4e
    move-exception v0

    move-object/from16 v34, v2

    move-object/from16 v29, v8

    move-object/from16 v20, v11

    move-object/from16 v49, v17

    move-object/from16 v12, v44

    :goto_4d
    move-object/from16 v15, v83

    move-object/from16 v9, v84

    move-object/from16 v31, v85

    move-object/from16 v2, p0

    :goto_4e
    move-object v1, v2

    goto :goto_4f

    :cond_31
    move-object/from16 v34, v2

    move-object/from16 v29, v8

    move-object/from16 v20, v11

    move-object/from16 v49, v17

    move-object/from16 v12, v44

    move-object/from16 v15, v83

    move-object/from16 v9, v84

    move-object/from16 v31, v85

    move-object v2, v1

    move-object/from16 v1, v86

    .line 465
    new-instance v0, Ljava/util/concurrent/CancellationException;

    invoke-direct {v0, v1}, Ljava/util/concurrent/CancellationException;-><init>(Ljava/lang/String;)V

    throw v0
    :try_end_77
    .catchall {:try_start_77 .. :try_end_77} :catchall_4f

    :catchall_4f
    move-exception v0

    move-object v1, v2

    move-object/from16 v2, v20

    move-object/from16 v8, v29

    goto :goto_50

    :catchall_50
    move-exception v0

    move-object/from16 v34, v2

    move-object/from16 v29, v8

    move-object/from16 v20, v11

    move-object/from16 v49, v17

    move-object/from16 v12, v44

    move-object/from16 v15, v83

    move-object/from16 v9, v84

    move-object/from16 v31, v85

    move-object v2, v1

    :goto_4f
    move-object/from16 v2, v20

    :goto_50
    move-object/from16 v13, v31

    move-object/from16 v3, v34

    move-object/from16 v4, v49

    :goto_51
    move-object/from16 v11, v82

    goto/16 :goto_66

    :catchall_51
    move-exception v0

    move-object v2, v1

    goto :goto_52

    :catchall_52
    move-exception v0

    move-object v2, v1

    move-object/from16 v19, v6

    :goto_52
    move-object/from16 v18, v7

    goto :goto_53

    :catchall_53
    move-exception v0

    move-object v2, v1

    move-object/from16 v19, v6

    goto :goto_53

    :catchall_54
    move-exception v0

    move-object v2, v1

    :goto_53
    move-object/from16 v16, v12

    move-object v4, v15

    move-object/from16 v12, v44

    move-object/from16 v15, v83

    move-object/from16 v9, v84

    move-object/from16 v31, v85

    goto :goto_54

    :catchall_55
    move-exception v0

    move-object/from16 v2, p0

    move-object/from16 v16, v12

    move-object v4, v15

    move-object/from16 v15, v83

    move-object/from16 v9, v84

    move-object/from16 v31, v85

    move-object v12, v11

    move-object v1, v2

    :goto_54
    move-object/from16 v3, v16

    move-object/from16 v8, v18

    move-object/from16 v2, v19

    move-object/from16 v13, v31

    goto :goto_51

    :cond_32
    move-wide v7, v5

    move-object/from16 v16, v12

    move-object v4, v15

    move-object/from16 v15, v83

    move-object/from16 v9, v84

    move-object/from16 v13, v85

    move-object/from16 v10, v90

    move-wide v5, v2

    move-object v12, v11

    move-object/from16 v3, v75

    move-object/from16 v11, v82

    move-object/from16 v2, p0

    .line 439
    :try_start_78
    sget-object v0, Lcom/bachatas4/android/service/ImportService;->Companion:Lcom/bachatas4/android/service/ImportService$Companion;

    invoke-virtual {v0, v5, v6}, Lcom/bachatas4/android/service/ImportService$Companion;->formatBytes(J)Ljava/lang/String;

    move-result-object v5

    .line 440
    invoke-virtual {v0, v7, v8}, Lcom/bachatas4/android/service/ImportService$Companion;->formatBytes(J)Ljava/lang/String;

    move-result-object v0

    new-instance v6, Ljava/lang/StringBuilder;

    invoke-direct {v6, v10}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v6, v5}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v5

    const-string v6, " free but only "

    invoke-virtual {v5, v6}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v5

    invoke-virtual {v5, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    .line 437
    invoke-direct {v2, v1, v0}, Lcom/bachatas4/android/service/ImportService;->failInstall(Lcom/bachatas4/android/data/InstallErrorCode;Ljava/lang/String;)Ljava/lang/Void;

    new-instance v0, Lkotlin/KotlinNothingValueException;

    invoke-direct {v0}, Lkotlin/KotlinNothingValueException;-><init>()V

    throw v0
    :try_end_78
    .catchall {:try_start_78 .. :try_end_78} :catchall_56

    :catchall_56
    move-exception v0

    goto/16 :goto_58

    :catchall_57
    move-exception v0

    move-object/from16 v2, p0

    move-object v12, v11

    move-object v4, v15

    move-object/from16 v11, v82

    move-object/from16 v15, v83

    move-object/from16 v9, v84

    move-object/from16 v13, v85

    goto :goto_58

    :catchall_58
    move-exception v0

    move-object/from16 v2, p0

    move-object/from16 v16, v12

    move-object v4, v15

    goto :goto_57

    :catchall_59
    move-exception v0

    move-object v2, v1

    move-object/from16 v16, v12

    move-object v4, v15

    move-object/from16 v15, v83

    move-object/from16 v9, v84

    move-object/from16 v13, v85

    move-object v12, v11

    move-object/from16 v11, v82

    goto :goto_59

    :catchall_5a
    move-exception v0

    move-object/from16 v2, p0

    move-object/from16 v4, p1

    move-object/from16 v16, v12

    goto :goto_57

    :catchall_5b
    move-exception v0

    move-object/from16 v2, p0

    move-object/from16 v4, p1

    move-object/from16 v16, v12

    move-object/from16 v19, v14

    goto :goto_57

    :catchall_5c
    move-exception v0

    move-object/from16 v2, p0

    move-object/from16 v4, p1

    goto :goto_56

    :catchall_5d
    move-exception v0

    move-object/from16 v4, p1

    goto :goto_55

    :catchall_5e
    move-exception v0

    move-object v4, v1

    :goto_55
    move-object v2, v9

    :goto_56
    move-object/from16 v16, v12

    move-object/from16 v19, v14

    move-object/from16 v18, v15

    :goto_57
    move-object/from16 v15, v83

    move-object/from16 v9, v84

    move-object/from16 v13, v85

    move-object v12, v11

    move-object/from16 v11, v82

    :goto_58
    move-object v1, v2

    :goto_59
    move-object/from16 v3, v16

    move-object/from16 v8, v18

    goto/16 :goto_5d

    :catch_2
    move-exception v0

    move-object v4, v1

    move-object v2, v9

    move-object/from16 v16, v12

    move-object/from16 v19, v14

    move-object/from16 v18, v15

    move-object/from16 v15, v83

    move-object/from16 v9, v84

    move-object/from16 v13, v85

    move-object v12, v11

    move-object/from16 v11, v82

    move-object v1, v2

    move-object v6, v4

    move-object/from16 v3, v16

    move-object/from16 v4, v18

    goto/16 :goto_5e

    :catch_3
    move-exception v0

    move-object v4, v1

    move-object v2, v9

    move-object/from16 v16, v12

    move-object/from16 v19, v14

    move-object/from16 v18, v15

    move-object/from16 v15, v83

    move-object/from16 v9, v84

    move-object/from16 v13, v85

    move-object v12, v11

    move-object/from16 v11, v82

    move-object v1, v2

    move-object v6, v4

    move-object/from16 v3, v16

    move-object/from16 v4, v18

    goto/16 :goto_5f

    :catchall_5f
    move-exception v0

    move-object v4, v1

    move-object v2, v9

    move-object/from16 v16, v12

    move-object/from16 v19, v14

    move-object/from16 v18, v15

    move-object/from16 v15, v83

    move-object/from16 v9, v84

    move-object/from16 v13, v85

    move-object v12, v11

    move-object/from16 v11, v82

    move-object v1, v2

    move-object v6, v4

    move-object v4, v5

    move-object/from16 v5, v18

    :goto_5a
    move-object v2, v0

    goto :goto_5c

    :catchall_60
    move-exception v0

    goto :goto_5b

    :catchall_61
    move-exception v0

    move-object/from16 v16, v3

    :goto_5b
    move-object v1, v9

    move-object v12, v11

    move-object v6, v15

    move-object/from16 v11, v82

    move-object/from16 v15, v83

    move-object/from16 v9, v84

    move-object/from16 v13, v85

    move-object/from16 v19, v2

    move-object v4, v8

    goto :goto_5a

    .line 368
    :goto_5c
    :try_start_79
    throw v2
    :try_end_79
    .catchall {:try_start_79 .. :try_end_79} :catchall_62

    :catchall_62
    move-exception v0

    :try_start_7a
    invoke-static {v4, v2}, Lkotlin/io/CloseableKt;->closeFinally(Ljava/io/Closeable;Ljava/lang/Throwable;)V

    throw v0
    :try_end_7a
    .catch Ljava/lang/SecurityException; {:try_start_7a .. :try_end_7a} :catch_5
    .catch Ljava/lang/Exception; {:try_start_7a .. :try_end_7a} :catch_4
    .catchall {:try_start_7a .. :try_end_7a} :catchall_63

    :catchall_63
    move-exception v0

    move-object v8, v5

    move-object v4, v6

    move-object/from16 v3, v16

    :goto_5d
    move-object/from16 v2, v19

    goto/16 :goto_66

    :catch_4
    move-exception v0

    move-object v4, v5

    move-object/from16 v3, v16

    :goto_5e
    move-object/from16 v2, v19

    goto/16 :goto_60

    :catch_5
    move-exception v0

    move-object v4, v5

    move-object/from16 v3, v16

    :goto_5f
    move-object/from16 v2, v19

    goto/16 :goto_61

    :catchall_64
    move-exception v0

    move-object/from16 v16, v3

    move-object v1, v9

    move-object v12, v11

    move-object v6, v15

    move-object/from16 v11, v82

    move-object/from16 v15, v83

    move-object/from16 v9, v84

    move-object/from16 v13, v85

    move-object v8, v5

    goto/16 :goto_65

    :catch_6
    move-exception v0

    move-object/from16 v16, v3

    move-object v1, v9

    move-object v12, v11

    move-object v6, v15

    move-object/from16 v11, v82

    move-object/from16 v15, v83

    move-object/from16 v9, v84

    move-object/from16 v13, v85

    move-object v4, v5

    goto :goto_60

    :catch_7
    move-exception v0

    move-object/from16 v16, v3

    move-object v1, v9

    move-object v12, v11

    move-object v6, v15

    move-object/from16 v11, v82

    move-object/from16 v15, v83

    move-object/from16 v9, v84

    move-object/from16 v13, v85

    move-object v4, v5

    goto :goto_61

    :catch_8
    move-exception v0

    move-object/from16 v43, v8

    move-object v1, v9

    move-object v12, v11

    move-object/from16 v11, v82

    move-object/from16 v15, v83

    move-object/from16 v9, v84

    move-object/from16 v13, v85

    .line 378
    :goto_60
    :try_start_7b
    sget-object v5, Lcom/bachatas4/android/data/InstallErrorCode;->SOURCE_INACCESSIBLE:Lcom/bachatas4/android/data/InstallErrorCode;

    invoke-virtual {v0}, Ljava/lang/Exception;->getMessage()Ljava/lang/String;

    move-result-object v0

    if-nez v0, :cond_33

    const-string v0, "Cannot open PKG"

    :cond_33
    invoke-direct {v1, v5, v0}, Lcom/bachatas4/android/service/ImportService;->failInstall(Lcom/bachatas4/android/data/InstallErrorCode;Ljava/lang/String;)Ljava/lang/Void;

    new-instance v0, Lkotlin/KotlinNothingValueException;

    invoke-direct {v0}, Lkotlin/KotlinNothingValueException;-><init>()V

    throw v0

    :catch_9
    move-exception v0

    move-object/from16 v43, v8

    move-object v1, v9

    move-object v12, v11

    move-object/from16 v11, v82

    move-object/from16 v15, v83

    move-object/from16 v9, v84

    move-object/from16 v13, v85

    .line 376
    :goto_61
    sget-object v5, Lcom/bachatas4/android/data/InstallErrorCode;->PERMISSION_LOST:Lcom/bachatas4/android/data/InstallErrorCode;

    invoke-virtual {v0}, Ljava/lang/SecurityException;->getMessage()Ljava/lang/String;

    move-result-object v0

    if-nez v0, :cond_34

    const-string v0, "Permission lost"

    :cond_34
    invoke-direct {v1, v5, v0}, Lcom/bachatas4/android/service/ImportService;->failInstall(Lcom/bachatas4/android/data/InstallErrorCode;Ljava/lang/String;)Ljava/lang/Void;

    new-instance v0, Lkotlin/KotlinNothingValueException;

    invoke-direct {v0}, Lkotlin/KotlinNothingValueException;-><init>()V

    throw v0

    :catchall_65
    move-exception v0

    goto :goto_64

    :catchall_66
    move-exception v0

    move-object/from16 v43, v8

    move-object v1, v9

    move-object v12, v11

    move-object/from16 v11, v82

    move-object/from16 v15, v83

    move-object/from16 v9, v84

    move-object/from16 v13, v85

    goto :goto_64

    :catchall_67
    move-exception v0

    move-object/from16 v43, v8

    move-object v1, v9

    goto :goto_62

    :cond_35
    move-object/from16 v1, p0

    move-object/from16 v43, v8

    move-object/from16 v11, v82

    move-object/from16 v15, v83

    move-object/from16 v9, v84

    move-object/from16 v13, v85

    move-object/from16 v12, v89

    .line 344
    const-string v5, "Games directory is not writable"

    invoke-direct {v1, v0, v5}, Lcom/bachatas4/android/service/ImportService;->failInstall(Lcom/bachatas4/android/data/InstallErrorCode;Ljava/lang/String;)Ljava/lang/Void;

    new-instance v0, Lkotlin/KotlinNothingValueException;

    invoke-direct {v0}, Lkotlin/KotlinNothingValueException;-><init>()V

    throw v0
    :try_end_7b
    .catchall {:try_start_7b .. :try_end_7b} :catchall_65

    :catchall_68
    move-exception v0

    move-object/from16 v1, p0

    move-object/from16 v43, v8

    :goto_62
    move-object/from16 v11, v82

    move-object/from16 v15, v83

    move-object/from16 v9, v84

    move-object/from16 v13, v85

    goto :goto_63

    :catchall_69
    move-exception v0

    move-object/from16 v1, p0

    move-object/from16 v11, v82

    move-object/from16 v15, v83

    move-object/from16 v9, v84

    move-object/from16 v13, v85

    move-object/from16 v43, v87

    :goto_63
    move-object/from16 v12, v89

    :goto_64
    move-object v8, v4

    :goto_65
    move-object v4, v6

    :goto_66
    const/16 v46, 0x0

    .line 641
    :goto_67
    :try_start_7c
    iget-boolean v5, v4, Lkotlin/jvm/internal/Ref$BooleanRef;->element:Z

    if-nez v5, :cond_36

    .line 642
    new-instance v5, Lcom/bachatas4/android/data/InstallCleanup;

    invoke-virtual {v1}, Lcom/bachatas4/android/service/ImportService;->getFilesDir()Ljava/io/File;

    move-result-object v6

    move-object/from16 v7, v43

    invoke-static {v6, v7}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullExpressionValue(Ljava/lang/Object;Ljava/lang/String;)V

    invoke-direct {v5, v6, v3}, Lcom/bachatas4/android/data/InstallCleanup;-><init>(Ljava/io/File;Lcom/bachatas4/android/data/InstallJobStore;)V

    invoke-virtual {v5, v2}, Lcom/bachatas4/android/data/InstallCleanup;->cleanupJob(Ljava/lang/String;)V

    .line 644
    :cond_36
    invoke-direct {v1, v0}, Lcom/bachatas4/android/service/ImportService;->handleFailure(Ljava/lang/Throwable;)V
    :try_end_7c
    .catchall {:try_start_7c .. :try_end_7c} :catchall_6b

    .line 646
    iget-boolean v0, v4, Lkotlin/jvm/internal/Ref$BooleanRef;->element:Z

    if-nez v0, :cond_38

    .line 647
    iget-object v0, v8, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v0, Ljava/io/File;

    if-eqz v0, :cond_37

    invoke-virtual {v0}, Ljava/io/File;->getAbsolutePath()Ljava/lang/String;

    move-result-object v0

    goto :goto_68

    :cond_37
    const/4 v0, 0x0

    :goto_68
    new-instance v2, Ljava/lang/StringBuilder;

    invoke-direct {v2, v9}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v2, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    invoke-static {v12, v0}, Landroid/util/Log;->w(Ljava/lang/String;Ljava/lang/String;)I

    .line 648
    iget-object v0, v8, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v0, Ljava/io/File;

    if-eqz v0, :cond_38

    invoke-static {v0}, Lkotlin/io/FilesKt;->deleteRecursively(Ljava/io/File;)Z

    move-result v0

    invoke-static {v0}, Lkotlin/coroutines/jvm/internal/Boxing;->boxBoolean(Z)Ljava/lang/Boolean;

    :cond_38
    if-eqz v46, :cond_39

    .line 651
    invoke-virtual/range {v46 .. v46}, Ljava/io/File;->getAbsolutePath()Ljava/lang/String;

    move-result-object v0

    new-instance v2, Ljava/lang/StringBuilder;

    invoke-direct {v2, v13}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v2, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    invoke-static {v12, v0}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    .line 652
    :try_start_7d
    sget-object v0, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    invoke-virtual/range {v46 .. v46}, Ljava/io/File;->delete()Z

    move-result v0

    invoke-static {v0}, Lkotlin/coroutines/jvm/internal/Boxing;->boxBoolean(Z)Ljava/lang/Boolean;

    move-result-object v0

    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v0
    :try_end_7d
    .catchall {:try_start_7d .. :try_end_7d} :catchall_6a

    goto :goto_69

    :catchall_6a
    move-exception v0

    sget-object v2, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    invoke-static {v0}, Lkotlin/ResultKt;->createFailure(Ljava/lang/Throwable;)Ljava/lang/Object;

    move-result-object v0

    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v0

    :goto_69
    invoke-static {v0}, Lkotlin/Result;->box-impl(Ljava/lang/Object;)Lkotlin/Result;

    :cond_39
    const/4 v10, 0x0

    .line 654
    iput-object v10, v1, Lcom/bachatas4/android/service/ImportService;->passcodeWaiter:Lkotlinx/coroutines/CompletableDeferred;

    .line 655
    iput-object v10, v1, Lcom/bachatas4/android/service/ImportService;->copyConfirmWaiter:Lkotlinx/coroutines/CompletableDeferred;

    .line 656
    sget-object v0, Lcom/bachatas4/android/data/ImportManager;->INSTANCE:Lcom/bachatas4/android/data/ImportManager;

    const/4 v2, 0x1

    invoke-static {v0, v10, v2, v10}, Lcom/bachatas4/android/data/ImportManager;->isBusy$default(Lcom/bachatas4/android/data/ImportManager;Lcom/bachatas4/android/data/ImportProgress;ILjava/lang/Object;)Z

    move-result v0

    if-eqz v0, :cond_3a

    sget-object v0, Lcom/bachatas4/android/data/ImportManager;->INSTANCE:Lcom/bachatas4/android/data/ImportManager;

    invoke-virtual {v0}, Lcom/bachatas4/android/data/ImportManager;->reset()V

    .line 657
    :cond_3a
    iget-boolean v0, v4, Lkotlin/jvm/internal/Ref$BooleanRef;->element:Z

    new-instance v2, Ljava/lang/StringBuilder;

    invoke-direct {v2, v15}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v2, v0}, Ljava/lang/StringBuilder;->append(Z)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0, v11}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    invoke-static {v12, v0}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    .line 658
    invoke-virtual {v1}, Lcom/bachatas4/android/service/ImportService;->stopSelf()V

    .line 660
    :goto_6a
    sget-object v0, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;

    return-object v0

    :catchall_6b
    move-exception v0

    move-object v2, v0

    .line 646
    iget-boolean v0, v4, Lkotlin/jvm/internal/Ref$BooleanRef;->element:Z

    if-nez v0, :cond_3c

    .line 647
    iget-object v0, v8, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v0, Ljava/io/File;

    if-eqz v0, :cond_3b

    invoke-virtual {v0}, Ljava/io/File;->getAbsolutePath()Ljava/lang/String;

    move-result-object v0

    goto :goto_6b

    :cond_3b
    const/4 v0, 0x0

    :goto_6b
    new-instance v3, Ljava/lang/StringBuilder;

    invoke-direct {v3, v9}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v3, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    invoke-static {v12, v0}, Landroid/util/Log;->w(Ljava/lang/String;Ljava/lang/String;)I

    .line 648
    iget-object v0, v8, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v0, Ljava/io/File;

    if-eqz v0, :cond_3c

    invoke-static {v0}, Lkotlin/io/FilesKt;->deleteRecursively(Ljava/io/File;)Z

    move-result v0

    invoke-static {v0}, Lkotlin/coroutines/jvm/internal/Boxing;->boxBoolean(Z)Ljava/lang/Boolean;

    :cond_3c
    if-eqz v46, :cond_3d

    .line 651
    invoke-virtual/range {v46 .. v46}, Ljava/io/File;->getAbsolutePath()Ljava/lang/String;

    move-result-object v0

    new-instance v3, Ljava/lang/StringBuilder;

    invoke-direct {v3, v13}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v3, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    invoke-static {v12, v0}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    .line 652
    :try_start_7e
    sget-object v0, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    invoke-virtual/range {v46 .. v46}, Ljava/io/File;->delete()Z

    move-result v0

    invoke-static {v0}, Lkotlin/coroutines/jvm/internal/Boxing;->boxBoolean(Z)Ljava/lang/Boolean;

    move-result-object v0

    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v0
    :try_end_7e
    .catchall {:try_start_7e .. :try_end_7e} :catchall_6c

    goto :goto_6c

    :catchall_6c
    move-exception v0

    sget-object v3, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    invoke-static {v0}, Lkotlin/ResultKt;->createFailure(Ljava/lang/Throwable;)Ljava/lang/Object;

    move-result-object v0

    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v0

    :goto_6c
    invoke-static {v0}, Lkotlin/Result;->box-impl(Ljava/lang/Object;)Lkotlin/Result;

    :cond_3d
    const/4 v10, 0x0

    .line 654
    iput-object v10, v1, Lcom/bachatas4/android/service/ImportService;->passcodeWaiter:Lkotlinx/coroutines/CompletableDeferred;

    .line 655
    iput-object v10, v1, Lcom/bachatas4/android/service/ImportService;->copyConfirmWaiter:Lkotlinx/coroutines/CompletableDeferred;

    .line 656
    sget-object v0, Lcom/bachatas4/android/data/ImportManager;->INSTANCE:Lcom/bachatas4/android/data/ImportManager;

    const/4 v8, 0x1

    invoke-static {v0, v10, v8, v10}, Lcom/bachatas4/android/data/ImportManager;->isBusy$default(Lcom/bachatas4/android/data/ImportManager;Lcom/bachatas4/android/data/ImportProgress;ILjava/lang/Object;)Z

    move-result v0

    if-eqz v0, :cond_3e

    sget-object v0, Lcom/bachatas4/android/data/ImportManager;->INSTANCE:Lcom/bachatas4/android/data/ImportManager;

    invoke-virtual {v0}, Lcom/bachatas4/android/data/ImportManager;->reset()V

    .line 657
    :cond_3e
    iget-boolean v0, v4, Lkotlin/jvm/internal/Ref$BooleanRef;->element:Z

    new-instance v3, Ljava/lang/StringBuilder;

    invoke-direct {v3, v15}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v3, v0}, Ljava/lang/StringBuilder;->append(Z)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0, v11}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    invoke-static {v12, v0}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    .line 658
    invoke-virtual {v1}, Lcom/bachatas4/android/service/ImportService;->stopSelf()V

    throw v2

    :pswitch_data_0
    .packed-switch 0x0
        :pswitch_9
        :pswitch_8
        :pswitch_7
        :pswitch_6
        :pswitch_5
        :pswitch_4
        :pswitch_3
        :pswitch_2
        :pswitch_1
        :pswitch_0
    .end packed-switch
.end method

.method private final updateNotification(Ljava/lang/String;IIZ)V
    .locals 7

    .line 1142
    const-class v0, Landroid/app/NotificationManager;

    invoke-virtual {p0, v0}, Lcom/bachatas4/android/service/ImportService;->getSystemService(Ljava/lang/Class;)Ljava/lang/Object;

    move-result-object v0

    check-cast v0, Landroid/app/NotificationManager;

    const/4 v5, 0x1

    move-object v1, p0

    move-object v2, p1

    move v3, p2

    move v4, p3

    move v6, p4

    .line 1144
    invoke-direct/range {v1 .. v6}, Lcom/bachatas4/android/service/ImportService;->buildNotification(Ljava/lang/String;IIZZ)Landroid/app/Notification;

    move-result-object p0

    const/16 p1, 0x2a

    .line 1142
    invoke-virtual {v0, p1, p0}, Landroid/app/NotificationManager;->notify(ILandroid/app/Notification;)V

    return-void
.end method

.method static synthetic updateNotification$default(Lcom/bachatas4/android/service/ImportService;Ljava/lang/String;IIZILjava/lang/Object;)V
    .locals 1

    and-int/lit8 p6, p5, 0x2

    const/4 v0, 0x0

    if-eqz p6, :cond_0

    move p2, v0

    :cond_0
    and-int/lit8 p6, p5, 0x4

    if-eqz p6, :cond_1

    move p3, v0

    :cond_1
    and-int/lit8 p5, p5, 0x8

    if-eqz p5, :cond_2

    move p4, v0

    .line 1136
    :cond_2
    invoke-direct {p0, p1, p2, p3, p4}, Lcom/bachatas4/android/service/ImportService;->updateNotification(Ljava/lang/String;IIZ)V

    return-void
.end method


# virtual methods
.method public final getContentImporter()Lcom/bachatas4/android/data/ContentImporter;
    .locals 0

    .line 66
    iget-object p0, p0, Lcom/bachatas4/android/service/ImportService;->contentImporter:Lcom/bachatas4/android/data/ContentImporter;

    if-eqz p0, :cond_0

    return-object p0

    :cond_0
    const-string p0, "contentImporter"

    invoke-static {p0}, Lkotlin/jvm/internal/Intrinsics;->throwUninitializedPropertyAccessException(Ljava/lang/String;)V

    const/4 p0, 0x0

    return-object p0
.end method

.method public final getGameRepository()Lcom/bachatas4/android/data/GameRepository;
    .locals 0

    .line 67
    iget-object p0, p0, Lcom/bachatas4/android/service/ImportService;->gameRepository:Lcom/bachatas4/android/data/GameRepository;

    if-eqz p0, :cond_0

    return-object p0

    :cond_0
    const-string p0, "gameRepository"

    invoke-static {p0}, Lkotlin/jvm/internal/Intrinsics;->throwUninitializedPropertyAccessException(Ljava/lang/String;)V

    const/4 p0, 0x0

    return-object p0
.end method

.method public final getPkgKeyStore()Lcom/bachatas4/android/data/PkgKeyStore;
    .locals 0

    .line 68
    iget-object p0, p0, Lcom/bachatas4/android/service/ImportService;->pkgKeyStore:Lcom/bachatas4/android/data/PkgKeyStore;

    if-eqz p0, :cond_0

    return-object p0

    :cond_0
    const-string p0, "pkgKeyStore"

    invoke-static {p0}, Lkotlin/jvm/internal/Intrinsics;->throwUninitializedPropertyAccessException(Ljava/lang/String;)V

    const/4 p0, 0x0

    return-object p0
.end method

.method public onBind(Landroid/content/Intent;)Landroid/os/IBinder;
    .locals 0

    const/4 p0, 0x0

    return-object p0
.end method

.method public onCreate()V
    .locals 0

    .line 76
    invoke-super {p0}, Lcom/bachatas4/android/service/Hilt_ImportService;->onCreate()V

    .line 77
    invoke-direct {p0}, Lcom/bachatas4/android/service/ImportService;->createNotificationChannel()V

    return-void
.end method

.method public onDestroy()V
    .locals 4

    .line 167
    iget-object v0, p0, Lcom/bachatas4/android/service/ImportService;->importJob:Lkotlinx/coroutines/Job;

    const/4 v1, 0x1

    const/4 v2, 0x0

    if-eqz v0, :cond_0

    invoke-static {v0, v2, v1, v2}, Lkotlinx/coroutines/Job;->cancel$default(Lkotlinx/coroutines/Job;Ljava/util/concurrent/CancellationException;ILjava/lang/Object;)V

    .line 168
    :cond_0
    iget-object v0, p0, Lcom/bachatas4/android/service/ImportService;->passcodeWaiter:Lkotlinx/coroutines/CompletableDeferred;

    if-eqz v0, :cond_1

    invoke-interface {v0, v2}, Lkotlinx/coroutines/CompletableDeferred;->complete(Ljava/lang/Object;)Z

    .line 169
    :cond_1
    iget-object v0, p0, Lcom/bachatas4/android/service/ImportService;->copyConfirmWaiter:Lkotlinx/coroutines/CompletableDeferred;

    if-eqz v0, :cond_2

    const/4 v3, 0x0

    invoke-static {v3}, Ljava/lang/Boolean;->valueOf(Z)Ljava/lang/Boolean;

    move-result-object v3

    invoke-interface {v0, v3}, Lkotlinx/coroutines/CompletableDeferred;->complete(Ljava/lang/Object;)Z

    .line 170
    :cond_2
    sget-object v0, Lcom/bachatas4/android/data/ImportManager;->INSTANCE:Lcom/bachatas4/android/data/ImportManager;

    invoke-static {v0, v2, v1, v2}, Lcom/bachatas4/android/data/ImportManager;->isBusy$default(Lcom/bachatas4/android/data/ImportManager;Lcom/bachatas4/android/data/ImportProgress;ILjava/lang/Object;)Z

    move-result v0

    if-eqz v0, :cond_3

    .line 171
    sget-object v0, Lcom/bachatas4/android/data/ImportManager;->INSTANCE:Lcom/bachatas4/android/data/ImportManager;

    invoke-virtual {v0}, Lcom/bachatas4/android/data/ImportManager;->reset()V

    .line 173
    :cond_3
    iget-object v0, p0, Lcom/bachatas4/android/service/ImportService;->scope:Lkotlinx/coroutines/CoroutineScope;

    invoke-static {v0, v2, v1, v2}, Lkotlinx/coroutines/CoroutineScopeKt;->cancel$default(Lkotlinx/coroutines/CoroutineScope;Ljava/util/concurrent/CancellationException;ILjava/lang/Object;)V

    .line 174
    invoke-super {p0}, Lcom/bachatas4/android/service/Hilt_ImportService;->onDestroy()V

    return-void
.end method

.method public onStartCommand(Landroid/content/Intent;II)I
    .locals 11

    const/4 p2, 0x0

    if-eqz p1, :cond_0

    .line 81
    invoke-virtual {p1}, Landroid/content/Intent;->getAction()Ljava/lang/String;

    move-result-object p3

    goto :goto_0

    :cond_0
    move-object p3, p2

    :goto_0
    const/4 v0, 0x2

    if-eqz p3, :cond_15

    invoke-virtual {p3}, Ljava/lang/String;->hashCode()I

    move-result v1

    const/4 v2, 0x0

    const/4 v3, 0x1

    const-string v4, "BachataImport"

    sparse-switch v1, :sswitch_data_0

    goto/16 :goto_3

    :sswitch_0
    const-string v1, "com.bachatas4.android.action.IMPORT_PKGS"

    invoke-virtual {p3, v1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result p3

    if-nez p3, :cond_1

    goto/16 :goto_3

    .line 107
    :cond_1
    const-string p3, "game_id"

    invoke-virtual {p1, p3}, Landroid/content/Intent;->getStringExtra(Ljava/lang/String;)Ljava/lang/String;

    move-result-object p3

    .line 108
    const-string v1, "source_uris"

    invoke-virtual {p1, v1}, Landroid/content/Intent;->getStringArrayListExtra(Ljava/lang/String;)Ljava/util/ArrayList;

    move-result-object p1

    .line 109
    move-object v1, p3

    check-cast v1, Ljava/lang/CharSequence;

    if-eqz v1, :cond_6

    invoke-static {v1}, Lkotlin/text/StringsKt;->isBlank(Ljava/lang/CharSequence;)Z

    move-result v1

    if-eqz v1, :cond_2

    goto :goto_1

    :cond_2
    move-object v1, p1

    check-cast v1, Ljava/util/Collection;

    if-eqz v1, :cond_6

    invoke-interface {v1}, Ljava/util/Collection;->isEmpty()Z

    move-result v1

    if-eqz v1, :cond_3

    goto :goto_1

    .line 117
    :cond_3
    invoke-virtual {p1}, Ljava/util/ArrayList;->size()I

    move-result v1

    new-instance v2, Ljava/lang/StringBuilder;

    const-string v5, "batch import start gameId="

    invoke-direct {v2, v5}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v2, p3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v2

    const-string v5, " count="

    invoke-virtual {v2, v5}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v2

    invoke-virtual {v2, v1}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v1

    invoke-static {v4, v1}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    .line 118
    iget-object v1, p0, Lcom/bachatas4/android/service/ImportService;->importJob:Lkotlinx/coroutines/Job;

    if-eqz v1, :cond_4

    invoke-interface {v1}, Lkotlinx/coroutines/Job;->isActive()Z

    move-result v1

    if-ne v1, v3, :cond_4

    .line 119
    const-string p0, "import already running \u2014 ignore batch request"

    invoke-static {v4, p0}, Landroid/util/Log;->w(Ljava/lang/String;Ljava/lang/String;)I

    return v0

    .line 122
    :cond_4
    sget-object v1, Lcom/bachatas4/android/data/ImportManager;->INSTANCE:Lcom/bachatas4/android/data/ImportManager;

    const-string v2, ""

    const-string v3, "pkg-batch"

    invoke-virtual {v1, v2, v3}, Lcom/bachatas4/android/data/ImportManager;->tryBeginImport(Ljava/lang/String;Ljava/lang/String;)Z

    move-result v1

    if-nez v1, :cond_5

    .line 123
    sget-object v1, Lcom/bachatas4/android/data/ImportManager;->INSTANCE:Lcom/bachatas4/android/data/ImportManager;

    invoke-virtual {v1}, Lcom/bachatas4/android/data/ImportManager;->reset()V

    .line 124
    sget-object v1, Lcom/bachatas4/android/data/ImportManager;->INSTANCE:Lcom/bachatas4/android/data/ImportManager;

    invoke-virtual {v1, v2, v3}, Lcom/bachatas4/android/data/ImportManager;->tryBeginImport(Ljava/lang/String;Ljava/lang/String;)Z

    move-result v1

    if-nez v1, :cond_5

    .line 125
    const-string p0, "import slot busy \u2014 abort batch"

    invoke-static {v4, p0}, Landroid/util/Log;->w(Ljava/lang/String;Ljava/lang/String;)I

    return v0

    .line 129
    :cond_5
    iget-object v5, p0, Lcom/bachatas4/android/service/ImportService;->scope:Lkotlinx/coroutines/CoroutineScope;

    new-instance v1, Lcom/bachatas4/android/service/ImportService$onStartCommand$1;

    invoke-direct {v1, p0, p3, p1, p2}, Lcom/bachatas4/android/service/ImportService$onStartCommand$1;-><init>(Lcom/bachatas4/android/service/ImportService;Ljava/lang/String;Ljava/util/ArrayList;Lkotlin/coroutines/Continuation;)V

    move-object v8, v1

    check-cast v8, Lkotlin/jvm/functions/Function2;

    const/4 v9, 0x3

    const/4 v10, 0x0

    const/4 v6, 0x0

    const/4 v7, 0x0

    invoke-static/range {v5 .. v10}, Lkotlinx/coroutines/BuildersKt;->launch$default(Lkotlinx/coroutines/CoroutineScope;Lkotlin/coroutines/CoroutineContext;Lkotlinx/coroutines/CoroutineStart;Lkotlin/jvm/functions/Function2;ILjava/lang/Object;)Lkotlinx/coroutines/Job;

    move-result-object p1

    iput-object p1, p0, Lcom/bachatas4/android/service/ImportService;->importJob:Lkotlinx/coroutines/Job;

    goto/16 :goto_3

    .line 110
    :cond_6
    :goto_1
    const-string p1, "batch import missing game id or uris"

    invoke-static {v4, p1}, Landroid/util/Log;->e(Ljava/lang/String;Ljava/lang/String;)I

    .line 111
    sget-object p1, Lcom/bachatas4/android/data/ImportManager;->INSTANCE:Lcom/bachatas4/android/data/ImportManager;

    .line 112
    new-instance p2, Lcom/bachatas4/android/data/ImportProgress$Failed;

    sget-object p3, Lcom/bachatas4/android/data/InstallErrorCode;->SOURCE_INACCESSIBLE:Lcom/bachatas4/android/data/InstallErrorCode;

    const-string v1, "Missing batch import parameters"

    invoke-direct {p2, p3, v1}, Lcom/bachatas4/android/data/ImportProgress$Failed;-><init>(Lcom/bachatas4/android/data/InstallErrorCode;Ljava/lang/String;)V

    check-cast p2, Lcom/bachatas4/android/data/ImportProgress;

    .line 111
    invoke-virtual {p1, p2}, Lcom/bachatas4/android/data/ImportManager;->update(Lcom/bachatas4/android/data/ImportProgress;)V

    .line 114
    invoke-virtual {p0}, Lcom/bachatas4/android/service/ImportService;->stopSelf()V

    return v0

    .line 81
    :sswitch_1
    const-string v1, "com.bachatas4.android.action.IMPORT_GAME"

    invoke-virtual {p3, v1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result p3

    if-nez p3, :cond_7

    goto/16 :goto_3

    .line 132
    :cond_7
    const-string p3, "source_uri"

    invoke-virtual {p1, p3}, Landroid/content/Intent;->getStringExtra(Ljava/lang/String;)Ljava/lang/String;

    move-result-object p3

    if-nez p3, :cond_8

    move-object p1, p0

    check-cast p1, Lcom/bachatas4/android/service/ImportService;

    .line 133
    const-string p1, "import missing source URI"

    invoke-static {v4, p1}, Landroid/util/Log;->e(Ljava/lang/String;Ljava/lang/String;)I

    .line 134
    sget-object p1, Lcom/bachatas4/android/data/ImportManager;->INSTANCE:Lcom/bachatas4/android/data/ImportManager;

    .line 135
    new-instance p2, Lcom/bachatas4/android/data/ImportProgress$Failed;

    sget-object p3, Lcom/bachatas4/android/data/InstallErrorCode;->SOURCE_INACCESSIBLE:Lcom/bachatas4/android/data/InstallErrorCode;

    const-string v1, "Missing source URI"

    invoke-direct {p2, p3, v1}, Lcom/bachatas4/android/data/ImportProgress$Failed;-><init>(Lcom/bachatas4/android/data/InstallErrorCode;Ljava/lang/String;)V

    check-cast p2, Lcom/bachatas4/android/data/ImportProgress;

    .line 134
    invoke-virtual {p1, p2}, Lcom/bachatas4/android/data/ImportManager;->update(Lcom/bachatas4/android/data/ImportProgress;)V

    .line 137
    invoke-virtual {p0}, Lcom/bachatas4/android/service/ImportService;->stopSelf()V

    return v0

    .line 140
    :cond_8
    const-string v1, "import_mode"

    invoke-virtual {p1, v1}, Landroid/content/Intent;->getStringExtra(Ljava/lang/String;)Ljava/lang/String;

    move-result-object p1

    if-nez p1, :cond_9

    const-string p1, "folder"

    .line 141
    :cond_9
    new-instance v1, Ljava/lang/StringBuilder;

    const-string v2, "import start mode="

    invoke-direct {v1, v2}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v1, p1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    const-string v2, " uri="

    invoke-virtual {v1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1, p3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v1

    invoke-static {v4, v1}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    .line 142
    iget-object v1, p0, Lcom/bachatas4/android/service/ImportService;->importJob:Lkotlinx/coroutines/Job;

    if-eqz v1, :cond_a

    invoke-interface {v1}, Lkotlinx/coroutines/Job;->isActive()Z

    move-result v1

    if-ne v1, v3, :cond_a

    .line 143
    const-string p0, "import already running \u2014 ignore new request"

    invoke-static {v4, p0}, Landroid/util/Log;->w(Ljava/lang/String;Ljava/lang/String;)I

    return v0

    .line 146
    :cond_a
    sget-object v1, Lcom/bachatas4/android/data/ImportManager;->INSTANCE:Lcom/bachatas4/android/data/ImportManager;

    invoke-virtual {v1, p3, p1}, Lcom/bachatas4/android/data/ImportManager;->tryBeginImport(Ljava/lang/String;Ljava/lang/String;)Z

    move-result v1

    if-nez v1, :cond_b

    .line 147
    sget-object v1, Lcom/bachatas4/android/data/ImportManager;->INSTANCE:Lcom/bachatas4/android/data/ImportManager;

    invoke-virtual {v1}, Lcom/bachatas4/android/data/ImportManager;->reset()V

    .line 148
    sget-object v1, Lcom/bachatas4/android/data/ImportManager;->INSTANCE:Lcom/bachatas4/android/data/ImportManager;

    invoke-virtual {v1, p3, p1}, Lcom/bachatas4/android/data/ImportManager;->tryBeginImport(Ljava/lang/String;Ljava/lang/String;)Z

    move-result v1

    if-nez v1, :cond_b

    .line 149
    const-string p0, "import slot busy \u2014 abort"

    invoke-static {v4, p0}, Landroid/util/Log;->w(Ljava/lang/String;Ljava/lang/String;)I

    return v0

    .line 153
    :cond_b
    iget-object v5, p0, Lcom/bachatas4/android/service/ImportService;->scope:Lkotlinx/coroutines/CoroutineScope;

    new-instance v1, Lcom/bachatas4/android/service/ImportService$onStartCommand$2;

    invoke-direct {v1, p1, p0, p3, p2}, Lcom/bachatas4/android/service/ImportService$onStartCommand$2;-><init>(Ljava/lang/String;Lcom/bachatas4/android/service/ImportService;Ljava/lang/String;Lkotlin/coroutines/Continuation;)V

    move-object v8, v1

    check-cast v8, Lkotlin/jvm/functions/Function2;

    const/4 v9, 0x3

    const/4 v10, 0x0

    const/4 v6, 0x0

    const/4 v7, 0x0

    invoke-static/range {v5 .. v10}, Lkotlinx/coroutines/BuildersKt;->launch$default(Lkotlinx/coroutines/CoroutineScope;Lkotlin/coroutines/CoroutineContext;Lkotlinx/coroutines/CoroutineStart;Lkotlin/jvm/functions/Function2;ILjava/lang/Object;)Lkotlinx/coroutines/Job;

    move-result-object p1

    iput-object p1, p0, Lcom/bachatas4/android/service/ImportService;->importJob:Lkotlinx/coroutines/Job;

    goto/16 :goto_3

    .line 81
    :sswitch_2
    const-string p1, "com.bachatas4.android.action.CANCEL_IMPORT"

    invoke-virtual {p3, p1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result p1

    if-nez p1, :cond_c

    goto/16 :goto_3

    .line 83
    :cond_c
    const-string p1, "cancel requested"

    invoke-static {v4, p1}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    .line 84
    invoke-static {}, Lcom/bachatas4/android/runtime/pkg/PkgExtractor;->nativeCancel()V

    .line 85
    iget-object p1, p0, Lcom/bachatas4/android/service/ImportService;->passcodeWaiter:Lkotlinx/coroutines/CompletableDeferred;

    if-eqz p1, :cond_d

    invoke-interface {p1, p2}, Lkotlinx/coroutines/CompletableDeferred;->complete(Ljava/lang/Object;)Z

    .line 86
    :cond_d
    iget-object p1, p0, Lcom/bachatas4/android/service/ImportService;->copyConfirmWaiter:Lkotlinx/coroutines/CompletableDeferred;

    if-eqz p1, :cond_e

    invoke-static {v2}, Ljava/lang/Boolean;->valueOf(Z)Ljava/lang/Boolean;

    move-result-object p3

    invoke-interface {p1, p3}, Lkotlinx/coroutines/CompletableDeferred;->complete(Ljava/lang/Object;)Z

    .line 87
    :cond_e
    iget-object p1, p0, Lcom/bachatas4/android/service/ImportService;->importJob:Lkotlinx/coroutines/Job;

    if-eqz p1, :cond_f

    invoke-static {p1, p2, v3, p2}, Lkotlinx/coroutines/Job;->cancel$default(Lkotlinx/coroutines/Job;Ljava/util/concurrent/CancellationException;ILjava/lang/Object;)V

    .line 88
    :cond_f
    const-class p1, Landroid/app/NotificationManager;

    invoke-virtual {p0, p1}, Lcom/bachatas4/android/service/ImportService;->getSystemService(Ljava/lang/Class;)Ljava/lang/Object;

    move-result-object p1

    check-cast p1, Landroid/app/NotificationManager;

    const/16 p2, 0x2a

    invoke-virtual {p1, p2}, Landroid/app/NotificationManager;->cancel(I)V

    .line 89
    iget-object p1, p0, Lcom/bachatas4/android/service/ImportService;->importJob:Lkotlinx/coroutines/Job;

    if-eqz p1, :cond_10

    invoke-interface {p1}, Lkotlinx/coroutines/Job;->isActive()Z

    move-result p1

    if-ne p1, v3, :cond_10

    goto :goto_2

    .line 90
    :cond_10
    sget-object p1, Lcom/bachatas4/android/data/ImportManager;->INSTANCE:Lcom/bachatas4/android/data/ImportManager;

    invoke-virtual {p1}, Lcom/bachatas4/android/data/ImportManager;->reset()V

    .line 91
    invoke-virtual {p0}, Lcom/bachatas4/android/service/ImportService;->stopSelf()V

    :goto_2
    return v0

    .line 81
    :sswitch_3
    const-string p2, "com.bachatas4.android.action.SUBMIT_PASSCODE"

    invoke-virtual {p3, p2}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result p2

    if-nez p2, :cond_11

    goto :goto_3

    .line 96
    :cond_11
    const-string p2, "passcode"

    invoke-virtual {p1, p2}, Landroid/content/Intent;->getStringExtra(Ljava/lang/String;)Ljava/lang/String;

    move-result-object p1

    if-eqz p1, :cond_12

    .line 97
    invoke-virtual {p1}, Ljava/lang/String;->length()I

    move-result v2

    :cond_12
    new-instance p2, Ljava/lang/StringBuilder;

    const-string p3, "passcode submitted (len="

    invoke-direct {p2, p3}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {p2, v2}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    move-result-object p2

    const-string p3, ")"

    invoke-virtual {p2, p3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p2

    invoke-virtual {p2}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p2

    invoke-static {v4, p2}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    .line 98
    iget-object p0, p0, Lcom/bachatas4/android/service/ImportService;->passcodeWaiter:Lkotlinx/coroutines/CompletableDeferred;

    if-eqz p0, :cond_13

    invoke-interface {p0, p1}, Lkotlinx/coroutines/CompletableDeferred;->complete(Ljava/lang/Object;)Z

    :cond_13
    return v0

    .line 81
    :sswitch_4
    const-string p1, "com.bachatas4.android.action.CONFIRM_PKG_COPY"

    invoke-virtual {p3, p1}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result p1

    if-nez p1, :cond_14

    goto :goto_3

    .line 102
    :cond_14
    const-string p1, "pkg copy confirmed by user"

    invoke-static {v4, p1}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    .line 103
    iget-object p0, p0, Lcom/bachatas4/android/service/ImportService;->copyConfirmWaiter:Lkotlinx/coroutines/CompletableDeferred;

    if-eqz p0, :cond_15

    invoke-static {v3}, Ljava/lang/Boolean;->valueOf(Z)Ljava/lang/Boolean;

    move-result-object p1

    invoke-interface {p0, p1}, Lkotlinx/coroutines/CompletableDeferred;->complete(Ljava/lang/Object;)Z

    :cond_15
    :goto_3
    return v0

    nop

    :sswitch_data_0
    .sparse-switch
        -0x4f24a830 -> :sswitch_4
        0x19c7d9bc -> :sswitch_3
        0x44d426c1 -> :sswitch_2
        0x751a57c3 -> :sswitch_1
        0x751e93f8 -> :sswitch_0
    .end sparse-switch
.end method

.method public final setContentImporter(Lcom/bachatas4/android/data/ContentImporter;)V
    .locals 1

    const-string v0, "<set-?>"

    invoke-static {p1, v0}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullParameter(Ljava/lang/Object;Ljava/lang/String;)V

    .line 66
    iput-object p1, p0, Lcom/bachatas4/android/service/ImportService;->contentImporter:Lcom/bachatas4/android/data/ContentImporter;

    return-void
.end method

.method public final setGameRepository(Lcom/bachatas4/android/data/GameRepository;)V
    .locals 1

    const-string v0, "<set-?>"

    invoke-static {p1, v0}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullParameter(Ljava/lang/Object;Ljava/lang/String;)V

    .line 67
    iput-object p1, p0, Lcom/bachatas4/android/service/ImportService;->gameRepository:Lcom/bachatas4/android/data/GameRepository;

    return-void
.end method

.method public final setPkgKeyStore(Lcom/bachatas4/android/data/PkgKeyStore;)V
    .locals 1

    const-string v0, "<set-?>"

    invoke-static {p1, v0}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullParameter(Ljava/lang/Object;Ljava/lang/String;)V

    .line 68
    iput-object p1, p0, Lcom/bachatas4/android/service/ImportService;->pkgKeyStore:Lcom/bachatas4/android/data/PkgKeyStore;

    return-void
.end method
