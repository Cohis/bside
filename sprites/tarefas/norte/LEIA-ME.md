# Norte — correção controlada dos dois ciclos

Os 16 PNGs de caminhada em `icaro/` e `eva/` foram substituídos por versões
editadas localmente após autorização do usuário. Os 16 arquivos originais da
geração, `rastreamento.json`, `tecnica.json` e `revisao.json` anteriores estão
preservados em `originais_edicao/`. As imagens `raws/` e os prompts também
permanecem intactos.

## Correção feita

- O pé de apoio recua cerca de 6 pixels verticais por quadro nas duas metades do
  ciclo. Na vista norte, o recuo projeta-se para baixo da tela. Ícaro:
  `467,473,479,485` em ambas as pernas; Eva: `475,480,486,492` e
  `474,480,486,492`.
- Os avanços `04` e `08`, cujos pés subiam quando deveriam descer rumo ao
  contato, usam a perna de balanço da passagem `03` e `07` do **mesmo
  personagem e direção**, deslocada até a altura adequada. Nenhum detalhe
  assimétrico, braço ou acessório foi espelhado.
- No contato `01` de Eva, o pé traseiro foi deslocado 17 pixels para separar
  os dois planos de profundidade.
- Todas as alterações ficam abaixo de `y=320`. Os pixels de cabeça, cabelo,
  tronco, braços e acessórios são idênticos aos originais. O calçado é
  transladado sem mudar de tamanho; o tecido da calça é remapeado por vizinho
  mais próximo entre a cintura e o calçado. A edição não cria cores novas.

`registro-edicao.json` identifica as fontes e hashes de cada quadro.
`editar_apoios.py` recria os candidatos; `verificar_candidatos.py` confere
dimensões, margens, transparência, paleta, quadros distintos e recuo; os
relatórios estão em `candidatos_v2/qa.json` e `verificacao-pos-edicao.json`.

## Revisão visual

As pranchas `icaro-prancha.png` e `eva-prancha.png` mostram as fases finais.
GIFs com chão marcado em 100 e 400 ms por quadro estão em
`candidatos_v2/*-chao-100ms.gif` e `*-chao-400ms.gif`. As transições `04→05` e
`08→01` foram suavizadas e o contato manteve ao menos um apoio aparente.

**Revisão independente concluída em 23/out/2026.** As duas pranchas com chão, as oito fases e as transições `04→05`/`08→01` foram conferidas pelo coordenador; ambos os `revisao.json` estão aprovados. O rastreamento de juntas ocultas continua sendo estimativa visual. O
rastreamento pós-edição mede a extremidade visível dos calçados; quadris,
joelhos e tornozelos encobertos pela calça continuam estimativas visuais.
