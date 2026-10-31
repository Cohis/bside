from __future__ import annotations

import math
import argparse
import os
import random
import re
from dataclasses import dataclass
from pathlib import Path

import pygame


PASTA = Path(__file__).resolve().parent
RAIZ = PASTA.parent
LARGURA = 640
ALTURA = 360
FAIXA_CIMA = 39
FAIXA_BAIXO = 43
VISTA_ALTURA = ALTURA - FAIXA_CIMA - FAIXA_BAIXO
FPS = 60
BRANCO = (242, 234, 220)
DOURADO = (233, 177, 93)
CORES_FALAS = {
    "NARRAÇÃO": (211, 202, 186),
    "ÍCARO": (230, 188, 204),
    "HANK": (106, 180, 216),
    "KAMI": (64, 184, 232),
    "FORD": (106, 106, 255),
    "AGENTE": (224, 40, 58),
    "EVA": (255, 176, 90),
}


@dataclass(frozen=True)
class Plano:
    capitulo: str
    cena: str
    falante: str
    texto: str
    duracao: float
    foco: tuple[float, float]
    zoom: float = 1.0
    poses: tuple[tuple[str, str], ...] = ()
    efeito: str = ""


def p(capitulo, cena, falante, texto, duracao, foco, zoom=1.0, poses=(), efeito=""):
    return Plano(capitulo, cena, falante, texto, duracao, foco, zoom, tuple(poses), efeito)


PLANOS = [
    p("A B-SIDE", "loja", "NARRAÇÃO", "Noite. Uma ligação muda o rumo de uma noite comum.", 4.0, (176, 204), 0.88, efeito="abertura"),
    p("A B-SIDE", "loja", "HANK", "O comprador ligou de novo. Quer o disco da Aurora ainda hoje.", 4.2, (290, 150), 1.0, (("HANK", "HANK_FALA"),)),
    p("A B-SIDE", "loja", "HANK", "Ficou no meu antigo galpão, perto da doca. Vendi o lugar, mas a caixa nunca saiu de lá.", 5.0, (290, 150), 1.04, (("HANK", "HANK_FALA"),)),
    p("A B-SIDE", "loja", "KAMI", "Tem uma gangue tomando conta daquele quarteirão.", 3.5, (206, 192), 1.08),
    p("A B-SIDE", "loja", "FORD", "A gente conversa primeiro. Se não der, eu converso do meu jeito.", 3.8, (236, 206), 1.06),
    p("A B-SIDE", "loja", "ÍCARO", "Eu vou junto.", 2.8, (176, 204), 1.24),
    p("A B-SIDE", "loja", "HANK", "Não.", 2.2, (290, 150), 1.28, (("HANK", "HANK_FALA"),)),
    p("A B-SIDE", "loja", "ÍCARO", "Hank, eu passo por onde o Ford não passa. Não disparo detector nem alarme de condutor.", 4.7, (176, 204), 1.13),
    p("A B-SIDE", "loja", "KAMI", "E não tem condução, não tem experiência e ainda é baixinho.", 3.8, (206, 192), 1.12),
    p("A B-SIDE", "loja", "HANK", "Kami e Ford: o galpão. Ícaro fica. Fim da conversa.", 4.0, (290, 150), 1.08, (("HANK", "HANK_FALA"),)),
    p("A B-SIDE", "loja", "NARRAÇÃO", "Eles partem. Ícaro espera alguns segundos… e escolhe a janela.", 4.3, (176, 204), 0.88, efeito="saida"),
    p("GALPÃO DE HANK", "galpao", "NARRAÇÃO", "Distrito 4. 23h. Uma janela quebrada, oito estantes e nenhum sinal de Kami ou Ford.", 4.7, (176, 170), 0.88, efeito="chegada"),
    p("GALPÃO DE HANK", "galpao", "KAMI", "(Lá fora) ...não é negociação. A gente só quer uma caixa. A da sétima estante.", 4.7, (176, 170), 1.02),
    p("GALPÃO DE HANK", "galpao", "ÍCARO", "Ela me viu entrar… e está me dizendo onde procurar.", 3.8, (58, 156), 1.15),
    p("GALPÃO DE HANK", "galpao", "NARRAÇÃO", "Fita amarela e preta. AURORA, escrito à mão. O vinil está frio demais.", 4.3, (62, 268), 1.36, efeito="disco"),
    p("GALPÃO DE HANK", "galpao", "NARRAÇÃO", "A estática acende a sala. Atrás do vidro alto, dois olhos observam Ícaro.", 4.4, (232, 16), 1.36, efeito="estatica"),
    p("GALPÃO DE HANK", "galpao", "ÍCARO", "Tinha alguém lá fora. Me olhando.", 3.2, (232, 16), 1.1),
    p("GALPÃO DE HANK", "galpao", "ÍCARO", "Isso foi um anjo?", 2.8, (220, 270), 1.2, efeito="grito"),
    p("GALPÃO DE HANK", "galpao", "AGENTE", "Não chega mais perto.", 2.8, (246, 322), 1.35, (("AGENTE", "AGENTE_SENTADO"),)),
    p("GALPÃO DE HANK", "galpao", "ÍCARO", "Um carmesim… Você está sangrando.", 3.2, (232, 298), 1.26),
    p("GALPÃO DE HANK", "galpao", "AGENTE", "Os anjos me marcaram. Escutou o grito? Estão vindo.", 4.0, (246, 322), 1.24, (("AGENTE", "AGENTE_SENTADO"),)),
    p("GALPÃO DE HANK", "galpao", "AGENTE", "E o que você tirou daquela caixa deixa eles ainda mais famintos.", 4.2, (246, 322), 1.24, (("AGENTE", "AGENTE_SENTADO"),)),
    p("GALPÃO DE HANK", "galpao", "ÍCARO", "O disco?", 2.5, (62, 268), 1.22),
    p("GALPÃO DE HANK", "galpao", "AGENTE", "Se sair por ali sozinho, morre também.", 3.6, (246, 322), 1.28, (("AGENTE", "AGENTE_SENTADO"),)),
    p("GALPÃO DE HANK", "galpao", "NARRAÇÃO", "Um grito rasga o galpão. Silhuetas descem das vigas.", 3.5, (220, 270), 0.98, efeito="anjos"),
    p("GALPÃO DE HANK", "galpao", "ÍCARO", "Então a gente sai junto. Levanta!", 3.2, (232, 298), 1.18),
    p("A DOCA", "doca", "NARRAÇÃO", "Anjos pousados por toda parte. Nenhum olha para eles; todos escutam.", 4.1, (184, 150), 0.84, efeito="doca"),
    p("A DOCA", "doca", "AGENTE", "Eles são cegos. Caçam pelo som.", 3.1, (200, 30), 1.04),
    p("A DOCA", "doca", "AGENTE", "Os alto-falantes ainda funcionam. Faça um berrar no tempo certo: eles vão atrás do ruído.", 4.8, (184, 40), 0.98),
    p("A DOCA", "doca", "AGENTE", "Fica na marca do chão. Um passo fora da hora e eles te escutam.", 4.1, (184, 40), 1.05),
    p("A DOCA", "doca", "NARRAÇÃO", "Primeiro ponto. Quatro pulsos. A nota certa no último — e corra.", 4.1, (80, 32), 1.12, efeito="pulso1"),
    p("A DOCA", "doca", "NARRAÇÃO", "O berro corta a névoa. As criaturas mergulham no cais vazio.", 3.5, (48, 168), 1.18, efeito="berro"),
    p("A DOCA", "doca", "AGENTE", "Bom. Continua assim.", 2.7, (184, 40), 1.0),
    p("A DOCA", "doca", "AGENTE", "Dois alto-falantes desta vez. Um deles fica no nosso caminho.", 3.7, (184, 40), 1.0, efeito="pulso2"),
    p("A DOCA", "doca", "NARRAÇÃO", "Uma isca arrasta os anjos para a passarela. Eles passam a um braço de distância.", 4.2, (176, 168), 1.12, efeito="isca"),
    p("A DOCA", "doca", "AGENTE", "Falta pouco. O portão fica depois daquele cais.", 3.3, (300, 250), 0.96, efeito="pulso3"),
    p("A DOCA", "doca", "NARRAÇÃO", "O último sinal. O caminho se abre — por um instante.", 3.1, (300, 250), 1.08, efeito="berro"),
    p("A DOCA", "doca", "AGENTE", "…Passamos.", 2.4, (308, 262), 1.28, (("AGENTE", "AGENTE_CAIDO"),)),
    p("A DOCA", "doca", "ÍCARO", "Ei! Ei, levanta! A gente já passou!", 3.3, (308, 262), 1.26, (("AGENTE", "AGENTE_CAIDO"),)),
    p("A DOCA", "doca", "FORD", "Ícaro?! Você está vivo?", 3.0, (322, 282), 1.14),
    p("A DOCA", "doca", "KAMI", "A gente revirou aquele galpão atrás de você! Que porra você acha que está fazendo?", 4.2, (286, 280), 1.15),
    p("A DOCA", "doca", "ÍCARO", "Depois vocês me matam. Me ajuda aqui.", 3.0, (308, 262), 1.2),
    p("A DOCA", "doca", "FORD", "Isso é um agente carmesim. Afasta, Ícaro.", 3.5, (322, 282), 1.16),
    p("A DOCA", "doca", "ÍCARO", "Ele me tirou daquele galpão vivo.", 3.2, (308, 262), 1.22),
    p("A DOCA", "revelacao", "NARRAÇÃO", "Ícaro se ajoelha. A máscara de porcelana cede, centímetro por centímetro.", 4.1, (308, 262), 1.18, efeito="revelacao"),
    p("A DOCA", "revelacao", "NARRAÇÃO", "Era uma garota. Pouco mais velha que ele.", 3.3, (308, 262), 1.2, efeito="revelacao"),
    p("A DOCA", "revelacao", "NARRAÇÃO", "Lágrimas roxas escorrem de seus olhos fechados.", 3.5, (308, 262), 1.2, efeito="revelacao"),
    p("A DOCA", "doca", "KAMI", "Essa tatuagem no pescoço… é da Ordem.", 3.2, (286, 280), 1.2),
    p("A DOCA", "doca", "FORD", "E ela está marcada pelos anjos. Se ficar aqui, não passa desta noite.", 4.0, (322, 282), 1.15),
    p("A DOCA", "doca", "ÍCARO", "Então ela vem com a gente.", 2.9, (308, 262), 1.24),
    p("A DOCA", "doca", "KAMI", "O Hank vai te matar.", 2.5, (286, 280), 1.12),
    p("A DOCA", "doca", "ÍCARO", "Ele vai ter que entrar na fila.", 3.0, (308, 262), 1.24, efeito="corte"),
    p("NA MANHÃ SEGUINTE", "loja_manha", "NARRAÇÃO", "Na manhã seguinte.", 3.0, (180, 200), 0.82, efeito="amanhecer"),
    p("NA MANHÃ SEGUINTE", "loja_manha", "HANK", "Então essa é a encrenca que você trouxe pra casa.", 4.0, (178, 190), 1.04, (("HANK", "HANK_FALA"),)),
    p("NA MANHÃ SEGUINTE", "loja_manha", "HANK", "Olha pra mim. Quantos bips você ouviu quando o Ícaro te trouxe até aqui?", 4.8, (178, 190), 1.12, (("HANK", "HANK_FALA"),)),
    p("NA MANHÃ SEGUINTE", "loja_manha", "EVA", "Eu não ouvi nada.", 2.9, (152, 196), 1.2),
    p("NA MANHÃ SEGUINTE", "loja_manha", "HANK", "Você lembra do caminho até aqui?", 3.2, (178, 190), 1.08, (("HANK", "HANK_FALA"),)),
    p("NA MANHÃ SEGUINTE", "loja_manha", "EVA", "Eu nem sei como cheguei aqui.", 3.3, (152, 196), 1.2),
    p("NA MANHÃ SEGUINTE", "loja_manha", "HANK", "Você se safou dessa vez. O Ícaro fez certo.", 3.6, (178, 190), 1.04, (("HANK", "HANK_FALA"),)),
    p("NA MANHÃ SEGUINTE", "loja_manha", "FORD", "…Sério?", 2.4, (220, 230), 1.1),
    p("NA MANHÃ SEGUINTE", "loja_manha", "KAMI", "E você? Tem nome?", 2.8, (190, 222), 1.12),
    p("NA MANHÃ SEGUINTE", "loja_manha", "EVA", "Eva.", 2.5, (152, 196), 1.3, efeito="fim"),
]


