# Order: reutilização de constantes grandes após o diagnóstico D375882C

## Evidência do aparelho

O diagnóstico D375882C registra CUSA00785 e core
`dbc91188b0058e67bcc5c9750dc202251e33e431`. O processo durou 188,230 segundos
e terminou por solicitação do usuário, com código 0. O modo recebido de
readbacks era Precise=2 e não é alterado por este grupo.

As 86 linhas `BACHATA_ORDER_READCONST_COST` somam 1.088.135 snapshots e
507.628.141.716 bytes copiados em 170,588 segundos de janelas observadas.
O tempo acumulado dentro do helper é 26,360 segundos. O campo chamado `cpu_us`
usa `steady_clock`: mede tempo decorrido dentro do helper na thread GpuDraw,
incluindo eventual espera ou desagendamento, não tempo de CPU de hardware.

| Janela observada | Snapshots | Bytes copiados | Tempo no helper / janela |
| --- | ---: | ---: | ---: |
| 12:23:02.254 UTC, linha 5279 | 26.421 | 20.784.737.236 | 1.028.605 / 2.009.758 µs, 51,18% |
| 12:23:22.292 UTC, linha 5349 | 23.947 | 12.731.922.528 | 671.474 / 2.000.712 µs, 33,56% |
| 12:23:24.294 UTC, linha 5351 | 25.734 | 14.226.542.348 | 734.120 / 2.001.470 µs, 36,68% |

Nas últimas 20 janelas, o helper copiou 241.926.089.068 bytes e acumulou
12,236 segundos em 40,074 segundos observados. Perto do pico, application.log
registra 20,02 FPS às 12:23:00.974 e 22,75 FPS às 12:23:02.974. As janelas não
coincidem exatamente; essa proximidade temporal não isola todos os custos do
frame nem explica por si só a limitação próxima de 30 FPS.

Fontes locais: `analysis/D375882C/shadps4.clean.log`, linhas 9, 21, 2639–5351;
`application.log`, linhas 147–151; `process-exit.json`. As métricas não incluem
endereços ou identidade dos recursos, portanto o log não permite quantificar
quantos bindings específicos repetiram a mesma região sem mudança.

## Diferença funcional encontrada

A comparação usa o doador Order efetivo, PC
`c53cd01d032995fe622033623ab64b4cf6b02233` com Android
`756a4f0cc603b02971d45b36354143249a4fe492`, em
`parity/sources/order-effective/gpu/shadps4`.

No doador, `CollectRingBindings` exclui `BufferType::ReadConst` do ring e só
copia os outros recursos read-only quando seu tamanho não ultrapassa
`BufferCache::STREAM_THRESHOLD`, de 16 KiB. Os recursos grandes seguem
`ObtainBuffer → SynchronizeMemory → MemoryTracker::ForEachUploadRange`.
Depois do primeiro upload, apenas páginas marcadas como alteradas pela CPU
são copiadas novamente. Fontes: `video_core/renderer_vulkan/vk_rasterizer.cpp`,
linhas 580–609 e 2629–2638; `video_core/buffer_cache/buffer_cache.h`, linha 57;
`buffer_cache.cpp`, linhas 602–634 e 934 em diante.

Na fonte Bachata anterior a este grupo, em `validation/freeze-perf-order`,
`vk_rasterizer.cpp`, linhas 1393–1399, todo recurso `used_as_readconst`, read-only
e sem dados GPU mais recentes tentava uma cópia imutável integral. O helper
aceita até 8 MiB. O pool elimina a alocação por binding, mas não elimina a cópia
repetida, mesmo quando o recurso permaneceu inalterado. Esse bypass do cache
explica um trabalho redundante concreto, reproduzível com a mesma fonte.

O flag `used_as_readconst` também aparece em recursos `BufferType::Guest`:
`resource_patching_pass.cpp`, linha 423, o marca para instruções
`ReadConstBuffer`. Isso distingue os recursos V# medidos dos buffers dinâmicos
criados por `LowerDynamicReadConstPass`; estes já seguem o caminho normal do
cache quando não têm aquele flag.

## Adaptação e alcance

`port_order_readconst_reuse.py` é aplicado depois de `port_order_readconst_pool.py`.
Somente CUSA00785 no Android muda a seleção:

- Recursos de até 16 KiB continuam usando snapshots imutáveis nos blocos held.
- Recursos maiores, alinhados a DWORD, usam o `BufferCache` existente, com o
  span completo validado. O limiar de 16 KiB decide o armazenamento; não reduz
  o tamanho que o shader pode acessar.
- Bases não alinhadas a DWORD conservam o snapshot alinhado, pois arredondar
  seu offset alteraria o endereçamento do shader.
- Dados escritos pela GPU conservam o caminho autoritativo do cache. Não são
  substituídos por uma cópia de RAM antiga.
- Recursos `Guest` marcados `used_as_readconst` passam pelo clamp estrito de
  VMA, inclusive abaixo de 1 GiB. O antigo `ClampRangeSize` tem um fast path
  permissivo nessa faixa. Não é criado um cache cego por endereço.

