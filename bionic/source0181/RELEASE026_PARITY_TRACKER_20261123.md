# Bachata S4+ — paridade funcional com o ELF verdadeiro 0.2.6/0.2.7

Referência verificável: `libbachata_native_runtime.so` — SHA-256 `f4ab401c9f05088d5379f466314fc74dadd37f0e7389d120e7490943e0ae7582` (0.2.6 e 0.2.7 idênticos). **Não usar** o ELF antigo incorretamente identificado (`3548cb...`). Auditoria exportada: `Bachata-Release026-vs-Bionic-d8a9-Simbolos-Categorias.csv` (3.630 linhas). O ELF de referência não contém código-fonte; diferenças de símbolo não provam por si só ausência funcional.

## Legenda

- **EQUIVALENTE VERIFICADO NO CÓDIGO:** método com nome diferente mas implementação efetiva correspondente; não duplicar.
- **INTEGRADO, SEM TESTE NO APARELHO:** alteração real conectada, passou fonte/mocks; não declarar paridade completa.
- **NÃO PORTADO:** faltam integração e teste da cadeia inteira.
- **INVESTIGAR:** ABI/CFG diferente, equivalência ainda não estabelecida.

## Matriz que governa o trabalho

| Família | Release 0.2.6 | Estado e equivalente/falta | Confirmação exigida |
|---|---|---|---|
| FIOS2 | `sceFiosArchiveMountSync -> MountAlias("/app0", mount)` | INTEGRADO, SEM TESTE NO APARELHO: clonagem de backend e alias → SAF real; parser PSARC especulativo removido | quatro CUSAs, arquivos da pasta Android |
| VFS/SAF | `SafFsBackend::Open`, `SafBrokerClient::{OpenRead,Stat,List}` | INTEGRADO, SEM TESTE NO APARELHO: `OpenSafGuestFile` com descritores independentes e casefold limitado | CUSA08809/CUSA05170 |
| Shader/SRT | `Arm64SrtEmitter` (12 métodos), `FlattenExtendedUserdataPass` | NÃO PORTADO integralmente: walker bytecode continua diferente do JIT ARM64 do Release; somente casos comprovadamente uniformes Phi/ReadLane/bitcast resolvidos, cache invalidado | CUSA00785, capturas SRT por shader |
| BufferCache | `SynchronizeBufferFromImage` | **EQUIVALENTE VERIFICADO NO CÓDIGO:** `SynchronizeMemoryFromImage` no 0.18.1; chamado por `SynchronizeMemory` na condição texel + !write, mesmas cópias mip `TileImage` | teste GPU/driver |
| BufferCache | `SnapshotGpuWrittenPages`, `UploadMergedCpuWrites`, `DownloadSrtSourcePage`, `AcquireImageStagingSlot` | NÃO PORTADO: exige coerência e proteção GPU→CPU, staging e tracker juntos; não inventar no-op | The Order e possíveis readbacks Shadow |
| TextureCache | `TryQueueTinyReadback`, `DrainTinyReadbacks`, `ResolveDimensionOverlap` | NÃO PORTADO: não equivale a mero `ProcessDownloadImages` sem análise de fusão/cache | shaders/descriptors |
| Rasterizer | `IsolateReadConstGuestBuffer`, `ReadBackGpuWrittenSrtSources`, `BindImageTable` | **ISOLAMENTO ReadConst CPU INTEGRADO, SEM TESTE NO APARELHO**: marcado pelo IR, cria `Buffer` host-visible e mantém vida útil pelo Scheduler; se a GPU escreveu, preserva a versão da BufferCache. **Readback GPU-written e BindImageTable NÃO PORTADOS** | CUSA00785 |
| Rasterizer | `DrawIndirect` | INVESTIGAR: o 0.18.1 já executa indirect draw, mas assinatura e fluxo são diferentes | traços de comandos |
| GPU PM4/CE | snapshot DCB/CCB e CE task FIFO | INTEGRADO antes deste patch (paridade de release anterior), SEM TESTE NO APARELHO; versão de referência mudou | regressão GPU |
| Vulkan Instance | `GetLiveGpuMemoryBudget`, `GetGpuMemoryTelemetry` | INTEGRADO neste patch, SEM TESTE NO APARELHO: Vk EXT + VMA live, não orçamento fixo | GC/sem OOM |
| Vulkan Instance | allocation/freed counters, transientes ETC2/BC, thresholds | NÃO PORTADO: contagem e ganchos de alocação requerem integrar TextureCache/BufferCache | pressão de RAM |
| MemoryManager | `ClampGpuRangeSize` | INTEGRADO neste patch, SEM TESTE NO APARELHO: VMA contígua mapeada e domínio de endereços GPU 40-bit para requisições grandes | CUSA08809 ~−2GiB, CUSA00785 |
| MemoryManager | `EqualsSparseMemory`, `InCachedMappedSpan`, `AddressSpace::Impl::{Map,Protect}` | NÃO PORTADO; assinaturas e fluxo FEX ARM64 precisam ser comparados | boot, FEX |
| Kernel | `sceKernelAllocateDirectMemory` | INVESTIGAR; o mesmo nome existe nos dois ELF mas tamanhos diferem. Não trocar por um corpo antigo sem semântica/ABI | memory map boot |
| Kernel | `FexDispatchPendingSignals`, Pthread signals/cancel, event flags | NÃO PORTADO; possíveis equivalentes no antigo FEX são parciais | CUSA00552 SIGSEGV |
| Loader | `Core::Module(...unique_ptr<IFile>...)`, `LoadLibcInternal` | NÃO PORTADO integralmente; o novo Linker ainda contém carregamento glibc próprio; comparar fontes e fd lifecycle | CUSA00552 |
| HLE/FEX | `HleCallRegistry::Borrow`, `ReturnsToGuest` | NÃO PORTADO integralmente; FEX guest fiber bridge (15 NIDs) integrada antes, mas retorno/sinais são cadeias separadas | Shadow callbacks |
| Android runtime IPC | restart, screenshots, trophies, telemetry, identity | NÃO PORTADO: verificar protocolo do EmulationService antes de adicionar pacotes nativos | restart/trophies/UI |

