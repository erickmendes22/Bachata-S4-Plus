# Polling de callbacks GPU — 26/11/2026

## Diferença corrigida

Os quatro caminhos de `Rasterizer::Draw`, `DrawIndirect`, `DispatchDirect` e
`DispatchIndirect` consultavam a timeline Vulkan em toda chamada, inclusive sem
callbacks pendentes. O doador Order retorna com fila vazia, reaproveita o tick
conhecido e limita consultas pendentes a uma por 32 chamadas. O doador SotC
também evita consultar callbacks cujo tick ainda não foi submetido.

Referências: `video_core/renderer_vulkan/vk_scheduler.cpp`, função
`Scheduler::PopPendingOperations`, nas árvores efetivas Order e SotC fixadas em
`parity/exact-revisions.txt`. No Order, `PendingPollLimit=8` está habilitado pela
máscara inicial zero; no SotC, `SOTC_POP_FAST` é habilitado por padrão.

## Adaptação e contratos

`port_pending_poll.py` acrescenta `PopPendingOperationsHot` somente aos quatro
callers de draw/dispatch, para Android e os seriais `CUSA00785`, `CUSA08809` e
`CUSA08034`. Outros títulos conservam a chamada forçada anterior. A política
consulta o serial atual; não fica presa ao primeiro título do processo.

Sob o mutex recursivo existente, o caminho hot retorna sem consultar Vulkan
quando a fila está vazia ou o primeiro callback ainda não pode estar submetido.
Com recorder, também exige a publicação de `RecordedSubmitTick`; avançar
`CurrentTick` sozinho não comprova que o driver recebeu o lote. Se o tick já é
conhecido como concluído, os callbacks elegíveis executam imediatamente sem
outra consulta. Para pendências submetidas ainda não concluídas, a política hot
dos dois cores consulta uma vez a cada 32 chamadas elegíveis.

O caminho público `PopPendingOperations` permanece forçado, com a opção de usar
um tick já conhecido. Recuperação de memória, os callers existentes após espera
e o caminho de submit não recebem o limitador. Não foram adicionados callbacks
dentro de `Wait`, onde o caller pode manter locks de cache.

O callback continua sendo movido e retirado da fila **antes** da invocação. Isso
preserva a ordem FIFO de início e a vida do callable, permitindo que um `Finish`
aninhado execute liberações posteriores antes de repetir uma alocação. Não se
impõe FIFO de término a callbacks aninhados. Não há mudanças em PM4,
`draw_pending_writes`, fences, ABI de shaders ou geração de cache.

## Verificação executável

`test_pending_poll.py --source <árvore>` compila os métodos reais de Hot/Pop,
DeferOperation, SubmitExecution, Wait e Finish, além de Semaphore::Refresh/Wait
e dos prefixos dos quatro entrypoints do rasterizer. O dispositivo Vulkan é a
fronteira determinística da fixture; a contagem ocorre nas chamadas de
`getSemaphoreCounterValue` emitidas pelo `Semaphore::Refresh` de produção.

| Cenário | Implementação anterior | Implementação nova |
| --- | ---: | ---: |
| 256 draws/dispatches com fila vazia | 256 consultas | 0 |
| 256 chamadas com primeiro callback não submetido | 256 | 0 |
| 64 chamadas com callback submetido ainda pendente | 64 | 2 |
| Callback já concluído no tick conhecido | consulta adicional | 0; callback imediato |

Os efetivos Order e SotC passaram para os três seriais, incluindo atraso do
recorder, contador com wrap, submit com/sem recorder, recuperação forçada,
espera seguida de limpeza, `Finish` aninhado/OOM, FIFO e lifetime. O gate anterior
`test_pending_gpu_callbacks.py` também passou nos dois cores sem alterações.

Oito controles negativos foram compilados e rejeitados em execução, sob UBSan:

1. Restaurar o polling em todo draw.
2. Consultar trabalho ainda não submetido.
3. Ignorar o atraso de publicação do recorder.
4. Remover o limite do caminho hot.
5. Adiar callbacks cujo tick já é conhecido como concluído.
6. Aplicar a política hot a títulos externos.
7. Invocar o callback antes de retirá-lo da fila.
8. Aplicar o limitador ao caminho forçado de conclusão.

Essas contagens comprovam a redução das consultas no contrato testado. Não são
medições de custo do driver, FPS ou estabilidade no aparelho e não atribuem a
esta diferença a espera observada no Order ou o congelamento do SotC. A
validação em gameplay continua necessária.
