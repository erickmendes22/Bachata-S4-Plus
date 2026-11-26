# Event flags: entrega preservada e observação de esperas guest

## Evidência desta rodada

O diagnóstico `08A542C3` veio do core SotC
`75a1cba457237be6e91524ba1f4f896afab53031`. A sessão durou
49,176917 s; o primeiro frame foi apresentado aos 18,495945 s e a saída foi
solicitada pelo usuário, com código 0. Esses tempos não representam um crash.

Em `analysis/08A542C3/native-clean.log`, as linhas 8351, 10762 e
11126–11136 contêm treze amostras de apresentação. Todas registram
`accepted=49 prepared=49 presented=49`, fila pendente vazia, nenhum retry,
nenhum frame à espera de fence e worker de swap ocioso. A idade sem novos
flips cresce de 2.133 a 27.733 ms. Logo, neste intervalo retido, o bloqueio
observado não é uma requisição presa na fila de apresentação. A linha 2444
também confirma a descoberta do pool LOD ativa, com bitmap válido, três
páginas livres e mip 4; a hipótese anterior de endereço fixo não se aplica.

O log real de referência, `analysis/port-reference-logs/sotc/logs/android-game.log`,
registra uma tela de carregamento sem frames aos 1,303 s (linha 191), esperas
de event flags `PS4SyncEvent` e de áudio durante o carregamento (linhas
228–268), e `st_gameflow()` iniciando o jogo aos 54,7153 s (linha 289).
Os relógios de início dessas duas execuções não foram alinhados, e elas não
constituem um benchmark pareado. A amostra Bachata, encerrada aos 49 s,
não demonstra sozinha um deadlock permanente nem identifica qual evento
estaria bloqueando o carregamento. Também não autoriza descartar o
congelamento relatado pelo usuário.

## Divergência funcional reproduzida

Os métodos ativos do doador foram conferidos no pin `732cb37d`, arquivo
`analysis/sotc-donor-runtime/runtime_sotc-732cb37d.c`: `evf_set` fixa o
resultado e o estado `ready` de cada waiter sob o mutex, antes de notificá-lo;
`evf_clear_bits` modifica apenas o padrão armazenado. A tabela de exports
do mesmo arquivo liga esses métodos às funções `sceKernel*EventFlag`.
Os dois corpos usados na reprodução são idênticos aos recuperados desse
pin. Nenhum runtime completo do port é incorporado ao Bachata.

O Bachata anterior notificava uma variável de condição, mas o waiter
reavaliava somente o padrão compartilhado ao retomar. A sequência real
reproduzida é:

1. `Wait` suspende porque o bit solicitado ainda não está presente.
2. `Set` satisfaz o pedido e notifica o waiter.
3. Antes da retomada, `Clear` apaga o padrão compartilhado.
4. O waiter anterior perde a entrega e volta a esperar, podendo expirar.

`analysis/repro_sotc_eventflag_delivery.py` executa os métodos extraídos
das fontes efetivas, controlando apenas a retomada do mutex no host.
O corpo anterior perde o sinal; o `Set`/`Clear` real do doador preserva
`result=1` mesmo com o padrão armazenado já em zero. A reprodução prova
esse mecanismo; não prova que a mesma corrida ocorreu no diagnóstico.

## Grupo implementado

`port_event_flag_delivery.py` é comum aos cores Order e SotC e altera
somente a família de event flags, sua declaração diagnóstica, um accessor
atômico de Liverpool e a chamada no observador de apresentação existente.

- Cada waiter possui resultado e estado próprios. `Set` avalia e consome
  os bits sob o mutex e conclui a entrega antes de notificar. `Clear`,
  `Cancel` ou `Delete` posteriores não retiram uma entrega concluída.
- FIFO preserva a ordem de chegada. `ThreadPrio` usa a prioridade guest
  capturada ao enfileirar, com menor número primeiro e FIFO nos empates;
  não usa a prioridade do escalonador host. `Poll` com timeout zero não
  toma o mutex da thread nem copia sua identidade.
- As condições AND/OR e as opções de limpeza permanecem explícitas.
  Timeouts usam um prazo absoluto de `steady_clock`; uma espera infinita
  continua dormindo sem despertares periódicos de diagnóstico.
- `Cancel` conclui apenas waiters pendentes, com snapshot do padrão de
  cancelamento e contagem correspondente. Uma nova espera pode começar
  sem esperar que os waiters antigos retomem; não há status global nem
  busy-wait de cancelamento.
