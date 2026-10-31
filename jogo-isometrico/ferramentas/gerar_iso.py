#!/usr/bin/env python3
"""Gera a pixel art isométrica da Fase 1 (interior da B-Side).

Reaproveita as texturas planas de gerar_tileset.py (pisos, papéis de parede,
janela da cozinha) e as projeta em losangos 32x16 e blocos isométricos.

Saídas:
  assets/tileset-iso.png  losangos, faces de parede, móveis e decalques
  tileset.inc             .equ com posição, tamanho e âncora de cada peça

Uso: python3 ferramentas/gerar_iso.py   (ou `make arte`)
"""
import math
import random
import sys
from pathlib import Path

from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))
import gerar_tileset as base  # noqa: E402
from gerar_tileset import CAPAS_SOBRIAS, CONTORNO, Tela, alfa, cor, mistura, mult  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
ALTURA_PAREDE = 48
LARGURA_ATLAS = 1024


# ------------------------------------------------------------- projeção

class Caixa:
    """Bloco alinhado à grade em coordenadas do objeto (px do mundo).

    topo/sul/leste: cor, função que pinta uma Tela plana, ou None (face omitida).
    A Tela do topo mede w x d; a do sul, w x h; a do leste, d x h, com a
    coluna 0 no lado sul (é o lado esquerdo de quem olha a face leste).
    """

    def __init__(self, ox, oy, oz, w, d, h, topo=None, sul=None, leste=None):
        self.ox, self.oy, self.oz, self.w, self.d, self.h = ox, oy, oz, w, d, h
        self.topo = self._plana(topo, w, d)
        self.sul = self._plana(sul, w, h)
        self.leste = self._plana(leste, d, h)

    @staticmethod
    def _plana(spec, lw, lh):
        if spec is None or lw <= 0 or lh <= 0:
            return None
        t = Tela(lw, lh)
        if callable(spec):
            spec(t)
        else:
            t.ret(0, 0, lw - 1, lh - 1, spec)
        return t


