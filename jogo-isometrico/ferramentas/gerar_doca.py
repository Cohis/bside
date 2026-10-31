#!/usr/bin/env python3
"""Fases da fuga pelos anjos (fim da Sala 2): dados, roteiro e verificação.

A fuga atravessa três trechos (doca, pátio de contêineres e quebra-mar), cada um
num andar de 22 x 22 tiles. Em cada ponto, Ícaro espera na marca verde; no 4º
pulso, a nota de um dos alto-falantes à mostra faz os anjos daquele ponto voarem
em linha reta até ele e pousarem em volta. Qualquer anjo a menos de RAIO_PEGA px
pega Ícaro: voando, pousado no alto-falante ou ainda escutando num cabeço. Os que
já pousaram em pontos anteriores continuam onde ficaram.

Este script descreve os trechos e, antes de gerar qualquer coisa, resolve cada
ponto: procura um caminho no espaço e no tempo (grade de 4 px) que chegue à marca
seguinte sem passar perto de nenhum anjo. Exige que exatamente o alto-falante da
solução funcione (mesmo jogando perfeito, os outros matam) e calcula a janela de
tempo a partir do caminho mais curto. Se algum ponto não fechar, para com erro.

Saídas:
  doca_dados.inc     plantas, móveis, luzes, alto-falantes, poleiros e pontos
  doca_roteiro.inc   a sequência dos trechos (incluída no roteiro de sala2.s)
  ferramentas/doca_solucoes.h   nota e caminho de cada ponto, para o robô de teste
  ../sprites/elenco-sala2/doca/<trecho>.png   mapa visto de cima com as soluções

Uso: python3 ferramentas/gerar_doca.py [--mapas]   (ou `make doca`)
"""
import math
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

RAIZ = Path(__file__).resolve().parent.parent
TILE, N = 16, 22
LADO = TILE * N

# Números do motor (bside.s, atores.s, doca.s, estruturas.inc).
VEL_ICARO = 56.0
VEL_ANJO = 170.0
RAIO_PEGA = 16.0
RAIO_AREA = 14
PE_LADO, PE_CIMA, PE_BAIXO = 5, 4, 1
Z_POLEIRO = 8
Z_CORNETA = 30
PISO = set("QTGS")

# Folgas do solucionador: o caminho do robô usa velocidade e raio conservadores;
# a prova de que os outros alto-falantes matam usa o jogador perfeito.
CELULA = 4
# Na solução, os anjos que acabam de pousar ficam a 28 px do caminho (folga que se
# vê na tela); em voo, a 20; os que já estavam parados, a 18.
CONSERVADOR = dict(vel=48.0, raio=28.0, raio_voo=20.0, raio_parados=18.0, alvo=9)
PERFEITO = dict(vel=VEL_ICARO, raio=RAIO_PEGA, raio_voo=RAIO_PEGA, raio_parados=RAIO_PEGA, alvo=RAIO_AREA)


@dataclass
class Falante:
    nome: str
    x: int
    y: int
    nota: int                      # 0 Dó, 1 Ré, 2 Mi, 3 Sol


@dataclass
class Ponto:
    ini: tuple
    fim: tuple
    bpm: int
    poleiros: list                 # (x, y) num cabeço; (x, y, "chao") agachado nas tábuas;
                                   # (x, y, z) em cima de algo (contêiner: z 40)
    agente: tuple
    folga: float = 1.4             # s além do caminho mais curto
    falantes: list = field(default_factory=list)   # escolhidos por escolher_falantes()
    solucao: str = ""


@dataclass
class Trecho:
    nome: str                      # rótulo no roteiro e prefixo dos dados
    andar: int
    titulo: str
    ambiente: int
    mapa: list
    comodos: list
    objetos: list
    luzes: list
    falantes: list
    pontos: list
    chegada: tuple                 # Ícaro ao entrar: x, y, direção da sprite
    agente: tuple
    intro: str


# ------------------------------------------------------------------ trechos

