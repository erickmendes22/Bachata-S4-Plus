.class public final synthetic Lcom/bachatas4/android/service/EmulationService$$ExternalSyntheticLambda3;
.super Ljava/lang/Object;
.source "D8$$SyntheticClass"

# interfaces
.implements Lkotlin/jvm/functions/Function2;


# instance fields
.field public final synthetic f$0:Ljava/util/concurrent/atomic/AtomicReference;

.field public final synthetic f$1:[J

.field public final synthetic f$2:Lcom/bachatas4/android/runtime/diagnostics/SessionLog;

.field public final synthetic f$3:Lcom/bachatas4/android/runtime/input/ControllerFrameEncoder;

.field public final synthetic f$4:Lcom/bachatas4/android/service/EmulationService;

.field public final synthetic f$5:Ljava/lang/Object;

.field public final synthetic f$6:Ljava/io/OutputStream;


# direct methods
.method public synthetic constructor <init>(Ljava/util/concurrent/atomic/AtomicReference;[JLcom/bachatas4/android/runtime/diagnostics/SessionLog;Lcom/bachatas4/android/runtime/input/ControllerFrameEncoder;Lcom/bachatas4/android/service/EmulationService;Ljava/lang/Object;Ljava/io/OutputStream;)V
    .locals 0

    .line 0
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    iput-object p1, p0, Lcom/bachatas4/android/service/EmulationService$$ExternalSyntheticLambda3;->f$0:Ljava/util/concurrent/atomic/AtomicReference;

    iput-object p2, p0, Lcom/bachatas4/android/service/EmulationService$$ExternalSyntheticLambda3;->f$1:[J

    iput-object p3, p0, Lcom/bachatas4/android/service/EmulationService$$ExternalSyntheticLambda3;->f$2:Lcom/bachatas4/android/runtime/diagnostics/SessionLog;

    iput-object p4, p0, Lcom/bachatas4/android/service/EmulationService$$ExternalSyntheticLambda3;->f$3:Lcom/bachatas4/android/runtime/input/ControllerFrameEncoder;

    iput-object p5, p0, Lcom/bachatas4/android/service/EmulationService$$ExternalSyntheticLambda3;->f$4:Lcom/bachatas4/android/service/EmulationService;

    iput-object p6, p0, Lcom/bachatas4/android/service/EmulationService$$ExternalSyntheticLambda3;->f$5:Ljava/lang/Object;

    iput-object p7, p0, Lcom/bachatas4/android/service/EmulationService$$ExternalSyntheticLambda3;->f$6:Ljava/io/OutputStream;

    return-void
.end method


# virtual methods
.method public final invoke(Ljava/lang/Object;Ljava/lang/Object;)Ljava/lang/Object;
    .locals 9

    .line 0
    iget-object v0, p0, Lcom/bachatas4/android/service/EmulationService$$ExternalSyntheticLambda3;->f$0:Ljava/util/concurrent/atomic/AtomicReference;

    iget-object v1, p0, Lcom/bachatas4/android/service/EmulationService$$ExternalSyntheticLambda3;->f$1:[J

    iget-object v2, p0, Lcom/bachatas4/android/service/EmulationService$$ExternalSyntheticLambda3;->f$2:Lcom/bachatas4/android/runtime/diagnostics/SessionLog;

    iget-object v3, p0, Lcom/bachatas4/android/service/EmulationService$$ExternalSyntheticLambda3;->f$3:Lcom/bachatas4/android/runtime/input/ControllerFrameEncoder;

    iget-object v4, p0, Lcom/bachatas4/android/service/EmulationService$$ExternalSyntheticLambda3;->f$4:Lcom/bachatas4/android/service/EmulationService;

    iget-object v5, p0, Lcom/bachatas4/android/service/EmulationService$$ExternalSyntheticLambda3;->f$5:Ljava/lang/Object;

    iget-object v6, p0, Lcom/bachatas4/android/service/EmulationService$$ExternalSyntheticLambda3;->f$6:Ljava/io/OutputStream;

    check-cast p1, Ljava/lang/Integer;

    invoke-virtual {p1}, Ljava/lang/Integer;->intValue()I

    move-result v7

    move-object v8, p2

    check-cast v8, Lcom/bachatas4/android/runtime/input/ControllerSnapshot;

    invoke-static/range {v0 .. v8}, Lcom/bachatas4/android/service/EmulationService;->runSession$lambda$9(Ljava/util/concurrent/atomic/AtomicReference;[JLcom/bachatas4/android/runtime/diagnostics/SessionLog;Lcom/bachatas4/android/runtime/input/ControllerFrameEncoder;Lcom/bachatas4/android/service/EmulationService;Ljava/lang/Object;Ljava/io/OutputStream;ILcom/bachatas4/android/runtime/input/ControllerSnapshot;)Lkotlin/Unit;

    move-result-object p0

    return-object p0
.end method
