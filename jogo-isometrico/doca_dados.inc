# Gerado por ferramentas/gerar_doca.py. Não editar à mão.
# Os três trechos da fuga: plantas, móveis, luzes, alto-falantes, poleiros e pontos.

# ---------------------------------------------------------------- DOCA
.section .rodata
nome_doca: .asciz "DOCA"
nome_doca_c0: .asciz "CAIS"
nome_doca_c1: .asciz "PÍER"
nome_doca_c2: .asciz "PASSARELA"
nome_doca_c3: .asciz "CAIS LESTE"
nome_doca_c4: .asciz "PÍER OESTE"
mapa_doca:
    LINHA "XXXXPPXXXXXXXXXXXXXXXX"
    LINHA "#QQQQQQQQQQQQQQQQQQQQ#"
    LINHA "#QQQQQQQQQQQQQQQQQQQQ#"
    LINHA "#QQQQQQQQQQQQQQQQQQQQ#"
    LINHA "#QQQQQQQQQQQQQQQQQQQQ#"
    LINHA "#~TT~~~~~TTTT~~~~QQQQ#"
    LINHA "#~TT~~~~~TTTT~~~~QQQQ#"
    LINHA "#~TT~~~~~TTTT~~~~QQQQ#"
    LINHA "#~TT~~~~~TTTT~~~~QQQQ#"
    LINHA "#~TTTTTTTTTTTTTTTQQQQ#"
    LINHA "#~TTTTTTTTTTTTTTTQQQQ#"
    LINHA "#~TT~~~~~TTTT~~~~QQQQ#"
    LINHA "#~TT~~~~~TTTT~~~~QQQQ#"
    LINHA "#~~~~~~~~TTTT~~~~QQQQ#"
    LINHA "#~~~~~~~~~~~~~~~~QQQQ#"
    LINHA "#~~~~~~~~~~~~~~~~QQQQ#"
    LINHA "#~~~~~~~~~~~~~~~~QQQQ#"
    LINHA "#~~~~~~~~~~~~~~~~QQQQ#"
    LINHA "#~~~~~~~~~~~~~~~~QQQQ#"
    LINHA "#~~~~~~~~~~~~~~~~QQQQ#"
    LINHA "#~~~~~~~~~~~~~~~~QQQQ#"
    LINHA "##################PP##"
.align 8
comodos_doca:
    COMODO 1, 1, 20, 4, nome_doca_c0
    COMODO 9, 5, 12, 13, nome_doca_c1
    COMODO 1, 9, 16, 10, nome_doca_c2
    COMODO 17, 5, 20, 20, nome_doca_c3
    COMODO 2, 5, 3, 12, nome_doca_c4
comodos_doca_fim:
transicoes_doca:
transicoes_doca_fim:
decalques_doca:
decalques_doca_fim:
luzes_doca:
    LUZ 80, 22, 30, 70, 230, 178, 110, OS_FIXA
    LUZ 132, 74, 56, 100, 255, 170, 90, OS_FIXA
    LUZ 216, 134, 56, 100, 255, 170, 90, OS_FALHA
    LUZ 282, 202, 56, 100, 255, 170, 90, OS_FIXA
    LUZ 58, 132, 56, 90, 255, 170, 90, OS_ROTEIRO
    LUZ 304, 330, 30, 80, 220, 120, 90, OS_FIXA
luzes_doca_fim:

.section .data
.align 8
objetos_doca:
    MOVEL4 CONTAINER_VERMELHO, 272, 20
    MOVEL4 CONTAINER_AZUL, 224, 52
    MOVEL POSTE, 128, 72
    MOVEL POSTE, 212, 132
    MOVEL POSTE, 278, 198
    MOVEL POSTE, 54, 130
    MOVEL4 CONTAINER_VERDE, 308, 200
    MOVEL2 CAIXAS_PILHA, 272, 290
    BLOQUEIO 288, 336, 32, 16
    MOVEL ALTO_FALANTE, 81, 80
    MOVEL ALTO_FALANTE, 17, 112
    MOVEL ALTO_FALANTE, 25, 160
    MOVEL ALTO_FALANTE, 129, 176
    MOVEL ALTO_FALANTE, 225, 40
    MOVEL ALTO_FALANTE, 137, 64
    MOVEL ALTO_FALANTE, 129, 112
    MOVEL ALTO_FALANTE, 137, 224
    MOVEL ALTO_FALANTE, 289, 192
    MOVEL ALTO_FALANTE, 321, 264
    MOVEL CABECO, 20, 212
    MOVEL CABECO, 68, 212
    MOVEL CABECO, 124, 200
