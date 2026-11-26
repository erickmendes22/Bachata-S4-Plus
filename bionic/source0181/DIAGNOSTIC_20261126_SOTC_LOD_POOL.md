# SotC: localização do pool de LOD no mapa FEX

## Alcance e conclusão demonstrada

A amostra `626236DC` executou o core
`3938820401a1a5971b3f96aac7c0e01d6037568c`. Ela apresentou frames, registrou
uma amostra de 51,87 FPS e depois congelou segundo o usuário. A saída foi
solicitada pelo usuário, com código zero. Este grupo corrige uma divergência
ativa do controle de pressão de texturas: o helper conservava o endereço
virtual fixo do runtime AOT, embora o FEX tivesse mapeado o bloco de metadados
do jogo em outro endereço.

A reprodução compila os métodos efetivos de tradução de memória e os dois
helpers de LOD. Para o mesmo bitmap válido com zero páginas livres, o código
anterior devolve `-1` e publica mip2; a correção devolve `0` e publica mip4.
Essa diferença está comprovada em teste. **O log não contém o conteúdo real
do bitmap nem uma captura da instrução de espera do jogo. Por isso, este
resultado não prova que a pressão de texturas seja a única causa do
congelamento observado.**

## Evidência da amostra e do port

Os caminhos de logs abaixo são relativos ao workspace de análise.

| Fonte | Evidência | Implicação |
|---|---|---|
| `analysis/626236DC/application.log`, linhas19 e25–28 | Backend 13:27:33.498006; primeiro frame apresentado 13:27:51.736724; FPS 51,87 em 13:27:53.750885 | O primeiro frame levou 18,239 s e houve apresentação posterior. Não é a falha antiga de nunca apresentar. |
| Mesmo arquivo, linhas33–35 | `backend stopped exitCode=0`, fim 13:28:05.209509 | Não classificar o stop voluntário como crash. |
| `analysis/626236DC/shadps4.clean.log`, linha2220 | DrawPipe habilitado, 8 CPUs, FEX, signals, recorder=true | A amostra executou o caminho ativo de fila já integrado. |
| Mesmo arquivo, linhas1643–1645 | Direct físico `0x127de0000`, tamanho `0x220000`, VA `0x200a30000` | O bloco de metadados termina exatamente no total Direct `0x128000000`. |
| Mesmo arquivo, linhas1650–1655 | Grandes blocos emVA `0x200d00000` e `0x240d00000`, físicos `0x100000` e `0x40100000` | O bloco de 1 GiB vem depois dos metadados; não se deve presumir que o objeto esteja nele. |
| `analysis/port-reference-logs/sotc/logs/android-game.log`, linhas126–135 | Metadados físicos `0x13bde0000`, tamanho2228224, emVA `0x1000000000`; 1 GiB emVA `0x1000300000` | A mesma organização possui VA diferente no runtime do port. |
| Mesmo log do port, linhas224–227 | ModoHigh, pool 0% livre, mip4 aos 2,095 s | O ajuste de pressão é ativo no perfil de referência. |
| Mesmo log do port, linhas272–273 e315–316 | Recuperação para mip3 com 10% e mip2 com 17% | A histerese pertence ao comportamento efetivo, não a uma opção desligada. |

Fonte anterior do Bachata:
`validation/pacing-waits-sotc/src/video_core/sotc_lod_stats.h`, linhas22–50.
O endereço fixo `0x1000000140` é lido em `pool+0x50`; a falha de leitura
retorna `-1` e não ajusta `coarser`, inicialmente zero.

Fonte doadora efetiva:
`parity/sources/sotc-effective/shadps4/video_core/sotc_lod_stats.h`,
linhas67–96 e205–239. O objeto do alocador tem bitmap em `+0x50`, número de
palavras em `+0x58` e páginas em `+0x60`; ele fica em `base+0x140` do primeiro
bloco de metadados Direct. A leitura usa backing físico para não disparar as
proteções GPU. Os limiares ativos são 3%, 8% e 16%.