DOCA = Trecho(
    nome="doca", andar=3, titulo="DOCA", ambiente=0xff40281c,
    mapa=[
        "XXXXPPXXXXXXXXXXXXXXXX",    #  0  fundos do galpão
        "#QQQQQQQQQQQQQQQQQQQQ#",    #  1  cais
        "#QQQQQQQQQQQQQQQQQQQQ#",
        "#QQQQQQQQQQQQQQQQQQQQ#",
        "#QQQQQQQQQQQQQQQQQQQQ#",
        "#~TT~~~~~TTTT~~~~QQQQ#",    #  5  píer oeste | píer | cais leste
        "#~TT~~~~~TTTT~~~~QQQQ#",
        "#~TT~~~~~TTTT~~~~QQQQ#",
        "#~TT~~~~~TTTT~~~~QQQQ#",
        "#~TTTTTTTTTTTTTTTQQQQ#",    #  9  passarela de ponta a ponta
        "#~TTTTTTTTTTTTTTTQQQQ#",
        "#~TT~~~~~TTTT~~~~QQQQ#",
        "#~TT~~~~~TTTT~~~~QQQQ#",
        "#~~~~~~~~TTTT~~~~QQQQ#",
        "#~~~~~~~~~~~~~~~~QQQQ#",
        "#~~~~~~~~~~~~~~~~QQQQ#",
        "#~~~~~~~~~~~~~~~~QQQQ#",
        "#~~~~~~~~~~~~~~~~QQQQ#",
        "#~~~~~~~~~~~~~~~~QQQQ#",
        "#~~~~~~~~~~~~~~~~QQQQ#",
        "#~~~~~~~~~~~~~~~~QQQQ#",
        "##################PP##",    # 21  portão do porto
    ],
    comodos=[(1, 1, 20, 4, "CAIS"), (9, 5, 12, 13, "PÍER"), (1, 9, 16, 10, "PASSARELA"),
             (17, 5, 20, 20, "CAIS LESTE"), (2, 5, 3, 12, "PÍER OESTE")],
    objetos=[
        ("MOVEL4", "CONTAINER_VERMELHO", 272, 20),
        ("MOVEL4", "CONTAINER_AZUL", 224, 52),
        ("MOVEL", "POSTE", 128, 72), ("MOVEL", "POSTE", 212, 132), ("MOVEL", "POSTE", 278, 198),
        ("MOVEL", "POSTE", 54, 130),
        ("MOVEL4", "CONTAINER_VERDE", 308, 200),
        ("MOVEL2", "CAIXAS_PILHA", 272, 290),
        ("BLOQUEIO", 288, 336, 32, 16),
    ],
    luzes=[
        (80, 22, 30, 70, 230, 178, 110, "OS_FIXA"),
        (132, 74, 56, 100, 255, 170, 90, "OS_FIXA"),
        (216, 134, 56, 100, 255, 170, 90, "OS_FALHA"),
        (282, 202, 56, 100, 255, 170, 90, "OS_FIXA"),
        (58, 132, 56, 90, 255, 170, 90, "OS_ROTEIRO"),
        (304, 330, 30, 80, 220, 120, 90, "OS_FIXA"),
    ],
    falantes=[
        Falante("cais_no", 28, 28, 0),
        Falante("cais_meio", 176, 22, 1),
        Falante("cais_ne", 252, 30, 2),
        Falante("pier_leste", 202, 104, 3),
        Falante("leste_norte", 322, 96, 0),
        Falante("ponta_pier", 202, 218, 2),
        Falante("leste_meio", 322, 180, 1),
        Falante("leste_sul", 324, 322, 3),
    ],
    pontos=[
        # O píer oeste é o único caminho: tire os anjos de cima dele.
        Ponto(ini=(64, 36), fim=(48, 188), bpm=80, folga=1.6,
              poleiros=[(48, 100, "chao"), (48, 116, "chao"), (56, 84, "chao")], agente=(48, 200)),
        # Cercado: um grupo na passarela, outro nos cabeços ao sul.
        Ponto(ini=(48, 188), fim=(176, 200), bpm=84, folga=1.4,
              poleiros=[(88, 160, "chao"), (104, 156, "chao"), (24, 216), (72, 216)], agente=(192, 206)),
        # Passarela e corredor do cais leste ocupados; mais dois a oeste.
        Ponto(ini=(176, 200), fim=(312, 318), bpm=90, folga=1.3,
              poleiros=[(232, 160, "chao"), (288, 240, "chao"), (128, 204)], agente=(300, 326)),
    ],
    chegada=(64, 32, 4), agente=(48, 38),
    intro=("Os anjos voam em linha reta até o som e pousam em volta dele.\\n"
           "Chegar perto de qualquer anjo, voando, pousado ou escutando, é morte."),
)


def blocos_conteineres():
    """3 x 3 blocos de dois contêineres empilhados; o do centro fica vazio (praça)."""
    obs = []
    cores = ["CONTAINER_VERMELHO", "CONTAINER_AZUL"]
    k = 0
    for by in (48, 136, 224):
        for bx in (48, 144, 240):
            if (bx, by) == (144, 136):
                continue
            obs.append(("MOVEL4", cores[k % 2], bx, by))
            obs.append(("MOVEL4", cores[(k + 1) % 2], bx, by + 28))
            k += 1
    return obs


PATIO = Trecho(
    nome="patio", andar=4, titulo="PÁTIO DE CONTÊINERES", ambiente=0xff3a2a22,
    mapa=["######################"] + ["#QQQQQQQQQQQQQQQQQQQQ#"] * 20 + ["#################PP###"],
    comodos=[(1, 1, 20, 20, "CONTÊINERES")],
    objetos=blocos_conteineres() + [
        ("MOVEL4", "CONTAINER_VERDE", 18, 50),        # fecha o corredor oeste no alto
        ("MOVEL4", "CONTAINER_AZUL", 144, 18),        # fecha o corredor de cima no meio
        ("MOVEL4", "CONTAINER_VERDE", 306, 226),      # fecha o corredor leste embaixo
        ("BLOQUEIO", 272, 336, 32, 16),
    ],
    luzes=[
        (32, 32, 50, 110, 255, 170, 90, "OS_FIXA"),
        (176, 160, 60, 130, 255, 170, 90, "OS_FALHA"),
        (320, 32, 50, 100, 255, 170, 90, "OS_FIXA"),
        (32, 300, 50, 100, 255, 170, 90, "OS_FIXA"),
        (300, 300, 50, 110, 255, 170, 90, "OS_ROTEIRO"),
        (128, 120, 40, 80, 150, 180, 255, "OS_FIXA"),
    ],
    falantes=[
        Falante("p_no", 22, 22, 0),
        Falante("p_ne", 330, 22, 1),
        Falante("p_praca", 176, 164, 2),
        Falante("p_so", 22, 330, 3),
        Falante("p_norte", 176, 22, 3),
        Falante("p_oeste", 22, 176, 1),
        Falante("p_leste", 330, 112, 0),
        Falante("p_sul", 176, 330, 2),
    ],
    pontos=[
        Ponto(ini=(32, 32), fim=(128, 120), bpm=92, folga=1.3,
              poleiros=[(80, 32, "chao"), (128, 76, "chao"), (80, 76, 40), (32, 84, 40)], agente=(120, 128)),
        Ponto(ini=(128, 120), fim=(224, 32), bpm=96, folga=1.2,
              poleiros=[(176, 120, "chao"), (224, 76, "chao"), (80, 160, 40), (176, 76, 40)], agente=(232, 26)),
        Ponto(ini=(224, 32), fim=(224, 208), bpm=100, folga=1.2,
              poleiros=[(224, 164, "chao"), (284, 32, "chao"), (176, 32, 40)], agente=(214, 214)),
        Ponto(ini=(224, 208), fim=(320, 316), bpm=104, folga=1.1,
              poleiros=[(224, 256, "chao"), (272, 308, "chao"), (176, 250, 40), (272, 250, 40)], agente=(330, 312)),
    ],
    chegada=(32, 28, 4), agente=(24, 40),
    intro=("Pátio de contêineres. Corredores estreitos: um anjo pousado fecha um corredor inteiro.\\n"
           "Os que já pousaram continuam lá."),
)

