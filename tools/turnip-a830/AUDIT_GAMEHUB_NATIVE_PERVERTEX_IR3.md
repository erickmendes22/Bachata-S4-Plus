# Correção funcional IR3 GameHub A830: PerVertexKHR via OPC_LDLV

## Evidência confirmada no GameHub que renderiza SotC corretamente

Binários de controle:
- GameHub original: SHA-256 `1a109bee1ad087aceee8436479c95c4cd3e66de0778bc79fc3ce9f637f9fe404`
- GameHub DD funcional: SHA-256 `4f242a453496ab27fc29be950d632edbae494dcc0c9b7d56c37c7ebdffe42df9`
- Turnip R11 defeituosa: SHA-256 `ba10389c1b22cb74eda7e094693a14d7f270d26bc92b408d3964cc5f7d68f322`

O original e o DD contêm as **mesmas instruções ARM64**:
`0xAD71C8` e `0xAD7354` emitem a operação IR3 `0x31F`.
Na ISA Mesa pinada `src/freedreno/ir3/instr-a3xx.h`, esta é
`OPC_LDLV = _OPC(6,31)`. A instrução carrega diretamente um valor
de entrada por vértice, sem invocar a interpolação `OPC_BARY_F`.

A R11, por sua vez, em
`tools/turnip-a830/apply_native_barycentrics.py`,
convertia **todas** as instruções NIR `load_input_vertex` de fragment shader
em `load_interpolated_input` com `IJ` artificial
`(0,0)`, `(1,0)` ou `(0,1)`. Isso força a geração de
`OPC_BARY_F`, perdendo a semântica de um acesso `PerVertexKHR` direto.
Essa diferença é substancial e não é só mudança de nomenclatura.

## Caminho REAL do jogo — sem modificar o APK

No código `gpu/shadps4/shader_recompiler/backend/spirv/spirv_emit_context.cpp`
da base `AjncSystem/ShadowOfTheColossus-PC`, o recompilador declara um
`Input` array de três vértices e o decora com
`spv::Decoration::PerVertexKHR` quando o shader pede
`Qualifier::PerVertex` e
`profile.supports_fragment_shader_barycentric` é verdadeiro.

Nos logs comparados:
- GameHub funcional 08:55: `KHR=1 AMD=0 GS_fallback=0`;
- R11 com cor fluorescente 13:50: `KHR=1 AMD=0 GS_fallback=0`.

Logo, **o fluxo do game realmente pode emitir os acessos** cujo
lowering foi corrigido. Isso não demonstra que o shader do personagem
que ficou amarelo/verde usa esse atributo. É necessário comparar um shader
real ou sua imagem para confirmar a causa.

## Integração realizada no driver

Na branch `fix/a830-native-ldlv-pervertex-sotc-20261103`:
1. Foi removido o caso `load_input_vertex` que fabricava `IJ` em NIR.
2. O `ir3_compiler_nir.c` recebe a operação NIR nativa e cria
`OPC_LDLV` para cada componente, mantendo `OPC_BARY_F` somente
em inputs realmente interpolados.
3. A implementação é protegida por verificação de geração >= A8xx,
de estágio fragmento e pela disposição das fontes NIR.
4. `pack_inlocs` do Mesa já reconhece `OPC_LDLV` como entrada e
atualiza seus offsets normalmente.

CI source-only:
[GitHub Actions #41701156557](https://github.com/erickmendes22/Bachata-S4-Plus/actions/runs/41701156557) — aprovado;
confere aplicação à fonte pinada, ISA e reconhecimento no input packer.
Execução interna de compilação nativa:
[GitHub Actions #41701283063](https://github.com/erickmendes22/Bachata-S4-Plus/actions/runs/41701283063).

## Divergência ainda pendente

O GameHub limita o índice aos vértices válidos (nos dados de variante):
`0xAD70CC` e `0xAD70D4` tratam índices de largura distinta;
`0xAD70DC` lê a contagem em `variant+0x43`,
`0xAD70E0..0xAD70E8` calculam
`min(index, primitive_vertices - 1)`.
Essas **oito instruções** foram verificadas em ambos os GameHub funcionais
pelo `verify_gamehub_native_ldlv_elf.py` — teste local aprovado.

A R11 tem chave de shader com outro layout, e ainda não foi reconstruído
**quem preenche** esse campo em todas as rotas de pipeline
(inclusive topologia dinâmica). Não é correto hardcodar todos os draws
como triângulos nem copiar um offset binário de 120 bytes para uma
estrutura C de 80 bytes. Os acessos de triângulos válidos passam sem essa
recuperação; pontos/linhas exigem cuidado adicional.

A compilação AArch64 e a verificação em hardware da mudança nativa
ainda não demonstraram a eliminação de ghosts, flicker e cores incorretas.
**Não apresentar a integração como correção visual garantida.**

## Fechamento da seleção do índice na rota Vulkan do GameHub

O fluxo `0x9E775C–0x9E776C` zera a chave nativa de 120 bytes.
A chamada `0x9E77B8` recebe a chave em `x3`, mas o trecho
`0xA216B0–0xA21BC0` não grava no campo `key[0x2B]`
nessa rota (o campo chega com valor 0).

A etapa IR3 lê esse campo em `0xAD70DC`, subtrai 1 em registro
de **32 bits** em `0xAD70E0`, e usa `csel ... lo` em
`0xAD70E8`. Para `mode=0`, a subtração unsigned produz
`0xffffffff`: todo índice de vértice válido permanece inalterado.

O comportamento do patch `create_frag_input_vertex`, que passa
diretamente o índice NIR para `OPC_LDLV`, corresponde a **essa
rota Vulkan com modo 0**. Isso resolve a incerteza sobre precisar
hardcodar número 3 de triângulo para a compilação observada. As
variantes que trazem `mode=1`, `2` ou `3` são alternativas
e não devem ser reproduzidas alterando todo fragment shader Vulkan.

O verificador `verify_gamehub_native_ldlv_elf.py` agora testa
a subtração unsigned, as entradas do modo 0 e os limites dos
modos 1/2/3 além das oito instruções ARM64 do GameHub original
e do DD funcional.

**Validação do executável Turnip experimental:**
CI [#41701283063](https://github.com/erickmendes22/Bachata-S4-Plus/actions/runs/41701283063)
aprovou compilação Android AArch64, integridade do ELF e ZIP.
O novo ELF é `d694fefbc49b161af3d22cfb50569a0cfcbbfb9eefdbdea359c1055b5db7a28c`
com 13.595.168 bytes. Contagem das instruções ARM64
`mov w1,#0x31f`: R11=1, com backport=2,
GameHub original=4 (duas dessas quatro estão em outros caminhos);
a diferença de contagem não é métrica de correção visual.
