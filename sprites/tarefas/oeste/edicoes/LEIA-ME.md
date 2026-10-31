# Correções locais — direção oeste

O usuário autorizou edição controlada quadro a quadro em 23/10/2026. As 16 células de caminhada originais normalizadas ficam em `originais/<personagem>/`; os raws de geração continuam intactos em `../<personagem>/*-raw*.png`.

1. `../corrigir_contato.py` remapeou somente as linhas y≥350 por vizinho mais próximo. Corrigiu os comprimentos inconsistentes gerados entre a cintura e os pés, mantendo cabeça, tronco, braços, paleta, alfa e x dos pixels. Todos os contatos inferiores passam a y=480. Cada fonte e resultado consta em `correcao-contato.json`.
2. `../aproximar_passagens.py` foi testado em 03/07 dos dois personagens, mas a translação das metades inferiores criou bordas serrilhadas e membros fundidos. Os quatro resultados estão em `rejeitados/`, os PNGs de produção foram restaurados; ver `passagens-rejeitadas.json`. **Não executar esse script sobre os PNGs atuais.**
3. Eva 07 foi substituído por variante raw-t2 já gerada, com o pé em balanço menos adiantado. A versão anterior está em `selecoes-anteriores/`; metadados em `selecionar-eva07.json`.
4. `../recompor_passagens.py` recortou e girou a perna em balanço **do próprio quadro** em Ícaro 03/07 e Eva 03. Usa amostragem de pixel por vizinho mais próximo e sobreposição por seleção, sem criar cores novas. A máscara, o pivô, a rotação, os candidatos, os estados anteriores e os hashes estão em `candidatos/`, `pre-composicao/` e `composicoes-adotadas.json`. Ícaro 07 com rotação maior que 12° aproximava/mesclava excessivamente os calçados; variantes preservadas em `candidatos/`.
5. `../revisar_edicoes.py` regenerou pranchas, GIFs a 100/400 ms com chão marcado, QA e rastreamento estimado. `revisao.json` continua `aprovado: false` para ambos. A normalização do contato inferior e o recorte local melhoram as passagens, mas ainda não certificam ausência de patinação horizontal ou qualidade do ciclo inteiro.

Ordem para reprodução em cópia limpa: `corrigir_contato.py`, `selecionar_eva07.py`, `recompor_passagens.py`, aplicar os três candidatos registrados em `composicoes-adotadas.json`, `revisar_edicoes.py`. Como os scripts preservam backups na primeira execução, não rodá-los cegamente sobre trabalho posterior.

### Revisão localizada posterior — passagens t1 e apoio de Eva

- Eva 02/06: remapeamento progressivo de pixels da perna de apoio (+20 px no calçado) adotado. Fontes anteriores em `pre-apoiar-eva/`; registro com hashes em `apoios-eva-02-06.json`.
- Ícaro e Eva 03/07: as variantes `raw-t1` do próprio personagem foram normalizadas a 384×512 pelo método de escala nearest e contato já usado nesta pasta. Substituíram as composições anteriores porque as pranchas mostravam pés quase fundidos; os quatro anteriores estão em `pre-t1-passagem/` e o registro com hashes em `passagens-t1-adotadas.json`.
- Candidatos `novo_passo.py`, `candidatos_passagem_07.py` e `compor_passagem_07.py` **rejeitados**: o primeiro deixou descontinuidade triangular no tornozelo; os dois de 07 criaram lacunas ou pés duplicados. Arquivos em `novos-candidatos/` são apenas ensaios e não representam quadros aprovados.
- Pranchas e GIFs 100/400 ms com chão marcado a 40 px/quadro foram regenerados por `../verificar_passagens_t1.py`. `../icaro/revisao.json` e `../eva/revisao.json` continuam com `aprovado: false`: joelho de 03/07 elevado demais para certificar caminhada natural, patinação ainda possível, e Eva 02 tem variação de escala aparente. Os pontos do rastreamento são estimativas, não prova de contato.

### Segunda revisão — joelhos e contatos

