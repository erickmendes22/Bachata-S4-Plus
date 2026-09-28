.class public final Lcom/bachatas4/android/service/EmulationService_MembersInjector;
.super Ljava/lang/Object;
.source "EmulationService_MembersInjector.java"

# interfaces
.implements Ldagger/MembersInjector;


# annotations
.annotation system Ldalvik/annotation/Signature;
    value = {
        "Ljava/lang/Object;",
        "Ldagger/MembersInjector<",
        "Lcom/bachatas4/android/service/EmulationService;",
        ">;"
    }
.end annotation


# instance fields
.field private final launchProfileProvider:Ldagger/internal/Provider;
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "Ldagger/internal/Provider<",
            "Lcom/bachatas4/android/RuntimeLaunchProfileProvider;",
            ">;"
        }
    .end annotation
.end field


# direct methods
.method private constructor <init>(Ldagger/internal/Provider;)V
    .locals 0
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "(",
            "Ldagger/internal/Provider<",
            "Lcom/bachatas4/android/RuntimeLaunchProfileProvider;",
            ">;)V"
        }
    .end annotation

    .line 30
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    .line 31
    iput-object p1, p0, Lcom/bachatas4/android/service/EmulationService_MembersInjector;->launchProfileProvider:Ldagger/internal/Provider;

    return-void
.end method

.method public static create(Ldagger/internal/Provider;)Ldagger/MembersInjector;
    .locals 1
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "(",
            "Ldagger/internal/Provider<",
            "Lcom/bachatas4/android/RuntimeLaunchProfileProvider;",
            ">;)",
            "Ldagger/MembersInjector<",
            "Lcom/bachatas4/android/service/EmulationService;",
            ">;"
        }
    .end annotation

    .line 41
    new-instance v0, Lcom/bachatas4/android/service/EmulationService_MembersInjector;

    invoke-direct {v0, p0}, Lcom/bachatas4/android/service/EmulationService_MembersInjector;-><init>(Ldagger/internal/Provider;)V

    return-object v0
.end method

.method public static injectLaunchProfileProvider(Lcom/bachatas4/android/service/EmulationService;Lcom/bachatas4/android/RuntimeLaunchProfileProvider;)V
    .locals 0

    .line 47
    iput-object p1, p0, Lcom/bachatas4/android/service/EmulationService;->launchProfileProvider:Lcom/bachatas4/android/RuntimeLaunchProfileProvider;

    return-void
.end method


# virtual methods
.method public injectMembers(Lcom/bachatas4/android/service/EmulationService;)V
    .locals 0

    .line 36
    iget-object p0, p0, Lcom/bachatas4/android/service/EmulationService_MembersInjector;->launchProfileProvider:Ldagger/internal/Provider;

    invoke-interface {p0}, Ldagger/internal/Provider;->get()Ljava/lang/Object;

    move-result-object p0

    check-cast p0, Lcom/bachatas4/android/RuntimeLaunchProfileProvider;

    invoke-static {p1, p0}, Lcom/bachatas4/android/service/EmulationService_MembersInjector;->injectLaunchProfileProvider(Lcom/bachatas4/android/service/EmulationService;Lcom/bachatas4/android/RuntimeLaunchProfileProvider;)V

    return-void
.end method

.method public bridge synthetic injectMembers(Ljava/lang/Object;)V
    .locals 0
    .annotation system Ldalvik/annotation/MethodParameters;
        accessFlags = {
            0x1000
        }
        names = {
            null
        }
    .end annotation

    .line 11
    check-cast p1, Lcom/bachatas4/android/service/EmulationService;

    invoke-virtual {p0, p1}, Lcom/bachatas4/android/service/EmulationService_MembersInjector;->injectMembers(Lcom/bachatas4/android/service/EmulationService;)V

    return-void
.end method
