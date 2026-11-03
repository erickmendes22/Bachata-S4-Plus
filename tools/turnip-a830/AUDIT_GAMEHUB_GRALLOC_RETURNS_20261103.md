# A830 GameHub → V38: retorno do gralloc e falhas de metadados (2026-11-03)

## Proveniência
Original GameHub funcional: `libvulkan_freedreno.so`, ELF64 AArch64 Android 34, SHA-256
`1a109bee1ad087aceee8436479c95c4cd3e66de0778bc79fc3ce9f637f9fe404`.
A base de integração é a branch R9 `fix/a830-gamehub-regular-indexed-guards-r9-20261103`,
sem mexer no APK, na escolha de driver nem nos patches de desempenho.

## Comportamento demonstrado pelo código de máquina

```asm
0xCA2F04  bl   0xCA1B7C       ; get_buffer_basic_info do gralloc legado
0xCA2F08  cbnz w0,0xCA3140   ; se falhar, propagar exatamente o erro
0xCA2F1C  mov  w1,#7          ; FourCC, AIMapper5
0xCA3034  mov  w1,#8          ; modifier, AIMapper5
0xCA3138  cbz  w0,0xCA3160   ; libui metadata: sucesso segue para overlay
0xCA313C  mov  w0,wzr         ; falha/ausência metadata => SUCESSO legado
0xCA316C  str  w25,[x23]     ; apenas FourCC
0xCA3170  str  x8,[x23,#8]   ; apenas modifier
```

A R7–R9 abandonava `inherited` quando AIMapper5/libui falhava e caía no
parser da `SMT_PLANE_LAYOUTS` da V38, ou retornava `-EINVAL` sem mapper.
Isto podia invalidar um buffer previamente importado pelo legado e
destruir o layout nativo QTI/UBWC apesar do sucesso inicial.

## Correção aplicada (script-fonte, NÃO driver compilado)

- Gralloc legado retornou erro: retornar o próprio erro, sem reinterpretar planos.
- Gralloc legado retornou sucesso: copiar `inherited` para `out` imediatamente.
- Consulta FourCC+modifier falha: manter todos os campos legados, retornar 0.
- Consulta FourCC+modifier funciona: substituir somente esses dois campos,
  sem converter FourCC zero via HAL, o que não ocorre no ELF original.
- O parser AIMapper5 independente permanece disponível apenas se não existir
  backend legado ao criar a instância, por compatibilidade com outros aparelhos.
  Essa via de compatibilidade **não** existe no controle de fluxo equivalente do
  driver original quando o gralloc legado foi criado e depois falhou.

A verificação `tools/turnip-a830/verify_gamehub_gralloc_result_semantics.py`
valida os invariantes no script e, recebendo como argumento o ELF original,
confere SHA-256 e 7 opcodes nos endereços acima. O workflow verifica o contrato
antes de tentar compilar, quando executado.

## Escopo real e pendências

A correção é uma divergência **comprovada** no importador, mas nenhum teste
gráfico A830 foi realizado nesta branch. Isso **não demonstra** eliminação
dos ghosts, flicker nem das texturas ausentes. Também não implica que todos
os recursos de Shadow of the Colossus passem por AHardwareBuffer/gralloc:
imagens criadas apenas por Vulkan seguem outros caminhos.

A linha `Cached permutation 0 ... conflicts with index 1` no log de
2026-11-03 08:41:55 foi emitida por `vk_pipeline_serialization.cpp:429`
do emulador, e não é prova de falha no cache IR3 do driver. Não foi criado
workaround IR3 a partir desse aviso. Os caminhos ainda por demonstrar são:
transições de layouts e visibilidade CCU/UCHE, imagem interna UBWC,
blits/resolves e variantes IR3 efetivamente usadas no jogo.