- `baixar_joelho_t1.py` foi inspecionado em prancha e ampliação 3×, sem costuras aparentes. As quatro passagens 03/07 foram adotadas; versões t1 anteriores em `pre-baixar-joelho/`, hashes e método em `joelho-baixo-adotado.json`.
- A tentativa `alinhar_apoio.py` foi **rejeitada** por pixels isolados e deformação dos calçados. A tentativa seguinte `apoiar_icaro_02_06.py` também foi **rejeitada**: em Ícaro 02 alterou parte da mão e em 06 abriu uma fenda entre as pernas. Nenhum desses candidatos entrou nos PNGs de produção.
- `icaro-transicoes-contato.png` e `eva-transicoes-contato.png` mostram 04→05 e 08→01. A ponta do pé que avança muda pouco na horizontal e desce até o chão: Ícaro 04R→05R x91→91, y446→469; 08L→01L x95→91, y462→475. Eva 04R→05R x97→100, y454→463; 08L→01L x96→106, y456→473. Pontos são estimativas com margem de aproximadamente 10 px.
- Eva 02: a largura aparente da cabeça na faixa y50–180 é 190 px, dentro da faixa 181–192 dos quadros vizinhos; a altura total é a mesma. Uma escala uniforme reduziria também tronco, pernas e altura, então não foi aplicada sem diagnóstico melhor.
- Oeste segue **reprovado**. O recuo do pé de apoio contra chão marcado e a leitura temporal das passagens ainda exigem confirmação; `revisao.json` explica cada pendência.

### Retomada de 24/out/2026 — sola de balanço e calibração do chão

- `testar_sola_baixa.py` gerou variantes 03/07 para os dois personagens. Inspeção da sequência 02–03–04 e 06–07–08 em prancha, seguida de ampliação 3×, não mostrou costuras, membros fundidos ou mudança de tronco/cabeça. As quatro variantes foram adotadas. PNGs anteriores em `pre-sola-baixa/`; hashes e método em `sola-baixa-adotada.json`.
- O remapeamento nearest abaixa só a sola em balanço: máximo 15 px para Ícaro e 11 px para Eva; o pé de apoio não se move. A sola continua elevada, com contato apenas na fase seguinte.
- `avaliar_apoio_24out.py` calcula o recuo a partir dos pontos visuais em `rastreamento.json`. Velocidade de teste: 43 px/quadro para Ícaro e 39 para Eva. Amplitude residual do pé de apoio contra esse chão: 15/18 px nos dois meios-ciclos de Ícaro e 18/9 px em Eva. Erro dos pontos observado ~10–12 px; isso não certifica ausência de patinação.
- `../verificar_passagens_t1.py` regenerou pranchas e GIFs de 100/400 ms com chão móvel calibrado por personagem. `revisao.json` segue **não aprovado** porque a naturalidade temporal e o contato do apoio não foram certificados em reprodução contínua. Os arquivos GIF têm 8 quadros e os tempos corretos; isso é verificação técnica, não aprovação visual do loop.

### Rearticulação das passagens — 24/out/2026

- `rearticular_passagens.py` criou candidatos para Ícaro/Eva 03/07 abaixando toda a perna em balanço por remapeamento vertical progressivo nearest, com pico de 30 px em Ícaro e 27 px em Eva. O efeito zera no quadril e antes da sola do pé de apoio. Os quatro candidatos foram comparados em ampliações 3× e pranchas 02–03–04/06–07–08, depois adotados nos PNGs de produção. Os anteriores estão em `pre-rearticular-passagens/`, com hashes, caixas de pixels alterados e método em `rearticulacao-passagens-adotada.json`.
- A diferença por pixel fica em x=108–205, y=315–459 conforme o quadro; tronco/cabeça acima de y312 e sola de apoio em x160–300, y460–512 permanecem idênticos. O remapeamento não introduz cores nem suavização.
- `gerar_evidencia_rearticulacao.py` produziu as pranchas candidatas e GIFs 100/400 ms com chão a 43 px/quadro para Ícaro e 39 para Eva. `../verificar_passagens_t1.py` regenerou os equivalentes da produção. Verificação de duração, sequência e pranchas feita; a animação temporal contínua não foi certificada visualmente nesta rodada.
- A melhora visual do joelho é concreta, mas Oeste permanece **não aprovado**: a transição de passagem ainda merece revisão temporal e o resíduo estimado do apoio contra chão móvel não elimina a possibilidade de patinação. Em Eva, 02 ainda parece variar em escala apesar das medidas de cabeça compatíveis.

### Ensaio de coxa ainda mais baixa — rejeitado

A revisão do coordenador apontou coxa ainda alta em Ícaro 03/07 e Eva 07. Testei `testar_coxa_baixa.py` (joelho +49/+45 px) e `testar_coxa_diagonal.py` (mesmo abaixamento com coxa ~18 px para trás). As pranchas 02–03–04/06–07–08 e a ampliação `novos-candidatos/coxa-variantes-comparacao-3x.png` mostram alongamento artificial da pantalona, dobra angular na variante diagonal e calçados quase fundidos com o apoio. **Nenhum desses candidatos entrou na produção.** Diagnóstico em `avaliacao-coxa-baixa.json`; a próxima correção deve redesenhar localmente a anatomia da perna inteira, pois ampliar o remapeamento já chegou ao limite útil.
