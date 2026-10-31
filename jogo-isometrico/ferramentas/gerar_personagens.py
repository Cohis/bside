#!/usr/bin/env python3
"""Gera o elenco da Sala 2 (galpão e doca) em pixel art na escala do jogo.

Cada quadro de corpo mede 36x48 com os pés em (18, 45), a mesma escala em que a
sprite de Ícaro aparece na isométrica. Personagens: Hank, agente carmesim, anjo e
os olhos de Mael. Objetos da Sala 1 que o roteiro mexe: o bilhete do balcão, a
lista do depósito e a caixa do pedido do Anderson. Também gera peças de interface (símbolos das notas, anel do
pulso, tecla E, área segura).

Saídas:
  assets/personagens.png            atlas
  personagens.inc                   .equ P_<POSE>_{X,Y,L,A,N,AX,AY} (N = quadros)
  ferramentas/previa_personagens.png  prévia ampliada para revisão

Uso: python3 ferramentas/gerar_personagens.py   (ou `make arte`)
"""
import math
import random
import sys
from pathlib import Path

from PIL import Image, ImageDraw

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gerar_tileset import CONTORNO, Tela, alfa, cor, mult  # noqa: E402

RAIZ = Path(__file__).resolve().parent.parent
L, A = 36, 48           # quadro de corpo
PE_X, PE_Y = 18, 45     # âncora (pés)
LARGURA_ATLAS = 1024

SUL, LESTE, NORTE, OESTE = "S", "L", "N", "O"


# ------------------------------------------------------------ utilidades

def espelhar(t):
    n = Tela(t.w, t.h)
    n.im = t.im.transpose(Image.FLIP_LEFT_RIGHT)
    n.p = n.im.load()
    return n


def contorno_externo(t, c=CONTORNO):
    """Contorno de 1 px por fora da silhueta (só onde está vazio)."""
    alvo = []
    for y in range(t.h):
        for x in range(t.w):
            if t.p[x, y][3] >= 128:
                continue
            for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                nx, ny = x + dx, y + dy
                if 0 <= nx < t.w and 0 <= ny < t.h and t.p[nx, ny][3] >= 200 and t.p[nx, ny][:3] != c[:3]:
                    alvo.append((x, y))
                    break
    for x, y in alvo:
        t.p[x, y] = alfa(c, 230)


def sombrear_lado(t, x_corte, f=0.82):
    """Escurece tudo à direita de x_corte: luz vindo da esquerda e de cima."""
    for y in range(t.h):
        for x in range(x_corte, t.w):
            c = t.p[x, y]
            if c[3] > 0 and c[:3] != CONTORNO[:3]:
                t.p[x, y] = mult(c, f)


def linha(t, x0, y0, x1, y1, c):
    n = int(max(abs(x1 - x0), abs(y1 - y0), 1))
    for i in range(n + 1):
        t.px(round(x0 + (x1 - x0) * i / n), round(y0 + (y1 - y0) * i / n), c)


# --------------------------------------------------------- corpo genérico
#
# Medidas para a altura base (Ícaro): topo do cabelo ~y5, rosto y8..17,
# pescoço y18, tronco y19..29, quadril y30..32, pernas y33..43, pés y44..45.
# dy desloca tudo para cima (personagens mais altos).

def passo(quadro):
    """Quadros de caminhada 0..3: (perna da frente, balanço, quique)."""
    if quadro is None:
        return 0, 0, 0
    return [(1, 1, 0), (0, 0, -1), (-1, -1, 0), (0, 0, -1)][quadro % 4]


def pernas(t, d, quadro, calca, bota, dy=0, largura=3, curta=0):
    frente, _, quique = passo(quadro)
    topo = 33 - dy + quique + curta
    if d in (SUL, NORTE):
        for lado, x0 in ((-1, 14), (1, 19)):
            x0 = x0 + (3 - largura) // 2 + (1 if lado < 0 else 0) - (0 if largura == 3 else 0)
            erguido = frente == lado
            avanco = frente == -lado
            y_pe = 44 - (1 if erguido else 0) + (1 if avanco and d == SUL else 0)
            t.ret(x0, topo, x0 + largura - 1, y_pe - 1, mult(calca, 0.92 if lado > 0 else 1.0))
            t.ret(x0 - (1 if lado < 0 else 0), y_pe, x0 + largura - (0 if lado < 0 else 1), y_pe + 1, bota)
    else:
        # perfil virado para a direita (leste); oeste é espelhado depois
        abre = frente * 3
        tras = (-abre, 17, mult(calca, 0.78))
        dian = (abre, 18, calca)
        for desloc, x0, c in (tras, dian):
            pe_y = 44 if desloc != 0 or quadro is None else 44
            linha_meio = x0 + desloc // 2
            t.ret(x0, topo, x0 + 2, topo + 4, c)
            t.ret(linha_meio, topo + 5, linha_meio + 2, 43 - (1 if desloc < 0 else 0), c)
            t.ret(x0 + desloc, pe_y - (1 if desloc < 0 else 0), x0 + desloc + 3, pe_y + 1 - (1 if desloc < 0 else 0),
                  bota if desloc >= 0 else mult(bota, 0.8))


