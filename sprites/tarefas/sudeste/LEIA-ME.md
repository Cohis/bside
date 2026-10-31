# Sudeste — pacote para revisão

16 PNGs individuais RGBA384×512 exportados em icaro/ e eva/. Todas as células têm transparência real, margens e pixels distintos.21 gerações brutas preservadas; prompts completos em prompts/, seleção em selecionados.json. Ferramenta artística: image_gen embutida, um personagem/quadro por chamada.

Os primeiros pedidos01 repetiram o contato direito do recorte; foram reclassificados como05 após inspeção anatômica. As versões01 posteriores corrigiram pernas. Eva01-t2 introduziu pulseira indevida, removida em01-t3. Eva07 inicialmente repetiu direita em balanço; a terceira versão, sem recorte de caminhada, corrigiu a lateral. Ícaro08 inicial mostrou conexão anômala do braço distante; versão08-t2 passou a ocultá-lo. Eva08 inicial repetiu contato direito;08-t2 corrigiu a perna avançada.

Enquadramento reproduzível por enquadrar.py: escala uniforme pelo tamanho estimado da cabeça, translação, NEAREST e remoção somente de alfa<8. Não forçar todas as solas ao mesmo chão preserva e revela falhas de proporção/projeção da geração. revisar.py grava rastreamento visual estimado e pendências. Não confundir pontos estimados sob a calça com medidas anatômicas exatas.

As duas revisões estão **não aprovadas**. Ícaro02 tem compressão excessiva do corpo;07 ainda parece retirada posterior do pé. Eva03 está adiantada demais para passagem;07 tem elevação excessiva. Há inconsistência de recuo do apoio e proporção de torso/pernas. Pranchas claras/escuras foram inspecionadas; GIFs100/400ms estão preparados, mas revisão temporal contínua e chão marcado ainda precisam ocorrer. As transições04→05 e08→01 foram comparadas estaticamente, sem aprovação. Não liberar montagem final com estes registros.

## Rodada corretiva de 23/out/2026

Os quadros originais substituídos foram copiados para `originais-pre-correcao/`. Foram aceitas
melhoras parciais em Ícaro 02 e 07 e Eva 03. Os brutos e prompts integrais estão em `raw/`
e `geracoes-correcao.json`; `selecionados.json` aponta para as versões atuais. Os candidatos
Eva 03-t2 e 07-t4 foram rejeitados após inspeção: o primeiro manteve o pé adiantado; o
segundo repetiu uma fase de avanço. O candidato `icaro-02-apoio-x.png` também foi
inspecionado e não selecionado, pois manteve o torso curto.

`validar_saida.py` atualiza `tecnica.json`, pranchas claras/escuras com chão y480 e GIFs
100/400ms a partir dos PNGs atuais. As pranchas foram inspecionadas nos dois fundos.
Cada personagem tem oito células RGBA 384×512 distintas, transparentes e com margens.
As transições 04→05 e 08→01 foram comparadas quadro a quadro. O solo ainda oscila: em
Ícaro, 01/04/08 ficam 9/12/17px acima e 03/05 avançam 4/3px abaixo; em Eva, 01/04/07
avançam 9/14/22px abaixo. O recuo estimado do apoio também segue irregular. A revisão
continua **não aprovada**; `revisao.json` registra as pendências por personagem. Os GIFs
regenerados permitem conferir ritmo, mas não constituem aprovação de reprodução temporal.

Não execute `enquadrar.py` ou `revisar.py` sobre este pacote corrigido: ambos são registros
históricos da primeira exportação e reescreveriam quadros/medições antigas. Use apenas
`validar_saida.py` para atualizar artefatos técnicos sem tocar nos PNGs individuais.

## Nova revisão localizada de 23/out/2026

O coordenador pode revisar os PNGs atuais; **Ícaro e Eva continuam não aprovados**.

- `candidatos_solo.py` testou e `aplicar_solo.py` adotou remapeamento vertical nearest abaixo de y330 (Ícaro) e y324 (Eva) em 13 células. Os 16 contatos inferiores terminam agora em y480. Originais em `originais-pre-solo/`, hashes e desvios em `correcao-solo.json`.
- `candidatos_apoio_02.py` testou e `aplicar_apoio_02.py` adotou recuo local progressivo do pé esquerdo de apoio em Ícaro 02 (−23 px) e Eva 02 (−24 px). Antes/apos e hashes em `originais-pre-apoio02/` e `correcao-apoio02.json`.
- `candidato_eva07_joelho.py` baixou localmente o joelho esquerdo de Eva 07 (pico 18 px), sem costuras aparentes na inspeção 3×. Célula anterior e hashes em `originais-pre-joelho07/` e `correcao-joelho07.json`.
- `candidato_eva03_passagem.py` **não foi adotado**: a composição funde os calçados na prancha 02–04. Não repetir sem outro diagnóstico.
- `validar_saida.py` regenerou pranchas claras/escuras e GIFs 100/400 ms com linha y480 e marcas móveis a 24 px/fase. Esta velocidade é só teste, sem calibração aprovada. `registrar_solo.py` transferiu as estimativas de rastreamento; pontos anatômicos sob a roupa ainda têm incerteza.
- Permanecem recuo desigual/patinação possível, Eva 03 próxima demais de 04, continuidade de braços e proporções. As transições 04→05/08→01 foram comparadas estaticamente; aprovação temporal fica aberta em `revisao.json`.

## Diagnóstico adicional de Eva 03 em 24/out/2026

Duas reautorias dirigidas por `image_gen` foram normalizadas sem suavização como `candidato-eva-03-t4.png` e `candidato-eva-03-t5.png`; raws e transformações estão preservados na pasta. As instruções usaram a base de Eva sudeste, o guia 03 e as fases 02/03/04, buscando aproximar o pé direito suspenso da perna de apoio. Ambas foram **rejeitadas**: trocaram visualmente a identidade do pé esquerdo de apoio para a posição adiantada (x≈260), enquanto o rastreamento desse apoio nas fases 01/02/04 recua x≈275→234→133. Promover qualquer uma criaria um salto anatômico e patinação na transição. O `eva/03.png` ativo e seu rastreamento foram preservados; a passagem continua pendente de redesenho que mantenha o apoio esquerdo na trajetória existente.

## Recuo do apoio em 06/07 — 24/out/2026

`testar_recuo_06_07.py` ensaiou remapeamento horizontal progressivo, sem interpolação, nos quadros 06/07. A primeira variante 07, com máscara poligonal, foi **rejeitada**: deixou cortes verticais e resíduos nas pernas; permanece em `candidatos-recuo-06-07/*-07-candidato.png`. A variante 07 com a faixa inferior inteira e a variante 06 com a perna de apoio isolada passaram na comparação em tamanho natural e ampliação 2×, sem costura visível. Foram adotadas para ambos os personagens por `aplicar_recuo_06_07.py`. Versões anteriores em `originais-pre-recuo-06-07/`, hashes em `recuo-06-07-adotado.json`.

Estimativas horizontais dos pés de apoio nas duas metades do ciclo: Ícaro 34/48/47 e 42/44/42 px por transição; Eva 41/44/57 e 38/42/39 px. As fases 05–08 melhoraram, mas a primeira metade de Eva segue irregular. As estimativas anatômicas em `rastreamento.json` foram transferidas pela mesma função de remapeamento. `validar_saida.py` regenerou pranchas e GIFs. **Ambos os ciclos permanecem não aprovados** até revisão temporal integral e correção da passagem Eva 03, dos braços e das oscilações de proporção apontadas em `revisao.json`.
