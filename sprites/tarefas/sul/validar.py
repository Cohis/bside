"""Confere quadros e registra rastreamento; não altera pixels dos personagens."""
from pathlib import Path
import hashlib
import json
import numpy as np
from PIL import Image

RAIZ = Path(__file__).resolve().parent
tecnica, rastreamento = {}, {}
for personagem in ('icaro', 'eva'):
    tecnica[personagem], quadros = [], []
    for fase in range(1, 9):
        arquivo = RAIZ / personagem / f'{fase:02}.png'
        imagem = Image.open(arquivo)
        pixels = np.array(imagem)
        caixa = imagem.getbbox()
        assert imagem.mode == 'RGBA' and imagem.size == (384, 512)
        assert caixa and min(caixa[:2]) >= 4 and caixa[2] <= 380 and caixa[3] <= 508
        assert imagem.getchannel('A').getextrema() == (0, 255)
        tecnica[personagem].append({'fase': fase, 'caixa': caixa,
            'sha256': hashlib.sha256(imagem.tobytes()).hexdigest(),
            'transparencia_real': True, 'margens_seguras': True})
        juntas = {}
        for lado, faixa in {'direita': (161, 169), 'esquerda': (209, 217)}.items():
            x0, x1 = faixa
            y, x = np.where(pixels[380:500, x0:x1, 3] > 64)
            sola = int(y.max() + 380)
            centro = (x0 + x1) // 2
            elevado = (lado == 'direita' and fase in (1, 2, 3, 8)) or (lado == 'esquerda' and fase in (4, 5, 6, 7))
            juntas[lado] = {
                'quadril': [174 if lado == 'direita' else 210, 315 + (4 if fase in (2, 6) else -2 if fase in (4, 8) else 0)],
                'joelho': [centro, 380 if elevado else 397],
                'tornozelo': [centro, sola - 27], 'ponta_pe': [centro, sola],
                'contato_chao': lado == ('esquerda' if fase <= 4 else 'direita') or fase in (1, 5),
                'oclusao': 'Quadril, joelho e parte do tornozelo ocultos pela roupa; dois calçados visíveis.',
                'metodo': {'ponta_pe': 'Borda inferior alpha na faixa central estreita do calçado; aproximação do ponto de apoio com incerteza ±3px.',
                    'tornozelo': 'Estimativa27px acima da borda do calçado; não é medição anatômica.',
                    'joelho': 'Estimativa visual sob calça larga.', 'quadril': 'Estimativa visual sob roupa.'}}
        quadros.append({'fase': fase, 'juntas': juntas})
    assert len({q['sha256'] for q in tecnica[personagem]}) == 8
    intervalos = []
    for fase in range(1, 9):
        proxima = fase % 8 + 1
        lado = 'esquerda' if fase <= 4 else 'direita'
        atual = quadros[fase - 1]['juntas'][lado]['ponta_pe'][1]
        seguinte = quadros[proxima - 1]['juntas'][lado]['ponta_pe'][1]
        intervalos.append({'de': fase, 'para': proxima, 'apoio': lado,
            'y_atual': atual, 'y_seguinte': seguinte,
            'recuo_px_projetados': atual - seguinte,
            'recuo_local_antes_projecao': round((atual - seguinte) / .35, 2)})
    rastreamento[personagem] = {'metodo': 'Bordas dos calçados medidas; juntas ocultas estimadas. Projeção sul y=local*.35. Não é captura biomecânica.',
        'quadros': quadros, 'intervalos_apoio': intervalos}
    media = sum(i['recuo_px_projetados'] for i in intervalos) / 8
    revisao = {
        'aprovado': False, 'estado': 'quadros completos; revisão final pendente',
        'quadros_revisados': list(range(1, 9)), 'transicoes_revisadas': ['04→05', '08→01'],
        'passada_teste_px_por_quadro': round(media / .35, 3),
        'passada_teste_projetada_px_por_quadro': round(media, 3),
        'perfil_recuo_projetado_por_intervalo': [i['recuo_px_projetados'] for i in intervalos],
        'observacoes': [
            'Oito imagens distintas geradas individualmente com image_gen; RGBA384x512 e margens técnicas aprovadas.',
            'Inspeção visual quadro a quadro e das transições nas pranchas: câmera frontal mantida, dois pés e duas mãos, sem espelhamento.',
            'Chaves01/03/05/07 aceitas pelo coordenador antes dos intermediários. Passagens03/07 usam v2; Eva05 usa v2.',
            'Apoio recua regularmente nos dois primeiros intervalos de cada passo. Último impulso tem recuo maior; uma velocidade constante pode mostrar patinação.',
            'Último intervalo tem diferença negativa1–2px, dentro da incerteza±3px da borda/rotação do calçado; não há evidência de inversão grande.',
            'Cabeça varia discretamente em desenho/escala. Não houve deformação de membros, espelhamento nem interpolação suave.',
            'GIFs100ms/400ms e prévia HTML preparados; inspeção realizada nas sequências estáticas, não alegamos observação temporal contínua do navegador.'
        ],
        'pendencias': [
            'Coordenador deve revisar reprodução normal/lenta e chão marcado com perfil de recuo antes de aprovar.',
            'Avaliar irregularidade do último impulso e variação residual de escala; não declarar ausência de patinação.'
        ],
        'evidencias': ['../' + personagem + '-ciclo.png', '../' + personagem + '-normal.gif', '../' + personagem + '-lento.gif', '../rastreamento.json', '../tecnica.json', '../previa-revisao.html']}
    (RAIZ / personagem / 'revisao.json').write_text(json.dumps(revisao, ensure_ascii=False, indent=2) + '\n')
(RAIZ / 'tecnica.json').write_text(json.dumps(tecnica, ensure_ascii=False, indent=2) + '\n')
(RAIZ / 'rastreamento.json').write_text(json.dumps(rastreamento, ensure_ascii=False, indent=2) + '\n')
print('16 PNGs tecnicamente válidos; 8 hashes distintos por personagem, sem células vazias. Aprovação visual final pendente.')
