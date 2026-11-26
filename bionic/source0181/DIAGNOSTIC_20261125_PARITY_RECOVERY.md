# Diagnóstico e integração funcional — 25/11/2026

## Escopo e referências

Esta integração mantém o Bachata shadPS4 0.18.1 ARM64 Bionic com FEX nos dois
cores. Preserva a interface, JNI, SAF, saves, controles e seleção de driver do
aplicativo. Nenhum APK, executável, DSO ou runtime completo dos ports foi
incorporado. A adaptação usa as fontes que os scripts dos doadores efetivamente
montam para compilação, comparadas com a fonte Bachata após seus overlays.

| Componente | Revisão usada como referência |
|---|---|
| Base ARM64 | `zenithblue-oss/shadps4-arm64@be6bc2e9c60799e071dd2fafa6216e8d80ec619c` |
| shadPS4 0.18.1 | `3912336fdfffbd5c99b59d92e997ea6ebd62216c` |
| FEX | `f2b679f6028ce1c38875233aecfcf5d3f8ebecec` |
| Order PC | `JulioCacko/The-Order-1886_pc@c53cd01d032995fe622033623ab64b4cf6b02233` |
| Order Android/staging | `erickmendes22/gow3_android_daedalus_fork@756a4f0cc603b02971d45b36354143249a4fe492` |
| SotC PC | `AjncSystem/ShadowOfTheColossus-PC@732cb37d3470d2dad2cc99da19283253c96b53fc` |
| SotC Android/staging | `erickmendes22/gow3_android_daedalus_fork@0366868550bde078d9ed9d88bc72d8acb1584679` |

O Order é montado por `the-order-1886-android/scripts/assemble.py`. O SotC é
montado por `ports/sotc/android/stage_renderer.py` e `wire_ahb.py`. Essa distinção
evita confundir o estado do repositório PC com as fontes que o APK do port usa.

## O que os dois diagnósticos mostram

Ambos foram capturados em nubia NX809J, Android 16, Adreno 840, com o driver
Turnip selecionado `turnip-8255659cc205110e`. São execuções de revisões anteriores
às últimas correções de WSI e à integração descrita aqui. A identidade do ELF
carregado é mais precisa que campos antigos de identificação do instalador.

* **Order, `48FCDEC7`:** jogo CUSA00785 v01.02, core `9b9f866e8467`, cerca de
  91 segundos até SIGSEGV em `Game:Main`. O RIP convidado salvo aponta para
  `+0xD` do veneer de `sceKernelClockGettime`, posição do `SYSCALL`, e não para
  seu `RET`. Esse RIP pode ser o estado salvo na fronteira HLE; não prova que
  o fault nativo ocorreu nessa instrução convidada. Há 213 eventos WSI_READY,
  correspondendo à criação inicial e 212 recriações de swapchain, sem mudança
  de dimensão. O log não contém evidência de OOM ou de falha na compilação do
  último shader. O pico de RSS foi aproximadamente 3,83 GiB.
* **SotC, `487A12C8`:** jogo CUSA08809 v01.00, core dedicado `a34bde82d9014`,
  cerca de 37,7 segundos, encerrado pelo usuário com saída zero. Os arquivos
  PSARC foram abertos e o loop principal foi alcançado. O diagnóstico não
  registrou primeiro frame nem eventos de FPS. Essa captura demonstra ausência
  da confirmação de apresentação; não identifica, sozinha, o ponto exato de
  bloqueio da GPU.

Os dois logs registram oito processadores lógicos, tracking por sinais e
marcadores host/guest desligados. Essas condições permitem o novo DrawPipe por
padrão. O recorder Vulkan permanece habilitado e não é usado como condição
para desativar a fila.

## Grupos corrigidos

### Apresentação e contador

As correções anteriores de propriedade do primeiro/último frame e do ciclo de
vida dos semáforos WSI foram preservadas. `SUBOPTIMAL_KHR` continua sendo um
resultado válido de aquisição/apresentação; seu semáforo e sua imagem precisam
ser consumidos antes de qualquer recriação. Isso elimina a recriação em ciclo
causada pelo tratamento anterior desse resultado como falha.

