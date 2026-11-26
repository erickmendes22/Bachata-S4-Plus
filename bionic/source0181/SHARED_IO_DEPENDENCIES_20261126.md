# Dependências da biblioteca FIOS original no FEX — 2026-11-26

## Evidência e alcance

A captura `analysis/B583A2F0/native-clean.log` pertence ao núcleo Order
`a2d61cca96e2c9b65276e307c0b10d4f950b3c9b`, contém 1.100 linhas e não foi
truncada. Ela não mostra primeiro frame. A preferência pelo FIOS original já
produziu efeito: o jogo carrega `libSceFios2.prx` e `libc.prx`, imprime a versão
SDK do FIOS e abre os cinco PSARC com tamanhos reais. O marcador de política
isolado não seria prova; as operações de arquivos e a ausência do caminho HLE
confirmam a mudança de execução.

| Evidência | Captura anterior `81209BF6` | Captura atual `B583A2F0` |
| --- | ---: | ---: |
| `BACHATA_FIOS_COMPLETION` do HLE | 112 | 0 |
| Inicialização FIOS HLE | 1 | 0 |
| Montagens FIOS HLE | 5 | 0 |
| Linhas SAF dos cinco arquivos PSARC | 0 | 25 |

Os tamanhos observados agora são 114.203.746, 678.424.953, 566.472.670,
163.264.452 e 180.774.780 bytes. A captura anterior usava o resultado fictício
de 1 MiB do HLE de montagem. Esta rodada não repete a correção de callback ABI
como causa restante e não implementa outro montador fictício.

O doador lido é `iss/port` em
`/workspace/scratch/ec4706415923/iss`, revisão local
`6fc684061cd3307c314ad9e0c37683bbb46f1645`. O root verificou por GitHub a revisão
atual `9542810428dca8f29695ce23610479c88389e4ed` e confirmou que a seleção de
módulos/exports permaneceu igual. O port atual pode usar AOT; o Bachata continua
com o seu FEX. Não foram copiados executáveis, PRX, runtime ou launcher.

## Contratos corrigidos

| Caminho | Divergência concreta | Correção e limite |
| --- | --- | --- |
| `Linker::Resolve` | O port procura export `libc` único para imports `libSceLibcInternal`. O Bachata só buscava a identidade exata. | Resolver os quatro NIDs de calendário observados somente quando há export de função real, não nulo, tipado e único; manter HLE forte e export exato prioritários. |
| `Linker::RelocateAnyImports` | A chegada tardia de `libc` não revisita importadores de `libSceLibcInternal`. | Reconsiderar esses importadores quando o novo módulo declara export library `libc`, antes do `Start` real. O bit de relocação pendente só é fechado quando a resolução consegue endereço válido. |
| Objeto `Need_sceLibcInternal` | Import `ZT4ODD2Ts9o` continua sem endereço nas linhas 738–739 e 924–925. | Após `RegisterFexLibcGuestObjects`, reutilizar o objeto `P330P3dFF68` já inicializado em memória guest; validar o span de quatro bytes e registrar o alias de objeto. Não publicar endereço `.bss` do host. |
| `__cxa_finalize` | O HLE `__cxa_atexit` possui a tabela, mas não havia finalizador correspondente. Usar o finalizador do PRX consumiria outra tabela. | Registrar finalizador forte nos namespaces `libc` e `libSceLibcInternal`, com a mesma `AtexitEntries`, filtro DSO, consumo exato e callback pelo bridge FEX. |
| `Func_7C980FFB0AA27E7A` do DiscMap | O Bachata retornava sucesso e escrevia três zeros sem backend de bitmap; o doador retorna ausência. | No FEX, retornar `0x81100004` sem escrever nos outputs, inclusive quando são nulos. Preservar o caminho desktop existente. |

Os NIDs de calendário permitidos são `1mecP7RgI2A` (`gmtime`), `5bBacGLyLOs`
(`gmtime_s`), `efhK-YSUYYQ` (`localtime`) e `n7AepwR0s34` (`mktime`). Eles
aparecem como imports pendentes do FIOS nas linhas 750–757 da captura atual.
`H2e8t5ScQGc` (`__cxa_finalize`) recebe a implementação compartilhada e não
entra no alias para o PRX.

O fallback amplo do port foi deliberadamente restringido: malloc/free,
realloc/calloc, memalign, usable-size, operadores new/delete, mspace, FILE e
outros imports não podem trocar silenciosamente de domínio de ownership só
porque um HLE não existe. O gate testa explicitamente essa família com e sem
HLE forte. Um export ausente ou ambíguo mantém o fallback anterior e a
relocação provisória. Não foram presumidos exports a partir do nome do PRX:
os binários do jogo não estão disponíveis no workspace.

### Finalização e lifetime

