.class final Lcom/bachatas4/android/feature/session/SessionViewModel_HiltModules_KeyModule_ProvideFactory$InstanceHolder;
.super Ljava/lang/Object;
.source "SessionViewModel_HiltModules_KeyModule_ProvideFactory.java"


# annotations
.annotation system Ldalvik/annotation/EnclosingClass;
    value = Lcom/bachatas4/android/feature/session/SessionViewModel_HiltModules_KeyModule_ProvideFactory;
.end annotation

.annotation system Ldalvik/annotation/InnerClass;
    accessFlags = 0x1a
    name = "InstanceHolder"
.end annotation


# static fields
.field static final INSTANCE:Lcom/bachatas4/android/feature/session/SessionViewModel_HiltModules_KeyModule_ProvideFactory;


# direct methods
.method static constructor <clinit>()V
    .locals 1

    .line 40
    new-instance v0, Lcom/bachatas4/android/feature/session/SessionViewModel_HiltModules_KeyModule_ProvideFactory;

    invoke-direct {v0}, Lcom/bachatas4/android/feature/session/SessionViewModel_HiltModules_KeyModule_ProvideFactory;-><init>()V

    sput-object v0, Lcom/bachatas4/android/feature/session/SessionViewModel_HiltModules_KeyModule_ProvideFactory$InstanceHolder;->INSTANCE:Lcom/bachatas4/android/feature/session/SessionViewModel_HiltModules_KeyModule_ProvideFactory;

    return-void
.end method

.method private constructor <init>()V
    .locals 0

    .line 39
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method