O ponto de apresentação envia o protocolo original
`BACHATA/1 EVENT Frame\n`, consumido pela interface Android. O teste usa a
implementação real de `runtime_client.cpp`, um socket e 120 frames, incluindo
Running/Stopped e desconexão. A contagem não usa frames inventados por timer nem
o reaproveitamento de um frame anterior. AHB continua disponível explicitamente;
WSI permanece o padrão já corrigido. A escolha de AHB por si só não demonstra
equivalência de desempenho no aparelho.

### FEX: fault e relógios

A recuperação restrita da área de guarda call/return agora inclui o dispatcher
do FEX, que também executa STP/LDP com X25. `IsAddressInCodeBuffer` cobre o JIT,
mas não esse dispatcher. O handler valida sinal, código de acesso, instrução,
registrador, limites da reserva e endereço do fault antes de recuperar. Um
fault nativo externo a esses casos não é ocultado. A evidência de falhas não
tratadas é escrita sem alocação ou mutex no signal handler, identificando
separadamente o PC host e o RIP convidado salvo.

O FEX escalona RDTSC/RDTSCP em hosts ARM64 com contador nativo de baixa
frequência. Antes, as funções HLE relacionadas ao TSC ainda devolviam o relógio
nativo sem essa escala. O core agora configura a relação a partir do CPUID
0x15 do próprio FEX e aplica a mesma escala às frequências e contadores HLE.
Relógios em micro/nanossegundos mantêm suas unidades reais. O teste cobre
frequências ARM comuns, diferença entre leituras HLE/JIT, wrap e rejeição de
relações inválidas. O marcador é `BACHATA_FEX_TSC_ALIGNED`.

### Shaders e cache

Foram adaptados grupos completos de semântica, incluindo dependências de IR,
emissão SPIR-V, especialização e invalidação do cache:

* Multiplicação legada e seus consumidores MUL/MAC/MAD, NaN nas comparações
  negadas e nas operações min/max/mediana, incluindo atualização de EXEC.
  Min/max F32/F64, clamp e saturate seguem a política ativa de cada doador:
  operações N por padrão no SotC e saturate com NaN→0 no Order. O opt-out
  `SHADPS4_IEEE_MINMAX` mantém a semântica de presença da variável do doador.
* Atômicos float min/max com ramos exclusivos: a emulação executa uma única
  operação atômica e devolve o valor anterior. O uso anterior de seleção de
  resultados podia executar os dois efeitos antes da seleção.
* Políticas Wave64/LDS dos doadores, identidade de lanes ausentes e o caminho
  completo de `SubgroupBarrier`, com tratamento específico por jogo.
* `S_WQM_B64` do SotC, constantes do fetch shader e índices de instância
  relativos a `BaseInstance`, incluindo step rates e as exceções de SGPR/fetch
  próprias de cada doador.
* BUFFER_LOAD ADDR64 do Order, preservação da tag no IR/GVN, exclusão do
  flattening CPU para endereços variáveis por lane e limites ReadConst
  calculados antes do fallback. A representação de limite desconhecido já não
  transforma indevidamente um teto de 4 MiB em 1 MiB após deslocamento.
* Early fragment tests do SotC quando Z_ORDER exige teste antecipado e não há
  exports incompatíveis. A emissão é restrita a shaders com escritas em imagens
  e sem discard/exports de profundidade, stencil ou máscara de amostras.

Os testes executam corpos C++ extraídos da fonte aplicada. O CI também gera
SPIR-V real com o Sirit fixado e o valida com `spirv-val`, incluindo os ramos
aninhados dos atômicos e a barreira de subgrupo. Versões de metadata, binário e
pipeline são atualizadas; o namespace persistente deriva das versões finais.
Caches de gerações anteriores permanecem no disco, mas não são carregados sob
a nova ABI.

