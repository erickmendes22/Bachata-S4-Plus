#!/usr/bin/env python3
"""Validate all existing Spider-Man patch sites on supplied uncompressed SELF."""
import argparse,hashlib,json,struct,xml.etree.ElementTree as E
from pathlib import Path
from capstone import Cs,CS_ARCH_X86,CS_MODE_64
EXPECTED={
0x1439671:'8b534c8b4b50',0x2e0ca22:'cc'*16,0x1275be3:'0f4548100f455014',
0x125d12d:'0f84b5000000',0x137b613:'730f',
0x905dd:'c5fa1005a3547602',0x9060f:'c5fa100571547602',0x90641:'c5fa10053f547602',
0x905f2:'c5fa590592547602',0x90624:'c5fa590560547602',0x90656:'c5fa59052e547602',
0xab6e3:'666666662e0f1f840000000000',0xab6f0:'c5782e3540b17402733a',
0xabb77:'0f8273fbffff',0xd5335:'c5fa5980c4f02000',0x125a866:'c5fa101d6a8b7501'}
def port(eboot,template,out):
    b=Path(eboot).read_bytes();assert b[:4]==bytes.fromhex('4f153d1d')
    count=struct.unpack_from('<H',b,24)[0];elf=32+32*count;assert b[elf:elf+4]==b'\x7fELF'
    entries=[struct.unpack_from('<QQQQ',b,32+32*i) for i in range(count)]
    entry=next(x for x in entries if x[0]>>20==0 and x[0]&0x800)
    assert entry[2]==entry[3] and entry[0]&0x8==0
    text=b[entry[1]:entry[1]+entry[2]]
    for va,original in EXPECTED.items():assert text[va:va+len(bytes.fromhex(original))].hex()==original,hex(va)
    p=0x125a866;target=p+8+struct.unpack_from('<i',text,p+4)[0]
    f30,f60=struct.unpack_from('<ff',text,target);assert abs(f30-1/30)<1e-8 and abs(f60-1/60)<1e-8
    root=E.fromstring(Path(template).read_bytes());ids=root.find('TitleID');ids.clear()
    for cusa in ['CUSA02999','CUSA02299']:E.SubElement(ids,'ID').text=cusa
    options=[];sites=set();md=Cs(CS_ARCH_X86,CS_MODE_64)
    for m in root.findall('Metadata'):
        m.set('Name',m.get('Name').split(' - R')[0]);m.set('Author','erickmendes22')
        options.append(m.get('Name'))
        for l in m.findall('./PatchList/Line'):
            va=int(l.get('Address'),16)-0x400000;replacement=bytes.fromhex(l.get('Value'))
            assert va in EXPECTED
            original=text[va:va+len(replacement)]
            assert len(original)==len(replacement)
            l.set('Expected',original.hex());sites.add(va)
            # Patches cover complete instruction spans or verified unused INT3 bytes.
            if va!=0x2e0ca22:
                decoded=list(md.disasm(replacement,va));assert sum(i.size for i in decoded)==len(replacement)
    E.indent(root,space='    ');dest=Path(out);dest.mkdir(parents=True,exist_ok=True)
    xml=E.tostring(root,encoding='utf-8',xml_declaration=True)+b'\n'
    (dest/'MarvelsSpiderMan_CUSA02999_0100.xml').write_bytes(xml)
    report={'ebootSha256':hashlib.sha256(b).hexdigest(),'codeSha256':hashlib.sha256(text).hexdigest(),
            'ids':['CUSA02999','CUSA02299'],'options':options,'verifiedSites':len(sites),
            'oldAddressesMatchSuppliedEboot':True,'allDisabledByDefault':all(m.get('isEnabled')=='false' for m in root.findall('Metadata')),
            'fpsConstants':[f30,f60],'deviceValidated':False}
    (dest/'spider-validation.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('eboot');p.add_argument('template');p.add_argument('out');a=p.parse_args();port(a.eboot,a.template,a.out)
