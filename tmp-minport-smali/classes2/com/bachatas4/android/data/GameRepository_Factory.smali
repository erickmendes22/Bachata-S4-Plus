.class public final Lcom/bachatas4/android/data/GameRepository_Factory;
.super Ljava/lang/Object;
.source "GameRepository_Factory.java"

# interfaces
.implements Ldagger/internal/Factory;


# annotations
.annotation system Ldalvik/annotation/Signature;
    value = {
        "Ljava/lang/Object;",
        "Ldagger/internal/Factory<",
        "Lcom/bachatas4/android/data/GameRepository;",
        ">;"
    }
.end annotation


# instance fields
.field private final contextProvider:Ldagger/internal/Provider;
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "Ldagger/internal/Provider<",
            "Landroid/content/Context;",
            ">;"
        }
    .end annotation
.end field

.field private final gameDaoProvider:Ldagger/internal/Provider;
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "Ldagger/internal/Provider<",
            "Lcom/bachatas4/android/database/GameDao;",
            ">;"
        }
    .end annotation
.end field


# direct methods
.method private constructor <init>(Ldagger/internal/Provider;Ldagger/internal/Provider;)V
    .locals 0
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "(",
            "Ldagger/internal/Provider<",
            "Lcom/bachatas4/android/database/GameDao;",
            ">;",
            "Ldagger/internal/Provider<",
            "Landroid/content/Context;",
            ">;)V"
        }
    .end annotation

    .line 34
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    .line 35
    iput-object p1, p0, Lcom/bachatas4/android/data/GameRepository_Factory;->gameDaoProvider:Ldagger/internal/Provider;

    .line 36
    iput-object p2, p0, Lcom/bachatas4/android/data/GameRepository_Factory;->contextProvider:Ldagger/internal/Provider;

    return-void
.end method

.method public static create(Ldagger/internal/Provider;Ldagger/internal/Provider;)Lcom/bachatas4/android/data/GameRepository_Factory;
    .locals 1
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "(",
            "Ldagger/internal/Provider<",
            "Lcom/bachatas4/android/database/GameDao;",
            ">;",
            "Ldagger/internal/Provider<",
            "Landroid/content/Context;",
            ">;)",
            "Lcom/bachatas4/android/data/GameRepository_Factory;"
        }
    .end annotation

    .line 46
    new-instance v0, Lcom/bachatas4/android/data/GameRepository_Factory;

    invoke-direct {v0, p0, p1}, Lcom/bachatas4/android/data/GameRepository_Factory;-><init>(Ldagger/internal/Provider;Ldagger/internal/Provider;)V

    return-object v0
.end method

.method public static newInstance(Lcom/bachatas4/android/database/GameDao;Landroid/content/Context;)Lcom/bachatas4/android/data/GameRepository;
    .locals 1

    .line 50
    new-instance v0, Lcom/bachatas4/android/data/GameRepository;

    invoke-direct {v0, p0, p1}, Lcom/bachatas4/android/data/GameRepository;-><init>(Lcom/bachatas4/android/database/GameDao;Landroid/content/Context;)V

    return-object v0
.end method


# virtual methods
.method public get()Lcom/bachatas4/android/data/GameRepository;
    .locals 1

    .line 41
    iget-object v0, p0, Lcom/bachatas4/android/data/GameRepository_Factory;->gameDaoProvider:Ldagger/internal/Provider;

    invoke-interface {v0}, Ldagger/internal/Provider;->get()Ljava/lang/Object;

    move-result-object v0

    check-cast v0, Lcom/bachatas4/android/database/GameDao;

    iget-object p0, p0, Lcom/bachatas4/android/data/GameRepository_Factory;->contextProvider:Ldagger/internal/Provider;

    invoke-interface {p0}, Ldagger/internal/Provider;->get()Ljava/lang/Object;

    move-result-object p0

    check-cast p0, Landroid/content/Context;

    invoke-static {v0, p0}, Lcom/bachatas4/android/data/GameRepository_Factory;->newInstance(Lcom/bachatas4/android/database/GameDao;Landroid/content/Context;)Lcom/bachatas4/android/data/GameRepository;

    move-result-object p0

    return-object p0
.end method

.method public bridge synthetic get()Ljava/lang/Object;
    .locals 0

    .line 12
    invoke-virtual {p0}, Lcom/bachatas4/android/data/GameRepository_Factory;->get()Lcom/bachatas4/android/data/GameRepository;

    move-result-object p0

    return-object p0
.end method
