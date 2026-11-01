#!/usr/bin/env python3
"""Prepara o anjo a partir da folha baixada pelo usuário (8 vistas sobre fundo preto).

A folha original (../sprites/elenco-sala2/anjo/folha-original.png, 1536x1024) tem
4x2 células de 384x512 na ordem das linhas do Ícaro: norte, nordeste, leste,
sudeste / sul, sudoeste, oeste, noroeste. Ela não tem transparência e a arte não
tem contorno; aqui o fundo preto vira transparente, ganha um contorno escuro de
3 px (o padrão de Ícaro, Eva e agente) e cada vista é posta com os pés em
(192, 480), o eixo das bases.

A segunda folha (poses-chatgpt.png, gerada no ChatGPT a partir da primeira, a
pedido do usuário) traz as poses da doca lado a lado: pousado escutando, grito e
voo para a direita. Elas são reduzidas na mesma escala das 8 vistas (o grito, em
pé, fica com a altura média delas) e recebem o mesmo recorte e contorno.

Saídas:
  ../sprites/elenco-sala2/anjo/bases/<direcao>.png   as 8 vistas, 384x512
  ../sprites/elenco-sala2/anjo/poses/<pose>.png      pousado, grito, voo-direita, voo-esquerda
  assets/anjo-parado.png   uma coluna 384x4096, linhas na ordem do Ícaro
  assets/anjo-poses.png    uma coluna 384x4096: linha 0 pousado, 1 grito,
                           2 voo para a direita, 3 voo para a esquerda (espelhado)

Uso: python3 ferramentas/gerar_anjo.py   (ou `make arte`)
"""
from pathlib import Path

import numpy as np
from PIL import Image

RAIZ = Path(__file__).resolve().parent.parent
PASTA = RAIZ.parent / "sprites" / "elenco-sala2" / "anjo"
DIRECOES = ["norte", "nordeste", "leste", "sudeste", "sul", "sudoeste", "oeste", "noroeste"]
L, A = 384, 512
ANCORA = (192, 480)
LIMIAR_FUNDO = 40          # máximo dos canais: abaixo disso e ligado à borda é fundo
PRETO_PURO = 12            # buracos pretos fechados (entre asa e corpo) também saem
CONTORNO = np.array([10, 6, 16])


def dilatar(m, raio):
    r = m.copy()
    for dy in range(-raio, raio + 1):
        for dx in range(-raio, raio + 1):
            if dx * dx + dy * dy <= raio * raio + 1:
                r |= np.roll(np.roll(m, dy, 0), dx, 1)
    return r


def recortar(celula):
    cor = celula.astype(int)
    mx = cor.max(2)
    # fundo: inunda a partir da borda pelos pixels escuros
    escuro = mx < LIMIAR_FUNDO
    fundo = np.zeros_like(escuro)
    fundo[0, :] = escuro[0, :]
    fundo[-1, :] = escuro[-1, :]
    fundo[:, 0] = escuro[:, 0]
    fundo[:, -1] = escuro[:, -1]
    while True:
        mais = dilatar(fundo, 1) & escuro & ~fundo
        if not mais.any():
            break
        fundo |= mais
    figura = ~(fundo | (mx < PRETO_PURO))
    # pontinhos soltos de ruído do fundo: some o pixel com poucos vizinhos de figura
    vizinhos = np.zeros(figura.shape, int)
    for dy in range(-3, 4):
        for dx in range(-3, 4):
            vizinhos += np.roll(np.roll(figura, dy, 0), dx, 1)
    figura &= vizinhos >= 12
    contorno = dilatar(figura, 3) & ~figura
    rgba = np.zeros(cor.shape[:2] + (4,), np.uint8)
    rgba[figura, :3] = cor[figura]
    rgba[figura, 3] = 255
    rgba[contorno, :3] = CONTORNO
    rgba[contorno, 3] = 255
    return rgba, figura


