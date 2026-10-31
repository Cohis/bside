# Fase 1 — plantas, tiles, desenho e luz

## Projeção e câmera

Cada andar é uma grade de 24 × 33 tiles de 16 px. O mundo é desenhado direto na resolução da janela, com zoom inteiro igual a altura ÷ 240: 3× em 1280 × 720, 4× em 1920 × 1080, 6× em 2560 × 1440. Assim, cada pixel da arte vira um quadrado exato de pixels da tela. O HUD usa fonte em múltiplos de 10 px pelo mesmo motivo, e o mapa de luz é recriado quando a janela muda de tamanho (F11). Na vista 3/4, uma parede horizontal ocupa uma linha de **topo** (`#`, o que se vê por cima) e três linhas de **face** (a parede de pé, com rodaforro em cima e rodapé embaixo). Paredes verticais são só colunas de topo. A câmera segue Ícaro e para nas bordas do andar; como os andares são mais estreitos que a tela, ficam centralizados na horizontal.

## Andar de cima (início da fase)

```
########################   0
#aaaaaaa#jjjjjjjjjjjjjj#   1   janela da cozinha de ponta a ponta
#aaaaaaa#jjjjjjjjjjjjjj#   2
#aaaaaaa#jjjjjjjjjjjjjj#   3
#.......#KKKKKKKKKKKKKK#   4   patamar | cozinha
#.......#KKKKKKKKKKKKKK#   5
#^^^|...#KKKKKKKKKKKKKK#   6   topo da escada
#^^^|....KKKKKKKKKKKKKK#   7   porta 1 → cozinha; degrau-gatilho de descida
#vvv|....KKKKKKKKKKKKKK#   8
#vvv|...#KKKKKKKKKKKKKK#   9
#vvv|...#KKKKKKKKKKKKKK#  10
#vvv|...################  11
#vvv|...#hhhhhhhhhhhhhh#  12
#vvv|...#hhhhhhhhhhhhhh#  13
#vvv|...#hhhhhhhhhhhhhh#  14
#####...#HHHHHHHHHHHHHH#  15   quarto de hóspedes
#####....HHHHHHHHHHHHHHw  16   porta 2 → quarto de hóspedes
#####....HHHHHHHHHHHHHHw  17
#####...#HHHHHHHHHHHHHHw  18
#####...#HHHHHHHHHHHHHH#  19
#####...################  20   fim do corredor → sala de estar
#llll...lllllllllllllll#  21
#llll...lllllllllllllll#  22
#llll...lllllllllllllll#  23
#LLLLLLLLLLLLLLLLLLLLLL#  24   sala de estar
  ...  (linhas 25-31: sala, janelas `w` a leste nas linhas 26-28)
########################  32
```

Quem sobe chega ao patamar (2, 5), vira à direita (leste) e de novo à direita (sul), entrando no corredor. A primeira porta leva à cozinha; a segunda, ao quarto de hóspedes; o fim do corredor dá na sala de estar. Ícaro começa na sala, em (4, 27), ao lado da própria cama.

- **Cozinha**: janela panorâmica com a cidade à noite, bancada com pia e fogão sob a janela, geladeira, mesa com duas cadeiras sobre um tapete, pendente, planta e lixeira.
- **Quarto de hóspedes**: só cama, escrivaninha com cadeira e luminária, e a janela lateral.
- **Sala de estar**: TV grande na parede (tela que tremeluz) sobre um rack com duas caixas de som, sofá de costas para a câmera, tapete, estante com livros, luminária de pé, pufe, planta, pôsteres e a **cama do Ícaro**. As barras e a escadinha ficam no chão; o colchão é desenhado na camada de teto, junto ao alto da parede.

## Térreo

