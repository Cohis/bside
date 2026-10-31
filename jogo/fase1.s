.intel_syntax noprefix

# Fase 1, sala 1: interior da B-Side em dois andares.
# Este arquivo só tem dados: plantas, móveis, luzes, cômodos e escadas.
# Coordenadas de objetos e luzes estão em px do mundo (TILE = 16 px).

.include "estruturas.inc"
.include "tileset.inc"

# Uma linha da planta. O montador recusa linhas com largura errada.
.macro LINHA texto
9:  .ascii "\texto"
    .if (. - 9b) - LARGURA_MAPA
    .error "linha do mapa com largura diferente de LARGURA_MAPA"
    .endif
.endm

# Móvel apoiado no chão: x à esquerda, base = y onde ele toca o piso.
.macro MOVEL nome, x, base, cx=0, cy=0, cl=0, ca=0, anim=AN_NENHUMA, osc=OS_FIXA
    .long \x, (\base) - S_\nome\()_A, S_\nome\()_L, S_\nome\()_A
    .long S_\nome\()_X, S_\nome\()_Y, S_\nome\()_L, S_\nome\()_A
    .long \base, CAM_ORDENADA, \cx, \cy, \cl, \ca, \anim, \osc
.endm

# Peça sem ordenação: tapetes e quadros (CAM_CHAO), teto ou brilho próprio.
.macro PECA nome, x, y, camada=CAM_CHAO, anim=AN_NENHUMA, osc=OS_FIXA
    .long \x, \y, S_\nome\()_L, S_\nome\()_A
    .long S_\nome\()_X, S_\nome\()_Y, S_\nome\()_L, S_\nome\()_A
    .long (\y) + S_\nome\()_A, \camada, 0, 0, 0, 0, \anim, \osc
.endm

# Só colisão, sem desenho (pés de móveis cujo sprite não bloqueia inteiro).
.macro BLOQUEIO cx, cy, cl, ca
    .long 0, 0, 0, 0, 0, 0, 0, 0
    .long 0, CAM_INVISIVEL, \cx, \cy, \cl, \ca, AN_NENHUMA, OS_FIXA
.endm

.macro LUZ x, y, raio, r, g, b, osc=OS_FIXA
    .long \x, \y, \raio, (\r) | ((\g) << 8) | ((\b) << 16) | (255 << 24), \osc, 0, 0, 0
.endm

.macro COMODO x0, y0, x1, y1, nome
    .long \x0, \y0, \x1, \y1
    .quad \nome
.endm

.macro ESCADA x, y, l, a, destino, chegada_x, chegada_y, direcao
    .long \x, \y, \l, \a, \destino, \chegada_x, \chegada_y, \direcao
.endm

.section .rodata
nome_andar_cima:   .asciz "ANDAR DE CIMA"
nome_terreo:       .asciz "TERREO"
nome_escada:       .asciz "ESCADA"
nome_corredor:     .asciz "CORREDOR"
nome_cozinha:      .asciz "COZINHA"
nome_hospedes:     .asciz "QUARTO DE HOSPEDES"
nome_sala:         .asciz "SALA DE ESTAR"
nome_loja:         .asciz "LOJA"
nome_cafeteria:    .asciz "CAFETERIA"
nome_deposito:     .asciz "DEPOSITO"

# Legenda dos caracteres das plantas.
.align 4
.global tipos_tile
.global n_tipos_tile
tipos_tile:
    .long 35,  T_TOPO, CL_TOPO, 16                 # parede vista de cima
    .long '.', T_PISO_CORREDOR, CL_PISO, 4         # patamar e corredor
    .long 'K', T_PISO_COZINHA, CL_PISO, 4
    .long 'H', T_PISO_HOSPEDES, CL_PISO, 4
    .long 'L', T_PISO_SALA, CL_PISO, 4
    .long 'S', T_PISO_LOJA, CL_PISO, 4
    .long 'C', T_PISO_CAFE, CL_PISO, 4
    .long 'D', T_PISO_DEPOSITO, CL_PISO, 4
    .long '^', T_DEGRAU, CL_PISO, 4                # degraus andáveis
    .long 'v', T_VAO, CL_SOLIDO, 4                 # vão da escada descendo
    .long 'a', T_FACE_CORREDOR, CL_FACE, 6
    .long 'j', T_FACE_JANELA, CL_FACE, 6
    .long 'h', T_FACE_HOSPEDES, CL_FACE, 6
    .long 'l', T_FACE_SALA, CL_FACE, 6
    .long 's', T_FACE_LOJA, CL_FACE, 6
    .long 'c', T_FACE_CAFE, CL_FACE, 6
    .long 'd', T_FACE_DEPOSITO, CL_FACE, 6
    .long 'o', T_FACE_ESCADA, CL_FACE, 6           # escada sumindo no teto
    .long 'w', T_JANELA_LATERAL, CL_COLUNA, 3
    .long 'e', T_PORTA_VIDRO, CL_COLUNA, 3
    .long '|', T_GUARDA_CIMA, CL_COLUNA, 3
    .long '!', T_GUARDA_TERREO, CL_COLUNA, 3