def posicionar(rgba, figura, pelos_pes=True):
    """Pés em ANCORA: base da figura em y = 480 e o meio dos pés em x = 192
    (no voo, sem pés no chão, o meio da figura inteira)."""
    ys, xs = np.nonzero(rgba[..., 3] > 0)
    baixo = ys.max()
    pes = figura[max(0, baixo - 30):baixo + 1]
    _, xs_pes = np.nonzero(pes)
    if pelos_pes and len(xs_pes):
        meio = int(round(xs_pes.mean()))
    else:
        meio = int(round((xs.min() + xs.max()) / 2))
    dx, dy = ANCORA[0] - meio, ANCORA[1] - baixo
    saida = np.zeros_like(rgba)
    y0, y1 = max(0, -dy), min(A, A - dy)
    x0, x1 = max(0, -dx), min(L, L - dx)
    saida[y0 + dy:y1 + dy, x0 + dx:x1 + dx] = rgba[y0:y1, x0:x1]
    cortado = rgba[..., 3].sum() - saida[..., 3].sum()
    return saida, cortado


def separar(mx):
    """Figuras lado a lado: faixas de colunas com algo acima do fundo, separadas por vão."""
    cols = np.nonzero((mx > LIMIAR_FUNDO).sum(0) > 2)[0]
    faixas, ini, ant = [], cols[0], cols[0]
    for c in cols[1:]:
        if c - ant > 20:
            faixas.append((ini, ant))
            ini = c
        ant = c
    faixas.append((ini, ant))
    return faixas


def poses_extras(altura_ref):
    folha = Image.open(PASTA / "poses-chatgpt.png").convert("RGB")
    mx = np.asarray(folha).max(2)
    faixas = separar(mx)
    if len(faixas) != 3:
        raise SystemExit(f"poses-chatgpt.png: esperava 3 figuras, achei {len(faixas)}")
    recortes = []
    for x0, x1 in faixas:
        ys = np.nonzero((mx[:, x0:x1 + 1] > LIMIAR_FUNDO).any(1))[0]
        recortes.append(folha.crop((x0, ys.min(), x1 + 1, ys.max() + 1)))
    escala = altura_ref / recortes[1].height        # o grito é a pose em pé
    saidas = []
    for k, (nome, pelos_pes) in enumerate((("pousado", True), ("grito", False), ("voo-direita", False))):
        r = recortes[k]
        r = r.resize((round(r.width * escala), round(r.height * escala)), Image.LANCZOS)
        tela = Image.new("RGB", (L, A), (0, 0, 0))
        tela.paste(r, ((L - r.width) // 2, A - 24 - r.height))
        rgba, figura = recortar(np.asarray(tela))
        rgba, cortado = posicionar(rgba, figura, pelos_pes)
        if cortado:
            print(f"aviso: {nome} perdeu {cortado // 255} px na borda da célula")
        saidas.append((nome, Image.fromarray(rgba, "RGBA")))
    saidas.append(("voo-esquerda", saidas[2][1].transpose(Image.FLIP_LEFT_RIGHT)))
    (PASTA / "poses").mkdir(parents=True, exist_ok=True)
    coluna = Image.new("RGBA", (L, A * 8), (0, 0, 0, 0))
    for k, (nome, im) in enumerate(saidas):
        im.save(PASTA / "poses" / f"{nome}.png")
        coluna.alpha_composite(im, (0, k * A))
    coluna.save(RAIZ / "assets" / "anjo-poses.png")
    print(f"anjo-poses.png 384x4096: {len(saidas)} poses (escala {escala:.3f})")


def main():
    folha = np.asarray(Image.open(PASTA / "folha-original.png").convert("RGB"))
    alturas = []
    (PASTA / "bases").mkdir(parents=True, exist_ok=True)
    coluna = Image.new("RGBA", (L, A * 8), (0, 0, 0, 0))
    for k, d in enumerate(DIRECOES):
        celula = folha[(k // 4) * A:(k // 4 + 1) * A, (k % 4) * L:(k % 4 + 1) * L]
        rgba, figura = recortar(celula)
        rgba, cortado = posicionar(rgba, figura)
        if cortado:
            print(f"aviso: {d} perdeu {cortado // 255} px na borda da célula")
        ys = np.nonzero(figura.any(1))[0]
        alturas.append(ys.max() - ys.min())
        im = Image.fromarray(rgba, "RGBA")
        im.save(PASTA / "bases" / f"{d}.png")
        coluna.alpha_composite(im, (0, k * A))
    coluna.save(RAIZ / "assets" / "anjo-parado.png")
    print("anjo-parado.png 384x4096: 8 direções")
    if (PASTA / "poses-chatgpt.png").exists():
        poses_extras(float(np.mean(alturas)))


if __name__ == "__main__":
    main()