Os avisos de `IT_SET_PREDICATION` e de textura parcialmente mapeada também
aparecem no port, nas linhas 231–239, e não demonstram por si só a causa do
stall. Da mesma forma, a última mensagem de um shader ou de uma arena não é
uma pilha de execução nem prova que aquele objeto bloqueou o jogo.

## Implementação

`port_sotc_lod_pool.py` modifica somente:

- `src/core/memory.h` e `src/core/memory.cpp`: query somente leitura do
  candidato Direct no topo físico, sob o mutex existente. A query exige uma
  tradução virtual completa, sem buracos e fisicamente contínua. Aceita
  splits de VMA e de áreas físicas; não fixa o VA nem lê bytes aleatórios à
  procura de uma assinatura.
- `src/video_core/sotc_lod_stats.h`: aplica o offset documentado `0x140` à
  base encontrada. Valida tipo de memória, tamanho do cabeçalho, bitmap,
  limites de palavras/páginas e todos os spans lidos. Mantém o limite de
  capacidade de bitmap do doador, inclusive capacidade arredondada. Relê
  os metadados e compara a geração do mapa ao fim para recusar uma amostra
  atravessada por unmap/remap ou por reset do alocador.

O mapa físico pode coalescer duas alocações adjacentes do mesmo tipo.
Portanto a query encontra um **candidato**, não prova identidade de
alocação. O teste inclui essa situação: um candidato aumentado sem layout
válido retorna desconhecido e não inventa 0% livre.

A política permanece a do port ativo: mip2 inicial, mip4 abaixo de 3%,
mip3 abaixo de 8%, recuperação 4→3 ao sair da pressão e 3→2 somente acima de 16%.
Pool desconhecido continua retornando `-1`, nunca zero. A consulta ocorre a
cada 30 relatórios de LOD, como antes; não é feita por DWORD nem por
descritor. A cadência em segundos depende da frequência dos relatórios.

O marcador `BACHATA_SOTC_LOD_POOL` contém pool, físico, bitmap, palavras,
páginas, livres, percentual e mip. Ele só é emitido ao descobrir/perder o
pool ou mudar o mip. Sua presença com endereço/bitmap válidos na próxima
captura permite confirmar o ponto que o teste host não observa: o layout
real inicializado pelo jogo nesse aparelho.

## Validação

Comando de reprodução e gate:

```sh
python3 -B bionic/source0181/test_sotc_lod_pool.py \
  --source /workspace/scratch/a834d08af999/analysis/sotc-lod-pool-validation \
  --baseline /workspace/scratch/a834d08af999/validation/pacing-waits-sotc
```

O teste compila a query, `TryReadBacking`, `VisitPhysicalSpans`, tipos VMA,
mutex e geração de mapa reais, além do helper de LOD efetivo. O armazenamento
físico e os eventos de mapeamento são fronteiras controladas. As duas faixas
de VA observadas permanecem `PROT_NONE`; acesso direto ao guest em vez do
backing falharia.

São cobertos os dois seriais SotC, as bases observada/do port/relocada,
percentuais e histerese, capacidade arredondada do bitmap, spans divididos,
aliases, unmap/remap, tipo físico errado, região livre, buracos, candidatos
coalescidos sem layout, metadados inválidos, substituição física entre
leituras, reset do alocador e ausência de consultas nos 29 relatórios
intermediários. Sete controles negativos executáveis restauram o VA fixo,
removem a geração, removem a releitura de metadata, ignoram a continuidade
física, ignoram falha de leitura do bitmap, confundem zero com desconhecido
ou removem a reação à pressão.

Resultado final: **91 casos positivos e sete controles negativos passaram
sob UBSan**, além da reprodução comparativa do helper anterior. A saída foi:

```text
BACHATA_SOTC_LOD_POOL_REPRO old=-1/mip2 relocated=0/mip4
BACHATA_SOTC_LOD_POOL_PASS cases=91 protected_guest=2 cadence=30
BACHATA_SOTC_LOD_POOL_SUITE_PASS negative_controls=7
```

O resultado host não substitui a compilação NDK, a prova do APK nem a
validação em gameplay. Este grupo preserva FEX, UI, apresentação, PM4,
predicados de espera, fences e a política de readback existentes. A
investigação independente dos episódios de espera segue em grupo separado.