tipos_tile_fim:
n_tipos_tile: .long (tipos_tile_fim - tipos_tile) / TT_TAM

# ------------------------------------------------------------------
# Andar de cima. Quem sobe chega ao patamar, vira à direita e de novo
# à direita para entrar no corredor: 1a porta cozinha, 2a porta quarto
# de hóspedes, fim do corredor sala de estar.
mapa_cima:
    LINHA "########################"    #  0
    LINHA "#aaaaaaa#jjjjjjjjjjjjjj#"    #  1  janela da cozinha de ponta a ponta
    LINHA "#aaaaaaa#jjjjjjjjjjjjjj#"    #  2
    LINHA "#aaaaaaa#jjjjjjjjjjjjjj#"    #  3
    LINHA "#.......#KKKKKKKKKKKKKK#"    #  4  patamar | cozinha
    LINHA "#.......#KKKKKKKKKKKKKK#"    #  5
    LINHA "#^^^|...#KKKKKKKKKKKKKK#"    #  6  topo da escada
    LINHA "#^^^|....KKKKKKKKKKKKKK#"    #  7  porta 1
    LINHA "#vvv|....KKKKKKKKKKKKKK#"    #  8
    LINHA "#vvv|...#KKKKKKKKKKKKKK#"    #  9
    LINHA "#vvv|...#KKKKKKKKKKKKKK#"    # 10
    LINHA "#vvv|...################"    # 11
    LINHA "#vvv|...#hhhhhhhhhhhhhh#"    # 12
    LINHA "#vvv|...#hhhhhhhhhhhhhh#"    # 13
    LINHA "#vvv|...#hhhhhhhhhhhhhh#"    # 14
    LINHA "#####...#HHHHHHHHHHHHHH#"    # 15  quarto de hóspedes
    LINHA "#####....HHHHHHHHHHHHHHw"    # 16  porta 2
    LINHA "#####....HHHHHHHHHHHHHHw"    # 17
    LINHA "#####...#HHHHHHHHHHHHHHw"    # 18
    LINHA "#####...#HHHHHHHHHHHHHH#"    # 19
    LINHA "#####...################"    # 20  fim do corredor
    LINHA "#llll...lllllllllllllll#"    # 21
    LINHA "#llll...lllllllllllllll#"    # 22
    LINHA "#llll...lllllllllllllll#"    # 23
    LINHA "#LLLLLLLLLLLLLLLLLLLLLL#"    # 24  sala de estar
    LINHA "#LLLLLLLLLLLLLLLLLLLLLL#"    # 25
    LINHA "#LLLLLLLLLLLLLLLLLLLLLLw"    # 26
    LINHA "#LLLLLLLLLLLLLLLLLLLLLLw"    # 27
    LINHA "#LLLLLLLLLLLLLLLLLLLLLLw"    # 28
    LINHA "#LLLLLLLLLLLLLLLLLLLLLL#"    # 29
    LINHA "#LLLLLLLLLLLLLLLLLLLLLL#"    # 30
    LINHA "#LLLLLLLLLLLLLLLLLLLLLL#"    # 31
    LINHA "########################"    # 32

