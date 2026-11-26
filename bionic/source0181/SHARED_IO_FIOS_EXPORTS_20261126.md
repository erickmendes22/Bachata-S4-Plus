# FIOS2: escolher os exports reais da biblioteca do jogo

## Evidência desta rodada

Captura: `analysis/81209BF6/native-clean.log`, 1.610 linhas, executando o core
`ea646fe37584534209ad5f64d2a21f75b7c18a90` (linha 9). A árvore comparada é
`validation/boot-lod-pass-order`, após os overlays daquela revisão.

| Caminho observado | Evidência | Consequência demonstrável |
| --- | --- | --- |
| A biblioteca original existe e é carregada | Linhas 701–702: SAF abre `sce_module/libSceFios2.prx`; a linha 825 registra seu `Start` | A ausência do PRX não explica a escolha do HLE nesta captura |
| As chamadas continuam no HLE | `sceFiosInitialize` na linha 958 e `sceFiosIOFilterAdd` na 959 entram em `fios2.cpp` | Carregar e iniciar o PRX não bastava para redirecionar os imports |
| A correção anterior de callback já funciona | 112 registros `BACHATA_FIOS_COMPLETION`, todos `event=1`, `error=0`; leituras de `all_shaders.xpps` ocorrem a partir da linha 1008 | A assinatura antiga do callback não é a causa restante identificada |
| As cinco montagens PSARC usam alias | Linhas 1571–1605: `music_a`, `music_b`, `music_c`, `english_a`, `english_b`; todas recebem tamanho de montagem 1 MiB e alias `/in_archive` para `/app0` | Esse caminho não abre nem descomprime o arquivo solicitado; não fornece o namespace interno de cada PSARC |
| A captura termina sem primeiro frame | Últimas linhas: evento de usuário, mensagens da thread Trophy, encerramento de 21 segundos e cache | A última mensagem de Trophy não prova a causa do bloqueio; o teste host também não prova primeiro frame |

Não existe abertura SAF de `.psarc` registrada nessa captura. A conclusão
sobre a montagem vem também do método real: `sceFiosArchiveGetMountBufferSizeSync`
retorna `0x100000`, e `sceFiosArchiveMountSync` ignora buffer, tamanho e flags,
chama `MountAlias("/app0", alias)` e entrega handle 1. O problema confirmado é a
seleção desse substituto mesmo com o PRX real disponível, não a infraestrutura
SAF que efetivamente abriu o PRX e os arquivos de shader.

## Comparação com a fonte efetivamente preparada pelo port

Fontes locais consultadas apenas para leitura:

- `iss`: `6fc684061cd3307c314ad9e0c37683bbb46f1645`, branch
  `feature/second-son-arm64-aot`.
- `iss-pc`: `270f12bb97909b0ec3dd8f4cca21acea6d3c591c`.

O nome da branch não determina o backend compilado. Nessa revisão local,
`tools/android/build/build_arm64.sh` compila FEXCore/libisscpu;
`tools/android/bionic/build_native_runtime.sh` compila `port/src/probe.c` e os
`runtime*.c`, com `-lisscpu`. `tools/android/runtime/launch.py` chama
`link_modules` sem `--native-aot` e inicia o loader FEX. Não se afirma aqui que
esse checkout é a revisão remota mais recente.

Revisão adicional de proveniência feita pelo integrador via GitHub MCP em
26/11/2026: a branch remota está em
`9542810428dca8f29695ce23610479c88389e4ed`, 14 commits após o checkout local.
O compare entre essas revisões mantém `link_modules.DEFAULT_MODULES` e a
seleção dos exports reais. As alterações relevantes são de `native_aot`,
imagem do runtime e TLS; o launcher atual seleciona AOT quando encontra o
perfil correspondente. Portanto, a análise local de FEX não é uma afirmação
de que todo o port atual usa FEX. O contrato de FIOS comparado continua sendo
a biblioteca original, e o Bachata conserva seu próprio caminho FEX.

O contrato de arquivos está explícito em três pontos:

- `port/launcher/infamous_run.py`: `MODULES = ['libc.prx', 'libSceFios2.prx']`.
- `port/scripts/link_modules.py`: lê os módulos do jogo, valida os exports
  dentro dos segmentos carregados, registra seus endereços e produz os bindings
  do executável para eles. O caminho Android chama esse script diretamente.
- `port/src/runtime_file.c`: oferece os serviços kernel/POSIX de arquivo. Não
  implementa as APIs de montagem FIOS com aliases. `probe.c` usa os bindings
  reais para imports que não pertencem aos serviços fornecidos pelo runtime.