- Cada entrada HLE obtém um `shared_ptr` do registro antes de acessar ou
  suspender no objeto. `Delete` retira a visibilidade do handle, acorda
  os pendentes com `EACCES` e revoga a publicação FEX. O objeto só é
  liberado após a última chamada já iniciada terminar. Lookup de handles
  inexistentes retorna `ESRCH` sem desreferenciar o valor recebido.

O ABI de handle opaco continua sendo um ponteiro. Depois de `Delete` e
do término de todos os donos anteriores, o alocador pode reutilizar esse
endereço para outro evento. Não há geração embutida no handle; portanto
o grupo não promete distinguir um handle obsoleto de uma futura alocação
no mesmo endereço. A segurança de chamadas já iniciadas e a retirada
do objeto excluído são verificadas separadamente dessa limitação de ABA.
Os stubs preexistentes de abertura/fechamento por nome não são ampliados.

## Captura decisiva, com custo limitado

`Libraries::Kernel::ReportEventFlagWaits()` é declarado em
`src/core/libraries/kernel/threads/event_flag_delivery.h` e chamado pelo
observador de apresentação somente quando este já registra falta de
avanço. Ele usa `try_lock` no registro e nos objetos, não toca Vulkan e
não acorda threads guest. No máximo quatro esperas por amostra e 32 por
processo são registradas, com intervalo global mínimo de dois segundos;
cada waiter é amostrado uma vez após cinco segundos.

O log `BACHATA_GUEST_WAIT phase=event_flag` contém nome e endereço do
evento, nome e ID guest, bits pedidos/observados, modo, prioridade, idade,
quantidade pendente, Sets desde a entrada e entregas do objeto. As strings
da thread são copiadas sob seu mutex; as do evento e o estado dos waiters,
sob o mutex do evento. Todos os locks são liberados antes do logger.
O log de apresentação acrescenta somente loads atômicos dos contadores
existentes `cp_commands`, `cp_submits` e `cp_submit_done`; esses campos são
uma observação concorrente, não uma transação consistente entre contadores.

Isso permite distinguir uma fila GPU ociosa com espera de evento guest
de trabalho ainda enfileirado no CP. A ausência de uma linha específica
não prova ausência de espera: o census é limitado e não bloqueia objetos
ocupados. Ele não cobre todos os tipos de sincronização do kernel.

## Validação e limites

O gate `test_event_flag_delivery.py` executa a classe, registry, wrappers
HLE, leitor de identidade e getter CP das fontes geradas. Apenas a
retomada do mutex é controlada para tornar as corridas determinísticas.
Os positivos cobrem Set/Clear, sinais repetidos, AND/OR e limpeza,
FIFO/prioridade/empate, timeout, Cancel seguido de nova espera,
Set seguido de Cancel, Delete pendente ou já entregue, posse concorrente,
handles inválidos, custo de Poll e o census limitado com strings próprias.

Quatorze controles negativos executáveis restauram perdas de entrega,
cancelamento indevido, ordenação errada, limpeza incorreta, quebra de
lifetime, excesso de logs ou leitura incorreta dos contadores. Uma prova
separada compila o header `Pthread` real e o leitor de identidade em
configurações Android/FEX e host; remover o include produz a falha de
tipo incompleto esperada. AddressSanitizer e UBSan estão ativos no gate;
LeakSanitizer fica desativado porque o executor local é rastreado. A saída
do registro e o término dos donos são conferidos explicitamente.

O gate de apresentação preserva seus 17 controles negativos e a prova
do header Liverpool real; sua única adaptação é declarar o census e usar
o novo getter CP real no fixture. A composição não muda contagens de FPS,
predicados PM4, FEX, apresentação AHB, filas de draws ou os resultados
guest para fabricar avanço.

Na composição local de ambos os cores, passaram os 14 casos positivos e
14 controles negativos de event flags, a dependência real de `Pthread`
com seu controle negativo, e os nove contratos e 17 controles negativos
da apresentação. O teste de apresentação também recompilou o header real
de Liverpool e confirmou a falha esperada sem seu include. Os logs locais
são `analysis/event-flag-{sotc,order}-gate.log`,
`analysis/event-flag-sotc-dependency.log` e
`analysis/event-flag-{sotc,order}-present-gate.log`; a prova de `Pthread`
do Order está no próprio log do gate. Os hashes de entradas, fontes e
logs estão em `validation/event-flag-delivery-validation.json`.

Compilação, reprodução e testes de host não provam
que o congelamento em gameplay foi resolvido. O próximo APK deve ainda
ser compilado e verificado; sua execução no aparelho deve demonstrar
avanço além da tela observada ou fornecer a identidade da espera restante.
