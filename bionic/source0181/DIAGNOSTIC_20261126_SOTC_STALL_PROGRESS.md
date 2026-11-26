# SotC: continuidade PM4 e espera cooperativa — 26/11/2026

## O que o novo diagnóstico demonstra

A sessão BS4-20261126-02E973D0 executou CUSA08809 com o core
`1dce219fa03518a24bd3e7327c5fa3b2b8b1ab14`, que já contém a correção
anterior de publicação EOP/EOS. A revisão aparece em `shadps4.clean.log`,
linha 9. O primeiro frame foi apresentado às 12:19:54.305011Z, **18,727 s**
após o lançamento do backend. A sessão inteira durou **33,753 s** e terminou
por solicitação do usuário, com código zero (`application.log`, linhas
19–30; `report.json`, linhas 48–59). O sintoma relatado é congelamento;
esse encerramento não demonstra crash.

O log nativo tem 1.770.994 bytes e está truncado (`report.json`, linhas
70–76), com corte na linha 6926 da cópia sem sequências ANSI. DrawPipe
está ativo com oito CPUs, FEX, signals e recorder (linha 2220). Os 366
marcadores de progresso são 183 pares fechados de criação de PSO no Main,
durante o carregamento do cache: 83 compute e 100 gráficos. O último par
termina na linha 509, com tick 1, submitted 0 e gpu 0. Não há marcador
retido de espera GPU prolongada nem de fault FEX.

O último registro GpuDraw está na linha 2537, mas o CP ainda conclui
liberações de arena até a linha 4908 e os workers continuam registrando
operações de memória. A ordem desses registros não identifica a pilha
bloqueada. Há somente a amostra inicial de FPS zero, no primeiro frame
(`application.log`, linha 27); ela não permite calcular a taxa posterior.

| Evidência | Conclusão ou teste que restringe a hipótese |
|---|---|
| Revisão correta, primeiro frame e congelamento posterior | A correção anterior de EOP/EOS foi insuficiente; o APK antigo não explica o resultado. |
| Todos os PSOs registrados terminam antes de rodar a sessão | O último shader registrado não está demonstrado como culpado. |
| CP ainda processa liberações depois do último registro GpuDraw | Não se pode localizar o bloqueio no último EnsureResident somente pela ordem do log. |
| Parser ASC dimensiona Type-2 como Type-3 antes da fragmentação | Repro real perde o cabeçalho seguinte e impede RELEASE_MEM/WAIT de progredir. |
| Espera de label de vídeo pode dormir dentro do único CP | Repro real deixa um flip tardio aguardando esse mesmo CP; espera cooperativa fecha o ciclo. |
| Fila ASC e sua contagem eram publicadas em momentos separados | A revisão encontrou leitura concorrente do limite e consumo possível antes de incrementar a contagem; a publicação passa a ser única. |

## 1. Fronteira Type-2 do stream ASC

Type-2 ocupa um DWORD; os bits inferiores não são um tamanho Type-3.
O parser anterior calculava `header->type3.NumWords() + 1` antes do teste
de fragmentação. Um padding no fim da submissão podia virar um fragmento
pendente de um DWORD e consumir o cabeçalho da próxima submissão.

O repro usa o prefixo efetivo de ProcessCompute, os layouts PM4 e os métodos
reais ReleaseMem::SignalFence, WaitRegMem::Test e AdvanceReadPointer. A
ordem anterior resultou em `buffered_padding=1`, label 0, IRQ 0, nenhum
WAIT satisfeito e um opcode malformado. A classificação antecipada de
Type-2 resultou em fragmento vazio, label 1, IRQ 1 e WAIT satisfeito.

A regra corrigida corresponde ao caminho ativo do doador SotC em
`shadps4/video_core/amdgpu/liverpool.cpp`, linhas 2173–2177. A adaptação
mantém a publicação do read pointer, a posse dos fragmentos Type-3 e o
tratamento de indirect buffers. O teste não relaxa a condição de WAIT.

## 2. Ciclo entre label de vídeo e comando tardio

O caminho anterior de WaitRegMem reconhecia um label VideoOut e chamava
WaitVoLabel, que dorme na condition variable. Um flip não-EOP que chega
depois entra em SendCommand; SubmitFlipInternal só prepara o request
quando o CP atende essa fila. Assim, o CP podia esperar pelo label enquanto
o comando necessário para produzir o flip aguardava o próprio CP.

O repro executa Process, ProcessCommands, SendCommand, o branch real de
WaitRegMem e os métodos reais de VideoOut. O caso anterior de chegada
tardia fica com `pending_cp_command=1`, `present_requests=0` e label 1.
O flip previamente enfileirado funciona. Removendo apenas o sono bloqueante
para os dois seriais SotC, o while/Test/YIELD já existente atende o comando
tardio e continua somente depois de o predicado verdadeiro ser observado.

