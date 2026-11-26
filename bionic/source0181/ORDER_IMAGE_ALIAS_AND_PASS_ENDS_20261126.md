# The Order: imagens alias, consumidores e encerramentos de passes

## Resultado desta rodada

A comparação encontrou uma família funcional ativa no port efetivo e ausente no
Bachata: imagens Vulkan distintas, com a mesma base de memória do jogo, não
compartilhavam a escrita mais recente da GPU. O caso real de lookup com imagens
lineares RGBA16F de 1280×736 e 1280×720 cria dois backings. A reprodução anterior
à correção escreve `17` no maior e lê `0` no menor; o protocolo de alias transmite
`17`. Isso demonstra perda de coerência. Não demonstra que essa perda explique
a diferença inteira de FPS relatada pelo usuário.

A adaptação inclui publicação do escritor, cópia de interseção, autoridade com
UID, invalidações, consumidores de download/GC, retirada parcial no owner GPU e
vida útil dos recursos na fila existente. A revisão encontrou e corrigiu arestas
do próprio algoritmo doador, descritas abaixo, em vez de reproduzi-las como uma
suposta equivalência.

Também foi removida uma chamada duplicada de sincronização de imagem no produtor
de texel buffers do Order. As funções reais `ObtainBuffer` e `SynchronizeMemory`
demonstram duas chamadas no caminho anterior e uma no caminho corrigido. A
frequência desse caminho no aparelho não consta no log atual.

A captura nova identifica por que um passe **aberto** foi encerrado. Ela acompanha
as correções funcionais; não é apresentada como otimização nem como medição de
tempo GPU.

## Evidência recebida do aparelho

Fonte: `analysis/53A4D3EC/native-clean.log`, extraída do ZIP de diagnóstico com CRC
validado pela tarefa principal. A linha 9 identifica o core
`ea646fe37584534209ad5f64d2a21f75b7c18a90`. A sessão foi de
14:34:13.297244 a 14:36:48.746768 UTC, encerrada pelo usuário, com código zero.
O primeiro present foi registrado às 14:34:28.670952 UTC no log da aplicação.

O log nativo registra `readbacksMode=2` na linha 21, readback de imagens lineares
desativado na linha 22 e DMA direto desativado na linha 23. O patch de 60 FPS está
verificado na linha 366; a linha 2447 registra `guest_rate=0`, vblank de 60 Hz e
limite de apresentação 60. Essa rodada não altera esses valores.

As somas abaixo são de janelas emitidas pelo mesmo produtor. Janelas de threads
diferentes não começam nem terminam juntas; não são um balanço por frame.

| Série no log | Cobertura emitida | Resultado observável |
|---|---:|---|
| `BACHATA_ORDER_RENDER_PASS`, GpuDraw, linhas 4430–5304 | 27 janelas; 136.762.123 µs | 361.899 begins, 352.897 ends, 848.677 decisões iguais, 22.703 coalescências após clear, zero inline clears |
| Mesma série, GpuComm, linhas 4604–5190 | 8 janelas; 123.000.862 µs | 8.192 ends, zero begins nessas janelas |
| `BACHATA_ORDER_READCONST_REUSE`, linhas 2533–5308 | 70 janelas; 138.489.423 µs | 1.070.654 bindings; 483.541.010.724 bytes solicitados |
| Snapshots ReadConst | Mesmas 70 janelas | 736.489 bindings; 2.310.519.972 bytes copiados |
| Cache rastreado ReadConst | Mesmas 70 janelas | 334.165 bindings; 34.496.512 bytes efetivamente enviados |
| Duração instrumentada dos bindings ReadConst | Mesmas 70 janelas | 825.738 µs; aproximadamente 0,596% da duração das janelas |

`bind_us` é duração da função instrumentada, não ocupação total de CPU. A série
não sustenta atribuir novamente a queda inteira a cópias ReadConst. O contador de
passes mostra que a coalescência anterior está sendo usada, mas não informa quem
encerra o passe antes da próxima tentativa de reutilizá-lo. Esse é o dado que a
captura de motivos passa a fornecer.

Não há ganho de FPS desta nova revisão medido no aparelho. Os valores anteriores
não são um ensaio controlado de mesma cena/cache, e não servem para declarar
equivalência de desempenho.

## Comparação com o port efetivo

Árvore comparada: `parity/sources/order-effective/gpu/shadps4`, resultado efetivo
do port PC `c53cd01d032995fe622033623ab64b4cf6b02233` com a montagem Android
`756a4f0cc603b02971d45b36354143249a4fe492`. A base Bachata desta rodada é
`validation/boot-lod-pass-order/src`, correspondente à produção `ea646fe3` salvo
marcador de build e fixture já verificados pela tarefa principal.

Os dois logs originais do port, em `analysis/port-reference-logs`, comprovam uso
de alias: `TheOrder1886-Android-log (11)(2).txt`, linha 1126, registra duas cópias
RGBA16F 1280×720 por frame, com 0,389 ms na janela; `(12)(3).txt`, linha 1126,
registra as mesmas duas cópias, com 0,510 ms. Há 60 e 62 linhas dessa etapa,
respectivamente. São medições do port nessas janelas, não previsão de custo ou
ganho para o Bachata.

