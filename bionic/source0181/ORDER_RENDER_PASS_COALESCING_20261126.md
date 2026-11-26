# The Order: transações de clear e continuidade de render pass

## Evidência que motivou esta rodada

O diagnóstico `EDF09A45` foi produzido pelo core
`ea720e1acac752be1e9bdfeaf1e097b1c509f174`, CUSA00785, aplicativo 01.02. A sessão
de 26/11/2026 durou aproximadamente 154,98 segundos e terminou por solicitação
do usuário, código 0. Esse encerramento não demonstra estabilidade em outras
cenas. O relato do usuário continua sendo desempenho inferior ao port na mesma
cena; não há uma captura pareada nova do port que permita atribuir uma diferença
numérica a esta alteração.

Fontes locais: `analysis/EDF09A45/shadps4.clean.log`, `session.json`,
`process-exit.json` e `report.json`, extraídos do ZIP original. A revisão nativa
está na linha 9 do log. As linhas 366 e 2446 confirmam a instrução do patch 60 FPS
verificada, limite de apresentação 60, `guest_rate=0` e vblank de 60 Hz.

As 69 janelas `BACHATA_ORDER_READCONST_REUSE` cobrem 136.381.685 µs e mostram:

| Medida observada | Total |
| --- | ---: |
| Bindings | 1.035.833 |
| Bytes solicitados pelos descritores | 447.182.472.684 |
| Bytes de snapshots pequenos | 2.278.420.972 |
| Upload efetivo pelo cache rastreado | 32.763.904 |
| Tempo decorrido dentro do binding medido | 831.578 µs |

O tempo agregado do binding equivale a aproximadamente 0,610% das janelas
observadas. A maior janela por tempo total, linha 5262, registra 22.389 µs de
binding em 2.007.567 µs, aproximadamente 1,115%. `bind_us` é duração de chamadas,
não uma medida de utilização total dos núcleos de CPU. Não se deve continuar
tratando os 447 GB de descritores solicitados como bytes novamente copiados.

Os 250 pares de criação de PSO gráfico fechados somam 218.998 µs; o maior é
4.364 µs. Não há `BACHATA_GPU_WAIT` retido. Os ticks nos pontos de PSO são
fotografias esparsas e não demonstram o tempo ocioso ou ocupado da GPU ao longo
de todo o frame. Esses dados não explicam sozinhos o desempenho restante.

## Diferença ativa encontrada

A comparação usou a fonte efetiva de produção
`validation/pacing-waits-order-stop/src` e o doador efetivo
`parity/sources/order-effective/gpu/shadps4`: PC
`c53cd01d032995fe622033623ab64b4cf6b02233`, composto com Android
`756a4f0cc603b02971d45b36354143249a4fe492`.

No doador, `vk_scheduler.cpp`, `Order1886MergePostClearPass` e
`Scheduler::BeginRendering`, preservam um render pass quando o clear inicial
já foi executado e o próximo desenho pede LOAD dos mesmos attachments. Um novo
clear compatível é emitido por `clearAttachments` dentro do pass. As duas
opções são ativas por padrão, inclusive no launcher Android:
`Order1886LauncherConfig.environment` define `ORDER1886_COALESCE_CLEAR_PASS` e
`ORDER1886_INLINE_ATTACHMENT_CLEAR` a partir de preferências cujo default é true.

Essa utilização é comprovada nos logs originais do port:

| Log do port | Ativação | Último contador de reutilização observado |
| --- | --- | ---: |
| `TheOrder1886-Android-log (11)(2).txt` | linha 467, `enabled=1` | linha 3622, `merged=98304` |
| `TheOrder1886-Android-log (12)(3).txt` | linha 461, `enabled=1` | linha 3722, `merged=102400` |

A fonte Bachata anterior somente reutilizava o pass se todo `RenderState`
continuasse byte a byte igual. Há um caminho concreto que muda apenas o clear:

