"""Candidatos para recuo do pé de apoio de Eva em 02 e 06 (oeste).

Remapeia exclusivamente faixas horizontais das pernas já existentes, com
deslocamento crescente de zero no quadril a 20 px no calçado. Não altera
tronco, rosto, roupa superior, acessórios, paleta ou transparência.
"""
from pathlib import Path
from PIL import Image, ImageDraw

R = Path(__file__).resolve().parents[1]
C = Path(__file__).resolve().parent / "novos-candidatos"
C.mkdir(parents=True, exist_ok=True)

PLANOS = {
    2: {
        "points": [(158, 312), (216, 312), (207, 370), (194, 429),
                   (190, 480), (79, 480), (82, 420), (115, 365)],
        "start": 312,
    },
    6: {
        "points": [(151, 319), (214, 319), (204, 370), (194, 427),
                   (190, 480), (68, 480), (72, 419), (109, 365)],
        "start": 319,
    },
}

for phase, plan in PLANOS.items():
    original = Image.open(R / "eva" / f"{phase:02}.png").convert("RGBA")
    mask = Image.new("L", original.size)
    ImageDraw.Draw(mask).polygon(plan["points"], fill=255)
    src, m = original.load(), mask.load()
    output = original.copy()
    out = output.load()
    lifted = []
    for y in range(original.height):
        dx = round(20 * max(0, min(1, (y - plan["start"]) / (465 - plan["start"]))))
        for x in range(original.width):
            if m[x, y] and src[x, y][3]:
                lifted.append((x + dx, y, src[x, y]))
                out[x, y] = (0, 0, 0, 0)
    for x, y, pixel in lifted:
        if 0 <= x < original.width:
            out[x, y] = pixel
    output.save(C / f"eva-{phase:02}-apoio.png")
