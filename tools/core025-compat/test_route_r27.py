#!/usr/bin/env python3
"""Execute the full Linux ARM64 dispatcher, including path construction and execve."""
import io,struct,json,sys
from pathlib import Path
from elftools.elf.elffile import ELFFile
from unicorn import Uc,UC_ARCH_ARM64,UC_MODE_ARM,UC_HOOK_INTR
from unicorn.arm64_const import *
def sfo(title,kind=0x204):
 key=b'TITLE_ID\0';data=title.encode()+b'\0';base=20+16+len(key)
 return struct.pack('<5I',0x46535000,0x101,36,base,1)+struct.pack('<HHIII',0,kind,len(data),len(data),0)+key+data
REG=[UC_ARM64_REG_X0,UC_ARM64_REG_X1,UC_ARM64_REG_X2,UC_ARM64_REG_X3]
def run(binary,args,env=None,files=None,bias=0):
 u=Uc(UC_ARCH_ARM64,UC_MODE_ARM);u.mem_map(bias,0x40000);e=ELFFile(io.BytesIO(binary))
 for s in e.iter_segments():
  if s['p_type']=='PT_LOAD':u.mem_write(bias+s['p_vaddr'],s.data())
 u.mem_map(0x800000,0x100000);sp=0x8f0000;buf=0x8f4000;args=['/runtime/host/shadps4-arm64-fex']+args;env=env or ['TEST=1'];ptrs=[]
 for s in args+env:
  ptrs.append(buf);d=s.encode()+b'\0';u.mem_write(buf,d);buf+=len(d)
 q=[len(args),*ptrs[:len(args)],0,*ptrs[len(args):],0];u.mem_write(sp,struct.pack('<'+'Q'*len(q),*q));u.reg_write(UC_ARM64_REG_SP,sp)
 def cstr(p):
  b=bytearray()
  while p and len(b)<20000:
   v=u.mem_read(p,1)[0];p+=1
   if not v:break
   b.append(v)
  return b.decode(errors='replace')
 def vector(p):
  out=[]
  for _ in range(510):
   v=struct.unpack('<Q',u.mem_read(p,8))[0];p+=8
   if not v:return out
   out.append(cstr(v))
  raise AssertionError('argv not terminated')
 fds={};logs=[];out={};opened=[]
 def intr(uc,n,unused):
  op=uc.reg_read(UC_ARM64_REG_X8);a=[uc.reg_read(r) for r in REG];ret=0
  if op==56:
   path=cstr(a[1]);opened.append(path)
   if path in (files or {}):fds[7]=(files[path],0);ret=7
   else:ret=-2
  elif op==63:
   data,pos=fds[a[0]];d=data[pos:pos+a[2]];uc.mem_write(a[1],d);fds[a[0]]=(data,pos+len(d));ret=len(d)
  elif op==57:ret=0
  elif op==64:logs.append(bytes(uc.mem_read(a[1],a[2])).decode());ret=a[2]
  elif op==78:
   d=b'/lib/ld-linux-aarch64.so.1';uc.mem_write(a[2],d);ret=len(d)
  elif op==221:
   out.update(executable=cstr(a[0]),argv=vector(a[1]),env=vector(a[2]),logs=logs,opened=opened);uc.emu_stop()
  elif op==93:out['exit']=a[0];uc.emu_stop()
  else:raise AssertionError(f'unmodeled syscall {op}')
  uc.reg_write(UC_ARM64_REG_X0,ret&((1<<64)-1))
 u.hook_add(UC_HOOK_INTR,intr);u.emu_start(bias+e['e_entry'],bias+0x40000,count=300000)
 assert out and 'argv' in out,out
 assert out['env']==env,out
 assert all('023' not in x for x in out['argv']+out['logs']),out
 return out

def test(path):
 b=Path(path).read_bytes();cases=[]
 for bias in [0,0x7000000000]:
  for title,want in [('CUSA18723','024'),('CUSA28527','024'),('CUSA28863','024'),('CUSA02299','025'),('CUSA02999','025'),('CUSA11993','025'),('CUSA00552','025'),('CUSA00560','025'),('CUSA01715','025'),('CUSA01623','025'),('CUSA00093','020'),('CUSA57548','025'),('CUSA187230','025')]:
   for mode in ['argv','env','sfo']:
    root='/games/'+(title if mode=='argv' else 'custom');args=['--override-root',root,'-g','eboot.bin'];env=['TEST=1']+(['GAME='+title] if mode=='env' else []);files={root+'/sce_sys/param.sfo':sfo(title)} if mode=='sfo' else {}
    expected='025' if title=='CUSA00093' and mode=='sfo' else want
    o=run(b,args,env,files,bias);assert any(x.endswith('shadps4-arm64-'+expected) for x in o['argv']),(title,mode,o)
    assert o['argv'][-len(args):]==args,o
    assert f'core={expected}' in ''.join(o['logs']),o
    cases.append((bias,title,mode,want))
  for data in [b'black ops 2\0',sfo('CUSA18723',0x404),sfo('CUSA18723')[:25],sfo('CUSA18723').replace(b'TITLE_ID',b'NOT_ANID')]:
   o=run(b,['--override-root','/games/custom','-g','eboot.bin'],files={'/games/custom/sce_sys/param.sfo':data},bias=bias)
   assert any(x.endswith('shadps4-arm64-025') for x in o['argv']),o;cases.append((bias,'malformed','sfo','025'))
  # Preserve the original Driveclub SFO route when -g is an absolute executable.
  o=run(b,['-g','/games/custom/eboot.bin'],files={'/games/custom/sce_sys/param.sfo':sfo('CUSA00093')},bias=bias)
  assert any(x.endswith('shadps4-arm64-020') for x in o['argv']),o;cases.append((bias,'Driveclub','absolute','020'))
 return {'cases':len(cases),'fullDispatcherExecve':True,'argvAndEnvironmentPreserved':True,'core023Absent':True,'deviceValidated':False}
if __name__=='__main__':print(json.dumps(test(sys.argv[1]),indent=2))
