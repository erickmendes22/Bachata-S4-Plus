# The Order: reuso da preparação de attachments e origem das barreiras

## Alcance e resultado comprovado

Esta rodada adapta o `RenderStateMemo` ativo do port ao cache de texturas e ao
recorder do Bachata ARM64 Bionic + FEX. O alcance funcional é Android,
`CUSA00785`. Também acrescenta uma captura amortizada dos produtores de
barreiras e dos critérios de registro de aliases. A captura não muda decisões
de sincronização, elegibilidade de imagens, modo de readback ou ordenação de
comandos.

O teste dos métodos reais demonstra redução de preparação repetida na CPU:
em 8.192 draws com dois attachments estáveis, o caminho completo cai de 8.192
para 2 chamadas e `UpdateImage` de 16.384 para 4. Os dois caminhos produzem
**um passe e uma barreira**, tanto com gravação imediata quanto com recorder
diferido. Isso não é uma medição de FPS no aparelho, nem demonstra redução
do número de barreiras GPU. A equivalência de desempenho e estabilidade em
gameplay continua dependendo da comparação da mesma cena, driver, patches,
resolução e estado do cache.

## Evidência do aparelho: B732DE22

A fonte da captura é `analysis/B732DE22/native-clean.log`, derivada do ZIP
fornecido pelo usuário. A linha 9 identifica o core
`a2d61cca96e2c9b65276e307c0b10d4f950b3c9b`. O `process-exit.json` registra
164,864476 s de processo e encerramento solicitado pelo usuário, código 0;
o primeiro frame apresentado ocorreu 16,665666 s após o início do processo
(`session.json`). Não houve falha terminal nessa sessão. Há duas recuperações
do guard CALL/RET do FEX nas linhas 5055 e 5171, ambas com guest RIP
`0x72c4ae600d`. O guard é preservado; esses dois eventos não explicam, por si,
o volume de barreiras observado.

As configurações efetivas verificadas são:

| Evidência | Valor e localização no log |
| --- | --- |
| Readback | `readbacksMode: 2`, `readbackLinearImages: false`, linhas 21–22 |
| Engine e samples | `-disablecloth -msaa 1`, linha 46; MSAA single, linha 118 |
| Apresentação | AHB elegível e ativo em 1280×720, janela 2688×1216, linhas 133–134 |
| Patch de apresentação | `patch60_verified=true`, app 01.02, limite 60, linha 369 |
| Solicitação guest | `guest_rate=0`, vblank 60 e limite 60, linha 2441 |

As 38 linhas de `BACHATA_ORDER_PASS_END_REASON` pertencem a duas threads.
Não se somam seus tempos como se fossem uma duração única de execução.
No GpuDraw, as janelas publicadas somam 146,036864 s e 396.288 encerramentos
de passes efetivamente abertos:

| Motivo no GpuDraw | Encerramentos |
| --- | ---: |
| Barrier | 267.115 (67,4% do total) |
| State | 45.484 |
| Buffer fill | 24.222 |
| Indirect clamp | 19.385 |
| Buffer copy | 13.550 |
| Image refresh | 10.835 |
| Resolve | 5.889 |
| Image download | 5.888 |
| Dispatch | 3.919 |
| Image copy | 1 |
| Image alias | 0 |

Na primeira janela GpuDraw, linha 4424, são 4.591 barreiras entre 7.168
encerramentos. Na última, linha 5420, são 11.661 entre 16.384. A linha 5425
registra `begins=16100`, `ends=15773`, `same=98553`, `post_clear=1670` e
`inline_clear=0`. A categoria Barrier identifica o local que encerrou o passe;
ela ainda não identifica o recurso, a dependência ou o tempo gasto na GPU.

A thread de comandos `GpuComm` publica outras 146,159679 s de janelas e 10.240 encerramentos:
4.531 por apresentação, 2.876 por cópia de buffer, 2.211 por preenchimento e
622 por submissão. Ela não registra encerramentos Barrier nessas janelas.
As janelas não incluem necessariamente o prefixo de inicialização e a cauda
da sessão antes do próximo intervalo de emissão.

