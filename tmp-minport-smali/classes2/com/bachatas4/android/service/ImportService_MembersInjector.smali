.class public final Lcom/bachatas4/android/service/ImportService_MembersInjector;
.super Ljava/lang/Object;
.source "ImportService_MembersInjector.java"

# interfaces
.implements Ldagger/MembersInjector;


# annotations
.annotation system Ldalvik/annotation/Signature;
    value = {
        "Ljava/lang/Object;",
        "Ldagger/MembersInjector<",
        "Lcom/bachatas4/android/service/ImportService;",
        ">;"
    }
.end annotation


# instance fields
.field private final contentImporterProvider:Ldagger/internal/Provider;
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "Ldagger/internal/Provider<",
            "Lcom/bachatas4/android/data/ContentImporter;",
            ">;"
        }
    .end annotation
.end field

.field private final gameRepositoryProvider:Ldagger/internal/Provider;
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "Ldagger/internal/Provider<",
            "Lcom/bachatas4/android/data/GameRepository;",
            ">;"
        }
    .end annotation
.end field

.field private final pkgKeyStoreProvider:Ldagger/internal/Provider;
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "Ldagger/internal/Provider<",
            "Lcom/bachatas4/android/data/PkgKeyStore;",
            ">;"
        }
    .end annotation
.end field


# direct methods
.method private constructor <init>(Ldagger/internal/Provider;Ldagger/internal/Provider;Ldagger/internal/Provider;)V
    .locals 0
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "(",
            "Ldagger/internal/Provider<",
            "Lcom/bachatas4/android/data/ContentImporter;",
            ">;",
            "Ldagger/internal/Provider<",
            "Lcom/bachatas4/android/data/GameRepository;",
            ">;",
            "Ldagger/internal/Provider<",
            "Lcom/bachatas4/android/data/PkgKeyStore;",
            ">;)V"
        }
    .end annotation

    .line 36
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    .line 37
    iput-object p1, p0, Lcom/bachatas4/android/service/ImportService_MembersInjector;->contentImporterProvider:Ldagger/internal/Provider;

    .line 38
    iput-object p2, p0, Lcom/bachatas4/android/service/ImportService_MembersInjector;->gameRepositoryProvider:Ldagger/internal/Provider;

    .line 39
    iput-object p3, p0, Lcom/bachatas4/android/service/ImportService_MembersInjector;->pkgKeyStoreProvider:Ldagger/internal/Provider;

    return-void
.end method

.method public static create(Ldagger/internal/Provider;Ldagger/internal/Provider;Ldagger/internal/Provider;)Ldagger/MembersInjector;
    .locals 1
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "(",
            "Ldagger/internal/Provider<",
            "Lcom/bachatas4/android/data/ContentImporter;",
            ">;",
            "Ldagger/internal/Provider<",
            "Lcom/bachatas4/android/data/GameRepository;",
            ">;",
            "Ldagger/internal/Provider<",
            "Lcom/bachatas4/android/data/PkgKeyStore;",
            ">;)",
            "Ldagger/MembersInjector<",
            "Lcom/bachatas4/android/service/ImportService;",
            ">;"
        }
    .end annotation

    .line 52
    new-instance v0, Lcom/bachatas4/android/service/ImportService_MembersInjector;

    invoke-direct {v0, p0, p1, p2}, Lcom/bachatas4/android/service/ImportService_MembersInjector;-><init>(Ldagger/internal/Provider;Ldagger/internal/Provider;Ldagger/internal/Provider;)V

    return-object v0
.end method

.method public static injectContentImporter(Lcom/bachatas4/android/service/ImportService;Lcom/bachatas4/android/data/ContentImporter;)V
    .locals 0

    .line 58
    iput-object p1, p0, Lcom/bachatas4/android/service/ImportService;->contentImporter:Lcom/bachatas4/android/data/ContentImporter;

    return-void
.end method

.method public static injectGameRepository(Lcom/bachatas4/android/service/ImportService;Lcom/bachatas4/android/data/GameRepository;)V
    .locals 0

    .line 63
    iput-object p1, p0, Lcom/bachatas4/android/service/ImportService;->gameRepository:Lcom/bachatas4/android/data/GameRepository;

    return-void
.end method

.method public static injectPkgKeyStore(Lcom/bachatas4/android/service/ImportService;Lcom/bachatas4/android/data/PkgKeyStore;)V
    .locals 0

    .line 68
    iput-object p1, p0, Lcom/bachatas4/android/service/ImportService;->pkgKeyStore:Lcom/bachatas4/android/data/PkgKeyStore;

    return-void
.end method


# virtual methods
.method public injectMembers(Lcom/bachatas4/android/service/ImportService;)V
    .locals 1

    .line 44
    iget-object v0, p0, Lcom/bachatas4/android/service/ImportService_MembersInjector;->contentImporterProvider:Ldagger/internal/Provider;

    invoke-interface {v0}, Ldagger/internal/Provider;->get()Ljava/lang/Object;

    move-result-object v0

    check-cast v0, Lcom/bachatas4/android/data/ContentImporter;

    invoke-static {p1, v0}, Lcom/bachatas4/android/service/ImportService_MembersInjector;->injectContentImporter(Lcom/bachatas4/android/service/ImportService;Lcom/bachatas4/android/data/ContentImporter;)V

    .line 45
    iget-object v0, p0, Lcom/bachatas4/android/service/ImportService_MembersInjector;->gameRepositoryProvider:Ldagger/internal/Provider;

    invoke-interface {v0}, Ldagger/internal/Provider;->get()Ljava/lang/Object;

    move-result-object v0

    check-cast v0, Lcom/bachatas4/android/data/GameRepository;

    invoke-static {p1, v0}, Lcom/bachatas4/android/service/ImportService_MembersInjector;->injectGameRepository(Lcom/bachatas4/android/service/ImportService;Lcom/bachatas4/android/data/GameRepository;)V

    .line 46
    iget-object p0, p0, Lcom/bachatas4/android/service/ImportService_MembersInjector;->pkgKeyStoreProvider:Ldagger/internal/Provider;

    invoke-interface {p0}, Ldagger/internal/Provider;->get()Ljava/lang/Object;

    move-result-object p0

    check-cast p0, Lcom/bachatas4/android/data/PkgKeyStore;

    invoke-static {p1, p0}, Lcom/bachatas4/android/service/ImportService_MembersInjector;->injectPkgKeyStore(Lcom/bachatas4/android/service/ImportService;Lcom/bachatas4/android/data/PkgKeyStore;)V

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

    .line 13
    check-cast p1, Lcom/bachatas4/android/service/ImportService;

    invoke-virtual {p0, p1}, Lcom/bachatas4/android/service/ImportService_MembersInjector;->injectMembers(Lcom/bachatas4/android/service/ImportService;)V

    return-void
.end method
