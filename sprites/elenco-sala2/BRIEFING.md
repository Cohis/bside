# Briefing de produção — elenco da Sala 2 (B-Side, Fase 1)

Você é o artista técnico responsável pelos sprites novos do jogo *B-Side* (Assembly x86-64 + Raylib, isométrico).
Leia este briefing inteiro antes de gerar qualquer imagem. Trabalhe **somente** dentro de
`/home/icaro/Documentos/AOC/sprites/elenco-sala2/`. Não altere nada fora desta pasta.

## 1. Contexto

A Sala 2 se passa num galpão abandonado e numa doca, de noite, com névoa. Os sprites de Ícaro e Eva já
existem e definem o padrão de arte do jogo. Os personagens novos precisam parecer do mesmo jogo, lado a lado
com Ícaro, na mesma escala e com o mesmo acabamento. No jogo, cada quadro 384 × 512 é reduzido para cerca de
36 × 48 px, então **silhueta e manchas de cor legíveis importam mais que detalhe fino**.

## 2. Referência de arte obrigatória

Antes de qualquer geração, abra e estude (view_image) estas imagens:

- `../bases/icaro/sul.png`, `../bases/icaro/leste.png`, `../bases/icaro/norte.png`, `../bases/icaro/sudeste.png`
- `../bases/eva/sul.png`, `../bases/eva/leste.png`, `../bases/eva/norte.png`, `../bases/eva/sudeste.png`
- `../tarefas/sul/icaro/01.png` e `../tarefas/leste/eva/03.png` (quadros de caminhada aprovados)
- `../ficha-visual.md`, `../contrato.json`, `../licoes-da-primeira-onda.md`
- Para contexto de cena: `registros/cena-galpao.png` e `registros/cena-doca.png` (o jogo rodando, com os sprites provisórios que você vai substituir)

Toda chamada de `image_gen` deve receber **pelo menos uma base de Ícaro ou Eva como imagem de referência de
estilo**, além das referências do próprio personagem. Copie do padrão existente:

- pixel art com blocos definidos e contorno muito escuro; luz difusa vinda de cima; sem nova fonte de luz;
- mesma câmera das bases (vista isométrica levemente de cima, a mesma inclinação de Ícaro em cada direção);
- mesma proporção estilizada de cabeça/corpo de Ícaro e Eva;
- fundo transparente real (alpha zero), sem quadriculado pintado, sem sombra de chão, sem halo, sem texto.

Não copie a roupa, o rosto nem as cores de Ícaro/Eva para os personagens novos: a referência é **de estilo**.

## 3. Personagens e entregáveis

### 3.1 Agente carmesim (prioridade 1)

Agente de campo da Ordem da Casa Carmesim. Gênero não identificável: o rosto fica inteiro coberto.
- Veste preta longa até o tornozelo, com capuz, mangas largas e detalhes vermelho-carmesim: barra, faixa da
  cintura e uma linha vertical no fecho. Luvas claras.
- Máscara de porcelana branca que cobre o rosto todo, com dois olhos azuis pintados e um risco carmesim vertical.
- Postura perfeita, ereta, quase militar. Botas pretas.
- Proporções: **mesma altura e silhueta corporal da base da Eva** (é ela sob a máscara; segredo de roteiro,
  então nenhum traço dela pode aparecer: nem cabelo, nem olhos, nem pele do rosto).

Entregáveis:
1. `agente/referencia-8-vistas.png` (1536 × 1024): folha de identidade com 8 vistas em 4 colunas × 2 linhas, no
   mesmo layout de `/home/icaro/Documentos/AOC/Ícaro.png` e `eva.png` (abra os dois e siga a ordem das vistas).
2. `agente/bases/<direcao>.png`: 8 bases paradas 384 × 512 (norte, nordeste, leste, sudeste, sul, sudoeste,
   oeste, noroeste), com âncora (192, 480), eixo x = 192 e altura corporal igual à da base da Eva na mesma direção.
3. `agente/sentado-ferido/01.png` e `02.png` (384 × 512, vista sul): sentado no chão encostado em caixotes
   (sem desenhar os caixotes), joelhos dobrados, mão esquerda segurando o ombro direito, mancha de sangue escuro
   no ombro, cabeça um pouco baixa. O quadro 02 difere só pela respiração (tronco 1 a 2 px mais alto). As solas
   e o quadril ficam apoiados perto de y = 480.

### 3.2 Anjo (prioridade 1)

Criatura "falsa" e cega: magra demais, humana demais, pele de porcelana pálida e rachada. **Sem olhos**: só
depressões. A mandíbula é alongada e tem dentes no lugar dos lábios, num sorriso contínuo de orelha a orelha.
Uma coroa de espinhos metálicos escuros flutua e gira em volta do crânio. Juntas finas, que dobram de jeito
errado. Não pode parecer robô nem zumbi: é uma estátua de porcelana viva.

Entregáveis (vista sul/frente, 384 × 512, âncora 192,480):
1. `anjo/referencia.png` (1536 × 1024): frente, três quartos e perfil, mais um detalhe do rosto.
2. `anjo/pousado/01.png` a `04.png`: agachado como aranha, mãos e pés no chão, cabeça inclinada escutando. Os
   4 quadros são **iguais**, exceto pelos espinhos da coroa, que giram 1/4 de volta ao longo do ciclo.
