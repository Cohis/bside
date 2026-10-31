# Gerado por ferramentas/gerar_doca.py. Não editar à mão.
# Incluído no roteiro_principal de sala2.s: os três trechos da fuga, ponto a ponto.

    ROTULO "doca"
    CMD OP_TRAVA
    CMD OP_ESCURECE
    CMD OP_ANDAR, 3, 64, 32, 4
    ATOR ATOR_AGENTE, 3, 48, 38, conj_AGENTE, AF_SOMBRA|AF_HD
    CMD OP_CHAMA, p=prepara_doca
    CMD OP_CLAREIA
    MSG "Os anjos voam em linha reta até o som e pousam em volta dele.\nChegar perto de qualquer anjo, voando, pousado ou escutando, é morte."
    CMD OP_DOCA, p=ponto_doca_1
    CMD OP_DOCA, p=ponto_doca_2
    CMD OP_DOCA, p=ponto_doca_3

    ROTULO "patio"
    CMD OP_TRAVA
    CMD OP_ESCURECE
    CMD OP_ANDAR, 4, 32, 28, 4
    ATOR ATOR_AGENTE, 4, 24, 40, conj_AGENTE, AF_SOMBRA|AF_HD
    CMD OP_CHAMA, p=prepara_patio
    CMD OP_CLAREIA
    MSG "Pátio de contêineres. Corredores estreitos: um anjo pousado fecha um corredor inteiro.\nOs que já pousaram continuam lá."
    CMD OP_DOCA, p=ponto_patio_1
    CMD OP_DOCA, p=ponto_patio_2
    CMD OP_DOCA, p=ponto_patio_3
    CMD OP_DOCA, p=ponto_patio_4

    ROTULO "quebramar"
    CMD OP_TRAVA
    CMD OP_ESCURECE
    CMD OP_ANDAR, 5, 40, 36, 4
    ATOR ATOR_AGENTE, 5, 24, 48, conj_AGENTE, AF_SOMBRA|AF_HD
    CMD OP_CHAMA, p=prepara_quebramar
    CMD OP_CLAREIA
    MSG "Quebra-mar. Tábuas de uma passada só: não há para onde desviar.\nO farol é a saída."
    CMD OP_DOCA, p=ponto_quebramar_1
    CMD OP_DOCA, p=ponto_quebramar_2
    CMD OP_DOCA, p=ponto_quebramar_3
