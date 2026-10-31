# Revisão de contatos e passagens

01 ambos: braço próximo permanece à frente junto da perna; três tentativas. Ícaro também trocou pulseira para distante e t2 duplicou braço. Reprovado, coordenador informado.
05 ambos: alternância de pernas legível e braço próximo à frente. Ícaro mantém pulseira próxima.
03 ambos: pé distante elevado ainda atrás à direita, não em passagem sob quadril. Duas tentativas; preservar pendência.
07 ambos: pé próximo elevado mas também atrasado. Ainda sugere recepção, não passagem. Não aprovar.

Continuar fases independentes usando somente bases e guias, sem derivar das fases defeituosas. Nenhum ciclo aprovado.

## Retomada de 23/10/2026

- Ícaro 01/08: pulseira transferida do pulso direito distante para o pulso esquerdo anatômico com pixels da própria fase 05. O recorte foi conferido nas pranchas de fundos claro e escuro. O contrabalanço dos braços continua errado e as fases seguem reprovadas.
- Ícaro e Eva 03/07: composição local do pé em passagem testada com deslocamento por vizinho mais próximo. O pé ficou parcialmente oculto ou cobriu a sola do apoio; a perna perdeu continuidade. Ensaios em `ensaios-reprovados/`, células finais preservadas.
- Ícaro e Eva 06: composição do contato direito da fase 05 produziu corte horizontal na cintura. Rejeitada; células finais preservadas.
- 01/08: tentativa de compor braços por recorte do tronco e por translação de membros gerou punhos cortados, contornos fantasmas ou mão na cintura. Rejeitada. A geração dirigida de Ícaro 01 voltou a pôr a pulseira no braço direito, também rejeitada.
- Os originais das 16 células estão em `../originais/`. `corrigir-pulseira.py` é a única edição promovida. `atualizar-qa.py` atualiza pranchas, GIFs e hashes sem aprovar o ciclo.
- Os GIFs de 100 e 400 ms foram regenerados e validados com oito quadros e duração correta; a prancha e o perfil de apoio ainda mostram passada irregular. A inspeção temporal contínua com chão marcado segue pendente. `revisao.json` permanece `aprovado: false` nos dois personagens.

## Diagnóstico independente de 24/10/2026

- Reabri as 16 células ativas, os guias 01/03/06/07/08 e os ensaios rejeitados. Nos dois personagens, 01/08 mantêm braço próximo avançado com a perna esquerda; 03/07 mantêm o pé suspenso atrás da passagem sob o quadril; 06 conserva a silhueta de apoio da perna esquerda quando o guia requer a direita.
- Os recortes anteriores de tronco e de perna foram confrontados novamente com os PNGs: o braço transplantado termina na cintura, e aproximar o pé abre um corte escuro ou oculta o tornozelo. Não se promoveu uma variação com erro de contorno ou oclusão duvidosa.
- `../gerar-previa-chao.py` criou prévias com malha móvel, âncora `(192,480)` e deslocamento do guia `(-12,728,-4,455)` por quadro. Pranchas dos dois personagens em `chao-marcado/` foram inspecionadas. Elas evidenciam salto de pose em 04→05/08→01 e recuo de apoio inconsistente.
- `../registrar-diagnostico.py` confirmou para cada personagem oito PNGs distintos RGBA 384×512 e GIFs de chão com oito quadros de 100/400 ms; hashes, bounding boxes e defeitos estão em `diagnostico-2026-10-24.json`.
- Nenhum PNG de produção foi alterado nesta retomada. Mantive `aprovado: false`. O ciclo requer reautoria de membros inteira, com desenho contínuo de ombro a mão e de quadril a pé; novo deslocamento simples de recorte repetiria os defeitos documentados.