## Portas de verificação obrigatórias

1. `assert_native_api.py` valida aplicação exata de código, incluindo SRT, clamping GPU e orçamento Vulkan; nenhum método equivale a símbolo dummy.
2. `build-generic.sh` compila as fontes reais `fs.cpp`, `saf_fs_backend.cpp`, `memory.cpp`, `vk_instance.cpp` e `texture_cache.cpp` primeiro; bloqueia build grande se a ABI 0.18.1 quebrar.
3. `native_cache.sh` rejeita cache sem `libFEXCore.a`, e o workflow aceita reparo direcionado; não recompilar FFmpeg/SDL inutilmente.
4. APK assinado só depois de core ARM64 com marcador `BACHATA_CORE_REVISION=<full sha>` e `runtimeVersion` derivado do hash do ELF.
5. Não marcar os quatro jogos como corrigidos só pelo sucesso da compilação. Logs e frames no aparelho são a prova final.

## Status desta revisão

O objetivo **é portar toda a paridade**, mas esta revisão não afirma que os 3.630 símbolos foram portados. Os métodos restantes requerem comparação de CFG, integração em fontes e verificações reais; símbolos privados/inline podem não ser reproduzíveis pelo `nm -D`.


## Tentativa de compilação integrada da paridade — 23/11/2026

O pré-voo automático da revisão `e969124afa07220799aedbc642debcf30c90a22d` passou em `#45256066897`, incluindo testes de x86 libSceFiber, SAF/alias FIOS2, cache nativo, fonte 0.18.1 e verificação obrigatória do gerador de marcadores. A nova compilação Android verifica que `src/core/memory.cpp`, `vk_instance.cpp`, `texture_cache.cpp`, `resource_patching_pass.cpp` e `vk_rasterizer.cpp` compilam contra os headers reais.

Correções nesta revisão (não confundam com soluções de gameplay): SRT Phi/ReadLane comprovadamente uniformes e recaptura por dispatch sem congelamento de leitura inválida; domínio GPU mapeado 40-bit; orçamento GPU Vulkan+VMA dinâmico; origem de buffers ReadConst no IR, snapshots estáveis somente de memória CPU e retenção da cópia até tick concluído. Ref compilado será `BACHATA_CORE_PARITY=20261123-SRT3-CTYPE3-CE1-OWNEDCB-FIBER1-RUNTIME1-RELEASEFIOS2-SAFDIRECT2-GPUCLAMP1-BUDGET1-RCSNAP1`. A atualização do nome do runtime deve ser derivada do hash real do ELF automaticamente.

Os itens restantes da matriz continuam **não portados** até integração coerente e teste; não afirmar equivalência integral ao Release 0.2.6/0.2.7 sem evidência por jogo.
