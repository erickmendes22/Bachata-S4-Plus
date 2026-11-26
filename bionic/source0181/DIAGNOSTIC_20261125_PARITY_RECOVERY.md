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

## Nova captura SotC de 26/11/2026: `5F5C7839`

Esta captura executa CUSA08809 v01.00 com o core dedicado
`36f6301f91b2c8fd49084ebae97bd5c8254992f1`, confirmado pelo marcador do core
carregado em `shadps4.log:9`. O processo começa às 00:31:55.204 UTC; o primeiro
frame é apresentado às 00:32:13.953 UTC, aproximadamente 18,75 segundos depois
(`application.log:20,29,30`; timestamps precisos também em `session.json`).
Portanto, esta execução alcançou apresentação e produziu eventos para o medidor.
As quatro janelas seguintes registram 48,73, 35,58, 31,00 e 32,54 FPS
(`application.log:32–35`). A amostra inicial de FPS zero tem janela de duração
zero e não é uma medida comparável de desempenho.

O usuário relata congelamento. O último evento de desempenho é das
00:32:22.016 UTC; a interface continua enviando inputs até 00:32:24.735 UTC,
e o usuário encerra a sessão às 00:32:26.293 UTC. `process-exit.json` registra
`CANCELLED_BY_USER`, saída zero e nenhum sinal. Esse encerramento não deve ser
classificado como crash, nem usado para negar o congelamento anterior.

Os caminhos novos estavam ativos: `shadps4.log:1854` registra DrawPipe habilitado
por padrão do SotC, oito CPUs, FEX, tracking por sinais e recorder habilitado.
O TSC registra cristal de 19,2 MHz, multiplicador 64 e frequência convidada de
1.228,8 MHz (`shadps4.log:1132`). O trecho retido não contém host fault FEX ou
perda de device Vulkan. Há truncamento intermediário em `shadps4.log:7189`,
portanto a ausência desses marcadores não prova que nenhum evento ocorreu em
toda a sessão.

O último trabalho visível do GpuDraw é uma operação de residência
(`shadps4.log:14485`). As últimas entradas da thread de comandos são os shaders
FS `0x465f664a` e VS `0x5dab0dab` em `CompileModule`
(`shadps4.log:14487–14488`). Depois disso, Game:Main e workers de carregamento
ainda registram atividade. A versão testada só registra a entrada da compilação;
não permite decidir se a pausa ocorreu na tradução, em um readback de SRT, na
criação do shader/pipeline ou em uma espera de GPU. A última entrada de shader
não é, por si só, prova de defeito nesse shader.

### Correção reproduzida de reentrância no unmap

A investigação encontrou um defeito independente e reproduzível em
`BufferCache::ReleaseUnmappedArena`: depois de coletar os backing ranges, um
`Flush()` podia executar callbacks que vinculavam um novo intervalo. A função
então removia todo o intervalo da tabela de residência, mas liberava apenas os
backings presentes na lista antiga. A reprodução com os métodos C++ reais
terminou com tabela vazia e 131.072 bytes ainda alocados. Outro controle
negativo demonstrou unbind antes da conclusão do lote recém-vinculado.

O unmap agora repete `Finish()` enquanto os callbacks publicarem novos binds,
coleta os backings somente após a conclusão desses lotes e não faz outro flush
reentrante entre essa coleta e o unbind. O teste acrescenta quatro combinações:
alocador SotC ou legado, com ou sem intervalos vizinhos que devem sobreviver.
Ele verifica conclusão dos binds antes do unbind, preservação dos vizinhos,
ausência de blocos órfãos e separação dos lotes sparse. A fonte anterior falha;
a correção passa junto com os casos existentes de OOM, migração de arena,
readback retido e callback durante flush. Isso comprova o defeito e a correção
do contrato exercitado; não comprova que ele causou o congelamento desta captura.

### Captura necessária para localizar uma próxima pausa

`BACHATA_GPU_PROGRESS` passa a registrar início e retorno de tradução, callback
SRT, emissão SPIR-V, criação de shader module e criação de PSO gráfico/compute.
Esses registros ocorrem nos misses de compilação, com hashes, variante, duração
e ticks publicados. O caminho de cache do Order e o worker de compute do SotC
mantêm suas respectivas implementações.

Uma espera CP/Draw que exceda dois segundos gera uma única amostra
`BACHATA_GPU_WAIT`, com posições da fila e hashes copiados no pacote sob o lock
da fila. Os ticks são leituras atômicas; a captura não inspeciona descriptors,
`Shader::Info` ou sessões do recorder enquanto outro thread os modifica. Uma
espera da timeline também registra uma amostra após dois segundos, com seu tick
alvo, e depois mantém a espera bloqueante. Um erro Vulkan distinto de timeout
é informado explicitamente, evitando o loop infinito anterior sobre o mesmo
erro. Não há logging por draw nem frames produzidos por essa instrumentação.

Os testes executam `CompileModule` e `Semaphore::Wait` extraídos da fonte final,
incluindo falhas por fase, shader patch, preservação de valores move-only,
espera com lock e erro de device. Eles tornam a próxima captura interpretável;
a estabilidade e a equivalência de desempenho continuam dependendo de gameplay
comparável no aparelho.

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