O port conserva a implementação original de FIOS, incluindo filtros PSARC,
agendamento e estado de operações. O Bachata pode executar essa mesma biblioteca
PS4 pelo FEX já existente; não precisa copiar o runtime, binários ou mecanismo
de preparação do port. A versão local do launcher cita CUSA00223/1.07, enquanto
a captura é CUSA00004/1.00; o ajuste não presume endereços, versão ou um serial.

## Contrato corrigido

`port_shared_io_fios_exports.py` altera somente:

1. `src/core/loader/symbols_resolver.h`: política FEX por instância do resolver,
   publicada por `atomic_bool`, preferindo exports reais de FIOS por padrão.
2. `src/core/libraries/libs.cpp`: registra o fallback HLE utilizável em qualquer
   serial e configura a política pelo override `libSceFios2.use-hle`.
3. `src/core/linker.cpp`: para `libSceFios2`, procura primeiro um export real
   carregado com a identidade de biblioteca, versão, módulo e tipo já exigida
   pelo linker. Os demais módulos e o caminho desktop mantêm sua prioridade.

Sem export real, o HLE existente continua sendo colocado no import, com o
veneer FEX existente. Essa escolha fica **provisória**: `Resolve` devolve o
registro completo, mas retorna `false` para impedir que `Relocate` fixe o bit
definitivo daquela relocação. Esse retorno controla a possibilidade de religar;
o endereço válido continua sendo escrito por `Relocate`.

Quando `LoadAndStartModule` carrega o PRX, sua chamada já existente a
`RelocateAnyImports` troca os imports provisórios antes de `Start`. Somente um
export real ou a preferência explícita por HLE finaliza esses imports. Isso
fecha a segunda parte do defeito: apenas mudar a ordem da procura não corrigiria
imports que o primeiro carregamento já marcou como resolvidos.

O ponteiro de HLE fica separado de `guest_record` durante a procura. Um guest
sem o export desejado não apaga a informação do fallback. Essa separação não é
apresentada como uma nova falha causal de funções: `AddUnsupportedFunction`
anteriormente podia recuperar um adapter HLE já existente.

Permanecem intactos a seleção staged `.sprx`/`.prx` do jogo, o loader SAF/IFile,
falhas de carregamento, `Start`/TLS e o fallback legado quando o PRX não existe.
Não há parser PSARC novo, novo alias, sucesso fabricado, lib do port ou mudança
de CPU. O override `.use-hle` continua tendo prioridade, inclusive se um PRX
já estiver carregado. O ajuste não amplia o relaxamento de identidade de exports
que o script do doador pode usar para módulos de firmware.

## Validação executada

```sh
python3 -B order/bionic/source0181/port_shared_io_fios_exports.py \
  --source analysis/shared-io-fios-exports-validation
python3 -u -B order/bionic/source0181/test_shared_io_fios_exports.py \
  --source analysis/shared-io-fios-exports-validation
```

A segunda aplicação do overlay é idempotente. O gate compila os corpos reais
de registro/política, `Linker::Resolve`, `Relocate`, `RelocateAnyImports`,
`RelocateAllImports`, `LoadAndStartModule` e o braço FIOS do loader sysmodule.
ELF, allocator de veneers e leitura dos bytes do PRX são fronteiras controladas;
a decisão de destino, escrita dos slots, bits de relocação e ordem perante
`Start` vêm dos métodos de produção. O corpo herdado de `LoadAndStartModule`
compara `u32` com o sentinel `-1`; só esse corpo tem o warning de sinalidade
suprimido, sem reescrevê-lo no teste.

Resultado sob UBSan, `-Wall -Wextra -Werror -Wunused-const-variable`:

- 14 cenários FEX e 6 desktop passam, incluindo seis seriais, função e dados,
  PRX tardio, override, SPRX staged, PRX ausente, export parcial/incompatível,
  ENOSYS, manutenção de outros módulos, TLS e retorno de `Start`.
- 7 controles negativos compilam e falham em runtime: HLE sombreando guest,
  bit definitivo prematuro, registro provisório descartado, override ignorado,
  prioridade invertida para todas as bibliotecas, religação dinâmica removida e
  fallback de dados perdido após guest incompatível.

Integração: chamar `apply(root)` após os ajustes comuns de FIOS/registro HLE,
por exemplo após `port_fios_callback_abi`, e incluir o gate com `--source` nas
duas etapas que validam a árvore efetiva. Nenhum arquivo de integração foi
alterado por este grupo.

## Limite da conclusão

O gate prova que a biblioteca original passa a atender os imports compatíveis,
incluindo o caso tardio que antes ficava preso ao HLE. Não executa um PSARC real,
o PRX completo, a GPU ou gameplay. O APK precisa confirmar a atividade da
biblioteca real e a progressão do boot; não há promessa de primeiro frame,
FPS ou correção integral do stall baseada nesta fixture.