objetos_doca_fim:

.section .bss
.align 16
itens_doca: .skip MAX_ITENS * IT_TAM

.section .data
.align 8
andar_doca:
    .quad mapa_doca
    .quad objetos_doca, (objetos_doca_fim - objetos_doca) / OBJ_TAM
    .quad luzes_doca, (luzes_doca_fim - luzes_doca) / LUZ_TAM
    .quad comodos_doca, (comodos_doca_fim - comodos_doca) / COM_TAM
    .quad transicoes_doca, 0
    .quad nome_doca
    .quad 0xff40281c
    .quad decalques_doca, 0
    .quad itens_doca, 0
    .quad 0, 0

# ---------------------------------------------------------------- PÁTIO DE CONTÊINERES
.section .rodata
nome_patio: .asciz "PÁTIO DE CONTÊINERES"
nome_patio_c0: .asciz "CONTÊINERES"
mapa_patio:
    LINHA "######################"
    LINHA "#QQQQQQQQQQQQQQQQQQQQ#"
    LINHA "#QQQQQQQQQQQQQQQQQQQQ#"
    LINHA "#QQQQQQQQQQQQQQQQQQQQ#"
    LINHA "#QQQQQQQQQQQQQQQQQQQQ#"
    LINHA "#QQQQQQQQQQQQQQQQQQQQ#"
    LINHA "#QQQQQQQQQQQQQQQQQQQQ#"
    LINHA "#QQQQQQQQQQQQQQQQQQQQ#"
    LINHA "#QQQQQQQQQQQQQQQQQQQQ#"
    LINHA "#QQQQQQQQQQQQQQQQQQQQ#"
    LINHA "#QQQQQQQQQQQQQQQQQQQQ#"
    LINHA "#QQQQQQQQQQQQQQQQQQQQ#"
    LINHA "#QQQQQQQQQQQQQQQQQQQQ#"
    LINHA "#QQQQQQQQQQQQQQQQQQQQ#"
    LINHA "#QQQQQQQQQQQQQQQQQQQQ#"
    LINHA "#QQQQQQQQQQQQQQQQQQQQ#"
    LINHA "#QQQQQQQQQQQQQQQQQQQQ#"
    LINHA "#QQQQQQQQQQQQQQQQQQQQ#"
    LINHA "#QQQQQQQQQQQQQQQQQQQQ#"
    LINHA "#QQQQQQQQQQQQQQQQQQQQ#"
    LINHA "#QQQQQQQQQQQQQQQQQQQQ#"
    LINHA "#################PP###"
.align 8
comodos_patio:
    COMODO 1, 1, 20, 20, nome_patio_c0
comodos_patio_fim:
transicoes_patio:
transicoes_patio_fim:
decalques_patio:
decalques_patio_fim:
luzes_patio:
    LUZ 32, 32, 50, 110, 255, 170, 90, OS_FIXA
    LUZ 176, 160, 60, 130, 255, 170, 90, OS_FALHA
    LUZ 320, 32, 50, 100, 255, 170, 90, OS_FIXA
    LUZ 32, 300, 50, 100, 255, 170, 90, OS_FIXA
    LUZ 300, 300, 50, 110, 255, 170, 90, OS_ROTEIRO
    LUZ 128, 120, 40, 80, 150, 180, 255, OS_FIXA
luzes_patio_fim:

