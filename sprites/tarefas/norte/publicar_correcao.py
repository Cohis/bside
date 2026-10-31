"""Publica candidatos norte com backup e rastreabilidade integral da edição."""

from pathlib import Path
import hashlib
import json
import shutil

from PIL import Image

from verificar_candidatos import extremo_pe


PASTA = Path(__file__).resolve().parent
CANDIDATOS = PASTA / "candidatos_v2"
BACKUP = PASTA / "originais_edicao"
AJUSTES_BALANCO = {"icaro": {4: (3, "direita", 5), 8: (7, "esquerda", 10)},
                   "eva": {4: (3, "direita", 17), 8: (7, "esquerda", 10)}}


def hash_arquivo(caminho: Path) -> str:
    return hashlib.sha256(caminho.read_bytes()).hexdigest()


def mover_y(y: int, delta: int) -> int:
    if y <= 320:
        return y
    return round(y + delta * min(1, (y - 320) / 110))


def main() -> None:
    if BACKUP.exists():
        raise SystemExit("Backup de edição já existe; publicação repetida bloqueada")
    qa = json.loads((CANDIDATOS / "qa.json").read_text())
    if set(qa["personagens"]) != {"icaro", "eva"}:
        raise SystemExit("QA incompleto")
    BACKUP.mkdir()
    for personagem in ("icaro", "eva"):
        (BACKUP / personagem).mkdir()
        for nome in ("revisao.json", "rastreamento.json", "tecnica.json"):
            shutil.copy2(PASTA / personagem / nome, BACKUP / personagem / nome)
        for q in range(1, 9):
            shutil.copy2(PASTA / personagem / f"{q:02}.png", BACKUP / personagem / f"{q:02}.png")

    registro = {"metodo": "Edição controlada RGBA por amostragem de vizinho mais próximo; apoio remapeado abaixo da cintura; dois avanços recompostos da perna de passagem original do mesmo personagem e direção.",
                "autorizacao": "Usuário autorizou edição controlada quadro a quadro nesta conversa.",
                "originais": "originais_edicao/", "candidatos": "candidatos_v2/",
                "quadros": []}
    v1 = json.loads((PASTA / "candidatos_v1" / "registro.json").read_text())
    deltas = {(i["personagem"], i["quadro"]): i for i in v1["quadros"]}
    for personagem in ("icaro", "eva"):
        pasta = PASTA / personagem
        dados = json.loads((pasta / "rastreamento.json").read_text())
        revisao = json.loads((pasta / "revisao.json").read_text())
        tecnica = []
        medidas = qa["personagens"][personagem]["quadros"]
        juntas_orig = [i["juntas"] for i in dados["quadros"]]
        for q in range(1, 9):
            candidato = CANDIDATOS / f"{personagem}-{q:02}.png"
            alvo = pasta / f"{q:02}.png"
            origem = BACKUP / personagem / f"{q:02}.png"
            info = deltas[(personagem, q)]
            lado_apoio = info["lado"]
            delta = info["delta_px"]
            antes, depois = hash_arquivo(origem), hash_arquivo(candidato)
            shutil.copy2(candidato, alvo)
            im = Image.open(alvo).convert("RGBA")
            alfa = im.getchannel("A")
            tecnica.append({"quadro": q, "dimensoes": [384, 512],
                "caixa": list(alfa.getbbox()), "sha256": depois,
                "alfa_extremos": list(alfa.getextrema()),
                "origem_edicao": f"originais_edicao/{personagem}/{q:02}.png"})

            juntas = dados["quadros"][q-1]["juntas"]
            for lado in ("esquerda", "direita"):
                donor = q
                mudanca = 0
                if lado == lado_apoio:
                    mudanca += delta
                if personagem == "eva" and q == 1 and lado == "direita":
                    mudanca += 17
                if q in AJUSTES_BALANCO[personagem] and lado != lado_apoio:
                    donor, _, mudanca = AJUSTES_BALANCO[personagem][q]
                fonte = juntas_orig[donor-1][lado]
                for ponto in ("joelho", "tornozelo"):
                    x, y = fonte[ponto]
                    juntas[lado][ponto] = [x, mover_y(y, mudanca)]
                    juntas[lado]["confianca"][ponto] = "estimativa após edição local; calça larga oculta a junta"
                juntas[lado]["ponta_pe"] = [fonte["ponta_pe"][0], extremo_pe(im, lado)]
                juntas[lado]["confianca"]["ponta_pe"] = "extremo inferior alfa no corredor do calçado; contato exato pode estar ocluído"

            registro["quadros"].append({"personagem": personagem, "quadro": q,
                "sha256_original": antes, "sha256_final": depois,
                "apoio": lado_apoio, "ajuste_apoio_px": delta,
                "fonte_balanco": AJUSTES_BALANCO[personagem].get(q, (q, None, None))[0],
                "ajuste_traseiro_extra_px": 17 if personagem == "eva" and q == 1 else 0})
        dados["metodo"] = "Rastreamento original preservado em originais_edicao/. Pontas dos calçados medidas após edição; juntas sob as calças seguem estimativas visuais."
        (pasta / "rastreamento.json").write_text(json.dumps(dados, indent=2, ensure_ascii=False) + "\n")
        (pasta / "tecnica.json").write_text(json.dumps(tecnica, indent=2, ensure_ascii=False) + "\n")
        revisao["pendencias_anteriores"] = revisao.get("pendencias", [])
        revisao["pendencias"] = ["Revisão independente do coordenador dos GIFs 100/400 ms e das costuras da composição pendente."]
        revisao["estado"] = "correção controlada publicada, aguardando revisão independente"
        revisao["aprovado"] = False
        revisao["apoio_observado_px"] = {
            "esquerda_01_04": qa["personagens"][personagem]["apoios_esquerda"],
            "direita_05_08": qa["personagens"][personagem]["apoios_direita"]}
        revisao["passada_teste_px_por_quadro"] = 17.14
        revisao["passada_teste_origem"] = "Apoio observado recua 6px verticais por quadro; projeção norte no plano -0,35; velocidade local estimada 6/0,35=17,14px/quadro."
        revisao["edicao_controlada"] = "../registro-edicao.json"
        revisao["previas_chao"] = [f"../candidatos_v2/{personagem}-chao-100ms.gif",
                                       f"../candidatos_v2/{personagem}-chao-400ms.gif"]
        (pasta / "revisao.json").write_text(json.dumps(revisao, indent=2, ensure_ascii=False) + "\n")

    (PASTA / "registro-edicao.json").write_text(json.dumps(registro, indent=2, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