QUEBRAMAR = Trecho(
    nome="quebramar", andar=5, titulo="QUEBRA-MAR", ambiente=0xff4a3020,
    mapa=[
        "######################",
        "#TTTT~~~~~~~~~~~~~~~~#",
        "#TTTT~~~~~~~~~~~~~~~~#",
        "#TTTTTTTTTTTTTTTTT~~~#",
        "#~~TT~~~~~~~~~~TTT~~~#",
        "#~~TT~~~~~~~~~~~TT~~~#",
        "#~~TT~~~~~~~~~~~TT~~~#",
        "#~~TTTTTTTTTTTTTTTTT~#",
        "#~~~~~~~~~~TT~~~~~TT~#",
        "#~~~~~~~~~~TT~~~~~TT~#",
        "#~~~~~~~~~~TT~~~~~TT~#",
        "#~TTTTTTTTTTTTT~~~TT~#",
        "#~TT~~~~~~~~~TT~~~TT~#",
        "#~TT~~~~~~~~~TT~~~TT~#",
        "#~TT~~~~~~~~~TTTTTTT~#",
        "#~TT~~~~~~~~~~~~~~~~~#",
        "#~TTTTTTTTTTTTTTTTT~~#",
        "#~~~~~~~~~~~~~~~~TT~~#",
        "#~~~~~~~~~~~~~~~~TT~~#",
        "#~~~~~~~~~~~~~QQQQQQ~#",
        "#~~~~~~~~~~~~~QQQQQQ~#",
        "######################",
    ],
    comodos=[(1, 1, 20, 18, "QUEBRA-MAR"), (14, 19, 19, 20, "FAROL")],
    objetos=[
        # postes em estacas na água, ao lado das tábuas (em cima delas fechariam a passagem)
        ("MOVEL", "POSTE", 100, 68), ("MOVEL", "POSTE", 200, 100), ("MOVEL", "POSTE", 120, 196),
        ("MOVEL", "POSTE", 248, 244), ("MOVEL", "POSTE", 150, 276), ("MOVEL", "POSTE", 300, 300),
    ],
    luzes=[
        (100, 70, 56, 100, 255, 170, 90, "OS_FIXA"),
        (200, 104, 56, 100, 255, 170, 90, "OS_FALHA"),
        (120, 200, 56, 100, 255, 170, 90, "OS_FIXA"),
        (250, 248, 56, 100, 255, 170, 90, "OS_FIXA"),
        (150, 280, 56, 100, 255, 170, 90, "OS_ROTEIRO"),
        (272, 316, 70, 140, 255, 240, 200, "OS_CHAMA"),
    ],
    falantes=[
        Falante("q_no", 20, 20, 0),
        Falante("q_norte", 200, 40, 1),
        Falante("q_ne", 296, 60, 2),
        Falante("q_meio", 120, 140, 3),
        Falante("q_leste", 328, 140, 0),
        Falante("q_oeste", 20, 200, 2),
        Falante("q_sul", 120, 296, 1),
        Falante("q_farol", 330, 300, 3),
    ],
    pontos=[
        Ponto(ini=(40, 40), fim=(192, 120), bpm=108, folga=1.2,
              poleiros=[(64, 92, "chao"), (128, 120, "chao"), (120, 56, "chao"), (24, 84)], agente=(204, 112)),
        Ponto(ini=(192, 120), fim=(48, 232), bpm=112, folga=1.1,
              poleiros=[(192, 152, "chao"), (120, 184, "chao"), (248, 120, "chao"), (192, 96)],
              agente=(40, 244)),
        Ponto(ini=(48, 232), fim=(272, 320), bpm=116, folga=1.0,
              poleiros=[(160, 264, "chao"), (288, 288, "chao"), (88, 204), (20, 240)], agente=(290, 314)),
    ],
    chegada=(40, 36, 4), agente=(24, 48),
    intro=("Quebra-mar. Tábuas de uma passada só: não há para onde desviar.\\n"
           "O farol é a saída."),
)

TRECHOS = [DOCA, PATIO, QUEBRAMAR]



# --------------------------------------------------------- medidas e colisão

def medidas_tileset():
    m = {}
    for linha in (RAIZ / "tileset.inc").read_text().splitlines():
        r = re.match(r"\.equ S_(\w+)_(OX|OY|W|D), (-?\d+)", linha)
        if r:
            m.setdefault(r.group(1), {})[r.group(2)] = int(r.group(3))
    return m


def pedacos(macro, nome):
    n = {"MOVEL": 1, "MOVEL2": 2, "MOVEL3": 3, "MOVEL4": 4}[macro]
    return [nome] if n == 1 else [f"{nome}_{k}" for k in range(n)]


def retangulos_colisao(trecho, S):
    """Como PEDACO em cenario.inc: (x+OX+1, y+OY+1, W-2, D-2) por pedaço."""
    rets = []
    for ob in objetos_completos(trecho):
        if ob[0] == "BLOQUEIO":
            rets.append(tuple(ob[1:5]))
            continue
        macro, nome, x, y = ob
        for p in pedacos(macro, nome):
            s = S[p]
            rets.append((x + s["OX"] + 1, y + s["OY"] + 1, s["W"] - 2, s["D"] - 2))
    return rets


def objetos_completos(trecho):
    """Cenário do trecho + um alto-falante por falante + um cabeço por poleiro."""
    obs = list(trecho.objetos)
    for f in trecho.falantes:
        obs.append(("MOVEL", "ALTO_FALANTE", f.x - 3, f.y - 4))
    vistos = set()
    for p in trecho.pontos:
        for pol in p.poleiros:
            if len(pol) == 2 and pol not in vistos:
                vistos.add(pol)
                obs.append(("MOVEL", "CABECO", pol[0] - 4, pol[1] - 4))
    return obs


