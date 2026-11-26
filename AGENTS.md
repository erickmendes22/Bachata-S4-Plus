# Bachata S4+ Android

Para tarefas de correção ou diagnóstico Android que pedem uma nova build, o
entregável é um APK assinado e instalável. Continue até compilar, acompanhar a
execução, corrigir falhas recuperáveis, baixar o APK, verificar a revisão e a
assinatura e entregar o link. Código integrado e testes locais são etapas
intermediárias. Se houver um bloqueio externo irrecuperável, informe a etapa
e a falha observada.

Cada build deve trazer uma correção fundamentada ou uma captura que responda
a uma pergunta concreta indispensável à correção. Identifique o alcance do
APK e informe quais resultados ainda precisam de validação em gameplay.

## Regra obrigatória de continuidade e encerramento

**Não parar por iniciativa própria.** Depois que o usuário solicitar uma correção
com entrega de APK, continuar a investigação, implementação, validação e
compilação até que **pelo menos uma** destas condições seja satisfeita:

1. O usuário dê uma ordem **explícita** para parar ou interromper a tarefa; **ou**
2. O APK solicitado esteja **compilado, assinado, verificado e entregue** ao usuário
   com um link real para baixar.

**Investigação parcial, diagnóstico inconclusivo, alterações de código, commit,
compilação iniciada, falhas recuperáveis, ausência de ganho confirmado ou demora
na execução NÃO autorizam encerrar a tarefa.** Continue procurando a causa real,
corrigindo e acompanhando as etapas necessárias, sem produzir builds apenas por
produzir. Uma resposta intermediária deve informar o progresso e prosseguir com
o trabalho, não substituir a entrega.

Se houver um bloqueio externo efetivamente irrecuperável ou uma limitação real
de acesso/ferramentas da sessão, descreva-o de maneira verificável e sem alegar
que o APK foi entregue. Não invente conclusão, resultado de build ou link; retome
assim que a execução estiver disponível. Esta ressalva de transparência não é
uma autorização para abandonar voluntariamente a investigação.

## Equivalência funcional dos ports (The Order e SotC)

O Bachata continua shadPS4 ARM64 Bionic + FEX nos dois cores. Não migrar para
AOT ARM64, não incorporar o APK, executável, DSO, launcher ou runtime completo
dos ports. Não substituir o core do Bachata pelo core de um port. Manter a
UI, integração JNI, SAF, saves, controles e arquitetura de CPU do Bachata.

Comparar a árvore de código que efetivamente compila nos ports com a árvore
0.18.1 após TODOS os overlays do Bachata. Adaptar a semântica de renderização,
compilação/cache de shaders e pipelines, sincronização, PM4, readbacks,
texturas, memória GPU, apresentação AHB e contagem de frames à arquitetura
FEX existente. Separar diferenças necessárias do backend CPU das divergências
funcionais. Corrigir os grupos de diferenças completos, não apenas logs ou
workarounds isolados. Preservar o comportamento dos demais jogos.

Não aceitar equivalência por número de patches, compilação bem-sucedida ou
presença de símbolos. A confirmação de equivalência funcional exige comparação em gameplay e estabilidade
com o mesmo driver, resolução, patches, cenas e cache frio/quente. Conforme a
instrução do usuário de 2026-11-25, essa confirmação NÃO é condição para a
entrega do APK: entregue a build assinada, com a implementação e testes disponíveis,
e identifique o que ainda precisa ser confirmado no aparelho. Não encerrar a
execução por falta de testes em gameplay. Não exigir
AOT como condição de equivalência ou como solução de desempenho. 
