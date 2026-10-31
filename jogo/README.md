# B-Side — Fase 1

Jogo em Assembly x86-64 sobre uma loja de discos. A Fase 1 é o interior da B-Side em dois andares, em visão top-down 3/4 e pixel art. A Raylib 6.2, incluída em `vendor/`, cuida da janela, entrada, texturas e desenho.

## Compilar e executar

Em Linux x86-64 com OpenGL e X11/XWayland, instale `gcc`, `make` e as bibliotecas de desenvolvimento de OpenGL e X11. Na raiz do repositório:

```sh
make
make run
```

`make arte` regera o tileset e as texturas de luz (precisa de Python 3 com Pillow). Os arquivos gerados já estão no repositório, então `make` não depende de Python.

## Controles

- **W A S D**: mover Ícaro
- **F11** ou **Alt+Enter**: alternar tela cheia (o jogo redesenha na resolução do monitor, com zoom inteiro)
- **Esc**: sair

O movimento diagonal é normalizado. Ícaro desliza ao longo de paredes e móveis quando um dos eixos continua livre. A escada troca de andar com um fade preto.

## Depuração

- `BSIDE_CAPTURE=1 make run`: salva `captura.png` no 45º quadro e fecha o jogo.
- `BSIDE_COLISOES=1 make run`: contorna paredes (magenta), colisão dos móveis (ciano) e gatilhos de escada (amarelo).
- `BSIDE_PONTO="andar x y"`: começa no andar `0` (de cima) ou `1` (térreo), no tile `(x, y)`. Exemplo: `BSIDE_PONTO="1 6 26" BSIDE_CAPTURE=1 ./bside` captura a cafeteria.

## Arquivos

- `bside.s`: motor — movimento, colisão, câmera, troca de andar, desenho dos tiles, ordenação por profundidade, luz e HUD.
- `fase1.s`: dados da fase — plantas dos dois andares em ASCII, móveis, luzes, cômodos e escadas.
- `estruturas.inc`: constantes e deslocamentos de campos usados pelos dois `.s`.
- `tileset.inc`: posições de cada peça no atlas, gerado por `ferramentas/gerar_tileset.py`.
- `assets/tileset-bside.png`, `assets/luz.png`, `assets/vinheta.png`: arte gerada pelo script.
- `assets/icaro-andar-rascunho.png`: sprite provisória de Ícaro. Quando existir `assets/icaro-andar-final.png`, ela é usada no lugar.
- `bside-cenario-pintado.s`: versão anterior do cenário com personagens controláveis.
- `ANALISE-CENARIO.md`: plantas, legenda dos tiles, camadas de desenho e luz.
- `vendor/raylib/`: biblioteca Raylib e sua licença.