def z_poleiro(pol):
    if len(pol) == 2:
        return Z_POLEIRO
    return 0 if pol[2] == "chao" else pol[2]


def mapa_solido(trecho, S):
    """solido[y, x] por px, como ponto_solido."""
    sol = np.ones((LADO, LADO), bool)
    for ty, linha in enumerate(trecho.mapa):
        assert len(linha) == N, (trecho.nome, ty, linha)
        for tx, c in enumerate(linha):
            if c in PISO:
                sol[ty * TILE:(ty + 1) * TILE, tx * TILE:(tx + 1) * TILE] = False
    for (x, y, l, a) in retangulos_colisao(trecho, S):
        sol[max(0, y):max(0, y + a), max(0, x):max(0, x + l)] = True
    return sol


def grade_andavel(sol):
    """andavel[j, i]: Ícaro com os pés no centro da célula (como pode_andar)."""
    nc = LADO // CELULA
    c = np.arange(nc) * CELULA + CELULA // 2
    X, Y = np.meshgrid(c, c)
    ok = np.ones((nc, nc), bool)
    # 1 px de margem além do pé do motor: o caminho nunca passa rente a uma quina
    m = 1
    for dx in range(-PE_LADO - m, PE_LADO + m + 1):
        for dy in (-PE_CIMA - m, PE_BAIXO + m):
            ok &= ~sol[np.clip(Y + dy, 0, LADO - 1), np.clip(X + dx, 0, LADO - 1)]
    for dy in range(-PE_CIMA - m, PE_BAIXO + m + 1):
        for dx in (-PE_LADO - m, PE_LADO + m):
            ok &= ~sol[np.clip(Y + dy, 0, LADO - 1), np.clip(X + dx, 0, LADO - 1)]
    return ok, X, Y


# ------------------------------------------------------------- anjos

def pousos(falante, n):
    """Onde cada anjo pousa em volta do alto-falante (doca.s, atrair)."""
    return [(falante.x + 12 * i - 12, falante.y + 4 + 8 * (i & 1)) for i in range(n)]


def trajetorias(poleiros, falante):
    """Funções t -> (x, y) de cada anjo do ponto voando até o falante."""
    fns = []
    for pol, (qx, qy) in zip(poleiros, pousos(falante, len(poleiros))):
        px, py = pol[0], pol[1]
        dz = (Z_CORNETA + 4) - z_poleiro(pol)
        dist = math.sqrt((qx - px) ** 2 + (qy - py) ** 2 + dz ** 2)
        dur = dist / VEL_ANJO

        def f(t, px=px, py=py, qx=qx, qy=qy, dur=dur):
            a = min(1.0, t / dur) if dur > 0 else 1.0
            return px + (qx - px) * a, py + (qy - py) * a, a >= 1.0
        fns.append(f)
    return fns


# -------------------------------------------------------------- solucionador

