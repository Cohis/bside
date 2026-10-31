"""Resume recuo observado do apoio sem confundir estimativas com aprovação anatômica."""
import json, math
from pathlib import Path
from rastreamento import normalizar as normalizar_rastreamento

raiz = Path(__file__).resolve().parents[1]
contrato = json.loads((raiz / 'contrato.json').read_text())
resultados = []
for indice, direcao in enumerate(contrato['direcoes']):
    angulo = indice * math.pi / 4
    # Direção do avanço projetada no plano da imagem, com profundidade comprimida.
    vetor = (math.sin(angulo), -.35 * math.cos(angulo))
    norma2 = sum(v*v for v in vetor)
    for personagem in contrato['personagens']:
        pasta = raiz / 'tarefas' / direcao
        arquivo = pasta / personagem / 'rastreamento.json'
        if arquivo.exists():
            dados = json.loads(arquivo.read_text())
        elif (pasta / 'rastreamento.json').exists():
            dados = json.loads((pasta / 'rastreamento.json').read_text()).get(personagem)
        else:
            continue
        if not dados or not isinstance(dados.get('quadros'), list):
            continue
        dados = normalizar_rastreamento(dados)
        quadros = {q.get('fase', q.get('quadro')): q for q in dados['quadros']}
        passos = []
        for lado, fases in [('esquerda', [1,2,3,4]), ('direita', [5,6,7,8])]:
            pontos = [quadros.get(f, {}).get('juntas', {}).get(lado, {}).get('ponta_pe') for f in fases]
            if not all(isinstance(p,list) and len(p)==2 for p in pontos):
                continue
            recuos = [round(-sum((b[j]-a[j])*vetor[j] for j in range(2))/norma2,2) for a,b in zip(pontos,pontos[1:])]
            passos.append({'apoio': lado, 'fases': fases, 'pontos_px': pontos,
                           'recuo_local_estimado_por_intervalo': recuos,
                           'intervalos_com_recuo_negativo': [f'{fases[i]:02d}→{fases[i+1]:02d}' for i,v in enumerate(recuos) if v<0]})
        resultados.append({'personagem':personagem,'direcao':direcao,'passos':passos,
                           'limite':'Ponta/borda do calçado pode variar por rotação e oclusão. Não certifica contato, comprimento ou patinação. Consulte incertezas do rastreamento original.'})
saida = {'metodo':'Projeção do deslocamento das pontas dos pés no eixo oposto ao avanço. Compara apenas intervalos 01→04 e 05→08, sem trocar a perna de apoio.', 'ciclos':resultados}
(raiz/'registros'/'auditoria-movimento.json').write_text(json.dumps(saida,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({'ciclos_com_rastreamento':len(resultados)},ensure_ascii=False))