### Metadata do Order

O atalho de compute clear só pode suprimir o shader se **todos** os destinos
escritos forem metadata válida. A validação é transacional: um destino inválido
não altera parcialmente as máscaras dos destinos anteriores. Escritas de CPU,
buffers GPU, imagens e cópias invalidam o estado de clear correspondente. O fill
de HTILE respeita o valor escrito. Depth read-only não consome o clear; views
com várias camadas atualizam todas as camadas. O registro ImageId/UID continua
protegendo contra reutilização de proprietários. A síntese opcional de HTILE,
desligada no doador, permanece desligada.

### Readbacks e memória do SotC

O ciclo de readback mantém o staging até a conclusão, intersecta as cópias com
os blocos realmente residentes e distingue itens solicitados de itens quentes
especulativos. Uma escrita posterior invalida apenas os itens afetados. A
conclusão aplica os itens limpos e repete a janela solicitada quando necessário.
A verificação de CPU dirty e a cópia dos itens quentes usam o lock do tracker;
a subtração de proveniência GPU alcança apenas as faixas elegíveis copiadas.

O ciclo de arenas usa chunks reutilizáveis, coalescência de faixas livres,
cache versionado de residência e épocas de último uso. A coleta fria segue o
contrato ativo do doador: limiar padrão de 1536 MiB, 30 segundos sem uso e lotes
de até 64 MiB, com comparação assíncrona antes de liberar. Blocos GPU dirty,
reutilizados durante a espera ou recuperados por fault permanecem residentes.
Unbind e rebind não compartilham o mesmo lote sparse. A liberação opcional
adiada de unmaps não foi ativada. Os uploads iniciais coerentes do Android e as
cópias pelas aliases físicas do FEX foram preservados.

### Fila de draws

O caminho anterior de draw completo em worker estava desabilitado e não
oferecia a divisão de trabalho do port. A nova fila separa a seleção/compilação
do pipeline na thread de comandos do binding de recursos e gravação Vulkan no
worker. Cada pacote possui os snapshots de registros, user data, buffers
achatados, tabelas de descriptors e descriptors de vértices apontados de que
precisa. Efeitos de DMA/fence são capturados por valor e mantidos em ordem.

Dependências de leitura e escrita, readbacks SRT, comandos de compute assíncrono,
troca de shader e teardown drenam ou recuperam a propriedade no ponto correto.
Há um único proprietário do recorder. O teste executa os métodos reais da fila
com consumidor bloqueado, mutação dos dados originais após publicação, operações
diretas/indiretas e milhares de voltas do buffer circular. O marcador
`BACHATA_DRAW_PIPELINE` registra ativação e motivo, CPUs, FEX, tracking e recorder.

A família de draw indireto inclui o opcode, layout, handler e produtor HLE de
`DrawIndirectCountMulti`. O produtor respeita o ponteiro de payload devolvido
por `WriteHeader`; o handler preserva endereço de contagem, limite, stride e
SGPRs, inclusive com alinhamento de apenas quatro bytes. `DrawIndirectMulti`
declara as seis palavras de payload que efetivamente escreve. O gate compila
e decodifica os produtores e handlers reais em 9.072 combinações com UBSan,
sentinelas e entradas inválidas; também rejeita as duas regressões anteriores.

### Callbacks e recuperação de memória

O scheduler remove e move o callback atual para armazenamento local **antes** de
executá-lo. Assim, um callback que chama `Finish()` pode liberar operações
posteriores sem executar novamente a si próprio. A fila mantém a ordem de
invocação; a conclusão aninhada necessária para liberar memória antes do retry
de alocação permanece permitida. O conjunto de faixas de cada batch de faults
passa a pertencer ao callback, evitando que uma execução aninhada invalide a
iteração externa. O teste executa o `Finish` e os callbacks reais, incluindo
liberação anterior ao retry e batches de faults intercalados.

## Reteste do Order em 26/11/2026: DB405003

