.class public final Lcom/bachatas4/android/data/PkgExtractionLocation_Factory;
.super Ljava/lang/Object;
.source "PkgExtractionLocation_Factory.java"

# interfaces
.implements Ldagger/internal/Factory;


# annotations
.annotation system Ldalvik/annotation/Signature;
    value = {
        "Ljava/lang/Object;",
        "Ldagger/internal/Factory<",
        "Lcom/bachatas4/android/data/PkgExtractionLocation;",
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


# direct methods
.method private constructor <init>(Ldagger/internal/Provider;)V
    .locals 0
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "(",
            "Ldagger/internal/Provider<",
            "Landroid/content/Context;",
            ">;)V"
        }
    .end annotation

    .line 30
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V

    .line 31
    iput-object p1, p0, Lcom/bachatas4/android/data/PkgExtractionLocation_Factory;->contextProvider:Ldagger/internal/Provider;

    return-void
.end method

.method public static create(Ldagger/internal/Provider;)Lcom/bachatas4/android/data/PkgExtractionLocation_Factory;
    .locals 1
    .annotation system Ldalvik/annotation/Signature;
        value = {
            "(",
            "Ldagger/internal/Provider<",
            "Landroid/content/Context;",
            ">;)",
            "Lcom/bachatas4/android/data/PkgExtractionLocation_Factory;"
        }
    .end annotation

    .line 40
    new-instance v0, Lcom/bachatas4/android/data/PkgExtractionLocation_Factory;

    invoke-direct {v0, p0}, Lcom/bachatas4/android/data/PkgExtractionLocation_Factory;-><init>(Ldagger/internal/Provider;)V

    return-object v0
.end method

.method public static newInstance(Landroid/content/Context;)Lcom/bachatas4/android/data/PkgExtractionLocation;
    .locals 1

    .line 44
    new-instance v0, Lcom/bachatas4/android/data/PkgExtractionLocation;

    invoke-direct {v0, p0}, Lcom/bachatas4/android/data/PkgExtractionLocation;-><init>(Landroid/content/Context;)V

    return-object v0
.end method


# virtual methods
.method public get()Lcom/bachatas4/android/data/PkgExtractionLocation;
    .locals 0

    .line 36
    iget-object p0, p0, Lcom/bachatas4/android/data/PkgExtractionLocation_Factory;->contextProvider:Ldagger/internal/Provider;

    invoke-interface {p0}, Ldagger/internal/Provider;->get()Ljava/lang/Object;

    move-result-object p0

    check-cast p0, Landroid/content/Context;

    invoke-static {p0}, Lcom/bachatas4/android/data/PkgExtractionLocation_Factory;->newInstance(Landroid/content/Context;)Lcom/bachatas4/android/data/PkgExtractionLocation;

    move-result-object p0

    return-object p0
.end method

.method public bridge synthetic get()Ljava/lang/Object;
    .locals 0

    .line 11
    invoke-virtual {p0}, Lcom/bachatas4/android/data/PkgExtractionLocation_Factory;->get()Lcom/bachatas4/android/data/PkgExtractionLocation;

    move-result-object p0

    return-object p0
.end method
