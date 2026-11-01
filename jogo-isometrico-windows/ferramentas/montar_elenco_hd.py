#!/usr/bin/env python3
"""Junta as colunas 384x4096 do elenco em alta resolução num atlas só.

Coluna 0: agente (gerar_agente.py); coluna 1: anjo (gerar_anjo.py); coluna 2:
poses extras do anjo, se existirem. Cada linha é uma direção, na ordem do Ícaro.
O jogo carrega assets/elenco-hd.png e reduz como a sprite do Ícaro (AF_HD).

Uso: python3 ferramentas/montar_elenco_hd.py   (ou `make arte`, depois dos outros)
"""
from pathlib import Path

from PIL import Image

RAIZ = Path(__file__).resolve().parent.parent
COLUNAS = ["agente-parado.png", "anjo-parado.png", "anjo-poses.png"]


def main():
    colunas = [Image.open(RAIZ / "assets" / c) for c in COLUNAS if (RAIZ / "assets" / c).exists()]
    atlas = Image.new("RGBA", (384 * len(colunas), 4096), (0, 0, 0, 0))
    for k, c in enumerate(colunas):
        atlas.alpha_composite(c.convert("RGBA"), (k * 384, 0))
    atlas.save(RAIZ / "assets" / "elenco-hd.png")
    print(f"elenco-hd.png {atlas.width}x{atlas.height}: {len(colunas)} colunas")


if __name__ == "__main__":
    main()
