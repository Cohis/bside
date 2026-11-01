# Prévia cinematográfica da Fase 1

`cutscene.py` apresenta a história da loja até o epílogo em uma janela Pygame. A cena é desenhada em tempo real: cenário isométrico com profundidade, câmera que reenquadra os personagens, letterbox, névoa, luzes móveis, efeitos de som e legendas. O roteiro visual reinterpreta as cenas existentes sem chamar nem alterar o motor Assembly.

## Executar

Crie um ambiente isolado e instale Pygame CE:

```sh
python3 -m venv .venv
.venv/bin/pip install pygame-ce
```

Depois, na pasta `jogo-isometrico/`, abra a prévia:

```sh
.venv/bin/python cutscene.py
```

O programa usa os atlas e sons que já estão em `assets/`. Quando disponível, usa também os quadros dos personagens em `../sprites/revisao/quadros/`; Ícaro tem uma imagem de reserva em `assets/icaro-andar-rascunho.png` e Eva usa o sprite do atlas do elenco se os quadros externos não estiverem presentes.

Para gerar uma imagem de qualquer plano sem abrir a janela, use `.venv/bin/python cutscene.py --captura /tmp/cutscene.png --plano 45`. `--plano` aceita índices de `0` a `61`.

## Controles

- `Espaço`, `Enter`, `E` ou clique esquerdo: avançar fala.
- `Backspace`, `←` ou clique direito: voltar uma fala.
- `1` a `4`: ir para loja, galpão, doca ou epílogo.
- `P`: pausar; `M`: silenciar; `F11`: tela cheia; `Esc`: sair.
