# SotC A830: identificação exata dos drivers nos logs (3 nov 2026)

## Evidência binária, não inferência por nome de versão

| Log SotC Android | SHA-256 do ZIP em `gpu-drivers/<hash>/` | Driver identificado pela comparação local | Versão exposta |
|---|---|---|---|
| `ShadowOfTheColossus-Logs-20261103-084155.zip` | `2aeb3b02444df8e2d241c293944705bb3b627f6cb51dfb10ab16385ef5e72756` | `Turnip_Gen8_V38_A830_GameHub_Drawstate_R8_20261103.zip` | 26.99.99 |
| `ShadowOfTheColossus-Logs-20261103-085512.zip` | `8255659cc205110e0fa89f2d364292b86fe563a2cedafbc41915bead5a611ecb` | `Turnip_GameHub_26.3_DD_GMEM_PWRMAX_EXPERIMENTAL.zip` (arquivos (1)/(2) idênticos) | 26.2.99 |

**O teste das 08:55 NÃO é da R9**: o hash exato corresponde ao ZIP GameHub modificado de 31/10, cujo ELF tem SHA-256 `4f242a453496ab27fc29be950d632edbae494dcc0c9b7d56c37c7ebdffe42df9`.
A R9 arquivada tem SHA-256 do ZIP `6d670757fd840c96ea503bb5642a3011152bb8b3c31e8fda29895f65fd11b2fa` e ELF `b8a589ee04205778935f8a0b1e3f396c5fa55edf22a7427e6ab0ac04906bb496`.
O ELF GameHub original de engenharia reversa (não modificado) possui SHA-256 `1a109bee1ad087aceee8436479c95c4cd3e66de0778bc79fc3ce9f637f9fe404`.

## Sintomas nas duas execuções (R8 e GameHub modificado)

Os logs de ambas contêm:
- `SotC experimental async graphics pipelines: 1`.
- `SotC render completeness: ... queued geometry draws can be skipped until ready`.
- `Unimplemented IT_SET_PREDICATION (reported once)` em `liverpool.cpp`.
- vários `Tracking memory region ... which is not fully GPU mapped` em `page_manager.cpp`.
- `Game texture memory 0% free` / pool texturas, exigindo mip mais grosseiro.

O aviso de `Cached permutation ... conflicts` aparece no log R8 (08:41)
e não no posterior; ele pertence a `vk_pipeline_serialization.cpp`
do **emulador**, não comprova bug de cache IR3 da Turnip.

## Conclusão técnica

Uma discrepância **comprovada** de gralloc FourCC/modifier da R9 foi corrigida
na branch desta auditoria, mas não explica todos esses sintomas: o driver GameHub
também é carregado pelo port Android quando os avisos continuam.
Logo, a resolução completa precisa considerar os caminhos de GPU do emulador,
em especial o descarte de draws, as regiões de memória GPU não mapeadas e a
predicação PM4, independentemente da paridade de driver. Isso evita tratar
sintomas do emulador como diferenças do driver e gerar builds repetidas da
Turnip sem correspondência causal.

O descarte de desenhos durante compilação assíncrona foi corrigido no **código
staged** do renderer SotC em:
`erickmendes22/gow3_android_daedalus_fork`,
branch `fix/sotc-async-graphics-draw-completeness-20261103`.
A pré-validação sem APK passou na Actions #41641595788.
**Ainda não foi validado em hardware A830.** Não afirmar correção de ghosting,
piscadas nem texturas ausentes só com os testes de source.
