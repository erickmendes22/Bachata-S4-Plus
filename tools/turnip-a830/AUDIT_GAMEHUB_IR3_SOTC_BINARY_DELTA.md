# Shadow of the Colossus — GameHub 26.3 vs R11: intrínsecos IR3 (03/11/2026)

## Binários de referência (SHA256 exato)

- GameHub original: `1a109bee1ad087aceee8436479c95c4cd3e66de0778bc79fc3ce9f637f9fe404`
- GameHub DD funcional: `4f242a453496ab27fc29be950d632edbae494dcc0c9b7d56c37c7ebdffe42df9`
- Turnip Gen8 R11: `ba10389c1b22cb74eda7e094693a14d7f270d26bc92b408d3964cc5f7d68f322`

A tabela de intrínsecos NIR foi identificada em `.data.rel.ro` de cada ELF,
referenciando nomes em `.rodata`. Cada entrada tem **136 bytes**, nome
apontado pelo primeiro ponteiro e metadados de fontes/destinos/índices a seguir.
O arquivo `audit_gamehub_r11_nir_intrinsics.py` executa essa reconstrução
automaticamente e valida hashes para evitar binários trocados.

## Resultado do diff binário (NÃO apenas 'strings')

| Campo | Original | DD funcional | R11 |
| --- | ---: | ---: | ---: |
| Entradas de NIR intrinsics | 958 | 958 | 967 |
| Metadados completos equivalentes ao GameHub original | 958/958 | 958/958 | não |
| Intrínsecos GameHub ausentes na R11 | 0 | 0 | 6 |
| Intrínsecos somente R11 | 0 | 0 | 15 |
| Entradas de nome comum com outros metadados | 0 | 0 | 3 |

**Ausentes na R11:**

1. `ddx_3d_ir3` — 1 entrada, 3 componentes de fonte e 3 de destino;
2. `ddy_3d_ir3` — 1 entrada, 3 componentes de fonte e 3 de destino;
3. `load_barycentric_coord_ir3` — 1 fonte de 2 componentes e destino de 3 componentes;
4. `load_frag_coord_gmem_ir3` — nenhuma fonte, destino 4 componentes de 32 bits;
5. `load_sample_pos_from_id_ir3` — 1 fonte, destino 2 componentes de 32 bits;
6. `select_barycentric_at_center_ir3` — 3 fontes, uma de 1 componente e duas de 2, destino 2 componentes de 32 bits.

**Somente na R11:** `bindless_image_depth_input_attachment_load`,
`bindless_image_input_attachment_load`,
`bindless_image_stencil_input_attachment_load`,
`image_depth_input_attachment_load`,
`image_deref_depth_input_attachment_load`,
`image_deref_input_attachment_load`,
`image_deref_stencil_input_attachment_load`,
`image_heap_depth_input_attachment_load`,
`image_heap_input_attachment_load`,
`image_heap_stencil_input_attachment_load`,
`image_input_attachment_load`,
`image_stencil_input_attachment_load`,
`load_depth_input_attachment_coord`,
`load_draw_id_offset_ir3`,
`load_stencil_input_attachment_coord`.

**Mesmo nome com metadados diferentes:** `load_input_attachment_coord`,
`load_user_data_amd`, `rq_initialize`.

O GameHub DD tem exatamente o **mesmo conjunto e metadados** do original.
Portanto, diferenças encontradas não são consequência de mudanças opcionais
no GameHub DD; antecedem essa modificação.

## O que o ELF prova — e o que não prova

- Mostra uma evolução estrutural específica entre compiladores IR3/NIR.
- Os seis intrínsecos existem como entradas **reais de metadata compilada**,
  não simples substrings isoladas; o campo de fontes/destinos foi inspecionado.
- **Não** prova que algum shader de SotC emite essas instruções.
- **Não** comprova por si só diferença nos valores interpolados ou textura:
  a R11 pode gerar código equivalente por *lowerings* diferentes.
- Os valores numéricos do enum mudam com o conjunto ordenado, então copiar
  instruções do GameHub ou comparar constantes de switch sem identificar a
  tabela acessada produz falsos diagnósticos.

Na R11, `apply_native_barycentrics.py` transforma a coordenada IJ em
`(1-I-J, I, J)` em alto nível NIR. O GameHub possui a operação especial
`load_barycentric_coord_ir3` cujo ABI explícito aceita IJ (2) e gera
barycentrics 3D. Isso é um **candidato concreto** para comparar o código
emitido e a precisão/seleção de centro, mas a equivalência (ou diferença)
não é demonstrada sem seguir as operações no bloco de compilação.
O trio `select_barycentric_at_center_ir3`, `ddx_3d_ir3` e
`ddy_3d_ir3` reforça a necessidade de reconstruir a política de
interpolação/derivadas, antes de iniciar outra build.

