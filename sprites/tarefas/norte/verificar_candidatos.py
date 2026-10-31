"""Mede os candidatos norte e produz prévias temporais com chão marcado."""

from pathlib import Path
import hashlib
import json

import numpy as np
from PIL import Image, ImageDraw


PASTA = Path(__file__).resolve().parent
CANDIDATOS = PASTA / "candidatos_v2"
CENTROS_PES = {"esquerda": (145, 180), "direita": (205, 240)}


def extremo_pe(imagem: Image.Image, lado: str) -> int:
    alfa = np.asarray(imagem.getchannel("A"))
    x0, x1 = CENTROS_PES[lado]
    posicoes = np.nonzero(alfa[380:, x0:x1] > 127)[0]
    if not posicoes.size:
        raise ValueError(f"Pé {lado} não encontrado")
    return int(posicoes.max() + 380)


def quadro_preview(imagem: Image.Image, indice: int) -> Image.Image:
    fundo = Image.new("RGB", (384, 512), "#e8e3dc")
    caneta = ImageDraw.Draw(fundo)
    # O chão desloca 6 px por fase, de modo que o ponto de contato de apoio
    # deve acompanhá-lo se não houver patinação aparente.
    deslocamento = 6 * indice
    for y in range(-100 + deslocamento, 600, 32):
        caneta.line((0, y, 383, y), fill="#d0c6bc", width=1)
    caneta.line((192, 0, 192, 511), fill="#d7cfc7", width=1)
    fundo.paste(imagem, (0, 0), imagem)
    caneta.text((8, 8), f"NORTE  {indice+1:02}/08", fill="#201e1c")
    return fundo


def main() -> None:
    relatorio = {"estado": "candidatos não publicados", "direcao": "norte", "personagens": {}}
    for personagem in ("icaro", "eva"):
        pngs = [CANDIDATOS / f"{personagem}-{q:02}.png" for q in range(1, 9)]
        imagens = [Image.open(p).convert("RGBA") for p in pngs]
        origem = PASTA / "originais_edicao" / personagem
        if not origem.exists():
            origem = PASTA / personagem
        originais = [Image.open(origem / f"{q:02}.png").convert("RGBA") for q in range(1, 9)]
        cor_original = set()
        cor_candidato = set()
        medicao = []
        for q, (p, imagem, original) in enumerate(zip(pngs, imagens, originais), 1):
            if imagem.size != (384, 512):
                raise ValueError(f"Dimensão inválida: {p}")
            cor_original.update(original.get_flattened_data())
            cor_candidato.update(imagem.get_flattened_data())
            caixa = imagem.getchannel("A").getbbox()
            if caixa is None or min(caixa[0], caixa[1], 384 - caixa[2], 512 - caixa[3]) < 8:
                raise ValueError(f"Vazio ou borda invadida: {p}: {caixa}")
            lado = "esquerda" if q <= 4 else "direita"
            medicao.append({
                "quadro": q, "apoio": lado, "ponta_apoio_y": extremo_pe(imagem, lado),
                "ponta_balanco_y": extremo_pe(imagem, "direita" if lado == "esquerda" else "esquerda"),
                "caixa": list(caixa), "sha256": hashlib.sha256(p.read_bytes()).hexdigest(),
            })
        if not cor_candidato <= cor_original:
            raise ValueError(f"Cor nova não autorizada em {personagem}")
        if len({m["sha256"] for m in medicao}) != 8:
            raise ValueError(f"Quadros duplicados em {personagem}")
        for inicio in (0, 4):
            y = [m["ponta_apoio_y"] for m in medicao[inicio:inicio+4]]
            if not (y[0] < y[1] < y[2] < y[3]):
                raise ValueError(f"Apoio não recua em {personagem} {inicio+1}-{inicio+4}: {y}")
        fundos = [quadro_preview(imagem, i) for i, imagem in enumerate(imagens)]
        for duracao in (100, 400):
            fundos[0].save(CANDIDATOS / f"{personagem}-chao-{duracao}ms.gif",
                            save_all=True, append_images=fundos[1:], duration=duracao,
                            loop=0, optimize=False, disposal=2)
        relatorio["personagens"][personagem] = {"quadros": medicao,
           "apoios_esquerda": [m["ponta_apoio_y"] for m in medicao[:4]],
           "apoios_direita": [m["ponta_apoio_y"] for m in medicao[4:]],
           "paleta_somente_original": True,
           "previews": [f"{personagem}-chao-100ms.gif", f"{personagem}-chao-400ms.gif"]}
    (CANDIDATOS / "qa.json").write_text(json.dumps(relatorio, ensure_ascii=False, indent=2) + "\n")


if __name__ == "__main__":
    main()
