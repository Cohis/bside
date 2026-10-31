"""Ensaios de composição local da caminhada noroeste.

Os quadros originais ficam em originais/. As operações trabalham exclusivamente
com pixels das poses desta direção e amostragem pelo vizinho mais próximo.
"""
from pathlib import Path
from PIL import Image

PASTA = Path(__file__).resolve().parent
ORIGINAIS = PASTA / "originais"
PREVIA = PASTA / "previa-correcao"
PREVIA.mkdir(exist_ok=True)


def ler(personagem, fase):
    origem = ORIGINAIS / personagem / f"{fase:02}.png"
    if not origem.exists():
        origem.parent.mkdir(parents=True, exist_ok=True)
        atual = PASTA / personagem / f"{fase:02}.png"
        origem.write_bytes(atual.read_bytes())
    return Image.open(origem).convert("RGBA")


def transferir_parte_superior(destino, origem, corte, deslocamento_y=0):
    """Substitui a pose dos braços junto com o tronco, sem refletir a imagem."""
    resultado = destino.copy()
    pixels = resultado.load()
    for y in range(corte):
        for x in range(384):
            pixels[x, y] = (0, 0, 0, 0)
    parte = Image.new("RGBA", (384, 512))
    parte.paste(origem, (0, deslocamento_y))
    mascara = Image.new("L", (384, 512))
    mp = mascara.load()
    for y in range(min(512, corte + 10)):
        for x in range(384):
            mp[x, y] = 255
    resultado.paste(parte, (0, 0), mascara)
    return resultado


def trazer_pe_para_passagem(imagem, inicio, fim, recuo):
    """Recompõe a perna distante com recuo crescente do pé para sob o quadril."""
    original = imagem.copy()
    saida = imagem.copy()
    src, dst = original.load(), saida.load()
    # A metade direita desta vista contém a perna em balanço. O recorte deixa
    # intocada a perna de apoio (esquerda na tela) e toda a parte superior.
    for y in range(inicio, fim):
        t = (y - inicio) / max(1, fim - inicio)
        limite = round(211 + 3 * t)
        for x in range(limite, 384):
            dst[x, y] = (0, 0, 0, 0)
    for y in range(inicio, fim):
        t = (y - inicio) / max(1, fim - inicio)
        dx = round(recuo * t)
        limite = round(211 + 3 * t)
        for x in range(limite, 384):
            rgba = src[x, y]
            nx = x - dx
            if rgba[3] and 0 <= nx < 384 and dst[nx, y][3] == 0:
                dst[nx, y] = rgba
    return saida


for personagem in ("icaro", "eva"):
    corte = 328 if personagem == "icaro" else 281
    passagem = 320 if personagem == "icaro" else 285
    for fase in range(1, 9):
        atual = ler(personagem, fase)
        if fase == 1:
            atual = transferir_parte_superior(atual, ler(personagem, 3), corte)
        elif fase == 8:
            atual = transferir_parte_superior(atual, ler(personagem, 7), corte, -2)
        elif fase in (3, 7):
            atual = trazer_pe_para_passagem(atual, passagem, 495, 42)
        elif fase == 6:
            # Contato direito já está expresso na fase 05. A recepção mantém
            # esse apoio enquanto o tronco desce no quadro 06.
            contato = ler(personagem, 5)
            parte = contato.crop((0, corte, 384, 512))
            for y in range(corte, 512):
                for x in range(384):
                    atual.putpixel((x, y), (0, 0, 0, 0))
            atual.alpha_composite(parte, (0, corte + 4))
        destino = PREVIA / personagem / f"{fase:02}.png"
        destino.parent.mkdir(parents=True, exist_ok=True)
        atual.save(destino)
