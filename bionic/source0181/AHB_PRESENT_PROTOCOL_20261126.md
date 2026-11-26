# Apresentação AHB: commit, liberação e geometria

## Diferença ativa comprovada

Na captura `analysis/53A4D3EC/native-clean.log`, o core
`ea646fe37584534209ad5f64d2a21f75b7c18a90` registra na linha 133:
`BACHATA_PRESENT_WSI_READY 2688x1216 images=5`. Não há tentativa nem rejeição
de AHB registrada. O motivo está na árvore efetiva: o overlay
`port_present_boot_ownership.py` tornou obrigatório
`BACHATA_AHB_PRESENT=1`, enquanto o ambiente normal não o fornece. Ausência
de tentativa não é evidência de extensão ou formato indisponível no driver.

Os logs de referência do Order registram conexão do protocolo de apresentação
com três buffers 1280×720, incluindo o modo sem VSync. O caminho compilado em
`parity/sources/order-effective/gpu/shadps4/video_core/renderer_vulkan/vk_swapchain_ahb.cpp`
aloca/importa AHBs e troca fences SYNC_FD. A referência Android do outro lado é
`/workspace/scratch/ec4706415923/fix/shadow-ref/tools/android/bionic/present/gow3present.c`
e `geometry.h`: fit centralizado; FIFO desbloqueado no commit; callback de
conclusão usado separadamente para liberar o buffer anterior. O callback não
aplica a próxima transação.

O Bachata já tinha importação AHB, release slots, propriedade de fila estrangeira
e fallback WSI. Seu adaptador não tinha o controle FIFO por commit e esticava o
buffer sobre toda a janela física. A ativação automática dependia de completar
esses contratos, não somente de retirar uma condição de ambiente.

## Alcance da implementação

`port_ahb_present_protocol.py` modifica somente:

- `src/video_core/renderer_vulkan/vk_ahb_present.h`;
- `src/video_core/renderer_vulkan/vk_swapchain.cpp`.

A implementação usa a biblioteca Android e o Vulkan já presentes. Não importa
o processo, socket, launcher ou binários do doador. O produtor e o worker de
apresentação do Bachata continuam os mesmos, assim como o contador de frames,
a integração JNI, FEX e as filas de submissão.

| Contrato | Comportamento aplicado |
| --- | --- |
| Política | Ativação automática apenas para CUSA00785, CUSA08809 e CUSA08034. `BACHATA_AHB_PRESENT=0` desativa; `1` permite; valores inválidos conservam WSI. Não amplia a lista para inFAMOUS ou outros jogos |
| Elegibilidade | Mantém RGBA8 SDR/sRGB, transformação identidade, memória externa AHB, queue-family foreign e importação/exportação SYNC_FD. Recursos insuficientes mantêm WSI |
| Modo | O modo FIFO já escolhido pelo Swapchain usa commit. Mailbox/Immediate continuam aplicando as novas transações sem esse limite de FIFO, como o modo newest do doador |
| FIFO | No máximo uma transação ainda não confirmada por commit. `Acquire` espera com prazo antes de entrar na submissão; `Present` nunca espera pelo callback segurando o mutex global |
| Callbacks | Contextos separados e estado compartilhado por instância. `OnCommit` somente valida a sequência, limpa o estado pendente e notifica. `OnComplete` somente obtém/devolve o fence de liberação anterior |
| Liberação | Fence `-1` permite reutilização imediata; fence válido é importado temporariamente no semáforo adquirido. Se a importação falha, há espera CPU limitada e fechamento do FD pelo dono correto |
| Prazo | Commit, disponibilidade de slot e fallback de importação compartilham o mesmo prazo padrão de dois segundos. EINTR não reinicia esse prazo |
| Geometria | Buffer na dimensão do frame, destino centralizado dentro da janela com proporção preservada. Multiplicações em 64 bits e mínimo de um pixel para casos extremos não representáveis por divisão inteira |
| Retirada | Destruição marca a sessão como retirada e acorda as esperas. Callbacks antigos só enxergam seu estado antigo; não acessam `this`, não submetem Vulkan e não afetam a instância nova |
| Falha | Motivo explícito em `BACHATA_AHB_SELECTION`/`BACHATA_AHB_FALLBACK`, seguido do caminho de recriação WSI já existente |

