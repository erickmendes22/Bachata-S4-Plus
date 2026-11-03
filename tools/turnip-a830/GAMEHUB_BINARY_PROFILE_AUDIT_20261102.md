# GameHub A830: auditoria de perfis do ELF (2026-11-02)

## Referência inequívoca

Biblioteca original de GameHub utilizada como referência: `libvulkan_freedreno.so`, ELF64 AArch64 Android 34, **SHA-256 `1a109bee1ad087aceee8436479c95c4cd3e66de0778bc79fc3ce9f637f9fe404`**.

As tabelas de perfis foram **extraídas diretamente do binário original**, sem atribuir significado a opções só pela existência de suas strings. Extração reproduzível por `audit_gamehub_driconf.py` (arquivo local de auditoria deste trabalho).

## Evidência de perfil, não de rotina de GPU

No ELF, `tu_sync_renderpass_cache` é uma opção de configuração. O endereço de código **0xCB6860** contém apenas:
```asm
ldrb w8, [x0, #0x4c]
and w0, w8, #0x1
ret
```
Isto **não reconstrói a rotina de sincronização do renderpass**. O construtor dos valores de configuração lê essa opção em `0x8DEDEC` e armazena seu resultado no deslocamento `+0x4c`.

O par `(tu_sync_renderpass_cache, true)` foi encontrado nas tabelas de configuração de **apenas dois executáveis**:

| Executável | Registro (VA) | Opções |
| --- | --- | --- |
| `^(007FirstLight|007FirstLight-Win64-Shipping|FirstLight|FirstLight-Win64-Shipping)[.]exe$` | `0xD99600` | `tu_restrict_subgroup_size_64=true`, `tu_advertise_wave32_compat=true`, `tu_sync_renderpass_cache=true` |
| `^PBZ[.]exe$` | `0xD99640` | `tu_sync_renderpass_cache=true` |

Os endereços das listas são `0xD99140` (007) e `0xD99170` (PBZ). Os dois valores do nome da opção no binário estão em `0xD99160` e `0xD99170`, que são endereços de **dados**, não de funções.

Outras opções com aplicações específicas:
- `tu_split_indexed_draws=true` é perfil para **Cyberpunk 2077** (`^[Cc][Yy][Bb][Ee][Rr][Pp][Uu][Nn][Kk]2077[.][Ee][Xx][Ee]$`), não global A830.
- `tu_uncharted_legacy_adreno_compat=true` é perfil para Uncharted Legacy of Thieves.
- `tu_restrict_subgroup_size_64=true` aparece em vários perfis de jogos, não deve ser assumido global sem verificar o processo em execução.

Nos 26 perfis explícitos recuperados **não há perfil nomeado de Shadow of the Colossus**. Isso não exclui configurações globais ou por engine, mas invalida a alegação de que a presença de `tu_sync_renderpass_cache` prova que essa opção é ativa no jogo.

## Consequência técnica

As versões anteriores de Turnip reconstruíram ou forçaram comportamentos seletivos sem confirmar se eram exercitados no caso real. O foco para Shadow of the Colossus deve ser a comparação das rotinas executáveis utilizadas no A830: geração/lowering IR3, UBWC/fdl6 layout, blits/resolves, hazards de memória e sincronização real. Não reutilizar automaticamente perfis de jogos diferentes.

**Não declarar integração completa nem correção de ghosts/flicker sem equivalência funcional e teste no A830.** Esta auditoria é verificação estática do binário funcional, não uma nova build nem um patch de renderização.
