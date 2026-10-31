.intel_syntax noprefix

# Fase 1, sala 2: o galpão de Hank e a fuga dos anjos. Só dados: planta, móveis
# e luzes do galpão, poses do elenco, interações e a sequência da fase, que
# começa no enigma da loja (sala 1): o bilhete do balcão, a melodia D-C-G no
# depósito e a caixa com o endereço do galpão. Os trechos da fuga vêm de
# doca_dados.inc e doca_roteiro.inc (ferramentas/gerar_doca.py).
# Coordenadas em px do mundo (TILE = 16 px). Andares: 0 cima e 1 térreo da
# B-Side (fase1.s), 2 galpão, 3 doca, 4 pátio de contêineres, 5 quebra-mar.

.include "estruturas.inc"
.include "tileset.inc"
.include "personagens.inc"
.include "cenario.inc"

# --------------------------------------------------------------- roteiro

.macro CMD op, a=0, b=0, c=0, d=0, e=0, p=0
    .long \op, \a, \b, \c, \d, \e
    .quad \p
.endm

.macro TEXTO texto
    .pushsection .rodata.textos, "a"
8:  .asciz "\texto"
    .popsection
.endm

.macro MSG texto
    TEXTO "\texto"
    CMD OP_MENSAGEM, p=8b
.endm

.macro OBJETIVO texto
    TEXTO "\texto"
    CMD OP_OBJETIVO, p=8b
.endm

.macro ROTULO nome
    TEXTO "\nome"
    CMD OP_ROTULO, p=8b
.endm

# Ator com conjunto de poses (anda e vira sozinho).
.macro ATOR i, andar, x, y, conj, flags=AF_SOMBRA
    CMD OP_ATOR, \i, ((\andar) & 0xff) | ((\flags) << 8), \x, \y, 0, \conj
.endm

# Ator numa pose só (anjos, Mael, o agente parado no galpão).
.macro FIXO i, andar, x, y, z, pose, flags=0
    CMD OP_ATOR_FIXO, \i, ((\andar) & 0xff) | ((\flags) << 8), \x, \y, \z, pose_\pose
.endm

.macro ESCONDE i
    CMD OP_ESCONDE, \i
.endm

# Ator desliza até (x, y, z) a vel px/s.
.macro MOVE i, x, y, z, vel
    CMD OP_MOVE, \i, \x, \y, \z, \vel
.endm

# Direções da sprite de Ícaro na tela.
.equ D_N, 0
.equ D_NE, 1
.equ D_L, 2
.equ D_SE, 3
.equ D_S, 4
.equ D_SO, 5
.equ D_O, 6
.equ D_NO, 7

# Flags do roteiro.
.equ FL_SAIU, 1
.equ FL_DISCO, 2
.equ FL_AGENTE, 3
.equ FL_BILHETE, 5
.equ FL_MELODIA, 6
.equ FL_ENDERECO, 7
.equ FL_NA_LOJA, 8

# --------------------------------------------------------------- poses

.macro POSE nome, fps=0
.global pose_\nome
pose_\nome:
    .long P_\nome\()_X, P_\nome\()_Y, P_\nome\()_L, P_\nome\()_A
    .long P_\nome\()_N, P_\nome\()_AX, P_\nome\()_AY, \fps
.endm

.macro CONJUNTO pessoa, fps=8
    POSE \pessoa\()_PARADO_S
    POSE \pessoa\()_PARADO_L
    POSE \pessoa\()_PARADO_N
    POSE \pessoa\()_PARADO_O
    POSE \pessoa\()_ANDA_S, \fps
    POSE \pessoa\()_ANDA_L, \fps
    POSE \pessoa\()_ANDA_N, \fps
    POSE \pessoa\()_ANDA_O, \fps
.endm

.section .rodata
.align 8
    CONJUNTO HANK
    CONJUNTO AGENTE
    POSE HANK_FALA, 3
    POSE AGENTE_OLHOS, 4
    POSE AGENTE_SENTADO, 2
    POSE CLARAO, 12
    POSE MAEL, 3
    POSE BILHETE
    POSE LISTA
    POSE CAIXA_PEDIDO
    POSE NOTA_0                      # as quatro em sequência: doca.s soma 32 por nota
    POSE NOTA_1
    POSE NOTA_2
    POSE NOTA_3
    POSE ANEL
    POSE TECLA_E
    POSE AREA_SEGURA

