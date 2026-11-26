# Mip-tail de SotC: origem, alcance e validação

## Origem e política ativa

A referência é a árvore que o port Android de SotC efetivamente monta, com
`AjncSystem/ShadowOfTheColossus-PC` em
`732cb37d3470d2dad2cc99da19283253c96b53fc` e o staging Android em
`0366868550bde078d9ed9d88bc72d8acb1584679`. O código PC isolado não foi usado
como substituto da árvore efetiva.

No doador, `video_core/texture_cache/texture_cache.h`, função `MipTailMode`
(linha 47 nessa revisão), retorna **Mode2 por padrão**. A variável
`SOTC_MIP_TAIL` admite três políticas:

| Valor | Política |
| --- | --- |
| `0` | Não reduzir a cadeia de mips. |
| `1` | Considerar apenas T# com o contador de streaming `lod_hw_cnt_en`. |
| `2`, ou variável ausente | Considerar todos os T# de cor elegíveis, somente para leitura, com `base_level > 0`. |

A elegibilidade e o contrato completo estão nas funções do doador
`ImageDesc::InitMipTail`, `TextureCache::DecideRebase`, `SetMipTailView`,
`ImageInfo::RebaseToMip`, `MipTailCreated`, `FreeRebased` e `MarkWritten`.
`FindImageFromRange`, a busca de stencil e `RefreshImage` também participam do
contrato: a redução não consiste apenas em deslocar um endereço.

A adaptação está em [port_sotc_mip_tail.py](port_sotc_mip_tail.py). Ela habilita
essa política nos títulos `CUSA08809` e `CUSA08034`, mantém `SOTC_MIP_TAIL` como
override e conserva a cadeia completa nos demais títulos. O core continua
shadPS4 0.18.1 ARM64 Bionic com FEX.

## Caso válido que demonstra a divergência

O teste constrói um T# RGBA8 com 1024×1024 pixels, pitch 1024, uma camada,
uma amostra, `base_level=2`, `last_level=4`, `min_lod=768` e
`lod_hw_cnt_en=0`. O valor 768 representa LOD 3,0, com oito bits fracionários.
A textura é linear, somente para leitura, sem fallback de mip e sem imagens
ou escritores sobrepostos no cache.

Esse caso foi executado com os métodos reais de cálculo de layout do core e
os métodos reais de decisão/rebase/view do doador. O gate da adaptação repete
o caso usando os métodos extraídos da fonte final. A evidência permanente está
em [test_sotc_mip_tail.py](test_sotc_mip_tail.py), especialmente
`LayoutAndView`.

| Propriedade | Core antes da família | Mode2 adaptado |
| --- | ---: | ---: |
| Dimensões do nível zero do objeto | 1024×1024 | 256×256 |
| Níveis do objeto | 5 | 3 |
| Span calculado de memória convidada | 5.586.944 bytes | 344.064 bytes |
| Deslocamento a partir do endereço original | 0 | 5.242.880 bytes |
| Mip base da view | 2 | 0 |
| Níveis da view | 3 | 3 |
| `min_lod` da view | 768 | 256 |

O core anterior usa `last_level + 1` para o número de níveis do objeto.
`base_level` restringe a view, mas não reduz o objeto. Na criação de uma imagem
nova, `Image::Image` usa as dimensões e a quantidade de mips de `ImageInfo`;
`RefreshImage` usa seu `guest_address` e `guest_size` para obter o buffer de
upload. Esses consumidores estão em `src/video_core/texture_cache/image.cpp`
e `src/video_core/texture_cache/texture_cache.cpp` na fonte efetiva.

A adaptação omite os dois mips mais detalhados que essa view não acessa. Para
cada mip retido, o teste confirma igualdade de tamanho, pitch, altura e
endereço absoluto dos dados. O mip original 3 continua correspondendo ao
mesmo conteúdo após tornar-se o mip 1 do objeto reduzido. Casos com LOD
fracionário e consultas repetidas também preservam essa correspondência.

**Esse é um descritor válido construído para reproduzir uma diferença de
código. Ele não foi extraído dos diagnósticos do aparelho.** Os valores acima
são spans calculados de memória convidada e quantidades de mips solicitadas;
não são uma medição de transferência física, alocação VMA, RSS ou FPS. A
redução de 5.242.880 bytes nesse caso não permite quantificar o ganho de um
frame ou de uma sessão do jogo.

## Adaptação do contrato completo

### Layout, view e fallback

`ImageInfo::RebaseToMip` usa o `UpdateSize` da 0.18.1, preservando a seleção de
mips microtiled e a proteção contra overflow. A forma reduzida só é aceita
quando seu layout corresponde exatamente ao trecho retido da cadeia original.
O cache do cálculo usa os quatro words do T#, `is_depth` e Neo mode.

Macro tiling, alternate tiling, bank swizzle, volumes, profundidade, MSAA e
formatos com menos de oito bits por bloco não entram no rebase. Storage e
fallbacks explícitos de mip também conservam a cadeia completa. Um layout
recusado não modifica a descrição original.

