"""Experimentos controlados de recuo do pé de apoio na vista leste.

Cada candidato preserva a metade superior e compõe apenas a perna de apoio
com o mesmo membro anatômico de outra fase. Originais nunca são apagados.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageChops

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent


def polygon(size, points):
    mask = Image.new("L", size)
    ImageDraw.Draw(mask).polygon(points, fill=255)
    return mask


def limpar_ilhas(imagem, limite=500):
    """Remove resíduos deixados no lugar antigo pelo recorte do calçado."""
    pixels = imagem.load()
    vistos = set()
    for y in range(imagem.height):
        for x in range(imagem.width):
            if pixels[x, y][3] <= 32 or (x, y) in vistos:
                continue
            pilha = [(x, y)]
            vistos.add((x, y))
            pontos = []
            while pilha:
                px, py = pilha.pop()
                pontos.append((px, py))
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        nx, ny = px + dx, py + dy
                        if (0 <= nx < imagem.width and 0 <= ny < imagem.height
                                and pixels[nx, ny][3] > 32 and (nx, ny) not in vistos):
                            vistos.add((nx, ny))
                            pilha.append((nx, ny))
            if len(pontos) < limite:
                for px, py in pontos:
                    for dx in (-1, 0, 1):
                        for dy in (-1, 0, 1):
                            nx, ny = px + dx, py + dy
                            if 0 <= nx < imagem.width and 0 <= ny < imagem.height:
                                pixels[nx, ny] = (0, 0, 0, 0)
    return imagem


def candidate(person, target, donor, dx, source_poly, erase_poly):
    original = Image.open(ROOT / person / f"{target:02}.png").convert("RGBA")
    transplante = Image.open(ROOT / person / f"{donor:02}.png").convert("RGBA")
    source_mask = polygon(original.size, source_poly)
    erase_mask = polygon(original.size, erase_poly)
    transplante.putalpha(ImageChops.multiply(transplante.getchannel("A"), source_mask))
    moved = Image.new("RGBA", original.size)
    moved.paste(transplante, (dx, 0))
    resto = original.copy()
    resto.putalpha(ImageChops.multiply(resto.getchannel("A"), ImageChops.invert(erase_mask)))
    moved.alpha_composite(resto)
    moved.save(OUT / f"{person}-{target:02}-apoio-proposta.png")


def remapear_apoio(person, phase, points, shift, start, end):
    """Desloca faixas horizontais do membro, zero no quadril e shift no pé."""
    original = Image.open(ROOT / person / f"{phase:02}.png").convert("RGBA")
    mask = polygon(original.size, points)
    source = original.load()
    m = mask.load()
    moved = Image.new("RGBA", original.size)
    out = moved.load()
    residual = original.copy()
    rem = residual.load()
    for y in range(original.height):
        fraction = max(0, min(1, (y - start) / (end - start)))
        dx = round(shift * fraction)
        for x in range(original.width):
            if m[x, y] and source[x, y][3]:
                nx = x + dx
                if 0 <= nx < original.width:
                    out[nx, y] = source[x, y]
                rem[x, y] = (0, 0, 0, 0)
    moved.alpha_composite(residual)
    moved = limpar_ilhas(moved)
    moved.save(OUT / f"{person}-{phase:02}-remapeado-proposta.png")


# Ícaro 02: esquerda distante recua 38 px no final do apoio.
remapear_apoio("icaro", 2,
                [(184, 330), (237, 330), (270, 365), (295, 415),
                 (312, 479), (179, 480), (180, 428), (186, 381)],
                -38, 330, 465)

remapear_apoio("eva", 2,
                [(183, 318), (243, 318), (279, 356), (316, 416),
                 (333, 479), (180, 480), (174, 430), (182, 371)],
                -50, 318, 465)

remapear_apoio("icaro", 4,
                [(160, 321), (196, 321), (188, 365), (184, 414),
                 (192, 480), (91, 480), (94, 422), (120, 366)],
                16, 321, 465)

remapear_apoio("eva", 4,
                [(157, 320), (196, 320), (191, 365), (185, 416),
                 (196, 480), (88, 480), (90, 425), (118, 366)],
                18, 320, 465)

remapear_apoio("icaro", 6,
                [(184, 330), (241, 330), (281, 375), (305, 431),
                 (317, 480), (170, 480), (173, 428), (181, 375)],
                -26, 330, 465)

remapear_apoio("eva", 6,
                [(175, 320), (236, 320), (275, 370), (310, 430),
                 (321, 480), (164, 480), (165, 430), (172, 374)],
                -32, 320, 465)
