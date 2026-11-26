# Eventos do kernel, dependências FIOS e preparação gráfica — 26/11/2026

## Escopo e evidência de entrada

Esta rodada responde às capturas `B732DE22` (The Order), `08A542C3`
(Shadow of the Colossus) e `B583A2F0` (inFAMOUS), obtidas com o pacote
`cfd8173bf49ee15649e046735259277ba305903f`. Os cores observados são
`a2d61cca96e2c9b65276e307c0b10d4f950b3c9b` e
`75a1cba457237be6e91524ba1f4f896afab53031`.

A revisão veio do marcador nativo `BACHATA_CORE_REVISION`. O campo
`runtimeRevision` do frontend conserva uma revisão antiga e não identifica
o core carregado. Os três ZIPs tiveram integridade, entradas, tamanhos e
SHA-256 conferidos contra os respectivos manifests.

| Captura | Observação | Limite da conclusão |
| --- | --- | --- |
| Order, CUSA00785 | 164,864 s; primeiro frame em 16,666 s; 72 amostras positivas, de 1,06 a 60,08 FPS; patch 1.02 verificado e flip rate 0 | O máximo registrado não demonstra 50/60 FPS sustentados na cena do port |
| SotC, CUSA08809 | 49,177 s; primeiro frame em 18,496 s; 49 pedidos aceitos, preparados e apresentados; depois até 27,733 s sem novo frame, com filas vazias | A produção parou antes da apresentação; idle não distingue sozinho carregamento e espera permanente; o log nativo está truncado |
| inFAMOUS, CUSA00004 | 22,040 s; sem primeiro frame; FIOS original selecionado e abertura real dos cinco PSARC | A seleção de FIOS anterior funcionou, mas a captura ainda não demonstra boot completo |

As três sessões terminam por parada solicitada pelo usuário, com código 0.
Isso descreve o conteúdo das capturas e não invalida os congelamentos e
falhas relatados. As capturas pertencem à build anterior à presente correção.

O caminho AHB/SurfaceControl aparece ativo no Order e no SotC. No inFAMOUS,
25 aberturas SAF alcançam os cinco arquivos PSARC reais; as montagens HLE
provisórias da rodada anterior não aparecem. Essas correções permanecem.

O Order também registra duas recuperações do guard CALL/RET do FEX. A
sessão continuou depois delas; não são uma falha terminal registrada. O
guard permanece preservado.

O driver do inFAMOUS é `turnip-2bbb279a3da76805`; Order e SotC usam
`turnip-8255659cc205110e`. Isso deve ser considerado em comparações futuras.

## 1. Entrega de event flags

O método antigo `EventFlagInternal::Set` apenas modificava os bits e
notificava uma condição. O waiter consultava os bits novamente quando
conseguia retomar o mutex. Uma reprodução determinística com os métodos
reais confirmou a perda: um waiter já adormecido recebe `Set(1)`, ocorre
`Clear(0)` antes de sua retomada, e o wait termina com timeout. No caminho
ativo do port, Set registra o resultado no próprio waiter antes de notificar;
a limpeza posterior não retira uma entrega já consumada.

`port_event_flag_delivery.py` adapta essa semântica aos dois cores Bachata:

- Set seleciona os waiters sob o mutex, registra o resultado e aplica a
  limpeza na ordem da fila. FIFO e prioridade guest preservam ordem de
  chegada para empates.
- Cancel e Delete concluem somente waiters ainda pendentes. Resultados já
  entregues continuam válidos até a thread consumi-los.
- Timeout usa relógio monotônico. Poll continua retornando busy quando não
  há sinal e não cria uma espera periódica.
- Um registro de objetos com posse compartilhada mantém chamadas iniciadas
  vivas durante Delete. A retirada do handle impede novas consultas; os
  waiters pendentes recebem o erro apropriado.
- A observação de waits usa snapshots com `try_lock`, sem acordar threads.
  A emissão é limitada e ocorre depois de soltar os mutexes. O mesmo ponto
  de progresso lê contadores atômicos do command processor.