O contrato da tabela comum, DSO específico ou nulo, ordem inversa e execução
exata uma vez é definido pelo
[Itanium C++ ABI, seção de destruição de DSO](https://itanium-cxx-abi.github.io/cxx-abi/abi.html#dso-dtor).
Cada retirada ocorre sob `AtexitMutex`; função e argumento são copiados e a
entrada é removida antes do callback. Nenhuma referência ao vetor ou lock da
tabela atravessa código guest. Uma chamada reentrante pode registrar novas
entradas ou drenar as restantes; chamadas concorrentes não podem selecionar
duas vezes a mesma entrada. A ordem é inversa na seleção protegida pela tabela;
callbacks de finalizações concorrentes podem se sobrepor.

No FEX, todos os destructors registrados por este HLE passam por
`RunGuestFunctionOrAbort`. Não há tentativa de chamar nativamente um endereço
guest não reconhecido. O gate compila o encoder e o helper do bridge reais,
controlando apenas a execução final de código x86. O comportamento de falha do
bridge existente permanece intacto.

O marcador SDK compartilha o backing de `Need_sceLibc`, que vive no VMM do
processo. A validação e o registro ocorrem depois da alocação e antes do primeiro
`LoadModule`; uma falha de mapeamento não cria um símbolo nulo ou nativo. O
endereço é copiado antes de `AddSymbol`, que pode realocar o registro de símbolos.

## Implementação e integração

Aplicar `port_shared_io_dependencies.apply(source)` após o grupo
`port_shared_io_fios_exports`. O overlay modifica somente:

- `src/core/linker.cpp` e `src/core/linker.h`;
- `src/emulator.cpp`;
- `src/core/libraries/libc_internal/libc_internal_cxa.cpp` e `.h`;
- `src/core/libraries/disc_map/disc_map.cpp`.

Os mesmos arquivos de overlay, teste e documento são usados nos dois cores.
O grupo não modifica os event flags, PSARC, SAF, scheduler de I/O, frontend,
allocators, FEX, driver ou apresentação. `bionic/generic/android_libc_compat.cpp`
é lido pelo gate para compilar o método real de alocação de objetos; seu conteúdo
não é alterado por este grupo.

Comando do gate:

```sh
python3 bionic/source0181/test_shared_io_dependencies.py --source /caminho/da/arvore-efetiva
```

O argumento opcional `--generic` seleciona o `android_libc_compat.cpp` usado pela
build. O padrão é o arquivo do mesmo worktree que contém o teste. O gate extrai
também o resolver, relocator, `LoadAndStartModule`, registro de objetos,
sequência de publicação do SDK, finalizador, registro de aliases C++ e DiscMap
reais. Fronteiras controladas: armazenamento ELF/símbolos, alocação de VMA,
registro HLE e execução guest final. Isso não é um teste de gameplay.

### Resultado local observado

O gate terminou com 82 casos FEX e 16 casos desktop aprovados. A execução FEX
passou 392 callbacks pelo encoder e helper reais do bridge. Os 17 controles
negativos compilaram e foram rejeitados em execução: alias ausente ou ambíguo,
namespace errado, alias amplo indevido, tipo objeto indevido, perda da prioridade
HLE, falta de religação tardia, marcador host/não mapeado/valor errado, filtro DSO,
ordem de finalização, descarte de outras entradas, callback duplicado, chamada
nativa de endereço guest e os dois retornos DiscMap incorretos.

O programa C++ extraído das árvores aplicadas Order e SotC é idêntico, com
SHA-256 `ec636eda3d04fd121c7bdd4334c015a8b677f8485a68d52d4d699091ad71e1ae`.
Portanto a mesma bateria de métodos cobre ambas as composições; ela não foi
repetida apenas para obter outra contagem. O gate anterior
`test_shared_io_fios_exports.py`, executado na composição atualizada, também
passou seus 14 casos FEX, 6 desktop e 7 controles negativos. A compilação usa
UBSan, `-Wall -Wextra -Werror -Wunused-const-variable`; somente parâmetros
legados intencionalmente não usados e o fallthrough já existente ficam fora
desses avisos. A build NDK e os gates CI da revisão publicada continuam sendo
etapas distintas exigidas antes da entrega.

## Observabilidade e limites

- `BACHATA_SHARED_IO_LIBC_BIND` aparece somente quando um export real é
  selecionado; inclui NID, módulo importador, módulo exportador e endereço.
- `BACHATA_SHARED_IO_LIBC_SDK_OBJECT` registra a publicação do objeto guest.
- `BACHATA_SHARED_IO_CXA_FINALIZE` aparece uma vez na primeira chamada real.
- `BACHATA_SHARED_IO_DISC_MAP` aparece uma vez na primeira consulta real e
  declara que os outputs ficaram intactos.

A captura disponível prova os imports e as divergências, mas não prova que
calendário, finalização ou DiscMap tenham sido chamados no ponto do congelamento.
O teste de host comprova os contratos corrigidos e a preservação das fronteiras;
não mede primeiro frame, estabilidade, FPS ou equivalência completa com o port.
Os novos marcadores distinguem vínculo efetivo de simples disponibilidade da
correção, sem logs por operação de arquivo ou polling.