Ambos os logs têm zero ocorrências de `ORDER1886_GPU_INLINE_CLEAR`. Portanto
`inline_clear=0` no Bachata não prova uma lacuna ativa. Não foi criado um toggle
para forçar clears. A política recebida de readbacks continua intacta: os logs
originais não provam qual override de modo foi efetivamente selecionado no port.

| Divergência ou hipótese | Evidência e alcance | Tratamento |
|---|---|---|
| Autoridade entre imagens da mesma base | Doador: `texture_cache.cpp` 376–492, 1349–1384 e `aliasing.cpp`; etapa de cópia presente nos dois logs originais. Baseline cria backings distintos e não sincroniza suas escritas | Protocolo completo restrito ao Order Android e a pares reconciliáveis nas duas direções |
| Texel buffer sincronizado duas vezes | Baseline `buffer_cache.cpp`: `ObtainBuffer` 203/208 e retorno de `SynchronizeMemory` 506; doador chama uma vez | Remover apenas a segunda chamada no Order; preservar a primeira, readbacks e upload rastreado |
| Muitos passes reabertos | 361.899 begins nas janelas de GpuDraw; causa dos ends não registrada | Contar closures efetivas por produtor, scheduler e thread |
| Ausência de inline clear | Também ausente nos dois logs do port | Hipótese descartada como prova de lacuna ativa |
| Algoritmo básico de barreiras de imagens | `Image::GetBarriers` e `Runtime::FlushBarriers` têm o mesmo fluxo relevante nas fontes comparadas | Nenhuma redução especulativa de barreiras |
| MultiCopy HLE/limites de lote do doador | Diferença de fonte; hash/etapa correspondente não observado nos logs retidos | Não usar como causa demonstrada nem portar isoladamente nesta rodada |
| Readbacks Relaxed versus Precise | Bachata prova modo 2; seleção efetiva no port não demonstrada pelos logs | Preservar modo recebido; não ativar merge diferido especulativo |

## Contratos da família de alias

`port_order_image_alias.py` acrescenta `GetOrderAliasCopyExtent`, estado por base,
geração por imagem, IDs acompanhados de UID e as transições/cópias no Runtime.
O acesso ao estado acontece sob a mutex de lifetime do TextureCache. O port
efetivo publica intenção de escrita em render targets e storage images; a
adaptação preserva esses produtores e sincroniza o alias antes de sua leitura.

O grupo exige compatibilidade de base, bits por pixel, samples, tiling, pitch,
tipo e demais propriedades de layout do helper doador. `CanAlias` exige também
que a cópia seja suportada em **ambas as direções**. Isso preserva o caso
demonstrado 736↔720 e evita registrar como autoridade um par que só poderia ser
lido em uma direção. Pares de uma e duas layers, larguras diferentes ou volumes
que não permitem reconciliação parcial permanecem no comportamento anterior.

Uma escrita menor fica pendente sobre a authority maior até ser combinada com
sua região não alterada. Registrar um terceiro tamanho não promove esse writer
parcial antes da combinação. Se o backing maior ainda contém somente dados de
CPU, ele é inicializado antes da publicação do primeiro writer parcial. O teste
com cauda CPU `31`, prefixo GPU `23` e terceiro tamanho intermediário preserva
ambas as regiões.

Invalidações CPU e de buffer GPU retiram a authority antiga. O caminho
`MaybeCpuDirty` também a retira quando o hash confirma uma mudança na página já
desprotegida. O mecanismo FEX, os aliases de memória guest e a política recebida
de readback não foram substituídos.

### Consumidores e retirada

Downloads e GC combinam o writer pendente e consultam a authority antes dos
filtros `GpuModified`/`SafeToDownload`. Só grupos efetivamente marcados `Aliased`
exigem a publicação síncrona do writeback; imagens sem alias mantêm a política
anterior. Após `TryWriteBacking` bem-sucedido, apenas aliases com geração mais
antiga reconsideram os bytes de CPU. A ordem de locks do processamento em lote é
lifetime, lista de downloads e estado diferido, coerente com a retirada.

No unmap parcial, simplesmente marcar a imagem sobrevivente como dirty não
resolve: a memória CPU pode ainda conter dados antigos. O wrapper detecta um
grupo real sob a mutex, solta essa mutex antes de esperar e executa a preservação
e a retirada juntas no owner GPU usando `Liverpool::SendCommand<true>`.
`UnmapImages` sincroniza apenas imagens que não intersectam nenhuma parte da
faixa retirada. Não faz `RefreshImage` nem lê memória guest nessa preparação.
No unmap total não há cópia de sobreviventes.

Os callers de `MemoryManager` fazem o early GPU unmap antes da aquisição do lock
escritor de VMA: baseline `memory.cpp` 474, 708, 889, 942 e 1023. O lock de
serialização de mapeamento continua preservado. O caminho sem alias conserva a
execução anterior. O teste executa `SendCommand` e `ProcessCommands` reais para
caller CP, caller Draw e caller externo, e verifica que a espera externa não
segura a mutex de textura.