.section .data
.align 8
objetos_patio:
    MOVEL4 CONTAINER_VERMELHO, 48, 48
    MOVEL4 CONTAINER_AZUL, 48, 76
    MOVEL4 CONTAINER_AZUL, 144, 48
    MOVEL4 CONTAINER_VERMELHO, 144, 76
    MOVEL4 CONTAINER_VERMELHO, 240, 48
    MOVEL4 CONTAINER_AZUL, 240, 76
    MOVEL4 CONTAINER_AZUL, 48, 136
    MOVEL4 CONTAINER_VERMELHO, 48, 164
    MOVEL4 CONTAINER_VERMELHO, 240, 136
    MOVEL4 CONTAINER_AZUL, 240, 164
    MOVEL4 CONTAINER_AZUL, 48, 224
    MOVEL4 CONTAINER_VERMELHO, 48, 252
    MOVEL4 CONTAINER_VERMELHO, 144, 224
    MOVEL4 CONTAINER_AZUL, 144, 252
    MOVEL4 CONTAINER_AZUL, 240, 224
    MOVEL4 CONTAINER_VERMELHO, 240, 252
    MOVEL4 CONTAINER_VERDE, 18, 50
    MOVEL4 CONTAINER_AZUL, 144, 18
    MOVEL4 CONTAINER_VERDE, 306, 226
    BLOQUEIO 272, 336, 32, 16
    MOVEL ALTO_FALANTE, 73, 104
    MOVEL ALTO_FALANTE, 113, 40
    MOVEL ALTO_FALANTE, 113, 88
    MOVEL ALTO_FALANTE, 233, 104
    MOVEL ALTO_FALANTE, 305, 64
    MOVEL ALTO_FALANTE, 209, 56
    MOVEL ALTO_FALANTE, 281, 280
    MOVEL ALTO_FALANTE, 305, 104
    MOVEL ALTO_FALANTE, 201, 280
objetos_patio_fim:

.section .bss
.align 16
itens_patio: .skip MAX_ITENS * IT_TAM

.section .data
.align 8
andar_patio:
    .quad mapa_patio
    .quad objetos_patio, (objetos_patio_fim - objetos_patio) / OBJ_TAM
    .quad luzes_patio, (luzes_patio_fim - luzes_patio) / LUZ_TAM
    .quad comodos_patio, (comodos_patio_fim - comodos_patio) / COM_TAM
    .quad transicoes_patio, 0
    .quad nome_patio
    .quad 0xff3a2a22
    .quad decalques_patio, 0
    .quad itens_patio, 0
    .quad 0, 0

# ---------------------------------------------------------------- QUEBRA-MAR
.section .rodata
nome_quebramar: .asciz "QUEBRA-MAR"
nome_quebramar_c0: .asciz "QUEBRA-MAR"
nome_quebramar_c1: .asciz "FAROL"
mapa_quebramar:
    LINHA "######################"
    LINHA "#TTTT~~~~~~~~~~~~~~~~#"
    LINHA "#TTTT~~~~~~~~~~~~~~~~#"
    LINHA "#TTTTTTTTTTTTTTTTT~~~#"
    LINHA "#~~TT~~~~~~~~~~TTT~~~#"
    LINHA "#~~TT~~~~~~~~~~~TT~~~#"
    LINHA "#~~TT~~~~~~~~~~~TT~~~#"
    LINHA "#~~TTTTTTTTTTTTTTTTT~#"
    LINHA "#~~~~~~~~~~TT~~~~~TT~#"
    LINHA "#~~~~~~~~~~TT~~~~~TT~#"
    LINHA "#~~~~~~~~~~TT~~~~~TT~#"
    LINHA "#~TTTTTTTTTTTTT~~~TT~#"
    LINHA "#~TT~~~~~~~~~TT~~~TT~#"
    LINHA "#~TT~~~~~~~~~TT~~~TT~#"
    LINHA "#~TT~~~~~~~~~TTTTTTT~#"
    LINHA "#~TT~~~~~~~~~~~~~~~~~#"
    LINHA "#~TTTTTTTTTTTTTTTTT~~#"
    LINHA "#~~~~~~~~~~~~~~~~TT~~#"
    LINHA "#~~~~~~~~~~~~~~~~TT~~#"
    LINHA "#~~~~~~~~~~~~~QQQQQQ~#"
    LINHA "#~~~~~~~~~~~~~QQQQQQ~#"
    LINHA "######################"