## Critérios para a próxima integração

1. Recuperar o lowering IR3 **executado** no GameHub para esses seis
   intrínsecos (não basta adicionar entradas de nomes).
2. Confrontar com lowering V38 R11 para entradas reais de shader de SotC,
   inclusive fragment interpolation, early Z, FDM/GMEM e derivadas.
3. Só alterar o driver se o resultado funcional diferir.
4. Compilar o driver consolidado **apenas quando esse contrato de shader
   estiver implementado**; sem APK e sem alteração dos avisos compartilhados.

A R11 falhou visualmente na captura enviada: nenhuma declaração de
correção dos ghosts, flicker ou cores pode ser feita com este relatório.

## Extensão executável — chaves IR3 e baricêntricas (auditoria binária)

A análise avançou da estrutura de metadados NIR para o **código executável**:

- GameHub original e GameHub DD funcional comparam `ir3_shader_key` de **120 bytes** em `0xAC5CCC` (`mov w2,#0x78` antes de `memcmp`).
- R11 compara **80 bytes** em `0xA25C50` e `0xA25CD0` (`mov w2,#0x50` antes de `memcmp`).
- O driver GameHub compara **separadamente** os bytes `key[0x2A]` e `key[0x2B]` com `variant[0x42]` / `variant[0x43]` em `0xAC5CE0..0xAC5CF8` para classificar variantes mesmo quando não faz o `memcmp` completo.
- A rotina real `load_barycentric_coord_ir3`, despachada em `0xAD60CC`, chama `0xADE7C4`, que consulta precisamente `variant[0x43]`, i.e. `key[0x2B]`. Portanto, **o campo adicional de chave altera a geração de instruções**, não é mero padding.
- `0xADE7E8..0xADE7FC` separa `mode==2`, `mode==1`, demais estados. Em `mode==1` a rotina gera `(1,0,0)`; em `mode==2` gera os pesos de linha `(1 - (I+J), I+J, 0)`; em demais modos, cria 3 entradas IR3 de índices consecutivos `0x100..0x102` via `0xAE2E04`.
- Outro caminho do compilador em `0xAD70D8..0xAD70E8` usa o mesmo `variant[0x43]-1` para limitar um índice, confirmando que o valor representa uma **dimensão de componente/primtiva** relevante para IR3.
- A chave R11 pública `src/freedreno/ir3/ir3_shader.h` possui `sizeof(ir3_shader_key)==0x50` e não codifica o mesmo campo no mesmo offset (0x2B da R11 é parte de outro layout). Não se deve copiar acesso binário `key[0x2B]` diretamente.

Reprodutibilidade:
`tools/turnip-a830/recover_gamehub_ir3_dispatch_elf.py` recupera a tabela
de saltos NIR; `tools/turnip-a830/verify_gamehub_ir3_shader_key_barycentric.py`
verifica o tamanho das chaves e palavras ARM64 nos três binários pinados.

### Interpretação e limites

A equivalência de **ABI e semântica do shader** está ausente na R11 e
essa diferença é potencialmente importante para materiais iluminados de
Shadow of the Colossus. Isso não demonstra que os shaders do personagem
tenham emitido a operação, nem que a causa do verde/amarelo esteja
exatamente nessa interpolação. Uma integração correta requer:

1. Traçar quem **preenche** o campo `key[0x2B]` no GameHub e a condição de pipeline;
2. Recriar a geração das entradas IR3 nativas e a seleção de variantes no
   código V38, não somente adicionar o intrínseco ao catálogo;
3. Validar os códigos de shader gerados com entrada equivalente e apenas
   então considerar uma build, sem mudar o APK.

Sem essas três condições, a R11 continua sendo **driver funcionalmente
diferente** da GameHub; **nenhuma correção gráfica final foi demonstrada**.

## Verificação independente contra a especificação Vulkan