## Comparação com a fonte efetiva do port

O doador utilizado é a árvore efetiva em
`parity/sources/order-effective/gpu/shadps4`, com PC
`c53cd01d032995fe622033623ab64b4cf6b02233` e adaptação Android
`756a4f0cc603b02971d45b36354143249a4fe492`. Não se comparou apenas o nome de
uma opção ou um repositório sem os overlays que realmente compilam.

O port define `BeginSignature` e `BeginMemo` em
`video_core/renderer_vulkan/vk_rasterizer.h:176–205`, constrói a assinatura em
`vk_rasterizer.cpp:3079` e aplica o memo em `BeginRendering`, linhas 3196–3253.
A verificação de passe aberto fica em `vk_scheduler.h:907`.

`RenderStateMemo` é o bit 44 em `gpu/shim/ps4_toggles.h:55`. O arquivo do pin
PC exato, preservado em
`analysis/order-donor-runtime/runtime_memory-c53cd01d.c`, define a máscara
global sem inicializador na linha 805: seu valor inicial é zero. A mudança
de máscara ocorre pelo watcher na linha 815, habilitado pelo ambiente
`ORDER1886_TOGGLE_FILE`, linha 828. A montagem Android não substitui esse
arquivo, conforme a origem já registrada em `TEXTURE_BINDING_MEMO_20261126.md`.
Portanto o memo está ativo por padrão; o port o suspende também durante sua
captura de frames. Fonte primária do arquivo PC:
<https://github.com/JulioCacko/The-Order-1886_pc/blob/c53cd01d032995fe622033623ab64b4cf6b02233/src/runtime_memory.c>.

| Divergência ou hipótese | Evidência | Tratamento desta rodada |
| --- | --- | --- |
| Preparação completa repetida de attachments | Memo ativo no doador; baseline Bachata prepara novamente mesmo em passe idêntico aberto | Memo adaptado com validação dos recursos vivos, metadados e limites de comando |
| Escrita de attachment idêntico causaria todas as barreiras | Hipótese refutada pelo código e pelo teste real: `GetBarriers` exclui ColorAttachmentWrite/DepthStencilAttachmentWrite de seu conjunto de escritas que exigem nova barreira | Nenhuma barreira removida; ambos os caminhos mantêm um passe e uma barreira na sequência estável |
| Ausência de `image_alias` significa ausência de registros | O contador anterior mede encerramentos por cópia, e o marker de alias mede cópias; nenhum mede todos os registros | Novo censo distingue registros, candidatos, rejeições, escritas e sincronizações de membros |
| `inline_clear=0` por si demonstraria defeito | O caminho inline também não é ativado por padrão no doador | Nenhuma mudança de política baseada nesse zero |
| Categoria Barrier explica tempo GPU | Não há identificação do produtor ou duração GPU nessa categoria | Captura dos produtores e dos hazards reais, sem alterar os hazards |

Os logs originais do port também contêm trabalho que deve ser comparado com
cautela. Em `TheOrder1886-Android-log (11)(2).txt:1126`, há duas cópias de
alias por frame, 0,389 ms/frame; em `(12)(3).txt:1126`, duas e 0,510 ms/frame.
Ambas são `R16G16B16A16Sfloat 1280x720`. O segundo log mostra sete passes
`lighting-post 1280x720` na linha 1124 e um download `R32Sfloat 1x1` por frame
na linha 1147. Esses valores não podem ser convertidos em ganho para a nova
build, nem provar que o mesmo grupo de aliases foi registrado na nova cena.

## Contrato do memo adaptado

`port_order_render_state_memo.py` conserva o corpo anterior como
`BeginRenderingFull` e acrescenta um caminho de reuso. O hit exige que
continuem iguais o tick do scheduler, a identidade do passe aberto e sua
serial, a assinatura dos attachments e os recursos efetivamente vivos.
Uma nova abertura física de passe incrementa a serial. Uma mudança de
command buffer, fim/reabertura de passe, feedback ou clear retorna ao
caminho completo. A primeira abertura exige uma transação adicional para
estabilizar a serial; por isso o teste final resulta em duas preparações.