```
########################   0
#ooosssssssssssssssssss#   1   escada sumindo no teto | placa B-SIDE
#ooosssssssssssssssssss#   2
#ooosssssssssssssssssss#   3
#^^^!SSSSSSSSSSSSSSSSSS#   4   degrau-gatilho de subida
#^^^!SSSSSSSSSSSSSSSSSSw   5   vitrine
  ...  (linhas 6-12 iguais: escada pela lateral oeste da loja)
#^^^SSSSSSSSSSSSSSSSSSS#  13   pé da escada
#SSSSSSSSSSSSSSSSSSSSSS#  14
#SSSSSSSSSSSSSSSSSSSSSSe  15   porta da rua (fechada nesta etapa)
  ...
#####CCC#########DD#####  20   passagens para cafeteria e depósito
#ccccCCCccccc#dddDDdddd#  21
#ccccCCCccccc#dddDDdddd#  22
#ccccCCCccccc#dddDDdddd#  23
#CCCCCCCCCCCC#DDDDDDDDD#  24   cafeteria | depósito
  ...
########################  32
```

- **Loja**: clima de loja de discos com café — parede verde-garrafa com lambri de nogueira, piso de parquete, placa esmaltada B-SIDE em vermelho e branco ("DISCOS E CAFE"), estantes de discos com luzes de latão, quatro ilhas de caixotes com capas em tons sóbrios, balcão do Hank com caixa registradora e o registro de estoque aberto, banquinho, capacho, plantas e pendentes.
- **Cafeteria** (abaixo da escada): lousa de cardápio, balcão com máquina de espresso, **vitrola com disco girando e notas musicais subindo**, catálogo num suporte ao lado, quadros de discos emoldurados em latão, duas mesas de bistrô com tampo de mármore e pendentes.
- **Depósito**: estantes metálicas com caixas, uma ilha de prateleiras com a **caixa marcada** (fita vermelha), pilhas de caixas e uma lâmpada que falha.

## Legenda dos tiles

| Caractere | Tile | Classe |
|---|---|---|
| `#` | topo de parede (16 variantes pelos lados abertos) | sólido |
| `.` `K` `H` `L` | piso do corredor, cozinha, hóspedes, sala | piso |
| `S` `C` `D` | piso da loja, cafeteria, depósito | piso |
| `^` | degraus | piso |
| `v` | vão da escada descendo | sólido |
| `a` `j` `h` `l` `s` `c` `d` `o` | faces de parede (corredor, janela, hóspedes, sala, loja, tijolo da cafeteria, bloco do depósito, escada subindo) | sólido |
| `w` `e` | janela lateral, porta de vidro | sólido |
| `\|` `!` | guarda-corpo (andar de cima, térreo) | sólido |

A tabela fica em `tipos_tile` (`fase1.s`). No início, o motor a expande para uma tabela de 256 entradas indexada pelo caractere.

## Desenho

1. **Tiles**: a variante de cada peça sai dos vizinhos (lados abertos do topo, posição da face, pontas de colunas) ou de um hash fixo da posição, nos pisos. O piso logo abaixo de uma face e à direita de uma parede recebe sombra.
2. **Camada do chão**: tapetes, passadeira, quadros, TV, janela da cozinha e batentes das portas.
3. **Camada ordenada**: móveis e Ícaro, pela base (y onde tocam o chão). Os objetos são ordenados uma vez no início; Ícaro entra na posição dos pés.
4. **Teto**: pendentes, lâmpada e o colchão da cama do Ícaro.
5. **Luz**: um mapa de luz do tamanho da tela começa com a cor ambiente do andar e soma cada luz (gradiente radial tingido, blend aditivo). Depois, multiplica a cena. Lâmpadas tremeluzem, a TV pisca e a lâmpada do depósito apaga às vezes.
6. **Brilhos próprios**: letras da placa B-SIDE, tela da TV, luzes da cidade na janela, notas musicais e a lâmpada acesa, por cima da luz.
7. **Vinheta**, fade da escada e HUD com andar e cômodo.

## Colisão

A colisão usa os quatro cantos de uma caixa nos pés de Ícaro (12 × 5 px). Cada canto precisa cair num tile de classe piso e fora de qualquer retângulo de colisão dos móveis. Por isso a cama do Ícaro só bloqueia nas barras, e dá para passar por baixo do colchão. `BSIDE_COLISOES=1` mostra essas áreas.

As rotas sala → corredor → patamar → escada → loja e loja → escada → patamar → corredor → cozinha foram percorridas com teclas simuladas. Também foram percorridas as entradas do quarto de hóspedes, da cafeteria e do depósito.
