# Revisão independente do coordenador

## Bases

- Dezesseis bases revisadas. Ícaro leste teve a pulseira removida do braço direito próximo; o esquerdo fica oculto nessa pose. Ícaro noroeste foi regenerado porque a primeira tentativa olhava para o lado errado.
- Todas as bases mantêm 424px de altura nominal, eixo corporal/apoio em torno de x192 e chão y480, RGBA384×512. Isso não implica que cada pé em caminhada fique em y480.

## Primeira onda — em andamento

### Sul

- Prancha inicial01/03/05: o apoio em03 parecia congelado na profundidade de01. Alinhamento automático de toda sola mais baixa em480 apagava o recuo do apoio.
- Solicitação: preservar a cabeça/torso, corrigir passagens03/07 e usar pisos projetados distintos. Agente informou novas gerações: apoio480→467, cabeça56, escala da cabeça com variação residual aproximada de2–4px. Ainda requer revisão do ciclo completo.

### Leste

- Agente corrigiu Eva07 porque repetia a lateral em balanço de03.
- Revisão independente de01/03/05/07: os quadros07 mostram pé avançado e perna quase estendida, mais próximos de uma fase de avanço do que de passagem. Solicitado revisar e corrigir07 com pé elevado próximo à perna de apoio e flexão, conservando o anterior como referência possível de08. Ainda não aprovado pelo coordenador.

### Norte

- Agente corrigiu lado da pulseira e contrabalanço nos contatos. Informou passagens inspecionadas e enquadramento pelo eixo/cabeça, preservando profundidade. Aguardando ciclo completo para revisão independente.

Os relatos dos agentes acima não substituem aprovação final. Não há16 ciclos aprovados neste momento.

## Retomada de 21/out

- Reinspecionadas pranchas do sul: alternância presente, porém a transferência03→04 e07→08 concentra mudança de comprimento/projeção dos pés; aprovação mantida pendente.
- Ícaro/leste07 com guia explícito: candidato rejeitado por elevar demais o pé e deixar tornozelo à frente do quadril; braços não transitam como solicitado. Arquivos preservados em `correcoes/`.
- Ícaro/norte02 com instrução de movimento pequeno: candidato melhora o tipo de recepção, mas o apoio esquerdo vai de aproximadamente y458 no01 a y449, contrariando o recuo esperado. Comparação na mesma escala0,36, sem deformação. Não substituído.
- Prévia passou nos testes com64 imagens: ciclo01–08, parado fora do loop, pausa, passo, velocidade lenta, troca de personagem/direção, chão, rastreamento do sul e avisos de pendência. Zero erros de JavaScript. Testes de controles não aprovam anatomia.
- `auditoria-movimento.json` reúne o recuo estimado dos seis ciclos rastreados. Pontos sob roupa continuam explicitamente estimados.

## Segunda onda — revisão independente

- Oeste: Ícaro 04 e 08 apresentam encurtamento aparente da perna de apoio e as duas solas sobem em relação ao corpo; Eva 03 mostra o pé de passagem atrás e 07 se adianta, com mudanças de escala/cabelo entre quadros. Não aprovada mesmo com 16 PNGs tecnicamente válidos.
- Sudeste: Ícaro 02 comprime corpo e antecipa braços, 07 mantém pé de balanço atrás; Eva 03 já estende o passo, 07 eleva demais a perna. Os contatos alternam pernas, mas recuo e proporção do tronco variam. Não aprovada.
- Nordeste: Ícaro 02 apoio ambíguo e 04/06 mostram pulseira/trajeto incoerentes; Eva 04–06 braços mudam sem fase correspondente; ambas 07 ainda parecem recepção. Não aprovada.

As três direções foram incluídas na prévia. Seus `revisao.json` e rastreamentos especificam quadro e defeito; nenhuma pendência foi convertida em aprovação por montagem técnica. A auditoria de recuo está em `auditoria-movimento.json`, com medidas aproximadas e incerteza explícita.

## Terceira onda — ponto de controle

Base parada de Ícaro noroeste corrigida antes da geração da direção: pulseira no pulso esquerdo anatômico, à esquerda da tela; base anterior e raw preservados em `geracoes/`. Os agentes de sudoeste/noroeste iniciaram chaves, mas geração foi interrompida por capacidade temporária do modelo em 22/out. Raws existentes preservados; células finais ainda faltam. Ambos os agentes foram retomados a partir do disco, sem modificar os quadros anteriores.

- Sudoeste: na prancha final, Ícaro07 mantém joelho alto de marcha e contato/apoio não progride com regularidade até08. Eva03 tem joelho muito alto para passagem discreta; 03/07 e 04/08 mostram variação de largura e comprimento das pernas. A diferença não foi ocultada por escala individual. Ambos reprovados, conforme registros da direção.

- Noroeste: com base parada corrigida, Ícaro01 e08 voltam a levar pulseira ao pulso distante;01 repetiu contrabalanço errado após três tentativas. Ícaro e Eva03/07 mantêm pé de balanço atrás em vez de passagem,06 troca ou não estabiliza apoio. Ambos reprovados. Registro detalhado em tarefas/noroeste/{icaro,eva}/revisao.json.

## Fechamento técnico das 144 células

As16 poses paradas e128 imagens de caminhada existem como PNGs RGBA384×512, com transparência/margens e sem duplicação exata por direção. `montar.py --rascunho` gerou duas folhas3456×4096 em `sprites/revisao/`,144 quadros individuais e JSON marcado `rascunho_nao_aprovado`; a prévia carregou144 imagens, ciclo01–08, controles de pausa/velocidade e rastreamento, sem erro de JavaScript. `montar.py` sem modo rascunho bloqueou corretamente as folhas finais porque0/16 revisões visuais foram aprovadas. Isso é uma limitação artística documentada, não falha de formato/exportação. Não renomear rascunhos para entrega final sem revisão real.

## Retomada de 23/out — sul04

- Nova tentativa localizada para Ícaro/sul04, usando apenas o quadro04 atual, a base parada congelada e o guia04. A instrução pedia apoio esquerdo sob o quadril e pé direito em avanço baixo, ainda sem contato. O resultado colocou os dois pés quase plantados, mais próximo de uma pose neutra/duplo apoio do que do avanço04; não resolveu o salto do recuo03→04. Foi preservado em `registros/correcoes/icaro-sul-04-tentativa2.png` e rejeitado, sem substituir a célula selecionada. A tentativa anterior havia convertido04 em uma repetição da passagem03. São duas tentativas localizadas malsucedidas para este defeito; não contar como aprovação nem prosseguir com variações cegas.
