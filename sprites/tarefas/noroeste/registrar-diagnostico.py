"""Registra integridade e a reprovação visual atual do ciclo noroeste."""
from pathlib import Path
from PIL import Image
import hashlib
import json

PASTA = Path(__file__).resolve().parent
REGISTROS = PASTA / "registros"
resultado = {"direcao": "noroeste", "data": "2026-10-24", "personagens": {}}
for personagem in ("icaro", "eva"):
    fases = []
    for indice in range(1, 9):
        nome = f"{indice:02}.png"
        caminho = PASTA / personagem / nome
        imagem = Image.open(caminho)
        assert imagem.mode == "RGBA" and imagem.size == (384, 512)
        assert imagem.getbbox() is not None
        fases.append({"fase": indice, "sha256_arquivo": hashlib.sha256(caminho.read_bytes()).hexdigest(),
                      "bbox": list(imagem.getbbox())})
    assert len({f["sha256_arquivo"] for f in fases}) == 8
    gifs = {}
    for tempo in (100, 400):
        caminho = REGISTROS / "chao-marcado" / f"{personagem}-{tempo}ms.gif"
        gif = Image.open(caminho)
        duracoes = []
        for i in range(gif.n_frames):
            gif.seek(i)
            duracoes.append(gif.info["duration"])
        assert gif.n_frames == 8 and duracoes == [tempo] * 8
        gifs[str(tempo)] = {"quadros": 8, "duracoes_ms": duracoes}
    resultado["personagens"][personagem] = {"quadros": fases, "previa_chao": gifs,
        "veredito_visual": "reprovado",
        "defeitos": ["01/08: contrabalanço de braços incorreto",
                     "03/07: pé suspenso permanece atrás da linha de passagem",
                     "06: identidade da perna de apoio diverge do guia",
                     "04→05 e 08→01: transições abruptas; patinação visível sobre chão marcado"]}
(REGISTROS / "diagnostico-2026-10-24.json").write_text(
    json.dumps(resultado, ensure_ascii=False, indent=2) + "\n")