.align 8
comodos_quebramar:
    COMODO 1, 1, 20, 18, nome_quebramar_c0
    COMODO 14, 19, 19, 20, nome_quebramar_c1
comodos_quebramar_fim:
transicoes_quebramar:
transicoes_quebramar_fim:
decalques_quebramar:
decalques_quebramar_fim:
luzes_quebramar:
    LUZ 100, 70, 56, 100, 255, 170, 90, OS_FIXA
    LUZ 200, 104, 56, 100, 255, 170, 90, OS_FALHA
    LUZ 120, 200, 56, 100, 255, 170, 90, OS_FIXA
    LUZ 250, 248, 56, 100, 255, 170, 90, OS_FIXA
    LUZ 150, 280, 56, 100, 255, 170, 90, OS_ROTEIRO
    LUZ 272, 316, 70, 140, 255, 240, 200, OS_CHAMA
luzes_quebramar_fim:

.section .data
.align 8
objetos_quebramar:
    MOVEL POSTE, 100, 68
    MOVEL POSTE, 200, 100
    MOVEL POSTE, 120, 196
    MOVEL POSTE, 248, 244
    MOVEL POSTE, 150, 276
    MOVEL POSTE, 300, 300
    MOVEL ALTO_FALANTE, 97, 72
    MOVEL ALTO_FALANTE, 33, 112
    MOVEL ALTO_FALANTE, 153, 104
    MOVEL ALTO_FALANTE, 289, 40
    MOVEL ALTO_FALANTE, 217, 328
    MOVEL ALTO_FALANTE, 257, 296
    MOVEL ALTO_FALANTE, 209, 280
    MOVEL ALTO_FALANTE, 17, 200
    MOVEL ALTO_FALANTE, 297, 80
    MOVEL ALTO_FALANTE, 249, 88
    MOVEL ALTO_FALANTE, 329, 120
    MOVEL CABECO, 20, 80
    MOVEL CABECO, 188, 92
    MOVEL CABECO, 84, 200
    MOVEL CABECO, 16, 236
objetos_quebramar_fim:

.section .bss
.align 16
itens_quebramar: .skip MAX_ITENS * IT_TAM

.section .data
.align 8
andar_quebramar:
    .quad mapa_quebramar
    .quad objetos_quebramar, (objetos_quebramar_fim - objetos_quebramar) / OBJ_TAM
    .quad luzes_quebramar, (luzes_quebramar_fim - luzes_quebramar) / LUZ_TAM
    .quad comodos_quebramar, (comodos_quebramar_fim - comodos_quebramar) / COM_TAM
    .quad transicoes_quebramar, 0
    .quad nome_quebramar
    .quad 0xff4a3020
    .quad decalques_quebramar, 0
    .quad itens_quebramar, 0
    .quad 0, 0

.section .data
.global alto_falantes
.align 4
# x, y (centro, mundo), altura da corneta, nota (0..3).
alto_falantes:
    .long 84, 84, 30, 3    # doca1_sol
    .long 20, 116, 30, 0    # doca1_arm1
    .long 28, 164, 30, 1    # doca1_arm2
    .long 132, 180, 30, 2    # doca2_sol
    .long 228, 44, 30, 0    # doca2_arm1
    .long 140, 68, 30, 1    # doca2_arm2
    .long 132, 116, 30, 3    # doca2_arm3
    .long 140, 228, 30, 1    # doca3_sol
    .long 292, 196, 30, 0    # doca3_arm1
    .long 324, 268, 30, 2    # doca3_arm2
    .long 76, 108, 30, 0    # patio1_sol
    .long 116, 44, 30, 1    # patio1_arm1
    .long 116, 92, 30, 3    # patio2_sol
    .long 236, 108, 30, 0    # patio2_arm1
    .long 308, 68, 30, 2    # patio3_sol
    .long 212, 60, 30, 0    # patio3_arm1
    .long 284, 284, 30, 1    # patio4_sol
    .long 308, 108, 30, 0    # patio4_arm1
    .long 204, 284, 30, 2    # patio4_arm2
    .long 100, 76, 30, 1    # quebramar1_sol
    .long 36, 116, 30, 0    # quebramar1_arm1
    .long 156, 108, 30, 2    # quebramar1_arm2
    .long 292, 44, 30, 0    # quebramar2_sol
    .long 220, 332, 30, 1    # quebramar2_arm1
    .long 260, 300, 30, 2    # quebramar2_arm2
    .long 212, 284, 30, 3    # quebramar2_arm3
    .long 20, 204, 30, 3    # quebramar3_sol
    .long 300, 84, 30, 0    # quebramar3_arm1
    .long 252, 92, 30, 1    # quebramar3_arm2
    .long 332, 124, 30, 2    # quebramar3_arm3

