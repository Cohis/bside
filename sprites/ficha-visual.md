# Ficha visual comum

Estado: 16 bases revisadas e congeladas em bases/congeladas.json. Animação liberada. Altura visual das bases: 424px; âncora comum (192,480). Correções aplicadas: lateral anatômica da pulseira no leste e no noroeste de Ícaro; câmera noroeste revisada. A base noroeste anterior está preservada em registros/geracoes/.

Os originais têm 1536 × 1024, oito vistas em quatro colunas e duas linhas. Os recortes preservam RGBA e pixels sem alterações. Não são fases consecutivas de um ciclo.

## Identidade

- Ícaro: cabelo branco quente com sombras cinza/lilás, pele quente, olhos castanho/dourado; regata violeta escura, símbolo dourado na frente, calça grafite larga e tênis escuros com detalhes amarelos e sola clara.
- Pulseira do Ícaro: **pulso esquerdo anatômico**. Na vista frontal aparece à direita da tela; na traseira aparece à esquerda. Não espelhar as vistas.
- Eva: cabelo quase preto com sombras frias e rabo de cavalo longo; olhos azuis, pele clara quente, brinco vermelho visível nas vistas laterais; blusa branca curta, mangas compridas e capuz, calça cinza larga, tênis escuros com sola clara.
- As vistas não estabelecem de forma inequívoca se o brinco de Eva é unilateral. Preservar a visibilidade da vista correspondente, sem inventar bijuterias nas regiões ocultas.
- Ambos têm altura corporal semelhante nas referências. A altura nominal das bases será 424 pixels, com eixo no x192 e chão y480; cabelos e roupas mantêm suas diferenças de volume.
- Contorno muito escuro, blocos de pixels definidos e luz difusa superior; sem nova fonte de luz. Sem sombra de chão ou halo luminoso. A pulseira mantém o amarelo emissivo dentro do acessório, sem halo externo.

## Exportação

384 × 512 por quadro. Quadro 00 parado, quadros 01–08 de caminhada. Âncora (192,480). Não espelhar, deformar partes ou usar interpolação suave. Se a geração vier maior, apenas escala uniforme da figura inteira por vizinho mais próximo, registrada no JSON da transformação. Remover apenas ruído quase invisível alfa < 8/255; resíduos maiores exigem nova geração.

Nenhuma referência isolada determina o lado anatômico por posição na tela. Usar o mapeamento frontal/traseiro e os guias. Não adicionar detalhes ocultos.
