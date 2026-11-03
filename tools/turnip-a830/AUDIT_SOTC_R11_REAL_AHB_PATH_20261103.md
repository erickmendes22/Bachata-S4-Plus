# SotC R11 sem melhoria — auditoria diferencial e fluxo AHB (03/11/2026)

## Regressão visual confirmada, NÃO corrigida

Captura do usuário de `2026-11-03 13:50` mostra personagem amarelo/verde fluorescente, bordas distorcidas/arrastadas e renderização irregular. O log `ShadowOfTheColossus-Logs-20261103-135010.zip` carrega corretamente `Turnip_GameHub_A830_R11_Instalavel.zip`, SHA256 ZIP `4c30251a0fdecfce533b863520dd8b811ef7ec775d138adcbf1a88eb5abbd80b`.

R11 tem `IT_SET_PREDICATION=1`, `not fully GPU mapped=8`; GameHub funcional tinha exatamente esses mesmos avisos. Eles não discriminam defeito da Turnip, não serão tratados como causa.

Dois `InvalidFileFourCC` (ruins_*_nml.chunk2.ctxc) ocorrem no carregador de recursos do **jogo**, não no `u_gralloc` ou `drm_fourcc` do Vulkan; mesmo texto FourCC não implica a mesma falha. O log GameHub não contém os mesmos erros, mas é outra sessão e não prova causalidade de driver.

## Descoberta crítica: swapchain real é AHB importado, NÃO VK_ANDROID_native_buffer

O renderer SotC é montado pelo próprio `ports/sotc/android/wire_ahb.py`, substituindo `vk_swapchain.cpp` de PC por:
`gpu/shadps4/video_core/renderer_vulkan/vk_swapchain_ahb.cpp`
em `erickmendes22/gow3_android_daedalus_fork`, branch `fix/sotc-simple-stable-036`.
O `CreateBuffer` cria três AHardwareBuffers RGBA8888 com
`AHARDWAREBUFFER_USAGE_GPU_COLOR_OUTPUT | GPU_SAMPLED_IMAGE | COMPOSER_OVERLAY`
e chama:
1. `vkGetAndroidHardwareBufferPropertiesANDROID`;
2. `vkCreateImage` com `VkExternalMemoryImageCreateInfo` AHB e `VK_IMAGE_TILING_OPTIMAL`;
3. `vkAllocateMemory` com `VkImportAndroidHardwareBufferInfoANDROID`;
4. `vkBindImageMemory` e apresentação via socket/SurfaceControl.

Na **Mesa V38 pinada** `f28352d1179a4a85b4be286a883747bae2d3786b`:
- `tu_CreateImage` inicialmente configura a imagem AHB como **deferred**;
- `tu_AllocateMemory`, `src/freedreno/vulkan/tu_device.cc`, chama `vk_android_get_ahb_layout`;
- `vk_android_get_ahb_layout`, `src/vulkan/runtime/vk_android.c`, chama `vk_gralloc_to_drm_explicit_layout` e `u_gralloc_get_buffer_basic_info`;
- `tu_image_init`, `src/freedreno/vulkan/tu_image.cc`, recebe **o modificador real** (ou desconhecido) e decide linear/tiled/UBWC.

Portanto, patch em `tu_CreateImage` limitado a `vk_image_is_android_native_buffer` NÃO intercepta o output do jogo. O script experimental `apply_gamehub_a830_anb_unknown_modifier.py` foi **apagado** da branch de análise para evitar outra build inútil.

## Falha potencial específica com fonte demonstrada

O importador R11 `apply_gamehub_gralloc_metadata_parity.py` usa `u_gralloc_fallback_create` para FD/stride e sobrepõe FourCC + modifier apenas quando AIMapper5/libui fornece ambos.

Se **a consulta falhar** e o backend legado retornar `DRM_FORMAT_MOD_INVALID`, a R11 devolve sucesso mantendo INVALID. Esse valor passa sem normalização por `vk_android_get_ahb_layout` → `tu_AllocateMemory` → `tu_image_init`. Nessa versão, somente `DRM_FORMAT_MOD_LINEAR` força `TILE6_LINEAR`; caso contrário a imagem começa como `TILE6_3`, com escolha UBWC dependente do formato. Um AHB fisicamente linear pode então ser tratado incorretamente.

Esse modo de falha foi identificado em A830 por outros projetos Turnip, após comparar `TU_DEBUG=layout` dos drivers com erro vs funcional. Isso justifica investigação PRIORITÁRIA da **importação AHB**, mas não comprova que o modifier realmente foi INVALID na sessão R11: o log fornecido não registra seu valor, e uma AHB **pode ser corretamente UBWC**. Forçar `INVALID` para `LINEAR` indiscriminadamente é inseguro e não será enviado aos testers.

## Outro diferencial não controlado entre os logs

| Dado | GameHub funcional 08:55 | R11 13:50 |
| --- | ---: | ---: |
| GPU shader cache | 7.121 arquivos | 5.661 arquivos |
| Do pacote (pack) | 0 | 5.350 |
| Cache driver carregado | 26.140 KiB | 19.793 KiB |
| Readback | Precise | Precise |
| Shader model | KHR barycentric=1 / Wave64 | KHR barycentric=1 / Wave64 |
| Async graphics | 1 | 1 |
| Present full-screen blit | 1 | 1 |

Os testes não partem de estado idêntico de **cache de shaders/pipelines**. Isso não justifica os defeitos só pelo cache, mas torna incorreto atribuir toda a diferença ao driver sem comparar o mesmo programa/shader.

## Critério obrigatório para o próximo release

Sem criar outra Turnip: identificar primeiro o modifier FourCC/stride e o layout AHB de saída, **no próprio caminho AHB**; usar dados de GameHub funcional para confirmar condição. Se o display estiver correto em ambos, seguir para exportação/diff de shader específico (IR3, barycentrics, texturas e resultados por pass), e não remendar KGSL ou registradores que já coincidem.

**Status:** bug visual da R11 NÃO resolvido; somente a trilha técnica e o bloqueio causal ficaram claros. Nenhum novo ZIP foi compilado por essa auditoria.
