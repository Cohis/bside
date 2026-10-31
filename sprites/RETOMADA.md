# Estado da produção

## Concluído

- Referências recortadas nas oito direções; originais intactos e hashes registrados.
- 16 bases paradas revisadas em `bases/`, todas 384 × 512. Correções: pulseira de Ícaro no leste e orientação noroeste.
- Contrato, ficha visual, paletas medidas e 64 guias anatômicos PNG/JSON.
- Rotina de enquadramento uniforme sem suavização e rotina de montagem com bloqueio de imagens ausentes/duplicadas ou revisão pendente.
- Prévia em `final/previa.html`, com controles testados em Brave headless. Evidência: `registros/verificacao-previa.json` e `registros/previa-testada.png`.
- Montagem testada em fixture isolada em `/tmp/aoc-montagem-teste-1n4sorls`: 144 células, alfa127 preservado, retângulos conferidos, duplicata bloqueada. Nenhum desenho da fixture pertence à entrega.

## Como conferir o disco

Execute `python sprites/scripts/inventariar.py` para atualizar `registros/inventario-atual.json`. O inventário confere a integridade dos originais e das16 bases, lista quadros faltantes e não conta raws/candidatos como células prontas.

## Em andamento

Primeira onda completa em produção: 48 quadros de caminhada (leste, sul, norte), com PNGs e registros. As seis revisões de personagem/direção permanecem NÃO aprovadas. Leste: passagem07 e recuo desigual; norte: projeção/recepção e recuo inconsistentes; sul: impulso irregular e revisão temporal pendente. Ver revisao.json em cada pasta.

Segunda onda iniciada: agentes direcao_oeste, direcao_sudeste e direcao_nordeste, ambos os personagens por direção. Não regenerar arquivos existentes sem inspecionar os registros. Terceira onda ainda por iniciar: sudoeste e noroeste.

Prévia atualizada com rastreamento estimado observado e pendências por ciclo;64 imagens passaram no teste de controles. Script `auditar_movimento.py` produz diagnóstico de recuo a partir das medições/estimativas, sem aprovar anatomia.

Correção diagnosticada de Ícaro/norte02 preservada separada: melhora recepção, mas apoio se move no sentido errado. Não substituiu o quadro anterior.

Correção diagnosticada de Ícaro/leste07 em registros/correcoes/ foi gerada e rejeitada: exagerou elevação e avanço do pé. O candidato foi preservado separado; não substituiu o quadro selecionado.

## Finalização

1. Revisar 16 ciclos, inclusive04→05 e08→01, transparência, anatomia, identidade, escala e patinação. Pedir correções localizadas; após3 falhas do mesmo defeito registrar diagnóstico.
2. Integrar rastreamento de juntas/pés e passada de teste medida de cada agente.
3. `python sprites/scripts/montar.py --previa` atualiza a prévia sem produzir folhas finais incompletas.
4. `python sprites/scripts/montar.py` só libera as duas folhas completas quando todos os144 quadros e as16 revisões aprovadas estiverem presentes.
5. Repetir verificação da prévia sobre os arquivos finais, inspecionar loops e registrar limitações reais em `final/validacao.md`.

Não apresentar a entrega como concluída enquanto faltarem ciclos ou revisões. Bases não são caminhada.

## Retomada22/out

Usuário pediu percentual e continuidade. Inventário às12:06UTC:16 bases+48 células de caminhada=64/144 (44,4% dos quadros formatados);0/16 ciclos com aprovação visual final. Infraestrutura pronta. Oeste22PNGs, sudeste21 e nordeste18 incluindo raws/tentativas, ainda sem células exportadas naquele instante. Três agentes retomados para finalizar fases faltantes e exportar sem repetir material existente.

Em22/out, na inspeção do noroeste, a pulseira da base Ícaro foi corrigida para o pulso esquerdo anatômico antes das animações. Raw e base anterior preservados em registros/geracoes; bases/congeladas.json e ficha-visual.md atualizados, integridade verificada. Sudoeste e noroeste foram iniciados como terceira onda.

## Estado final técnico em22/out

`python sprites/scripts/inventariar.py`: 144/144 células disponíveis, originais e bases íntegros,0/16 ciclos visualmente aprovados. `python sprites/scripts/montar.py --rascunho`: duas folhas de revisão3456×4096 em `sprites/revisao/`,144 arquivos individuais e `animacoes-rascunho.json`; nenhuma folha final liberada. `python sprites/scripts/montar.py` bloqueia com16 revisões pendentes. Prévia testada com144 imagens e nenhum erro JavaScript. A correção artística por image_gen esgotou3 tentativas em defeitos específicos de várias direções e segue sem controle anatômico suficiente. Aguardando resposta do usuário sobre permitir edição controlada quadro a quadro, que altera a regra de geração artística do plano. Não registrar essa pergunta como autorização.

Em23/out, o inventário continua em144/144 e0/16. Houve segunda tentativa localizada de Ícaro/sul04, com a base e o guia explícitos, mas o gerador retornou quase dois pés plantados em vez do avanço direito. Candidato preservado em `registros/correcoes/icaro-sul-04-tentativa2.png` e rejeitado; nenhuma célula nem folha foi trocada. Diagnóstico em `registros/revisao-coordenacao.md`.

