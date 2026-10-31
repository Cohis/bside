#!/usr/bin/env python3
"""Gera a pixel art da Fase 1 (interior da B-Side).

Saídas, sempre iguais para a mesma semente:
  assets/tileset-bside.png  tiles 16x16 e sprites dos móveis
  assets/luz.png            gradiente radial usado pelas luzes
  assets/vinheta.png        escurecimento das bordas da tela
  tileset.inc               .equ com a posição de cada peça no atlas

Uso: python3 ferramentas/gerar_tileset.py   (ou `make arte`)
"""
import math
import random
from pathlib import Path

from PIL import Image

RAIZ = Path(__file__).resolve().parent.parent
T = 16
LARGURA_ATLAS = 512


def cor(h, a=255):
    h = h.lstrip("#")
    return (int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16), a)


def mult(c, f):
    return tuple(max(0, min(255, int(round(v * f)))) for v in c[:3]) + (c[3],)


def mistura(a, b, t):
    return tuple(int(round(a[i] + (b[i] - a[i]) * t)) for i in range(3)) + (255,)


def alfa(c, a):
    return c[:3] + (a,)


CONTORNO = cor("120e18")

# Capas de disco da loja: tons de papel antigo, vinho, ocre, verde e azul fechados.
CAPAS_SOBRIAS = (cor("d8cdb0"), cor("8a2a2a"), cor("b08840"), cor("3a5a44"), cor("2a3a5a"),
                 cor("1e1c20"), cor("6a4a34"), cor("c8c0b0"), cor("a83a30"))
MADEIRA_ESCURA = cor("2d201c")
MADEIRA = cor("5c3b2a")
MADEIRA_CLARA = cor("8a5d3e")
METAL = cor("4a4d5a")
METAL_CLARO = cor("7d8294")


class Tela:
    def __init__(self, w, h):
        self.w, self.h = w, h
        self.im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
        self.p = self.im.load()

    def px(self, x, y, c):
        x, y = int(x), int(y)
        if not (0 <= x < self.w and 0 <= y < self.h):
            return
        if c[3] < 255:
            b = self.p[x, y]
            a = c[3] / 255
            if b[3] == 0:
                self.p[x, y] = c
            else:
                self.p[x, y] = tuple(int(b[i] * (1 - a) + c[i] * a) for i in range(3)) + (max(b[3], c[3]),)
        else:
            self.p[x, y] = c

    def ret(self, x0, y0, x1, y1, c):
        for y in range(int(y0), int(y1) + 1):
            for x in range(int(x0), int(x1) + 1):
                self.px(x, y, c)

    def hlin(self, x0, x1, y, c):
        self.ret(x0, y, x1, y, c)

    def vlin(self, x, y0, y1, c):
        self.ret(x, y0, x, y1, c)

    def moldura(self, x0, y0, x1, y1, c):
        self.hlin(x0, x1, y0, c)
        self.hlin(x0, x1, y1, c)
        self.vlin(x0, y0, y1, c)
        self.vlin(x1, y0, y1, c)

    def elipse(self, cx, cy, rx, ry, c):
        for y in range(int(cy - ry) - 1, int(cy + ry) + 2):
            for x in range(int(cx - rx) - 1, int(cx + rx) + 2):
                if ((x + 0.5 - cx) / rx) ** 2 + ((y + 0.5 - cy) / ry) ** 2 <= 1:
                    self.px(x, y, c)

    def ruido(self, x0, y0, x1, y1, rng, amp, prob=1.0):
        for y in range(y0, y1 + 1):
            for x in range(x0, x1 + 1):
                if 0 <= x < self.w and 0 <= y < self.h and self.p[x, y][3] and rng.random() < prob:
                    self.p[x, y] = mult(self.p[x, y], 1 + rng.uniform(-amp, amp))

    def contornar(self, c=CONTORNO):
        """Contorno interno: todo pixel opaco que encosta no vazio vira contorno."""
        alvo = []
        for y in range(self.h):
            for x in range(self.w):
                if self.p[x, y][3] < 200:
                    continue
                for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    nx, ny = x + dx, y + dy
                    if not (0 <= nx < self.w and 0 <= ny < self.h) or self.p[nx, ny][3] < 200:
                        alvo.append((x, y))
                        break
        for x, y in alvo:
            self.p[x, y] = c

    def colar(self, outra, x, y):
        self.im.alpha_composite(outra.im, (int(x), int(y)))


# ---------------------------------------------------------------- pisos

