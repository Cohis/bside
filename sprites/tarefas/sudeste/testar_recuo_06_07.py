"""Ensaios reversíveis de recuo do pé de apoio nos quadros 06 e 07."""
from pathlib import Path
from PIL import Image, ImageDraw

RAIZ = Path(__file__).resolve().parent
SAIDA = RAIZ / "candidatos-recuo-06-07"
SAIDA.mkdir(exist_ok=True)

PLANOS = {
    ("icaro", 6): ([(178, 328), (240, 328), (248, 362), (267, 419), (290, 484), (176, 484), (185, 405)], -18),
    ("icaro", 7): ([(149, 329), (221, 329), (221, 362), (208, 419), (218, 484), (119, 484), (130, 411)], -15),
    ("eva", 6): ([(174, 329), (245, 329), (257, 400), (285, 484), (165, 484), (168, 410)], -21),
    ("eva", 7): ([(151, 329), (221, 329), (220, 405), (222, 484), (124, 484), (135, 413)], -17),
}

for (pessoa, fase), (poligono, deslocamento) in PLANOS.items():
    origem = Image.open(RAIZ / pessoa / f"{fase:02}.png").convert("RGBA")
    mascara = Image.new("L", origem.size)
    ImageDraw.Draw(mascara).polygon(poligono, fill=255)
    entrada, selecionados = origem.load(), mascara.load()
    resultado = origem.copy()
    saida = resultado.load()
    movidos = []
    for y in range(328, 484):
        dx = round(deslocamento * max(0, min(1, (y - 328) / 140)))
        for x in range(384):
            if selecionados[x, y] and entrada[x, y][3]:
                movidos.append((x + dx, y, entrada[x, y]))
                saida[x, y] = (0, 0, 0, 0)
    for x, y, pixel in movidos:
        if 0 <= x < 384:
            saida[x, y] = pixel
    resultado.save(SAIDA / f"{pessoa}-{fase:02}-candidato.png")

# Alternativa para 07: deslocar a faixa inferior inteira, sem recorte que rache
# a perna em balanço ou deixe resíduos da antiga silhueta.
for pessoa, deslocamento in (("icaro", -15), ("eva", -17)):
    origem = Image.open(RAIZ / pessoa / "07.png").convert("RGBA")
    resultado = Image.new("RGBA", origem.size)
    for y in range(512):
        dx = round(deslocamento * max(0, min(1, (y - 328) / 140)))
        linha = origem.crop((0, y, 384, y + 1))
        resultado.paste(linha, (dx, y))
    resultado.save(SAIDA / f"{pessoa}-07-faixa.png")

for pessoa in ("icaro", "eva"):
    prancha = Image.new("RGB", (384 * 4, 512 * 2), "#efefeb")
    for linha in range(2):
        for coluna, fase in enumerate(range(5, 9)):
            sufixo = "faixa" if fase == 7 else "candidato"
            variante = SAIDA / f"{pessoa}-{fase:02}-{sufixo}.png"
            arquivo = variante if linha and variante.exists() else RAIZ / pessoa / f"{fase:02}.png"
            celula = Image.open(arquivo).convert("RGBA")
            fundo = Image.new("RGB", celula.size, "#efefeb")
            fundo.paste(celula, (0, 0), celula)
            ImageDraw.Draw(fundo).line((0, 480, 383, 480), fill="teal")
            prancha.paste(fundo, (coluna * 384, linha * 512))
    prancha.save(SAIDA / f"{pessoa}-comparacao-05-08.png")
