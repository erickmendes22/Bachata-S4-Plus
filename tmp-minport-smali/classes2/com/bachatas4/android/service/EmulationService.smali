.class public final Lcom/bachatas4/android/service/EmulationService;
.super Lcom/bachatas4/android/service/Hilt_EmulationService;
.source "EmulationService.kt"


# annotations
.annotation runtime Ldagger/hilt/android/AndroidEntryPoint;
.end annotation

.annotation system Ldalvik/annotation/MemberClasses;
    value = {
        Lcom/bachatas4/android/service/EmulationService$Companion;
    }
.end annotation

.annotation system Ldalvik/annotation/SourceDebugExtension;
    value = "SMAP\nEmulationService.kt\nKotlin\n*S Kotlin\n*F\n+ 1 EmulationService.kt\ncom/bachatas4/android/service/EmulationService\n+ 2 fake.kt\nkotlin/jvm/internal/FakeKt\n+ 3 Json.kt\nkotlinx/serialization/json/Json\n+ 4 _Arrays.kt\nkotlin/collections/ArraysKt___ArraysKt\n+ 5 _Sequences.kt\nkotlin/sequences/SequencesKt___SequencesKt\n*L\n1#1,818:1\n1#2:819\n222#3:820\n1401#4,2:821\n184#5,2:823\n184#5,2:825\n*S KotlinDebug\n*F\n+ 1 EmulationService.kt\ncom/bachatas4/android/service/EmulationService\n*L\n634#1:820\n646#1:821,2\n659#1:823,2\n660#1:825,2\n*E\n"
.end annotation

.annotation runtime Lkotlin/Metadata;
    d1 = {
        "\u0000\u00b8\u0001\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0002\u0008\u0003\n\u0002\u0018\u0002\n\u0002\u0008\u0004\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0010\u0002\n\u0000\n\u0002\u0010\u0008\n\u0000\n\u0002\u0018\u0002\n\u0002\u0008\u0003\n\u0002\u0018\u0002\n\u0002\u0008\u0003\n\u0002\u0010\u000e\n\u0002\u0008\u0002\n\u0002\u0018\u0002\n\u0002\u0008\u0002\n\u0002\u0018\u0002\n\u0002\u0008\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\u0008\u0004\n\u0002\u0010\u000b\n\u0000\n\u0002\u0018\u0002\n\u0002\u0008\u0008\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\u0008\u0004\n\u0002\u0010$\n\u0002\u0008\u0003\n\u0002\u0018\u0002\n\u0002\u0008\u0008\n\u0002\u0018\u0002\n\u0002\u0008\u0002\n\u0002\u0018\u0002\n\u0002\u0018\u0002\n\u0000\u0008\u0007\u0018\u0000 R2\u00020\u0001:\u0001RB\u0007\u00a2\u0006\u0004\u0008\u0002\u0010\u0003J\u0008\u0010\u0013\u001a\u00020\u0014H\u0016J\"\u0010\u0015\u001a\u00020\u00162\u0008\u0010\u0017\u001a\u0004\u0018\u00010\u00182\u0006\u0010\u0019\u001a\u00020\u00162\u0006\u0010\u001a\u001a\u00020\u0016H\u0016J\u0014\u0010\u001b\u001a\u0004\u0018\u00010\u001c2\u0008\u0010\u0017\u001a\u0004\u0018\u00010\u0018H\u0016J\u0008\u0010\u001d\u001a\u00020\u0014H\u0016J&\u0010\u001e\u001a\u00020\u00142\u0006\u0010\u001f\u001a\u00020 2\u0006\u0010!\u001a\u00020 2\u0006\u0010\"\u001a\u00020#H\u0082@\u00a2\u0006\u0002\u0010$J\u0089\u0001\u0010%\u001a\u00020&2\u0006\u0010\'\u001a\u00020 2\u0006\u0010(\u001a\u00020)2\u0006\u0010*\u001a\u00020+2\u0006\u0010,\u001a\u00020 2\u0006\u0010-\u001a\u00020 2\u0006\u0010.\u001a\u00020 2\u0006\u0010/\u001a\u0002002\u0006\u00101\u001a\u0002022\u0008\u00103\u001a\u0004\u0018\u00010 2\u0008\u00104\u001a\u0004\u0018\u00010 2\u0008\u00105\u001a\u0004\u0018\u00010\u00162\u0006\u00106\u001a\u0002002\n\u0008\u0002\u00107\u001a\u0004\u0018\u00010 2\u0008\u00108\u001a\u0004\u0018\u00010 H\u0002\u00a2\u0006\u0002\u00109J\u0008\u0010:\u001a\u00020;H\u0002J\u0008\u0010<\u001a\u00020=H\u0002J\u0008\u0010>\u001a\u00020?H\u0002J\u0018\u0010@\u001a\u00020\u00142\u0006\u0010A\u001a\u00020?2\u0006\u0010(\u001a\u00020)H\u0002J\u0010\u0010B\u001a\u00020 2\u0006\u0010A\u001a\u00020?H\u0002J<\u0010C\u001a\u0016\u0012\u0004\u0012\u00020 \u0012\u000c\u0012\n E*\u0004\u0018\u00010 0 0D2\u0006\u0010A\u001a\u00020?2\u0006\u0010F\u001a\u00020?2\u0006\u0010G\u001a\u00020H2\u0006\u0010I\u001a\u00020 H\u0002J\u001e\u0010J\u001a\u000e\u0012\u0004\u0012\u00020 \u0012\u0004\u0012\u00020 0D2\u0008\u0008\u0002\u0010K\u001a\u000200H\u0002J\u0012\u0010L\u001a\u0004\u0018\u00010 2\u0006\u0010M\u001a\u00020 H\u0002J\u0008\u0010N\u001a\u00020\u0014H\u0002J\u0008\u0010O\u001a\u00020\u0014H\u0002J\u0008\u0010P\u001a\u00020QH\u0002R#\u0010\u0004\u001a\u00020\u00058\u0006@\u0006X\u0087.\u0092\u0002\u0002\u0008\n\u00a2\u0006\u000e\n\u0000\u001a\u0004\u0008\u0006\u0010\u0007\"\u0004\u0008\u0008\u0010\tR\u000e\u0010\u000b\u001a\u00020\u000cX\u0082\u0004\u00a2\u0006\u0002\n\u0000R\u0010\u0010\r\u001a\u0004\u0018\u00010\u000eX\u0082\u000e\u00a2\u0006\u0002\n\u0000R\u0010\u0010\u000f\u001a\u0004\u0018\u00010\u0010X\u0082\u000e\u00a2\u0006\u0002\n\u0000R\u000e\u0010\u0011\u001a\u00020\u0012X\u0082\u0004\u00a2\u0006\u0002\n\u0000\u00ca\u0001\u0002\u0008T\u00ca\u0001\u000c\u0008U\u0012\u0008\u0008V\u0012\u0004\u0008\u0003\u0010\u0000\u00a8\u0006S"
    }
    d2 = {
        "Lcom/bachatas4/android/service/EmulationService;",
        "Landroid/app/Service;",
        "<init>",
        "()V",
        "launchProfileProvider",
        "Lcom/bachatas4/android/RuntimeLaunchProfileProvider;",
        "getLaunchProfileProvider",
        "()Lcom/bachatas4/android/RuntimeLaunchProfileProvider;",
        "setLaunchProfileProvider",
        "(Lcom/bachatas4/android/RuntimeLaunchProfileProvider;)V",
        "Ljavax/inject/Inject;",
        "scope",
        "Lkotlinx/coroutines/CoroutineScope;",
        "sessionJob",
        "Lkotlinx/coroutines/Job;",
        "process",
        "Lcom/bachatas4/android/runtime/process/RuntimeProcessHandle;",
        "userRequestedStop",
        "Ljava/util/concurrent/atomic/AtomicBoolean;",
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
        "runSession",
        "gameId",
        "",
        "relativePath",
        "vulkanDriver",
        "Lcom/bachatas4/android/runtime/process/RuntimeVulkanDriver;",
        "(Ljava/lang/String;Ljava/lang/String;Lcom/bachatas4/android/runtime/process/RuntimeVulkanDriver;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;",
        "buildReportContext",
        "Lcom/bachatas4/android/runtime/diagnostics/DiagnosticReportContext;",
        "reportId",
        "sessionLog",
        "Lcom/bachatas4/android/runtime/diagnostics/SessionLog;",
        "checkpointStore",
        "Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpointStore;",
        "gameTitle",
        "cusaId",
        "guestBackend",
        "firstFrameReached",
        "",
        "driverInfo",
        "Lcom/bachatas4/android/runtime/diagnostics/DiagnosticDriverInfo;",
        "processStartUtc",
        "processEndUtc",
        "exitCode",
        "launchFailed",
        "runtimeErrorCode",
        "settingsJson",
        "(Ljava/lang/String;Lcom/bachatas4/android/runtime/diagnostics/SessionLog;Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpointStore;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;ZLcom/bachatas4/android/runtime/diagnostics/DiagnosticDriverInfo;Ljava/lang/String;Ljava/lang/String;Ljava/lang/Integer;ZLjava/lang/String;Ljava/lang/String;)Lcom/bachatas4/android/runtime/diagnostics/DiagnosticReportContext;",
        "diagnosticAppInfo",
        "Lcom/bachatas4/android/runtime/diagnostics/DiagnosticAppInfo;",
        "diagnosticDeviceInfo",
        "Lcom/bachatas4/android/runtime/diagnostics/DiagnosticDeviceInfo;",
        "installRuntime",
        "Ljava/nio/file/Path;",
        "verifyDeepGuestRuntime",
        "runtimeRoot",
        "guestSha256",
        "runtimeEnvironment",
        "",
        "kotlin.jvm.PlatformType",
        "runtimeHome",
        "socketRoot",
        "Ljava/io/File;",
        "display",
        "stagingDiagEnvironment",
        "maliGpuOptimizations",
        "readSystemProperty",
        "key",
        "stopSession",
        "createNotificationChannel",
        "notification",
        "Landroid/app/Notification;",
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

.field public static final ACCEPT_POLL_MILLIS:J = 0xfaL
    .annotation runtime Ljava/lang/Deprecated;
    .end annotation
.end field

.field public static final CHANNEL_ID:Ljava/lang/String; = "emulation"
    .annotation runtime Ljava/lang/Deprecated;
    .end annotation
.end field

.field private static final Companion:Lcom/bachatas4/android/service/EmulationService$Companion;

.field public static final EMULATED_LIBRARIES:Ljava/lang/String; = "libSDL2-2.0.so.0:libudev.so.1:libuuid.so.1"
    .annotation runtime Ljava/lang/Deprecated;
    .end annotation
.end field

.field public static final EXPECTED_DEEP_GUEST_SHA256:Ljava/lang/String; = "7e922b148c2cb12c70933494ce3d0f14034b4e26955aa4e19161eee85652137a"
    .annotation runtime Ljava/lang/Deprecated;
    .end annotation
.end field

.field public static final MAX_ERROR_LOG_LINES:I = 0x14
    .annotation runtime Ljava/lang/Deprecated;
    .end annotation
.end field

.field public static final MAX_LOG_SESSIONS:I = 0xa
    .annotation runtime Ljava/lang/Deprecated;
    .end annotation
.end field

.field public static final NOTIFICATION_ID:I = 0x29
    .annotation runtime Ljava/lang/Deprecated;
    .end annotation
.end field

.field public static final PROCESS_EXIT_TIMEOUT_SECONDS:J = 0x5L
    .annotation runtime Ljava/lang/Deprecated;
    .end annotation
.end field

.field public static final SURFACE_TIMEOUT_MS:J = 0x7530L
    .annotation runtime Ljava/lang/Deprecated;
    .end annotation
.end field

.field public static final TAG:Ljava/lang/String; = "EmulationService"
    .annotation runtime Ljava/lang/Deprecated;
    .end annotation
.end field


# instance fields
.field public launchProfileProvider:Lcom/bachatas4/android/RuntimeLaunchProfileProvider;
    .annotation runtime Ljavax/inject/Inject;
    .end annotation
.end field

.field private volatile process:Lcom/bachatas4/android/runtime/process/RuntimeProcessHandle;

.field private final scope:Lkotlinx/coroutines/CoroutineScope;

.field private sessionJob:Lkotlinx/coroutines/Job;

.field private final userRequestedStop:Ljava/util/concurrent/atomic/AtomicBoolean;


# direct methods
.method public static synthetic $r8$lambda$BNirmT9VBt15wfCs4b8GaTodwdw(Ljava/util/concurrent/atomic/AtomicReference;Lcom/bachatas4/android/runtime/input/ControllerMotion;)Lkotlin/Unit;
    .locals 0

    invoke-static {p0, p1}, Lcom/bachatas4/android/service/EmulationService;->runSession$lambda$10$0(Ljava/util/concurrent/atomic/AtomicReference;Lcom/bachatas4/android/runtime/input/ControllerMotion;)Lkotlin/Unit;

    move-result-object p0

    return-object p0
.end method

.method public static synthetic $r8$lambda$Sx4SauI5ao51poWE5iUgn3UV-u0(Lkotlinx/serialization/json/JsonBuilder;)Lkotlin/Unit;
    .locals 0

    invoke-static {p0}, Lcom/bachatas4/android/service/EmulationService;->installRuntime$lambda$0$0(Lkotlinx/serialization/json/JsonBuilder;)Lkotlin/Unit;

    move-result-object p0

    return-object p0
.end method

.method static constructor <clinit>()V
    .locals 2

    new-instance v0, Lcom/bachatas4/android/service/EmulationService$Companion;

    const/4 v1, 0x0

    invoke-direct {v0, v1}, Lcom/bachatas4/android/service/EmulationService$Companion;-><init>(Lkotlin/jvm/internal/DefaultConstructorMarker;)V

    sput-object v0, Lcom/bachatas4/android/service/EmulationService;->Companion:Lcom/bachatas4/android/service/EmulationService$Companion;

    const/16 v0, 0x8

    sput v0, Lcom/bachatas4/android/service/EmulationService;->$stable:I

    return-void
.end method

.method public constructor <init>()V
    .locals 2

    .line 80
    invoke-direct {p0}, Lcom/bachatas4/android/service/Hilt_EmulationService;-><init>()V

    const/4 v0, 0x0

    const/4 v1, 0x1

    .line 84
    invoke-static {v0, v1, v0}, Lkotlinx/coroutines/SupervisorKt;->SupervisorJob$default(Lkotlinx/coroutines/Job;ILjava/lang/Object;)Lkotlinx/coroutines/CompletableJob;

    move-result-object v0

    invoke-static {}, Lkotlinx/coroutines/Dispatchers;->getIO()Lkotlinx/coroutines/CoroutineDispatcher;

    move-result-object v1

    check-cast v1, Lkotlin/coroutines/CoroutineContext;

    invoke-interface {v0, v1}, Lkotlinx/coroutines/CompletableJob;->plus(Lkotlin/coroutines/CoroutineContext;)Lkotlin/coroutines/CoroutineContext;

    move-result-object v0

    invoke-static {v0}, Lkotlinx/coroutines/CoroutineScopeKt;->CoroutineScope(Lkotlin/coroutines/CoroutineContext;)Lkotlinx/coroutines/CoroutineScope;

    move-result-object v0

    iput-object v0, p0, Lcom/bachatas4/android/service/EmulationService;->scope:Lkotlinx/coroutines/CoroutineScope;

    .line 87
    new-instance v0, Ljava/util/concurrent/atomic/AtomicBoolean;

    const/4 v1, 0x0

    invoke-direct {v0, v1}, Ljava/util/concurrent/atomic/AtomicBoolean;-><init>(Z)V

    iput-object v0, p0, Lcom/bachatas4/android/service/EmulationService;->userRequestedStop:Ljava/util/concurrent/atomic/AtomicBoolean;

    return-void
.end method

.method public static final synthetic access$runSession(Lcom/bachatas4/android/service/EmulationService;Ljava/lang/String;Ljava/lang/String;Lcom/bachatas4/android/runtime/process/RuntimeVulkanDriver;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;
    .locals 0

    .line 80
    invoke-direct {p0, p1, p2, p3, p4}, Lcom/bachatas4/android/service/EmulationService;->runSession(Ljava/lang/String;Ljava/lang/String;Lcom/bachatas4/android/runtime/process/RuntimeVulkanDriver;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;

    move-result-object p0

    return-object p0
.end method

.method private final buildReportContext(Ljava/lang/String;Lcom/bachatas4/android/runtime/diagnostics/SessionLog;Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpointStore;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;ZLcom/bachatas4/android/runtime/diagnostics/DiagnosticDriverInfo;Ljava/lang/String;Ljava/lang/String;Ljava/lang/Integer;ZLjava/lang/String;Ljava/lang/String;)Lcom/bachatas4/android/runtime/diagnostics/DiagnosticReportContext;
    .locals 21

    move-object/from16 v5, p6

    move-object/from16 v0, p0

    .line 570
    iget-object v1, v0, Lcom/bachatas4/android/service/EmulationService;->userRequestedStop:Ljava/util/concurrent/atomic/AtomicBoolean;

    invoke-virtual {v1}, Ljava/util/concurrent/atomic/AtomicBoolean;->get()Z

    move-result v8

    .line 571
    sget-object v6, Lcom/bachatas4/android/runtime/diagnostics/ProcessTerminationClassifier;->INSTANCE:Lcom/bachatas4/android/runtime/diagnostics/ProcessTerminationClassifier;

    .line 575
    const-string v1, "fex"

    invoke-static {v5, v1}, Lkotlin/jvm/internal/Intrinsics;->areEqual(Ljava/lang/Object;Ljava/lang/Object;)Z

    move-result v1

    if-eqz v1, :cond_0

    sget-object v1, Lcom/bachatas4/android/runtime/diagnostics/ProcessRole;->FEX:Lcom/bachatas4/android/runtime/diagnostics/ProcessRole;

    :goto_0
    move-object v9, v1

    goto :goto_1

    .line 576
    :cond_0
    const-string v1, "box64"

    invoke-static {v5, v1}, Lkotlin/jvm/internal/Intrinsics;->areEqual(Ljava/lang/Object;Ljava/lang/Object;)Z

    move-result v1

    if-eqz v1, :cond_1

    sget-object v1, Lcom/bachatas4/android/runtime/diagnostics/ProcessRole;->BOX64:Lcom/bachatas4/android/runtime/diagnostics/ProcessRole;

    goto :goto_0

    .line 577
    :cond_1
    sget-object v1, Lcom/bachatas4/android/runtime/diagnostics/ProcessRole;->BACKEND:Lcom/bachatas4/android/runtime/diagnostics/ProcessRole;

    goto :goto_0

    :goto_1
    if-eqz p12, :cond_2

    if-nez v8, :cond_2

    const/4 v1, 0x1

    goto :goto_2

    :cond_2
    const/4 v1, 0x0

    :goto_2
    move v13, v1

    const/16 v15, 0x80

    const/16 v16, 0x0

    const/4 v14, 0x0

    move-object/from16 v10, p9

    move-object/from16 v11, p10

    move-object/from16 v7, p11

    move-object/from16 v12, p13

    .line 571
    invoke-static/range {v6 .. v16}, Lcom/bachatas4/android/runtime/diagnostics/ProcessTerminationClassifier;->fromJavaExitValue$default(Lcom/bachatas4/android/runtime/diagnostics/ProcessTerminationClassifier;Ljava/lang/Integer;ZLcom/bachatas4/android/runtime/diagnostics/ProcessRole;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;ZZILjava/lang/Object;)Lcom/bachatas4/android/runtime/diagnostics/ProcessTerminationInfo;

    move-result-object v9

    .line 584
    new-instance v0, Lcom/bachatas4/android/runtime/diagnostics/DiagnosticReportContext;

    .line 586
    invoke-virtual/range {p2 .. p2}, Lcom/bachatas4/android/runtime/diagnostics/SessionLog;->getDirectory()Ljava/nio/file/Path;

    move-result-object v1

    invoke-virtual {v1}, Ljava/lang/Object;->toString()Ljava/lang/String;

    move-result-object v2

    .line 590
    invoke-virtual/range {p3 .. p3}, Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpointStore;->getLastCheckpoint()Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpoint;

    move-result-object v1

    if-eqz v1, :cond_3

    invoke-virtual {v1}, Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpoint;->name()Ljava/lang/String;

    move-result-object v1

    goto :goto_3

    :cond_3
    const/4 v1, 0x0

    :goto_3
    move-object v6, v1

    .line 595
    invoke-direct/range {p0 .. p0}, Lcom/bachatas4/android/service/EmulationService;->diagnosticAppInfo()Lcom/bachatas4/android/runtime/diagnostics/DiagnosticAppInfo;

    move-result-object v11

    .line 596
    invoke-direct/range {p0 .. p0}, Lcom/bachatas4/android/service/EmulationService;->diagnosticDeviceInfo()Lcom/bachatas4/android/runtime/diagnostics/DiagnosticDeviceInfo;

    move-result-object v12

    const/16 v19, 0x3000

    const/16 v20, 0x0

    const/4 v13, 0x0

    const/4 v14, 0x0

    move-object/from16 v1, p1

    move-object/from16 v3, p4

    move-object/from16 v4, p5

    move/from16 v7, p7

    move-object/from16 v10, p8

    move-object/from16 v15, p9

    move-object/from16 v16, p10

    move-object/from16 v17, p13

    move-object/from16 v18, p14

    .line 584
    invoke-direct/range {v0 .. v20}, Lcom/bachatas4/android/runtime/diagnostics/DiagnosticReportContext;-><init>(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;ZZLcom/bachatas4/android/runtime/diagnostics/ProcessTerminationInfo;Lcom/bachatas4/android/runtime/diagnostics/DiagnosticDriverInfo;Lcom/bachatas4/android/runtime/diagnostics/DiagnosticAppInfo;Lcom/bachatas4/android/runtime/diagnostics/DiagnosticDeviceInfo;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;ILkotlin/jvm/internal/DefaultConstructorMarker;)V

    return-object v0
.end method

.method static synthetic buildReportContext$default(Lcom/bachatas4/android/service/EmulationService;Ljava/lang/String;Lcom/bachatas4/android/runtime/diagnostics/SessionLog;Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpointStore;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;ZLcom/bachatas4/android/runtime/diagnostics/DiagnosticDriverInfo;Ljava/lang/String;Ljava/lang/String;Ljava/lang/Integer;ZLjava/lang/String;Ljava/lang/String;ILjava/lang/Object;)Lcom/bachatas4/android/runtime/diagnostics/DiagnosticReportContext;
    .locals 16

    move/from16 v0, p15

    and-int/lit16 v0, v0, 0x1000

    if-eqz v0, :cond_0

    const/4 v0, 0x0

    move-object v14, v0

    goto :goto_0

    :cond_0
    move-object/from16 v14, p13

    :goto_0
    move-object/from16 v1, p0

    move-object/from16 v2, p1

    move-object/from16 v3, p2

    move-object/from16 v4, p3

    move-object/from16 v5, p4

    move-object/from16 v6, p5

    move-object/from16 v7, p6

    move/from16 v8, p7

    move-object/from16 v9, p8

    move-object/from16 v10, p9

    move-object/from16 v11, p10

    move-object/from16 v12, p11

    move/from16 v13, p12

    move-object/from16 v15, p14

    .line 554
    invoke-direct/range {v1 .. v15}, Lcom/bachatas4/android/service/EmulationService;->buildReportContext(Ljava/lang/String;Lcom/bachatas4/android/runtime/diagnostics/SessionLog;Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpointStore;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;ZLcom/bachatas4/android/runtime/diagnostics/DiagnosticDriverInfo;Ljava/lang/String;Ljava/lang/String;Ljava/lang/Integer;ZLjava/lang/String;Ljava/lang/String;)Lcom/bachatas4/android/runtime/diagnostics/DiagnosticReportContext;

    move-result-object v0

    return-object v0
.end method

.method private final createNotificationChannel()V
    .locals 4

    .line 779
    const-class v0, Landroid/app/NotificationManager;

    invoke-virtual {p0, v0}, Lcom/bachatas4/android/service/EmulationService;->getSystemService(Ljava/lang/Class;)Ljava/lang/Object;

    move-result-object p0

    check-cast p0, Landroid/app/NotificationManager;

    .line 780
    new-instance v0, Landroid/app/NotificationChannel;

    const-string v1, "Emulation"

    check-cast v1, Ljava/lang/CharSequence;

    const/4 v2, 0x2

    const-string v3, "emulation"

    invoke-direct {v0, v3, v1, v2}, Landroid/app/NotificationChannel;-><init>(Ljava/lang/String;Ljava/lang/CharSequence;I)V

    .line 779
    invoke-virtual {p0, v0}, Landroid/app/NotificationManager;->createNotificationChannel(Landroid/app/NotificationChannel;)V

    return-void
.end method

.method private final diagnosticAppInfo()Lcom/bachatas4/android/runtime/diagnostics/DiagnosticAppInfo;
    .locals 9

    .line 608
    invoke-virtual {p0}, Lcom/bachatas4/android/service/EmulationService;->getPackageName()Ljava/lang/String;

    move-result-object v4

    const-string p0, "getPackageName(...)"

    invoke-static {v4, p0}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullExpressionValue(Ljava/lang/Object;Ljava/lang/String;)V

    .line 609
    const-string p0, "fdroid"

    check-cast p0, Ljava/lang/CharSequence;

    invoke-static {p0}, Lkotlin/text/StringsKt;->isBlank(Ljava/lang/CharSequence;)Z

    move-result v0

    if-eqz v0, :cond_0

    const-string p0, "unknown"

    :cond_0
    move-object v5, p0

    check-cast v5, Ljava/lang/String;

    .line 605
    new-instance v0, Lcom/bachatas4/android/runtime/diagnostics/DiagnosticAppInfo;

    const-string v1, "0.2.3"

    const-wide/32 v2, 0x18df878

    const-string v6, "adeb7dca313f"

    const-string v7, "50c8b90b09b433ab0767de44af2d0731cb0748b7"

    const/4 v8, 0x0

    invoke-direct/range {v0 .. v8}, Lcom/bachatas4/android/runtime/diagnostics/DiagnosticAppInfo;-><init>(Ljava/lang/String;JLjava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Z)V

    return-object v0
.end method

.method private final diagnosticDeviceInfo()Lcom/bachatas4/android/runtime/diagnostics/DiagnosticDeviceInfo;
    .locals 13

    .line 617
    sget-object p0, Landroid/os/Build;->MANUFACTURER:Ljava/lang/String;

    const-string v0, ""

    if-nez p0, :cond_0

    move-object v2, v0

    goto :goto_0

    :cond_0
    move-object v2, p0

    .line 618
    :goto_0
    sget-object p0, Landroid/os/Build;->MODEL:Ljava/lang/String;

    if-nez p0, :cond_1

    move-object v3, v0

    goto :goto_1

    :cond_1
    move-object v3, p0

    .line 619
    :goto_1
    sget-object p0, Landroid/os/Build;->DEVICE:Ljava/lang/String;

    if-nez p0, :cond_2

    move-object v4, v0

    goto :goto_2

    :cond_2
    move-object v4, p0

    .line 620
    :goto_2
    sget-object p0, Landroid/os/Build$VERSION;->RELEASE:Ljava/lang/String;

    if-nez p0, :cond_3

    move-object v5, v0

    goto :goto_3

    :cond_3
    move-object v5, p0

    .line 621
    :goto_3
    sget v6, Landroid/os/Build$VERSION;->SDK_INT:I

    .line 622
    sget-object p0, Landroid/os/Build;->SUPPORTED_ABIS:[Ljava/lang/String;

    const/4 v0, 0x0

    if-eqz p0, :cond_4

    invoke-static {p0}, Lkotlin/collections/ArraysKt;->toList([Ljava/lang/Object;)Ljava/util/List;

    move-result-object p0

    goto :goto_4

    :cond_4
    move-object p0, v0

    :goto_4
    if-nez p0, :cond_5

    invoke-static {}, Lkotlin/collections/CollectionsKt;->emptyList()Ljava/util/List;

    move-result-object p0

    :cond_5
    move-object v7, p0

    .line 623
    sget-object p0, Landroid/os/Build;->SOC_MODEL:Ljava/lang/String;

    invoke-static {p0}, Lkotlin/jvm/internal/Intrinsics;->checkNotNull(Ljava/lang/Object;)V

    move-object v1, p0

    check-cast v1, Ljava/lang/CharSequence;

    invoke-static {v1}, Lkotlin/text/StringsKt;->isBlank(Ljava/lang/CharSequence;)Z

    move-result v1

    if-nez v1, :cond_6

    move-object v0, p0

    :cond_6
    if-nez v0, :cond_7

    sget-object v0, Landroid/os/Build;->HARDWARE:Ljava/lang/String;

    :cond_7
    move-object v8, v0

    .line 616
    new-instance v1, Lcom/bachatas4/android/runtime/diagnostics/DiagnosticDeviceInfo;

    const/4 v9, 0x0

    const/4 v10, 0x0

    const/4 v11, 0x0

    const/4 v12, 0x0

    invoke-direct/range {v1 .. v12}, Lcom/bachatas4/android/runtime/diagnostics/DiagnosticDeviceInfo;-><init>(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;ILjava/util/List;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/Long;)V

    return-object v1
.end method

.method private final guestSha256(Ljava/nio/file/Path;)Ljava/lang/String;
    .locals 10

    .line 677
    const-string p0, "host/shadps4-arm64-fex"

    invoke-interface {p1, p0}, Ljava/nio/file/Path;->resolve(Ljava/lang/String;)Ljava/nio/file/Path;

    move-result-object p0

    invoke-interface {p0}, Ljava/nio/file/Path;->toFile()Ljava/io/File;

    move-result-object p0

    .line 678
    invoke-virtual {p0}, Ljava/io/File;->isFile()Z

    move-result p1

    if-nez p1, :cond_0

    const-string p0, "missing"

    return-object p0

    .line 679
    :cond_0
    const-string p1, "SHA-256"

    invoke-static {p1}, Ljava/security/MessageDigest;->getInstance(Ljava/lang/String;)Ljava/security/MessageDigest;

    move-result-object p1

    new-instance v0, Ljava/io/FileInputStream;

    .line 680
    invoke-static {p0}, Lkotlin/jvm/internal/Intrinsics;->checkNotNull(Ljava/lang/Object;)V

    invoke-direct {v0, p0}, Ljava/io/FileInputStream;-><init>(Ljava/io/File;)V

    move-object p0, v0

    check-cast p0, Ljava/io/Closeable;

    :try_start_0
    move-object v0, p0

    check-cast v0, Ljava/io/FileInputStream;

    const/high16 v1, 0x100000

    .line 681
    new-array v1, v1, [B

    .line 683
    :goto_0
    invoke-virtual {v0, v1}, Ljava/io/FileInputStream;->read([B)I

    move-result v2

    if-lez v2, :cond_1

    const/4 v3, 0x0

    .line 685
    invoke-virtual {p1, v1, v3, v2}, Ljava/security/MessageDigest;->update([BII)V

    goto :goto_0

    .line 687
    :cond_1
    sget-object v0, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;
    :try_end_0
    .catchall {:try_start_0 .. :try_end_0} :catchall_0

    const/4 v0, 0x0

    .line 680
    invoke-static {p0, v0}, Lkotlin/io/CloseableKt;->closeFinally(Ljava/io/Closeable;Ljava/lang/Throwable;)V

    .line 688
    invoke-virtual {p1}, Ljava/security/MessageDigest;->digest()[B

    move-result-object v1

    const-string p0, "digest(...)"

    invoke-static {v1, p0}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullExpressionValue(Ljava/lang/Object;Ljava/lang/String;)V

    const-string p0, ""

    move-object v2, p0

    check-cast v2, Ljava/lang/CharSequence;

    new-instance v7, Lcom/bachatas4/android/service/EmulationService$$ExternalSyntheticLambda5;

    invoke-direct {v7}, Lcom/bachatas4/android/service/EmulationService$$ExternalSyntheticLambda5;-><init>()V

    const/16 v8, 0x1e

    const/4 v9, 0x0

    const/4 v3, 0x0

    const/4 v4, 0x0

    const/4 v5, 0x0

    const/4 v6, 0x0

    invoke-static/range {v1 .. v9}, Lkotlin/collections/ArraysKt;->joinToString$default([BLjava/lang/CharSequence;Ljava/lang/CharSequence;Ljava/lang/CharSequence;ILjava/lang/CharSequence;Lkotlin/jvm/functions/Function1;ILjava/lang/Object;)Ljava/lang/String;

    move-result-object p0

    return-object p0

    :catchall_0
    move-exception v0

    move-object p1, v0

    .line 680
    :try_start_1
    throw p1
    :try_end_1
    .catchall {:try_start_1 .. :try_end_1} :catchall_1

    :catchall_1
    move-exception v0

    invoke-static {p0, p1}, Lkotlin/io/CloseableKt;->closeFinally(Ljava/io/Closeable;Ljava/lang/Throwable;)V

    throw v0
.end method

.method static final guestSha256$lambda$1(B)Ljava/lang/CharSequence;
    .locals 1

    .line 688
    invoke-static {p0}, Ljava/lang/Byte;->valueOf(B)Ljava/lang/Byte;

    move-result-object p0

    filled-new-array {p0}, [Ljava/lang/Object;

    move-result-object p0

    const/4 v0, 0x1

    invoke-static {p0, v0}, Ljava/util/Arrays;->copyOf([Ljava/lang/Object;I)[Ljava/lang/Object;

    move-result-object p0

    const-string v0, "%02x"

    invoke-static {v0, p0}, Ljava/lang/String;->format(Ljava/lang/String;[Ljava/lang/Object;)Ljava/lang/String;

    move-result-object p0

    const-string v0, "format(...)"

    invoke-static {p0, v0}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullExpressionValue(Ljava/lang/Object;Ljava/lang/String;)V

    check-cast p0, Ljava/lang/CharSequence;

    return-object p0
.end method

.method private final installRuntime()Ljava/nio/file/Path;
    .locals 9

    .line 631
    new-instance v0, Ljava/io/File;

    invoke-virtual {p0}, Lcom/bachatas4/android/service/EmulationService;->getFilesDir()Ljava/io/File;

    move-result-object v1

    const-string v2, "runtime"

    invoke-direct {v0, v1, v2}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    invoke-virtual {v0}, Ljava/io/File;->toPath()Ljava/nio/file/Path;

    move-result-object v0

    .line 632
    sget-object v1, Lcom/bachatas4/android/BuildConfig;->DOWNLOAD_RUNTIME:Ljava/lang/Boolean;

    invoke-virtual {v1}, Ljava/lang/Boolean;->booleanValue()Z

    move-result v1

    const/4 v2, 0x2

    const/4 v3, 0x0

    if-nez v1, :cond_4

    .line 633
    invoke-virtual {p0}, Lcom/bachatas4/android/service/EmulationService;->getAssets()Landroid/content/res/AssetManager;

    move-result-object v1

    const-string v4, "runtime/manifest.json"

    invoke-virtual {v1, v4}, Landroid/content/res/AssetManager;->open(Ljava/lang/String;)Ljava/io/InputStream;

    move-result-object v1

    const-string v4, "open(...)"

    invoke-static {v1, v4}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullExpressionValue(Ljava/lang/Object;Ljava/lang/String;)V

    sget-object v4, Lkotlin/text/Charsets;->UTF_8:Ljava/nio/charset/Charset;

    new-instance v5, Ljava/io/InputStreamReader;

    invoke-direct {v5, v1, v4}, Ljava/io/InputStreamReader;-><init>(Ljava/io/InputStream;Ljava/nio/charset/Charset;)V

    check-cast v5, Ljava/io/Reader;

    instance-of v1, v5, Ljava/io/BufferedReader;

    if-eqz v1, :cond_0

    check-cast v5, Ljava/io/BufferedReader;

    goto :goto_0

    :cond_0
    new-instance v1, Ljava/io/BufferedReader;

    const/16 v4, 0x2000

    invoke-direct {v1, v5, v4}, Ljava/io/BufferedReader;-><init>(Ljava/io/Reader;I)V

    move-object v5, v1

    :goto_0
    check-cast v5, Ljava/io/Closeable;

    :try_start_0
    move-object v1, v5

    check-cast v1, Ljava/io/BufferedReader;

    .line 634
    new-instance v4, Lcom/bachatas4/android/service/EmulationService$$ExternalSyntheticLambda0;

    invoke-direct {v4}, Lcom/bachatas4/android/service/EmulationService$$ExternalSyntheticLambda0;-><init>()V

    const/4 v6, 0x1

    invoke-static {v3, v4, v6, v3}, Lkotlinx/serialization/json/JsonKt;->Json$default(Lkotlinx/serialization/json/Json;Lkotlin/jvm/functions/Function1;ILjava/lang/Object;)Lkotlinx/serialization/json/Json;

    move-result-object v4

    check-cast v1, Ljava/io/Reader;

    invoke-static {v1}, Lkotlin/io/TextStreamsKt;->readText(Ljava/io/Reader;)Ljava/lang/String;

    move-result-object v1

    .line 820
    invoke-virtual {v4}, Lkotlinx/serialization/json/Json;->getSerializersModule()Lkotlinx/serialization/modules/SerializersModule;

    move-result-object v6

    const-class v7, Lcom/bachatas4/android/runtime/install/RuntimeManifest;

    invoke-static {v7}, Lkotlin/jvm/internal/Reflection;->typeOf(Ljava/lang/Class;)Lkotlin/reflect/KType;

    move-result-object v7

    const-string v8, "kotlinx.serialization.serializer.withModule"

    invoke-static {v8}, Lkotlin/jvm/internal/MagicApiIntrinsics;->voidMagicApiCall(Ljava/lang/Object;)V

    invoke-static {v6, v7}, Lkotlinx/serialization/SerializersKt;->serializer(Lkotlinx/serialization/modules/SerializersModule;Lkotlin/reflect/KType;)Lkotlinx/serialization/KSerializer;

    move-result-object v6

    check-cast v6, Lkotlinx/serialization/DeserializationStrategy;

    invoke-virtual {v4, v6, v1}, Lkotlinx/serialization/json/Json;->decodeFromString(Lkotlinx/serialization/DeserializationStrategy;Ljava/lang/String;)Ljava/lang/Object;

    move-result-object v1

    check-cast v1, Lcom/bachatas4/android/runtime/install/RuntimeManifest;
    :try_end_0
    .catchall {:try_start_0 .. :try_end_0} :catchall_2

    .line 633
    invoke-static {v5, v3}, Lkotlin/io/CloseableKt;->closeFinally(Ljava/io/Closeable;Ljava/lang/Throwable;)V

    .line 636
    invoke-virtual {v1}, Lcom/bachatas4/android/runtime/install/RuntimeManifest;->getRuntimeVersion()Ljava/lang/String;

    move-result-object v4

    invoke-interface {v0, v4}, Ljava/nio/file/Path;->resolve(Ljava/lang/String;)Ljava/nio/file/Path;

    move-result-object v4

    .line 637
    invoke-interface {v4}, Ljava/nio/file/Path;->toFile()Ljava/io/File;

    move-result-object v5

    invoke-virtual {v5}, Ljava/io/File;->isDirectory()Z

    move-result v5

    if-eqz v5, :cond_1

    .line 638
    invoke-static {v4}, Lkotlin/jvm/internal/Intrinsics;->checkNotNull(Ljava/lang/Object;)V

    return-object v4

    .line 640
    :cond_1
    invoke-virtual {p0}, Lcom/bachatas4/android/service/EmulationService;->getAssets()Landroid/content/res/AssetManager;

    move-result-object p0

    const-string v5, "runtime/runtime.zip"

    invoke-virtual {p0, v5}, Landroid/content/res/AssetManager;->open(Ljava/lang/String;)Ljava/io/InputStream;

    move-result-object p0

    check-cast p0, Ljava/io/Closeable;

    :try_start_1
    move-object v5, p0

    check-cast v5, Ljava/io/InputStream;

    .line 641
    new-instance v6, Lcom/bachatas4/android/runtime/install/RuntimeInstaller;

    invoke-static {v0}, Lkotlin/jvm/internal/Intrinsics;->checkNotNull(Ljava/lang/Object;)V

    invoke-direct {v6, v0, v3, v2, v3}, Lcom/bachatas4/android/runtime/install/RuntimeInstaller;-><init>(Ljava/nio/file/Path;Lkotlin/jvm/functions/Function2;ILkotlin/jvm/internal/DefaultConstructorMarker;)V

    invoke-static {v5}, Lkotlin/jvm/internal/Intrinsics;->checkNotNull(Ljava/lang/Object;)V

    invoke-virtual {v6, v5, v1}, Lcom/bachatas4/android/runtime/install/RuntimeInstaller;->install-gIAlu-s(Ljava/io/InputStream;Lcom/bachatas4/android/runtime/install/RuntimeManifest;)Ljava/lang/Object;

    move-result-object v0

    invoke-static {v0}, Lkotlin/Result;->exceptionOrNull-impl(Ljava/lang/Object;)Ljava/lang/Throwable;

    move-result-object v1

    if-nez v1, :cond_2

    move-object v4, v0

    goto :goto_1

    .line 642
    :cond_2
    instance-of v0, v1, Ljava/nio/file/FileAlreadyExistsException;

    if-eqz v0, :cond_3

    invoke-interface {v4}, Ljava/nio/file/Path;->toFile()Ljava/io/File;

    move-result-object v0

    invoke-virtual {v0}, Ljava/io/File;->isDirectory()Z

    move-result v0

    if-eqz v0, :cond_3

    .line 641
    :goto_1
    check-cast v4, Ljava/nio/file/Path;
    :try_end_1
    .catchall {:try_start_1 .. :try_end_1} :catchall_0

    .line 640
    invoke-static {p0, v3}, Lkotlin/io/CloseableKt;->closeFinally(Ljava/io/Closeable;Ljava/lang/Throwable;)V

    const-string p0, "use(...)"

    invoke-static {v4, p0}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullExpressionValue(Ljava/lang/Object;Ljava/lang/String;)V

    return-object v4

    .line 642
    :cond_3
    :try_start_2
    throw v1
    :try_end_2
    .catchall {:try_start_2 .. :try_end_2} :catchall_0

    :catchall_0
    move-exception v0

    .line 640
    :try_start_3
    throw v0
    :try_end_3
    .catchall {:try_start_3 .. :try_end_3} :catchall_1

    :catchall_1
    move-exception v1

    invoke-static {p0, v0}, Lkotlin/io/CloseableKt;->closeFinally(Ljava/io/Closeable;Ljava/lang/Throwable;)V

    throw v1

    :catchall_2
    move-exception p0

    .line 633
    :try_start_4
    throw p0
    :try_end_4
    .catchall {:try_start_4 .. :try_end_4} :catchall_3

    :catchall_3
    move-exception v0

    invoke-static {v5, p0}, Lkotlin/io/CloseableKt;->closeFinally(Ljava/io/Closeable;Ljava/lang/Throwable;)V

    throw v0

    .line 646
    :cond_4
    invoke-interface {v0}, Ljava/nio/file/Path;->toFile()Ljava/io/File;

    move-result-object p0

    invoke-virtual {p0}, Ljava/io/File;->listFiles()[Ljava/io/File;

    move-result-object p0

    if-eqz p0, :cond_6

    .line 821
    array-length v0, p0

    const/4 v1, 0x0

    move v4, v1

    :goto_2
    if-ge v4, v0, :cond_6

    aget-object v5, p0, v4

    .line 646
    invoke-virtual {v5}, Ljava/io/File;->isDirectory()Z

    move-result v6

    if-eqz v6, :cond_5

    invoke-virtual {v5}, Ljava/io/File;->getName()Ljava/lang/String;

    move-result-object v6

    const-string v7, "getName(...)"

    invoke-static {v6, v7}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullExpressionValue(Ljava/lang/Object;Ljava/lang/String;)V

    const-string v7, "box64-"

    invoke-static {v6, v7, v1, v2, v3}, Lkotlin/text/StringsKt;->startsWith$default(Ljava/lang/String;Ljava/lang/String;ZILjava/lang/Object;)Z

    move-result v6

    if-eqz v6, :cond_5

    move-object v3, v5

    goto :goto_3

    :cond_5
    add-int/lit8 v4, v4, 0x1

    goto :goto_2

    :cond_6
    :goto_3
    if-eqz v3, :cond_7

    .line 647
    invoke-virtual {v3}, Ljava/io/File;->toPath()Ljava/nio/file/Path;

    move-result-object p0

    const-string v0, "toPath(...)"

    invoke-static {p0, v0}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullExpressionValue(Ljava/lang/Object;Ljava/lang/String;)V

    return-object p0

    .line 648
    :cond_7
    new-instance p0, Ljava/lang/IllegalStateException;

    const-string v0, "Runtime not installed"

    invoke-direct {p0, v0}, Ljava/lang/IllegalStateException;-><init>(Ljava/lang/String;)V

    throw p0
.end method

.method private static final installRuntime$lambda$0$0(Lkotlinx/serialization/json/JsonBuilder;)Lkotlin/Unit;
    .locals 1

    const-string v0, "$this$Json"

    invoke-static {p0, v0}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullParameter(Ljava/lang/Object;Ljava/lang/String;)V

    const/4 v0, 0x1

    .line 634
    invoke-virtual {p0, v0}, Lkotlinx/serialization/json/JsonBuilder;->setIgnoreUnknownKeys(Z)V

    sget-object p0, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;

    return-object p0
.end method

.method private final notification()Landroid/app/Notification;
    .locals 6

    .line 786
    move-object v0, p0

    check-cast v0, Landroid/content/Context;

    new-instance v1, Landroid/content/Intent;

    const-class v2, Lcom/bachatas4/android/MainActivity;

    invoke-direct {v1, v0, v2}, Landroid/content/Intent;-><init>(Landroid/content/Context;Ljava/lang/Class;)V

    const/4 v2, 0x0

    const/high16 v3, 0xc000000

    .line 785
    invoke-static {v0, v2, v1, v3}, Landroid/app/PendingIntent;->getActivity(Landroid/content/Context;ILandroid/content/Intent;I)Landroid/app/PendingIntent;

    move-result-object v1

    .line 790
    new-instance v4, Landroid/content/Intent;

    const-string v5, "com.bachatas4.android.action.STOP_EMULATION"

    invoke-direct {v4, v5}, Landroid/content/Intent;-><init>(Ljava/lang/String;)V

    invoke-virtual {p0}, Lcom/bachatas4/android/service/EmulationService;->getPackageName()Ljava/lang/String;

    move-result-object p0

    const-string v5, "com.bachatas4.android.service.EmulationService"

    invoke-virtual {v4, p0, v5}, Landroid/content/Intent;->setClassName(Ljava/lang/String;Ljava/lang/String;)Landroid/content/Intent;

    move-result-object p0

    const/4 v4, 0x1

    .line 788
    invoke-static {v0, v4, p0, v3}, Landroid/app/PendingIntent;->getService(Landroid/content/Context;ILandroid/content/Intent;I)Landroid/app/PendingIntent;

    move-result-object p0

    .line 793
    new-instance v3, Landroidx/core/app/NotificationCompat$Builder;

    const-string v5, "emulation"

    invoke-direct {v3, v0, v5}, Landroidx/core/app/NotificationCompat$Builder;-><init>(Landroid/content/Context;Ljava/lang/String;)V

    const v0, 0x1080024

    .line 794
    invoke-virtual {v3, v0}, Landroidx/core/app/NotificationCompat$Builder;->setSmallIcon(I)Landroidx/core/app/NotificationCompat$Builder;

    move-result-object v0

    .line 795
    const-string v3, "Bachata S4 emulation"

    check-cast v3, Ljava/lang/CharSequence;

    invoke-virtual {v0, v3}, Landroidx/core/app/NotificationCompat$Builder;->setContentTitle(Ljava/lang/CharSequence;)Landroidx/core/app/NotificationCompat$Builder;

    move-result-object v0

    .line 796
    const-string v3, "Game session running"

    check-cast v3, Ljava/lang/CharSequence;

    invoke-virtual {v0, v3}, Landroidx/core/app/NotificationCompat$Builder;->setContentText(Ljava/lang/CharSequence;)Landroidx/core/app/NotificationCompat$Builder;

    move-result-object v0

    .line 797
    invoke-virtual {v0, v1}, Landroidx/core/app/NotificationCompat$Builder;->setContentIntent(Landroid/app/PendingIntent;)Landroidx/core/app/NotificationCompat$Builder;

    move-result-object v0

    .line 798
    const-string v1, "Stop"

    check-cast v1, Ljava/lang/CharSequence;

    invoke-virtual {v0, v2, v1, p0}, Landroidx/core/app/NotificationCompat$Builder;->addAction(ILjava/lang/CharSequence;Landroid/app/PendingIntent;)Landroidx/core/app/NotificationCompat$Builder;

    move-result-object p0

    .line 799
    invoke-virtual {p0, v4}, Landroidx/core/app/NotificationCompat$Builder;->setOngoing(Z)Landroidx/core/app/NotificationCompat$Builder;

    move-result-object p0

    .line 800
    invoke-virtual {p0}, Landroidx/core/app/NotificationCompat$Builder;->build()Landroid/app/Notification;

    move-result-object p0

    const-string v0, "build(...)"

    invoke-static {p0, v0}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullExpressionValue(Ljava/lang/Object;Ljava/lang/String;)V

    return-object p0
.end method

.method private final rbSwizzleEnvironment(Lcom/bachatas4/android/runtime/settings/ResolvedRuntimeProfile;)Ljava/util/Map;
    .locals 3

    invoke-virtual {p1}, Lcom/bachatas4/android/runtime/settings/ResolvedRuntimeProfile;->getSettings()Ljava/util/Map;

    move-result-object v0

    const-string v1, "bachata.rb_channel_fix"

    invoke-interface {v0, v1}, Ljava/util/Map;->get(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v0

    check-cast v0, Lcom/bachatas4/android/runtime/settings/ResolvedSetting;

    if-eqz v0, :cond_0

    invoke-virtual {v0}, Lcom/bachatas4/android/runtime/settings/ResolvedSetting;->getValue()Lkotlinx/serialization/json/JsonElement;

    move-result-object v0

    instance-of v1, v0, Lkotlinx/serialization/json/JsonPrimitive;

    if-eqz v1, :cond_0

    check-cast v0, Lkotlinx/serialization/json/JsonPrimitive;

    invoke-static {v0}, Lkotlinx/serialization/json/JsonElementKt;->getBooleanOrNull(Lkotlinx/serialization/json/JsonPrimitive;)Ljava/lang/Boolean;

    move-result-object v0

    if-eqz v0, :cond_0

    invoke-virtual {v0}, Ljava/lang/Boolean;->booleanValue()Z

    move-result v0

    if-eqz v0, :cond_0

    const-string v0, "BACHATA_RB_SWIZZLE"

    const-string v1, "1"

    invoke-static {v0, v1}, Lkotlin/TuplesKt;->to(Ljava/lang/Object;Ljava/lang/Object;)Lkotlin/Pair;

    move-result-object v0

    invoke-static {v0}, Lkotlin/collections/MapsKt;->mapOf(Lkotlin/Pair;)Ljava/util/Map;

    move-result-object v0

    return-object v0

    :cond_0
    invoke-static {}, Lkotlin/collections/MapsKt;->emptyMap()Ljava/util/Map;

    move-result-object v0

    return-object v0
.end method

.method private final readSystemProperty(Ljava/lang/String;)Ljava/lang/String;
    .locals 5

    const/4 p0, 0x0

    .line 764
    :try_start_0
    const-string v0, "android.os.SystemProperties"

    invoke-static {v0}, Ljava/lang/Class;->forName(Ljava/lang/String;)Ljava/lang/Class;

    move-result-object v0

    .line 765
    const-string v1, "get"

    const/4 v2, 0x1

    new-array v2, v2, [Ljava/lang/Class;

    const-class v3, Ljava/lang/String;

    const/4 v4, 0x0

    aput-object v3, v2, v4

    invoke-virtual {v0, v1, v2}, Ljava/lang/Class;->getMethod(Ljava/lang/String;[Ljava/lang/Class;)Ljava/lang/reflect/Method;

    move-result-object v0

    .line 766
    filled-new-array {p1}, [Ljava/lang/Object;

    move-result-object p1

    invoke-virtual {v0, p0, p1}, Ljava/lang/reflect/Method;->invoke(Ljava/lang/Object;[Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object p1

    instance-of v0, p1, Ljava/lang/String;

    if-eqz v0, :cond_0

    check-cast p1, Ljava/lang/String;

    goto :goto_0

    :cond_0
    move-object p1, p0

    :goto_0
    if-eqz p1, :cond_1

    move-object v0, p1

    check-cast v0, Ljava/lang/CharSequence;

    invoke-interface {v0}, Ljava/lang/CharSequence;->length()I

    move-result v0
    :try_end_0
    .catchall {:try_start_0 .. :try_end_0} :catchall_0

    if-lez v0, :cond_1

    return-object p1

    :catchall_0
    :cond_1
    return-object p0
.end method

.method private final runSession(Ljava/lang/String;Ljava/lang/String;Lcom/bachatas4/android/runtime/process/RuntimeVulkanDriver;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;
    .locals 156
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "(",
            "Ljava/lang/String;",
            "Ljava/lang/String;",
            "Lcom/bachatas4/android/runtime/process/RuntimeVulkanDriver;",
            "Lkotlin/coroutines/Continuation<",
            "-",
            "Lkotlin/Unit;",
            ">;)",
            "Ljava/lang/Object;"
        }
    .end annotation

    move-object/from16 v2, p0

    move-object/from16 v1, p1

    move-object/from16 v0, p4

    const-string v3, "toPath(...)"

    const-string v4, "vortek_guest_launch_failed: "

    const-string v5, "persistent pipeline cache enabled home="

    const-string v6, "driver="

    const-string v7, "guestBackend="

    const-string v8, "installed version="

    const-string v9, "schema="

    const-string v10, "vortek_window_bridge: "

    const-string v11, "{\"schemaVersion\":"

    const-string v12, "embedded X server started display="

    const-string v13, "surface="

    instance-of v14, v0, Lcom/bachatas4/android/service/EmulationService$runSession$1;

    if-eqz v14, :cond_0

    move-object v14, v0

    check-cast v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;

    iget v15, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->label:I

    const/high16 v16, -0x80000000

    and-int v15, v15, v16

    if-eqz v15, :cond_0

    iget v0, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->label:I

    sub-int v0, v0, v16

    iput v0, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->label:I

    goto :goto_0

    :cond_0
    new-instance v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;

    invoke-direct {v14, v2, v0}, Lcom/bachatas4/android/service/EmulationService$runSession$1;-><init>(Lcom/bachatas4/android/service/EmulationService;Lkotlin/coroutines/Continuation;)V

    :goto_0
    iget-object v0, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->result:Ljava/lang/Object;

    invoke-static {}, Lkotlin/coroutines/intrinsics/IntrinsicsKt;->getCOROUTINE_SUSPENDED()Ljava/lang/Object;

    move-result-object v15

    move-object/from16 v21, v4

    .line 119
    iget v4, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->label:I

    move-object/from16 v22, v5

    const-string v5, "Display"

    move-object/from16 v23, v6

    const-string v6, ": "

    move-object/from16 v24, v7

    const-string v7, "Vulkan"

    move-object/from16 v25, v3

    const-string v3, "Runtime"

    move-object/from16 v26, v6

    const-string v6, "vortek_server_stop_failed: "

    move-object/from16 v27, v6

    const-string v6, "cleanup complete"

    move-object/from16 v28, v6

    const-string v6, "shadps4-internal.log"

    move-object/from16 v29, v6

    const-string v6, "internal backend log copy failed: "

    move-object/from16 v30, v6

    const-string v6, "Logs"

    move-object/from16 v31, v6

    const-string v6, ".local/share/shadPS4/log/shad_log.txt"

    move-object/from16 v32, v6

    const-string v6, "Vortek"

    move-object/from16 v33, v10

    const-string v10, "Session"

    const-string v35, ""

    move-object/from16 v36, v7

    const/4 v7, 0x1

    move-object/from16 v38, v6

    if-eqz v4, :cond_6

    if-eq v4, v7, :cond_5

    const/4 v1, 0x2

    if-eq v4, v1, :cond_4

    const/4 v1, 0x3

    if-eq v4, v1, :cond_3

    const/4 v1, 0x4

    if-eq v4, v1, :cond_2

    const/4 v1, 0x5

    if-ne v4, v1, :cond_1

    iget-boolean v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->Z$0:Z

    iget v4, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->I$0:I

    iget-object v5, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$36:Ljava/lang/Object;

    check-cast v5, Lcom/bachatas4/android/runtime/vortek/VortekWindowBridge;

    iget-object v5, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$35:Ljava/lang/Object;

    check-cast v5, Lcom/winlator/xserver/XServer;

    iget-object v5, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$34:Ljava/lang/Object;

    check-cast v5, Lcom/bachatas4/android/runtime/vortek/VortekStartResult;

    iget-object v5, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$33:Ljava/lang/Object;

    check-cast v5, Lcom/bachatas4/android/runtime/vortek/VortekSessionSupport;

    iget-object v8, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$32:Ljava/lang/Object;

    check-cast v8, Ljava/lang/String;

    iget-object v8, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$31:Ljava/lang/Object;

    check-cast v8, Ljava/nio/file/Path;

    iget-object v9, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$30:Ljava/lang/Object;

    check-cast v9, Ljava/io/File;

    iget-object v11, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$29:Ljava/lang/Object;

    check-cast v11, Lcom/bachatas4/android/runtime/session/RuntimeSurface;

    iget-object v11, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$28:Ljava/lang/Object;

    check-cast v11, Ljava/nio/file/Path;

    iget-object v12, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$27:Ljava/lang/Object;

    check-cast v12, Lcom/bachatas4/android/runtime/settings/ResolvedRuntimeProfile;

    iget-object v13, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$26:Ljava/lang/Object;

    check-cast v13, Ljava/io/File;

    iget-object v15, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$25:Ljava/lang/Object;

    check-cast v15, Ljava/io/File;

    iget-object v7, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$24:Ljava/lang/Object;

    check-cast v7, Ljava/io/File;

    iget-object v7, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$23:Ljava/lang/Object;

    check-cast v7, Lcom/bachatas4/android/runtime/vortek/VortekSessionSupport;

    iget-object v6, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$22:Ljava/lang/Object;

    check-cast v6, Lkotlin/jvm/internal/Ref$BooleanRef;

    move/from16 v16, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$21:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$ObjectRef;

    move-object/from16 p1, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$20:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$ObjectRef;

    move-object/from16 p2, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$19:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$ObjectRef;

    move-object/from16 p3, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$18:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$ObjectRef;

    move-object/from16 p4, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$17:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$ObjectRef;

    move-object/from16 v17, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$16:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$BooleanRef;

    move-object/from16 v18, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$15:Ljava/lang/Object;

    check-cast v1, Lcom/bachatas4/android/runtime/session/FrameTelemetryReporter;

    move-object/from16 v19, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$14:Ljava/lang/Object;

    check-cast v1, Ljava/io/File;

    move-object/from16 v20, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$13:Ljava/lang/Object;

    check-cast v1, Ljava/lang/String;

    move-object/from16 v41, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$12:Ljava/lang/Object;

    check-cast v1, Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpointStore;

    move-object/from16 v42, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$11:Ljava/lang/Object;

    check-cast v1, Lcom/bachatas4/android/runtime/diagnostics/SessionLog;

    move-object/from16 v43, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$10:Ljava/lang/Object;

    check-cast v1, Ljava/nio/file/Path;

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$9:Ljava/lang/Object;

    check-cast v1, Ljava/io/File;

    move-object/from16 v44, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$8:Ljava/lang/Object;

    check-cast v1, Ljava/util/concurrent/ExecutorService;

    move-object/from16 v45, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$7:Ljava/lang/Object;

    check-cast v1, Ljava/nio/file/Path;

    move-object/from16 v46, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$6:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$ObjectRef;

    move-object/from16 v47, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$5:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$ObjectRef;

    move-object/from16 v48, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$4:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$ObjectRef;

    move-object/from16 v49, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$3:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$ObjectRef;

    move-object/from16 v50, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$2:Ljava/lang/Object;

    check-cast v1, Lcom/bachatas4/android/runtime/process/RuntimeVulkanDriver;

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$1:Ljava/lang/Object;

    check-cast v1, Ljava/lang/String;

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$0:Ljava/lang/Object;

    check-cast v1, Ljava/lang/String;

    :try_start_0
    invoke-static {v0}, Lkotlin/ResultKt;->throwOnFailure(Ljava/lang/Object;)V
    :try_end_0
    .catch Ljava/util/concurrent/CancellationException; {:try_start_0 .. :try_end_0} :catch_1
    .catch Ljava/lang/Exception; {:try_start_0 .. :try_end_0} :catch_0
    .catchall {:try_start_0 .. :try_end_0} :catchall_0

    move/from16 v56, v4

    move-object/from16 v55, v5

    move-object/from16 v54, v8

    move-object/from16 v53, v10

    move-object/from16 v52, v11

    move-object/from16 v51, v12

    move-object/from16 v4, v20

    move-object/from16 v2, v41

    move-object/from16 v5, v43

    move-object/from16 v12, v45

    move-object/from16 v11, v46

    move-object/from16 v41, p3

    move-object/from16 v20, p4

    move-object/from16 v43, v3

    move-object v8, v7

    move-object/from16 v3, p1

    move-object v7, v6

    move-object/from16 v6, v42

    move-object/from16 v42, p2

    goto/16 :goto_c

    :catchall_0
    move-exception v0

    move-object v4, v0

    move-object/from16 v155, v7

    move-object/from16 v154, v10

    move-object/from16 v151, v27

    move-object/from16 v152, v28

    move-object/from16 v6, v29

    move-object/from16 v7, v30

    move-object/from16 v9, v31

    move-object/from16 v15, v32

    move-object/from16 v153, v38

    move-object/from16 v14, v42

    move-object/from16 v5, v43

    move-object/from16 v33, v45

    move-object/from16 v0, v46

    move-object/from16 v13, v47

    move-object/from16 v10, v48

    move-object/from16 v11, v49

    move-object/from16 v12, v50

    goto/16 :goto_1

    :catch_0
    move-exception v0

    move-object/from16 v12, p1

    move-object/from16 v13, p2

    move-object/from16 v11, p3

    move-object/from16 v16, v0

    move/from16 v90, v4

    move-object v3, v6

    move-object/from16 v130, v7

    move-object/from16 v127, v10

    move-object/from16 v9, v17

    move-object/from16 v8, v18

    move-object/from16 v112, v26

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v126, v38

    move-object/from16 v7, v41

    move-object/from16 v4, v42

    move-object/from16 v5, v43

    move-object/from16 v33, v45

    move-object/from16 v129, v46

    move-object/from16 v15, v47

    move-object/from16 v22, v48

    move-object/from16 v120, v49

    const/4 v14, 0x0

    const/16 v34, 0x4

    const/16 v37, 0x0

    const/16 v128, 0x0

    move-object/from16 v10, p4

    move-object v6, v1

    move-object/from16 v1, v20

    move-object/from16 v20, v50

    goto/16 :goto_10d

    :catch_1
    move-object/from16 v12, p1

    move-object/from16 v14, p2

    move-object/from16 v9, p3

    move-object/from16 v0, p4

    move-object v11, v2

    move/from16 v90, v4

    move-object/from16 v145, v7

    move-object v15, v10

    move-object/from16 v13, v17

    move-object/from16 v141, v28

    move-object/from16 v10, v29

    move-object/from16 v8, v32

    move-object/from16 v142, v38

    move-object/from16 v3, v41

    move-object/from16 v5, v42

    move-object/from16 v4, v43

    move-object/from16 v33, v45

    move-object/from16 v144, v46

    move-object/from16 v22, v47

    move-object/from16 v21, v48

    move-object/from16 v20, v49

    move-object/from16 v19, v50

    const/4 v2, 0x1

    const/16 v34, 0x4

    const/16 v37, 0x0

    const/16 v40, 0x0

    const/16 v143, 0x0

    move-object v7, v1

    move-object v1, v6

    move-object/from16 v6, v18

    goto/16 :goto_12b

    :cond_1
    new-instance v0, Ljava/lang/IllegalStateException;

    const-string v1, "call to \'resume\' before \'invoke\' with coroutine"

    invoke-direct {v0, v1}, Ljava/lang/IllegalStateException;-><init>(Ljava/lang/String;)V

    throw v0

    :cond_2
    iget-boolean v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->Z$0:Z

    iget v4, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->I$0:I

    iget-object v5, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$33:Ljava/lang/Object;

    check-cast v5, Lcom/bachatas4/android/runtime/vortek/VortekSessionSupport;

    iget-object v6, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$32:Ljava/lang/Object;

    check-cast v6, Ljava/lang/String;

    iget-object v7, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$31:Ljava/lang/Object;

    check-cast v7, Ljava/nio/file/Path;

    iget-object v8, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$30:Ljava/lang/Object;

    check-cast v8, Ljava/io/File;

    iget-object v9, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$29:Ljava/lang/Object;

    check-cast v9, Lcom/bachatas4/android/runtime/session/RuntimeSurface;

    iget-object v11, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$28:Ljava/lang/Object;

    check-cast v11, Ljava/nio/file/Path;

    iget-object v12, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$27:Ljava/lang/Object;

    check-cast v12, Lcom/bachatas4/android/runtime/settings/ResolvedRuntimeProfile;

    iget-object v13, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$26:Ljava/lang/Object;

    check-cast v13, Ljava/io/File;

    move/from16 v16, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$25:Ljava/lang/Object;

    check-cast v1, Ljava/io/File;

    move-object/from16 p1, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$24:Ljava/lang/Object;

    check-cast v1, Ljava/io/File;

    move-object/from16 p2, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$23:Ljava/lang/Object;

    check-cast v1, Lcom/bachatas4/android/runtime/vortek/VortekSessionSupport;

    move-object/from16 p3, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$22:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$BooleanRef;

    move-object/from16 v17, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$21:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$ObjectRef;

    move-object/from16 v18, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$20:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$ObjectRef;

    move-object/from16 v19, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$19:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$ObjectRef;

    move-object/from16 v20, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$18:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$ObjectRef;

    move-object/from16 v41, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$17:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$ObjectRef;

    move-object/from16 v42, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$16:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$BooleanRef;

    move-object/from16 v43, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$15:Ljava/lang/Object;

    check-cast v1, Lcom/bachatas4/android/runtime/session/FrameTelemetryReporter;

    move-object/from16 v44, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$14:Ljava/lang/Object;

    check-cast v1, Ljava/io/File;

    move-object/from16 v45, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$13:Ljava/lang/Object;

    check-cast v1, Ljava/lang/String;

    move-object/from16 v46, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$12:Ljava/lang/Object;

    check-cast v1, Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpointStore;

    move-object/from16 v47, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$11:Ljava/lang/Object;

    check-cast v1, Lcom/bachatas4/android/runtime/diagnostics/SessionLog;

    move-object/from16 v48, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$10:Ljava/lang/Object;

    check-cast v1, Ljava/nio/file/Path;

    move-object/from16 v49, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$9:Ljava/lang/Object;

    check-cast v1, Ljava/io/File;

    move-object/from16 v50, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$8:Ljava/lang/Object;

    check-cast v1, Ljava/util/concurrent/ExecutorService;

    move-object/from16 v51, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$7:Ljava/lang/Object;

    check-cast v1, Ljava/nio/file/Path;

    move-object/from16 v52, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$6:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$ObjectRef;

    move-object/from16 v53, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$5:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$ObjectRef;

    move-object/from16 v54, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$4:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$ObjectRef;

    move-object/from16 v55, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$3:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$ObjectRef;

    move-object/from16 v56, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$2:Ljava/lang/Object;

    check-cast v1, Lcom/bachatas4/android/runtime/process/RuntimeVulkanDriver;

    move-object/from16 v57, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$1:Ljava/lang/Object;

    check-cast v1, Ljava/lang/String;

    move-object/from16 v58, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$0:Ljava/lang/Object;

    check-cast v1, Ljava/lang/String;

    :try_start_1
    invoke-static {v0}, Lkotlin/ResultKt;->throwOnFailure(Ljava/lang/Object;)V
    :try_end_1
    .catch Ljava/util/concurrent/CancellationException; {:try_start_1 .. :try_end_1} :catch_3
    .catch Ljava/lang/Exception; {:try_start_1 .. :try_end_1} :catch_2
    .catchall {:try_start_1 .. :try_end_1} :catchall_1

    move-object/from16 v2, v43

    move-object/from16 v43, v3

    move-object v3, v2

    move-object/from16 v2, v53

    move-object/from16 v53, v10

    move-object v10, v2

    move-object/from16 v110, p1

    move-object/from16 v104, p3

    move/from16 v102, v4

    move-object/from16 p1, v5

    move-object/from16 v59, v6

    move-object/from16 v105, v7

    move-object/from16 v106, v8

    move-object/from16 v107, v11

    move-object/from16 v108, v12

    move-object/from16 v109, v13

    move/from16 v101, v16

    move-object/from16 v103, v17

    move-object/from16 v100, v18

    move-object/from16 v99, v19

    move-object/from16 v98, v20

    move-object/from16 v97, v41

    move-object/from16 v96, v42

    move-object/from16 v4, v45

    move-object/from16 v2, v46

    move-object/from16 v6, v47

    move-object/from16 v5, v48

    move-object/from16 v13, v50

    move-object/from16 v12, v51

    move-object/from16 v11, v52

    move-object/from16 v8, v55

    move-object/from16 v7, v56

    move-object/from16 v56, p2

    move-object/from16 v45, v9

    move-object/from16 v46, v15

    move-object/from16 v9, v54

    move-object/from16 v54, v57

    move-object v15, v14

    move-object/from16 v14, v44

    move-object/from16 v44, v49

    goto/16 :goto_a

    :catchall_1
    move-exception v0

    move-object/from16 v155, p3

    move-object v4, v0

    move-object/from16 v154, v10

    move-object/from16 v151, v27

    move-object/from16 v152, v28

    move-object/from16 v6, v29

    move-object/from16 v7, v30

    move-object/from16 v9, v31

    move-object/from16 v15, v32

    move-object/from16 v153, v38

    move-object/from16 v14, v47

    move-object/from16 v5, v48

    move-object/from16 v44, v50

    move-object/from16 v33, v51

    move-object/from16 v0, v52

    move-object/from16 v13, v53

    move-object/from16 v10, v54

    move-object/from16 v11, v55

    move-object/from16 v12, v56

    :goto_1
    const/4 v1, 0x4

    const/4 v3, 0x0

    const/4 v8, 0x1

    const/16 v37, 0x0

    goto/16 :goto_146

    :catch_2
    move-exception v0

    move-object/from16 v130, p3

    move-object/from16 v16, v0

    move-object v6, v1

    move/from16 v90, v4

    move-object/from16 v127, v10

    move-object/from16 v3, v17

    move-object/from16 v12, v18

    move-object/from16 v13, v19

    move-object/from16 v11, v20

    move-object/from16 v112, v26

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v126, v38

    move-object/from16 v10, v41

    move-object/from16 v9, v42

    move-object/from16 v8, v43

    move-object/from16 v1, v45

    move-object/from16 v7, v46

    move-object/from16 v4, v47

    move-object/from16 v5, v48

    move-object/from16 v44, v50

    move-object/from16 v33, v51

    move-object/from16 v129, v52

    move-object/from16 v15, v53

    move-object/from16 v22, v54

    move-object/from16 v120, v55

    move-object/from16 v20, v56

    const/4 v14, 0x0

    const/16 v34, 0x4

    const/16 v37, 0x0

    const/16 v128, 0x0

    goto/16 :goto_10d

    :catch_3
    move-object/from16 v145, p3

    move-object v7, v1

    move-object v11, v2

    move/from16 v90, v4

    move-object v15, v10

    move-object/from16 v1, v17

    move-object/from16 v12, v18

    move-object/from16 v14, v19

    move-object/from16 v9, v20

    move-object/from16 v141, v28

    move-object/from16 v10, v29

    move-object/from16 v8, v32

    move-object/from16 v142, v38

    move-object/from16 v0, v41

    move-object/from16 v13, v42

    move-object/from16 v6, v43

    move-object/from16 v3, v46

    move-object/from16 v5, v47

    move-object/from16 v4, v48

    move-object/from16 v44, v50

    move-object/from16 v33, v51

    move-object/from16 v144, v52

    move-object/from16 v22, v53

    move-object/from16 v21, v54

    move-object/from16 v20, v55

    move-object/from16 v19, v56

    const/4 v2, 0x1

    const/16 v34, 0x4

    const/16 v37, 0x0

    const/16 v40, 0x0

    const/16 v143, 0x0

    goto/16 :goto_12b

    :cond_3
    iget v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->I$0:I

    iget-object v4, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$29:Ljava/lang/Object;

    check-cast v4, Ljava/io/File;

    iget-object v6, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$28:Ljava/lang/Object;

    check-cast v6, Lcom/bachatas4/android/runtime/session/RuntimeSurface;

    iget-object v7, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$27:Ljava/lang/Object;

    check-cast v7, Ljava/nio/file/Path;

    iget-object v8, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$26:Ljava/lang/Object;

    check-cast v8, Lcom/bachatas4/android/runtime/settings/ResolvedRuntimeProfile;

    iget-object v9, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$25:Ljava/lang/Object;

    check-cast v9, Ljava/io/File;

    iget-object v11, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$24:Ljava/lang/Object;

    check-cast v11, Ljava/io/File;

    iget-object v13, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$23:Ljava/lang/Object;

    check-cast v13, Ljava/io/File;

    move/from16 v16, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$22:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$BooleanRef;

    move-object/from16 p1, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$21:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$ObjectRef;

    move-object/from16 p2, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$20:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$ObjectRef;

    move-object/from16 p3, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$19:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$ObjectRef;

    move-object/from16 v17, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$18:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$ObjectRef;

    move-object/from16 v18, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$17:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$ObjectRef;

    move-object/from16 v19, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$16:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$BooleanRef;

    move-object/from16 v20, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$15:Ljava/lang/Object;

    check-cast v1, Lcom/bachatas4/android/runtime/session/FrameTelemetryReporter;

    move-object/from16 v41, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$14:Ljava/lang/Object;

    check-cast v1, Ljava/io/File;

    move-object/from16 v42, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$13:Ljava/lang/Object;

    check-cast v1, Ljava/lang/String;

    move-object/from16 v43, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$12:Ljava/lang/Object;

    check-cast v1, Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpointStore;

    move-object/from16 v44, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$11:Ljava/lang/Object;

    check-cast v1, Lcom/bachatas4/android/runtime/diagnostics/SessionLog;

    move-object/from16 v45, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$10:Ljava/lang/Object;

    check-cast v1, Ljava/nio/file/Path;

    move-object/from16 v46, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$9:Ljava/lang/Object;

    check-cast v1, Ljava/io/File;

    move-object/from16 v47, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$8:Ljava/lang/Object;

    check-cast v1, Ljava/util/concurrent/ExecutorService;

    move-object/from16 v48, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$7:Ljava/lang/Object;

    check-cast v1, Ljava/nio/file/Path;

    move-object/from16 v49, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$6:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$ObjectRef;

    move-object/from16 v50, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$5:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$ObjectRef;

    move-object/from16 v51, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$4:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$ObjectRef;

    move-object/from16 v52, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$3:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$ObjectRef;

    move-object/from16 v53, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$2:Ljava/lang/Object;

    check-cast v1, Lcom/bachatas4/android/runtime/process/RuntimeVulkanDriver;

    move-object/from16 v54, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$1:Ljava/lang/Object;

    check-cast v1, Ljava/lang/String;

    move-object/from16 v55, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$0:Ljava/lang/Object;

    check-cast v1, Ljava/lang/String;

    :try_start_2
    invoke-static {v0}, Lkotlin/ResultKt;->throwOnFailure(Ljava/lang/Object;)V
    :try_end_2
    .catch Ljava/util/concurrent/CancellationException; {:try_start_2 .. :try_end_2} :catch_5
    .catch Ljava/lang/Exception; {:try_start_2 .. :try_end_2} :catch_4
    .catchall {:try_start_2 .. :try_end_2} :catchall_2

    move-object/from16 v92, p1

    move-object/from16 v89, p2

    move-object/from16 v88, p3

    move-object/from16 v91, v4

    move-object/from16 v93, v7

    move-object/from16 p1, v8

    move-object/from16 v94, v9

    move-object/from16 v95, v11

    move-object v0, v12

    move-object/from16 v56, v13

    move/from16 v90, v16

    move-object/from16 v87, v19

    move-object/from16 v4, v41

    move-object/from16 v13, v47

    move-object/from16 v12, v48

    move-object/from16 v11, v49

    move-object/from16 v9, v51

    move-object/from16 v8, v52

    move-object/from16 v7, v53

    move-object/from16 v53, v10

    move-object/from16 v41, v17

    move-object/from16 v10, v50

    move-object/from16 v17, v5

    move-object/from16 v5, v45

    move-object/from16 v45, v6

    move-object/from16 v6, v44

    move-object/from16 v44, v46

    move-object/from16 v46, v15

    move-object/from16 v15, v43

    move-object/from16 v43, v3

    move-object/from16 v3, v42

    move-object/from16 v42, v18

    :goto_2
    move-object/from16 v47, v20

    goto/16 :goto_9

    :catch_4
    move-exception v0

    move-object/from16 v3, p1

    move-object/from16 v12, p2

    move-object/from16 v13, p3

    move-object v6, v1

    move-object/from16 v127, v10

    move/from16 v90, v16

    move-object/from16 v11, v17

    move-object/from16 v10, v18

    move-object/from16 v9, v19

    move-object/from16 v8, v20

    move-object/from16 v112, v26

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v126, v38

    move-object/from16 v1, v42

    move-object/from16 v7, v43

    move-object/from16 v4, v44

    move-object/from16 v5, v45

    move-object/from16 v44, v47

    move-object/from16 v33, v48

    move-object/from16 v129, v49

    move-object/from16 v15, v50

    move-object/from16 v22, v51

    move-object/from16 v120, v52

    move-object/from16 v20, v53

    const/4 v14, 0x0

    const/16 v34, 0x4

    const/16 v37, 0x0

    const/16 v128, 0x0

    const/16 v130, 0x0

    move-object/from16 v16, v0

    goto/16 :goto_10d

    :catch_5
    move-object/from16 v12, p2

    move-object/from16 v14, p3

    move-object v7, v1

    move-object v11, v2

    move-object v15, v10

    move/from16 v90, v16

    move-object/from16 v9, v17

    move-object/from16 v0, v18

    move-object/from16 v13, v19

    move-object/from16 v6, v20

    move-object/from16 v141, v28

    move-object/from16 v10, v29

    move-object/from16 v8, v32

    move-object/from16 v142, v38

    move-object/from16 v3, v43

    move-object/from16 v5, v44

    move-object/from16 v4, v45

    move-object/from16 v44, v47

    move-object/from16 v33, v48

    move-object/from16 v144, v49

    move-object/from16 v22, v50

    move-object/from16 v21, v51

    move-object/from16 v20, v52

    move-object/from16 v19, v53

    const/4 v2, 0x1

    const/16 v34, 0x4

    const/16 v37, 0x0

    const/16 v40, 0x0

    const/16 v143, 0x0

    goto/16 :goto_6

    :cond_4
    iget v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->I$0:I

    iget-object v4, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$27:Ljava/lang/Object;

    check-cast v4, Ljava/nio/file/Path;

    iget-object v6, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$26:Ljava/lang/Object;

    check-cast v6, Lcom/bachatas4/android/runtime/settings/ResolvedRuntimeProfile;

    iget-object v7, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$25:Ljava/lang/Object;

    check-cast v7, Ljava/io/File;

    iget-object v8, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$24:Ljava/lang/Object;

    check-cast v8, Ljava/io/File;

    iget-object v9, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$23:Ljava/lang/Object;

    check-cast v9, Ljava/io/File;

    iget-object v11, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$22:Ljava/lang/Object;

    check-cast v11, Lkotlin/jvm/internal/Ref$BooleanRef;

    move/from16 v17, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$21:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$ObjectRef;

    move-object/from16 p1, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$20:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$ObjectRef;

    move-object/from16 p2, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$19:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$ObjectRef;

    move-object/from16 p3, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$18:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$ObjectRef;

    move-object/from16 v18, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$17:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$ObjectRef;

    move-object/from16 v19, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$16:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$BooleanRef;

    move-object/from16 v20, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$15:Ljava/lang/Object;

    check-cast v1, Lcom/bachatas4/android/runtime/session/FrameTelemetryReporter;

    move-object/from16 v41, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$14:Ljava/lang/Object;

    check-cast v1, Ljava/io/File;

    move-object/from16 v42, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$13:Ljava/lang/Object;

    check-cast v1, Ljava/lang/String;

    move-object/from16 v43, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$12:Ljava/lang/Object;

    check-cast v1, Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpointStore;

    move-object/from16 v44, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$11:Ljava/lang/Object;

    check-cast v1, Lcom/bachatas4/android/runtime/diagnostics/SessionLog;

    move-object/from16 v45, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$10:Ljava/lang/Object;

    check-cast v1, Ljava/nio/file/Path;

    move-object/from16 v46, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$9:Ljava/lang/Object;

    check-cast v1, Ljava/io/File;

    move-object/from16 v47, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$8:Ljava/lang/Object;

    check-cast v1, Ljava/util/concurrent/ExecutorService;

    move-object/from16 v48, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$7:Ljava/lang/Object;

    check-cast v1, Ljava/nio/file/Path;

    move-object/from16 v49, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$6:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$ObjectRef;

    move-object/from16 v50, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$5:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$ObjectRef;

    move-object/from16 v51, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$4:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$ObjectRef;

    move-object/from16 v52, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$3:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$ObjectRef;

    move-object/from16 v53, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$2:Ljava/lang/Object;

    check-cast v1, Lcom/bachatas4/android/runtime/process/RuntimeVulkanDriver;

    move-object/from16 v54, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$1:Ljava/lang/Object;

    check-cast v1, Ljava/lang/String;

    move-object/from16 v55, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$0:Ljava/lang/Object;

    check-cast v1, Ljava/lang/String;

    :try_start_3
    invoke-static {v0}, Lkotlin/ResultKt;->throwOnFailure(Ljava/lang/Object;)V
    :try_end_3
    .catch Ljava/util/concurrent/CancellationException; {:try_start_3 .. :try_end_3} :catch_7
    .catch Ljava/lang/Exception; {:try_start_3 .. :try_end_3} :catch_6
    .catchall {:try_start_3 .. :try_end_3} :catchall_2

    move-object/from16 v80, p1

    move-object/from16 v79, p2

    move-object/from16 v78, p3

    move-object/from16 p1, v0

    move-object/from16 v83, v4

    move-object/from16 v84, v6

    move-object/from16 v85, v7

    move-object/from16 v86, v8

    move-object/from16 v56, v9

    move-object/from16 v82, v11

    move-object v0, v12

    move/from16 v81, v17

    move-object/from16 v77, v18

    move-object/from16 v76, v19

    move-object/from16 v11, v41

    move-object/from16 v6, v44

    move-object/from16 v44, v46

    move-object/from16 v12, v48

    move-object/from16 v4, v49

    move-object/from16 v9, v51

    move-object/from16 v8, v52

    move-object/from16 v7, v53

    move-object/from16 v17, v5

    move-object/from16 v53, v10

    move-object/from16 v18, v13

    move-object/from16 v46, v15

    move-object/from16 v10, v43

    move-object/from16 v5, v45

    move-object/from16 v13, v47

    move-object/from16 v15, v50

    move-object/from16 v43, v3

    move-object/from16 v3, v42

    :goto_3
    move-object/from16 v2, v20

    goto/16 :goto_8

    :catchall_2
    move-exception v0

    move-object v4, v0

    move-object/from16 v154, v10

    move-object/from16 v151, v27

    move-object/from16 v152, v28

    move-object/from16 v6, v29

    move-object/from16 v7, v30

    move-object/from16 v9, v31

    move-object/from16 v15, v32

    move-object/from16 v153, v38

    move-object/from16 v14, v44

    move-object/from16 v5, v45

    move-object/from16 v44, v47

    move-object/from16 v33, v48

    move-object/from16 v0, v49

    move-object/from16 v13, v50

    move-object/from16 v10, v51

    move-object/from16 v11, v52

    move-object/from16 v12, v53

    goto/16 :goto_5

    :catch_6
    move-exception v0

    move-object/from16 v12, p1

    move-object/from16 v13, p2

    move-object/from16 v16, v0

    move-object v6, v1

    move-object/from16 v127, v10

    move-object v3, v11

    move/from16 v90, v17

    move-object/from16 v10, v18

    move-object/from16 v9, v19

    move-object/from16 v8, v20

    move-object/from16 v112, v26

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v126, v38

    move-object/from16 v1, v42

    move-object/from16 v7, v43

    move-object/from16 v4, v44

    move-object/from16 v5, v45

    move-object/from16 v44, v47

    move-object/from16 v33, v48

    move-object/from16 v129, v49

    move-object/from16 v15, v50

    move-object/from16 v22, v51

    move-object/from16 v120, v52

    move-object/from16 v20, v53

    const/4 v14, 0x0

    const/16 v34, 0x4

    const/16 v37, 0x0

    const/16 v128, 0x0

    const/16 v130, 0x0

    move-object/from16 v11, p3

    goto/16 :goto_10d

    :catch_7
    move-object/from16 v12, p1

    move-object/from16 v14, p2

    move-object/from16 v9, p3

    move-object v7, v1

    move-object v15, v10

    move-object v1, v11

    move/from16 v90, v17

    move-object/from16 v0, v18

    move-object/from16 v13, v19

    move-object/from16 v6, v20

    move-object/from16 v141, v28

    move-object/from16 v10, v29

    move-object/from16 v8, v32

    move-object/from16 v142, v38

    move-object/from16 v3, v43

    move-object/from16 v5, v44

    move-object/from16 v4, v45

    move-object/from16 v44, v47

    move-object/from16 v33, v48

    move-object/from16 v144, v49

    move-object/from16 v22, v50

    move-object/from16 v21, v51

    move-object/from16 v20, v52

    move-object/from16 v19, v53

    const/16 v34, 0x4

    const/16 v37, 0x0

    const/16 v40, 0x0

    const/16 v143, 0x0

    const/16 v145, 0x0

    move-object v11, v2

    :goto_4
    const/4 v2, 0x1

    goto/16 :goto_12b

    :cond_5
    iget v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->I$0:I

    iget-object v4, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$24:Ljava/lang/Object;

    check-cast v4, Ljava/io/File;

    iget-object v6, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$23:Ljava/lang/Object;

    check-cast v6, Ljava/io/File;

    iget-object v7, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$22:Ljava/lang/Object;

    check-cast v7, Ljava/io/File;

    move/from16 v17, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$21:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$BooleanRef;

    move-object/from16 p1, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$20:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$ObjectRef;

    move-object/from16 p2, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$19:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$ObjectRef;

    move-object/from16 p3, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$18:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$ObjectRef;

    move-object/from16 v18, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$17:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$ObjectRef;

    move-object/from16 v19, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$16:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$ObjectRef;

    move-object/from16 v20, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$15:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$BooleanRef;

    move-object/from16 v41, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$14:Ljava/lang/Object;

    check-cast v1, Lcom/bachatas4/android/runtime/session/FrameTelemetryReporter;

    move-object/from16 v42, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$13:Ljava/lang/Object;

    check-cast v1, Ljava/io/File;

    move-object/from16 v43, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$12:Ljava/lang/Object;

    check-cast v1, Ljava/lang/String;

    move-object/from16 v44, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$11:Ljava/lang/Object;

    check-cast v1, Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpointStore;

    move-object/from16 v45, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$10:Ljava/lang/Object;

    check-cast v1, Lcom/bachatas4/android/runtime/diagnostics/SessionLog;

    move-object/from16 v46, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$9:Ljava/lang/Object;

    check-cast v1, Ljava/nio/file/Path;

    move-object/from16 v47, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$8:Ljava/lang/Object;

    check-cast v1, Ljava/io/File;

    move-object/from16 v48, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$7:Ljava/lang/Object;

    check-cast v1, Ljava/util/concurrent/ExecutorService;

    move-object/from16 v49, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$6:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$ObjectRef;

    move-object/from16 v50, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$5:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$ObjectRef;

    move-object/from16 v51, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$4:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$ObjectRef;

    move-object/from16 v52, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$3:Ljava/lang/Object;

    check-cast v1, Lkotlin/jvm/internal/Ref$ObjectRef;

    move-object/from16 v53, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$2:Ljava/lang/Object;

    check-cast v1, Lcom/bachatas4/android/runtime/process/RuntimeVulkanDriver;

    move-object/from16 v54, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$1:Ljava/lang/Object;

    check-cast v1, Ljava/lang/String;

    move-object/from16 v55, v1

    iget-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$0:Ljava/lang/Object;

    check-cast v1, Ljava/lang/String;

    :try_start_4
    invoke-static {v0}, Lkotlin/ResultKt;->throwOnFailure(Ljava/lang/Object;)V
    :try_end_4
    .catch Ljava/util/concurrent/CancellationException; {:try_start_4 .. :try_end_4} :catch_9
    .catch Ljava/lang/Exception; {:try_start_4 .. :try_end_4} :catch_8
    .catchall {:try_start_4 .. :try_end_4} :catchall_3

    move-object/from16 v2, v42

    move-object/from16 v42, v11

    move-object v11, v2

    move-object/from16 v64, p1

    move-object/from16 v62, p2

    move-object/from16 p1, v0

    move-object/from16 v63, v4

    move-object/from16 v65, v6

    move-object/from16 v56, v7

    move-object v0, v12

    move/from16 v66, v17

    move-object/from16 v61, v18

    move-object/from16 v60, v19

    move-object/from16 v59, v20

    move-object/from16 v2, v43

    move-object/from16 v12, v44

    move-object/from16 v6, v45

    move-object/from16 v44, v47

    move-object/from16 v7, v53

    move-object/from16 p2, v55

    move-object/from16 v4, p3

    move-object/from16 v17, v5

    move-object/from16 v19, v8

    move-object/from16 v20, v9

    move-object/from16 v53, v10

    move-object/from16 v18, v13

    move-object/from16 v43, v15

    move-object/from16 v45, v41

    move-object/from16 v5, v46

    move-object/from16 v13, v48

    move-object/from16 v10, v49

    move-object/from16 v15, v50

    move-object/from16 v9, v51

    move-object/from16 v8, v52

    move-object/from16 v41, v3

    goto/16 :goto_7

    :catchall_3
    move-exception v0

    move-object v4, v0

    move-object/from16 v154, v10

    move-object/from16 v151, v27

    move-object/from16 v152, v28

    move-object/from16 v6, v29

    move-object/from16 v7, v30

    move-object/from16 v9, v31

    move-object/from16 v15, v32

    move-object/from16 v153, v38

    move-object/from16 v14, v45

    move-object/from16 v5, v46

    move-object/from16 v44, v48

    move-object/from16 v33, v49

    move-object/from16 v13, v50

    move-object/from16 v10, v51

    move-object/from16 v11, v52

    move-object/from16 v12, v53

    const/4 v0, 0x0

    :goto_5
    const/4 v1, 0x4

    const/4 v3, 0x0

    const/4 v8, 0x1

    const/16 v37, 0x0

    const/16 v155, 0x0

    goto/16 :goto_146

    :catch_8
    move-exception v0

    move-object/from16 v3, p1

    move-object/from16 v12, p2

    move-object/from16 v13, p3

    move-object/from16 v16, v0

    move-object v6, v1

    move-object/from16 v127, v10

    move/from16 v90, v17

    move-object/from16 v11, v18

    move-object/from16 v10, v19

    move-object/from16 v9, v20

    move-object/from16 v112, v26

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v126, v38

    move-object/from16 v8, v41

    move-object/from16 v1, v43

    move-object/from16 v7, v44

    move-object/from16 v4, v45

    move-object/from16 v5, v46

    move-object/from16 v44, v48

    move-object/from16 v33, v49

    move-object/from16 v15, v50

    move-object/from16 v22, v51

    move-object/from16 v120, v52

    move-object/from16 v20, v53

    const/4 v14, 0x0

    const/16 v34, 0x4

    const/16 v37, 0x0

    const/16 v128, 0x0

    const/16 v129, 0x0

    const/16 v130, 0x0

    goto/16 :goto_10d

    :catch_9
    move-object/from16 v12, p2

    move-object/from16 v14, p3

    move-object v7, v1

    move-object v11, v2

    move-object v15, v10

    move/from16 v90, v17

    move-object/from16 v9, v18

    move-object/from16 v0, v19

    move-object/from16 v13, v20

    move-object/from16 v141, v28

    move-object/from16 v10, v29

    move-object/from16 v8, v32

    move-object/from16 v142, v38

    move-object/from16 v6, v41

    move-object/from16 v3, v44

    move-object/from16 v5, v45

    move-object/from16 v4, v46

    move-object/from16 v44, v48

    move-object/from16 v33, v49

    move-object/from16 v22, v50

    move-object/from16 v21, v51

    move-object/from16 v20, v52

    move-object/from16 v19, v53

    const/4 v2, 0x1

    const/16 v34, 0x4

    const/16 v37, 0x0

    const/16 v40, 0x0

    const/16 v143, 0x0

    const/16 v144, 0x0

    :goto_6
    const/16 v145, 0x0

    move-object/from16 v1, p1

    goto/16 :goto_12b

    :cond_6
    invoke-static {v0}, Lkotlin/ResultKt;->throwOnFailure(Ljava/lang/Object;)V

    .line 120
    new-instance v4, Lkotlin/jvm/internal/Ref$ObjectRef;

    invoke-direct {v4}, Lkotlin/jvm/internal/Ref$ObjectRef;-><init>()V

    .line 121
    new-instance v6, Lkotlin/jvm/internal/Ref$ObjectRef;

    invoke-direct {v6}, Lkotlin/jvm/internal/Ref$ObjectRef;-><init>()V

    .line 122
    new-instance v7, Lkotlin/jvm/internal/Ref$ObjectRef;

    invoke-direct {v7}, Lkotlin/jvm/internal/Ref$ObjectRef;-><init>()V

    move-object v0, v12

    .line 123
    new-instance v12, Lkotlin/jvm/internal/Ref$ObjectRef;

    invoke-direct {v12}, Lkotlin/jvm/internal/Ref$ObjectRef;-><init>()V

    move-object/from16 v17, v5

    .line 126
    invoke-static {}, Ljava/util/concurrent/Executors;->newSingleThreadExecutor()Ljava/util/concurrent/ExecutorService;

    move-result-object v5

    move-object/from16 v18, v13

    .line 127
    new-instance v13, Ljava/io/File;

    move-object/from16 v41, v3

    invoke-virtual {v2}, Lcom/bachatas4/android/service/EmulationService;->getFilesDir()Ljava/io/File;

    move-result-object v3

    move-object/from16 v19, v8

    const-string v8, "runtime-control.sock"

    invoke-direct {v13, v3, v8}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    invoke-virtual {v13}, Ljava/io/File;->delete()Z

    .line 128
    new-instance v3, Ljava/io/File;

    invoke-virtual {v2}, Lcom/bachatas4/android/service/EmulationService;->getFilesDir()Ljava/io/File;

    move-result-object v8

    move-object/from16 v20, v9

    const-string v9, "logs"

    invoke-direct {v3, v8, v9}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    invoke-virtual {v3}, Ljava/io/File;->toPath()Ljava/nio/file/Path;

    move-result-object v3

    .line 129
    sget-object v8, Lcom/bachatas4/android/runtime/diagnostics/SessionLog;->Companion:Lcom/bachatas4/android/runtime/diagnostics/SessionLog$Companion;

    invoke-static {v3}, Lkotlin/jvm/internal/Intrinsics;->checkNotNull(Ljava/lang/Object;)V

    const/16 v9, 0x9

    invoke-virtual {v8, v3, v9}, Lcom/bachatas4/android/runtime/diagnostics/SessionLog$Companion;->prune(Ljava/nio/file/Path;I)V

    .line 130
    iget-object v8, v2, Lcom/bachatas4/android/service/EmulationService;->userRequestedStop:Ljava/util/concurrent/atomic/AtomicBoolean;

    const/4 v9, 0x0

    invoke-virtual {v8, v9}, Ljava/util/concurrent/atomic/AtomicBoolean;->set(Z)V

    .line 131
    sget-object v8, Lcom/bachatas4/android/runtime/diagnostics/SessionLog;->Companion:Lcom/bachatas4/android/runtime/diagnostics/SessionLog$Companion;

    .line 134
    invoke-static {}, Ljava/time/Instant;->now()Ljava/time/Instant;

    move-result-object v9

    const-string v2, "now(...)"

    invoke-static {v9, v2}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullExpressionValue(Ljava/lang/Object;Ljava/lang/String;)V

    .line 135
    invoke-static {}, Ljava/util/UUID;->randomUUID()Ljava/util/UUID;

    move-result-object v2

    invoke-virtual {v2}, Ljava/util/UUID;->toString()Ljava/lang/String;

    move-result-object v2

    move-object/from16 v42, v11

    const-string v11, "toString(...)"

    invoke-static {v2, v11}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullExpressionValue(Ljava/lang/Object;Ljava/lang/String;)V

    const/16 v11, 0x8

    move-object/from16 v43, v15

    const/4 v15, 0x0

    invoke-virtual {v2, v15, v11}, Ljava/lang/String;->substring(II)Ljava/lang/String;

    move-result-object v2

    const-string v11, "substring(...)"

    invoke-static {v2, v11}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullExpressionValue(Ljava/lang/Object;Ljava/lang/String;)V

    .line 131
    invoke-virtual {v8, v3, v1, v9, v2}, Lcom/bachatas4/android/runtime/diagnostics/SessionLog$Companion;->create(Ljava/nio/file/Path;Ljava/lang/String;Ljava/time/Instant;Ljava/lang/String;)Lcom/bachatas4/android/runtime/diagnostics/SessionLog;

    move-result-object v46

    .line 137
    new-instance v44, Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpointStore;

    invoke-virtual/range {v46 .. v46}, Lcom/bachatas4/android/runtime/diagnostics/SessionLog;->getDirectory()Ljava/nio/file/Path;

    move-result-object v45

    const/16 v49, 0xc

    const/16 v50, 0x0

    const/16 v47, 0x0

    const/16 v48, 0x0

    invoke-direct/range {v44 .. v50}, Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpointStore;-><init>(Ljava/nio/file/Path;Lcom/bachatas4/android/runtime/diagnostics/SessionLog;Lkotlinx/serialization/json/Json;Lkotlin/jvm/functions/Function0;ILkotlin/jvm/internal/DefaultConstructorMarker;)V

    move-object/from16 v8, v44

    move-object/from16 v2, v46

    .line 138
    sget-object v9, Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpoint;->SESSION_CREATED:Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpoint;

    invoke-virtual {v8, v9}, Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpointStore;->mark(Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpoint;)V

    .line 139
    sget-object v9, Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpoint;->SESSION_DIRECTORY_READY:Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpoint;

    invoke-virtual {v8, v9}, Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpointStore;->mark(Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpoint;)V

    .line 140
    sget-object v9, Lcom/bachatas4/android/runtime/diagnostics/DiagnosticReportIds;->INSTANCE:Lcom/bachatas4/android/runtime/diagnostics/DiagnosticReportIds;

    const/4 v11, 0x3

    const/4 v15, 0x0

    invoke-static {v9, v15, v15, v11, v15}, Lcom/bachatas4/android/runtime/diagnostics/DiagnosticReportIds;->generate$default(Lcom/bachatas4/android/runtime/diagnostics/DiagnosticReportIds;Ljava/time/Clock;Ljava/security/SecureRandom;ILjava/lang/Object;)Ljava/lang/String;

    move-result-object v9

    .line 141
    invoke-virtual {v2}, Lcom/bachatas4/android/runtime/diagnostics/SessionLog;->getBackendLog()Ljava/nio/file/Path;

    move-result-object v11

    invoke-interface {v11}, Ljava/nio/file/Path;->toFile()Ljava/io/File;

    move-result-object v11

    move-object/from16 v44, v3

    .line 142
    new-instance v3, Lcom/bachatas4/android/runtime/session/FrameTelemetryReporter;

    move-object/from16 v46, v11

    move-object/from16 v45, v12

    const-wide/16 v11, 0x0

    move-object/from16 v47, v8

    const/4 v8, 0x1

    invoke-direct {v3, v11, v12, v8, v15}, Lcom/bachatas4/android/runtime/session/FrameTelemetryReporter;-><init>(JILkotlin/jvm/internal/DefaultConstructorMarker;)V

    .line 143
    new-instance v8, Lkotlin/jvm/internal/Ref$BooleanRef;

    invoke-direct {v8}, Lkotlin/jvm/internal/Ref$BooleanRef;-><init>()V

    .line 144
    new-instance v11, Lkotlin/jvm/internal/Ref$ObjectRef;

    invoke-direct {v11}, Lkotlin/jvm/internal/Ref$ObjectRef;-><init>()V

    .line 146
    new-instance v12, Lkotlin/jvm/internal/Ref$ObjectRef;

    invoke-direct {v12}, Lkotlin/jvm/internal/Ref$ObjectRef;-><init>()V

    const-string v15, "unknown"

    iput-object v15, v12, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    .line 147
    new-instance v15, Lkotlin/jvm/internal/Ref$ObjectRef;

    invoke-direct {v15}, Lkotlin/jvm/internal/Ref$ObjectRef;-><init>()V

    new-instance v48, Lcom/bachatas4/android/runtime/diagnostics/DiagnosticDriverInfo;

    const/16 v56, 0x7c

    const/16 v57, 0x0

    const-string v49, "unknown"

    const-string v50, "unknown"

    const/16 v51, 0x0

    const/16 v52, 0x0

    const/16 v53, 0x0

    const/16 v54, 0x0

    const/16 v55, 0x0

    invoke-direct/range {v48 .. v57}, Lcom/bachatas4/android/runtime/diagnostics/DiagnosticDriverInfo;-><init>(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;ILkotlin/jvm/internal/DefaultConstructorMarker;)V

    move-object/from16 v49, v12

    move-object/from16 v12, v48

    iput-object v12, v15, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    .line 148
    new-instance v12, Lkotlin/jvm/internal/Ref$ObjectRef;

    invoke-direct {v12}, Lkotlin/jvm/internal/Ref$ObjectRef;-><init>()V

    move-object/from16 v48, v12

    .line 149
    new-instance v12, Lkotlin/jvm/internal/Ref$ObjectRef;

    invoke-direct {v12}, Lkotlin/jvm/internal/Ref$ObjectRef;-><init>()V

    iput-object v1, v12, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    move-object/from16 v50, v15

    .line 151
    new-instance v15, Lkotlin/jvm/internal/Ref$BooleanRef;

    invoke-direct {v15}, Lkotlin/jvm/internal/Ref$BooleanRef;-><init>()V

    move-object/from16 v51, v15

    .line 152
    new-instance v15, Ljava/lang/StringBuilder;

    move-object/from16 v52, v11

    const-string v11, "start game="

    invoke-direct {v15, v11}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v15, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v11

    const-string v15, " intentDriver="

    invoke-virtual {v11, v15}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v11

    move-object/from16 v15, p3

    invoke-virtual {v11, v15}, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;

    move-result-object v11

    const-string v15, " reportId="

    invoke-virtual {v11, v15}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v11

    invoke-virtual {v11, v9}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v11

    invoke-virtual {v11}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v11

    invoke-virtual {v2, v10, v11}, Lcom/bachatas4/android/runtime/diagnostics/SessionLog;->info(Ljava/lang/String;Ljava/lang/String;)V

    .line 153
    sget-object v11, Lcom/bachatas4/android/runtime/input/GamepadInputManager;->INSTANCE:Lcom/bachatas4/android/runtime/input/GamepadInputManager;

    invoke-virtual {v11}, Lcom/bachatas4/android/runtime/input/GamepadInputManager;->onSessionStart()V

    .line 156
    sget-object v11, Landroid/os/Build;->MANUFACTURER:Ljava/lang/String;

    sget-object v15, Landroid/os/Build;->MODEL:Ljava/lang/String;

    move-object/from16 v53, v10

    sget v10, Landroid/os/Build$VERSION;->SDK_INT:I

    move-object/from16 v54, v8

    new-instance v8, Ljava/lang/StringBuilder;

    move-object/from16 v55, v3

    const-string v3, "manufacturer="

    invoke-direct {v8, v3}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v8, v11}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v3

    const-string v8, " model="

    invoke-virtual {v3, v8}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v3

    invoke-virtual {v3, v15}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v3

    const-string v8, " sdk="

    invoke-virtual {v3, v8}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v3

    invoke-virtual {v3, v10}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    move-result-object v3

    invoke-virtual {v3}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v3

    .line 154
    const-string v8, "Device"

    invoke-virtual {v2, v8, v3}, Lcom/bachatas4/android/runtime/diagnostics/SessionLog;->info(Ljava/lang/String;Ljava/lang/String;)V

    .line 160
    :try_start_5
    move-object v3, v1

    check-cast v3, Ljava/lang/CharSequence;
    :try_end_5
    .catch Ljava/util/concurrent/CancellationException; {:try_start_5 .. :try_end_5} :catch_112
    .catch Ljava/lang/Exception; {:try_start_5 .. :try_end_5} :catch_111
    .catchall {:try_start_5 .. :try_end_5} :catchall_4d

    :try_start_6
    new-instance v8, Lkotlin/text/Regex;

    const-string v10, "[A-Za-z0-9._-]+"

    invoke-direct {v8, v10}, Lkotlin/text/Regex;-><init>(Ljava/lang/String;)V

    invoke-virtual {v8, v3}, Lkotlin/text/Regex;->matches(Ljava/lang/CharSequence;)Z

    move-result v3

    if-eqz v3, :cond_32

    .line 161
    new-instance v3, Ljava/io/File;

    invoke-virtual/range {p0 .. p0}, Lcom/bachatas4/android/service/EmulationService;->getFilesDir()Ljava/io/File;

    move-result-object v8

    const-string v10, "games"

    invoke-direct {v3, v8, v10}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    invoke-virtual {v3}, Ljava/io/File;->getCanonicalFile()Ljava/io/File;

    move-result-object v3

    .line 162
    new-instance v8, Ljava/io/File;

    invoke-virtual/range {p0 .. p0}, Lcom/bachatas4/android/service/EmulationService;->getFilesDir()Ljava/io/File;

    move-result-object v10

    move-object/from16 v11, p2

    invoke-direct {v8, v10, v11}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    invoke-virtual {v8}, Ljava/io/File;->getCanonicalFile()Ljava/io/File;

    move-result-object v8

    .line 163
    invoke-virtual {v8}, Ljava/io/File;->toPath()Ljava/nio/file/Path;

    move-result-object v10

    invoke-virtual {v3}, Ljava/io/File;->toPath()Ljava/nio/file/Path;

    move-result-object v15

    invoke-interface {v10, v15}, Ljava/nio/file/Path;->startsWith(Ljava/nio/file/Path;)Z

    move-result v10

    nop

    nop

    .line 164
    new-instance v10, Ljava/io/File;

    const-string v15, "eboot.bin"

    invoke-direct {v10, v8, v15}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    .line 165
    invoke-virtual {v10}, Ljava/io/File;->isFile()Z

    move-result v15

    if-eqz v15, :cond_31

    .line 166
    const-string v15, "Content"

    move-object/from16 v56, v3

    const-string v3, "validated game root and eboot.bin"

    invoke-virtual {v2, v15, v3}, Lcom/bachatas4/android/runtime/diagnostics/SessionLog;->info(Ljava/lang/String;Ljava/lang/String;)V

    .line 167
    iput-object v1, v12, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    .line 168
    invoke-virtual/range {p0 .. p0}, Lcom/bachatas4/android/service/EmulationService;->getLaunchProfileProvider()Lcom/bachatas4/android/RuntimeLaunchProfileProvider;

    move-result-object v3

    iput-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$0:Ljava/lang/Object;

    invoke-static {v11}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v15

    iput-object v15, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$1:Ljava/lang/Object;

    invoke-static/range {p3 .. p3}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v15

    iput-object v15, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$2:Ljava/lang/Object;

    iput-object v4, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$3:Ljava/lang/Object;

    iput-object v6, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$4:Ljava/lang/Object;

    iput-object v7, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$5:Ljava/lang/Object;
    :try_end_6
    .catch Ljava/util/concurrent/CancellationException; {:try_start_6 .. :try_end_6} :catch_110
    .catch Ljava/lang/Exception; {:try_start_6 .. :try_end_6} :catch_111
    .catchall {:try_start_6 .. :try_end_6} :catchall_4d

    move-object/from16 v15, v45

    :try_start_7
    iput-object v15, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$6:Ljava/lang/Object;

    iput-object v5, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$7:Ljava/lang/Object;

    iput-object v13, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$8:Ljava/lang/Object;
    :try_end_7
    .catch Ljava/util/concurrent/CancellationException; {:try_start_7 .. :try_end_7} :catch_10c
    .catch Ljava/lang/Exception; {:try_start_7 .. :try_end_7} :catch_10b
    .catchall {:try_start_7 .. :try_end_7} :catchall_4b

    move-object/from16 v45, v4

    :try_start_8
    invoke-static/range {v44 .. v44}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v4

    iput-object v4, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$9:Ljava/lang/Object;

    iput-object v2, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$10:Ljava/lang/Object;
    :try_end_8
    .catch Ljava/util/concurrent/CancellationException; {:try_start_8 .. :try_end_8} :catch_10d
    .catch Ljava/lang/Exception; {:try_start_8 .. :try_end_8} :catch_10a
    .catchall {:try_start_8 .. :try_end_8} :catchall_4a

    move-object/from16 v4, v47

    :try_start_9
    iput-object v4, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$11:Ljava/lang/Object;

    iput-object v9, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$12:Ljava/lang/Object;
    :try_end_9
    .catch Ljava/util/concurrent/CancellationException; {:try_start_9 .. :try_end_9} :catch_108
    .catch Ljava/lang/Exception; {:try_start_9 .. :try_end_9} :catch_107
    .catchall {:try_start_9 .. :try_end_9} :catchall_49

    move-object/from16 v47, v2

    move-object/from16 v2, v46

    :try_start_a
    iput-object v2, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$13:Ljava/lang/Object;
    :try_end_a
    .catch Ljava/util/concurrent/CancellationException; {:try_start_a .. :try_end_a} :catch_109
    .catch Ljava/lang/Exception; {:try_start_a .. :try_end_a} :catch_106
    .catchall {:try_start_a .. :try_end_a} :catchall_48

    move-object/from16 v46, v2

    move-object/from16 v2, v55

    :try_start_b
    iput-object v2, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$14:Ljava/lang/Object;
    :try_end_b
    .catch Ljava/util/concurrent/CancellationException; {:try_start_b .. :try_end_b} :catch_109
    .catch Ljava/lang/Exception; {:try_start_b .. :try_end_b} :catch_105
    .catchall {:try_start_b .. :try_end_b} :catchall_48

    move-object/from16 v55, v2

    move-object/from16 v2, v54

    :try_start_c
    iput-object v2, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$15:Ljava/lang/Object;
    :try_end_c
    .catch Ljava/util/concurrent/CancellationException; {:try_start_c .. :try_end_c} :catch_104
    .catch Ljava/lang/Exception; {:try_start_c .. :try_end_c} :catch_103
    .catchall {:try_start_c .. :try_end_c} :catchall_48

    move-object/from16 v54, v2

    move-object/from16 v2, v52

    :try_start_d
    iput-object v2, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$16:Ljava/lang/Object;
    :try_end_d
    .catch Ljava/util/concurrent/CancellationException; {:try_start_d .. :try_end_d} :catch_102
    .catch Ljava/lang/Exception; {:try_start_d .. :try_end_d} :catch_101
    .catchall {:try_start_d .. :try_end_d} :catchall_48

    move-object/from16 v52, v2

    move-object/from16 v2, v49

    :try_start_e
    iput-object v2, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$17:Ljava/lang/Object;
    :try_end_e
    .catch Ljava/util/concurrent/CancellationException; {:try_start_e .. :try_end_e} :catch_100
    .catch Ljava/lang/Exception; {:try_start_e .. :try_end_e} :catch_ff
    .catchall {:try_start_e .. :try_end_e} :catchall_48

    move-object/from16 v49, v2

    move-object/from16 v2, v50

    :try_start_f
    iput-object v2, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$18:Ljava/lang/Object;
    :try_end_f
    .catch Ljava/util/concurrent/CancellationException; {:try_start_f .. :try_end_f} :catch_fe
    .catch Ljava/lang/Exception; {:try_start_f .. :try_end_f} :catch_fd
    .catchall {:try_start_f .. :try_end_f} :catchall_48

    move-object/from16 v50, v2

    move-object/from16 v2, v48

    :try_start_10
    iput-object v2, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$19:Ljava/lang/Object;

    iput-object v12, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$20:Ljava/lang/Object;
    :try_end_10
    .catch Ljava/util/concurrent/CancellationException; {:try_start_10 .. :try_end_10} :catch_fc
    .catch Ljava/lang/Exception; {:try_start_10 .. :try_end_10} :catch_fb
    .catchall {:try_start_10 .. :try_end_10} :catchall_48

    move-object/from16 v48, v2

    move-object/from16 v2, v51

    :try_start_11
    iput-object v2, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$21:Ljava/lang/Object;
    :try_end_11
    .catch Ljava/util/concurrent/CancellationException; {:try_start_11 .. :try_end_11} :catch_fa
    .catch Ljava/lang/Exception; {:try_start_11 .. :try_end_11} :catch_f9
    .catchall {:try_start_11 .. :try_end_11} :catchall_48

    move-object/from16 v51, v2

    :try_start_12
    invoke-static/range {v56 .. v56}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v2

    iput-object v2, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$22:Ljava/lang/Object;

    iput-object v8, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$23:Ljava/lang/Object;

    iput-object v10, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$24:Ljava/lang/Object;
    :try_end_12
    .catch Ljava/util/concurrent/CancellationException; {:try_start_12 .. :try_end_12} :catch_109
    .catch Ljava/lang/Exception; {:try_start_12 .. :try_end_12} :catch_105
    .catchall {:try_start_12 .. :try_end_12} :catchall_48

    const/4 v2, 0x0

    :try_start_13
    iput v2, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->I$0:I
    :try_end_13
    .catch Ljava/util/concurrent/CancellationException; {:try_start_13 .. :try_end_13} :catch_f8
    .catch Ljava/lang/Exception; {:try_start_13 .. :try_end_13} :catch_f7
    .catchall {:try_start_13 .. :try_end_13} :catchall_47

    const/4 v2, 0x1

    :try_start_14
    iput v2, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->label:I
    :try_end_14
    .catch Ljava/util/concurrent/CancellationException; {:try_start_14 .. :try_end_14} :catch_f6
    .catch Ljava/lang/Exception; {:try_start_14 .. :try_end_14} :catch_105
    .catchall {:try_start_14 .. :try_end_14} :catchall_48

    :try_start_15
    invoke-virtual {v3, v1, v14}, Lcom/bachatas4/android/RuntimeLaunchProfileProvider;->resolve(Ljava/lang/String;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;

    move-result-object v2
    :try_end_15
    .catch Ljava/util/concurrent/CancellationException; {:try_start_15 .. :try_end_15} :catch_109
    .catch Ljava/lang/Exception; {:try_start_15 .. :try_end_15} :catch_105
    .catchall {:try_start_15 .. :try_end_15} :catchall_48

    move-object/from16 v3, v43

    if-ne v2, v3, :cond_7

    goto/16 :goto_b

    :cond_7
    move-object/from16 p1, v2

    move-object/from16 v43, v3

    move-object/from16 v65, v8

    move-object/from16 v63, v10

    move-object/from16 p2, v11

    move-object/from16 v62, v12

    move-object/from16 v2, v46

    move-object/from16 v60, v49

    move-object/from16 v61, v50

    move-object/from16 v64, v51

    move-object/from16 v59, v52

    move-object/from16 v11, v55

    const/16 v66, 0x0

    move-object v10, v5

    move-object v8, v6

    move-object v12, v9

    move-object/from16 v5, v47

    move-object v6, v4

    move-object v9, v7

    move-object/from16 v7, v45

    move-object/from16 v4, v48

    move-object/from16 v45, v54

    move-object/from16 v54, p3

    .line 119
    :goto_7
    :try_start_16
    move-object/from16 v3, p1

    check-cast v3, Lcom/bachatas4/android/runtime/settings/ResolvedRuntimeProfile;

    move-object/from16 v46, v11

    .line 170
    invoke-virtual {v3}, Lcom/bachatas4/android/runtime/settings/ResolvedRuntimeProfile;->getSchemaVersion()I

    move-result v11

    .line 171
    invoke-virtual {v3}, Lcom/bachatas4/android/runtime/settings/ResolvedRuntimeProfile;->getGuestBackend()Lcom/bachatas4/android/runtime/settings/RuntimeGuestBackend;

    move-result-object v47
    :try_end_16
    .catch Ljava/util/concurrent/CancellationException; {:try_start_16 .. :try_end_16} :catch_f5
    .catch Ljava/lang/Exception; {:try_start_16 .. :try_end_16} :catch_f4
    .catchall {:try_start_16 .. :try_end_16} :catchall_46

    move-object/from16 v48, v2

    :try_start_17
    invoke-virtual/range {v47 .. v47}, Lcom/bachatas4/android/runtime/settings/RuntimeGuestBackend;->name()Ljava/lang/String;

    move-result-object v2
    :try_end_17
    .catch Ljava/util/concurrent/CancellationException; {:try_start_17 .. :try_end_17} :catch_f5
    .catch Ljava/lang/Exception; {:try_start_17 .. :try_end_17} :catch_f3
    .catchall {:try_start_17 .. :try_end_17} :catchall_46

    move-object/from16 v47, v12

    .line 172
    :try_start_18
    invoke-virtual {v3}, Lcom/bachatas4/android/runtime/settings/ResolvedRuntimeProfile;->getDriverId()Ljava/lang/String;

    move-result-object v12
    :try_end_18
    .catch Ljava/util/concurrent/CancellationException; {:try_start_18 .. :try_end_18} :catch_f2
    .catch Ljava/lang/Exception; {:try_start_18 .. :try_end_18} :catch_f1
    .catchall {:try_start_18 .. :try_end_18} :catchall_46

    move-object/from16 v49, v13

    :try_start_19
    new-instance v13, Ljava/lang/StringBuilder;
    :try_end_19
    .catch Ljava/util/concurrent/CancellationException; {:try_start_19 .. :try_end_19} :catch_f0
    .catch Ljava/lang/Exception; {:try_start_19 .. :try_end_19} :catch_ef
    .catchall {:try_start_19 .. :try_end_19} :catchall_45

    move-object/from16 v50, v10

    move-object/from16 v10, v42

    :try_start_1a
    invoke-direct {v13, v10}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v13, v11}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    move-result-object v10

    const-string v11, ",\"guestBackend\":\""

    invoke-virtual {v10, v11}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v10

    invoke-virtual {v10, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v2

    const-string v10, "\",\"driverId\":\""

    invoke-virtual {v2, v10}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v2

    invoke-virtual {v2, v12}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v2

    const-string v10, "\"}"

    invoke-virtual {v2, v10}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v2

    invoke-virtual {v2}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v2

    .line 169
    iput-object v2, v4, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    .line 175
    const-string v2, "Config"

    .line 176
    invoke-virtual {v3}, Lcom/bachatas4/android/runtime/settings/ResolvedRuntimeProfile;->getSchemaVersion()I

    move-result v10

    invoke-virtual/range {p0 .. p0}, Lcom/bachatas4/android/service/EmulationService;->getLaunchProfileProvider()Lcom/bachatas4/android/RuntimeLaunchProfileProvider;

    move-result-object v11

    invoke-virtual {v11, v3}, Lcom/bachatas4/android/RuntimeLaunchProfileProvider;->explicitSettingIds(Lcom/bachatas4/android/runtime/settings/ResolvedRuntimeProfile;)Ljava/util/List;

    move-result-object v11

    move-object/from16 v67, v11

    check-cast v67, Ljava/lang/Iterable;

    const-string v11, ","

    move-object/from16 v68, v11

    check-cast v68, Ljava/lang/CharSequence;

    const/16 v74, 0x3e

    const/16 v75, 0x0

    const/16 v69, 0x0

    const/16 v70, 0x0

    const/16 v71, 0x0

    const/16 v72, 0x0

    const/16 v73, 0x0

    invoke-static/range {v67 .. v75}, Lkotlin/collections/CollectionsKt;->joinToString$default(Ljava/lang/Iterable;Ljava/lang/CharSequence;Ljava/lang/CharSequence;Ljava/lang/CharSequence;ILjava/lang/CharSequence;Lkotlin/jvm/functions/Function1;ILjava/lang/Object;)Ljava/lang/String;

    move-result-object v11

    new-instance v12, Ljava/lang/StringBuilder;

    move-object/from16 v13, v20

    invoke-direct {v12, v13}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v12, v10}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    move-result-object v10

    const-string v12, " settings="

    invoke-virtual {v10, v12}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v10

    invoke-virtual {v10, v11}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v10

    invoke-virtual {v10}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v10

    .line 174
    invoke-virtual {v5, v2, v10}, Lcom/bachatas4/android/runtime/diagnostics/SessionLog;->info(Ljava/lang/String;Ljava/lang/String;)V

    .line 179
    sget-object v2, Lcom/bachatas4/android/runtime/session/ManagedSession;->INSTANCE:Lcom/bachatas4/android/runtime/session/ManagedSession;

    new-instance v10, Lcom/bachatas4/android/runtime/session/ManagedSessionState$Preparing;

    const-string v11, "runtime"

    invoke-direct {v10, v11}, Lcom/bachatas4/android/runtime/session/ManagedSessionState$Preparing;-><init>(Ljava/lang/String;)V

    check-cast v10, Lcom/bachatas4/android/runtime/session/ManagedSessionState;

    invoke-virtual {v2, v10}, Lcom/bachatas4/android/runtime/session/ManagedSession;->update(Lcom/bachatas4/android/runtime/session/ManagedSessionState;)V

    .line 180
    invoke-direct/range {p0 .. p0}, Lcom/bachatas4/android/service/EmulationService;->installRuntime()Ljava/nio/file/Path;

    move-result-object v2
    :try_end_1a
    .catch Ljava/util/concurrent/CancellationException; {:try_start_1a .. :try_end_1a} :catch_ee
    .catch Ljava/lang/Exception; {:try_start_1a .. :try_end_1a} :catch_ed
    .catchall {:try_start_1a .. :try_end_1a} :catchall_44

    .line 182
    :try_start_1b
    invoke-interface {v2}, Ljava/nio/file/Path;->getFileName()Ljava/nio/file/Path;

    move-result-object v10

    new-instance v11, Ljava/lang/StringBuilder;

    move-object/from16 v12, v19

    invoke-direct {v11, v12}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v11, v10}, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;

    move-result-object v10

    invoke-virtual {v10}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v10

    move-object/from16 v11, v41

    invoke-virtual {v5, v11, v10}, Lcom/bachatas4/android/runtime/diagnostics/SessionLog;->info(Ljava/lang/String;Ljava/lang/String;)V
    :try_end_1b
    .catch Ljava/util/concurrent/CancellationException; {:try_start_1b .. :try_end_1b} :catch_eb
    .catch Ljava/lang/Exception; {:try_start_1b .. :try_end_1b} :catch_ea
    .catchall {:try_start_1b .. :try_end_1b} :catchall_43

    move-object/from16 v10, p0

    .line 183
    :try_start_1c
    invoke-direct {v10, v2, v5}, Lcom/bachatas4/android/service/EmulationService;->verifyDeepGuestRuntime(Ljava/nio/file/Path;Lcom/bachatas4/android/runtime/diagnostics/SessionLog;)V

    .line 184
    sget-object v12, Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpoint;->RUNTIME_VERIFIED:Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpoint;

    invoke-virtual {v6, v12}, Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpointStore;->mark(Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpoint;)V

    .line 185
    const-string v12, ".local/share"

    invoke-interface {v2, v12}, Ljava/nio/file/Path;->resolve(Ljava/lang/String;)Ljava/nio/file/Path;

    move-result-object v12

    invoke-interface {v12}, Ljava/nio/file/Path;->toFile()Ljava/io/File;

    move-result-object v12

    invoke-virtual {v12}, Ljava/io/File;->mkdirs()Z

    .line 186
    const-string v12, ".config"

    invoke-interface {v2, v12}, Ljava/nio/file/Path;->resolve(Ljava/lang/String;)Ljava/nio/file/Path;

    move-result-object v12

    invoke-interface {v12}, Ljava/nio/file/Path;->toFile()Ljava/io/File;

    move-result-object v12

    invoke-virtual {v12}, Ljava/io/File;->mkdirs()Z

    .line 187
    sget-object v12, Lcom/bachatas4/android/runtime/session/ManagedSession;->INSTANCE:Lcom/bachatas4/android/runtime/session/ManagedSession;

    new-instance v13, Lcom/bachatas4/android/runtime/session/ManagedSessionState$Preparing;
    :try_end_1c
    .catch Ljava/util/concurrent/CancellationException; {:try_start_1c .. :try_end_1c} :catch_e9
    .catch Ljava/lang/Exception; {:try_start_1c .. :try_end_1c} :catch_e8
    .catchall {:try_start_1c .. :try_end_1c} :catchall_42

    :try_start_1d
    const-string v10, "display"

    invoke-direct {v13, v10}, Lcom/bachatas4/android/runtime/session/ManagedSessionState$Preparing;-><init>(Ljava/lang/String;)V

    check-cast v13, Lcom/bachatas4/android/runtime/session/ManagedSessionState;

    invoke-virtual {v12, v13}, Lcom/bachatas4/android/runtime/session/ManagedSession;->update(Lcom/bachatas4/android/runtime/session/ManagedSessionState;)V

    .line 188
    new-instance v10, Lcom/bachatas4/android/service/EmulationService$runSession$target$1;
    :try_end_1d
    .catch Ljava/util/concurrent/CancellationException; {:try_start_1d .. :try_end_1d} :catch_eb
    .catch Ljava/lang/Exception; {:try_start_1d .. :try_end_1d} :catch_ea
    .catchall {:try_start_1d .. :try_end_1d} :catchall_43

    const/4 v12, 0x0

    :try_start_1e
    invoke-direct {v10, v12}, Lcom/bachatas4/android/service/EmulationService$runSession$target$1;-><init>(Lkotlin/coroutines/Continuation;)V
    :try_end_1e
    .catch Ljava/util/concurrent/CancellationException; {:try_start_1e .. :try_end_1e} :catch_e7
    .catch Ljava/lang/Exception; {:try_start_1e .. :try_end_1e} :catch_e6
    .catchall {:try_start_1e .. :try_end_1e} :catchall_41

    :try_start_1f
    check-cast v10, Lkotlin/jvm/functions/Function2;

    iput-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$0:Ljava/lang/Object;

    invoke-static/range {p2 .. p2}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v12

    iput-object v12, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$1:Ljava/lang/Object;

    invoke-static/range {v54 .. v54}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v12

    iput-object v12, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$2:Ljava/lang/Object;

    iput-object v7, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$3:Ljava/lang/Object;

    iput-object v8, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$4:Ljava/lang/Object;

    iput-object v9, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$5:Ljava/lang/Object;

    iput-object v15, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$6:Ljava/lang/Object;

    iput-object v2, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$7:Ljava/lang/Object;
    :try_end_1f
    .catch Ljava/util/concurrent/CancellationException; {:try_start_1f .. :try_end_1f} :catch_eb
    .catch Ljava/lang/Exception; {:try_start_1f .. :try_end_1f} :catch_ea
    .catchall {:try_start_1f .. :try_end_1f} :catchall_43

    move-object/from16 v12, v50

    :try_start_20
    iput-object v12, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$8:Ljava/lang/Object;
    :try_end_20
    .catch Ljava/util/concurrent/CancellationException; {:try_start_20 .. :try_end_20} :catch_e5
    .catch Ljava/lang/Exception; {:try_start_20 .. :try_end_20} :catch_e4
    .catchall {:try_start_20 .. :try_end_20} :catchall_40

    move-object/from16 v13, v49

    :try_start_21
    iput-object v13, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$9:Ljava/lang/Object;
    :try_end_21
    .catch Ljava/util/concurrent/CancellationException; {:try_start_21 .. :try_end_21} :catch_e2
    .catch Ljava/lang/Exception; {:try_start_21 .. :try_end_21} :catch_e1
    .catchall {:try_start_21 .. :try_end_21} :catchall_3f

    move-object/from16 v19, v1

    :try_start_22
    invoke-static/range {v44 .. v44}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v1

    iput-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$10:Ljava/lang/Object;

    iput-object v5, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$11:Ljava/lang/Object;

    iput-object v6, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$12:Ljava/lang/Object;
    :try_end_22
    .catch Ljava/util/concurrent/CancellationException; {:try_start_22 .. :try_end_22} :catch_e3
    .catch Ljava/lang/Exception; {:try_start_22 .. :try_end_22} :catch_e0
    .catchall {:try_start_22 .. :try_end_22} :catchall_3f

    move-object/from16 v1, v47

    :try_start_23
    iput-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$13:Ljava/lang/Object;
    :try_end_23
    .catch Ljava/util/concurrent/CancellationException; {:try_start_23 .. :try_end_23} :catch_df
    .catch Ljava/lang/Exception; {:try_start_23 .. :try_end_23} :catch_de
    .catchall {:try_start_23 .. :try_end_23} :catchall_3f

    move-object/from16 v47, v1

    move-object/from16 v1, v48

    :try_start_24
    iput-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$14:Ljava/lang/Object;
    :try_end_24
    .catch Ljava/util/concurrent/CancellationException; {:try_start_24 .. :try_end_24} :catch_e3
    .catch Ljava/lang/Exception; {:try_start_24 .. :try_end_24} :catch_dd
    .catchall {:try_start_24 .. :try_end_24} :catchall_3f

    move-object/from16 v48, v1

    move-object/from16 v1, v46

    :try_start_25
    iput-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$15:Ljava/lang/Object;
    :try_end_25
    .catch Ljava/util/concurrent/CancellationException; {:try_start_25 .. :try_end_25} :catch_e3
    .catch Ljava/lang/Exception; {:try_start_25 .. :try_end_25} :catch_e0
    .catchall {:try_start_25 .. :try_end_25} :catchall_3f

    move-object/from16 v46, v1

    move-object/from16 v1, v45

    :try_start_26
    iput-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$16:Ljava/lang/Object;
    :try_end_26
    .catch Ljava/util/concurrent/CancellationException; {:try_start_26 .. :try_end_26} :catch_dc
    .catch Ljava/lang/Exception; {:try_start_26 .. :try_end_26} :catch_db
    .catchall {:try_start_26 .. :try_end_26} :catchall_3f

    move-object/from16 v20, v1

    move-object/from16 v1, v59

    :try_start_27
    iput-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$17:Ljava/lang/Object;
    :try_end_27
    .catch Ljava/util/concurrent/CancellationException; {:try_start_27 .. :try_end_27} :catch_da
    .catch Ljava/lang/Exception; {:try_start_27 .. :try_end_27} :catch_d9
    .catchall {:try_start_27 .. :try_end_27} :catchall_3f

    move-object/from16 v41, v1

    move-object/from16 v1, v60

    :try_start_28
    iput-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$18:Ljava/lang/Object;
    :try_end_28
    .catch Ljava/util/concurrent/CancellationException; {:try_start_28 .. :try_end_28} :catch_d8
    .catch Ljava/lang/Exception; {:try_start_28 .. :try_end_28} :catch_d7
    .catchall {:try_start_28 .. :try_end_28} :catchall_3f

    move-object/from16 v42, v1

    move-object/from16 v1, v61

    :try_start_29
    iput-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$19:Ljava/lang/Object;

    iput-object v4, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$20:Ljava/lang/Object;
    :try_end_29
    .catch Ljava/util/concurrent/CancellationException; {:try_start_29 .. :try_end_29} :catch_d6
    .catch Ljava/lang/Exception; {:try_start_29 .. :try_end_29} :catch_d5
    .catchall {:try_start_29 .. :try_end_29} :catchall_3f

    move-object/from16 v45, v1

    move-object/from16 v1, v62

    :try_start_2a
    iput-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$21:Ljava/lang/Object;
    :try_end_2a
    .catch Ljava/util/concurrent/CancellationException; {:try_start_2a .. :try_end_2a} :catch_d4
    .catch Ljava/lang/Exception; {:try_start_2a .. :try_end_2a} :catch_d3
    .catchall {:try_start_2a .. :try_end_2a} :catchall_3f

    move-object/from16 v49, v1

    move-object/from16 v1, v64

    :try_start_2b
    iput-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$22:Ljava/lang/Object;
    :try_end_2b
    .catch Ljava/util/concurrent/CancellationException; {:try_start_2b .. :try_end_2b} :catch_d2
    .catch Ljava/lang/Exception; {:try_start_2b .. :try_end_2b} :catch_d1
    .catchall {:try_start_2b .. :try_end_2b} :catchall_3f

    move-object/from16 v50, v1

    :try_start_2c
    invoke-static/range {v56 .. v56}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v1

    iput-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$23:Ljava/lang/Object;

    move-object/from16 v1, v65

    iput-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$24:Ljava/lang/Object;

    move-object/from16 v51, v1

    move-object/from16 v1, v63

    iput-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$25:Ljava/lang/Object;

    iput-object v3, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$26:Ljava/lang/Object;

    iput-object v2, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$27:Ljava/lang/Object;
    :try_end_2c
    .catch Ljava/util/concurrent/CancellationException; {:try_start_2c .. :try_end_2c} :catch_d0
    .catch Ljava/lang/Exception; {:try_start_2c .. :try_end_2c} :catch_cf
    .catchall {:try_start_2c .. :try_end_2c} :catchall_3f

    move-object/from16 v52, v1

    move/from16 v1, v66

    :try_start_2d
    iput v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->I$0:I
    :try_end_2d
    .catch Ljava/util/concurrent/CancellationException; {:try_start_2d .. :try_end_2d} :catch_cd
    .catch Ljava/lang/Exception; {:try_start_2d .. :try_end_2d} :catch_cc
    .catchall {:try_start_2d .. :try_end_2d} :catchall_3f

    move/from16 v55, v1

    const/4 v1, 0x2

    :try_start_2e
    iput v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->label:I
    :try_end_2e
    .catch Ljava/util/concurrent/CancellationException; {:try_start_2e .. :try_end_2e} :catch_ce
    .catch Ljava/lang/Exception; {:try_start_2e .. :try_end_2e} :catch_cb
    .catchall {:try_start_2e .. :try_end_2e} :catchall_3f

    move-object/from16 p1, v2

    const-wide/16 v1, 0x7530

    :try_start_2f
    invoke-static {v1, v2, v10, v14}, Lkotlinx/coroutines/TimeoutKt;->withTimeout(JLkotlin/jvm/functions/Function2;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;

    move-result-object v1
    :try_end_2f
    .catch Ljava/util/concurrent/CancellationException; {:try_start_2f .. :try_end_2f} :catch_ec
    .catch Ljava/lang/Exception; {:try_start_2f .. :try_end_2f} :catch_ca
    .catchall {:try_start_2f .. :try_end_2f} :catchall_3e

    move-object/from16 v2, v43

    if-ne v1, v2, :cond_8

    move-object v3, v2

    goto/16 :goto_b

    :cond_8
    move-object/from16 v83, p1

    move-object/from16 v84, v3

    move-object/from16 v79, v4

    move-object/from16 v43, v11

    move-object/from16 v76, v41

    move-object/from16 v77, v42

    move-object/from16 v78, v45

    move-object/from16 v11, v46

    move-object/from16 v10, v47

    move-object/from16 v3, v48

    move-object/from16 v80, v49

    move-object/from16 v82, v50

    move-object/from16 v86, v51

    move-object/from16 v85, v52

    move/from16 v81, v55

    move-object/from16 v4, v83

    move-object/from16 v55, p2

    move-object/from16 p1, v1

    move-object/from16 v46, v2

    move-object/from16 v1, v19

    goto/16 :goto_3

    .line 119
    :goto_8
    :try_start_30
    move-object/from16 v19, p1

    check-cast v19, Lcom/bachatas4/android/runtime/session/RuntimeSurface;
    :try_end_30
    .catch Ljava/util/concurrent/CancellationException; {:try_start_30 .. :try_end_30} :catch_c7
    .catch Ljava/lang/Exception; {:try_start_30 .. :try_end_30} :catch_c6
    .catchall {:try_start_30 .. :try_end_30} :catchall_3d

    move-object/from16 v20, v2

    .line 189
    :try_start_31
    invoke-virtual/range {v19 .. v19}, Lcom/bachatas4/android/runtime/session/RuntimeSurface;->getWidth()I

    move-result v2

    move-object/from16 v41, v11

    invoke-virtual/range {v19 .. v19}, Lcom/bachatas4/android/runtime/session/RuntimeSurface;->getHeight()I

    move-result v11
    :try_end_31
    .catch Ljava/util/concurrent/CancellationException; {:try_start_31 .. :try_end_31} :catch_c5
    .catch Ljava/lang/Exception; {:try_start_31 .. :try_end_31} :catch_c4
    .catchall {:try_start_31 .. :try_end_31} :catchall_3d

    move-object/from16 v42, v3

    :try_start_32
    new-instance v3, Ljava/lang/StringBuilder;
    :try_end_32
    .catch Ljava/util/concurrent/CancellationException; {:try_start_32 .. :try_end_32} :catch_c5
    .catch Ljava/lang/Exception; {:try_start_32 .. :try_end_32} :catch_c3
    .catchall {:try_start_32 .. :try_end_32} :catchall_3d

    move-object/from16 v45, v10

    move-object/from16 v10, v18

    :try_start_33
    invoke-direct {v3, v10}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v3, v2}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    move-result-object v2

    const-string v3, "x"

    invoke-virtual {v2, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v2

    invoke-virtual {v2, v11}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    move-result-object v2

    invoke-virtual {v2}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v2

    move-object/from16 v3, v17

    invoke-virtual {v5, v3, v2}, Lcom/bachatas4/android/runtime/diagnostics/SessionLog;->info(Ljava/lang/String;Ljava/lang/String;)V

    .line 190
    new-instance v2, Ljava/io/File;

    invoke-virtual/range {p0 .. p0}, Lcom/bachatas4/android/service/EmulationService;->getFilesDir()Ljava/io/File;

    move-result-object v10

    const-string v11, "x"

    invoke-direct {v2, v10, v11}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    invoke-virtual {v2}, Ljava/io/File;->mkdirs()Z

    .line 194
    new-instance v57, Lcom/bachatas4/android/runtime/display/WinlatorEmbeddedXServer;

    .line 195
    move-object/from16 v58, p0

    check-cast v58, Landroid/content/Context;

    .line 198
    const-string v61, "/tmp/.X11-unix/X0"

    const/16 v64, 0x20

    const/16 v65, 0x0

    const/16 v60, 0x1

    const/16 v62, 0x0

    const/16 v63, 0x0

    move-object/from16 v59, v2

    .line 194
    invoke-direct/range {v57 .. v65}, Lcom/bachatas4/android/runtime/display/WinlatorEmbeddedXServer;-><init>(Landroid/content/Context;Ljava/io/File;ZLjava/lang/String;ZLkotlinx/coroutines/CoroutineScope;ILkotlin/jvm/internal/DefaultConstructorMarker;)V

    move-object/from16 v10, v57

    iput-object v10, v7, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    .line 201
    iget-object v10, v7, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v10, Lcom/bachatas4/android/runtime/display/WinlatorEmbeddedXServer;

    invoke-virtual/range {v19 .. v19}, Lcom/bachatas4/android/runtime/session/RuntimeSurface;->getSurface()Landroid/view/Surface;

    move-result-object v11

    move-object/from16 v17, v3

    invoke-virtual/range {v19 .. v19}, Lcom/bachatas4/android/runtime/session/RuntimeSurface;->getWidth()I

    move-result v3

    move/from16 p1, v3

    invoke-virtual/range {v19 .. v19}, Lcom/bachatas4/android/runtime/session/RuntimeSurface;->getHeight()I

    move-result v3

    iput-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$0:Ljava/lang/Object;
    :try_end_33
    .catch Ljava/util/concurrent/CancellationException; {:try_start_33 .. :try_end_33} :catch_c2
    .catch Ljava/lang/Exception; {:try_start_33 .. :try_end_33} :catch_c1
    .catchall {:try_start_33 .. :try_end_33} :catchall_3d

    move-object/from16 v18, v1

    :try_start_34
    invoke-static/range {v55 .. v55}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v1

    iput-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$1:Ljava/lang/Object;

    invoke-static/range {v54 .. v54}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v1

    iput-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$2:Ljava/lang/Object;

    iput-object v7, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$3:Ljava/lang/Object;

    iput-object v8, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$4:Ljava/lang/Object;

    iput-object v9, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$5:Ljava/lang/Object;

    iput-object v15, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$6:Ljava/lang/Object;

    iput-object v4, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$7:Ljava/lang/Object;

    iput-object v12, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$8:Ljava/lang/Object;

    iput-object v13, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$9:Ljava/lang/Object;

    invoke-static/range {v44 .. v44}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v1

    iput-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$10:Ljava/lang/Object;

    iput-object v5, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$11:Ljava/lang/Object;

    iput-object v6, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$12:Ljava/lang/Object;
    :try_end_34
    .catch Ljava/util/concurrent/CancellationException; {:try_start_34 .. :try_end_34} :catch_c8
    .catch Ljava/lang/Exception; {:try_start_34 .. :try_end_34} :catch_c0
    .catchall {:try_start_34 .. :try_end_34} :catchall_3d

    move-object/from16 v1, v45

    :try_start_35
    iput-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$13:Ljava/lang/Object;
    :try_end_35
    .catch Ljava/util/concurrent/CancellationException; {:try_start_35 .. :try_end_35} :catch_bf
    .catch Ljava/lang/Exception; {:try_start_35 .. :try_end_35} :catch_be
    .catchall {:try_start_35 .. :try_end_35} :catchall_3d

    move-object/from16 v45, v1

    move-object/from16 v1, v42

    :try_start_36
    iput-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$14:Ljava/lang/Object;
    :try_end_36
    .catch Ljava/util/concurrent/CancellationException; {:try_start_36 .. :try_end_36} :catch_c8
    .catch Ljava/lang/Exception; {:try_start_36 .. :try_end_36} :catch_bd
    .catchall {:try_start_36 .. :try_end_36} :catchall_3d

    move-object/from16 v42, v1

    move-object/from16 v1, v41

    :try_start_37
    iput-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$15:Ljava/lang/Object;
    :try_end_37
    .catch Ljava/util/concurrent/CancellationException; {:try_start_37 .. :try_end_37} :catch_c8
    .catch Ljava/lang/Exception; {:try_start_37 .. :try_end_37} :catch_c0
    .catchall {:try_start_37 .. :try_end_37} :catchall_3d

    move-object/from16 v41, v1

    move-object/from16 v1, v20

    :try_start_38
    iput-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$16:Ljava/lang/Object;
    :try_end_38
    .catch Ljava/util/concurrent/CancellationException; {:try_start_38 .. :try_end_38} :catch_bc
    .catch Ljava/lang/Exception; {:try_start_38 .. :try_end_38} :catch_bb
    .catchall {:try_start_38 .. :try_end_38} :catchall_3d

    move-object/from16 v20, v1

    move-object/from16 v1, v76

    :try_start_39
    iput-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$17:Ljava/lang/Object;
    :try_end_39
    .catch Ljava/util/concurrent/CancellationException; {:try_start_39 .. :try_end_39} :catch_ba
    .catch Ljava/lang/Exception; {:try_start_39 .. :try_end_39} :catch_b9
    .catchall {:try_start_39 .. :try_end_39} :catchall_3d

    move-object/from16 v47, v1

    move-object/from16 v1, v77

    :try_start_3a
    iput-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$18:Ljava/lang/Object;
    :try_end_3a
    .catch Ljava/util/concurrent/CancellationException; {:try_start_3a .. :try_end_3a} :catch_b8
    .catch Ljava/lang/Exception; {:try_start_3a .. :try_end_3a} :catch_b7
    .catchall {:try_start_3a .. :try_end_3a} :catchall_3d

    move-object/from16 v48, v1

    move-object/from16 v1, v78

    :try_start_3b
    iput-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$19:Ljava/lang/Object;
    :try_end_3b
    .catch Ljava/util/concurrent/CancellationException; {:try_start_3b .. :try_end_3b} :catch_b6
    .catch Ljava/lang/Exception; {:try_start_3b .. :try_end_3b} :catch_b5
    .catchall {:try_start_3b .. :try_end_3b} :catchall_3d

    move-object/from16 v49, v1

    move-object/from16 v1, v79

    :try_start_3c
    iput-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$20:Ljava/lang/Object;
    :try_end_3c
    .catch Ljava/util/concurrent/CancellationException; {:try_start_3c .. :try_end_3c} :catch_b4
    .catch Ljava/lang/Exception; {:try_start_3c .. :try_end_3c} :catch_b3
    .catchall {:try_start_3c .. :try_end_3c} :catchall_3d

    move-object/from16 v50, v1

    move-object/from16 v1, v80

    :try_start_3d
    iput-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$21:Ljava/lang/Object;
    :try_end_3d
    .catch Ljava/util/concurrent/CancellationException; {:try_start_3d .. :try_end_3d} :catch_b2
    .catch Ljava/lang/Exception; {:try_start_3d .. :try_end_3d} :catch_b1
    .catchall {:try_start_3d .. :try_end_3d} :catchall_3d

    move-object/from16 v51, v1

    move-object/from16 v1, v82

    :try_start_3e
    iput-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$22:Ljava/lang/Object;
    :try_end_3e
    .catch Ljava/util/concurrent/CancellationException; {:try_start_3e .. :try_end_3e} :catch_b0
    .catch Ljava/lang/Exception; {:try_start_3e .. :try_end_3e} :catch_af
    .catchall {:try_start_3e .. :try_end_3e} :catchall_3d

    move-object/from16 v52, v1

    :try_start_3f
    invoke-static/range {v56 .. v56}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v1

    iput-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$23:Ljava/lang/Object;

    move-object/from16 v1, v86

    iput-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$24:Ljava/lang/Object;

    move-object/from16 v57, v1

    move-object/from16 v1, v85

    iput-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$25:Ljava/lang/Object;

    move-object/from16 v58, v1

    move-object/from16 v1, v84

    iput-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$26:Ljava/lang/Object;

    move-object/from16 v59, v1

    move-object/from16 v1, v83

    iput-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$27:Ljava/lang/Object;

    move-object/from16 v60, v1

    invoke-static/range {v19 .. v19}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v1

    iput-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$28:Ljava/lang/Object;

    iput-object v2, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$29:Ljava/lang/Object;
    :try_end_3f
    .catch Ljava/util/concurrent/CancellationException; {:try_start_3f .. :try_end_3f} :catch_ae
    .catch Ljava/lang/Exception; {:try_start_3f .. :try_end_3f} :catch_ad
    .catchall {:try_start_3f .. :try_end_3f} :catchall_3d

    move/from16 v1, v81

    :try_start_40
    iput v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->I$0:I
    :try_end_40
    .catch Ljava/util/concurrent/CancellationException; {:try_start_40 .. :try_end_40} :catch_ac
    .catch Ljava/lang/Exception; {:try_start_40 .. :try_end_40} :catch_ab
    .catchall {:try_start_40 .. :try_end_40} :catchall_3d

    move/from16 v61, v1

    const/4 v1, 0x3

    :try_start_41
    iput v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->label:I

    move/from16 v1, p1

    invoke-virtual {v10, v11, v1, v3, v14}, Lcom/bachatas4/android/runtime/display/WinlatorEmbeddedXServer;->start(Landroid/view/Surface;IILkotlin/coroutines/Continuation;)Ljava/lang/Object;

    move-result-object v1
    :try_end_41
    .catch Ljava/util/concurrent/CancellationException; {:try_start_41 .. :try_end_41} :catch_c9
    .catch Ljava/lang/Exception; {:try_start_41 .. :try_end_41} :catch_aa
    .catchall {:try_start_41 .. :try_end_41} :catchall_3d

    move-object/from16 v3, v46

    if-ne v1, v3, :cond_9

    goto/16 :goto_b

    :cond_9
    move-object/from16 v91, v2

    move-object/from16 v46, v3

    move-object v11, v4

    move-object v10, v15

    move-object/from16 v1, v18

    move-object/from16 v4, v41

    move-object/from16 v3, v42

    move-object/from16 v15, v45

    move-object/from16 v87, v47

    move-object/from16 v42, v48

    move-object/from16 v41, v49

    move-object/from16 v88, v50

    move-object/from16 v89, v51

    move-object/from16 v92, v52

    move-object/from16 v95, v57

    move-object/from16 v94, v58

    move-object/from16 p1, v59

    move-object/from16 v93, v60

    move/from16 v90, v61

    move-object/from16 v45, v19

    goto/16 :goto_2

    .line 202
    :goto_9
    :try_start_42
    iget-object v2, v7, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v2, Lcom/bachatas4/android/runtime/display/WinlatorEmbeddedXServer;

    invoke-virtual {v2}, Lcom/bachatas4/android/runtime/display/WinlatorEmbeddedXServer;->getDisplay()Ljava/lang/String;

    move-result-object v2

    move-object/from16 v48, v4

    new-instance v4, Ljava/lang/StringBuilder;

    invoke-direct {v4, v0}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v4, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    move-object/from16 v2, v17

    invoke-virtual {v5, v2, v0}, Lcom/bachatas4/android/runtime/diagnostics/SessionLog;->info(Ljava/lang/String;Ljava/lang/String;)V

    .line 203
    sget-object v0, Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpoint;->DISPLAY_READY:Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpoint;

    invoke-virtual {v6, v0}, Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpointStore;->mark(Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpoint;)V

    .line 205
    new-instance v0, Landroid/net/LocalSocket;

    invoke-direct {v0}, Landroid/net/LocalSocket;-><init>()V

    .line 206
    new-instance v2, Landroid/net/LocalSocketAddress;

    invoke-virtual {v13}, Ljava/io/File;->getPath()Ljava/lang/String;

    move-result-object v4
    :try_end_42
    .catch Ljava/util/concurrent/CancellationException; {:try_start_42 .. :try_end_42} :catch_a9
    .catch Ljava/lang/Exception; {:try_start_42 .. :try_end_42} :catch_a8
    .catchall {:try_start_42 .. :try_end_42} :catchall_3c

    move-object/from16 v49, v3

    :try_start_43
    sget-object v3, Landroid/net/LocalSocketAddress$Namespace;->FILESYSTEM:Landroid/net/LocalSocketAddress$Namespace;

    invoke-direct {v2, v4, v3}, Landroid/net/LocalSocketAddress;-><init>(Ljava/lang/String;Landroid/net/LocalSocketAddress$Namespace;)V

    invoke-virtual {v0, v2}, Landroid/net/LocalSocket;->bind(Landroid/net/LocalSocketAddress;)V

    .line 207
    sget-object v2, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;

    .line 205
    iput-object v0, v8, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    .line 208
    new-instance v0, Landroid/net/LocalServerSocket;

    iget-object v2, v8, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v2, Landroid/net/LocalSocket;

    invoke-virtual {v2}, Landroid/net/LocalSocket;->getFileDescriptor()Ljava/io/FileDescriptor;

    move-result-object v2

    invoke-direct {v0, v2}, Landroid/net/LocalServerSocket;-><init>(Ljava/io/FileDescriptor;)V

    iput-object v0, v9, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    .line 209
    invoke-virtual/range {p0 .. p0}, Lcom/bachatas4/android/service/EmulationService;->getApplicationInfo()Landroid/content/pm/ApplicationInfo;

    move-result-object v0

    iget-object v0, v0, Landroid/content/pm/ApplicationInfo;->nativeLibraryDir:Ljava/lang/String;
    :try_end_43
    .catch Ljava/util/concurrent/CancellationException; {:try_start_43 .. :try_end_43} :catch_a9
    .catch Ljava/lang/Exception; {:try_start_43 .. :try_end_43} :catch_a7
    .catchall {:try_start_43 .. :try_end_43} :catchall_3c

    const/4 v2, 0x0

    :try_start_44
    new-array v3, v2, [Ljava/lang/String;
    :try_end_44
    .catch Ljava/util/concurrent/CancellationException; {:try_start_44 .. :try_end_44} :catch_a6
    .catch Ljava/lang/Exception; {:try_start_44 .. :try_end_44} :catch_a5
    .catchall {:try_start_44 .. :try_end_44} :catchall_3b

    :try_start_45
    invoke-static {v0, v3}, Ljava/nio/file/Paths;->get(Ljava/lang/String;[Ljava/lang/String;)Ljava/nio/file/Path;

    move-result-object v0

    .line 211
    sget-object v2, Lcom/bachatas4/android/runtime/process/RuntimeVulkanDriverIds;->INSTANCE:Lcom/bachatas4/android/runtime/process/RuntimeVulkanDriverIds;

    invoke-virtual/range {p1 .. p1}, Lcom/bachatas4/android/runtime/settings/ResolvedRuntimeProfile;->getDriverId()Ljava/lang/String;

    move-result-object v3

    invoke-virtual {v2, v3}, Lcom/bachatas4/android/runtime/process/RuntimeVulkanDriverIds;->isVortek(Ljava/lang/String;)Z

    move-result v2
    :try_end_45
    .catch Ljava/util/concurrent/CancellationException; {:try_start_45 .. :try_end_45} :catch_a9
    .catch Ljava/lang/Exception; {:try_start_45 .. :try_end_45} :catch_a7
    .catchall {:try_start_45 .. :try_end_45} :catchall_3c

    if-eqz v2, :cond_f

    .line 214
    :try_start_46
    sget-object v3, Lcom/bachatas4/android/runtime/vortek/VortekSessionSupport;->Companion:Lcom/bachatas4/android/runtime/vortek/VortekSessionSupport$Companion;

    invoke-virtual {v3}, Lcom/bachatas4/android/runtime/vortek/VortekSessionSupport$Companion;->newSessionId()Ljava/lang/String;

    move-result-object v59

    .line 215
    new-instance v57, Lcom/bachatas4/android/runtime/vortek/VortekSessionSupport;

    .line 216
    invoke-virtual/range {p0 .. p0}, Lcom/bachatas4/android/service/EmulationService;->getFilesDir()Ljava/io/File;

    move-result-object v3

    const-string v4, "getFilesDir(...)"

    invoke-static {v3, v4}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullExpressionValue(Ljava/lang/Object;Ljava/lang/String;)V

    .line 218
    new-instance v4, Lcom/bachatas4/android/service/EmulationService$$ExternalSyntheticLambda1;

    invoke-direct {v4, v5}, Lcom/bachatas4/android/service/EmulationService$$ExternalSyntheticLambda1;-><init>(Lcom/bachatas4/android/runtime/diagnostics/SessionLog;)V

    const/16 v62, 0x4

    const/16 v63, 0x0

    const/16 v60, 0x0

    move-object/from16 v58, v3

    move-object/from16 v61, v4

    .line 215
    invoke-direct/range {v57 .. v63}, Lcom/bachatas4/android/runtime/vortek/VortekSessionSupport;-><init>(Ljava/io/File;Ljava/lang/String;Lcom/bachatas4/android/runtime/vortek/VortekServerController;Lkotlin/jvm/functions/Function2;ILkotlin/jvm/internal/DefaultConstructorMarker;)V
    :try_end_46
    .catch Ljava/util/concurrent/CancellationException; {:try_start_46 .. :try_end_46} :catch_4c
    .catch Ljava/lang/Exception; {:try_start_46 .. :try_end_46} :catch_4b
    .catchall {:try_start_46 .. :try_end_46} :catchall_c

    move-object/from16 v3, v57

    .line 224
    :try_start_47
    iput-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$0:Ljava/lang/Object;

    invoke-static/range {v55 .. v55}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v4

    iput-object v4, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$1:Ljava/lang/Object;

    invoke-static/range {v54 .. v54}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v4

    iput-object v4, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$2:Ljava/lang/Object;

    iput-object v7, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$3:Ljava/lang/Object;

    iput-object v8, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$4:Ljava/lang/Object;

    iput-object v9, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$5:Ljava/lang/Object;

    iput-object v10, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$6:Ljava/lang/Object;

    iput-object v11, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$7:Ljava/lang/Object;

    iput-object v12, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$8:Ljava/lang/Object;

    iput-object v13, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$9:Ljava/lang/Object;

    invoke-static/range {v44 .. v44}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v4

    iput-object v4, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$10:Ljava/lang/Object;

    iput-object v5, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$11:Ljava/lang/Object;

    iput-object v6, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$12:Ljava/lang/Object;

    iput-object v15, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$13:Ljava/lang/Object;
    :try_end_47
    .catch Ljava/util/concurrent/CancellationException; {:try_start_47 .. :try_end_47} :catch_49
    .catch Ljava/lang/Exception; {:try_start_47 .. :try_end_47} :catch_48
    .catchall {:try_start_47 .. :try_end_47} :catchall_b

    move-object/from16 v4, v49

    :try_start_48
    iput-object v4, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$14:Ljava/lang/Object;
    :try_end_48
    .catch Ljava/util/concurrent/CancellationException; {:try_start_48 .. :try_end_48} :catch_49
    .catch Ljava/lang/Exception; {:try_start_48 .. :try_end_48} :catch_47
    .catchall {:try_start_48 .. :try_end_48} :catchall_b

    move-object/from16 v49, v1

    move-object/from16 v1, v48

    :try_start_49
    iput-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$15:Ljava/lang/Object;
    :try_end_49
    .catch Ljava/util/concurrent/CancellationException; {:try_start_49 .. :try_end_49} :catch_4a
    .catch Ljava/lang/Exception; {:try_start_49 .. :try_end_49} :catch_46
    .catchall {:try_start_49 .. :try_end_49} :catchall_b

    move-object/from16 v48, v1

    move-object/from16 v1, v47

    :try_start_4a
    iput-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$16:Ljava/lang/Object;
    :try_end_4a
    .catch Ljava/util/concurrent/CancellationException; {:try_start_4a .. :try_end_4a} :catch_45
    .catch Ljava/lang/Exception; {:try_start_4a .. :try_end_4a} :catch_44
    .catchall {:try_start_4a .. :try_end_4a} :catchall_b

    move-object/from16 v47, v1

    move-object/from16 v1, v87

    :try_start_4b
    iput-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$17:Ljava/lang/Object;
    :try_end_4b
    .catch Ljava/util/concurrent/CancellationException; {:try_start_4b .. :try_end_4b} :catch_43
    .catch Ljava/lang/Exception; {:try_start_4b .. :try_end_4b} :catch_42
    .catchall {:try_start_4b .. :try_end_4b} :catchall_b

    move-object/from16 v50, v1

    move-object/from16 v1, v42

    :try_start_4c
    iput-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$18:Ljava/lang/Object;
    :try_end_4c
    .catch Ljava/util/concurrent/CancellationException; {:try_start_4c .. :try_end_4c} :catch_41
    .catch Ljava/lang/Exception; {:try_start_4c .. :try_end_4c} :catch_40
    .catchall {:try_start_4c .. :try_end_4c} :catchall_b

    move-object/from16 v42, v1

    move-object/from16 v1, v41

    :try_start_4d
    iput-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$19:Ljava/lang/Object;
    :try_end_4d
    .catch Ljava/util/concurrent/CancellationException; {:try_start_4d .. :try_end_4d} :catch_3f
    .catch Ljava/lang/Exception; {:try_start_4d .. :try_end_4d} :catch_3e
    .catchall {:try_start_4d .. :try_end_4d} :catchall_b

    move-object/from16 v41, v1

    move-object/from16 v1, v88

    :try_start_4e
    iput-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$20:Ljava/lang/Object;
    :try_end_4e
    .catch Ljava/util/concurrent/CancellationException; {:try_start_4e .. :try_end_4e} :catch_3d
    .catch Ljava/lang/Exception; {:try_start_4e .. :try_end_4e} :catch_3c
    .catchall {:try_start_4e .. :try_end_4e} :catchall_b

    move-object/from16 v51, v1

    move-object/from16 v1, v89

    :try_start_4f
    iput-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$21:Ljava/lang/Object;
    :try_end_4f
    .catch Ljava/util/concurrent/CancellationException; {:try_start_4f .. :try_end_4f} :catch_3b
    .catch Ljava/lang/Exception; {:try_start_4f .. :try_end_4f} :catch_3a
    .catchall {:try_start_4f .. :try_end_4f} :catchall_b

    move-object/from16 v52, v1

    move-object/from16 v1, v92

    :try_start_50
    iput-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$22:Ljava/lang/Object;

    iput-object v3, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$23:Ljava/lang/Object;
    :try_end_50
    .catch Ljava/util/concurrent/CancellationException; {:try_start_50 .. :try_end_50} :catch_39
    .catch Ljava/lang/Exception; {:try_start_50 .. :try_end_50} :catch_38
    .catchall {:try_start_50 .. :try_end_50} :catchall_b

    move-object/from16 v57, v1

    :try_start_51
    invoke-static/range {v56 .. v56}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v1

    iput-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$24:Ljava/lang/Object;

    move-object/from16 v1, v95

    iput-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$25:Ljava/lang/Object;

    move-object/from16 v58, v1

    move-object/from16 v1, v94

    iput-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$26:Ljava/lang/Object;

    move-object/from16 v60, v1

    move-object/from16 v1, p1

    iput-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$27:Ljava/lang/Object;

    move-object/from16 v61, v1

    move-object/from16 v1, v93

    iput-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$28:Ljava/lang/Object;

    move-object/from16 v62, v1

    invoke-static/range {v45 .. v45}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v1

    iput-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$29:Ljava/lang/Object;

    move-object/from16 v1, v91

    iput-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$30:Ljava/lang/Object;

    iput-object v0, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$31:Ljava/lang/Object;

    move-object/from16 v63, v1

    invoke-static/range {v59 .. v59}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v1

    iput-object v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$32:Ljava/lang/Object;

    iput-object v3, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$33:Ljava/lang/Object;
    :try_end_51
    .catch Ljava/util/concurrent/CancellationException; {:try_start_51 .. :try_end_51} :catch_37
    .catch Ljava/lang/Exception; {:try_start_51 .. :try_end_51} :catch_36
    .catchall {:try_start_51 .. :try_end_51} :catchall_b

    move/from16 v1, v90

    :try_start_52
    iput v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->I$0:I

    iput-boolean v2, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->Z$0:Z
    :try_end_52
    .catch Ljava/util/concurrent/CancellationException; {:try_start_52 .. :try_end_52} :catch_35
    .catch Ljava/lang/Exception; {:try_start_52 .. :try_end_52} :catch_34
    .catchall {:try_start_52 .. :try_end_52} :catchall_b

    move/from16 v64, v1

    const/4 v1, 0x4

    :try_start_53
    iput v1, v14, Lcom/bachatas4/android/service/EmulationService$runSession$1;->label:I
    :try_end_53
    .catch Ljava/util/concurrent/CancellationException; {:try_start_53 .. :try_end_53} :catch_33
    .catch Ljava/lang/Exception; {:try_start_53 .. :try_end_53} :catch_32
    .catchall {:try_start_53 .. :try_end_53} :catchall_b

    const/16 v16, 0x0

    const/16 v17, 0x0

    const/16 v19, 0x3

    const/16 v20, 0x0

    move-object/from16 v18, v14

    move-object v1, v15

    move-object v15, v3

    move-object/from16 v3, v46

    :try_start_54
    invoke-static/range {v15 .. v20}, Lcom/bachatas4/android/runtime/vortek/VortekSessionSupport;->startServer$default(Lcom/bachatas4/android/runtime/vortek/VortekSessionSupport;Ljava/lang/String;ILkotlin/coroutines/Continuation;ILjava/lang/Object;)Ljava/lang/Object;

    move-result-object v14
    :try_end_54
    .catch Ljava/util/concurrent/CancellationException; {:try_start_54 .. :try_end_54} :catch_31
    .catch Ljava/lang/Exception; {:try_start_54 .. :try_end_54} :catch_30
    .catchall {:try_start_54 .. :try_end_54} :catchall_a

    move-object/from16 v16, v15

    move-object/from16 v15, v18

    if-ne v14, v3, :cond_a

    goto/16 :goto_b

    :cond_a
    move-object/from16 v105, v0

    move/from16 v101, v2

    move-object/from16 v46, v3

    move-object v0, v14

    move-object/from16 p1, v16

    move-object/from16 v104, p1

    move-object/from16 v98, v41

    move-object/from16 v97, v42

    move-object/from16 v3, v47

    move-object/from16 v14, v48

    move-object/from16 v96, v50

    move-object/from16 v99, v51

    move-object/from16 v100, v52

    move-object/from16 v103, v57

    move-object/from16 v110, v58

    move-object/from16 v109, v60

    move-object/from16 v108, v61

    move-object/from16 v107, v62

    move-object/from16 v106, v63

    move/from16 v102, v64

    move-object v2, v1

    move-object/from16 v1, v49

    move-object/from16 v58, v55

    .line 119
    :goto_a
    :try_start_55
    check-cast v0, Lcom/bachatas4/android/runtime/vortek/VortekStartResult;

    .line 225
    invoke-virtual {v0}, Lcom/bachatas4/android/runtime/vortek/VortekStartResult;->getOk()Z

    move-result v16
    :try_end_55
    .catch Ljava/util/concurrent/CancellationException; {:try_start_55 .. :try_end_55} :catch_2d
    .catch Ljava/lang/Exception; {:try_start_55 .. :try_end_55} :catch_2c
    .catchall {:try_start_55 .. :try_end_55} :catchall_9

    if-eqz v16, :cond_e

    move-object/from16 v16, v3

    .line 229
    :try_start_56
    iget-object v3, v7, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v3, Lcom/bachatas4/android/runtime/display/WinlatorEmbeddedXServer;

    invoke-virtual {v3}, Lcom/bachatas4/android/runtime/display/WinlatorEmbeddedXServer;->getXServer()Lcom/winlator/xserver/XServer;

    move-result-object v3

    if-eqz v3, :cond_d

    move-object/from16 v17, v14

    .line 231
    new-instance v14, Lcom/bachatas4/android/runtime/vortek/VortekWindowBridge;

    invoke-direct {v14, v3}, Lcom/bachatas4/android/runtime/vortek/VortekWindowBridge;-><init>(Lcom/winlator/xserver/XServer;)V

    move-object/from16 p2, v3

    .line 232
    invoke-virtual/range {p1 .. p1}, Lcom/bachatas4/android/runtime/vortek/VortekSessionSupport;->getController()Lcom/bachatas4/android/runtime/vortek/VortekServerController;

    move-result-object v3

    iput-object v1, v15, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$0:Ljava/lang/Object;
    :try_end_56
    .catch Ljava/util/concurrent/CancellationException; {:try_start_56 .. :try_end_56} :catch_28
    .catch Ljava/lang/Exception; {:try_start_56 .. :try_end_56} :catch_27
    .catchall {:try_start_56 .. :try_end_56} :catchall_9

    move-object/from16 v18, v1

    :try_start_57
    invoke-static/range {v58 .. v58}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v1

    iput-object v1, v15, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$1:Ljava/lang/Object;

    invoke-static/range {v54 .. v54}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v1

    iput-object v1, v15, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$2:Ljava/lang/Object;

    iput-object v7, v15, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$3:Ljava/lang/Object;

    iput-object v8, v15, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$4:Ljava/lang/Object;

    iput-object v9, v15, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$5:Ljava/lang/Object;

    iput-object v10, v15, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$6:Ljava/lang/Object;

    iput-object v11, v15, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$7:Ljava/lang/Object;

    iput-object v12, v15, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$8:Ljava/lang/Object;

    iput-object v13, v15, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$9:Ljava/lang/Object;

    invoke-static/range {v44 .. v44}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v1

    iput-object v1, v15, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$10:Ljava/lang/Object;

    iput-object v5, v15, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$11:Ljava/lang/Object;

    iput-object v6, v15, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$12:Ljava/lang/Object;

    iput-object v2, v15, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$13:Ljava/lang/Object;

    iput-object v4, v15, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$14:Ljava/lang/Object;

    move-object/from16 v1, v17

    iput-object v1, v15, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$15:Ljava/lang/Object;
    :try_end_57
    .catch Ljava/util/concurrent/CancellationException; {:try_start_57 .. :try_end_57} :catch_2e
    .catch Ljava/lang/Exception; {:try_start_57 .. :try_end_57} :catch_25
    .catchall {:try_start_57 .. :try_end_57} :catchall_9

    move-object/from16 v17, v1

    move-object/from16 v1, v16

    :try_start_58
    iput-object v1, v15, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$16:Ljava/lang/Object;
    :try_end_58
    .catch Ljava/util/concurrent/CancellationException; {:try_start_58 .. :try_end_58} :catch_24
    .catch Ljava/lang/Exception; {:try_start_58 .. :try_end_58} :catch_23
    .catchall {:try_start_58 .. :try_end_58} :catchall_9

    move-object/from16 v16, v1

    move-object/from16 v1, v96

    :try_start_59
    iput-object v1, v15, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$17:Ljava/lang/Object;
    :try_end_59
    .catch Ljava/util/concurrent/CancellationException; {:try_start_59 .. :try_end_59} :catch_22
    .catch Ljava/lang/Exception; {:try_start_59 .. :try_end_59} :catch_21
    .catchall {:try_start_59 .. :try_end_59} :catchall_9

    move-object/from16 v19, v1

    move-object/from16 v1, v97

    :try_start_5a
    iput-object v1, v15, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$18:Ljava/lang/Object;
    :try_end_5a
    .catch Ljava/util/concurrent/CancellationException; {:try_start_5a .. :try_end_5a} :catch_20
    .catch Ljava/lang/Exception; {:try_start_5a .. :try_end_5a} :catch_1f
    .catchall {:try_start_5a .. :try_end_5a} :catchall_9

    move-object/from16 v20, v1

    move-object/from16 v1, v98

    :try_start_5b
    iput-object v1, v15, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$19:Ljava/lang/Object;
    :try_end_5b
    .catch Ljava/util/concurrent/CancellationException; {:try_start_5b .. :try_end_5b} :catch_1e
    .catch Ljava/lang/Exception; {:try_start_5b .. :try_end_5b} :catch_1d
    .catchall {:try_start_5b .. :try_end_5b} :catchall_9

    move-object/from16 v41, v1

    move-object/from16 v1, v99

    :try_start_5c
    iput-object v1, v15, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$20:Ljava/lang/Object;
    :try_end_5c
    .catch Ljava/util/concurrent/CancellationException; {:try_start_5c .. :try_end_5c} :catch_1c
    .catch Ljava/lang/Exception; {:try_start_5c .. :try_end_5c} :catch_1b
    .catchall {:try_start_5c .. :try_end_5c} :catchall_9

    move-object/from16 v42, v1

    move-object/from16 v1, v100

    :try_start_5d
    iput-object v1, v15, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$21:Ljava/lang/Object;
    :try_end_5d
    .catch Ljava/util/concurrent/CancellationException; {:try_start_5d .. :try_end_5d} :catch_1a
    .catch Ljava/lang/Exception; {:try_start_5d .. :try_end_5d} :catch_19
    .catchall {:try_start_5d .. :try_end_5d} :catchall_9

    move-object/from16 v44, v1

    move-object/from16 v1, v103

    :try_start_5e
    iput-object v1, v15, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$22:Ljava/lang/Object;
    :try_end_5e
    .catch Ljava/util/concurrent/CancellationException; {:try_start_5e .. :try_end_5e} :catch_18
    .catch Ljava/lang/Exception; {:try_start_5e .. :try_end_5e} :catch_17
    .catchall {:try_start_5e .. :try_end_5e} :catchall_9

    move-object/from16 v47, v1

    move-object/from16 v1, v104

    :try_start_5f
    iput-object v1, v15, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$23:Ljava/lang/Object;
    :try_end_5f
    .catch Ljava/util/concurrent/CancellationException; {:try_start_5f .. :try_end_5f} :catch_15
    .catch Ljava/lang/Exception; {:try_start_5f .. :try_end_5f} :catch_14
    .catchall {:try_start_5f .. :try_end_5f} :catchall_7

    move-object/from16 v48, v1

    :try_start_60
    invoke-static/range {v56 .. v56}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v1

    iput-object v1, v15, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$24:Ljava/lang/Object;

    move-object/from16 v1, v110

    iput-object v1, v15, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$25:Ljava/lang/Object;

    move-object/from16 v49, v1

    move-object/from16 v1, v109

    iput-object v1, v15, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$26:Ljava/lang/Object;

    move-object/from16 v50, v1

    move-object/from16 v1, v108

    iput-object v1, v15, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$27:Ljava/lang/Object;

    move-object/from16 v51, v1

    move-object/from16 v1, v107

    iput-object v1, v15, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$28:Ljava/lang/Object;

    move-object/from16 v52, v1

    invoke-static/range {v45 .. v45}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v1

    iput-object v1, v15, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$29:Ljava/lang/Object;

    move-object/from16 v1, v106

    iput-object v1, v15, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$30:Ljava/lang/Object;

    move-object/from16 v45, v1

    move-object/from16 v1, v105

    iput-object v1, v15, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$31:Ljava/lang/Object;

    move-object/from16 v54, v1

    invoke-static/range {v59 .. v59}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v1

    iput-object v1, v15, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$32:Ljava/lang/Object;

    move-object/from16 v1, p1

    iput-object v1, v15, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$33:Ljava/lang/Object;

    invoke-static {v0}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v0

    iput-object v0, v15, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$34:Ljava/lang/Object;

    invoke-static/range {p2 .. p2}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v0

    iput-object v0, v15, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$35:Ljava/lang/Object;

    invoke-static {v14}, Lkotlin/coroutines/jvm/internal/SpillingKt;->nullOutSpilledVariable(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v0

    iput-object v0, v15, Lcom/bachatas4/android/service/EmulationService$runSession$1;->L$36:Ljava/lang/Object;
    :try_end_60
    .catch Ljava/util/concurrent/CancellationException; {:try_start_60 .. :try_end_60} :catch_16
    .catch Ljava/lang/Exception; {:try_start_60 .. :try_end_60} :catch_13
    .catchall {:try_start_60 .. :try_end_60} :catchall_6

    move-object/from16 v55, v1

    move/from16 v1, v102

    :try_start_61
    iput v1, v15, Lcom/bachatas4/android/service/EmulationService$runSession$1;->I$0:I

    move/from16 v0, v101

    iput-boolean v0, v15, Lcom/bachatas4/android/service/EmulationService$runSession$1;->Z$0:Z
    :try_end_61
    .catch Ljava/util/concurrent/CancellationException; {:try_start_61 .. :try_end_61} :catch_12
    .catch Ljava/lang/Exception; {:try_start_61 .. :try_end_61} :catch_11
    .catchall {:try_start_61 .. :try_end_61} :catchall_6

    move/from16 v56, v1

    const/4 v1, 0x5

    :try_start_62
    iput v1, v15, Lcom/bachatas4/android/service/EmulationService$runSession$1;->label:I

    invoke-virtual {v3, v14, v15}, Lcom/bachatas4/android/runtime/vortek/VortekServerController;->setWindowBridge(Ljava/lang/Object;Lkotlin/coroutines/Continuation;)Ljava/lang/Object;

    move-result-object v1
    :try_end_62
    .catch Ljava/util/concurrent/CancellationException; {:try_start_62 .. :try_end_62} :catch_2f
    .catch Ljava/lang/Exception; {:try_start_62 .. :try_end_62} :catch_10
    .catchall {:try_start_62 .. :try_end_62} :catchall_6

    move-object/from16 v3, v46

    if-ne v1, v3, :cond_b

    :goto_b
    return-object v3

    :cond_b
    move-object/from16 v3, v16

    move/from16 v16, v0

    move-object v0, v1

    move-object/from16 v1, v18

    move-object/from16 v18, v3

    move-object/from16 v3, v19

    move-object/from16 v19, v17

    move-object/from16 v17, v3

    move-object/from16 v3, v44

    move-object/from16 v15, v49

    move-object/from16 v49, v8

    move-object/from16 v44, v13

    move-object/from16 v8, v48

    move-object/from16 v13, v50

    move-object/from16 v50, v7

    move-object/from16 v48, v9

    move-object/from16 v9, v45

    move-object/from16 v7, v47

    move-object/from16 v47, v10

    .line 119
    :goto_c
    :try_start_63
    check-cast v0, Lcom/bachatas4/android/runtime/vortek/NativeVortekResult;

    .line 233
    invoke-virtual {v0}, Lcom/bachatas4/android/runtime/vortek/NativeVortekResult;->isOk()Z

    move-result v10

    if-eqz v10, :cond_c

    .line 236
    const-string v0, "window_bridge=attached"
    :try_end_63
    .catch Ljava/util/concurrent/CancellationException; {:try_start_63 .. :try_end_63} :catch_f
    .catch Ljava/lang/Exception; {:try_start_63 .. :try_end_63} :catch_e
    .catchall {:try_start_63 .. :try_end_63} :catchall_5

    move-object/from16 v14, v38

    :try_start_64
    invoke-virtual {v5, v14, v0}, Lcom/bachatas4/android/runtime/diagnostics/SessionLog;->info(Ljava/lang/String;Ljava/lang/String;)V

    .line 240
    invoke-virtual/range {v55 .. v55}, Lcom/bachatas4/android/runtime/vortek/VortekSessionSupport;->socketAsPath()Ljava/nio/file/Path;

    move-result-object v0

    .line 241
    const-string v10, "driver=system-vortek box64Mode=HOST_GLIBC"
    :try_end_64
    .catch Ljava/util/concurrent/CancellationException; {:try_start_64 .. :try_end_64} :catch_b
    .catch Ljava/lang/Exception; {:try_start_64 .. :try_end_64} :catch_a
    .catchall {:try_start_64 .. :try_end_64} :catchall_4

    move-object/from16 p1, v1

    move-object/from16 v1, v36

    :try_start_65
    invoke-virtual {v5, v1, v10}, Lcom/bachatas4/android/runtime/diagnostics/SessionLog;->info(Ljava/lang/String;Ljava/lang/String;)V

    .line 242
    sget-object v10, Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpoint;->VORTEK_READY:Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpoint;

    invoke-virtual {v6, v10}, Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpointStore;->mark(Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpoint;)V

    move-object/from16 v10, v19

    move-object/from16 v19, v4

    move-object v4, v5

    move-object/from16 v5, v48

    move-object/from16 v48, v10

    move-object/from16 v10, v47

    move-object/from16 v47, v18

    move-object/from16 v18, v10

    move-object/from16 v45, v2

    move-object/from16 v111, v8

    move-object/from16 v94, v13

    move-object/from16 v95, v15

    move-object/from16 v2, v17

    move-object/from16 v10, v20

    move-object/from16 v13, v50

    move-object/from16 v15, v52

    move-object/from16 v55, v54

    move/from16 v90, v56

    move-object v8, v0

    move-object/from16 v52, v3

    move-object/from16 v17, v7

    move-object v7, v9

    move-object/from16 v0, v51

    move-object/from16 v9, p1

    move-object v3, v12

    move-object v12, v6

    move-object/from16 p1, v11

    move-object/from16 v11, v41

    goto/16 :goto_3f

    :catch_a
    move-exception v0

    move-object/from16 p1, v1

    goto/16 :goto_f

    :catch_b
    move-object/from16 p1, v1

    goto :goto_d

    :cond_c
    move-object/from16 p1, v1

    move-object/from16 v14, v38

    .line 234
    new-instance v1, Ljava/lang/IllegalStateException;

    invoke-virtual {v0}, Lcom/bachatas4/android/runtime/vortek/NativeVortekResult;->getMessage()Ljava/lang/String;

    move-result-object v0

    new-instance v9, Ljava/lang/StringBuilder;

    move-object/from16 v10, v33

    invoke-direct {v9, v10}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v9, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    invoke-direct {v1, v0}, Ljava/lang/IllegalStateException;-><init>(Ljava/lang/String;)V

    throw v1
    :try_end_65
    .catch Ljava/util/concurrent/CancellationException; {:try_start_65 .. :try_end_65} :catch_d
    .catch Ljava/lang/Exception; {:try_start_65 .. :try_end_65} :catch_c
    .catchall {:try_start_65 .. :try_end_65} :catchall_4

    :catchall_4
    move-exception v0

    goto :goto_e

    :catch_c
    move-exception v0

    goto :goto_f

    :catch_d
    :goto_d
    move-object v4, v5

    move-object v5, v6

    move-object v1, v7

    move-object/from16 v145, v8

    move-object/from16 v144, v11

    move-object/from16 v33, v12

    move-object/from16 v142, v14

    move-object/from16 v13, v17

    move-object/from16 v6, v18

    move-object/from16 v0, v20

    move-object/from16 v141, v28

    move-object/from16 v10, v29

    move-object/from16 v8, v32

    goto/16 :goto_10

    :catchall_5
    move-exception v0

    move-object/from16 v14, v38

    :goto_e
    move-object/from16 v2, p0

    move-object v4, v0

    move-object/from16 v155, v8

    move-object v0, v11

    move-object/from16 v33, v12

    move-object/from16 v153, v14

    move-object/from16 v151, v27

    move-object/from16 v152, v28

    move-object/from16 v7, v30

    move-object/from16 v9, v31

    move-object/from16 v15, v32

    move-object/from16 v13, v47

    move-object/from16 v10, v48

    move-object/from16 v11, v49

    move-object/from16 v12, v50

    move-object/from16 v154, v53

    const/4 v1, 0x4

    const/4 v3, 0x0

    const/4 v8, 0x1

    const/16 v37, 0x0

    move-object v14, v6

    move-object/from16 v6, v29

    goto/16 :goto_146

    :catch_e
    move-exception v0

    move-object/from16 p1, v1

    move-object/from16 v14, v38

    :goto_f
    move-object/from16 v16, v0

    move-object v1, v4

    move-object v4, v6

    move-object/from16 v130, v8

    move-object/from16 v129, v11

    move-object/from16 v33, v12

    move-object/from16 v126, v14

    move-object/from16 v9, v17

    move-object/from16 v8, v18

    move-object/from16 v10, v20

    move-object/from16 v112, v26

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v11, v41

    move-object/from16 v13, v42

    move-object/from16 v15, v47

    move-object/from16 v22, v48

    move-object/from16 v120, v49

    move-object/from16 v20, v50

    move-object/from16 v127, v53

    move/from16 v90, v56

    const/4 v14, 0x0

    const/16 v34, 0x4

    const/16 v37, 0x0

    const/16 v128, 0x0

    move-object/from16 v6, p1

    move-object v12, v3

    move-object v3, v7

    goto/16 :goto_20

    :catch_f
    move-object/from16 p1, v1

    move-object v4, v5

    move-object v5, v6

    move-object v1, v7

    move-object/from16 v145, v8

    move-object/from16 v144, v11

    move-object/from16 v33, v12

    move-object/from16 v13, v17

    move-object/from16 v6, v18

    move-object/from16 v0, v20

    move-object/from16 v141, v28

    move-object/from16 v10, v29

    move-object/from16 v8, v32

    move-object/from16 v142, v38

    :goto_10
    move-object/from16 v9, v41

    move-object/from16 v14, v42

    move-object/from16 v22, v47

    move-object/from16 v21, v48

    move-object/from16 v20, v49

    move-object/from16 v19, v50

    move-object/from16 v15, v53

    move/from16 v90, v56

    const/16 v34, 0x4

    const/16 v37, 0x0

    const/16 v40, 0x0

    const/16 v143, 0x0

    move-object/from16 v11, p0

    move-object/from16 v7, p1

    move-object v12, v3

    move-object v3, v2

    goto/16 :goto_4

    :catch_10
    move-exception v0

    goto :goto_11

    :catch_11
    move-exception v0

    move/from16 v56, v1

    :goto_11
    move-object/from16 v14, v38

    goto/16 :goto_1b

    :catch_12
    move/from16 v56, v1

    goto/16 :goto_28

    :catchall_6
    move-exception v0

    goto :goto_12

    :catch_13
    move-exception v0

    goto :goto_13

    :catchall_7
    move-exception v0

    move-object/from16 v48, v1

    :goto_12
    move-object/from16 v14, v38

    goto/16 :goto_1c

    :catch_14
    move-exception v0

    move-object/from16 v48, v1

    :goto_13
    move-object/from16 v14, v38

    move/from16 v56, v102

    goto/16 :goto_1b

    :catch_15
    move-object/from16 v48, v1

    :catch_16
    move/from16 v56, v102

    goto/16 :goto_28

    :catch_17
    move-exception v0

    move-object/from16 v47, v1

    move-object/from16 v14, v38

    move/from16 v56, v102

    goto/16 :goto_1a

    :catch_18
    move-object/from16 v47, v1

    move/from16 v56, v102

    move-object/from16 v48, v104

    move-object v3, v2

    move-object v4, v5

    move-object v5, v6

    move-object/from16 v21, v9

    move-object/from16 v22, v10

    move-object/from16 v144, v11

    move-object/from16 v33, v12

    move-object/from16 v6, v16

    move-object/from16 v0, v20

    move-object/from16 v141, v28

    move-object/from16 v10, v29

    move-object/from16 v142, v38

    move-object/from16 v9, v41

    move-object/from16 v14, v42

    move-object/from16 v12, v44

    goto/16 :goto_2a

    :catch_19
    move-exception v0

    move-object/from16 v44, v1

    move-object/from16 v14, v38

    goto/16 :goto_19

    :catch_1a
    move-object/from16 v44, v1

    goto/16 :goto_27

    :catch_1b
    move-exception v0

    move-object/from16 v42, v1

    move-object/from16 v14, v38

    goto/16 :goto_18

    :catch_1c
    move-object/from16 v42, v1

    goto/16 :goto_26

    :catch_1d
    move-exception v0

    move-object/from16 v41, v1

    move-object/from16 v14, v38

    goto :goto_17

    :catch_1e
    move-object/from16 v41, v1

    goto/16 :goto_25

    :catch_1f
    move-exception v0

    move-object/from16 v20, v1

    move-object/from16 v14, v38

    goto :goto_16

    :catch_20
    move-object/from16 v20, v1

    goto/16 :goto_24

    :catch_21
    move-exception v0

    move-object/from16 v19, v1

    move-object/from16 v14, v38

    goto :goto_15

    :catch_22
    move-object/from16 v19, v1

    goto/16 :goto_23

    :catch_23
    move-exception v0

    move-object/from16 v16, v1

    goto :goto_14

    :catch_24
    move-object/from16 v16, v1

    goto/16 :goto_22

    :catch_25
    move-exception v0

    goto :goto_14

    :cond_d
    move-object/from16 v18, v1

    move-object/from16 v14, v38

    move-object/from16 v19, v96

    move-object/from16 v20, v97

    move-object/from16 v41, v98

    move-object/from16 v42, v99

    move-object/from16 v44, v100

    move/from16 v56, v102

    move-object/from16 v47, v103

    move-object/from16 v48, v104

    .line 238
    :try_start_66
    new-instance v0, Ljava/lang/IllegalStateException;

    const-string v1, "vortek_surface_unavailable: x_server_missing"

    invoke-direct {v0, v1}, Ljava/lang/IllegalStateException;-><init>(Ljava/lang/String;)V

    throw v0
    :try_end_66
    .catch Ljava/util/concurrent/CancellationException; {:try_start_66 .. :try_end_66} :catch_2b
    .catch Ljava/lang/Exception; {:try_start_66 .. :try_end_66} :catch_26
    .catchall {:try_start_66 .. :try_end_66} :catchall_8

    :catch_26
    move-exception v0

    goto :goto_1b

    :catch_27
    move-exception v0

    move-object/from16 v18, v1

    :goto_14
    move-object/from16 v14, v38

    move-object/from16 v19, v96

    :goto_15
    move-object/from16 v20, v97

    :goto_16
    move-object/from16 v41, v98

    :goto_17
    move-object/from16 v42, v99

    :goto_18
    move-object/from16 v44, v100

    :goto_19
    move/from16 v56, v102

    move-object/from16 v47, v103

    :goto_1a
    move-object/from16 v48, v104

    :goto_1b
    move-object v1, v4

    move-object v4, v6

    move-object/from16 v120, v8

    move-object/from16 v22, v9

    move-object v15, v10

    move-object/from16 v129, v11

    move-object/from16 v33, v12

    move-object/from16 v126, v14

    move-object/from16 v8, v16

    move-object/from16 v6, v18

    move-object/from16 v9, v19

    move-object/from16 v10, v20

    move-object/from16 v112, v26

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v11, v41

    move-object/from16 v12, v44

    move-object/from16 v3, v47

    move-object/from16 v130, v48

    move-object/from16 v127, v53

    move/from16 v90, v56

    const/4 v14, 0x0

    const/16 v34, 0x4

    const/16 v37, 0x0

    const/16 v128, 0x0

    move-object/from16 v16, v0

    move-object/from16 v20, v7

    move-object/from16 v44, v13

    move-object/from16 v13, v42

    goto/16 :goto_20

    :catch_28
    move-object/from16 v18, v1

    goto/16 :goto_22

    :cond_e
    move-object/from16 v18, v1

    move-object/from16 v16, v3

    move-object/from16 v14, v38

    move-object/from16 v19, v96

    move-object/from16 v20, v97

    move-object/from16 v41, v98

    move-object/from16 v42, v99

    move-object/from16 v44, v100

    move/from16 v56, v102

    move-object/from16 v47, v103

    move-object/from16 v48, v104

    .line 226
    :try_start_67
    new-instance v1, Ljava/lang/IllegalStateException;

    invoke-static {v0}, Lcom/bachatas4/android/runtime/vortek/VortekSessionSupportKt;->failureCategory(Lcom/bachatas4/android/runtime/vortek/VortekStartResult;)Ljava/lang/String;

    move-result-object v3

    invoke-virtual {v0}, Lcom/bachatas4/android/runtime/vortek/VortekStartResult;->getMessage()Ljava/lang/String;

    move-result-object v0

    new-instance v15, Ljava/lang/StringBuilder;

    invoke-direct {v15}, Ljava/lang/StringBuilder;-><init>()V

    invoke-virtual {v15, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v3
    :try_end_67
    .catch Ljava/util/concurrent/CancellationException; {:try_start_67 .. :try_end_67} :catch_2b
    .catch Ljava/lang/Exception; {:try_start_67 .. :try_end_67} :catch_2a
    .catchall {:try_start_67 .. :try_end_67} :catchall_8

    move-object/from16 v15, v26

    :try_start_68
    invoke-virtual {v3, v15}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v3

    invoke-virtual {v3, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    invoke-direct {v1, v0}, Ljava/lang/IllegalStateException;-><init>(Ljava/lang/String;)V

    throw v1
    :try_end_68
    .catch Ljava/util/concurrent/CancellationException; {:try_start_68 .. :try_end_68} :catch_2b
    .catch Ljava/lang/Exception; {:try_start_68 .. :try_end_68} :catch_29
    .catchall {:try_start_68 .. :try_end_68} :catchall_8

    :catch_29
    move-exception v0

    goto/16 :goto_1f

    :catchall_8
    move-exception v0

    goto :goto_1c

    :catch_2a
    move-exception v0

    move-object/from16 v15, v26

    goto/16 :goto_1f

    :catch_2b
    move-object v3, v2

    move-object v4, v5

    move-object v5, v6

    move-object/from16 v21, v9

    move-object/from16 v22, v10

    move-object/from16 v144, v11

    move-object/from16 v33, v12

    move-object/from16 v142, v14

    move-object/from16 v6, v16

    move-object/from16 v0, v20

    move-object/from16 v141, v28

    move-object/from16 v10, v29

    goto/16 :goto_29

    :catchall_9
    move-exception v0

    move-object/from16 v14, v38

    move-object/from16 v48, v104

    :goto_1c
    move-object/from16 v2, p0

    move-object v4, v0

    move-object v0, v11

    move-object/from16 v33, v12

    move-object/from16 v44, v13

    move-object/from16 v153, v14

    move-object/from16 v151, v27

    move-object/from16 v152, v28

    move-object/from16 v15, v32

    move-object/from16 v155, v48

    :goto_1d
    move-object/from16 v154, v53

    const/4 v1, 0x4

    const/4 v3, 0x0

    const/16 v37, 0x0

    :goto_1e
    move-object v14, v6

    move-object v12, v7

    move-object v11, v8

    move-object v13, v10

    move-object/from16 v6, v29

    move-object/from16 v7, v30

    const/4 v8, 0x1

    move-object v10, v9

    move-object/from16 v9, v31

    goto/16 :goto_146

    :catch_2c
    move-exception v0

    move-object/from16 v18, v1

    move-object/from16 v16, v3

    move-object/from16 v15, v26

    move-object/from16 v14, v38

    move-object/from16 v19, v96

    move-object/from16 v20, v97

    move-object/from16 v41, v98

    move-object/from16 v42, v99

    move-object/from16 v44, v100

    move/from16 v56, v102

    move-object/from16 v47, v103

    move-object/from16 v48, v104

    :goto_1f
    move-object v1, v4

    move-object v4, v6

    move-object/from16 v120, v8

    move-object/from16 v22, v9

    move-object/from16 v129, v11

    move-object/from16 v33, v12

    move-object/from16 v126, v14

    move-object/from16 v112, v15

    move-object/from16 v8, v16

    move-object/from16 v6, v18

    move-object/from16 v9, v19

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v11, v41

    move-object/from16 v12, v44

    move-object/from16 v3, v47

    move-object/from16 v130, v48

    move-object/from16 v127, v53

    move/from16 v90, v56

    const/4 v14, 0x0

    const/16 v34, 0x4

    const/16 v37, 0x0

    const/16 v128, 0x0

    move-object/from16 v16, v0

    move-object v15, v10

    move-object/from16 v44, v13

    move-object/from16 v10, v20

    move-object/from16 v13, v42

    move-object/from16 v20, v7

    :goto_20
    move-object v7, v2

    :goto_21
    move-object/from16 v2, p0

    goto/16 :goto_10d

    :catch_2d
    move-object/from16 v18, v1

    move-object/from16 v16, v3

    :catch_2e
    :goto_22
    move-object/from16 v19, v96

    :goto_23
    move-object/from16 v20, v97

    :goto_24
    move-object/from16 v41, v98

    :goto_25
    move-object/from16 v42, v99

    :goto_26
    move-object/from16 v44, v100

    :goto_27
    move/from16 v56, v102

    move-object/from16 v47, v103

    move-object/from16 v48, v104

    :catch_2f
    :goto_28
    move-object v3, v2

    move-object v4, v5

    move-object v5, v6

    move-object/from16 v21, v9

    move-object/from16 v22, v10

    move-object/from16 v144, v11

    move-object/from16 v33, v12

    move-object/from16 v6, v16

    move-object/from16 v0, v20

    move-object/from16 v141, v28

    move-object/from16 v10, v29

    move-object/from16 v142, v38

    :goto_29
    move-object/from16 v9, v41

    move-object/from16 v14, v42

    move-object/from16 v12, v44

    move-object/from16 v1, v47

    :goto_2a
    move-object/from16 v145, v48

    move-object/from16 v15, v53

    move/from16 v90, v56

    const/4 v2, 0x1

    const/16 v34, 0x4

    const/16 v37, 0x0

    const/16 v40, 0x0

    const/16 v143, 0x0

    move-object/from16 v11, p0

    move-object/from16 v20, v8

    move-object/from16 v44, v13

    move-object/from16 v13, v19

    move-object/from16 v8, v32

    move-object/from16 v19, v7

    move-object/from16 v7, v18

    goto/16 :goto_12b

    :catchall_a
    move-exception v0

    move-object/from16 v16, v15

    goto/16 :goto_35

    :catch_30
    move-exception v0

    move-object/from16 v45, v1

    move-object/from16 v16, v15

    goto :goto_2c

    :catch_31
    move-object/from16 v45, v1

    move-object/from16 v16, v15

    goto/16 :goto_2d

    :catch_32
    move-exception v0

    goto :goto_2b

    :catch_33
    move-object/from16 v16, v3

    move-object/from16 v45, v15

    move/from16 v34, v1

    move-object v4, v5

    move-object v5, v6

    move-object/from16 v19, v7

    move-object/from16 v20, v8

    move-object/from16 v21, v9

    move-object/from16 v22, v10

    move-object/from16 v144, v11

    move-object/from16 v33, v12

    move-object/from16 v44, v13

    move-object/from16 v145, v16

    move-object/from16 v141, v28

    move-object/from16 v10, v29

    move-object/from16 v8, v32

    move-object/from16 v142, v38

    move-object/from16 v9, v41

    move-object/from16 v0, v42

    move-object/from16 v3, v45

    move-object/from16 v6, v47

    move-object/from16 v7, v49

    move-object/from16 v13, v50

    move-object/from16 v14, v51

    move-object/from16 v12, v52

    move-object/from16 v15, v53

    move-object/from16 v1, v57

    move/from16 v90, v64

    const/4 v2, 0x1

    goto/16 :goto_3e

    :catch_34
    move-exception v0

    move/from16 v64, v1

    :goto_2b
    move-object/from16 v16, v3

    move-object/from16 v45, v15

    :goto_2c
    move-object/from16 v15, v26

    move-object/from16 v14, v38

    move-object/from16 v2, p0

    move-object v1, v4

    move-object v4, v6

    move-object/from16 v20, v7

    move-object/from16 v120, v8

    move-object/from16 v22, v9

    move-object/from16 v129, v11

    move-object/from16 v33, v12

    move-object/from16 v44, v13

    move-object/from16 v126, v14

    move-object/from16 v112, v15

    move-object/from16 v130, v16

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v11, v41

    move-object/from16 v7, v45

    move-object/from16 v8, v47

    move-object/from16 v6, v49

    move-object/from16 v9, v50

    move-object/from16 v13, v51

    move-object/from16 v12, v52

    move-object/from16 v127, v53

    move-object/from16 v3, v57

    move/from16 v90, v64

    goto/16 :goto_37

    :catch_35
    move/from16 v64, v1

    move-object/from16 v16, v3

    move-object/from16 v45, v15

    :goto_2d
    move-object v4, v5

    move-object v5, v6

    move-object/from16 v19, v7

    move-object/from16 v20, v8

    move-object/from16 v21, v9

    move-object/from16 v22, v10

    move-object/from16 v144, v11

    move-object/from16 v33, v12

    move-object/from16 v44, v13

    move-object/from16 v145, v16

    move-object/from16 v141, v28

    move-object/from16 v10, v29

    move-object/from16 v8, v32

    move-object/from16 v142, v38

    move-object/from16 v9, v41

    move-object/from16 v0, v42

    move-object/from16 v3, v45

    move-object/from16 v6, v47

    move-object/from16 v7, v49

    move-object/from16 v13, v50

    move-object/from16 v14, v51

    move-object/from16 v12, v52

    move-object/from16 v15, v53

    move-object/from16 v1, v57

    move/from16 v90, v64

    goto/16 :goto_3d

    :catch_36
    move-exception v0

    goto :goto_2e

    :catch_37
    move-object/from16 v16, v3

    move-object/from16 v45, v15

    move/from16 v64, v90

    goto/16 :goto_3c

    :catch_38
    move-exception v0

    move-object/from16 v57, v1

    :goto_2e
    move-object/from16 v16, v3

    move-object/from16 v45, v15

    move-object/from16 v15, v26

    move-object/from16 v14, v38

    move/from16 v64, v90

    goto/16 :goto_36

    :catch_39
    move-object/from16 v57, v1

    move-object/from16 v16, v3

    move-object/from16 v45, v15

    move/from16 v64, v90

    move-object v4, v5

    move-object v5, v6

    move-object/from16 v19, v7

    move-object/from16 v20, v8

    move-object/from16 v21, v9

    move-object/from16 v22, v10

    move-object/from16 v144, v11

    move-object/from16 v33, v12

    move-object/from16 v44, v13

    move-object/from16 v145, v16

    move-object/from16 v141, v28

    move-object/from16 v10, v29

    move-object/from16 v8, v32

    move-object/from16 v142, v38

    move-object/from16 v9, v41

    move-object/from16 v0, v42

    move-object/from16 v3, v45

    move-object/from16 v6, v47

    move-object/from16 v7, v49

    move-object/from16 v13, v50

    move-object/from16 v14, v51

    move-object/from16 v12, v52

    move-object/from16 v15, v53

    goto/16 :goto_3d

    :catch_3a
    move-exception v0

    move-object/from16 v52, v1

    move-object/from16 v16, v3

    move-object/from16 v45, v15

    move-object/from16 v15, v26

    move-object/from16 v14, v38

    goto/16 :goto_34

    :catch_3b
    move-object/from16 v52, v1

    move-object/from16 v16, v3

    move-object/from16 v45, v15

    goto/16 :goto_3b

    :catch_3c
    move-exception v0

    move-object/from16 v51, v1

    move-object/from16 v16, v3

    move-object/from16 v45, v15

    move-object/from16 v15, v26

    move-object/from16 v14, v38

    goto :goto_33

    :catch_3d
    move-object/from16 v51, v1

    move-object/from16 v16, v3

    move-object/from16 v45, v15

    goto/16 :goto_3a

    :catch_3e
    move-exception v0

    move-object/from16 v41, v1

    goto :goto_2f

    :catch_3f
    move-object/from16 v41, v1

    goto :goto_30

    :catch_40
    move-exception v0

    move-object/from16 v42, v1

    goto :goto_2f

    :catch_41
    move-object/from16 v42, v1

    goto :goto_30

    :catch_42
    move-exception v0

    move-object/from16 v50, v1

    :goto_2f
    move-object/from16 v16, v3

    move-object/from16 v45, v15

    move-object/from16 v15, v26

    move-object/from16 v14, v38

    goto :goto_32

    :catch_43
    move-object/from16 v50, v1

    :goto_30
    move-object/from16 v16, v3

    move-object/from16 v45, v15

    goto/16 :goto_39

    :catch_44
    move-exception v0

    move-object/from16 v47, v1

    goto :goto_31

    :catch_45
    move-object/from16 v47, v1

    goto/16 :goto_38

    :catch_46
    move-exception v0

    goto :goto_31

    :catch_47
    move-exception v0

    move-object/from16 v49, v1

    :goto_31
    move-object/from16 v16, v3

    move-object/from16 v45, v15

    move-object/from16 v15, v26

    move-object/from16 v14, v38

    move-object/from16 v50, v87

    :goto_32
    move-object/from16 v51, v88

    :goto_33
    move-object/from16 v52, v89

    :goto_34
    move/from16 v64, v90

    move-object/from16 v57, v92

    goto :goto_36

    :catchall_b
    move-exception v0

    move-object/from16 v16, v3

    :goto_35
    move-object/from16 v14, v38

    move-object/from16 v2, p0

    move-object v4, v0

    move-object v0, v11

    move-object/from16 v33, v12

    move-object/from16 v44, v13

    move-object/from16 v153, v14

    move-object/from16 v155, v16

    move-object/from16 v151, v27

    move-object/from16 v152, v28

    move-object/from16 v15, v32

    goto/16 :goto_1d

    :catch_48
    move-exception v0

    move-object/from16 v16, v3

    move-object/from16 v45, v15

    move-object/from16 v15, v26

    move-object/from16 v14, v38

    move-object/from16 v4, v49

    move-object/from16 v50, v87

    move-object/from16 v51, v88

    move-object/from16 v52, v89

    move/from16 v64, v90

    move-object/from16 v57, v92

    move-object/from16 v49, v1

    :goto_36
    move-object/from16 v2, p0

    move-object v1, v4

    move-object v4, v6

    move-object/from16 v20, v7

    move-object/from16 v120, v8

    move-object/from16 v22, v9

    move-object/from16 v129, v11

    move-object/from16 v33, v12

    move-object/from16 v44, v13

    move-object/from16 v126, v14

    move-object/from16 v112, v15

    move-object/from16 v130, v16

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v11, v41

    move-object/from16 v7, v45

    move-object/from16 v8, v47

    move-object/from16 v6, v49

    move-object/from16 v9, v50

    move-object/from16 v13, v51

    move-object/from16 v12, v52

    move-object/from16 v127, v53

    move-object/from16 v3, v57

    :goto_37
    const/4 v14, 0x0

    const/16 v34, 0x4

    const/16 v37, 0x0

    const/16 v128, 0x0

    move-object/from16 v16, v0

    goto/16 :goto_bc

    :catch_49
    move-object/from16 v49, v1

    :catch_4a
    :goto_38
    move-object/from16 v16, v3

    move-object/from16 v45, v15

    move-object/from16 v50, v87

    :goto_39
    move-object/from16 v51, v88

    :goto_3a
    move-object/from16 v52, v89

    :goto_3b
    move/from16 v64, v90

    move-object/from16 v57, v92

    :goto_3c
    move-object v4, v5

    move-object v5, v6

    move-object/from16 v19, v7

    move-object/from16 v20, v8

    move-object/from16 v21, v9

    move-object/from16 v22, v10

    move-object/from16 v144, v11

    move-object/from16 v33, v12

    move-object/from16 v44, v13

    move-object/from16 v145, v16

    move-object/from16 v141, v28

    move-object/from16 v10, v29

    move-object/from16 v8, v32

    move-object/from16 v142, v38

    move-object/from16 v9, v41

    move-object/from16 v0, v42

    move-object/from16 v3, v45

    move-object/from16 v6, v47

    move-object/from16 v7, v49

    move-object/from16 v13, v50

    move-object/from16 v14, v51

    move-object/from16 v12, v52

    move-object/from16 v15, v53

    move-object/from16 v1, v57

    :goto_3d
    const/4 v2, 0x1

    const/16 v34, 0x4

    :goto_3e
    const/16 v37, 0x0

    const/16 v40, 0x0

    const/16 v143, 0x0

    goto/16 :goto_bd

    :catchall_c
    move-exception v0

    move-object/from16 v14, v38

    move-object/from16 v2, p0

    move-object v4, v0

    move-object v0, v11

    move-object/from16 v33, v12

    move-object/from16 v44, v13

    move-object/from16 v153, v14

    move-object/from16 v151, v27

    move-object/from16 v152, v28

    move-object/from16 v15, v32

    move-object/from16 v154, v53

    const/4 v1, 0x4

    const/4 v3, 0x0

    const/16 v37, 0x0

    const/16 v155, 0x0

    goto/16 :goto_1e

    :catch_4b
    move-exception v0

    move-object/from16 v45, v15

    move-object/from16 v15, v26

    move-object/from16 v14, v38

    move-object/from16 v4, v49

    move-object/from16 v50, v87

    move-object/from16 v51, v88

    move-object/from16 v52, v89

    move/from16 v64, v90

    move-object/from16 v57, v92

    move-object/from16 v49, v1

    move-object/from16 v2, p0

    move-object/from16 v16, v0

    move-object v1, v4

    move-object v4, v6

    move-object/from16 v20, v7

    move-object/from16 v120, v8

    move-object/from16 v22, v9

    move-object/from16 v129, v11

    move-object/from16 v33, v12

    move-object/from16 v44, v13

    move-object/from16 v126, v14

    move-object/from16 v112, v15

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v11, v41

    move-object/from16 v7, v45

    move-object/from16 v8, v47

    move-object/from16 v6, v49

    move-object/from16 v9, v50

    move-object/from16 v13, v51

    move-object/from16 v12, v52

    move-object/from16 v127, v53

    move-object/from16 v3, v57

    const/4 v14, 0x0

    const/16 v34, 0x4

    const/16 v37, 0x0

    const/16 v128, 0x0

    const/16 v130, 0x0

    goto/16 :goto_bc

    :catch_4c
    move-object/from16 v49, v1

    move-object/from16 v45, v15

    move-object/from16 v50, v87

    move-object/from16 v51, v88

    move-object/from16 v52, v89

    move/from16 v64, v90

    move-object/from16 v57, v92

    move-object v4, v5

    move-object v5, v6

    move-object/from16 v19, v7

    move-object/from16 v20, v8

    move-object/from16 v21, v9

    move-object/from16 v22, v10

    move-object/from16 v144, v11

    move-object/from16 v33, v12

    move-object/from16 v44, v13

    move-object/from16 v141, v28

    move-object/from16 v10, v29

    move-object/from16 v8, v32

    move-object/from16 v142, v38

    move-object/from16 v9, v41

    move-object/from16 v0, v42

    move-object/from16 v3, v45

    move-object/from16 v6, v47

    move-object/from16 v7, v49

    move-object/from16 v13, v50

    move-object/from16 v14, v51

    move-object/from16 v12, v52

    move-object/from16 v15, v53

    move-object/from16 v1, v57

    const/4 v2, 0x1

    const/16 v34, 0x4

    const/16 v37, 0x0

    const/16 v40, 0x0

    const/16 v143, 0x0

    const/16 v145, 0x0

    goto/16 :goto_bd

    :cond_f
    move-object/from16 v61, p1

    move-object/from16 v45, v15

    move-object/from16 v14, v38

    move-object/from16 v4, v49

    move-object/from16 v50, v87

    move-object/from16 v51, v88

    move-object/from16 v52, v89

    move/from16 v64, v90

    move-object/from16 v63, v91

    move-object/from16 v57, v92

    move-object/from16 v62, v93

    move-object/from16 v60, v94

    move-object/from16 v58, v95

    move-object/from16 v49, v1

    move-object/from16 v1, v36

    move-object/from16 v55, v0

    move/from16 v16, v2

    move-object/from16 v19, v4

    move-object v4, v5

    move-object v5, v9

    move-object/from16 v18, v10

    move-object/from16 v44, v13

    move-object/from16 v10, v42

    move-object/from16 v9, v49

    move-object/from16 v2, v50

    move-object/from16 v42, v51

    move-object/from16 v17, v57

    move-object/from16 v0, v61

    move-object/from16 v15, v62

    const/16 v111, 0x0

    move-object v13, v7

    move-object/from16 v49, v8

    move-object/from16 v7, v63

    const/4 v8, 0x0

    move-object/from16 p1, v11

    move-object v3, v12

    move-object/from16 v11, v41

    move-object v12, v6

    .line 245
    :goto_3f
    :try_start_69
    invoke-virtual/range {p0 .. p0}, Lcom/bachatas4/android/service/EmulationService;->getLaunchProfileProvider()Lcom/bachatas4/android/RuntimeLaunchProfileProvider;

    move-result-object v6

    .line 248
    invoke-virtual/range {p0 .. p0}, Lcom/bachatas4/android/service/EmulationService;->getFilesDir()Ljava/io/File;

    move-result-object v20
    :try_end_69
    .catch Ljava/util/concurrent/CancellationException; {:try_start_69 .. :try_end_69} :catch_a4
    .catch Ljava/lang/Exception; {:try_start_69 .. :try_end_69} :catch_a3
    .catchall {:try_start_69 .. :try_end_69} :catchall_3a

    move-object/from16 v33, v3

    :try_start_6a
    invoke-virtual/range {v20 .. v20}, Ljava/io/File;->toPath()Ljava/nio/file/Path;

    move-result-object v3
    :try_end_6a
    .catch Ljava/util/concurrent/CancellationException; {:try_start_6a .. :try_end_6a} :catch_a2
    .catch Ljava/lang/Exception; {:try_start_6a .. :try_end_6a} :catch_a1
    .catchall {:try_start_6a .. :try_end_6a} :catchall_39

    move-object/from16 v20, v5

    move-object/from16 v5, v25

    :try_start_6b
    invoke-static {v3, v5}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullExpressionValue(Ljava/lang/Object;Ljava/lang/String;)V

    .line 245
    invoke-virtual {v6, v0, v15, v3, v8}, Lcom/bachatas4/android/RuntimeLaunchProfileProvider;->vulkanConfiguration(Lcom/bachatas4/android/runtime/settings/ResolvedRuntimeProfile;Ljava/nio/file/Path;Ljava/nio/file/Path;Ljava/nio/file/Path;)Lcom/bachatas4/android/runtime/process/VulkanDriverConfiguration;

    move-result-object v3

    .line 251
    invoke-virtual {v0}, Lcom/bachatas4/android/runtime/settings/ResolvedRuntimeProfile;->getGuestBackend()Lcom/bachatas4/android/runtime/settings/RuntimeGuestBackend;

    move-result-object v6

    .line 252
    invoke-virtual {v6}, Lcom/bachatas4/android/runtime/settings/RuntimeGuestBackend;->name()Ljava/lang/String;

    move-result-object v8

    move-object/from16 p2, v3

    sget-object v3, Ljava/util/Locale;->ROOT:Ljava/util/Locale;

    invoke-virtual {v8, v3}, Ljava/lang/String;->toLowerCase(Ljava/util/Locale;)Ljava/lang/String;

    move-result-object v3

    const-string v8, "toLowerCase(...)"

    invoke-static {v3, v8}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullExpressionValue(Ljava/lang/Object;Ljava/lang/String;)V

    iput-object v3, v10, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    .line 253
    new-instance v56, Lcom/bachatas4/android/runtime/diagnostics/DiagnosticDriverInfo;
    :try_end_6b
    .catch Ljava/util/concurrent/CancellationException; {:try_start_6b .. :try_end_6b} :catch_a0
    .catch Ljava/lang/Exception; {:try_start_6b .. :try_end_6b} :catch_9f
    .catchall {:try_start_6b .. :try_end_6b} :catchall_38

    if-eqz v16, :cond_10

    .line 255
    :try_start_6c
    const-string v3, "vortek"
    :try_end_6c
    .catch Ljava/util/concurrent/CancellationException; {:try_start_6c .. :try_end_6c} :catch_4e
    .catch Ljava/lang/Exception; {:try_start_6c .. :try_end_6c} :catch_4d
    .catchall {:try_start_6c .. :try_end_6c} :catchall_d

    move-object/from16 v57, v3

    move-object/from16 v25, v10

    goto/16 :goto_46

    :catchall_d
    move-exception v0

    move-object/from16 v2, p0

    move-object v5, v4

    move-object/from16 v153, v14

    move-object/from16 v10, v20

    move-object/from16 v151, v27

    move-object/from16 v152, v28

    move-object/from16 v6, v29

    move-object/from16 v7, v30

    move-object/from16 v9, v31

    move-object/from16 v15, v32

    move-object/from16 v11, v49

    move-object/from16 v154, v53

    move-object/from16 v155, v111

    const/4 v1, 0x4

    const/4 v3, 0x0

    const/4 v8, 0x1

    const/16 v37, 0x0

    move-object v4, v0

    move-object v14, v12

    move-object v12, v13

    move-object/from16 v13, v18

    :goto_40
    move-object/from16 v0, p1

    goto/16 :goto_146

    :catch_4d
    move-exception v0

    move-object/from16 v129, p1

    move-object/from16 v16, v0

    move-object v5, v4

    move-object v6, v9

    move-object v4, v12

    move-object/from16 v126, v14

    move-object/from16 v3, v17

    move-object/from16 v15, v18

    move-object/from16 v1, v19

    move-object/from16 v22, v20

    :goto_41
    move-object/from16 v112, v26

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    :goto_42
    move-object/from16 v7, v45

    move-object/from16 v8, v47

    move-object/from16 v120, v49

    move-object/from16 v12, v52

    move-object/from16 v127, v53

    move-object/from16 v130, v111

    const/4 v14, 0x0

    const/16 v34, 0x4

    const/16 v37, 0x0

    const/16 v128, 0x0

    move-object v9, v2

    move-object/from16 v20, v13

    move-object/from16 v13, v42

    goto/16 :goto_21

    :catch_4e
    move-object/from16 v144, p1

    move-object v7, v9

    move-object v0, v10

    move-object v9, v11

    move-object v5, v12

    move-object/from16 v19, v13

    move-object/from16 v142, v14

    move-object/from16 v1, v17

    move-object/from16 v22, v18

    move-object/from16 v21, v20

    :goto_43
    move-object/from16 v141, v28

    move-object/from16 v10, v29

    move-object/from16 v8, v32

    move-object/from16 v14, v42

    move-object/from16 v3, v45

    move-object/from16 v6, v47

    move-object/from16 v20, v49

    move-object/from16 v12, v52

    move-object/from16 v15, v53

    move-object/from16 v145, v111

    const/16 v34, 0x4

    const/16 v37, 0x0

    const/16 v40, 0x0

    const/16 v143, 0x0

    move-object/from16 v11, p0

    :goto_44
    move-object v13, v2

    goto/16 :goto_4

    .line 256
    :cond_10
    :try_start_6d
    invoke-virtual/range {p2 .. p2}, Lcom/bachatas4/android/runtime/process/VulkanDriverConfiguration;->getDriverProfileId()Ljava/lang/String;

    move-result-object v3

    check-cast v3, Ljava/lang/CharSequence;

    const-string v8, "turnip"

    check-cast v8, Ljava/lang/CharSequence;
    :try_end_6d
    .catch Ljava/util/concurrent/CancellationException; {:try_start_6d .. :try_end_6d} :catch_a0
    .catch Ljava/lang/Exception; {:try_start_6d .. :try_end_6d} :catch_9f
    .catchall {:try_start_6d .. :try_end_6d} :catchall_38

    move-object/from16 v25, v10

    const/4 v10, 0x1

    :try_start_6e
    invoke-static {v3, v8, v10}, Lkotlin/text/StringsKt;->contains(Ljava/lang/CharSequence;Ljava/lang/CharSequence;Z)Z

    move-result v3
    :try_end_6e
    .catch Ljava/util/concurrent/CancellationException; {:try_start_6e .. :try_end_6e} :catch_9e
    .catch Ljava/lang/Exception; {:try_start_6e .. :try_end_6e} :catch_9c
    .catchall {:try_start_6e .. :try_end_6e} :catchall_38

    if-eqz v3, :cond_11

    :try_start_6f
    const-string v3, "turnip"
    :try_end_6f
    .catch Ljava/util/concurrent/CancellationException; {:try_start_6f .. :try_end_6f} :catch_50
    .catch Ljava/lang/Exception; {:try_start_6f .. :try_end_6f} :catch_4f
    .catchall {:try_start_6f .. :try_end_6f} :catchall_d

    goto :goto_45

    :catch_4f
    move-exception v0

    move-object/from16 v129, p1

    move-object/from16 v16, v0

    move-object v5, v4

    move-object v6, v9

    move-object v4, v12

    move-object/from16 v126, v14

    move-object/from16 v3, v17

    move-object/from16 v15, v18

    move-object/from16 v1, v19

    move-object/from16 v22, v20

    move-object/from16 v10, v25

    goto :goto_41

    :catch_50
    move-object/from16 v144, p1

    move-object v7, v9

    move-object v9, v11

    move-object v5, v12

    move-object/from16 v19, v13

    move-object/from16 v142, v14

    move-object/from16 v1, v17

    move-object/from16 v22, v18

    move-object/from16 v21, v20

    move-object/from16 v0, v25

    goto :goto_43

    .line 257
    :cond_11
    :try_start_70
    const-string v3, "system"

    :goto_45
    move-object/from16 v57, v3

    .line 259
    :goto_46
    invoke-virtual/range {p2 .. p2}, Lcom/bachatas4/android/runtime/process/VulkanDriverConfiguration;->getDriverProfileId()Ljava/lang/String;

    move-result-object v58

    .line 261
    invoke-virtual/range {p2 .. p2}, Lcom/bachatas4/android/runtime/process/VulkanDriverConfiguration;->getBox64Mode()Lcom/bachatas4/android/runtime/process/Box64Mode;

    move-result-object v3

    invoke-virtual {v3}, Lcom/bachatas4/android/runtime/process/Box64Mode;->name()Ljava/lang/String;

    move-result-object v60
    :try_end_70
    .catch Ljava/util/concurrent/CancellationException; {:try_start_70 .. :try_end_70} :catch_9d
    .catch Ljava/lang/Exception; {:try_start_70 .. :try_end_70} :catch_9c
    .catchall {:try_start_70 .. :try_end_70} :catchall_38

    if-eqz v16, :cond_12

    .line 262
    :try_start_71
    const-string v3, "system vortek"
    :try_end_71
    .catch Ljava/util/concurrent/CancellationException; {:try_start_71 .. :try_end_71} :catch_50
    .catch Ljava/lang/Exception; {:try_start_71 .. :try_end_71} :catch_4f
    .catchall {:try_start_71 .. :try_end_71} :catchall_d

    goto :goto_47

    :cond_12
    :try_start_72
    const-string v3, "selected profile"

    :goto_47
    move-object/from16 v61, v3

    .line 263
    invoke-virtual/range {p2 .. p2}, Lcom/bachatas4/android/runtime/process/VulkanDriverConfiguration;->getDriverProfileId()Ljava/lang/String;

    move-result-object v63

    const/16 v64, 0x20

    const/16 v65, 0x0

    const/16 v59, 0x0

    const/16 v62, 0x0

    .line 253
    invoke-direct/range {v56 .. v65}, Lcom/bachatas4/android/runtime/diagnostics/DiagnosticDriverInfo;-><init>(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;ILkotlin/jvm/internal/DefaultConstructorMarker;)V

    move-object/from16 v3, v56

    iput-object v3, v11, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    .line 265
    sget-object v3, Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpoint;->DRIVER_SELECTED:Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpoint;

    invoke-virtual {v12, v3}, Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpointStore;->mark(Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpoint;)V

    .line 266
    sget-object v3, Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpoint;->DRIVER_LOADED:Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpoint;

    invoke-virtual {v12, v3}, Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpointStore;->mark(Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpoint;)V

    .line 267
    invoke-virtual {v6}, Lcom/bachatas4/android/runtime/settings/RuntimeGuestBackend;->name()Ljava/lang/String;

    move-result-object v3

    sget-object v8, Ljava/util/Locale;->ROOT:Ljava/util/Locale;

    invoke-virtual {v3, v8}, Ljava/lang/String;->toLowerCase(Ljava/util/Locale;)Ljava/lang/String;

    move-result-object v3

    const-string v8, "toLowerCase(...)"

    invoke-static {v3, v8}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullExpressionValue(Ljava/lang/Object;Ljava/lang/String;)V

    new-instance v8, Ljava/lang/StringBuilder;

    move-object/from16 v10, v24

    invoke-direct {v8, v10}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v8, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v3

    invoke-virtual {v3}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v3

    move-object/from16 v8, v43

    invoke-virtual {v4, v8, v3}, Lcom/bachatas4/android/runtime/diagnostics/SessionLog;->info(Ljava/lang/String;Ljava/lang/String;)V

    .line 270
    invoke-virtual/range {p2 .. p2}, Lcom/bachatas4/android/runtime/process/VulkanDriverConfiguration;->getDriverProfileId()Ljava/lang/String;

    move-result-object v3

    invoke-virtual/range {p2 .. p2}, Lcom/bachatas4/android/runtime/process/VulkanDriverConfiguration;->getBox64Mode()Lcom/bachatas4/android/runtime/process/Box64Mode;

    move-result-object v10
    :try_end_72
    .catch Ljava/util/concurrent/CancellationException; {:try_start_72 .. :try_end_72} :catch_9d
    .catch Ljava/lang/Exception; {:try_start_72 .. :try_end_72} :catch_9c
    .catchall {:try_start_72 .. :try_end_72} :catchall_38

    move-object/from16 v24, v11

    :try_start_73
    new-instance v11, Ljava/lang/StringBuilder;
    :try_end_73
    .catch Ljava/util/concurrent/CancellationException; {:try_start_73 .. :try_end_73} :catch_9b
    .catch Ljava/lang/Exception; {:try_start_73 .. :try_end_73} :catch_9a
    .catchall {:try_start_73 .. :try_end_73} :catchall_38

    move-object/from16 v36, v12

    move-object/from16 v12, v23

    :try_start_74
    invoke-direct {v11, v12}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v11, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v3

    const-string v11, " box64Mode="

    invoke-virtual {v3, v11}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v3

    invoke-virtual {v3, v10}, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;

    move-result-object v3

    invoke-virtual {v3}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v3

    .line 268
    invoke-virtual {v4, v1, v3}, Lcom/bachatas4/android/runtime/diagnostics/SessionLog;->info(Ljava/lang/String;Ljava/lang/String;)V
    :try_end_74
    .catch Ljava/util/concurrent/CancellationException; {:try_start_74 .. :try_end_74} :catch_99
    .catch Ljava/lang/Exception; {:try_start_74 .. :try_end_74} :catch_98
    .catchall {:try_start_74 .. :try_end_74} :catchall_37

    if-eqz v16, :cond_13

    .line 273
    :try_start_75
    const-string v3, "guest_launch=begin"

    invoke-virtual {v4, v14, v3}, Lcom/bachatas4/android/runtime/diagnostics/SessionLog;->info(Ljava/lang/String;Ljava/lang/String;)V
    :try_end_75
    .catch Ljava/util/concurrent/CancellationException; {:try_start_75 .. :try_end_75} :catch_52
    .catch Ljava/lang/Exception; {:try_start_75 .. :try_end_75} :catch_51
    .catchall {:try_start_75 .. :try_end_75} :catchall_e

    goto/16 :goto_4a

    :catchall_e
    move-exception v0

    move-object/from16 v2, p0

    move-object v5, v4

    :goto_48
    move-object v12, v13

    move-object/from16 v153, v14

    move-object/from16 v13, v18

    move-object/from16 v10, v20

    move-object/from16 v151, v27

    move-object/from16 v152, v28

    move-object/from16 v6, v29

    move-object/from16 v7, v30

    move-object/from16 v9, v31

    move-object/from16 v15, v32

    move-object/from16 v14, v36

    move-object/from16 v11, v49

    move-object/from16 v154, v53

    move-object/from16 v155, v111

    const/4 v1, 0x4

    const/4 v3, 0x0

    const/4 v8, 0x1

    const/16 v37, 0x0

    :goto_49
    move-object v4, v0

    goto/16 :goto_40

    :catch_51
    move-exception v0

    move-object/from16 v129, p1

    move-object/from16 v16, v0

    move-object v5, v4

    move-object v6, v9

    move-object/from16 v126, v14

    move-object/from16 v3, v17

    move-object/from16 v15, v18

    move-object/from16 v1, v19

    move-object/from16 v22, v20

    move-object/from16 v11, v24

    move-object/from16 v10, v25

    move-object/from16 v112, v26

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v4, v36

    goto/16 :goto_42

    :catch_52
    move-object/from16 v11, p0

    :catch_53
    move-object/from16 v144, p1

    move-object v7, v9

    move-object/from16 v19, v13

    move-object/from16 v142, v14

    move-object/from16 v1, v17

    move-object/from16 v22, v18

    move-object/from16 v21, v20

    move-object/from16 v9, v24

    move-object/from16 v0, v25

    move-object/from16 v141, v28

    move-object/from16 v10, v29

    move-object/from16 v8, v32

    move-object/from16 v5, v36

    move-object/from16 v14, v42

    move-object/from16 v3, v45

    move-object/from16 v6, v47

    move-object/from16 v20, v49

    move-object/from16 v12, v52

    move-object/from16 v15, v53

    move-object/from16 v145, v111

    const/16 v34, 0x4

    const/16 v37, 0x0

    const/16 v40, 0x0

    const/16 v143, 0x0

    goto/16 :goto_44

    .line 275
    :cond_13
    :goto_4a
    :try_start_76
    invoke-virtual/range {p0 .. p0}, Lcom/bachatas4/android/service/EmulationService;->getFilesDir()Ljava/io/File;

    move-result-object v3

    invoke-virtual {v3}, Ljava/io/File;->toPath()Ljava/nio/file/Path;

    move-result-object v3

    const-string v10, "runtime-home"

    invoke-interface {v3, v10}, Ljava/nio/file/Path;->resolve(Ljava/lang/String;)Ljava/nio/file/Path;

    move-result-object v3

    .line 276
    sget-object v10, Lcom/bachatas4/android/runtime/config/Fios2CompatibilityFlags;->INSTANCE:Lcom/bachatas4/android/runtime/config/Fios2CompatibilityFlags;

    invoke-static {v3}, Lkotlin/jvm/internal/Intrinsics;->checkNotNull(Ljava/lang/Object;)V

    invoke-virtual {v10, v3, v9}, Lcom/bachatas4/android/runtime/config/Fios2CompatibilityFlags;->ensure(Ljava/nio/file/Path;Ljava/lang/String;)V

    .line 277
    sget-object v10, Lcom/bachatas4/android/runtime/config/ShadPs4ConfigManager;->INSTANCE:Lcom/bachatas4/android/runtime/config/ShadPs4ConfigManager;

    invoke-virtual {v10, v15, v0}, Lcom/bachatas4/android/runtime/config/ShadPs4ConfigManager;->write(Ljava/nio/file/Path;Lcom/bachatas4/android/runtime/settings/ResolvedRuntimeProfile;)V

    const-string v10, "CUSA00093"

    invoke-static {v9, v10}, Lkotlin/jvm/internal/Intrinsics;->areEqual(Ljava/lang/Object;Ljava/lang/Object;)Z

    move-result v10

    goto/16 :goto_4b

    sget-object v10, Lcom/bachatas4/android/runtime/config/ShadPs4ConfigManager;->INSTANCE:Lcom/bachatas4/android/runtime/config/ShadPs4ConfigManager;

    invoke-virtual {v10, v15}, Lcom/bachatas4/android/runtime/config/ShadPs4ConfigManager;->applyDriveclubReadbackProfile(Ljava/nio/file/Path;)V

    const-string v10, "Driveclub"

    const-string v11, "compat_profile=config_path:runtime/user/config.json,config_version:adeb7dca313f5a8fe64d9e50f237ca67dc582a93,readbacks_mode:1,readback_linear_images_enabled:true,copy_gpu_buffers:true"

    invoke-virtual {v4, v10, v11}, Lcom/bachatas4/android/runtime/diagnostics/SessionLog;->info(Ljava/lang/String;Ljava/lang/String;)V

    .line 278
    :goto_4b
    new-instance v10, Ljava/lang/StringBuilder;

    move-object/from16 v11, v22

    invoke-direct {v10, v11}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v10, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;

    move-result-object v10

    invoke-virtual {v10}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v10

    invoke-virtual {v4, v1, v10}, Lcom/bachatas4/android/runtime/diagnostics/SessionLog;->info(Ljava/lang/String;Ljava/lang/String;)V

    .line 279
    sget-object v1, Lcom/bachatas4/android/runtime/settings/RuntimeGuestBackend;->BOX64:Lcom/bachatas4/android/runtime/settings/RuntimeGuestBackend;
    :try_end_76
    .catch Ljava/util/concurrent/CancellationException; {:try_start_76 .. :try_end_76} :catch_99
    .catch Ljava/lang/Exception; {:try_start_76 .. :try_end_76} :catch_98
    .catchall {:try_start_76 .. :try_end_76} :catchall_37

    if-ne v6, v1, :cond_14

    .line 280
    :try_start_77
    invoke-virtual/range {p0 .. p0}, Lcom/bachatas4/android/service/EmulationService;->getLaunchProfileProvider()Lcom/bachatas4/android/RuntimeLaunchProfileProvider;

    move-result-object v1

    invoke-virtual {v1, v0}, Lcom/bachatas4/android/RuntimeLaunchProfileProvider;->box64Environment(Lcom/bachatas4/android/runtime/settings/ResolvedRuntimeProfile;)Ljava/util/Map;

    move-result-object v1
    :try_end_77
    .catch Ljava/util/concurrent/CancellationException; {:try_start_77 .. :try_end_77} :catch_52
    .catch Ljava/lang/Exception; {:try_start_77 .. :try_end_77} :catch_51
    .catchall {:try_start_77 .. :try_end_77} :catchall_e

    goto :goto_4c

    .line 282
    :cond_14
    :try_start_78
    invoke-static {}, Lkotlin/collections/MapsKt;->emptyMap()Ljava/util/Map;

    move-result-object v1

    .line 284
    :goto_4c
    iget-object v10, v13, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v10, Lcom/bachatas4/android/runtime/display/WinlatorEmbeddedXServer;

    invoke-virtual {v10}, Lcom/bachatas4/android/runtime/display/WinlatorEmbeddedXServer;->getDisplay()Ljava/lang/String;

    move-result-object v10
    :try_end_78
    .catch Ljava/util/concurrent/CancellationException; {:try_start_78 .. :try_end_78} :catch_99
    .catch Ljava/lang/Exception; {:try_start_78 .. :try_end_78} :catch_98
    .catchall {:try_start_78 .. :try_end_78} :catchall_37

    move-object/from16 v11, p0

    :try_start_79
    invoke-direct {v11, v15, v3, v7, v10}, Lcom/bachatas4/android/service/EmulationService;->runtimeEnvironment(Ljava/nio/file/Path;Ljava/nio/file/Path;Ljava/io/File;Ljava/lang/String;)Ljava/util/Map;

    move-result-object v3

    .line 285
    invoke-virtual/range {p2 .. p2}, Lcom/bachatas4/android/runtime/process/VulkanDriverConfiguration;->getEnvironment()Ljava/util/Map;

    move-result-object v7

    .line 284
    invoke-static {v3, v7}, Lkotlin/collections/MapsKt;->plus(Ljava/util/Map;Ljava/util/Map;)Ljava/util/Map;

    move-result-object v3

    invoke-static {v3, v1}, Lkotlin/collections/MapsKt;->plus(Ljava/util/Map;Ljava/util/Map;)Ljava/util/Map;

    move-result-object v1

    .line 286
    invoke-virtual {v0}, Lcom/bachatas4/android/runtime/settings/ResolvedRuntimeProfile;->getMaliGpuOptimizations()Z

    move-result v3

    invoke-direct {v11, v3}, Lcom/bachatas4/android/service/EmulationService;->stagingDiagEnvironment(Z)Ljava/util/Map;

    move-result-object v3

    .line 284
    invoke-static {v1, v3}, Lkotlin/collections/MapsKt;->plus(Ljava/util/Map;Ljava/util/Map;)Ljava/util/Map;

    move-result-object v61

    invoke-direct {v11, v0}, Lcom/bachatas4/android/service/EmulationService;->rbSwizzleEnvironment(Lcom/bachatas4/android/runtime/settings/ResolvedRuntimeProfile;)Ljava/util/Map;

    move-result-object v1

    move-object/from16 v3, v61

    invoke-static {v3, v1}, Lkotlin/collections/MapsKt;->plus(Ljava/util/Map;Ljava/util/Map;)Ljava/util/Map;

    move-result-object v61

    .line 287
    invoke-virtual {v0}, Lcom/bachatas4/android/runtime/settings/ResolvedRuntimeProfile;->getMaliGpuOptimizations()Z

    move-result v0
    :try_end_79
    .catch Ljava/util/concurrent/CancellationException; {:try_start_79 .. :try_end_79} :catch_97
    .catch Ljava/lang/Exception; {:try_start_79 .. :try_end_79} :catch_96
    .catchall {:try_start_79 .. :try_end_79} :catchall_36

    if-eqz v0, :cond_15

    .line 288
    :try_start_7a
    const-string v0, "maliGpuOptimizations=true"

    invoke-virtual {v4, v8, v0}, Lcom/bachatas4/android/runtime/diagnostics/SessionLog;->info(Ljava/lang/String;Ljava/lang/String;)V
    :try_end_7a
    .catch Ljava/util/concurrent/CancellationException; {:try_start_7a .. :try_end_7a} :catch_53
    .catch Ljava/lang/Exception; {:try_start_7a .. :try_end_7a} :catch_54
    .catchall {:try_start_7a .. :try_end_7a} :catchall_f

    goto :goto_4d

    :catchall_f
    move-exception v0

    move-object v5, v4

    move-object v2, v11

    goto/16 :goto_48

    :catch_54
    move-exception v0

    move-object/from16 v129, p1

    move-object/from16 v16, v0

    move-object v5, v4

    move-object v6, v9

    move-object/from16 v126, v14

    move-object/from16 v3, v17

    move-object/from16 v15, v18

    move-object/from16 v1, v19

    move-object/from16 v22, v20

    move-object/from16 v10, v25

    move-object/from16 v112, v26

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v4, v36

    move-object/from16 v7, v45

    move-object/from16 v8, v47

    move-object/from16 v120, v49

    move-object/from16 v12, v52

    move-object/from16 v127, v53

    move-object/from16 v130, v111

    const/4 v14, 0x0

    const/16 v34, 0x4

    const/16 v37, 0x0

    const/16 v128, 0x0

    move-object v9, v2

    move-object v2, v11

    move-object/from16 v20, v13

    move-object/from16 v11, v24

    goto/16 :goto_b2

    .line 290
    :cond_15
    :goto_4d
    :try_start_7b
    sget-object v0, Lcom/bachatas4/android/runtime/settings/RuntimeGuestBackend;->FEX:Lcom/bachatas4/android/runtime/settings/RuntimeGuestBackend;
    :try_end_7b
    .catch Ljava/util/concurrent/CancellationException; {:try_start_7b .. :try_end_7b} :catch_97
    .catch Ljava/lang/Exception; {:try_start_7b .. :try_end_7b} :catch_96
    .catchall {:try_start_7b .. :try_end_7b} :catchall_36

    if-ne v6, v0, :cond_16

    .line 291
    :try_start_7c
    const-string v0, "host/shadps4-arm64-fex"

    invoke-interface {v15, v0}, Ljava/nio/file/Path;->resolve(Ljava/lang/String;)Ljava/nio/file/Path;

    move-result-object v0
    :try_end_7c
    .catch Ljava/util/concurrent/CancellationException; {:try_start_7c .. :try_end_7c} :catch_53
    .catch Ljava/lang/Exception; {:try_start_7c .. :try_end_7c} :catch_54
    .catchall {:try_start_7c .. :try_end_7c} :catchall_f

    goto :goto_4e

    .line 293
    :cond_16
    :try_start_7d
    const-string v0, "bin/shadps4"

    invoke-interface {v15, v0}, Ljava/nio/file/Path;->resolve(Ljava/lang/String;)Ljava/nio/file/Path;

    move-result-object v0
    :try_end_7d
    .catch Ljava/util/concurrent/CancellationException; {:try_start_7d .. :try_end_7d} :catch_97
    .catch Ljava/lang/Exception; {:try_start_7d .. :try_end_7d} :catch_96
    .catchall {:try_start_7d .. :try_end_7d} :catchall_36

    :goto_4e
    move-object/from16 v59, v0

    .line 296
    :try_start_7e
    new-instance v0, Lcom/bachatas4/android/runtime/process/RuntimeProcessLauncher;
    :try_end_7e
    .catch Ljava/lang/Exception; {:try_start_7e .. :try_end_7e} :catch_92
    .catch Ljava/util/concurrent/CancellationException; {:try_start_7e .. :try_end_7e} :catch_91
    .catchall {:try_start_7e .. :try_end_7e} :catchall_34

    const/4 v10, 0x1

    const/4 v12, 0x0

    :try_start_7f
    invoke-direct {v0, v12, v10, v12}, Lcom/bachatas4/android/runtime/process/RuntimeProcessLauncher;-><init>(Lcom/bachatas4/android/runtime/process/RuntimeProcessStarter;ILkotlin/jvm/internal/DefaultConstructorMarker;)V
    :try_end_7f
    .catch Ljava/lang/Exception; {:try_start_7f .. :try_end_7f} :catch_90
    .catch Ljava/util/concurrent/CancellationException; {:try_start_7f .. :try_end_7f} :catch_8f
    .catchall {:try_start_7f .. :try_end_7f} :catchall_33

    .line 297
    :try_start_80
    new-instance v54, Lcom/bachatas4/android/runtime/process/RuntimeProcessRequest;

    .line 298
    invoke-static/range {v55 .. v55}, Lkotlin/jvm/internal/Intrinsics;->checkNotNull(Ljava/lang/Object;)V

    .line 300
    invoke-virtual/range {v95 .. v95}, Ljava/io/File;->toPath()Ljava/nio/file/Path;

    move-result-object v1

    invoke-static {v1, v5}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullExpressionValue(Ljava/lang/Object;Ljava/lang/String;)V

    .line 301
    invoke-virtual {v11}, Lcom/bachatas4/android/service/EmulationService;->getFilesDir()Ljava/io/File;

    move-result-object v3

    invoke-virtual {v3}, Ljava/io/File;->toPath()Ljava/nio/file/Path;

    move-result-object v3

    invoke-static {v3, v5}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullExpressionValue(Ljava/lang/Object;Ljava/lang/String;)V

    .line 302
    invoke-static/range {v59 .. v59}, Lkotlin/jvm/internal/Intrinsics;->checkNotNull(Ljava/lang/Object;)V

    .line 303
    invoke-virtual/range {v44 .. v44}, Ljava/io/File;->getPath()Ljava/lang/String;

    move-result-object v5

    const-string v7, "getPath(...)"

    invoke-static {v5, v7}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullExpressionValue(Ljava/lang/Object;Ljava/lang/String;)V

    const/4 v7, 0x2

    .line 305
    new-array v10, v7, [Ljava/lang/String;

    const-string v22, "-g"
    :try_end_80
    .catch Ljava/lang/Exception; {:try_start_80 .. :try_end_80} :catch_8e
    .catch Ljava/util/concurrent/CancellationException; {:try_start_80 .. :try_end_80} :catch_8d
    .catchall {:try_start_80 .. :try_end_80} :catchall_32

    const/16 v37, 0x0

    :try_start_81
    aput-object v22, v10, v37

    invoke-virtual/range {v94 .. v94}, Ljava/io/File;->getPath()Ljava/lang/String;

    move-result-object v22
    :try_end_81
    .catch Ljava/lang/Exception; {:try_start_81 .. :try_end_81} :catch_8c
    .catch Ljava/util/concurrent/CancellationException; {:try_start_81 .. :try_end_81} :catch_8b
    .catchall {:try_start_81 .. :try_end_81} :catchall_31

    const/16 v39, 0x1

    :try_start_82
    aput-object v22, v10, v39
    :try_end_82
    .catch Ljava/lang/Exception; {:try_start_82 .. :try_end_82} :catch_8a
    .catch Ljava/util/concurrent/CancellationException; {:try_start_82 .. :try_end_82} :catch_89
    .catchall {:try_start_82 .. :try_end_82} :catchall_30

    :try_start_83
    invoke-static {v10}, Lkotlin/collections/CollectionsKt;->listOf([Ljava/lang/Object;)Ljava/util/List;

    move-result-object v62

    .line 306
    invoke-virtual/range {v19 .. v19}, Ljava/io/File;->toPath()Ljava/nio/file/Path;

    move-result-object v63

    .line 307
    invoke-virtual/range {p2 .. p2}, Lcom/bachatas4/android/runtime/process/VulkanDriverConfiguration;->getBox64Mode()Lcom/bachatas4/android/runtime/process/Box64Mode;

    move-result-object v64

    move-object/from16 v57, v1

    move-object/from16 v58, v3

    move-object/from16 v60, v5

    move-object/from16 v65, v6

    move-object/from16 v56, v15

    .line 297
    invoke-direct/range {v54 .. v65}, Lcom/bachatas4/android/runtime/process/RuntimeProcessRequest;-><init>(Ljava/nio/file/Path;Ljava/nio/file/Path;Ljava/nio/file/Path;Ljava/nio/file/Path;Ljava/nio/file/Path;Ljava/lang/String;Ljava/util/Map;Ljava/util/List;Ljava/nio/file/Path;Lcom/bachatas4/android/runtime/process/Box64Mode;Lcom/bachatas4/android/runtime/settings/RuntimeGuestBackend;)V

    move-object/from16 v1, v54

    .line 296
    invoke-virtual/range {p2 .. p2}, Lcom/bachatas4/android/runtime/process/VulkanDriverConfiguration;->getBox64Mode()Lcom/bachatas4/android/runtime/process/Box64Mode;

    move-result-object v5

    sget-object v7, Lcom/bachatas4/android/runtime/process/Box64Mode;->APK_NATIVE:Lcom/bachatas4/android/runtime/process/Box64Mode;

    if-ne v5, v7, :cond_17

    const-string v5, "BIONIC_SURFACE_DIRECT renderer=skipped"

    invoke-virtual {v4, v8, v5}, Lcom/bachatas4/android/runtime/diagnostics/SessionLog;->info(Ljava/lang/String;Ljava/lang/String;)V

    move-object/from16 v5, p0

    check-cast v5, Landroid/content/Context;

    invoke-static {v5, v1}, Lcom/bachatas4/android/runtime/process/BionicLaunchBridge;->launch(Landroid/content/Context;Lcom/bachatas4/android/runtime/process/RuntimeProcessRequest;)Lcom/bachatas4/android/runtime/process/RuntimeProcessHandle;

    move-result-object v0

    const-string v7, "bachata_adreno_turbo"

    const/4 v10, 0x0

    invoke-virtual {v5, v7, v10}, Landroid/content/Context;->getSharedPreferences(Ljava/lang/String;I)Landroid/content/SharedPreferences;

    move-result-object v7

    const-string v10, "enabled"

    const/4 v6, 0x0

    invoke-interface {v7, v10, v6}, Landroid/content/SharedPreferences;->getBoolean(Ljava/lang/String;Z)Z

    move-result v39

    invoke-static/range {v39 .. v39}, Lcom/bachatas4/android/turbo/AdrenoTurbo;->apply(Z)Z

    move-result v39

    goto :goto_4f

    :cond_17
    iget-object v5, v13, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v5, Lcom/bachatas4/android/runtime/display/WinlatorEmbeddedXServer;

    invoke-virtual {v5}, Lcom/bachatas4/android/runtime/display/WinlatorEmbeddedXServer;->startRenderer()V

    const-string v5, "GLIBC_SURFACE_RENDERER started"

    invoke-virtual {v4, v8, v5}, Lcom/bachatas4/android/runtime/diagnostics/SessionLog;->info(Ljava/lang/String;Ljava/lang/String;)V

    invoke-virtual {v0, v1}, Lcom/bachatas4/android/runtime/process/RuntimeProcessLauncher;->launch(Lcom/bachatas4/android/runtime/process/RuntimeProcessRequest;)Lcom/bachatas4/android/runtime/process/RuntimeProcessHandle;

    move-result-object v0
    :try_end_83
    .catch Ljava/lang/Exception; {:try_start_83 .. :try_end_83} :catch_8c
    .catch Ljava/util/concurrent/CancellationException; {:try_start_83 .. :try_end_83} :catch_8b
    .catchall {:try_start_83 .. :try_end_83} :catchall_31

    .line 295
    :goto_4f
    :try_start_84
    iput-object v0, v11, Lcom/bachatas4/android/service/EmulationService;->process:Lcom/bachatas4/android/runtime/process/RuntimeProcessHandle;

    .line 321
    invoke-static {}, Ljava/time/Instant;->now()Ljava/time/Instant;

    move-result-object v0

    invoke-virtual {v0}, Ljava/time/Instant;->toString()Ljava/lang/String;

    move-result-object v0

    iput-object v0, v2, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    .line 322
    const-string v0, "backend process launched"

    invoke-virtual {v4, v8, v0}, Lcom/bachatas4/android/runtime/diagnostics/SessionLog;->info(Ljava/lang/String;Ljava/lang/String;)V

    .line 323
    sget-object v0, Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpoint;->BACKEND_LAUNCHED:Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpoint;
    :try_end_84
    .catch Ljava/util/concurrent/CancellationException; {:try_start_84 .. :try_end_84} :catch_8b
    .catch Ljava/lang/Exception; {:try_start_84 .. :try_end_84} :catch_88
    .catchall {:try_start_84 .. :try_end_84} :catchall_31

    move-object/from16 v10, v36

    :try_start_85
    invoke-virtual {v10, v0}, Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpointStore;->mark(Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpoint;)V

    .line 326
    new-instance v0, Lcom/bachatas4/android/service/EmulationService$$ExternalSyntheticLambda2;
    :try_end_85
    .catch Ljava/util/concurrent/CancellationException; {:try_start_85 .. :try_end_85} :catch_87
    .catch Ljava/lang/Exception; {:try_start_85 .. :try_end_85} :catch_86
    .catchall {:try_start_85 .. :try_end_85} :catchall_2f

    move-object/from16 v1, v20

    :try_start_86
    invoke-direct {v0, v1}, Lcom/bachatas4/android/service/EmulationService$$ExternalSyntheticLambda2;-><init>(Lkotlin/jvm/internal/Ref$ObjectRef;)V
    :try_end_86
    .catch Ljava/util/concurrent/CancellationException; {:try_start_86 .. :try_end_86} :catch_85
    .catch Ljava/lang/Exception; {:try_start_86 .. :try_end_86} :catch_84
    .catchall {:try_start_86 .. :try_end_86} :catchall_2e

    move-object/from16 v3, v33

    :try_start_87
    invoke-interface {v3, v0}, Ljava/util/concurrent/ExecutorService;->submit(Ljava/util/concurrent/Callable;)Ljava/util/concurrent/Future;

    move-result-object v0
    :try_end_87
    .catch Ljava/util/concurrent/CancellationException; {:try_start_87 .. :try_end_87} :catch_83
    .catch Ljava/lang/Exception; {:try_start_87 .. :try_end_87} :catch_82
    .catchall {:try_start_87 .. :try_end_87} :catchall_2d

    move-object/from16 v5, v18

    .line 327
    :goto_50
    :try_start_88
    iget-object v6, v5, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;
    :try_end_88
    .catch Ljava/util/concurrent/CancellationException; {:try_start_88 .. :try_end_88} :catch_81
    .catch Ljava/lang/Exception; {:try_start_88 .. :try_end_88} :catch_80
    .catchall {:try_start_88 .. :try_end_88} :catchall_2c

    if-nez v6, :cond_1b

    .line 329
    :try_start_89
    sget-object v6, Ljava/util/concurrent/TimeUnit;->MILLISECONDS:Ljava/util/concurrent/TimeUnit;

    const-wide/16 v7, 0xfa

    invoke-interface {v0, v7, v8, v6}, Ljava/util/concurrent/Future;->get(JLjava/util/concurrent/TimeUnit;)Ljava/lang/Object;

    move-result-object v6

    move-object v15, v6

    check-cast v15, Landroid/net/LocalSocket;
    :try_end_89
    .catch Ljava/util/concurrent/TimeoutException; {:try_start_89 .. :try_end_89} :catch_57
    .catch Ljava/util/concurrent/CancellationException; {:try_start_89 .. :try_end_89} :catch_56
    .catch Ljava/lang/Exception; {:try_start_89 .. :try_end_89} :catch_55
    .catchall {:try_start_89 .. :try_end_89} :catchall_10

    const/4 v8, 0x1

    goto/16 :goto_53

    :catchall_10
    move-exception v0

    move-object/from16 v33, v3

    move-object v2, v11

    move-object v3, v12

    move-object v12, v13

    move-object/from16 v153, v14

    move-object/from16 v151, v27

    move-object/from16 v152, v28

    move-object/from16 v6, v29

    move-object/from16 v7, v30

    move-object/from16 v9, v31

    move-object/from16 v15, v32

    move-object/from16 v11, v49

    move-object/from16 v154, v53

    move-object/from16 v155, v111

    const/4 v8, 0x1

    :goto_51
    move-object v13, v5

    move-object v14, v10

    move-object v10, v1

    move-object v5, v4

    const/4 v1, 0x4

    goto/16 :goto_49

    :catch_55
    move-exception v0

    :goto_52
    move-object/from16 v129, p1

    move-object/from16 v16, v0

    move-object/from16 v22, v1

    move-object/from16 v33, v3

    move-object v15, v5

    move-object v6, v9

    move-object/from16 v128, v12

    move-object/from16 v20, v13

    move-object/from16 v126, v14

    move-object/from16 v3, v17

    move-object/from16 v1, v19

    move-object/from16 v112, v26

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v13, v42

    move-object/from16 v7, v45

    move-object/from16 v8, v47

    move-object/from16 v120, v49

    move-object/from16 v127, v53

    move-object/from16 v130, v111

    const/16 v34, 0x4

    move-object v9, v2

    move-object v5, v4

    move-object v4, v10

    move-object v2, v11

    move-object/from16 v14, v128

    move-object/from16 v11, v24

    move-object/from16 v10, v25

    goto/16 :goto_90

    :catch_56
    move-object/from16 v144, p1

    move-object/from16 v21, v1

    move-object/from16 v33, v3

    move-object/from16 v22, v5

    move-object v7, v9

    move-object v5, v10

    move-object/from16 v40, v12

    move-object/from16 v143, v40

    move-object/from16 v19, v13

    move-object/from16 v142, v14

    move-object/from16 v1, v17

    move-object/from16 v9, v24

    move-object/from16 v0, v25

    move-object/from16 v141, v28

    move-object/from16 v10, v29

    move-object/from16 v8, v32

    move-object/from16 v14, v42

    move-object/from16 v3, v45

    move-object/from16 v6, v47

    move-object/from16 v20, v49

    move-object/from16 v12, v52

    move-object/from16 v15, v53

    move-object/from16 v145, v111

    const/16 v34, 0x4

    goto/16 :goto_44

    .line 331
    :catch_57
    :try_start_8a
    iget-object v6, v11, Lcom/bachatas4/android/service/EmulationService;->process:Lcom/bachatas4/android/runtime/process/RuntimeProcessHandle;

    if-eqz v6, :cond_18

    invoke-interface {v6}, Lcom/bachatas4/android/runtime/process/RuntimeProcessHandle;->isAlive()Z

    move-result v6
    :try_end_8a
    .catch Ljava/util/concurrent/CancellationException; {:try_start_8a .. :try_end_8a} :catch_56
    .catch Ljava/lang/Exception; {:try_start_8a .. :try_end_8a} :catch_59
    .catchall {:try_start_8a .. :try_end_8a} :catchall_12

    const/4 v8, 0x1

    if-ne v6, v8, :cond_19

    move-object v15, v12

    .line 328
    :goto_53
    :try_start_8b
    iput-object v15, v5, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    const/4 v7, 0x2

    goto/16 :goto_50

    :catchall_11
    move-exception v0

    goto :goto_55

    :catch_58
    move-object/from16 v144, p1

    move-object/from16 v21, v1

    move-object/from16 v33, v3

    move-object/from16 v22, v5

    move-object v7, v9

    move-object v5, v10

    move-object/from16 v40, v12

    move-object/from16 v143, v40

    move-object/from16 v19, v13

    move-object/from16 v142, v14

    move-object/from16 v1, v17

    move-object/from16 v9, v24

    move-object/from16 v0, v25

    move-object/from16 v141, v28

    move-object/from16 v10, v29

    move-object/from16 v14, v42

    move-object/from16 v3, v45

    move-object/from16 v6, v47

    move-object/from16 v20, v49

    move-object/from16 v12, v52

    move-object/from16 v15, v53

    move-object/from16 v145, v111

    const/16 v34, 0x4

    move-object v13, v2

    move v2, v8

    goto/16 :goto_fb

    :cond_18
    const/4 v8, 0x1

    .line 332
    :cond_19
    iget-object v0, v11, Lcom/bachatas4/android/service/EmulationService;->process:Lcom/bachatas4/android/runtime/process/RuntimeProcessHandle;

    if-eqz v0, :cond_1a

    invoke-interface {v0}, Lcom/bachatas4/android/runtime/process/RuntimeProcessHandle;->getExitCode()Ljava/lang/Integer;

    move-result-object v15

    goto :goto_54

    :cond_1a
    move-object v15, v12

    :goto_54
    new-instance v0, Ljava/lang/StringBuilder;

    invoke-direct {v0}, Ljava/lang/StringBuilder;-><init>()V

    const-string v6, "shadPS4 exited before socket connect: "

    invoke-virtual {v0, v6}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0, v15}, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0

    .line 331
    new-instance v6, Ljava/lang/IllegalStateException;

    invoke-virtual {v0}, Ljava/lang/Object;->toString()Ljava/lang/String;

    move-result-object v0

    invoke-direct {v6, v0}, Ljava/lang/IllegalStateException;-><init>(Ljava/lang/String;)V

    throw v6
    :try_end_8b
    .catch Ljava/util/concurrent/CancellationException; {:try_start_8b .. :try_end_8b} :catch_58
    .catch Ljava/lang/Exception; {:try_start_8b .. :try_end_8b} :catch_55
    .catchall {:try_start_8b .. :try_end_8b} :catchall_11

    :catchall_12
    move-exception v0

    const/4 v8, 0x1

    :goto_55
    move-object/from16 v33, v3

    move-object v2, v11

    move-object v3, v12

    move-object v12, v13

    move-object/from16 v153, v14

    move-object/from16 v151, v27

    move-object/from16 v152, v28

    move-object/from16 v6, v29

    move-object/from16 v7, v30

    move-object/from16 v9, v31

    move-object/from16 v15, v32

    move-object/from16 v11, v49

    move-object/from16 v154, v53

    move-object/from16 v155, v111

    goto/16 :goto_51

    :catch_59
    move-exception v0

    const/4 v8, 0x1

    goto/16 :goto_52

    :cond_1b
    const/4 v8, 0x1

    .line 337
    :try_start_8c
    sget-object v0, Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpoint;->CONTROL_SOCKET_CONNECTED:Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpoint;

    invoke-virtual {v10, v0}, Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpointStore;->mark(Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpoint;)V

    .line 338
    new-instance v0, Lcom/bachatas4/android/runtime/input/ControllerFrameEncoder;

    invoke-direct {v0}, Lcom/bachatas4/android/runtime/input/ControllerFrameEncoder;-><init>()V

    .line 339
    iget-object v6, v5, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v6, Landroid/net/LocalSocket;

    invoke-virtual {v6}, Landroid/net/LocalSocket;->getOutputStream()Ljava/io/OutputStream;

    move-result-object v6

    .line 340
    new-instance v7, Ljava/lang/Object;

    invoke-direct {v7}, Ljava/lang/Object;-><init>()V
    :try_end_8c
    .catch Ljava/util/concurrent/CancellationException; {:try_start_8c .. :try_end_8c} :catch_7f
    .catch Ljava/lang/Exception; {:try_start_8c .. :try_end_8c} :catch_7e
    .catchall {:try_start_8c .. :try_end_8c} :catchall_2b

    move-object/from16 v33, v3

    const/4 v15, 0x4

    .line 341
    :try_start_8d
    new-array v3, v15, [J
    :try_end_8d
    .catch Ljava/util/concurrent/CancellationException; {:try_start_8d .. :try_end_8d} :catch_7d
    .catch Ljava/lang/Exception; {:try_start_8d .. :try_end_8d} :catch_7c
    .catchall {:try_start_8d .. :try_end_8d} :catchall_2a

    move-object/from16 v50, v2

    .line 342
    :try_start_8e
    new-instance v2, Ljava/util/concurrent/atomic/AtomicReference;

    sget-object v16, Lcom/bachatas4/android/runtime/input/ControllerSnapshot;->Companion:Lcom/bachatas4/android/runtime/input/ControllerSnapshot$Companion;
    :try_end_8e
    .catch Ljava/util/concurrent/CancellationException; {:try_start_8e .. :try_end_8e} :catch_7b
    .catch Ljava/lang/Exception; {:try_start_8e .. :try_end_8e} :catch_7a
    .catchall {:try_start_8e .. :try_end_8e} :catchall_2a

    :try_start_8f
    invoke-virtual/range {v16 .. v16}, Lcom/bachatas4/android/runtime/input/ControllerSnapshot$Companion;->getNeutral()Lcom/bachatas4/android/runtime/input/ControllerSnapshot;

    move-result-object v8

    invoke-direct {v2, v8}, Ljava/util/concurrent/atomic/AtomicReference;-><init>(Ljava/lang/Object;)V
    :try_end_8f
    .catch Ljava/util/concurrent/CancellationException; {:try_start_8f .. :try_end_8f} :catch_79
    .catch Ljava/lang/Exception; {:try_start_8f .. :try_end_8f} :catch_78
    .catchall {:try_start_8f .. :try_end_8f} :catchall_29

    move-object/from16 v20, v1

    .line 343
    :try_start_90
    new-instance v1, Lcom/bachatas4/android/service/EmulationService$$ExternalSyntheticLambda3;
    :try_end_90
    .catch Ljava/util/concurrent/CancellationException; {:try_start_90 .. :try_end_90} :catch_77
    .catch Ljava/lang/Exception; {:try_start_90 .. :try_end_90} :catch_76
    .catchall {:try_start_90 .. :try_end_90} :catchall_28

    move-object v8, v6

    move-object v6, v11

    move-object/from16 v40, v12

    move-object/from16 v119, v14

    move-object/from16 v112, v26

    move-object/from16 v113, v27

    move-object/from16 v114, v28

    move-object/from16 v115, v29

    move-object/from16 v116, v30

    move-object/from16 v117, v31

    move-object/from16 v118, v32

    move-object/from16 v11, v50

    move-object/from16 v14, p1

    move-object v12, v5

    move-object v5, v0

    :try_start_91
    invoke-direct/range {v1 .. v8}, Lcom/bachatas4/android/service/EmulationService$$ExternalSyntheticLambda3;-><init>(Ljava/util/concurrent/atomic/AtomicReference;[JLcom/bachatas4/android/runtime/diagnostics/SessionLog;Lcom/bachatas4/android/runtime/input/ControllerFrameEncoder;Lcom/bachatas4/android/service/EmulationService;Ljava/lang/Object;Ljava/io/OutputStream;)V
    :try_end_91
    .catch Ljava/util/concurrent/CancellationException; {:try_start_91 .. :try_end_91} :catch_75
    .catch Ljava/lang/Exception; {:try_start_91 .. :try_end_91} :catch_74
    .catchall {:try_start_91 .. :try_end_91} :catchall_27

    .line 364
    :try_start_92
    sget-object v0, Lcom/bachatas4/android/runtime/session/ManagedSession;->INSTANCE:Lcom/bachatas4/android/runtime/session/ManagedSession;

    invoke-virtual {v0, v1}, Lcom/bachatas4/android/runtime/session/ManagedSession;->attachControllerSlotSink(Lkotlin/jvm/functions/Function2;)V

    .line 365
    const-string v0, "Input"

    const-string v3, "controller transport attached"

    invoke-virtual {v4, v0, v3}, Lcom/bachatas4/android/runtime/diagnostics/SessionLog;->info(Ljava/lang/String;Ljava/lang/String;)V

    .line 366
    iget-object v0, v12, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v0, Landroid/net/LocalSocket;

    invoke-virtual {v0}, Landroid/net/LocalSocket;->getInputStream()Ljava/io/InputStream;

    move-result-object v0

    const-string v3, "getInputStream(...)"

    invoke-static {v0, v3}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullExpressionValue(Ljava/lang/Object;Ljava/lang/String;)V

    sget-object v3, Lkotlin/text/Charsets;->UTF_8:Ljava/nio/charset/Charset;

    new-instance v5, Ljava/io/InputStreamReader;

    invoke-direct {v5, v0, v3}, Ljava/io/InputStreamReader;-><init>(Ljava/io/InputStream;Ljava/nio/charset/Charset;)V

    check-cast v5, Ljava/io/Reader;

    instance-of v0, v5, Ljava/io/BufferedReader;
    :try_end_92
    .catch Ljava/util/concurrent/CancellationException; {:try_start_92 .. :try_end_92} :catch_73
    .catch Ljava/lang/Exception; {:try_start_92 .. :try_end_92} :catch_72
    .catchall {:try_start_92 .. :try_end_92} :catchall_26

    if-eqz v0, :cond_1c

    :try_start_93
    check-cast v5, Ljava/io/BufferedReader;
    :try_end_93
    .catch Ljava/util/concurrent/CancellationException; {:try_start_93 .. :try_end_93} :catch_5b
    .catch Ljava/lang/Exception; {:try_start_93 .. :try_end_93} :catch_5a
    .catchall {:try_start_93 .. :try_end_93} :catchall_13

    goto/16 :goto_56

    :catchall_13
    move-exception v0

    move-object v2, v13

    move-object v13, v12

    move-object v12, v2

    move-object/from16 v2, p0

    move-object v3, v1

    move-object v5, v4

    move v1, v15

    move-object/from16 v11, v49

    move-object/from16 v154, v53

    move-object/from16 v155, v111

    move-object/from16 v151, v113

    move-object/from16 v152, v114

    move-object/from16 v6, v115

    move-object/from16 v7, v116

    move-object/from16 v9, v117

    move-object/from16 v15, v118

    move-object/from16 v153, v119

    const/4 v8, 0x1

    move-object v4, v0

    move-object v0, v14

    move-object v14, v10

    move-object/from16 v10, v20

    goto/16 :goto_146

    :catch_5a
    move-exception v0

    move-object/from16 v2, p0

    move-object/from16 v16, v0

    move-object/from16 v128, v1

    move-object v5, v4

    move-object v6, v9

    move-object v4, v10

    move-object v9, v11

    move-object/from16 v129, v14

    move/from16 v34, v15

    move-object/from16 v3, v17

    move-object/from16 v1, v19

    move-object/from16 v22, v20

    move-object/from16 v11, v24

    move-object/from16 v10, v25

    move-object/from16 v14, v40

    move-object/from16 v7, v45

    move-object/from16 v8, v47

    move-object/from16 v120, v49

    move-object/from16 v127, v53

    move-object/from16 v130, v111

    move-object/from16 v124, v113

    move-object/from16 v125, v114

    move-object/from16 v29, v115

    move-object/from16 v30, v116

    move-object/from16 v31, v117

    move-object/from16 v32, v118

    move-object/from16 v126, v119

    move-object v15, v12

    move-object/from16 v20, v13

    goto/16 :goto_8f

    :catch_5b
    move-object/from16 v143, v1

    move-object v7, v9

    move-object v5, v10

    move-object/from16 v22, v12

    move-object/from16 v19, v13

    move-object/from16 v144, v14

    move/from16 v34, v15

    move-object/from16 v1, v17

    move-object/from16 v21, v20

    move-object/from16 v9, v24

    move-object/from16 v0, v25

    move-object/from16 v14, v42

    move-object/from16 v3, v45

    move-object/from16 v6, v47

    move-object/from16 v20, v49

    move-object/from16 v12, v52

    move-object/from16 v15, v53

    move-object/from16 v145, v111

    move-object/from16 v27, v113

    move-object/from16 v141, v114

    move-object/from16 v10, v115

    move-object/from16 v30, v116

    move-object/from16 v31, v117

    move-object/from16 v8, v118

    move-object/from16 v142, v119

    const/4 v2, 0x1

    move-object v13, v11

    goto/16 :goto_bd

    :cond_1c
    :try_start_94
    new-instance v0, Ljava/io/BufferedReader;

    const/16 v3, 0x2000

    invoke-direct {v0, v5, v3}, Ljava/io/BufferedReader;-><init>(Ljava/io/Reader;I)V

    move-object v5, v0

    :goto_56
    check-cast v5, Ljava/io/Reader;

    new-instance v0, Lcom/bachatas4/android/service/EmulationService$$ExternalSyntheticLambda4;
    :try_end_94
    .catch Ljava/util/concurrent/CancellationException; {:try_start_94 .. :try_end_94} :catch_73
    .catch Ljava/lang/Exception; {:try_start_94 .. :try_end_94} :catch_72
    .catchall {:try_start_94 .. :try_end_94} :catchall_26

    move-object/from16 v3, p0

    move-object/from16 p1, v1

    move-object v1, v4

    move-object v15, v5

    move-object v4, v9

    move-object/from16 v50, v13

    move-object/from16 v121, v14

    move-object/from16 v13, v17

    move-object/from16 v9, v25

    move-object/from16 v7, v45

    move-object/from16 v5, v47

    move-object/from16 v6, v48

    move-object/from16 v120, v49

    move-object/from16 v8, v52

    move-object/from16 v122, v53

    move-object v14, v2

    move-object v2, v10

    move-object/from16 v47, v12

    move-object/from16 v10, v24

    move-object/from16 v12, v42

    :try_start_95
    invoke-direct/range {v0 .. v14}, Lcom/bachatas4/android/service/EmulationService$$ExternalSyntheticLambda4;-><init>(Lcom/bachatas4/android/runtime/diagnostics/SessionLog;Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpointStore;Lcom/bachatas4/android/service/EmulationService;Ljava/lang/String;Lkotlin/jvm/internal/Ref$BooleanRef;Lcom/bachatas4/android/runtime/session/FrameTelemetryReporter;Ljava/lang/String;Lkotlin/jvm/internal/Ref$ObjectRef;Lkotlin/jvm/internal/Ref$ObjectRef;Lkotlin/jvm/internal/Ref$ObjectRef;Lkotlin/jvm/internal/Ref$ObjectRef;Lkotlin/jvm/internal/Ref$ObjectRef;Lkotlin/jvm/internal/Ref$BooleanRef;Ljava/util/concurrent/atomic/AtomicReference;)V
    :try_end_95
    .catch Ljava/util/concurrent/CancellationException; {:try_start_95 .. :try_end_95} :catch_71
    .catch Ljava/lang/Exception; {:try_start_95 .. :try_end_95} :catch_70
    .catchall {:try_start_95 .. :try_end_95} :catchall_25

    move-object v6, v11

    move-object v11, v3

    move-object v3, v6

    move-object/from16 v49, v4

    move-object v6, v5

    move-object v4, v1

    move-object v5, v2

    move-object v1, v9

    move-object v2, v10

    move-object v9, v12

    move-object v10, v13

    :try_start_96
    invoke-static {v15, v0}, Lkotlin/io/TextStreamsKt;->forEachLine(Ljava/io/Reader;Lkotlin/jvm/functions/Function1;)V

    .line 421
    iget-object v0, v11, Lcom/bachatas4/android/service/EmulationService;->process:Lcom/bachatas4/android/runtime/process/RuntimeProcessHandle;
    :try_end_96
    .catch Ljava/util/concurrent/CancellationException; {:try_start_96 .. :try_end_96} :catch_6f
    .catch Ljava/lang/Exception; {:try_start_96 .. :try_end_96} :catch_6e
    .catchall {:try_start_96 .. :try_end_96} :catchall_24

    if-eqz v0, :cond_1d

    :try_start_97
    sget-object v12, Ljava/util/concurrent/TimeUnit;->SECONDS:Ljava/util/concurrent/TimeUnit;

    const-wide/16 v13, 0x5

    invoke-interface {v0, v13, v14, v12}, Lcom/bachatas4/android/runtime/process/RuntimeProcessHandle;->waitFor(JLjava/util/concurrent/TimeUnit;)Z

    move-result v0

    invoke-static {v0}, Lkotlin/coroutines/jvm/internal/Boxing;->boxBoolean(Z)Ljava/lang/Boolean;
    :try_end_97
    .catch Ljava/util/concurrent/CancellationException; {:try_start_97 .. :try_end_97} :catch_5d
    .catch Ljava/lang/Exception; {:try_start_97 .. :try_end_97} :catch_5c
    .catchall {:try_start_97 .. :try_end_97} :catchall_14

    goto/16 :goto_59

    :catchall_14
    move-exception v0

    move-object/from16 v3, p1

    move-object v14, v5

    move-object v2, v11

    move-object/from16 v10, v20

    move-object/from16 v13, v47

    move-object/from16 v12, v50

    move-object/from16 v155, v111

    move-object/from16 v151, v113

    move-object/from16 v152, v114

    move-object/from16 v6, v115

    move-object/from16 v7, v116

    move-object/from16 v9, v117

    move-object/from16 v15, v118

    move-object/from16 v153, v119

    move-object/from16 v11, v120

    move-object/from16 v154, v122

    :goto_57
    const/4 v1, 0x4

    const/4 v8, 0x1

    const/16 v37, 0x0

    :goto_58
    move-object v5, v4

    move-object v4, v0

    move-object/from16 v0, v121

    goto/16 :goto_146

    :catch_5c
    move-exception v0

    move-object v12, v11

    move-object v11, v2

    move-object v2, v12

    move-object v12, v5

    move-object v5, v4

    move-object v4, v12

    move-object/from16 v128, p1

    move-object/from16 v16, v0

    move-object v12, v8

    move-object v13, v9

    move-object/from16 v22, v20

    move-object/from16 v15, v47

    move-object/from16 v20, v50

    move-object/from16 v130, v111

    move-object/from16 v124, v113

    move-object/from16 v125, v114

    move-object/from16 v29, v115

    move-object/from16 v30, v116

    move-object/from16 v31, v117

    move-object/from16 v32, v118

    move-object/from16 v126, v119

    move-object/from16 v129, v121

    move-object/from16 v127, v122

    const/4 v14, 0x0

    const/16 v34, 0x4

    const/16 v37, 0x0

    move-object v9, v3

    move-object v8, v6

    move-object v3, v10

    move-object/from16 v6, v49

    move-object v10, v1

    move-object/from16 v1, v19

    goto/16 :goto_10d

    :catch_5d
    move-object/from16 v143, p1

    move-object v0, v1

    move-object v13, v3

    move-object v3, v7

    move-object v12, v8

    move-object v14, v9

    move-object v1, v10

    move-object/from16 v21, v20

    move-object/from16 v22, v47

    move-object/from16 v7, v49

    move-object/from16 v19, v50

    move-object/from16 v145, v111

    move-object/from16 v27, v113

    move-object/from16 v141, v114

    move-object/from16 v10, v115

    move-object/from16 v30, v116

    move-object/from16 v31, v117

    move-object/from16 v8, v118

    move-object/from16 v142, v119

    move-object/from16 v20, v120

    move-object/from16 v144, v121

    move-object/from16 v15, v122

    const/16 v34, 0x4

    const/16 v37, 0x0

    const/16 v40, 0x0

    move-object v9, v2

    goto/16 :goto_4

    .line 422
    :cond_1d
    :goto_59
    :try_start_98
    invoke-static {}, Ljava/time/Instant;->now()Ljava/time/Instant;

    move-result-object v0

    invoke-virtual {v0}, Ljava/time/Instant;->toString()Ljava/lang/String;

    move-result-object v12

    .line 423
    iget-object v0, v11, Lcom/bachatas4/android/service/EmulationService;->process:Lcom/bachatas4/android/runtime/process/RuntimeProcessHandle;
    :try_end_98
    .catch Ljava/util/concurrent/CancellationException; {:try_start_98 .. :try_end_98} :catch_6f
    .catch Ljava/lang/Exception; {:try_start_98 .. :try_end_98} :catch_6e
    .catchall {:try_start_98 .. :try_end_98} :catchall_24

    if-eqz v0, :cond_1e

    :try_start_99
    invoke-interface {v0}, Lcom/bachatas4/android/runtime/process/RuntimeProcessHandle;->getExitCode()Ljava/lang/Integer;

    move-result-object v0
    :try_end_99
    .catch Ljava/util/concurrent/CancellationException; {:try_start_99 .. :try_end_99} :catch_5d
    .catch Ljava/lang/Exception; {:try_start_99 .. :try_end_99} :catch_5c
    .catchall {:try_start_99 .. :try_end_99} :catchall_14

    goto :goto_5a

    :cond_1e
    const/4 v0, 0x0

    :goto_5a
    :try_start_9a
    new-instance v13, Ljava/lang/StringBuilder;

    invoke-direct {v13}, Ljava/lang/StringBuilder;-><init>()V

    const-string v14, "backend stopped exitCode="

    invoke-virtual {v13, v14}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v13

    invoke-virtual {v13, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;

    move-result-object v0

    invoke-virtual {v0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v0
    :try_end_9a
    .catch Ljava/util/concurrent/CancellationException; {:try_start_9a .. :try_end_9a} :catch_6f
    .catch Ljava/lang/Exception; {:try_start_9a .. :try_end_9a} :catch_6e
    .catchall {:try_start_9a .. :try_end_9a} :catchall_24

    move-object/from16 v13, v122

    :try_start_9b
    invoke-virtual {v4, v13, v0}, Lcom/bachatas4/android/runtime/diagnostics/SessionLog;->info(Ljava/lang/String;Ljava/lang/String;)V
    :try_end_9b
    .catch Ljava/util/concurrent/CancellationException; {:try_start_9b .. :try_end_9b} :catch_6d
    .catch Ljava/lang/Exception; {:try_start_9b .. :try_end_9b} :catch_6c
    .catchall {:try_start_9b .. :try_end_9b} :catchall_23

    .line 424
    :try_start_9c
    iget-boolean v0, v10, Lkotlin/jvm/internal/Ref$BooleanRef;->element:Z
    :try_end_9c
    .catch Ljava/util/concurrent/CancellationException; {:try_start_9c .. :try_end_9c} :catch_6d
    .catch Ljava/lang/Exception; {:try_start_9c .. :try_end_9c} :catch_6c
    .catchall {:try_start_9c .. :try_end_9c} :catchall_22

    if-nez v0, :cond_21

    .line 425
    :try_start_9d
    sget-object v0, Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpoint;->SESSION_STOPPING:Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpoint;

    invoke-virtual {v5, v0}, Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpointStore;->mark(Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpoint;)V

    .line 430
    iget-object v0, v8, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v0, Ljava/lang/String;

    .line 432
    iget-object v14, v1, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v14, Ljava/lang/String;

    .line 433
    iget-boolean v15, v6, Lkotlin/jvm/internal/Ref$BooleanRef;->element:Z
    :try_end_9d
    .catch Ljava/util/concurrent/CancellationException; {:try_start_9d .. :try_end_9d} :catch_6a
    .catch Ljava/lang/Exception; {:try_start_9d .. :try_end_9d} :catch_69
    .catchall {:try_start_9d .. :try_end_9d} :catchall_1a

    move-object/from16 v25, v1

    .line 434
    :try_start_9e
    iget-object v1, v2, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v1, Lcom/bachatas4/android/runtime/diagnostics/DiagnosticDriverInfo;

    move-object/from16 p2, v1

    .line 435
    iget-object v1, v3, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v1, Ljava/lang/String;

    move-object/from16 p3, v1

    .line 437
    iget-object v1, v11, Lcom/bachatas4/android/service/EmulationService;->process:Lcom/bachatas4/android/runtime/process/RuntimeProcessHandle;
    :try_end_9e
    .catch Ljava/util/concurrent/CancellationException; {:try_start_9e .. :try_end_9e} :catch_6b
    .catch Ljava/lang/Exception; {:try_start_9e .. :try_end_9e} :catch_68
    .catchall {:try_start_9e .. :try_end_9e} :catchall_1a

    if-eqz v1, :cond_1f

    :try_start_9f
    invoke-interface {v1}, Lcom/bachatas4/android/runtime/process/RuntimeProcessHandle;->getExitCode()Ljava/lang/Integer;

    move-result-object v1
    :try_end_9f
    .catch Ljava/util/concurrent/CancellationException; {:try_start_9f .. :try_end_9f} :catch_5f
    .catch Ljava/lang/Exception; {:try_start_9f .. :try_end_9f} :catch_5e
    .catchall {:try_start_9f .. :try_end_9f} :catchall_15

    move-object/from16 v122, v13

    move-object v13, v1

    goto/16 :goto_5b

    :catchall_15
    move-exception v0

    move-object/from16 v3, p1

    move-object v14, v5

    move-object v2, v11

    move-object/from16 v154, v13

    move-object/from16 v10, v20

    move-object/from16 v13, v47

    move-object/from16 v12, v50

    move-object/from16 v155, v111

    move-object/from16 v151, v113

    move-object/from16 v152, v114

    move-object/from16 v6, v115

    move-object/from16 v7, v116

    move-object/from16 v9, v117

    move-object/from16 v15, v118

    move-object/from16 v153, v119

    move-object/from16 v11, v120

    goto/16 :goto_57

    :catch_5e
    move-exception v0

    move-object v1, v11

    move-object v11, v2

    move-object v2, v1

    move-object v1, v5

    move-object v5, v4

    move-object v4, v1

    move-object/from16 v128, p1

    move-object/from16 v16, v0

    move-object v12, v8

    move-object/from16 v127, v13

    move-object/from16 v1, v19

    move-object/from16 v22, v20

    move-object/from16 v15, v47

    move-object/from16 v20, v50

    move-object/from16 v130, v111

    move-object/from16 v124, v113

    move-object/from16 v125, v114

    move-object/from16 v29, v115

    move-object/from16 v30, v116

    move-object/from16 v31, v117

    move-object/from16 v32, v118

    move-object/from16 v126, v119

    move-object/from16 v129, v121

    const/4 v14, 0x0

    const/16 v34, 0x4

    const/16 v37, 0x0

    move-object v8, v6

    move-object v13, v9

    move-object/from16 v6, v49

    move-object v9, v3

    move-object v3, v10

    move-object/from16 v10, v25

    goto/16 :goto_10d

    :catch_5f
    move-object/from16 v143, p1

    move-object v12, v8

    move-object v14, v9

    move-object v1, v10

    move-object v15, v13

    move-object/from16 v21, v20

    move-object/from16 v0, v25

    move-object/from16 v22, v47

    move-object/from16 v19, v50

    move-object/from16 v145, v111

    move-object/from16 v27, v113

    move-object/from16 v141, v114

    move-object/from16 v10, v115

    move-object/from16 v30, v116

    move-object/from16 v31, v117

    move-object/from16 v8, v118

    move-object/from16 v142, v119

    move-object/from16 v20, v120

    move-object/from16 v144, v121

    const/16 v34, 0x4

    const/16 v37, 0x0

    const/16 v40, 0x0

    move-object v9, v2

    move-object v13, v3

    move-object v3, v7

    move-object/from16 v7, v49

    goto/16 :goto_4

    :cond_1f
    move-object/from16 v122, v13

    const/4 v13, 0x0

    .line 439
    :goto_5b
    :try_start_a0
    iget-object v1, v9, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    move-object/from16 v16, v1

    check-cast v16, Ljava/lang/String;
    :try_end_a0
    .catch Ljava/util/concurrent/CancellationException; {:try_start_a0 .. :try_end_a0} :catch_67
    .catch Ljava/lang/Exception; {:try_start_a0 .. :try_end_a0} :catch_66
    .catchall {:try_start_a0 .. :try_end_a0} :catchall_19

    const/16 v17, 0x1000

    const/16 v18, 0x0

    move-object/from16 v52, v8

    move-object v8, v14

    const/4 v14, 0x0

    move-object/from16 v42, v9

    move v9, v15

    const/4 v15, 0x0

    move-object/from16 v24, v2

    move-object/from16 v23, v6

    move-object v1, v10

    move-object v2, v11

    move-object/from16 v22, v20

    move-object/from16 v20, v50

    move-object/from16 v123, v122

    move-object/from16 v10, p2

    move-object/from16 v11, p3

    move-object v6, v0

    move-object/from16 v50, v3

    move-object v3, v7

    move-object/from16 v7, v49

    .line 426
    :try_start_a1
    invoke-static/range {v2 .. v18}, Lcom/bachatas4/android/service/EmulationService;->buildReportContext$default(Lcom/bachatas4/android/service/EmulationService;Ljava/lang/String;Lcom/bachatas4/android/runtime/diagnostics/SessionLog;Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpointStore;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;ZLcom/bachatas4/android/runtime/diagnostics/DiagnosticDriverInfo;Ljava/lang/String;Ljava/lang/String;Ljava/lang/Integer;ZLjava/lang/String;Ljava/lang/String;ILjava/lang/Object;)Lcom/bachatas4/android/runtime/diagnostics/DiagnosticReportContext;

    move-result-object v0
    :try_end_a1
    .catch Ljava/util/concurrent/CancellationException; {:try_start_a1 .. :try_end_a1} :catch_65
    .catch Ljava/lang/Exception; {:try_start_a1 .. :try_end_a1} :catch_64
    .catchall {:try_start_a1 .. :try_end_a1} :catchall_18

    move-object v7, v3

    .line 441
    :try_start_a2
    sget-object v3, Lcom/bachatas4/android/runtime/session/ManagedSession;->INSTANCE:Lcom/bachatas4/android/runtime/session/ManagedSession;

    .line 442
    new-instance v6, Lcom/bachatas4/android/runtime/session/ManagedSessionState$Stopped;

    .line 443
    iget-object v8, v2, Lcom/bachatas4/android/service/EmulationService;->process:Lcom/bachatas4/android/runtime/process/RuntimeProcessHandle;
    :try_end_a2
    .catch Ljava/util/concurrent/CancellationException; {:try_start_a2 .. :try_end_a2} :catch_63
    .catch Ljava/lang/Exception; {:try_start_a2 .. :try_end_a2} :catch_62
    .catchall {:try_start_a2 .. :try_end_a2} :catchall_18

    if-eqz v8, :cond_20

    :try_start_a3
    invoke-interface {v8}, Lcom/bachatas4/android/runtime/process/RuntimeProcessHandle;->getExitCode()Ljava/lang/Integer;

    move-result-object v8
    :try_end_a3
    .catch Ljava/util/concurrent/CancellationException; {:try_start_a3 .. :try_end_a3} :catch_63
    .catch Ljava/lang/Exception; {:try_start_a3 .. :try_end_a3} :catch_60
    .catchall {:try_start_a3 .. :try_end_a3} :catchall_16

    goto :goto_5c

    :catchall_16
    move-exception v0

    move-object/from16 v3, p1

    move-object v14, v5

    move-object/from16 v12, v20

    move-object/from16 v10, v22

    move-object/from16 v13, v47

    move-object/from16 v155, v111

    move-object/from16 v151, v113

    move-object/from16 v152, v114

    move-object/from16 v6, v115

    move-object/from16 v7, v116

    move-object/from16 v9, v117

    move-object/from16 v15, v118

    move-object/from16 v153, v119

    move-object/from16 v11, v120

    move-object/from16 v154, v123

    goto/16 :goto_57

    :catch_60
    move-exception v0

    goto/16 :goto_63

    :cond_20
    const/4 v8, 0x0

    .line 444
    :goto_5c
    :try_start_a4
    invoke-virtual {v0}, Lcom/bachatas4/android/runtime/diagnostics/DiagnosticReportContext;->getTermination()Lcom/bachatas4/android/runtime/diagnostics/ProcessTerminationInfo;

    move-result-object v9

    .line 442
    invoke-direct {v6, v8, v9, v0}, Lcom/bachatas4/android/runtime/session/ManagedSessionState$Stopped;-><init>(Ljava/lang/Integer;Lcom/bachatas4/android/runtime/diagnostics/ProcessTerminationInfo;Lcom/bachatas4/android/runtime/diagnostics/DiagnosticReportContext;)V

    check-cast v6, Lcom/bachatas4/android/runtime/session/ManagedSessionState;

    .line 441
    invoke-virtual {v3, v6}, Lcom/bachatas4/android/runtime/session/ManagedSession;->update(Lcom/bachatas4/android/runtime/session/ManagedSessionState;)V
    :try_end_a4
    .catch Ljava/util/concurrent/CancellationException; {:try_start_a4 .. :try_end_a4} :catch_63
    .catch Ljava/lang/Exception; {:try_start_a4 .. :try_end_a4} :catch_62
    .catchall {:try_start_a4 .. :try_end_a4} :catchall_18

    const/4 v3, 0x1

    .line 448
    :try_start_a5
    iput-boolean v3, v1, Lkotlin/jvm/internal/Ref$BooleanRef;->element:Z
    :try_end_a5
    .catch Ljava/util/concurrent/CancellationException; {:try_start_a5 .. :try_end_a5} :catch_61
    .catch Ljava/lang/Exception; {:try_start_a5 .. :try_end_a5} :catch_60
    .catchall {:try_start_a5 .. :try_end_a5} :catchall_17

    goto/16 :goto_66

    :catchall_17
    move-exception v0

    goto/16 :goto_5f

    :catch_61
    move-object/from16 v143, p1

    move-object v11, v2

    move v2, v3

    move-object v3, v7

    move-object/from16 v19, v20

    move-object/from16 v21, v22

    move-object/from16 v6, v23

    move-object/from16 v9, v24

    move-object/from16 v0, v25

    move-object/from16 v14, v42

    move-object/from16 v22, v47

    move-object/from16 v7, v49

    move-object/from16 v13, v50

    move-object/from16 v12, v52

    move-object/from16 v145, v111

    move-object/from16 v27, v113

    move-object/from16 v141, v114

    move-object/from16 v10, v115

    move-object/from16 v30, v116

    move-object/from16 v31, v117

    move-object/from16 v8, v118

    move-object/from16 v142, v119

    move-object/from16 v20, v120

    move-object/from16 v144, v121

    move-object/from16 v15, v123

    goto/16 :goto_65

    :catch_62
    move-exception v0

    goto/16 :goto_62

    :catch_63
    move-object/from16 v143, p1

    move-object v11, v2

    move-object v3, v7

    goto :goto_5d

    :catchall_18
    move-exception v0

    goto/16 :goto_5e

    :catch_64
    move-exception v0

    move-object/from16 v49, v7

    move-object v7, v3

    goto/16 :goto_62

    :catch_65
    move-object/from16 v49, v7

    move-object v7, v3

    move-object/from16 v143, p1

    move-object v11, v2

    :goto_5d
    move-object/from16 v19, v20

    move-object/from16 v21, v22

    move-object/from16 v6, v23

    move-object/from16 v9, v24

    move-object/from16 v0, v25

    move-object/from16 v14, v42

    move-object/from16 v22, v47

    move-object/from16 v7, v49

    move-object/from16 v13, v50

    move-object/from16 v12, v52

    move-object/from16 v145, v111

    move-object/from16 v27, v113

    move-object/from16 v141, v114

    move-object/from16 v10, v115

    move-object/from16 v30, v116

    move-object/from16 v31, v117

    move-object/from16 v8, v118

    move-object/from16 v142, v119

    move-object/from16 v20, v120

    move-object/from16 v144, v121

    move-object/from16 v15, v123

    goto/16 :goto_64

    :catchall_19
    move-exception v0

    move-object v2, v11

    move-object/from16 v22, v20

    move-object/from16 v20, v50

    move-object/from16 v123, v122

    goto/16 :goto_5e

    :catch_66
    move-exception v0

    move-object/from16 v24, v2

    move-object/from16 v23, v6

    move-object/from16 v52, v8

    move-object/from16 v42, v9

    move-object v1, v10

    move-object v2, v11

    move-object/from16 v22, v20

    move-object/from16 v20, v50

    move-object/from16 v123, v122

    goto/16 :goto_61

    :catch_67
    move-object/from16 v24, v2

    move-object/from16 v23, v6

    move-object/from16 v52, v8

    move-object/from16 v42, v9

    move-object v1, v10

    move-object/from16 v22, v20

    move-object/from16 v20, v50

    move-object/from16 v50, v3

    move-object/from16 v143, p1

    move-object v3, v7

    move-object/from16 v19, v20

    move-object/from16 v21, v22

    move-object/from16 v9, v24

    move-object/from16 v0, v25

    move-object/from16 v14, v42

    move-object/from16 v22, v47

    move-object/from16 v7, v49

    move-object/from16 v13, v50

    move-object/from16 v12, v52

    move-object/from16 v145, v111

    move-object/from16 v27, v113

    move-object/from16 v141, v114

    move-object/from16 v10, v115

    move-object/from16 v30, v116

    move-object/from16 v31, v117

    move-object/from16 v8, v118

    move-object/from16 v142, v119

    move-object/from16 v20, v120

    move-object/from16 v144, v121

    move-object/from16 v15, v122

    goto/16 :goto_64

    :catch_68
    move-exception v0

    goto :goto_60

    :catchall_1a
    move-exception v0

    move-object v2, v11

    move-object/from16 v123, v13

    move-object/from16 v22, v20

    move-object/from16 v20, v50

    :goto_5e
    const/4 v3, 0x1

    :goto_5f
    move v8, v3

    move-object v14, v5

    move-object/from16 v12, v20

    move-object/from16 v10, v22

    move-object/from16 v13, v47

    move-object/from16 v155, v111

    move-object/from16 v151, v113

    move-object/from16 v152, v114

    move-object/from16 v6, v115

    move-object/from16 v7, v116

    move-object/from16 v9, v117

    move-object/from16 v15, v118

    move-object/from16 v153, v119

    move-object/from16 v11, v120

    move-object/from16 v154, v123

    const/4 v1, 0x4

    const/16 v37, 0x0

    move-object/from16 v3, p1

    goto/16 :goto_58

    :catch_69
    move-exception v0

    move-object/from16 v25, v1

    :goto_60
    move-object/from16 v24, v2

    move-object/from16 v23, v6

    move-object/from16 v52, v8

    move-object/from16 v42, v9

    move-object v1, v10

    move-object v2, v11

    move-object/from16 v123, v13

    move-object/from16 v22, v20

    move-object/from16 v20, v50

    :goto_61
    move-object/from16 v50, v3

    :goto_62
    const/4 v3, 0x1

    :goto_63
    move-object v3, v5

    move-object v5, v4

    move-object v4, v3

    move-object/from16 v128, p1

    move-object/from16 v16, v0

    move-object v3, v1

    move-object/from16 v1, v19

    move-object/from16 v8, v23

    move-object/from16 v11, v24

    move-object/from16 v10, v25

    move-object/from16 v13, v42

    move-object/from16 v15, v47

    move-object/from16 v6, v49

    move-object/from16 v9, v50

    move-object/from16 v12, v52

    move-object/from16 v130, v111

    move-object/from16 v124, v113

    move-object/from16 v125, v114

    move-object/from16 v29, v115

    move-object/from16 v30, v116

    move-object/from16 v31, v117

    move-object/from16 v32, v118

    move-object/from16 v126, v119

    move-object/from16 v129, v121

    move-object/from16 v127, v123

    const/4 v14, 0x0

    const/16 v34, 0x4

    const/16 v37, 0x0

    goto/16 :goto_10d

    :catch_6a
    move-object/from16 v25, v1

    :catch_6b
    move-object/from16 v24, v2

    move-object/from16 v23, v6

    move-object/from16 v52, v8

    move-object/from16 v42, v9

    move-object v1, v10

    move-object/from16 v22, v20

    move-object/from16 v20, v50

    move-object/from16 v50, v3

    move-object/from16 v143, p1

    move-object v3, v7

    move-object v15, v13

    move-object/from16 v19, v20

    move-object/from16 v21, v22

    move-object/from16 v9, v24

    move-object/from16 v0, v25

    move-object/from16 v14, v42

    move-object/from16 v22, v47

    move-object/from16 v7, v49

    move-object/from16 v13, v50

    move-object/from16 v12, v52

    move-object/from16 v145, v111

    move-object/from16 v27, v113

    move-object/from16 v141, v114

    move-object/from16 v10, v115

    move-object/from16 v30, v116

    move-object/from16 v31, v117

    move-object/from16 v8, v118

    move-object/from16 v142, v119

    move-object/from16 v20, v120

    move-object/from16 v144, v121

    :goto_64
    const/4 v2, 0x1

    :goto_65
    const/16 v34, 0x4

    const/16 v37, 0x0

    const/16 v40, 0x0

    goto/16 :goto_12b

    :cond_21
    move-object v2, v11

    move-object/from16 v123, v13

    move-object/from16 v22, v20

    move-object/from16 v20, v50

    const/4 v3, 0x1

    :goto_66
    move-object/from16 v14, v121

    if-eqz v14, :cond_25

    move-object/from16 v15, v118

    .line 512
    invoke-interface {v14, v15}, Ljava/nio/file/Path;->resolve(Ljava/lang/String;)Ljava/nio/file/Path;

    move-result-object v0

    if-eqz v0, :cond_25

    .line 513
    :try_start_a6
    sget-object v1, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    move-object v1, v2

    check-cast v1, Lcom/bachatas4/android/service/EmulationService;

    .line 514
    invoke-interface {v0}, Ljava/nio/file/Path;->toFile()Ljava/io/File;

    move-result-object v1

    invoke-virtual {v1}, Ljava/io/File;->isFile()Z

    move-result v1

    if-eqz v1, :cond_22

    .line 517
    invoke-virtual {v4}, Lcom/bachatas4/android/runtime/diagnostics/SessionLog;->getDirectory()Ljava/nio/file/Path;

    move-result-object v1

    move-object/from16 v6, v115

    invoke-interface {v1, v6}, Ljava/nio/file/Path;->resolve(Ljava/lang/String;)Ljava/nio/file/Path;

    move-result-object v1

    .line 518
    new-array v6, v3, [Ljava/nio/file/CopyOption;

    sget-object v7, Ljava/nio/file/StandardCopyOption;->REPLACE_EXISTING:Ljava/nio/file/StandardCopyOption;
    :try_end_a6
    .catchall {:try_start_a6 .. :try_end_a6} :catchall_1c

    const/16 v37, 0x0

    :try_start_a7
    aput-object v7, v6, v37

    .line 515
    invoke-static {v0, v1, v6}, Ljava/nio/file/Files;->copy(Ljava/nio/file/Path;Ljava/nio/file/Path;[Ljava/nio/file/CopyOption;)Ljava/nio/file/Path;

    goto :goto_67

    :cond_22
    const/16 v37, 0x0

    .line 521
    :goto_67
    sget-object v0, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;

    .line 513
    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v0
    :try_end_a7
    .catchall {:try_start_a7 .. :try_end_a7} :catchall_1b

    goto :goto_69

    :catchall_1b
    move-exception v0

    goto :goto_68

    :catchall_1c
    move-exception v0

    const/16 v37, 0x0

    :goto_68
    sget-object v1, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    invoke-static {v0}, Lkotlin/ResultKt;->createFailure(Ljava/lang/Throwable;)Ljava/lang/Object;

    move-result-object v0

    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v0

    .line 521
    :goto_69
    invoke-static {v0}, Lkotlin/Result;->exceptionOrNull-impl(Ljava/lang/Object;)Ljava/lang/Throwable;

    move-result-object v1

    if-eqz v1, :cond_24

    .line 522
    invoke-virtual {v1}, Ljava/lang/Throwable;->getMessage()Ljava/lang/String;

    move-result-object v1

    if-nez v1, :cond_23

    move-object/from16 v1, v35

    :cond_23
    new-instance v6, Ljava/lang/StringBuilder;

    move-object/from16 v8, v116

    invoke-direct {v6, v8}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v6, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v1

    move-object/from16 v9, v117

    invoke-virtual {v4, v9, v1}, Lcom/bachatas4/android/runtime/diagnostics/SessionLog;->warning(Ljava/lang/String;Ljava/lang/String;)V

    .line 523
    :cond_24
    invoke-static {v0}, Lkotlin/Result;->box-impl(Ljava/lang/Object;)Lkotlin/Result;

    goto :goto_6a

    :cond_25
    const/16 v37, 0x0

    :goto_6a
    move/from16 v7, v37

    const/4 v10, 0x4

    :goto_6b
    if-ge v7, v10, :cond_26

    .line 526
    sget-object v0, Lcom/bachatas4/android/runtime/session/ManagedSession;->INSTANCE:Lcom/bachatas4/android/runtime/session/ManagedSession;

    sget-object v1, Lcom/bachatas4/android/runtime/input/ControllerSnapshot;->Companion:Lcom/bachatas4/android/runtime/input/ControllerSnapshot$Companion;

    invoke-virtual {v1}, Lcom/bachatas4/android/runtime/input/ControllerSnapshot$Companion;->getNeutral()Lcom/bachatas4/android/runtime/input/ControllerSnapshot;

    move-result-object v1

    invoke-virtual {v0, v7, v1}, Lcom/bachatas4/android/runtime/session/ManagedSession;->submitController(ILcom/bachatas4/android/runtime/input/ControllerSnapshot;)V

    add-int/lit8 v7, v7, 0x1

    goto :goto_6b

    .line 527
    :cond_26
    sget-object v0, Lcom/bachatas4/android/runtime/session/ManagedSession;->INSTANCE:Lcom/bachatas4/android/runtime/session/ManagedSession;

    move-object/from16 v11, p1

    invoke-virtual {v0, v11}, Lcom/bachatas4/android/runtime/session/ManagedSession;->detachControllerSlotSink(Lkotlin/jvm/functions/Function2;)V

    .line 525
    sget-object v0, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;

    .line 529
    sget-object v0, Lcom/bachatas4/android/runtime/input/PhoneMotionSource;->INSTANCE:Lcom/bachatas4/android/runtime/input/PhoneMotionSource;

    invoke-virtual {v0}, Lcom/bachatas4/android/runtime/input/PhoneMotionSource;->stop()V

    .line 530
    sget-object v0, Lcom/bachatas4/android/runtime/input/GamepadInputManager;->INSTANCE:Lcom/bachatas4/android/runtime/input/GamepadInputManager;

    invoke-virtual {v0}, Lcom/bachatas4/android/runtime/input/GamepadInputManager;->onSessionEnd()V

    .line 531
    iget-object v0, v2, Lcom/bachatas4/android/service/EmulationService;->process:Lcom/bachatas4/android/runtime/process/RuntimeProcessHandle;

    if-eqz v0, :cond_27

    invoke-interface {v0}, Lcom/bachatas4/android/runtime/process/RuntimeProcessHandle;->getExitCode()Ljava/lang/Integer;

    move-result-object v6

    goto :goto_6c

    :cond_27
    const/4 v6, 0x0

    .line 532
    :goto_6c
    iget-object v0, v2, Lcom/bachatas4/android/service/EmulationService;->process:Lcom/bachatas4/android/runtime/process/RuntimeProcessHandle;

    if-eqz v0, :cond_28

    invoke-interface {v0}, Lcom/bachatas4/android/runtime/process/RuntimeProcessHandle;->destroyForcibly()V

    sget-object v0, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;

    :cond_28
    const/4 v12, 0x0

    .line 533
    iput-object v12, v2, Lcom/bachatas4/android/service/EmulationService;->process:Lcom/bachatas4/android/runtime/process/RuntimeProcessHandle;

    .line 534
    :try_start_a8
    sget-object v0, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    move-object v0, v2

    check-cast v0, Lcom/bachatas4/android/service/EmulationService;

    move-object/from16 v13, v47

    iget-object v0, v13, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v0, Landroid/net/LocalSocket;

    if-eqz v0, :cond_29

    invoke-virtual {v0}, Landroid/net/LocalSocket;->close()V

    sget-object v0, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;

    goto :goto_6d

    :cond_29
    move-object v0, v12

    :goto_6d
    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;
    :try_end_a8
    .catchall {:try_start_a8 .. :try_end_a8} :catchall_1d

    goto :goto_6e

    :catchall_1d
    move-exception v0

    sget-object v1, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    invoke-static {v0}, Lkotlin/ResultKt;->createFailure(Ljava/lang/Throwable;)Ljava/lang/Object;

    move-result-object v0

    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;

    .line 535
    :goto_6e
    :try_start_a9
    sget-object v0, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    move-object v0, v2

    check-cast v0, Lcom/bachatas4/android/service/EmulationService;

    move-object/from16 v1, v22

    iget-object v0, v1, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v0, Landroid/net/LocalServerSocket;

    if-eqz v0, :cond_2a

    invoke-virtual {v0}, Landroid/net/LocalServerSocket;->close()V

    sget-object v0, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;

    goto :goto_6f

    :cond_2a
    move-object v0, v12

    :goto_6f
    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;
    :try_end_a9
    .catchall {:try_start_a9 .. :try_end_a9} :catchall_1e

    goto :goto_70

    :catchall_1e
    move-exception v0

    sget-object v1, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    invoke-static {v0}, Lkotlin/ResultKt;->createFailure(Ljava/lang/Throwable;)Ljava/lang/Object;

    move-result-object v0

    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;

    .line 536
    :goto_70
    :try_start_aa
    sget-object v0, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    move-object v0, v2

    check-cast v0, Lcom/bachatas4/android/service/EmulationService;

    move-object/from16 v7, v120

    iget-object v0, v7, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v0, Landroid/net/LocalSocket;

    if-eqz v0, :cond_2b

    invoke-virtual {v0}, Landroid/net/LocalSocket;->close()V

    sget-object v0, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;

    goto :goto_71

    :cond_2b
    move-object v0, v12

    :goto_71
    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;
    :try_end_aa
    .catchall {:try_start_aa .. :try_end_aa} :catchall_1f

    goto :goto_72

    :catchall_1f
    move-exception v0

    sget-object v1, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    invoke-static {v0}, Lkotlin/ResultKt;->createFailure(Ljava/lang/Throwable;)Ljava/lang/Object;

    move-result-object v0

    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;

    .line 537
    :goto_72
    invoke-interface/range {v33 .. v33}, Ljava/util/concurrent/ExecutorService;->shutdownNow()Ljava/util/List;

    .line 538
    :try_start_ab
    sget-object v0, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    move-object v0, v2

    check-cast v0, Lcom/bachatas4/android/service/EmulationService;

    move-object/from16 v1, v20

    iget-object v0, v1, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v0, Lcom/bachatas4/android/runtime/display/WinlatorEmbeddedXServer;

    if-eqz v0, :cond_2c

    new-instance v1, Lcom/bachatas4/android/service/EmulationService$runSession$16$1$1;

    invoke-direct {v1, v0, v12}, Lcom/bachatas4/android/service/EmulationService$runSession$16$1$1;-><init>(Lcom/bachatas4/android/runtime/display/WinlatorEmbeddedXServer;Lkotlin/coroutines/Continuation;)V

    check-cast v1, Lkotlin/jvm/functions/Function2;

    invoke-static {v12, v1, v3, v12}, Lkotlinx/coroutines/BuildersKt;->runBlockingK$default(Lkotlin/coroutines/CoroutineContext;Lkotlin/jvm/functions/Function2;ILjava/lang/Object;)Ljava/lang/Object;

    sget-object v0, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;

    goto :goto_73

    :cond_2c
    move-object v0, v12

    :goto_73
    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;
    :try_end_ab
    .catchall {:try_start_ab .. :try_end_ab} :catchall_20

    goto :goto_74

    :catchall_20
    move-exception v0

    sget-object v1, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    invoke-static {v0}, Lkotlin/ResultKt;->createFailure(Ljava/lang/Throwable;)Ljava/lang/Object;

    move-result-object v0

    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;

    :goto_74
    move-object/from16 v1, v111

    if-eqz v1, :cond_2f

    .line 541
    :try_start_ac
    sget-object v0, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    move-object v0, v2

    check-cast v0, Lcom/bachatas4/android/service/EmulationService;

    .line 542
    new-instance v0, Lcom/bachatas4/android/service/EmulationService$runSession$17$1$1;

    invoke-direct {v0, v1, v6, v12}, Lcom/bachatas4/android/service/EmulationService$runSession$17$1$1;-><init>(Lcom/bachatas4/android/runtime/vortek/VortekSessionSupport;Ljava/lang/Integer;Lkotlin/coroutines/Continuation;)V

    check-cast v0, Lkotlin/jvm/functions/Function2;

    invoke-static {v12, v0, v3, v12}, Lkotlinx/coroutines/BuildersKt;->runBlockingK$default(Lkotlin/coroutines/CoroutineContext;Lkotlin/jvm/functions/Function2;ILjava/lang/Object;)Ljava/lang/Object;

    move-result-object v0

    check-cast v0, Lcom/bachatas4/android/runtime/vortek/VortekStopResult;

    .line 541
    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v0
    :try_end_ac
    .catchall {:try_start_ac .. :try_end_ac} :catchall_21

    goto :goto_75

    :catchall_21
    move-exception v0

    sget-object v1, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    invoke-static {v0}, Lkotlin/ResultKt;->createFailure(Ljava/lang/Throwable;)Ljava/lang/Object;

    move-result-object v0

    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v0

    .line 543
    :goto_75
    invoke-static {v0}, Lkotlin/Result;->exceptionOrNull-impl(Ljava/lang/Object;)Ljava/lang/Throwable;

    move-result-object v1

    if-eqz v1, :cond_2e

    .line 544
    invoke-virtual {v1}, Ljava/lang/Throwable;->getMessage()Ljava/lang/String;

    move-result-object v1

    if-nez v1, :cond_2d

    move-object/from16 v1, v35

    :cond_2d
    new-instance v3, Ljava/lang/StringBuilder;

    move-object/from16 v6, v113

    invoke-direct {v3, v6}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v3, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v1

    move-object/from16 v3, v119

    invoke-virtual {v4, v3, v1}, Lcom/bachatas4/android/runtime/diagnostics/SessionLog;->warning(Ljava/lang/String;Ljava/lang/String;)V

    .line 545
    :cond_2e
    invoke-static {v0}, Lkotlin/Result;->box-impl(Ljava/lang/Object;)Lkotlin/Result;

    .line 547
    :cond_2f
    invoke-virtual/range {v44 .. v44}, Ljava/io/File;->delete()Z

    .line 548
    sget-object v0, Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpoint;->SESSION_FINISHED:Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpoint;

    invoke-virtual {v5, v0}, Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpointStore;->mark(Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpoint;)V

    move-object/from16 v1, v114

    move-object/from16 v3, v123

    goto/16 :goto_142

    :catchall_22
    move-exception v0

    move-object v2, v11

    move-object/from16 v127, v13

    move-object/from16 v1, v20

    move-object/from16 v13, v47

    move-object/from16 v20, v50

    move-object/from16 v40, v111

    move-object/from16 v124, v113

    move-object/from16 v125, v114

    move-object/from16 v6, v115

    move-object/from16 v8, v116

    move-object/from16 v9, v117

    move-object/from16 v15, v118

    move-object/from16 v126, v119

    move-object/from16 v7, v120

    move-object/from16 v14, v121

    const/4 v3, 0x1

    const/4 v10, 0x4

    const/4 v12, 0x0

    const/16 v37, 0x0

    move-object/from16 v11, p1

    move-object v12, v4

    move-object v4, v0

    move-object v0, v14

    move-object v14, v5

    move-object v5, v12

    move v12, v10

    move-object v10, v1

    move v1, v12

    move-object v12, v8

    move v8, v3

    move-object v3, v11

    move-object v11, v7

    move-object v7, v12

    move-object/from16 v12, v20

    move-object/from16 v155, v40

    move-object/from16 v151, v124

    move-object/from16 v152, v125

    move-object/from16 v153, v126

    move-object/from16 v154, v127

    goto/16 :goto_146

    :catchall_23
    move-exception v0

    move-object v2, v11

    move-object/from16 v127, v13

    move-object/from16 v22, v20

    move-object/from16 v13, v47

    move-object/from16 v20, v50

    move-object/from16 v40, v111

    move-object/from16 v124, v113

    move-object/from16 v125, v114

    move-object/from16 v6, v115

    move-object/from16 v8, v116

    move-object/from16 v9, v117

    move-object/from16 v15, v118

    move-object/from16 v126, v119

    move-object/from16 v14, v121

    goto/16 :goto_76

    :catch_6c
    move-exception v0

    move-object/from16 v25, v1

    move-object/from16 v24, v2

    move-object/from16 v23, v6

    move-object/from16 v52, v8

    move-object/from16 v42, v9

    move-object v1, v10

    move-object v2, v11

    move-object/from16 v127, v13

    move-object/from16 v22, v20

    move-object/from16 v13, v47

    move-object/from16 v20, v50

    move-object/from16 v40, v111

    move-object/from16 v124, v113

    move-object/from16 v125, v114

    move-object/from16 v6, v115

    move-object/from16 v8, v116

    move-object/from16 v9, v117

    move-object/from16 v15, v118

    move-object/from16 v126, v119

    move-object/from16 v14, v121

    goto/16 :goto_77

    :catch_6d
    move-object/from16 v25, v1

    move-object/from16 v24, v2

    move-object/from16 v23, v6

    move-object/from16 v52, v8

    move-object/from16 v42, v9

    move-object v1, v10

    move-object v2, v11

    move-object/from16 v127, v13

    move-object/from16 v22, v20

    move-object/from16 v13, v47

    move-object/from16 v20, v50

    move-object/from16 v40, v111

    move-object/from16 v14, v121

    move-object/from16 v11, p1

    move-object/from16 v50, v3

    move-object v3, v7

    move-object/from16 v143, v11

    move-object/from16 v144, v14

    move-object/from16 v19, v20

    move-object/from16 v21, v22

    move-object/from16 v9, v24

    move-object/from16 v0, v25

    move-object/from16 v145, v40

    move-object/from16 v14, v42

    move-object/from16 v7, v49

    move-object/from16 v12, v52

    move-object/from16 v27, v113

    move-object/from16 v141, v114

    move-object/from16 v10, v115

    move-object/from16 v30, v116

    move-object/from16 v31, v117

    move-object/from16 v8, v118

    move-object/from16 v142, v119

    move-object/from16 v20, v120

    move-object/from16 v15, v127

    goto/16 :goto_79

    :catchall_24
    move-exception v0

    move-object v2, v11

    move-object/from16 v22, v20

    move-object/from16 v13, v47

    move-object/from16 v20, v50

    move-object/from16 v40, v111

    move-object/from16 v124, v113

    move-object/from16 v125, v114

    move-object/from16 v6, v115

    move-object/from16 v8, v116

    move-object/from16 v9, v117

    move-object/from16 v15, v118

    move-object/from16 v126, v119

    move-object/from16 v14, v121

    move-object/from16 v127, v122

    :goto_76
    const/4 v3, 0x1

    const/4 v10, 0x4

    const/4 v12, 0x0

    const/16 v37, 0x0

    move-object/from16 v11, p1

    goto/16 :goto_7a

    :catch_6e
    move-exception v0

    move-object/from16 v25, v1

    move-object/from16 v24, v2

    move-object/from16 v23, v6

    move-object/from16 v52, v8

    move-object/from16 v42, v9

    move-object v1, v10

    move-object v2, v11

    move-object/from16 v22, v20

    move-object/from16 v13, v47

    move-object/from16 v20, v50

    move-object/from16 v40, v111

    move-object/from16 v124, v113

    move-object/from16 v125, v114

    move-object/from16 v6, v115

    move-object/from16 v8, v116

    move-object/from16 v9, v117

    move-object/from16 v15, v118

    move-object/from16 v126, v119

    move-object/from16 v14, v121

    move-object/from16 v127, v122

    :goto_77
    const/4 v10, 0x4

    const/4 v12, 0x0

    const/16 v37, 0x0

    move-object/from16 v11, p1

    move-object/from16 v50, v3

    const/4 v3, 0x1

    goto/16 :goto_7c

    :catch_6f
    move-object/from16 v25, v1

    move-object/from16 v24, v2

    move-object/from16 v23, v6

    move-object/from16 v52, v8

    move-object/from16 v42, v9

    move-object v1, v10

    move-object v2, v11

    move-object/from16 v22, v20

    move-object/from16 v13, v47

    move-object/from16 v20, v50

    move-object/from16 v40, v111

    move-object/from16 v14, v121

    move-object/from16 v11, p1

    move-object/from16 v50, v3

    move-object v3, v7

    move-object/from16 v143, v11

    move-object/from16 v144, v14

    move-object/from16 v19, v20

    move-object/from16 v21, v22

    goto/16 :goto_78

    :catchall_25
    move-exception v0

    move-object/from16 v11, p1

    move-object v4, v1

    move-object v5, v2

    move-object v2, v3

    move-object/from16 v22, v20

    move-object/from16 v13, v47

    move-object/from16 v20, v50

    move-object/from16 v40, v111

    move-object/from16 v124, v113

    move-object/from16 v125, v114

    move-object/from16 v6, v115

    move-object/from16 v8, v116

    move-object/from16 v9, v117

    move-object/from16 v15, v118

    move-object/from16 v126, v119

    move-object/from16 v14, v121

    move-object/from16 v127, v122

    const/4 v3, 0x1

    const/4 v10, 0x4

    const/4 v12, 0x0

    const/16 v37, 0x0

    goto/16 :goto_7b

    :catch_70
    move-exception v0

    move-object/from16 v49, v4

    move-object/from16 v23, v5

    move-object/from16 v52, v8

    move-object/from16 v25, v9

    move-object/from16 v24, v10

    move-object/from16 v42, v12

    move-object/from16 v22, v20

    move-object/from16 v20, v50

    move-object/from16 v40, v111

    move-object/from16 v124, v113

    move-object/from16 v125, v114

    move-object/from16 v6, v115

    move-object/from16 v8, v116

    move-object/from16 v9, v117

    move-object/from16 v15, v118

    move-object/from16 v126, v119

    move-object/from16 v14, v121

    move-object/from16 v127, v122

    const/4 v10, 0x4

    const/4 v12, 0x0

    const/16 v37, 0x0

    move-object v4, v1

    move-object v5, v2

    move-object v2, v3

    move-object/from16 v50, v11

    move-object v1, v13

    move-object/from16 v13, v47

    const/4 v3, 0x1

    move-object/from16 v11, p1

    goto/16 :goto_7c

    :catch_71
    move-object/from16 v49, v4

    move-object/from16 v23, v5

    move-object/from16 v52, v8

    move-object/from16 v25, v9

    move-object/from16 v24, v10

    move-object/from16 v42, v12

    move-object/from16 v22, v20

    move-object/from16 v20, v50

    move-object/from16 v40, v111

    move-object/from16 v14, v121

    move-object v4, v1

    move-object v5, v2

    move-object v2, v3

    move-object/from16 v50, v11

    move-object v1, v13

    move-object/from16 v13, v47

    move-object/from16 v11, p1

    move-object v3, v7

    move-object/from16 v143, v11

    move-object/from16 v144, v14

    move-object/from16 v19, v20

    move-object/from16 v21, v22

    move-object/from16 v6, v23

    :goto_78
    move-object/from16 v9, v24

    move-object/from16 v0, v25

    move-object/from16 v145, v40

    move-object/from16 v14, v42

    move-object/from16 v7, v49

    move-object/from16 v12, v52

    move-object/from16 v27, v113

    move-object/from16 v141, v114

    move-object/from16 v10, v115

    move-object/from16 v30, v116

    move-object/from16 v31, v117

    move-object/from16 v8, v118

    move-object/from16 v142, v119

    move-object/from16 v20, v120

    move-object/from16 v15, v122

    :goto_79
    const/16 v34, 0x4

    const/16 v37, 0x0

    const/16 v40, 0x0

    move-object v11, v2

    move-object/from16 v22, v13

    move-object/from16 v13, v50

    goto/16 :goto_4

    :catchall_26
    move-exception v0

    move-object/from16 v2, p0

    move-object v11, v1

    move-object v5, v10

    move v10, v15

    move-object/from16 v22, v20

    move-object/from16 v120, v49

    move-object/from16 v127, v53

    move-object/from16 v124, v113

    move-object/from16 v125, v114

    move-object/from16 v6, v115

    move-object/from16 v8, v116

    move-object/from16 v9, v117

    move-object/from16 v15, v118

    move-object/from16 v126, v119

    const/4 v3, 0x1

    move-object/from16 v20, v13

    move-object v13, v12

    move-object/from16 v12, v40

    move-object/from16 v40, v111

    :goto_7a
    move-object v1, v4

    :goto_7b
    move-object v4, v0

    move-object v0, v14

    move-object v14, v5

    move-object v5, v1

    move-object v7, v8

    move v1, v10

    move-object/from16 v12, v20

    move-object/from16 v10, v22

    move-object/from16 v155, v40

    move-object/from16 v151, v124

    move-object/from16 v152, v125

    move-object/from16 v153, v126

    move-object/from16 v154, v127

    move v8, v3

    move-object v3, v11

    move-object/from16 v11, v120

    goto/16 :goto_146

    :catch_72
    move-exception v0

    move-object/from16 v2, p0

    move-object v5, v10

    move-object/from16 v50, v11

    move v10, v15

    move-object/from16 v22, v20

    move-object/from16 v7, v45

    move-object/from16 v23, v47

    move-object/from16 v120, v49

    move-object/from16 v127, v53

    move-object/from16 v124, v113

    move-object/from16 v125, v114

    move-object/from16 v6, v115

    move-object/from16 v8, v116

    move-object/from16 v15, v118

    move-object/from16 v126, v119

    const/4 v3, 0x1

    move-object v11, v1

    move-object/from16 v49, v9

    move-object/from16 v20, v13

    move-object/from16 v1, v17

    move-object/from16 v9, v117

    move-object v13, v12

    move-object/from16 v12, v40

    move-object/from16 v40, v111

    :goto_7c
    move-object v3, v5

    move-object v5, v4

    move-object v4, v3

    move-object/from16 v16, v0

    move-object v3, v1

    move-object/from16 v29, v6

    move-object/from16 v30, v8

    move-object/from16 v31, v9

    move/from16 v34, v10

    move-object/from16 v128, v11

    move-object/from16 v129, v14

    move-object/from16 v32, v15

    move-object/from16 v1, v19

    move-object/from16 v8, v23

    move-object/from16 v11, v24

    move-object/from16 v10, v25

    move-object/from16 v130, v40

    move-object/from16 v6, v49

    move-object/from16 v9, v50

    move-object v14, v12

    goto/16 :goto_8e

    :catch_73
    move-object v5, v10

    move-object/from16 v50, v11

    move v10, v15

    move-object/from16 v22, v20

    move-object/from16 v7, v45

    move-object/from16 v23, v47

    move-object/from16 v120, v49

    move-object v11, v1

    move-object/from16 v49, v9

    move-object/from16 v20, v13

    move-object/from16 v1, v17

    move-object v13, v12

    move-object/from16 v12, v40

    move-object/from16 v40, v111

    move-object v3, v7

    move/from16 v34, v10

    move-object/from16 v143, v11

    move-object/from16 v144, v14

    move-object/from16 v19, v20

    move-object/from16 v21, v22

    move-object/from16 v6, v23

    move-object/from16 v9, v24

    move-object/from16 v0, v25

    move-object/from16 v145, v40

    move-object/from16 v14, v42

    move-object/from16 v7, v49

    move-object/from16 v15, v53

    move-object/from16 v27, v113

    move-object/from16 v141, v114

    move-object/from16 v10, v115

    move-object/from16 v30, v116

    move-object/from16 v31, v117

    move-object/from16 v8, v118

    move-object/from16 v142, v119

    move-object/from16 v20, v120

    const/4 v2, 0x1

    move-object/from16 v11, p0

    move-object/from16 v40, v12

    goto/16 :goto_a1

    :catchall_27
    move-exception v0

    move-object v2, v6

    move-object v5, v10

    move v10, v15

    move-object/from16 v22, v20

    move-object/from16 v120, v49

    move-object/from16 v127, v53

    move-object/from16 v124, v113

    move-object/from16 v125, v114

    move-object/from16 v6, v115

    move-object/from16 v8, v116

    move-object/from16 v9, v117

    move-object/from16 v15, v118

    move-object/from16 v126, v119

    const/4 v3, 0x1

    move-object/from16 v20, v13

    move-object v13, v12

    move-object/from16 v12, v40

    move-object/from16 v40, v111

    goto/16 :goto_9b

    :catch_74
    move-exception v0

    move-object v2, v6

    move-object v5, v10

    move-object/from16 v50, v11

    move v10, v15

    move-object/from16 v1, v17

    move-object/from16 v22, v20

    move-object/from16 v7, v45

    move-object/from16 v23, v47

    move-object/from16 v120, v49

    move-object/from16 v127, v53

    move-object/from16 v124, v113

    move-object/from16 v125, v114

    move-object/from16 v6, v115

    move-object/from16 v8, v116

    move-object/from16 v15, v118

    move-object/from16 v126, v119

    const/4 v3, 0x1

    move-object/from16 v49, v9

    move-object/from16 v20, v13

    move-object/from16 v9, v117

    move-object v13, v12

    move-object/from16 v12, v40

    move-object/from16 v40, v111

    move-object v3, v5

    move-object v5, v4

    move-object v4, v3

    move-object/from16 v16, v0

    move-object v3, v1

    move-object/from16 v29, v6

    move-object/from16 v30, v8

    move-object/from16 v31, v9

    move/from16 v34, v10

    move-object/from16 v128, v12

    move-object/from16 v129, v14

    move-object/from16 v32, v15

    goto/16 :goto_8d

    :catch_75
    move-object v2, v6

    move-object v5, v10

    move-object/from16 v50, v11

    move v10, v15

    move-object/from16 v1, v17

    move-object/from16 v22, v20

    move-object/from16 v7, v45

    move-object/from16 v23, v47

    move-object/from16 v120, v49

    move-object/from16 v49, v9

    move-object/from16 v20, v13

    move-object v13, v12

    move-object/from16 v12, v40

    move-object/from16 v40, v111

    move-object v11, v2

    move-object v3, v7

    move/from16 v34, v10

    move-object/from16 v143, v12

    move-object/from16 v144, v14

    move-object/from16 v19, v20

    move-object/from16 v21, v22

    move-object/from16 v6, v23

    move-object/from16 v9, v24

    move-object/from16 v0, v25

    move-object/from16 v145, v40

    move-object/from16 v14, v42

    move-object/from16 v7, v49

    move-object/from16 v15, v53

    move-object/from16 v27, v113

    move-object/from16 v141, v114

    move-object/from16 v10, v115

    move-object/from16 v30, v116

    move-object/from16 v31, v117

    move-object/from16 v8, v118

    move-object/from16 v142, v119

    move-object/from16 v20, v120

    goto/16 :goto_7e

    :catchall_28
    move-exception v0

    move-object v2, v11

    move-object/from16 v126, v14

    move-object/from16 v22, v20

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v6, v29

    move-object/from16 v8, v30

    move-object/from16 v9, v31

    move-object/from16 v120, v49

    move-object/from16 v127, v53

    move-object/from16 v40, v111

    const/4 v3, 0x1

    move-object/from16 v14, p1

    move-object/from16 v20, v13

    goto/16 :goto_80

    :catch_76
    move-exception v0

    move-object v2, v11

    move-object/from16 v126, v14

    move-object/from16 v1, v17

    move-object/from16 v22, v20

    move-object/from16 v112, v26

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v6, v29

    move-object/from16 v8, v30

    move-object/from16 v7, v45

    move-object/from16 v23, v47

    move-object/from16 v120, v49

    move-object/from16 v127, v53

    move-object/from16 v40, v111

    const/4 v3, 0x1

    move-object/from16 v14, p1

    move-object/from16 v49, v9

    move-object/from16 v20, v13

    move-object/from16 v9, v31

    move-object v13, v5

    move-object v5, v10

    move v10, v15

    goto/16 :goto_83

    :catch_77
    move-object/from16 v126, v14

    move-object/from16 v1, v17

    move-object/from16 v22, v20

    move-object/from16 v7, v45

    move-object/from16 v23, v47

    move-object/from16 v120, v49

    move-object/from16 v40, v111

    move-object/from16 v14, p1

    move-object/from16 v49, v9

    move-object/from16 v20, v13

    move-object v13, v5

    goto :goto_7d

    :catchall_29
    move-exception v0

    move-object/from16 v22, v1

    move-object v2, v11

    move-object/from16 v20, v13

    move-object/from16 v126, v14

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v6, v29

    move-object/from16 v8, v30

    move-object/from16 v9, v31

    move-object/from16 v120, v49

    move-object/from16 v127, v53

    move-object/from16 v40, v111

    const/4 v3, 0x1

    goto/16 :goto_7f

    :catch_78
    move-exception v0

    move-object/from16 v22, v1

    move-object v2, v11

    move-object/from16 v20, v13

    move-object/from16 v126, v14

    move-object/from16 v1, v17

    move-object/from16 v112, v26

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v6, v29

    move-object/from16 v8, v30

    move-object/from16 v7, v45

    move-object/from16 v23, v47

    move-object/from16 v120, v49

    move-object/from16 v127, v53

    move-object/from16 v40, v111

    const/4 v3, 0x1

    goto/16 :goto_82

    :catch_79
    move-object/from16 v22, v1

    move-object/from16 v20, v13

    move-object/from16 v126, v14

    move-object/from16 v1, v17

    move-object/from16 v7, v45

    move-object/from16 v23, v47

    move-object/from16 v120, v49

    move-object/from16 v40, v111

    move-object/from16 v14, p1

    move-object v13, v5

    move-object/from16 v49, v9

    :goto_7d
    move-object v5, v10

    move v10, v15

    move-object v3, v7

    move/from16 v34, v10

    move-object/from16 v143, v12

    move-object/from16 v144, v14

    move-object/from16 v19, v20

    move-object/from16 v21, v22

    move-object/from16 v6, v23

    move-object/from16 v9, v24

    move-object/from16 v0, v25

    move-object/from16 v141, v28

    move-object/from16 v10, v29

    move-object/from16 v8, v32

    move-object/from16 v145, v40

    move-object/from16 v14, v42

    move-object/from16 v7, v49

    move-object/from16 v15, v53

    move-object/from16 v20, v120

    move-object/from16 v142, v126

    :goto_7e
    const/4 v2, 0x1

    goto/16 :goto_a0

    :catch_7a
    move-exception v0

    move-object/from16 v22, v1

    goto :goto_81

    :catch_7b
    move-object/from16 v22, v1

    goto/16 :goto_84

    :catchall_2a
    move-exception v0

    move-object/from16 v22, v1

    move v3, v8

    move-object v2, v11

    move-object/from16 v20, v13

    move-object/from16 v126, v14

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v6, v29

    move-object/from16 v8, v30

    move-object/from16 v9, v31

    move-object/from16 v120, v49

    move-object/from16 v127, v53

    move-object/from16 v40, v111

    :goto_7f
    move-object/from16 v14, p1

    :goto_80
    move-object v13, v5

    move-object v5, v10

    move v10, v15

    move-object/from16 v15, v32

    goto/16 :goto_9b

    :catch_7c
    move-exception v0

    move-object/from16 v22, v1

    move-object/from16 v50, v2

    :goto_81
    move v3, v8

    move-object v2, v11

    move-object/from16 v20, v13

    move-object/from16 v126, v14

    move-object/from16 v1, v17

    move-object/from16 v112, v26

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v6, v29

    move-object/from16 v8, v30

    move-object/from16 v7, v45

    move-object/from16 v23, v47

    move-object/from16 v120, v49

    move-object/from16 v127, v53

    move-object/from16 v40, v111

    :goto_82
    move-object/from16 v14, p1

    move-object v13, v5

    move-object/from16 v49, v9

    move-object v5, v10

    move v10, v15

    move-object/from16 v9, v31

    :goto_83
    move-object/from16 v15, v32

    goto/16 :goto_8c

    :catch_7d
    move-object/from16 v22, v1

    move-object/from16 v50, v2

    :goto_84
    move v3, v8

    move-object/from16 v20, v13

    move-object/from16 v126, v14

    move-object/from16 v1, v17

    move-object/from16 v7, v45

    move-object/from16 v23, v47

    move-object/from16 v120, v49

    move-object/from16 v40, v111

    move-object/from16 v14, p1

    move-object v13, v5

    move-object/from16 v49, v9

    move-object v5, v10

    move v10, v15

    move v2, v3

    move-object v3, v7

    move/from16 v34, v10

    move-object/from16 v143, v12

    move-object/from16 v144, v14

    move-object/from16 v19, v20

    move-object/from16 v21, v22

    move-object/from16 v6, v23

    move-object/from16 v9, v24

    move-object/from16 v0, v25

    move-object/from16 v141, v28

    move-object/from16 v10, v29

    move-object/from16 v8, v32

    move-object/from16 v145, v40

    move-object/from16 v14, v42

    move-object/from16 v7, v49

    move-object/from16 v15, v53

    move-object/from16 v20, v120

    move-object/from16 v142, v126

    goto/16 :goto_a0

    :catchall_2b
    move-exception v0

    move-object/from16 v22, v1

    move-object/from16 v33, v3

    move v3, v8

    move-object v2, v11

    move-object/from16 v20, v13

    move-object/from16 v126, v14

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v6, v29

    move-object/from16 v8, v30

    move-object/from16 v9, v31

    move-object/from16 v15, v32

    move-object/from16 v120, v49

    move-object/from16 v127, v53

    move-object/from16 v40, v111

    goto/16 :goto_85

    :catch_7e
    move-exception v0

    move-object/from16 v22, v1

    move-object/from16 v50, v2

    move-object/from16 v33, v3

    move v3, v8

    move-object v2, v11

    move-object/from16 v20, v13

    move-object/from16 v126, v14

    move-object/from16 v1, v17

    move-object/from16 v112, v26

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v6, v29

    move-object/from16 v8, v30

    move-object/from16 v15, v32

    move-object/from16 v7, v45

    move-object/from16 v23, v47

    move-object/from16 v120, v49

    move-object/from16 v127, v53

    move-object/from16 v40, v111

    goto/16 :goto_86

    :catch_7f
    move-object/from16 v22, v1

    move-object/from16 v50, v2

    move-object/from16 v33, v3

    move v3, v8

    move-object/from16 v20, v13

    move-object/from16 v126, v14

    move-object/from16 v1, v17

    move-object/from16 v7, v45

    move-object/from16 v23, v47

    move-object/from16 v120, v49

    move-object/from16 v40, v111

    move-object/from16 v14, p1

    move-object v13, v5

    move-object/from16 v49, v9

    move-object v5, v10

    goto/16 :goto_96

    :catchall_2c
    move-exception v0

    move-object/from16 v22, v1

    move-object/from16 v33, v3

    move-object v2, v11

    move-object/from16 v20, v13

    move-object/from16 v126, v14

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v6, v29

    move-object/from16 v8, v30

    move-object/from16 v9, v31

    move-object/from16 v15, v32

    move-object/from16 v120, v49

    move-object/from16 v127, v53

    move-object/from16 v40, v111

    const/4 v3, 0x1

    :goto_85
    move-object/from16 v14, p1

    move-object v13, v5

    move-object v5, v10

    const/4 v10, 0x4

    goto/16 :goto_9b

    :catch_80
    move-exception v0

    move-object/from16 v22, v1

    move-object/from16 v50, v2

    move-object/from16 v33, v3

    move-object v2, v11

    move-object/from16 v20, v13

    move-object/from16 v126, v14

    move-object/from16 v1, v17

    move-object/from16 v112, v26

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v6, v29

    move-object/from16 v8, v30

    move-object/from16 v15, v32

    move-object/from16 v7, v45

    move-object/from16 v23, v47

    move-object/from16 v120, v49

    move-object/from16 v127, v53

    move-object/from16 v40, v111

    const/4 v3, 0x1

    :goto_86
    move-object/from16 v14, p1

    move-object v13, v5

    move-object/from16 v49, v9

    move-object v5, v10

    move-object/from16 v9, v31

    const/4 v10, 0x4

    goto/16 :goto_8c

    :catch_81
    move-object/from16 v22, v1

    move-object/from16 v50, v2

    move-object/from16 v33, v3

    move-object/from16 v20, v13

    move-object/from16 v126, v14

    move-object/from16 v1, v17

    move-object/from16 v7, v45

    move-object/from16 v23, v47

    move-object/from16 v120, v49

    move-object/from16 v40, v111

    move-object/from16 v14, p1

    move-object v13, v5

    move-object/from16 v49, v9

    move-object v5, v10

    goto/16 :goto_9e

    :catchall_2d
    move-exception v0

    move-object/from16 v22, v1

    move-object/from16 v33, v3

    goto :goto_87

    :catch_82
    move-exception v0

    move-object/from16 v22, v1

    move-object/from16 v50, v2

    move-object/from16 v33, v3

    goto :goto_88

    :catch_83
    move-object/from16 v22, v1

    move-object/from16 v50, v2

    move-object/from16 v33, v3

    goto/16 :goto_89

    :catchall_2e
    move-exception v0

    move-object/from16 v22, v1

    :goto_87
    move-object v5, v10

    move-object v2, v11

    move-object/from16 v20, v13

    move-object/from16 v126, v14

    move-object/from16 v13, v18

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v6, v29

    move-object/from16 v8, v30

    move-object/from16 v9, v31

    move-object/from16 v15, v32

    move-object/from16 v120, v49

    move-object/from16 v127, v53

    move-object/from16 v40, v111

    const/4 v3, 0x1

    const/4 v10, 0x4

    move-object/from16 v14, p1

    goto/16 :goto_9b

    :catch_84
    move-exception v0

    move-object/from16 v22, v1

    move-object/from16 v50, v2

    :goto_88
    move-object v5, v10

    move-object v2, v11

    move-object/from16 v20, v13

    move-object/from16 v126, v14

    move-object/from16 v1, v17

    move-object/from16 v13, v18

    move-object/from16 v112, v26

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v6, v29

    move-object/from16 v8, v30

    move-object/from16 v15, v32

    move-object/from16 v7, v45

    move-object/from16 v23, v47

    move-object/from16 v120, v49

    move-object/from16 v127, v53

    move-object/from16 v40, v111

    const/4 v3, 0x1

    const/4 v10, 0x4

    move-object/from16 v14, p1

    move-object/from16 v49, v9

    goto/16 :goto_8b

    :catch_85
    move-object/from16 v22, v1

    move-object/from16 v50, v2

    :goto_89
    move-object v5, v10

    move-object/from16 v20, v13

    move-object/from16 v126, v14

    move-object/from16 v1, v17

    move-object/from16 v13, v18

    move-object/from16 v7, v45

    move-object/from16 v23, v47

    move-object/from16 v120, v49

    move-object/from16 v40, v111

    move-object/from16 v14, p1

    move-object/from16 v49, v9

    goto/16 :goto_9e

    :catchall_2f
    move-exception v0

    move-object v5, v10

    move-object v2, v11

    move-object/from16 v126, v14

    move-object/from16 v22, v20

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v6, v29

    move-object/from16 v8, v30

    move-object/from16 v9, v31

    move-object/from16 v15, v32

    goto/16 :goto_91

    :catch_86
    move-exception v0

    move-object/from16 v50, v2

    move-object v5, v10

    move-object v2, v11

    move-object/from16 v126, v14

    move-object/from16 v1, v17

    move-object/from16 v22, v20

    move-object/from16 v112, v26

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v6, v29

    move-object/from16 v8, v30

    move-object/from16 v15, v32

    goto :goto_8a

    :catch_87
    move-object/from16 v50, v2

    move-object v5, v10

    move-object/from16 v126, v14

    move-object/from16 v1, v17

    move-object/from16 v22, v20

    goto/16 :goto_93

    :catch_88
    move-exception v0

    move-object/from16 v50, v2

    move-object v2, v11

    move-object/from16 v126, v14

    move-object/from16 v1, v17

    move-object/from16 v22, v20

    move-object/from16 v112, v26

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v6, v29

    move-object/from16 v8, v30

    move-object/from16 v15, v32

    move-object/from16 v5, v36

    :goto_8a
    move-object/from16 v7, v45

    move-object/from16 v23, v47

    move-object/from16 v120, v49

    move-object/from16 v127, v53

    move-object/from16 v40, v111

    const/4 v3, 0x1

    const/4 v10, 0x4

    move-object/from16 v14, p1

    move-object/from16 v49, v9

    move-object/from16 v20, v13

    move-object/from16 v13, v18

    :goto_8b
    move-object/from16 v9, v31

    :goto_8c
    move-object v3, v5

    move-object v5, v4

    move-object v4, v3

    move-object/from16 v16, v0

    move-object v3, v1

    move/from16 v34, v10

    move-object/from16 v128, v12

    move-object/from16 v129, v14

    :goto_8d
    move-object/from16 v1, v19

    move-object/from16 v8, v23

    move-object/from16 v11, v24

    move-object/from16 v10, v25

    move-object/from16 v130, v40

    move-object/from16 v6, v49

    move-object/from16 v9, v50

    move-object/from16 v14, v128

    :goto_8e
    move-object v15, v13

    :goto_8f
    move-object/from16 v13, v42

    :goto_90
    move-object/from16 v12, v52

    goto/16 :goto_10d

    :catchall_30
    move-exception v0

    move-object v2, v11

    move-object/from16 v126, v14

    move-object/from16 v22, v20

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v6, v29

    move-object/from16 v8, v30

    move-object/from16 v9, v31

    move-object/from16 v15, v32

    move-object/from16 v5, v36

    move/from16 v3, v39

    move-object/from16 v120, v49

    move-object/from16 v127, v53

    move-object/from16 v40, v111

    goto/16 :goto_92

    :catch_89
    move-object/from16 v50, v2

    move-object/from16 v126, v14

    move-object/from16 v1, v17

    move-object/from16 v22, v20

    move-object/from16 v5, v36

    move-object/from16 v7, v45

    move-object/from16 v23, v47

    move-object/from16 v120, v49

    move-object/from16 v40, v111

    move-object/from16 v14, p1

    move-object/from16 v49, v9

    move-object/from16 v20, v13

    move-object/from16 v13, v18

    move-object v3, v7

    move-object/from16 v143, v12

    move-object/from16 v144, v14

    move-object/from16 v19, v20

    move-object/from16 v21, v22

    move-object/from16 v6, v23

    move-object/from16 v9, v24

    move-object/from16 v0, v25

    move-object/from16 v141, v28

    move-object/from16 v10, v29

    move-object/from16 v8, v32

    move/from16 v2, v39

    goto/16 :goto_97

    :catch_8a
    move-exception v0

    move-object/from16 v50, v2

    move-object v2, v11

    move-object/from16 v126, v14

    move-object/from16 v1, v17

    move-object/from16 v22, v20

    move-object/from16 v112, v26

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v6, v29

    move-object/from16 v8, v30

    move-object/from16 v15, v32

    move-object/from16 v5, v36

    move/from16 v3, v39

    move-object/from16 v7, v45

    move-object/from16 v23, v47

    move-object/from16 v120, v49

    move-object/from16 v127, v53

    move-object/from16 v40, v111

    goto/16 :goto_94

    :catchall_31
    move-exception v0

    move-object v2, v11

    move-object/from16 v126, v14

    move-object/from16 v22, v20

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v6, v29

    move-object/from16 v8, v30

    move-object/from16 v9, v31

    move-object/from16 v15, v32

    move-object/from16 v5, v36

    :goto_91
    move-object/from16 v120, v49

    move-object/from16 v127, v53

    move-object/from16 v40, v111

    const/4 v3, 0x1

    :goto_92
    const/4 v10, 0x4

    goto/16 :goto_9a

    :catch_8b
    move-object/from16 v50, v2

    move-object/from16 v126, v14

    move-object/from16 v1, v17

    move-object/from16 v22, v20

    move-object/from16 v5, v36

    :goto_93
    move-object/from16 v7, v45

    move-object/from16 v23, v47

    move-object/from16 v120, v49

    move-object/from16 v40, v111

    goto/16 :goto_9d

    :catch_8c
    move-exception v0

    move-object/from16 v50, v2

    move-object v2, v11

    move-object/from16 v126, v14

    move-object/from16 v1, v17

    move-object/from16 v22, v20

    move-object/from16 v112, v26

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v6, v29

    move-object/from16 v8, v30

    move-object/from16 v15, v32

    move-object/from16 v5, v36

    move-object/from16 v7, v45

    move-object/from16 v23, v47

    move-object/from16 v120, v49

    move-object/from16 v127, v53

    move-object/from16 v40, v111

    const/4 v3, 0x1

    :goto_94
    const/4 v10, 0x4

    goto/16 :goto_a3

    :catchall_32
    move-exception v0

    move-object v2, v11

    move-object/from16 v126, v14

    move-object/from16 v22, v20

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v6, v29

    move-object/from16 v8, v30

    move-object/from16 v9, v31

    move-object/from16 v15, v32

    move-object/from16 v5, v36

    move-object/from16 v120, v49

    move-object/from16 v127, v53

    move-object/from16 v40, v111

    const/4 v3, 0x1

    goto/16 :goto_95

    :catch_8d
    move-object/from16 v50, v2

    move-object/from16 v126, v14

    move-object/from16 v1, v17

    move-object/from16 v22, v20

    move-object/from16 v5, v36

    move-object/from16 v7, v45

    move-object/from16 v23, v47

    move-object/from16 v120, v49

    move-object/from16 v40, v111

    goto/16 :goto_9c

    :catch_8e
    move-exception v0

    move-object/from16 v50, v2

    move-object v2, v11

    move-object/from16 v126, v14

    move-object/from16 v1, v17

    move-object/from16 v22, v20

    move-object/from16 v112, v26

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v6, v29

    move-object/from16 v8, v30

    move-object/from16 v15, v32

    move-object/from16 v5, v36

    move-object/from16 v7, v45

    move-object/from16 v23, v47

    move-object/from16 v120, v49

    move-object/from16 v127, v53

    move-object/from16 v40, v111

    const/4 v3, 0x1

    goto/16 :goto_98

    :catchall_33
    move-exception v0

    move v3, v10

    move-object v2, v11

    move-object/from16 v126, v14

    move-object/from16 v22, v20

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v6, v29

    move-object/from16 v8, v30

    move-object/from16 v9, v31

    move-object/from16 v15, v32

    move-object/from16 v5, v36

    move-object/from16 v120, v49

    move-object/from16 v127, v53

    move-object/from16 v40, v111

    :goto_95
    const/4 v10, 0x4

    goto/16 :goto_99

    :catch_8f
    move-object/from16 v50, v2

    move v3, v10

    move-object/from16 v126, v14

    move-object/from16 v1, v17

    move-object/from16 v22, v20

    move-object/from16 v5, v36

    move-object/from16 v7, v45

    move-object/from16 v23, v47

    move-object/from16 v120, v49

    move-object/from16 v40, v111

    const/16 v37, 0x0

    move-object/from16 v14, p1

    move-object/from16 v49, v9

    move-object/from16 v20, v13

    move-object/from16 v13, v18

    :goto_96
    move v2, v3

    move-object v3, v7

    move-object/from16 v143, v12

    move-object/from16 v144, v14

    move-object/from16 v19, v20

    move-object/from16 v21, v22

    move-object/from16 v6, v23

    move-object/from16 v9, v24

    move-object/from16 v0, v25

    move-object/from16 v141, v28

    move-object/from16 v10, v29

    move-object/from16 v8, v32

    :goto_97
    move-object/from16 v145, v40

    move-object/from16 v14, v42

    move-object/from16 v7, v49

    move-object/from16 v15, v53

    move-object/from16 v20, v120

    move-object/from16 v142, v126

    goto/16 :goto_9f

    :catch_90
    move-exception v0

    move-object/from16 v50, v2

    move v3, v10

    move-object v2, v11

    move-object/from16 v126, v14

    move-object/from16 v1, v17

    move-object/from16 v22, v20

    move-object/from16 v112, v26

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v6, v29

    move-object/from16 v8, v30

    move-object/from16 v15, v32

    move-object/from16 v5, v36

    move-object/from16 v7, v45

    move-object/from16 v23, v47

    move-object/from16 v120, v49

    move-object/from16 v127, v53

    move-object/from16 v40, v111

    :goto_98
    const/4 v10, 0x4

    goto/16 :goto_a2

    :catchall_34
    move-exception v0

    move-object v2, v11

    move-object/from16 v126, v14

    move-object/from16 v22, v20

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v6, v29

    move-object/from16 v8, v30

    move-object/from16 v9, v31

    move-object/from16 v15, v32

    move-object/from16 v5, v36

    move-object/from16 v120, v49

    move-object/from16 v127, v53

    move-object/from16 v40, v111

    const/4 v3, 0x1

    const/4 v10, 0x4

    const/4 v12, 0x0

    :goto_99
    const/16 v37, 0x0

    :goto_9a
    move-object/from16 v14, p1

    move-object/from16 v20, v13

    move-object/from16 v13, v18

    :goto_9b
    move-object v1, v4

    move-object v4, v0

    move-object v0, v14

    move-object v14, v5

    move-object v5, v1

    move-object v7, v8

    move v1, v10

    move-object/from16 v10, v22

    move-object/from16 v155, v40

    move-object/from16 v11, v120

    move-object/from16 v151, v124

    move-object/from16 v152, v125

    move-object/from16 v153, v126

    move-object/from16 v154, v127

    move v8, v3

    move-object v3, v12

    move-object/from16 v12, v20

    goto/16 :goto_146

    :catch_91
    move-object/from16 v50, v2

    move-object/from16 v126, v14

    move-object/from16 v1, v17

    move-object/from16 v22, v20

    move-object/from16 v5, v36

    move-object/from16 v7, v45

    move-object/from16 v23, v47

    move-object/from16 v120, v49

    move-object/from16 v40, v111

    const/4 v12, 0x0

    :goto_9c
    const/16 v37, 0x0

    :goto_9d
    move-object/from16 v14, p1

    move-object/from16 v49, v9

    move-object/from16 v20, v13

    move-object/from16 v13, v18

    :goto_9e
    move-object v3, v7

    move-object/from16 v143, v12

    move-object/from16 v144, v14

    move-object/from16 v19, v20

    move-object/from16 v21, v22

    move-object/from16 v6, v23

    move-object/from16 v9, v24

    move-object/from16 v0, v25

    move-object/from16 v141, v28

    move-object/from16 v10, v29

    move-object/from16 v8, v32

    move-object/from16 v145, v40

    move-object/from16 v14, v42

    move-object/from16 v7, v49

    move-object/from16 v15, v53

    move-object/from16 v20, v120

    move-object/from16 v142, v126

    const/4 v2, 0x1

    :goto_9f
    const/16 v34, 0x4

    :goto_a0
    move-object/from16 v40, v143

    :goto_a1
    move-object/from16 v22, v13

    move-object/from16 v13, v50

    move-object/from16 v12, v52

    goto/16 :goto_12b

    :catch_92
    move-exception v0

    move-object/from16 v50, v2

    move-object v2, v11

    move-object/from16 v126, v14

    move-object/from16 v1, v17

    move-object/from16 v22, v20

    move-object/from16 v112, v26

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v6, v29

    move-object/from16 v8, v30

    move-object/from16 v15, v32

    move-object/from16 v5, v36

    move-object/from16 v7, v45

    move-object/from16 v23, v47

    move-object/from16 v120, v49

    move-object/from16 v127, v53

    move-object/from16 v40, v111

    const/4 v3, 0x1

    const/4 v10, 0x4

    const/4 v12, 0x0

    :goto_a2
    const/16 v37, 0x0

    :goto_a3
    move-object/from16 v14, p1

    move-object/from16 v49, v9

    move-object/from16 v20, v13

    move-object/from16 v13, v18

    move-object/from16 v9, v31

    if-eqz v16, :cond_30

    .line 314
    :try_start_ad
    new-instance v11, Ljava/lang/IllegalStateException;
    :try_end_ad
    .catch Ljava/util/concurrent/CancellationException; {:try_start_ad .. :try_end_ad} :catch_93
    .catch Ljava/lang/Exception; {:try_start_ad .. :try_end_ad} :catch_94
    .catchall {:try_start_ad .. :try_end_ad} :catchall_35

    .line 315
    :try_start_ae
    invoke-virtual {v0}, Ljava/lang/Exception;->getMessage()Ljava/lang/String;

    move-result-object v10

    new-instance v12, Ljava/lang/StringBuilder;

    move-object/from16 v3, v21

    invoke-direct {v12, v3}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v12, v10}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v3

    invoke-virtual {v3}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v3

    .line 316
    check-cast v0, Ljava/lang/Throwable;

    .line 314
    invoke-direct {v11, v3, v0}, Ljava/lang/IllegalStateException;-><init>(Ljava/lang/String;Ljava/lang/Throwable;)V

    throw v11

    :catch_93
    move-object v11, v2

    move-object v3, v7

    move-object/from16 v30, v8

    move-object/from16 v31, v9

    move/from16 v34, v10

    move-object/from16 v144, v14

    move-object v8, v15

    move-object/from16 v19, v20

    move-object/from16 v21, v22

    move-object/from16 v9, v24

    move-object/from16 v0, v25

    move-object/from16 v145, v40

    move-object/from16 v14, v42

    move-object/from16 v7, v49

    move-object/from16 v12, v52

    move-object/from16 v20, v120

    move-object/from16 v27, v124

    move-object/from16 v141, v125

    move-object/from16 v142, v126

    move-object/from16 v15, v127

    const/4 v2, 0x1

    const/16 v40, 0x0

    const/16 v90, 0x1

    const/16 v143, 0x0

    move-object v10, v6

    move-object/from16 v22, v13

    move-object/from16 v6, v23

    goto/16 :goto_b8

    .line 319
    :cond_30
    throw v0
    :try_end_ae
    .catch Ljava/util/concurrent/CancellationException; {:try_start_ae .. :try_end_ae} :catch_95
    .catch Ljava/lang/Exception; {:try_start_ae .. :try_end_ae} :catch_94
    .catchall {:try_start_ae .. :try_end_ae} :catchall_35

    :catchall_35
    move-exception v0

    goto/16 :goto_ad

    :catch_94
    move-exception v0

    move-object v3, v5

    move-object v5, v4

    move-object v4, v3

    move-object/from16 v16, v0

    move-object v3, v1

    move-object/from16 v29, v6

    move-object/from16 v30, v8

    move-object/from16 v31, v9

    move-object/from16 v129, v14

    move-object/from16 v32, v15

    move-object/from16 v1, v19

    move-object/from16 v8, v23

    move-object/from16 v11, v24

    move-object/from16 v10, v25

    move-object/from16 v130, v40

    move-object/from16 v6, v49

    move-object/from16 v9, v50

    move-object/from16 v12, v52

    const/4 v14, 0x0

    const/16 v34, 0x4

    const/16 v90, 0x1

    goto/16 :goto_b1

    :catch_95
    move-object v11, v2

    move-object v10, v6

    move-object v3, v7

    move-object/from16 v30, v8

    move-object/from16 v31, v9

    move-object/from16 v144, v14

    move-object v8, v15

    move-object/from16 v19, v20

    move-object/from16 v21, v22

    move-object/from16 v6, v23

    move-object/from16 v9, v24

    move-object/from16 v0, v25

    move-object/from16 v145, v40

    move-object/from16 v14, v42

    move-object/from16 v7, v49

    move-object/from16 v12, v52

    move-object/from16 v20, v120

    move-object/from16 v27, v124

    move-object/from16 v141, v125

    move-object/from16 v142, v126

    move-object/from16 v15, v127

    const/4 v2, 0x1

    const/16 v34, 0x4

    const/16 v40, 0x0

    const/16 v90, 0x1

    goto/16 :goto_b7

    :catchall_36
    move-exception v0

    move-object v2, v11

    goto :goto_a4

    :catch_96
    move-exception v0

    move-object/from16 v50, v2

    move-object v2, v11

    move-object/from16 v126, v14

    move-object/from16 v1, v17

    move-object/from16 v22, v20

    move-object/from16 v112, v26

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v6, v29

    move-object/from16 v8, v30

    move-object/from16 v15, v32

    move-object/from16 v5, v36

    move-object/from16 v7, v45

    move-object/from16 v23, v47

    move-object/from16 v120, v49

    move-object/from16 v127, v53

    move-object/from16 v40, v111

    const/16 v37, 0x0

    goto/16 :goto_a6

    :catch_97
    move-object/from16 v50, v2

    move-object/from16 v126, v14

    move-object/from16 v1, v17

    move-object/from16 v22, v20

    move-object/from16 v5, v36

    move-object/from16 v7, v45

    move-object/from16 v23, v47

    move-object/from16 v120, v49

    move-object/from16 v40, v111

    const/16 v37, 0x0

    move-object/from16 v14, p1

    move-object/from16 v49, v9

    move-object/from16 v20, v13

    move-object/from16 v13, v18

    goto/16 :goto_b5

    :catchall_37
    move-exception v0

    move-object/from16 v2, p0

    :goto_a4
    move-object/from16 v126, v14

    move-object/from16 v22, v20

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v6, v29

    move-object/from16 v8, v30

    move-object/from16 v9, v31

    move-object/from16 v15, v32

    move-object/from16 v5, v36

    goto/16 :goto_a8

    :catch_98
    move-exception v0

    move-object/from16 v50, v2

    move-object/from16 v126, v14

    move-object/from16 v1, v17

    move-object/from16 v22, v20

    move-object/from16 v112, v26

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v6, v29

    move-object/from16 v8, v30

    move-object/from16 v15, v32

    move-object/from16 v5, v36

    goto :goto_a5

    :catch_99
    move-object/from16 v50, v2

    move-object/from16 v126, v14

    move-object/from16 v1, v17

    move-object/from16 v22, v20

    move-object/from16 v5, v36

    goto/16 :goto_ab

    :catch_9a
    move-exception v0

    move-object/from16 v50, v2

    move-object v5, v12

    move-object/from16 v126, v14

    move-object/from16 v1, v17

    move-object/from16 v22, v20

    move-object/from16 v112, v26

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v6, v29

    move-object/from16 v8, v30

    move-object/from16 v15, v32

    :goto_a5
    move-object/from16 v7, v45

    move-object/from16 v23, v47

    move-object/from16 v120, v49

    move-object/from16 v127, v53

    move-object/from16 v40, v111

    const/16 v37, 0x0

    move-object/from16 v2, p0

    :goto_a6
    move-object/from16 v14, p1

    move-object/from16 v49, v9

    move-object/from16 v20, v13

    move-object/from16 v13, v18

    move-object/from16 v9, v31

    move-object v3, v5

    move-object v5, v4

    move-object v4, v3

    move-object/from16 v16, v0

    move-object v3, v1

    move-object/from16 v129, v14

    move-object/from16 v1, v19

    move-object/from16 v8, v23

    move-object/from16 v11, v24

    goto :goto_a7

    :catch_9b
    move-object/from16 v50, v2

    goto/16 :goto_aa

    :catch_9c
    move-exception v0

    move-object/from16 v50, v2

    move-object/from16 v24, v11

    move-object v5, v12

    move-object/from16 v126, v14

    move-object/from16 v1, v17

    move-object/from16 v22, v20

    move-object/from16 v112, v26

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v6, v29

    move-object/from16 v8, v30

    move-object/from16 v15, v32

    move-object/from16 v7, v45

    move-object/from16 v23, v47

    move-object/from16 v120, v49

    move-object/from16 v127, v53

    move-object/from16 v40, v111

    const/16 v37, 0x0

    move-object/from16 v2, p0

    move-object/from16 v14, p1

    move-object/from16 v49, v9

    move-object/from16 v20, v13

    move-object/from16 v13, v18

    move-object/from16 v9, v31

    move-object v3, v5

    move-object v5, v4

    move-object v4, v3

    move-object/from16 v16, v0

    move-object v3, v1

    move-object/from16 v129, v14

    move-object/from16 v1, v19

    move-object/from16 v8, v23

    :goto_a7
    move-object/from16 v10, v25

    goto/16 :goto_b0

    :catch_9d
    move-object/from16 v50, v2

    goto/16 :goto_a9

    :catch_9e
    move-object/from16 v50, v2

    move-object/from16 v24, v11

    move-object v5, v12

    move-object/from16 v126, v14

    move-object/from16 v1, v17

    move-object/from16 v22, v20

    move-object/from16 v7, v45

    move-object/from16 v23, v47

    move-object/from16 v120, v49

    move-object/from16 v40, v111

    const/16 v37, 0x0

    move-object/from16 v14, p1

    move-object/from16 v49, v9

    move-object/from16 v20, v13

    move-object/from16 v13, v18

    move-object/from16 v11, p0

    move-object v3, v7

    move v2, v10

    move-object/from16 v144, v14

    move-object/from16 v19, v20

    move-object/from16 v21, v22

    move-object/from16 v6, v23

    move-object/from16 v9, v24

    move-object/from16 v0, v25

    move-object/from16 v141, v28

    move-object/from16 v10, v29

    move-object/from16 v8, v32

    move-object/from16 v145, v40

    move-object/from16 v14, v42

    move-object/from16 v7, v49

    move-object/from16 v12, v52

    move-object/from16 v15, v53

    move-object/from16 v20, v120

    move-object/from16 v142, v126

    goto/16 :goto_b6

    :catchall_38
    move-exception v0

    move-object/from16 v2, p0

    move-object v5, v12

    move-object/from16 v126, v14

    move-object/from16 v22, v20

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v6, v29

    move-object/from16 v8, v30

    move-object/from16 v9, v31

    move-object/from16 v15, v32

    :goto_a8
    move-object/from16 v120, v49

    move-object/from16 v127, v53

    move-object/from16 v40, v111

    const/16 v37, 0x0

    move-object/from16 v14, p1

    move-object/from16 v20, v13

    move-object/from16 v13, v18

    goto/16 :goto_ad

    :catch_9f
    move-exception v0

    move-object/from16 v50, v2

    move-object/from16 v25, v10

    move-object/from16 v24, v11

    move-object v5, v12

    move-object/from16 v126, v14

    move-object/from16 v1, v17

    move-object/from16 v22, v20

    move-object/from16 v112, v26

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v6, v29

    move-object/from16 v8, v30

    move-object/from16 v15, v32

    move-object/from16 v7, v45

    move-object/from16 v23, v47

    move-object/from16 v120, v49

    move-object/from16 v127, v53

    move-object/from16 v40, v111

    const/16 v37, 0x0

    move-object/from16 v2, p0

    move-object/from16 v14, p1

    move-object/from16 v49, v9

    move-object/from16 v20, v13

    move-object/from16 v13, v18

    goto/16 :goto_af

    :catch_a0
    move-object/from16 v50, v2

    move-object/from16 v25, v10

    :goto_a9
    move-object/from16 v24, v11

    :goto_aa
    move-object v5, v12

    move-object/from16 v126, v14

    move-object/from16 v1, v17

    move-object/from16 v22, v20

    :goto_ab
    move-object/from16 v7, v45

    move-object/from16 v23, v47

    move-object/from16 v120, v49

    move-object/from16 v40, v111

    const/16 v37, 0x0

    move-object/from16 v14, p1

    move-object/from16 v49, v9

    move-object/from16 v20, v13

    move-object/from16 v13, v18

    goto/16 :goto_b4

    :catchall_39
    move-exception v0

    move-object/from16 v2, p0

    goto :goto_ac

    :catch_a1
    move-exception v0

    move-object/from16 v50, v2

    goto :goto_ae

    :catch_a2
    move-object/from16 v50, v2

    goto/16 :goto_b3

    :catchall_3a
    move-exception v0

    move-object/from16 v2, p0

    move-object/from16 v33, v3

    :goto_ac
    move-object/from16 v22, v5

    move-object v5, v12

    move-object/from16 v20, v13

    move-object/from16 v126, v14

    move-object/from16 v13, v18

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v6, v29

    move-object/from16 v8, v30

    move-object/from16 v9, v31

    move-object/from16 v15, v32

    move-object/from16 v120, v49

    move-object/from16 v127, v53

    move-object/from16 v40, v111

    const/16 v37, 0x0

    move-object/from16 v14, p1

    :goto_ad
    move-object v1, v4

    move-object v4, v0

    move-object v0, v14

    move-object v14, v5

    move-object v5, v1

    move-object v7, v8

    move-object/from16 v12, v20

    move-object/from16 v10, v22

    move-object/from16 v155, v40

    move-object/from16 v11, v120

    move-object/from16 v151, v124

    move-object/from16 v152, v125

    move-object/from16 v153, v126

    move-object/from16 v154, v127

    const/4 v1, 0x4

    const/4 v3, 0x0

    const/4 v8, 0x1

    goto/16 :goto_146

    :catch_a3
    move-exception v0

    move-object/from16 v50, v2

    move-object/from16 v33, v3

    :goto_ae
    move-object/from16 v22, v5

    move-object/from16 v25, v10

    move-object/from16 v24, v11

    move-object v5, v12

    move-object/from16 v20, v13

    move-object/from16 v126, v14

    move-object/from16 v1, v17

    move-object/from16 v13, v18

    move-object/from16 v112, v26

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v6, v29

    move-object/from16 v8, v30

    move-object/from16 v15, v32

    move-object/from16 v7, v45

    move-object/from16 v23, v47

    move-object/from16 v120, v49

    move-object/from16 v127, v53

    move-object/from16 v40, v111

    const/16 v37, 0x0

    move-object/from16 v2, p0

    move-object/from16 v14, p1

    move-object/from16 v49, v9

    :goto_af
    move-object/from16 v9, v31

    move-object v3, v5

    move-object v5, v4

    move-object v4, v3

    move-object/from16 v16, v0

    move-object v3, v1

    move-object/from16 v129, v14

    move-object/from16 v1, v19

    move-object/from16 v8, v23

    :goto_b0
    move-object/from16 v130, v40

    move-object/from16 v6, v49

    move-object/from16 v9, v50

    move-object/from16 v12, v52

    const/4 v14, 0x0

    const/16 v34, 0x4

    :goto_b1
    const/16 v128, 0x0

    move-object v15, v13

    :goto_b2
    move-object/from16 v13, v42

    goto/16 :goto_10d

    :catch_a4
    move-object/from16 v50, v2

    move-object/from16 v33, v3

    :goto_b3
    move-object/from16 v22, v5

    move-object/from16 v25, v10

    move-object/from16 v24, v11

    move-object v5, v12

    move-object/from16 v20, v13

    move-object/from16 v126, v14

    move-object/from16 v1, v17

    move-object/from16 v13, v18

    move-object/from16 v7, v45

    move-object/from16 v23, v47

    move-object/from16 v120, v49

    move-object/from16 v40, v111

    const/16 v37, 0x0

    move-object/from16 v14, p1

    move-object/from16 v49, v9

    :goto_b4
    move-object/from16 v11, p0

    :goto_b5
    move-object v3, v7

    move-object/from16 v144, v14

    move-object/from16 v19, v20

    move-object/from16 v21, v22

    move-object/from16 v6, v23

    move-object/from16 v9, v24

    move-object/from16 v0, v25

    move-object/from16 v141, v28

    move-object/from16 v10, v29

    move-object/from16 v8, v32

    move-object/from16 v145, v40

    move-object/from16 v14, v42

    move-object/from16 v7, v49

    move-object/from16 v12, v52

    move-object/from16 v15, v53

    move-object/from16 v20, v120

    move-object/from16 v142, v126

    const/4 v2, 0x1

    :goto_b6
    const/16 v34, 0x4

    const/16 v40, 0x0

    :goto_b7
    const/16 v143, 0x0

    move-object/from16 v22, v13

    :goto_b8
    move-object/from16 v13, v50

    goto/16 :goto_12b

    :catchall_3b
    move-exception v0

    move v3, v2

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v15, v32

    move-object/from16 v126, v38

    move-object/from16 v127, v53

    const/4 v14, 0x0

    const/16 v34, 0x4

    move-object/from16 v2, p0

    goto/16 :goto_ba

    :catch_a5
    move-exception v0

    move v3, v2

    move-object/from16 v45, v15

    move-object/from16 v112, v26

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v15, v32

    move-object/from16 v126, v38

    move-object/from16 v4, v49

    move-object/from16 v127, v53

    move-object/from16 v50, v87

    move-object/from16 v51, v88

    move-object/from16 v52, v89

    move/from16 v64, v90

    move-object/from16 v57, v92

    const/4 v14, 0x0

    const/16 v34, 0x4

    move-object/from16 v2, p0

    goto/16 :goto_b9

    :catch_a6
    move-object/from16 v49, v1

    move-object/from16 v45, v15

    move-object/from16 v50, v87

    move-object/from16 v51, v88

    move-object/from16 v52, v89

    move/from16 v64, v90

    move-object/from16 v57, v92

    const/4 v14, 0x0

    const/16 v34, 0x4

    move/from16 v37, v2

    move-object v4, v5

    move-object v5, v6

    move-object/from16 v19, v7

    move-object/from16 v20, v8

    move-object/from16 v21, v9

    move-object/from16 v22, v10

    move-object/from16 v144, v11

    move-object/from16 v33, v12

    move-object/from16 v44, v13

    move-object/from16 v40, v14

    move-object/from16 v143, v40

    move-object/from16 v145, v143

    move-object/from16 v141, v28

    move-object/from16 v10, v29

    move-object/from16 v8, v32

    move-object/from16 v142, v38

    move-object/from16 v9, v41

    move-object/from16 v0, v42

    move-object/from16 v3, v45

    move-object/from16 v6, v47

    move-object/from16 v7, v49

    move-object/from16 v13, v50

    move-object/from16 v14, v51

    move-object/from16 v12, v52

    move-object/from16 v15, v53

    move-object/from16 v1, v57

    const/4 v2, 0x1

    goto/16 :goto_bd

    :catch_a7
    move-exception v0

    move-object/from16 v2, p0

    move-object/from16 v45, v15

    move-object/from16 v112, v26

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v15, v32

    move-object/from16 v126, v38

    move-object/from16 v4, v49

    move-object/from16 v127, v53

    move-object/from16 v50, v87

    move-object/from16 v51, v88

    move-object/from16 v52, v89

    move/from16 v64, v90

    move-object/from16 v57, v92

    const/4 v3, 0x0

    const/4 v14, 0x0

    const/16 v34, 0x4

    :goto_b9
    move-object/from16 v49, v1

    goto :goto_bb

    :catchall_3c
    move-exception v0

    move-object/from16 v2, p0

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v15, v32

    move-object/from16 v126, v38

    move-object/from16 v127, v53

    const/4 v3, 0x0

    const/4 v14, 0x0

    const/16 v34, 0x4

    :goto_ba
    move-object v4, v0

    move/from16 v37, v3

    move-object v0, v11

    move-object/from16 v33, v12

    move-object/from16 v44, v13

    move-object v3, v14

    move-object/from16 v155, v3

    move/from16 v1, v34

    move-object/from16 v151, v124

    move-object/from16 v152, v125

    move-object/from16 v153, v126

    move-object/from16 v154, v127

    goto/16 :goto_1e

    :catch_a8
    move-exception v0

    move-object/from16 v2, p0

    move-object/from16 v49, v1

    move-object v4, v3

    move-object/from16 v45, v15

    move-object/from16 v112, v26

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v15, v32

    move-object/from16 v126, v38

    move-object/from16 v127, v53

    move-object/from16 v50, v87

    move-object/from16 v51, v88

    move-object/from16 v52, v89

    move/from16 v64, v90

    move-object/from16 v57, v92

    const/4 v3, 0x0

    const/4 v14, 0x0

    const/16 v34, 0x4

    :goto_bb
    move-object/from16 v16, v0

    move/from16 v37, v3

    move-object v1, v4

    move-object v4, v6

    move-object/from16 v20, v7

    move-object/from16 v120, v8

    move-object/from16 v22, v9

    move-object/from16 v129, v11

    move-object/from16 v33, v12

    move-object/from16 v44, v13

    move-object/from16 v128, v14

    move-object/from16 v130, v128

    move-object/from16 v11, v41

    move-object/from16 v7, v45

    move-object/from16 v8, v47

    move-object/from16 v6, v49

    move-object/from16 v9, v50

    move-object/from16 v13, v51

    move-object/from16 v12, v52

    move-object/from16 v3, v57

    :goto_bc
    move-object v15, v10

    move-object/from16 v10, v42

    goto/16 :goto_10d

    :catch_a9
    move-object/from16 v49, v1

    move-object/from16 v45, v15

    move-object/from16 v50, v87

    move-object/from16 v51, v88

    move-object/from16 v52, v89

    move/from16 v64, v90

    move-object/from16 v57, v92

    const/4 v14, 0x0

    const/16 v34, 0x4

    move-object v4, v5

    move-object v5, v6

    move-object/from16 v19, v7

    move-object/from16 v20, v8

    move-object/from16 v21, v9

    move-object/from16 v22, v10

    move-object/from16 v144, v11

    move-object/from16 v33, v12

    move-object/from16 v44, v13

    move-object/from16 v40, v14

    move-object/from16 v143, v40

    move-object/from16 v145, v143

    move-object/from16 v141, v28

    move-object/from16 v10, v29

    move-object/from16 v8, v32

    move-object/from16 v142, v38

    move-object/from16 v9, v41

    move-object/from16 v0, v42

    move-object/from16 v3, v45

    move-object/from16 v6, v47

    move-object/from16 v7, v49

    move-object/from16 v13, v50

    move-object/from16 v14, v51

    move-object/from16 v12, v52

    move-object/from16 v15, v53

    move-object/from16 v1, v57

    const/4 v2, 0x1

    const/16 v37, 0x0

    :goto_bd
    move-object/from16 v11, p0

    goto/16 :goto_12b

    :catch_aa
    move-exception v0

    move-object/from16 v2, p0

    goto :goto_be

    :catch_ab
    move-exception v0

    move-object/from16 v2, p0

    move/from16 v61, v1

    :goto_be
    move-object/from16 v112, v26

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v126, v38

    move-object/from16 v127, v53

    goto/16 :goto_c7

    :catch_ac
    move/from16 v61, v1

    goto/16 :goto_d1

    :catch_ad
    move-exception v0

    move-object/from16 v2, p0

    goto :goto_bf

    :catch_ae
    move/from16 v61, v81

    goto/16 :goto_d1

    :catch_af
    move-exception v0

    move-object/from16 v2, p0

    move-object/from16 v52, v1

    :goto_bf
    move-object/from16 v112, v26

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v126, v38

    move-object/from16 v127, v53

    move/from16 v61, v81

    goto/16 :goto_c7

    :catch_b0
    move-object/from16 v52, v1

    move/from16 v61, v81

    const/4 v14, 0x0

    const/16 v34, 0x4

    move-object/from16 v11, p0

    move-object/from16 v144, v4

    move-object v4, v5

    move-object v5, v6

    move-object/from16 v19, v7

    move-object/from16 v21, v9

    move-object/from16 v33, v12

    move-object/from16 v44, v13

    move-object/from16 v40, v14

    move-object/from16 v143, v40

    move-object/from16 v145, v143

    move-object/from16 v22, v15

    move-object/from16 v7, v18

    move-object/from16 v6, v20

    move-object/from16 v141, v28

    move-object/from16 v10, v29

    move-object/from16 v142, v38

    move-object/from16 v3, v45

    move-object/from16 v13, v47

    move-object/from16 v0, v48

    move-object/from16 v9, v49

    move-object/from16 v14, v50

    move-object/from16 v12, v51

    goto/16 :goto_d2

    :catch_b1
    move-exception v0

    move-object/from16 v2, p0

    move-object/from16 v51, v1

    move-object/from16 v112, v26

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v126, v38

    move-object/from16 v127, v53

    goto/16 :goto_c6

    :catch_b2
    move-object/from16 v51, v1

    goto/16 :goto_d0

    :catch_b3
    move-exception v0

    move-object/from16 v2, p0

    move-object/from16 v50, v1

    move-object/from16 v112, v26

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v126, v38

    move-object/from16 v127, v53

    goto/16 :goto_c5

    :catch_b4
    move-object/from16 v50, v1

    goto/16 :goto_cf

    :catch_b5
    move-exception v0

    move-object/from16 v2, p0

    move-object/from16 v49, v1

    move-object/from16 v112, v26

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v126, v38

    move-object/from16 v127, v53

    goto/16 :goto_c4

    :catch_b6
    move-object/from16 v49, v1

    goto/16 :goto_ce

    :catch_b7
    move-exception v0

    move-object/from16 v2, p0

    move-object/from16 v48, v1

    move-object/from16 v112, v26

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v126, v38

    move-object/from16 v127, v53

    goto/16 :goto_c3

    :catch_b8
    move-object/from16 v48, v1

    goto/16 :goto_cd

    :catch_b9
    move-exception v0

    move-object/from16 v2, p0

    move-object/from16 v47, v1

    move-object/from16 v112, v26

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v126, v38

    move-object/from16 v127, v53

    goto/16 :goto_c2

    :catch_ba
    move-object/from16 v47, v1

    goto/16 :goto_cc

    :catch_bb
    move-exception v0

    move-object/from16 v2, p0

    move-object/from16 v20, v1

    goto/16 :goto_c1

    :catch_bc
    move-object/from16 v20, v1

    goto/16 :goto_cb

    :catch_bd
    move-exception v0

    move-object/from16 v2, p0

    move-object/from16 v42, v1

    move-object/from16 v112, v26

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v126, v38

    move-object/from16 v127, v53

    move-object/from16 v47, v76

    move-object/from16 v48, v77

    move-object/from16 v49, v78

    move-object/from16 v50, v79

    move-object/from16 v51, v80

    move/from16 v61, v81

    move-object/from16 v52, v82

    const/4 v3, 0x0

    const/4 v14, 0x0

    const/16 v34, 0x4

    move-object/from16 v16, v0

    move/from16 v37, v3

    move-object/from16 v129, v4

    move-object v4, v6

    move-object/from16 v120, v8

    move-object/from16 v22, v9

    move-object/from16 v33, v12

    move-object/from16 v44, v13

    move-object/from16 v128, v14

    move-object/from16 v130, v128

    move-object/from16 v6, v18

    move-object/from16 v8, v20

    goto/16 :goto_c9

    :catch_be
    move-exception v0

    move-object/from16 v2, p0

    move-object/from16 v45, v1

    goto :goto_c1

    :catch_bf
    move-object/from16 v45, v1

    goto/16 :goto_cb

    :catch_c0
    move-exception v0

    move-object/from16 v2, p0

    goto :goto_c1

    :catch_c1
    move-exception v0

    move-object/from16 v2, p0

    move-object/from16 v18, v1

    goto :goto_c1

    :catch_c2
    move-object/from16 v18, v1

    goto/16 :goto_cb

    :catch_c3
    move-exception v0

    move-object/from16 v2, p0

    move-object/from16 v18, v1

    goto :goto_c0

    :catch_c4
    move-exception v0

    move-object/from16 v2, p0

    move-object/from16 v18, v1

    move-object/from16 v42, v3

    :goto_c0
    move-object/from16 v45, v10

    :goto_c1
    move-object/from16 v112, v26

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v126, v38

    move-object/from16 v127, v53

    move-object/from16 v47, v76

    :goto_c2
    move-object/from16 v48, v77

    :goto_c3
    move-object/from16 v49, v78

    :goto_c4
    move-object/from16 v50, v79

    :goto_c5
    move-object/from16 v51, v80

    :goto_c6
    move/from16 v61, v81

    move-object/from16 v52, v82

    :goto_c7
    const/4 v3, 0x0

    const/4 v14, 0x0

    const/16 v34, 0x4

    goto :goto_c8

    :catch_c5
    move-object/from16 v18, v1

    goto/16 :goto_ca

    :catchall_3d
    move-exception v0

    move-object/from16 v2, p0

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v126, v38

    move-object/from16 v127, v53

    const/4 v3, 0x0

    const/4 v14, 0x0

    const/16 v34, 0x4

    move-object v1, v4

    move-object v4, v0

    move-object v0, v1

    move/from16 v37, v3

    move-object v11, v8

    move-object v10, v9

    move-object/from16 v33, v12

    move-object/from16 v44, v13

    move-object v3, v14

    goto/16 :goto_f1

    :catch_c6
    move-exception v0

    move-object/from16 v18, v1

    move-object/from16 v20, v2

    move-object/from16 v42, v3

    move-object/from16 v45, v10

    move-object/from16 v112, v26

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v126, v38

    move-object/from16 v127, v53

    move-object/from16 v47, v76

    move-object/from16 v48, v77

    move-object/from16 v49, v78

    move-object/from16 v50, v79

    move-object/from16 v51, v80

    move/from16 v61, v81

    move-object/from16 v52, v82

    const/4 v3, 0x0

    const/4 v14, 0x0

    const/16 v34, 0x4

    move-object/from16 v2, p0

    :goto_c8
    move-object/from16 v16, v0

    move/from16 v37, v3

    move-object/from16 v129, v4

    move-object v4, v6

    move-object/from16 v120, v8

    move-object/from16 v22, v9

    move-object/from16 v33, v12

    move-object/from16 v44, v13

    move-object/from16 v128, v14

    move-object/from16 v130, v128

    move-object/from16 v6, v18

    move-object/from16 v8, v20

    move-object/from16 v1, v42

    :goto_c9
    move-object/from16 v9, v47

    move-object/from16 v10, v48

    move-object/from16 v11, v49

    move-object/from16 v13, v50

    move-object/from16 v12, v51

    move-object/from16 v3, v52

    move/from16 v90, v61

    move-object/from16 v20, v7

    move-object/from16 v7, v45

    goto/16 :goto_10d

    :catch_c7
    move-object/from16 v18, v1

    move-object/from16 v20, v2

    :goto_ca
    move-object/from16 v45, v10

    :catch_c8
    :goto_cb
    move-object/from16 v47, v76

    :goto_cc
    move-object/from16 v48, v77

    :goto_cd
    move-object/from16 v49, v78

    :goto_ce
    move-object/from16 v50, v79

    :goto_cf
    move-object/from16 v51, v80

    :goto_d0
    move/from16 v61, v81

    move-object/from16 v52, v82

    :catch_c9
    :goto_d1
    const/4 v14, 0x0

    const/16 v34, 0x4

    move-object/from16 v11, p0

    move-object/from16 v144, v4

    move-object v4, v5

    move-object v5, v6

    move-object/from16 v19, v7

    move-object/from16 v21, v9

    move-object/from16 v33, v12

    move-object/from16 v44, v13

    move-object/from16 v40, v14

    move-object/from16 v143, v40

    move-object/from16 v145, v143

    move-object/from16 v22, v15

    move-object/from16 v7, v18

    move-object/from16 v6, v20

    move-object/from16 v141, v28

    move-object/from16 v10, v29

    move-object/from16 v142, v38

    move-object/from16 v3, v45

    move-object/from16 v13, v47

    move-object/from16 v0, v48

    move-object/from16 v9, v49

    move-object/from16 v14, v50

    move-object/from16 v12, v51

    move-object/from16 v1, v52

    :goto_d2
    move-object/from16 v15, v53

    move/from16 v90, v61

    const/4 v2, 0x1

    const/16 v37, 0x0

    goto/16 :goto_fa

    :catchall_3e
    move-exception v0

    move-object/from16 v2, p0

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v126, v38

    goto/16 :goto_d7

    :catch_ca
    move-exception v0

    move-object/from16 v2, p0

    move-object/from16 v112, v26

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v126, v38

    move-object/from16 v127, v53

    goto/16 :goto_d8

    :catch_cb
    move-exception v0

    goto :goto_d3

    :catch_cc
    move-exception v0

    move/from16 v55, v1

    :goto_d3
    move-object/from16 p1, v2

    move-object/from16 v112, v26

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v126, v38

    move-object/from16 v127, v53

    goto/16 :goto_e2

    :catch_cd
    move/from16 v55, v1

    :catch_ce
    move-object/from16 p1, v2

    goto/16 :goto_eb

    :catch_cf
    move-exception v0

    goto :goto_d4

    :catch_d0
    move-object/from16 p1, v2

    goto/16 :goto_ea

    :catch_d1
    move-exception v0

    move-object/from16 v50, v1

    :goto_d4
    move-object/from16 p1, v2

    move-object/from16 v112, v26

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v126, v38

    move-object/from16 v127, v53

    goto/16 :goto_e1

    :catch_d2
    move-object/from16 v50, v1

    move-object/from16 p1, v2

    move/from16 v55, v66

    const/4 v14, 0x0

    const/16 v34, 0x4

    move-object/from16 v0, v19

    move-object/from16 v19, v7

    move-object v7, v0

    move-object/from16 v11, p0

    move-object/from16 v144, p1

    move-object/from16 v21, v9

    move-object/from16 v33, v12

    move-object/from16 v44, v13

    move-object/from16 v40, v14

    move-object/from16 v143, v40

    move-object/from16 v145, v143

    move-object/from16 v22, v15

    move-object/from16 v141, v28

    move-object/from16 v10, v29

    move-object/from16 v142, v38

    move-object/from16 v13, v41

    move-object/from16 v0, v42

    move-object/from16 v9, v45

    move-object/from16 v3, v47

    move-object/from16 v12, v49

    goto/16 :goto_f9

    :catch_d3
    move-exception v0

    move-object/from16 v49, v1

    move-object/from16 p1, v2

    move-object/from16 v112, v26

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v126, v38

    move-object/from16 v127, v53

    goto/16 :goto_e0

    :catch_d4
    move-object/from16 v49, v1

    move-object/from16 p1, v2

    goto/16 :goto_e9

    :catch_d5
    move-exception v0

    move-object/from16 v45, v1

    move-object/from16 p1, v2

    move-object/from16 v112, v26

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v126, v38

    move-object/from16 v127, v53

    goto/16 :goto_df

    :catch_d6
    move-object/from16 v45, v1

    move-object/from16 p1, v2

    goto/16 :goto_e8

    :catch_d7
    move-exception v0

    move-object/from16 v42, v1

    move-object/from16 p1, v2

    move-object/from16 v112, v26

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v126, v38

    move-object/from16 v127, v53

    goto/16 :goto_de

    :catch_d8
    move-object/from16 v42, v1

    move-object/from16 p1, v2

    goto/16 :goto_e7

    :catch_d9
    move-exception v0

    move-object/from16 v41, v1

    move-object/from16 p1, v2

    move-object/from16 v112, v26

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v126, v38

    move-object/from16 v127, v53

    goto/16 :goto_dd

    :catch_da
    move-object/from16 v41, v1

    move-object/from16 p1, v2

    goto/16 :goto_e6

    :catch_db
    move-exception v0

    move-object/from16 v20, v1

    move-object/from16 p1, v2

    move-object/from16 v112, v26

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v126, v38

    goto/16 :goto_dc

    :catch_dc
    move-object/from16 v20, v1

    move-object/from16 p1, v2

    goto/16 :goto_e5

    :catch_dd
    move-exception v0

    move-object/from16 v48, v1

    move-object/from16 p1, v2

    move-object/from16 v112, v26

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v126, v38

    move-object/from16 v20, v45

    move-object/from16 v127, v53

    move-object/from16 v41, v59

    move-object/from16 v42, v60

    move-object/from16 v45, v61

    move-object/from16 v49, v62

    move-object/from16 v50, v64

    move/from16 v55, v66

    const/4 v3, 0x0

    const/4 v14, 0x0

    const/16 v34, 0x4

    move-object/from16 v2, p0

    move-object/from16 v129, p1

    move-object/from16 v16, v0

    move/from16 v37, v3

    move-object/from16 v120, v8

    move-object/from16 v22, v9

    move-object/from16 v33, v12

    move-object/from16 v44, v13

    move-object/from16 v128, v14

    move-object/from16 v130, v128

    move-object/from16 v8, v20

    move-object/from16 v9, v41

    move-object/from16 v10, v42

    move-object/from16 v11, v45

    goto/16 :goto_f6

    :catch_de
    move-exception v0

    move-object/from16 v47, v1

    goto :goto_d5

    :catch_df
    move-object/from16 v47, v1

    goto :goto_d6

    :catch_e0
    move-exception v0

    goto :goto_d5

    :catchall_3f
    move-exception v0

    move-object/from16 p1, v2

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v126, v38

    goto/16 :goto_d9

    :catch_e1
    move-exception v0

    move-object/from16 v19, v1

    :goto_d5
    move-object/from16 p1, v2

    move-object/from16 v112, v26

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v126, v38

    move-object/from16 v20, v45

    goto/16 :goto_dc

    :catch_e2
    move-object/from16 v19, v1

    :catch_e3
    :goto_d6
    move-object/from16 p1, v2

    move-object/from16 v20, v45

    goto/16 :goto_e5

    :catchall_40
    move-exception v0

    move-object/from16 p1, v2

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v126, v38

    move-object/from16 v13, v49

    goto/16 :goto_d9

    :catch_e4
    move-exception v0

    move-object/from16 v19, v1

    move-object/from16 p1, v2

    move-object/from16 v112, v26

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v126, v38

    move-object/from16 v20, v45

    move-object/from16 v13, v49

    goto/16 :goto_dc

    :catch_e5
    move-object/from16 v19, v1

    move-object/from16 p1, v2

    move-object/from16 v20, v45

    move-object/from16 v13, v49

    goto/16 :goto_e5

    :catchall_41
    move-exception v0

    move-object/from16 p1, v2

    move-object v14, v12

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v126, v38

    move-object/from16 v13, v49

    move-object/from16 v12, v50

    move-object/from16 v127, v53

    const/4 v3, 0x0

    goto/16 :goto_da

    :catch_e6
    move-exception v0

    move-object/from16 v19, v1

    move-object/from16 p1, v2

    move-object v14, v12

    move-object/from16 v112, v26

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v126, v38

    move-object/from16 v20, v45

    move-object/from16 v13, v49

    move-object/from16 v12, v50

    move-object/from16 v127, v53

    move-object/from16 v41, v59

    move-object/from16 v42, v60

    move-object/from16 v45, v61

    move-object/from16 v49, v62

    move-object/from16 v50, v64

    move/from16 v55, v66

    const/4 v3, 0x0

    goto/16 :goto_e3

    :catch_e7
    move-object/from16 v19, v1

    move-object/from16 p1, v2

    move-object v14, v12

    move-object/from16 v20, v45

    move-object/from16 v13, v49

    move-object/from16 v12, v50

    move-object/from16 v41, v59

    move-object/from16 v42, v60

    move-object/from16 v45, v61

    move-object/from16 v49, v62

    move-object/from16 v50, v64

    move/from16 v55, v66

    goto/16 :goto_ec

    :catchall_42
    move-exception v0

    move-object/from16 p1, v2

    move-object v2, v10

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v126, v38

    move-object/from16 v13, v49

    move-object/from16 v12, v50

    :goto_d7
    move-object/from16 v127, v53

    const/4 v3, 0x0

    const/4 v14, 0x0

    const/16 v34, 0x4

    goto/16 :goto_db

    :catch_e8
    move-exception v0

    move-object/from16 v19, v1

    move-object/from16 p1, v2

    move-object v2, v10

    move-object/from16 v112, v26

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v126, v38

    move-object/from16 v20, v45

    move-object/from16 v13, v49

    move-object/from16 v12, v50

    move-object/from16 v127, v53

    move-object/from16 v41, v59

    move-object/from16 v42, v60

    move-object/from16 v45, v61

    move-object/from16 v49, v62

    move-object/from16 v50, v64

    move/from16 v55, v66

    :goto_d8
    const/4 v3, 0x0

    const/4 v14, 0x0

    const/16 v34, 0x4

    goto/16 :goto_e4

    :catch_e9
    move-object/from16 v19, v1

    move-object/from16 p1, v2

    move-object/from16 v20, v45

    move-object/from16 v13, v49

    move-object/from16 v12, v50

    move-object/from16 v41, v59

    move-object/from16 v42, v60

    move-object/from16 v45, v61

    move-object/from16 v49, v62

    move-object/from16 v50, v64

    move/from16 v55, v66

    const/4 v14, 0x0

    const/16 v34, 0x4

    move-object/from16 v0, v19

    move-object/from16 v19, v7

    move-object v7, v0

    move-object/from16 v144, p1

    move-object/from16 v21, v9

    move-object v11, v10

    goto/16 :goto_ed

    :catchall_43
    move-exception v0

    move-object/from16 p1, v2

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v126, v38

    move-object/from16 v13, v49

    move-object/from16 v12, v50

    :goto_d9
    move-object/from16 v127, v53

    const/4 v3, 0x0

    const/4 v14, 0x0

    :goto_da
    const/16 v34, 0x4

    move-object/from16 v2, p0

    :goto_db
    move-object v4, v0

    move/from16 v37, v3

    move-object v11, v8

    move-object v10, v9

    move-object/from16 v33, v12

    move-object/from16 v44, v13

    move-object v3, v14

    move-object/from16 v155, v3

    move-object v13, v15

    move-object/from16 v9, v31

    move-object/from16 v15, v32

    move/from16 v1, v34

    move-object/from16 v151, v124

    move-object/from16 v152, v125

    move-object/from16 v153, v126

    move-object/from16 v154, v127

    const/4 v8, 0x1

    move-object/from16 v0, p1

    goto/16 :goto_f2

    :catch_ea
    move-exception v0

    move-object/from16 v19, v1

    move-object/from16 p1, v2

    move-object/from16 v112, v26

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v126, v38

    move-object/from16 v20, v45

    move-object/from16 v13, v49

    move-object/from16 v12, v50

    :goto_dc
    move-object/from16 v127, v53

    move-object/from16 v41, v59

    :goto_dd
    move-object/from16 v42, v60

    :goto_de
    move-object/from16 v45, v61

    :goto_df
    move-object/from16 v49, v62

    :goto_e0
    move-object/from16 v50, v64

    :goto_e1
    move/from16 v55, v66

    :goto_e2
    const/4 v3, 0x0

    const/4 v14, 0x0

    :goto_e3
    const/16 v34, 0x4

    move-object/from16 v2, p0

    :goto_e4
    move-object/from16 v129, p1

    move-object/from16 v16, v0

    move/from16 v37, v3

    move-object/from16 v120, v8

    move-object/from16 v22, v9

    move-object/from16 v33, v12

    move-object/from16 v44, v13

    move-object/from16 v128, v14

    move-object/from16 v130, v128

    goto/16 :goto_f5

    :catch_eb
    move-object/from16 v19, v1

    move-object/from16 p1, v2

    move-object/from16 v20, v45

    move-object/from16 v13, v49

    move-object/from16 v12, v50

    :goto_e5
    move-object/from16 v41, v59

    :goto_e6
    move-object/from16 v42, v60

    :goto_e7
    move-object/from16 v45, v61

    :goto_e8
    move-object/from16 v49, v62

    :goto_e9
    move-object/from16 v50, v64

    :goto_ea
    move/from16 v55, v66

    :catch_ec
    :goto_eb
    const/4 v14, 0x0

    :goto_ec
    const/16 v34, 0x4

    move-object/from16 v0, v19

    move-object/from16 v19, v7

    move-object v7, v0

    move-object/from16 v11, p0

    move-object/from16 v144, p1

    move-object/from16 v21, v9

    :goto_ed
    move-object/from16 v33, v12

    move-object/from16 v44, v13

    move-object/from16 v40, v14

    move-object/from16 v143, v40

    move-object/from16 v145, v143

    goto/16 :goto_f8

    :catchall_44
    move-exception v0

    move-object/from16 v2, p0

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v126, v38

    move-object/from16 v13, v49

    move-object/from16 v12, v50

    goto/16 :goto_f0

    :catch_ed
    move-exception v0

    move-object/from16 v2, p0

    move-object/from16 v19, v1

    move-object/from16 v112, v26

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v126, v38

    move-object/from16 v20, v45

    move-object/from16 v13, v49

    move-object/from16 v12, v50

    goto :goto_ee

    :catch_ee
    move-object/from16 v19, v1

    move-object/from16 v20, v45

    move-object/from16 v13, v49

    move-object/from16 v12, v50

    goto/16 :goto_ef

    :catchall_45
    move-exception v0

    move-object/from16 v2, p0

    move-object v12, v10

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v126, v38

    move-object/from16 v13, v49

    goto/16 :goto_f0

    :catch_ef
    move-exception v0

    move-object/from16 v2, p0

    move-object/from16 v19, v1

    move-object v12, v10

    move-object/from16 v112, v26

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v126, v38

    move-object/from16 v20, v45

    move-object/from16 v13, v49

    goto :goto_ee

    :catch_f0
    move-object/from16 v19, v1

    move-object v12, v10

    move-object/from16 v20, v45

    move-object/from16 v13, v49

    goto :goto_ef

    :catch_f1
    move-exception v0

    move-object/from16 v2, p0

    move-object/from16 v19, v1

    move-object v12, v10

    move-object/from16 v112, v26

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v126, v38

    move-object/from16 v20, v45

    :goto_ee
    move-object/from16 v127, v53

    move-object/from16 v41, v59

    move-object/from16 v42, v60

    move-object/from16 v45, v61

    move-object/from16 v49, v62

    move-object/from16 v50, v64

    move/from16 v55, v66

    const/4 v3, 0x0

    const/4 v14, 0x0

    const/16 v34, 0x4

    goto/16 :goto_f4

    :catch_f2
    move-object/from16 v19, v1

    move-object v12, v10

    move-object/from16 v20, v45

    :goto_ef
    move-object/from16 v41, v59

    move-object/from16 v42, v60

    move-object/from16 v45, v61

    move-object/from16 v49, v62

    move-object/from16 v50, v64

    move/from16 v55, v66

    const/4 v14, 0x0

    const/16 v34, 0x4

    goto/16 :goto_f7

    :catch_f3
    move-exception v0

    move-object/from16 v2, p0

    move-object/from16 v19, v1

    move-object/from16 v47, v12

    move-object/from16 v112, v26

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v126, v38

    move-object/from16 v20, v45

    move-object/from16 v127, v53

    move-object/from16 v41, v59

    move-object/from16 v42, v60

    move-object/from16 v45, v61

    move-object/from16 v49, v62

    move-object/from16 v50, v64

    move/from16 v55, v66

    const/4 v3, 0x0

    const/4 v14, 0x0

    const/16 v34, 0x4

    goto/16 :goto_f3

    :catchall_46
    move-exception v0

    move-object/from16 v2, p0

    move-object v12, v10

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v126, v38

    :goto_f0
    move-object/from16 v127, v53

    const/4 v3, 0x0

    const/4 v14, 0x0

    const/16 v34, 0x4

    move-object v4, v0

    move/from16 v37, v3

    move-object v11, v8

    move-object v10, v9

    move-object/from16 v33, v12

    move-object/from16 v44, v13

    move-object v0, v14

    move-object v3, v0

    :goto_f1
    move-object/from16 v155, v3

    move-object v13, v15

    move-object/from16 v9, v31

    move-object/from16 v15, v32

    move/from16 v1, v34

    move-object/from16 v151, v124

    move-object/from16 v152, v125

    move-object/from16 v153, v126

    move-object/from16 v154, v127

    const/4 v8, 0x1

    :goto_f2
    move-object v14, v6

    move-object v12, v7

    move-object/from16 v6, v29

    move-object/from16 v7, v30

    goto/16 :goto_146

    :catch_f4
    move-exception v0

    move-object/from16 v19, v1

    move-object/from16 v48, v2

    move-object/from16 v47, v12

    move-object/from16 v112, v26

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v126, v38

    move-object/from16 v20, v45

    move-object/from16 v127, v53

    move-object/from16 v41, v59

    move-object/from16 v42, v60

    move-object/from16 v45, v61

    move-object/from16 v49, v62

    move-object/from16 v50, v64

    move/from16 v55, v66

    const/4 v3, 0x0

    const/4 v14, 0x0

    const/16 v34, 0x4

    move-object/from16 v2, p0

    :goto_f3
    move-object v12, v10

    :goto_f4
    move-object/from16 v16, v0

    move/from16 v37, v3

    move-object/from16 v120, v8

    move-object/from16 v22, v9

    move-object/from16 v33, v12

    move-object/from16 v44, v13

    move-object/from16 v128, v14

    move-object/from16 v129, v128

    move-object/from16 v130, v129

    :goto_f5
    move-object/from16 v8, v20

    move-object/from16 v9, v41

    move-object/from16 v10, v42

    move-object/from16 v11, v45

    move-object/from16 v1, v48

    :goto_f6
    move-object/from16 v12, v49

    move-object/from16 v3, v50

    move/from16 v90, v55

    move-object v13, v4

    move-object v4, v6

    move-object/from16 v20, v7

    move-object/from16 v6, v19

    move-object/from16 v7, v47

    goto/16 :goto_10d

    :catch_f5
    move-object/from16 v19, v1

    move-object/from16 v47, v12

    move-object/from16 v20, v45

    move-object/from16 v41, v59

    move-object/from16 v42, v60

    move-object/from16 v45, v61

    move-object/from16 v49, v62

    move-object/from16 v50, v64

    move/from16 v55, v66

    const/4 v14, 0x0

    const/16 v34, 0x4

    move-object v12, v10

    :goto_f7
    move-object/from16 v0, v19

    move-object/from16 v19, v7

    move-object v7, v0

    move-object/from16 v11, p0

    move-object/from16 v21, v9

    move-object/from16 v33, v12

    move-object/from16 v44, v13

    move-object/from16 v40, v14

    move-object/from16 v143, v40

    move-object/from16 v144, v143

    move-object/from16 v145, v144

    :goto_f8
    move-object/from16 v22, v15

    move-object/from16 v141, v28

    move-object/from16 v10, v29

    move-object/from16 v142, v38

    move-object/from16 v13, v41

    move-object/from16 v0, v42

    move-object/from16 v9, v45

    move-object/from16 v3, v47

    move-object/from16 v12, v49

    move-object/from16 v1, v50

    :goto_f9
    move-object/from16 v15, v53

    move/from16 v90, v55

    const/4 v2, 0x1

    const/16 v37, 0x0

    move-object v14, v4

    move-object v4, v5

    move-object v5, v6

    move-object/from16 v6, v20

    :goto_fa
    move-object/from16 v20, v8

    :goto_fb
    move-object/from16 v8, v32

    goto/16 :goto_12b

    :catch_f6
    const/4 v3, 0x0

    const/4 v14, 0x0

    const/16 v34, 0x4

    move-object/from16 v11, p0

    move/from16 v37, v3

    move/from16 v90, v37

    move-object/from16 v33, v5

    move-object/from16 v20, v6

    move-object/from16 v21, v7

    move-object v3, v9

    move-object/from16 v44, v13

    move-object/from16 v40, v14

    move-object/from16 v143, v40

    move-object/from16 v144, v143

    move-object/from16 v145, v144

    move-object/from16 v22, v15

    move-object/from16 v141, v28

    move-object/from16 v10, v29

    move-object/from16 v8, v32

    move-object/from16 v142, v38

    move-object/from16 v19, v45

    move-object/from16 v14, v48

    move-object/from16 v0, v49

    move-object/from16 v9, v50

    move-object/from16 v13, v52

    move-object/from16 v15, v53

    move-object/from16 v6, v54

    goto/16 :goto_106

    :catchall_47
    move-exception v0

    move v3, v2

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v126, v38

    move-object/from16 v127, v53

    goto/16 :goto_fc

    :catch_f7
    move-exception v0

    move v3, v2

    move-object/from16 v112, v26

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v126, v38

    move-object/from16 v127, v53

    goto/16 :goto_fe

    :catch_f8
    move v3, v2

    goto/16 :goto_100

    :catch_f9
    move-exception v0

    move-object/from16 v51, v2

    goto/16 :goto_fd

    :catch_fa
    move-object/from16 v51, v2

    goto/16 :goto_ff

    :catch_fb
    move-exception v0

    move-object/from16 v48, v2

    goto/16 :goto_fd

    :catch_fc
    move-object/from16 v48, v2

    goto/16 :goto_ff

    :catch_fd
    move-exception v0

    move-object/from16 v50, v2

    goto/16 :goto_fd

    :catch_fe
    move-object/from16 v50, v2

    goto/16 :goto_ff

    :catch_ff
    move-exception v0

    move-object/from16 v49, v2

    goto :goto_fd

    :catch_100
    move-object/from16 v49, v2

    goto/16 :goto_ff

    :catch_101
    move-exception v0

    move-object/from16 v52, v2

    goto :goto_fd

    :catch_102
    move-object/from16 v52, v2

    goto :goto_ff

    :catch_103
    move-exception v0

    move-object/from16 v54, v2

    goto :goto_fd

    :catch_104
    move-object/from16 v54, v2

    goto :goto_ff

    :catch_105
    move-exception v0

    move-object/from16 v2, p0

    move-object/from16 v112, v26

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v126, v38

    move-object/from16 v127, v53

    const/4 v3, 0x0

    const/4 v14, 0x0

    const/16 v34, 0x4

    goto/16 :goto_10c

    :catchall_48
    move-exception v0

    move-object/from16 v2, p0

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v126, v38

    move-object/from16 v127, v53

    const/4 v3, 0x0

    const/4 v14, 0x0

    const/16 v34, 0x4

    goto/16 :goto_109

    :catch_106
    move-exception v0

    move-object/from16 v46, v2

    goto :goto_fd

    :catchall_49
    move-exception v0

    move-object/from16 v47, v2

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v126, v38

    move-object/from16 v127, v53

    const/4 v3, 0x0

    :goto_fc
    const/4 v14, 0x0

    const/16 v34, 0x4

    goto/16 :goto_108

    :catch_107
    move-exception v0

    move-object/from16 v47, v2

    :goto_fd
    move-object/from16 v112, v26

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v126, v38

    move-object/from16 v127, v53

    const/4 v3, 0x0

    :goto_fe
    const/4 v14, 0x0

    const/16 v34, 0x4

    goto/16 :goto_10b

    :catch_108
    move-object/from16 v47, v2

    :catch_109
    :goto_ff
    const/4 v3, 0x0

    :goto_100
    const/4 v14, 0x0

    const/16 v34, 0x4

    goto/16 :goto_104

    :catchall_4a
    move-exception v0

    goto :goto_101

    :catch_10a
    move-exception v0

    goto :goto_102

    :catchall_4b
    move-exception v0

    move-object/from16 v45, v4

    :goto_101
    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v126, v38

    move-object/from16 v4, v47

    move-object/from16 v127, v53

    const/4 v3, 0x0

    const/4 v14, 0x0

    const/16 v34, 0x4

    goto/16 :goto_107

    :catch_10b
    move-exception v0

    move-object/from16 v45, v4

    :goto_102
    move-object/from16 v112, v26

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v126, v38

    move-object/from16 v4, v47

    move-object/from16 v127, v53

    const/4 v3, 0x0

    const/4 v14, 0x0

    const/16 v34, 0x4

    goto/16 :goto_10a

    :catch_10c
    move-object/from16 v45, v4

    :catch_10d
    move-object/from16 v4, v47

    const/4 v3, 0x0

    const/4 v14, 0x0

    const/16 v34, 0x4

    goto/16 :goto_103

    :cond_31
    move-object/from16 v112, v26

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v126, v38

    move-object/from16 v15, v45

    move-object/from16 v127, v53

    const/4 v3, 0x0

    const/4 v14, 0x0

    const/16 v34, 0x4

    move-object/from16 v45, v4

    move-object/from16 v4, v47

    move-object/from16 v47, v2

    move-object/from16 v2, p0

    .line 165
    :try_start_af
    const-string v0, "Imported eboot.bin is missing"

    new-instance v8, Ljava/lang/IllegalArgumentException;

    invoke-virtual {v0}, Ljava/lang/Object;->toString()Ljava/lang/String;

    move-result-object v0

    invoke-direct {v8, v0}, Ljava/lang/IllegalArgumentException;-><init>(Ljava/lang/String;)V

    throw v8

    move-object/from16 v112, v26

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v126, v38

    move-object/from16 v15, v45

    move-object/from16 v127, v53

    const/4 v3, 0x0

    const/4 v14, 0x0

    const/16 v34, 0x4

    move-object/from16 v45, v4

    move-object/from16 v4, v47

    move-object/from16 v47, v2

    move-object/from16 v2, p0

    .line 163
    const-string v0, "Game path escapes app storage"

    new-instance v8, Ljava/lang/IllegalArgumentException;

    invoke-virtual {v0}, Ljava/lang/Object;->toString()Ljava/lang/String;

    move-result-object v0

    invoke-direct {v8, v0}, Ljava/lang/IllegalArgumentException;-><init>(Ljava/lang/String;)V

    throw v8

    :cond_32
    move-object/from16 v112, v26

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v126, v38

    move-object/from16 v15, v45

    move-object/from16 v127, v53

    const/4 v3, 0x0

    const/4 v14, 0x0

    const/16 v34, 0x4

    move-object/from16 v45, v4

    move-object/from16 v4, v47

    move-object/from16 v47, v2

    move-object/from16 v2, p0

    .line 160
    const-string v0, "Invalid game id"

    new-instance v8, Ljava/lang/IllegalArgumentException;

    invoke-virtual {v0}, Ljava/lang/Object;->toString()Ljava/lang/String;

    move-result-object v0

    invoke-direct {v8, v0}, Ljava/lang/IllegalArgumentException;-><init>(Ljava/lang/String;)V

    throw v8
    :try_end_af
    .catch Ljava/util/concurrent/CancellationException; {:try_start_af .. :try_end_af} :catch_10f
    .catch Ljava/lang/Exception; {:try_start_af .. :try_end_af} :catch_10e
    .catchall {:try_start_af .. :try_end_af} :catchall_4c

    :catchall_4c
    move-exception v0

    goto/16 :goto_109

    :catch_10e
    move-exception v0

    goto/16 :goto_10c

    :catch_10f
    move-object v11, v2

    move/from16 v37, v3

    move/from16 v90, v37

    move-object/from16 v33, v5

    move-object/from16 v20, v6

    move-object/from16 v21, v7

    move-object v3, v9

    move-object/from16 v44, v13

    move-object/from16 v40, v14

    move-object/from16 v143, v40

    move-object/from16 v144, v143

    move-object/from16 v145, v144

    move-object/from16 v22, v15

    move-object/from16 v10, v29

    move-object/from16 v8, v32

    move-object/from16 v19, v45

    move-object/from16 v14, v48

    move-object/from16 v0, v49

    move-object/from16 v9, v50

    move-object/from16 v13, v52

    move-object/from16 v6, v54

    move-object/from16 v27, v124

    move-object/from16 v141, v125

    move-object/from16 v142, v126

    move-object/from16 v15, v127

    goto :goto_105

    :catch_110
    move-object/from16 v15, v45

    const/4 v3, 0x0

    const/4 v14, 0x0

    const/16 v34, 0x4

    move-object/from16 v45, v4

    move-object/from16 v4, v47

    :goto_103
    move-object/from16 v47, v2

    :goto_104
    move-object/from16 v11, p0

    move/from16 v37, v3

    move/from16 v90, v37

    move-object/from16 v33, v5

    move-object/from16 v20, v6

    move-object/from16 v21, v7

    move-object v3, v9

    move-object/from16 v44, v13

    move-object/from16 v40, v14

    move-object/from16 v143, v40

    move-object/from16 v144, v143

    move-object/from16 v145, v144

    move-object/from16 v22, v15

    move-object/from16 v141, v28

    move-object/from16 v10, v29

    move-object/from16 v8, v32

    move-object/from16 v142, v38

    move-object/from16 v19, v45

    move-object/from16 v14, v48

    move-object/from16 v0, v49

    move-object/from16 v9, v50

    move-object/from16 v13, v52

    move-object/from16 v15, v53

    move-object/from16 v6, v54

    :goto_105
    const/4 v2, 0x1

    :goto_106
    move-object v7, v1

    move-object v5, v4

    move-object/from16 v4, v47

    move-object/from16 v1, v51

    goto/16 :goto_12b

    :catchall_4d
    move-exception v0

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v126, v38

    move-object/from16 v15, v45

    move-object/from16 v127, v53

    const/4 v3, 0x0

    const/4 v14, 0x0

    const/16 v34, 0x4

    move-object/from16 v45, v4

    move-object/from16 v4, v47

    :goto_107
    move-object/from16 v47, v2

    :goto_108
    move-object/from16 v2, p0

    :goto_109
    move/from16 v37, v3

    move-object/from16 v33, v5

    move-object v11, v6

    move-object v10, v7

    move-object/from16 v44, v13

    move-object v3, v14

    move-object/from16 v155, v3

    move-object v13, v15

    move-object/from16 v6, v29

    move-object/from16 v7, v30

    move-object/from16 v9, v31

    move-object/from16 v15, v32

    move/from16 v1, v34

    move-object/from16 v12, v45

    move-object/from16 v5, v47

    move-object/from16 v151, v124

    move-object/from16 v152, v125

    move-object/from16 v153, v126

    move-object/from16 v154, v127

    const/4 v8, 0x1

    move-object v14, v4

    move-object v4, v0

    move-object/from16 v0, v155

    goto/16 :goto_146

    :catch_111
    move-exception v0

    move-object/from16 v112, v26

    move-object/from16 v124, v27

    move-object/from16 v125, v28

    move-object/from16 v126, v38

    move-object/from16 v15, v45

    move-object/from16 v127, v53

    const/4 v3, 0x0

    const/4 v14, 0x0

    const/16 v34, 0x4

    move-object/from16 v45, v4

    move-object/from16 v4, v47

    :goto_10a
    move-object/from16 v47, v2

    :goto_10b
    move-object/from16 v2, p0

    :goto_10c
    move-object/from16 v16, v0

    move/from16 v37, v3

    move/from16 v90, v37

    move-object/from16 v33, v5

    move-object/from16 v120, v6

    move-object/from16 v22, v7

    move-object v7, v9

    move-object/from16 v44, v13

    move-object/from16 v128, v14

    move-object/from16 v129, v128

    move-object/from16 v130, v129

    move-object/from16 v20, v45

    move-object/from16 v5, v47

    move-object/from16 v13, v48

    move-object/from16 v10, v49

    move-object/from16 v11, v50

    move-object/from16 v3, v51

    move-object/from16 v9, v52

    move-object/from16 v8, v54

    move-object v6, v1

    move-object/from16 v1, v46

    .line 480
    :goto_10d
    :try_start_b0
    invoke-static {}, Ljava/time/Instant;->now()Ljava/time/Instant;

    move-result-object v0

    invoke-virtual {v0}, Ljava/time/Instant;->toString()Ljava/lang/String;

    move-result-object v17
    :try_end_b0
    .catchall {:try_start_b0 .. :try_end_b0} :catchall_63

    .line 481
    :try_start_b1
    sget-object v0, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    invoke-static {v1}, Lkotlin/jvm/internal/Intrinsics;->checkNotNull(Ljava/lang/Object;)V
    :try_end_b1
    .catchall {:try_start_b1 .. :try_end_b1} :catchall_4f

    move-object/from16 p1, v4

    const/4 v4, 0x1

    :try_start_b2
    invoke-static {v1, v14, v4, v14}, Lkotlin/io/FilesKt;->readLines$default(Ljava/io/File;Ljava/nio/charset/Charset;ILjava/lang/Object;)Ljava/util/List;

    move-result-object v0

    const/16 v1, 0x14

    invoke-static {v0, v1}, Lkotlin/collections/CollectionsKt;->takeLast(Ljava/util/List;I)Ljava/util/List;

    move-result-object v0

    move-object/from16 v45, v0

    check-cast v45, Ljava/lang/Iterable;

    const-string v0, " | "

    move-object/from16 v46, v0

    check-cast v46, Ljava/lang/CharSequence;

    const/16 v52, 0x3e

    const/16 v53, 0x0

    const/16 v47, 0x0

    const/16 v48, 0x0

    const/16 v49, 0x0

    const/16 v50, 0x0

    const/16 v51, 0x0

    invoke-static/range {v45 .. v53}, Lkotlin/collections/CollectionsKt;->joinToString$default(Ljava/lang/Iterable;Ljava/lang/CharSequence;Ljava/lang/CharSequence;Ljava/lang/CharSequence;ILjava/lang/CharSequence;Lkotlin/jvm/functions/Function1;ILjava/lang/Object;)Ljava/lang/String;

    move-result-object v0

    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v0
    :try_end_b2
    .catchall {:try_start_b2 .. :try_end_b2} :catchall_4e

    goto :goto_10f

    :catchall_4e
    move-exception v0

    goto :goto_10e

    :catchall_4f
    move-exception v0

    move-object/from16 p1, v4

    :goto_10e
    :try_start_b3
    sget-object v1, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    invoke-static {v0}, Lkotlin/ResultKt;->createFailure(Ljava/lang/Throwable;)Ljava/lang/Object;

    move-result-object v0

    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v0

    .line 482
    :goto_10f
    invoke-static {v0}, Lkotlin/Result;->isFailure-impl(Ljava/lang/Object;)Z

    move-result v1

    if-eqz v1, :cond_33

    move-object/from16 v0, v35

    :cond_33
    check-cast v0, Ljava/lang/String;

    const/4 v1, 0x2

    .line 483
    new-array v4, v1, [Ljava/lang/String;

    invoke-virtual/range {v16 .. v16}, Ljava/lang/Exception;->getMessage()Ljava/lang/String;

    move-result-object v18

    aput-object v18, v4, v37

    check-cast v0, Ljava/lang/CharSequence;

    invoke-static {v0}, Lkotlin/text/StringsKt;->isBlank(Ljava/lang/CharSequence;)Z

    move-result v18
    :try_end_b3
    .catchall {:try_start_b3 .. :try_end_b3} :catchall_62

    if-eqz v18, :cond_34

    move-object v0, v14

    :cond_34
    const/16 v39, 0x1

    :try_start_b4
    aput-object v0, v4, v39
    :try_end_b4
    .catchall {:try_start_b4 .. :try_end_b4} :catchall_61

    :try_start_b5
    invoke-static {v4}, Lkotlin/collections/CollectionsKt;->listOfNotNull([Ljava/lang/Object;)Ljava/util/List;

    move-result-object v0

    move-object/from16 v45, v0

    check-cast v45, Ljava/lang/Iterable;

    move-object/from16 v4, v112

    move-object/from16 v46, v4

    check-cast v46, Ljava/lang/CharSequence;

    const/16 v52, 0x3e

    const/16 v53, 0x0

    const/16 v47, 0x0

    const/16 v48, 0x0

    const/16 v49, 0x0

    const/16 v50, 0x0

    const/16 v51, 0x0

    invoke-static/range {v45 .. v53}, Lkotlin/collections/CollectionsKt;->joinToString$default(Ljava/lang/Iterable;Ljava/lang/CharSequence;Ljava/lang/CharSequence;Ljava/lang/CharSequence;ILjava/lang/CharSequence;Lkotlin/jvm/functions/Function1;ILjava/lang/Object;)Ljava/lang/String;

    move-result-object v0

    .line 484
    invoke-virtual/range {v16 .. v16}, Ljava/lang/Object;->getClass()Ljava/lang/Class;

    move-result-object v18

    invoke-virtual/range {v18 .. v18}, Ljava/lang/Class;->getSimpleName()Ljava/lang/String;

    move-result-object v1

    invoke-virtual/range {v16 .. v16}, Ljava/lang/Exception;->getMessage()Ljava/lang/String;

    move-result-object v18
    :try_end_b5
    .catchall {:try_start_b5 .. :try_end_b5} :catchall_62

    if-nez v18, :cond_35

    move-object/from16 v14, v35

    goto :goto_110

    :cond_35
    move-object/from16 v14, v18

    :goto_110
    move-object/from16 p2, v6

    :try_start_b6
    new-instance v6, Ljava/lang/StringBuilder;

    invoke-direct {v6}, Ljava/lang/StringBuilder;-><init>()V

    invoke-virtual {v6, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1, v4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1, v14}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v1
    :try_end_b6
    .catchall {:try_start_b6 .. :try_end_b6} :catchall_60

    move-object/from16 v4, v127

    :try_start_b7
    invoke-virtual {v5, v4, v1}, Lcom/bachatas4/android/runtime/diagnostics/SessionLog;->error(Ljava/lang/String;Ljava/lang/String;)V

    .line 485
    iget-boolean v1, v3, Lkotlin/jvm/internal/Ref$BooleanRef;->element:Z
    :try_end_b7
    .catchall {:try_start_b7 .. :try_end_b7} :catchall_5f

    if-nez v1, :cond_3b

    .line 490
    :try_start_b8
    iget-object v1, v12, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v1, Ljava/lang/String;

    .line 492
    iget-object v6, v10, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v6, Ljava/lang/String;

    .line 493
    iget-boolean v8, v8, Lkotlin/jvm/internal/Ref$BooleanRef;->element:Z

    .line 494
    iget-object v10, v11, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v10, Lcom/bachatas4/android/runtime/diagnostics/DiagnosticDriverInfo;

    .line 495
    iget-object v9, v9, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v9, Ljava/lang/String;

    .line 497
    iget-object v11, v2, Lcom/bachatas4/android/service/EmulationService;->process:Lcom/bachatas4/android/runtime/process/RuntimeProcessHandle;
    :try_end_b8
    .catchall {:try_start_b8 .. :try_end_b8} :catchall_58

    if-eqz v11, :cond_36

    :try_start_b9
    invoke-interface {v11}, Lcom/bachatas4/android/runtime/process/RuntimeProcessHandle;->getExitCode()Ljava/lang/Integer;

    move-result-object v11
    :try_end_b9
    .catchall {:try_start_b9 .. :try_end_b9} :catchall_50

    move-object v12, v11

    goto :goto_112

    :catchall_50
    move-exception v0

    move-object/from16 v14, p1

    move-object/from16 v154, v4

    move-object v13, v15

    move-object/from16 v12, v20

    move-object/from16 v10, v22

    move-object/from16 v6, v29

    move-object/from16 v7, v30

    move-object/from16 v9, v31

    move-object/from16 v15, v32

    move/from16 v1, v34

    move-object/from16 v11, v120

    move-object/from16 v151, v124

    move-object/from16 v152, v125

    move-object/from16 v153, v126

    move-object/from16 v3, v128

    move-object/from16 v155, v130

    :goto_111
    const/4 v8, 0x1

    goto/16 :goto_11b

    :cond_36
    const/4 v12, 0x0

    :goto_112
    if-nez v90, :cond_39

    .line 498
    :try_start_ba
    invoke-virtual/range {v16 .. v16}, Ljava/lang/Exception;->getMessage()Ljava/lang/String;

    move-result-object v11

    if-eqz v11, :cond_37

    check-cast v11, Ljava/lang/CharSequence;

    const-string v14, "exited before socket"

    check-cast v14, Ljava/lang/CharSequence;
    :try_end_ba
    .catchall {:try_start_ba .. :try_end_ba} :catchall_52

    move-object/from16 p3, v1

    move-object/from16 v18, v3

    move/from16 v2, v37

    const/4 v1, 0x2

    const/4 v3, 0x0

    :try_start_bb
    invoke-static {v11, v14, v2, v1, v3}, Lkotlin/text/StringsKt;->contains$default(Ljava/lang/CharSequence;Ljava/lang/CharSequence;ZILjava/lang/Object;)Z

    move-result v1
    :try_end_bb
    .catchall {:try_start_bb .. :try_end_bb} :catchall_51

    const/4 v11, 0x1

    if-ne v1, v11, :cond_38

    goto :goto_114

    :catchall_51
    move-exception v0

    const/4 v11, 0x1

    move-object/from16 v14, p1

    move/from16 v37, v2

    goto :goto_113

    :cond_37
    move-object/from16 p3, v1

    move-object/from16 v18, v3

    move/from16 v2, v37

    const/4 v3, 0x0

    const/4 v11, 0x1

    :cond_38
    move v1, v2

    goto :goto_115

    :catchall_52
    move-exception v0

    move/from16 v2, v37

    const/4 v3, 0x0

    const/4 v11, 0x1

    move-object/from16 v14, p1

    :goto_113
    move-object/from16 v154, v4

    move v8, v11

    move-object v13, v15

    move-object/from16 v12, v20

    move-object/from16 v10, v22

    move-object/from16 v6, v29

    move-object/from16 v7, v30

    move-object/from16 v9, v31

    move-object/from16 v15, v32

    move/from16 v1, v34

    move-object/from16 v11, v120

    move-object/from16 v151, v124

    move-object/from16 v152, v125

    move-object/from16 v153, v126

    move-object/from16 v3, v128

    move-object/from16 v155, v130

    move-object/from16 v2, p0

    goto/16 :goto_11b

    :cond_39
    move-object/from16 p3, v1

    move-object/from16 v18, v3

    move/from16 v2, v37

    const/4 v3, 0x0

    const/4 v11, 0x1

    :goto_114
    move v1, v11

    .line 499
    :goto_115
    :try_start_bc
    const-string v14, "BACKEND_CRASHED"

    .line 500
    iget-object v13, v13, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v13, Ljava/lang/String;
    :try_end_bc
    .catchall {:try_start_bc .. :try_end_bc} :catchall_57

    move-object v3, v10

    move-object v10, v9

    move-object v9, v3

    move/from16 v37, v2

    move-object/from16 v140, v4

    move-object v3, v5

    move-object v2, v7

    move-object/from16 v135, v15

    move-object/from16 v11, v17

    move-object/from16 v131, v18

    move-object/from16 v132, v20

    move-object/from16 v134, v22

    move-object/from16 v136, v29

    move-object/from16 v137, v30

    move-object/from16 v138, v31

    move-object/from16 v139, v32

    move-object/from16 v133, v120

    move-object/from16 v4, p1

    move-object/from16 v5, p3

    move-object v7, v6

    move-object v15, v13

    move-object/from16 v6, p2

    move v13, v1

    move-object/from16 v1, p0

    .line 486
    :try_start_bd
    invoke-direct/range {v1 .. v15}, Lcom/bachatas4/android/service/EmulationService;->buildReportContext(Ljava/lang/String;Lcom/bachatas4/android/runtime/diagnostics/SessionLog;Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpointStore;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;ZLcom/bachatas4/android/runtime/diagnostics/DiagnosticDriverInfo;Ljava/lang/String;Ljava/lang/String;Ljava/lang/Integer;ZLjava/lang/String;Ljava/lang/String;)Lcom/bachatas4/android/runtime/diagnostics/DiagnosticReportContext;

    move-result-object v2
    :try_end_bd
    .catchall {:try_start_bd .. :try_end_bd} :catchall_56

    move-object v11, v1

    .line 502
    :try_start_be
    sget-object v1, Lcom/bachatas4/android/runtime/session/ManagedSession;->INSTANCE:Lcom/bachatas4/android/runtime/session/ManagedSession;

    .line 504
    sget-object v5, Lcom/bachatas4/android/model/RuntimeErrorCode;->BACKEND_CRASHED:Lcom/bachatas4/android/model/RuntimeErrorCode;

    .line 505
    check-cast v0, Ljava/lang/CharSequence;

    invoke-static {v0}, Lkotlin/text/StringsKt;->isBlank(Ljava/lang/CharSequence;)Z

    move-result v6
    :try_end_be
    .catchall {:try_start_be .. :try_end_be} :catchall_55

    if-eqz v6, :cond_3a

    :try_start_bf
    invoke-virtual/range {v16 .. v16}, Ljava/lang/Object;->getClass()Ljava/lang/Class;

    move-result-object v0

    invoke-virtual {v0}, Ljava/lang/Class;->getSimpleName()Ljava/lang/String;

    move-result-object v0
    :try_end_bf
    .catchall {:try_start_bf .. :try_end_bf} :catchall_53

    goto :goto_116

    :catchall_53
    move-exception v0

    move-object v5, v3

    move-object v14, v4

    move-object v2, v11

    move-object/from16 v151, v124

    move-object/from16 v152, v125

    move-object/from16 v153, v126

    move-object/from16 v3, v128

    move-object/from16 v155, v130

    move-object/from16 v12, v132

    move-object/from16 v11, v133

    move-object/from16 v10, v134

    move-object/from16 v13, v135

    move-object/from16 v6, v136

    move-object/from16 v7, v137

    move-object/from16 v9, v138

    move-object/from16 v15, v139

    move-object/from16 v154, v140

    const/4 v1, 0x4

    goto/16 :goto_111

    :cond_3a
    :goto_116
    :try_start_c0
    const-string v6, "ifBlank(...)"

    invoke-static {v0, v6}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullExpressionValue(Ljava/lang/Object;Ljava/lang/String;)V

    check-cast v0, Ljava/lang/String;

    .line 503
    new-instance v6, Lcom/bachatas4/android/runtime/session/ManagedSessionState$Failed;

    invoke-direct {v6, v5, v0, v2}, Lcom/bachatas4/android/runtime/session/ManagedSessionState$Failed;-><init>(Lcom/bachatas4/android/model/RuntimeErrorCode;Ljava/lang/String;Lcom/bachatas4/android/runtime/diagnostics/DiagnosticReportContext;)V

    check-cast v6, Lcom/bachatas4/android/runtime/session/ManagedSessionState;

    .line 502
    invoke-virtual {v1, v6}, Lcom/bachatas4/android/runtime/session/ManagedSession;->update(Lcom/bachatas4/android/runtime/session/ManagedSessionState;)V
    :try_end_c0
    .catchall {:try_start_c0 .. :try_end_c0} :catchall_55

    move-object/from16 v1, v131

    const/4 v2, 0x1

    .line 509
    :try_start_c1
    iput-boolean v2, v1, Lkotlin/jvm/internal/Ref$BooleanRef;->element:Z
    :try_end_c1
    .catchall {:try_start_c1 .. :try_end_c1} :catchall_54

    goto/16 :goto_11c

    :catchall_54
    move-exception v0

    goto :goto_118

    :catchall_55
    move-exception v0

    goto :goto_117

    :catchall_56
    move-exception v0

    move-object v11, v1

    :goto_117
    const/4 v2, 0x1

    :goto_118
    move v8, v2

    move-object v5, v3

    goto :goto_11a

    :catchall_57
    move-exception v0

    move/from16 v37, v2

    move-object/from16 v140, v4

    move-object v3, v5

    move v2, v11

    move-object/from16 v135, v15

    move-object/from16 v132, v20

    move-object/from16 v134, v22

    move-object/from16 v136, v29

    move-object/from16 v137, v30

    move-object/from16 v138, v31

    move-object/from16 v139, v32

    move-object/from16 v133, v120

    move-object/from16 v11, p0

    goto :goto_119

    :catchall_58
    move-exception v0

    move-object v11, v2

    move-object/from16 v140, v4

    move-object v3, v5

    move-object/from16 v135, v15

    move-object/from16 v132, v20

    move-object/from16 v134, v22

    move-object/from16 v136, v29

    move-object/from16 v137, v30

    move-object/from16 v138, v31

    move-object/from16 v139, v32

    move-object/from16 v133, v120

    const/4 v2, 0x1

    :goto_119
    move-object/from16 v4, p1

    move v8, v2

    :goto_11a
    move-object v14, v4

    move-object v2, v11

    move-object/from16 v151, v124

    move-object/from16 v152, v125

    move-object/from16 v153, v126

    move-object/from16 v3, v128

    move-object/from16 v155, v130

    move-object/from16 v12, v132

    move-object/from16 v11, v133

    move-object/from16 v10, v134

    move-object/from16 v13, v135

    move-object/from16 v6, v136

    move-object/from16 v7, v137

    move-object/from16 v9, v138

    move-object/from16 v15, v139

    move-object/from16 v154, v140

    const/4 v1, 0x4

    :goto_11b
    move-object v4, v0

    move-object/from16 v0, v129

    goto/16 :goto_146

    :cond_3b
    move-object v11, v2

    move-object/from16 v140, v4

    move-object v3, v5

    move-object/from16 v135, v15

    move-object/from16 v132, v20

    move-object/from16 v134, v22

    move-object/from16 v136, v29

    move-object/from16 v137, v30

    move-object/from16 v138, v31

    move-object/from16 v139, v32

    move-object/from16 v133, v120

    const/4 v2, 0x1

    move-object/from16 v4, p1

    :goto_11c
    move-object/from16 v14, v129

    if-eqz v14, :cond_3f

    move-object/from16 v8, v139

    .line 512
    invoke-interface {v14, v8}, Ljava/nio/file/Path;->resolve(Ljava/lang/String;)Ljava/nio/file/Path;

    move-result-object v0

    if-eqz v0, :cond_3f

    .line 513
    :try_start_c2
    sget-object v1, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    .line 514
    invoke-interface {v0}, Ljava/nio/file/Path;->toFile()Ljava/io/File;

    move-result-object v1

    invoke-virtual {v1}, Ljava/io/File;->isFile()Z

    move-result v1

    if-eqz v1, :cond_3c

    .line 517
    invoke-virtual {v3}, Lcom/bachatas4/android/runtime/diagnostics/SessionLog;->getDirectory()Ljava/nio/file/Path;

    move-result-object v1

    move-object/from16 v10, v136

    invoke-interface {v1, v10}, Ljava/nio/file/Path;->resolve(Ljava/lang/String;)Ljava/nio/file/Path;

    move-result-object v1

    .line 518
    new-array v5, v2, [Ljava/nio/file/CopyOption;

    sget-object v6, Ljava/nio/file/StandardCopyOption;->REPLACE_EXISTING:Ljava/nio/file/StandardCopyOption;

    aput-object v6, v5, v37

    .line 515
    invoke-static {v0, v1, v5}, Ljava/nio/file/Files;->copy(Ljava/nio/file/Path;Ljava/nio/file/Path;[Ljava/nio/file/CopyOption;)Ljava/nio/file/Path;

    .line 521
    :cond_3c
    sget-object v0, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;

    .line 513
    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v0
    :try_end_c2
    .catchall {:try_start_c2 .. :try_end_c2} :catchall_59

    goto :goto_11d

    :catchall_59
    move-exception v0

    sget-object v1, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    invoke-static {v0}, Lkotlin/ResultKt;->createFailure(Ljava/lang/Throwable;)Ljava/lang/Object;

    move-result-object v0

    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v0

    .line 521
    :goto_11d
    invoke-static {v0}, Lkotlin/Result;->exceptionOrNull-impl(Ljava/lang/Object;)Ljava/lang/Throwable;

    move-result-object v1

    if-eqz v1, :cond_3e

    .line 522
    invoke-virtual {v1}, Ljava/lang/Throwable;->getMessage()Ljava/lang/String;

    move-result-object v1

    if-nez v1, :cond_3d

    move-object/from16 v1, v35

    :cond_3d
    new-instance v5, Ljava/lang/StringBuilder;

    move-object/from16 v6, v137

    invoke-direct {v5, v6}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v5, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v1

    move-object/from16 v5, v138

    invoke-virtual {v3, v5, v1}, Lcom/bachatas4/android/runtime/diagnostics/SessionLog;->warning(Ljava/lang/String;Ljava/lang/String;)V

    .line 523
    :cond_3e
    invoke-static {v0}, Lkotlin/Result;->box-impl(Ljava/lang/Object;)Lkotlin/Result;

    :cond_3f
    move-object/from16 v12, v128

    if-eqz v12, :cond_41

    move/from16 v7, v37

    const/4 v1, 0x4

    :goto_11e
    if-ge v7, v1, :cond_40

    .line 526
    sget-object v0, Lcom/bachatas4/android/runtime/session/ManagedSession;->INSTANCE:Lcom/bachatas4/android/runtime/session/ManagedSession;

    sget-object v5, Lcom/bachatas4/android/runtime/input/ControllerSnapshot;->Companion:Lcom/bachatas4/android/runtime/input/ControllerSnapshot$Companion;

    invoke-virtual {v5}, Lcom/bachatas4/android/runtime/input/ControllerSnapshot$Companion;->getNeutral()Lcom/bachatas4/android/runtime/input/ControllerSnapshot;

    move-result-object v5

    invoke-virtual {v0, v7, v5}, Lcom/bachatas4/android/runtime/session/ManagedSession;->submitController(ILcom/bachatas4/android/runtime/input/ControllerSnapshot;)V

    add-int/lit8 v7, v7, 0x1

    goto :goto_11e

    .line 527
    :cond_40
    sget-object v0, Lcom/bachatas4/android/runtime/session/ManagedSession;->INSTANCE:Lcom/bachatas4/android/runtime/session/ManagedSession;

    invoke-virtual {v0, v12}, Lcom/bachatas4/android/runtime/session/ManagedSession;->detachControllerSlotSink(Lkotlin/jvm/functions/Function2;)V

    .line 525
    sget-object v0, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;

    .line 529
    :cond_41
    sget-object v0, Lcom/bachatas4/android/runtime/input/PhoneMotionSource;->INSTANCE:Lcom/bachatas4/android/runtime/input/PhoneMotionSource;

    invoke-virtual {v0}, Lcom/bachatas4/android/runtime/input/PhoneMotionSource;->stop()V

    .line 530
    sget-object v0, Lcom/bachatas4/android/runtime/input/GamepadInputManager;->INSTANCE:Lcom/bachatas4/android/runtime/input/GamepadInputManager;

    invoke-virtual {v0}, Lcom/bachatas4/android/runtime/input/GamepadInputManager;->onSessionEnd()V

    .line 531
    iget-object v0, v11, Lcom/bachatas4/android/service/EmulationService;->process:Lcom/bachatas4/android/runtime/process/RuntimeProcessHandle;

    if-eqz v0, :cond_42

    invoke-interface {v0}, Lcom/bachatas4/android/runtime/process/RuntimeProcessHandle;->getExitCode()Ljava/lang/Integer;

    move-result-object v6

    goto :goto_11f

    :cond_42
    const/4 v6, 0x0

    .line 532
    :goto_11f
    iget-object v0, v11, Lcom/bachatas4/android/service/EmulationService;->process:Lcom/bachatas4/android/runtime/process/RuntimeProcessHandle;

    if-eqz v0, :cond_43

    invoke-interface {v0}, Lcom/bachatas4/android/runtime/process/RuntimeProcessHandle;->destroyForcibly()V

    sget-object v0, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;

    :cond_43
    const/4 v7, 0x0

    .line 533
    iput-object v7, v11, Lcom/bachatas4/android/service/EmulationService;->process:Lcom/bachatas4/android/runtime/process/RuntimeProcessHandle;

    .line 534
    :try_start_c3
    sget-object v0, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    move-object/from16 v15, v135

    iget-object v0, v15, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v0, Landroid/net/LocalSocket;

    if-eqz v0, :cond_44

    invoke-virtual {v0}, Landroid/net/LocalSocket;->close()V

    sget-object v0, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;

    goto :goto_120

    :cond_44
    move-object v0, v7

    :goto_120
    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;
    :try_end_c3
    .catchall {:try_start_c3 .. :try_end_c3} :catchall_5a

    goto :goto_121

    :catchall_5a
    move-exception v0

    sget-object v1, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    invoke-static {v0}, Lkotlin/ResultKt;->createFailure(Ljava/lang/Throwable;)Ljava/lang/Object;

    move-result-object v0

    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;

    .line 535
    :goto_121
    :try_start_c4
    sget-object v0, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    move-object/from16 v9, v134

    iget-object v0, v9, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v0, Landroid/net/LocalServerSocket;

    if-eqz v0, :cond_45

    invoke-virtual {v0}, Landroid/net/LocalServerSocket;->close()V

    sget-object v0, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;

    goto :goto_122

    :cond_45
    move-object v0, v7

    :goto_122
    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;
    :try_end_c4
    .catchall {:try_start_c4 .. :try_end_c4} :catchall_5b

    goto :goto_123

    :catchall_5b
    move-exception v0

    sget-object v1, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    invoke-static {v0}, Lkotlin/ResultKt;->createFailure(Ljava/lang/Throwable;)Ljava/lang/Object;

    move-result-object v0

    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;

    .line 536
    :goto_123
    :try_start_c5
    sget-object v0, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    move-object/from16 v13, v133

    iget-object v0, v13, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v0, Landroid/net/LocalSocket;

    if-eqz v0, :cond_46

    invoke-virtual {v0}, Landroid/net/LocalSocket;->close()V

    sget-object v0, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;

    goto :goto_124

    :cond_46
    move-object v0, v7

    :goto_124
    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;
    :try_end_c5
    .catchall {:try_start_c5 .. :try_end_c5} :catchall_5c

    goto :goto_125

    :catchall_5c
    move-exception v0

    sget-object v1, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    invoke-static {v0}, Lkotlin/ResultKt;->createFailure(Ljava/lang/Throwable;)Ljava/lang/Object;

    move-result-object v0

    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;

    .line 537
    :goto_125
    invoke-interface/range {v33 .. v33}, Ljava/util/concurrent/ExecutorService;->shutdownNow()Ljava/util/List;

    .line 538
    :try_start_c6
    sget-object v0, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    move-object/from16 v1, v132

    iget-object v0, v1, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v0, Lcom/bachatas4/android/runtime/display/WinlatorEmbeddedXServer;

    if-eqz v0, :cond_47

    new-instance v1, Lcom/bachatas4/android/service/EmulationService$runSession$16$1$1;

    invoke-direct {v1, v0, v7}, Lcom/bachatas4/android/service/EmulationService$runSession$16$1$1;-><init>(Lcom/bachatas4/android/runtime/display/WinlatorEmbeddedXServer;Lkotlin/coroutines/Continuation;)V

    check-cast v1, Lkotlin/jvm/functions/Function2;

    invoke-static {v7, v1, v2, v7}, Lkotlinx/coroutines/BuildersKt;->runBlockingK$default(Lkotlin/coroutines/CoroutineContext;Lkotlin/jvm/functions/Function2;ILjava/lang/Object;)Ljava/lang/Object;

    sget-object v0, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;

    goto :goto_126

    :cond_47
    move-object v0, v7

    :goto_126
    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;
    :try_end_c6
    .catchall {:try_start_c6 .. :try_end_c6} :catchall_5d

    goto :goto_127

    :catchall_5d
    move-exception v0

    sget-object v1, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    invoke-static {v0}, Lkotlin/ResultKt;->createFailure(Ljava/lang/Throwable;)Ljava/lang/Object;

    move-result-object v0

    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;

    :goto_127
    move-object/from16 v1, v130

    if-eqz v1, :cond_4a

    .line 541
    :try_start_c7
    sget-object v0, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    .line 542
    new-instance v0, Lcom/bachatas4/android/service/EmulationService$runSession$17$1$1;

    invoke-direct {v0, v1, v6, v7}, Lcom/bachatas4/android/service/EmulationService$runSession$17$1$1;-><init>(Lcom/bachatas4/android/runtime/vortek/VortekSessionSupport;Ljava/lang/Integer;Lkotlin/coroutines/Continuation;)V

    check-cast v0, Lkotlin/jvm/functions/Function2;

    invoke-static {v7, v0, v2, v7}, Lkotlinx/coroutines/BuildersKt;->runBlockingK$default(Lkotlin/coroutines/CoroutineContext;Lkotlin/jvm/functions/Function2;ILjava/lang/Object;)Ljava/lang/Object;

    move-result-object v0

    check-cast v0, Lcom/bachatas4/android/runtime/vortek/VortekStopResult;

    .line 541
    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v0
    :try_end_c7
    .catchall {:try_start_c7 .. :try_end_c7} :catchall_5e

    goto :goto_128

    :catchall_5e
    move-exception v0

    sget-object v1, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    invoke-static {v0}, Lkotlin/ResultKt;->createFailure(Ljava/lang/Throwable;)Ljava/lang/Object;

    move-result-object v0

    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v0

    .line 543
    :goto_128
    invoke-static {v0}, Lkotlin/Result;->exceptionOrNull-impl(Ljava/lang/Object;)Ljava/lang/Throwable;

    move-result-object v1

    if-eqz v1, :cond_49

    .line 544
    invoke-virtual {v1}, Ljava/lang/Throwable;->getMessage()Ljava/lang/String;

    move-result-object v1

    if-nez v1, :cond_48

    move-object/from16 v1, v35

    :cond_48
    new-instance v2, Ljava/lang/StringBuilder;

    move-object/from16 v5, v124

    invoke-direct {v2, v5}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v2, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v1

    move-object/from16 v2, v126

    invoke-virtual {v3, v2, v1}, Lcom/bachatas4/android/runtime/diagnostics/SessionLog;->warning(Ljava/lang/String;Ljava/lang/String;)V

    .line 545
    :cond_49
    invoke-static {v0}, Lkotlin/Result;->box-impl(Ljava/lang/Object;)Lkotlin/Result;

    .line 547
    :cond_4a
    invoke-virtual/range {v44 .. v44}, Ljava/io/File;->delete()Z

    .line 548
    sget-object v0, Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpoint;->SESSION_FINISHED:Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpoint;

    invoke-virtual {v4, v0}, Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpointStore;->mark(Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpoint;)V

    move-object/from16 v1, v125

    move-object/from16 v2, v140

    .line 549
    invoke-virtual {v3, v2, v1}, Lcom/bachatas4/android/runtime/diagnostics/SessionLog;->info(Ljava/lang/String;Ljava/lang/String;)V

    .line 550
    invoke-virtual {v11}, Lcom/bachatas4/android/service/EmulationService;->stopSelf()V

    goto/16 :goto_143

    :catchall_5f
    move-exception v0

    move-object v11, v2

    move-object v3, v5

    move-object/from16 v135, v15

    move-object/from16 v132, v20

    move-object/from16 v9, v22

    move-object/from16 v10, v29

    move-object/from16 v6, v30

    move-object/from16 v5, v31

    move-object/from16 v8, v32

    move-object/from16 v13, v120

    move-object/from16 v1, v124

    move-object/from16 v141, v125

    move-object/from16 v142, v126

    move-object/from16 v12, v128

    move-object/from16 v14, v129

    move-object/from16 v40, v130

    const/4 v2, 0x1

    const/4 v7, 0x0

    move-object v15, v4

    move-object/from16 v4, p1

    goto/16 :goto_12a

    :catchall_60
    move-exception v0

    move-object/from16 v4, p1

    move-object v11, v2

    move-object v3, v5

    move-object/from16 v135, v15

    move-object/from16 v132, v20

    move-object/from16 v9, v22

    move-object/from16 v10, v29

    move-object/from16 v6, v30

    move-object/from16 v5, v31

    move-object/from16 v8, v32

    move-object/from16 v13, v120

    move-object/from16 v1, v124

    move-object/from16 v141, v125

    move-object/from16 v142, v126

    move-object/from16 v15, v127

    move-object/from16 v12, v128

    move-object/from16 v14, v129

    move-object/from16 v40, v130

    const/4 v2, 0x1

    const/4 v7, 0x0

    goto/16 :goto_12a

    :catchall_61
    move-exception v0

    move-object/from16 v4, p1

    move-object v11, v2

    move-object v3, v5

    move-object v7, v14

    move-object/from16 v135, v15

    move-object/from16 v132, v20

    move-object/from16 v9, v22

    move-object/from16 v10, v29

    move-object/from16 v6, v30

    move-object/from16 v5, v31

    move-object/from16 v8, v32

    move/from16 v2, v39

    move-object/from16 v13, v120

    move-object/from16 v1, v124

    move-object/from16 v141, v125

    move-object/from16 v142, v126

    move-object/from16 v15, v127

    move-object/from16 v12, v128

    move-object/from16 v14, v129

    move-object/from16 v40, v130

    goto :goto_12a

    :catchall_62
    move-exception v0

    move-object/from16 v4, p1

    goto :goto_129

    :catchall_63
    move-exception v0

    :goto_129
    move-object v11, v2

    move-object v3, v5

    move-object v7, v14

    move-object/from16 v135, v15

    move-object/from16 v132, v20

    move-object/from16 v9, v22

    move-object/from16 v10, v29

    move-object/from16 v6, v30

    move-object/from16 v5, v31

    move-object/from16 v8, v32

    move-object/from16 v13, v120

    move-object/from16 v1, v124

    move-object/from16 v141, v125

    move-object/from16 v142, v126

    move-object/from16 v15, v127

    move-object/from16 v12, v128

    move-object/from16 v14, v129

    move-object/from16 v40, v130

    const/4 v2, 0x1

    :goto_12a
    move-object v7, v4

    move-object v4, v0

    move-object v0, v14

    move-object v14, v7

    move-object/from16 v151, v1

    move-object v7, v6

    move-object v6, v10

    move-object/from16 v154, v15

    move-object/from16 v155, v40

    move-object/from16 v152, v141

    move-object/from16 v153, v142

    const/4 v1, 0x4

    move-object v15, v8

    move-object v10, v9

    move v8, v2

    move-object v9, v5

    move-object v2, v11

    move-object v11, v13

    move-object/from16 v13, v135

    move-object v5, v3

    move-object v3, v12

    move-object/from16 v12, v132

    goto/16 :goto_146

    :catch_112
    move-object/from16 v11, p0

    move-object/from16 v141, v28

    move-object/from16 v10, v29

    move-object/from16 v8, v32

    move-object/from16 v142, v38

    move-object/from16 v3, v45

    move-object/from16 v15, v53

    const/16 v34, 0x4

    const/16 v37, 0x0

    const/16 v40, 0x0

    move-object/from16 v45, v4

    move-object/from16 v4, v47

    move-object/from16 v47, v2

    const/4 v2, 0x1

    move-object/from16 v22, v3

    move-object/from16 v33, v5

    move-object/from16 v20, v6

    move-object/from16 v21, v7

    move-object v3, v9

    move-object/from16 v44, v13

    move/from16 v90, v37

    move-object/from16 v143, v40

    move-object/from16 v144, v143

    move-object/from16 v145, v144

    move-object/from16 v19, v45

    move-object/from16 v14, v48

    move-object/from16 v0, v49

    move-object/from16 v9, v50

    move-object/from16 v1, v51

    move-object/from16 v13, v52

    move-object/from16 v6, v54

    move-object/from16 v7, p1

    move-object v5, v4

    move-object/from16 v4, v47

    .line 451
    :goto_12b
    :try_start_c8
    invoke-static {}, Ljava/time/Instant;->now()Ljava/time/Instant;

    move-result-object v16

    invoke-virtual/range {v16 .. v16}, Ljava/time/Instant;->toString()Ljava/lang/String;

    move-result-object v16
    :try_end_c8
    .catchall {:try_start_c8 .. :try_end_c8} :catchall_72

    .line 452
    :try_start_c9
    iget-object v2, v11, Lcom/bachatas4/android/service/EmulationService;->process:Lcom/bachatas4/android/runtime/process/RuntimeProcessHandle;
    :try_end_c9
    .catchall {:try_start_c9 .. :try_end_c9} :catchall_71

    if-eqz v2, :cond_4b

    :try_start_ca
    invoke-interface {v2}, Lcom/bachatas4/android/runtime/process/RuntimeProcessHandle;->getExitCode()Ljava/lang/Integer;

    move-result-object v2
    :try_end_ca
    .catchall {:try_start_ca .. :try_end_ca} :catchall_64

    goto :goto_12d

    :catchall_64
    move-exception v0

    move-object v14, v5

    move-object v6, v10

    move-object v2, v11

    move-object/from16 v154, v15

    move-object/from16 v12, v19

    move-object/from16 v11, v20

    move-object/from16 v10, v21

    move-object/from16 v13, v22

    move-object/from16 v151, v27

    move-object/from16 v7, v30

    move-object/from16 v9, v31

    move/from16 v1, v34

    move-object/from16 v152, v141

    move-object/from16 v153, v142

    move-object/from16 v3, v143

    move-object/from16 v155, v145

    move-object v5, v4

    move-object v15, v8

    const/4 v8, 0x1

    :goto_12c
    move-object v4, v0

    move-object/from16 v0, v144

    goto/16 :goto_146

    :cond_4b
    move-object/from16 v2, v40

    :goto_12d
    move-object/from16 p1, v3

    :try_start_cb
    iget-object v3, v11, Lcom/bachatas4/android/service/EmulationService;->userRequestedStop:Ljava/util/concurrent/atomic/AtomicBoolean;

    invoke-virtual {v3}, Ljava/util/concurrent/atomic/AtomicBoolean;->get()Z

    move-result v3

    move-object/from16 p2, v7

    new-instance v7, Ljava/lang/StringBuilder;

    invoke-direct {v7}, Ljava/lang/StringBuilder;-><init>()V
    :try_end_cb
    .catchall {:try_start_cb .. :try_end_cb} :catchall_71

    move-object/from16 v32, v8

    :try_start_cc
    const-string v8, "cancelled exitCode="

    invoke-virtual {v7, v8}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v7

    invoke-virtual {v7, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;

    move-result-object v2

    const-string v7, " userStop="

    invoke-virtual {v2, v7}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v2

    invoke-virtual {v2, v3}, Ljava/lang/StringBuilder;->append(Z)Ljava/lang/StringBuilder;

    move-result-object v2

    invoke-virtual {v2}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v2

    invoke-virtual {v4, v15, v2}, Lcom/bachatas4/android/runtime/diagnostics/SessionLog;->info(Ljava/lang/String;Ljava/lang/String;)V

    .line 453
    iget-boolean v2, v1, Lkotlin/jvm/internal/Ref$BooleanRef;->element:Z
    :try_end_cc
    .catchall {:try_start_cc .. :try_end_cc} :catchall_70

    if-nez v2, :cond_4f

    .line 454
    :try_start_cd
    sget-object v2, Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpoint;->SESSION_STOPPING:Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpoint;

    invoke-virtual {v5, v2}, Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpointStore;->mark(Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpoint;)V

    .line 459
    iget-object v2, v12, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v2, Ljava/lang/String;

    .line 461
    iget-object v0, v0, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    move-object v8, v0

    check-cast v8, Ljava/lang/String;

    .line 462
    iget-boolean v0, v6, Lkotlin/jvm/internal/Ref$BooleanRef;->element:Z

    .line 463
    iget-object v3, v9, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v3, Lcom/bachatas4/android/runtime/diagnostics/DiagnosticDriverInfo;

    .line 464
    iget-object v6, v13, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v6, Ljava/lang/String;

    .line 466
    iget-object v7, v11, Lcom/bachatas4/android/service/EmulationService;->process:Lcom/bachatas4/android/runtime/process/RuntimeProcessHandle;
    :try_end_cd
    .catchall {:try_start_cd .. :try_end_cd} :catchall_69

    if-eqz v7, :cond_4c

    :try_start_ce
    invoke-interface {v7}, Lcom/bachatas4/android/runtime/process/RuntimeProcessHandle;->getExitCode()Ljava/lang/Integer;

    move-result-object v7
    :try_end_ce
    .catchall {:try_start_ce .. :try_end_ce} :catchall_65

    move-object v13, v7

    goto :goto_12f

    :catchall_65
    move-exception v0

    move-object v14, v5

    move-object v6, v10

    move-object v2, v11

    move-object/from16 v154, v15

    move-object/from16 v12, v19

    move-object/from16 v11, v20

    move-object/from16 v10, v21

    move-object/from16 v13, v22

    move-object/from16 v151, v27

    move-object/from16 v7, v30

    move-object/from16 v9, v31

    move-object/from16 v15, v32

    move/from16 v1, v34

    move-object/from16 v152, v141

    move-object/from16 v153, v142

    move-object/from16 v3, v143

    move-object/from16 v155, v145

    :goto_12e
    const/4 v8, 0x1

    goto/16 :goto_134

    :cond_4c
    move-object/from16 v13, v40

    :goto_12f
    if-eqz v90, :cond_4d

    const/4 v7, 0x1

    goto :goto_130

    :cond_4d
    move/from16 v7, v37

    .line 468
    :goto_130
    :try_start_cf
    iget-object v9, v14, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v9, Ljava/lang/String;
    :try_end_cf
    .catchall {:try_start_cf .. :try_end_cf} :catchall_69

    const/16 v17, 0x1000

    const/16 v18, 0x0

    move-object/from16 v122, v15

    const/4 v15, 0x0

    move-object v12, v6

    move-object v6, v2

    move-object v2, v11

    move-object v11, v12

    move v14, v7

    move-object/from16 v146, v10

    move-object/from16 v12, v16

    move-object/from16 v147, v30

    move-object/from16 v148, v31

    move-object/from16 v149, v32

    move-object/from16 v150, v122

    move-object/from16 v7, p2

    move-object v10, v3

    move-object/from16 v16, v9

    move-object/from16 v3, p1

    move v9, v0

    .line 455
    :try_start_d0
    invoke-static/range {v2 .. v18}, Lcom/bachatas4/android/service/EmulationService;->buildReportContext$default(Lcom/bachatas4/android/service/EmulationService;Ljava/lang/String;Lcom/bachatas4/android/runtime/diagnostics/SessionLog;Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpointStore;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;ZLcom/bachatas4/android/runtime/diagnostics/DiagnosticDriverInfo;Ljava/lang/String;Ljava/lang/String;Ljava/lang/Integer;ZLjava/lang/String;Ljava/lang/String;ILjava/lang/Object;)Lcom/bachatas4/android/runtime/diagnostics/DiagnosticReportContext;

    move-result-object v0

    .line 470
    sget-object v3, Lcom/bachatas4/android/runtime/session/ManagedSession;->INSTANCE:Lcom/bachatas4/android/runtime/session/ManagedSession;

    .line 471
    new-instance v6, Lcom/bachatas4/android/runtime/session/ManagedSessionState$Stopped;

    .line 472
    iget-object v7, v2, Lcom/bachatas4/android/service/EmulationService;->process:Lcom/bachatas4/android/runtime/process/RuntimeProcessHandle;
    :try_end_d0
    .catchall {:try_start_d0 .. :try_end_d0} :catchall_68

    if-eqz v7, :cond_4e

    :try_start_d1
    invoke-interface {v7}, Lcom/bachatas4/android/runtime/process/RuntimeProcessHandle;->getExitCode()Ljava/lang/Integer;

    move-result-object v7
    :try_end_d1
    .catchall {:try_start_d1 .. :try_end_d1} :catchall_66

    goto :goto_131

    :catchall_66
    move-exception v0

    move-object v14, v5

    move-object/from16 v12, v19

    move-object/from16 v11, v20

    move-object/from16 v10, v21

    move-object/from16 v13, v22

    move-object/from16 v151, v27

    move-object/from16 v152, v141

    move-object/from16 v153, v142

    move-object/from16 v3, v143

    move-object/from16 v155, v145

    move-object/from16 v6, v146

    move-object/from16 v7, v147

    move-object/from16 v9, v148

    move-object/from16 v15, v149

    move-object/from16 v154, v150

    const/4 v1, 0x4

    goto :goto_12e

    :cond_4e
    const/4 v7, 0x0

    .line 473
    :goto_131
    :try_start_d2
    invoke-virtual {v0}, Lcom/bachatas4/android/runtime/diagnostics/DiagnosticReportContext;->getTermination()Lcom/bachatas4/android/runtime/diagnostics/ProcessTerminationInfo;

    move-result-object v8

    .line 471
    invoke-direct {v6, v7, v8, v0}, Lcom/bachatas4/android/runtime/session/ManagedSessionState$Stopped;-><init>(Ljava/lang/Integer;Lcom/bachatas4/android/runtime/diagnostics/ProcessTerminationInfo;Lcom/bachatas4/android/runtime/diagnostics/DiagnosticReportContext;)V

    check-cast v6, Lcom/bachatas4/android/runtime/session/ManagedSessionState;

    .line 470
    invoke-virtual {v3, v6}, Lcom/bachatas4/android/runtime/session/ManagedSession;->update(Lcom/bachatas4/android/runtime/session/ManagedSessionState;)V
    :try_end_d2
    .catchall {:try_start_d2 .. :try_end_d2} :catchall_68

    const/4 v8, 0x1

    .line 477
    :try_start_d3
    iput-boolean v8, v1, Lkotlin/jvm/internal/Ref$BooleanRef;->element:Z
    :try_end_d3
    .catchall {:try_start_d3 .. :try_end_d3} :catchall_67

    goto :goto_135

    :catchall_67
    move-exception v0

    goto :goto_133

    :catchall_68
    move-exception v0

    goto :goto_132

    :catchall_69
    move-exception v0

    move-object/from16 v146, v10

    move-object v2, v11

    move-object/from16 v150, v15

    move-object/from16 v147, v30

    move-object/from16 v148, v31

    move-object/from16 v149, v32

    :goto_132
    const/4 v8, 0x1

    :goto_133
    move-object v14, v5

    move-object/from16 v12, v19

    move-object/from16 v11, v20

    move-object/from16 v10, v21

    move-object/from16 v13, v22

    move-object/from16 v151, v27

    move-object/from16 v152, v141

    move-object/from16 v153, v142

    move-object/from16 v3, v143

    move-object/from16 v155, v145

    move-object/from16 v6, v146

    move-object/from16 v7, v147

    move-object/from16 v9, v148

    move-object/from16 v15, v149

    move-object/from16 v154, v150

    const/4 v1, 0x4

    :goto_134
    move-object v5, v4

    goto/16 :goto_12c

    :cond_4f
    move-object/from16 v146, v10

    move-object v2, v11

    move-object/from16 v150, v15

    move-object/from16 v147, v30

    move-object/from16 v148, v31

    move-object/from16 v149, v32

    const/4 v8, 0x1

    :goto_135
    move-object/from16 v14, v144

    if-eqz v14, :cond_53

    move-object/from16 v15, v149

    .line 512
    invoke-interface {v14, v15}, Ljava/nio/file/Path;->resolve(Ljava/lang/String;)Ljava/nio/file/Path;

    move-result-object v0

    if-eqz v0, :cond_53

    .line 513
    :try_start_d4
    sget-object v1, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    .line 514
    invoke-interface {v0}, Ljava/nio/file/Path;->toFile()Ljava/io/File;

    move-result-object v1

    invoke-virtual {v1}, Ljava/io/File;->isFile()Z

    move-result v1

    if-eqz v1, :cond_50

    .line 517
    invoke-virtual {v4}, Lcom/bachatas4/android/runtime/diagnostics/SessionLog;->getDirectory()Ljava/nio/file/Path;

    move-result-object v1

    move-object/from16 v6, v146

    invoke-interface {v1, v6}, Ljava/nio/file/Path;->resolve(Ljava/lang/String;)Ljava/nio/file/Path;

    move-result-object v1

    .line 518
    new-array v3, v8, [Ljava/nio/file/CopyOption;

    sget-object v6, Ljava/nio/file/StandardCopyOption;->REPLACE_EXISTING:Ljava/nio/file/StandardCopyOption;

    aput-object v6, v3, v37

    .line 515
    invoke-static {v0, v1, v3}, Ljava/nio/file/Files;->copy(Ljava/nio/file/Path;Ljava/nio/file/Path;[Ljava/nio/file/CopyOption;)Ljava/nio/file/Path;

    .line 521
    :cond_50
    sget-object v0, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;

    .line 513
    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v0
    :try_end_d4
    .catchall {:try_start_d4 .. :try_end_d4} :catchall_6a

    goto :goto_136

    :catchall_6a
    move-exception v0

    sget-object v1, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    invoke-static {v0}, Lkotlin/ResultKt;->createFailure(Ljava/lang/Throwable;)Ljava/lang/Object;

    move-result-object v0

    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v0

    .line 521
    :goto_136
    invoke-static {v0}, Lkotlin/Result;->exceptionOrNull-impl(Ljava/lang/Object;)Ljava/lang/Throwable;

    move-result-object v1

    if-eqz v1, :cond_52

    .line 522
    invoke-virtual {v1}, Ljava/lang/Throwable;->getMessage()Ljava/lang/String;

    move-result-object v1

    if-nez v1, :cond_51

    move-object/from16 v1, v35

    :cond_51
    new-instance v3, Ljava/lang/StringBuilder;

    move-object/from16 v7, v147

    invoke-direct {v3, v7}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v3, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v1

    move-object/from16 v9, v148

    invoke-virtual {v4, v9, v1}, Lcom/bachatas4/android/runtime/diagnostics/SessionLog;->warning(Ljava/lang/String;Ljava/lang/String;)V

    .line 523
    :cond_52
    invoke-static {v0}, Lkotlin/Result;->box-impl(Ljava/lang/Object;)Lkotlin/Result;

    :cond_53
    move-object/from16 v12, v143

    if-eqz v12, :cond_55

    move/from16 v7, v37

    const/4 v1, 0x4

    :goto_137
    if-ge v7, v1, :cond_54

    .line 526
    sget-object v0, Lcom/bachatas4/android/runtime/session/ManagedSession;->INSTANCE:Lcom/bachatas4/android/runtime/session/ManagedSession;

    sget-object v3, Lcom/bachatas4/android/runtime/input/ControllerSnapshot;->Companion:Lcom/bachatas4/android/runtime/input/ControllerSnapshot$Companion;

    invoke-virtual {v3}, Lcom/bachatas4/android/runtime/input/ControllerSnapshot$Companion;->getNeutral()Lcom/bachatas4/android/runtime/input/ControllerSnapshot;

    move-result-object v3

    invoke-virtual {v0, v7, v3}, Lcom/bachatas4/android/runtime/session/ManagedSession;->submitController(ILcom/bachatas4/android/runtime/input/ControllerSnapshot;)V

    add-int/lit8 v7, v7, 0x1

    goto :goto_137

    .line 527
    :cond_54
    sget-object v0, Lcom/bachatas4/android/runtime/session/ManagedSession;->INSTANCE:Lcom/bachatas4/android/runtime/session/ManagedSession;

    invoke-virtual {v0, v12}, Lcom/bachatas4/android/runtime/session/ManagedSession;->detachControllerSlotSink(Lkotlin/jvm/functions/Function2;)V

    .line 525
    sget-object v0, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;

    .line 529
    :cond_55
    sget-object v0, Lcom/bachatas4/android/runtime/input/PhoneMotionSource;->INSTANCE:Lcom/bachatas4/android/runtime/input/PhoneMotionSource;

    invoke-virtual {v0}, Lcom/bachatas4/android/runtime/input/PhoneMotionSource;->stop()V

    .line 530
    sget-object v0, Lcom/bachatas4/android/runtime/input/GamepadInputManager;->INSTANCE:Lcom/bachatas4/android/runtime/input/GamepadInputManager;

    invoke-virtual {v0}, Lcom/bachatas4/android/runtime/input/GamepadInputManager;->onSessionEnd()V

    .line 531
    iget-object v0, v2, Lcom/bachatas4/android/service/EmulationService;->process:Lcom/bachatas4/android/runtime/process/RuntimeProcessHandle;

    if-eqz v0, :cond_56

    invoke-interface {v0}, Lcom/bachatas4/android/runtime/process/RuntimeProcessHandle;->getExitCode()Ljava/lang/Integer;

    move-result-object v6

    goto :goto_138

    :cond_56
    const/4 v6, 0x0

    .line 532
    :goto_138
    iget-object v0, v2, Lcom/bachatas4/android/service/EmulationService;->process:Lcom/bachatas4/android/runtime/process/RuntimeProcessHandle;

    if-eqz v0, :cond_57

    invoke-interface {v0}, Lcom/bachatas4/android/runtime/process/RuntimeProcessHandle;->destroyForcibly()V

    sget-object v0, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;

    :cond_57
    const/4 v3, 0x0

    .line 533
    iput-object v3, v2, Lcom/bachatas4/android/service/EmulationService;->process:Lcom/bachatas4/android/runtime/process/RuntimeProcessHandle;

    .line 534
    :try_start_d5
    sget-object v0, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    move-object/from16 v13, v22

    iget-object v0, v13, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v0, Landroid/net/LocalSocket;

    if-eqz v0, :cond_58

    invoke-virtual {v0}, Landroid/net/LocalSocket;->close()V

    sget-object v0, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;

    goto :goto_139

    :cond_58
    move-object v0, v3

    :goto_139
    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;
    :try_end_d5
    .catchall {:try_start_d5 .. :try_end_d5} :catchall_6b

    goto :goto_13a

    :catchall_6b
    move-exception v0

    sget-object v1, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    invoke-static {v0}, Lkotlin/ResultKt;->createFailure(Ljava/lang/Throwable;)Ljava/lang/Object;

    move-result-object v0

    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;

    .line 535
    :goto_13a
    :try_start_d6
    sget-object v0, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    move-object/from16 v10, v21

    iget-object v0, v10, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v0, Landroid/net/LocalServerSocket;

    if-eqz v0, :cond_59

    invoke-virtual {v0}, Landroid/net/LocalServerSocket;->close()V

    sget-object v0, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;

    goto :goto_13b

    :cond_59
    move-object v0, v3

    :goto_13b
    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;
    :try_end_d6
    .catchall {:try_start_d6 .. :try_end_d6} :catchall_6c

    goto :goto_13c

    :catchall_6c
    move-exception v0

    sget-object v1, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    invoke-static {v0}, Lkotlin/ResultKt;->createFailure(Ljava/lang/Throwable;)Ljava/lang/Object;

    move-result-object v0

    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;

    .line 536
    :goto_13c
    :try_start_d7
    sget-object v0, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    move-object/from16 v11, v20

    iget-object v0, v11, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v0, Landroid/net/LocalSocket;

    if-eqz v0, :cond_5a

    invoke-virtual {v0}, Landroid/net/LocalSocket;->close()V

    sget-object v0, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;

    goto :goto_13d

    :cond_5a
    move-object v0, v3

    :goto_13d
    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;
    :try_end_d7
    .catchall {:try_start_d7 .. :try_end_d7} :catchall_6d

    goto :goto_13e

    :catchall_6d
    move-exception v0

    sget-object v1, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    invoke-static {v0}, Lkotlin/ResultKt;->createFailure(Ljava/lang/Throwable;)Ljava/lang/Object;

    move-result-object v0

    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;

    .line 537
    :goto_13e
    invoke-interface/range {v33 .. v33}, Ljava/util/concurrent/ExecutorService;->shutdownNow()Ljava/util/List;

    .line 538
    :try_start_d8
    sget-object v0, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    move-object/from16 v1, v19

    iget-object v0, v1, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v0, Lcom/bachatas4/android/runtime/display/WinlatorEmbeddedXServer;

    if-eqz v0, :cond_5b

    new-instance v1, Lcom/bachatas4/android/service/EmulationService$runSession$16$1$1;

    invoke-direct {v1, v0, v3}, Lcom/bachatas4/android/service/EmulationService$runSession$16$1$1;-><init>(Lcom/bachatas4/android/runtime/display/WinlatorEmbeddedXServer;Lkotlin/coroutines/Continuation;)V

    check-cast v1, Lkotlin/jvm/functions/Function2;

    invoke-static {v3, v1, v8, v3}, Lkotlinx/coroutines/BuildersKt;->runBlockingK$default(Lkotlin/coroutines/CoroutineContext;Lkotlin/jvm/functions/Function2;ILjava/lang/Object;)Ljava/lang/Object;

    sget-object v0, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;

    goto :goto_13f

    :cond_5b
    move-object v0, v3

    :goto_13f
    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;
    :try_end_d8
    .catchall {:try_start_d8 .. :try_end_d8} :catchall_6e

    goto :goto_140

    :catchall_6e
    move-exception v0

    sget-object v1, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    invoke-static {v0}, Lkotlin/ResultKt;->createFailure(Ljava/lang/Throwable;)Ljava/lang/Object;

    move-result-object v0

    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;

    :goto_140
    move-object/from16 v1, v145

    if-eqz v1, :cond_5e

    .line 541
    :try_start_d9
    sget-object v0, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    .line 542
    new-instance v0, Lcom/bachatas4/android/service/EmulationService$runSession$17$1$1;

    invoke-direct {v0, v1, v6, v3}, Lcom/bachatas4/android/service/EmulationService$runSession$17$1$1;-><init>(Lcom/bachatas4/android/runtime/vortek/VortekSessionSupport;Ljava/lang/Integer;Lkotlin/coroutines/Continuation;)V

    check-cast v0, Lkotlin/jvm/functions/Function2;

    invoke-static {v3, v0, v8, v3}, Lkotlinx/coroutines/BuildersKt;->runBlockingK$default(Lkotlin/coroutines/CoroutineContext;Lkotlin/jvm/functions/Function2;ILjava/lang/Object;)Ljava/lang/Object;

    move-result-object v0

    check-cast v0, Lcom/bachatas4/android/runtime/vortek/VortekStopResult;

    .line 541
    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v0
    :try_end_d9
    .catchall {:try_start_d9 .. :try_end_d9} :catchall_6f

    goto :goto_141

    :catchall_6f
    move-exception v0

    sget-object v1, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    invoke-static {v0}, Lkotlin/ResultKt;->createFailure(Ljava/lang/Throwable;)Ljava/lang/Object;

    move-result-object v0

    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v0

    .line 543
    :goto_141
    invoke-static {v0}, Lkotlin/Result;->exceptionOrNull-impl(Ljava/lang/Object;)Ljava/lang/Throwable;

    move-result-object v1

    if-eqz v1, :cond_5d

    .line 544
    invoke-virtual {v1}, Ljava/lang/Throwable;->getMessage()Ljava/lang/String;

    move-result-object v1

    if-nez v1, :cond_5c

    move-object/from16 v1, v35

    :cond_5c
    new-instance v3, Ljava/lang/StringBuilder;

    move-object/from16 v6, v27

    invoke-direct {v3, v6}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v3, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v1

    move-object/from16 v3, v142

    invoke-virtual {v4, v3, v1}, Lcom/bachatas4/android/runtime/diagnostics/SessionLog;->warning(Ljava/lang/String;Ljava/lang/String;)V

    .line 545
    :cond_5d
    invoke-static {v0}, Lkotlin/Result;->box-impl(Ljava/lang/Object;)Lkotlin/Result;

    .line 547
    :cond_5e
    invoke-virtual/range {v44 .. v44}, Ljava/io/File;->delete()Z

    .line 548
    sget-object v0, Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpoint;->SESSION_FINISHED:Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpoint;

    invoke-virtual {v5, v0}, Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpointStore;->mark(Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpoint;)V

    move-object/from16 v1, v141

    move-object/from16 v3, v150

    .line 549
    :goto_142
    invoke-virtual {v4, v3, v1}, Lcom/bachatas4/android/runtime/diagnostics/SessionLog;->info(Ljava/lang/String;Ljava/lang/String;)V

    .line 550
    invoke-virtual {v2}, Lcom/bachatas4/android/service/EmulationService;->stopSelf()V

    .line 552
    :goto_143
    sget-object v0, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;

    return-object v0

    :catchall_70
    move-exception v0

    move-object v6, v10

    move-object v2, v11

    move-object/from16 v154, v15

    move-object/from16 v11, v20

    move-object/from16 v10, v21

    move-object/from16 v13, v22

    move-object/from16 v151, v27

    move-object/from16 v7, v30

    move-object/from16 v9, v31

    move-object/from16 v15, v32

    move/from16 v1, v34

    move-object/from16 v3, v40

    move-object/from16 v152, v141

    move-object/from16 v153, v142

    move-object/from16 v12, v143

    move-object/from16 v14, v144

    move-object/from16 v40, v145

    const/4 v8, 0x1

    goto :goto_144

    :catchall_71
    move-exception v0

    move-object v6, v10

    move-object v2, v11

    move-object/from16 v154, v15

    move-object/from16 v11, v20

    move-object/from16 v10, v21

    move-object/from16 v13, v22

    move-object/from16 v151, v27

    move-object/from16 v7, v30

    move-object/from16 v9, v31

    move/from16 v1, v34

    move-object/from16 v3, v40

    move-object/from16 v152, v141

    move-object/from16 v153, v142

    move-object/from16 v12, v143

    move-object/from16 v14, v144

    move-object/from16 v40, v145

    move-object v15, v8

    move-object/from16 v20, v19

    const/4 v8, 0x1

    goto :goto_145

    :catchall_72
    move-exception v0

    move-object v6, v10

    move-object/from16 v154, v15

    move-object/from16 v10, v21

    move-object/from16 v13, v22

    move-object/from16 v151, v27

    move-object/from16 v7, v30

    move-object/from16 v9, v31

    move/from16 v1, v34

    move-object/from16 v3, v40

    move-object/from16 v152, v141

    move-object/from16 v153, v142

    move-object/from16 v12, v143

    move-object/from16 v14, v144

    move-object/from16 v40, v145

    move-object v15, v8

    move v8, v2

    move-object v2, v11

    move-object/from16 v11, v20

    :goto_144
    move-object/from16 v20, v19

    :goto_145
    move-object v3, v4

    move-object v4, v0

    move-object v0, v14

    move-object v14, v5

    move-object v5, v3

    move-object v3, v12

    move-object/from16 v12, v20

    move-object/from16 v155, v40

    :goto_146
    if-eqz v0, :cond_62

    .line 512
    invoke-interface {v0, v15}, Ljava/nio/file/Path;->resolve(Ljava/lang/String;)Ljava/nio/file/Path;

    move-result-object v0

    if-eqz v0, :cond_62

    .line 513
    :try_start_da
    sget-object v15, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    .line 514
    invoke-interface {v0}, Ljava/nio/file/Path;->toFile()Ljava/io/File;

    move-result-object v15

    invoke-virtual {v15}, Ljava/io/File;->isFile()Z

    move-result v15

    if-eqz v15, :cond_5f

    .line 517
    invoke-virtual {v5}, Lcom/bachatas4/android/runtime/diagnostics/SessionLog;->getDirectory()Ljava/nio/file/Path;

    move-result-object v15

    invoke-interface {v15, v6}, Ljava/nio/file/Path;->resolve(Ljava/lang/String;)Ljava/nio/file/Path;

    move-result-object v6

    .line 518
    new-array v15, v8, [Ljava/nio/file/CopyOption;

    sget-object v16, Ljava/nio/file/StandardCopyOption;->REPLACE_EXISTING:Ljava/nio/file/StandardCopyOption;

    aput-object v16, v15, v37

    .line 515
    invoke-static {v0, v6, v15}, Ljava/nio/file/Files;->copy(Ljava/nio/file/Path;Ljava/nio/file/Path;[Ljava/nio/file/CopyOption;)Ljava/nio/file/Path;

    .line 521
    :cond_5f
    sget-object v0, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;

    .line 513
    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v0
    :try_end_da
    .catchall {:try_start_da .. :try_end_da} :catchall_73

    goto :goto_147

    :catchall_73
    move-exception v0

    sget-object v6, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    invoke-static {v0}, Lkotlin/ResultKt;->createFailure(Ljava/lang/Throwable;)Ljava/lang/Object;

    move-result-object v0

    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v0

    .line 521
    :goto_147
    invoke-static {v0}, Lkotlin/Result;->exceptionOrNull-impl(Ljava/lang/Object;)Ljava/lang/Throwable;

    move-result-object v6

    if-eqz v6, :cond_61

    .line 522
    invoke-virtual {v6}, Ljava/lang/Throwable;->getMessage()Ljava/lang/String;

    move-result-object v6

    if-nez v6, :cond_60

    move-object/from16 v6, v35

    :cond_60
    new-instance v15, Ljava/lang/StringBuilder;

    invoke-direct {v15, v7}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v15, v6}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v6

    invoke-virtual {v6}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v6

    invoke-virtual {v5, v9, v6}, Lcom/bachatas4/android/runtime/diagnostics/SessionLog;->warning(Ljava/lang/String;Ljava/lang/String;)V

    .line 523
    :cond_61
    invoke-static {v0}, Lkotlin/Result;->box-impl(Ljava/lang/Object;)Lkotlin/Result;

    :cond_62
    if-eqz v3, :cond_64

    move/from16 v7, v37

    :goto_148
    if-ge v7, v1, :cond_63

    .line 526
    sget-object v0, Lcom/bachatas4/android/runtime/session/ManagedSession;->INSTANCE:Lcom/bachatas4/android/runtime/session/ManagedSession;

    sget-object v6, Lcom/bachatas4/android/runtime/input/ControllerSnapshot;->Companion:Lcom/bachatas4/android/runtime/input/ControllerSnapshot$Companion;

    invoke-virtual {v6}, Lcom/bachatas4/android/runtime/input/ControllerSnapshot$Companion;->getNeutral()Lcom/bachatas4/android/runtime/input/ControllerSnapshot;

    move-result-object v6

    invoke-virtual {v0, v7, v6}, Lcom/bachatas4/android/runtime/session/ManagedSession;->submitController(ILcom/bachatas4/android/runtime/input/ControllerSnapshot;)V

    add-int/lit8 v7, v7, 0x1

    goto :goto_148

    .line 527
    :cond_63
    sget-object v0, Lcom/bachatas4/android/runtime/session/ManagedSession;->INSTANCE:Lcom/bachatas4/android/runtime/session/ManagedSession;

    invoke-virtual {v0, v3}, Lcom/bachatas4/android/runtime/session/ManagedSession;->detachControllerSlotSink(Lkotlin/jvm/functions/Function2;)V

    .line 525
    sget-object v0, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;

    .line 529
    :cond_64
    sget-object v0, Lcom/bachatas4/android/runtime/input/PhoneMotionSource;->INSTANCE:Lcom/bachatas4/android/runtime/input/PhoneMotionSource;

    invoke-virtual {v0}, Lcom/bachatas4/android/runtime/input/PhoneMotionSource;->stop()V

    .line 530
    sget-object v0, Lcom/bachatas4/android/runtime/input/GamepadInputManager;->INSTANCE:Lcom/bachatas4/android/runtime/input/GamepadInputManager;

    invoke-virtual {v0}, Lcom/bachatas4/android/runtime/input/GamepadInputManager;->onSessionEnd()V

    .line 531
    iget-object v0, v2, Lcom/bachatas4/android/service/EmulationService;->process:Lcom/bachatas4/android/runtime/process/RuntimeProcessHandle;

    if-eqz v0, :cond_65

    invoke-interface {v0}, Lcom/bachatas4/android/runtime/process/RuntimeProcessHandle;->getExitCode()Ljava/lang/Integer;

    move-result-object v6

    goto :goto_149

    :cond_65
    const/4 v6, 0x0

    .line 532
    :goto_149
    iget-object v0, v2, Lcom/bachatas4/android/service/EmulationService;->process:Lcom/bachatas4/android/runtime/process/RuntimeProcessHandle;

    if-eqz v0, :cond_66

    invoke-interface {v0}, Lcom/bachatas4/android/runtime/process/RuntimeProcessHandle;->destroyForcibly()V

    sget-object v0, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;

    :cond_66
    const/4 v3, 0x0

    .line 533
    iput-object v3, v2, Lcom/bachatas4/android/service/EmulationService;->process:Lcom/bachatas4/android/runtime/process/RuntimeProcessHandle;

    .line 534
    :try_start_db
    sget-object v0, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    iget-object v0, v13, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v0, Landroid/net/LocalSocket;

    if-eqz v0, :cond_67

    invoke-virtual {v0}, Landroid/net/LocalSocket;->close()V

    sget-object v0, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;

    goto :goto_14a

    :cond_67
    const/4 v0, 0x0

    :goto_14a
    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;
    :try_end_db
    .catchall {:try_start_db .. :try_end_db} :catchall_74

    goto :goto_14b

    :catchall_74
    move-exception v0

    sget-object v1, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    invoke-static {v0}, Lkotlin/ResultKt;->createFailure(Ljava/lang/Throwable;)Ljava/lang/Object;

    move-result-object v0

    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;

    .line 535
    :goto_14b
    :try_start_dc
    sget-object v0, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    iget-object v0, v10, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v0, Landroid/net/LocalServerSocket;

    if-eqz v0, :cond_68

    invoke-virtual {v0}, Landroid/net/LocalServerSocket;->close()V

    sget-object v0, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;

    goto :goto_14c

    :cond_68
    const/4 v0, 0x0

    :goto_14c
    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;
    :try_end_dc
    .catchall {:try_start_dc .. :try_end_dc} :catchall_75

    goto :goto_14d

    :catchall_75
    move-exception v0

    sget-object v1, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    invoke-static {v0}, Lkotlin/ResultKt;->createFailure(Ljava/lang/Throwable;)Ljava/lang/Object;

    move-result-object v0

    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;

    .line 536
    :goto_14d
    :try_start_dd
    sget-object v0, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    iget-object v0, v11, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v0, Landroid/net/LocalSocket;

    if-eqz v0, :cond_69

    invoke-virtual {v0}, Landroid/net/LocalSocket;->close()V

    sget-object v0, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;

    goto :goto_14e

    :cond_69
    const/4 v0, 0x0

    :goto_14e
    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;
    :try_end_dd
    .catchall {:try_start_dd .. :try_end_dd} :catchall_76

    goto :goto_14f

    :catchall_76
    move-exception v0

    sget-object v1, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    invoke-static {v0}, Lkotlin/ResultKt;->createFailure(Ljava/lang/Throwable;)Ljava/lang/Object;

    move-result-object v0

    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;

    .line 537
    :goto_14f
    invoke-interface/range {v33 .. v33}, Ljava/util/concurrent/ExecutorService;->shutdownNow()Ljava/util/List;

    .line 538
    :try_start_de
    sget-object v0, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    iget-object v0, v12, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v0, Lcom/bachatas4/android/runtime/display/WinlatorEmbeddedXServer;

    if-eqz v0, :cond_6a

    new-instance v1, Lcom/bachatas4/android/service/EmulationService$runSession$16$1$1;

    const/4 v12, 0x0

    invoke-direct {v1, v0, v12}, Lcom/bachatas4/android/service/EmulationService$runSession$16$1$1;-><init>(Lcom/bachatas4/android/runtime/display/WinlatorEmbeddedXServer;Lkotlin/coroutines/Continuation;)V

    check-cast v1, Lkotlin/jvm/functions/Function2;

    invoke-static {v12, v1, v8, v12}, Lkotlinx/coroutines/BuildersKt;->runBlockingK$default(Lkotlin/coroutines/CoroutineContext;Lkotlin/jvm/functions/Function2;ILjava/lang/Object;)Ljava/lang/Object;

    sget-object v0, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;

    goto :goto_150

    :cond_6a
    const/4 v0, 0x0

    :goto_150
    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;
    :try_end_de
    .catchall {:try_start_de .. :try_end_de} :catchall_77

    goto :goto_151

    :catchall_77
    move-exception v0

    sget-object v1, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    invoke-static {v0}, Lkotlin/ResultKt;->createFailure(Ljava/lang/Throwable;)Ljava/lang/Object;

    move-result-object v0

    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;

    :goto_151
    move-object/from16 v7, v155

    if-eqz v7, :cond_6d

    .line 541
    :try_start_df
    sget-object v0, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    .line 542
    new-instance v0, Lcom/bachatas4/android/service/EmulationService$runSession$17$1$1;

    const/4 v12, 0x0

    invoke-direct {v0, v7, v6, v12}, Lcom/bachatas4/android/service/EmulationService$runSession$17$1$1;-><init>(Lcom/bachatas4/android/runtime/vortek/VortekSessionSupport;Ljava/lang/Integer;Lkotlin/coroutines/Continuation;)V

    check-cast v0, Lkotlin/jvm/functions/Function2;

    invoke-static {v12, v0, v8, v12}, Lkotlinx/coroutines/BuildersKt;->runBlockingK$default(Lkotlin/coroutines/CoroutineContext;Lkotlin/jvm/functions/Function2;ILjava/lang/Object;)Ljava/lang/Object;

    move-result-object v0

    check-cast v0, Lcom/bachatas4/android/runtime/vortek/VortekStopResult;

    .line 541
    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v0
    :try_end_df
    .catchall {:try_start_df .. :try_end_df} :catchall_78

    goto :goto_152

    :catchall_78
    move-exception v0

    sget-object v1, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    invoke-static {v0}, Lkotlin/ResultKt;->createFailure(Ljava/lang/Throwable;)Ljava/lang/Object;

    move-result-object v0

    invoke-static {v0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;

    move-result-object v0

    .line 543
    :goto_152
    invoke-static {v0}, Lkotlin/Result;->exceptionOrNull-impl(Ljava/lang/Object;)Ljava/lang/Throwable;

    move-result-object v1

    if-eqz v1, :cond_6c

    .line 544
    invoke-virtual {v1}, Ljava/lang/Throwable;->getMessage()Ljava/lang/String;

    move-result-object v1

    if-nez v1, :cond_6b

    move-object/from16 v1, v35

    :cond_6b
    new-instance v3, Ljava/lang/StringBuilder;

    move-object/from16 v6, v151

    invoke-direct {v3, v6}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {v3, v1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object v1

    invoke-virtual {v1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object v1

    move-object/from16 v3, v153

    invoke-virtual {v5, v3, v1}, Lcom/bachatas4/android/runtime/diagnostics/SessionLog;->warning(Ljava/lang/String;Ljava/lang/String;)V

    .line 545
    :cond_6c
    invoke-static {v0}, Lkotlin/Result;->box-impl(Ljava/lang/Object;)Lkotlin/Result;

    .line 547
    :cond_6d
    invoke-virtual/range {v44 .. v44}, Ljava/io/File;->delete()Z

    .line 548
    sget-object v0, Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpoint;->SESSION_FINISHED:Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpoint;

    invoke-virtual {v14, v0}, Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpointStore;->mark(Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpoint;)V

    move-object/from16 v1, v152

    move-object/from16 v3, v154

    .line 549
    invoke-virtual {v5, v3, v1}, Lcom/bachatas4/android/runtime/diagnostics/SessionLog;->info(Ljava/lang/String;Ljava/lang/String;)V

    .line 550
    invoke-virtual {v2}, Lcom/bachatas4/android/service/EmulationService;->stopSelf()V

    throw v4
.end method

.method static final runSession$lambda$10(Lcom/bachatas4/android/runtime/diagnostics/SessionLog;Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpointStore;Lcom/bachatas4/android/service/EmulationService;Ljava/lang/String;Lkotlin/jvm/internal/Ref$BooleanRef;Lcom/bachatas4/android/runtime/session/FrameTelemetryReporter;Ljava/lang/String;Lkotlin/jvm/internal/Ref$ObjectRef;Lkotlin/jvm/internal/Ref$ObjectRef;Lkotlin/jvm/internal/Ref$ObjectRef;Lkotlin/jvm/internal/Ref$ObjectRef;Lkotlin/jvm/internal/Ref$ObjectRef;Lkotlin/jvm/internal/Ref$BooleanRef;Ljava/util/concurrent/atomic/AtomicReference;Ljava/lang/String;)Lkotlin/Unit;
    .locals 19

    move-object/from16 v2, p0

    move-object/from16 v3, p1

    move-object/from16 v0, p2

    move-object/from16 v1, p4

    move-object/from16 v15, p14

    const-string v4, "frame"

    invoke-static {v15, v4}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullParameter(Ljava/lang/Object;Ljava/lang/String;)V

    .line 368
    const-string v4, "BACHATA/1 EVENT Running"

    invoke-static {v15, v4}, Lkotlin/jvm/internal/Intrinsics;->areEqual(Ljava/lang/Object;Ljava/lang/Object;)Z

    move-result v4

    if-eqz v4, :cond_0

    .line 369
    const-string v1, "Session"

    const-string v4, "backend reported Running"

    invoke-virtual {v2, v1, v4}, Lcom/bachatas4/android/runtime/diagnostics/SessionLog;->info(Ljava/lang/String;Ljava/lang/String;)V

    .line 370
    sget-object v1, Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpoint;->SHADPS4_RUNNING:Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpoint;

    invoke-virtual {v3, v1}, Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpointStore;->mark(Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpoint;)V

    .line 373
    sget-object v1, Lcom/bachatas4/android/runtime/input/PhoneMotionSource;->INSTANCE:Lcom/bachatas4/android/runtime/input/PhoneMotionSource;

    check-cast v0, Landroid/content/Context;

    new-instance v2, Lcom/bachatas4/android/service/EmulationService$$ExternalSyntheticLambda6;

    move-object/from16 v3, p13

    invoke-direct {v2, v3}, Lcom/bachatas4/android/service/EmulationService$$ExternalSyntheticLambda6;-><init>(Ljava/util/concurrent/atomic/AtomicReference;)V

    invoke-virtual {v1, v0, v2}, Lcom/bachatas4/android/runtime/input/PhoneMotionSource;->start(Landroid/content/Context;Lkotlin/jvm/functions/Function1;)V

    .line 378
    sget-object v0, Lcom/bachatas4/android/runtime/session/ManagedSession;->INSTANCE:Lcom/bachatas4/android/runtime/session/ManagedSession;

    new-instance v1, Lcom/bachatas4/android/runtime/session/ManagedSessionState$Running;

    move-object/from16 v5, p3

    invoke-direct {v1, v5}, Lcom/bachatas4/android/runtime/session/ManagedSessionState$Running;-><init>(Ljava/lang/String;)V

    check-cast v1, Lcom/bachatas4/android/runtime/session/ManagedSessionState;

    invoke-virtual {v0, v1}, Lcom/bachatas4/android/runtime/session/ManagedSession;->update(Lcom/bachatas4/android/runtime/session/ManagedSessionState;)V

    goto/16 :goto_1

    :cond_0
    move-object/from16 v5, p3

    .line 380
    const-string v4, "BACHATA/1 EVENT Frame"

    invoke-static {v15, v4}, Lkotlin/jvm/internal/Intrinsics;->areEqual(Ljava/lang/Object;Ljava/lang/Object;)Z

    move-result v4

    const/4 v6, 0x1

    if-eqz v4, :cond_2

    .line 381
    invoke-static {}, Ljava/lang/System;->nanoTime()J

    move-result-wide v4

    .line 382
    iget-boolean v0, v1, Lkotlin/jvm/internal/Ref$BooleanRef;->element:Z

    if-nez v0, :cond_1

    .line 383
    iput-boolean v6, v1, Lkotlin/jvm/internal/Ref$BooleanRef;->element:Z

    .line 384
    sget-object v0, Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpoint;->FIRST_FRAME_SUBMITTED:Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpoint;

    invoke-virtual {v3, v0}, Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpointStore;->mark(Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpoint;)V

    .line 385
    sget-object v0, Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpoint;->FIRST_FRAME_PRESENTED:Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpoint;

    invoke-virtual {v3, v0}, Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpointStore;->mark(Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpoint;)V

    .line 387
    :cond_1
    sget-object v0, Lcom/bachatas4/android/runtime/session/ManagedSession;->INSTANCE:Lcom/bachatas4/android/runtime/session/ManagedSession;

    invoke-virtual {v0, v4, v5}, Lcom/bachatas4/android/runtime/session/ManagedSession;->recordPresentedFrame(J)V

    .line 388
    sget-object v0, Lcom/bachatas4/android/runtime/session/ManagedSession;->INSTANCE:Lcom/bachatas4/android/runtime/session/ManagedSession;

    invoke-virtual {v0}, Lcom/bachatas4/android/runtime/session/ManagedSession;->getFrameTelemetry()Lkotlinx/coroutines/flow/StateFlow;

    move-result-object v0

    invoke-interface {v0}, Lkotlinx/coroutines/flow/StateFlow;->getValue()Ljava/lang/Object;

    move-result-object v0

    check-cast v0, Lcom/bachatas4/android/runtime/session/FrameTelemetry;

    move-object/from16 v1, p5

    invoke-virtual {v1, v4, v5, v0}, Lcom/bachatas4/android/runtime/session/FrameTelemetryReporter;->record(JLcom/bachatas4/android/runtime/session/FrameTelemetry;)Lcom/bachatas4/android/runtime/session/FrameTelemetrySample;

    move-result-object v0

    if-eqz v0, :cond_4

    .line 389
    const-string v1, "Performance"

    invoke-virtual {v0}, Lcom/bachatas4/android/runtime/session/FrameTelemetrySample;->logLine()Ljava/lang/String;

    move-result-object v0

    invoke-virtual {v2, v1, v0}, Lcom/bachatas4/android/runtime/diagnostics/SessionLog;->info(Ljava/lang/String;Ljava/lang/String;)V

    goto/16 :goto_1

    .line 392
    :cond_2
    const-string v4, "BACHATA/1 ERROR code"

    const/4 v7, 0x0

    const/4 v8, 0x2

    const/4 v9, 0x0

    invoke-static {v15, v4, v7, v8, v9}, Lkotlin/text/StringsKt;->startsWith$default(Ljava/lang/String;Ljava/lang/String;ZILjava/lang/Object;)Z

    move-result v4

    if-eqz v4, :cond_4

    .line 393
    const-string v4, "Backend"

    invoke-virtual {v2, v4, v15}, Lcom/bachatas4/android/runtime/diagnostics/SessionLog;->error(Ljava/lang/String;Ljava/lang/String;)V

    move-object/from16 v4, p7

    .line 398
    iget-object v4, v4, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v4, Ljava/lang/String;

    move-object/from16 v7, p8

    .line 400
    iget-object v7, v7, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v7, Ljava/lang/String;

    .line 401
    iget-boolean v1, v1, Lkotlin/jvm/internal/Ref$BooleanRef;->element:Z

    move-object/from16 v10, p9

    .line 402
    iget-object v10, v10, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v10, Lcom/bachatas4/android/runtime/diagnostics/DiagnosticDriverInfo;

    move-object/from16 v11, p10

    .line 403
    iget-object v11, v11, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v11, Ljava/lang/String;

    .line 404
    invoke-static {}, Ljava/time/Instant;->now()Ljava/time/Instant;

    move-result-object v12

    invoke-virtual {v12}, Ljava/time/Instant;->toString()Ljava/lang/String;

    move-result-object v12

    .line 405
    iget-object v13, v0, Lcom/bachatas4/android/service/EmulationService;->process:Lcom/bachatas4/android/runtime/process/RuntimeProcessHandle;

    if-eqz v13, :cond_3

    invoke-interface {v13}, Lcom/bachatas4/android/runtime/process/RuntimeProcessHandle;->getExitCode()Ljava/lang/Integer;

    move-result-object v13

    goto :goto_0

    :cond_3
    move-object v13, v9

    .line 407
    :goto_0
    const-string v14, "code="

    move-object/from16 v16, v11

    move-object v11, v13

    invoke-static {v15, v14, v9, v8, v9}, Lkotlin/text/StringsKt;->substringAfter$default(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;ILjava/lang/Object;)Ljava/lang/String;

    move-result-object v13

    move-object/from16 v6, p11

    .line 408
    iget-object v6, v6, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast v6, Ljava/lang/String;

    move/from16 v17, v8

    move-object v8, v10

    move-object v10, v12

    const/4 v12, 0x0

    move-object/from16 v18, v14

    move-object/from16 v9, v16

    move-object v14, v6

    move-object v6, v7

    move v7, v1

    move-object/from16 v1, p6

    .line 394
    invoke-direct/range {v0 .. v14}, Lcom/bachatas4/android/service/EmulationService;->buildReportContext(Ljava/lang/String;Lcom/bachatas4/android/runtime/diagnostics/SessionLog;Lcom/bachatas4/android/runtime/diagnostics/DiagnosticCheckpointStore;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;ZLcom/bachatas4/android/runtime/diagnostics/DiagnosticDriverInfo;Ljava/lang/String;Ljava/lang/String;Ljava/lang/Integer;ZLjava/lang/String;Ljava/lang/String;)Lcom/bachatas4/android/runtime/diagnostics/DiagnosticReportContext;

    move-result-object v0

    .line 410
    sget-object v1, Lcom/bachatas4/android/runtime/session/ManagedSession;->INSTANCE:Lcom/bachatas4/android/runtime/session/ManagedSession;

    .line 411
    new-instance v2, Lcom/bachatas4/android/runtime/session/ManagedSessionState$Failed;

    .line 412
    sget-object v3, Lcom/bachatas4/android/model/RuntimeErrorCode;->CONTENT_INVALID:Lcom/bachatas4/android/model/RuntimeErrorCode;

    move-object/from16 v4, v18

    const/4 v5, 0x2

    const/4 v6, 0x0

    .line 413
    invoke-static {v15, v4, v6, v5, v6}, Lkotlin/text/StringsKt;->substringAfter$default(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;ILjava/lang/Object;)Ljava/lang/String;

    move-result-object v4

    .line 411
    invoke-direct {v2, v3, v4, v0}, Lcom/bachatas4/android/runtime/session/ManagedSessionState$Failed;-><init>(Lcom/bachatas4/android/model/RuntimeErrorCode;Ljava/lang/String;Lcom/bachatas4/android/runtime/diagnostics/DiagnosticReportContext;)V

    check-cast v2, Lcom/bachatas4/android/runtime/session/ManagedSessionState;

    .line 410
    invoke-virtual {v1, v2}, Lcom/bachatas4/android/runtime/session/ManagedSession;->update(Lcom/bachatas4/android/runtime/session/ManagedSessionState;)V

    move-object/from16 v0, p12

    const/4 v1, 0x1

    .line 417
    iput-boolean v1, v0, Lkotlin/jvm/internal/Ref$BooleanRef;->element:Z

    .line 420
    :cond_4
    :goto_1
    sget-object v0, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;

    return-object v0
.end method

.method private static final runSession$lambda$10$0(Ljava/util/concurrent/atomic/AtomicReference;Lcom/bachatas4/android/runtime/input/ControllerMotion;)Lkotlin/Unit;
    .locals 1

    const-string v0, "motion"

    invoke-static {p1, v0}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullParameter(Ljava/lang/Object;Ljava/lang/String;)V

    .line 376
    sget-object v0, Lcom/bachatas4/android/runtime/session/ManagedSession;->INSTANCE:Lcom/bachatas4/android/runtime/session/ManagedSession;

    invoke-virtual {p0}, Ljava/util/concurrent/atomic/AtomicReference;->get()Ljava/lang/Object;

    move-result-object p0

    check-cast p0, Lcom/bachatas4/android/runtime/input/ControllerSnapshot;

    invoke-virtual {p0, p1}, Lcom/bachatas4/android/runtime/input/ControllerSnapshot;->withMotion(Lcom/bachatas4/android/runtime/input/ControllerMotion;)Lcom/bachatas4/android/runtime/input/ControllerSnapshot;

    move-result-object p0

    const/4 p1, 0x0

    invoke-virtual {v0, p1, p0}, Lcom/bachatas4/android/runtime/session/ManagedSession;->submitController(ILcom/bachatas4/android/runtime/input/ControllerSnapshot;)V

    .line 377
    sget-object p0, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;

    return-object p0
.end method

.method static final runSession$lambda$6(Lcom/bachatas4/android/runtime/diagnostics/SessionLog;Ljava/lang/String;Ljava/lang/String;)Lkotlin/Unit;
    .locals 1

    const-string v0, "tag"

    invoke-static {p1, v0}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullParameter(Ljava/lang/Object;Ljava/lang/String;)V

    const-string v0, "msg"

    invoke-static {p2, v0}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullParameter(Ljava/lang/Object;Ljava/lang/String;)V

    .line 219
    const-string v0, "Bachata.Vortek"

    invoke-static {p1, v0}, Lkotlin/jvm/internal/Intrinsics;->areEqual(Ljava/lang/Object;Ljava/lang/Object;)Z

    move-result v0

    if-eqz v0, :cond_0

    const-string p1, "Vortek"

    .line 220
    :cond_0
    invoke-virtual {p0, p1, p2}, Lcom/bachatas4/android/runtime/diagnostics/SessionLog;->info(Ljava/lang/String;Ljava/lang/String;)V

    .line 221
    sget-object p0, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;

    return-object p0
.end method

.method static final runSession$lambda$7(Lkotlin/jvm/internal/Ref$ObjectRef;)Landroid/net/LocalSocket;
    .locals 0

    .line 326
    iget-object p0, p0, Lkotlin/jvm/internal/Ref$ObjectRef;->element:Ljava/lang/Object;

    check-cast p0, Landroid/net/LocalServerSocket;

    invoke-virtual {p0}, Landroid/net/LocalServerSocket;->accept()Landroid/net/LocalSocket;

    move-result-object p0

    return-object p0
.end method

.method static final runSession$lambda$9(Ljava/util/concurrent/atomic/AtomicReference;[JLcom/bachatas4/android/runtime/diagnostics/SessionLog;Lcom/bachatas4/android/runtime/input/ControllerFrameEncoder;Lcom/bachatas4/android/service/EmulationService;Ljava/lang/Object;Ljava/io/OutputStream;ILcom/bachatas4/android/runtime/input/ControllerSnapshot;)Lkotlin/Unit;
    .locals 4

    const-string p4, "snapshot"

    invoke-static {p8, p4}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullParameter(Ljava/lang/Object;Ljava/lang/String;)V

    if-nez p7, :cond_0

    .line 344
    invoke-virtual {p8}, Lcom/bachatas4/android/runtime/input/ControllerSnapshot;->withoutMotion()Lcom/bachatas4/android/runtime/input/ControllerSnapshot;

    move-result-object p4

    invoke-virtual {p0, p4}, Ljava/util/concurrent/atomic/AtomicReference;->set(Ljava/lang/Object;)V

    .line 345
    :cond_0
    invoke-virtual {p8}, Lcom/bachatas4/android/runtime/input/ControllerSnapshot;->getButtons()J

    move-result-wide v0

    aget-wide v2, p1, p7

    cmp-long p0, v0, v2

    if-eqz p0, :cond_1

    .line 346
    invoke-virtual {p8}, Lcom/bachatas4/android/runtime/input/ControllerSnapshot;->getButtons()J

    move-result-wide v0

    aput-wide v0, p1, p7

    .line 347
    const-string p0, "Input"

    invoke-virtual {p8}, Lcom/bachatas4/android/runtime/input/ControllerSnapshot;->getButtons()J

    move-result-wide v0

    new-instance p1, Ljava/lang/StringBuilder;

    const-string p4, "slot="

    invoke-direct {p1, p4}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {p1, p7}, Ljava/lang/StringBuilder;->append(I)Ljava/lang/StringBuilder;

    move-result-object p1

    const-string p4, " buttons="

    invoke-virtual {p1, p4}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p1

    invoke-virtual {p1, v0, v1}, Ljava/lang/StringBuilder;->append(J)Ljava/lang/StringBuilder;

    move-result-object p1

    invoke-virtual {p1}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p1

    invoke-virtual {p2, p0, p1}, Lcom/bachatas4/android/runtime/diagnostics/SessionLog;->info(Ljava/lang/String;Ljava/lang/String;)V

    :cond_1
    if-nez p7, :cond_2

    .line 350
    sget-object p0, Lcom/bachatas4/android/runtime/input/PhoneMotionSource;->INSTANCE:Lcom/bachatas4/android/runtime/input/PhoneMotionSource;

    invoke-virtual {p0}, Lcom/bachatas4/android/runtime/input/PhoneMotionSource;->getCurrent()Lcom/bachatas4/android/runtime/input/ControllerMotion;

    move-result-object p0

    invoke-virtual {p8, p0}, Lcom/bachatas4/android/runtime/input/ControllerSnapshot;->withMotion(Lcom/bachatas4/android/runtime/input/ControllerMotion;)Lcom/bachatas4/android/runtime/input/ControllerSnapshot;

    move-result-object p8

    .line 354
    :cond_2
    invoke-virtual {p3, p7, p8}, Lcom/bachatas4/android/runtime/input/ControllerFrameEncoder;->encode(ILcom/bachatas4/android/runtime/input/ControllerSnapshot;)[B

    move-result-object p0

    if-eqz p0, :cond_3

    .line 355
    :try_start_0
    sget-object p1, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    .line 356
    monitor-enter p5
    :try_end_0
    .catchall {:try_start_0 .. :try_end_0} :catchall_1

    .line 357
    :try_start_1
    invoke-virtual {p6, p0}, Ljava/io/OutputStream;->write([B)V

    .line 358
    invoke-virtual {p6}, Ljava/io/OutputStream;->flush()V

    .line 359
    sget-object p0, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;
    :try_end_1
    .catchall {:try_start_1 .. :try_end_1} :catchall_0

    .line 356
    :try_start_2
    monitor-exit p5

    .line 360
    sget-object p0, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;

    .line 355
    invoke-static {p0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;

    goto :goto_0

    :catchall_0
    move-exception p0

    .line 356
    monitor-exit p5

    throw p0
    :try_end_2
    .catchall {:try_start_2 .. :try_end_2} :catchall_1

    :catchall_1
    move-exception p0

    .line 355
    sget-object p1, Lkotlin/Result;->Companion:Lkotlin/Result$Companion;

    invoke-static {p0}, Lkotlin/ResultKt;->createFailure(Ljava/lang/Throwable;)Ljava/lang/Object;

    move-result-object p0

    invoke-static {p0}, Lkotlin/Result;->constructor-impl(Ljava/lang/Object;)Ljava/lang/Object;

    .line 362
    :cond_3
    :goto_0
    sget-object p0, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;

    return-object p0
.end method

.method private final runtimeEnvironment(Ljava/nio/file/Path;Ljava/nio/file/Path;Ljava/io/File;Ljava/lang/String;)Ljava/util/Map;
    .locals 4
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "(",
            "Ljava/nio/file/Path;",
            "Ljava/nio/file/Path;",
            "Ljava/io/File;",
            "Ljava/lang/String;",
            ")",
            "Ljava/util/Map<",
            "Ljava/lang/String;",
            "Ljava/lang/String;",
            ">;"
        }
    .end annotation

    const/16 v0, 0x11

    .line 692
    new-array v0, v0, [Lkotlin/Pair;

    const-string v1, "HOME"

    invoke-virtual {p2}, Ljava/lang/Object;->toString()Ljava/lang/String;

    move-result-object p2

    invoke-static {v1, p2}, Lkotlin/TuplesKt;->to(Ljava/lang/Object;Ljava/lang/Object;)Lkotlin/Pair;

    move-result-object p2

    const/4 v1, 0x0

    aput-object p2, v0, v1

    .line 693
    const-string p2, "bin"

    invoke-interface {p1, p2}, Ljava/nio/file/Path;->resolve(Ljava/lang/String;)Ljava/nio/file/Path;

    move-result-object p2

    invoke-virtual {p2}, Ljava/lang/Object;->toString()Ljava/lang/String;

    move-result-object p2

    const-string v1, "BOX64_PATH"

    invoke-static {v1, p2}, Lkotlin/TuplesKt;->to(Ljava/lang/Object;Ljava/lang/Object;)Lkotlin/Pair;

    move-result-object p2

    const/4 v1, 0x1

    aput-object p2, v0, v1

    .line 694
    const-string p2, "BOX64_LOG"

    const-string v1, "1"

    invoke-static {p2, v1}, Lkotlin/TuplesKt;->to(Ljava/lang/Object;Ljava/lang/Object;)Lkotlin/Pair;

    move-result-object p2

    const/4 v2, 0x2

    aput-object p2, v0, v2

    .line 695
    const-string p2, "BOX64_LOAD_ADDR"

    const-string v2, "0x6000000000"

    invoke-static {p2, v2}, Lkotlin/TuplesKt;->to(Ljava/lang/Object;Ljava/lang/Object;)Lkotlin/Pair;

    move-result-object p2

    const/4 v2, 0x3

    aput-object p2, v0, v2

    .line 696
    const-string p2, "BOX64_PREFER_WRAPPED"

    invoke-static {p2, v1}, Lkotlin/TuplesKt;->to(Ljava/lang/Object;Ljava/lang/Object;)Lkotlin/Pair;

    move-result-object p2

    const/4 v2, 0x4

    aput-object p2, v0, v2

    .line 697
    const-string p2, "BOX64_DYNAREC_CALLRET"

    invoke-static {p2, v1}, Lkotlin/TuplesKt;->to(Ljava/lang/Object;Ljava/lang/Object;)Lkotlin/Pair;

    move-result-object p2

    const/4 v2, 0x5

    aput-object p2, v0, v2

    .line 698
    const-string p2, "lib/x86_64-linux-gnu"

    invoke-interface {p1, p2}, Ljava/nio/file/Path;->resolve(Ljava/lang/String;)Ljava/nio/file/Path;

    move-result-object p2

    const-string v2, "lib64"

    invoke-interface {p1, v2}, Ljava/nio/file/Path;->resolve(Ljava/lang/String;)Ljava/nio/file/Path;

    move-result-object v2

    new-instance v3, Ljava/lang/StringBuilder;

    invoke-direct {v3}, Ljava/lang/StringBuilder;-><init>()V

    invoke-virtual {v3, p2}, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;

    move-result-object p2

    const-string v3, ":"

    invoke-virtual {p2, v3}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p2

    invoke-virtual {p2, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;

    move-result-object p2

    invoke-virtual {p2}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p2

    const-string v2, "BOX64_LD_LIBRARY_PATH"

    invoke-static {v2, p2}, Lkotlin/TuplesKt;->to(Ljava/lang/Object;Ljava/lang/Object;)Lkotlin/Pair;

    move-result-object p2

    const/4 v2, 0x6

    aput-object p2, v0, v2

    .line 699
    const-string p2, "BOX64_EMULATED_LIBS"

    const-string v2, "libSDL2-2.0.so.0:libudev.so.1:libuuid.so.1"

    invoke-static {p2, v2}, Lkotlin/TuplesKt;->to(Ljava/lang/Object;Ljava/lang/Object;)Lkotlin/Pair;

    move-result-object p2

    const/4 v2, 0x7

    aput-object p2, v0, v2

    .line 700
    new-instance p2, Ljava/io/File;

    const-string v2, "/tmp/.sound/AS0"

    invoke-direct {p2, p3, v2}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    invoke-virtual {p2}, Ljava/io/File;->getPath()Ljava/lang/String;

    move-result-object p2

    const-string p3, "BACHATA_ALSA_SOCKET"

    invoke-static {p3, p2}, Lkotlin/TuplesKt;->to(Ljava/lang/Object;Ljava/lang/Object;)Lkotlin/Pair;

    move-result-object p2

    const/16 p3, 0x8

    aput-object p2, v0, p3

    .line 701
    const-string p2, "DISPLAY"

    invoke-static {p2, p4}, Lkotlin/TuplesKt;->to(Ljava/lang/Object;Ljava/lang/Object;)Lkotlin/Pair;

    move-result-object p2

    const/16 p3, 0x9

    aput-object p2, v0, p3

    .line 702
    const-string p2, "SDL_VIDEODRIVER"

    const-string p3, "x11"

    invoke-static {p2, p3}, Lkotlin/TuplesKt;->to(Ljava/lang/Object;Ljava/lang/Object;)Lkotlin/Pair;

    move-result-object p2

    const/16 p3, 0xa

    aput-object p2, v0, p3

    .line 703
    const-string p2, "usr/share/X11/xkb"

    invoke-interface {p1, p2}, Ljava/nio/file/Path;->resolve(Ljava/lang/String;)Ljava/nio/file/Path;

    move-result-object p1

    invoke-virtual {p1}, Ljava/lang/Object;->toString()Ljava/lang/String;

    move-result-object p1

    const-string p2, "XKB_CONFIG_ROOT"

    invoke-static {p2, p1}, Lkotlin/TuplesKt;->to(Ljava/lang/Object;Ljava/lang/Object;)Lkotlin/Pair;

    move-result-object p1

    const/16 p2, 0xb

    aput-object p1, v0, p2

    .line 704
    invoke-virtual {p0}, Lcom/bachatas4/android/service/EmulationService;->getCacheDir()Ljava/io/File;

    move-result-object p1

    invoke-virtual {p1}, Ljava/io/File;->getPath()Ljava/lang/String;

    move-result-object p1

    const-string p2, "TMPDIR"

    invoke-static {p2, p1}, Lkotlin/TuplesKt;->to(Ljava/lang/Object;Ljava/lang/Object;)Lkotlin/Pair;

    move-result-object p1

    const/16 p2, 0xc

    aput-object p1, v0, p2

    .line 705
    new-instance p1, Ljava/io/File;

    invoke-virtual {p0}, Lcom/bachatas4/android/service/EmulationService;->getCacheDir()Ljava/io/File;

    move-result-object p0

    const-string p2, "xdg"

    invoke-direct {p1, p0, p2}, Ljava/io/File;-><init>(Ljava/io/File;Ljava/lang/String;)V

    invoke-virtual {p1}, Ljava/io/File;->mkdirs()Z

    sget-object p0, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;

    invoke-virtual {p1}, Ljava/io/File;->getPath()Ljava/lang/String;

    move-result-object p0

    const-string p1, "XDG_CACHE_HOME"

    invoke-static {p1, p0}, Lkotlin/TuplesKt;->to(Ljava/lang/Object;Ljava/lang/Object;)Lkotlin/Pair;

    move-result-object p0

    const/16 p1, 0xd

    aput-object p0, v0, p1

    .line 706
    const-string p0, "GLIBC_TUNABLES"

    const-string p1, "glibc.pthread.rseq=0"

    invoke-static {p0, p1}, Lkotlin/TuplesKt;->to(Ljava/lang/Object;Ljava/lang/Object;)Lkotlin/Pair;

    move-result-object p0

    const/16 p1, 0xe

    aput-object p0, v0, p1

    .line 707
    const-string p0, "BACHATA_VORTEK_TRACE_BIND_VERTEX_BUFFERS"

    invoke-static {p0, v1}, Lkotlin/TuplesKt;->to(Ljava/lang/Object;Ljava/lang/Object;)Lkotlin/Pair;

    move-result-object p0

    const/16 p1, 0xf

    aput-object p0, v0, p1

    .line 708
    const-string p0, "BACHATA_FEX_TRACE_SIGSYS"

    invoke-static {p0, v1}, Lkotlin/TuplesKt;->to(Ljava/lang/Object;Ljava/lang/Object;)Lkotlin/Pair;

    move-result-object p0

    const/16 p1, 0x10

    aput-object p0, v0, p1

    .line 691
    invoke-static {v0}, Lkotlin/collections/MapsKt;->mapOf([Lkotlin/Pair;)Ljava/util/Map;

    move-result-object p0

    return-object p0
.end method

.method private final stagingDiagEnvironment(Z)Ljava/util/Map;
    .locals 6
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "(Z)",
            "Ljava/util/Map<",
            "Ljava/lang/String;",
            "Ljava/lang/String;",
            ">;"
        }
    .end annotation

    .line 722
    new-instance v0, Ljava/util/LinkedHashMap;

    invoke-direct {v0}, Ljava/util/LinkedHashMap;-><init>()V

    check-cast v0, Ljava/util/Map;

    .line 723
    const-string v1, "debug.bachata.mali_gpu_opt"

    invoke-direct {p0, v1}, Lcom/bachatas4/android/service/EmulationService;->readSystemProperty(Ljava/lang/String;)Ljava/lang/String;

    move-result-object v1

    const/4 v2, 0x0

    const/4 v3, 0x1

    if-eqz v1, :cond_1

    .line 725
    move-object v4, v1

    check-cast v4, Ljava/lang/CharSequence;

    invoke-static {v4}, Lkotlin/text/StringsKt;->isBlank(Ljava/lang/CharSequence;)Z

    move-result v4

    if-nez v4, :cond_1

    const-string p1, "0"

    invoke-static {v1, p1}, Lkotlin/jvm/internal/Intrinsics;->areEqual(Ljava/lang/Object;Ljava/lang/Object;)Z

    move-result p1

    if-nez p1, :cond_0

    move p1, v3

    goto :goto_0

    :cond_0
    move p1, v2

    .line 728
    :cond_1
    :goto_0
    const-string v1, "BACHATA_STAGING_TICK_LAG"

    const-string v4, "debug.bachata.staging_tick_lag"

    if-eqz p1, :cond_4

    .line 729
    const-string p1, "BACHATA_MALI_GPU_OPT"

    const-string v5, "1"

    invoke-interface {v0, p1, v5}, Ljava/util/Map;->put(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;

    .line 731
    invoke-direct {p0, v4}, Lcom/bachatas4/android/service/EmulationService;->readSystemProperty(Ljava/lang/String;)Ljava/lang/String;

    move-result-object p1

    check-cast p1, Ljava/lang/CharSequence;

    if-eqz p1, :cond_2

    invoke-static {p1}, Lkotlin/text/StringsKt;->isBlank(Ljava/lang/CharSequence;)Z

    move-result p1

    if-eqz p1, :cond_3

    :cond_2
    move v2, v3

    :cond_3
    if-eqz v2, :cond_4

    .line 732
    const-string p1, "12"

    invoke-interface {v0, v1, p1}, Ljava/util/Map;->put(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;

    .line 735
    :cond_4
    const-string p1, "debug.bachata.staging_strict_scratch"

    invoke-direct {p0, p1}, Lcom/bachatas4/android/service/EmulationService;->readSystemProperty(Ljava/lang/String;)Ljava/lang/String;

    move-result-object p1

    const/4 v2, 0x0

    if-eqz p1, :cond_6

    move-object v3, p1

    check-cast v3, Ljava/lang/CharSequence;

    invoke-static {v3}, Lkotlin/text/StringsKt;->isBlank(Ljava/lang/CharSequence;)Z

    move-result v3

    if-nez v3, :cond_5

    goto :goto_1

    :cond_5
    move-object p1, v2

    :goto_1
    if-eqz p1, :cond_6

    .line 736
    const-string v3, "BACHATA_STAGING_STRICT_SCRATCH"

    invoke-interface {v0, v3, p1}, Ljava/util/Map;->put(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;

    .line 738
    :cond_6
    const-string p1, "debug.bachata.staging_strict_stream"

    invoke-direct {p0, p1}, Lcom/bachatas4/android/service/EmulationService;->readSystemProperty(Ljava/lang/String;)Ljava/lang/String;

    move-result-object p1

    if-eqz p1, :cond_8

    move-object v3, p1

    check-cast v3, Ljava/lang/CharSequence;

    invoke-static {v3}, Lkotlin/text/StringsKt;->isBlank(Ljava/lang/CharSequence;)Z

    move-result v3

    if-nez v3, :cond_7

    goto :goto_2

    :cond_7
    move-object p1, v2

    :goto_2
    if-eqz p1, :cond_8

    .line 739
    const-string v3, "BACHATA_STAGING_STRICT_STREAM"

    invoke-interface {v0, v3, p1}, Ljava/util/Map;->put(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;

    .line 741
    :cond_8
    const-string p1, "debug.bachata.staging_strict_buffer_cache"

    invoke-direct {p0, p1}, Lcom/bachatas4/android/service/EmulationService;->readSystemProperty(Ljava/lang/String;)Ljava/lang/String;

    move-result-object p1

    if-eqz p1, :cond_a

    move-object v3, p1

    check-cast v3, Ljava/lang/CharSequence;

    invoke-static {v3}, Lkotlin/text/StringsKt;->isBlank(Ljava/lang/CharSequence;)Z

    move-result v3

    if-nez v3, :cond_9

    goto :goto_3

    :cond_9
    move-object p1, v2

    :goto_3
    if-eqz p1, :cond_a

    .line 742
    const-string v3, "BACHATA_STAGING_STRICT_BUFFER_CACHE"

    invoke-interface {v0, v3, p1}, Ljava/util/Map;->put(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;

    .line 744
    :cond_a
    invoke-direct {p0, v4}, Lcom/bachatas4/android/service/EmulationService;->readSystemProperty(Ljava/lang/String;)Ljava/lang/String;

    move-result-object p1

    if-eqz p1, :cond_c

    move-object v3, p1

    check-cast v3, Ljava/lang/CharSequence;

    invoke-static {v3}, Lkotlin/text/StringsKt;->isBlank(Ljava/lang/CharSequence;)Z

    move-result v3

    if-nez v3, :cond_b

    goto :goto_4

    :cond_b
    move-object p1, v2

    :goto_4
    if-eqz p1, :cond_c

    .line 745
    invoke-interface {v0, v1, p1}, Ljava/util/Map;->put(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;

    .line 747
    :cond_c
    const-string p1, "debug.bachata.buffer_cache_tick_lag"

    invoke-direct {p0, p1}, Lcom/bachatas4/android/service/EmulationService;->readSystemProperty(Ljava/lang/String;)Ljava/lang/String;

    move-result-object p1

    if-eqz p1, :cond_e

    move-object v1, p1

    check-cast v1, Ljava/lang/CharSequence;

    invoke-static {v1}, Lkotlin/text/StringsKt;->isBlank(Ljava/lang/CharSequence;)Z

    move-result v1

    if-nez v1, :cond_d

    goto :goto_5

    :cond_d
    move-object p1, v2

    :goto_5
    if-eqz p1, :cond_e

    .line 748
    const-string v1, "BACHATA_BUFFER_CACHE_TICK_LAG"

    invoke-interface {v0, v1, p1}, Ljava/util/Map;->put(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;

    .line 750
    :cond_e
    const-string p1, "debug.bachata.staging_fhd_ring"

    invoke-direct {p0, p1}, Lcom/bachatas4/android/service/EmulationService;->readSystemProperty(Ljava/lang/String;)Ljava/lang/String;

    move-result-object p1

    if-eqz p1, :cond_10

    move-object v1, p1

    check-cast v1, Ljava/lang/CharSequence;

    invoke-static {v1}, Lkotlin/text/StringsKt;->isBlank(Ljava/lang/CharSequence;)Z

    move-result v1

    if-nez v1, :cond_f

    goto :goto_6

    :cond_f
    move-object p1, v2

    :goto_6
    if-eqz p1, :cond_10

    .line 751
    const-string v1, "BACHATA_STAGING_FHD_RING"

    invoke-interface {v0, v1, p1}, Ljava/util/Map;->put(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;

    .line 753
    :cond_10
    const-string p1, "debug.bachata.staging_verbose"

    invoke-direct {p0, p1}, Lcom/bachatas4/android/service/EmulationService;->readSystemProperty(Ljava/lang/String;)Ljava/lang/String;

    move-result-object p0

    if-eqz p0, :cond_12

    move-object p1, p0

    check-cast p1, Ljava/lang/CharSequence;

    invoke-static {p1}, Lkotlin/text/StringsKt;->isBlank(Ljava/lang/CharSequence;)Z

    move-result p1

    if-nez p1, :cond_11

    move-object v2, p0

    :cond_11
    if-eqz v2, :cond_12

    .line 754
    const-string p0, "BACHATA_STAGING_VERBOSE"

    invoke-interface {v0, p0, v2}, Ljava/util/Map;->put(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;

    .line 756
    :cond_12
    invoke-interface {v0}, Ljava/util/Map;->isEmpty()Z

    move-result p0

    if-nez p0, :cond_13

    .line 757
    new-instance p0, Ljava/lang/StringBuilder;

    const-string p1, "staging diag env="

    invoke-direct {p0, p1}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {p0, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/Object;)Ljava/lang/StringBuilder;

    move-result-object p0

    invoke-virtual {p0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p0

    const-string p1, "EmulationService"

    invoke-static {p1, p0}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    :cond_13
    return-object v0
.end method

.method static synthetic stagingDiagEnvironment$default(Lcom/bachatas4/android/service/EmulationService;ZILjava/lang/Object;)Ljava/util/Map;
    .locals 0

    and-int/lit8 p2, p2, 0x1

    if-eqz p2, :cond_0

    const/4 p1, 0x0

    .line 721
    :cond_0
    invoke-direct {p0, p1}, Lcom/bachatas4/android/service/EmulationService;->stagingDiagEnvironment(Z)Ljava/util/Map;

    move-result-object p0

    return-object p0
.end method

.method private final stopSession()V
    .locals 3

    .line 772
    iget-object v0, p0, Lcom/bachatas4/android/service/EmulationService;->userRequestedStop:Ljava/util/concurrent/atomic/AtomicBoolean;

    const/4 v1, 0x1

    invoke-virtual {v0, v1}, Ljava/util/concurrent/atomic/AtomicBoolean;->set(Z)V

    .line 773
    iget-object v0, p0, Lcom/bachatas4/android/service/EmulationService;->process:Lcom/bachatas4/android/runtime/process/RuntimeProcessHandle;

    if-eqz v0, :cond_0

    invoke-interface {v0}, Lcom/bachatas4/android/runtime/process/RuntimeProcessHandle;->destroy()V

    .line 774
    :cond_0
    iget-object v0, p0, Lcom/bachatas4/android/service/EmulationService;->sessionJob:Lkotlinx/coroutines/Job;

    const/4 v2, 0x0

    if-eqz v0, :cond_1

    invoke-static {v0, v2, v1, v2}, Lkotlinx/coroutines/Job;->cancel$default(Lkotlinx/coroutines/Job;Ljava/util/concurrent/CancellationException;ILjava/lang/Object;)V

    .line 775
    :cond_1
    iput-object v2, p0, Lcom/bachatas4/android/service/EmulationService;->sessionJob:Lkotlinx/coroutines/Job;

    return-void
.end method

.method private final verifyDeepGuestRuntime(Ljava/nio/file/Path;Lcom/bachatas4/android/runtime/diagnostics/SessionLog;)V
    .locals 9

    .line 656
    invoke-direct {p0, p1}, Lcom/bachatas4/android/service/EmulationService;->guestSha256(Ljava/nio/file/Path;)Ljava/lang/String;

    move-result-object p0

    .line 657
    const-string v0, "usr/share/bachata/guest-runtime.txt"

    invoke-interface {p1, v0}, Ljava/nio/file/Path;->resolve(Ljava/lang/String;)Ljava/nio/file/Path;

    move-result-object p1

    invoke-interface {p1}, Ljava/nio/file/Path;->toFile()Ljava/io/File;

    move-result-object p1

    .line 658
    invoke-virtual {p1}, Ljava/io/File;->isFile()Z

    move-result v0

    const/4 v1, 0x0

    if-eqz v0, :cond_0

    invoke-static {p1}, Lkotlin/jvm/internal/Intrinsics;->checkNotNull(Ljava/lang/Object;)V

    const/4 v0, 0x1

    invoke-static {p1, v1, v0, v1}, Lkotlin/io/FilesKt;->readText$default(Ljava/io/File;Ljava/nio/charset/Charset;ILjava/lang/Object;)Ljava/lang/String;

    move-result-object p1

    check-cast p1, Ljava/lang/CharSequence;

    invoke-static {p1}, Lkotlin/text/StringsKt;->trim(Ljava/lang/CharSequence;)Ljava/lang/CharSequence;

    move-result-object p1

    invoke-virtual {p1}, Ljava/lang/Object;->toString()Ljava/lang/String;

    move-result-object p1

    goto :goto_0

    :cond_0
    const-string p1, "missing guest-runtime.txt"

    .line 659
    :goto_0
    check-cast p1, Ljava/lang/CharSequence;

    invoke-static {p1}, Lkotlin/text/StringsKt;->lineSequence(Ljava/lang/CharSequence;)Lkotlin/sequences/Sequence;

    move-result-object v0

    .line 823
    invoke-interface {v0}, Lkotlin/sequences/Sequence;->iterator()Ljava/util/Iterator;

    move-result-object v0

    :cond_1
    invoke-interface {v0}, Ljava/util/Iterator;->hasNext()Z

    move-result v2

    const/4 v3, 0x0

    const/4 v4, 0x2

    if-eqz v2, :cond_2

    invoke-interface {v0}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v2

    move-object v5, v2

    check-cast v5, Ljava/lang/String;

    .line 659
    const-string v6, "variant="

    invoke-static {v5, v6, v3, v4, v1}, Lkotlin/text/StringsKt;->startsWith$default(Ljava/lang/String;Ljava/lang/String;ZILjava/lang/Object;)Z

    move-result v5

    if-eqz v5, :cond_1

    goto :goto_1

    :cond_2
    move-object v2, v1

    :goto_1
    check-cast v2, Ljava/lang/String;

    const-string v0, "="

    const-string v5, "?"

    if-eqz v2, :cond_3

    invoke-static {v2, v0, v1, v4, v1}, Lkotlin/text/StringsKt;->substringAfter$default(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;ILjava/lang/Object;)Ljava/lang/String;

    move-result-object v2

    if-nez v2, :cond_4

    :cond_3
    move-object v2, v5

    .line 660
    :cond_4
    invoke-static {p1}, Lkotlin/text/StringsKt;->lineSequence(Ljava/lang/CharSequence;)Lkotlin/sequences/Sequence;

    move-result-object p1

    .line 825
    invoke-interface {p1}, Lkotlin/sequences/Sequence;->iterator()Ljava/util/Iterator;

    move-result-object p1

    :cond_5
    invoke-interface {p1}, Ljava/util/Iterator;->hasNext()Z

    move-result v6

    if-eqz v6, :cond_6

    invoke-interface {p1}, Ljava/util/Iterator;->next()Ljava/lang/Object;

    move-result-object v6

    move-object v7, v6

    check-cast v7, Ljava/lang/String;

    .line 660
    const-string v8, "revision="

    invoke-static {v7, v8, v3, v4, v1}, Lkotlin/text/StringsKt;->startsWith$default(Ljava/lang/String;Ljava/lang/String;ZILjava/lang/Object;)Z

    move-result v7

    if-eqz v7, :cond_5

    goto :goto_2

    :cond_6
    move-object v6, v1

    :goto_2
    check-cast v6, Ljava/lang/String;

    if-eqz v6, :cond_8

    invoke-static {v6, v0, v1, v4, v1}, Lkotlin/text/StringsKt;->substringAfter$default(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;ILjava/lang/Object;)Ljava/lang/String;

    move-result-object p1

    if-nez p1, :cond_7

    goto :goto_3

    :cond_7
    move-object v5, p1

    .line 662
    :cond_8
    :goto_3
    new-instance p1, Ljava/lang/StringBuilder;

    const-string v0, "GUEST_RUNTIME_BUILD variant="

    invoke-direct {p1, v0}, Ljava/lang/StringBuilder;-><init>(Ljava/lang/String;)V

    invoke-virtual {p1, v2}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p1

    const-string v0, " sha256="

    invoke-virtual {p1, v0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p1

    invoke-virtual {p1, p0}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p0

    const-string p1, " revision="

    invoke-virtual {p0, p1}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p0

    invoke-virtual {p0, v5}, Ljava/lang/StringBuilder;->append(Ljava/lang/String;)Ljava/lang/StringBuilder;

    move-result-object p0

    invoke-virtual {p0}, Ljava/lang/StringBuilder;->toString()Ljava/lang/String;

    move-result-object p0

    .line 663
    const-string p1, "Runtime"

    invoke-virtual {p2, p1, p0}, Lcom/bachatas4/android/runtime/diagnostics/SessionLog;->info(Ljava/lang/String;Ljava/lang/String;)V

    .line 664
    const-string p1, "EmulationService"

    invoke-static {p1, p0}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I

    return-void
.end method


# virtual methods
.method public final getLaunchProfileProvider()Lcom/bachatas4/android/RuntimeLaunchProfileProvider;
    .locals 0

    .line 82
    iget-object p0, p0, Lcom/bachatas4/android/service/EmulationService;->launchProfileProvider:Lcom/bachatas4/android/RuntimeLaunchProfileProvider;

    if-eqz p0, :cond_0

    return-object p0

    :cond_0
    const-string p0, "launchProfileProvider"

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

    .line 90
    invoke-super {p0}, Lcom/bachatas4/android/service/Hilt_EmulationService;->onCreate()V

    return-void
.end method

.method public onDestroy()V
    .locals 3

    .line 114
    invoke-direct {p0}, Lcom/bachatas4/android/service/EmulationService;->stopSession()V

    .line 115
    iget-object v0, p0, Lcom/bachatas4/android/service/EmulationService;->scope:Lkotlinx/coroutines/CoroutineScope;

    const/4 v1, 0x0

    const/4 v2, 0x1

    invoke-static {v0, v1, v2, v1}, Lkotlinx/coroutines/CoroutineScopeKt;->cancel$default(Lkotlinx/coroutines/CoroutineScope;Ljava/util/concurrent/CancellationException;ILjava/lang/Object;)V

    .line 116
    invoke-static {}, Lcom/bachatas4/android/turbo/AdrenoTurbo;->stop()V

    invoke-super {p0}, Lcom/bachatas4/android/service/Hilt_EmulationService;->onDestroy()V

    return-void
.end method

.method public onStartCommand(Landroid/content/Intent;II)I
    .locals 12

    if-eqz p1, :cond_0

    .line 94
    invoke-virtual {p1}, Landroid/content/Intent;->getAction()Ljava/lang/String;

    move-result-object p2

    goto :goto_0

    :cond_0
    const/4 p2, 0x0

    :goto_0
    const/4 p3, 0x2

    if-eqz p2, :cond_8

    invoke-virtual {p2}, Ljava/lang/String;->hashCode()I

    move-result v0

    const v1, -0x556481de

    if-eq v0, v1, :cond_7

    const v1, 0x2358b530

    if-eq v0, v1, :cond_1

    goto :goto_3

    :cond_1
    const-string v0, "com.bachatas4.android.action.START_EMULATION"

    invoke-virtual {p2, v0}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result p2

    if-nez p2, :cond_2

    goto :goto_3

    .line 97
    :cond_2
    iget-object p2, p0, Lcom/bachatas4/android/service/EmulationService;->sessionJob:Lkotlinx/coroutines/Job;

    if-eqz p2, :cond_3

    invoke-interface {p2}, Lkotlinx/coroutines/Job;->isActive()Z

    move-result p2

    const/4 v0, 0x1

    if-ne p2, v0, :cond_3

    return p3

    .line 100
    :cond_3
    const-string p2, "game_id"

    invoke-virtual {p1, p2}, Landroid/content/Intent;->getStringExtra(Ljava/lang/String;)Ljava/lang/String;

    move-result-object p2

    const-string v0, ""

    if-nez p2, :cond_4

    move-object v3, v0

    goto :goto_1

    :cond_4
    move-object v3, p2

    .line 101
    :goto_1
    const-string p2, "game_path"

    invoke-virtual {p1, p2}, Landroid/content/Intent;->getStringExtra(Ljava/lang/String;)Ljava/lang/String;

    move-result-object p2

    if-nez p2, :cond_5

    move-object v4, v0

    goto :goto_2

    :cond_5
    move-object v4, p2

    .line 102
    :goto_2
    const-string p2, "vulkan_driver"

    invoke-virtual {p1, p2}, Landroid/content/Intent;->getStringExtra(Ljava/lang/String;)Ljava/lang/String;

    move-result-object p1

    if-nez p1, :cond_6

    .line 103
    const-string p1, "TURNIP_26_1_0"

    :cond_6
    move-object v5, p1

    .line 104
    iget-object p1, p0, Lcom/bachatas4/android/service/EmulationService;->scope:Lkotlinx/coroutines/CoroutineScope;

    new-instance v1, Lcom/bachatas4/android/service/EmulationService$onStartCommand$1;

    const/4 v6, 0x0

    move-object v2, p0

    invoke-direct/range {v1 .. v6}, Lcom/bachatas4/android/service/EmulationService$onStartCommand$1;-><init>(Lcom/bachatas4/android/service/EmulationService;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;Lkotlin/coroutines/Continuation;)V

    move-object v9, v1

    check-cast v9, Lkotlin/jvm/functions/Function2;

    const/4 v10, 0x3

    const/4 v11, 0x0

    const/4 v7, 0x0

    const/4 v8, 0x0

    move-object v6, p1

    invoke-static/range {v6 .. v11}, Lkotlinx/coroutines/BuildersKt;->launch$default(Lkotlinx/coroutines/CoroutineScope;Lkotlin/coroutines/CoroutineContext;Lkotlinx/coroutines/CoroutineStart;Lkotlin/jvm/functions/Function2;ILjava/lang/Object;)Lkotlinx/coroutines/Job;

    move-result-object p0

    iput-object p0, v2, Lcom/bachatas4/android/service/EmulationService;->sessionJob:Lkotlinx/coroutines/Job;

    goto :goto_3

    :cond_7
    move-object v2, p0

    .line 94
    const-string p0, "com.bachatas4.android.action.STOP_EMULATION"

    invoke-virtual {p2, p0}, Ljava/lang/String;->equals(Ljava/lang/Object;)Z

    move-result p0

    if-eqz p0, :cond_8

    .line 95
    invoke-direct {v2}, Lcom/bachatas4/android/service/EmulationService;->stopSession()V

    :cond_8
    :goto_3
    return p3
.end method

.method public final setLaunchProfileProvider(Lcom/bachatas4/android/RuntimeLaunchProfileProvider;)V
    .locals 1

    const-string v0, "<set-?>"

    invoke-static {p1, v0}, Lkotlin/jvm/internal/Intrinsics;->checkNotNullParameter(Ljava/lang/Object;Ljava/lang/String;)V

    .line 82
    iput-object p1, p0, Lcom/bachatas4/android/service/EmulationService;->launchProfileProvider:Lcom/bachatas4/android/RuntimeLaunchProfileProvider;

    return-void
.end method