# Térreo. A escada sobe pela lateral oeste da loja; cafeteria e
# depósito ficam abaixo dela.
mapa_terreo:
    LINHA "########################"    #  0
    LINHA "#ooosssssssssssssssssss#"    #  1  letreiro B-SIDE
    LINHA "#ooosssssssssssssssssss#"    #  2
    LINHA "#ooosssssssssssssssssss#"    #  3
    LINHA "#^^^!SSSSSSSSSSSSSSSSSS#"    #  4  topo da escada
    LINHA "#^^^!SSSSSSSSSSSSSSSSSSw"    #  5  vitrine
    LINHA "#^^^!SSSSSSSSSSSSSSSSSSw"    #  6
    LINHA "#^^^!SSSSSSSSSSSSSSSSSSw"    #  7
    LINHA "#^^^!SSSSSSSSSSSSSSSSSS#"    #  8
    LINHA "#^^^!SSSSSSSSSSSSSSSSSS#"    #  9
    LINHA "#^^^!SSSSSSSSSSSSSSSSSS#"    # 10
    LINHA "#^^^!SSSSSSSSSSSSSSSSSS#"    # 11
    LINHA "#^^^!SSSSSSSSSSSSSSSSSS#"    # 12
    LINHA "#^^^SSSSSSSSSSSSSSSSSSS#"    # 13  pé da escada
    LINHA "#SSSSSSSSSSSSSSSSSSSSSS#"    # 14
    LINHA "#SSSSSSSSSSSSSSSSSSSSSSe"    # 15  porta da rua
    LINHA "#SSSSSSSSSSSSSSSSSSSSSSe"    # 16
    LINHA "#SSSSSSSSSSSSSSSSSSSSSSe"    # 17
    LINHA "#SSSSSSSSSSSSSSSSSSSSSS#"    # 18
    LINHA "#SSSSSSSSSSSSSSSSSSSSSS#"    # 19
    LINHA "#####CCC#########DD#####"    # 20  passagens
    LINHA "#ccccCCCccccc#dddDDdddd#"    # 21
    LINHA "#ccccCCCccccc#dddDDdddd#"    # 22
    LINHA "#ccccCCCccccc#dddDDdddd#"    # 23
    LINHA "#CCCCCCCCCCCC#DDDDDDDDD#"    # 24  cafeteria | depósito
    LINHA "#CCCCCCCCCCCC#DDDDDDDDD#"    # 25
    LINHA "#CCCCCCCCCCCC#DDDDDDDDD#"    # 26
    LINHA "#CCCCCCCCCCCC#DDDDDDDDD#"    # 27
    LINHA "#CCCCCCCCCCCC#DDDDDDDDD#"    # 28
    LINHA "#CCCCCCCCCCCC#DDDDDDDDD#"    # 29
    LINHA "#CCCCCCCCCCCC#DDDDDDDDD#"    # 30
    LINHA "#CCCCCCCCCCCC#DDDDDDDDD#"    # 31
    LINHA "########################"    # 32

.align 8
comodos_cima:
    COMODO 1, 6, 3, 14, nome_escada
    COMODO 1, 4, 8, 23, nome_corredor
    COMODO 9, 4, 22, 10, nome_cozinha
    COMODO 9, 15, 22, 19, nome_hospedes
    COMODO 1, 24, 22, 31, nome_sala
comodos_cima_fim:

comodos_terreo:
    COMODO 1, 4, 3, 13, nome_escada
    COMODO 1, 4, 22, 19, nome_loja
    COMODO 1, 20, 12, 31, nome_cafeteria
    COMODO 14, 20, 22, 31, nome_deposito
comodos_terreo_fim:

# Gatilhos nos degraus; a chegada fica fora do gatilho do outro andar.
transicoes_cima:
    ESCADA 1*TILE, 7*TILE, 3*TILE, TILE, 1, 2*TILE+8, 5*TILE+12, DIR_SUL
transicoes_cima_fim:

transicoes_terreo:
    ESCADA 1*TILE, 4*TILE, 3*TILE, 12, 0, 2*TILE+8, 5*TILE+8, DIR_NORTE
transicoes_terreo_fim:

luzes_cima:
    LUZ 64, 52, 80, 202, 148, 94, OS_CHAMA              # arandela do patamar
    LUZ 104, 190, 98, 162, 122, 81, OS_CHAMA            # teto do corredor
    LUZ 104, 300, 69, 122, 94, 68                       # fim do corredor
    LUZ 190, 74, 86, 81, 108, 189                       # luar pela janela
    LUZ 270, 74, 86, 81, 108, 189
    LUZ 345, 74, 80, 81, 108, 189
    LUZ 246, 128, 98, 255, 189, 108, OS_CHAMA           # pendente da mesa
    LUZ 168, 236, 63, 255, 202, 108, OS_CHAMA           # luminária da escrivaninha
    LUZ 360, 272, 92, 74, 101, 176                      # janela do quarto de hóspedes
    LUZ 192, 404, 144, 94, 162, 255, OS_TV              # brilho da TV
    LUZ 246, 432, 103, 255, 182, 101, OS_CHAMA          # luminária de pé
    LUZ 66, 352, 48, 255, 216, 122                      # luz de leitura da cama do Ícaro
    LUZ 360, 444, 92, 74, 101, 176                      # janelas da sala