O reteste executou efetivamente o core
`887d05d3c8afbb42e67510ed51ef45037e3a7bdd`, confirmado por
`BACHATA_CORE_REVISION` em `DB405003/shadps4.log:9`. O título é CUSA00785
v01.02 (`shadps4.log:41–42`), com FEX, DrawPipe e recorder habilitados. Portanto,
esta captura não pode ser descartada como execução do core anterior à integração.

O processo começou às 00:37:03.293550 UTC e terminou às 00:39:07.741951 UTC,
aproximadamente 124,45 segundos depois (`process-exit.json`). O aplicativo recebeu
`FIRST_FRAME_PRESENTED` às 00:37:18.898280, cerca de 15,60 segundos após o início
(`application.log:25–26`). Há amostras subsequentes de FPS, incluindo 30/60 no
início e valores menores mais adiante. Isso confirma o caminho de telemetria nessa
execução, sem demonstrar equivalência de desempenho nem corrigir a amostra inicial
isolada de `frameTimeMs=79165.76` (`application.log:27`).

A falha nativa observável é **Vulkan DeviceLost**. As últimas quatro linhas de
`shadps4.log:4542–4545` registram falha de leitura do master semaphore em GpuDraw
e falha de QueueSubmit em Present, ambas com `ErrorDeviceLost`. O encerramento
reportado pelo aplicativo é `BACKEND_CRASHED`, saída -1, sem wait status ou sinal
disponível. Esta captura não contém um novo `BIONIC_HOST_FAULT`, RIP ou opcode
que sustente atribuir a falha ao guard FEX do diagnóstico anterior.

O descriptor do shader `0xa7b66f58`, com span `0x39f53d00`, foi rejeitado pelo
guard antes de `FindImage` e recebeu binding nulo. Sua proximidade temporal com
DeviceLost não prova que esse descriptor inválido tenha sido enviado a Vulkan.
A comparação dos caminhos ativos dos doadores encontrou os contratos abaixo;
eles são correções de diferenças funcionais demonstradas, sem alegação de serem
a causa exclusiva do DeviceLost capturado.

### Acessos indiretos e índices produzidos pela GPU

`port_indirect_submission_protocol.py` registra leituras de argumentos e do
contador de draws indiretos, argumentos de dispatch indireto e vertex/index
buffers. `eIndirectCommandRead` participa do `READ_MASK`, para que Copy, Fill e
WRITE_DATA posteriores aguardem essas leituras. O tracker e os métodos de escrita
existentes continuam responsáveis por emitir a barreira necessária.

No Order, o binding de índice indireto usa `max_index_size` e a faixa efetivamente
mapeada. A validação usa `ClampGpuRangeSize`; o `ClampRangeSize` antigo deixa
tamanhos menores que 1 GiB passar sem verificar o mapeamento. O protocolo
preserva a semântica do doador quando `max_index_size` não está definido e rejeita
records incompletos ou fora do mapeamento antes da submissão Vulkan.

O compute shader limita somente `indexCount` ao espaço restante após `firstIndex`.
Preserva `instanceCount`, `firstIndex`, os bits de `vertexOffset` e `firstInstance`.
Os dados de argumentos e contagem produzidos por shaders anteriores permanecem
na GPU: não são substituídos por cópias desatualizadas da CPU. A divisão em batches
respeita os limites de storage buffer, dispatch e draw do dispositivo, ajustando a
contagem de cada batch na GPU. As saídas usam o staging pool sincronizado e seus
ticks de conclusão; não usam o ring sem fences do doador.

A rejeição de índice vazio ocorre antes de `PrepareRenderState`, `BindResources`
e `BeginRendering`. Esses caminhos já atualizam o estado de layout das imagens e
consomem metadata de clear, mesmo antes de gravar o draw Vulkan. Retornar depois
deles com `ResetBindings` poderia perder a indicação de transição pendente ou o
clear. Os limites são resolvidos antes dessa preparação e passados por valor ao
binding, que continua sendo gravado na posição original. O gate executa o prefixo
real de `DrawIndirect` e verifica a preservação desses estados nas rejeições.