O gate `test_event_flag_delivery.py` exercita as operações de produção e
as disputas de entrega/lifetime. A reprodução estabelece um erro funcional
real; a captura anterior não permite afirmar que esse foi o sinal específico
perdido no telefone. O novo estado de espera permite verificar essa ligação.

O log do port de SotC também contém um período de loading sem produção de
frames antes de chegar a `st_gameflow`. Portanto, o teste de progresso deve
distinguir a fase de carregamento de uma espera sem saída.

## 2. Dependências do FIOS original

Após a ativação comprovada do FIOS original, a auditoria passou às suas
dependências. O resolvedor Bachata exigia correspondência exata de
namespace; o doador admite exports únicos da biblioteca libc para certas
importações de `libSceLibcInternal`. Também havia um objeto SDK sem endereço
válido e uma consulta DiscMap que fabricava sucesso sem possuir bitmap.

`port_shared_io_dependencies.py` fecha os seguintes contratos em ambos os
cores:

- As quatro importações observadas de calendário (`gmtime`, `gmtime_s`,
  `localtime`, `mktime`) podem alcançar um export guest real e único de
  libc, depois das implementações HLE fortes e da resolução exata. Tipo,
  namespace e ambiguidade são verificados.
- Se libc chegar depois do FIOS, suas importações pendentes são novamente
  resolvidas antes de executar o início do módulo. Uma correção limitada
  ao primeiro carregamento deixaria esse caminho incompleto.
- O alias é restrito. Allocators e objetos FILE continuam no domínio de
  memória do FEX; uma função ausente não passa silenciosamente a operar
  sobre outro heap.
- `Need_sceLibcInternal` reutiliza o objeto inteiro de 32 bits com valor 1
  que já foi alocado na memória guest por `RegisterFexLibcGuestObjects`.
  O alias é registrado depois dessa alocação e antes das relocações.
- `__cxa_finalize` utiliza a mesma tabela já mantida por `__cxa_atexit`.
  As entradas são selecionadas em ordem inversa e retiradas sob o mutex;
  os callbacks guest passam pela ponte FEX fora desse mutex. Há filtro
  por DSO, suporte a finalize global e proteção contra execução duplicada.
- A consulta DiscMap `7C980FFB0AA27E7A` informa ausência de bitmap e
  preserva os outputs, conforme o doador. O retorno anterior escrevia
  três zeros e anunciava sucesso sem possuir a informação.

O gate `test_shared_io_dependencies.py` usa os métodos reais do resolvedor,
religação, registro de objetos, finalização e DiscMap, com controles de
ownership e falha. A seleção efetiva de exports e a consulta DiscMap recebem
evidência limitada no runtime.

As importações aparecem no log do FIOS, mas o PRX específico do usuário
não está disponível para rastrear todas as chamadas. A equivalência desses
contratos é verificável; atribuir-lhes todo o bloqueio do inFAMOUS exige
observar o próximo progresso real do jogo.

## 3. Reaproveitamento do estado de renderização do Order

O port efetivo possui `RenderStateMemo` habilitado por padrão. A variável
global `runtime_disabled_optimizations` começa em zero; o bit 44 somente é
alterado pelo arquivo opcional de toggles. O Bachata não possuía o atalho
equivalente na preparação dos attachments.

A reprodução usa `BeginRendering`, `GetBarriers`, `FlushBarriers` e o
Scheduler reais. Draws com attachments idênticos já compartilham um passe;
essa sequência não explica as barreiras dominantes do log. A divergência
comprovada é repetir `UpdateImage` e a localização dos render targets em
cada draw, mesmo quando o estado da transação continua utilizável.

`port_order_render_state_memo.py`, apenas no core principal e com seleção
de CUSA00785, acrescenta o reaproveitamento conservador:

- A assinatura inclui os alvos, views, samples, metadados e controles de
  depth/stencil relevantes.
- O passe precisa continuar aberto com o mesmo estado, serial de início
  e tick do command buffer.
- A validação sob o mutex da texture cache confere identidade e geração
  de imagem, backing e view; layout/acesso dos subrecursos; rastreamento,
  dirtiness e metadados de clear. Recursos retirados ou substituídos não
  podem reutilizar uma entrada antiga.
