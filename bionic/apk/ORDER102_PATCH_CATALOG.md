# Catálogo The Order 1886 01.02

## Origem e alcance

`order102_patch_catalog.py` adapta as receitas de preparação do port à aplicação
em memória do Bachata. O backend continua FEX, e nenhum executável preparado,
launcher ou runtime do port é incorporado.

A fonte PC fixada é
[`c53cd01d032995fe622033623ab64b4cf6b02233`](https://github.com/JulioCacko/The-Order-1886_pc/tree/c53cd01d032995fe622033623ab64b4cf6b02233/scripts).
As receitas relevantes de `order1886_resolution.py`, `order1886_post_effects.py`,
`order1886_display.py`, `order1886_frame_rate.py`, `order1886_editions.py` e
`patches.py` continuam iguais no PC remoto `37482884cf72e8920b9c8357600b5f271befadfe`,
verificado em 2026-11-26. A adaptação Android que permite largura mínima 640 é
`patch_android_resolution.py` em `756a4f0cc603b02971d45b36354143249a4fe492`.
Os arquivos executados no teste e seus SHA-256 estão em
`testdata/order102_donor/provenance.json`.

No APK anterior `200a16e8`, as opções 01.02 incluíam resolução, 60 FPS, 16:9 e
cloth. As opções de motion blur/DoF eram somente 01.00; film grain e chromatic
aberration não existiam. Os três writes da resolução antiga não cobriam a receita
completa do port. O catálogo novo conserva nomes, autores e seleções existentes
das resoluções e acrescenta quatro opções de efeitos para 01.02, desligadas.

## Receitas e dimensões efetivas

| Nome preservado no seletor | Quadro | Cena cinematográfica | Cena com 16:9 selecionado |
| --- | --- | --- | --- |
| Resolution Patch (900p) | 1600 × 896 | 1600 × 667 | 1600 × 896 |
| Resolution Patch (720p) | 1280 × 720 | 1280 × 533 | 1280 × 720 |
| Resolution: 540p (extreme performance) | 960 × 544 | 960 × 400 | 960 × 544 |
| Resolution: 360p (ultra performance) | 640 × 360 | 640 × 267 | 640 × 360 |

Os nomes antigos permanecem para preservar as escolhas. As notas mostram as
dimensões reais: os valores 896/544 reproduzem o arredondamento do script doador.
Escolher somente uma resolução. Nenhum perfil é ativado automaticamente.

Cada grupo valida a instrução completa do branch, quatro stores, dimensões da
cena e as instruções de capacidade de GPU stack/heap, inclusive quando
`Value == Expected`. Nas larguras deste catálogo, o doador mantém a capacidade
retail porque aplica `max(1, scene_pixels / native_pixels)`.

| Elemento | Endereços do XML |
| --- | --- |
| Branch de resolução | `0x0084cef5` |
| Quatro stores completos | `0x0084cef7`, `0x0084cf01`, `0x0084cf1f`, `0x0084cf29` |
| Largura/altura da cena | `0x00c39c54`, `0x00c39c59` |
| Instrução completa de aspecto, quando 16:9 está ativo | `0x0084ce86` |
| GPU stack, 13 instruções | `0x010a6030`, `0x010a5e87`, `0x010a5e92`, `0x010a5ea5`, `0x010a5eb5`, `0x010a5ecb`, `0x010a5ee4`, `0x010a5f7a`, `0x010a5efd`, `0x010a5f16`, `0x010a5f2f`, `0x010a5f48`, `0x010a5f61` |
| Heap, quatro instruções | `0x00698d0b`, `0x00698d33`, `0x00698d63`, `0x006997cc` |

Cada XML tem 26 linhas por resolução; ficam ativas 24 na apresentação
cinematográfica ou 25 com 16:9. Duas alternativas da altura da cena são
mutuamente exclusivas. O aspecto completo fica no mesmo grupo transacional da
cena 16:9. O patch separado de aspecto escreve exatamente o mesmo imediato,
portanto pode ser aplicado antes ou depois.

| Nova opção 01.02 | Endereços do XML | Instruções |
| --- | --- | ---: |
| Disable Motion Blur | `0x00c35086` | 1 |
| Disable Depth of Field | `0x00c358af`, `0x00c35617`, `0x00c1dd89` | 3 |
| Disable Film Grain | `0x00c355df`, `0x00c35887` | 2 |
| Disable Chromatic Aberration | `0x00c1de57`, `0x00c1de63`, `0x00c1dec1`, `0x00c1deca`, `0x00c1def7`, `0x00c1defd` | 6 |

Os bytes `Expected`/`Value` completos estão nas constantes `EFFECTS`, `STORES`,
`STACK_SITES`, `HEAP_SITES` e na função `resolution_lines`. Os endereços públicos
do XML são os RVAs do doador mais `0x400000`.

As receitas legadas 01.00, 1440p e 4K permanecem intactas. O doador não fornece
receitas 01.02 equivalentes aos antigos jumps de Bloom/Lens Flares; elas não são
copiadas entre versões. O modo de engine `-msaa 1 -disablecloth` já estava
integrado e aparece no log real do jogo. Este grupo fecha o catálogo de escolhas;
não atribui a ele a causa do crash Vulkan nem confirma ganho de FPS no aparelho.

## Contrato nativo obrigatório

Os oito grupos novos/completados usam `Metadata RequireAllExpected="true"` e
linhas `Type="bytes"`, com `Expected`/`Value` do mesmo tamanho. O core deve validar
todas as linhas ativas antes de qualquer escrita; aceitar bytes já iguais a
`Value` dá idempotência. Condições `IfEnabled`/`IfDisabled` referem-se ao nome
exato `16:9 Aspect Ratio (Full Screen)`, na mesma versão do jogo. Condições
ambíguas/desconhecidas, bounds inválidos ou overlap conflitante rejeitam o grupo.
Esse contrato é implementado separadamente por `port_guarded_patch_groups.py`.

## Caminhos, instalação e preservação das escolhas

Dentro de `assets/runtime/runtime.zip`, substituir simultaneamente:

- `patches/bachata-official/TheOrder1886.xml`: cópia imutável do catálogo.
- `user/patches/bachata-official/TheOrder1886.xml`: cópia inicial do usuário.

`runtime_updates(base_apk_zipfile)` retorna ambas as entradas. Atualizar tamanho
e SHA-256 de cada uma no manifesto verificado; a identidade do catálogo deve
participar da identidade do runtime para que uma atualização de catálogo também
produza extração nova. `files.json` já mapeia o XML para CUSA00785 e os outros
cinco IDs existentes.

No aparelho os caminhos são relativos a
`files/runtime/<manifest.runtimeVersion>/`. O core e o seletor usam a cópia em
`user/patches`. O marcador do XML é `BachataPortCatalog="order1886-0102-port-v1"`.

`patch_order_catalog_frontend.py` faz duas alterações:

1. `PatchSelectorActivity.activeRuntimeDirectory` chama o método existente
   `GlibcSessionRuntime(Context).install()`, converte o `Path` em `File`, executa
   `OrderPatchCatalog.prepare(File)` e retorna. A chamada já ocorre na worker de
   `loadPatchesAsync`, com progresso e tratamento de erro existentes. Assim o
   catálogo fica visível antes do primeiro lançamento. O instalador existente
   verifica e promove o runtime completo. Não se cria runtime parcial e não se
   altera o XML de uma build anterior.
2. `NativeRuntimeProcessLauncher.validateRequest` chama
   `OrderPatchCatalog.prepare(Path)` imediatamente depois de obter o runtime.
   Nenhum registrador vivo ou número de registradores é alterado nesse hook.

O helper Java migra somente `isEnabled`, por identidade completa
`(Title, Name, Author, AppVer, AppElf)`. Ele escolhe a fonte comprovadamente
editada com mtime mais recente: o XML do usuário deve diferir da cópia imutável
do mesmo runtime. Isso também reconhece uma escolha explícita de desligar tudo.
Não há ordenação por hash do runtime. Uma escolha já salva no runtime atual
tem prioridade. Novas opções continuam desligadas.

Arquivo de bloqueio entre processos, escrita atômica e marcador por versão
tornam a migração idempotente. Apenas os valores de `isEnabled` são alterados;
bytes funcionais, atributos, condições e notas do catálogo novo permanecem.
Fonte ausente, XML malformado, DTD ou fontes igualmente recentes com escolhas
divergentes não sobrescrevem o XML válido. Nenhuma ação extra do usuário é
necessária para atualizar o catálogo.

## Integração de build

Depois de decodificar a base exata e aplicar `patch_frontend.py`, antes do
`apktool b`:

```bash
python3 bionic/apk/patch_order_catalog_frontend.py out/apk/decoded
```

Depois do rebuild, incluir os dois DEX alterados:

```bash
unzip -p out/apk/recompiled-smali.apk classes4.dex > out/apk/classes4-order-catalog.dex
unzip -p out/apk/recompiled-smali.apk classes8.dex > out/apk/classes8-bionic.dex
```

Compilar o helper em DEX independente:

```bash
mkdir -p out/apk/order-catalog-classes out/apk/order-catalog-dex
javac --release 8 -Xlint:all -Werror \
  -d out/apk/order-catalog-classes \
  bionic/apk/java/com/bachatas4/android/patches/OrderPatchCatalog.java
jar cf out/apk/order-catalog-helper.jar -C out/apk/order-catalog-classes .
"$ANDROID_HOME/build-tools/36.0.0/d8" --min-api 31 \
  --output out/apk/order-catalog-dex out/apk/order-catalog-helper.jar
```

O assembler deve substituir `classes4.dex` e `classes8.dex` pelos arquivos acima
e incluir `out/apk/order-catalog-dex/classes.dex` como `classes14.dex`, falhando
se a base já contiver esse destino. Incluir todas as classes internas do helper
no JAR. O helper usa somente Java/XML/NIO, sem depender de `android.jar`.

## Verificação

```bash
python3 -B bionic/apk/test_order102_patch_catalog.py
python3 -B bionic/apk/test_order_patch_catalog_migration.py
```

O primeiro teste executa os aplicadores reais fixados do doador em imagens de
instruções e compara a memória final inteira: oito combinações de resolução e
aspecto e 15 combinações não vazias de efeitos. Também confere preimages,
idempotência e preservação funcional das opções legadas.

O segundo compila o helper Java exato e executa dez árvores reais de arquivos,
incluindo identidade completa, escolha recente, all-off, conflito/malformed,
bytes novos preservados, idempotência e dois processos concorrentes. Executa
também o fluxo de registradores do método do seletor com o contrato do instalador
simulado: `install → prepare → return`, sem migração nem retorno antigo quando
a instalação falha. O fluxo do launcher conserva as demais instruções.

Ambos passaram localmente. O helper real também foi compilado por D8 com API 31,
correspondente ao mínimo do frontend, sem erros nem warnings. O DEX emitido é
versão 039; as instruções desassembladas são iguais às do teste anterior com
API 33. O helper usa JAXP/SAX/DOM disponível antes da API 31, `StandardCharsets`
desde API 19 e NIO `Path`/`Files` desde API 26. Não usa métodos JAXP modernos como
`newDefaultInstance` ou `newNSInstance`.

Referências Android: [Files](https://developer.android.com/reference/java/nio/file/Files),
[FileChannel](https://developer.android.com/reference/java/nio/channels/FileChannel),
[DocumentBuilderFactory](https://developer.android.com/reference/javax/xml/parsers/DocumentBuilder)
e [DocumentBuilder](https://developer.android.com/reference/javax/xml/parsers/DocumentBuilder).

A montagem Apktool/DEX final, inclusão no APK e validação
de identidade/assinatura fazem parte do pipeline de entrega; estabilidade e
desempenho ainda precisam ser comparados no aparelho.
