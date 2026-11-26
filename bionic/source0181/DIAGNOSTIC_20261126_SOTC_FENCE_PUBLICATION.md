# SotC: publicação de fences e readbacks — 26/11/2026

## Evidência e limite da amostra

O diagnóstico BS4-20261126-42D59D11 identifica CUSA08809 e o core
d95da7bddb405a4a2da9a8f1d7451a0aab2cdb87 (shadps4.log, linha 9).
Readbacks estão no modo 2 e a cópia de buffers GPU está habilitada
(linhas 21 e 26). DrawPipe está ativo com FEX, oito CPUs, signals e
recorder (linha 2218).

O primeiro frame foi apresentado às 11:22:17.684884Z, cerca de 18,45 s
após o lançamento do backend. A sessão terminou por solicitação do
usuário às 11:22:45.089214Z, código zero, após 45,86 s. Esse encerramento
não demonstra crash. O aplicativo registra somente FPS zero no primeiro
frame e continua recebendo controles antes da parada.

Todos os 366 marcadores de progresso são 183 pares fechados de PSOs no
Main: 83 compute e 100 gráficos, tick 1. O maior tempo é 59.727 µs
(linha 334). O último par FS465f664a/VS5dab0dab termina em 10.546 µs
(linha 509). Não há fase aberta, compilação de shader em runtime ou
GPU_WAIT/GPU_STALL retido. O corte de tamanho está na linha 6934.

| Evidência | Hipótese | Teste ou conclusão |
|---|---|---|
| Todos os PSOs registrados terminam | Último PSO preso | Não sustentada pelos marcadores |
| GpuDraw deixa último registro na linha 2508; GpuComm conclui liberações até 4907; workers continuam até 12506 | Bloqueio global do CP desde a última residência | Não sustentado durante essas liberações; uma espera guest por memória continua possível |
| Cancelamento solicitado e saída zero | Crash observado | Não demonstrado; o sintoma relatado é congelamento |
| EOP/EOS usam backing físico sem invalidar o tracker | Readback restaura label antigo e impede progresso | Reproduzido com os métodos reais; corrigido pela ordem ativa do doador |
| Log não contém endereço/valor do label aguardado | Este defeito explica integralmente a sessão | Pendente de confirmação no aparelho; o repro demonstra o mecanismo, não identifica o label da amostra |

## Defeito reproduzido e caminho ativo do doador

O alias físico FEX contorna a proteção da página guest. Os callbacks
EOP/EOS anteriores publicavam o novo valor por TryWriteBacking sem marcar
a cópia GPU como desatualizada nem invalidar um readback anterior:

1. A página GPU contém zero no label e dados novos nos bytes vizinhos.
2. EOP/EOS escreve o novo label no backing físico.
3. Um readback posterior, ou iniciado antes do fence, restaura zero.
4. A condição que aguarda o novo valor permanece falsa.

O repro executou oito combinações sob UBSan: EOP64/EOS32,
readback anterior/posterior e ordem antiga/corrigida. A ordem antiga
perdeu o valor em todos os quatro casos correspondentes. A correção
preservou o label, os bytes GPU vizinhos e rejeitou o snapshot antigo.

Na árvore efetiva do doador SotC, shadps4/video_core/amdgpu/liverpool.cpp,
WriteFenceValue nas linhas 875–885 invalida antes da escrita física.
EOS chama esse helper nas linhas 1793–1794 e o EOP normal nas 1874–1876.
É o caminho ativo normal; SOTC_EOP_DEFER é uma opção separada e não foi
habilitada por esta adaptação.

## Correção e ownership

port_sotc_fence_publication.py adiciona o helper e liga os callbacks
EOP/EOS somente para CUSA08809/CUSA08034. A invalidação antes da escrita
resolve os bytes GPU vizinhos, invalida snapshots anteriores e marca a
página para o próximo upload. Outros títulos mantêm a escrita anterior.

EOP/EOS já executam via QueueGpuTask, no proprietário CP/Draw. O argumento
assume_locks=true mantém o readback nesse proprietário, sem esperar por
uma tarefa reenfileirada nele próprio. Os locks reais do tracker continuam
ativos; InvalidateRegion os libera antes do callback de readback. Os
pacotes PM4 continuam capturados por valor dentro da tarefa existente.
O grupo não altera ASC/rptr, fila, FEX, UI ou a política de EOP deferido.

## Verificação

test_sotc_fence_publication.py compila o helper, os callbacks e os métodos
efetivos de MemoryTracker/RegionManager, invalidação do rasterizer e
ReadMemory/BeginAsyncReadback/FinishAsyncReadback. Apenas armazenamento e
execução Vulkan são substituídos por dados determinísticos.

- 61 casos sob UBSan passaram: dois CUSAs, 4/8 bytes, fronteiras de
  páginas, snapshots retidos, vizinhos, upload seguinte, página somente
  cacheada sem espera GPU, outros títulos e execução sem rasterizer.
- Quatro controles negativos passaram: remover invalidação, movê-la
  para depois da escrita, EOP pulando o helper e EOS pulando-o.
- DrawPipe/PM4 passaram na fonte corrigida: 9.072 casos de protocolo
  e 4.096 voltas da fila.
- A reconstrução completa aplicou todos os overlays sem âncora pendente;
  os 312 contratos de API passaram com o polling e a publicação de fences
  combinados. O marcador de revisão é gerado a partir do checkout nativo.

Gameplay no aparelho deverá confirmar se esta correção elimina o
congelamento observado; os testes não substituem essa validação.