- Clears rearmados, aliasing, feedback, rebind e dependências pendentes
  percorrem a preparação completa. O reaproveitamento conserva os efeitos
  necessários de acesso/LRU.

O gate `test_order_render_state_memo.py` compara o trabalho da preparação
e verifica invalidações nos métodos reais. A adaptação conserva um
aquecimento inicial na abertura do passe. A redução observada no teste
é de chamadas da preparação, não um multiplicador de FPS do jogo.

Na captura B732DE22, 28 amostras do GpuDraw somam 396.288 encerramentos em
146,037 s de janelas: 267.115 (67,4%) foram classificados como Barrier.
`port_order_barrier_census.py` separa os produtores reais dessa categoria e
registra os critérios de alias com custo amortizado. Isso responde à
pergunta ainda aberta de quais dependências encerram os passes durante
gameplay. Barreiras necessárias continuam sendo emitidas.

## 4. Contagem de frames e patches 1.02

O APK cfd8173b foi inspecionado diretamente. O callback Android chama
`ManagedSession.recordPresentedFrame` em cada evento Frame; o booleano
de primeiro frame protege apenas os checkpoints. A taxa usa os intervalos
de uma janela de um segundo. Após um segundo sem frame, o valor volta a 0.
O logger de desempenho é chamado pela chegada dos frames e registra
amostras com intervalo mínimo de dois segundos.

Uma sequência curta de 49 frames seguida de idle é compatível com o único
registro inicial zero do SotC. O log não estabelece uma nova falha de
transporte do contador. O Order tem 72 amostras positivas pelo mesmo
caminho. O contador continua contando apresentações guest concluídas.

O patch 60 FPS do Order foi verificado nos bytes mapeados da versão 01.02,
e o log registra `guest_rate=0`, limite 60 e amostras acima de 30. Isso afasta
um limite permanente de 30 FPS nessa captura, sem explicar sozinho as
quedas posteriores. O catálogo preserva 60 FPS, quatro opções de efeitos
e 900p/720p/540p/360p. Na captura atual, 720p e os quatro grupos de
efeitos aparecem como aplicados com expected bytes verificados; 16:9 e
Disable Cloth Simulation também foram aplicados.

## Fontes, validação e limites

Order efetivo: PC `c53cd01d032995fe622033623ab64b4cf6b02233` composto com
Android `756a4f0cc603b02971d45b36354143249a4fe492`.
SotC efetivo: PC `732cb37d3470d2dad2cc99da19283253c96b53fc` composto com
Android `0366868550bde078d9ed9d88bc72d8acb1584679`.
inFAMOUS: contratos do runtime e linker do port, sem incorporar seu
executável, launcher ou arquitetura AOT.

Referências de código: `runtime_sotc.c` (event flags), `link_modules.py`
(resolução libc), `runtime.c` (objeto SDK), `runtime_tlg.c` (DiscMap),
`vk_rasterizer.cpp`/`vk_scheduler.cpp`/texture cache (Order). O contrato
de finalização usa também a
[ABI C++, seção de destruição de DSOs](https://itanium-cxx-abi.github.io/cxx-abi/abi.html#dso-dtor).

O runner desta rodada registra hashes dos inputs antes e depois dos gates
locais. A publicação exige igualdade entre esses inputs e os commits dos
cores; o CI executa novamente os gates e compila integralmente o Android.
A montagem utiliza somente os dois artefatos nativos bem-sucedidos das
revisões verificadas. O recibo acompanha contagens finais, hashes,
Actions, assinatura e a identidade do APK efetivamente baixado.

Os testes host utilizam dublês explícitos para dispositivo Vulkan e execução
guest quando necessários. Eles não executam os três jogos no telefone.
Não há confirmação de boot completo do inFAMOUS, eliminação definitiva
do congelamento do SotC ou 50/60 FPS sustentados na cena do port.

Equivalência funcional completa permanece sem confirmação. O Bachata
continua shadPS4 ARM64 Bionic + FEX, com sua UI, JNI, SAF, saves e controles.
As correções de sincronização, leitura, apresentação e patches já presentes
foram preservadas.
