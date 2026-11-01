# B-Side — Fase 1 em perspectiva isométrica

Versão paralela de `../jogo/` para comparar jogabilidade: o mesmo interior da B-Side, a mesma música, luz, HUD e escada, mas em vista isométrica. A lógica continua toda em Assembly x86-64; a Raylib 6.2, em `vendor/`, cuida de janela, entrada, áudio e desenho.

## Compilar e executar

```sh
make
make run
```

`make arte` regera os atlas, a névoa e os sons (Python 3 + Pillow + NumPy): `assets/tileset-iso.png` e `tileset.inc` (cenário), `assets/personagens.png` e `personagens.inc` (elenco e interface), `assets/elenco-hd.png` (agente carmesim e anjo, em células 384 × 512 como o Ícaro), `assets/nevoa.png` e `assets/sons/`. O gerador isométrico reaproveita as texturas de `ferramentas/gerar_tileset.py`, copiado da versão top-down.

`make teste` roda a fase com um robô no lugar do teclado (`ferramentas/teste_auto.c`, ligado com `--wrap`): o primeiro percurso resolve o enigma da loja (tenta a porta antes da hora, pega o bilhete, erra uma nota e toca D-C-G no depósito, lê a etiqueta e sai); o segundo pega o disco e fala com o agente; o terceiro atravessa a doca, errando de propósito uma vez no 2º ponto. As capturas ficam em `teste/`.

## Sala 1 — o pedido do Anderson

1. **Porta da rua**: antes de descobrir o endereço, Ícaro só diz que não sabe onde fica o galpão.
2. **Balcão da loja**: o bilhete pede para pegar o pedido do Anderson no depósito, "logo depois da estante com a lista do depósito", e termina com **D - C - G** e as teclas das notas (1 = C, 2 = D, 3 = E, 4 = G).
3. **Depósito** (térreo, abaixo da escada): a lista está presa na estante oeste; a caixa do pedido, no alto da estante leste. Diante dela, tocar **D, C, G** (teclas **2, 1, 4** ou MIDI), sem metrônomo. Nota errada recomeça a sequência.
4. A caixa cai; a etiqueta tem o endereço do galpão do Hank. Só então a porta da rua leva à Sala 2.

## Sala 2 — galpão e doca

1. **Loja**: depois do enigma da Sala 1, a porta da rua, no térreo, leva ao galpão (**E**).
2. **Galpão**: oito estantes numeradas no chão; a prancheta perto da bancada diz qual caixa é. Pegar o disco faz os aparelhos chiarem, as luzes falharem, a névoa entrar e Mael aparecer na janela do fundo. O agente carmesim, marcado pelos anjos, espera de pé junto ao portão; falar com ele leva à doca.
3. **Doca**: três pontos. Em cada um, Ícaro espera na marca verde enquanto os anjos escutam. O metrônomo marca 4 pulsos; no 4º, toque a nota do alto-falante certo (teclas **1-4** ou teclado MIDI). Os anjos gritam, levantam voo até ele e a barra "CORRA!" mostra quanto tempo resta para chegar à próxima marca. Nos pontos 2 e 3 há um alto-falante isca no caminho. Nota errada, fora do pulso, sair da marca antes da hora ou tempo esgotado: o anjo grita e só aquele ponto recomeça. O agente reaparece em cada marca alcançada com um clarão azul.

O teclado MIDI é lido de `/dev/snd/midiC0D0` a `midiC3D0`, sem bloquear; vale a classe da nota (Dó, Ré, Mi, Sol em qualquer oitava, tabela `notas_midi` em `ritmo.s`).

## Controles

- **W A S D**: mover Ícaro na tela (W sobe, D vai para a direita)
- **Duas teclas juntas** (W+D, W+A, S+D, S+A): andar rente à grade do chão, ao longo das paredes
- **E**: interagir e avançar mensagens
- **1-4** (ou teclado MIDI): as quatro notas
- **F11** ou **Alt+Enter**: tela cheia, com zoom inteiro na resolução do monitor
- **Esc**: sair

## O que muda em relação à versão top-down

