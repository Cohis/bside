# Reautoria focal 01/08 — prompts e referências

Modo: `image_gen`, uma célula por solicitação, `transparent_background=true`. Todos os quatro resultados foram rejeitados; as imagens estão preservadas como `*-imagegen-rejeitado.png`. Esses prompts foram usados como instrução artística integral para os quatro candidatos.

## Ícaro 01

Referências: `sprites/bases/icaro/nordeste.png`, `sprites/guias/nordeste/01.png`.

> Produza SOMENTE Ícaro, direção NORDESTE (diagonal de costas, rosto olhando para a direita da tela), quadro 01 CONTATO ESQUERDO de caminhada no lugar. Imagem 1 é base fixa de identidade/câmera/escala/paleta; Imagem 2 é guia anatômico esquemático (laranja perna esquerda, azul direita), não copiar desenho ou textos. Preserve cabelo branco, regata violeta, calça grafite larga, tênis amarelo/escuro, pele, contorno pixelado. Pulseira luminosa APENAS no pulso ESQUERDO ANATÔMICO, que aparece à esquerda da tela nesta vista de costas; nunca no braço próximo à direita. Pose de dois contatos: pé esquerdo anatômico à frente da caminhada, projetado mais à direita/atrás no espaço visual do sprite, toca o chão com calcanhar; pé direito atrás termina impulso com ponta tocando chão. Não faça pé esquerdo longe à esquerda com o direito erguido. Perna esquerda avança, braço direito acompanha à frente; braço esquerdo recua. Pelo menos um pé firmemente apoiado, sem salto. Corpo inteiro, altura da figura cerca de 424 px ao ajustar numa célula 384x512, cabeça e torso iguais à base, âncora de chão (192,480). Fundo transparente real, sem sombra, sem suavização, sem texto, um único personagem. Arte pixel rígida, sem membros extras.

## Ícaro 08

Referências: `sprites/bases/icaro/nordeste.png`, `sprites/guias/nordeste/08.png`.

> Produza SOMENTE Ícaro, direção NORDESTE (diagonal de costas, olhando para a direita da tela), quadro 08 AVANÇO ESQUERDO de caminhada no lugar. Imagem 1 base fixa define identidade, paleta, pixel art e escala; imagem 2 é somente guia anatômico de pose, laranja=perna esquerda anatômica e azul=direita, não copiar textos. A perna DIREITA está plantada no chão sob o quadril, com pé por volta de x200,y480; o pé DIREITO NÃO pode estar muito à esquerda nem erguido. A perna ESQUERDA avança pelo centro, pé esquerdo elevado cerca de 18 px, ponta por volta de x200,y450, logo acima e levemente à frente do direito, preparando contato no próximo quadro 01. Joelhos distintos, sem cruzar ou fundir os pés. Braço DIREITO anatômico (à direita da tela) avança oposto à perna esquerda; pulseira dourada só no pulso ESQUERDO anatômico, à esquerda da tela, sem mudar de lado. Cabelo branco, regata violeta, calça grafite larga, tênis escuros com amarelo, contorno pixelado igual à base. Figura inteira proporcional à base, altura nominal 424 px na célula384x512, âncora (192,480). Fundo transparente verdadeiro; sem chão desenhado, sem sombra, sem texto, sem outros objetos, sem suavização.

## Eva 01

Referências: `sprites/bases/eva/nordeste.png`, `sprites/guias/nordeste/01.png`.

> Produza SOMENTE Eva em pixel art, direção NORDESTE, quadro 01 CONTATO ESQUERDO de caminhada no lugar, diagonal vista de costas olhando para direita da tela. Imagem1 é a base fixa de identidade, proporções, rabo de cavalo longo, olhos azuis, brinco vermelho, blusa branca curta com capuz, calça cinza larga e tênis escuros de sola clara. Imagem2 é guia anatômico (laranja=esquerda anatômica, azul=direita) somente para pose, não copiar linhas/textos. PERNAS: pé esquerdo anatômico à FRENTE, projetado perto do centro/direita da figura (x~214 após normalizar para 384x512), calcanhar tocando chão; pé direito atrás perto do centro (x~188), ponta tocando o chão e terminando impulso. Os DOIS pés têm contato nesta fase, nenhuma sola suspensa. Braço direito anatômico acompanha o avanço da perna esquerda, braço esquerdo recua. Não inverter pernas. Preserve câmera, escala, todas as roupas e acessórios; não fundir membros. Personagem inteiro em uma célula384x512, altura aparente424px, âncora de chão (192,480), transparente real sem cenário/sombra, arte pixel sem suavização, sem texto.

## Eva 08

Referências: `sprites/bases/eva/nordeste.png`, `sprites/guias/nordeste/08.png`.

> Produza SOMENTE Eva em pixel art, direção NORDESTE diagonal de costas olhando à direita da tela, quadro 08 AVANÇO ESQUERDO do ciclo. Imagem1 é a base fixa de identidade/proporção/câmera, Imagem2 é guia anatômico esquemático laranja=esquerda azul=direita. A perna DIREITA está em APOIO sob o centro do quadril: pé direito plantado por volta de x200,y480 após normalização384x512. A perna ESQUERDA está em BALANÇO AVANÇANDO para o próximo contato: joelho passa à frente do quadril e pé esquerdo elevado pouco, próximo ao outro pé por volta de x200,y450. Não faça a direita muito à esquerda e a esquerda muito à direita; os dois pés estão próximos mas não fundidos. Braço direito à frente oposto à esquerda que avança, braço esquerdo atrás. Preserve cabelo escuro com rabo de cavalo longo, brinco vermelho, olhos azuis, blusa branca curta com capuz, calça cinza larga, tênis escuros sola clara; não mudar lado ou número de acessórios. Corpo inteiro e escala da base, altura nominal424px em célula384x512, âncora(192,480), transparência real; sem sombra, sem cenário, sem texto, sem suavização, sem membros extras.
# Tentativa adicional do coordenador em 24/out/2026 — Ícaro 01

Referências: `sprites/bases/icaro/nordeste.png`, `sprites/guias/nordeste/01.png` e `sprites/tarefas/nordeste/icaro/05.png`. Pedido ao `image_gen`: reautorizar um quadro único Ícaro nordeste, contato **esquerdo**; a perna conectada ao lado da pulseira deveria avançar para a direita da tela e tocar o chão, enquanto a direita terminaria o impulso atrás. Braços opostos, pulseira mantida no punho esquerdo, escala e câmera da base, fundo transparente e pixel art sem suavização. Resultado salvo em `icaro-01-reautoria-2026-10-24-rejeitado.png`.

**Rejeitado:** apesar da instrução anatômica explícita, a perna do lado da pulseira ficou atrás (calçado à esquerda da tela) e a outra avançou à direita, repetindo a troca da fase 05. A célula ativa `icaro/01.png` não foi substituída; a revisão continua não aprovada. Nova tentativa com a mesma formulação não teria justificativa sem redesenho controlado da perna inteira.
