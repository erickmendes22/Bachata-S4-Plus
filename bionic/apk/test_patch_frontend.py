import subprocess,sys,tempfile
from pathlib import Path
from patch_frontend import CLASS,OLD
with tempfile.TemporaryDirectory() as d:
    p=Path(d)/CLASS
    p.parent.mkdir(parents=True)
    p.write_text(".method static constructor <clinit>()V\n"+OLD+"\n.end method\n")
    subprocess.run([sys.executable,str(Path(__file__).with_name("patch_frontend.py")),d],check=True)
    assert p.read_text().count(".method public static final loadCoreAndSetupJNI(Z)V")==1
    assert subprocess.run([sys.executable,str(Path(__file__).with_name("patch_frontend.py")),d]).returncode!=0
print("SMALI_PATCH_REGRESSION_PASS")