poleiros_doca_1: .long 48, 100, 0,  48, 116, 0,  56, 84, 0
poleiros_doca_2: .long 88, 160, 0,  104, 156, 0,  24, 216, 8,  72, 216, 8
poleiros_doca_3: .long 232, 160, 0,  288, 240, 0,  128, 204, 8
poleiros_patio_1: .long 80, 32, 0,  128, 76, 0,  80, 76, 40,  32, 84, 40
poleiros_patio_2: .long 176, 120, 0,  224, 76, 0,  80, 160, 40,  176, 76, 40
poleiros_patio_3: .long 224, 164, 0,  284, 32, 0,  176, 32, 40
poleiros_patio_4: .long 224, 256, 0,  272, 308, 0,  176, 250, 40,  272, 250, 40
poleiros_quebramar_1: .long 64, 92, 0,  128, 120, 0,  120, 56, 0,  24, 84, 8
poleiros_quebramar_2: .long 192, 152, 0,  120, 184, 0,  248, 120, 0,  192, 96, 8
poleiros_quebramar_3: .long 160, 264, 0,  288, 288, 0,  88, 204, 8,  20, 240, 8

.align 8
ponto_doca_1:
    .long 64, 36, 48, 188, 80, 5100
    .long 0, 3, ATOR_ANJO + 0, 3
    .quad poleiros_doca_1
    .long 48, 200, 0, 0
ponto_doca_2:
    .long 48, 188, 176, 200, 84, 6200
    .long 3, 4, ATOR_ANJO + 3, 4
    .quad poleiros_doca_2
    .long 192, 206, 0, 0
ponto_doca_3:
    .long 176, 200, 312, 318, 90, 8200
    .long 7, 3, ATOR_ANJO + 7, 3
    .quad poleiros_doca_3
    .long 300, 326, 0, 0
ponto_patio_1:
    .long 32, 32, 128, 120, 92, 5000
    .long 10, 2, ATOR_ANJO + 0, 4
    .quad poleiros_patio_1
    .long 120, 128, 0, 0
ponto_patio_2:
    .long 128, 120, 224, 32, 96, 5400
    .long 12, 2, ATOR_ANJO + 4, 4
    .quad poleiros_patio_2
    .long 232, 26, 0, 0
ponto_patio_3:
    .long 224, 32, 224, 208, 100, 5200
    .long 14, 2, ATOR_ANJO + 8, 3
    .quad poleiros_patio_3
    .long 214, 214, 0, 0
ponto_patio_4:
    .long 224, 208, 320, 316, 104, 5600
    .long 16, 3, ATOR_ANJO + 11, 4
    .quad poleiros_patio_4
    .long 330, 312, 0, 0
ponto_quebramar_1:
    .long 40, 40, 192, 120, 108, 5800
    .long 19, 3, ATOR_ANJO + 0, 4
    .quad poleiros_quebramar_1
    .long 204, 112, 0, 0
ponto_quebramar_2:
    .long 192, 120, 48, 232, 112, 6700
    .long 22, 4, ATOR_ANJO + 4, 4
    .quad poleiros_quebramar_2
    .long 40, 244, 0, 0