# Pose em assets/elenco-hd.png: células 384x512; coluna 0 agente, 1 anjo (linhas
# na ordem do Ícaro: norte, nordeste, leste, sudeste, sul, sudoeste, oeste,
# noroeste), 2 poses da doca (pousado, grito, voo à direita, voo à esquerda).
.macro POSE_HD nome, coluna, linha
.global pose_\nome
pose_\nome:
    .long (\coluna) * 384, (\linha) * 512, 384, 512, 1, 192, 480, 0
.endm
    POSE_HD AGENTE_HD_N, 0, 0
    POSE_HD AGENTE_HD_L, 0, 2
    POSE_HD AGENTE_HD_S, 0, 4
    POSE_HD AGENTE_HD_O, 0, 6
    POSE_HD ANJO_HD_N, 1, 0
    POSE_HD ANJO_HD_L, 1, 2
    POSE_HD ANJO_HD_S, 1, 4
    POSE_HD ANJO_HD_O, 1, 6
    POSE_HD ANJO_POUSADO, 2, 0
    POSE_HD ANJO_GRITO, 2, 1
    POSE_HD ANJO_VOO_D, 2, 2
    POSE_HD ANJO_VOO_E, 2, 3

# Parado S L N O, andando S L N O.
.macro LISTA_CONJ pessoa
conj_\pessoa:
    .quad pose_\pessoa\()_PARADO_S, pose_\pessoa\()_PARADO_L, pose_\pessoa\()_PARADO_N, pose_\pessoa\()_PARADO_O
    .quad pose_\pessoa\()_ANDA_S, pose_\pessoa\()_ANDA_L, pose_\pessoa\()_ANDA_N, pose_\pessoa\()_ANDA_O
.endm
    LISTA_CONJ HANK
# Anjo em voo, virado para onde vai: leste e norte à direita, oeste e sul à
# esquerda (doca.s troca para pousado ao chegar).
.global conj_ANJO_VOO
conj_ANJO_VOO:
    .quad pose_ANJO_VOO_E, pose_ANJO_VOO_D, pose_ANJO_VOO_D, pose_ANJO_VOO_E
    .quad pose_ANJO_VOO_E, pose_ANJO_VOO_D, pose_ANJO_VOO_D, pose_ANJO_VOO_E
# Agente: só as poses paradas em alta resolução; andando, ele desliza parado.
conj_AGENTE:
    .quad pose_AGENTE_HD_S, pose_AGENTE_HD_L, pose_AGENTE_HD_N, pose_AGENTE_HD_O
    .quad pose_AGENTE_HD_S, pose_AGENTE_HD_L, pose_AGENTE_HD_N, pose_AGENTE_HD_O

nome_galpao:    .asciz "GALPÃO DE HANK"
nome_estantes:  .asciz "ESTANTES"

# --------------------------------------------------------------- galpão
#
# Janelas altas ao norte (atrás delas, Mael) e a oeste (por onde Ícaro entra).
# Oito estantes em quatro fileiras, numeradas no chão; a 7 tem a caixa marcada.
# A bancada de rádios fica ao norte; o portão dos fundos, ao sul, leva à doca.

