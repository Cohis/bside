"""Adota os ensaios sem costura de 06/07, preservando versões anteriores."""
import hashlib
import json
import shutil
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
CANDIDATOS = RAIZ / "candidatos-recuo-06-07"
BACKUP = RAIZ / "originais-pre-recuo-06-07"
BACKUP.mkdir(exist_ok=True)
REGISTRO = {}

def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def deslocamento(pessoa, fase, y):
    deslocamento_maximo = {"icaro": {6: -18, 7: -15}, "eva": {6: -21, 7: -17}}[pessoa][fase]
    return round(deslocamento_maximo * max(0, min(1, (y - 328) / 140)))

for pessoa in ("icaro", "eva"):
    REGISTRO[pessoa] = {}
    for fase in (6, 7):
        atual = RAIZ / pessoa / f"{fase:02}.png"
        anterior = BACKUP / f"{pessoa}-{fase:02}.png"
        sufixo = "faixa" if fase == 7 else "candidato"
        candidato = CANDIDATOS / f"{pessoa}-{fase:02}-{sufixo}.png"
        if anterior.exists():
            raise SystemExit(f"Backup já existe: {anterior}; não repetir a promoção")
        shutil.copy2(atual, anterior)
        shutil.copy2(candidato, atual)
        REGISTRO[pessoa][f"{fase:02}"] = {
            "antes": str(anterior.relative_to(RAIZ)),
            "sha256_antes": sha(anterior),
            "depois": str(atual.relative_to(RAIZ)),
            "sha256_depois": sha(atual),
            "metodo": "06: máscara da perna de apoio; 07: faixa inferior inteira, ambos com translação horizontal progressiva por vizinho mais próximo",
        }

    rastreio = RAIZ / pessoa / "rastreamento.json"
    dados = json.loads(rastreio.read_text())
    for fase in (6, 7):
        juntas = dados["quadros"][fase - 1]["juntas"]
        lados = ("direita",) if fase == 6 else ("esquerda", "direita")
        for lado in lados:
            for nome in ("joelho", "tornozelo", "ponta_pe"):
                ponto = juntas[lado][nome]
                ponto[0] += deslocamento(pessoa, fase, ponto[1])
        dados["quadros"][fase - 1]["natureza"] += " Recuo 24/out: x dos pontos afetados atualizado pela função de remapeamento; permanece estimativa."
    pernas = dados["quadros"]
    esquerda = [pernas[i]["juntas"]["esquerda"]["ponta_pe"][0] for i in range(4)]
    direita = [pernas[i]["juntas"]["direita"]["ponta_pe"][0] for i in range(4, 8)]
    recuos = [esquerda[i] - esquerda[i + 1] for i in range(3)] + [direita[i] - direita[i + 1] for i in range(3)]
    dados["recuo_horizontal_estimado_transicoes_apoio"] = recuos
    dados["recuo_local_estimado_transicoes_apoio"] = None
    dados["calibracao_aprovada"] = False
    dados["motivo"] = "Recuo horizontal estimado atualizado; contato e naturalidade do loop ainda precisam de revisão temporal."
    rastreio.write_text(json.dumps(dados, ensure_ascii=False, indent=2) + "\n")
    revisao = RAIZ / pessoa / "revisao.json"
    dados = json.loads(revisao.read_text())
    dados["observacoes"].append("Quadros 06/07 ajustados para recuo horizontal mais uniforme do apoio; backups e hashes em recuo-06-07-adotado.json.")
    dados["pendencias"] = [p for p in dados["pendencias"] if not p.startswith("Recuo estimado do apoio")]
    dados["pendencias"].append("Recuo horizontal estimado agora " + "/".join(map(str, recuos)) + " px; confirmar com chão marcado e inspeção temporal antes de aprovar.")
    dados["passada_teste_px_por_quadro"] = 43 if pessoa == "icaro" else 40
    dados["recuo_local_estimado_transicoes_apoio"] = None
    dados["recuo_horizontal_estimado_transicoes_apoio"] = recuos
    revisao.write_text(json.dumps(dados, ensure_ascii=False, indent=2) + "\n")
    REGISTRO[pessoa]["recuo_horizontal_estimado"] = recuos

(RAIZ / "recuo-06-07-adotado.json").write_text(json.dumps(REGISTRO, ensure_ascii=False, indent=2) + "\n")