def tronco(t, d, quadro, roupa, dy=0, largo=0):
    _, _, quique = passo(quadro)
    y0, y1 = 19 - dy + quique, 32 - dy + quique
    if d in (SUL, NORTE):
        t.ret(13 - largo, y0 + 1, 22 + largo, y1, roupa)
        t.ret(12 - largo, y0 + 1, 23 + largo, y0 + 3, roupa)       # ombros
        t.hlin(14 - largo, 21 + largo, y0, roupa)
    else:
        t.ret(15 - largo // 2, y0, 21 + largo // 2, y1, roupa)
    return y0, y1


def bracos(t, d, quadro, manga, pele, dy=0, largo=0, mao_esq=None, mao_dir=None, manga_curta=False):
    _, balanco, quique = passo(quadro)
    y0 = 20 - dy + quique
    if d in (SUL, NORTE):
        for lado, x in ((-1, 11 - largo), (1, 23 + largo)):
            desloc = balanco * lado
            fim = 29 - dy + quique + desloc
            c = manga if not manga_curta else pele
            t.ret(x, y0, x + 1, fim, mult(c, 0.9 if lado > 0 else 1.0))
            if manga_curta:
                t.ret(x, y0, x + 1, y0 + 2, manga)
            t.ret(x, fim + 1, x + 1, fim + 2, pele)
    else:
        desloc = balanco * 2
        x = 17 + desloc
        fim = 29 - dy + quique
        t.ret(17, y0, 19, y0 + 4, manga)
        linha(t, 18, y0 + 4, x + 1, fim, manga)
        linha(t, 19, y0 + 4, x + 2, fim, manga)
        t.ret(x + 1, fim + 1, x + 2, fim + 2, pele)


def cabeca(t, d, quadro, pele, dy=0, olhos=cor("2a2030"), boca=None, largura=10):
    _, _, quique = passo(quadro)
    y0 = 8 - dy + quique
    if d in (SUL, NORTE):
        x0 = 18 - largura // 2
        t.ret(x0, y0, x0 + largura - 1, y0 + 9, pele)
        t.hlin(x0 + 1, x0 + largura - 2, y0 + 10, pele)
        t.ret(17, y0 + 10, 19, y0 + 11, mult(pele, 0.8))           # pescoço
        if d == SUL:
            t.px(15, y0 + 5, olhos)
            t.px(20, y0 + 5, olhos)
            t.px(15, y0 + 4, mult(olhos, 1.6))
            t.px(20, y0 + 4, mult(olhos, 1.6))
            if boca:
                t.hlin(17, 18, y0 + 8, boca)
    else:
        t.ret(14, y0, 22, y0 + 9, pele)
        t.hlin(15, 21, y0 + 10, pele)
        t.px(23, y0 + 5, pele)                                      # nariz
        t.ret(17, y0 + 10, 19, y0 + 11, mult(pele, 0.8))
        t.px(21, y0 + 5, olhos)
        t.px(21, y0 + 4, mult(olhos, 1.6))
    return y0


def corpo(d, quadro, P):
    """Monta um humanoide de roupa comum; P é o dicionário do personagem."""
    t = Tela(L, A)
    dy = P.get("dy", 0)
    largo = P.get("largo", 0)
    if P.get("atras"):
        P["atras"](t, d, quadro)
    pernas(t, d, quadro, P["calca"], P["bota"], dy, P.get("largura_perna", 3))
    tronco(t, d, quadro, P["roupa"], dy, largo)
    if P.get("sobre_tronco"):
        P["sobre_tronco"](t, d, quadro)
    if d != NORTE:
        bracos(t, d, quadro, P.get("manga", P["roupa"]), P["pele"], dy, largo, manga_curta=P.get("manga_curta", False))
    cabeca(t, d, quadro, P["pele"], dy, P.get("olhos", cor("2a2030")), P.get("boca"))
    P["cabelo"](t, d, quadro)
    if d == NORTE:
        bracos(t, d, quadro, P.get("manga", P["roupa"]), P["pele"], dy, largo, manga_curta=P.get("manga_curta", False))
    if P.get("frente"):
        P["frente"](t, d, quadro)
    contorno_externo(t)
    return t


def ciclo(P, d):
    """Parado + 4 quadros de caminhada numa direção; oeste é leste espelhado."""
    base = LESTE if d == OESTE else d
    quadros = [corpo(base, None, P)] + [corpo(base, q, P) for q in range(4)]
    if d == OESTE:
        quadros = [espelhar(q) for q in quadros]
    return quadros


# ----------------------------------------------------------------- Hank

HANK_PELE = cor("c08c6c")
HANK_BARBA = cor("b4aea8")
HANK_CHAPEU = cor("5a4232")


def hank_cabelo(t, d, quadro):
    _, _, q = passo(quadro)
    y = 8 - 3 + q
    cinza, escuro = HANK_BARBA, cor("7a7470")
    if d == SUL:
        # barba cheia do queixo até as bochechas
        t.ret(13, y + 6, 22, y + 10, cinza)
        t.ret(14, y + 11, 21, y + 12, cinza)
        t.hlin(15, 20, y + 13, mult(cinza, 0.85))
        t.hlin(16, 19, y + 7, mult(HANK_PELE, 0.7))                 # boca na barba
        t.ret(13, y + 2, 13, y + 6, escuro)
        t.ret(22, y + 2, 22, y + 6, escuro)
        t.hlin(14, 16, y + 3, escuro)                               # sobrancelhas
        t.hlin(19, 21, y + 3, escuro)
    elif d == LESTE:
        t.ret(15, y + 6, 22, y + 10, cinza)
        t.ret(16, y + 11, 21, y + 12, cinza)
        t.px(23, y + 7, cinza)
        t.ret(14, y + 2, 16, y + 7, escuro)
        t.hlin(20, 22, y + 3, escuro)
    else:
        t.ret(13, y + 2, 22, y + 10, escuro)
        t.ret(14, y + 6, 21, y + 11, mult(escuro, 0.9))
    # chapéu gasto de aba larga
    aba = mult(HANK_CHAPEU, 0.82)
    if d in (SUL, NORTE):
        t.ret(10, y - 1, 25, y + 1, aba)
        t.ret(13, y - 5, 22, y - 1, HANK_CHAPEU)
        t.hlin(13, 22, y - 2, cor("2e2018"))                        # fita
        t.hlin(14, 21, y - 5, mult(HANK_CHAPEU, 1.15))
        t.px(15, y - 4, mult(HANK_CHAPEU, 1.25))
    else:
        t.ret(11, y - 1, 26, y + 1, aba)
        t.ret(14, y - 5, 22, y - 1, HANK_CHAPEU)
        t.hlin(14, 22, y - 2, cor("2e2018"))
        t.hlin(15, 21, y - 5, mult(HANK_CHAPEU, 1.15))


def hank_casaco(t, d, quadro):
    _, _, q = passo(quadro)
    y0 = 19 - 3 + q
    camisa = cor("8a7c62")
    if d == SUL:
        t.ret(16, y0, 19, y0 + 8, camisa)                           # camisa aberta
        t.vlin(15, y0, y0 + 13, mult(cor("4e5236"), 0.7))
        t.vlin(20, y0, y0 + 13, mult(cor("4e5236"), 0.7))
        t.hlin(12, 23, y0 + 9, cor("3a2a1e"))                       # cinto
        t.px(17, y0 + 9, cor("c8a050"))
    elif d == LESTE:
        t.ret(20, y0 + 1, 21, y0 + 7, camisa)
        t.hlin(14, 22, y0 + 9, cor("3a2a1e"))
    else:
        t.vlin(17, y0 + 2, y0 + 12, mult(cor("4e5236"), 0.8))


def hank_aliança(t, d, quadro):
    if d == SUL:
        _, b, q = passo(quadro)
        t.px(10, 30 - 3 + q - b, cor("e8c060"))


HANK = dict(dy=3, largo=1, pele=HANK_PELE, roupa=cor("4e5236"), manga=cor("464a30"),
            calca=cor("3a3028"), bota=cor("221a18"), cabelo=hank_cabelo,
            sobre_tronco=hank_casaco, frente=hank_aliança, olhos=cor("3a3040"))


def hank_falando():
    t = corpo(SUL, None, HANK)
    # mão direita erguida na altura do peito, palma aberta
    t.ret(24, 18, 26, 20, cor("464a30"))
    t.ret(25, 14, 27, 17, HANK_PELE)
    t.px(26, 13, HANK_PELE)
    t.ret(24, 21, 25, 27, (0, 0, 0, 0))
    contorno_externo(t)
    return t


# ------------------------------------------------- agente carmesim / Eva

VESTE = cor("17141c")
VESTE_DOBRA = cor("26212e")
CARMIM = cor("a3182a")
CARMIM_VIVO = cor("e0303e")
PORCELANA = cor("e9e3da")
PORCELANA_SOMBRA = cor("b3aaa2")
OLHO_AZUL = cor("5ab4ff")
OLHO_BRILHO = cor("d2f0ff")


def veste(t, d, quadro, dy=1):
    """Manto preto até o tornozelo, barra e faixa carmesim."""
    frente, balanco, q = passo(quadro)
    y0 = 19 - dy + q
    if d in (SUL, NORTE):
        for y in range(y0, 44):
            meia = 5 + (y - y0) * 4 // (44 - y0)
            x0, x1 = 18 - meia, 17 + meia
            if y >= 41:
                x0 += balanco
                x1 += balanco
            t.hlin(x0, x1, y, VESTE)
        t.ret(12, y0 + 1, 23, y0 + 3, VESTE)
        # dobras e faixas
        for x in (15, 20):
            t.vlin(x, y0 + 12, 43, VESTE_DOBRA)
        t.hlin(10 + balanco, 25 + balanco, 43, CARMIM)
        if d == SUL:
            t.vlin(18, y0 + 2, 42, CARMIM)                          # fecho carmesim
            t.hlin(13, 22, y0 + 10, CARMIM)                         # faixa da cintura
            t.px(18, y0 + 10, CARMIM_VIVO)
        else:
            t.hlin(13, 22, y0 + 10, CARMIM)
        # botas aparecendo
        pe = 44
        t.ret(14 - (1 if frente > 0 else 0), pe, 16, pe + 1, cor("0c0a10"))
        t.ret(19, pe, 21 + (1 if frente < 0 else 0), pe + 1, cor("0c0a10"))
    else:
        for y in range(y0, 44):
            meia = 3 + (y - y0) * 3 // (44 - y0)
            x0, x1 = 18 - meia - (1 if y > 38 else 0), 18 + meia
            if y >= 40:
                x0 -= frente
                x1 += frente
            t.hlin(x0, x1, y, VESTE)
        t.vlin(16, y0 + 10, 43, VESTE_DOBRA)
        t.hlin(13 - frente, 23 + frente, 43, CARMIM)
        t.hlin(15, 21, y0 + 10, CARMIM)
        t.px(21, y0 + 10, CARMIM_VIVO)
        t.ret(19 + frente * 2, 44, 22 + frente * 2, 45, cor("0c0a10"))
        t.ret(14 - frente * 2, 44, 16 - frente * 2, 45, cor("08060c"))


def capuz(t, d, quadro, dy=1, olhos_acesos=False):
    _, _, q = passo(quadro)
    y = 8 - dy + q
    if d in (SUL, NORTE):
        t.ret(12, y - 2, 23, y + 11, VESTE)
        t.hlin(13, 22, y - 3, VESTE)
        t.hlin(15, 20, y - 4, VESTE_DOBRA)
        t.vlin(12, y + 2, y + 11, CARMIM)
        t.vlin(23, y + 2, y + 11, CARMIM)
        if d == SUL:
            t.ret(14, y + 1, 21, y + 10, PORCELANA)
            t.hlin(15, 20, y + 11, PORCELANA_SOMBRA)
            t.vlin(21, y + 2, y + 10, PORCELANA_SOMBRA)
            olho = OLHO_BRILHO if olhos_acesos else OLHO_AZUL
            t.hlin(15, 16, y + 5, olho)
            t.hlin(19, 20, y + 5, olho)
            t.vlin(18, y + 7, y + 9, CARMIM)                        # risco carmesim da máscara
            t.px(17, y + 2, mult(PORCELANA, 1.05))
    else:
        t.ret(13, y - 2, 22, y + 11, VESTE)
        t.hlin(14, 21, y - 3, VESTE)
        t.vlin(13, y + 2, y + 11, CARMIM)
        t.ret(19, y + 1, 23, y + 10, PORCELANA)
        t.vlin(19, y + 1, y + 10, PORCELANA_SOMBRA)
        t.hlin(21, 22, y + 5, OLHO_BRILHO if olhos_acesos else OLHO_AZUL)
        t.px(23, y + 8, CARMIM)


def agente(d, quadro, olhos_acesos=False):
    t = Tela(L, A)
    base = LESTE if d == OESTE else d
    veste(t, base, quadro)
    # mangas largas
    _, balanco, q = passo(quadro)
    if base in (SUL, NORTE):
        for lado, x in ((-1, 10), (1, 24)):
            fim = 30 + q + balanco * lado
            t.ret(x, 20 + q, x + 1, fim, mult(VESTE, 1.3 if lado < 0 else 1.0))
            t.hlin(x, x + 1, fim, CARMIM)
            if base == SUL:
                t.ret(x, fim + 1, x + 1, fim + 2, cor("e8e0d8"))     # luvas claras
    else:
        t.ret(17 + balanco * 2, 20 + q, 19 + balanco * 2, 30 + q, mult(VESTE, 1.3))
        t.hlin(17 + balanco * 2, 19 + balanco * 2, 30 + q, CARMIM)
    capuz(t, base, quadro, olhos_acesos=olhos_acesos)
    contorno_externo(t)
    return espelhar(t) if d == OESTE else t


def agente_ciclo(d):
    return [agente(d, None)] + [agente(d, q) for q in range(4)]


def agente_sentado(respira=0):
    """Sentado no chão contra os caixotes: joelhos para cima, mão no ombro ferido."""
    t = Tela(L, A)
    r = respira
    # pernas: coxas subindo até os joelhos e canelas descendo até as botas
    for lado, xj in ((-1, 12), (1, 22)):
        t.ret(xj - 2, 33, xj + 2, 40, VESTE)                        # canela
        t.ret(xj - 3, 31, xj + 3, 34, mult(VESTE, 1.2))             # joelho
        t.ret(xj - 3, 41, xj + 3, 45, cor("0c0a10"))                # bota
    t.ret(9, 38, 27, 42, VESTE)                                     # manto caído entre as pernas
    t.hlin(9, 27, 42, CARMIM)
    # tronco curvado, mais baixo que em pé
    y0 = 22 + r
    for y in range(y0, 40):
        meia = 5 + (y - y0) // 4
        t.hlin(18 - meia, 17 + meia, y, VESTE)
    t.hlin(13, 22, y0 + 9, CARMIM)
    t.vlin(18, y0 + 1, y0 + 8, CARMIM)
    # braço esquerdo cruzando até o ombro direito
    linha(t, 12, y0 + 2, 18, y0 + 8, mult(VESTE, 1.4))
    linha(t, 12, y0 + 3, 18, y0 + 9, mult(VESTE, 1.4))
    linha(t, 18, y0 + 8, 21, y0 + 2, mult(VESTE, 1.4))
    t.ret(20, y0, 22, y0 + 2, cor("e8e0d8"))                        # luva sobre o ombro
    t.px(23, y0 + 1, cor("6a1020"))                                 # sangue
    t.px(23, y0 + 3, cor("6a1020"))
    t.px(22, y0 + 4, cor("4a0a16"))
    t.px(21, 43, cor("4a0a16"))
    # braço direito largado sobre o joelho
    t.ret(24, y0 + 2, 25, 31, VESTE)
    t.ret(24, 32, 25, 33, cor("e8e0d8"))
    # cabeça baixa, inclinada para o lado ferido
    c = Tela(L, A)
    capuz(c, SUL, None, dy=0)
    t.colar(c, 1, 9 + r)
    contorno_externo(t)
    return t


def clarao(k):
    """Clarão azul do teleporte: anel que abre e some (3 quadros)."""
    t = Tela(L, A)
    raio = [5, 10, 15][k]
    a = [255, 200, 110][k]
    for ang in range(0, 360, 6):
        r = math.radians(ang)
        x = 18 + math.cos(r) * raio
        y = 30 + math.sin(r) * raio * 0.9
        t.px(x, y, alfa(OLHO_AZUL, a))
        t.px(x + 0.6, y, alfa(OLHO_BRILHO, a // 2))
    if k == 0:
        t.ret(16, 8, 20, 44, alfa(OLHO_BRILHO, 220))
        t.ret(14, 14, 22, 40, alfa(OLHO_AZUL, 140))
    elif k == 1:
        t.ret(17, 4, 19, 44, alfa(OLHO_BRILHO, 150))
    rng = random.Random(k)
    for _ in range(12 - 3 * k):
        t.px(rng.randint(6, 30), rng.randint(10, 44), alfa(OLHO_BRILHO, a))
    return t


# ---------------------------------------------------------------- anjo

ANJO_PELE = cor("e6e0d8")
ANJO_SOMBRA = cor("a8a0a0")
ESPINHO = cor("5a5866")


def coroa(t, cx, cy, fase, raio=7, rapido=False):
    n = 8
    for i in range(n):
        ang = fase + i * 2 * math.pi / n
        x = cx + math.cos(ang) * raio
        y = cy + math.sin(ang) * raio * 0.45 - (2 if rapido else 0)
        frente = math.sin(ang) > 0
        c = ESPINHO if frente else mult(ESPINHO, 0.65)
        t.px(x, y, c)
        t.px(x, y - 1, c)
        t.px(x, y - 2, mult(c, 1.4))
        if rapido:
            t.px(x + 1, y, alfa(c, 120))


def anjo_cabeca(t, cx, cy, boca_aberta=0):
    """Crânio alongado de porcelana, sem olhos; a mandíbula comprida tem dentes no
    lugar dos lábios, num sorriso que vai de orelha a orelha."""
    for y in range(cy - 8, cy + 6):
        meia = 3.6 if y < cy + 1 else 3.6 - (y - cy - 1) * 0.35
        t.hlin(round(cx - meia), round(cx + meia - 0.4), y, ANJO_PELE)
    t.hlin(cx - 2, cx + 2, cy - 9, ANJO_PELE)
    t.vlin(cx + 3, cy - 7, cy + 2, ANJO_SOMBRA)
    t.px(cx - 2, cy - 3, ANJO_SOMBRA)                               # depressões sem olhos
    t.px(cx + 1, cy - 3, ANJO_SOMBRA)
    # sorriso: linha escura atravessando o rosto, dentes em cima e embaixo
    yb = cy + 1
    t.hlin(cx - 5, cx + 5, yb, cor("3a1418"))
    t.px(cx - 5, yb - 1, cor("3a1418"))
    t.px(cx + 5, yb - 1, cor("3a1418"))
    if boca_aberta:
        t.ret(cx - 4, yb, cx + 4, yb + boca_aberta, cor("1a0408"))
        t.ret(cx - 3, yb + boca_aberta + 1, cx + 3, yb + boca_aberta + 3, ANJO_PELE)
    for x in range(cx - 4, cx + 5):
        t.px(x, yb - 1, cor("f8f4ec"))
        t.px(x, yb + 1 + boca_aberta, cor("f8f4ec") if x % 2 else ANJO_SOMBRA)


def anjo_tronco(t, cx, y0, y1):
    for y in range(y0, y1 + 1):
        meia = 3 if y < y0 + 6 else 2
        t.hlin(cx - meia, cx + meia - 1, y, ANJO_PELE)
    t.vlin(cx + 2, y0, y1, ANJO_SOMBRA)
    for y in range(y0 + 1, y0 + 7, 2):
        t.hlin(cx - 2, cx + 1, y, ANJO_SOMBRA)                      # costelas
    t.ret(cx - 1, y0 - 2, cx, y0 - 1, ANJO_SOMBRA)                  # pescoço fino


def anjo_pousado(k):
    """Agachado como aranha à espera de vibração; k gira a coroa de espinhos."""
    t = Tela(40, 40)
    cx = 20
    for lado in (-1, 1):
        # braços: cotovelos acima dos ombros, dedos no chão
        linha(t, cx + 2 * lado, 21, cx + 9 * lado, 13, ANJO_SOMBRA)
        linha(t, cx + 9 * lado, 13, cx + 14 * lado, 37, ANJO_SOMBRA)
        t.hlin(cx + 13 * lado - (1 if lado > 0 else 0), cx + 15 * lado, 37, ANJO_SOMBRA)
        # pernas dobradas
        linha(t, cx + 1 * lado, 30, cx + 8 * lado, 25, ANJO_PELE)
        linha(t, cx + 8 * lado, 25, cx + 7 * lado, 37, ANJO_PELE)
    anjo_tronco(t, cx, 20, 30)
    anjo_cabeca(t, cx, 13)
    contorno_externo(t)
    coroa(t, cx, 3, k * math.pi / 8)
    return t


def anjo_voando(k):
    t = Tela(40, 40)
    cx = 20
    anjo_tronco(t, cx, 16, 30)
    for lado in (-1, 1):
        linha(t, cx + 2 * lado, 17, cx + 12 * lado, 21 + k, ANJO_SOMBRA)
        linha(t, cx + 12 * lado, 21 + k, cx + 16 * lado, 29 + k, ANJO_SOMBRA)
        linha(t, cx + 1 * lado, 30, cx + 3 * lado, 38, ANJO_PELE)
    anjo_cabeca(t, cx, 9)
    contorno_externo(t)
    coroa(t, cx, 0, k * math.pi / 3, raio=8, rapido=True)
    return t


def anjo_gritando(k):
    t = Tela(40, 40)
    cx = 20
    for lado in (-1, 1):
        linha(t, cx + 2 * lado, 21, cx + 11 * lado, 10 - k, ANJO_SOMBRA)
        linha(t, cx + 11 * lado, 10 - k, cx + 14 * lado, 37, ANJO_SOMBRA)
        linha(t, cx + 1 * lado, 30, cx + 8 * lado, 26, ANJO_PELE)
        linha(t, cx + 8 * lado, 26, cx + 7 * lado, 37, ANJO_PELE)
    anjo_tronco(t, cx, 20, 30)
    anjo_cabeca(t, cx, 11, boca_aberta=3 + 2 * k)
    contorno_externo(t)
    coroa(t, cx, 1, k * math.pi / 2, raio=9, rapido=True)
    for i in range(3):                                              # ondas do grito
        r = 7 + i * 4 + k * 2
        for ang in range(20, 161, 10):
            a = math.radians(ang)
            t.px(cx + math.cos(a) * r * 1.5, 14 + math.sin(a) * r * 0.6, alfa(cor("ffe0e8"), 170 - i * 45))
    return t


def mael_olhos(k):
    t = Tela(20, 8)
    brilho = [cor("e8b030"), cor("ffd860")][k]
    for cx in (5, 14):
        t.elipse(cx, 4, 3.2, 1.8 + 0.4 * k, alfa(cor("8a5010"), 120))
        t.hlin(cx - 2, cx + 2, 4, brilho)
        t.hlin(cx - 1, cx + 1, 3, brilho)
        t.px(cx, 4, cor("2a1404"))                                  # pupila humana
        t.px(cx - 1, 5, alfa(brilho, 160))
        t.px(cx + 1, 5, alfa(brilho, 160))
    return t


# ------------------------------------------------- objetos da Sala 1
#
# Desenhados na projeção do jogo (tela x = x - y, tela y = (x + y) / 2 - z), com
# a âncora no ponto do chão sob o centro do objeto.

def poligono(t, pontos, c):
    ImageDraw.Draw(t.im).polygon(pontos, fill=c)


def bilhete():
    """Papel de 8x5 px deitado no tampo, dobrado ao meio, com três linhas de tinta."""
    t = Tela(16, 9)
    poligono(t, [(7, 1), (14, 4), (9, 7), (2, 4)], cor("e8e0c8"))
    poligono(t, [(7, 1), (10, 2), (5, 6), (2, 4)], cor("f6f0de"))
    for k in range(3):
        t.px(6 + k * 2, 3 + k, cor("4a4a6a"))
        t.px(7 + k * 2, 4 + k, cor("4a4a6a"))
    contorno_externo(t)
    return t


def lista_deposito():
    """Folha presa na frente da estante (face sul), com o cabeçalho e as linhas."""
    t = Tela(10, 14)
    poligono(t, [(1, 1), (8, 4), (8, 12), (1, 9)], cor("e8e0c8"))
    for x in range(2, 8):
        t.px(x, 2 + (x - 1) // 2, cor("a83030"))
        for linha in (5, 7, 9):
            if x < 7 or linha == 5:
                t.px(x, linha + (x - 1) // 2, cor("5a5a70"))
    t.px(4, 1, cor("c8c8d0"))                       # alfinete
    contorno_externo(t)
    return t


def caixa_pedido():
    """Caixa de 10x10x8 px de papelão, com fita no tampo e etiqueta branca na frente."""
    t = Tela(24, 22)
    c = cor("a8865a")
    poligono(t, [(12, 2), (22, 7), (12, 12), (2, 7)], mult(c, 1.15))
    poligono(t, [(2, 7), (12, 12), (12, 20), (2, 15)], mult(c, 0.84))
    poligono(t, [(12, 12), (22, 7), (22, 15), (12, 20)], mult(c, 0.64))
    for k in range(10):                              # fita ao longo do tampo
        t.px(7 + k, 4 + k // 2, cor("d8c8a0"))
    for x in range(4, 10):                           # etiqueta na face sul
        for y in range(12, 15):
            t.px(x, y + (x - 4) // 2, cor("f0ece0"))
        t.px(x, 13 + (x - 4) // 2, cor("4a4a6a") if x % 2 else cor("f0ece0"))
    contorno_externo(t)
    return t


# ------------------------------------------------------------ interface

NOTAS_CORES = [cor("e05a5a"), cor("e0b040"), cor("50c080"), cor("5a9ae8")]


def simbolo_nota(i, aceso=False):
    """Os 4 símbolos das notas: losango, triângulo, círculo e quadrado."""
    t = Tela(12, 12)
    c = NOTAS_CORES[i] if aceso else mult(NOTAS_CORES[i], 0.62)
    if i == 0:
        for y in range(12):
            m = 5 - abs(y - 5.5) + 0.5
            t.hlin(6 - m, 5 + m, y, c)
    elif i == 1:
        for y in range(1, 11):
            m = (y - 1) * 5 / 9
            t.hlin(6 - m - 0.5, 5 + m + 0.5, y, c)
    elif i == 2:
        t.elipse(6, 6, 5.5, 5.5, c)
    else:
        t.ret(1, 1, 10, 10, c)
    if aceso:
        t.px(4, 3, cor("ffffff"))
    contorno_externo(t)
    return t


def anel_pulso():
    t = Tela(32, 16)
    for ang in range(0, 360, 4):
        a = math.radians(ang)
        t.px(16 + math.cos(a) * 14.5, 8 + math.sin(a) * 7, cor("ffffff"))
    return t


def tecla_e():
    t = Tela(11, 11)
    t.ret(0, 0, 10, 10, cor("e8e0d0"))
    t.ret(1, 9, 9, 10, cor("9a948a"))
    t.moldura(0, 0, 10, 10, CONTORNO)
    for (x0, y0, x1, y1) in ((3, 2, 7, 2), (3, 2, 3, 7), (3, 4, 6, 4), (3, 7, 7, 7)):
        t.ret(x0, y0, x1, y1, CONTORNO)
    return t


def area_segura():
    """Marca no chão em losango (32x16): faixas de tinta reflexiva."""
    t = Tela(32, 16)
    for y in range(16):
        m = 16 - abs(y - 7.5) * 2
        if m > 0:
            t.hlin(16 - m, 15 + m, y, alfa(cor("50e0a0"), 70))
    for y in range(16):
        m = 16 - abs(y - 7.5) * 2
        t.px(16 - m, y, alfa(cor("80ffc0"), 220))
        t.px(15 + m, y, alfa(cor("80ffc0"), 220))
    return t


# --------------------------------------------------------------- montagem

def montar():
    """Lista de (nome, [quadros], âncora). Quadros de uma pose ficam lado a lado."""
    poses = []

    def pose(nome, quadros, ancora=(PE_X, PE_Y)):
        poses.append((nome, quadros, ancora))

    for d in (SUL, LESTE, NORTE, OESTE):
        hk = ciclo(HANK, d)
        pose(f"HANK_PARADO_{d}", hk[:1])
        pose(f"HANK_ANDA_{d}", hk[1:])
    pose("HANK_FALA", [hank_falando(), corpo(SUL, None, HANK)])

    for d in (SUL, LESTE, NORTE, OESTE):
        ag = agente_ciclo(d)
        pose(f"AGENTE_PARADO_{d}", ag[:1])
        pose(f"AGENTE_ANDA_{d}", ag[1:])
    pose("AGENTE_OLHOS", [agente(SUL, None, olhos_acesos=True), agente(SUL, None)])
    pose("AGENTE_SENTADO", [agente_sentado(respira=0), agente_sentado(respira=1)])
    pose("CLARAO", [clarao(k) for k in range(3)])

    pose("ANJO_POUSADO", [anjo_pousado(k) for k in range(4)], (20, 38))
    pose("ANJO_VOO", [anjo_voando(k) for k in range(2)], (20, 38))
    pose("ANJO_GRITO", [anjo_gritando(k) for k in range(2)], (20, 38))
    pose("MAEL", [mael_olhos(k) for k in range(2)], (10, 4))

    pose("BILHETE", [bilhete()], (8, 4))
    pose("LISTA", [lista_deposito()], (5, 11))
    pose("CAIXA_PEDIDO", [caixa_pedido()], (12, 16))

    for i in range(4):
        pose(f"NOTA_{i}", [simbolo_nota(i, False), simbolo_nota(i, True)], (6, 6))
    pose("ANEL", [anel_pulso()], (16, 8))
    pose("TECLA_E", [tecla_e()], (5, 5))
    pose("AREA_SEGURA", [area_segura()], (16, 8))
    return poses


def empacotar(poses):
    """Cada pose vira uma faixa horizontal; faixas em prateleiras, mais altas primeiro."""
    faixas = []
    for nome, quadros, ancora in poses:
        w, h = quadros[0].w, quadros[0].h
        f = Tela(w * len(quadros), h)
        for k, q in enumerate(quadros):
            f.colar(q, k * w, 0)
        faixas.append((nome, f, w, h, len(quadros), ancora))
    pos = {}
    x = y = linha_h = 0
    for nome, f, *_ in sorted(faixas, key=lambda i: -i[1].h):
        if x + f.w > LARGURA_ATLAS:
            x, y, linha_h = 0, y + linha_h + 2, 0
        pos[nome] = (x, y)
        x += f.w + 2
        linha_h = max(linha_h, f.h)
    altura = 1
    while altura < y + linha_h:
        altura *= 2
    atlas = Image.new("RGBA", (LARGURA_ATLAS, altura), (0, 0, 0, 0))
    for nome, f, *_ in faixas:
        atlas.paste(f.im, pos[nome])
    return atlas, pos, faixas


def previa(faixas, caminho):
    escala = 4
    linhas = []
    for nome, f, w, h, n, _ in faixas:
        if nome.startswith(("NOTA_", "ANEL", "TECLA", "AREA")):
            continue
        linhas.append((nome, f))
    larg = max(f.w for _, f in linhas) * escala + 8
    alt = sum(f.h * escala + 6 for _, f in linhas)
    im = Image.new("RGBA", (min(larg, 4000), alt), (34, 30, 40, 255))
    y = 0
    for nome, f in linhas:
        im.alpha_composite(f.im.resize((f.w * escala, f.h * escala), Image.NEAREST), (4, y))
        y += f.h * escala + 6
    im.save(caminho)


def main():
    poses = montar()
    atlas, pos, faixas = empacotar(poses)
    atlas.save(RAIZ / "assets" / "personagens.png")
    previa(faixas, RAIZ / "ferramentas" / "previa_personagens.png")
    linhas = ["# Gerado por ferramentas/gerar_personagens.py. Não editar à mão.",
              f"# Atlas {LARGURA_ATLAS}x{atlas.height}. Quadros de uma pose lado a lado, a cada P_*_L px.", ""]
    for nome, f, w, h, n, ancora in faixas:
        x, y = pos[nome]
        for campo, valor in (("X", x), ("Y", y), ("L", w), ("A", h), ("N", n), ("AX", ancora[0]), ("AY", ancora[1])):
            linhas.append(f".equ P_{nome}_{campo}, {valor}")
    (RAIZ / "personagens.inc").write_text("\n".join(linhas) + "\n", encoding="utf-8")
    print(f"personagens.png {LARGURA_ATLAS}x{atlas.height}: {len(faixas)} poses")


if __name__ == "__main__":
    main()