`Runtime::CopyAliasImage` mantém as transições transfer-read/transfer-write e
grava o comando por `RecordDeferred`, capturando handles e região por valor.
Recursos e views continuam sendo liberados pelo `DeferOperation` existente.
UID e estado Registered impedem uso de uma slot reciclada como authority;
`TouchImage` não toca um nó LRU já retirado durante uma consulta para rebind.

## Captura dos motivos de encerramento

`port_order_pass_end_reasons.py` acrescenta um argumento com default em
`Scheduler::EndRendering`. A decisão permanece igual: drenar a fila de desenho,
retornar se não há passe aberto e só então encerrá-lo. A contagem acontece apenas
nesse último ramo. Os contadores `BACHATA_ORDER_RENDER_PASS` anteriores continuam
presentes.

O registro `BACHATA_ORDER_PASS_END_REASON` separa troca de estado, submissão,
cópia/fill/inline de buffer, refresh/upload/download/cópia/alias de imagem,
resolve, clear, troca de samples, barreira, dispatch, clamp indireto, tiling,
blit, fault buffer, retirada de pipeline e apresentação. Cada bucket pertence a
um scheduler e à thread que efetivamente encerrou o passe. Motivo não anotado
continua visível como `other`.

Não há relógio em cada draw nem em `EndRendering` que não fecha passe. O relógio
é consultado após 1.024 closures reais, além da inicialização do bucket, e o log
compacto usa janelas de cinco segundos por bucket. Se uma thread excepcionalmente
usar mais de oito schedulers distintos, o bucket substituído é emitido antes,
para não misturar ou perder sua contagem. A saída informa
`wall_ms`, `window_us`, `owner`, `thread`, total e motivos. Esses números são
contagens de encerramentos, não duração GPU. A relação com FPS exige nova
medição do aparelho.

As anotações do presenter ficam em `port_order_present_end_reasons.py`, aplicado
depois do grupo de progresso/FIFO de apresentação. Elas só atribuem o motivo
`Present`; não alteram o fluxo pertencente àquele grupo.

## Validação e integração

A fonte aplicada de trabalho é `analysis/order-image-alias-validation`. O gate
`test_order_image_alias.py` executa métodos de produção de lookup/overlap,
registro, refresh, invalidação, autoridade, cópia, retirada, unmap e fila de
comandos. A execução Vulkan, armazenamento de pixels, proteção de página e hash
são fronteiras simuladas. Isso prova os contratos exercitados e não substitui
validação no driver Adreno.

O gate passou com UBSan e rejeitou 18 controles negativos, incluindo perda da
cauda ao registrar terceiro tamanho, backing CPU não inicializado, autoridade
obsoleta após escrita, UID reciclado, acesso a LRU retirada, unmap sem
preservação/owner, sobrevivente que intersecta a remoção, download parcial sem
commit, grupo de apenas uma direção, duplicação de sincronização texel e registro
concorrente entre o antigo probe de alias e a retirada. A decisão do caminho sem
alias agora ocorre sob a mesma mutex que protege a retirada; a espera do owner
sempre acontece depois de soltar essa mutex.

`test_order_pass_end_reasons.py` passou os métodos reais de encerramento e
agregação, com relógio controlado na fronteira. Seus cinco controles negativos
rejeitam contar no-op, remover a contagem real, misturar owners, consultar relógio
a cada closure e retirar o dreno anterior à decisão. O contrato verifica os 25
produtores fora do presenter e, após a anotação final, também seus três callers.

Os gates existentes de memo de lookup, memo de views, indirect, coalescência e
ReadConst passaram sobre
a fonte integrada. Os dublês que não têm grupos alias conservam essa fronteira
explícita; o novo gate testa o protocolo real. Os dublês de scheduler aceitam o
motivo adicional. Os controles anteriores de coalescência e ReadConst são
preservados. O gate de consumidor `test_order_alias_download.py`, mantido pela
tarefa principal, compila adicionalmente o download real e seus caminhos de
publicação: sete casos e quatro controles negativos passaram.

Ordem de integração requerida:

1. Aplicar os overlays anteriores de textura/memos/ReadConst/coalescência.
2. Aplicar `port_order_image_alias.apply(root)`.
3. Aplicar `port_order_pass_end_reasons.apply(root)`.
4. Aplicar o grupo compartilhado `port_present_queue_progress`.
5. Aplicar `port_order_present_end_reasons.apply(root)`.

Comandos dos novos gates, usando a raiz efetiva em `SOURCE`:

```sh
python3 -B bionic/source0181/test_order_image_alias.py --source "$SOURCE"
python3 -B bionic/source0181/test_order_alias_download.py --source "$SOURCE"
python3 -B bionic/source0181/test_order_pass_end_reasons.py --source "$SOURCE"
```

A integração, API preflight, compilação Android, assinatura, revisão efetiva do
APK e entrega permanecem sob responsabilidade da tarefa principal. Este
documento não declara equivalência completa de gameplay ou ganho de FPS antes
de uma nova captura comparável no aparelho.