mapa_galpao:
    LINHA "#####JJJJ####JJJJ#####"    #  0
    LINHA "#GGGGGGGGGGGGGGGGGGGG#"    #  1
    LINHA "JGGGGGGGGGGGGGGGGGGGG#"    #  2  janela quebrada: entrada
    LINHA "JGGGGGGGGGGGGGGGGGGGG#"    #  3
    LINHA "#GGGGGGGGGGGGGGGGGGGG#"    #  4
    LINHA "#GGGGGGGGGGGGGGGGGGGG#"    #  5
    LINHA "#GGGGGGGGGGGGGGGGGGGG#"    #  6
    LINHA "#GGGGGGGGGGGGGGGGGGGG#"    #  7
    LINHA "#GGGGGGGGGGGGGGGGGGGG#"    #  8
    LINHA "#GGGGGGGGGGGGGGGGGGGG#"    #  9
    LINHA "#GGGGGGGGGGGGGGGGGGGG#"    # 10
    LINHA "#GGGGGGGGGGGGGGGGGGGG#"    # 11
    LINHA "#GGGGGGGGGGGGGGGGGGGG#"    # 12
    LINHA "#GGGGGGGGGGGGGGGGGGGG#"    # 13
    LINHA "#GGGGGGGGGGGGGGGGGGGG#"    # 14
    LINHA "#GGGGGGGGGGGGGGGGGGGG#"    # 15
    LINHA "#GGGGGGGGGGGGGGGGGGGG#"    # 16
    LINHA "#GGGGGGGGGGGGGGGGGGGG#"    # 17
    LINHA "#GGGGGGGGGGGGGGGGGGGG#"    # 18
    LINHA "#GGGGGGGGGGGGGGGGGGGG#"    # 19
    LINHA "#GGGGGGGGGGGGGGGGGGGG#"    # 20
    LINHA "################PP####"    # 21  portão dos fundos

.align 8
comodos_galpao:
    COMODO 1, 1, 20, 20, nome_estantes
comodos_galpao_fim:


transicoes_galpao:
transicoes_galpao_fim:
decalques_galpao:
decalques_galpao_fim:

luzes_galpao:
    LUZ 64, 92, 50, 110, 220, 186, 132, OS_ROTEIRO        # lâmpadas sobre os corredores
    LUZ 192, 92, 50, 110, 220, 186, 132, OS_ROTEIRO
    LUZ 64, 220, 50, 110, 220, 186, 132, OS_ROTEIRO
    LUZ 192, 220, 50, 110, 220, 186, 132, OS_ROTEIRO
    LUZ 292, 290, 40, 100, 200, 160, 110, OS_ROTEIRO      # perto do portão
    LUZ 20, 48, 24, 70, 81, 108, 189                      # luar pela janela quebrada
    LUZ 112, 24, 20, 90, 81, 108, 189                     # janelas altas
    LUZ 240, 24, 20, 90, 81, 108, 189
    LUZ 274, 44, 24, 80, 150, 180, 255, OS_ESTATICA       # a TV chiando
luzes_galpao_fim:


.section .data
.align 8
objetos_galpao:
    # estantes: fileiras em y = 48, 112, 176, 240; colunas em x = 40 e 168
    MOVEL3 PRATELEIRA_G, 40, 48
    MOVEL3 PRATELEIRA_G2, 168, 48
    MOVEL3 PRATELEIRA_G2, 40, 112
    MOVEL3 PRATELEIRA_G, 168, 112
    MOVEL3 PRATELEIRA_G, 40, 176
    MOVEL3 PRATELEIRA_G2, 168, 176
    MOVEL3 PRATELEIRA_G_MARCADA, 40, 240
    MOVEL3 PRATELEIRA_G, 168, 240
    TAPETE NUMERO_1, 57, 64
    TAPETE NUMERO_2, 185, 64
    TAPETE NUMERO_3, 57, 128
    TAPETE NUMERO_4, 185, 128
    TAPETE NUMERO_5, 57, 192
    TAPETE NUMERO_6, 185, 192
    TAPETE NUMERO_7, 57, 256
    TAPETE NUMERO_8, 185, 256
    # bancada de rádios e a TV que chia depois do disco
    MOVEL4 BANCADA_RADIOS, 248, 17
    SOLTO ESTATICA_TV, 272, 30, 23, CAM_EMISSIVA, AN_NENHUMA, OS_ESTATICA
    MOVEL MESA_PRANCHETA, 120, 18
    MOVEL2 CAIXAS_PILHA, 300, 120
    MOVEL2 CAIXAS_PILHA, 296, 200
    MOVEL3 CAIXOTES_GALPAO, 200, 300
objetos_galpao_fim:



.section .bss
.align 16
itens_galpao: .skip MAX_ITENS * IT_TAM

