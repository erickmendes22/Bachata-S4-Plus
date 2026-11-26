# Comparação funcional: I/O, imagens compartilhadas e apresentação

## O que esta revisão entrega

Esta revisão adapta três famílias funcionais ausentes ou incompletas no
Bachata e integra o protocolo de apresentação AHB usado pelas referências.
Ela mantém shadPS4 ARM64 Bionic + FEX nos dois cores, o frontend original,
JNI, SAF, saves e controles. Não incorpora executável, launcher, runtime
completo ou backend AOT dos ports.

O resultado demonstrado é a correção dos contratos exercitados no código,
com fontes efetivas comparadas e reproduções que falham sem as correções.
Não há execução desta revisão no telefone durante a preparação do APK.
Boot completo do inFAMOUS, estabilidade do Colossus e 50–60 FPS na cena do
Order continuam sendo resultados a confirmar em gameplay.

## Diagnósticos que fundamentam a mudança

As três capturas pertencem à build anterior. Foram conferidos CRC, tamanhos
e SHA-256 das entradas contra seus manifests. O marcador nativo
`BACHATA_CORE_REVISION` identifica os cores efetivamente executados; o campo
`runtimeRevision` herdado do frontend não substitui essa identificação.

| Captura | Core nativo observado | Constatação |
| --- | --- | --- |
| `BS4-20261126-28BD3630`, CUSA08809 | `4979bd728764ee1dceb42f92c74d70fcd470e7f9` | Primeiro present em 18,332241 s; nenhuma amostra positiva de FPS; LOD anterior ativo; freeze relatado pelo usuário |
| `BS4-20261126-81209BF6`, CUSA00004 | `ea646fe37584534209ad5f64d2a21f75b7c18a90` | Nenhum primeiro frame; FIOS original carregado, mas funções HLE provisórias continuam resolvendo o I/O |
| `BS4-20261126-53A4D3EC`, CUSA00785 01.02 | `ea646fe37584534209ad5f64d2a21f75b7c18a90` | 69 amostras positivas entre 26,32 e 62,01 FPS; patch de 60 FPS verificado; apresentação WSI de 2688×1216, cinco imagens, sem tentativa AHB |

As capturas terminam por parada solicitada pelo usuário, com código zero.
Isso não invalida os travamentos relatados; somente impede interpretar esses
três encerramentos como um crash registrado nesta amostra.

### O que já estava ativo e não resolveu

No Order, `patch60_verified=true`, `guest_rate=0` e limite de apresentação
60 aparecem no log. A amostra ultrapassa 30 FPS. Portanto, ela não sustenta
um limitador fixo de 30 nem mostra o patch sendo desligado durante a sessão.
O catálogo 1.02 e sua verificação por preimagem permanecem preservados.

O log também confirma a coalescência de passes anterior: 361.899 begins,
848.677 decisões iguais e 22.703 coalescências após clear nas 27 janelas de
GpuDraw. Zero inline clears também aparece nas duas referências do port;
esse zero isolado não prova uma diferença ativa.

O helper instrumentado de ReadConst soma 825.738 µs em 138.489.423 µs de
janelas, aproximadamente 0,596%. Esse valor é duração dentro do helper,
não tempo total de CPU/GPU. Não justifica atribuir a ele toda a diferença
de desempenho restante.

No Colossus, o pool real foi encontrado em `0x200a30140`, com 75.760 páginas,
três livres, 0% e mip 4. A correção LOD anterior estava ativa. Não há stack
de fence bloqueada nem `BACHATA_GPU_WAIT` nessa captura, portanto a nova
correção não é apresentada como causalidade única provada do freeze.

No inFAMOUS, os 112 callbacks já usam evento 1 e erro 0. Corrigir novamente
esse ABI não explicaria o boot restante; a divergência está na escolha de
implementação após carregar `libSceFios2.prx`.

## 1. I/O original do jogo e resolução tardia de imports

As referências de inFAMOUS registram a biblioteca FIOS original e permitem
que seus exports resolvam as operações. O Bachata mantinha símbolos HLE
fortes que continuavam vencendo mesmo com a biblioteca original carregada.
O fallback cria aliases de montagem, mas não implementa a leitura completa
dos arquivos PSARC solicitados pelo jogo.

