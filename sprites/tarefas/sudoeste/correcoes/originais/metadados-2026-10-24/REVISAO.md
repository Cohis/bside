# Sudoeste — correção localizada de 23/out/2026

As 16 células existem em RGBA 384×512. Foram selecionadas quatro correções: Ícaro 02 e 07, Eva 02 e 03. Os PNGs e JSONs anteriores desses quadros estão em `correcoes/originais/`; as gerações originais em `raws/` permanecem intactas. `correcoes/correcoes-selecionadas.json` registra candidatos aceitos e rejeitados. As pranchas clara/escura e os GIFs de 100/400 ms foram refeitos com as quatro células atualizadas.

Ícaro 07 usa a perna elevada corrigida e o apoio original, compostos com pixels do próprio personagem sem espelhar a pulseira. A sola elevada desceu aproximadamente 19 px. Eva 03 recebeu perna de balanço reconstruída e composição local; a sola desceu aproximadamente 23 px. A diferença de elevação 03/07 da Eva caiu de cerca de 38 para 14 px. Ícaro 02 e Eva 02 ganharam flexão de joelho na recepção com escala e sola próximas das anteriores. Candidatos de 06 foram rejeitados: encurtavam a figura ou deslocavam o apoio.

Verificação técnica: 16 PNGs com alpha, margens válidas e sem duplicatas exatas; GIFs com oito quadros nas durações declaradas. Inspeção estática feita nas pranchas sobre claro e escuro. A reprodução contínua no navegador não foi verificada porque a política de URL bloqueou a abertura local dos GIFs. Não contornar esse bloqueio.

O teste estático de chão em `teste-chao.json` aplica o deslocamento projetado do guia aos pontos de apoio estimados. A ponta de apoio varia em x aproximadamente 82/91 px no Ícaro e 85/84 px na Eva entre as duas metades do ciclo. Esse deslizamento é grande e não se corrige movendo a figura inteira; as pernas e os avanços 04/08 ainda precisam de redesenho. As juntas sob a roupa são estimativas visuais, não medições garantidas.

**Ambos os ciclos continuam reprovados e não estão prontos para a folha final.** Consulte `icaro/revisao.json` e `eva/revisao.json` para as pendências específicas. `exportar.py` bloqueia execução acidental sobre as composições selecionadas; use `correcoes/aplicar.py` para refazer pranchas e GIFs sem perder essas correções.
