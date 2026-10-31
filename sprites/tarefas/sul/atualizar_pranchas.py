"""Atualiza pranchas e GIFs de revisão a partir dos quadros selecionados."""

from pathlib import Path
from PIL import Image, ImageDraw

RAIZ = Path(__file__).resolve().parent
FUNDO = "#eeeae4"

for personagem in ("icaro", "eva"):
    originais = [Image.open(RAIZ / personagem / f"{i:02}.png").convert("RGBA") for i in range(1, 9)]
    quadro = Image.new("RGBA", (384 * 4, 512 * 2), FUNDO)
    desenhar = ImageDraw.Draw(quadro)
    animacao = []
    for indice, imagem in enumerate(originais):
        x, y = (indice % 4) * 384, (indice // 4) * 512
        quadro.alpha_composite(imagem, (x, y))
        desenhar.text((x + 6, y + 6), f"{personagem} {indice + 1:02}", fill="#201c24")
        fundo = Image.new("RGBA", (384, 512), FUNDO)
        fundo.alpha_composite(imagem)
        animacao.append(fundo.convert("RGB"))
    quadro.save(RAIZ / f"{personagem}-ciclo.png")
    for atraso, nome in ((100, "normal"), (400, "lento")):
        animacao[0].save(RAIZ / f"{personagem}-{nome}.gif", save_all=True,
                         append_images=animacao[1:], duration=atraso, loop=0,
                         disposal=2, optimize=False)