def ler_constantes(caminho, prefixo):
    padrao = re.compile(rf"\.equ {re.escape(prefixo)}_(.+)_(X|Y|L|A|N|AX|AY|OX|OY|W|D), (-?\d+)")
    resultado = {}
    for linha in caminho.read_text(encoding="utf-8").splitlines():
        encontrado = padrao.search(linha)
        if encontrado:
            nome, campo, valor = encontrado.groups()
            resultado.setdefault(nome, {})[campo] = int(valor)
    return resultado


class Atlas:
    def __init__(self, caminho_png, caminho_inc, prefixo, tamanho_padrao=(32, 16)):
        self.imagem = pygame.image.load(str(caminho_png)).convert_alpha()
        self.dados = ler_constantes(caminho_inc, prefixo)
        self.prefixo = prefixo
        self.tamanho_padrao = tamanho_padrao
        self.cache = {}
        self.cache_escala = {}

    def existe(self, nome):
        return nome in self.dados and "X" in self.dados[nome] and "Y" in self.dados[nome]

    def quadro(self, nome, indice=0):
        chave = (nome, indice)
        if chave in self.cache:
            return self.cache[chave]
        dado = self.dados.get(nome)
        if not dado:
            return None
        largura = dado.get("L", self.tamanho_padrao[0])
        altura = dado.get("A", self.tamanho_padrao[1])
        quantidade = max(1, dado.get("N", 1))
        indice %= quantidade
        retangulo = pygame.Rect(dado["X"] + largura * indice, dado["Y"], largura, altura)
        quadro = self.imagem.subsurface(retangulo).copy()
        self.cache[chave] = quadro
        return quadro

    def escala(self, quadro, fator):
        largura = max(1, round(quadro.get_width() * fator))
        altura = max(1, round(quadro.get_height() * fator))
        chave = (id(quadro), largura, altura)
        if chave not in self.cache_escala:
            self.cache_escala[chave] = pygame.transform.scale(quadro, (largura, altura))
        return self.cache_escala[chave]


