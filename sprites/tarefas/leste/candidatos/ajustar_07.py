"""Candidatos controlados para a passagem esquerda na direção leste.

Remove apenas a parte visível da perna esquerda que ficou atrás no quadro 07
e transplanta rigidamente a silhueta completa de tênis flexionado do quadro 03
do mesmo personagem para o lado da frente, atrás da perna direita de apoio.
Nenhum pixel é interpolado, espelhado ou redesenhado. Os pontos foram
definidos após inspeção ampliada com grade.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageChops

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(__file__).resolve().parent

CONFIG = {
    "icaro": {
        "polygon": [(175, 340), (156, 340), (135, 349), (130, 365),
                    (130, 377), (114, 381), (111, 397), (118, 414),
                    (128, 426), (144, 440), (171, 441), (176, 434),
                    (178, 419), (178, 400), (179, 381), (177, 353)],
        "patch_polygon": [(181, 288), (212, 288), (232, 309),
                          (251, 332), (263, 351), (264, 368),
                          (250, 390), (249, 404), (255, 424),
                          (251, 443), (196, 447), (171, 426),
                          (172, 393), (185, 369), (190, 344),
                          (188, 312)],
        "patch_shift": (20, 0),
        "support_polygon": [(174, 317), (230, 317), (251, 371),
                            (267, 431), (281, 480), (167, 480),
                            (170, 426), (178, 376)],
        "support_shift": -42,
        "support_start": 317,
    },
    "eva": {
        "polygon": [(161, 373), (136, 373), (125, 382), (120, 400),
                    (113, 414), (112, 434), (123, 450), (139, 460),
                    (164, 460), (165, 446), (164, 429), (164, 410),
                    (163, 391)],
        "patch_polygon": [(174, 285), (212, 285), (236, 301),
                          (255, 320), (262, 345), (258, 373),
                          (262, 389), (294, 396), (297, 414),
                          (282, 437), (227, 444), (195, 429),
                          (185, 397), (184, 365), (188, 335),
                          (180, 309)],
        "patch_shift": (-10, 0),
        "support_polygon": [(165, 311), (232, 311), (252, 373),
                            (278, 430), (283, 480), (160, 480),
                            (161, 428), (169, 372)],
        "support_shift": -20,
        "support_start": 311,
    },
}


def remover_residuos_isolados(im):
    """Apaga só ilhas de até 100 px desconectadas da figura principal."""
    alpha = im.getchannel("A")
    pix = alpha.load()
    vistos = set()
    for y in range(im.height):
        for x in range(im.width):
            if pix[x, y] <= 32 or (x, y) in vistos:
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
                        if (0 <= nx < im.width and 0 <= ny < im.height
                                and pix[nx, ny] > 32 and (nx, ny) not in vistos):
                            vistos.add((nx, ny))
                            pilha.append((nx, ny))
            if len(pontos) <= 100:
                for px, py in pontos:
                    # Inclui a franja alfa adjacente da pequena ilha.
                    for dx in (-1, 0, 1):
                        for dy in (-1, 0, 1):
                            nx, ny = px + dx, py + dy
                            if 0 <= nx < im.width and 0 <= ny < im.height:
                                pix[nx, ny] = 0
    im.putalpha(alpha)
    return im

for person, spec in CONFIG.items():
    src = Image.open(ROOT / "registros" / "edicoes" / f"{person}-07-antes.png").convert("RGBA")
    mask = Image.new("L", src.size)
    ImageDraw.Draw(mask).polygon(spec["polygon"], fill=255)
    alpha = src.getchannel("A")
    part = Image.open(ROOT / person / "03.png").convert("RGBA")
    part_mask = Image.new("L", src.size)
    ImageDraw.Draw(part_mask).polygon(spec["patch_polygon"], fill=255)
    part.putalpha(ImageChops.multiply(part.getchannel("A"), part_mask))
    shifted = Image.new("RGBA", src.size)
    shifted.paste(part, spec["patch_shift"])

    sem_balanco = src.copy()
    sem_balanco.putalpha(ImageChops.multiply(alpha, ImageChops.invert(mask)))
    apoio_mask = Image.new("L", src.size)
    ImageDraw.Draw(apoio_mask).polygon(spec["support_polygon"], fill=255)
    apoio_src = sem_balanco.load()
    apoio = Image.new("RGBA", src.size)
    apoio_px = apoio.load()
    for y in range(src.height):
        factor = max(0, min(1, (y - spec["support_start"]) / (465 - spec["support_start"])))
        dx = round(spec["support_shift"] * factor)
        for x in range(src.width):
            if apoio_mask.getpixel((x, y)) and apoio_src[x, y][3]:
                nx = x + dx
                if 0 <= nx < src.width:
                    apoio_px[nx, y] = apoio_src[x, y]
    restante = sem_balanco.copy()
    restante.putalpha(ImageChops.multiply(sem_balanco.getchannel("A"),
                                         ImageChops.invert(apoio_mask)))
    shifted.alpha_composite(apoio)
    shifted.alpha_composite(restante)
    shifted = remover_residuos_isolados(shifted)
    shifted.save(OUT / f"{person}-07-proposta.png")
