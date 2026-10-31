# Validação das spritesheets

Em produção. As bases não representam ciclos de caminhada aprovados.

| Personagem | Direção | Quadros | Revisão visual |
|---|---|---|---|
| icaro | norte | 9/9 | aprovada |
| icaro | nordeste | 9/9 | pendente |
| icaro | leste | 9/9 | aprovada |
| icaro | sudeste | 9/9 | pendente |
| icaro | sul | 9/9 | aprovada |
| icaro | sudoeste | 9/9 | pendente |
| icaro | oeste | 9/9 | pendente |
| icaro | noroeste | 9/9 | pendente |
| eva | norte | 9/9 | aprovada |
| eva | nordeste | 9/9 | pendente |
| eva | leste | 9/9 | aprovada |
| eva | sudeste | 9/9 | pendente |
| eva | sul | 9/9 | aprovada |
| eva | sudoeste | 9/9 | pendente |
| eva | oeste | 9/9 | pendente |
| eva | noroeste | 9/9 | pendente |

Verificação técnica: dimensões, RGBA, transparência, margem, células vazias e duplicação exata. Anatomia, paleta, estabilidade temporal e patinação exigem revisão visual independente.

## Pendências por ciclo

### icaro · nordeste

- 01 permanece com pé esquerdo aparente atrás/à esquerda e o outro pé suspenso, contrário ao contato esquerdo do guia.
- 08 mostra pés separados (~145/255px) em vez da passagem para contato (~200px); 08→01 salta e não fecha anatomicamente.
- 04/05 braços ainda não acompanham de forma inequívoca o avanço da perna oposta; comprimento aparente das pernas varia.
- A passagem07 melhorou, mas 07→08 inverte projeção dos pés abruptamente; joelho e identidade anatômica seguem incertos.
- Recuo do apoio e piso marcado não calibrados; há patinação/variação entre fases.
- Reautorias image_gen de 01/08 ignoraram o guia; composição experimental criou corte na cintura e foi rejeitada.
- Nova composição controlada 01/08 rejeitada: 01 afina/rompe o contorno das pernas e fragmenta calçado; 08 transplanta a fase 07 quase imóvel, com costura residual e sem fechar 08→01. Ativos preservados; hashes em correcoes/originais-01-08-2026-10-24/manifesto.json.

### icaro · sudeste

- 02→03 altera extensão dos braços abruptamente; 07→08 muda a oclusão do braço distante.
- Largura do tronco e proporção aparente das pernas oscilam entre gerações; confirmar continuidade em reprodução temporal.
- Recuo horizontal estimado agora 34/48/47/43/43/42 px; confirmar com chão marcado e inspeção temporal antes de aprovar.

### icaro · sudoeste

- Ícaro07: composição baixou o pé de balanço cerca de19px e eliminou a marcha mais exagerada, mas a continuidade06→07→08 ainda exige revisão temporal independente.
- Recepção02 tem joelho de apoio mais flexo;06 permaneceu original porque candidato encurtou a figura cerca de23px.
- Na prévia atual, apoio 03→04 recua 38 px em x versus cerca de 41 px esperados; manter 04. O apoio aparente 07→08 diverge do guia, mas o rastreamento pode trocar a identidade das solas; duas tentativas localizadas de 08 rejeitadas por não resolverem a postura.
- Teste de chão permanece reprovado: a variação das amostras em x/y e a incerteza de apoio exigem revisão temporal real e nova construção anatômica da passagem 07→08.
- Terceira reautoria 08 rejeitada após prancha 07→08→01 com chão e GIFs de ensaio: ambas as solas continuam baixas/separadas, apoio direito não é inequívoco e balanço esquerdo não se eleva. Limite de três tentativas atingido; ativos preservados.

### icaro · oeste

- O resíduo do pé de apoio contra chão móvel ainda chega a 15–18 px em alguns meios-ciclos, comparável à incerteza do rastreio; patinação não pode ser descartada.
- Após baixar o membro em balanço inteiro em 03/07, o joelho parece menos alto em prancha, mas a naturalidade da passagem e a separação perceptiva da sola perto do apoio ainda precisam de validação em movimento contínuo.
- Ensaio de abaixar ainda mais a coxa/joelho foi rejeitado: achatou e alongou a pantalona e aproximou o calçado do apoio; ver edicoes/avaliacao-coxa-baixa.json. Os quadros atuais continuam sem aprovação anatômica.

### icaro · noroeste