1. `Rasterizer::BeginRendering` lê `IsMetaCleared` e consome a máscara com
   `TouchMeta(..., false)`; no efetivo anterior, linhas 1856–1857.
2. O próximo desenho conserva view, layout, tamanho e camadas, mas recebe
   `is_clear=0`, porque a transação anterior consumiu o clear.
3. `Image::GetBarriers` não cria outra barreira para o mesmo layout e acesso de
   attachment. Seu conjunto de escritas que obriga uma nova transição inclui
   transfer/shader/memory, não a continuidade do acesso ao mesmo attachment.
4. Sem uma barreira real adicional, o `Scheduler::BeginRendering` anterior
   ainda encerrava e reabria o pass só pela diferença entre CLEAR e LOAD.

A reprodução executa esses métodos reais, incluindo o estado de metadata e as
transições de imagem, e confirma a emissão extra. Ela não estima milissegundos
de driver nem ganho de FPS no aparelho.

## Adaptação e invariantes

`port_order_render_pass_coalescing.py` modifica somente
`vk_scheduler.{h,cpp}` e `vk_rasterizer.{h,cpp}` na árvore gerada. O caminho novo
é restrito ao Android/CUSA00785. Os overrides do doador continuam aceitos;
`ORDER1886_COALESCE_CLEAR_PASS=0` mantém o comportamento anterior, e
`ORDER1886_INLINE_ATTACHMENT_CLEAR=0` mantém a reutilização CLEAR→LOAD, mas
conserva um novo render pass para os clears seguintes.

A comparação normaliza apenas os pedidos/valores de clear. A igualdade de
views, layouts, attachments/aspectos, extensão e camadas permanece obrigatória.
Formato e número de amostras pertencem à identidade imutável da imagem/view.
O caminho existente `Runtime::SetBackingSamples` troca o backing e conserva
as views associadas ao respectivo backing; não se trata uma view diferente
como equivalente porque tem o mesmo endereço guest.

O contrato 0.18.1 usa STORE, nenhum resolve, `viewMask=0` e offset de render area
`{0,0}`. O overlay verifica explicitamente esse contrato e a composição de
`RenderState` antes de aplicar. Uma alteração futura de STORE/resolve/viewMask,
offset, camadas ou identidade faz a aplicação falhar, em vez de ampliar
silenciosamente a regra de reutilização.

Novos clears dentro do pass exigem a mesma identidade, entre 1 e 16 camadas e
layouts compatíveis com escrita do aspecto solicitado. A área e as camadas de
`ClearRect` reproduzem a área inteira do pass original. Valores de cor mantêm
seus bits; profundidade usa `bit_cast`, incluindo -0 e payloads NaN nos testes.
Stencil e profundidade são tratados independentemente. As barreiras reais e
os outros motivos para `EndRendering` continuam encerrando o pass.

O recorder existente rejeita comandos com ponteiros que não tenham cópia
profunda. Por isso, `clearAttachments` usa `Scheduler::RecordDeferred` com
attachments, quantidade e retângulo capturados por valor. A chamada ao driver
ocorre com o command buffer real; nenhum ponteiro à pilha do produtor escapa.

### Clear idêntico rearmado

O gate adicional solicitado na revisão reproduziu um erro também presente no
atalho do doador: depois de um desenho, rearmar a metadata com exatamente o
mesmo valor pode produzir `render_state == new_state`. O retorno imediato
perdia a nova transação. Com execução imediata e diferida, a reprodução anterior
terminava com valor 100 do desenho onde o novo clear exigia valor 11.

A correção passa um argumento explícito `metadata_clear_consumed` do consumo
real em `Rasterizer::BeginRendering` até `Scheduler::BeginRendering`. Os dois
consumidores, Draw e DrawIndirect, transportam esse resultado. A API tem default
false para os outros callers. Somente o caminho Order evita o atalho de estado
idêntico quando houve consumo real de uma nova máscara. A continuidade de
`depth_clear_enable`, sem nova metadata, conserva o comportamento anterior;
não se infere uma nova transação apenas porque o registrador permanece ligado.