## Retomada após autorização para edição manual — 23/out

O usuário autorizou edição controlada de pixels e pediu correções de todos os erros identificados. Não solicitar nova autorização para essas correções. Exigir cópia original e registro para cada alteração; não marcar ciclo como aprovado sem inspecionar o loop, inclusive04→05 e08→01, além do teste com chão marcado.

Estado atual: **144/144 quadros disponíveis, 6/16 ciclos aprovados (37,5% dos ciclos)**. Norte, sul e leste estão aprovados para ambos os personagens. Leste recebeu ajustes locais de apoio em02/04/06/07, com imagens anteriores e hashes em `tarefas/leste/registros/edicoes/antes-correcao-apoio-2026-10-23/`; um candidato de03 foi rejeitado ao piorar o deslizamento. A revisão visual de leste usou reprodução100/400ms e chão marcado. Prévia geral em `final/previa.html` testada para personagem/direção, caminhada, velocidade lenta, pausa, avanço de quadro e deslocamento no chão.

Correções ainda parciais e não aprovadas: sudeste, sudoeste, oeste, noroeste e nordeste, ambos personagens. Os agentes registraram candidatos e rejeições nos diretórios por direção; consultar `revisao.json` e `LEIA-ME.md` antes de retomar. Noroeste corrigiu a pulseira de Ícaro01/08 mas mantém problemas nos pés03/07, apoio06 e braços. Sudeste substituiu alguns candidatos por versões parcialmente melhores, mas Eva03/07 e patinação persistem. Oeste recebeu ajustes em Eva02/06 e variantes de passagem03/07, ainda com joelhos altos e apoio irregular. Sudoeste precisa reduzir/igualar passagens03/07 e revisar recepções; não repetir geração sem diagnóstico após tentativas rejeitadas. Nordeste segue corrigindo acessórios e pernas; guias e candidatos já foram reavaliados após limpeza de alfa residual.

`montar.py --previa` e `auditar_movimento.py` foram atualizados após as correções. `montar.py --rascunho` regenerou folhas3456×4096 em `revisao/`, explicitamente não aprovadas. **Não executar montagem final até as 16 revisões aprovadas**; atualmente `final/` contém a prévia e o registro, não as duas spritesheets finais nem `animacoes.json` final.

## Continuação de 24/out

Inventário confirmado: **144/144 células presentes e 6/16 ciclos aprovados**. A prévia e as folhas de rascunho foram regeneradas; `montar.py --rascunho` informou dez revisões pendentes. Os arquivos finais continuam bloqueados.

- Sudeste: rejeitadas duas reautorias de Eva03 que trocavam o pé de apoio de lado. Ajustados 06/07 de ambos para recuo horizontal mais uniforme; a primeira variante de 07 foi descartada por cortar as pernas. PNGs anteriores, candidatos, hashes e medidas estão em `tarefas/sudeste/`. Revisões ainda falsas por passagem Eva03, braços e continuidade temporal.
- Oeste: 03/07 de ambos foram rearticulados para baixar joelho e sola, com originais e hashes em `tarefas/oeste/edicoes/`. Inspeção do coordenador ainda encontrou joelhos excessivamente elevados; nova correção localizada em andamento. Nenhuma aprovação nova.
- Nordeste: ensaios de enxerto integral de pernas em 01/08 dos dois personagens foram rejeitados por cortes e ausência de avanço. Produção ativa preservada; requer desenho anatômico novo. Registros em `tarefas/nordeste/correcoes/`.
- Noroeste: Ícaro01/08 ganhou candidatos de braços anatomicamente corretos, ainda não promovidos porque 02/07 interromperiam a continuidade. Eva01/08 testados e rejeitados por lado de braço/bolso novo. Reautoria segue em andamento na pasta.
- Sudoeste: recálculo de apoio com passada real revelou patinação concentrada em 07→08; novas tentativas localizadas em andamento. Não declarar aprovado.

Próxima ação: revisar resultados das três direções em andamento e os loops com chão marcado, mantendo `revisao.json` falso se qualquer defeito anatômico ou temporal permanecer. Não usar presença dos 144 PNGs como sinônimo de conclusão.

## Verificação de 25/out

Após a última rodada, foram executados `inventariar.py`, `auditar_movimento.py`, `montar.py --previa` e `montar.py --rascunho`. Resultado: 16 bases, 128 células de caminhada, rastreamento presente nos 16 ciclos e **6/16 aprovados**; a prévia e os rascunhos registram dez pendências. A montagem final continua corretamente bloqueada.

Oeste rejeitou novas deformações de coxa/joelho: produziram calça tubular, dobra angular ou calçados fundidos. Nordeste 01/08 e Sudoeste 08 alcançaram o limite de três tentativas sem solução anatômica limpa; seus PNGs de produção foram preservados e as causas estão nos registros por direção. Não repetir a mesma classe de geração/deformação sem uma referência artística nova ou redesenho manual especializado.