3. `anjo/voo/01.png` e `02.png`: corpo esticado no ar, braços para trás, coroa girando rápido (borrão de pixels
   permitido só nos espinhos).
4. `anjo/grito/01.png` e `02.png`: mandíbula escancarada além do humano, coroa em auréola, corpo tenso.

### 3.3 Hank (prioridade 2, só depois de 3.1 e 3.2 aprovados)

Dono da loja B-Side, 63 anos, ex-agente de uma organização paramilitar. Alto, grisalho, barba cheia e branca,
chapéu de aba larga gasto, casaco verde-oliva por cima de camisa clara, cinto de couro, calça marrom escura,
botas. Aliança dourada na mão esquerda. Expressão seca. É **mais alto que Ícaro**: topo do chapéu perto de y = 24.

Entregáveis:
1. `hank/referencia-8-vistas.png` (1536 × 1024, mesmo layout dos originais).
2. `hank/bases/<direcao>.png`: 8 bases paradas 384 × 512, âncora (192, 480).
3. `hank/falando/01.png` (vista sul): mão direita erguida na altura do peito, palma aberta.

### Fora de escopo nesta rodada

Ciclos de caminhada de qualquer personagem, Kami, Ford, Eva sem máscara, retratos de diálogo e cutscenes.

## 4. Processo e portões de aprovação

**Etapa 1 — identidade.** Gere `agente/referencia-8-vistas.png`, `anjo/referencia.png` e
`hank/referencia-8-vistas.png`. Monte `revisao/etapa1-prancha.png`: as três folhas e, ao lado, as bases
sul de Ícaro e Eva na mesma escala, para comparar estilo e altura. Escreva `STATUS.md` e **pare**. Não avance
sem aprovação do usuário; ela virá numa retomada desta sessão.

**Etapa 2 — prioridade 1.** Gere as bases e poses do agente e do anjo (3.1 e 3.2). Ordem do agente: sul,
norte, leste, oeste, depois as diagonais; depois o sentado. Cada chamada recebe a referência aprovada do
personagem, a base do Ícaro ou da Eva **na mesma direção** como referência de câmera e escala, e, quando
houver, a base vizinha já aprovada do próprio personagem. Monte `revisao/etapa2-prancha.png` e pare de novo.

**Etapa 3 — Hank.** Só depois de aprovado o que foi feito na etapa 2.

Regras de geração (são as mesmas que funcionaram para Ícaro e Eva):
- Uma imagem por chamada, um personagem por imagem, uma pose por imagem. Nunca gere grade de poses para
  recortar depois (a folha de referência da etapa 1 é a única exceção).
- Prompt no molde: "Produza somente [personagem], direção [direção], [pose]. As imagens de referência de
  Ícaro/Eva definem estilo de pixel art, câmera, escala e acabamento; a referência do personagem define a
  identidade. Corpo inteiro, PNG 384 × 512 com transparência real, âncora de chão (192,480), eixo x192, sem
  texto, sem objetos, sem sombra de chão, sem suavização nova."
- Nada de espelhar oeste a partir de leste, nem deformar membros por código. A única pós-produção permitida é
  o enquadramento de `../scripts/normalizar.py` (escala uniforme por vizinho mais próximo e remoção de ruído
  com alfa < 8). Registre a transformação em JSON ao lado do PNG.
- Copie cada imagem gerada para esta pasta; não dependa de `~/.codex/generated_images`.
- Registre em `registros/<arquivo>.prompt.txt` o prompt integral, as referências usadas e o resultado.
- Depois de 3 tentativas que falharem no mesmo defeito, registre o diagnóstico em `STATUS.md` e siga para o
  próximo item; não insista na mesma abordagem.

## 5. Critérios de aceite (verifique e registre em `revisao/<personagem>.json`)

- Arquivo RGBA no tamanho pedido, alfa zero fora da figura, sem resíduo de fundo (verifique sobre claro e escuro).
- Âncora: solas em y ≈ 480, eixo do corpo em x ≈ 192; altura dentro de ±8 px da meta.
- Mesma câmera da base de Ícaro na mesma direção; não pode ficar mais frontal nem mais de cima.
- Identidade estável entre direções: cores, acessórios, lado anatômico da aliança de Hank e do ombro ferido do agente.
- Legibilidade reduzida: gere `revisao/escala-jogo.png` com cada sprite reduzido a 36 × 48 (área) ao lado do
  Ícaro reduzido igual. Os personagens precisam ser reconhecíveis nessa escala.
- Estilo: colocados lado a lado com as bases de Ícaro e Eva, os sprites não podem parecer de outro jogo.

Só marque `"aprovado": true` se tudo foi conferido de fato. A aprovação final é do usuário.

## 6. STATUS.md

Mantenha sempre atualizado: etapa atual, o que está pronto, o que foi rejeitado e por quê, pendências e
o próximo passo. Ao parar num portão, termine a resposta com um resumo curto do que o usuário deve revisar.