`port_shared_io_fios_exports.py` mantém o fallback utilizável e dá prioridade
a um export compatível da biblioteca FIOS original. Um import atendido
provisoriamente pelo HLE recebe seu endereço, mas não é marcado como
relocação definitivamente resolvida. Quando o módulo chega,
`RelocateAnyImports` pode vinculá-lo à implementação original antes de seu
Start. O override explícito `.use-hle` continua respeitado.

A política é por resolver e restrita à FIOS; não troca a prioridade de
outras bibliotecas. Módulos ausentes continuam contando com fallback.
Loader, leitura por SAF e execução x86 por FEX permanecem os mesmos.
Isso corrige a divergência de I/O identificada, sem afirmar boot completo
ou compatibilidade de todos os jogos sem execução no aparelho.

O gate executa o resolver e o fluxo de relocação reais, incluindo chegada
tardia, ausência de módulo, override, namespaces e política desktop:
14 casos FEX, seis desktop e sete controles negativos de runtime.

## 2. Coerência de imagens e consumidores do Order

As fontes efetivas do Order e seus logs de referência usam cópias entre
imagens distintas que compartilham a mesma memória guest. A reprodução
do lookup real com imagens RGBA16F de 1280×736 e 1280×720 cria dois backings.
Sem o protocolo, escrever `17` no maior deixa `0` no menor; a correção
transmite o valor escrito. Essa é uma falha funcional reproduzida, não uma
medição de ganho de FPS.

`port_order_image_alias.py` mantém autoridade e gerações por grupo, identifica
imagens por ID e UID, publica escritas em render targets/storage e sincroniza
o consumidor com cópias GPU–GPU. A compatibilidade de layout é exigida nas
duas direções. Uma escrita parcial é combinada com a região intacta antes
de promover outro backing ou servir um download.

O grupo cobre registro de terceiro tamanho, inicialização da cauda que ainda
vem da CPU, invalidação CPU/GPU/hash, UID reciclado, download/GC e retirada
parcial. O unmap preserva sobreviventes no owner GPU e retira as imagens sob
a mesma exclusão que protege a decisão; a espera externa não segura o mutex
de textura. O unmap total não faz cópias de sobreviventes. Recursos gravados
na fila conservam sua vida útil até o tick apropriado.

Downloads consultam a autoridade antes dos filtros de elegibilidade. Só
imagens de grupos efetivamente marcados como alias exigem writeback síncrono;
as demais conservam a política anterior. A publicação de writeback só ocorre
se `TryWriteBacking` tiver sucesso. O gate adicional do consumidor executa
`DownloadImageMemory` real em sete casos e rejeita quatro controles negativos.

Foi removida também uma segunda sincronização redundante de imagem em texel
buffers somente no Order. O modo de readback recebido do frontend permanece
inalterado. Não foi removida uma barreira ou espera sem demonstrar a
dependência correspondente.

Os motivos de encerramento de passes agora distinguem cópia, upload,
download, alias, barreira, dispatch, submissão e apresentação, entre outros.
A contagem ocorre somente quando um passe aberto realmente fecha, separada
por scheduler e thread, sem consulta de relógio em cada draw. Ela responde
à pergunta ainda aberta sobre quem impede a reutilização dos passes.

## 3. Progresso da apresentação, fechamento e FPS

O código anterior permitia que CP/GpuDraw aguardassem um frame ou fence cuja
liberação dependia de comandos que esses mesmos produtores ainda tinham de
executar. Também fazia `Present` na thread responsável pelo vblank.

O protocolo adaptado permite poll de pool/fence nos dois produtores e retoma
a cabeça pendente em callback ordenado, sem loop de retry dentro do callback.
A posição FIFO, atributos, endereço, HDR e geração da porta são fixados na
aceitação. Existe no máximo um preparo pendente, e um flip posterior não
ultrapassa o anterior.

Um worker único executa apresentação, HDR e redraws, enquanto vblank continua
avançando. Um idle blank que já estava enfileirado também faz poll, evitando
que ocupe o único worker esperando um frame de um flip posterior.

