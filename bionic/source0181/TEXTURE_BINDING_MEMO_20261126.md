# The Order: família ativa de memoização de texturas

## Fonte e escopo

Adaptação da árvore que efetivamente compila no port Android, composta pelo
port PC `c53cd01d032995fe622033623ab64b4cf6b02233` e pelos arquivos substituídos
do Android `756a4f0cc603b02971d45b36354143249a4fe492`. As referências abaixo
ficam sob `gpu/shadps4/video_core/` na árvore efetiva do Order.

O PC define `runtime_disabled_optimizations` sem inicializador em
`src/runtime_memory.c`; o valor inicial é zero. A montagem Android não substitui
esse arquivo. Em `gpu/shim/ps4_toggles.h`, `ImageDescCache=32` e
`TextureBindingMemo=1024` estão, portanto, habilitados por padrão. O arquivo de
toggles só passa a alterar a máscara se `ORDER1886_TOGGLE_FILE` for configurado.

| Caminho ativo do doador | Adaptação no core Bionic/FEX |
| --- | --- |
| `Rasterizer::CachedImageDescEntry`, 4096 entradas e chave T# completa | Cache associativo de duas vias com T# completo e os três flags usados pelo construtor 0.18; descritores retornados por valor |
| `Rasterizer::BindTextures`, memo de `FindImage` | Reutilização para T# escalar e arrays; consulta real quando há override de mip; o descritor resolvido é copiado para a binding |
| `Rasterizer::FindTargetMemoized`, usado por `PrepareRenderState` | CB/DB com todos os argumentos dos construtores na chave, 64 entradas e último resultado por attachment |
| `BufferCache::SynchronizeMemoryFromImage`, cache de misses | Cache negativo apenas para ausência estrutural comprovada na tabela de imagens |
| `TextureCache::RegisterImage` / `UnregisterImage` | Geração global e validação de slot, UID, registro e `needs_rebind` antes da reutilização |

`TextureSetMemo` é outra família: seu consumidor exige `PreparedStage`; no
Android efetivo, os workers de `DrawPreparation` ficam desligados por padrão.
Este grupo não introduz workers, replay de estágios ou ponteiros para estruturas
preparadas. O memo interno SotC tem outro overlay e outra política de título.

## Contratos preservados

A política se aplica somente a `CUSA00785`. `BACHATA_ORDER_TEXTURE_MEMO=0`
desliga o grupo. Apenas a configuração de ambiente é estática; o serial é
verificado a cada consulta, inclusive se o processo for reutilizado entre jogos.
O cache de descritores é alocado somente quando o grupo é usado.

Um hit atualiza `tick_accessed_last` e a posição no LRU sob o mutex da textura.
`UnregisterImage` invalida a geração antes da destruição diferida do slot; o UID
impede reutilização de um slot reciclado. Um lookup que registra, mescla ou
aposenta imagens não grava um resultado com a geração anterior.

Os consumidores mantêm as verificações de formato, endereço, tamanho e
footprint anteriores ao lookup. Também mantêm `GetAssociatedDepth`, flags de
binding, segundo passe de `needs_rebind`, `FindTexture`, uploads de imagens
dirty, metadata de storage, views e transições. O cache armazena IDs e
descritores por valor; não armazena `VkImageView` ou ponteiros para descritores
de outro draw.

O cache negativo é deliberadamente mais restrito que o doador. Um resultado
nulo de `FindImageFromRange` também pode significar imagem existente que ainda
não satisfaz `SafeToDownload`, ou candidatos ambíguos. A elegibilidade pode mudar
sem `RegisterImage`/`UnregisterImage`. Apenas a inexistência de imagem com o
endereço base permite memorizar o miss; os demais resultados nulos repetem a
consulta real. CMask e HTile permanecem antes dessa consulta.

## Integração e verificação

Aplicar depois dos overlays de indiretos e patch groups, antes do fechamento
final da árvore:

```sh
python3 -B bionic/source0181/port_texture_binding_memo.py CAMINHO_DO_CORE
python3 -B bionic/source0181/test_texture_binding_memo.py CAMINHO_DO_CORE
```

O caminho contém `src/`. O overlay confere todas as âncoras e a ausência de
alterações concorrentes antes de escrever os seis arquivos. A mudança é apenas
de caches de execução; não altera o formato serializado de shader, metadata ou
PSO.

O teste extrai e compila métodos reais da árvore resultante com stubs de Vulkan
e armazenamento. Exercita chave completa, colisões/substituições, vida útil de
descritores por valor, geração durante lookup, aposentadoria diferida, reciclagem
de UID, rebind, tick/LRU, efeitos de `FindTexture`, CB/DB e misses cuja
elegibilidade muda sem alteração estrutural. Também executa o caminho de outro
jogo, o override desligado e alternância de títulos no mesmo processo.

Resultado local: `TEXTURE_BINDING_MEMO_REAL_METHODS_PASS` e os dois processos
`TEXTURE_MEMO_DISABLED_POLICY_PASS`. Revisão independente dos consumidores e
ownership concluída sem bloqueador. Esses testes confirmam os contratos
exercitados; compilação nativa e gameplay seguem como validações distintas. Não
há medição de ganho de FPS deste grupo nem atribuição causal ao crash anterior.
