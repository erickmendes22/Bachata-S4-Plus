#!/usr/bin/env python3
"""Patch only Android integration boundaries in the three decompiled APKs."""
from pathlib import Path
import argparse
import re

BRIDGE = "Lcom/bachata/ports/PortBridge;"
HOST = "com.bachatas4.plusapp"
ORDER = "ro/cobrabm/fexdroid/Order1886Activity"
SOTC_MAIN = "com/gow3/android/MainActivity"
SOTC_GAME = "ro/cobrabm/fexdroid/GameActivity"

def unique(root, name):
    matches = list(root.glob("smali*/" + name + ".smali"))
    if len(matches) != 1:
        raise RuntimeError(f"expected exactly one {name}, got {matches}")
    return matches[0]

def method(text, sig):
    pat = r"(?ms)^\.method [^\n]*" + re.escape(sig) + r"\n.*?^\.end method"
    matches = list(re.finditer(pat, text))
    if len(matches) != 1:
        raise RuntimeError(f"method anchor {sig}: {len(matches)}")
    return matches[0]

def edit_method(text, sig, func):
    m = method(text, sig)
    return text[:m.start()] + func(m.group()) + text[m.end():]

def before_instruction(body, pattern, code):
    m = re.search(pattern, body, re.M)
    if not m:
        raise RuntimeError("instruction anchor missing: " + pattern)
    return body[:m.start()] + code + body[m.start():]

def activity(root, name, sotc=False, main=False):
    path = unique(root, name)
    s = path.read_text()
    superclass = re.search(r"(?m)^\.super (L[^;]+;)", s).group(1)
    attach = "attachBaseContext(Landroid/content/Context;)V"
    wrap = f"    invoke-static {{p1}}, {BRIDGE}->wrap(Landroid/content/Context;)Landroid/content/Context;\n    move-result-object p1\n\n"
    if re.search(r"(?m)^\.method [^\n]*" + re.escape(attach), s):
        s = edit_method(s, attach, lambda t: before_instruction(t, r"^    invoke-", wrap))
    else:
        s += ("\n.method protected " + attach + "\n    .locals 0\n" + wrap +
              f"    invoke-super {{p0, p1}}, {superclass}->attachBaseContext(Landroid/content/Context;)V\n"
              "    return-void\n.end method\n")
    def init(t):
        code = f"    invoke-static {{p0}}, {BRIDGE}->prepareActivity(Landroid/app/Activity;)V\n\n"
        t = before_instruction(t,r"^    invoke-super(?:/range)? .*->onCreate\(Landroid/os/Bundle;\)V",code)
        if not sotc:
            # The original Activity initializes UI and preparation state before
            # starting the original game path. Do not bypass its prepare step.
            k = t.rfind("    return-void")
            if k < 0: raise RuntimeError("Order onCreate exit missing")
            t = t[:k] + f"    invoke-direct {{p0}}, L{name};->startGame()V\n\n" + t[k:]
        return t
    s = edit_method(s,"onCreate(Landroid/os/Bundle;)V",init)
    if main:
        def permission(t):
            return (t.splitlines()[0] + "\n    .locals 1\n" +
                    f"    invoke-static {{p0}}, {BRIDGE}->hasGameAccess(Landroid/app/Activity;)Z\n"
                    "    move-result v0\n    return v0\n.end method")
        s = edit_method(s,"hasStoragePermission()Z",permission)
    path.write_text(s)

def patch_donor(root, kind):
    stats={"starts":0,"identity":0,"resources":0}
    for base in root.glob("smali*"):
        for p in base.rglob("*.smali"):
            rel=p.relative_to(base).as_posix()
            if not rel.startswith(("ro/cobrabm/fexdroid/","com/gow3/android/")):
                continue
            s=p.read_text()
            s,n=re.subn(r"invoke-virtual(/range)? (\{[^\n]*\}), Ljava/lang/ProcessBuilder;->start\(\)Ljava/lang/Process;",
                        lambda m:"invoke-static"+(m.group(1) or "")+" "+m.group(2)+", "+BRIDGE+"->start(Ljava/lang/ProcessBuilder;)Ljava/lang/Process;",s)
            stats["starts"]+=n
            if kind=="sotc":
                # Only standalone identity strings, not embedded payload
                # manifest JSON or resource package names.
                s,n=re.subn(r'(const-string(?:/jumbo)? [vp]\d+, )"com\.sotc\.android\.daedalus"',
                             lambda m:m.group(1)+'"'+HOST+'"',s)
                stats["identity"]+=n
                s,n=re.subn(r"invoke-virtual(/range)? (\{[^\n]*\}), Landroid/content/res/Resources;->getIdentifier\(Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;\)I",
                    lambda m:"invoke-static"+(m.group(1) or "")+" "+m.group(2)+", "+BRIDGE+"->resourceIdentifier(Landroid/content/res/Resources;Ljava/lang/String;Ljava/lang/String;Ljava/lang/String;)I",s)
                stats["resources"]+=n
            p.write_text(s)
    if not stats["starts"]:raise RuntimeError(f"{kind}: no donor process boundaries")
    if kind=="order":
        activity(root,ORDER)
    else:
        if not stats["identity"]:raise RuntimeError("missing SotC identity boundaries")
        activity(root,SOTC_MAIN,sotc=True,main=True)
        activity(root,SOTC_GAME,sotc=True)
    print(kind,stats)

def patch_host(root):
    p=unique(root,"com/bachatas4/android/feature/session/SessionViewModel$launch$1")
    s=p.read_text()
    def route(t):
        pat=(r"(?m)^    invoke-static \{v0\}, Lcom/bachatas4/android/feature/session/SessionViewModel;"
             r"->access\$getContext\$p\([^\n]+\)Landroid/content/Context;\n\n    move-result-object v0\n")
        # Find the actual launch context register; the old source is pinned
        # and the APK is independently hash-verified before this edit.
        m=re.search(pat,t)
        if not m:
            # Different debug line metadata may separate the two instructions.
            pat=(r"(?m)^    invoke-static \{v0\}, Lcom/bachatas4/android/feature/session/SessionViewModel;"
                 r"->access\$getContext\$p\([^\n]+\)Landroid/content/Context;\s+move-result-object v0\n")
            m=re.search(pat,t)
        if not m:raise RuntimeError("Bachata session launch context anchor missing")
        code=("\n    invoke-static {v0, p1}, "+BRIDGE+"->tryLaunch(Landroid/content/Context;Ljava/lang/Object;)Z\n"
              "    move-result v1\n    if-eqz v1, :bachata_generic_route\n"
              "    sget-object v1, Lkotlin/Unit;->INSTANCE:Lkotlin/Unit;\n"
              "    return-object v1\n\n    :bachata_generic_route\n")
        return t[:m.end()]+code+t[m.end():]
    s=edit_method(s,"invokeSuspend(Ljava/lang/Object;)Ljava/lang/Object;",route)
    p.write_text(s)
    print("host launch route patched",p)

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("kind",choices=["order","sotc","bachata"])
    p.add_argument("root",type=Path)
    a=p.parse_args()
    if a.kind=="bachata":patch_host(a.root)
    else:patch_donor(a.root,a.kind)
