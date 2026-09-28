.class public final Lcom/bachatas4/android/feature/session/SessionViewModel_HiltModules_KeyModule_ProvideFactory;
.super Ljava/lang/Object;
.source "SessionViewModel_HiltModules_KeyModule_ProvideFactory.java"

# interfaces
.implements Ldagger/internal/Factory;


# annotations
.annotation system Ldalvik/annotation/MemberClasses;
    value = {
        Lcom/bachatas4/android/feature/session/SessionViewModel_HiltModules_KeyModule_ProvideFactory$InstanceHolder;
    }
.end annotation

.annotation system Ldalvik/annotation/Signature;
    value = {
        "Ljava/lang/Object;",
        "Ldagger/internal/Factory<",
        "Ljava/lang/Boolean;",
        ">;"
    }
.end annotation


# direct methods
.method public constructor <init>()V
    .locals 0

    .line 25
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    return-void
.end method

.method public static create()Lcom/bachatas4/android/feature/session/SessionViewModel_HiltModules_KeyModule_ProvideFactory;
    .locals 1

    .line 32
    sget-object v0, Lcom/bachatas4/android/feature/session/SessionViewModel_HiltModules_KeyModule_ProvideFactory$InstanceHolder;->INSTANCE:Lcom/bachatas4/android/feature/session/SessionViewModel_HiltModules_KeyModule_ProvideFactory;

    return-object v0
.end method

.method public static provide()Z
    .locals 1

    .line 36
    invoke-static {}, Lcom/bachatas4/android/feature/session/SessionViewModel_HiltModules$KeyModule;->provide()Z

    move-result v0

    return v0
.end method


# virtual methods
.method public get()Ljava/lang/Boolean;
    .locals 0

    .line 28
    invoke-static {}, Lcom/bachatas4/android/feature/session/SessionViewModel_HiltModules_KeyModule_ProvideFactory;->provide()Z

    move-result p0

    invoke-static {p0}, Ljava/lang/Boolean;->valueOf(Z)Ljava/lang/Boolean;

    move-result-object p0

    return-object p0
.end method

.method public bridge synthetic get()Ljava/lang/Object;
    .locals 0

    .line 9
    invoke-virtual {p0}, Lcom/bachatas4/android/feature/session/SessionViewModel_HiltModules_KeyModule_ProvideFactory;->get()Ljava/lang/Boolean;

    move-result-object p0

    return-object p0
.end method