.section .data
.global andares
.global n_andares
.align 8
andar_galpao:
    .quad mapa_galpao
    .quad objetos_galpao, (objetos_galpao_fim - objetos_galpao) / OBJ_TAM
    .quad luzes_galpao, (luzes_galpao_fim - luzes_galpao) / LUZ_TAM
    .quad comodos_galpao, (comodos_galpao_fim - comodos_galpao) / COM_TAM
    .quad transicoes_galpao, 0
    .quad nome_galpao
    .quad 0xff2a1e1a                                  # ambiente: quase preto, azulado
    .quad decalques_galpao, 0
    .quad itens_galpao, 0
    .quad 0, 0
andares:
    .quad andar_cima, andar_terreo, andar_galpao, andar_doca, andar_patio, andar_quebramar
n_andares: .quad 6

# Fuga dos anjos: doca, pátio e quebra-mar (andares 3 a 5), seus alto-falantes,
# poleiros, pontos e arrumação, gerados por ferramentas/gerar_doca.py.
.include "doca_dados.inc"

# --------------------------------------------------------- interações

.macro INTERACAO x, y, l, a, andar, exige, some, rotulo, programa
    .long \x, \y, \l, \a, \andar, \exige, \some, 0
    .quad \rotulo, \programa
.endm

.section .rodata
r_sair:         .asciz "ir ao galpão"
r_bilhete:      .asciz "pegar o bilhete"
r_etiqueta:     .asciz "ler a etiqueta"
r_prancheta:    .asciz "examinar a prancheta"
r_estante:      .asciz "examinar a estante"
r_caixa:        .asciz "pegar o disco"
r_aparelhos:    .asciz "examinar os aparelhos"
r_agente:       .asciz "falar com o agente"

.align 8
interacoes_loja:
    INTERACAO 0, 186, 40, 44, 1, -1, FL_ENDERECO, r_sair, prog_sem_endereco
    INTERACAO 0, 186, 40, 44, 1, FL_ENDERECO, FL_SAIU, r_sair, prog_sair
    INTERACAO 256, 174, 64, 20, 1, -1, FL_BILHETE, r_bilhete, prog_bilhete
    # depósito: a lista na estante oeste; o pedido no alto da estante leste
    INTERACAO 192, 253, 32, 22, 1, -1, -1, r_estante, prog_lista
    INTERACAO 272, 253, 32, 22, 1, -1, FL_MELODIA, r_estante, prog_caixa_alto
    INTERACAO 224, 292, 48, 18, 1, -1, -1, r_estante, prog_devolucao
    INTERACAO 284, 256, 36, 30, 1, FL_MELODIA, FL_ENDERECO, r_etiqueta, prog_etiqueta
    INTERACAO 284, 256, 36, 30, 1, FL_ENDERECO, -1, r_etiqueta, prog_etiqueta_lida
interacoes_loja_fim:

interacoes_galpao:
    INTERACAO 112, 30, 36, 18, 2, -1, -1, r_prancheta, prog_prancheta
    INTERACAO 40, 252, 48, 22, 2, -1, FL_DISCO, r_caixa, prog_caixa
    INTERACAO 40, 252, 48, 22, 2, FL_DISCO, -1, r_estante, prog_caixa_vazia
    INTERACAO 244, 31, 64, 18, 2, -1, FL_DISCO, r_aparelhos, prog_aparelhos
    INTERACAO 244, 31, 64, 18, 2, FL_DISCO, -1, r_aparelhos, prog_aparelhos_chiando
    INTERACAO 40, 60, 48, 20, 2, -1, -1, r_estante, prog_fitas
    INTERACAO 168, 60, 48, 20, 2, -1, -1, r_estante, prog_som
    INTERACAO 40, 124, 48, 20, 2, -1, -1, r_estante, prog_sem_capa
    INTERACAO 168, 124, 48, 20, 2, -1, -1, r_estante, prog_fitas
    INTERACAO 40, 188, 48, 20, 2, -1, -1, r_estante, prog_som
    INTERACAO 168, 188, 48, 20, 2, -1, -1, r_estante, prog_sem_capa
    INTERACAO 168, 252, 48, 22, 2, -1, -1, r_estante, prog_sem_capa
    # depois do disco, o agente marcado espera de pé junto ao portão
    INTERACAO 216, 300, 60, 36, 2, FL_DISCO, FL_AGENTE, r_agente, prog_agente