O warning recorrente de leitura de metadata em `BindTextures` passa a exigir
`ORDER1886_WARN_META_TEXTURE=1` no Order, conforme o caminho ativo do doador. Essa
mudança elimina custo de diagnóstico no caminho frequente, sem classificá-lo como
causa comprovada do DeviceLost. Outros títulos preservam o warning anterior.

O teste do protocolo executa métodos reais de Runtime/StreamBuffer e o corpo real
do shader, com 178.542 records em 12.377 batches por execução. Cobre conflitos de
leitura→escrita, mapeamento, stride, count, dados produzidos após a gravação dos
comandos, campos preservados e reutilização somente após o tick da GPU. Remover
apenas `eIndirectCommandRead` do `READ_MASK` reproduz a falha da asserção de hazard.
O shader GLSL real compilou localmente em target Vulkan 1.3; o gate native exige
também `spirv-val`, além da compilação C++ completa.

### Guards de patches e mapeamento antes da execução

O guard transacional de patches também usa `ClampGpuRangeSize` para verificar
cada preimage antes de acessá-la; `ClampRangeSize` não serve como prova de
mapeamento para patches curtos por causa do fast path abaixo de 1 GiB
(`src/core/memory.cpp:98–137`). A verificação estrita percorre VMAs contíguas e
exige `IsMapped()`, que rejeita Free, Reserved e PoolReserved
(`src/core/memory.h:129–131`). Nenhuma escrita do grupo ocorre se uma preimage
estiver em um buraco. O teste mantém o fast path permissivo no mock legado;
substituir o clamp estrito pelo legado reproduz a falha, confirmada nos dois cores.

Essa aplicação acontece durante o carregamento, antes da execução do jogo:
`src/emulator.cpp:529` carrega o EBOOT antes de `Linker::Execute` em
`src/emulator.cpp:563`. `Module::LoadModuleToMemory` mapeia os segmentos em
`src/core/module.cpp:174–179` e só então publica `g_eboot_address`, o tamanho da
imagem e chama `OnGameLoaded` em `src/core/module.cpp:275–279`. O callback aplica
a sessão managed ou os patches legados sincronamente. A criação de Game:Main e
`RunMainEntry` pertencem ao `Linker::Execute` posterior
(`src/core/linker.cpp:468–575`).

O limite de 40 bits é compatível com esse EBOOT: a base observada é `0x800000000`
e o tamanho `0x1764000` (`DB405003/shadps4.log:245–249`), coerentes com
`ModuleLoadBase` em `src/core/module.cpp:26`. No runtime Android, o limite do
espaço do convidado é `0x3FFFFFFFFF`, inferior a 40 bits
(`src/core/address_space.cpp:49–52`). O clamp valida VMAs de código/memória
flexível; não depende de um registro adicional da imagem como recurso Vulkan.

## Verificação e limites da conclusão

O workflow reconstrói a fonte a partir das revisões fixadas, aplica todos os
overlays, exige os testes de contrato e a validação do SPIR-V, compila com NDK
r30 e publica os cores. O empacotamento verifica o run e a revisão exata de
ambos, hashes das dependências compartilhadas, exports JNI, identidade de
extração do runtime e certificado P36 original. Código ou build iniciado não
constituem a entrega: a entrega exige APK compilado, assinado e verificado.

Os testes demonstram os contratos exercitados e a integridade da build. Não
medem FPS no Adreno 840 nem comprovam que todo crash/stall foi eliminado em
gameplay. Essa confirmação exige execução no aparelho, com o mesmo driver,
resolução, patches, cenas e caches comparáveis. Conforme a instrução do usuário,
essa medição não bloqueia gerar e entregar o APK assinado. Não se deve chamar
compilação bem-sucedida de equivalência completa de desempenho ou estabilidade.
