"""Gera evidências de caminhada no lugar sobre chão marcado.

O deslocamento é o vetor projetado do guia noroeste; esta rotina não altera
nenhum PNG de produção. A linha de chão e a malha são apenas elementos de QA.
"""
from pathlib import Path
from PIL import Image, ImageDraw
import json

PASTA = Path(__file__).resolve().parent
GUIA = json.loads((PASTA.parent.parent / "guias/noroeste/01.json").read_text())
DX, DY = GUIA["deslocamento_por_quadro_projetado"]
SAIDA = PASTA / "registros" / "chao-marcado"
SAIDA.mkdir(parents=True, exist_ok=True)

for personagem in ("icaro", "eva"):
    quadros = []
    for indice in range(8):
        cena = Image.new("RGB", (384, 512), "#efeee8")
        d = ImageDraw.Draw(cena)
        # A malha recua no sentido contrário ao movimento do personagem.
        xoff, yoff = (-DX * indice, -DY * indice)
        for coluna in range(-6, 12):
            x = round(coluna * 48 + xoff)
            d.line((x, 440, x, 511), fill="#bbb9ad", width=1)
        for linha in range(-2, 5):
            y = round(480 + linha * 24 + yoff)
            d.line((0, y, 383, y), fill="#bbb9ad", width=1)
        d.line((0, 480, 383, 480), fill="#918e80", width=2)
        d.ellipse((189, 477, 195, 483), fill="#d9403c")
        personagem_png = Image.open(PASTA / personagem / f"{indice + 1:02}.png").convert("RGBA")
        cena.paste(personagem_png, (0, 0), personagem_png)
        d = ImageDraw.Draw(cena)
        d.text((8, 8), f"NO {indice + 1:02} | solo {round(xoff)},{round(yoff)}", fill="#202020")
        quadros.append(cena)
    for tempo in (100, 400):
        quadros[0].save(SAIDA / f"{personagem}-{tempo}ms.gif", save_all=True,
                        append_images=quadros[1:], duration=tempo, loop=0)
    prancha = Image.new("RGB", (1536, 1024), "#efeee8")
    for indice, quadro in enumerate(quadros):
        prancha.paste(quadro, ((indice % 4) * 384, (indice // 4) * 512))
    prancha.save(SAIDA / f"{personagem}-prancha.png")