A assinatura guarda valores, não ponteiros para descritores temporários:
IDs, `ImageViewInfo` completo, samples, máscara de render targets, estado
depth/stencil, endereços de metadados e geração do registro. A validação de
`TextureCache::CheckRenderStateImages` mantém o mutex durante toda a
verificação e repete a leitura da geração depois de adquirir esse mutex.
Ela verifica:

- Imagem registrada, ID/UID vivo, backing/UID e view/UID correspondentes,
  limites de mip/layer, samples e layout/access dos subrecursos selecionados.
- Ausência de CpuDirty/GpuDirty/MaybeDirty, `needs_rebind`, binding ativo ou
  estado Aliased. Exige conteúdo GPU materializado e cobertura completa do
  rastreamento de memória. Aliases continuam executando a transação original
  de autoridade e escrita.
- Propriedade dos metadados por tipo, ID e UID; nenhum clear pode ter sido
  rearmado nas layers usadas. Um probe que falha não consome o clear.
- Associação viva entre depth e stencil companion. A captura encontra a
  associação; hits posteriores validam as identidades armazenadas.

Uma aresta encontrada na revisão independente foi fechada: o caminho
completo consulta os endereços crus CMask/HTile dos registradores, enquanto
`ImageInfo` pode normalizá-los para zero quando os bits de uso estão
desligados. Endereços diferentes agora impedem tanto o hit quanto a captura
do memo, preservando a transação original. O teste rearma CMask e HTile
válidos registrados por outra imagem e rejeita a remoção desse guard.

Só depois de todos os attachments serem aceitos o hit atualiza tick/LRU.
A validação não grava comandos, não espera outro owner e não copia memória
guest. Não há nova semântica de shader nem formato de cache de shaders.
Os demais títulos e a execução fora de Android seguem o caminho completo.

Referências na árvore de validação desta etapa
`analysis/order-renderstate-validation/src`:
`vk_rasterizer.cpp:1887–2002`, `texture_cache.cpp:1484` e
`vk_scheduler.h:398–403`. Os caminhos são, respectivamente,
`video_core/renderer_vulkan` e `video_core/texture_cache`.

## Captura de barreiras e registro de aliases

`port_order_barrier_census.py` não é uma otimização de GPU. Ele responde à
pergunta que o contador anterior deixa em aberto: quais consumidores e
dependências realmente precedem os encerramentos Barrier nessa execução?

`Runtime::IsBufferAccessed` preserva seu resultado e seu curto-circuito,
registrando RAW/WAW/WAR somente quando o tracker detecta conflito.
`Runtime::Transit` inspeciona apenas as novas barreiras de imagem geradas.
`FlushBarriers` contabiliza somente a chamada que realmente encerra um
passe aberto e limpa a atribuição pendente ao publicar as dependências.
A atribuição pendente fica no `Runtime`, acompanhando a transferência de
owner/recorder; os escopos léxicos por thread apenas identificam a origem.

O marker `BACHATA_ORDER_BARRIER_CAUSE` distingue buffers, ReadConst, GDS,
texturas, attachments, vertex/index buffers, indiretos e dispatch. Separa
dependências só de memória, só de imagem e mistas; registra também layout,
access e escrita de imagem. Vários produtores ou tipos podem participar da
mesma publicação: esses campos não são partições que devam ser somadas.
`unattributed` conserva casos sem origem identificada em vez de atribuí-los
artificialmente a um produtor.

O marker `BACHATA_ORDER_ALIAS_CENSUS` diferencia registros e registros
marcados Aliased, candidatos na mesma base, pares elegíveis nas duas
direções, rejeições de layout/shape/format/direção e uso por escrita/sync.
Ele usa os critérios reais de `GetOrderAliasCopyExtent` e não altera
`CanAlias`, a authority, os copies ou o retirement. O scan adicional ocorre
no registro, não em cada draw.

