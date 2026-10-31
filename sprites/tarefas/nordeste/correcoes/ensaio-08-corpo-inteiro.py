"""Reproduz o enxerto integral de pernas 07→08, rejeitado na revisão."""
from pathlib import Path
from PIL import Image, ImageDraw

p = Path(__file__).resolve().parent.parent
configs = {
    'icaro': (300, [(157, 300), (232, 300), (233, 345), (235, 385),
                    (246, 420), (261, 484), (155, 484), (153, 420),
                    (157, 385), (157, 345)], [(90, 300, 150, 326)]),
    'eva': (272, [(154, 272), (231, 272), (234, 345), (239, 390),
                  (252, 440), (275, 490), (155, 490), (154, 440),
                  (155, 390), (153, 345)],
            [(90, 272, 152, 340), (240, 272, 310, 327)]),
}
for personagem, (corte, contorno, bracos) in configs.items():
    original = Image.open(p / personagem / '08.png').convert('RGBA')
    doador = Image.open(p / personagem / '07.png').convert('RGBA')
    resultado = original.copy()
    for y in range(corte, 512):
        for x in range(90, 310):
            resultado.putpixel((x, y), (0, 0, 0, 0))
    mascara = Image.new('L', resultado.size, 0)
    ImageDraw.Draw(mascara).polygon(contorno, fill=255)
    alfa = Image.composite(doador.getchannel('A'), Image.new('L', resultado.size), mascara)
    enxerto = Image.new('RGBA', resultado.size)
    enxerto.paste(doador, (0, 0), alfa)
    resultado.alpha_composite(enxerto)
    for caixa in bracos:
        recorte = original.crop(caixa)
        resultado.paste(recorte, caixa[:2], recorte)
    candidato = p / 'correcoes' / f'{personagem}-08-transplante-v3.png'
    resultado.save(candidato)
    fundo = Image.new('RGBA', resultado.size, '#eee')
    fundo.alpha_composite(resultado)
    fundo.convert('RGB').save(p / 'correcoes' / f'{personagem}-08-transplante-v3-fundo.png')