def resolver(andavel, X, Y, ini, fim, parados, voando, janela, vel, raio, raio_voo, raio_parados, alvo,
             caminho=False):
    """Busca em largura no espaço-tempo. -> (tempo de chegada ou None, caminho)."""
    dt = CELULA / vel
    passos = int(janela / dt) + 1
    nc = andavel.shape[0]

    fixo = np.zeros_like(andavel)
    for (ax, ay) in parados:
        fixo |= (X - ax) ** 2 + (Y - ay) ** 2 < raio_parados * raio_parados

    def perigo(t):
        p = fixo.copy()
        for f in voando:
            ax, ay, pousou = f(t)
            r = raio if pousou else raio_voo
            p |= (X - ax) ** 2 + (Y - ay) ** 2 < r * r
        return p

    meta = (np.abs(X - fim[0]) <= alvo) & (np.abs(Y - fim[1]) <= alvo)
    i0, j0 = int(ini[0] // CELULA), int(ini[1] // CELULA)
    alcance = np.zeros_like(andavel)
    alcance[j0, i0] = True
    alcance &= ~perigo(0.0)
    camadas = [alcance.copy()]
    for k in range(1, passos + 1):
        if not alcance.any():
            return None, []
        viz = alcance.copy()
        viz[1:, :] |= alcance[:-1, :]
        viz[:-1, :] |= alcance[1:, :]
        viz[:, 1:] |= alcance[:, :-1]
        viz[:, :-1] |= alcance[:, 1:]
        alcance = viz & andavel & ~perigo(k * dt)
        camadas.append(alcance.copy())
        if (alcance & meta).any():
            if not caminho:
                return k * dt, []
            # volta pelo caminho, camada a camada
            js, is_ = np.nonzero(alcance & meta)
            j, i = js[0], is_[0]
            rota = [(k, i, j)]
            for kk in range(k - 1, -1, -1):
                for dj, di in ((0, 0), (-1, 0), (1, 0), (0, -1), (0, 1)):
                    jj, ii = j + dj, i + di
                    if 0 <= jj < nc and 0 <= ii < nc and camadas[kk][jj, ii]:
                        j, i = jj, ii
                        break
                rota.append((kk, i, j))
            rota.reverse()
            return k * dt, [(kk * dt, int(X[j, i]), int(Y[j, i])) for (kk, i, j) in rota]
    return None, []


def verificar(trecho, S):
    """Resolve os pontos em sequência; devolve janelas e caminhos (para o robô)."""
    sol = mapa_solido(trecho, S)
    andavel, X, Y = grade_andavel(sol)
    falantes = {f.nome: f for f in trecho.falantes}
    pousados = []                                  # anjos que ficaram de pontos anteriores
    resultados = []
    erros = []
    for k, p in enumerate(trecho.pontos):
        notas = [falantes[n].nota for n in p.falantes]
        if len(set(notas)) != len(notas):
            erros.append(f"{trecho.nome} ponto {k + 1}: dois alto-falantes com a mesma nota")
        futuros = [pol[:2] for q in trecho.pontos[k + 1:] for pol in q.poleiros]
        parados = pousados + futuros
        sol_f = falantes[p.solucao]
        t, rota = resolver(andavel, X, Y, p.ini, p.fim, parados, trajetorias(p.poleiros, sol_f),
                           12.0, caminho=True, **CONSERVADOR)
        linha = f"{trecho.nome} ponto {k + 1}: solução {p.solucao}"
        if t is None:
            erros.append(linha + " NÃO tem caminho")
            resultados.append(None)
            pousados += pousos(sol_f, len(p.poleiros))
            continue
        janela = round(t + p.folga, 1)
        tp, _ = resolver(andavel, X, Y, p.ini, p.fim, parados, trajetorias(p.poleiros, sol_f),
                         janela, **PERFEITO)
        linha += f" em {t:.1f}s (perfeito {tp:.1f}s), janela {janela:.1f}s"
        for nome in p.falantes:
            if nome == p.solucao:
                continue
            te, _ = resolver(andavel, X, Y, p.ini, p.fim, parados, trajetorias(p.poleiros, falantes[nome]),
                             janela, **PERFEITO)
            linha += f"; {nome}: " + ("morte" if te is None else f"PASSA em {te:.1f}s")
            if te is not None:
                erros.append(f"{trecho.nome} ponto {k + 1}: {nome} também passa")
        print(linha)
        resultados.append(dict(janela=janela, rota=rota, falante=sol_f))
        pousados += pousos(sol_f, len(p.poleiros))
    return resultados, erros, (sol, andavel)


# --------------------------------------------------- escolha dos alto-falantes

def dist_segmento(px, py, a, b):
    ax, ay = a
    bx, by = b
    vx, vy = bx - ax, by - ay
    t = max(0.0, min(1.0, ((px - ax) * vx + (py - ay) * vy) / max(1e-9, vx * vx + vy * vy)))
    return math.hypot(px - (ax + t * vx), py - (ay + t * vy))


def candidatos_falante(trecho, sol):
    """Lugares para um alto-falante sem fechar passagem: estacas na água junto às
    tábuas, ou chão encostado em parede, contêiner ou beira d'água."""
    livres = []
    for y in range(12, LADO - 12, 8):
        for x in range(12, LADO - 12, 8):
            c = trecho.mapa[y // TILE][x // TILE]
            perto_chao = (~sol[max(0, y - 18):y + 19, max(0, x - 18):x + 19]).any()
            perto_solido = sol[max(0, y - 10):y + 11, max(0, x - 10):x + 11].any()
            if c == "~" and perto_chao:
                livres.append((x, y))
            elif c in PISO and perto_solido and not sol[y - 5:y + 6, x - 5:x + 6].any():
                livres.append((x, y))
    return livres


def conectado(andavel, a, b):
    """Há caminho (sem contar anjos) de a até b?"""
    r = np.zeros_like(andavel)
    r[a[1] // CELULA, a[0] // CELULA] = True
    r &= andavel
    alvo = (b[1] // CELULA, b[0] // CELULA)
    while True:
        if r[alvo]:
            return True
        v = r.copy()
        v[1:] |= r[:-1]
        v[:-1] |= r[1:]
        v[:, 1:] |= r[:, :-1]
        v[:, :-1] |= r[:, 1:]
        v &= andavel
        if (v == r).all():
            return False
        r = v


def tapa_passagem(trecho, S, k, x, y):
    """Um alto-falante em (x, y) fecharia algum caminho deste ponto ou dos seguintes?"""
    trecho.falantes.append(Falante("?", x, y, 0))
    andavel, _, _ = grade_andavel(mapa_solido(trecho, S))
    trecho.falantes.pop()
    return any(not conectado(andavel, q.ini, q.fim) for q in trecho.pontos[k:])


def posicionar_falantes(trecho, S, nomes_notas=("Dó", "Ré", "Mi", "Sol")):
    """Para cada ponto, escolhe onde ficam seus alto-falantes. A solução é um lugar
    que funciona e exige mais espera ou desvio; as armadilhas, até 3 lugares que
    matam, os mais longe da rota (os que parecem seguros)."""
    trecho.falantes = []
    sol = mapa_solido(trecho, S)
    cands = candidatos_falante(trecho, sol)
    pousados, usados = [], []
    for k, p in enumerate(trecho.pontos):
        # os alto-falantes já postos também são obstáculo
        sol = mapa_solido(trecho, S)
        andavel, X, Y = grade_andavel(sol)
        futuros = [pol[:2] for q in trecho.pontos[k + 1:] for pol in q.poleiros]
        parados = pousados + futuros
        t_livre, _ = resolver(andavel, X, Y, p.ini, p.fim, parados, [], 15.0, **CONSERVADOR)
        if t_livre is None:
            raise SystemExit(f"{trecho.nome} ponto {k + 1}: sem caminho nem sem os anjos do ponto")

        def ok_lugar(x, y, longe=40):
            if min(math.hypot(x - a, y - b) for (a, b) in (p.ini, p.fim)) < 30:
                return False
            if any(math.hypot(x - a, y - b) < 24 for (a, b) in [pol[:2] for pol in p.poleiros] + parados):
                return False
            return all(math.hypot(x - a, y - b) >= longe for (a, b) in usados)
        lugares = [(x, y) for (x, y) in cands if ok_lugar(x, y)]
        tapam = {}

        def livre(x, y):
            if (x, y) not in tapam:
                tapam[(x, y)] = tapa_passagem(trecho, S, k, x, y)
            return not tapam[(x, y)]
        bons = []
        for (x, y) in lugares:
            tc, _ = resolver(andavel, X, Y, p.ini, p.fim, parados, trajetorias(p.poleiros, Falante("?", x, y, 0)),
                             t_livre + 3.0, **CONSERVADOR)
            if tc is not None:
                # espera em degraus de meio segundo; empatado, o mais perto da rota
                bons.append((math.floor((tc - t_livre) * 2) / 2, -dist_segmento(x, y, p.ini, p.fim), x, y, tc))
        if not bons:
            raise SystemExit(f"{trecho.nome} ponto {k + 1}: nenhum lugar funciona")
        bons.sort(reverse=True)
        # os pousos da solução não podem fechar nenhum ponto seguinte do trecho
        escolha = None
        for cand in bons:
            if not livre(cand[2], cand[3]):
                continue
            novos = pousos(Falante("?", cand[2], cand[3], 0), len(p.poleiros))
            fecha = False
            for jj in range(k + 1, len(trecho.pontos)):
                q = trecho.pontos[jj]
                depois = [pol[:2] for r in trecho.pontos[jj + 1:] for pol in r.poleiros]
                tq, _ = resolver(andavel, X, Y, q.ini, q.fim, pousados + novos + depois, [], 15.0, **CONSERVADOR)
                if tq is None:
                    fecha = True
                    break
            if not fecha:
                escolha = cand
                break
        if escolha is None:
            raise SystemExit(f"{trecho.nome} ponto {k + 1}: toda solução fecha um ponto seguinte")
        espera, _, gx, gy, tc = escolha
        janela = round(tc + p.folga, 1)
        ruins = []
        for (x, y) in sorted(lugares, key=lambda c: -dist_segmento(c[0], c[1], p.ini, p.fim)):
            if math.hypot(x - gx, y - gy) < 48 or any(math.hypot(x - a, y - b) < 48 for (a, b) in ruins):
                continue
            tp, _ = resolver(andavel, X, Y, p.ini, p.fim, parados, trajetorias(p.poleiros, Falante("?", x, y, 0)),
                             janela, **PERFEITO)
            if tp is None and livre(x, y):
                ruins.append((x, y))
            if len(ruins) == 3:
                break
        if not ruins:
            raise SystemExit(f"{trecho.nome} ponto {k + 1}: nenhuma armadilha possível")
        nota0 = (k * 3 + trecho.andar) % 4
        notas = [nota0] + [n for n in range(4) if n != nota0]
        p.falantes = []
        for i, (x, y) in enumerate([(gx, gy)] + ruins):
            f = Falante(f"{trecho.nome}{k + 1}_{'sol' if i == 0 else 'arm' + str(i)}", x, y, notas[i])
            trecho.falantes.append(f)
            p.falantes.append(f.nome)
            usados.append((x, y))
        p.solucao = p.falantes[0]
        print(f"{trecho.nome} ponto {k + 1}: solução em ({gx},{gy}) {nomes_notas[nota0]}, "
              f"espera {espera:.1f}s, armadilhas {ruins}")
        pousados += pousos(trecho.falantes[-len(p.falantes)], len(p.poleiros))


# ---------------------------------------------------------------- mapa visto de cima

def desenhar_mapa(trecho, S, resultados, sol, caminho_png):
    from PIL import Image, ImageDraw
    esc = 3
    im = Image.new("RGB", (LADO * esc, LADO * esc), (20, 30, 50))
    px = im.load()
    for y in range(LADO):
        for x in range(LADO):
            if not sol[y, x]:
                for a in range(esc):
                    for b in range(esc):
                        px[x * esc + a, y * esc + b] = (90, 88, 80)
    d = ImageDraw.Draw(im)
    for (x, y, l, a) in retangulos_colisao(trecho, S):
        d.rectangle((x * esc, y * esc, (x + l) * esc, (y + a) * esc), outline=(160, 120, 80))
    falantes = {f.nome: f for f in trecho.falantes}
    cores = [(255, 90, 90), (240, 190, 60), (90, 210, 130), (100, 160, 250)]
    for f in trecho.falantes:
        d.ellipse(((f.x - 5) * esc, (f.y - 5) * esc, (f.x + 5) * esc, (f.y + 5) * esc), fill=cores[f.nota])
        d.text(((f.x + 6) * esc, (f.y - 4) * esc), f.nome, fill=(255, 255, 255))
    for k, p in enumerate(trecho.pontos):
        for pol in p.poleiros:
            x, y = pol[0], pol[1]
            d.ellipse(((x - 4) * esc, (y - 4) * esc, (x + 4) * esc, (y + 4) * esc), outline=(230, 230, 255))
            d.text(((x - 3) * esc, (y - 14) * esc), str(k + 1), fill=(230, 230, 255))
            alvo = falantes[p.solucao]
            d.line((x * esc, y * esc, alvo.x * esc, alvo.y * esc), fill=(200, 200, 255), width=1)
        for (cx, cy), cor in ((p.ini, (80, 255, 160)), (p.fim, (80, 255, 160))):
            d.rectangle(((cx - RAIO_AREA) * esc, (cy - RAIO_AREA) * esc, (cx + RAIO_AREA) * esc,
                         (cy + RAIO_AREA) * esc), outline=cor)
        r = resultados[k]
        if r:
            pts = [(x * esc, y * esc) for (_, x, y) in r["rota"]]
            d.line(pts, fill=(255, 255, 0), width=2)
            d.text((p.fim[0] * esc + 20, p.fim[1] * esc), f"P{k + 1}", fill=(255, 255, 0))
    caminho_png.parent.mkdir(parents=True, exist_ok=True)
    im.save(caminho_png)


# --------------------------------------------- exploração (ajuda a desenhar fases)

def explorar(trecho, S, k, caminho_png, janela=8.0):
    """Mapa de calor do ponto k: para um alto-falante hipotético em cada lugar livre,
    o tempo do jogador perfeito (verde rápido, amarelo lento) ou morte (vermelho)."""
    from PIL import Image, ImageDraw
    sol = mapa_solido(trecho, S)
    andavel, X, Y = grade_andavel(sol)
    falantes = {f.nome: f for f in trecho.falantes}
    pousados = []
    for q in trecho.pontos[:k]:
        pousados += pousos(falantes[q.solucao], len(q.poleiros))
    p = trecho.pontos[k]
    futuros = [pol[:2] for q in trecho.pontos[k + 1:] for pol in q.poleiros]
    t_livre, _ = resolver(andavel, X, Y, p.ini, p.fim, pousados + futuros, [], janela, **PERFEITO)
    esc = 2
    im = Image.new("RGB", (LADO * esc, LADO * esc), (20, 30, 50))
    d = ImageDraw.Draw(im)
    for y in range(0, LADO, 8):
        for x in range(0, LADO, 8):
            if sol[y, x]:
                continue
            t, _ = resolver(andavel, X, Y, p.ini, p.fim, pousados + futuros,
                            trajetorias(p.poleiros, Falante("?", x, y, 0)), janela, **PERFEITO)
            if t is None:
                c = (170, 40, 40)
            else:
                a = min(1.0, max(0.0, (t - (t_livre or t)) / 2.0))
                c = (int(60 + 180 * a), int(200 - 40 * a), 60)
            d.rectangle((x * esc, y * esc, (x + 8) * esc - 1, (y + 8) * esc - 1), fill=c)
    for pol in p.poleiros:
        x, y = pol[0], pol[1]
        d.ellipse(((x - 4) * esc, (y - 4) * esc, (x + 4) * esc, (y + 4) * esc), outline=(255, 255, 255), width=2)
    for (x, y) in pousados + futuros:
        d.ellipse(((x - 16) * esc, (y - 16) * esc, (x + 16) * esc, (y + 16) * esc), outline=(140, 140, 255))
    for (cx, cy) in (p.ini, p.fim):
        d.rectangle(((cx - RAIO_AREA) * esc, (cy - RAIO_AREA) * esc, (cx + RAIO_AREA) * esc,
                     (cy + RAIO_AREA) * esc), outline=(80, 255, 160), width=2)
    d.text((6, 6), f"{trecho.nome} ponto {k + 1}: sem anjos {t_livre}", fill=(255, 255, 255))
    im.save(caminho_png)


# ------------------------------------------------------------- saída em assembly

OBJETIVOS = {"doca": "Atravesse a doca", "patio": "Atravesse o pátio", "quebramar": "Chegue ao farol"}


def gerar_dados(trechos):
    L = ["# Gerado por ferramentas/gerar_doca.py. Não editar à mão.",
         "# Os três trechos da fuga: plantas, móveis, luzes, alto-falantes, poleiros e pontos.", ""]
    indice_falante = 0
    for tr in trechos:
        n = tr.nome
        L += [f"# ---------------------------------------------------------------- {tr.titulo}",
              ".section .rodata", f"nome_{n}: .asciz \"{tr.titulo}\""]
        for i, c in enumerate(tr.comodos):
            L.append(f"nome_{n}_c{i}: .asciz \"{c[4]}\"")
        L.append(f"mapa_{n}:")
        L += [f'    LINHA "{linha}"' for linha in tr.mapa]
        L += [".align 8", f"comodos_{n}:"]
        L += [f"    COMODO {c[0]}, {c[1]}, {c[2]}, {c[3]}, nome_{n}_c{i}" for i, c in enumerate(tr.comodos)]
        L += [f"comodos_{n}_fim:", f"transicoes_{n}:", f"transicoes_{n}_fim:", f"decalques_{n}:",
              f"decalques_{n}_fim:", f"luzes_{n}:"]
        L += [f"    LUZ {x}, {y}, {z}, {r}, {cr}, {cg}, {cb}, {osc}" for (x, y, z, r, cr, cg, cb, osc) in tr.luzes]
        L += [f"luzes_{n}_fim:", "", ".section .data", ".align 8", f"objetos_{n}:"]
        for ob in objetos_completos(tr):
            if ob[0] == "BLOQUEIO":
                L.append(f"    BLOQUEIO {ob[1]}, {ob[2]}, {ob[3]}, {ob[4]}")
            else:
                L.append(f"    {ob[0]} {ob[1]}, {ob[2]}, {ob[3]}")
        L += [f"objetos_{n}_fim:", "", ".section .bss", ".align 16", f"itens_{n}: .skip MAX_ITENS * IT_TAM", "",
              ".section .data", ".align 8", f"andar_{n}:",
              f"    .quad mapa_{n}",
              f"    .quad objetos_{n}, (objetos_{n}_fim - objetos_{n}) / OBJ_TAM",
              f"    .quad luzes_{n}, (luzes_{n}_fim - luzes_{n}) / LUZ_TAM",
              f"    .quad comodos_{n}, (comodos_{n}_fim - comodos_{n}) / COM_TAM",
              f"    .quad transicoes_{n}, 0",
              f"    .quad nome_{n}",
              f"    .quad 0x{tr.ambiente:08x}",
              f"    .quad decalques_{n}, 0",
              f"    .quad itens_{n}, 0",
              "    .quad 0, 0", ""]
    # alto-falantes de todos os trechos, na ordem dos pontos (os de um ponto são vizinhos)
    L += [".section .data", ".global alto_falantes", ".align 4",
          "# x, y (centro, mundo), altura da corneta, nota (0..3).", "alto_falantes:"]
    for tr in trechos:
        for f in tr.falantes:
            L.append(f"    .long {f.x}, {f.y}, {Z_CORNETA}, {f.nota}    # {f.nome}")
    L.append("")
    for tr in trechos:
        anjo = 0
        falantes = {f.nome: i for i, f in enumerate(tr.falantes)}
        for k, p in enumerate(tr.pontos):
            L.append(f"poleiros_{tr.nome}_{k + 1}: .long " +
                     ",  ".join(f"{pol[0]}, {pol[1]}, {z_poleiro(pol)}" for pol in p.poleiros))
            p._anjo0 = anjo
            anjo += len(p.poleiros)
            p._falante0 = indice_falante + falantes[p.falantes[0]]
        indice_falante += len(tr.falantes)
        assert anjo <= 16, f"{tr.nome}: {anjo} anjos (máximo 16)"
    L += ["", ".align 8"]
    for tr in trechos:
        for k, p in enumerate(tr.pontos):
            L += [f"ponto_{tr.nome}_{k + 1}:",
                  f"    .long {p.ini[0]}, {p.ini[1]}, {p.fim[0]}, {p.fim[1]}, {p.bpm}, {int(round(p._janela * 1000))}",
                  f"    .long {p._falante0}, {len(p.falantes)}, ATOR_ANJO + {p._anjo0}, {len(p.poleiros)}",
                  f"    .quad poleiros_{tr.nome}_{k + 1}",
                  f"    .long {p.agente[0]}, {p.agente[1]}, 0, 0"]
    # arrumação de cada trecho: anjos nos poleiros e clima (roteiro, chamada com OP_CHAMA)
    L += ["", ".section .rodata", ".align 8"]
    for tr in trechos:
        L.append(f"prepara_{tr.nome}:")
        L.append("    ESCONDE ATOR_MAEL")
        L += [f"    ESCONDE ATOR_ANJO + {i}" for i in range(16)]
        i = 0
        for p in tr.pontos:
            for pol in p.poleiros:
                L.append(f"    FIXO ATOR_ANJO + {i}, {tr.andar}, {pol[0]}, {pol[1]}, {z_poleiro(pol)}, ANJO_POUSADO, AF_HD")
                i += 1
        L += ["    CMD OP_MUSICA, 0", "    CMD OP_ZUMBIDO, 70", "    CMD OP_NEVOA, 45", "    CMD OP_PERTURBA, 1",
              "    CMD OP_INTERACOES", f"    OBJETIVO \"{OBJETIVOS[tr.nome]}\"", "    CMD OP_VOLTA"]
    return "\n".join(L) + "\n"


def gerar_roteiro(trechos):
    L = ["# Gerado por ferramentas/gerar_doca.py. Não editar à mão.",
         "# Incluído no roteiro_principal de sala2.s: os três trechos da fuga, ponto a ponto.", ""]
    for tr in trechos:
        cx, cy, d = tr.chegada
        L += [f'    ROTULO "{tr.nome}"', "    CMD OP_TRAVA", "    CMD OP_ESCURECE",
              f"    CMD OP_ANDAR, {tr.andar}, {cx}, {cy}, {d}",
              f"    ATOR ATOR_AGENTE, {tr.andar}, {tr.agente[0]}, {tr.agente[1]}, conj_AGENTE, AF_SOMBRA|AF_HD",
              f"    CMD OP_CHAMA, p=prepara_{tr.nome}", "    CMD OP_CLAREIA", f'    MSG "{tr.intro}"']
        L += [f"    CMD OP_DOCA, p=ponto_{tr.nome}_{k + 1}" for k in range(len(tr.pontos))]
        L.append("")
    return "\n".join(L)


def comprimir(rota):
    """Só os pontos onde o passo muda (o robô interpola entre eles)."""
    if len(rota) < 3:
        return rota
    saida = [rota[0]]
    for a, b, c in zip(rota, rota[1:], rota[2:]):
        if (b[1] - a[1], b[2] - a[2]) != (c[1] - b[1], c[2] - b[2]):
            saida.append(b)
    saida.append(rota[-1])
    return saida


def gerar_solucoes(trechos):
    L = ["/* Gerado por ferramentas/gerar_doca.py. Não editar à mão.",
         " * Para o robô de teste: em cada ponto da fuga, a nota da solução, a de uma",
         " * armadilha e o caminho (ms desde a nota, x, y) que o solucionador achou. */", ""]
    notas, erros, nomes = [], [], []
    for tr in trechos:
        falantes = {f.nome: f for f in tr.falantes}
        for k, p in enumerate(tr.pontos):
            nome = f"cam_{tr.nome}_{k + 1}"
            nomes.append(nome)
            pts = comprimir(p._rota)
            L.append(f"static const short {nome}[][3] = {{" +
                     ", ".join(f"{{{int(t * 1000)}, {x}, {y}}}" for (t, x, y) in pts) + "};")
            notas.append(falantes[p.solucao].nota)
            erros.append(falantes[p.falantes[1]].nota)
    L += ["", f"#define N_PONTOS_FUGA {len(nomes)}",
          "static const int fuga_nota[] = {" + ", ".join(map(str, notas)) + "};",
          "static const int fuga_nota_armadilha[] = {" + ", ".join(map(str, erros)) + "};",
          "static const short (*const fuga_caminho[])[3] = {" + ", ".join(nomes) + "};",
          "static const int fuga_n_caminho[] = {" +
          ", ".join(f"(int)(sizeof {n} / sizeof {n}[0])" for n in nomes) + "};", ""]
    return "\n".join(L)


# -------------------------------------------------------------------- main

def main():
    S = medidas_tileset()
    if "--explorar" in sys.argv:
        nome, k = sys.argv[sys.argv.index("--explorar") + 1].split(":")
        tr = next(t for t in TRECHOS if t.nome == nome)
        destino = RAIZ.parent / "sprites" / "elenco-sala2" / "doca" / f"explorar-{nome}-{k}.png"
        destino.parent.mkdir(parents=True, exist_ok=True)
        explorar(tr, S, int(k) - 1, destino)
        return
    todos_erros = []
    for tr in TRECHOS:
        posicionar_falantes(tr, S)
        resultados, erros, (sol, _) = verificar(tr, S)
        todos_erros += erros
        for p, r in zip(tr.pontos, resultados):
            if r:
                p._janela, p._rota = r["janela"], r["rota"]
        if "--mapas" in sys.argv:
            desenhar_mapa(tr, S, resultados, sol, RAIZ.parent / "sprites" / "elenco-sala2" / "doca" / f"{tr.nome}.png")
    if todos_erros:
        print("\n".join("ERRO: " + e for e in todos_erros))
        sys.exit(1)
    (RAIZ / "doca_dados.inc").write_text(gerar_dados(TRECHOS), encoding="utf-8")
    (RAIZ / "doca_roteiro.inc").write_text(gerar_roteiro(TRECHOS), encoding="utf-8")
    (RAIZ / "ferramentas" / "doca_solucoes.h").write_text(gerar_solucoes(TRECHOS), encoding="utf-8")
    n = sum(len(t.pontos) for t in TRECHOS)
    print(f"doca_dados.inc, doca_roteiro.inc, doca_solucoes.h: {len(TRECHOS)} trechos, {n} pontos")


if __name__ == "__main__":
    main()
