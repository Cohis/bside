"""Atualiza evidências da direção leste após edição manual, sem renormalizar raws."""
import hashlib
import json
from pathlib import Path
from PIL import Image, ImageDraw

raiz = Path(__file__).resolve().parent
for pessoa in ("icaro", "eva"):
    quadros = [Image.open(raiz / pessoa / f"{i:02}.png").convert("RGBA") for i in range(1, 9)]
    checks = []
    for i, imagem in enumerate(quadros, 1):
        alfa = imagem.getchannel("A")
        checks.append({
            "fase": i,
            "dimensoes": list(imagem.size),
            "modo": imagem.mode,
            "caixa": alfa.getbbox(),
            "alfa": alfa.getextrema(),
            "sha256": hashlib.sha256(imagem.tobytes()).hexdigest(),
        })

    for cor, nome in [((244, 244, 239), "claro"), ((35, 38, 45), "escuro")]:
        folha = Image.new("RGB", (1536, 1080), cor)
        desenho = ImageDraw.Draw(folha)
        for idx, quadro in enumerate(quadros):
            x = (idx % 4) * 384
            y = (idx // 4) * 540
            folha.paste(quadro, (x, y + 24), quadro)
            desenho.text((x + 10, y + 5), f"{pessoa} {idx + 1:02}", fill=(140, 140, 140))
        folha.save(raiz / f"{pessoa}-inspecao-{nome}.png")

    fundo = []
    for quadro in quadros:
        tela = Image.new("RGB", (384, 512), (225, 225, 225))
        tela.paste(quadro, (0, 0), quadro)
        fundo.append(tela)
    fundo[0].save(raiz / f"{pessoa}-loop.gif", save_all=True,
                  append_images=fundo[1:], duration=100, loop=0)
    fundo[0].save(raiz / f"{pessoa}-lento.gif", save_all=True,
                  append_images=fundo[1:], duration=400, loop=0)

    tecnica = raiz / pessoa / "tecnica.json"
    conteudo = json.loads(tecnica.read_text())
    conteudo["quadros"] = checks
    conteudo["duplicatas"] = len({c["sha256"] for c in checks}) != 8
    conteudo["edicao_controlada"] = [2, 4, 6, 7]
    tecnica.write_text(json.dumps(conteudo, ensure_ascii=False, indent=2) + "\n")