luzes_cima_fim:

luzes_terreo:
    LUZ 228, 76, 120, 200, 120, 100                     # placa B-SIDE, luz morna
    LUZ 180, 140, 130, 235, 170, 100, OS_CHAMA          # pendentes da loja
    LUZ 180, 228, 130, 235, 170, 100, OS_CHAMA
    LUZ 124, 58, 85, 220, 160, 95                       # luzes de latão das estantes
    LUZ 324, 58, 85, 220, 160, 95
    LUZ 300, 162, 80, 243, 189, 108                     # luminária do balcão
    LUZ 360, 104, 80, 74, 101, 176                      # vitrine
    LUZ 362, 266, 103, 255, 162, 74                     # poste da rua pela porta
    LUZ 40, 150, 69, 148, 108, 74                       # escada
    LUZ 69, 455, 98, 255, 176, 94, OS_CHAMA             # pendentes da cafeteria
    LUZ 149, 470, 98, 255, 176, 94, OS_CHAMA
    LUZ 150, 384, 80, 255, 189, 81, OS_CHAMA            # vitrola
    LUZ 296, 432, 132, 255, 250, 189, OS_FALHA          # lâmpada do depósito
luzes_terreo_fim:

.section .data
.align 8
# Os objetos ficam em .data porque o motor os ordena por base no início.
objetos_cima:
    # patamar e corredor
    PECA QUADRO_1, 22, 24
    PECA QUADRO_3, 82, 24
    PECA ARANDELA, 60, 30
    MOVEL PLANTA, 62, 80, 66, 74, 10, 6
    PECA PASSADEIRA, 91, 128
    PECA PASSADEIRA, 91, 192
    PECA PASSADEIRA, 91, 256
    PECA BATENTE, 80, 336
    PECA BATENTE, 124, 336
    # cozinha
    PECA JANELA_COZINHA, 144, 16
    PECA JANELA_COZINHA_LUZ, 144, 16, CAM_EMISSIVA
    MOVEL BANCADA, 144, 80, 144, 66, 144, 14
    MOVEL GELADEIRA, 348, 112, 348, 92, 20, 20
    MOVEL MESA_COZINHA, 226, 144, 226, 130, 44, 14
    MOVEL CADEIRA_E, 212, 140, 212, 134, 12, 6
    MOVEL CADEIRA_D, 272, 140, 272, 134, 12, 6
    PECA PENDENTE, 242, 96, CAM_TETO
    PECA TAPETE_COZINHA, 204, 112
    MOVEL PLANTA, 146, 176, 150, 170, 10, 6
    MOVEL LIXEIRA, 326, 80, 327, 74, 10, 6
    # quarto de hóspedes: só cama, mesa e janela
    MOVEL CAMA_HOSPEDES, 312, 290, 313, 246, 30, 44
    MOVEL ESCRIVANINHA, 160, 258, 160, 244, 44, 14
    MOVEL CADEIRA_COSTAS, 175, 274, 176, 268, 12, 6
    # sala de estar
    PECA POSTER_1, 100, 346
    PECA POSTER_3, 248, 346
    PECA TV, 163, 340
    PECA TELA_TV, 165, 342, CAM_EMISSIVA, AN_NENHUMA, OS_TV
    PECA TAPETE, 140, 404
    MOVEL RACK, 158, 400, 158, 390, 68, 10
    MOVEL CAIXA_SOM, 136, 400, 136, 392, 14, 8
    MOVEL CAIXA_SOM, 234, 400, 234, 392, 14, 8
    MOVEL PUFE, 96, 470, 98, 460, 18, 10
    MOVEL SOFA, 160, 472, 160, 454, 64, 18
    MOVEL ESTANTE, 288, 394, 288, 384, 56, 10
    PECA PLANTA_TOPO, 324, 334, CAM_TETO
    MOVEL LUMINARIA, 240, 462, 242, 456, 8, 6
    MOVEL PLANTA, 344, 506, 348, 500, 10, 6
    # cama do Ícaro: barras no chão, colchão quase no teto
    MOVEL CAMA_ICARO_ESTRUTURA, 18, 416
    BLOQUEIO 18, 410, 6, 6
    BLOQUEIO 60, 410, 14, 6
    PECA CAMA_ICARO_COLCHAO, 18, 340, CAM_TETO
objetos_cima_fim:

