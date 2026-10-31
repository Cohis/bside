"""Corrige a lateral anatômica da pulseira em Ícaro 01/08.

Lê os PNGs originais preservados, remove a pulseira do pulso distante
com pixels da própria pele e compõe a pulseira esquerda da fase 05.
Não altera a pose dos braços; esse defeito segue indicado na revisão.
"""
from pathlib import Path
from PIL import Image
import json

PASTA = Path(__file__).resolve().parent
ORIGINAIS = PASTA / "originais" / "icaro"

fonte = Image.open(ORIGINAIS / "05.png").convert("RGBA")
pulseira = fonte.crop((102, 265, 124, 287))

for fase, intervalo_y, posicao in (
    (1, (294, 319), (116, 296)),
    (8, (292, 316), (94, 301)),
):
    imagem = Image.open(ORIGINAIS / f"{fase:02}.png").convert("RGBA")
    pixels = imagem.load()
    fim = intervalo_y[1]
    for y in range(*intervalo_y):
        ocupados = [x for x in range(250, 282) if pixels[x, y][3] > 180]
        if not ocupados:
            continue
        esquerda, direita = min(ocupados), max(ocupados)
        for x in range(max(250, esquerda + 2), min(282, direita - 1)):
            if pixels[x, y][3] <= 180:
                continue
            # Reusa a cor local da mão/antebraço, preservando o contorno externo.
            cor = pixels[x, min(340, fim + 6)]
            if cor[0] <= 100 or cor[1] <= 60:
                cor = (219, 148, 106, 255)
            pixels[x, y] = (*cor[:3], 255)
    imagem.paste(pulseira, posicao, pulseira)
    imagem.save(PASTA / "icaro" / f"{fase:02}.png")
    transformacao = PASTA / "icaro" / f"{fase:02}.transformacao.json"
    dados = json.loads(transformacao.read_text())
    dados["pos_processamento"] = {
        "tipo": "composicao_local_nearest",
        "script": "corrigir-pulseira.py",
        "fonte": "originais/icaro/05.png",
        "alvo": "pulso esquerdo anatômico",
        "alterou_pose": False,
    }
    transformacao.write_text(json.dumps(dados, ensure_ascii=False, indent=2) + "\n")
