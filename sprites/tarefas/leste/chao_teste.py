"""Prévia local de patinação com chão marcado a 40 px por fase."""
from pathlib import Path
from PIL import Image, ImageDraw

raiz = Path(__file__).resolve().parent
for pessoa in ("icaro", "eva"):
    frames = []
    for i in range(8):
        fundo = Image.new("RGB", (384, 512), (239, 237, 229))
        desenho = ImageDraw.Draw(fundo)
        desenho.line((0, 480, 383, 480), fill=(128, 120, 104), width=2)
        # Marcas principais a cada 80 px e secundárias a cada 40 px.
        for mundo_x in range(-320, 841, 40):
            x = mundo_x - i * 40
            if not 0 <= x < 384:
                continue
            principal = mundo_x % 80 == 0
            desenho.line((x, 480, x, 510 if principal else 498),
                          fill=(142, 132, 111), width=2 if principal else 1)
            if principal:
                desenho.text((x + 2, 499), str(mundo_x), fill=(100, 92, 77))
        sprite = Image.open(raiz / pessoa / f"{i + 1:02}.png").convert("RGBA")
        fundo.paste(sprite, (0, 0), sprite)
        desenho = ImageDraw.Draw(fundo)
        desenho.text((8, 8), f"{pessoa.upper()} LESTE {i + 1:02}", fill=(80, 75, 65))
        frames.append(fundo)
    frames[0].save(raiz / f"{pessoa}-chao-teste.gif", save_all=True,
                   append_images=frames[1:], duration=100, loop=0)
    frames[0].save(raiz / f"{pessoa}-chao-teste-lento.gif", save_all=True,
                   append_images=frames[1:], duration=400, loop=0)