objetos_terreo:
    # loja
    PECA LETREIRO_FUNDO, 172, 20
    PECA LETREIRO_LETRAS, 172, 20, CAM_EMISSIVA
    MOVEL ESTANTE_DISCOS, 84, 80, 84, 66, 80, 14
    MOVEL ESTANTE_DISCOS, 284, 80, 284, 66, 80, 14
    MOVEL CAIXOTE, 112, 160, 112, 146, 44, 14
    MOVEL CAIXOTE, 208, 160, 208, 146, 44, 14
    MOVEL CAIXOTE, 112, 240, 112, 226, 44, 14
    MOVEL CAIXOTE, 208, 240, 208, 226, 44, 14
    PECA PENDENTE_COBRE, 174, 92, CAM_TETO
    PECA PENDENTE_COBRE, 174, 180, CAM_TETO
    MOVEL BANQUINHO, 330, 172, 331, 166, 10, 6
    MOVEL BALCAO, 288, 192, 288, 176, 80, 16
    PECA CAPACHO, 352, 242
    MOVEL PLANTA, 82, 316, 86, 310, 10, 6
    MOVEL PLANTA, 348, 128, 352, 122, 10, 6
    PECA BATENTE, 80, 336
    PECA BATENTE, 124, 336
    PECA BATENTE, 272, 336
    PECA BATENTE, 300, 336
    # cafeteria, com o vinil tocando
    PECA LOUSA, 24, 342
    PECA QUADRO_DISCO_1, 88, 346
    PECA QUADRO_DISCO_2, 184, 342
    MOVEL BALCAO_CAFE, 16, 400, 16, 386, 64, 14
    MOVEL VITROLA, 128, 400, 128, 388, 44, 12
    MOVEL DISCO, 137, 382, 0, 0, 0, 0, AN_DISCO
    PECA NOTA, 148, 356, CAM_EMISSIVA, AN_NOTAS
    MOVEL CATALOGO, 178, 402, 180, 394, 20, 8
    MOVEL MESA_REDONDA, 56, 466, 60, 458, 18, 8
    MOVEL CADEIRA_E, 42, 464, 42, 458, 12, 6
    MOVEL CADEIRA_D, 84, 464, 84, 458, 12, 6
    MOVEL MESA_REDONDA, 136, 482, 140, 474, 18, 8
    MOVEL CADEIRA_E, 122, 480, 122, 474, 12, 6
    MOVEL CADEIRA_D, 164, 480, 164, 474, 12, 6
    PECA PENDENTE_COBRE, 63, 410, CAM_TETO
    PECA PENDENTE_COBRE, 143, 426, CAM_TETO
    MOVEL PLANTA, 188, 508, 192, 502, 10, 6
    # depósito: estantes, caixas e a caixa marcada
    MOVEL PRATELEIRA, 224, 400, 224, 388, 48, 12
    MOVEL PRATELEIRA, 320, 400, 320, 388, 48, 12
    MOVEL PRATELEIRA_MARCADA, 248, 464, 248, 452, 80, 12
    MOVEL CAIXAS_PILHA, 334, 508, 334, 494, 30, 14
    MOVEL CAIXA_PEQUENA, 228, 506, 228, 496, 16, 10
    PECA LAMPADA, 292, 392, CAM_TETO
    PECA BRILHO_LAMPADA, 290, 405, CAM_EMISSIVA, AN_NENHUMA, OS_FALHA
objetos_terreo_fim:

.global andares
.align 8
andar_cima:
    .quad mapa_cima
    .quad objetos_cima, (objetos_cima_fim - objetos_cima) / OBJ_TAM
    .quad luzes_cima, (luzes_cima_fim - luzes_cima) / LUZ_TAM
    .quad comodos_cima, (comodos_cima_fim - comodos_cima) / COM_TAM
    .quad transicoes_cima, (transicoes_cima_fim - transicoes_cima) / TR_TAM
    .quad nome_andar_cima
    .quad 0xff3a2826                                  # ambiente (ABGR): azul-arroxeado escuro
andar_terreo:
    .quad mapa_terreo
    .quad objetos_terreo, (objetos_terreo_fim - objetos_terreo) / OBJ_TAM
    .quad luzes_terreo, (luzes_terreo_fim - luzes_terreo) / LUZ_TAM
    .quad comodos_terreo, (comodos_terreo_fim - comodos_terreo) / COM_TAM
    .quad transicoes_terreo, (transicoes_terreo_fim - transicoes_terreo) / TR_TAM
    .quad nome_terreo
    .quad 0xff1e2834                                  # ambiente morno
andares:
    .quad andar_cima, andar_terreo

.section .note.GNU-stack,"",@progbits