O doador também conserva esse atalho de WaitVoLabel; esta correção decorre
do ciclo reproduzido, não de uma alegação de que o doador já o elimina.
O backoff acompanha a política do CP do doador (`liverpool.cpp`, linhas
959–1013): pausa inicial, yield e espera de até 100 µs após 500 µs sem
progresso. A adaptação usa a fila CP/CE existente do Bachata. Comandos,
novas submissões e stop despertam a espera; o vencimento de tempo nunca
satisfaz o predicado.

As comparações, a máscara, a referência, os endereços e o avanço do parser
permanecem iguais. Test, Signaled e Valid recebem uma saída opcional para
o valor já lido; não fazem uma segunda leitura da memória guest para o
diagnóstico. Outros títulos conservam o atalho VO anterior.

## 3. Publicação da fila ASC

O limite `num_mapped_queues` era escrito em SubmitAsc sob submit_mutex e
lido pelo CP sem esse lock. Além da corrida de dados, SubmitAsc liberava
queue.m_access após enqueue e só então incrementava num_submits. Uma fila
já conhecida podia ser consumida nessa janela.

A adaptação usa o mesmo scoped_lock conjunto de SubmitGfx: enqueue,
incremento da contagem e publicação do limite acontecem sob submit_mutex
e queue.m_access. O limite atômico é publicado com release depois da
preparação; Process e Backoff o leem com acquire. ProcessCompute começa
suspenso, e a configuração da fila precede essa publicação. Não há mudança
no formato de comando, prioridade, read pointer ou FIFO.

## Captura indispensável e alcance

Uma espera CP prolongada passa a produzir um único registro por episódio:
`BACHATA_GPU_WAIT phase=cp_predicate reason=...`. Ele contém fila, endereço,
referência, máscara, valor observado, comparação, comandos/submissões
pendentes e os contadores publicados de tick/submitted/gpu. A emissão só
ocorre após dois segundos sem progresso. Os dados de espera pertencem ao
CP; os contadores GPU são atômicos já publicados. Não há consulta Vulkan,
leitura de objetos mutáveis do Draw nem relógio/log por DWORD.
O registro conserva a fila da última espera falsa durante a volta pelas
filas vazias e é reiniciado quando há progresso. Isso evita perder a
evidência ou atribuí-la à fila vazia em que o backoff foi executado; os
contadores CE identificam explicitamente a fila gráfica.

O overlay altera somente `liverpool.cpp`, `liverpool.h` e `pm4_cmds.h`.
Mantém FEX, Bionic, JNI, UI, SAF, saves, controles, shaders, caches e a
correção anterior de publicação EOP/EOS.

## Verificação

O wrapper `test_sotc_stall_progress.py` compila os métodos reais sob UBSan
e chama `test_sotc_cp_wait_graph.py`. A parte de framing cobre 32.768
combinações de padding e IB, 48 casos de dois paddings/submissões/IBs e
1.105 fragmentações Type-3. Os predicados são verificados em 168 combinações
de memória/registrador, máscara e comparação, oito Rewind e sete semáforos.
Seis controles negativos detectam perda de cabeçalho, read pointer,
continuação, isolamento de IB, máscara e valor observado.

O gate CP/VO cobre ambos os seriais SotC e títulos legados, flip prévio
e tardio, comando síncrono tardio, wake/backoff, stop com predicado falso,
predicado já verdadeiro, publicação ASC e emissão limitada do diagnóstico.
Os métodos de concorrência são extraídos da fonte aplicada; apenas Vulkan
e fronteiras de IRQ/memória são substituídos pelo fixture.
Passaram os casos de fila ASC nova, já conhecida e criada durante a espera
gráfica, com verificação da publicação no instante exato em que o mutex é
liberado. Também passaram duas e três filas com espera na fila 0 e backoff
na fila vazia 1. Os oito controles negativos rejeitam a volta do sono VO,
o bypass do predicado, a perda de dispatch/backoff/observação, a publicação
parcial da tarefa e os dois erros de diagnóstico entre filas.

Na fonte aplicada, também passaram o gate DrawPipe/PM4 (4.096 voltas de
fila e 9.072 casos de protocolo), publicação EOP/EOS (61 casos e quatro
negativos), shader-progress e os 325 contratos de API, incluindo o grupo
novo. As três fontes efetivas conferem byte a byte com a reconstrução
completa usada para a próxima compilação.

Esses testes comprovam os defeitos e as correções descritos. O diagnóstico
truncado não contém o opcode/endereço esperado no instante do congelamento;
portanto, não prova qual desses mecanismos foi acionado naquela sessão.
A próxima execução no aparelho deve confirmar a continuidade de frames.
Persistindo uma espera, o novo registro delimita o predicado e seus
produtores sem ocultar o bloqueio por timeout ou valor artificial.
Ele depende de o CP alcançar o teste do predicado: não substitui uma
captura de pilha para um bloqueio ocorrido antes dessa leitura.
