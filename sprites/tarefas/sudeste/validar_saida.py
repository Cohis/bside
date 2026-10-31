"""Atualiza artefatos de inspeção sem alterar os PNGs individuais."""

from pathlib import Path
from PIL import Image, ImageDraw
import hashlib
import json

RAIZ = Path(__file__).parent
SOLO = 480


def marcar_solo(desenho, x, y, fase):
    """Linha e marcas móveis para revelar deslize; 24 px/fase é só teste."""
    desenho.line((x, y + SOLO, x + 383, y + SOLO), fill="#30a7ab", width=1)
    for marca in range(-384 - fase * 24, 768, 64):
        xm = x + marca
        if x <= xm < x + 384:
            desenho.line((xm, y + SOLO + 1, xm, y + SOLO + 11), fill="#bb7333", width=1)

for personagem in ("icaro", "eva"):
    quadros = [Image.open(RAIZ / personagem / f"{fase:02}.png").convert("RGBA") for fase in range(1, 9)]
    tecnica = []
    for fase, quadro in enumerate(quadros, 1):
        caixa = quadro.getbbox()
        tecnica.append({
            "fase": fase,
            "bbox": caixa,
            "rgba": quadro.mode == "RGBA",
            "dimensoes": list(quadro.size),
            "margens_ok": caixa[0] > 3 and caixa[1] > 3 and caixa[2] < 381 and caixa[3] < 509,
            "sha256_pixels": hashlib.sha256(quadro.tobytes()).hexdigest(),
            "pixels_transparentes": quadro.getchannel("A").histogram()[0],
            "desvio_extremo_solo_px": caixa[3] - SOLO,
        })
    (RAIZ / personagem / "tecnica.json").write_text(json.dumps(tecnica, ensure_ascii=False, indent=2) + "\n")

    for nome, cor in (("claro", "#ededeb"), ("escuro", "#20252b")):
        prancha = Image.new("RGB", (1536, 1084), cor)
        desenho = ImageDraw.Draw(prancha)
        for indice, quadro in enumerate(quadros):
            x, y = (indice % 4) * 384, (indice // 4) * 542
            marcar_solo(desenho, x, y, indice)
            prancha.paste(quadro, (x, y), quadro)
            desenho.text((x + 12, y + 515), f"{personagem} / {indice + 1:02} | chao 480", fill="#bb7333")
        prancha.save(RAIZ / f"{personagem}-{nome}.png")
        prancha.save(RAIZ / f"{personagem}-{nome}-solo.png")

    quadros_gif = []
    for indice, quadro in enumerate(quadros):
        tela = Image.new("RGB", (384, 512), "#dddddd")
        marcar_solo(ImageDraw.Draw(tela), 0, 0, indice)
        tela.paste(quadro, (0, 0), quadro)
        quadros_gif.append(tela)
    for nome, duracao in (("normal", 100), ("lento", 400)):
        quadros_gif[0].save(
            RAIZ / f"{personagem}-{nome}.gif",
            save_all=True,
            append_images=quadros_gif[1:],
            duration=duracao,
            loop=0,
            disposal=2,
        )