ponto_quebramar_3:
    .long 48, 232, 272, 320, 116, 7400
    .long 26, 4, ATOR_ANJO + 8, 4
    .quad poleiros_quebramar_3
    .long 290, 314, 0, 0

.section .rodata
.align 8
prepara_doca:
    ESCONDE ATOR_MAEL
    ESCONDE ATOR_ANJO + 0
    ESCONDE ATOR_ANJO + 1
    ESCONDE ATOR_ANJO + 2
    ESCONDE ATOR_ANJO + 3
    ESCONDE ATOR_ANJO + 4
    ESCONDE ATOR_ANJO + 5
    ESCONDE ATOR_ANJO + 6
    ESCONDE ATOR_ANJO + 7
    ESCONDE ATOR_ANJO + 8
    ESCONDE ATOR_ANJO + 9
    ESCONDE ATOR_ANJO + 10
    ESCONDE ATOR_ANJO + 11
    ESCONDE ATOR_ANJO + 12
    ESCONDE ATOR_ANJO + 13
    ESCONDE ATOR_ANJO + 14
    ESCONDE ATOR_ANJO + 15
    FIXO ATOR_ANJO + 0, 3, 48, 100, 0, ANJO_POUSADO, AF_HD
    FIXO ATOR_ANJO + 1, 3, 48, 116, 0, ANJO_POUSADO, AF_HD
    FIXO ATOR_ANJO + 2, 3, 56, 84, 0, ANJO_POUSADO, AF_HD
    FIXO ATOR_ANJO + 3, 3, 88, 160, 0, ANJO_POUSADO, AF_HD
    FIXO ATOR_ANJO + 4, 3, 104, 156, 0, ANJO_POUSADO, AF_HD
    FIXO ATOR_ANJO + 5, 3, 24, 216, 8, ANJO_POUSADO, AF_HD
    FIXO ATOR_ANJO + 6, 3, 72, 216, 8, ANJO_POUSADO, AF_HD
    FIXO ATOR_ANJO + 7, 3, 232, 160, 0, ANJO_POUSADO, AF_HD
    FIXO ATOR_ANJO + 8, 3, 288, 240, 0, ANJO_POUSADO, AF_HD
    FIXO ATOR_ANJO + 9, 3, 128, 204, 8, ANJO_POUSADO, AF_HD
    CMD OP_MUSICA, 0
    CMD OP_ZUMBIDO, 70
    CMD OP_NEVOA, 45
    CMD OP_PERTURBA, 1
    CMD OP_INTERACOES
    OBJETIVO "Atravesse a doca"
    CMD OP_VOLTA
