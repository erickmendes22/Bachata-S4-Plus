# SotC 28BD3630: progresso da apresentação e posse de frames

## Amostra e limite da conclusão

O diagnóstico `BS4-20261126-28BD3630` executou o core SotC
`4979bd728764ee1dceb42f92c74d70fcd470e7f9`, CUSA08809 01.00,
no nubia NX809J, SDK 36, FEX e Turnip `8255659cc205110e`.
As referências abaixo usam `analysis/28BD3630/native-clean.log`, cuja numeração
preserva as 2.721 linhas do log sem escapes de cor. O manifesto informa
389.143 bytes e `truncated=false` para `shadps4.log`.

- Linha 9: revisão nativa correta. Linha 41: versão 01.00.
- Linha 2222: DrawPipe ativo, oito CPUs, FEX, tracking por signals e recorder ativo.
- Linha 2472: a correção anterior de descoberta do LOD está **ativa**:
  `status=0`, pool `0x200a30140`, físico `0x127de0000`, bitmap `0x200c42ff8`,
  1.184 palavras, 75.760 páginas, três livres, 0%, mip 4.
- Linha 2479: primeiro `Present` de jogo concluído. `session.json` registra
  14:33:59.110612 UTC, 18,332241 s após o início do processo.
- `application.log:27` contém somente a amostra inicial de performance,
  com tempo decorrido zero e FPS zero. Os eventos de input posteriores são
  eventos do aplicativo e não demonstram avanço do jogo.
- `process-exit.json` registra parada solicitada pelo usuário, código 0,
  em 14:34:04.508264 UTC; duração de processo 23,729893 s. Não é evidência de crash.

Não há `BACHATA_GPU_WAIT`, `STALLED` ou `ErrorDeviceLost` nesta amostra.
As 100 fases de PSO gráfico e 83 de PSO compute registradas no aquecimento
possuem pares begin/end completos. O último shader registrado não é tratado
como culpado pela sua posição no arquivo.
O log não contém stack ou identidade de uma fence bloqueada. Portanto, a
correção abaixo demonstra e elimina mecanismos reais de bloqueio do código
ativo, mas **não identifica por stack a causa única deste congelamento**.
O endereço antigo do pool LOD não é uma hipótese restante para esta amostra.

## Matriz de comparação e fechamento

| Mecanismo | Evidência no código efetivo | Resultado desta rodada |
| --- | --- | --- |
| Produtor GPU espera frame/fence de apresentação | Baseline SotC `vk_presenter.cpp:1151–1170` e Order `:1368–1386`: `free_cv.wait` e `waitForFences` sem limite, inclusive no produtor. `Present` pode aguardar `draw_scheduler.WaitSubmitted` e a timeline que dependem desse produtor. | Poll de fila/fence em CP **e GpuDraw**, retorno sem tocar cache ou recursos quando indisponível e retomada da cabeça FIFO pelo CP. A reprodução mostra que o comando posterior consegue publicar a dependência. |
| Vblank fica preso dentro de `Present` | `driver.cpp` do baseline chama `Present` na própria thread que publica vblank. O Order doador possui `RunPresenter`/`SwapThread` em `driver.cpp:85/100`. | Worker único para HDR, apresentação de jogo e redraws. A thread de vblank continua avançando enquanto o mock de WSI aguarda 15 vblanks produzidos pelo método real. |
| Retry perde ordem ou conta novamente | O Order doador trata `Request.deferred` em `driver.cpp:305` reenviando a preparação; a adaptação precisa preservar a posição antiga na fila FEX. | Aceitação fixa sequência, descritor e geração. Um flip posterior não prepara à frente de uma cabeça pendente. Existe no máximo um callback de retry; o callback que falha não se reenfileira. |
| Idle blank ocupa o único worker esperando um frame posterior | Um idle já enfileirado pode executar depois da chegada de um flip. | `PrepareBlankFrame(true)` também faz poll. Teste mantém o worker parado, enfileira idle, aceita o flip e libera o worker: idle retorna e o flip progride. |
| Fechar/reabrir mistura sessões ou recicla frame cedo | A nova fila mantém trabalho depois da aceitação; uma apresentação pode terminar depois de `Close`. | Geração capturada na aceitação e validada antes/depois de `Present`. Frames cancelados só voltam ao pool após publicação do recorder e conclusão real da timeline. |
| FPS conta uma tentativa que não foi apresentada | O baseline publica o frame ao frontend depois de uma função `Present` sem retorno, inclusive se a aquisição da swapchain falhou. | `Presenter::Present` retorna o resultado real. O contador do frontend só avança para uma apresentação concluída e pertencente à geração vigente. Retry, idle e cancelamento não contam. |
| Observadores de PM4 não veem espera dentro da apresentação | Os oito predicados instrumentados não envolvem `GetRenderFrame`, WSI, `WaitSubmitted` nem um guest que deixa de enviar flips. | A thread independente de vblank emite um resumo limitado quando não há avanço de apresentação por aproximadamente dois segundos. Não consulta Vulkan nem caches de textura/memória. |

