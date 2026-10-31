"""Candidatos de correção local para o apoio na vista norte.

O código trabalha em pixels RGBA por vizinho mais próximo. Apenas a região das
calças/pernas (abaixo de y=320) é remapeada; rosto, cabelo, roupa e acessórios
continuam exatamente nos pixels originais. Os PNGs publicados são preservados
até a revisão humana dos candidatos.
"""

from pathlib import Path
import json

import numpy as np
from PIL import Image, ImageDraw


PASTA = Path(__file__).resolve().parent
CHAO_ALVO = {
    "icaro": [467, 473, 479, 485],
    "eva": [474, 480, 486, 492],
}


def fonte_original(personagem: str) -> Path:
    copia = PASTA / "originais_edicao" / personagem
    return copia if copia.exists() else PASTA / personagem


def suporte_atual(personagem: str, quadro: int) -> int:
    rastreio = json.loads((fonte_original(personagem) / "rastreamento.json").read_text())
    lado = "esquerda" if quadro < 5 else "direita"
    return rastreio["quadros"][quadro - 1]["juntas"][lado]["ponta_pe"][1]


def corrigir(imagem: Image.Image, lado: str, delta: int) -> Image.Image:
    rgba = np.asarray(imagem.convert("RGBA"))
    altura, largura, _ = rgba.shape
    ys, xs = np.mgrid[:altura, :largura]

    # A transição horizontal passa pelo espaço entre as pernas. No alto da
    # perna a deformação é zero; cresce gradualmente até o calçado inteiro,
    # que é apenas transladado e mantém sua altura e seu desenho.
    if lado == "esquerda":
        peso = np.clip((200.0 - xs) / 16.0, 0, 1)
    else:
        peso = np.clip((xs - 184.0) / 16.0, 0, 1)
    deslocamento = delta * peso
    inicio, fim = 320.0, 430.0
    origem_y = np.where(
        ys < inicio,
        ys,
        np.where(
            ys <= fim + deslocamento,
            inicio + (ys - inicio) * (fim - inicio) / (fim - inicio + deslocamento),
            ys - deslocamento,
        ),
    )
    origem_y = np.clip(np.rint(origem_y).astype(np.int16), 0, altura - 1)
    saida = rgba[origem_y, xs]
    return Image.fromarray(saida, "RGBA")


def main() -> None:
    destino = PASTA / "candidatos_v1"
    destino.mkdir(exist_ok=True)
    relatorio = []
    for personagem in ("icaro", "eva"):
        alvo = CHAO_ALVO[personagem]
        tiras = []
        for quadro in range(1, 9):
            lado = "esquerda" if quadro <= 4 else "direita"
            atual = suporte_atual(personagem, quadro)
            desejado = alvo[(quadro - 1) % 4]
            delta = desejado - atual
            original = Image.open(fonte_original(personagem) / f"{quadro:02}.png").convert("RGBA")
            candidato = corrigir(original, lado, delta)
            caminho = destino / f"{personagem}-{quadro:02}.png"
            candidato.save(caminho)
            relatorio.append({"personagem": personagem, "quadro": quadro,
                              "lado": lado, "apoio_atual_y": atual,
                              "apoio_alvo_y": desejado, "delta_px": delta,
                              "candidato": str(caminho.relative_to(PASTA))})
            tiras.extend((original, candidato))

        fundo = Image.new("RGB", (384 * 8, 512 * 2), "#e8e3dc")
        desenho = ImageDraw.Draw(fundo)
        for i, frame in enumerate(tiras):
            x = (i // 2) * 384
            y = (i % 2) * 512
            fundo.paste(frame, (x, y), frame)
            desenho.text((x + 8, y + 8),
                         f"{personagem} {i // 2 + 1:02} {'original' if i % 2 == 0 else 'candidato'}",
                         fill="#262626")
            desenho.line((x, y + 480, x + 383, y + 480), fill="#b5aaa0", width=1)
        fundo.save(destino / f"{personagem}-comparativo.png")

    (destino / "registro.json").write_text(json.dumps({
        "metodo": "Remapeamento vertical local RGBA, amostra mais próxima, sem alterar pixels acima de y=320 nem escala dos calçados.",
        "fase": "candidato não publicado; conferir anatomia, solo e costuras",
        "quadros": relatorio,
    }, indent=2, ensure_ascii=False) + "\n")

    # A passagem 03/07 gerada tem a perna de balanço em posição mais
    # coerente que o avanço 04/08: nesses dois quadros o pé sobe em vez de
    # descer para o contato seguinte. Compomos apenas a metade inferior da
    # perna correspondente, conservando tronco, cabelo, braço e acessório.
    destino2 = PASTA / "candidatos_v2"
    destino2.mkdir(exist_ok=True)
    ajustes = {"icaro": {4: (3, "direita", 5), 8: (7, "esquerda", 10)},
               "eva": {4: (3, "direita", 17), 8: (7, "esquerda", 10)}}
    for personagem in ("icaro", "eva"):
        for quadro in range(1, 9):
            base = Image.open(destino / f"{personagem}-{quadro:02}.png").convert("RGBA")
            if personagem == "eva" and quadro == 1:
                base = corrigir(base, "direita", 17)
            if quadro in ajustes[personagem]:
                fonte, lado, delta = ajustes[personagem][quadro]
                doador = Image.open(fonte_original(personagem) / f"{fonte:02}.png").convert("RGBA")
                doador = corrigir(doador, lado, delta)
                corrente = np.asarray(base).copy()
                pixels_doador = np.asarray(doador)
                ys, xs = np.mgrid[:512, :384]
                regiao = (ys >= 320) & ((xs >= 192) if lado == "direita" else (xs < 192))
                corrente[regiao] = pixels_doador[regiao]
                base = Image.fromarray(corrente, "RGBA")
            base.save(destino2 / f"{personagem}-{quadro:02}.png")

    (destino2 / "registro.json").write_text(json.dumps({
        "base": "candidatos_v1",
        "mudancas": [
            {"personagem": "eva", "quadro": 1, "acao": "pé direito anatômico de trás +17px para distinguir profundidade no contato esquerdo"},
            *({"personagem": p, "quadro": q, "fonte_perna": d,
               "lado": l, "deslocamento_pe_px": delta,
               "acao": "substituir apenas perna em balanço após y=320, abaixo da cintura"}
              for p, m in ajustes.items() for q, (d, l, delta) in m.items()),
        ],
        "estado": "candidato não publicado; inspeção visual pendente",
    }, indent=2, ensure_ascii=False) + "\n")

    for personagem in ("icaro", "eva"):
        painel = Image.new("RGB", (384 * 8, 512), "#e8e3dc")
        desenho = ImageDraw.Draw(painel)
        for quadro in range(1, 9):
            imagem = Image.open(destino2 / f"{personagem}-{quadro:02}.png").convert("RGBA")
            x = (quadro - 1) * 384
            painel.paste(imagem, (x, 0), imagem)
            desenho.text((x + 8, 8), f"{personagem} {quadro:02}", fill="#262626")
            desenho.line((x, 480, x + 383, 480), fill="#b5aaa0", width=1)
        painel.save(destino2 / f"{personagem}-ciclo.png")


if __name__ == "__main__":
    main()
