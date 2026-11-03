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