O doador Order efetivo contém o poll de aquisição em
`video_core/renderer_vulkan/vk_presenter.cpp:1223–1260`, com null-checks nos dois
preparadores. O doador SotC ainda tem aquisição bloqueante; esta família é uma
adaptação do protocolo funcional do Order aos dois cores Bionic/FEX, não uma
afirmação de que o mesmo trecho já existia no doador SotC.

`pool_owner` continua como diferença ativa do runtime SotC doador, documentada
no log real do port. O replay dos mapeamentos retidos nesta amostra não mostrou
o gatilho de consulta a alias físico com outro dono. A remoção de aliases no
free físico já existe no core. Nenhum guard por callsite foi aplicado sem essa
evidência. `BpeHeapGuard` não foi transplantado: os accessors usados pelo caminho
Android do doador retornam zero, tornando aquele consumidor inativo.

## Contrato implementado

O overlay `port_present_queue_progress.py` altera somente VideoOut e Presenter
e instala `common/present_queue_progress.h`. A política nova é Android + FEX,
para CUSA00785, CUSA08809 e CUSA08034. Os demais títulos mantêm a preparação e
apresentação síncronas existentes.

A aceitação de `SubmitFlip` copia `BufferAttributeGroup`, endereço e HDR sob o
mutex da porta e fixa a geração e a posição FIFO. A ativação continua no produtor
GPU correto: EOP no GpuDraw/CP atual; flip CPU em callback ordenado do CP. A
retomada reaproveita o dreno de DrawPipe já existente em `ProcessCommands`.

`PrepareFrame` verifica disponibilidade antes de `FindImage`/`UpdateImage`.
O descritor usa o construtor real, cujo tamanho vem dos atributos VideoOut.
No Order, a extensão final continua sendo a da imagem resolvida, inclusive
quando `FindImage` escolhe backing maior por alias. `PrepareBlankFrame` testa
null antes de iniciar gravação. A fence de apresentação não é resetada no poll.

O pool continua retendo o último frame apresentado. `DiscardFrame` roda no
worker de apresentação, espera `WaitSubmitted` quando aplicável e depois a
timeline de produção. Somente então devolve um frame cancelado à fila livre.
O teste separa essas duas dependências; nenhuma delas é satisfeita artificialmente
pelo cancelamento, timeout ou retry.

`Close` retira requests pendentes, incrementa a geração e agenda recolhimento
dos frames preparados. Uma operação já no worker valida novamente a geração
depois de um `Present` ativo. Ela não altera contadores, eventos ou labels da
porta reaberta. Um callback de retry antigo pode preparar a nova cabeça válida
ou limpar sua marca antes da ativação nova; a serialização do CP impede um
segundo preparo concorrente. Os callbacks retêm um token com lifetime próprio,
e o destructor espera um callback ativo, junta vblank e drena o worker antes
de destruir suas filas. Stop e o predicado de espera compartilham o mutex.

O resumo `BACHATA_GPU_WAIT phase=present_progress` contém accepted, prepared,
presented, tamanho da FIFO, sequência da cabeça, retry/preparing, contagens de
pool vazio/fence pendente, busy/fila do swap e idade do último avanço observado.
Ele lê atomics e estado protegido do driver; não faz query de timeline, leitura
de objeto de textura ou acesso a memória guest.

## Validação e entrega

O gate `test_present_queue_progress.py` compila métodos reais de VideoOut,
`GetRenderFrame`, `DiscardFrame`, `Scheduler::WaitSubmitted`, os construtores
ImageInfo/ImageDesc e os tipos BufferAttributeGroup. Vulkan/WSI são fronteiras
controladas do teste, sem GPU física. O método real de retenção/liberação do
último frame também é exercitado.

Nas árvores efetivas SotC e Order passaram os três seriais ativos, seleção legada, FIFO de
múltiplos flips, CPU/EOP, pool vazio, fence pendente, vblank independente, idle
previamente enfileirado, descritor por valor, extensão resolvida, fechamento
antes da ativação/depois do preparo/com swap enfileirado/durante Present,
retry antigo após reopen e destruição com callbacks e frames pendentes.
Foram rejeitados **17 controles negativos executáveis em cada core**. O gate composto
`test_sotc_cp_wait_graph.py` manteve seus **oito negativos** e passou com os novos
métodos de aceitação, ativação e conclusão. `test_wsi_fex_guard.py` passou nos
dois efetivos, preservando 2.048 codificações do guard FEX.

A composição final do pacing é registrada no fechamento de integração desta
rodada pelo gate próprio. Compilação nativa,
assinatura e revisão do APK permanecem gates separados de entrega.

Estes testes demonstram progresso e preservação do protocolo em interleavings
reproduzíveis. Eles não medem FPS em Android, não comprovam gameplay estável e
não permitem declarar equivalência completa no aparelho. A próxima captura
deve confirmar avanço após o primeiro frame e, caso o congelamento persista,
distinguir falta de novas requisições, preparo retido e WSI ocupado pelos
contadores independentes de apresentação.
