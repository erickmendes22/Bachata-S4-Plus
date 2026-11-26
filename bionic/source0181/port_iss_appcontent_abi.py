"""Match the inFAMOUS AppContent boot and absent entitlement ABI.

Port runtime_content.c initializes all 40 bytes of BootParam; runtime_infamous.c
reports 0x80d90005 for absent add-on. Preserve genuine loaded DLC and licenses.
"""
from pathlib import Path

def apply(root:Path):
    p=Path(root)/"src/core/libraries/app_content/app_content.cpp"
    s=p.read_text()
    def rewrite(marker,transform):
        nonlocal s
        a=s.index(marker);o=s.index("{",a);depth=1;b=o+1
        while depth:
            depth+=(s[b]=="{")-(s[b]=="}");b+=1
        s=s[:a]+transform(s[a:b])+s[b:]
    def target(body):
        o=body.index("{")
        return body[:o+1]+'''
    const auto bachata_serial=Common::ElfInfo::Instance().GameSerial();
    const bool bachata_iss=bachata_serial=="CUSA00004"||bachata_serial=="CUSA00223";
'''+body[o+1:]
    def init(body):
        body=target(body)
        insert='''    if (bachata_iss && (!initParam || !bootParam)) {
        return ORBIS_APP_CONTENT_ERROR_PARAMETER;
    }
'''
        o=body.index('    LOG_WARNING(Lib_AppContent, "(DUMMY) called");')
        body=body[:o]+insert+body[o:]
        o=body.rindex('    return ORBIS_OK;')
        return body[:o]+'''    if (bachata_iss) {
        static_assert(sizeof(OrbisAppContentBootParam)==40);
        *bootParam=OrbisAppContentBootParam{};
        LOG_INFO(Lib_AppContent,"BACHATA_ISS_APPCONTENT_BOOT initialized 40 bytes");
    }
'''+body[o:]
    def addon(body):
        body=target(body)
        old='    return ORBIS_APP_CONTENT_ERROR_DRM_NO_ENTITLEMENT;'
        if body.count(old)!=1: raise RuntimeError("ISS add-on absence return drift")
        return body.replace(old,'''    if (bachata_iss) {
        LOG_INFO(Lib_AppContent,"BACHATA_ISS_APPCONTENT_ABSENT returning NOT_FOUND");
        return ORBIS_APP_CONTENT_ERROR_NOT_FOUND;
    }
'''+old,1)
    rewrite('int PS4_SYSV_ABI sceAppContentInitialize(',init)
    rewrite('int PS4_SYSV_ABI sceAppContentGetAddcontInfo(',addon)
    p.write_text(s)
    print("BACHATA_ISS_APPCONTENT_ABI applied")
    return {"boot":"40 bytes zeroed on successful initialization","missing_addon":"NOT_FOUND",
            "installed_dlc":"existing entitlement search untouched"}
