"""Mede patinação projetada dos pontos de apoio estimados manualmente."""

from pathlib import Path
import json
import math

D = Path(__file__).resolve().parent.parent
G = D.parent.parent / 'guias' / 'sudoeste' / '01.json'
passo_guia = json.loads(G.read_text())['deslocamento_por_quadro_projetado']
theta = 5 * math.pi / 4
resultado = {
    'tipo': 'teste estático de chão com pontos de pé estimados visualmente',
    'deslocamento_guia_por_quadro': passo_guia,
    'limite': 'sem tolerância formal de aprovação no contrato',
    'interpretacao': 'O guia usa passada de 18 px/quadro. A prévia usa a passada_teste_px_por_quadro de cada personagem; ambos os cenários são mostrados separadamente. A associação anatômica dos pés em 07→08 é incerta, portanto a deriva da segunda metade não é medição conclusiva.',
    'personagens': {},
}
for personagem in ('icaro', 'eva'):
    rastreio = json.loads((D / personagem / 'rastreamento.json').read_text())
    passada = rastreio['passada_teste_px_por_quadro']
    passo_previa = [round(passada * math.sin(theta), 3),
                    round(-passada * .35 * math.cos(theta), 3)]
    cenarios = {}
    for nome, passo in (('guia_18', passo_guia), ('previa_atual', passo_previa)):
        metades = []
        for inicio, lado in ((1, 'esquerda'), (5, 'direita')):
            amostras = []
            for fase in range(inicio, inicio + 4):
                ponta = rastreio['quadros'][fase - 1]['juntas'][lado]['ponta_pe']
                mundo = [round(ponta[eixo] + (fase - inicio) * passo[eixo], 2)
                         for eixo in (0, 1)]
                amostras.append({'fase': fase, 'ponta_celula': ponta, 'ponta_mundo': mundo})
            valores_x = [a['ponta_mundo'][0] for a in amostras]
            valores_y = [a['ponta_mundo'][1] for a in amostras]
            metades.append({
                'apoio': lado, 'amostras': amostras,
                'amplitude_x_mundo_px': round(max(valores_x) - min(valores_x), 2),
                'amplitude_y_mundo_px': round(max(valores_y) - min(valores_y), 2),
            })
        cenarios[nome] = {'deslocamento_personagem_por_quadro': passo,
                          'metades': metades}
    resultado['personagens'][personagem] = {
        'cenarios': cenarios,
        'diagnostico_transicoes': {
            '03_para_04': {
                'recuo_apoio_celula_x_px': rastreio['quadros'][3]['juntas']['esquerda']['ponta_pe'][0] - rastreio['quadros'][2]['juntas']['esquerda']['ponta_pe'][0],
                'recuo_esperado_previa_x_px': round(-passo_previa[0], 2),
                'leitura': 'Próximo do deslocamento da prévia; não transladar o pé de apoio do quadro 04 somente para ajustá-lo ao guia de 18 px.'
            },
            '07_para_08': {
                'diferenca_rastreio_x_px': rastreio['quadros'][7]['juntas']['direita']['ponta_pe'][0] - rastreio['quadros'][6]['juntas']['direita']['ponta_pe'][0],
                'recuo_esperado_previa_x_px': round(-passo_previa[0], 2),
                'leitura': 'Comparação anatômica incerta: as solas sobrepostas podem ter sido atribuídas a pernas diferentes. A forma do 08 também diverge do guia; revisar apoio e balanço sem forçar alinhamento numérico.'
            }
        },
        'chao_aprovado': False,
        'motivo': 'Na velocidade da prévia, as amostras variam em x e y. A amplitude da segunda metade é indício, não prova de patinação, porque a identidade do apoio em 07→08 é incerta. Sem conferência temporal e contato físico consistente, não aprovar.'
    }
(D / 'teste-chao.json').write_text(json.dumps(resultado, ensure_ascii=False, indent=2) + '\n')
print(json.dumps({p: {n: [(m['amplitude_x_mundo_px'], m['amplitude_y_mundo_px'])
                          for m in c['metades']]
                      for n, c in d['cenarios'].items()}
                  for p, d in resultado['personagens'].items()}, ensure_ascii=False))