def piso_tabuas(base, semente, var, largura_tabua=4):
    t = Tela(T, T)
    rng = random.Random(semente * 97 + var)
    junta = mult(base, 0.55)
    for linha in range(T // largura_tabua):
        y0 = linha * largura_tabua
        tom = mult(base, rng.uniform(0.93, 1.07))
        t.ret(0, y0, 15, y0 + largura_tabua - 1, tom)
        t.hlin(0, 15, y0, mult(tom, 1.08))
        for _ in range(3):
            x = rng.randrange(16)
            y = y0 + rng.randrange(1, largura_tabua - 1)
            t.hlin(x, min(15, x + rng.randrange(2, 7)), y, mult(tom, 0.86))
        t.hlin(0, 15, y0 + largura_tabua - 1, junta)
        if rng.random() < 0.3:
            jx = rng.randrange(16)
            t.vlin(jx, y0, y0 + largura_tabua - 2, junta)
        if rng.random() < 0.25:
            t.px(rng.randrange(16), y0 + 1, mult(tom, 0.7))
    t.ruido(0, 0, 15, 15, rng, 0.04)
    return t


def piso_xadrez(var):
    t = Tela(T, T)
    rng = random.Random(500 + var)
    claro, escuro = cor("a99f8e"), cor("34323f")
    for qy in range(2):
        for qx in range(2):
            c = claro if (qx + qy) % 2 == 0 else escuro
            t.ret(qx * 8, qy * 8, qx * 8 + 7, qy * 8 + 7, c)
            t.hlin(qx * 8, qx * 8 + 6, qy * 8, mult(c, 1.08))
    for k in (7, 15):
        t.hlin(0, 15, k, cor("1f1d26"))
        t.vlin(k, 0, 15, cor("1f1d26"))
    t.ruido(0, 0, 15, 15, rng, 0.07)
    if var == 2:
        t.elipse(5, 11, 3, 2, cor("3d2f26", 70))
    if var == 3:
        t.hlin(9, 13, 3, mult(claro, 0.8))
    return t


def piso_parquete(var):
    """Parquete de nogueira em cesto: blocos 8x8 de tacos alternando a direção."""
    t = Tela(T, T)
    rng = random.Random(700 + var)
    base = cor("3f2c1f")
    junta = cor("2a1c13")
    for by in range(2):
        for bx in range(2):
            x0, y0 = bx * 8, by * 8
            horizontal = (bx + by) % 2 == 0
            for k in range(4):
                tom = mult(base, rng.uniform(0.93, 1.07))
                if horizontal:
                    t.ret(x0, y0 + k * 2, x0 + 7, y0 + k * 2 + 1, tom)
                    t.hlin(x0, x0 + 7, y0 + k * 2, mult(tom, 1.05))
                else:
                    t.ret(x0 + k * 2, y0, x0 + k * 2 + 1, y0 + 7, tom)
                    t.vlin(x0 + k * 2, y0, y0 + 7, mult(tom, 1.05))
            t.hlin(x0, x0 + 7, y0 + 7, junta)
            t.vlin(x0 + 7, y0, y0 + 7, junta)
    t.ruido(0, 0, 15, 15, rng, 0.04)
    return t


def piso_concreto(var):
    t = Tela(T, T)
    rng = random.Random(900 + var)
    base = cor("4f4d4c")
    t.ret(0, 0, 15, 15, base)
    t.ruido(0, 0, 15, 15, rng, 0.12)
    for _ in range(5):
        t.px(rng.randrange(16), rng.randrange(16), mult(base, 0.7))
    if var == 1:
        x, y = 0, rng.randrange(4, 12)
        while x < 16:
            t.px(x, y, mult(base, 0.55))
            x += 1
            y += rng.choice((-1, 0, 0, 1))
    if var == 2:
        t.elipse(8, 8, 5, 3, cor("2e2a26", 70))
    if var == 3:
        t.hlin(0, 15, 15, mult(base, 0.75))
    return t


def degrau(fator, var):
    t = Tela(T, T)
    rng = random.Random(1100 + var)
    piso = mult(cor("6e4a35"), fator)
    for k in range(2):
        y0 = k * 8
        t.ret(0, y0, 15, y0 + 5, piso)
        t.hlin(0, 15, y0, mult(piso, 1.25))
        t.hlin(0, 15, y0 + 5, mult(piso, 0.8))
        t.ret(0, y0 + 6, 15, y0 + 7, mult(cor("24170f"), fator + 0.2))
    t.ruido(0, 0, 15, 15, rng, 0.06)
    return t


def vao_escada(var):
    t = degrau(0.32, var)
    t.ret(0, 0, 15, 15, cor("05040a", 90))
    return t


# --------------------------------------------------------------- paredes

def topo(mascara):
    """Topo de parede (o que a câmera vê por cima). Bits abertos: N=1, L=2, S=4, O=8."""
    t = Tela(T, T)
    t.ret(0, 0, 15, 15, cor("0e0c14"))
    rng = random.Random(1300 + mascara)
    t.ruido(0, 0, 15, 15, rng, 0.25, 0.3)
    borda = cor("2c2638")
    if mascara & 1:
        t.hlin(0, 15, 0, CONTORNO)
        t.hlin(0, 15, 1, borda)
    if mascara & 2:
        t.vlin(15, 0, 15, CONTORNO)
        t.vlin(14, 0, 15, borda)
    if mascara & 8:
        t.vlin(0, 0, 15, CONTORNO)
        t.vlin(1, 0, 15, borda)
    if mascara & 4:
        t.hlin(0, 15, 13, borda)
        t.hlin(0, 15, 14, cor("3d354e"))
        t.hlin(0, 15, 15, cor("4a4060"))
    return t


def face(padrao, rodape=MADEIRA_ESCURA, moldura=None, semente=0):
    """Seis tiles: (topo, meio, base) x (coluna par, ímpar)."""
    pecas = []
    for posicao in range(3):
        for paridade in range(2):
            t = Tela(T, T)
            rng = random.Random(semente * 31 + posicao * 7 + paridade)
            padrao(t, posicao, paridade, rng)
            if posicao == 0:
                m = moldura or mult(t.p[8, 8], 1.35)
                t.hlin(0, 15, 0, mult(m, 0.6))
                t.hlin(0, 15, 1, m)
                t.hlin(0, 15, 2, mult(m, 0.8))
                t.hlin(0, 15, 3, alfa(CONTORNO, 120))
            if posicao == 2:
                t.hlin(0, 15, 11, alfa(CONTORNO, 110))
                t.ret(0, 12, 15, 15, rodape)
                t.hlin(0, 15, 12, mult(rodape, 1.5))
                t.hlin(0, 15, 15, CONTORNO)
            pecas.append(t)
    return pecas


def padrao_corredor(t, pos, par, rng):
    base = cor("2c403b")
    t.ret(0, 0, 15, 15, base)
    for x in (2, 3, 10, 11):
        t.vlin(x, 0, 15, cor("35504a"))
    t.vlin(6, 0, 15, cor("27393a"))
    t.ruido(0, 0, 15, 15, rng, 0.05)


def padrao_hospedes(t, pos, par, rng):
    base = cor("4f3b4d")
    t.ret(0, 0, 15, 15, base)
    for (x, y) in ((3, 3), (11, 11), (11, 3), (3, 11)):
        c = cor("634a60") if (x + y) % 16 == 6 else cor("5a4457")
        t.px(x, y, c)
        t.px(x + 1, y, c)
        t.px(x, y + 1, c)
        t.px(x + 1, y + 1, c)
    t.ruido(0, 0, 15, 15, rng, 0.06)
    if par and pos == 1:
        t.elipse(6, 10, 3, 4, cor("3a2a38", 60))


def padrao_sala(t, pos, par, rng):
    base = cor("232a46")
    t.ret(0, 0, 15, 15, base)
    for x in range(0, 16, 4):
        t.vlin(x, 0, 15, cor("2a3354"))
    if pos == 2:
        t.ret(0, 2, 15, 11, cor("2f2226"))
        t.hlin(0, 15, 2, cor("4a3530"))
        t.vlin(0 if par == 0 else 15, 3, 11, cor("221819"))
    t.ruido(0, 0, 15, 15, rng, 0.05)


def padrao_loja(t, pos, par, rng):
    """Verde-garrafa em painéis, com lambri de nogueira na faixa de baixo."""
    base = cor("1f3229")
    t.ret(0, 0, 15, 15, base)
    t.ruido(0, 0, 15, 15, rng, 0.05)
    if pos == 1:
        # moldura dos painéis, uma a cada dois tiles
        x0, x1 = (2, 15) if par == 0 else (0, 13)
        t.hlin(x0, x1, 2, cor("2c4438"))
        t.hlin(x0, x1, 14, cor("16241d"))
        t.vlin(2 if par == 0 else 13, 2, 14, cor("2c4438") if par == 0 else cor("16241d"))
    if pos == 2:
        t.ret(0, 0, 15, 11, cor("3e2618"))
        t.hlin(0, 15, 0, cor("a8823e"))
        t.hlin(0, 15, 1, cor("5e3c26"))
        t.moldura(2 + par * 2, 3, 13 + par * 2, 9, cor("2a190f"))
        t.hlin(3 + par * 2, 12 + par * 2, 4, cor("54351f"))


def padrao_cafe(t, pos, par, rng):
    argamassa = cor("33221c")
    t.ret(0, 0, 15, 15, argamassa)
    for linha in range(4):
        y0 = linha * 4
        desloc = 4 if (linha + par) % 2 else 0
        for bx in range(-8, 16, 8):
            x0 = bx + desloc
            tom = mult(cor("7a3f2c"), rng.uniform(0.8, 1.12))
            t.ret(max(0, x0), y0, min(15, x0 + 6), y0 + 2, tom)
            t.hlin(max(0, x0), min(15, x0 + 6), y0, mult(tom, 1.15))
    if pos == 0:
        t.ret(0, 0, 15, 5, cor("2a1a14"))


def padrao_deposito(t, pos, par, rng):
    argamassa = cor("2f3036")
    t.ret(0, 0, 15, 15, argamassa)
    for linha in range(2):
        y0 = linha * 8
        desloc = 8 if (linha + par) % 2 else 0
        for bx in range(-16, 16, 16):
            x0 = bx + desloc
            tom = mult(cor("55565e"), rng.uniform(0.85, 1.08))
            t.ret(max(0, x0), y0, min(15, x0 + 14), y0 + 6, tom)
            t.hlin(max(0, x0), min(15, x0 + 14), y0, mult(tom, 1.15))
    t.ruido(0, 0, 15, 15, rng, 0.08)
    if pos == 2:
        t.ret(0, 6, 15, 11, cor("2a2620", 90))


def padrao_janela(t, pos, par, rng):
    t.ret(0, 0, 15, 15, cor("141c34"))
    t.vlin(0, 0, 15, cor("3a2a22"))


def padrao_escada(t, pos, par, rng):
    fator = (0.12, 0.25, 0.45)[pos]
    d = degrau(fator, par)
    t.colar(d, 0, 0)
    t.vlin(0, 0, 15, CONTORNO)
    t.vlin(15, 0, 15, CONTORNO)


def faces_escada():
    pecas = []
    for posicao in range(3):
        for paridade in range(2):
            t = Tela(T, T)
            padrao_escada(t, posicao, paridade, None)
            if posicao == 0:
                t.ret(0, 0, 15, 15, cor("05040a", 150))
            pecas.append(t)
    return pecas


# -------------------------------------------- colunas (paredes verticais)

def coluna_janela(pos, porta=False):
    t = topo(0)
    vidro = cor("4a3a30") if porta else cor("23345e")
    caixilho = cor("5a4636")
    x0, x1 = (3, 12) if porta else (5, 10)
    y0 = 2 if pos == 0 else 0
    y1 = 13 if pos == 2 else 15
    t.ret(x0 - 1, y0, x1 + 1, y1, caixilho)
    t.ret(x0, y0 + (1 if pos == 0 else 0), x1, y1 - (1 if pos == 2 else 0), vidro)
    t.vlin(x0 + 1, y0, y1, mult(vidro, 1.5))
    if porta and pos == 1:
        t.ret(x1 - 2, 6, x1 - 1, 9, cor("c9a24a"))
    if pos == 1 and not porta:
        t.hlin(x0, x1, 8, caixilho)
    t.vlin(0, 0, 15, CONTORNO)
    t.vlin(15, 0, 15, CONTORNO)
    if pos == 0:
        t.hlin(0, 15, 0, CONTORNO)
    if pos == 2:
        t.hlin(0, 15, 15, CONTORNO)
    return t


def coluna_guarda(pos, piso):
    t = Tela(T, T)
    t.colar(piso, 0, 0)
    t.ret(0, 0, 4, 15, cor("05040a", 120))
    corrimao = cor("4a2f22")
    t.ret(6, 0, 9, 15, cor("0a080e", 90))
    for y in range(1, 16, 4):
        t.ret(7, y, 8, y + 1, cor("2a1c16"))
    t.ret(5, 0, 8, 15, corrimao)
    t.vlin(5, 0, 15, mult(corrimao, 1.5))
    t.vlin(8, 0, 15, mult(corrimao, 0.6))
    if pos == 0:
        t.ret(4, 0, 9, 5, cor("5a3828"))
        t.moldura(4, 0, 9, 5, CONTORNO)
        t.hlin(5, 8, 1, cor("8a5a40"))
    if pos == 2:
        t.ret(4, 10, 9, 15, cor("5a3828"))
        t.moldura(4, 10, 9, 15, CONTORNO)
        t.hlin(5, 8, 11, cor("8a5a40"))
    return t


def sombra_norte():
    t = Tela(T, T)
    for y in range(8):
        t.hlin(0, 15, y, cor("05040a", int(150 * (1 - y / 8) ** 1.5)))
    return t


def sombra_oeste():
    t = Tela(T, T)
    for x in range(6):
        t.vlin(x, 0, 15, cor("05040a", int(110 * (1 - x / 6) ** 1.5)))
    return t


# ------------------------------------------------------------- móveis

def caixa(t, x, y, w, h, topo_h, c_topo, c_frente):
    """Bloco em 3/4: tampa clara em cima e frente mais escura embaixo."""
    t.ret(x, y, x + w - 1, y + topo_h - 1, c_topo)
    t.hlin(x, x + w - 1, y, mult(c_topo, 1.18))
    t.ret(x, y + topo_h, x + w - 1, y + h - 1, c_frente)
    t.hlin(x, x + w - 1, y + topo_h, mult(c_frente, 0.7))


def janela_cozinha(brilho=False):
    w, h = 224, 48
    t = Tela(w, h)
    rng = random.Random(42)
    if not brilho:
        for y in range(h):
            t.hlin(0, w - 1, y, mistura(cor("0b1028"), cor("2a2f5c"), y / h))
        # lua
        t.elipse(170, 13, 6, 6, cor("d8d4c0"))
        t.elipse(172, 12, 5, 5, cor("1b2244"))
        # silhueta da cidade
    predios = []
    x = 0
    while x < w:
        largura = rng.randrange(10, 26)
        altura = rng.randrange(12, 34)
        predios.append((x, largura, altura))
        x += largura + rng.randrange(0, 3)
    for (x0, largura, altura) in predios:
        topo_y = h - 4 - altura
        if not brilho:
            t.ret(x0, topo_y, x0 + largura - 1, h - 4, mult(cor("0a0c1c"), rng.uniform(0.9, 1.3)))
            if rng.random() < 0.3:
                t.vlin(x0 + largura // 2, topo_y - 4, topo_y, cor("0a0c1c"))
        for wy in range(topo_y + 3, h - 6, 4):
            for wx in range(x0 + 2, x0 + largura - 2, 3):
                if rng.random() < 0.22:
                    c = rng.choice((cor("e8c070"), cor("f0d890"), cor("8fb0e0"), cor("e89060")))
                    t.px(wx, wy, c if brilho else mult(c, 0.75))
    if brilho:
        t.elipse(170, 13, 6, 6, cor("d8d4c0", 220))
        t.elipse(172, 12, 5, 5, (0, 0, 0, 0))
        # recorta a parte escura da lua
        for yy in range(h):
            for xx in range(w):
                if ((xx + 0.5 - 172) / 5) ** 2 + ((yy + 0.5 - 12) / 5) ** 2 <= 1:
                    t.p[xx, yy] = (0, 0, 0, 0)
        return t
    # chuva fina no vidro
    for _ in range(70):
        rx, ry = rng.randrange(w), rng.randrange(h - 8)
        t.vlin(rx, ry, ry + rng.randrange(2, 5), cor("6a7aa8", 70))
    # caixilhos e peitoril
    caixilho = cor("4a3426")
    t.ret(0, 0, w - 1, 2, caixilho)
    t.hlin(0, w - 1, 1, mult(caixilho, 1.3))
    for k in range(0, w, 32):
        t.ret(k, 0, k + 2, h - 1, caixilho)
        t.vlin(k + 1, 0, h - 1, mult(caixilho, 1.3))
    t.ret(w - 3, 0, w - 1, h - 1, caixilho)
    t.hlin(0, w - 1, 22, caixilho)
    t.ret(0, h - 5, w - 1, h - 1, cor("7a5a42"))
    t.hlin(0, w - 1, h - 5, cor("a07a58"))
    t.hlin(0, w - 1, h - 1, CONTORNO)
    for k in range(4, w - 4, 32):
        t.ret(k + 2, 3, k + 12, 21, cor("ffffff", 10))
    return t


def bancada():
    w, h = 144, 28
    t = Tela(w, h)
    caixa(t, 0, 0, w, h, 11, cor("8e8b84"), cor("5a3a2a"))
    for k in range(0, w, 24):
        t.moldura(k + 2, 13, k + 21, h - 3, mult(cor("5a3a2a"), 0.7))
        t.ret(k + 10, 15, k + 13, 15, METAL_CLARO)
    # pia
    t.ret(54, 2, 78, 9, cor("5d636e"))
    t.ret(56, 3, 76, 8, cor("2c3038"))
    t.ret(64, 0, 66, 4, METAL_CLARO)
    # fogão
    t.ret(100, 1, 130, 10, cor("26252b"))
    for (cx, cy) in ((107, 4), (121, 4), (107, 8), (121, 8)):
        t.elipse(cx, cy, 3, 1.6, cor("4b4a52"))
        t.elipse(cx, cy, 1.5, 0.8, cor("26252b"))
    t.ret(100, 12, 130, h - 3, cor("2e2d33"))
    t.ret(104, 15, 126, h - 6, cor("1a1a20"))
    t.hlin(104, 126, 13, METAL_CLARO)
    # tábua e panela
    t.ret(18, 2, 34, 8, cor("a77b52"))
    t.ret(86, -1, 94, 6, cor("3b3f48"))
    t.contornar()
    return t


def geladeira():
    w, h = 20, 46
    t = Tela(w, h)
    caixa(t, 0, 0, w, h, 6, cor("aab8b0"), cor("8a9a92"))
    t.ret(0, 6, 3, h - 1, cor("6e7d76"))
    t.hlin(0, w - 1, 22, cor("5e6b65"))
    t.vlin(5, 10, 18, cor("cdd8d2"))
    t.vlin(5, 26, 36, cor("cdd8d2"))
    t.ret(10, 12, 12, 14, cor("c8584a"))
    t.ret(14, 28, 16, 30, cor("e0c060"))
    t.contornar()
    return t


def mesa(w=44, h=24, c=None):
    t = Tela(w, h)
    c = c or cor("6d4a34")
    t.ret(0, 0, w - 1, 11, c)
    t.hlin(0, w - 1, 0, mult(c, 1.25))
    t.ret(0, 12, w - 1, 14, mult(c, 0.6))
    for x in (2, w - 5):
        t.ret(x, 15, x + 2, h - 1, mult(c, 0.55))
    return t


def mesa_cozinha():
    t = mesa()
    t.elipse(12, 6, 4, 2.5, cor("d8d0c4"))
    t.elipse(12, 6, 2, 1.2, cor("b0a090"))
    t.ret(30, 3, 33, 7, cor("c05040"))
    t.ret(31, 3, 32, 3, cor("e07060"))
    t.contornar()
    return t


def tapete_cozinha():
    w, h = 72, 44
    t = Tela(w, h)
    rng = random.Random(14)
    t.ret(0, 0, w - 1, h - 1, cor("3a4a5a"))
    for y in range(2, h - 2, 4):
        t.hlin(2, w - 3, y, cor("4e6070"))
    t.moldura(1, 1, w - 2, h - 2, cor("c8b48a"))
    t.ruido(0, 0, w - 1, h - 1, rng, 0.08)
    return t


def lixeira():
    t = Tela(12, 16)
    t.ret(1, 2, 10, 15, cor("5a5f6a"))
    t.ret(0, 0, 11, 3, cor("7d8294"))
    t.hlin(0, 11, 0, cor("a8acb8"))
    for x in (3, 6, 9):
        t.vlin(x, 5, 13, cor("4a4e58"))
    t.contornar()
    return t


def cadeira(lado):
    w, h = 12, 20
    t = Tela(w, h)
    c = cor("4e3426")
    encosto_x = 0 if lado == "e" else w - 3
    t.ret(encosto_x, 0, encosto_x + 2, 13, c)
    t.vlin(encosto_x + (2 if lado == "e" else 0), 1, 12, mult(c, 1.4))
    t.ret(0, 9, w - 1, 12, mult(c, 1.25))
    t.ret(0, 13, w - 1, 14, mult(c, 0.7))
    t.ret(0, 15, 1, h - 1, mult(c, 0.6))
    t.ret(w - 2, 15, w - 1, h - 1, mult(c, 0.6))
    t.contornar()
    return t


def cadeira_costas():
    w, h = 14, 22
    t = Tela(w, h)
    c = cor("3a3346")
    t.ret(1, 0, w - 2, 11, c)
    t.hlin(1, w - 2, 1, mult(c, 1.4))
    t.ret(0, 12, w - 1, 15, mult(c, 0.8))
    t.vlin(6, 16, h - 1, METAL)
    t.hlin(1, w - 2, h - 1, METAL)
    t.contornar()
    return t


def pendente(c_cupula):
    w, h = 12, 22
    t = Tela(w, h)
    t.vlin(5, 0, 12, cor("1a1820"))
    t.vlin(6, 0, 12, cor("1a1820"))
    t.ret(2, 12, 9, 15, c_cupula)
    t.ret(0, 16, 11, 18, mult(c_cupula, 0.85))
    t.hlin(1, 10, 12, mult(c_cupula, 1.3))
    t.contornar()
    t.ret(3, 19, 8, 20, cor("ffe2a0"))
    return t


def cama_hospedes():
    w, h = 32, 50
    t = Tela(w, h)
    madeira = cor("5a3a2a")
    t.ret(0, 0, w - 1, 9, madeira)
    t.hlin(0, w - 1, 1, mult(madeira, 1.4))
    t.ret(1, 10, w - 2, 40, cor("c8c0b0"))
    t.ret(4, 11, w - 5, 17, cor("e2dccc"))
    t.hlin(4, w - 5, 17, cor("a8a090"))
    t.ret(1, 21, w - 2, 40, cor("44506e"))
    t.hlin(1, w - 2, 21, cor("6a789a"))
    for y in range(24, 40, 4):
        t.hlin(2, w - 3, y, cor("3a4560"))
    t.ret(1, 41, w - 2, 45, mult(madeira, 0.8))
    t.ret(0, 46, 2, h - 1, mult(madeira, 0.6))
    t.ret(w - 3, 46, w - 1, h - 1, mult(madeira, 0.6))
    t.contornar()
    return t


def escrivaninha():
    w, h = 44, 26
    t = Tela(w, h)
    c = cor("5e4030")
    caixa(t, 0, 8, w, 18, 8, c, mult(c, 0.75))
    t.ret(w - 16, 18, w - 3, h - 3, mult(c, 0.6))
    t.hlin(w - 12, w - 7, 21, METAL_CLARO)
    # luminária
    t.vlin(8, 1, 9, cor("2a2a30"))
    t.ret(5, 0, 12, 3, cor("b58a3a"))
    t.ret(5, 12, 10, 13, cor("2a2a30"))
    # papéis
    t.ret(20, 9, 30, 14, cor("d8d0bc"))
    t.hlin(22, 28, 11, cor("8a8478"))
    t.contornar()
    return t


def tv():
    w, h = 58, 34
    t = Tela(w, h)
    t.ret(0, 0, w - 1, h - 1, cor("0c0c10"))
    t.ret(2, 2, w - 3, h - 4, cor("141a26"))
    t.hlin(1, w - 2, h - 2, cor("26262e"))
    t.px(w // 2, h - 2, cor("e05050"))
    t.contornar()
    return t


def tela_tv():
    w, h = 54, 28
    t = Tela(w, h)
    rng = random.Random(77)
    for y in range(h):
        for x in range(w):
            v = rng.uniform(0.75, 1.0)
            t.p[x, y] = mult(cor("6fa8d8"), v * (0.85 if y % 2 else 1.0))
    t.ret(6, 6, 24, 18, cor("9cc8f0"))
    t.ret(28, 10, 46, 22, cor("4a7ab0"))
    t.hlin(0, w - 1, 3, cor("c0e0ff"))
    return t


def rack():
    w, h = 68, 20
    t = Tela(w, h)
    c = cor("3a2a24")
    caixa(t, 0, 0, w, h, 6, c, mult(c, 0.75))
    for k in range(3):
        t.moldura(3 + k * 21, 8, 21 + k * 21, h - 3, mult(c, 0.55))
    t.ret(26, 9, 40, 14, cor("1a1a20"))
    t.px(38, 11, cor("40d070"))
    t.ret(6, -1, 12, 4, cor("2a2a30"))
    t.contornar()
    return t


def sofa_costas():
    w, h = 64, 30
    t = Tela(w, h)
    c = cor("5a2a36")
    t.ret(0, 4, 7, h - 4, mult(c, 0.85))
    t.ret(w - 8, 4, w - 1, h - 4, mult(c, 0.85))
    t.ret(6, 0, w - 7, 12, mult(c, 1.1))
    for x in (6, 23, 40):
        t.ret(x + 1, 1, x + 16, 10, mult(c, 1.2))
        t.hlin(x + 2, x + 15, 1, mult(c, 1.45))
    t.ret(6, 13, w - 7, h - 4, c)
    for x in range(10, w - 10, 6):
        t.vlin(x, 15, h - 6, mult(c, 0.82))
    t.ret(2, h - 3, 4, h - 1, MADEIRA_ESCURA)
    t.ret(w - 5, h - 3, w - 3, h - 1, MADEIRA_ESCURA)
    t.contornar()
    return t


def tapete():
    w, h = 104, 64
    t = Tela(w, h)
    rng = random.Random(9)
    base = cor("5a2430")
    t.ret(0, 0, w - 1, h - 1, base)
    t.moldura(2, 2, w - 3, h - 3, cor("c49a5a"))
    t.moldura(5, 5, w - 6, h - 6, cor("2e1c40"))
    t.moldura(6, 6, w - 7, h - 7, cor("2e1c40"))
    cx, cy = w / 2, h / 2
    for y in range(9, h - 9):
        for x in range(9, w - 9):
            d = abs(x - cx) / (w / 2 - 9) + abs(y - cy) / (h / 2 - 9)
            if 0.55 < d < 0.62 or 0.25 < d < 0.3:
                t.px(x, y, cor("c49a5a"))
            elif d < 0.12:
                t.px(x, y, cor("2e1c40"))
    t.ruido(0, 0, w - 1, h - 1, rng, 0.08)
    for x in range(0, w, 3):
        t.vlin(x, 0, 0, cor("d8c8a8"))
        t.vlin(x, h - 1, h - 1, cor("d8c8a8"))
    return t


def estante(livros=True):
    w, h = 56, 52
    t = Tela(w, h)
    rng = random.Random(21)
    c = cor("4a3020")
    caixa(t, 0, 0, w, h, 6, mult(c, 1.2), c)
    for k in range(4):
        y0 = 8 + k * 11
        t.ret(3, y0, w - 4, y0 + 8, cor("1c120e"))
        t.hlin(2, w - 3, y0 + 9, mult(c, 1.3))
        x = 4
        while x < w - 5:
            largura = rng.choice((1, 2, 2, 3))
            altura = rng.randrange(5, 9)
            tom = rng.choice((cor("8a3a3a"), cor("3a5a7a"), cor("c8a050"), cor("4a6a4a"), cor("6a4a7a"), cor("b0a090"), cor("1a1a24")))
            if rng.random() < 0.85:
                t.ret(x, y0 + 8 - altura + 1, x + largura - 1, y0 + 8, mult(tom, 0.8))
                t.vlin(x, y0 + 8 - altura + 1, y0 + 8, tom)
            x += largura
    # planta no topo
    t.ret(40, 0, 47, 4, cor("6a4030"))
    t.contornar()
    return t


def planta_topo():
    t = Tela(16, 12)
    for (cx, cy) in ((4, 6), (8, 3), (12, 6), (8, 8)):
        t.elipse(cx, cy, 3.5, 2.5, cor("3a6a40"))
        t.px(cx, cy - 1, cor("5a9a5a"))
    t.contornar()
    return t


def cama_icaro_estrutura():
    w, h = 56, 84
    t = Tela(w, h)
    barra = cor("3e4250")
    luz = cor("7c8296")
    # postes traseiros (encostados na parede, mais curtos na tela)
    for x in (1, w - 13):
        t.ret(x, 0, x + 2, 52, mult(barra, 0.8))
    # postes da frente
    for x in (1, w - 13):
        t.ret(x, 20, x + 2, h - 1, barra)
        t.vlin(x, 20, h - 1, luz)
        t.ret(x - 1, h - 2, x + 3, h - 1, mult(barra, 0.7))
    # travessas
    t.hlin(1, w - 11, 56, barra)
    t.hlin(1, w - 11, 57, mult(barra, 0.7))
    # escada lateral
    x0, x1 = w - 9, w - 2
    t.ret(x0, 22, x0 + 1, h - 1, barra)
    t.ret(x1 - 1, 22, x1, h - 1, barra)
    t.vlin(x0, 22, h - 1, luz)
    for y in range(28, h - 2, 8):
        t.hlin(x0, x1, y, luz)
        t.hlin(x0, x1, y + 1, barra)
    return t


def cama_icaro_colchao():
    w, h = 50, 34
    t = Tela(w, h)
    barra = cor("3e4250")
    # plataforma vista de cima e de lado
    t.ret(0, 6, w - 1, 27, cor("2e3140"))
    t.ret(1, 7, w - 2, 24, cor("d0c8c0"))
    t.ret(2, 8, 11, 15, cor("ece6dc"))
    t.hlin(2, 11, 15, cor("b0a8a0"))
    t.ret(12, 9, w - 2, 24, cor("4a3666"))
    t.hlin(12, w - 2, 9, cor("6a5090"))
    for x in range(16, w - 2, 7):
        t.vlin(x, 11, 23, cor("3c2c56"))
    t.ret(0, 25, w - 1, 30, barra)
    t.hlin(0, w - 1, 25, cor("7c8296"))
    t.ret(0, 31, w - 1, 33, cor("161820"))
    # grade de proteção
    t.hlin(0, w - 1, 0, cor("7c8296"))
    t.hlin(0, w - 1, 1, barra)
    for x in range(0, w, 6):
        t.vlin(x, 0, 7, barra)
    t.contornar()
    # luzinha de leitura presa na grade
    t.ret(w - 6, 2, w - 4, 4, cor("ffd890"))
    return t


def pufe():
    w, h = 22, 18
    t = Tela(w, h)
    c = cor("3a5a5a")
    t.elipse(11, 10, 10.5, 7.5, mult(c, 0.8))
    t.elipse(11, 8, 10, 6.5, c)
    t.elipse(9, 6, 5, 3, mult(c, 1.25))
    t.contornar()
    return t


def luminaria():
    w, h = 12, 38
    t = Tela(w, h)
    t.ret(1, 0, 10, 8, cor("c9a46a"))
    t.hlin(1, 10, 0, cor("e0c490"))
    t.ret(2, 9, 9, 9, cor("8a6a40"))
    t.vlin(5, 10, h - 3, cor("2a2a30"))
    t.vlin(6, 10, h - 3, cor("4a4a54"))
    t.ret(2, h - 3, 9, h - 1, cor("2a2a30"))
    t.contornar()
    return t


def planta():
    w, h = 18, 28
    t = Tela(w, h)
    rng = random.Random(5)
    for _ in range(9):
        cx = rng.uniform(4, 14)
        cy = rng.uniform(2, 14)
        t.elipse(cx, cy, rng.uniform(2.5, 4), rng.uniform(1.5, 2.5), mult(cor("3a6a40"), rng.uniform(0.8, 1.2)))
    for _ in range(6):
        t.px(rng.uniform(4, 14), rng.uniform(2, 13), cor("6aa86a"))
    t.ret(4, 17, 13, h - 1, cor("8a4a34"))
    t.hlin(4, 13, 17, cor("b06a4a"))
    t.hlin(4, 13, 18, cor("5a2e20"))
    t.contornar()
    return t


def quadro(w, h, tela_c, semente):
    t = Tela(w, h)
    rng = random.Random(semente)
    t.ret(0, 0, w - 1, h - 1, cor("6a4a2a"))
    t.ret(2, 2, w - 3, h - 3, tela_c)
    for _ in range(4):
        t.elipse(rng.uniform(3, w - 3), rng.uniform(3, h - 3), rng.uniform(1, 3), rng.uniform(1, 2), mult(tela_c, rng.uniform(0.6, 1.5)))
    t.contornar()
    return t


def arandela():
    t = Tela(8, 10)
    t.ret(3, 4, 4, 9, cor("4a3a2a"))
    t.ret(0, 0, 7, 4, cor("e8c88a"))
    t.hlin(0, 7, 0, cor("fff0c8"))
    t.contornar()
    return t


def passadeira():
    w, h = 26, 64
    t = Tela(w, h)
    rng = random.Random(3)
    t.ret(0, 0, w - 1, h - 1, cor("4a2a2a"))
    t.vlin(2, 0, h - 1, cor("a07a4a"))
    t.vlin(w - 3, 0, h - 1, cor("a07a4a"))
    for y in range(0, h, 8):
        t.px(w // 2, y + 3, cor("a07a4a"))
        t.px(w // 2 - 1, y + 4, cor("a07a4a"))
        t.px(w // 2 + 1, y + 4, cor("a07a4a"))
        t.px(w // 2, y + 5, cor("a07a4a"))
    t.ruido(0, 0, w - 1, h - 1, rng, 0.08)
    return t


def batente():
    w, h = 4, 48
    t = Tela(w, h)
    t.ret(0, 0, w - 1, h - 1, cor("4a3020"))
    t.vlin(1, 0, h - 1, cor("6a4a30"))
    t.contornar()
    return t


def letreiro_fundo():
    """Placa esmaltada vermelha com filete creme e moldura de latão."""
    w, h = 112, 36
    t = Tela(w, h)
    t.ret(0, 0, w - 1, h - 1, cor("8a6a32"))
    t.hlin(1, w - 2, 1, cor("c8a258"))
    t.ret(2, 2, w - 3, h - 3, cor("7a1418"))
    for y in range(2, h - 2):
        t.hlin(2, w - 3, y, mistura(cor("8e1a1e"), cor("5e0e12"), (y - 2) / (h - 4)))
    t.moldura(4, 4, w - 5, h - 5, cor("e8dfcc"))
    t.contornar()
    return t


LETRAS = {
    "B": ["1110", "1001", "1110", "1001", "1001", "1110"],
    "-": ["000", "000", "111", "000", "000", "000"],
    "S": ["0111", "1000", "1000", "0110", "0001", "1110"],
    "I": ["1", "1", "1", "1", "1", "1"],
    "D": ["1110", "1001", "1001", "1001", "1001", "1110"],
    "E": ["1111", "1000", "1110", "1000", "1000", "1111"],
}

# Fonte miúda 3x5 para a linha de baixo da placa.
LETRAS_MIUDAS = {
    "D": ["110", "101", "101", "101", "110"],
    "I": ["111", "010", "010", "010", "111"],
    "S": ["011", "100", "010", "001", "110"],
    "C": ["011", "100", "100", "100", "011"],
    "O": ["010", "101", "101", "101", "010"],
    "E": ["111", "100", "110", "100", "111"],
    "A": ["010", "101", "111", "101", "101"],
    "F": ["111", "100", "110", "100", "100"],
    " ": ["0", "0", "0", "0", "0"],
}


def letreiro_letras():
    """Letras e disco brancos da placa, desenhados com brilho próprio."""
    w, h = 112, 36
    t = Tela(w, h)
    branco = cor("f4efe6")
    escala = 3
    x = 10
    for letra in "B-SIDE":
        mapa = LETRAS[letra]
        for ly, linha in enumerate(mapa):
            for lx, v in enumerate(linha):
                if v == "1":
                    t.ret(x + lx * escala, 7 + ly * escala, x + lx * escala + escala - 1, 7 + ly * escala + escala - 1, branco)
        x += (len(mapa[0]) + 1) * escala
    # disco branco com selo vermelho (o vermelho vem da placa por baixo)
    cx, cy = 92, 15.5
    t.elipse(cx, cy, 9, 9, branco)
    for yy in range(h):
        for xx in range(w):
            d = math.hypot(xx + 0.5 - cx, yy + 0.5 - cy)
            if d < 3.2 or 5.0 < d < 5.8:
                t.p[xx, yy] = (0, 0, 0, 0)
    t.px(int(cx), int(cy), branco)
    # linha de baixo: DISCOS E CAFE
    x = 22
    for letra in "DISCOS E CAFE":
        mapa = LETRAS_MIUDAS[letra]
        for ly, linha in enumerate(mapa):
            for lx, v in enumerate(linha):
                if v == "1":
                    t.px(x + lx, 26 + ly, cor("e8dfcc"))
        x += len(mapa[0]) + 1
    return t


def quadro_disco(fundo, selo, semente):
    """Capa de disco emoldurada em latão, com passe-partout creme."""
    w, h = 18, 22
    t = Tela(w, h)
    rng = random.Random(semente)
    t.ret(0, 0, w - 1, h - 1, cor("a8823e"))
    t.hlin(1, w - 2, 1, cor("d0aa60"))
    t.ret(2, 2, w - 3, h - 3, cor("e8dfcc"))
    t.ret(4, 4, w - 5, h - 7, fundo)
    t.elipse(w / 2, 9.5, 4.5, 4.5, cor("141214"))
    t.elipse(w / 2, 9.5, 1.5, 1.5, selo)
    t.hlin(5, w - 6, h - 5, cor("8a8070"))
    t.hlin(6, w - 7 - rng.randrange(0, 3), h - 4, cor("b0a690"))
    t.contornar()
    return t


def poster(c1, c2, semente):
    w, h = 18, 24
    t = Tela(w, h)
    rng = random.Random(semente)
    for y in range(h):
        t.hlin(0, w - 1, y, mistura(c1, c2, y / h))
    t.elipse(9, 9, 5, 5, cor("101018"))
    t.elipse(9, 9, 1.5, 1.5, c1)
    for x in range(1, w - 1, 3):
        t.vlin(x, 17 - rng.randrange(0, 4), 19, cor("101018"))
    t.hlin(3, 14, 21, cor("e8e0d0"))
    t.contornar()
    return t


def estante_discos():
    w, h = 80, 46
    t = Tela(w, h)
    rng = random.Random(33)
    c = cor("4a3022")
    caixa(t, 0, 0, w, h, 5, mult(c, 1.25), c)
    for k in range(3):
        y0 = 7 + k * 13
        t.ret(3, y0, w - 4, y0 + 10, cor("1a100c"))
        t.hlin(2, w - 3, y0 + 11, mult(c, 1.35))
        x = 4
        while x < w - 5:
            if rng.random() < 0.12 and x < w - 16:
                capa = rng.choice(CAPAS_SOBRIAS)
                t.ret(x, y0 + 1, x + 9, y0 + 10, capa)
                t.elipse(x + 5, y0 + 5.5, 3, 3, cor("141418"))
                t.px(x + 5, y0 + 5, capa)
                x += 11
                continue
            tom = mult(rng.choice(CAPAS_SOBRIAS), rng.uniform(0.75, 0.95))
            t.vlin(x, y0 + 2, y0 + 10, tom)
            x += 1 if rng.random() < 0.7 else 2
    t.contornar()
    return t


def caixote():
    """Ilha de caixotes de vinil: capas em pé, viradas para quem passa."""
    w, h = 44, 30
    t = Tela(w, h)
    rng = random.Random(55)
    madeira = cor("6a4a30")
    caixa(t, 0, 14, w, 16, 3, mult(madeira, 1.25), madeira)
    t.vlin(w // 2, 17, h - 2, mult(madeira, 0.6))
    for x in (3, w // 2 + 3):
        t.ret(x, 20, x + 14, 25, cor("d8cdb0"))
        t.hlin(x + 2, x + 10, 22, cor("6a5a40"))
    # duas fileiras de capas; a de trás mais escura
    for fileira, (y_topo, escurecer) in enumerate(((1, 0.7), (5, 1.0))):
        x = 2 + fileira * 2
        while x < w - 8:
            capa = mult(rng.choice(CAPAS_SOBRIAS), escurecer)
            topo_y = y_topo + rng.randrange(0, 3)
            t.ret(x, topo_y, x + 7, 15, capa)
            t.hlin(x, x + 7, topo_y, mult(capa, 1.3))
            t.vlin(x + 7, topo_y, 15, mult(capa, 0.55))
            if fileira == 1 and rng.random() < 0.5:
                t.hlin(x + 1, x + 5, topo_y + 3, mult(capa, 0.7))
            x += rng.randrange(5, 8)
    t.contornar()
    return t


def balcao():
    w, h = 80, 40
    t = Tela(w, h)
    c = cor("5a3a26")
    caixa(t, 0, 12, w, 28, 10, cor("7a5236"), c)
    for x in range(4, w - 4, 10):
        t.vlin(x, 23, h - 3, mult(c, 0.75))
    t.ret(6, 26, 18, 34, cor("a8823e"))
    t.ret(7, 27, 17, 33, cor("7a1418"))
    t.elipse(12, 30, 2.5, 2.5, cor("f4efe6"))
    t.px(12, 30, cor("7a1418"))
    # caixa registradora
    t.ret(52, 2, 70, 15, cor("2e2e36"))
    t.ret(54, 4, 68, 8, cor("6a8a60"))
    t.ret(54, 10, 68, 14, cor("4a4a54"))
    for x in range(55, 68, 3):
        t.px(x, 11, cor("a8a8b0"))
        t.px(x, 13, cor("a8a8b0"))
    # registro de estoque aberto
    t.ret(22, 12, 42, 19, cor("e8dcc0"))
    t.vlin(32, 12, 19, cor("8a7a60"))
    for y in (14, 16):
        t.hlin(24, 30, y, cor("6a6050"))
        t.hlin(34, 40, y, cor("6a6050"))
    t.ret(21, 19, 43, 20, cor("6a2a2a"))
    # luminária pequena
    t.vlin(10, 4, 14, cor("2a2a30"))
    t.ret(6, 2, 14, 5, cor("3a6a5a"))
    t.contornar()
    return t


def banquinho():
    t = Tela(12, 16)
    t.elipse(6, 3, 5.5, 2.5, cor("6a2a2a"))
    t.vlin(3, 5, 15, METAL)
    t.vlin(8, 5, 15, METAL)
    t.hlin(3, 8, 11, METAL)
    t.contornar()
    return t


def capacho():
    w, h = 14, 44
    t = Tela(w, h)
    rng = random.Random(4)
    t.ret(0, 0, w - 1, h - 1, cor("3a3226"))
    t.moldura(1, 1, w - 2, h - 2, cor("6a5a40"))
    t.ruido(0, 0, w - 1, h - 1, rng, 0.15)
    return t


def lousa():
    w, h = 32, 24
    t = Tela(w, h)
    t.ret(0, 0, w - 1, h - 1, cor("5a3a24"))
    t.ret(2, 2, w - 3, h - 3, cor("1e2a24"))
    giz = cor("d8d8cc")
    t.hlin(5, 18, 5, giz)
    for y in (9, 12, 15, 18):
        t.hlin(5, 5 + (y * 7) % 14 + 6, y, mult(giz, 0.8))
        t.hlin(24, 26, y, cor("e8b060"))
    t.contornar()
    return t


def balcao_cafe():
    w, h = 64, 34
    t = Tela(w, h)
    c = cor("4a2e22")
    caixa(t, 0, 10, w, 24, 9, cor("2a2a30"), c)
    t.hlin(0, w - 1, 10, cor("5a5a66"))
    for x in range(6, w - 4, 12):
        t.ret(x, 22, x + 7, h - 4, mult(c, 1.25))
    # máquina de espresso
    t.ret(6, 0, 30, 14, METAL_CLARO)
    t.ret(6, 0, 30, 1, cor("b8bccc"))
    t.ret(9, 4, 27, 9, cor("2a2a30"))
    t.ret(12, 10, 14, 13, cor("1a1a20"))
    t.ret(22, 10, 24, 13, cor("1a1a20"))
    t.px(25, 6, cor("e04040"))
    # xícaras e redoma
    for x in (36, 42):
        t.ret(x, 8, x + 3, 11, cor("e8e0d4"))
    t.elipse(55, 7, 6, 5, cor("b8d0d8", 140))
    t.ret(51, 9, 59, 11, cor("a0603a"))
    t.contornar()
    return t


def vitrola():
    w, h = 44, 30
    t = Tela(w, h)
    c = cor("6a3e26")
    caixa(t, 0, 0, w, h, 14, mult(c, 1.15), c)
    t.ret(3, 2, w - 4, 12, cor("2a1a14"))
    t.elipse(17, 7, 9, 5, cor("16161c"))
    # braço
    t.vlin(34, 3, 10, METAL_CLARO)
    t.hlin(26, 34, 3, METAL_CLARO)
    t.ret(33, 9, 36, 11, cor("3a3a40"))
    # tecido do alto-falante
    t.ret(4, 17, w - 5, h - 4, cor("8a6a4a"))
    for y in range(18, h - 4, 2):
        t.hlin(4, w - 5, y, cor("6a4e36"))
    t.ret(2, h - 2, 5, h - 1, MADEIRA_ESCURA)
    t.ret(w - 6, h - 2, w - 3, h - 1, MADEIRA_ESCURA)
    t.contornar()
    return t


def disco():
    t = Tela(16, 10)
    t.elipse(8, 5, 7.5, 4.5, cor("101014"))
    t.elipse(8, 5, 5.5, 3.2, cor("1c1c24"))
    t.elipse(8, 5, 2.2, 1.4, cor("d04060"))
    t.px(8, 5, cor("101014"))
    t.hlin(3, 6, 2, cor("5a5a6a"))
    t.hlin(10, 12, 8, cor("3a3a48"))
    return t


def nota():
    t = Tela(7, 9)
    c = cor("ffd890")
    t.vlin(5, 0, 6, c)
    t.hlin(5, 6, 0, c)
    t.px(6, 1, c)
    t.elipse(3, 7, 2.5, 1.6, c)
    return t


def catalogo():
    w, h = 24, 32
    t = Tela(w, h)
    c = cor("4a3020")
    t.ret(9, 12, 14, h - 3, c)
    t.vlin(9, 12, h - 3, mult(c, 1.4))
    t.ret(4, h - 3, 19, h - 1, mult(c, 0.8))
    t.ret(1, 4, 22, 13, mult(c, 1.1))
    t.ret(2, 3, 21, 11, cor("e0d4b8"))
    t.vlin(11, 3, 11, cor("8a7a60"))
    for y in (5, 7, 9):
        t.hlin(3, 9, y, cor("6a6050"))
        t.hlin(13, 19, y, cor("6a6050"))
    t.ret(13, 5, 16, 8, cor("8a2a2a"))
    t.ret(2, 0, 21, 2, cor("2c4438"))
    t.contornar()
    return t


def caixa_som():
    w, h = 14, 26
    t = Tela(w, h)
    caixa(t, 0, 0, w, h, 4, cor("2e2a2a"), cor("1e1a1a"))
    t.elipse(7, 10, 4, 4, cor("3a3638"))
    t.elipse(7, 10, 1.5, 1.5, cor("141214"))
    t.elipse(7, 19, 3, 3, cor("3a3638"))
    t.contornar()
    return t


def mesa_redonda():
    """Mesa de bistrô: tampo de mármore claro e pé de ferro com base de latão."""
    w, h = 26, 24
    t = Tela(w, h)
    t.elipse(13, 6, 12.5, 6, cor("8a8478"))
    t.elipse(13, 5, 11.5, 4.5, cor("d8d2c4"))
    t.hlin(7, 12, 4, cor("b8b0a0"))
    t.hlin(12, 16, 5, cor("b8b0a0"))
    t.ret(12, 11, 13, h - 3, cor("1e1c20"))
    t.ret(7, h - 3, 18, h - 1, cor("a8823e"))
    t.hlin(7, 18, h - 3, cor("d0aa60"))
    t.ret(15, 2, 18, 5, cor("f0ebe0"))
    t.px(16, 2, cor("5a3420"))
    t.contornar()
    return t


def prateleira_metal(w=48, h=52, marcada=False, semente=8):
    t = Tela(w, h)
    rng = random.Random(semente)
    for x in (0, w - 3):
        t.ret(x, 0, x + 2, h - 1, METAL)
        t.vlin(x, 0, h - 1, METAL_CLARO)
    niveis = 4 if h > 40 else 3
    passo = (h - 4) // niveis
    for k in range(niveis):
        y = 3 + k * passo + passo - 2
        t.ret(0, y, w - 1, y + 2, METAL)
        t.hlin(0, w - 1, y, METAL_CLARO)
        x = 4
        while x < w - 8:
            bw = rng.randrange(8, 15)
            bh = rng.randrange(6, passo - 2)
            if x + bw > w - 4:
                break
            papelao = mult(cor("9a7a52"), rng.uniform(0.8, 1.1))
            t.ret(x, y - bh, x + bw - 1, y - 1, papelao)
            t.hlin(x, x + bw - 1, y - bh, mult(papelao, 1.2))
            t.vlin(x + bw // 2, y - bh, y - bh + 2, cor("c8b890"))
            x += bw + rng.randrange(1, 4)
    if marcada:
        # caixa do disco: fita vermelha em X e etiqueta
        x, y = 30, 3 + passo - 2
        t.ret(x, y - 11, x + 15, y - 1, cor("a8845a"))
        t.hlin(x, x + 15, y - 11, cor("c8a070"))
        for k in range(11):
            t.px(x + int(k * 1.4), y - 11 + k, cor("c02a2a"))
            t.px(x + 15 - int(k * 1.4), y - 11 + k, cor("c02a2a"))
        t.ret(x + 5, y - 7, x + 10, y - 4, cor("e8e0c8"))
    t.contornar()
    return t


def caixas_pilha():
    w, h = 30, 34
    t = Tela(w, h)
    for (x, y, bw, bh, f) in ((0, 14, 18, 20, 1.0), (16, 18, 14, 16, 0.9), (3, 0, 15, 15, 1.08)):
        c = mult(cor("9a7a52"), f)
        caixa(t, x, y, bw, bh, 5, mult(c, 1.15), mult(c, 0.85))
        t.vlin(x + bw // 2, y, y + 4, cor("c8b890"))
    t.contornar()
    return t


def caixa_pequena():
    t = Tela(16, 16)
    c = cor("8a6c48")
    caixa(t, 0, 0, 16, 16, 5, mult(c, 1.15), mult(c, 0.85))
    t.hlin(2, 13, 2, cor("c8b890"))
    t.contornar()
    return t


def lampada():
    w, h = 8, 20
    t = Tela(w, h)
    t.vlin(3, 0, 12, cor("1a1820"))
    t.vlin(4, 0, 12, cor("1a1820"))
    t.ret(2, 12, 5, 13, cor("3a3a40"))
    t.contornar()
    t.elipse(4, 16.5, 2.5, 3, cor("fff0c0"))
    return t


def brilho_lampada():
    t = Tela(8, 8)
    t.elipse(4, 4, 3, 3.5, cor("fff6d8"))
    return t


def sombra_pes():
    t = Tela(16, 6)
    for y in range(6):
        for x in range(16):
            d = ((x + 0.5 - 8) / 8) ** 2 + ((y + 0.5 - 3) / 3) ** 2
            if d < 1:
                t.px(x, y, cor("05040a", int(130 * (1 - d))))
    return t


# ----------------------------------------------------------- montagem

def montar():
    tiles = []   # (nome, [Tela])
    sprites = []  # (nome, Tela)

    def grupo(nome, pecas):
        tiles.append((nome, pecas))

    grupo("PISO_CORREDOR", [piso_tabuas(cor("5a3d2e"), 1, v) for v in range(4)])
    grupo("PISO_COZINHA", [piso_xadrez(v) for v in range(4)])
    grupo("PISO_HOSPEDES", [piso_tabuas(cor("67503f"), 2, v) for v in range(4)])
    grupo("PISO_SALA", [piso_tabuas(cor("432c29"), 3, v) for v in range(4)])
    grupo("PISO_LOJA", [piso_parquete(v) for v in range(4)])
    grupo("PISO_CAFE", [piso_tabuas(cor("5a3824"), 4, v) for v in range(4)])
    grupo("PISO_DEPOSITO", [piso_concreto(v) for v in range(4)])
    grupo("DEGRAU", [degrau(1.0, v) for v in range(4)])
    grupo("VAO", [vao_escada(v) for v in range(4)])
    grupo("TOPO", [topo(m) for m in range(16)])
    grupo("FACE_CORREDOR", face(padrao_corredor, semente=1))
    grupo("FACE_JANELA", face(padrao_janela, semente=2))
    grupo("FACE_HOSPEDES", face(padrao_hospedes, semente=3))
    grupo("FACE_SALA", face(padrao_sala, rodape=cor("1e1416"), semente=4))
    grupo("FACE_LOJA", face(padrao_loja, rodape=cor("1e1410"), moldura=cor("6a4630"), semente=5))
    grupo("FACE_CAFE", face(padrao_cafe, rodape=cor("2a1a14"), moldura=cor("4a3020"), semente=6))
    grupo("FACE_DEPOSITO", face(padrao_deposito, rodape=cor("26262c"), moldura=cor("6a6a72"), semente=7))
    grupo("FACE_ESCADA", faces_escada())
    grupo("JANELA_LATERAL", [coluna_janela(p) for p in range(3)])
    grupo("PORTA_VIDRO", [coluna_janela(p, porta=True) for p in range(3)])
    grupo("GUARDA_CIMA", [coluna_guarda(p, piso_tabuas(cor("5a3d2e"), 1, p)) for p in range(3)])
    grupo("GUARDA_TERREO", [coluna_guarda(p, piso_parquete(p)) for p in range(3)])
    grupo("SOMBRA_NORTE", [sombra_norte()])
    grupo("SOMBRA_OESTE", [sombra_oeste()])

    def s(nome, tela):
        sprites.append((nome, tela))

    s("JANELA_COZINHA", janela_cozinha())
    s("JANELA_COZINHA_LUZ", janela_cozinha(brilho=True))
    s("BANCADA", bancada())
    s("GELADEIRA", geladeira())
    s("MESA_COZINHA", mesa_cozinha())
    s("TAPETE_COZINHA", tapete_cozinha())
    s("LIXEIRA", lixeira())
    s("CADEIRA_E", cadeira("e"))
    s("CADEIRA_D", cadeira("d"))
    s("CADEIRA_COSTAS", cadeira_costas())
    s("PENDENTE", pendente(cor("3a5a4a")))
    s("PENDENTE_COBRE", pendente(cor("a0603a")))
    s("CAMA_HOSPEDES", cama_hospedes())
    s("ESCRIVANINHA", escrivaninha())
    s("TV", tv())
    s("TELA_TV", tela_tv())
    s("RACK", rack())
    s("SOFA", sofa_costas())
    s("TAPETE", tapete())
    s("ESTANTE", estante())
    s("PLANTA_TOPO", planta_topo())
    s("CAMA_ICARO_ESTRUTURA", cama_icaro_estrutura())
    s("CAMA_ICARO_COLCHAO", cama_icaro_colchao())
    s("LUMINARIA", luminaria())
    s("PUFE", pufe())
    s("PLANTA", planta())
    s("QUADRO_1", quadro(16, 13, cor("6a7a5a"), 1))
    s("QUADRO_2", quadro(12, 16, cor("8a5a4a"), 2))
    s("QUADRO_3", quadro(22, 14, cor("4a5a7a"), 3))
    s("ARANDELA", arandela())
    s("PASSADEIRA", passadeira())
    s("BATENTE", batente())
    s("LETREIRO_FUNDO", letreiro_fundo())
    s("LETREIRO_LETRAS", letreiro_letras())
    s("QUADRO_DISCO_1", quadro_disco(cor("2c4438"), cor("a83a30"), 1))
    s("QUADRO_DISCO_2", quadro_disco(cor("8a2a2a"), cor("e8dfcc"), 2))
    s("POSTER_1", poster(cor("c84a6a"), cor("2a1a4a"), 1))
    s("POSTER_2", poster(cor("4ac8c0"), cor("1a2a4a"), 2))
    s("POSTER_3", poster(cor("e0a040"), cor("4a1a2a"), 3))
    s("ESTANTE_DISCOS", estante_discos())
    s("CAIXOTE", caixote())
    s("BALCAO", balcao())
    s("BANQUINHO", banquinho())
    s("CAPACHO", capacho())
    s("LOUSA", lousa())
    s("BALCAO_CAFE", balcao_cafe())
    s("VITROLA", vitrola())
    s("DISCO", disco())
    s("NOTA", nota())
    s("CATALOGO", catalogo())
    s("CAIXA_SOM", caixa_som())
    s("MESA_REDONDA", mesa_redonda())
    s("PRATELEIRA", prateleira_metal())
    s("PRATELEIRA_MARCADA", prateleira_metal(80, 44, marcada=True, semente=12))
    s("CAIXAS_PILHA", caixas_pilha())
    s("CAIXA_PEQUENA", caixa_pequena())
    s("LAMPADA", lampada())
    s("BRILHO_LAMPADA", brilho_lampada())
    s("SOMBRA_PES", sombra_pes())
    return tiles, sprites


def empacotar(tiles, sprites):
    por_linha = LARGURA_ATLAS // T
    indices = {}
    n = 0
    for nome, pecas in tiles:
        indices[nome] = n
        n += len(pecas)
    y_sprites = ((n + por_linha - 1) // por_linha) * T + 2
    # prateleiras: sprites mais altos primeiro, 1 px de folga entre eles
    ordem = sorted(sprites, key=lambda s: -s[1].h)
    posicoes = {}
    x, y, altura_linha = 0, y_sprites, 0
    for nome, tela in ordem:
        if x + tela.w > LARGURA_ATLAS:
            x, y = 0, y + altura_linha + 2
            altura_linha = 0
        posicoes[nome] = (x, y, tela.w, tela.h)
        x += tela.w + 2
        altura_linha = max(altura_linha, tela.h)
    altura = 1
    while altura < y + altura_linha:
        altura *= 2
    atlas = Image.new("RGBA", (LARGURA_ATLAS, altura), (0, 0, 0, 0))
    k = 0
    for nome, pecas in tiles:
        for peca in pecas:
            atlas.paste(peca.im, ((k % por_linha) * T, (k // por_linha) * T))
            k += 1
    for nome, tela in sprites:
        px, py, _, _ = posicoes[nome]
        atlas.paste(tela.im, (px, py))
    return atlas, indices, posicoes


def gerar_luz():
    n = 128
    im = Image.new("RGBA", (n, n))
    p = im.load()
    for y in range(n):
        for x in range(n):
            d = math.hypot(x + 0.5 - n / 2, y + 0.5 - n / 2) / (n / 2)
            a = max(0.0, 1 - d) ** 1.8
            p[x, y] = (255, 255, 255, int(a * 255))
    return im


def gerar_vinheta():
    w, h = 320, 180
    im = Image.new("RGBA", (w, h))
    p = im.load()
    for y in range(h):
        for x in range(w):
            dx = (x + 0.5 - w / 2) / (w / 2)
            dy = (y + 0.5 - h / 2) / (h / 2)
            r = math.sqrt(dx * dx * 0.8 + dy * dy)
            t = min(1.0, max(0.0, (r - 0.55) / 0.6))
            v = int(255 * (1 - 0.6 * t * t * (3 - 2 * t)))
            p[x, y] = (v, v, min(255, v + 6), 255)
    return im


def main():
    tiles, sprites = montar()
    atlas, indices, posicoes = empacotar(tiles, sprites)
    assets = RAIZ / "assets"
    atlas.save(assets / "tileset-bside.png")
    gerar_luz().save(assets / "luz.png")
    gerar_vinheta().save(assets / "vinheta.png")
    linhas = [
        "# Gerado por ferramentas/gerar_tileset.py. Não editar à mão.",
        f"# Atlas {LARGURA_ATLAS}x{atlas.height}; tiles de {T} px, {LARGURA_ATLAS // T} por linha.",
        "",
    ]
    for nome, _ in tiles:
        linhas.append(f".equ T_{nome}, {indices[nome]}")
    linhas.append("")
    for nome, _ in sprites:
        x, y, w, h = posicoes[nome]
        linhas.append(f".equ S_{nome}_X, {x}")
        linhas.append(f".equ S_{nome}_Y, {y}")
        linhas.append(f".equ S_{nome}_L, {w}")
        linhas.append(f".equ S_{nome}_A, {h}")
    (RAIZ / "tileset.inc").write_text("\n".join(linhas) + "\n", encoding="utf-8")
    print(f"tileset-bside.png {LARGURA_ATLAS}x{atlas.height}, {sum(len(p) for _, p in tiles)} tiles, {len(sprites)} sprites")


if __name__ == "__main__":
    main()