interacoes_galpao_fim:

.equ N_INTER_LOJA, (interacoes_loja_fim - interacoes_loja) / IN_TAM

# D - C - G diante da estante leste do depósito (Ré, Dó, Sol: índices de notas_midi).
.align 4
melodia_deposito:
    .long 1, 264, 253, 48, 30, FL_MELODIA, 3
    .byte 1, 0, 3, 0, 0, 0, 0, 0
.equ N_INTER_GALPAO, (interacoes_galpao_fim - interacoes_galpao) / IN_TAM

prog_sair:
    CMD OP_FLAG, FL_SAIU
    CMD OP_FIM
prog_sem_endereco:
    MSG "Ainda não sei onde fica o galpão... talvez seja melhor procurar por alguma informação."
    CMD OP_FIM
prog_bilhete:
    MSG "Um bilhete no balcão:\n'Pegar o pedido do Anderson. Ele deve estar no depósito,\nlogo depois da estante com a lista do depósito.'\nNo pé do papel: D - C - G\nNotas? No teclado: 1 = C (Dó), 2 = D (Ré), 3 = E (Mi), 4 = G (Sol)."
    CMD OP_ESCONDE, ATOR_BILHETE
    CMD OP_FLAG, FL_BILHETE
    CMD OP_FIM
prog_lista:
    MSG "Presa na estante, a lista do depósito:\n'Usados para triagem, capas avulsas, fitas, encomendas.'"
    CMD OP_FIM
prog_caixa_alto:
    MSG "Lá no alto, uma caixa com etiqueta. Não alcanço."
    CMD OP_FIM
prog_devolucao:
    MSG "Discos riscados separados para devolução. Nada do Anderson."
    CMD OP_FIM
prog_etiqueta:
    MSG "Etiqueta na caixa:\n'Pedido de Anderson - retirar no galpão do Hank,\nRua do Cais, 7, zona portuária.'"
    CMD OP_FLAG, FL_ENDERECO
    CMD OP_FIM
prog_etiqueta_lida:
    MSG "'Galpão do Hank, Rua do Cais, 7, zona portuária.'"
    CMD OP_FIM
prog_prancheta:
    MSG "Inventário do galpão, na letra do Hank:\n'Estante 7 - caixa lacrada. AURORA. NÃO TOCAR.'"
    CMD OP_FIM
prog_caixa:
    MSG "Caixa com fita de aviso. Dentro, um vinil translúcido.\nFrio. Frio demais."
    CMD OP_FLAG, FL_DISCO
    CMD OP_FIM
prog_caixa_vazia:
    MSG "Só o feltro e a fita de aviso ficaram na caixa."
    CMD OP_FIM
prog_aparelhos:
    MSG "Rádios valvulados e uma TV de tubo, desligados da tomada."
    CMD OP_FIM
prog_aparelhos_chiando:
    MSG "Desligados da tomada... e chiando mesmo assim."
    CMD OP_FIM
prog_fitas:
    MSG "Caixas de fita cassete mofadas. Nenhuma com aviso."
    CMD OP_FIM
prog_som:
    MSG "Amplificadores velhos e cabos embolados."
    CMD OP_FIM
prog_sem_capa:
    MSG "Discos sem capa empilhados. Nada lacrado aqui."
    CMD OP_FIM
prog_agente:
    MSG "Agente carmesim: 'Os anjos me marcaram. Se sair sozinho, morre também.'"
    CMD OP_FLAG, FL_AGENTE
    CMD OP_FIM

# ------------------------------------------------------------ roteiro

.global roteiro_principal
.align 8
roteiro_principal:
    # ---- Loja: o bilhete do balcão leva ao depósito; a melodia derruba a caixa
    # com o endereço do galpão. Só depois a porta da rua leva até lá.
    CMD OP_FLAG, FL_NA_LOJA
    ROTULO "loja"
    CMD OP_SE_FLAG, FL_NA_LOJA, p=loja_jogo
    CMD OP_ANDAR, 1, 176, 200, D_S       # só com BSIDE_CENA=loja: começa no térreo
