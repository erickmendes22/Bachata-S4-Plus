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