- **Paredes**: só as paredes ao norte e a oeste de cada cômodo aparecem de pé. As da frente do prédio ficam baixas, e qualquer parede entre a câmera e Ícaro fica transparente quando ele passa atrás dela (mantém a altura; janelas e quadros dela também ficam translúcidos).
- **Planta**: para as janelas aparecerem, elas foram para as paredes do fundo. A cozinha tem a janela de ponta a ponta na parede norte, e o quarto de hóspedes fica no lado oeste, com a janela nessa parede. A sala de estar ocupa o fim do corredor em L. O térreo mantém a escada pela lateral oeste, com a cafeteria e o depósito abaixo dela.
- **Escada**: no térreo os degraus têm altura de verdade, e Ícaro sobe e desce com eles.
- **Profundidade**: paredes, degraus e móveis entram numa lista ordenada por `x + y` (montada uma vez por andar), e Ícaro é inserido nela a cada quadro. Móveis compridos são cortados em pedaços de 16 px para a ordenação não errar.

## Depuração

- `BSIDE_CAPTURE=1 ./bside`: salva `captura.png` no 45º quadro e fecha.
- `BSIDE_COLISOES=1 ./bside`: contorna paredes (magenta), móveis (ciano) e gatilhos de escada (amarelo) no chão isométrico.
- `BSIDE_PONTO="andar x y"`: começa no andar `0` (de cima), `1` (térreo), `2` (galpão) ou `3` (doca), no tile `(x, y)`, em passeio livre (sem a sequência da fase).
- `BSIDE_CENA=loja`: começa no térreo, já no enigma da Sala 1.
- `BSIDE_SALA=2` ou `BSIDE_CENA=galpao`: começa no galpão. `BSIDE_CENA=doca`, `doca2` ou `doca3` começa no ponto correspondente da doca.

## Arquivos

- `bside.s`: motor isométrico (projeção, lista de profundidade, paredes que ficam transparentes, luz, HUD, música).
- `fase1.s`: B-Side: plantas 22 × 22, papéis de parede, móveis, decalques de parede, luzes, cômodos e escadas; a legenda dos tiles serve aos quatro andares.
- `sala2.s`: galpão e doca: plantas, móveis, luzes, poses do elenco, interações, os três pontos da doca e a sequência da fase, que começa no enigma da loja (bilhete, melodia do depósito, caixa com o endereço).
- `atores.s`: agente, anjos, Mael e clarões na lista de profundidade, com animação e movimento.
- `roteiro.s`: interpretador da sequência da fase, interações com E, melodias a tocar num lugar certo, mensagens, objetivo, névoa, foco e tremor da câmera.
- `ritmo.s`: teclado MIDI, teclas 1-4, sons, metrônomo e a validação única de nota e pulso.
- `doca.s`: os três pontos da fuga (áreas seguras, alto-falantes, anjos, janela de corrida).
- `cenario.inc`: macros de dados de cenário usadas por `fase1.s` e `sala2.s`.
- `ferramentas/gerar_agente.py`: o agente carmesim parado nas 8 direções, repintado das bases da Eva (`../sprites/bases/eva/`): farda preta com cinto, gola e punhos vermelhos e máscara preta só com os olhos azuis. Grava as bases em `../sprites/elenco-sala2/agente/` e a coluna 384 × 4096 do jogo (`assets/agente-parado.png`). Aparece parado no galpão e na doca; andando, ainda desliza na pose parada. Medidas de cada direção (elipse da máscara, gola, cinto, costas, manga) ficam no topo do script.
- `ferramentas/gerar_anjo.py`: o anjo a partir de duas folhas em `../sprites/elenco-sala2/anjo/`: `folha-original.png` (8 vistas, baixada pelo usuário) e `poses-chatgpt.png` (pousado escutando, grito e voo, geradas no ChatGPT a partir da primeira). Tira o fundo preto, põe contorno de 3 px, leva todas à mesma escala e aos pés em (192, 480); o voo à esquerda é o da direita espelhado.
- `ferramentas/montar_elenco_hd.py`: junta as colunas do agente, do anjo e das poses do anjo em `assets/elenco-hd.png`. Atores com a flag `AF_HD` (`atores.s`) são desenhados dessa textura, com a mesma redução e os mesmos mipmaps do Ícaro.
- `ferramentas/gerar_personagens.py`, `ferramentas/gerar_sons.py`: elenco em pixel art (e o bilhete, a lista e a caixa da Sala 1) e efeitos sonoros.
- `estruturas.inc`: constantes e deslocamentos de campos.
- `ferramentas/gerar_iso.py`: projeta texturas planas em losangos 32 × 16, faces de parede e caixas isométricas.