O grupo mantém os métodos existentes de upload, invalidação e readback. A
única adição em `SynchronizeMemory` é um contador dos bytes coletados pelo
`ForEachUploadRange`, para distinguir tamanho solicitado de tráfego real.
Esse contador é atômico e usa operações relaxed, pois a observação não detém
o lock do cache; ele não estabelece a sincronização de dados do recurso.
O limiar privado é consultado por um accessor público constexpr, inclusive
na seleção, e o teste conserva a mesma visibilidade da classe real.
Não altera FEX, política de readbacks, ISA/SPIR-V, cache de shaders ou outros
títulos.

## Coerência e lifetime

O upload existente protege as páginas e limpa seus bits CPU dirty através de
`MemoryTracker`/`RegionManager`. Uma escrita posterior invalida essas páginas;
o binding seguinte coleta novamente os ranges modificados. A janela de escrita
de 256 KiB do Order continua marcando os vizinhos limpos conforme seu contrato.
O conteúdo é lido por `CopySparseMemory` através do backing físico FEX, sem
acessar o VA guest protegido.

Escritas GPU preservam os bits GPU e os ranges exatos. O caminho de readback
publica os bytes no backing antes de permitir uma escrita CPU sobre a página.
Unmap invalida a região antes de substituir suas áreas físicas; um remap no
mesmo endereço precisa reenviar os novos dados. Nenhuma dessas mudanças pode
ser ocultada por um hit de memo.

A cópia de upload para a arena é gravada antes de retornar `ObtainBuffer`.
Assim, um Flush posterior pode concluir essa cópia e reciclar seu staging sem
afetar o binding: o consumidor lê a arena persistente. Uma nova escrita CPU
gera outra cópia ordenada, com a barreira read→write antes de sobrescrever o
mesmo range. Os snapshots pequenos e não alinhados mantêm o pin explícito,
aposentadoria no tick final e cleanup sem alocação do grupo anterior.

## Prova executável

Comando:

    python3 -B bionic/source0181/test_order_readconst_reuse.py --source EFFECTIVE_SOURCE

O gate inclui os headers reais `MemoryTracker` e `RegionManager`. Também
extrai os métodos reais `ObtainBuffer`, `SynchronizeMemory`, `InvalidateMemory`,
`ReadMemory`, `DownloadMemory`, `MarkGuestWriteWindow`, as cópias de backing,
os clamps, a seleção do binding, o pool, os watches do stream e `Runtime::CopyBuffer`.

Alocação/residência Vulkan, execução dos comandos, coleção auxiliar de ranges
GPU e alterações de proteção são fronteiras simuladas. A região VA guest da
prova é realmente reservada com PROT_NONE; os dados físicos ficam em outro
endereço. Uma mutação que lê diretamente o guest falha. O teste não executa
FEX nem mede tempo de gameplay no host.

Resultados:

- 5.000 bindings de 4 MiB sem alteração: o helper anterior copiou
  20.971.520.000 bytes; a seleção nova enviou 4.194.304 bytes uma vez.
- A mesma VA alterada antes do binding seguinte, no mesmo tick: somente uma
  página de 4.096 bytes foi reenviada. O consumidor anterior leu os bytes antigos
  e o seguinte leu os novos. A região atravessa dois RegionManagers.
- Escrita GPU, readback, escrita CPU posterior à GPU e preservação dos bytes
  vizinhos passaram com o tracker real.
- Janela CPU de 256 KiB, unmap/remap na mesma VA e clamp de regiões reservadas,
  fim de VMA e overflow passaram.
- Binding persistente sobreviveu ao Flush e à reciclagem do staging; snapshots
  pequenos permaneceram imutáveis. Outros títulos e builds sem Android
  conservaram o caminho legado.
- Oito controles negativos rejeitados: cópia a cada binding, invalidação CPU
  ausente, upload dirty omitido, clamp permissivo, snapshot GPU antigo, readback
  não publicado, barreira read→write perdida e leitura guest em vez do alias.
- Um controle de compilação adicional rejeita o acesso direto ao limiar
  privado, cobrindo o defeito de interface encontrado na revisão independente.

## Medição na próxima build

`BACHATA_ORDER_READCONST_REUSE` registra o primeiro exemplo e depois no máximo
uma linha a cada dois segundos de atividade por thread. Informa bindings,
bytes solicitados, bindings/bytes de snapshot, bindings de cache, bytes realmente
coletados para upload e tempo decorrido no binding.

`cache_upload_bytes` pode incluir páginas alinhadas maiores que o descritor e
trabalho de sincronização necessário durante aquele binding. Não se presume
reutilização apenas por repetir um endereço. O contador anterior de snapshots
permanece ativo para os recursos que ainda precisam de cópia imutável.

A correção elimina um trabalho redundante demonstrado e preserva os contratos
testados. A redução efetiva de tráfego na cena, o ganho de FPS e a estabilidade
prolongada precisam ser confirmados no aparelho; este documento não afirma
equivalência completa de gameplay.