Os três markers novos usam janelas por owner e thread, com oito slots TLS.
O relógio é consultado na criação da janela e a cada 1.024 eventos; uma
linha só é publicada após pelo menos cinco segundos. O caminho por draw
não aloca nem emite logs individuais. Janelas com poucos eventos podem
demorar mais ou não ser publicadas antes do encerramento.

## Validação concluída antes do congelamento

Todos os comandos abaixo foram executados sobre
`analysis/order-renderstate-validation` com os dois overlays finais:

| Gate | Resultado observado |
| --- | --- |
| `test_order_render_state_memo.py` | Métodos reais, recorder imediato/diferido, desktop e 18 controles negativos: PASS |
| `test_order_barrier_census.py` | Tracker/proveniência reais, relógio/owner, critérios de alias, 7 negativos e 8 guards de produtores: PASS |
| `test_order_render_pass_coalescing.py` | 10 controles negativos e 6 guards de aplicação preservados: PASS |
| `test_indirect_submission_protocol.py` | 178.542 records, 12.377 batches, hazards reais, GPU-produced, limites/lifetime e 3 negativos de dependências: PASS |
| `test_order_image_alias.py` | Find/refresh/authority/copy/invalidation/retire e 18 negativos preservados: PASS |

Os negativos do memo modificam os métodos extraídos da produção. Além de
identidade, dirty, alias, metadata, subrecursos, companion, título, passe e
tick, o fechamento inclui os três casos dirigidos:
`raw_metadata_addresses`, `missing_validation_lock` e
`generation_after_lock`. Os dois últimos coordenam threads através do
mutex: validam a espera real e a alteração ocorrida antes da aquisição.
As fronteiras Vulkan, upload e proteção de páginas são controladas pelo
fixture; isso não é execução de gameplay no Android.

A revisão independente do runtime foi concluída após o guard CMask/HTile,
sem outro bloqueador material identificado. As adaptações nos três gates
anteriores apenas reconhecem `BeginRenderingFull`, a nova serial e os
contadores observacionais; os controles existentes continuam presentes.

### Ajuste da fixture de polling na integração completa

A reconstrução integrada passou os 489 contratos de API, mas o runner host
encontrou uma dependência ausente em `test_pending_poll.py`: os prefixos reais
de `DrawIndirect`, `DispatchDirect` e `DispatchIndirect` agora contêm
`OrderBarrierScope`, enquanto a fixture não declarava esse tipo nem o owner
`runtime`. A falha está preservada em
`validation/event-io-renderstate-order-host-run.log:94–101`.

O ajuste é restrito à fixture. Ela inclui o header gerado real do census,
consome os argumentos de logging numa fronteira explícita e fornece um
objeto de identidade para `&runtime`. Os prefixos de produção e todos os
asserts e mutantes de polling permanecem presentes. O gate foi executado
sobre `validation/parity-flow-order`: `BACHATA_PENDING_POLL_PASS` e os oito
controles negativos passaram. Não houve alteração de produção.

Os demais extratores foram examinados para essa mesma dependência. Os
fixtures de pool/reuse recortam seus fragmentos depois dos scopes; os de
metadados, motivos e apresentação não compilam os métodos alterados. Os
gates de memo, census, indiretos, aliases e coalescência já contêm as
dependências explícitas necessárias.

Arquivos executáveis congelados desta família:

- `port_order_render_state_memo.py` e `test_order_render_state_memo.py`.
- `port_order_barrier_census.py` e `test_order_barrier_census.py`.
- Adaptações em `test_order_render_pass_coalescing.py`,
  `test_indirect_submission_protocol.py`, `test_order_image_alias.py` e
  `test_pending_poll.py`.

O manifesto externo `analysis/order-renderstate-freeze.json` vincula os
hashes desses oito arquivos, desta nota, da captura e dos resultados locais.
O candidato integrado, o CI nativo, o APK assinado e o recibo de entrega
recebem suas próprias provas de revisão. Os resultados acima não substituem
essas etapas nem autorizam declarar equivalência completa em gameplay.
