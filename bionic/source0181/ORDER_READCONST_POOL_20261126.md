# Order: custo de snapshots ReadConst e evidência de desempenho

## Sessão recebida

O diagnóstico B46E3851 registra CUSA00785, versão 01.02, core
b343962accf4cc758a8052bb340cfde9babbc3a0. O processo durou 116,828 segundos
e terminou por solicitação do usuário, com código 0. O primeiro frame apareceu
cerca de 14,984 segundos após o lançamento do processo.

O log confirma as escritas verificadas de 720p e dos quatro efeitos:
motion blur, depth of field, film grain e chromatic aberration. Também confirma
60 FPS, 16:9, cloth desativado e os argumentos -disablecloth -msaa 1.
O caminho de apresentação registrou 1280×720, sem cópia/blit intermediário.
Isso confirma aplicação das opções nessa sessão, não equivalência de desempenho.

Evidência local: analysis/B46E3851/shadps4.log, linhas 9, 40–46, 358–365,
2445–2448 e 4957; application.log, linhas 141–171; process-exit.json.

## Matriz de evidência, hipótese e teste

| Evidência | Interpretação limitada | Teste/ação |
| --- | --- | --- |
| FPS do aplicativo cai para 7,64–11,12 nas últimas amostras, sem crash | Existe perda sustentada de desempenho; esses números não localizam o custo | Medir custos por janela e correlacionar com os mesmos intervalos do aplicativo |
| 230 criações de PSO gráfico somam 194.121 µs, máximo 8.729 µs; seis traduções somam 1.887 µs; compute PSO soma 250.268 µs, incluindo startup | Os eventos medidos de compilação não explicam sozinhos a queda sustentada | Preservar a captura de fases; não atribuir a queda a compilação sem outra evidência |
| BACHATA_GPU_WAIT phase=cp_draw_drain em head=187169, tail=187158, kind=1, tick=29238, submitted=gpu=29237 | CP esperou pelo consumidor de draw indireto; a amostra de timeline mostra o trabalho submetido concluído, mas não identifica qual operação de CPU bloqueou o consumidor | Auditoria separada de drenos/recorder; medir o custo de preparação de buffers |
| O clamp de índices indiretos atual e o doador ambos encerram rendering, executam compute e retomam rendering | A passagem compute não é uma divergência demonstrada apenas por existir | Manter o clamp e seus fences; nenhuma remoção especulativa |
| MakeReadConstSnapshot cria um Buffer por binding CPU; AllFlags inclui BDA e UniqueBuffer::Create força alocação VMA dedicada | Custo repetido de criação/destruição demonstrável no caminho de snapshots | Subalocar blocos held do pool, mantendo a cópia imutável até gravar o consumidor e depois até concluir seu tick |
| B46E3851 usa readbacks Precise=2; DB405003 usava Relaxed=1; o shim do port define seu modo relaxado próprio como default | Configuração e semântica de readbacks diferem; os relatórios não demonstram a origem da alteração de configuração | Preservar o modo recebido; não trocar enum nem importar deferred merge com corrida conhecida |

Os contadores de fases não cobrem todo o custo de binding, walks SRT em cache
hit, fault handlers ou espera do recorder. A ausência de um evento de compilação
longo não comprova ausência de espera em outros pontos.

## Comparação disponível com os logs originais do port

Foram lidos os arquivos locais originais:

- analysis/port-reference-logs/TheOrder1886-Android-log (11)(2).txt
- analysis/port-reference-logs/TheOrder1886-Android-log (12)(3).txt

Ambos registram FEX, 1280×720, limite de 60 FPS e o catálogo aplicado. O feed
CPU/GPU soma 16.774 frames em 302,31 s no primeiro e 17.419 frames em 307,52 s
no segundo. Após startup, o número de submissões gráficas por janela costuma
ficar próximo ao número de frames. Esses registros não foram sincronizados
cena a cena com a nova sessão Bachata e não fornecem uma razão causal de ganho.

Há uma diferença relevante entre as próprias referências: embora ambos anunciem
VRS 2×2 habilitado, os contadores de draws 2×2 permanecem em zero no primeiro
arquivo e chegam a aproximadamente 34–35 mil por janela de cinco segundos no
segundo. Não se deve comparar os resultados como se a taxa de shading fosse
idêntica. Os arquivos também não imprimem o valor/override efetivo do modo de
readbacks. Seu default é evidência de fonte, não confirmação de configuração no
aparelho.

## Alteração implementada

O overlay port_order_readconst_pool.py mantém o helper legado e seu comportamento
para os outros jogos. Apenas CUSA00785 no Android usa
MakePooledReadConstSnapshot, sobre o StagingBufferPool já existente no core
0.18.1. O doador atual evita uma alocação por constante usando ConstantRing
e o caminho de ObtainBuffer; a adaptação reutiliza a infraestrutura de
aposentadoria já integrada ao Bachata.

Foram conservados:

- Prova de que o recurso é read-only, usado por ReadConst e não tem origem GPU
  mais recente. Os recursos escritos pela GPU continuam no BufferCache.
- Clamp externo do descritor, consulta da VMA legível, recusa de overflow e o
  limite de 8 MiB da cópia.
- Bytes copiados pelo alias físico FEX, padding zerado e chamada de flush.
- Alinhamento de storage buffer e do átomo não coerente.
- Identidade da cópia até o término da submissão correspondente na GPU.