A view é derivada novamente dos valores originais em cada consulta. A revisão
independente encontrou um caso em que uma primeira resolução de overlap
emprestava a layer 3 de um array de oito camadas; após a retirada desse array,
o segundo passe criava um objeto de uma camada e ainda conservava a layer 3.
A adaptação salva `orig_base_layer` e a restaura antes de cada decisão. Uma
nova resolução de overlap ainda pode selecionar outra layer válida. Os testes
cobrem o retorno às layers originais 0 e 2, além de mip e minLOD.

### Escritores, aliases e geração

`FindImage` retira as tails não modificadas que se sobrepõem a um escritor.
As consultas por range usadas por cópias/clears e a busca de stencil não
selecionam uma tail como destino de escrita. As decisões mantêm a imagem
completa quando os dados necessários estão em outra imagem modificada pela
GPU ou quando a cadeia completa continua em uso.

Na 0.18, storage é descoberto no primeiro passe de bindings, enquanto
`GpuModified` é publicado mais tarde. `MarkMipTailWriterIntent` publica essa
intenção e altera o epoch antes de um novo probe de tail. O mesmo contrato é
aplicado à preparação de targets, à reutilização de targets preparados e à
propagação de target durante a resolução de overlaps.

`MarkMipTailGpuModified` também altera o epoch na primeira escrita efetiva,
incluindo cópias, resolves e clears que podem ocorrer fora de um lookup de
escritor. Memos de tails e de escritores conferem o epoch de escrita e a
geração global de aliases. Isso cobre mudanças em outra base de endereço que
não alteram a geração por endereço usada pelo memo comum. Permanecem as
validações de UID, slot alocado, registro vivo, recursos e `needs_rebind`.

Uma escrita inesperada em uma tail é diagnosticada por
`BACHATA_MIP_TAIL_WRITE`. Seus dados passam a ser tratados como modificados
pela GPU; a tail não é descartada como uma cópia somente de leitura.

### Tempo de vida e atualização dos dados

A retirada usa `FreeImage`: tracking e registro são removidos imediatamente;
backing, views e slot seguem a destruição deferida do scheduler. Uma tail que
ainda participa dos bindings recebe `needs_rebind`. `TouchImage` verifica
`Registered` antes de tocar a LRU, pois o segundo passe pode consultar o slot
antigo apenas para observar `needs_rebind`, depois que seu nó LRU já foi
liberado ou reutilizado.

Tails antigas da mesma cadeia só são retiradas pela deduplicação quando estão
ociosas, não vinculadas e sem dados modificados pela GPU. Escritas de buffer
na base da cadeia invalidam a tail correspondente; DMA mantém a invalidação
de overlaps já existente.

`MaybeCpuDirty` em uma tail provoca reupload. Uma escrita em outro mip pode
deixar inalterados os primeiros texels, portanto o hash do prefixo 8×8 não é
usado para descartar essa atualização. O caminho de imagens completas conserva
sua política anterior.

## Integração e validação local

Aplicar `port_sotc_mip_tail.apply(source)` depois de
`port_sotc_texture_find_memo` e antes de `port_texture_view_memo`. O último
atalho de view continua usando `ImageViewInfo` completo, incluindo layer, mip
e minLOD. Esta família não modifica SPIR-V nem a ABI serializada de shaders
ou PSOs.

```sh
python3 -B bionic/source0181/test_sotc_mip_tail.py --source CAMINHO_DO_CORE
python3 -B bionic/source0181/test_sotc_texture_find_memo.py --source CAMINHO_DO_CORE
python3 -B bionic/source0181/assert_native_api.py --source CAMINHO_DO_CORE
```

O gate de mip-tail compila os campos reais de T#, tabelas de tiling, métodos
de `ImageInfo`, métodos de lookup/registro, `SlotVector`, LRU e métodos da
família extraídos da fonte efetiva. Construção Vulkan, conversão de formato,
resolução de overlaps e submissão de comandos são fronteiras de fixture;
o teste não executa uma GPU. A decisão de `MaybeCpuDirty` usa o trecho real
de `RefreshImage`.

Resultados locais antes da reconstrução final:

- 2.160 combinações de layout aceitas, com comparação dos mips retidos,
  além dos casos deliberadamente recusados: **PASS**.
- View, LOD, cache de T#, re-find de layers, escritor pendente, escrita de GPU
  sem troca de registro, aliases, range, retirada deferida, LRU e CPU dirty:
  **PASS**.
- Mode0, Mode1 e política para outro título: **PASS**.
- Nove controles negativos do gate de mip-tail compilam e falham nas
  assertions esperadas: LOD, layer de re-find, epoch de intenção, epoch de
  escrita, validação do epoch pelo memo, geração de aliases, LRU retirada,
  CPU dirty e exclusão de tails da busca por range.
- Gate do memo existente adaptado às interfaces finais: **PASS**, incluindo
  seus nove controles negativos.
- `assert_native_api`: **PASS**, 301 contratos, com o marcador da cópia
  sincronizado ao HEAD real usado para aquela validação.
- Revisão independente: o caso de layer foi reproduzido antes da correção e
  passou depois; nenhum outro bloqueador foi identificado no grupo fechado.

Esses resultados demonstram os contratos exercitados em host. Não identificam
esta divergência como causa exclusiva do congelamento observado em SotC e não
comprovam aumento de FPS ou estabilidade no aparelho. A reconstrução final,
compilação nativa, empacotamento e validação de gameplay permanecem etapas
distintas da prova descrita aqui.
