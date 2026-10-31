"""Recalcula metadados e prévias a partir das células noroeste atuais."""
from pathlib import Path
from PIL import Image, ImageDraw
import hashlib
import json

PASTA = Path(__file__).resolve().parent
tecnica = json.loads((PASTA / "tecnica.json").read_text())

for personagem in ("icaro", "eva"):
    quadros = []
    for fase in range(1, 9):
        imagem = Image.open(PASTA / personagem / f"{fase:02}.png")
        assert imagem.size == (384, 512) and imagem.mode == "RGBA"
        caixa = imagem.getbbox()
        assert caixa and caixa[0] > 3 and caixa[1] > 3
        assert caixa[2] < 381 and caixa[3] < 509
        quadros.append(imagem.copy())
        item = tecnica[personagem][fase - 1]
        item["bbox"] = list(caixa)
        item["sha256"] = hashlib.sha256(imagem.tobytes()).hexdigest()
        if personagem == "icaro" and fase in (1, 8):
            item["pos_processamento"] = "pulseira recomposta no pulso esquerdo anatômico, sem espelhamento"

    for tema, fundo in (("claro", "#efeee8"), ("escuro", "#252930")):
        prancha = Image.new("RGB", (1536, 1080), fundo)
        texto = ImageDraw.Draw(prancha)
        for indice, imagem in enumerate(quadros):
            x, y = (indice % 4) * 384, (indice // 4) * 540
            prancha.paste(imagem, (x, y + 24), imagem)
            texto.text((x + 12, y + 8), f"{personagem} NO {indice + 1:02}",
                       fill="#000000" if tema == "claro" else "#ffffff")
        prancha.save(PASTA / f"{personagem}-{tema}.png")

    for tempo in (100, 400):
        cenas = []
        for imagem in quadros:
            cena = Image.new("RGB", (384, 512), "#efeee8")
            cena.paste(imagem, (0, 0), imagem)
            cenas.append(cena)
        cenas[0].save(PASTA / f"{personagem}-{tempo}ms.gif", save_all=True,
                      append_images=cenas[1:], duration=tempo, loop=0)

    assert len({item["sha256"] for item in tecnica[personagem]}) == 8

(PASTA / "tecnica.json").write_text(json.dumps(tecnica, ensure_ascii=False, indent=2) + "\n")