- 01/08: lateral anatômica da pulseira corrigida, mas ambos os braços ainda avançam no mesmo sentido da perna próxima; contrabalanço reprovado.
- 01: braço próximo avança junto com perna próxima; três tentativas, requer novo diagnóstico antes de outra geração.
- 03/07: pé em balanço permanece atrás; passagem sob quadril não alcançada.
- 06: perna próxima continua à frente, não sustenta com a direita conforme fase requerida.
- 08: braço próximo continua avançado junto da perna próxima.
- Apoio e comprimento aparente variam, particularmente04→05 e07→08.
- Escala fixa pelo topo/cabeça preserva pixels mas revela variação residual de volume e altura gerada; verificar em comparação com base.
- Loop contínuo e chão marcado ainda não aprovados; GIFs são recursos de inspeção, não prova de aprovação.
- Reconstruções locais de 03/07 e 06 foram rejeitadas: geraram sobreposição, pé oculto ou corte de cintura/contorno. PNGs originais dessas fases preservados.

### eva · nordeste

- 01 ainda põe perna esquerda aparente atrás/à esquerda do contato projetado no guia; 08→01 troca a posição dos pés abruptamente.
- 08 mantém pés muito separados e identidade do apoio incerta; candidato image_gen de 08 sobrepôs pés sem apoio legível.
- O braço distante de 04–06 e o contrabalanço com a perna oposta ainda não foram validados.
- 07 melhorou como passagem, mas 07→08 tem salto na projeção e possível fusão visual da calça.
- Recuo do apoio e piso marcado não calibrados; há patinação/variação entre fases.
- Reautorias image_gen de 01/08 não resolveram o lado anatômico do contato.
- Nova composição controlada 01/08 rejeitada: 01 afina/rompe o contorno das pernas e fragmenta calçado; 08 transplanta a fase 07 quase imóvel, com costura residual e sem fechar 08→01. Ativos preservados; hashes em correcoes/originais-01-08-2026-10-24/manifesto.json.

### eva · sudeste

- 03 ainda projeta o pé direito em balanço perto do avanço 04; candidato de composição manual foi rejeitado por fundir pés.
- 07 melhorou a altura do joelho, mas sua passagem e a sequência 06→07→08 ainda exigem revisão temporal.
- Balanço dos braços e proporção aparente das pernas ainda oscilam entre fases.
- Recuo horizontal estimado agora 41/44/57/40/40/39 px; confirmar com chão marcado e inspeção temporal antes de aprovar.

### eva · sudoeste

- Eva03: composição baixou o pé de balanço cerca de23px; diferença residual de elevação em relação07 é aproximadamente14px e requer revisão temporal.
- Recepção02 tem flexão melhor;06 permaneceu original porque candidato alterou escala/chão. Proporção da perna02 e extensão08 ainda variam.
- Na prévia atual, apoio 03→04 recua 39 px em x versus cerca de 41 px esperados; manter 04. O apoio aparente 07→08 diverge do guia, mas o rastreamento pode trocar a identidade das solas; duas tentativas localizadas de 08 rejeitadas por não resolverem a postura.
- Teste de chão permanece reprovado: a variação das amostras em x/y e a incerteza de apoio exigem revisão temporal real e nova construção anatômica da passagem 07→08.
- Terceira reautoria 08 rejeitada após prancha 07→08→01 com chão e GIFs de ensaio: ambas as solas continuam baixas/separadas, apoio direito não é inequívoco e balanço esquerdo não se eleva. Limite de três tentativas atingido; ativos preservados.

### eva · oeste

- O resíduo do pé de apoio contra chão móvel ainda chega a 15–18 px em alguns meios-ciclos, comparável à incerteza do rastreio; patinação não pode ser descartada.
- Eva 02 parece variar de escala na prancha, embora largura medida da cabeça (190 px) esteja na faixa vizinha 181–192; não há base para redimensionamento uniforme.
- Após baixar o membro em balanço inteiro em 03/07, o joelho parece menos alto em prancha, mas a naturalidade da passagem e a separação perceptiva da sola perto do apoio ainda precisam de validação em movimento contínuo.
- Ensaio de abaixar ainda mais a coxa/joelho foi rejeitado: achatou e alongou a pantalona e aproximou o calçado do apoio; ver edicoes/avaliacao-coxa-baixa.json. Os quadros atuais continuam sem aprovação anatômica.

### eva · noroeste

- 01: braço próximo avança junto com perna próxima; três tentativas, requer novo diagnóstico antes de outra geração.
- 03/07: pé em balanço permanece atrás; passagem sob quadril não alcançada.
- 06: perna próxima continua à frente, não sustenta com a direita conforme fase requerida.
- 08: braço próximo continua avançado junto da perna próxima.
- Apoio e comprimento aparente variam, particularmente04→05 e07→08.
- Escala fixa pelo topo/cabeça preserva pixels mas revela variação residual de volume e altura gerada; verificar em comparação com base.
- Loop contínuo e chão marcado ainda não aprovados; GIFs são recursos de inspeção, não prova de aprovação.
- Reconstruções locais de 03/07 e 06 não preservaram o desenho: pé oculto/sobreposto e corte de cintura; não substituídas.