O capítulo [Primitive Rasterization de Vulkan-Docs](https://github.com/KhronosGroup/Vulkan-Docs/blob/main/chapters/primsrast.adoc)
define os pesos `BaryCoordKHR`: pontos `(1,0,0)`; linhas interpolam de
`(1,0,0)` para `(0,1,0)`; triângulos interpolam os pesos dos três vértices.
Isso coincide com **a interpretação de 1/2/3 vértices** dos três ramos
encontrados na função `0xADE7C4`, inclusive os pesos reconstruídos
`(1-(I+J),I+J,0)` para linha. É forte evidência semântica sobre o campo
`variant[0x43]`, ainda que não determine seu preenchimento pelo TU pipeline.

Também reconstruí o caminho que **armazena** o shader key no GameHub:
`0xAC7DB0–0xAC7E58` copia sequencialmente os 120 bytes de
`key` para `variant+0x18`. `0xAC5CE0..0xAC5CF8` compara
explicitamente os bytes `variant+0x42/0x43` com `key+0x2a/0x2b`.
O compilador `0xADE7C4` lê precisamente `variant+0x43`.
A estrutura não pode ser portável por mera cópia de offset: no layout
publicado da Mesa R11, o byte `key+0x2b` pertence ao bloco de swizzles.

### Alcance sobre o defeito observado

A transformação do Intel BRW
(`src/intel/compiler/brw/brw_nir_lower_fs_barycentrics.c`) também usa
`(1-I-J,I,J)` para triângulos, uma transformação
legítima conforme a especificação. Portanto **não basta** apontar que
o GameHub usa entradas nativas e a R11 usa cálculo NIR para afirmar
que o personagem verde é consequência: ambos podem ser numericamente
equivalentes no caso mais comum (triângulos).

Os ramos de pontos/linhas e a especialização separada do GameHub
**são diferenças reais**, mas a causalidade com as falhas visuais da
cena precisa ser demonstrada por shader de material real ou por
diferença nos valores interpolados. Nenhum patch ou APK foi gerado
a partir desta análise sem essa comprovação.

## Verificação independente local 03/11 — caminho real de shaders Vulkan

Foi extraído e desmontado o ELF do GameHub original e do GameHub DD funcional
com `llvm-objdump`. A mesma comparação foi feita com a R11 real.

O novo verificador `verify_gamehub_vulkan_shader_path.py` **passou em execução
local** usando os três binários: 11 opcodes do original + 11 do DD + 2 da R11.
Ele confirma a sequência de criação e variação de shaders Vulkan no próprio
ELF (não se limita a strings de bibliotecas embutidas):

- `0xA2317C`: compilação/criação da estrutura `ir3_shader`;
- `0xA2318C`: criação da `ir3_shader_variant` a partir da chave;
- `0xAC7E40..0xAC7E50`: cópia dos bytes da chave para a variante;
- `0xAC5CCC`: comparação de 120 bytes para busca da variante GameHub;
- `0xADE7D8`: a etapa IR3 de baricêntricas lê `variant+0x43`;
- `0xA25C50` e `0xA25CD0` R11: comparação de 80 bytes.

**Distinção essencial que evita correção falsa:** o trecho Vulkan original
`0x9E775C..0x9E776C` zera os 120 bytes da chave na pilha antes do fluxo
que eventualmente chama `0xA22588` em `0x9E77EC`. Nesse caminho
específico, `key+0x2B = 0` por padrão, ativando a rota nativa
de triângulos de `0xADE7C4`. Portanto, a diferença 120/80 por si só
não demonstra erro de triângulo/material em SotC, e **não deve virar R12**.

A origem de topologia em outras rotas de pipeline e a equivalência da
instrução final de fragment shader ainda requerem comparação específica.
A questão visual da R11 permanece aberta. **Não foi gerada uma nova build.**

## Controle adicional: versão DD não altera o compilador GameHub

O novo `audit_gamehub_original_dd_text.py` foi executado localmente com
os ELFs de SHA-256 pinado. Ambos têm a mesma seção executável
`.text` em `0x8DEBB0`, com **4.344.768 bytes**.

Foram encontrados **12 bytes diferentes em somente 7 regiões**:
`0x8E8EF0` (1), `0xA3A02A` (1), `0xA3A0C0` (4),
`0xA3B8B6` (1), `0xA3B8FE` (1), `0xA3B930` (2) e
`0xA3BAB4` (2). Todos os outros 4.344.756 bytes coincidem.
A região `0xAC5CCC–0xADEB00` (101.940 bytes), cobrindo a
comparação de variantes e o código IR3 examinado, é idêntica entre
original e DD.

Isso permite usar o GameHub **original** como alvo exato da
reconstrução IR3. **Não** implica que copiar rotinas ou flags
da seção `.text` para a R11 produza a mesma saída sem
reconstruir também seus dados, layout de estruturas e contratos NIR.

### Resultado técnico da retomada

Os verificadores locais passaram com os três ELFs:
- 11 instruções de shader creation/IR3 em cada GameHub;
- 2 instruções do comparator R11;
- 7 instruções adicionais de inicialização de chave GameHub, onde
  a chave de 120 bytes é zerada antes do caminho Vulkan verificado;
- Diff `.text` GameHub vs GameHub DD: 12 bytes diferentes.

**Nenhuma build nova foi gerada.** O defeito visual da R11 continua
sem correção comprovada. O próximo código que merece integração é
uma divergência da saída ou armazenamento do shader/material real
do SotC, não o tamanho da chave isoladamente.
