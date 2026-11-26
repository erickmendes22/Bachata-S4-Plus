# Reutilização de views: Order e SotC

## Diferença efetiva

O core 0.18 já mantém uma lista de `VkImageView` por backing e reutiliza a view
correspondente. A diferença encontrada é a busca repetida nessa lista, não a
criação repetida de objetos Vulkan.

As árvores Android efetivas do Order (PC `c53cd01` + Android `756a4f0`) e SotC
(PC `732cb37d3470` + Android `0366868550`) têm um atalho `last_view` em
`Image::FindView`. O SotC habilita esse caminho quando `SOTC_TEX_BIND_P1` não é
definido como zero. No Order, `TextureCache::FindTexture` também aceita um
`ViewMemo` por descritor; `Rasterizer::BindTextures` usa esse memo no caminho
normal de bindings, sem depender dos workers de `DrawPreparation`.

A fixture compilou os métodos `FindView` dos doadores e do core 0.18. Em 4096
bindings consecutivos da última view de uma lista, observou:

| Views na lista | Comparações no 0.18 | Comparações com `last_view` dos doadores |
| --- | ---: | ---: |
| 1 | 4096 | 4096 |
| 4 | 16384 | 4096 |
| 16 | 65536 | 4096 |
| 64 | 262144 | 4096 |

Nenhum desses casos criou novas views durante o trecho medido. Outra fixture,
com `FindTexture` real do doador Order, alternou duas views entre 64: o memo por
descritor evitou a busca, mantendo os 4096 refreshes e 4096 writes de metadata
de storage. São contagens de operações em host, não uma medição de FPS Android.

## Adaptação completa

`port_texture_view_memo.py` aplica `last_view` aos dois cores. O índice pertence
ao backing e só é consultado depois da conversão de samples necessária ao guest.
A chave continua sendo `ImageViewInfo` completo: tipo, formato, mip, camada,
extent, swizzle, minLOD e indicação de storage. No SotC, isso preserva os valores
resolvidos pela família de mip tails.

No Order, o overlay acrescenta o memo por descritor sem emprestar um descritor
do cache para o draw. Cada entrada do cache de descritores recebe uma identidade
que muda na substituição. O primeiro passe registra um token de índice e
identidade; o segundo passe só o aceita enquanto essa identidade continuar
atual. Rebind descarta o token, e overrides de mip continuam no caminho normal.

O memo é copiado para uma variável local antes de `FindTexture`. Depois de
refreshes e possíveis callbacks, o token é verificado outra vez antes de gravar
o resultado no cache. Assim, uma colisão entre passes ou durante um callback não
grava estado no slot de outro descritor.

A reutilização da view verifica `ImageId`, UID da imagem, registro vivo,
`needs_rebind`, ponteiro e UID próprio do backing, `ImageViewInfo`, alocação do
slot da view e UID próprio da view. Os UIDs de backing e view são gerados por
`IncrementalIdProvider`, incluindo reconstrução no mesmo endereço e reciclagem
de slot. A validação ocorre sob o mutex de texturas; não estende o tempo de vida
de imagens ou views aposentadas. O novo memo compara o descriptor completo uma
vez por hit, em troca de não depender dos ponteiros emprestados do doador.

Os efeitos anteriores a `FindView` permanecem: escrita de metadata de storage,
`GpuModified`, participação em readback, `UpdateImage`, tracking e refresh. Os
callers ainda executam o segundo passe, transições e escrita dos descriptors
Vulkan. O memo só evita a busca da view.

O escopo permanece nos títulos `CUSA00785`, `CUSA08809` e `CUSA08034`.
`BACHATA_ORDER_TEXTURE_VIEW_MEMO=0` desliga o grupo de views do Order;
`SOTC_TEX_BIND_P1=0` desliga `last_view` do SotC. O memo por descritor do Order
também depende do cache de bindings anterior estar habilitado. A política
reavalia o serial se o processo mudar de jogo.

## Integração e gates

Aplicar depois de `port_texture_binding_memo` no Order. No SotC, aplicar depois
de `port_sotc_texture_find_memo` e `port_sotc_mip_tail`. Ambos ficam antes do
fechamento final da árvore e do marcador de revisão:

```sh
python3 -B bionic/source0181/port_texture_view_memo.py --source CAMINHO_DO_CORE
python3 -B bionic/source0181/test_texture_view_memo.py --source CAMINHO_DO_CORE
```

O overlay identifica explicitamente o grupo Order ou SotC pelo marker da família
de lookup já aplicada; exige exatamente um deles. A extensão por descritor só é
aplicada no Order. Não muda ABI serializada de shader ou PSO.

O gate compila métodos reais, `ImageViewInfo`, membros de backing/view,
`IncrementalIdProvider`, `SlotVector`, registro, retirement e tokens. Testa
conversão MSAA, criação/reutilização correta de views, todos os campos da chave,
backing reconstruído no mesmo endereço, slot de view reciclado, registro
removido antes da destruição diferida, colisão real no cache e substituição
durante refresh. Sete controles negativos no Order e dois no SotC precisam
compilar e falhar em runtime. As execuções usam UBSan.

Resultados locais: os dois cores e políticas de título/override passaram; os
controles negativos foram rejeitados. A única fixture anterior adaptada é
`test_texture_binding_memo.py` do Order, que aceita o parâmetro opcional de
`FindTexture` enquanto continua passando `nullptr`. Seus stubs dos métodos de
views abortam se chamados: os contratos do novo caminho são exercitados pelo
gate específico, não simulados pelo gate antigo.

Compilação nativa e estabilidade em gameplay continuam sendo validações
distintas. Este grupo não é apresentado como causa ou solução comprovada do
crash observado no aparelho.