`Close` incrementa a geração e retira requests pendentes. A geração é
verificada antes e depois de `Present`; trabalho antigo não publica labels,
eventos ou contadores na porta reaberta. Frames cancelados aguardam a
publicação real do recorder e a timeline antes de voltar ao pool. Callbacks
têm token de vida próprio, e o encerramento drena o worker com stop/predicado
sincronizados.

`Presenter::Present` retorna o resultado efetivo. O contador do frontend só
recebe uma apresentação de jogo concluída, da geração vigente. Tentativa
falha, retry, cancelamento e idle não contam como frames novos.

A política de progresso é Android + FEX para CUSA00785, CUSA08809 e CUSA08034.
Os demais títulos conservam seu fluxo anterior. O resumo independente
`BACHATA_GPU_WAIT phase=present_progress` distingue requests aceitos,
preparados e apresentados, pool vazio, fence pendente e worker ocupado.

O gate real dos dois cores cobre CP/Draw, FIFO, vblank durante Present,
idle previamente enfileirado, quatro janelas de Close/reopen, retry antigo,
callbacks ativos e teardown; rejeita 17 controles negativos. A composição
preserva os oito negativos anteriores do grafo CP do SotC e os 11 do pacing
do Order. Os FPS sintéticos desses testes não são FPS medidos nos jogos.

## 4. AHB: ativação, commit e liberação

A captura do Order não contém tentativa AHB porque a política exigia uma
variável de ambiente ausente na execução normal. A ausência de tentativa
não demonstrava falta de capacidade do driver.

O adaptador agora ativa AHB automaticamente para os mesmos três seriais,
quando formato SDR/RGBA, transformação, memória externa e SYNC_FD permitem.
Não amplia essa seleção para inFAMOUS. `BACHATA_AHB_PRESENT=0` continua
desativando o caminho. O buffer usa a dimensão do frame e é ajustado à
janela com proporção preservada.

FIFO avança pelo callback de commit, separado da conclusão que devolve o
fence do buffer anterior. Os callbacks só alteram seu estado compartilhado;
não aplicam transações nem esperam pela GPU. O estado é publicado antes de
`apply`, inclusive para callback antecipado. Sessões retiradas não acessam
o objeto destruído.

Commit, slot disponível e fallback de importação compartilham um prazo
limitado. A aquisição ocorre fora do mutex global de submissão. Erros
mantêm o fallback WSI existente e registram a etapa e o motivo em
`BACHATA_AHB_SELECTION`/`BACHATA_AHB_FALLBACK`.

O gate compila a classe AHB e os braços reais da swapchain, cobre propriedade
de FDs, callbacks antecipados/atrasados, retirada, falhas de criação em cada
slot e 400 geometrias. Onze controles negativos são rejeitados em runtime.
Esse teste não substitui scanout nem desempenho real do Android.

## Referências e rastreabilidade

As notas de cada grupo registram fontes, chamadas, testes e limites:

- `SHARED_IO_FIOS_EXPORTS_20261126.md`;
- `ORDER_IMAGE_ALIAS_AND_PASS_ENDS_20261126.md` no core Order;
- `DIAGNOSTIC_20261126_SOTC28_PRESENT_PROGRESS.md`;
- `AHB_PRESENT_PROTOCOL_20261126.md`.

Order efetivo: port PC `c53cd01d032995fe622033623ab64b4cf6b02233` e montagem
Android `756a4f0cc603b02971d45b36354143249a4fe492`. SotC efetivo: port PC
`732cb37d3470d2dad2cc99da19283253c96b53fc` e montagem Android
`0366868550bde078d9ed9d88bc72d8acb1584679`. A referência inFAMOUS
`9542810428dca8f29695ce23610479c88389e4ed` foi conferida contra sua base local,
separando exportação de bibliotecas das diferenças opcionais de backend AOT.

Todos os grupos são aplicados à árvore depois dos overlays existentes; os
gates obrigatórios usam essa árvore final. Build Android, proveniência dos
dois ELF, revisão embutida, assinatura original, alinhamento do APK e catálogo
de patches são verificações separadas, registradas no recibo da entrega.

Equivalência funcional completa exige comparação em gameplay com o mesmo
driver, resolução, patches, cena e cache frio/quente. Não é inferida da
quantidade de patches, de símbolos presentes ou de uma compilação aprovada.
