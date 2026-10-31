"""Candidatos de passagem oeste com calçados dos próprios quadros.

Preserva os quadros atuais. Retira o pé em balanço que ficou rente ao chão
e compõe o trecho inferior de outro quadro da mesma perna anatômica, sem
espelhar nem interpolar pixels. Antes de uso, revisar silhueta e contato.
"""
from pathlib import Path
from PIL import Image, ImageDraw, ImageChops

R = Path(__file__).resolve().parents[1]
C = Path(__file__).resolve().parent / "novos-candidatos"
C.mkdir(parents=True, exist_ok=True)


def mk_mask(size, points):
    result = Image.new("L", size)
    ImageDraw.Draw(result).polygon(points, fill=255)
    return result


def compose(person, phase, donor_phase, dx, dy, erase_points, donor_points):
    saved = R / "edicoes" / "pre-composicao" / person / f"{phase:02}.png"
    if not saved.exists():
        saved = R / "edicoes" / "pos-contato" / person / f"{phase:02}.png"
    src = Image.open(saved).convert("RGBA")
    donor = Image.open(R / person / f"{donor_phase:02}.png").convert("RGBA")
    erase = mk_mask(src.size, erase_points)
    donor_mask = mk_mask(src.size, donor_points)
    residual = src.copy()
    residual.putalpha(ImageChops.multiply(src.getchannel("A"), ImageChops.invert(erase)))
    donor.putalpha(ImageChops.multiply(donor.getchannel("A"), donor_mask))
    moved = Image.new("RGBA", src.size)
    moved.paste(donor, (dx, dy))
    moved.alpha_composite(residual)
    moved.save(C / f"{person}-{phase:02}-passagem.png")


compose("icaro", 3, 4, 55, -10,
        [(135, 384), (181, 384), (177, 410),
         (174, 470), (90, 470), (94, 410)],
        [(144, 349), (184, 349), (181, 392), (168, 432),
         (177, 470), (65, 470), (77, 420), (111, 371)])
