"""Adapta os registros de pose para uma leitura comum, sem alterar estimativas."""


def normalizar(dados):
    if not dados or not isinstance(dados.get('quadros'), list):
        return dados
    quadros = []
    for quadro in dados['quadros']:
        if 'juntas' in quadro:
            quadros.append(quadro)
            continue
        # No oeste, cada lado foi descrito diretamente no quadro.
        juntas = {}
        for lado in ('esquerda', 'direita'):
            origem = quadro.get(lado, {})
            juntas[lado] = {
                'quadril': quadro.get('quadril_estimado'),
                'joelho': origem.get('joelho_estimado_oculto'),
                'tornozelo': origem.get('tornozelo_estimado'),
                'ponta_pe': origem.get('ponta_pe_observada_aproximada'),
                'contato_chao': None,
                'observacao': 'Joelho oculto e estimado; ponta aproximada. Contato não atestado por este registro.',
            }
        quadros.append({**quadro, 'juntas': juntas})
    return {**dados, 'quadros': quadros}
