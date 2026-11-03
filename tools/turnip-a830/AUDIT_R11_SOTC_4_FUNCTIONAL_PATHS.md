# R11 — integração prioritária SotC A830 (2026-11-03)

## Artefato real, validado

- Branch de código: `fix/a830-gamehub-kgsl-4gb-parity-r11-20261103`
- Branch de compilação controlada: `build/a830-gamehub-r11-integrated-20261103`
- Build de driver AArch64: Actions [#41665336347](https://github.com/erickmendes22/Bachata-S4-Plus/actions/runs/41665336347) — **SUCCESS**, incluindo integridade do ZIP e inspeção da `libvulkan_freedreno.so`.
- Validação conjunta na árvore Mesa pinada: Actions [#41665113610](https://github.com/erickmendes22/Bachata-S4-Plus/actions/runs/41665113610) — **SUCCESS**, os quatro blocos aplicados simultaneamente.
- KGSL C++ boundary test (16 casos): Actions [#41663779602](https://github.com/erickmendes22/Bachata-S4-Plus/actions/runs/41663779602) — **SUCCESS**.
- ZIP instalável com `libvulkan_freedreno.so` e `meta.json`: SHA-256 `4c30251a0fdecfce533b863520dd8b811ef7ec775d138adcbf1a88eb5abbd80b`.
- ELF compilado: SHA-256 `ba10389c1b22cb74eda7e094693a14d7f270d26bc92b408d3964cc5f7d68f322`, 13.595.504 bytes, ELF64 AArch64.
- ELF original GameHub funcional: SHA-256 `1a109bee1ad087aceee8436479c95c4cd3e66de0778bc79fc3ce9f637f9fe404`.

## Matriz de cobertura — alterações no próprio driver

| Bloco | Integrações em R11 | Evidência | Status |
|---|---|---|---|
| IR3 e draw state | KHR barycentric NIR lowering, vertex side effects, validação de primitivas, draws indexados diretos e indiretos, offsets DrawID, const shared | ELF: caminho direto `0x94c42c–0x94c93c`; upstream backports pinados; fonte conjunta | Integrado/compilado; shader-output equivalence não validada |
| Blit, resolve e UBWC | RGB96 sampled/transfer por CP_MEMCPY linear, gralloc FD/stride/offset preservados, FourCC/modifier sobrepostos somente se obtidos, seleção GMEM/SYSMEM por MSAA | Função GameHub `0xca2ec0–0xca3178`; teste da fonte, formatos e renderpass | Integrado/compilado; conteúdo final dos render targets não validado |
| Cache e sincronização | Promoção antecipada da invalidação GMEM e slice fence às operações globais do GameHub, sem patches R5/R6 duplicados | GameHub: 19 opcodes ARM64 e 9 pares PM4, teste de flags; pré-validação R10 | Integrado/compilado; sem prova visual |
| KGSL e memória | Recuperação de alias IB que cruza 4GB com retry `KGSL_MEMFLAGS_FORCE_32BIT`; cleanup e preservação de GPUMEM_BIND_RANGES | GameHub `0xa3c698–0xa3cb54`, 11 opcodes verificados, 16 casos compilados | Integrado/compilado; sem prova visual |

## O que esta documentação NÃO afirma

As verificações garantem que a fonte foi integrada, compilada e que as
rotinas comparadas reproduzem caminhos **específicos** do GameHub. Elas
**não** demonstram equivalência funcional de toda a execução do driver
nem que o Shadow of the Colossus deixou de apresentar **ghosting, flicker
e texturas ausentes** na Adreno A830. Isso requer resultado comparativo de
renderização no aparelho sob a mesma carga e as mesmas configurações.

Avisos compartilhados com o driver GameHub funcional (`IT_SET_PREDICATION`,
`not fully GPU mapped`, nove formatos Vulkan incompletos) foram excluídos
da causalidade diferencial: não motivaram alterações do emulador.

Os nomes de intrínsecos do IR3 presentes apenas no ELF 26.3 não foram
copiados sem verificar semântica; a V38 usa lowering/nomes distintos.
Se ocorrerem bugs visuais na R11, o trabalho restante é correlação por
**diferença de saída gráfica real**, não outra rodada de patches aleatórios.

Instalar somente o arquivo ZIP interno do artefato Actions no importador
de driver Vulkan da aplicação; o ZIP exterior de Actions é um envelope.
