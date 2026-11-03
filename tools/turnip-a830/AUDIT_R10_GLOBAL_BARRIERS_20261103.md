# A830 GameHub → Turnip V38 R10: reconstrução de barreiras globais

**Base:** `fix/a830-gamehub-regular-indexed-guards-r9-20261103` + correção anterior de gralloc. Apenas a Turnip foi modificada: nenhum arquivo do emulador foi alterado.

**Origem:** ELF GameHub original, SHA-256 `1a109bee1ad087aceee8436479c95c4cd3e66de0778bc79fc3ce9f637f9fe404`.

## Fato técnico

O commit Mesa `10b1ef466fae56505fdcab72f7855100311ae22e` introduziu duas flags de granularidade mais fraca:

- `TU_CMD_FLAG_CACHE_INVALIDATE_GMEM`: invalidação UCHE limitada à janela GMEM;
- `TU_CMD_FLAG_SUBPASS_SLICE_FENCE`: espera das operações de fragmento limitada por slice.

O GameHub original usa `FD_CACHE_INVALIDATE` global e `CP_WAIT_FOR_IDLE`. Seu caminho de flush principal está em `0x95ef54..0x95f550`; os pacotes básicos e as condicionais foram comprovados independentemente no ELF.

A R9 reconstruiu essas ações parcialmente como overrides na emissão, por meio dos scripts R5/R6. A R10 substitui ambos por transformação antecipada das flags **antes da primeira emissão de evento** dentro de `tu6_emit_flushes`, usando os comandos já implementados e ordenados na Mesa V38. A atualização aplica-se apenas aos chip IDs A830 (`0xffff44050000`, `0xffff44050001`, `0x44050001`).

O evento blit clean deixa de ser suprimido devido ao fence por slice removido. As demais GPUs não são afetadas. Não há override global para SYSMEM ou alteração dos patches da R9.

## Verificações concluídas

- SHA-256 do ELF GameHub original confirmado.
- 9 pares de palavras PM4 e 19 instruções ARM64 relacionadas a flush/cache verificados em offsets fixos.
- Modelo reconstruído testado para todas as 4096 máscaras de 12 flags primitivas.
- Workflow source-only `a830-r10-source-only-preflight.yml` aprovado em <https://github.com/erickmendes22/Bachata-S4-Plus/actions/runs/41646271783> (32 cenários de 2 flags novas × status A830/não-A830, ordem de comandos e ausência de sobreposição R5/R6).
- Patch aplicado ao arquivo-fonte pinado Mesa `f28352d1179a4a85b4be286a883747bae2d3786b` na pré-validação.
- Workflow de build da Turnip é manual nesta branch, para não produzir mais drivers sem validação gráfica.

## Limitações — não confundir equivalência parcial com correção visual

Esta revisão reproduz o **subset** básico de sincronização verificado no ELF, e não constitui uma engenharia reversa integral dos 14 MB do driver GameHub. Persistem diferenças que não foram fechadas por evidência: emissão de subpasses/resolve fora do flush básico; shader IR3 com shader real do SotC; tracking de mudanças de layout; bindings e invalidações fora dos estados comparados; nenhuma execução R10 no A830.

Os avisos do emulador `IT_SET_PREDICATION`, memória GPU parcialmente mapeada e formatos Vulkan não suportados aparecem no **GameHub funcional também**. Esses avisos compartilhados não são tratados como causa dos defeitos exclusivos da Turnip, conforme pedido do usuário.

**Status correto:** correção source-level integrada e validação independente dos comandos básicos; ainda não demonstrada a remoção de ghosts/piscadas/texturas ausentes no aparelho.
