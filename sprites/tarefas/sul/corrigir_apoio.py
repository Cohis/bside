"""Candidatos de correção local das pernas de apoio na vista frontal.

Reposiciona linhas de pixels do segmento inferior com vizinho mais próximo,
ancorando o quadril. Não mexe na outra perna, tronco, cabelo ou acessórios.
Os candidatos só substituem os quadros depois de revisão visual.
"""

from pathlib import Path
from PIL import Image, ImageDraw

RAIZ = Path(__file__).resolve().parent
ANCORA_Y = 335
# fase: (lado na tela, borda inferior atual, borda desejada)
METAS = {
    "icaro": {1: ("esquerdo", 435, 450), 4: ("direito", 450, 458),
              5: ("direito", 443, 450), 8: ("esquerdo", 434, 458)},
    "eva": {1: ("esquerdo", 440, 450), 4: ("direito", 466, 458),
            5: ("direito", 439, 450), 8: ("esquerdo", 438, 458)},
}


def editar(imagem: Image.Image, lado: str, antigo: int, novo: int) -> Image.Image:
    saida = imagem.copy()
    faixa = range(115, 191) if lado == "esquerdo" else range(194, 268)
    for y in range(ANCORA_Y, 491):
        for x in faixa:
            saida.putpixel((x, y), (0, 0, 0, 0))
    for y in range(ANCORA_Y, novo + 1):
        origem_y = round(ANCORA_Y + (y - ANCORA_Y) * (antigo - ANCORA_Y) / (novo - ANCORA_Y))
        for x in faixa:
            saida.putpixel((x, y), imagem.getpixel((x, origem_y)))
    return saida


def prancha(personagem: str, pasta: Path) -> None:
    quadro = Image.new("RGBA", (384 * 4, 512 * 2), "#eeeae4")
    desenhar = ImageDraw.Draw(quadro)
    for fase in range(1, 9):
        caminho = pasta / f"{fase:02}.png" if fase in METAS[personagem] else RAIZ / personagem / f"{fase:02}.png"
        imagem = Image.open(caminho).convert("RGBA")
        x, y = ((fase - 1) % 4) * 384, ((fase - 1) // 4) * 512
        quadro.alpha_composite(imagem, (x, y))
        desenhar.text((x + 6, y + 6), f"{personagem} {fase:02}", fill="#201c24")
    quadro.save(pasta / "ciclo-candidato.png")


for personagem, fases in METAS.items():
    pasta = RAIZ / "candidatos-apoio" / personagem
    pasta.mkdir(parents=True, exist_ok=True)
    for fase, (lado, antigo, novo) in fases.items():
        entrada = Image.open(RAIZ / personagem / f"{fase:02}.png").convert("RGBA")
        editar(entrada, lado, antigo, novo).save(pasta / f"{fase:02}.png")
    prancha(personagem, pasta)