A documentação oficial do NDK distingue o commit, que permite aplicar outra
transação sem substituir a anterior, da conclusão/liberação dos buffers. Os
callbacks podem chegar em qualquer thread. O fence de liberação válido precisa
ser consumido ou fechado; `-1` significa buffer já liberado. Ver:
[Android NDK — Native Activity / SurfaceControl](https://developer.android.com/ndk/reference/group/native-activity).
`ASurfaceTransaction_setOnCommit` está disponível a partir da API 31; o frontend
tem minSDK 31 e o build nativo atual usa ANDROID_PLATFORM 33.

O worker existente aplica a próxima transação. Dentro dos callbacks há apenas
o mutex curto do estado e a notificação; não há espera de GPU/fence, chamada
recursiva de `ASurfaceTransaction_apply`, consulta ao scheduler ou acesso ao
objeto AndroidAhbPresent destruído. A sequência pendente é publicada antes de
`apply`, cobrindo callback que chega antes de a chamada retornar.

## Validação

```sh
python3 -B order/bionic/source0181/port_ahb_present_protocol.py \
  --source analysis/ahb-present-protocol-validation
python3 -u -B order/bionic/source0181/test_ahb_present_protocol.py \
  --source analysis/ahb-present-protocol-validation
```

Aplicação idempotente. Gate C++23 com UBSan, `-Wall -Wextra -Werror` e
`-Wunused-const-variable`. Compila a classe real AndroidAhbPresent e ReleaseSlots,
os braços reais AHB de Create/AcquireNextImage/Present e a expressão real de
capacidades do Instance. Só a visibilidade de membros privados é exposta para
os casos diretos de estado/geometria. APIs Android/Vulkan, composição e alocação
de recursos são fronteiras controladas; FDs usados no teste são eventfds reais.

Resultado:

- FIFO avança após OnCommit sem esperar OnComplete; conclusão sozinha não abre
  o gate e commit sozinho não libera um buffer;
- callbacks síncronos à aplicação, atrasados e de sessão destruída, incluindo
  retorno de FD após retirada;
- importação bem-sucedida transfere o FD ao driver; importação falha cobre fence
  sinalizado, não sinalizado, inválido e EINTR;
- criação parcial falha em cada etapa e em cada um dos três slots, com contagem
  de recursos e FDs sem vazamento;
- 400 combinações geométricas, além de verificação da geometria recebida pela
  transação real do adaptador;
- matriz de política/capacidades, formato/HDR/transformação, falhas de
  criação/importação/exportação e fallback WSI;
- 11 controles negativos compilados e rejeitados em runtime: espera de commit
  removida, commit sem progresso, token antigo aceito, slots sem retirada,
  stretch, fechamento duplo, FD vazado, fence não sinalizado reutilizado,
  opt-out ignorado, view vazada na criação parcial e capacidade foreign omitida.

Integração: `apply(root)` depois dos overlays existentes de AHB, dimensão do
frame e `port_present_boot_ownership`. Gate:
`test_ahb_present_protocol.py --source <árvore efetiva>`. Não houve edição de
compatibility/workflow/assert por este grupo.

## Limite do resultado

Os testes provam contratos de seleção, ordenação, propriedade e limpeza com
fronteiras controladas. Não medem FPS, latência real, scanout, gameplay ou
estabilidade do driver Android. A próxima captura deve mostrar a seleção real
AHB ou o motivo preciso de fallback; ganho de desempenho e equivalência de
apresentação continuam dependendo dessa execução no dispositivo.