class Som:
    def __init__(self):
        self.ativo = False
        self.mudo = False
        self.sons = {}
        try:
            pygame.mixer.init()
            self.ativo = True
            trilha = PASTA / "assets" / "musica-fundo.mp3"
            if trilha.exists():
                pygame.mixer.music.load(str(trilha))
                pygame.mixer.music.set_volume(0.2)
                pygame.mixer.music.play(-1, fade_ms=1200)
            for nome in ("estatica", "grito", "berro"):
                arquivo = PASTA / "assets" / "sons" / f"{nome}.wav"
                if arquivo.exists():
                    self.sons[nome] = pygame.mixer.Sound(str(arquivo))
                    self.sons[nome].set_volume(0.24)
        except pygame.error:
            self.ativo = False

    def tocar(self, nome):
        if self.ativo and not self.mudo and nome in self.sons:
            self.sons[nome].play()

    def alternar(self):
        self.mudo = not self.mudo
        if self.ativo:
            pygame.mixer.music.set_volume(0.0 if self.mudo else 0.2)


class Cinematica:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("B-Side — Cinemática 2.5D")
        self.janela = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
        self.relogio = pygame.time.Clock()
        self.tela = pygame.Surface((LARGURA, ALTURA)).convert()
        self.cena_tela = pygame.Surface((LARGURA, VISTA_ALTURA)).convert()
        self.atlas_cenario = Atlas(PASTA / "assets" / "tileset-iso.png", PASTA / "tileset.inc", "S")
        self.atlas_pessoas = Atlas(PASTA / "assets" / "personagens.png", PASTA / "personagens.inc", "P", (36, 48))
        self.nevoa = pygame.image.load(str(PASTA / "assets" / "nevoa.png")).convert_alpha()
        self.vinheta_vista = self.criar_vinheta()
        self.nevoa_vista = pygame.transform.scale(self.nevoa, (LARGURA, VISTA_ALTURA))
        self.figuras = self.carregar_figuras()
        self.figuras_escala = {}
        self.luzes_escala = {}
        self.som = Som()
        self.fonte = self.carregar_fonte("DejaVuSans.ttf", 12)
        self.fonte_pequena = self.carregar_fonte("DejaVuSans.ttf", 9)
        self.fonte_titulo = self.carregar_fonte("DejaVuSerif.ttf", 15)
        self.tempo_total = 0.0
        self.tempo_plano = 0.0
        self.indice = 0
        self.foco_atual = list(PLANOS[0].foco)
        self.zoom_atual = PLANOS[0].zoom
        self.cheio = False
        self.pausado = False
        self.rodando = True
        self.granulado = self.criar_grao()
        self.particulas = [(random.random(), random.random(), random.uniform(0.4, 1.1), random.random() * math.tau) for _ in range(68)]
        self.som.tocar(PLANOS[0].efeito)

    @staticmethod
    def carregar_fonte(nome, tamanho):
        candidatos = [
            Path("/usr/share/fonts/TTF") / nome,
            Path("/usr/share/fonts/truetype/dejavu") / nome,
            Path("/usr/share/fonts/truetype/liberation") / nome,
        ]
        for caminho in candidatos:
            if caminho.exists():
                return pygame.font.Font(str(caminho), tamanho)
        return pygame.font.Font(None, tamanho)

    def carregar_figuras(self):
        figuras = {}
        for pessoa, arquivo in (("ÍCARO", "icaro"), ("EVA", "eva")):
            caminho = RAIZ / "sprites" / "revisao" / "quadros" / arquivo / "sul" / "00.png"
            if not caminho.exists():
                caminho = PASTA / "assets" / "icaro-andar-rascunho.png"
                if caminho.exists():
                    sheet = pygame.image.load(str(caminho)).convert_alpha()
                    linha = 4 if arquivo == "icaro" else 0
                    quadro = sheet.subsurface(pygame.Rect(0, linha * 512, 384, 512)).copy()
                else:
                    continue
            else:
                quadro = pygame.image.load(str(caminho)).convert_alpha()
            limites = quadro.get_bounding_rect(min_alpha=8)
            if limites.width and limites.height:
                quadro = quadro.subsurface(limites).copy()
            figuras[pessoa] = quadro
        return figuras

    @staticmethod
    def criar_grao():
        superficie = pygame.Surface((LARGURA, VISTA_ALTURA), pygame.SRCALPHA)
        rng = random.Random(29)
        for _ in range(360):
            x = rng.randrange(LARGURA)
            y = rng.randrange(VISTA_ALTURA)
            superficie.set_at((x, y), (238, 221, 185, rng.randrange(4, 13)))
        return superficie

    @staticmethod
    def criar_vinheta():
        superficie = pygame.Surface((LARGURA, VISTA_ALTURA), pygame.SRCALPHA)
        centro_x, centro_y = LARGURA * 0.5, VISTA_ALTURA * 0.5
        for y in range(VISTA_ALTURA):
            for x in range(LARGURA):
                dx = abs(x - centro_x) / centro_x
                dy = abs(y - centro_y) / centro_y
                distancia = max(dx, dy * 1.35)
                alfa = max(0, min(146, round((distancia - 0.38) * 235)))
                if alfa:
                    superficie.set_at((x, y), (0, 0, 4, alfa))
        return superficie

    @property
    def plano(self):
        return PLANOS[self.indice]

    def avancar(self, direcao=1):
        proximo = max(0, min(len(PLANOS) - 1, self.indice + direcao))
        if proximo == self.indice:
            if direcao > 0 and self.indice == len(PLANOS) - 1:
                self.pausado = True
            return
        self.indice = proximo
        self.tempo_plano = 0.0
        self.som.tocar(self.plano.efeito)

    def ir_capitulo(self, tecla):
        indices = {pygame.K_1: "A B-SIDE", pygame.K_2: "GALPÃO DE HANK", pygame.K_3: "A DOCA", pygame.K_4: "NA MANHÃ SEGUINTE"}
        nome = indices.get(tecla)
        if not nome:
            return
        encontrados = [i for i, plano in enumerate(PLANOS) if plano.capitulo == nome]
        if encontrados:
            self.indice = encontrados[0]
            self.tempo_plano = 0.0
            self.som.tocar(self.plano.efeito)

    def tratar_eventos(self):
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                self.rodando = False
            elif evento.type == pygame.VIDEORESIZE and not self.cheio:
                self.janela = pygame.display.set_mode(evento.size, pygame.RESIZABLE)
            elif evento.type == pygame.MOUSEBUTTONDOWN:
                if evento.button == 1:
                    self.avancar()
                elif evento.button == 3:
                    self.avancar(-1)
            elif evento.type == pygame.KEYDOWN:
                if evento.key == pygame.K_ESCAPE:
                    self.rodando = False
                elif evento.key in (pygame.K_SPACE, pygame.K_RETURN, pygame.K_RIGHT, pygame.K_e):
                    self.avancar()
                elif evento.key in (pygame.K_BACKSPACE, pygame.K_LEFT):
                    self.avancar(-1)
                elif evento.key == pygame.K_p:
                    self.pausado = not self.pausado
                elif evento.key == pygame.K_m:
                    self.som.alternar()
                elif evento.key == pygame.K_F11:
                    self.cheio = not self.cheio
                    if self.cheio:
                        self.janela = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                    else:
                        self.janela = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
                else:
                    self.ir_capitulo(evento.key)

    def atualizar(self, dt):
        if self.pausado:
            return
        self.tempo_total += dt
        self.tempo_plano += dt
        alvo = self.plano.foco
        suavidade = min(1.0, dt * 1.5)
        self.foco_atual[0] += (alvo[0] - self.foco_atual[0]) * suavidade
        self.foco_atual[1] += (alvo[1] - self.foco_atual[1]) * suavidade
        self.zoom_atual += (self.plano.zoom - self.zoom_atual) * min(1.0, dt * 1.2)
        if self.tempo_plano >= self.plano.duracao:
            self.avancar()

    def mundo_tela(self, x, y, z=0):
        fator = 0.88 * self.zoom_atual
        deriva = math.sin(self.tempo_total * 0.32) * 1.5
        cx, cy = self.foco_atual[0] + deriva, self.foco_atual[1] - deriva * 0.35
        return (
            LARGURA * 0.5 + ((x - y) - (cx - cy)) * fator,
            VISTA_ALTURA * 0.5 + ((x + y) - (cx + cy)) * 0.25 * self.zoom_atual - z * fator,
        )

    def desenhar_sprite_mundo(self, nome, x, y, z=0, atlas=None, indice=0, ancora=True, brilho=None):
        atlas = atlas or self.atlas_cenario
        quadro = atlas.quadro(nome, indice)
        if quadro is None:
            return
        fator = 0.88 * self.zoom_atual
        escalado = atlas.escala(quadro, fator)
        dado = atlas.dados[nome]
        sx, sy = self.mundo_tela(x, y, z)
        if ancora:
            ax = dado.get("AX", escalado.get_width() / max(fator, 0.01) * 0.5) * fator
            ay = dado.get("AY", escalado.get_height() / max(fator, 0.01)) * fator
            sx -= ax
            sy -= ay
        destino = (round(sx), round(sy))
        if brilho:
            aura = pygame.Surface((escalado.get_width() + 10, escalado.get_height() + 10), pygame.SRCALPHA)
            pygame.draw.ellipse(aura, (*brilho, 48), aura.get_rect().inflate(-2, -3))
            self.cena_tela.blit(aura, (destino[0] - 5, destino[1] - 5), special_flags=pygame.BLEND_RGBA_ADD)
        self.cena_tela.blit(escalado, destino)

    def piso(self, cena):
        if cena in ("doca", "revelacao"):
            rows = [
                "XXXXPPXXXXXXXXXXXXXXXX",
                "#QQQQQQQQQQQQQQQQQQQQ#",
                "#QQQQQQQQQQQQQQQQQQQQ#",
                "#QQQQQQQQQQQQQQQQQQQQ#",
                "#QQQQQQQQQQQQQQQQQQQQ#",
                "#~TT~~~~~TTTT~~~~QQQQ#",
                "#~TT~~~~~TTTT~~~~QQQQ#",
                "#~TT~~~~~TTTT~~~~QQQQ#",
                "#~TT~~~~~TTTT~~~~QQQQ#",
                "#~TT~~~~~TTTTTTTTQQQQ#",
                "#~TT~~~~~TTTTTTTTQQQQ#",
                "#~TT~~~~~TTTTTTTTQQQQ#",
                "#~~~~~~~~TTTT~~~~QQQQ#",
                "#~~~~~~~~TTTT~~~~QQQQ#",
                "#~~~~~~~~~~~~~~~~QQQQ#",
                "#~~~~~~~~~~~~~~~~QQQQ#",
                "#~~~~~~~~~~~~~~~~QQQQ#",
                "#~~~~~~~~~~~~~~~~QQQQ#",
                "#~~~~~~~~~~~~~~~~QQQQ#",
                "#~~~~~~~~~~~~~~~~QQQQ#",
                "#~~~~~~~~~~~~~~~~QQQQ#",
                "##################QQ##",
            ]
        elif cena == "galpao":
            rows = [
                "#####JJJJ####JJJJ#####",
                "#GGGGGGGGGGGGGGGGGGGG#",
                "JGGGGGGGGGGGGGGGGGGGG#",
                "JGGGGGGGGGGGGGGGGGGGG#",
            ] + ["#GGGGGGGGGGGGGGGGGGGG#"] * 17 + ["################PP####"]
        else:
            rows = ["#" + "L" * 20 + "#"] * 22
        for ty, linha in enumerate(rows[:22]):
            for tx, codigo in enumerate(linha[:22]):
                if codigo == "#" and cena not in ("galpao", "doca", "revelacao"):
                    continue
                nome = "PISO_LOJA"
                if cena == "galpao":
                    nome = "PISO_GALPAO"
                elif cena in ("doca", "revelacao"):
                    nome = "AGUA" if codigo in "~X" else "PISO_DOCA" if codigo == "T" else "PISO_CAIS"
                    if codigo == "P":
                        nome = "PISO_CAIS"
                if self.atlas_cenario.existe(nome):
                    self.desenhar_sprite_mundo(nome, tx * 16, ty * 16, ancora=False)
                else:
                    x, y = self.mundo_tela(tx * 16, ty * 16)
                    c = (39, 45, 56) if cena != "doca" else (17, 35, 53)
                    pontos = [(x, y), (x + 16 * self.zoom_atual, y + 8 * self.zoom_atual), (x, y + 16 * self.zoom_atual), (x - 16 * self.zoom_atual, y + 8 * self.zoom_atual)]
                    pygame.draw.polygon(self.cena_tela, c, pontos)

    def parede(self, eixo, fixo, inicio, fim, altura, cor, variacao):
        passo = 16
        for pos in range(inicio, fim, passo):
            fim_bloco = min(fim, pos + passo)
            if eixo == "x":
                a = self.mundo_tela(pos, fixo, 0)
                b = self.mundo_tela(fim_bloco, fixo, 0)
                c = self.mundo_tela(fim_bloco, fixo, altura)
                d = self.mundo_tela(pos, fixo, altura)
            else:
                a = self.mundo_tela(fixo, pos, 0)
                b = self.mundo_tela(fixo, fim_bloco, 0)
                c = self.mundo_tela(fixo, fim_bloco, altura)
                d = self.mundo_tela(fixo, pos, altura)
            tom = max(0, min(255, cor[0] + (pos // 16 % 3 - 1) * variacao))
            face = (tom, cor[1], cor[2])
            pygame.draw.polygon(self.cena_tela, face, [a, b, c, d])
            pygame.draw.line(self.cena_tela, tuple(min(255, v + 24) for v in face), d, c, 1)
            pygame.draw.line(self.cena_tela, (14, 17, 24), a, b, 1)
            if pos % 32 == 0:
                pygame.draw.line(self.cena_tela, (21, 23, 30), a, d, 1)

    def painel_parede(self, eixo, fixo, pos, largura, z, altura, cor, contorno):
        if eixo == "x":
            pontos = [self.mundo_tela(pos, fixo, z), self.mundo_tela(pos + largura, fixo, z), self.mundo_tela(pos + largura, fixo, z + altura), self.mundo_tela(pos, fixo, z + altura)]
        else:
            pontos = [self.mundo_tela(fixo, pos, z), self.mundo_tela(fixo, pos + largura, z), self.mundo_tela(fixo, pos + largura, z + altura), self.mundo_tela(fixo, pos, z + altura)]
        pygame.draw.polygon(self.cena_tela, cor, pontos)
        pygame.draw.polygon(self.cena_tela, contorno, pontos, 1)

    def arquitetura(self, cena):
        if cena == "galpao":
            self.parede("x", 16, 16, 336, 70, (48, 49, 61), 5)
            self.parede("y", 16, 16, 336, 70, (38, 43, 57), 4)
            for pos in (112, 240):
                self.painel_parede("x", 16, pos, 44, 36, 24, (35, 76, 103), (125, 155, 166))
                self.painel_parede("x", 16, pos + 21, 2, 36, 24, (128, 144, 148), (15, 25, 36))
            self.painel_parede("x", 16, 220, 26, 34, 25, (5, 10, 17), (95, 113, 136))
            for pos in (64, 192, 288):
                x, y = self.mundo_tela(pos, 16, 56)
                pygame.draw.circle(self.cena_tela, (212, 137, 77), (round(x), round(y)), max(2, round(2 * self.zoom_atual)))
        elif cena in ("loja", "loja_manha"):
            tom = (82, 57, 48) if cena == "loja" else (117, 78, 57)
            self.parede("x", 16, 16, 336, 64, tom, 6)
            self.parede("y", 16, 16, 336, 64, (49, 47, 62), 4)
            for pos in (48, 96, 144, 192, 240, 288):
                self.painel_parede("x", 16, pos, 18, 24, 25, (33, 49, 70), (152, 129, 94))
                self.painel_parede("x", 16, pos + 8, 1, 24, 25, (176, 141, 91), (24, 25, 34))

    def props(self, cena):
        lista = []

        def adicionar_serie(nome, x, y, quantidade=None, passo=16):
            if quantidade is None:
                quantidade = 0
                while self.atlas_cenario.existe(f"{nome}_{quantidade}"):
                    quantidade += 1
            for indice in range(quantidade):
                parte = f"{nome}_{indice}"
                if self.atlas_cenario.existe(parte):
                    lista.append((x + indice * passo, y, parte, 0))

        def adicionar(nome, x, y, z=0):
            if self.atlas_cenario.existe(nome):
                lista.append((x, y, nome, z))

        if cena == "galpao":
            fileiras = ((40, 48, "PRATELEIRA_G"), (168, 48, "PRATELEIRA_G2"), (40, 112, "PRATELEIRA_G2"), (168, 112, "PRATELEIRA_G"), (40, 176, "PRATELEIRA_G"), (168, 176, "PRATELEIRA_G2"), (40, 240, "PRATELEIRA_G_MARCADA"), (168, 240, "PRATELEIRA_G"))
            for x, y, nome in fileiras:
                adicionar_serie(nome, x, y, 3)
            adicionar_serie("BANCADA_RADIOS", 248, 17, 4)
            adicionar("MESA_PRANCHETA", 120, 18)
            adicionar_serie("CAIXAS_PILHA", 296, 120, 2)
            adicionar_serie("CAIXAS_PILHA", 296, 200, 2)
            adicionar_serie("CAIXOTES_GALPAO", 200, 300, 3)
            adicionar("DISCO", 62, 268, 16)
            adicionar("ESTATICA_TV", 272, 30, 23)
        elif cena in ("doca", "revelacao"):
            adicionar_serie("CONTAINER_VERMELHO", 272, 20, 4)
            adicionar_serie("CONTAINER_AZUL", 224, 52, 4)
            for x, y in ((108, 68), (144, 68), (136, 116), (210, 96), (248, 132), (324, 210), (272, 226)):
                adicionar("CABECO", x, y)
            for x, y in ((128, 72), (212, 148), (278, 198), (54, 138)):
                adicionar("POSTE", x, y)
            for x, y in ((45, 164), (307, 62), (173, 208), (45, 100), (313, 276)):
                adicionar("ALTO_FALANTE", x, y, 30)
        else:
            adicionar_serie("ESTANTE_DISCOS", 80, 17, 2)
            adicionar_serie("ESTANTE_DISCOS", 240, 17, 2)
            for x, y in ((128, 80), (208, 80), (128, 144), (208, 144)):
                adicionar_serie("CAIXOTE", x, y, 2)
            adicionar("PLANTA", 310, 18)
            adicionar("PLANTA", 82, 196)
            adicionar_serie("BALCAO", 256, 160, 4)
            adicionar_serie("BALCAO_CAFE", 17, 241, 3)
            adicionar_serie("VITROLA", 129, 241, 2)
        for x, y, nome, z in sorted(lista, key=lambda item: item[0] + item[1]):
            if nome == "DISCO":
                pulso = (math.sin(self.tempo_total * 2.1) + 1) * 0.5
                brilho = (120, 190, 255) if self.plano.efeito == "disco" else None
                self.desenhar_sprite_mundo(nome, x, y, z + pulso * 7, brilho=brilho)
            elif nome == "ESTATICA_TV":
                brilho = (90, 160, 255) if self.plano.efeito == "estatica" else None
                self.desenhar_sprite_mundo(nome, x, y, z, brilho=brilho)
            else:
                self.desenhar_sprite_mundo(nome, x, y, z)

    def estados_atores(self, cena, indice=None):
        indice = self.indice if indice is None else indice
        plano = PLANOS[indice]
        if cena == "loja":
            estados = {
                "ÍCARO": (176, 204, "ÍCARO"), "HANK": (290, 150, "HANK_PARADO_S"),
                "KAMI": (206, 192, "KAMI_PARADO_S"), "FORD": (236, 206, "FORD_PARADO_S"),
            }
            if plano.efeito == "saida":
                estados.pop("KAMI")
                estados.pop("FORD")
                estados["ÍCARO"] = (18, 190, "ÍCARO")
            return estados
        if cena == "loja_manha":
            return {
                "ÍCARO": (116, 214, "ÍCARO"), "HANK": (178, 190, "HANK_PARADO_S"),
                "EVA": (152, 196, "EVA" if "EVA" in self.figuras else "EVA_PARADA"), "KAMI": (190, 222, "KAMI_PARADO_S"),
                "FORD": (220, 230, "FORD_PARADO_S"),
            }
        if cena == "galpao":
            icaro = (62, 268, "ÍCARO") if plano.efeito in ("disco", "estatica") else (220, 304, "ÍCARO") if plano.efeito in ("grito", "anjos") else (58, 156, "ÍCARO")
            return {"ÍCARO": icaro, "AGENTE": (246, 322, "AGENTE_SENTADO")}
        if cena == "revelacao":
            return {
                "ÍCARO": (288, 286, "ÍCARO"), "AGENTE": (308, 262, "EVA_CAIDA"),
                "KAMI": (286, 280, "KAMI_PARADO_S"), "FORD": (322, 282, "FORD_PARADO_S"),
            }
        if indice <= 32:
            icaro, agente = (80, 32), (200, 30)
        elif indice <= 34:
            icaro, agente = (184, 40), (200, 30)
        elif indice <= 36:
            icaro, agente = (176, 168), (194, 160)
        else:
            icaro, agente = (300, 250), (320, 244)
        atores = {
            "ÍCARO": (*icaro, "ÍCARO"), "AGENTE": (*agente, "AGENTE_PARADO_S"),
            "ANJO_0": (112, 72, "ANJO_POUSADO"), "ANJO_1": (148, 72, "ANJO_POUSADO"),
            "ANJO_2": (140, 120, "ANJO_POUSADO"), "ANJO_3": (214, 100, "ANJO_POUSADO"),
            "ANJO_4": (252, 136, "ANJO_POUSADO"), "ANJO_5": (328, 214, "ANJO_POUSADO"),
            "ANJO_6": (276, 230, "ANJO_POUSADO"),
        }
        if indice >= 39:
            atores["KAMI"] = (286, 280, "KAMI_PARADO_S")
            atores["FORD"] = (322, 282, "FORD_PARADO_S")
        return atores

    def desenhar_ator(self, pessoa, x, y, pose, indice_pose=0):
        if pessoa in self.figuras:
            quadro = self.figuras[pessoa]
            altura = round(44 * self.zoom_atual)
            largura = round(26 * self.zoom_atual)
            chave = (pessoa, largura, altura)
            if chave not in self.figuras_escala:
                self.figuras_escala[chave] = pygame.transform.scale(quadro, (largura, altura))
            quadro = self.figuras_escala[chave]
            sx, sy = self.mundo_tela(x, y)
            sy += math.sin(self.tempo_total * 2.2 + x * 0.04) * 0.7 * self.zoom_atual
            self.cena_tela.blit(quadro, (round(sx - largura * 0.5), round(sy - altura)))
            return
        nome = pose
        if pose == "HANK_PARADO_S" and self.plano.falante == "HANK":
            nome = "HANK_FALA"
        if pose == "AGENTE_PARADO_S":
            nome = "AGENTE_PARADO_S"
        if not self.atlas_pessoas.existe(nome):
            return
        quant = self.atlas_pessoas.dados[nome].get("N", 1)
        quadro_indice = int(self.tempo_total * 5) % quant if quant > 1 else indice_pose
        quadro = self.atlas_pessoas.quadro(nome, quadro_indice)
        fator = 0.88 * self.zoom_atual
        escalado = self.atlas_pessoas.escala(quadro, fator)
        dado = self.atlas_pessoas.dados[nome]
        sx, sy = self.mundo_tela(x, y)
        sy += math.sin(self.tempo_total * 2 + x * 0.03) * 0.4
        ax = dado.get("AX", 18) * fator
        ay = dado.get("AY", 45) * fator
        self.cena_tela.blit(escalado, (round(sx - ax), round(sy - ay)))

    def atores(self, cena):
        estados = self.estados_atores(cena)
        if self.indice > 0 and PLANOS[self.indice - 1].cena == cena and self.tempo_plano < 0.9:
            anteriores = self.estados_atores(cena, self.indice - 1)
            progresso = min(1.0, self.tempo_plano / 0.9)
            progresso = progresso * progresso * (3 - 2 * progresso)
            for pessoa, estado in tuple(estados.items()):
                if pessoa in anteriores:
                    antes = anteriores[pessoa]
                    x = antes[0] + (estado[0] - antes[0]) * progresso
                    y = antes[1] + (estado[1] - antes[1]) * progresso
                    estados[pessoa] = (x, y, estado[2])
        for pessoa, pose in self.plano.poses:
            if pessoa in estados:
                x, y, _ = estados[pessoa]
                estados[pessoa] = (x, y, pose)
        if cena == "doca":
            if self.plano.efeito in ("berro", "isca"):
                estados = {nome: (x, y, "ANJO_VOO") if nome.startswith("ANJO") else (x, y, pose) for nome, (x, y, pose) in estados.items()}
            elif self.plano.efeito in ("pulso1", "pulso2", "pulso3"):
                estados = {nome: (x, y, "ANJO_GRITO") if nome.startswith("ANJO") else (x, y, pose) for nome, (x, y, pose) in estados.items()}
        elif cena == "galpao" and self.plano.efeito == "anjos":
            estados.update({"ANJO_0": (176, 250, "ANJO_VOO"), "ANJO_1": (300, 236, "ANJO_VOO")})
        for pessoa, (x, y, pose) in sorted(estados.items(), key=lambda item: item[1][0] + item[1][1]):
            chave = pose if pessoa.startswith("ANJO") else pessoa
            if chave == "ÍCARO":
                self.desenhar_ator("ÍCARO", x, y, pose)
            elif chave == "EVA":
                self.desenhar_ator("EVA", x, y, pose)
            else:
                nome = pose
                if pessoa.startswith("ANJO") and pose in ("ANJO_VOO", "ANJO_GRITO") and self.atlas_pessoas.existe(pose):
                    nome = pose
                self.desenhar_ator(pessoa, x, y, nome)

    def desenhar_olhos_mael(self):
        x, y = self.mundo_tela(232, 16, 40)
        largura = max(18, round(26 * self.zoom_atual))
        altura = max(8, round(10 * self.zoom_atual))
        camada = pygame.Surface((largura + 18, altura + 14), pygame.SRCALPHA)
        meio_x, meio_y = camada.get_width() // 2, camada.get_height() // 2
        pygame.draw.ellipse(camada, (89, 79, 202, 34), (2, meio_y - altura // 2, largura + 14, altura + 8))
        pygame.draw.ellipse(camada, (114, 115, 255, 82), (8, meio_y - altura // 2 + 2, largura + 2, altura + 3))
        pygame.draw.ellipse(camada, (220, 211, 255, 205), (meio_x - largura // 2, meio_y - 1, largura // 2 - 2, 3))
        pygame.draw.ellipse(camada, (220, 211, 255, 205), (meio_x + 2, meio_y - 1, largura // 2 - 2, 3))
        pygame.draw.line(camada, (255, 247, 225, 220), (meio_x - 2, meio_y), (meio_x - 2, meio_y + 1), 1)
        pygame.draw.line(camada, (255, 247, 225, 220), (meio_x + 2, meio_y), (meio_x + 2, meio_y + 1), 1)
        self.cena_tela.blit(camada, (round(x - camada.get_width() / 2), round(y - camada.get_height() / 2)))

    def ceu(self, cena):
        if cena == "doca" or cena == "revelacao":
            topo, base = (12, 23, 43), (55, 56, 73)
        elif cena == "loja_manha":
            topo, base = (99, 68, 72), (221, 151, 95)
        elif cena == "galpao":
            topo, base = (8, 14, 27), (25, 35, 49)
        else:
            topo, base = (17, 20, 32), (58, 42, 43)
        for y in range(VISTA_ALTURA):
            t = y / max(1, VISTA_ALTURA - 1)
            cor = tuple(round(topo[i] * (1 - t) + base[i] * t) for i in range(3))
            pygame.draw.line(self.cena_tela, cor, (0, y), (LARGURA, y))
        if cena in ("doca", "revelacao"):
            for i in range(12):
                x = (i * 71 - round(self.tempo_total * 5)) % (LARGURA + 80) - 40
                pygame.draw.line(self.cena_tela, (75, 93, 117), (x, 42 + i % 3 * 8), (x + 24, 42 + i % 3 * 8), 1)
        elif cena == "loja_manha":
            for i in range(8):
                x = i * 96 - 18
                altura = 24 + (i * 37 % 32)
                pygame.draw.rect(self.cena_tela, (38, 43, 57), (x, 94 - altura, 42, altura))
                pygame.draw.rect(self.cena_tela, (197, 145, 92), (x + 8, 70 - altura, 3, 2))

    def poeira(self, cena):
        cor = (223, 193, 145) if cena != "doca" else (138, 179, 210)
        camada = pygame.Surface((LARGURA, VISTA_ALTURA), pygame.SRCALPHA)
        for u, v, velocidade, fase in self.particulas:
            x = round((u * LARGURA + math.sin(self.tempo_total * velocidade + fase) * 7) % LARGURA)
            y = round((v * VISTA_ALTURA + self.tempo_total * velocidade * 2) % VISTA_ALTURA)
            brilho = 55 + round(45 * (math.sin(self.tempo_total * 1.7 + fase) + 1) / 2)
            camada.set_at((x, y), (*cor, brilho))
        self.cena_tela.blit(camada, (0, 0))

    def luz_dramatica(self, cena):
        planos = {
            "galpao": [(64, 92, 50, (104, 137, 198), 46), (192, 92, 50, (104, 137, 198), 42), (274, 44, 24, (91, 149, 231), 50)],
            "doca": [(132, 74, 56, (234, 153, 82), 50), (216, 150, 56, (235, 148, 73), 46), (282, 202, 56, (235, 148, 73), 42)],
            "revelacao": [(216, 150, 56, (173, 105, 226), 55), (282, 202, 56, (228, 132, 87), 38)],
            "loja": [(64, 24, 42, (224, 164, 102), 48), (220, 24, 42, (219, 151, 91), 43), (274, 156, 28, (105, 144, 194), 28)],
            "loja_manha": [(176, 24, 68, (255, 185, 119), 62), (48, 32, 58, (236, 147, 127), 38)],
        }
        for wx, wy, altura_luz, cor, alfa in planos[cena]:
            raio = round((44 if self.plano.zoom > 1.2 else 64) * self.zoom_atual)
            x, y = self.mundo_tela(wx, wy, altura_luz)
            x, y = round(x), round(y)
            chave = (raio, cor, alfa)
            if chave not in self.luzes_escala:
                camada = pygame.Surface((raio * 2, raio * 2), pygame.SRCALPHA)
                for r in range(raio, 1, -2):
                    opacidade = round(alfa * (1 - r / raio) ** 2.35)
                    pygame.draw.circle(camada, (*cor, opacidade), (raio, raio), r)
                self.luzes_escala[chave] = camada
            camada = self.luzes_escala[chave]
            self.cena_tela.blit(camada, (x - raio, y - raio))

    def efeito_plano(self):
        efeito = self.plano.efeito
        if efeito in ("estatica", "grito"):
            alfa = 12 + round(8 * (0.5 + 0.5 * math.sin(self.tempo_total * 28)))
            camada = pygame.Surface((LARGURA, VISTA_ALTURA), pygame.SRCALPHA)
            camada.fill((100, 150, 255, alfa))
            self.cena_tela.blit(camada, (0, 0))
            if efeito == "grito":
                ondas = pygame.Surface((LARGURA, VISTA_ALTURA), pygame.SRCALPHA)
                for i in range(3):
                    r = round((self.tempo_plano * 48 + i * 36) % 180)
                    pygame.draw.ellipse(ondas, (211, 197, 238, 52), (LARGURA // 2 - r, VISTA_ALTURA // 2 - r // 3, r * 2, r // 2), 1)
                self.cena_tela.blit(ondas, (0, 0))
        if efeito in ("pulso1", "pulso2", "pulso3", "berro", "isca"):
            if efeito == "pulso1" or (efeito == "berro" and self.indice == 31):
                centro = self.mundo_tela(48, 168, 30)
            elif efeito == "pulso2":
                centro = self.mundo_tela(310, 66, 30)
            elif efeito == "isca":
                centro = self.mundo_tela(176, 212, 30)
            else:
                centro = self.mundo_tela(48, 104, 30)
            centro = (round(centro[0]), round(centro[1]))
            ondas = pygame.Surface((LARGURA, VISTA_ALTURA), pygame.SRCALPHA)
            for i in range(4):
                r = round((self.tempo_plano * 46 + i * 28) % 118)
                pygame.draw.circle(ondas, (243, 189, 115, 86), centro, r, 1)
            self.cena_tela.blit(ondas, (0, 0))
        if efeito == "revelacao":
            nome = "REVELACAO"
            if self.atlas_pessoas.existe(nome):
                quantidade = self.atlas_pessoas.dados[nome].get("N", 7)
                if self.tempo_plano < 1.1:
                    quadro_indice = 0
                elif self.tempo_plano < 1.8:
                    quadro_indice = 1
                elif self.tempo_plano < 2.35:
                    quadro_indice = 2
                elif self.tempo_plano < 2.9:
                    quadro_indice = 3
                elif self.tempo_plano < 3.5:
                    quadro_indice = min(4, quantidade - 1)
                else:
                    quadro_indice = min(6, quantidade - 1)
                quadro = self.atlas_pessoas.quadro(nome, quadro_indice)
                if quadro:
                    altura = 178
                    largura = round(quadro.get_width() * altura / quadro.get_height())
                    close = pygame.transform.scale(quadro, (largura, altura))
                    x = (LARGURA - largura) // 2
                    y = (VISTA_ALTURA - altura) // 2 - 2
                    fundo = pygame.Surface((largura + 22, altura + 22), pygame.SRCALPHA)
                    pygame.draw.rect(fundo, (8, 8, 16, 224), fundo.get_rect(), border_radius=7)
                    pygame.draw.rect(fundo, (166, 109, 176, 225), fundo.get_rect(), width=1, border_radius=7)
                    self.cena_tela.blit(fundo, (x - 11, y - 11))
                    self.cena_tela.blit(close, (x, y))
        if efeito == "fim" and self.tempo_plano > 1.1:
            camada = pygame.Surface((LARGURA, VISTA_ALTURA), pygame.SRCALPHA)
            camada.fill((3, 5, 9, min(225, round((self.tempo_plano - 1.1) * 110))))
            self.cena_tela.blit(camada, (0, 0))
            titulo = self.fonte_titulo.render("B-SIDE", True, (235, 216, 186))
            fim = self.fonte_pequena.render("FIM DA FASE 1", True, (193, 175, 151))
            self.cena_tela.blit(titulo, titulo.get_rect(center=(LARGURA // 2, VISTA_ALTURA // 2 - 6)))
            self.cena_tela.blit(fim, fim.get_rect(center=(LARGURA // 2, VISTA_ALTURA // 2 + 10)))

    def desenhar_cena(self):
        cena = self.plano.cena
        ambiente = "doca" if cena in ("doca", "revelacao") else "loja_manha" if cena == "loja_manha" else cena
        self.ceu(ambiente)
        self.piso(ambiente)
        self.arquitetura(ambiente)
        self.props(ambiente)
        if ambiente == "galpao" and self.atlas_pessoas.existe("MAEL") and self.plano.efeito == "estatica":
            self.desenhar_sprite_mundo("MAEL", 232, 16, 37, self.atlas_pessoas, int(self.tempo_total * 3) % 2, False, (108, 128, 255))
            self.desenhar_olhos_mael()
        self.atores(cena)
        if ambiente in ("doca", "galpao"):
            desloc = round(math.sin(self.tempo_total * 0.12) * 10)
            fog = self.nevoa_vista.copy()
            fog.set_alpha(12 if ambiente == "galpao" else 20)
            self.cena_tela.blit(fog, (desloc, 0))
            self.cena_tela.blit(fog, (-LARGURA + desloc, 0))
        self.luz_dramatica(ambiente)
        self.efeito_plano()
        self.poeira(ambiente)
        self.cena_tela.blit(self.vinheta_vista, (0, 0))
        self.cena_tela.blit(self.granulado, (0, 0))
        self.tela.fill((0, 0, 0))
        self.tela.blit(self.cena_tela, (0, FAIXA_CIMA))
        self.desenhar_letterbox()
        self.transicao()

    def renderizar_texto(self, fonte, texto, cor, x, y, centralizar=False):
        sombra = fonte.render(texto, True, (7, 8, 12))
        imagem = fonte.render(texto, True, cor)
        destino = imagem.get_rect(center=(x, y)) if centralizar else imagem.get_rect(topleft=(x, y))
        self.tela.blit(sombra, (destino.x + 1, destino.y + 1))
        self.tela.blit(imagem, destino)

    def quebrar(self, texto, fonte, largura):
        palavras = texto.split()
        linhas = []
        atual = ""
        for palavra in palavras:
            teste = f"{atual} {palavra}".strip()
            if fonte.size(teste)[0] <= largura or not atual:
                atual = teste
            else:
                linhas.append(atual)
                atual = palavra
        if atual:
            linhas.append(atual)
        return linhas[:2]

    def desenhar_letterbox(self):
        pygame.draw.rect(self.tela, (2, 3, 6), (0, 0, LARGURA, FAIXA_CIMA))
        pygame.draw.rect(self.tela, (2, 3, 6), (0, ALTURA - FAIXA_BAIXO, LARGURA, FAIXA_BAIXO))
        pygame.draw.line(self.tela, (31, 32, 38), (0, FAIXA_CIMA - 1), (LARGURA, FAIXA_CIMA - 1), 1)
        pygame.draw.line(self.tela, (31, 32, 38), (0, ALTURA - FAIXA_BAIXO), (LARGURA, ALTURA - FAIXA_BAIXO), 1)
        self.renderizar_texto(self.fonte_pequena, self.plano.capitulo.upper(), (163, 154, 141), 20, 15)
        ajuda = self.fonte_pequena.render("ESPAÇO / CLIQUE  AVANÇAR     P  PAUSAR     M  ÁUDIO     F11  TELA CHEIA", True, (116, 112, 111))
        self.tela.blit(ajuda, (LARGURA - 20 - ajuda.get_width(), 15))
        pygame.draw.line(self.tela, (33, 31, 33), (20, ALTURA - 4), (LARGURA - 20, ALTURA - 4), 1)
        progresso = (self.indice + min(1.0, self.tempo_plano / self.plano.duracao)) / len(PLANOS)
        pygame.draw.line(self.tela, (218, 160, 84), (20, ALTURA - 4), (20 + round((LARGURA - 40) * progresso), ALTURA - 4), 1)
        if self.plano.falante:
            cor = CORES_FALAS.get(self.plano.falante, BRANCO)
            self.renderizar_texto(self.fonte_pequena, self.plano.falante, cor, 24, ALTURA - FAIXA_BAIXO + 4)
            linhas = self.quebrar(self.plano.texto, self.fonte, LARGURA - 48)
            if len(linhas) == 1:
                self.renderizar_texto(self.fonte, linhas[0], BRANCO, 24, ALTURA - FAIXA_BAIXO + 17)
            else:
                self.renderizar_texto(self.fonte, linhas[0], BRANCO, 24, ALTURA - FAIXA_BAIXO + 15)
                self.renderizar_texto(self.fonte, linhas[1], BRANCO, 24, ALTURA - FAIXA_BAIXO + 27)
        if self.pausado:
            self.renderizar_texto(self.fonte_pequena, "PAUSADO", DOURADO, LARGURA - 72, ALTURA - FAIXA_BAIXO + 5)

    def transicao(self):
        alfa = 0
        if self.tempo_plano < 0.55:
            alfa = round(210 * (1 - self.tempo_plano / 0.55))
        restante = self.plano.duracao - self.tempo_plano
        if restante < 0.38:
            alfa = max(alfa, round(180 * (1 - restante / 0.38)))
        if alfa:
            camada = pygame.Surface((LARGURA, ALTURA), pygame.SRCALPHA)
            camada.fill((0, 0, 0, min(225, alfa)))
            self.tela.blit(camada, (0, 0))

    def apresentar(self):
        largura, altura = self.janela.get_size()
        escala = min(largura / LARGURA, altura / ALTURA)
        destino = (round(LARGURA * escala), round(ALTURA * escala))
        imagem = pygame.transform.scale(self.tela, destino)
        self.janela.fill((0, 0, 0))
        self.janela.blit(imagem, ((largura - destino[0]) // 2, (altura - destino[1]) // 2))
        pygame.display.flip()

    def executar(self):
        while self.rodando:
            dt = min(self.relogio.tick(FPS) / 1000.0, 0.05)
            self.tratar_eventos()
            self.atualizar(dt)
            self.desenhar_cena()
            self.apresentar()
        pygame.quit()


def main():
    argumentos = argparse.ArgumentParser(description="Prévia jogável da cinemática 2.5D da B-Side.")
    argumentos.add_argument("--captura", metavar="ARQUIVO", help="salva um quadro PNG e encerra")
    argumentos.add_argument("--plano", type=int, default=0, help="índice do plano a capturar")
    opcoes = argumentos.parse_args()
    if not (PASTA / "assets" / "tileset-iso.png").exists():
        raise SystemExit("Não encontrei os assets do jogo em jogo-isometrico/assets/.")
    try:
        if opcoes.captura:
            os.environ.setdefault("SDL_VIDEODRIVER", "dummy")
            os.environ["SDL_AUDIODRIVER"] = "dummy"
        cinematica = Cinematica()
        if opcoes.captura:
            cinematica.indice = max(0, min(len(PLANOS) - 1, opcoes.plano))
            cinematica.foco_atual = list(cinematica.plano.foco)
            cinematica.zoom_atual = cinematica.plano.zoom
            cinematica.tempo_plano = 2.2
            cinematica.tempo_total = 9.0
            cinematica.desenhar_cena()
            previa = pygame.transform.scale(cinematica.tela, (1280, 720))
            pygame.image.save(previa, opcoes.captura)
            pygame.quit()
        else:
            cinematica.executar()
    except pygame.error as erro:
        raise SystemExit(f"Não consegui abrir a janela Pygame: {erro}") from erro


if __name__ == "__main__":
    main()
