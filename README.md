# B-Side — loja isométrica

Jogo em Assembly x86-64 sobre uma loja de discos. A Raylib 6.2, incluída em `vendor/`, cuida da janela, entrada, texturas e desenho.

## Compilar e executar

Em Linux x86-64 com OpenGL e X11/XWayland, instale `gcc`, `make` e as bibliotecas de desenvolvimento de OpenGL e X11. Na raiz do repositório:

```sh
make
make run
```

## Controles

- **W A S D**: mover Ícaro
- **Esc**: sair

O movimento diagonal é normalizado. Ícaro desliza ao longo de obstáculos quando um dos eixos continua livre.

Para salvar uma captura em `captura.png`, execute `BSIDE_CAPTURE=1 make run`. Para mostrar o contorno das células bloqueadas, use `BSIDE_COLISOES=1 make run`.

## Arquivos

- `bside.s`: mapa, projeção isométrica, câmera, colisões e renderização em Assembly.
- `bside-cenario-pintado.s`: versão anterior do cenário com personagens controláveis.
- `assets/`: texturas, artes de referência e sprites provisórias necessárias para executar o jogo.
- `vendor/raylib/`: biblioteca Raylib e sua licença.
- `ANALISE-CENARIO.md`: planta, tipos de célula, movimento e conferência das áreas.

As sprites finais são opcionais. Quando adicionadas como `assets/icaro-andar-final.png` (e, na versão pintada, `assets/eva-andar-final.png`), elas substituem as sprites provisórias.
