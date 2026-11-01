#!/usr/bin/env python3
"""Gera o agente carmesim parado nas 8 direções repintando as bases da Eva.

O corpo e a pose são os da Eva pixel a pixel (é ela sob a máscara). Por cima:
farda militar preta com detalhes vermelhos (cinto, gola e punhos) e uma máscara
preta lisa que cobre a cabeça inteira, só com os olhos azuis à mostra. O cabelo
e os brincos somem.

Entradas: ../sprites/bases/eva/<direcao>.png (384x512, âncora 192,480).
Saídas:
  ../sprites/elenco-sala2/agente/bases/<direcao>.png   as 8 bases paradas
  ../sprites/elenco-sala2/agente/referencia-8-vistas.png  folha de identidade
  assets/agente-parado.png   uma coluna 384x4096, linhas na ordem do Ícaro
                             (norte, nordeste, leste, sudeste, sul, sudoeste, oeste, noroeste)

Uso: python3 ferramentas/gerar_agente.py [--grade]   (ou `make arte`)
     --grade salva também a prévia com as elipses e faixas medidas.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw

RAIZ = Path(__file__).resolve().parent.parent
AOC = RAIZ.parent
BASES_EVA = AOC / "sprites" / "bases" / "eva"
SAIDA_BASES = AOC / "sprites" / "elenco-sala2" / "agente" / "bases"
DIRECOES = ["norte", "nordeste", "leste", "sudeste", "sul", "sudoeste", "oeste", "noroeste"]

# Medidas por direção, em px da base 384x512:
#   cabeca   elipse da máscara (cx, cy, rx, ry)
#   pescoco  y onde a gola começa (pele acima disso vira máscara)
#   cinto    faixa de linhas do cós (y0, y1), que vira cinto vermelho
#   costas   retângulos (x0, y0, x1, y1, barra) onde o rabo de cavalo cobria a
#            roupa; barra = linha da bainha da jaqueta
#   manga    (lado, y0, y1): borda da manga que o cabelo escondia, refeita em reta
MEDIDAS = {
    "sul":      dict(cabeca=(192, 147, 46, 46), pescoco=200, cinto=(276, 290), costas=[]),
    "sudeste":  dict(cabeca=(194, 147, 46, 46), pescoco=200, cinto=(276, 290), costas=[]),
    "leste":    dict(cabeca=(188, 141, 48, 44), pescoco=196, cinto=(268, 282), costas=[]),
    "nordeste": dict(cabeca=(194, 143, 48, 44), pescoco=196, cinto=(270, 284), costas=[], manga=("esq", 246, 286)),
    "norte":    dict(cabeca=(194, 143, 47, 44), pescoco=194, cinto=(268, 282), costas=[(160, 192, 230, 284, 252)]),
    "noroeste": dict(cabeca=(190, 141, 48, 44), pescoco=196, cinto=(268, 282), costas=[], manga=("dir", 250, 278)),
    "oeste":    dict(cabeca=(196, 141, 48, 44), pescoco=196, cinto=(268, 282), costas=[]),
    "sudoeste": dict(cabeca=(186, 147, 46, 46), pescoco=200, cinto=(276, 290), costas=[]),
}

CONTORNO = np.array([10, 6, 16], float)


def luminancia(c):
    return 0.299 * c[..., 0] + 0.587 * c[..., 1] + 0.114 * c[..., 2]


def tom_farda(lum, escuro=0.0):
    """Luminância original (pano claro) -> preto da farda, frio, com as dobras preservadas."""
    l = np.clip(16 + (lum - 100) / 145 * 44 - escuro, 12, 62)
    return np.stack([l * 0.94, l * 0.92, l * 1.14], -1)


def tom_vermelho(lum):
    l = np.clip(lum, 25, 120)
    return np.stack([np.clip(l * 2.4 + 30, 0, 230), l * 0.30 + 6, l * 0.42 + 10], -1)


def perto(mascara, raio):
    """Dilatação quadrada: True onde há algum True a até `raio` px."""
    m = mascara.copy()
    for dy in range(-raio, raio + 1):
        for dx in range(-raio, raio + 1):
            m |= np.roll(np.roll(mascara, dy, 0), dx, 1)
    return m


def repintar(direcao):
    m = MEDIDAS[direcao]
    im = np.asarray(Image.open(BASES_EVA / f"{direcao}.png").convert("RGBA")).astype(float)
    cor, alfa = im[..., :3], im[..., 3]
    r, g, b = cor[..., 0], cor[..., 1], cor[..., 2]
    lum = luminancia(cor)
    h, w = alfa.shape
    yy, xx = np.mgrid[0:h, 0:w]

    opaco = alfa >= 8
    azul = opaco & (b > r + 35) & (b > 90)
    brinco = opaco & (r > 140) & (g < 100) & (b < 100) & (r - g > 70)
    pele = opaco & (r - b > 35) & (r > 110) & (r > g) & ~brinco
    escuro = opaco & (lum < 95) & ~azul & ~pele & ~brinco
    claro = opaco & ~azul & ~pele & ~escuro & ~brinco

    cx, cy, rx, ry = m["cabeca"]
    nx, ny = (xx - cx) / rx, (yy - cy) / ry
    # crânio redondo em cima, queixo afinando embaixo
    nx_q = nx / np.where(ny > 0, 1 - 0.38 * np.clip(ny, 0, 1) ** 2, 1)
    cabeca = nx_q ** 2 + ny ** 2 <= 1.0
    pescoco, (c0, c1) = m["pescoco"], m["cinto"]

    # Linha a linha, o corpo vai do primeiro ao último pixel de pano ou pele fora
    # da cabeça; o escuro fora desse vão é cabelo solto.
    corpo_linha = (pele | claro) & ~cabeca
    vao = np.zeros_like(opaco)
    for y in range(h):
        xs = np.nonzero(corpo_linha[y])[0]
        if len(xs):
            vao[y, max(0, xs[0] - 3):xs[-1] + 4] = True
    # do joelho para baixo não há cabelo: botas e solas ficam inteiras
    fica = opaco & (cabeca | vao | (yy > c1 + 30)) & ~(brinco & ~cabeca)
    # acima da gola, fora da máscara, só o pescoço e o pano (com o contorno deles);
    # orelhas e mechas saem
    orelha = pele & ~cabeca & (yy < pescoco) & ((yy < cy + ry * 0.8) | (np.abs(xx - cx) > rx * 0.55))
    pescoco_ou_pano = ((pele & ~orelha) | claro) & ~cabeca
    fica &= (yy >= pescoco) | cabeca | perto(pescoco_ou_pano, 2)
    fica &= ~orelha

    # mechas que descem por cima da roupa: segue o cabelo a partir do que já
    # saiu, por pixels escuros que não são contorno (o contorno é mais escuro)
    costas = np.zeros_like(opaco)
    for (x0, y0, x1, y1, _) in m["costas"]:
        costas[y0:y1 + 1, x0:x1 + 1] = True
    fio = escuro & (lum > 19) & ~cabeca & ~costas & ((yy < c0) | ((yy > c1) & (yy < c1 + 30)))
    cabelo = opaco & ~fica & escuro
    while True:
        mais = perto(cabelo, 1) & fio & ~cabelo
        if not mais.any():
            break
        cabelo |= mais
    fica &= ~cabelo

    nova = np.zeros((h, w, 4), float)
    nova[..., :3] = cor
    nova[..., 3] = np.where(fica, 255, 0)

    # farda: todo o pano claro; a pele da barriga vira camisa, a das mãos luva
    nova[claro & fica] = np.concatenate([tom_farda(lum), np.full(lum.shape + (1,), 255)], -1)[claro & fica]
    camisa = pele & (yy >= pescoco) & (yy < c1)
    luva = pele & (yy >= c1)
    nova[camisa, :3] = tom_farda(lum * 0.92)[camisa]
    nova[luva, :3] = tom_farda(lum - 70, 10)[luva]

    # onde o rabo de cavalo cobria as costas: pano da farda, sem os fios
    # costas cobertas pelo rabo de cavalo: pano liso no tom do pano que aparece
    # dos lados, a barra da jaqueta continuada e, abaixo dela, a camisa
    for (x0, y0, x1, y1, barra) in m["costas"]:
        lados = claro & (lum > 150) & (((xx >= x0 - 14) & (xx < x0)) | ((xx > x1) & (xx <= x1 + 14)))
        ref = 190.0
        for y in range(y0, min(y1, c0 - 1) + 1):
            amostra = lum[y][lados[y]]
            if len(amostra):
                ref = 0.7 * ref + 0.3 * float(amostra.mean())
            sel = opaco[y, x0:x1 + 1].copy()
            if y < barra:
                tom = tom_farda(np.array(ref))
            elif y < barra + 2:
                tom = CONTORNO
            else:
                tom = tom_farda(np.array(150.0))
            nova[y, x0:x1 + 1][sel, :3] = tom
            nova[y, x0:x1 + 1][sel, 3] = 255

    # cinto vermelho no cós (só o pano escuro, não o contorno)
    cos = escuro & fica & ~costas & (yy >= c0) & (yy <= c1) & (lum > 18) & ~cabeca
    nova[cos, :3] = tom_vermelho(lum + 20)[cos]
    # nas costas, o cinto passa liso por onde o cabelo caía
    cos_costas = costas & opaco & (yy > c0) & (yy < c1)
    nova[cos_costas, :3] = tom_vermelho(np.full(lum.shape, 62.0))[cos_costas]
    nova[cos_costas, 3] = 255

    # máscara: elipse inteira, luz difusa de cima, borda escura; pescoço também
    # tecido fosco: quase chapado, um brilho largo no alto e sombra no queixo
    nivel = np.where(ny < -0.62, 2, np.where(ny < 0.55, 1, 0))
    nivel = np.where((ny < -0.35) & (nx < -0.2) & (nx_q ** 2 + ny ** 2 > 0.55), 2, nivel)
    tom = np.choose(nivel, [15, 21, 30]).astype(float)
    mascara_cor = np.stack([tom * 0.92, tom * 0.90, tom * 1.12], -1)
    pescoco_pele = pele & (yy < pescoco) & ~cabeca
    area_mascara = cabeca | pescoco_pele
    # olhos: o desenho inteiro do olho (íris, pupila e brilho), sem pele nem cílios
    azul_cab = azul & cabeca
    olhos = perto(azul_cab, 1) & cabeca & ~pele & ~(escuro & ~perto(azul_cab, 0))
    olhos |= azul_cab
    brilho = cabeca & (lum > 170) & perto(azul_cab, 2) & ~pele
    pinta = area_mascara & ~olhos & ~brilho
    nova[pinta, :3] = mascara_cor[pinta]
    nova[pescoco_pele, :3] = tom_farda(lum - 60, 10)[pescoco_pele]
    nova[cabeca, 3] = 255
    nuca = (np.abs(xx - cx) <= rx * 0.22) & (yy >= cy + ry * 0.6) & (yy < pescoco + 4) & ~cabeca \
        & (nova[..., 3] == 0) & opaco
    nova[nuca, :3] = mascara_cor[nuca] * 0 + np.array([15 * 0.92, 15 * 0.9, 15 * 1.12])
    nova[nuca, 3] = 255
    # íris mais viva e um halo azul fraco, para ler na escala do jogo
    nova[azul_cab, :3] = np.clip(cor[azul_cab] * np.array([0.9, 1.15, 1.35]) + 12, 0, 255)
    halo = perto(azul_cab, 2) & cabeca & ~olhos & ~brilho
    nova[halo, :3] = np.array([26, 44, 92], float)
    borda = cabeca & ~(((nx * rx / (rx - 3)) ** 2 + (ny * ry / (ry - 3)) ** 2) <= 1.0)
    nova[borda & ~olhos, :3] = CONTORNO

    # gola e punhos vermelhos: pano colado ao pescoço e às luvas
    gola = claro & fica & (yy < pescoco + 14) & perto(pescoco_pele | cabeca, 4) & ~cabeca
    acima_da_luva = np.zeros_like(luva)
    for d in range(1, 6):
        acima_da_luva |= np.roll(luva, -d, 0)
    punho = claro & fica & acima_da_luva
    for parte in (gola, punho):
        nova[parte, :3] = tom_vermelho(lum * 0.45)[parte]

    # mechas que passavam por cima da manga deixam falhas estreitas: fecha as de
    # até 6 px na linha, com a média do pano dos dois lados
    for y in range(pescoco, h):
        cheio = nova[y, :, 3] > 0
        xs = np.nonzero(cheio)[0]
        for x0, x1 in zip(xs[:-1], xs[1:]):
            if 1 < x1 - x0 <= 11 and opaco[y, x0 + 1:x1].all():
                meio = (nova[y, x0, :3] + nova[y, x1, :3]) / 2
                if luminancia(meio) < 18:
                    meio = tom_farda(np.array(150.0))
                nova[y, x0 + 1:x1, :3] = meio
                nova[y, x0 + 1:x1, 3] = 255

    # manga escondida pelo cabelo: a borda vira uma reta entre as duas pontas
    if "manga" in m:
        lado, y0, y1 = m["manga"]
        def borda(y):
            xs = np.nonzero(nova[y, :, 3] > 0)[0]
            return xs[0] if lado == "esq" else xs[-1]
        b0, b1 = borda(y0), borda(y1)
        for y in range(y0, y1 + 1):
            alvo = int(round(b0 + (b1 - b0) * (y - y0) / (y1 - y0)))
            atual = borda(y)
            if lado == "esq" and alvo < atual:
                nova[y, alvo:atual + 3, :3] = tom_farda(np.array(185.0))
                nova[y, alvo:atual + 3, 3] = 255
            elif lado == "dir" and alvo > atual:
                nova[y, atual - 2:alvo + 1, :3] = tom_farda(np.array(185.0))
                nova[y, atual - 2:alvo + 1, 3] = 255

    # contorno onde o cabelo foi cortado
    sumiu = opaco & (nova[..., 3] == 0)
    exposto = (nova[..., 3] > 0) & perto(sumiu, 2) & (luminancia(nova[..., :3]) > 14)
    nova[exposto, :3] = CONTORNO

    return Image.fromarray(np.clip(nova, 0, 255).astype(np.uint8), "RGBA")


def folha_referencia(imagens):
    """1536x1024, 4x2, na ordem visual das folhas originais de Ícaro e Eva."""
    ordem = ["norte", "noroeste", "oeste", "sudoeste", "sul", "sudeste", "leste", "nordeste"]
    folha = Image.new("RGBA", (1536, 1024), (24, 20, 26, 255))
    for k, d in enumerate(ordem):
        folha.alpha_composite(imagens[d], ((k % 4) * 384, (k // 4) * 512))
    return folha


def grade(imagens, caminho):
    larg = 300
    prev = Image.new("RGBA", (larg * 8, 340), (90, 140, 90, 255))
    for k, d in enumerate(DIRECOES):
        m = MEDIDAS[d]
        base = Image.open(BASES_EVA / f"{d}.png").convert("RGBA")
        quadro = Image.new("RGBA", (384, 512), (90, 140, 90, 255))
        quadro.alpha_composite(base)
        dr = ImageDraw.Draw(quadro)
        cx, cy, rx, ry = m["cabeca"]
        dr.ellipse((cx - rx, cy - ry, cx + rx, cy + ry), outline=(255, 255, 0, 255))
        dr.line((0, m["pescoco"], 384, m["pescoco"]), fill=(0, 255, 255, 255))
        for y in m["cinto"]:
            dr.line((0, y, 384, y), fill=(255, 0, 0, 255))
        prev.alpha_composite(quadro.crop((40, 40, 340, 380)).resize((150, 170)), (k * larg, 0))
        novo = Image.new("RGBA", (384, 512), (90, 140, 90, 255))
        novo.alpha_composite(imagens[d])
        prev.alpha_composite(novo.crop((40, 40, 340, 380)).resize((150, 170)), (k * larg + 150, 0))
        prev.alpha_composite(novo.crop((40, 40, 340, 380)).resize((150, 170)), (k * larg + 150, 170))
    prev.save(caminho)


def main():
    imagens = {d: repintar(d) for d in DIRECOES}
    SAIDA_BASES.mkdir(parents=True, exist_ok=True)
    for d, im in imagens.items():
        im.save(SAIDA_BASES / f"{d}.png")
    folha_referencia(imagens).save(SAIDA_BASES.parent / "referencia-8-vistas.png")
    coluna = Image.new("RGBA", (384, 512 * 8), (0, 0, 0, 0))
    for k, d in enumerate(DIRECOES):
        coluna.alpha_composite(imagens[d], (0, k * 512))
    coluna.save(RAIZ / "assets" / "agente-parado.png")
    if "--grade" in sys.argv:
        grade(imagens, SAIDA_BASES.parent / "grade-medidas.png")
    print("agente-parado.png 384x4096: 8 direções")


if __name__ == "__main__":
    main()