Cada arena reserva blocos de 16 MiB por StagingBufferPool::Request com
deferred=true e unsynchronized=false. As constantes pequenas são subalocadas
dentro desses blocos, com avanço monotônico do offset. Um bloco cheio permanece
held até que o guard de Draw, DrawIndirect, DispatchDirect ou DispatchIndirect
termine após gravar o consumidor. FreeDeferred então registra o CurrentTick
final. O pool só pode reutilizar o bloco depois que esse tick estiver concluído
na GPU. Um guard aninhado não libera blocos do consumidor externo.

A cauda parcial permanece held entre draws e só ocupa a parte ainda livre do
mesmo bloco. Na troca de bloco, o anterior entra na lista pendente; no teardown,
a arena devolve sua cauda ao pool por FreeDeferred. Presenter declara Runtime
antes de Rasterizer, portanto a arena morre enquanto o pool ainda existe. O
teardown existente conclui e drena o recorder antes de destruir esses membros.
Não há callback de destruição nem buffer dedicado por snapshot, e não foi
modificado o contrato compartilhado de StreamBuffer.

No rollover, a arena transfere o bloco anterior para a lista pendente e limpa
current/offset antes de pedir a próxima alocação. Se RequestLarge lançar durante
a construção do novo Buffer, o guard aposenta o bloco anterior uma única vez;
o destructor não conserva outro alias para a mesma reserva deferred.
RetireRecorded não insere elementos nem reserva memória: libera os blocos
pendentes existentes e, se current terminou cheio, libera-o diretamente.
Assim a aposentadoria chamada pelo destructor do guard também funciona quando
novas alocações estão proibidas.

Essa retenção explícita é necessária: durante a preparação, BindBuffers pode
ser seguido por outro binding/BindTextures. Um wrap de stream.Map alcança
Scheduler::Wait, que pode submeter e concluir o tick da reserva antes que o
draw consumidor seja gravado. A primeira proposta, baseada somente no tick da
reserva do ring, foi rejeitada na revisão antes da publicação. Um repro com
métodos reais reproduziu em 12 combinações a sobrescrita 23→61 dos bytes ainda
vivos quando havia submit interno; o controle sem submit preservou 23. Isso é
um caso construído no host, não um evento observado no aparelho. A arena held
cobre essa janela inclusive quando outro submit ocorre após trocar de bloco.

## Validação

Comando do gate sobre a fonte efetiva:

    python3 -B bionic/source0181/test_order_readconst_pool.py --source EFFECTIVE_SOURCE

O teste compila os helpers de snapshot, a seleção do binding, a arena e seu
guard, os métodos de alocação/liberação do pool, Scheduler::Wait e os métodos
de reserva/watches extraídos da fonte efetiva.
Vulkan/VMA e o alias de memória FEX são fronteiras simuladas; não se apresenta
tempo de execução no host como medição do aparelho.

Resultados:

- 5.000 snapshots de 512 bytes: 5.000 chamadas de construção de Buffer no
  caminho antigo e uma no novo, mantendo o tick pendente e os mesmos bytes.
  A cadeia real Buffer → AllFlags/BDA → VMA dedicada é verificada na fonte.
- 216 combinações de tamanho, coerência e alinhamento, incluindo 8 MiB:
  conteúdo, padding, offset e flush equivalentes.
- Trabalho apenas enfileirado no recorder, trabalho submetido ainda ocupado,
  e reutilização somente após a conclusão do tick na GPU.
- 12 combinações com/sem submit interno, inclusive dois submits antes do draw:
  snapshot preservado até o consumo e bloco aposentado no tick final.
- Guard de recording aninhado, saída antecipada e devolução da cauda no
  teardown, sem destruir diretamente seu Buffer.
- Exceção de alocação na construção de Buffer chamada pelo RequestLarge real:
  unwind do guard, nova tentativa e destruição sem dupla aposentadoria.
- Alocações globais proibidas durante a saída do guard e destruição da arena:
  cauda parcial, bloco exatamente cheio e pendentes mais bloco cheio passam.
- Preservação de VMA/readability, bounds, recursos escritos pela GPU e títulos
  não afetados; compilação com e sem __ANDROID__.
- Controles negativos para reutilização sem fence, bloco sem held, liberação
  antes do consumidor, tick final perdido, saída aninhada prematura, cauda não
  devolvida, alias duplicado no rollover que falha, alocação no cleanup, flush ausente, alinhamento
  perdido, padding perdido, snapshot de bytes GPU e limite ampliado. A ausência do guard em cada um dos quatro
  entrypoints também é rejeitada.

## Medição incluída no próximo APK

BACHATA_ORDER_READCONST_COST registra o primeiro exemplo e depois no máximo
uma linha por dois segundos de atividade em cada thread. Os campos incluem
wall_ms, window_us, calls, snapshots, bytes, cpu_us e max_us.
O tempo cobre o helper de snapshot, incluindo consulta da VMA, reserva, cópia
e flush. Não cobre todo BindBuffers, o teste anterior de origem GPU nem o
tempo de execução do shader.

O contador permitirá confirmar a frequência e o custo real desse caminho.
Os testes demonstram redução de chamadas de alocação e preservação de
contratos; não demonstram ainda aumento de FPS, estabilidade prolongada ou
equivalência completa em gameplay.