prepara_patio:
    ESCONDE ATOR_MAEL
    ESCONDE ATOR_ANJO + 0
    ESCONDE ATOR_ANJO + 1
    ESCONDE ATOR_ANJO + 2
    ESCONDE ATOR_ANJO + 3
    ESCONDE ATOR_ANJO + 4
    ESCONDE ATOR_ANJO + 5
    ESCONDE ATOR_ANJO + 6
    ESCONDE ATOR_ANJO + 7
    ESCONDE ATOR_ANJO + 8
    ESCONDE ATOR_ANJO + 9
    ESCONDE ATOR_ANJO + 10
    ESCONDE ATOR_ANJO + 11
    ESCONDE ATOR_ANJO + 12
    ESCONDE ATOR_ANJO + 13
    ESCONDE ATOR_ANJO + 14
    ESCONDE ATOR_ANJO + 15
    FIXO ATOR_ANJO + 0, 4, 80, 32, 0, ANJO_POUSADO, AF_HD
    FIXO ATOR_ANJO + 1, 4, 128, 76, 0, ANJO_POUSADO, AF_HD
    FIXO ATOR_ANJO + 2, 4, 80, 76, 40, ANJO_POUSADO, AF_HD
    FIXO ATOR_ANJO + 3, 4, 32, 84, 40, ANJO_POUSADO, AF_HD
    FIXO ATOR_ANJO + 4, 4, 176, 120, 0, ANJO_POUSADO, AF_HD
    FIXO ATOR_ANJO + 5, 4, 224, 76, 0, ANJO_POUSADO, AF_HD
    FIXO ATOR_ANJO + 6, 4, 80, 160, 40, ANJO_POUSADO, AF_HD
    FIXO ATOR_ANJO + 7, 4, 176, 76, 40, ANJO_POUSADO, AF_HD
    FIXO ATOR_ANJO + 8, 4, 224, 164, 0, ANJO_POUSADO, AF_HD
    FIXO ATOR_ANJO + 9, 4, 284, 32, 0, ANJO_POUSADO, AF_HD
    FIXO ATOR_ANJO + 10, 4, 176, 32, 40, ANJO_POUSADO, AF_HD
    FIXO ATOR_ANJO + 11, 4, 224, 256, 0, ANJO_POUSADO, AF_HD
    FIXO ATOR_ANJO + 12, 4, 272, 308, 0, ANJO_POUSADO, AF_HD
    FIXO ATOR_ANJO + 13, 4, 176, 250, 40, ANJO_POUSADO, AF_HD
    FIXO ATOR_ANJO + 14, 4, 272, 250, 40, ANJO_POUSADO, AF_HD
    CMD OP_MUSICA, 0
    CMD OP_ZUMBIDO, 70
    CMD OP_NEVOA, 45
    CMD OP_PERTURBA, 1
    CMD OP_INTERACOES
    OBJETIVO "Atravesse o pátio"
    CMD OP_VOLTA
prepara_quebramar:
    ESCONDE ATOR_MAEL
    ESCONDE ATOR_ANJO + 0
    ESCONDE ATOR_ANJO + 1
    ESCONDE ATOR_ANJO + 2
    ESCONDE ATOR_ANJO + 3
    ESCONDE ATOR_ANJO + 4
    ESCONDE ATOR_ANJO + 5
    ESCONDE ATOR_ANJO + 6
    ESCONDE ATOR_ANJO + 7
    ESCONDE ATOR_ANJO + 8
    ESCONDE ATOR_ANJO + 9
    ESCONDE ATOR_ANJO + 10
    ESCONDE ATOR_ANJO + 11
    ESCONDE ATOR_ANJO + 12
    ESCONDE ATOR_ANJO + 13
    ESCONDE ATOR_ANJO + 14
    ESCONDE ATOR_ANJO + 15
    FIXO ATOR_ANJO + 0, 5, 64, 92, 0, ANJO_POUSADO, AF_HD
    FIXO ATOR_ANJO + 1, 5, 128, 120, 0, ANJO_POUSADO, AF_HD
    FIXO ATOR_ANJO + 2, 5, 120, 56, 0, ANJO_POUSADO, AF_HD
    FIXO ATOR_ANJO + 3, 5, 24, 84, 8, ANJO_POUSADO, AF_HD
    FIXO ATOR_ANJO + 4, 5, 192, 152, 0, ANJO_POUSADO, AF_HD
    FIXO ATOR_ANJO + 5, 5, 120, 184, 0, ANJO_POUSADO, AF_HD
    FIXO ATOR_ANJO + 6, 5, 248, 120, 0, ANJO_POUSADO, AF_HD
    FIXO ATOR_ANJO + 7, 5, 192, 96, 8, ANJO_POUSADO, AF_HD
    FIXO ATOR_ANJO + 8, 5, 160, 264, 0, ANJO_POUSADO, AF_HD
    FIXO ATOR_ANJO + 9, 5, 288, 288, 0, ANJO_POUSADO, AF_HD
    FIXO ATOR_ANJO + 10, 5, 88, 204, 8, ANJO_POUSADO, AF_HD
    FIXO ATOR_ANJO + 11, 5, 20, 240, 8, ANJO_POUSADO, AF_HD
    CMD OP_MUSICA, 0
    CMD OP_ZUMBIDO, 70
    CMD OP_NEVOA, 45
    CMD OP_PERTURBA, 1
    CMD OP_INTERACOES
    OBJETIVO "Chegue ao farol"
    CMD OP_VOLTA