loja_jogo:
    FIXO ATOR_BILHETE, 1, 291, 172, 18, BILHETE
    FIXO ATOR_LISTA, 1, 212, 254, 20, LISTA
    FIXO ATOR_CAIXA, 1, 296, 248, 34, CAIXA_PEDIDO
    OBJETIVO "Descubra onde fica o galpão"
    CMD OP_INTERACOES, N_INTER_LOJA, p=interacoes_loja
    CMD OP_LIBERA
    CMD OP_AGUARDA, FL_BILHETE
    OBJETIVO "Ache o pedido do Anderson no depósito: D - C - G"
    CMD OP_MELODIA, p=melodia_deposito
    CMD OP_AGUARDA, FL_MELODIA
    # a caixa escorrega do alto e cai na frente da estante
    CMD OP_TRAVA
    CMD OP_OBJETIVO
    CMD OP_CAMERA, 296, 262
    CMD OP_TREME, 250
    CMD OP_ESPERA, 400
    MOVE ATOR_CAIXA, 302, 268, 0, 200
    CMD OP_ESPERA, 220
    CMD OP_SOM, SOM_BAQUE
    CMD OP_TREME, 200
    CMD OP_ESPERA, 600
    CMD OP_CAMERA, -1
    OBJETIVO "Leia a etiqueta da caixa"
    CMD OP_LIBERA
    CMD OP_AGUARDA, FL_ENDERECO
    OBJETIVO "Vá ao galpão: saia pela porta da rua"
    CMD OP_AGUARDA, FL_SAIU
    CMD OP_TRAVA
    CMD OP_OBJETIVO
    CMD OP_ESCURECE

    # ---- Galpão: achar a caixa marcada e pegar o disco.
    ROTULO "galpao"
    CMD OP_TRAVA
    CMD OP_ESCURECE
    CMD OP_ANDAR, 2, 22, 52, D_L
    ESCONDE ATOR_AGENTE
    CMD OP_MUSICA, 0
    CMD OP_ZUMBIDO, 20
    CMD OP_NEVOA, 0
    CMD OP_PERTURBA, 0
    CMD OP_CLAREIA
    OBJETIVO "Encontre a caixa marcada"
    CMD OP_INTERACOES, N_INTER_GALPAO, p=interacoes_galpao
    CMD OP_LIBERA
    CMD OP_AGUARDA, FL_DISCO
    # o disco sai da caixa: estática, luz falhando, névoa e Mael na janela
    CMD OP_TRAVA
    CMD OP_OBJETIVO
    CMD OP_SOM, SOM_ESTATICA
    CMD OP_PERTURBA, 1
    CMD OP_TREME, 700
    CMD OP_ZUMBIDO, 60
    CMD OP_NEVOA, 35
    CMD OP_CAMERA, 232, 60
    CMD OP_ESPERA, 900
    FIXO ATOR_MAEL, 2, 232, 16, 37, MAEL, AF_EMISSIVO
    CMD OP_ESPERA, 1500
    ESCONDE ATOR_MAEL
    CMD OP_SOM, SOM_GRITO
    CMD OP_CAMERA, -1
    FIXO ATOR_AGENTE, 2, 246, 322, 0, AGENTE_HD_S, AF_SOMBRA|AF_HD
    OBJETIVO "Saia pelo portão dos fundos"
    CMD OP_LIBERA
    CMD OP_AGUARDA, FL_AGENTE
    CMD OP_TRAVA
    CMD OP_SOM, SOM_GRITO
    CMD OP_TREME, 500
    CMD OP_ESCURECE

    # ---- Fuga: doca, pátio e quebra-mar, ponto a ponto (ferramentas/gerar_doca.py).
    .include "doca_roteiro.inc"

    CMD OP_TRAVA
    CMD OP_OBJETIVO
    MSG "Fim da Sala 2."
    CMD OP_LIBERA
    CMD OP_FIM


.section .note.GNU-stack,"",@progbits
