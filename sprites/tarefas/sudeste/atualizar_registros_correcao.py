"""Registra estimativas visuais e decisões desta rodada; não altera imagens."""

from pathlib import Path
import json

raiz = Path(__file__).parent
substituicoes = {
    "icaro": {
        2: {
            "esquerda": [[204, 310], [222, 378], [228, 449], [258, 468]],
            "direita": [[180, 310], [151, 373], [105, 419], [130, 442]],
        },
        7: {
            "esquerda": [[204, 311], [221, 376], [222, 411], [244, 430]],
            "direita": [[180, 311], [177, 388], [168, 451], [194, 469]],
        },
    },
    "eva": {
        3: {
            "esquerda": [[204, 305], [174, 380], [159, 447], [190, 470]],
            "direita": [[178, 305], [216, 375], [238, 423], [273, 448]],
        },
    },
}

for personagem in ("icaro", "eva"):
    pasta = raiz / personagem
    rastreio = json.loads((pasta / "rastreamento.json").read_text())
    for fase, lados in substituicoes[personagem].items():
        quadro = rastreio["quadros"][fase - 1]
        for lado, pontos in lados.items():
            for nome, valor in zip(("quadril", "joelho", "tornozelo", "ponta_pe"), pontos):
                quadro["juntas"][lado][nome] = valor
        quadro["natureza"] = (
            "estimativa visual revista após troca da imagem; quadril/joelho oclusos "
            "pela roupa; erro ~5-10px, ponta ~3px"
        )
    recuos = []
    for inicio, lado in ((0, "esquerda"), (4, "direita")):
        for atual, seguinte in zip(rastreio["quadros"][inicio:inicio + 3], rastreio["quadros"][inicio + 1:inicio + 4]):
            p = atual["juntas"][lado]["ponta_pe"]
            q = seguinte["juntas"][lado]["ponta_pe"]
            recuos.append(round(((p[0] - q[0]) + 0.35 * (p[1] - q[1])) / (0.70710678 * (1 + 0.35**2)), 2))
    rastreio["recuo_local_estimado_transicoes_apoio"] = recuos
    rastreio["calibracao_aprovada"] = False
    rastreio["motivo"] = "Chão e recuo do pé de apoio variam além do aceitável; pontos ainda são estimativas visuais."
    (pasta / "rastreamento.json").write_text(json.dumps(rastreio, ensure_ascii=False, indent=2) + "\n")

    revisao = json.loads((pasta / "revisao.json").read_text())
    revisao["aprovado"] = False
    revisao["quadros_revisados"] = list(range(1, 9))
    revisao["transicoes_revisadas"] = ["04→05", "08→01"]
    revisao["observacoes"] = [
        "Pranchas de fundo claro/escuro inspecionadas com linha de chão y480; 16 PNGs RGBA384x512 mantêm margens e alpha real.",
        "GIFs de 100 e 400 ms regenerados com chão marcado; sequência inspecionada quadro a quadro, sem aprovação temporal contínua.",
        "Originais substituídos preservados em originais-pre-correcao/; brutos novos e prompts em raw/ e geracoes-correcao.json.",
        "A pulseira de Ícaro permanece no braço esquerdo anatômico; Eva mantém brinco vermelho visível e não ganhou pulseira.",
    ]
    if personagem == "icaro":
        revisao["observacoes"] += [
            "02: nova geração restaurou comprimento do torso/pernas e apoio próximo a y480.",
            "07: nova geração aproxima o pé esquerdo em balanço do eixo do corpo.",
            "Transições 04→05 e 08→01 comparadas: silhueta e altura do apoio saltam; braço distante em 08 continua oculto.",
        ]
        revisao["pendencias"] = [
            "Chão dos quadros 01/04/08 fica 9/12/17 px acima da linha; 03/05 cruzam 4/3 px abaixo.",
            "Recuo local do apoio permanece irregular; velocidade única não remove patinação.",
            "02→03 altera extensão dos braços abruptamente e 07→08 passa de braço visível para oculto.",
            "Proporção e largura do tronco ainda oscilam discretamente entre gerações; requer redesenho de sequência antes da montagem.",
        ]
    else:
        revisao["observacoes"] += [
            "03: terceira geração recuou o pé em balanço, mas ainda se aproxima de 04.",
            "07: quarta geração rejeitada por repetir pose de avanço; 07 anterior preservado.",
            "Transições 04→05 e 08→01 comparadas: pés e braços mudam abruptamente e não sustentam passada homogênea.",
        ]
        revisao["pendencias"] = [
            "07: pé de apoio ultrapassa o chão em 22 px e joelho do balanço sobe demais; após três tentativas sem correção, precisa redesenho manual/novo ciclo dirigido.",
            "03 ainda projeta o pé em balanço perto da posição de avanço 04; três tentativas não resolveram totalmente.",
            "04 e 01 ultrapassam chão em 14/9 px; recuo e altura do apoio variam entre fases.",
            "02/03/04 e 06/07/08 têm balanço de braços e proporção de pernas pouco consistentes para loop final.",
        ]
    revisao["passada_teste_px_por_quadro"] = None
    revisao["recuo_local_estimado_transicoes_apoio"] = recuos
    (pasta / "revisao.json").write_text(json.dumps(revisao, ensure_ascii=False, indent=2) + "\n")

selecionados = json.loads((raiz / "selecionados.json").read_text())
for item in selecionados:
    substituto = {("icaro", 2): "icaro-02-t2.png", ("icaro", 7): "icaro-07-t2.png", ("eva", 3): "eva-03-t3.png"}.get((item["personagem"], item["fase"]))
    if substituto and item["raw"] != substituto:
        item["raw_anterior"] = item["raw"]
        item["raw"] = substituto
        item["reclassificacao"] = "correcao parcial apos revisao visual"
(raiz / "selecionados.json").write_text(json.dumps(selecionados, ensure_ascii=False, indent=2) + "\n")