## Validação

Comando do gate:

```sh
python3 -B bionic/source0181/test_order_render_pass_coalescing.py --source CAMINHO_DA_FONTE_EFETIVA
```

O gate compila e executa o código efetivo de `Rasterizer::BeginRendering`,
`Image::GetBarriers`, `Runtime::Transit/FlushBarriers`, metadata de produção e
`Scheduler::BeginRendering/EndRendering/RecordDeferred`, com UBSan. Lookup de
texturas, dispositivo Vulkan e fila do recorder são fronteiras simuladas. As
filas diferidas verificam ordem e propriedade dos argumentos depois que a pilha
e os valores do chamador já foram sobrescritos.

Na sequência reproduzível de 2.048 ciclos de clear/desenhos:

| Política | Begins/ends | Clears inline | Draws preservados |
| --- | ---: | ---: | ---: |
| Baseline / override desligado / desktop | 4.096 / 4.096 | 0 | 4.096 |
| Coalescência completa | 1 / 1 | 2.047 | 4.096 |
| Coalescência, inline desligado | 2.048 / 2.048 | 0 | 4.096 |

Os resultados de cor/profundidade/stencil e a barreira original são verificados.
Outras variantes cobrem views/layouts/dimensões/camadas/slots incompatíveis,
oito alvos de cor mais profundidade/stencil, máscaras esparsas, clears de aspectos
isolados, limite de camadas, clear idêntico rearmado, zclear persistente e outros
títulos. Dez mutações negativas rejeitam perda de reutilização, comparação
relaxada, clear descartado, comando não emitido, ponteiro em fake handle,
camadas incorretas, clear inline em aspecto read-only, alteração de outros
títulos, clear rearmado perdido e reclear por registrador persistente. Seis
controles de aplicação rejeitam mudanças no contrato de dynamic rendering.

## Captura de atividade e limites da conclusão

`BACHATA_ORDER_RENDER_PASS` registra `begins`, `ends`, `same`, `post_clear` e
`inline_clear`, com `wall_ms` e duração da janela. Os contadores pertencem ao
thread produtor; não são contadores de frames. O relógio é consultado a cada
1.024 decisões, e há no máximo uma linha por cinco segundos por thread ativo.
Isso permite confirmar a atividade no aparelho sem emitir uma linha por desenho
ou introduzir uma espera de GPU.

| Evidência | Conclusão permitida | Verificação restante |
| --- | --- | --- |
| ReadConst medido em aproximadamente 0,61% das janelas | As grandes cópias redundantes anteriores deixaram de dominar esse caminho | Correlacionar outros custos do frame |
| Coalescência ativa em ambos os logs do port e ausente na fonte Bachata anterior | Divergência funcional de emissão de render passes | Contadores desta build na cena do usuário |
| Métodos reais preservam o resultado com menos begins/ends no gate | Redução reproduzível de comandos equivalentes | Tempo de driver/GPU e FPS no aparelho |
| Metadata idêntica rearmada perde clear no atalho anterior | Erro reproduzido e corrigido por transação explícita | Ausência de regressão visual em gameplay |

O log EDF09A45 recebe `readbacksMode: 2` (linha 21). O shim do port usa Relaxed
como default; o launcher injeta `ORDER1886_READBACKS` conforme a preferência,
default relaxed→1, precise→2 e selective→3. Os dois logs do port disponíveis não
incluem essa preferência nem o valor efetivo da variável. Portanto, o default
é comprovado, mas não se pode afirmar o modo dessas duas execuções. Esta
alteração não muda o modo recebido, o tracker de memória ou a política de
readback para tornar a comparação artificialmente mais rápida.

Este documento registra uma correção concreta e suas provas locais. Não afirma
equivalência completa, ganho de FPS em gameplay nem ausência de outros gargalos.
FEX, instruções do jogo, shaders, caches binários, apresentação, UI e catálogo
de patches permanecem fora deste grupo.