def renderizar(caixas, X0, Y0, X1, Y1, H, contorno=True, f_sul=0.84, f_leste=0.64):
    """Projeta as caixas recortadas ao retângulo [X0,X1)x[Y0,Y1) do chão.

    Projeção: px = DY + (X-X0) - (Y-Y0); py = ((X-X0)+(Y-Y0))/2 + H - Z.
    Âncora devolvida = vértice inferior do recorte no chão.
    """
    WX, DY = X1 - X0, Y1 - Y0
    largura = WX + DY
    altura = (WX + DY) // 2 + H
    t = Tela(largura, altura)
    for c in caixas:
        x0, x1 = max(c.ox, X0), min(c.ox + c.w, X1)
        y0, y1 = max(c.oy, Y0), min(c.oy + c.d, Y1)
        if x0 >= x1 or y0 >= y1:
            continue
        for py in range(altura):
            for px in range(largura):
                cx, cy = px + 0.5, py + 0.5
                a = cx - DY
                pixel = None
                if c.topo is not None:
                    s2 = 2 * (cy - H + c.oz + c.h)
                    X = (a + s2) / 2 + X0
                    Y = (s2 - a) / 2 + Y0
                    if x0 <= X < x1 and y0 <= Y < y1:
                        pixel = c.topo.p[int(X - c.ox), int(Y - c.oy)]
                if pixel is None and c.sul is not None and c.oy + c.d <= Y1:
                    Y = c.oy + c.d
                    Xl = a + (Y - Y0)
                    X = Xl + X0
                    Z = (Xl + (Y - Y0)) / 2 + H - cy
                    if x0 <= X < x1 and c.oz <= Z < c.oz + c.h:
                        v = min(c.h - 1, int(c.oz + c.h - Z))
                        bruto = c.sul.p[int(X - c.ox), v]
                        if bruto[3]:
                            pixel = mult(bruto, f_sul)
                if pixel is None and c.leste is not None and c.ox + c.w <= X1:
                    X = c.ox + c.w
                    Xl = X - X0
                    Yl = Xl - a
                    Y = Yl + Y0
                    Z = (Xl + Yl) / 2 + H - cy
                    if y0 <= Y < y1 and c.oz <= Z < c.oz + c.h:
                        u = min(c.d - 1, int(c.oy + c.d - Y))
                        v = min(c.h - 1, int(c.oz + c.h - Z))
                        bruto = c.leste.p[u, v]
                        if bruto[3]:
                            pixel = mult(bruto, f_leste)
                if pixel is not None and pixel[3]:
                    t.px(px, py, pixel)
    if contorno:
        t.contornar()
    return t, (WX, (WX + DY) // 2 + H)


def losango(textura16):
    t, _ = renderizar([Caixa(0, 0, 0, 16, 16, 0, topo=lambda p: p.colar(textura16, 0, 0))],
                      0, 0, 16, 16, 0, contorno=False)
    return t


def face_parede(plana, lado, altura=ALTURA_PAREDE):
    """Face sul ou leste de um bloco 16x16 de altura dada, num quadro 32x(16+altura)."""
    pintar = (lambda p: p.colar(plana, 0, 0))
    if lado == "sul":
        caixa = Caixa(0, 0, 0, 16, 16, altura, sul=pintar)
    else:
        caixa = Caixa(0, 0, 0, 16, 16, altura, leste=pintar)
    t, _ = renderizar([caixa], 0, 0, 16, 16, altura, contorno=False, f_sul=0.9, f_leste=0.7)
    return t


def cisalhar(plana, lado):
    """Decalque de parede: imagem plana inclinada para a face sul ou leste.

    Sul: a coluna i desce i//2. Leste: a coluna j desce (L - j)//2.
    """
    L, A = plana.w, plana.h
    t = Tela(L, A + L // 2)
    for x in range(L):
        desloc = x // 2 if lado == "sul" else (L - x) // 2
        for y in range(A):
            c = plana.p[x, y]
            if c[3]:
                t.p[x, y + desloc] = mult(c, 0.92 if lado == "sul" else 0.75)
    return t


def segmentar(nome, caixas, WX, DY, H, eixo="x", contorno=True):
    """Corta móveis compridos em pedaços de 16 px para a ordenação de profundidade."""
    pedacos = []
    comprimento = WX if eixo == "x" else DY
    inicio = 0
    k = 0
    while inicio < comprimento:
        fim = min(comprimento, inicio + 16)
        if eixo == "x":
            tela, ancora = renderizar(caixas, inicio, 0, fim, DY, H, contorno)
            pedacos.append((f"{nome}_{k}", tela, ancora, inicio, 0, fim - inicio, DY))
        else:
            tela, ancora = renderizar(caixas, 0, inicio, WX, fim, H, contorno)
            pedacos.append((f"{nome}_{k}", tela, ancora, 0, inicio, WX, fim - inicio))
        inicio = fim
        k += 1
    return pedacos


def inteiro(nome, caixas, WX, DY, H, contorno=True):
    tela, ancora = renderizar(caixas, 0, 0, WX, DY, H, contorno)
    return [(nome, tela, ancora, 0, 0, WX, DY)]


# ------------------------------------------------------- texturas planas

def empilhar_face(pecas):
    """As seis peças de base.face() viram uma parede plana 16x48 (topo, meio, rodapé)."""
    t = Tela(16, 48)
    t.colar(pecas[0], 0, 0)
    t.colar(pecas[2], 0, 16)
    t.colar(pecas[4], 0, 32)
    return t


def padrao_azulejo(t, pos, par, rng):
    t.ret(0, 0, 15, 15, cor("a8b4ac"))
    for k in (0, 8):
        t.hlin(0, 15, k, cor("6e7a74"))
        t.vlin(k, 0, 15, cor("6e7a74"))
    for (x, y) in ((3, 3), (11, 11)):
        t.px(x, y, cor("4a6a6a"))
    t.ruido(0, 0, 15, 15, rng, 0.05)
    if pos == 2:
        t.ret(0, 6, 15, 11, cor("5a6a66"))


def plana_janela_cozinha(k, brilho):
    jan = base.janela_cozinha(brilho=brilho)
    t = Tela(16, 48)
    t.im.paste(jan.im.crop((16 * k, 0, 16 * k + 16, 48)), (0, 0))
    t.p = t.im.load()
    return t


def plana_janela(brilho):
    t = Tela(16, 48)
    if brilho:
        t.ret(4, 10, 11, 34, cor("8ea6d8", 70))
        t.px(6, 14, cor("e8c070"))
        t.px(9, 22, cor("f0d890"))
        return t
    t.ret(0, 0, 15, 47, cor("2a2a36"))
    t.ret(2, 6, 13, 38, cor("5a4636"))
    for y in range(8, 37):
        t.hlin(3, 12, y, mistura(cor("0e1430"), cor("26305a"), (y - 8) / 29))
    t.hlin(3, 12, 22, cor("5a4636"))
    t.vlin(7, 8, 36, cor("5a4636"))
    t.vlin(4, 9, 21, cor("4a5a8a"))
    t.ret(1, 38, 14, 40, cor("7a5a42"))
    t.ret(0, 44, 15, 47, cor("1e1614"))
    return t


def plana_porta(brilho):
    t = Tela(16, 48)
    if brilho:
        t.ret(4, 8, 11, 40, cor("e8a860", 60))
        return t
    t.ret(0, 0, 15, 47, cor("2a2a36"))
    t.ret(1, 2, 14, 47, cor("4a3020"))
    t.ret(3, 5, 12, 42, cor("3a2c24"))
    for y in range(6, 41):
        t.hlin(4, 11, y, mistura(cor("6a4a30"), cor("3a2a22"), (y - 6) / 35))
    t.ret(10, 24, 11, 27, cor("c9a24a"))
    return t


def plana_guarda(t):
    """Guarda-corpo baixo: corrimão e balaústres alinhados à base (o motor corta de baixo)."""
    t.ret(0, 34, t.w - 1, 36, cor("6a4430"))
    t.hlin(0, t.w - 1, 34, cor("8a5a40"))
    for x in range(1, t.w, 4):
        t.vlin(x, 37, t.h - 1, cor("4a3020"))


def plana_madeira(cor_base):
    def pintar(t):
        t.ret(0, 0, t.w - 1, t.h - 1, cor_base)
        rng = random.Random(t.w * 7 + t.h)
        for x in range(0, t.w, 4):
            t.vlin(x, 0, t.h - 1, mult(cor_base, 0.8))
        t.ruido(0, 0, t.w - 1, t.h - 1, rng, 0.06)
        t.hlin(0, t.w - 1, 0, mult(cor_base, 1.25))
    return pintar


def degrau_plano(t):
    t.ret(0, 0, t.w - 1, t.h - 1, cor("5a3a28"))
    for y in range(0, t.h, 3):
        t.hlin(0, t.w - 1, y, cor("3a2418"))
    t.hlin(0, t.w - 1, 0, cor("8a5d3e"))


def topo_parede():
    t = losango(base.topo(0))
    # contorno escuro em cima e borda clara nas arestas da frente
    for x in range(32):
        col = [y for y in range(16) if t.p[x, y][3]]
        if not col:
            continue
        t.p[x, col[0]] = CONTORNO
        t.p[x, col[-1]] = cor("4a4060")
        if len(col) > 2:
            t.p[x, col[-2]] = cor("2c2638")
    return t


def topo_madeira():
    tex = Tela(16, 16)
    tex.ret(0, 0, 15, 15, cor("6a4430"))
    for y in range(0, 16, 4):
        tex.hlin(0, 15, y, cor("8a5a40"))
    return losango(tex)


def sombra_losango(lado):
    """Escurece a aresta de cima do losango encostada numa parede (norte ou oeste)."""
    t = Tela(32, 16)
    for y in range(16):
        for x in range(32):
            lx = y + (x + 0.5 - 16) / 2
            ly = y - (x + 0.5 - 16) / 2
            if not (0 <= lx < 16 and 0 <= ly < 16):
                continue
            dist = ly if lado == "norte" else lx
            if dist < 7:
                t.p[x, y] = cor("05040a", int(150 * (1 - dist / 7) ** 1.6))
    return t


# --------------------------------------------------------------- móveis

def pinta(fn):
    return fn


def armario(t):
    t.ret(0, 0, t.w - 1, t.h - 1, cor("5a3a2a"))
    t.moldura(2, 2, t.w - 3, t.h - 2, cor("3e281c"))
    t.ret(t.w // 2 - 2, 5, t.w // 2 + 1, 5, base.METAL_CLARO)


def tampo_pedra(t):
    t.ret(0, 0, t.w - 1, t.h - 1, cor("8e8b84"))
    t.ruido(0, 0, t.w - 1, t.h - 1, random.Random(t.w), 0.05)


def bancada(variante):
    def topo(t):
        tampo_pedra(t)
        if variante == "pia":
            t.ret(3, 2, 12, 9, cor("5d636e"))
            t.ret(4, 3, 11, 8, cor("2c3038"))
            t.ret(7, 0, 8, 2, base.METAL_CLARO)
        elif variante == "fogao":
            t.ret(1, 1, 14, 12, cor("26252b"))
            for (cx, cy) in ((4, 4), (11, 4), (4, 9), (11, 9)):
                t.elipse(cx, cy, 2.2, 2.2, cor("4b4a52"))
                t.px(cx, cy, cor("26252b"))
        else:
            t.ret(3, 3, 11, 9, cor("a77b52"))

    def frente(t):
        if variante == "fogao":
            t.ret(0, 0, t.w - 1, t.h - 1, cor("2e2d33"))
            t.ret(2, 4, t.w - 3, t.h - 3, cor("1a1a20"))
            t.hlin(2, t.w - 3, 2, base.METAL_CLARO)
        else:
            armario(t)

    return inteiro(f"BANCADA_{variante.upper()}", [
        Caixa(0, 0, 0, 16, 13, 16, sul=frente, leste=cor("4a3022")),
        Caixa(0, 0, 16, 16, 13, 2, topo=topo, sul=cor("6e6b64"), leste=cor("5e5b54")),
    ], 16, 14, 18)


def geladeira():
    def frente(t):
        t.ret(0, 0, t.w - 1, t.h - 1, cor("aab8b0"))
        t.hlin(0, t.w - 1, 16, cor("6e7d76"))
        t.vlin(3, 4, 13, cor("e0e8e4"))
        t.vlin(3, 20, 34, cor("e0e8e4"))
        t.ret(9, 6, 10, 7, cor("c8584a"))
        t.ret(11, 24, 12, 25, cor("e0c060"))
    return inteiro("GELADEIRA", [Caixa(0, 0, 0, 14, 13, 44, topo=cor("c8d4ce"), sul=frente, leste=cor("8a9a92"))],
                   14, 14, 44)


def madeira_lisa(c):
    def pintar(t):
        t.ret(0, 0, t.w - 1, t.h - 1, c)
        for y in range(0, t.h, 5):
            t.hlin(0, t.w - 1, y, mult(c, 0.88))
        t.hlin(0, t.w - 1, 0, mult(c, 1.15))
    return pintar


def pernas(w, d, h, c, grossura=2):
    g = grossura
    return [Caixa(x, y, 0, g, g, h, topo=c, sul=c, leste=mult(c, 0.8))
            for (x, y) in ((0, 0), (w - g, 0), (0, d - g), (w - g, d - g))]


def mesa_cozinha():
    c = cor("6d4a34")

    def topo(t):
        madeira_lisa(c)(t)
        t.elipse(8, 9, 3.5, 3.5, cor("d8d0c4"))
        t.elipse(8, 9, 1.8, 1.8, cor("b0a090"))
        t.ret(22, 6, 24, 9, cor("c05040"))
    caixas = pernas(32, 20, 12, mult(c, 0.7)) + [Caixa(0, 0, 12, 32, 20, 3, topo=topo, sul=mult(c, 0.8), leste=mult(c, 0.7))]
    return segmentar("MESA_COZINHA", caixas, 32, 20, 15)


def cadeira(lado, c=cor("4e3426")):
    caixas = pernas(10, 10, 7, mult(c, 0.7))
    encosto = {"norte": (0, 0, 10, 2), "sul": (0, 8, 10, 2), "oeste": (0, 0, 2, 10), "leste": (8, 0, 2, 10)}[lado]
    ex, ey, ew, ed = encosto
    assento = Caixa(0, 0, 7, 10, 10, 2, topo=mult(c, 1.2), sul=c, leste=mult(c, 0.8))
    costas = Caixa(ex, ey, 7, ew, ed, 11, topo=mult(c, 1.25), sul=mult(c, 1.05), leste=mult(c, 0.85))
    if lado in ("norte", "oeste"):
        caixas += [costas, assento]
    else:
        caixas += [assento, costas]
    return inteiro(f"CADEIRA_{lado.upper()}", caixas, 10, 10, 18)


def lixeira():
    return inteiro("LIXEIRA", [Caixa(0, 0, 0, 8, 8, 12, topo=cor("a8acb8"), sul=cor("6a6f7a"), leste=cor("5a5f6a"))], 8, 8, 12)


def planta(nome="PLANTA", semente=5):
    rng = random.Random(semente)
    caixas = [Caixa(1, 1, 0, 10, 10, 9, topo=cor("3a2418"), sul=cor("8a4a34"), leste=cor("6a3424"))]
    folhas = []
    for _ in range(9):
        w = rng.randrange(4, 7)
        x = rng.randrange(0, 12 - w + 1)
        y = rng.randrange(0, 12 - w + 1)
        z = rng.randrange(8, 20)
        verde = mult(cor("3a6a40"), rng.uniform(0.8, 1.25))
        folhas.append(Caixa(x, y, z, w, w, rng.randrange(3, 6), topo=mult(verde, 1.2), sul=verde, leste=mult(verde, 0.8)))
    folhas.sort(key=lambda c: (c.ox + c.oy, c.oz))
    return inteiro(nome, caixas + folhas, 12, 12, 26)


def cama_hospedes():
    madeira = cor("5a3a2a")

    def cobertor(t):
        t.ret(0, 0, t.w - 1, t.h - 1, cor("44506e"))
        for y in range(0, t.h, 4):
            t.hlin(0, t.w - 1, y, cor("3a4560"))
        t.hlin(0, t.w - 1, 0, cor("6a789a"))
    caixas = [
        Caixa(0, 0, 0, 22, 3, 20, topo=mult(madeira, 1.3), sul=madeira, leste=mult(madeira, 0.8)),
        Caixa(0, 3, 0, 22, 29, 7, topo=madeira, sul=mult(madeira, 0.9), leste=mult(madeira, 0.75)),
        Caixa(1, 3, 7, 20, 28, 3, topo=cor("d8d0c4"), sul=cor("c8c0b0"), leste=cor("b8b0a0")),
        Caixa(3, 4, 10, 16, 6, 3, topo=cor("ece6dc"), sul=cor("d0c8bc"), leste=cor("c0b8ac")),
        Caixa(1, 12, 10, 20, 19, 1, topo=cobertor, sul=cor("3a4560"), leste=cor("2e3850")),
    ]
    return segmentar("CAMA_HOSPEDES", caixas, 22, 32, 20, eixo="y")


def escrivaninha():
    c = cor("5e4030")

    def papeis(t):
        madeira_lisa(c)(t)
        t.ret(12, 3, 22, 9, cor("d8d0bc"))
        t.hlin(14, 20, 5, cor("8a8478"))
    caixas = pernas(32, 14, 13, mult(c, 0.7)) + [
        Caixa(20, 0, 0, 12, 14, 13, sul=lambda t: (t.ret(0, 0, t.w - 1, t.h - 1, mult(c, 0.8)), t.hlin(3, 8, 4, base.METAL_CLARO), t.hlin(3, 8, 9, base.METAL_CLARO)), leste=mult(c, 0.6)),
        Caixa(0, 0, 13, 32, 14, 3, topo=papeis, sul=mult(c, 0.85), leste=mult(c, 0.7)),
        Caixa(4, 3, 16, 2, 2, 9, topo=cor("2a2a30"), sul=cor("2a2a30"), leste=cor("1e1e24")),
        Caixa(2, 2, 25, 6, 5, 4, topo=cor("d8b060"), sul=cor("b58a3a"), leste=cor("8a6a2a")),
    ]
    return segmentar("ESCRIVANINHA", caixas, 32, 14, 29)


def rack():
    c = cor("3a2a24")

    def frente(t):
        t.ret(0, 0, t.w - 1, t.h - 1, c)
        for k in range(0, t.w - 2, 13):
            t.moldura(k + 1, 2, k + 12, t.h - 2, mult(c, 0.6))
        t.ret(16, 3, 26, 6, cor("1a1a20"))
        t.px(25, 4, cor("40d070"))
    return segmentar("RACK", [Caixa(0, 0, 0, 40, 12, 10, topo=madeira_lisa(mult(c, 1.25)), sul=frente, leste=mult(c, 0.8))], 40, 12, 10)


def sofa():
    c = cor("5a2a36")
    caixas = [
        Caixa(0, 0, 0, 48, 18, 7, topo=c, sul=mult(c, 0.8), leste=mult(c, 0.7)),
        Caixa(4, 1, 7, 40, 11, 3, topo=lambda t: (t.ret(0, 0, t.w - 1, t.h - 1, mult(c, 1.2)), [t.vlin(x, 0, t.h - 1, mult(c, 0.9)) for x in (13, 26)]), sul=mult(c, 1.0), leste=mult(c, 0.8)),
        Caixa(0, 0, 0, 4, 18, 13, topo=mult(c, 1.15), sul=c, leste=mult(c, 0.8)),
        Caixa(44, 0, 0, 4, 18, 13, topo=mult(c, 1.15), sul=c, leste=mult(c, 0.8)),
        Caixa(4, 12, 0, 40, 6, 19, topo=mult(c, 1.25), sul=lambda t: (t.ret(0, 0, t.w - 1, t.h - 1, c), [t.vlin(x, 2, t.h - 3, mult(c, 0.82)) for x in range(4, t.w, 6)]), leste=mult(c, 0.8)),
    ]
    return segmentar("SOFA", caixas, 48, 18, 19)


def estante_livros():
    c = cor("4a3020")
    rng = random.Random(21)

    def frente(t):
        t.ret(0, 0, t.w - 1, t.h - 1, c)
        for k in range(4):
            y0 = 2 + k * 10
            t.ret(2, y0, t.w - 3, y0 + 7, cor("1c120e"))
            t.hlin(1, t.w - 2, y0 + 8, mult(c, 1.3))
            x = 3
            while x < t.w - 3:
                largura = rng.choice((1, 2, 2))
                altura = rng.randrange(4, 8)
                tom = rng.choice((cor("8a3a3a"), cor("3a5a7a"), cor("c8a050"), cor("4a6a4a"), cor("6a4a7a"), cor("b0a090")))
                t.ret(x, y0 + 7 - altura + 1, x + largura - 1, y0 + 7, mult(tom, 0.85))
                x += largura
    return segmentar("ESTANTE", [Caixa(0, 0, 0, 32, 12, 44, topo=mult(c, 1.25), sul=frente, leste=mult(c, 0.75))], 32, 12, 44)


def luminaria():
    return inteiro("LUMINARIA", [
        Caixa(1, 1, 0, 6, 6, 2, topo=cor("2a2a30"), sul=cor("2a2a30"), leste=cor("1e1e24")),
        Caixa(3, 3, 2, 2, 2, 28, topo=cor("4a4a54"), sul=cor("3a3a44"), leste=cor("2a2a30")),
        Caixa(0, 0, 28, 8, 8, 8, topo=cor("e0c490"), sul=cor("c9a46a"), leste=cor("a8844a")),
    ], 8, 8, 36)


def pufe():
    c = cor("3a5a5a")
    return inteiro("PUFE", [Caixa(0, 0, 0, 14, 14, 8, topo=mult(c, 1.25), sul=c, leste=mult(c, 0.8)),
                            Caixa(2, 2, 8, 10, 10, 2, topo=mult(c, 1.4), sul=mult(c, 1.1), leste=mult(c, 0.9))], 14, 14, 10)


def cama_icaro():
    barra = cor("3e4250")
    luz = cor("7c8296")

    def cobertor(t):
        t.ret(0, 0, t.w - 1, t.h - 1, cor("4a3666"))
        for x in range(0, t.w, 7):
            t.vlin(x, 0, t.h - 1, cor("3c2c56"))
        t.ret(0, 0, 9, t.h - 1, cor("d0c8c0"))
        t.ret(1, 2, 8, t.h - 3, cor("ece6dc"))
    postes = [Caixa(x, y, 0, 3, 3, 40, topo=luz, sul=barra, leste=mult(barra, 0.8))
              for (x, y) in ((0, 0), (45, 0), (0, 29), (45, 29))]
    escada = [Caixa(48, 6 + k * 0, 0, 2, 2, 34, topo=luz, sul=barra, leste=barra) for k in range(1)]
    escada += [Caixa(48, 22, 0, 2, 2, 34, topo=luz, sul=barra, leste=barra)]
    escada += [Caixa(48, 6, z, 2, 18, 1, topo=luz, sul=luz, leste=luz) for z in range(6, 34, 7)]
    plataforma = [
        Caixa(0, 0, 30, 48, 32, 3, topo=barra, sul=barra, leste=mult(barra, 0.8)),
        Caixa(1, 1, 33, 46, 30, 3, topo=cobertor, sul=cor("c8c0b8"), leste=cor("a8a098")),
        Caixa(0, 0, 36, 48, 2, 4, topo=luz, sul=barra, leste=barra),
        Caixa(0, 30, 36, 30, 2, 4, topo=luz, sul=barra, leste=barra),
    ]
    caixas = postes[:2] + plataforma[:1] + postes[2:] + plataforma[1:] + escada
    return segmentar("CAMA_ICARO", caixas, 50, 32, 40)


def tapete(nome, w, d, fundo, borda, semente):
    rng = random.Random(semente)

    def pintar(t):
        t.ret(0, 0, t.w - 1, t.h - 1, fundo)
        t.moldura(1, 1, t.w - 2, t.h - 2, borda)
        t.moldura(4, 4, t.w - 5, t.h - 5, mult(fundo, 0.6))
        cx, cy = t.w / 2, t.h / 2
        for y in range(7, t.h - 7):
            for x in range(7, t.w - 7):
                dd = abs(x - cx) / (t.w / 2 - 7) + abs(y - cy) / (t.h / 2 - 7)
                if 0.5 < dd < 0.58 or 0.2 < dd < 0.26:
                    t.px(x, y, borda)
        t.ruido(0, 0, t.w - 1, t.h - 1, rng, 0.08)
    tela, ancora = renderizar([Caixa(0, 0, 0, w, d, 0, topo=pintar)], 0, 0, w, d, 0, contorno=False)
    return [(nome, tela, ancora, 0, 0, w, d)]


def passadeira():
    def pintar(t):
        t.ret(0, 0, t.w - 1, t.h - 1, cor("4a2a2a"))
        t.vlin(1, 0, t.h - 1, cor("a07a4a"))
        t.vlin(t.w - 2, 0, t.h - 1, cor("a07a4a"))
        for y in range(4, t.h, 10):
            t.px(t.w // 2, y, cor("a07a4a"))
            t.px(t.w // 2 - 1, y + 1, cor("a07a4a"))
            t.px(t.w // 2 + 1, y + 1, cor("a07a4a"))
            t.px(t.w // 2, y + 2, cor("a07a4a"))
    tela, ancora = renderizar([Caixa(0, 0, 0, 16, 176, 0, topo=pintar)], 0, 0, 16, 176, 0, contorno=False)
    return [("PASSADEIRA", tela, ancora, 0, 0, 16, 176)]


def capacho():
    def pintar(t):
        t.ret(0, 0, t.w - 1, t.h - 1, cor("3a3226"))
        t.moldura(1, 1, t.w - 2, t.h - 2, cor("6a5a40"))
        t.ruido(0, 0, t.w - 1, t.h - 1, random.Random(4), 0.15)
    tela, ancora = renderizar([Caixa(0, 0, 0, 12, 28, 0, topo=pintar)], 0, 0, 12, 28, 0, contorno=False)
    return [("CAPACHO", tela, ancora, 0, 0, 12, 28)]


def estante_discos():
    c = cor("4a3022")
    rng = random.Random(33)

    def frente(t):
        t.ret(0, 0, t.w - 1, t.h - 1, c)
        for k in range(3):
            y0 = 3 + k * 12
            t.ret(2, y0, t.w - 3, y0 + 9, cor("1a100c"))
            t.hlin(1, t.w - 2, y0 + 10, mult(c, 1.35))
            x = 3
            while x < t.w - 3:
                if rng.random() < 0.15 and x < t.w - 13:
                    capa = rng.choice(CAPAS_SOBRIAS)
                    t.ret(x, y0 + 1, x + 8, y0 + 9, capa)
                    t.elipse(x + 4.5, y0 + 5, 2.5, 2.5, cor("141418"))
                    x += 10
                    continue
                t.vlin(x, y0 + 2, y0 + 9, mult(rng.choice(CAPAS_SOBRIAS), rng.uniform(0.75, 0.95)))
                x += 1 if rng.random() < 0.7 else 2
    return segmentar("ESTANTE_DISCOS", [Caixa(0, 0, 0, 32, 12, 40, topo=mult(c, 1.25), sul=frente, leste=mult(c, 0.75))], 32, 12, 40)


def caixote():
    madeira = cor("6a4a30")
    rng = random.Random(55)
    caixas = [Caixa(0, 0, 0, 32, 16, 12, topo=mult(madeira, 1.2),
                    sul=lambda t: (t.ret(0, 0, t.w - 1, t.h - 1, madeira), t.vlin(16, 0, t.h - 1, mult(madeira, 0.6)),
                                   t.ret(3, 4, 12, 8, cor("d8cdb0")), t.ret(19, 4, 28, 8, cor("d8cdb0"))),
                    leste=mult(madeira, 0.8))]
    # capas em pé, de lado, viradas para quem passa
    for fileira, y in enumerate((3, 9)):
        x = 1
        while x < 30:
            capa = mult(rng.choice(CAPAS_SOBRIAS), 0.75 if fileira == 0 else 1.0)
            h = rng.randrange(7, 10)
            caixas.append(Caixa(x, y, 12, 3, 5, h, topo=mult(capa, 1.2), sul=capa, leste=mult(capa, 0.7)))
            x += 4
    caixas[1:] = sorted(caixas[1:], key=lambda c: (c.oy, c.ox))
    return segmentar("CAIXOTE", caixas, 32, 16, 22)


def balcao():
    c = cor("5a3a26")

    def frente(t):
        t.ret(0, 0, t.w - 1, t.h - 1, c)
        for x in range(4, t.w, 8):
            t.vlin(x, 2, t.h - 2, mult(c, 0.75))
        t.ret(26, 4, 37, 12, cor("a8823e"))
        t.ret(27, 5, 36, 11, cor("7a1418"))
        t.elipse(31.5, 8, 2.5, 2.5, cor("f4efe6"))

    def tampo(t):
        t.ret(0, 0, t.w - 1, t.h - 1, cor("7a5236"))
        t.hlin(0, t.w - 1, 0, cor("9a6a46"))
        # registro de estoque aberto
        t.ret(18, 3, 30, 10, cor("e8dcc0"))
        t.vlin(24, 3, 10, cor("8a7a60"))
        for y in (5, 7):
            t.hlin(19, 22, y, cor("6a6050"))
            t.hlin(26, 29, y, cor("6a6050"))
    caixas = [
        Caixa(0, 0, 0, 64, 14, 18, topo=tampo, sul=frente, leste=mult(c, 0.8)),
        Caixa(46, 2, 18, 12, 9, 9, topo=cor("4a4a54"), sul=lambda t: (t.ret(0, 0, t.w - 1, t.h - 1, cor("2e2e36")), t.ret(2, 1, t.w - 3, 3, cor("6a8a60"))), leste=cor("22222a")),
        Caixa(4, 4, 18, 2, 2, 10, topo=cor("2a2a30"), sul=cor("2a2a30"), leste=cor("1e1e24")),
        Caixa(2, 2, 28, 6, 6, 3, topo=cor("4a7a6a"), sul=cor("3a6a5a"), leste=cor("2a4a40")),
    ]
    return segmentar("BALCAO", caixas, 64, 14, 31)


def banquinho():
    return inteiro("BANQUINHO", [Caixa(4, 4, 0, 2, 2, 10, topo=base.METAL, sul=base.METAL, leste=base.METAL),
                                 Caixa(0, 0, 10, 10, 10, 2, topo=cor("8a3a3a"), sul=cor("6a2a2a"), leste=cor("5a2020"))], 10, 10, 12)


def balcao_cafe():
    c = cor("4a2e22")

    def frente(t):
        t.ret(0, 0, t.w - 1, t.h - 1, c)
        for x in range(3, t.w - 2, 10):
            t.ret(x, 4, x + 6, t.h - 3, mult(c, 1.25))
    caixas = [
        Caixa(0, 0, 0, 48, 13, 16, topo=cor("2a2a30"), sul=frente, leste=mult(c, 0.8)),
        Caixa(0, 0, 16, 48, 13, 2, topo=cor("3a3a42"), sul=cor("5a5a66"), leste=cor("4a4a54")),
        Caixa(3, 1, 18, 14, 9, 12, topo=cor("b8bccc"), sul=lambda t: (t.ret(0, 0, t.w - 1, t.h - 1, base.METAL_CLARO), t.ret(2, 2, t.w - 3, 5, cor("2a2a30")), t.px(t.w - 3, 3, cor("e04040"))), leste=base.METAL),
        Caixa(24, 4, 18, 3, 3, 3, topo=cor("f0ebe0"), sul=cor("e8e0d4"), leste=cor("c8c0b4")),
        Caixa(30, 4, 18, 3, 3, 3, topo=cor("f0ebe0"), sul=cor("e8e0d4"), leste=cor("c8c0b4")),
        Caixa(37, 3, 18, 8, 6, 4, topo=cor("a0603a"), sul=cor("8a4a2a"), leste=cor("6a3a20")),
    ]
    return segmentar("BALCAO_CAFE", caixas, 48, 14, 30)


def vitrola():
    c = cor("6a3e26")

    def tampo(t):
        t.ret(0, 0, t.w - 1, t.h - 1, mult(c, 1.15))
        t.ret(2, 1, t.w - 3, t.h - 2, cor("2a1a14"))
        t.ret(24, 2, 25, 9, base.METAL_CLARO)

    def frente(t):
        t.ret(0, 0, t.w - 1, t.h - 1, c)
        t.ret(3, 3, t.w - 4, t.h - 3, cor("8a6a4a"))
        for y in range(4, t.h - 3, 2):
            t.hlin(3, t.w - 4, y, cor("6a4e36"))
    return segmentar("VITROLA", [Caixa(0, 0, 0, 32, 13, 16, topo=tampo, sul=frente, leste=mult(c, 0.8))], 32, 14, 16)


def catalogo():
    c = cor("4a3020")

    def pagina(t):
        t.ret(0, 0, t.w - 1, t.h - 1, cor("e0d4b8"))
        t.vlin(t.w // 2, 0, t.h - 1, cor("8a7a60"))
        t.ret(7, 2, 9, 4, cor("8a2a2a"))
    return inteiro("CATALOGO", [
        Caixa(4, 4, 0, 4, 4, 16, topo=c, sul=c, leste=mult(c, 0.8)),
        Caixa(0, 1, 16, 12, 9, 2, topo=pagina, sul=cor("2c4438"), leste=cor("1f3229")),
    ], 12, 10, 18)


def mesa_bistro():
    return inteiro("MESA_BISTRO", [
        Caixa(4, 4, 0, 4, 4, 2, topo=cor("d0aa60"), sul=cor("a8823e"), leste=cor("8a6a32")),
        Caixa(5, 5, 2, 2, 2, 10, topo=cor("1e1c20"), sul=cor("1e1c20"), leste=cor("141216")),
        Caixa(0, 0, 12, 12, 12, 2, topo=lambda t: (t.ret(0, 0, 11, 11, cor("d8d2c4")), t.hlin(2, 6, 4, cor("b8b0a0")), t.ret(7, 6, 9, 8, cor("f0ebe0"))), sul=cor("a8a294"), leste=cor("8a8478")),
    ], 12, 12, 14)


def prateleira(nome, w, h, marcada=False, semente=8):
    rng = random.Random(semente)
    caixas = []
    for (x, y) in ((0, 0), (w - 2, 0), (0, 10), (w - 2, 10)):
        caixas.append(Caixa(x, y, 0, 2, 2, h, topo=base.METAL_CLARO, sul=base.METAL, leste=mult(base.METAL, 0.8)))
    niveis = 4 if h > 40 else 3
    for k in range(niveis):
        z = 2 + k * (h - 4) // niveis
        caixas.append(Caixa(0, 0, z, w, 12, 2, topo=base.METAL, sul=base.METAL_CLARO, leste=base.METAL))
        x = 2
        while x < w - 6:
            bw = rng.randrange(6, 12)
            if x + bw > w - 2:
                break
            bh = rng.randrange(5, (h - 4) // niveis - 1)
            papelao = mult(cor("9a7a52"), rng.uniform(0.8, 1.1))
            caixas.append(Caixa(x, 2, z + 2, bw, 8, bh, topo=mult(papelao, 1.15), sul=papelao, leste=mult(papelao, 0.8)))
            x += bw + rng.randrange(1, 3)
    if marcada:
        def fita(t):
            t.ret(0, 0, t.w - 1, t.h - 1, cor("a8845a"))
            for k in range(t.h):
                t.px(int(k * (t.w - 1) / max(1, t.h - 1)), k, cor("c02a2a"))
                t.px(t.w - 1 - int(k * (t.w - 1) / max(1, t.h - 1)), k, cor("c02a2a"))
            t.ret(t.w // 2 - 2, t.h // 2 - 1, t.w // 2 + 1, t.h // 2 + 1, cor("e8e0c8"))
        caixas.append(Caixa(w // 2 - 6, 1, (h - 4) // niveis + 4, 12, 10, 9, topo=cor("c8a070"), sul=fita, leste=cor("8a6a42")))
    return segmentar(nome, caixas, w, 12, h)


def caixas_pilha():
    caixas = []
    for (x, y, z, w, d, h, f) in ((0, 0, 0, 16, 14, 12, 1.0), (16, 2, 0, 12, 12, 10, 0.9), (2, 1, 12, 13, 12, 10, 1.08)):
        c = mult(cor("9a7a52"), f)
        caixas.append(Caixa(x, y, z, w, d, h, topo=lambda t, c=c: (t.ret(0, 0, t.w - 1, t.h - 1, mult(c, 1.15)), t.vlin(t.w // 2, 0, t.h - 1, cor("c8b890"))), sul=c, leste=mult(c, 0.8)))
    return segmentar("CAIXAS_PILHA", caixas, 28, 16, 22)


def caixa_pequena():
    c = cor("8a6c48")
    return inteiro("CAIXA_PEQUENA", [Caixa(0, 0, 0, 12, 12, 10, topo=lambda t: (t.ret(0, 0, 11, 11, mult(c, 1.15)), t.hlin(1, 10, 5, cor("c8b890"))), sul=c, leste=mult(c, 0.8))], 12, 12, 10)


def sombra_pes():
    t = Tela(16, 8)
    for y in range(8):
        for x in range(16):
            d = ((x + 0.5 - 8) / 8) ** 2 + ((y + 0.5 - 4) / 4) ** 2
            if d < 1:
                t.px(x, y, cor("05040a", int(130 * (1 - d))))
    return t


# ---------------------------------------------------- decalques de parede

def tv_plana(tela_ligada):
    w, h = 44, 26
    t = Tela(w, h)
    if tela_ligada:
        rng = random.Random(77)
        for y in range(2, h - 3):
            for x in range(2, w - 2):
                t.p[x, y] = mult(cor("6fa8d8"), rng.uniform(0.75, 1.0) * (0.85 if y % 2 else 1.0))
        t.ret(6, 5, 20, 14, cor("9cc8f0"))
        t.ret(23, 9, 38, 19, cor("4a7ab0"))
        return t
    t.ret(0, 0, w - 1, h - 1, cor("0c0c10"))
    t.ret(2, 2, w - 3, h - 4, cor("141a26"))
    t.px(w // 2, h - 2, cor("e05050"))
    t.contornar()
    return t


def lousa_plana():
    t = base.lousa()
    return t


def quadro_plano(nome):
    return {"QUADRO_1": base.quadro(16, 13, cor("6a7a5a"), 1), "QUADRO_3": base.quadro(22, 14, cor("4a5a7a"), 3),
            "POSTER_1": base.poster(cor("c84a6a"), cor("2a1a4a"), 1), "POSTER_3": base.poster(cor("e0a040"), cor("4a1a2a"), 3),
            "QUADRO_DISCO_1": base.quadro_disco(cor("2c4438"), cor("a83a30"), 1),
            "QUADRO_DISCO_2": base.quadro_disco(cor("8a2a2a"), cor("e8dfcc"), 2)}[nome]


def disco_topo():
    """Vinil visto de cima, já em losango achatado."""
    t = Tela(14, 8)
    t.elipse(7, 4, 6.5, 3.6, cor("101014"))
    t.elipse(7, 4, 4.6, 2.5, cor("1c1c24"))
    t.elipse(7, 4, 1.8, 1.1, cor("c02a2a"))
    t.px(7, 4, cor("101014"))
    return t


# ------------------------------------------------- sala 2: galpão e doca

DIGITOS = {
    "1": ["010", "110", "010", "010", "111"], "2": ["110", "001", "010", "100", "111"],
    "3": ["110", "001", "010", "001", "110"], "4": ["101", "101", "111", "001", "001"],
    "5": ["111", "100", "110", "001", "110"], "6": ["011", "100", "110", "101", "010"],
    "7": ["111", "001", "010", "010", "010"], "8": ["010", "101", "010", "101", "010"],
}


def escrever(t, texto, x, y, c, escala=1):
    for ch in texto:
        for j, linha in enumerate(DIGITOS[ch]):
            for i, b in enumerate(linha):
                if b == "1":
                    t.ret(x + i * escala, y + j * escala, x + i * escala + escala - 1, y + j * escala + escala - 1, c)
        x += 4 * escala


def piso_galpao(var):
    """Concreto industrial com manchas de óleo e faixa amarela gasta."""
    t = base.piso_concreto(var)
    rng = random.Random(1200 + var)
    for y in range(16):
        for x in range(16):
            c = t.p[x, y]
            t.p[x, y] = mult(mistura(c, cor("3c3a3e"), 0.35), 0.92)
    if var == 2:
        t.elipse(7, 9, 5, 3, cor("141218", 120))
        t.elipse(9, 8, 2, 1, cor("2a3040", 120))
    if var == 3:
        for x in range(16):
            if rng.random() < 0.8:
                t.px(x, 13, cor("8a7a3a"))
                t.px(x, 14, cor("6a5e2e"))
    return t


def piso_cais(var):
    """Concreto do cais, molhado de névoa: mais escuro e com poças."""
    t = base.piso_concreto(var + 4)
    for y in range(16):
        for x in range(16):
            t.p[x, y] = mult(mistura(t.p[x, y], cor("2a3038"), 0.45), 0.85)
    if var == 1:
        t.elipse(8, 8, 5, 2.5, cor("4a5a70", 90))
    if var == 3:
        t.hlin(0, 15, 0, cor("6a6a4a"))
    return t


def piso_doca(var):
    t = base.piso_tabuas(cor("4a3a2e"), 40 + var, var)
    for y in range(16):
        for x in range(16):
            t.p[x, y] = mult(mistura(t.p[x, y], cor("2a3038"), 0.3), 0.9)
    if var == 2:
        t.px(3, 2, cor("8a8a90"))                                   # pregos
        t.px(12, 10, cor("8a8a90"))
    return t


def agua(var):
    t = Tela(16, 16)
    rng = random.Random(1500 + var)
    for y in range(16):
        t.hlin(0, 15, y, mistura(cor("0c1420"), cor("142236"), (y % 8) / 8))
    for _ in range(4):
        x, y = rng.randrange(14), rng.randrange(16)
        t.hlin(x, x + rng.randrange(2, 5), y, cor("3a5068", 150))
    return t


def padrao_galpao(t, pos, par, rng):
    """Chapa metálica ondulada, enferrujada embaixo."""
    base_c = cor("3a4048")
    t.ret(0, 0, 15, 15, base_c)
    for x in range(0, 16, 4):
        t.vlin(x, 0, 15, mult(base_c, 1.25))
        t.vlin(x + 1, 0, 15, mult(base_c, 1.1))
        t.vlin(x + 3, 0, 15, mult(base_c, 0.75))
    t.ruido(0, 0, 15, 15, rng, 0.06)
    if pos == 2:
        for _ in range(14):
            x, y = rng.randrange(16), rng.randrange(0, 12)
            t.px(x, y, cor("6a3a22", 200))
    if pos == 1 and par == 1:
        t.vlin(15, 0, 15, cor("1e2228"))                            # emenda das chapas


def padrao_galpao_ext(t, pos, par, rng):
    padrao_galpao(t, pos, par, rng)
    for y in range(16):
        for x in range(16):
            t.p[x, y] = mult(mistura(t.p[x, y], cor("4a2a24"), 0.25), 0.85)


def padrao_muro(t, pos, par, rng):
    t.ret(0, 0, 15, 15, cor("4a4a50"))
    t.ruido(0, 0, 15, 15, rng, 0.1)
    t.hlin(0, 15, 15, cor("2e2e34"))
    if par == 0:
        t.vlin(0, 0, 15, cor("2e2e34"))
    if pos == 1 and rng.random() < 0.6:
        t.ret(3, 5, 10, 8, cor("6a2a3a", 140))                      # pichação apagada


def plana_janela_galpao(brilho):
    """Janelas altas de caixilho de ferro, perto do teto."""
    t = Tela(16, 48)
    if brilho:
        t.ret(2, 3, 13, 18, cor("8ea6d8", 60))
        return t
    plana = empilhar_face(base.face(padrao_galpao, rodape=cor("22262c"), moldura=cor("5a626e"), semente=21))
    t.colar(plana, 0, 0)
    t.ret(1, 2, 14, 19, cor("22262c"))
    for y in range(3, 19):
        t.hlin(2, 13, y, mistura(cor("0e1830"), cor("1e2c4a"), (y - 3) / 16))
    for x in (5, 9):
        t.vlin(x, 3, 18, cor("22262c"))
    for y in (8, 13):
        t.hlin(2, 13, y, cor("22262c"))
    t.px(3, 4, cor("6a7aa0"))
    t.px(11, 15, cor("2a3a5a"))                                     # vidro quebrado
    t.px(12, 16, cor("0a0a10"))
    return t


def plana_portao(brilho):
    """Portão de correr do galpão, aberto numa fresta escura."""
    t = Tela(16, 48)
    if brilho:
        t.ret(5, 10, 10, 46, cor("e8c070", 50))
        return t
    t.ret(0, 0, 15, 47, cor("4a3a30"))
    for y in range(2, 48, 3):
        t.hlin(0, 15, y, cor("3a2c24"))
    t.ret(4, 8, 11, 47, cor("0a0a0e"))
    t.vlin(3, 8, 47, cor("8a7040"))
    t.vlin(12, 8, 47, cor("8a7040"))
    return t


def prateleira_galpao(nome, n_caixas, marcada=False, semente=0):
    """Estante industrial alta: 48 x 12 x 54, montantes laranja, caixas de papelão."""
    w, d, h = 48, 12, 54
    rng = random.Random(400 + semente)
    laranja = cor("b0602a")
    caixas = []
    for (x, y) in ((0, 0), (w - 2, 0), (0, d - 2), (w - 2, d - 2)):
        caixas.append(Caixa(x, y, 0, 2, 2, h, topo=laranja, sul=mult(laranja, 0.95), leste=mult(laranja, 0.75)))
    niveis = 4
    for k in range(niveis):
        z = 1 + k * 13
        caixas.append(Caixa(0, 0, z, w, d, 2, topo=cor("5a6a7a"), sul=cor("3a6aa0"), leste=cor("2a4a70")))
        x = 3
        while x < w - 8:
            bw = rng.randrange(7, 13)
            if x + bw > w - 3:
                break
            bh = rng.randrange(6, 11)
            papelao = mult(cor("9a7a52"), rng.uniform(0.75, 1.05))
            caixas.append(Caixa(x, 2, z + 2, bw, 8, bh, topo=mult(papelao, 1.15),
                                sul=lambda t, c=papelao: (t.ret(0, 0, t.w - 1, t.h - 1, c),
                                                          t.hlin(0, t.w - 1, t.h // 2, mult(c, 0.8))),
                                leste=mult(papelao, 0.8)))
            x += bw + rng.randrange(1, 3)
    if marcada:
        def fita(t):
            t.ret(0, 0, t.w - 1, t.h - 1, cor("a8845a"))
            for k in range(0, t.w, 3):
                t.vlin(k, 0, t.h - 1, cor("e0c020"))
                t.vlin(k + 1, 0, t.h - 1, cor("1a1a1a"))
            t.ret(t.w // 2 - 3, 2, t.w // 2 + 2, t.h - 3, cor("e8e0c8"))
            t.ret(t.w // 2 - 1, 3, t.w // 2, t.h - 5, cor("c02a2a"))  # ponto de exclamação
            t.px(t.w // 2 - 1, t.h - 4, cor("c02a2a"))
            t.px(t.w // 2, t.h - 4, cor("c02a2a"))
        caixas.append(Caixa(w // 2 - 7, 1, 15, 14, 10, 10, topo=cor("c8a070"), sul=fita, leste=cor("8a6a42")))
    caixas[4:] = sorted(caixas[4:], key=lambda c: (c.oz, c.oy, c.ox))
    return segmentar(nome, caixas, w, d, h)


def numero_chao(n):
    """Número da estante pintado no chão, em losango (como TAPETE)."""
    def pintar(t):
        t.ret(0, 0, t.w - 1, t.h - 1, cor("00000000"))
        t.ret(1, 1, t.w - 2, t.h - 2, cor("c8b040", 170))
        t.ret(2, 2, t.w - 3, t.h - 3, cor("2a2a2e", 0))
        escrever(t, str(n), 5, 3, cor("e0c850", 220), 1)
    return inteiro(f"NUMERO_{n}", [Caixa(0, 0, 0, 14, 12, 0, topo=pintar)], 14, 12, 0, contorno=False)


def bancada_radios():
    madeira = cor("4a3426")

    def tampo(t):
        t.ret(0, 0, t.w - 1, t.h - 1, mult(madeira, 1.2))
        t.ret(30, 3, 40, 9, cor("e8dcc0"))                          # papéis
    caixas = [
        Caixa(0, 0, 0, 56, 14, 16, topo=tampo, sul=lambda t: (t.ret(0, 0, t.w - 1, t.h - 1, madeira),
                                                              t.vlin(t.w // 2, 0, t.h - 1, mult(madeira, 0.7))),
              leste=mult(madeira, 0.8)),
        # rádio valvulado
        Caixa(3, 2, 16, 12, 8, 10, topo=cor("6a4a30"), sul=lambda t: (t.ret(0, 0, t.w - 1, t.h - 1, cor("7a5a3a")),
                                                                     t.ret(2, 2, 6, 6, cor("c8b890")),
                                                                     t.px(9, 4, cor("2a2018")), t.px(9, 7, cor("2a2018"))),
              leste=cor("5a3a24")),
        # TV de tubo
        Caixa(18, 1, 16, 14, 11, 13, topo=cor("8a8478"), sul=lambda t: (t.ret(0, 0, t.w - 1, t.h - 1, cor("a8a294")),
                                                                       t.ret(2, 2, 10, 10, cor("101418"))),
              leste=cor("6a6458")),
        # rádio de pilha
        Caixa(42, 3, 16, 10, 6, 7, topo=cor("3a3a42"), sul=lambda t: (t.ret(0, 0, t.w - 1, t.h - 1, cor("2a2a30")),
                                                                     t.ret(1, 1, 5, 5, cor("6a6a72"))),
              leste=cor("1e1e24")),
        Caixa(52, 4, 23, 1, 1, 10, topo=cor("aaaaaa"), sul=cor("aaaaaa"), leste=cor("888888")),     # antena
    ]
    return segmentar("BANCADA_RADIOS", caixas, 56, 14, 33)


def estatica_tela(nome, w, h, semente):
    """Tela chiando (emissiva): ruído claro em linhas."""
    t = Tela(w, h)
    rng = random.Random(semente)
    for y in range(h):
        for x in range(w):
            v = rng.uniform(0.4, 1.0) * (0.75 if y % 2 else 1.0)
            t.p[x, y] = mult(cor("c8d8f0"), v)
    return (nome, cisalhar(t, "sul"))


def caixotes_galpao():
    caixas = []
    madeira = cor("6a4a30")
    for (x, y, z, w, d, h) in ((0, 0, 0, 20, 18, 16), (20, 2, 0, 16, 16, 14), (2, 2, 16, 16, 14, 14)):
        caixas.append(Caixa(x, y, z, w, d, h, topo=lambda t: (t.ret(0, 0, t.w - 1, t.h - 1, mult(madeira, 1.2)),
                                                             t.vlin(t.w // 2, 0, t.h - 1, mult(madeira, 0.8))),
                            sul=lambda t: (t.ret(0, 0, t.w - 1, t.h - 1, madeira),
                                           [t.hlin(0, t.w - 1, k, mult(madeira, 0.7)) for k in range(3, t.h, 5)],
                                           linha_diag(t, mult(madeira, 1.2))),
                            leste=mult(madeira, 0.78)))
    return segmentar("CAIXOTES_GALPAO", caixas, 36, 18, 30)


def linha_diag(t, c):
    for k in range(min(t.w, t.h)):
        t.px(k, t.h - 1 - k, c)


def mesa_prancheta():
    c = cor("5a5a62")
    return inteiro("MESA_PRANCHETA", [
        Caixa(1, 1, 0, 2, 2, 12, topo=c, sul=c, leste=mult(c, 0.8)),
        Caixa(15, 1, 0, 2, 2, 12, topo=c, sul=c, leste=mult(c, 0.8)),
        Caixa(1, 9, 0, 2, 2, 12, topo=c, sul=c, leste=mult(c, 0.8)),
        Caixa(15, 9, 0, 2, 2, 12, topo=c, sul=c, leste=mult(c, 0.8)),
        Caixa(0, 0, 12, 18, 12, 2, topo=lambda t: (t.ret(0, 0, t.w - 1, t.h - 1, cor("6a5a4a")),
                                                   t.ret(4, 2, 12, 9, cor("8a6a3a")),
                                                   t.ret(5, 3, 11, 9, cor("e8e0c8")),
                                                   [t.hlin(6, 10, y, cor("6a6050")) for y in (5, 7)],
                                                   t.ret(7, 2, 9, 2, base.METAL_CLARO)),
              sul=cor("4a3e32"), leste=cor("3a2e24")),
    ], 18, 12, 14)


def container(nome, c, semente):
    """Contêiner de 64 x 28 x 40, com nervuras."""
    def lado(t):
        t.ret(0, 0, t.w - 1, t.h - 1, c)
        for x in range(0, t.w, 3):
            t.vlin(x, 1, t.h - 2, mult(c, 0.82))
        t.hlin(0, t.w - 1, 0, mult(c, 1.3))
        t.hlin(0, t.w - 1, t.h - 1, mult(c, 0.6))
        rng = random.Random(semente)
        for _ in range(20):
            t.px(rng.randrange(t.w), rng.randrange(t.h), cor("6a3a22", 180))

    def topo(t):
        t.ret(0, 0, t.w - 1, t.h - 1, mult(c, 1.15))
        for y in range(2, t.h, 4):
            t.hlin(1, t.w - 2, y, mult(c, 1.0))
    return segmentar(nome, [Caixa(0, 0, 0, 64, 28, 40, topo=topo, sul=lado, leste=lado)], 64, 28, 40)


def cabeco():
    c = cor("2a2a30")
    return inteiro("CABECO", [Caixa(1, 1, 0, 6, 6, 6, topo=c, sul=c, leste=mult(c, 0.7)),
                              Caixa(0, 0, 6, 8, 8, 2, topo=mult(c, 1.3), sul=c, leste=mult(c, 0.7))], 8, 8, 8)


def poste():
    c = cor("3a3e44")
    return inteiro("POSTE", [Caixa(0, 0, 0, 4, 4, 2, topo=c, sul=c, leste=mult(c, 0.7)),
                             Caixa(1, 1, 2, 2, 2, 56, topo=c, sul=mult(c, 1.1), leste=mult(c, 0.7)),
                             Caixa(0, 1, 56, 8, 3, 3, topo=cor("5a5e66"), sul=cor("f0e0a0"), leste=cor("c8b880"))],
                   8, 4, 60)


def alto_falante():
    """Corneta de porto num poste baixo, a boca virada para a câmera."""
    c = cor("6a6e5a")
    caixas = [Caixa(2, 2, 0, 3, 3, 26, topo=cor("3a3e44"), sul=cor("44484e"), leste=cor("2e3238")),
              Caixa(0, 0, 26, 7, 7, 5, topo=mult(c, 1.2), sul=c, leste=mult(c, 0.7)),
              Caixa(-1, 6, 23, 9, 3, 11, topo=mult(c, 1.1),
                    sul=lambda t: (t.ret(0, 0, t.w - 1, t.h - 1, cor("1a1c18")), t.moldura(0, 0, t.w - 1, t.h - 1, mult(c, 1.3))),
                    leste=mult(c, 0.7))]
    t, ancora = renderizar(caixas, -1, 0, 8, 9, 34)
    return [("ALTO_FALANTE", t, ancora, -1, 0, 9, 9)]


def grade_portao():
    c = cor("4a4e56")

    def grade(t):
        for x in range(0, t.w, 3):
            t.vlin(x, 0, t.h - 1, c)
        t.hlin(0, t.w - 1, 0, mult(c, 1.3))
        t.hlin(0, t.w - 1, t.h // 2, c)
    return segmentar("GRADE", [Caixa(0, 0, 0, 32, 2, 30, topo=c, sul=grade, leste=c)], 32, 2, 30)


def nevoa_textura():
    """Névoa tileável 256x256: ruído de valor suavizado, só alfa."""
    n = 256
    rng = random.Random(77)
    grade = [[rng.random() for _ in range(17)] for _ in range(17)]
    for i in range(17):
        grade[16][i] = grade[0][i]
        grade[i][16] = grade[i][0]
    im = Image.new("RGBA", (n, n))
    px = im.load()

    def suave(t):
        return t * t * (3 - 2 * t)
    for y in range(n):
        for x in range(n):
            v = 0.0
            amp, total = 1.0, 0.0
            for oit in (1, 2, 4):
                cel = 16 // oit
                gx, gy = x * 16 / n, y * 16 / n
                i0, j0 = int(gx) // cel * cel, int(gy) // cel * cel
                fx, fy = suave((gx - i0) / cel), suave((gy - j0) / cel)
                i1, j1 = (i0 + cel) % 16, (j0 + cel) % 16
                a = grade[j0][i0] * (1 - fx) + grade[j0][i1] * fx
                b = grade[j1][i0] * (1 - fx) + grade[j1][i1] * fx
                v += amp * (a * (1 - fy) + b * fy)
                total += amp
                amp *= 0.5
            v /= total
            a = max(0, min(255, int((v - 0.3) * 1.6 * 255)))
            px[x, y] = (178, 190, 210, a)
    im.save(RAIZ / "assets" / "nevoa.png")


# ----------------------------------------------------------- montagem

def montar():
    pecas = []      # (nome, Tela, ancora, ox, oy, w, d)
    pisos = []      # (nome, [Tela])

    def piso(nome, texturas):
        pisos.append((nome, [losango(tx) for tx in texturas]))

    piso("PISO_CORREDOR", [base.piso_tabuas(cor("5a3d2e"), 1, v) for v in range(4)])
    piso("PISO_COZINHA", [base.piso_xadrez(v) for v in range(4)])
    piso("PISO_HOSPEDES", [base.piso_tabuas(cor("67503f"), 2, v) for v in range(4)])
    piso("PISO_SALA", [base.piso_tabuas(cor("432c29"), 3, v) for v in range(4)])
    piso("PISO_LOJA", [base.piso_parquete(v) for v in range(4)])
    piso("PISO_CAFE", [base.piso_tabuas(cor("5a3824"), 4, v) for v in range(4)])
    piso("PISO_DEPOSITO", [base.piso_concreto(v) for v in range(4)])
    piso("DEGRAU", [base.degrau(1.0, v) for v in range(4)])
    piso("VAO", [base.vao_escada(v) for v in range(4)])
    piso("PISO_GALPAO", [piso_galpao(v) for v in range(4)])
    piso("PISO_CAIS", [piso_cais(v) for v in range(4)])
    piso("PISO_DOCA", [piso_doca(v) for v in range(4)])
    piso("AGUA", [agua(v) for v in range(4)])
    pisos.append(("TOPO", [topo_parede()]))
    pisos.append(("TOPO_MADEIRA", [topo_madeira()]))
    pisos.append(("SOMBRA_NORTE", [sombra_losango("norte")]))
    pisos.append(("SOMBRA_OESTE", [sombra_losango("oeste")]))

    # Papéis de parede: uma face sul e uma leste para cada um.
    papeis = [
        ("CORREDOR", empilhar_face(base.face(base.padrao_corredor, semente=1))),
        ("COZINHA", empilhar_face(base.face(padrao_azulejo, rodape=cor("3a4a46"), semente=8))),
        ("HOSPEDES", empilhar_face(base.face(base.padrao_hospedes, semente=3))),
        ("SALA", empilhar_face(base.face(base.padrao_sala, rodape=cor("1e1416"), semente=4))),
        ("LOJA", empilhar_face(base.face(base.padrao_loja, rodape=cor("1e1410"), moldura=cor("6a4630"), semente=5))),
        ("CAFE", empilhar_face(base.face(base.padrao_cafe, rodape=cor("2a1a14"), moldura=cor("4a3020"), semente=6))),
        ("DEPOSITO", empilhar_face(base.face(base.padrao_deposito, rodape=cor("26262c"), moldura=cor("6a6a72"), semente=7))),
    ]
    papeis += [(f"JANELA_COZINHA_{k}", plana_janela_cozinha(k, False)) for k in range(4)]
    papeis += [("JANELA", plana_janela(False)), ("PORTA", plana_porta(False))]
    papeis += [("GALPAO", empilhar_face(base.face(padrao_galpao, rodape=cor("22262c"), moldura=cor("5a626e"), semente=21))),
               ("GALPAO_EXT", empilhar_face(base.face(padrao_galpao_ext, rodape=cor("1e1a1a"), moldura=cor("4a3a34"), semente=22))),
               ("MURO", empilhar_face(base.face(padrao_muro, rodape=cor("26262c"), moldura=cor("5a5a62"), semente=23))),
               ("JANELA_GALPAO", plana_janela_galpao(False)), ("PORTAO", plana_portao(False))]
    guarda = Tela(16, 48)
    plana_guarda(guarda)
    papeis.append(("GUARDA", guarda))
    escada = Tela(16, 48)
    plana_madeira(cor("4a3020"))(escada)
    papeis.append(("ESCADA", escada))
    brilhos = {f"JANELA_COZINHA_{k}": plana_janela_cozinha(k, True) for k in range(4)}
    brilhos["JANELA"] = plana_janela(True)
    brilhos["PORTA"] = plana_porta(True)
    brilhos["JANELA_GALPAO"] = plana_janela_galpao(True)
    brilhos["PORTAO"] = plana_portao(True)

    faces = []   # (nome, Tela)
    for nome, plana in papeis:
        faces.append((f"PAREDE_SUL_{nome}", face_parede(plana, "sul")))
        faces.append((f"PAREDE_LESTE_{nome}", face_parede(plana, "leste")))
        if nome in brilhos:
            faces.append((f"BRILHO_SUL_{nome}", face_parede(brilhos[nome], "sul")))
            faces.append((f"BRILHO_LESTE_{nome}", face_parede(brilhos[nome], "leste")))

    for gerador in (lambda: bancada("lisa"), lambda: bancada("pia"), lambda: bancada("fogao"), geladeira,
                    mesa_cozinha, lambda: cadeira("norte"), lambda: cadeira("sul"), lambda: cadeira("oeste"),
                    lambda: cadeira("leste"), lixeira, planta, cama_hospedes, escrivaninha, rack, sofa,
                    estante_livros, luminaria, pufe, cama_icaro, passadeira, capacho, estante_discos, caixote,
                    balcao, banquinho, balcao_cafe, vitrola, catalogo, mesa_bistro,
                    lambda: prateleira("PRATELEIRA", 32, 44),
                    lambda: prateleira("PRATELEIRA_MARCADA", 48, 36, marcada=True, semente=12),
                    caixas_pilha, caixa_pequena,
                    lambda: tapete("TAPETE_SALA", 64, 48, cor("5a2430"), cor("c49a5a"), 9),
                    lambda: tapete("TAPETE_COZINHA", 40, 32, cor("3a4a5a"), cor("c8b48a"), 14),
                    lambda: prateleira_galpao("PRATELEIRA_G", 0),
                    lambda: prateleira_galpao("PRATELEIRA_G2", 0, semente=3),
                    lambda: prateleira_galpao("PRATELEIRA_G_MARCADA", 0, marcada=True, semente=7),
                    bancada_radios, caixotes_galpao, mesa_prancheta,
                    lambda: container("CONTAINER_VERMELHO", cor("7a2a24"), 1),
                    lambda: container("CONTAINER_AZUL", cor("2a4a6a"), 2),
                    cabeco, poste, alto_falante, grade_portao,
                    *[(lambda n=n: numero_chao(n)) for n in range(1, 9)]):
        pecas.extend(gerador())

    # Decalques de parede, já inclinados: (nome, Tela, n_tiles)
    decalques = []
    for nome, plana, lado in (("TV", tv_plana(False), "sul"), ("TELA_TV", tv_plana(True), "sul"),
                              ("PLACA", base.letreiro_fundo(), "sul"), ("PLACA_LETRAS", base.letreiro_letras(), "sul"),
                              ("LOUSA", lousa_plana(), "sul"),
                              ("QUADRO_1", quadro_plano("QUADRO_1"), "sul"), ("QUADRO_3", quadro_plano("QUADRO_3"), "sul"),
                              ("POSTER_1", quadro_plano("POSTER_1"), "leste"), ("POSTER_3", quadro_plano("POSTER_3"), "leste"),
                              ("QUADRO_DISCO_1", quadro_plano("QUADRO_DISCO_1"), "sul"),
                              ("QUADRO_DISCO_2", quadro_plano("QUADRO_DISCO_2"), "sul")):
        # largura arredondada para múltiplo de 16, centrada, para casar com as faces
        n = max(1, math.ceil(plana.w / 16))
        larga = Tela(16 * n, plana.h)
        larga.colar(plana, (16 * n - plana.w) // 2, 0)
        decalques.append((nome, cisalhar(larga, lado), n))

    extras = [("SOMBRA_PES", sombra_pes()), ("DISCO", disco_topo()), ("NOTA", base.nota()),
              estatica_tela("ESTATICA_TV", 9, 8, 1), estatica_tela("ESTATICA_RADIO", 5, 5, 2)]
    return pisos, faces, pecas, decalques, extras


def empacotar(itens):
    """itens: (nome, Tela). Prateleiras simples, os mais altos primeiro."""
    posicoes = {}
    x, y, linha = 0, 0, 0
    for nome, tela in sorted(itens, key=lambda i: -i[1].h):
        if x + tela.w > LARGURA_ATLAS:
            x, y = 0, y + linha + 2
            linha = 0
        posicoes[nome] = (x, y)
        x += tela.w + 2
        linha = max(linha, tela.h)
    altura = 1
    while altura < y + linha:
        altura *= 2
    atlas = Image.new("RGBA", (LARGURA_ATLAS, altura), (0, 0, 0, 0))
    for nome, tela in itens:
        atlas.paste(tela.im, posicoes[nome])
    return atlas, posicoes


def main():
    pisos, faces, pecas, decalques, extras = montar()
    itens = []
    # Variantes de piso lado a lado, para o motor somar 34 px por variante.
    for nome, telas in pisos:
        faixa = Tela(34 * len(telas) - 2, 16)
        for k, tela in enumerate(telas):
            faixa.colar(tela, 34 * k, 0)
        itens.append((nome, faixa))
    itens += faces
    itens += [(n, t) for (n, t, *_resto) in pecas]
    itens += [(n, t) for (n, t, _) in decalques]
    itens += extras
    atlas, pos = empacotar(itens)
    atlas.save(RAIZ / "assets" / "tileset-iso.png")
    nevoa_textura()

    linhas = ["# Gerado por ferramentas/gerar_iso.py. Não editar à mão.",
              f"# Atlas {LARGURA_ATLAS}x{atlas.height}. Variantes de piso a cada 34 px.", ""]

    def eq(nome, valor):
        linhas.append(f".equ {nome}, {valor}")

    for nome, telas in pisos:
        x, y = pos[nome]
        eq(f"S_{nome}_X", x)
        eq(f"S_{nome}_Y", y)
    linhas.append("")
    for nome, tela in faces:
        x, y = pos[nome]
        eq(f"S_{nome}_X", x)
        eq(f"S_{nome}_Y", y)
    linhas.append("")
    for (nome, tela, ancora, ox, oy, w, d) in pecas:
        x, y = pos[nome]
        # KX/KY: centro do tile mais à frente do pedaço, usado como chave de profundidade
        for campo, valor in (("X", x), ("Y", y), ("L", tela.w), ("A", tela.h), ("AX", ancora[0]), ("AY", ancora[1]),
                             ("OX", ox), ("OY", oy), ("W", w), ("D", d),
                             ("KX", w - min(w, 16) // 2), ("KY", d - min(d, 16) // 2)):
            eq(f"S_{nome}_{campo}", valor)
    linhas.append("")
    for (nome, tela, n) in decalques:
        x, y = pos[nome]
        for campo, valor in (("X", x), ("Y", y), ("L", tela.w), ("A", tela.h), ("N", n)):
            eq(f"S_{nome}_{campo}", valor)
    linhas.append("")
    for nome, tela in extras:
        x, y = pos[nome]
        for campo, valor in (("X", x), ("Y", y), ("L", tela.w), ("A", tela.h)):
            eq(f"S_{nome}_{campo}", valor)
    (RAIZ / "tileset.inc").write_text("\n".join(linhas) + "\n", encoding="utf-8")
    print(f"tileset-iso.png {LARGURA_ATLAS}x{atlas.height}: {len(pecas)} peças de móvel, {len(faces)} faces, {len(decalques)} decalques")


if __name__ == "__main__":
    main()
