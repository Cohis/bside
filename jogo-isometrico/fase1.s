.intel_syntax noprefix

# Fase 1, sala 1: interior da B-Side em dois andares, versão isométrica.
# Só dados: plantas, papéis de parede, móveis, decalques, luzes, cômodos e escadas.
# Coordenadas de móveis e luzes em px do mundo (TILE = 16 px). Na isométrica só
# as paredes do norte e do oeste de cada cômodo aparecem de pé; por isso as
# janelas ficam nessas paredes.

.include "estruturas.inc"
.include "tileset.inc"

.include "cenario.inc"

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

# Papéis de parede, na ordem dos índices usados em tipos_tile.
.align 4
.global papeis
papeis:
    PAPEL CORREDOR                  #  0
    PAPEL COZINHA                   #  1
    PAPEL HOSPEDES                  #  2
    PAPEL SALA                      #  3
    PAPEL LOJA                      #  4
    PAPEL CAFE                      #  5
    PAPEL DEPOSITO                  #  6
    PAPEL_BRILHO JANELA_COZINHA_0   #  7  janela de ponta a ponta, 4 recortes da cidade
    PAPEL_BRILHO JANELA_COZINHA_1   #  8
    PAPEL_BRILHO JANELA_COZINHA_2   #  9
    PAPEL_BRILHO JANELA_COZINHA_3   # 10
    PAPEL_BRILHO JANELA             # 11
    PAPEL_BRILHO PORTA              # 12
    PAPEL GUARDA                    # 13
    PAPEL ESCADA                    # 14
    # Sala 2: galpão e doca
    PAPEL GALPAO                    # 15  chapa ondulada por dentro
    PAPEL GALPAO_EXT                # 16  a mesma chapa vista da doca
    PAPEL MURO                      # 17  muro de concreto do porto
    PAPEL_BRILHO JANELA_GALPAO      # 18  janelas altas de caixilho de ferro
    PAPEL_BRILHO PORTAO             # 19  portão de correr entreaberto

.global tipos_tile
.global n_tipos_tile
tipos_tile:
    .long 35,  S_TOPO_X, S_TOPO_Y, CL_PAREDE, 1, PAPEL_VIZINHO, ALTURA_PAREDE, 0
    .long 'j', S_TOPO_X, S_TOPO_Y, CL_PAREDE, 4, 7, ALTURA_PAREDE, 0
    .long 'w', S_TOPO_X, S_TOPO_Y, CL_PAREDE, 1, 11, ALTURA_PAREDE, 0
    .long 'e', S_TOPO_X, S_TOPO_Y, CL_PAREDE, 1, 12, ALTURA_PAREDE, 0
    .long '|', S_TOPO_MADEIRA_X, S_TOPO_MADEIRA_Y, CL_PAREDE, 1, 13, 14, 0
    .long '!', S_TOPO_MADEIRA_X, S_TOPO_MADEIRA_Y, CL_PAREDE, 1, 13, 14, 0
    .long '.', S_PISO_CORREDOR_X, S_PISO_CORREDOR_Y, CL_PISO, 4, 0, 0, 0
    .long 'K', S_PISO_COZINHA_X, S_PISO_COZINHA_Y, CL_PISO, 4, 1, 0, 0
    .long 'H', S_PISO_HOSPEDES_X, S_PISO_HOSPEDES_Y, CL_PISO, 4, 2, 0, 0
    .long 'L', S_PISO_SALA_X, S_PISO_SALA_Y, CL_PISO, 4, 3, 0, 0
    .long 'S', S_PISO_LOJA_X, S_PISO_LOJA_Y, CL_PISO, 4, 4, 0, 0
    .long 'C', S_PISO_CAFE_X, S_PISO_CAFE_Y, CL_PISO, 4, 5, 0, 0
    .long 'D', S_PISO_DEPOSITO_X, S_PISO_DEPOSITO_Y, CL_PISO, 4, 6, 0, 0
    .long '^', S_DEGRAU_X, S_DEGRAU_Y, CL_DEGRAU, 4, 4, 0, 0        # degraus do térreo
    .long ',', S_DEGRAU_X, S_DEGRAU_Y, CL_DEGRAU, 4, 0, 0, 0        # topo da escada, em cima
    .long 'v', S_VAO_X, S_VAO_Y, CL_VAO, 4, 0, 0, 0
    # Sala 2
    .long 'J', S_TOPO_X, S_TOPO_Y, CL_PAREDE, 1, 18, ALTURA_PAREDE, 0
    .long 'X', S_TOPO_X, S_TOPO_Y, CL_PAREDE, 1, 16, ALTURA_PAREDE, 0
    .long 'P', S_TOPO_X, S_TOPO_Y, CL_PAREDE, 1, 19, ALTURA_PAREDE, 0
    .long 'G', S_PISO_GALPAO_X, S_PISO_GALPAO_Y, CL_PISO, 4, 15, 0, 0
    .long 'Q', S_PISO_CAIS_X, S_PISO_CAIS_Y, CL_PISO, 4, 17, 0, 0
    .long 'T', S_PISO_DOCA_X, S_PISO_DOCA_Y, CL_PISO, 4, 17, 0, 0
    .long '~', S_AGUA_X, S_AGUA_Y, CL_VAO, 4, 17, 0, 0
tipos_tile_fim:
n_tipos_tile: .long (tipos_tile_fim - tipos_tile) / TT_TAM

# ------------------------------------------------------------------
# Andar de cima. Quem sobe chega ao patamar, vira à direita e de novo à
# direita para entrar no corredor: 1a porta cozinha (leste), 2a porta quarto
# de hóspedes (oeste), fim do corredor sala de estar.
mapa_cima:
    LINHA "########jjjjjjjjjjjjj#"    #  0  janela da cozinha de ponta a ponta
    LINHA "#......#KKKKKKKKKKKKK#"    #  1  patamar | cozinha
    LINHA "#......#KKKKKKKKKKKKK#"    #  2
    LINHA "#,,,|..#KKKKKKKKKKKKK#"    #  3  topo da escada
    LINHA "#,,,|...KKKKKKKKKKKKK#"    #  4  porta 1
    LINHA "#vvv|...KKKKKKKKKKKKK#"    #  5
    LINHA "#vvv|..#KKKKKKKKKKKKK#"    #  6
    LINHA "#vvv|..#KKKKKKKKKKKKK#"    #  7
    LINHA "#####..###############"    #  8
    LINHA "#HHH#..#LLLLLLLLLLLLL#"    #  9  hóspedes | sala
    LINHA "wHHH...#LLLLLLLLLLLLL#"    # 10  porta 2, janela a oeste
    LINHA "wHHH...#LLLLLLLLLLLLL#"    # 11
    LINHA "wHHH#..#LLLLLLLLLLLLL#"    # 12
    LINHA "#HHH#..#LLLLLLLLLLLLL#"    # 13
    LINHA "#####..#LLLLLLLLLLLLL#"    # 14
    LINHA "#LLLLLLLLLLLLLLLLLLLL#"    # 15  fim do corredor
    LINHA "#LLLLLLLLLLLLLLLLLLLL#"    # 16
    LINHA "#LLLLLLLLLLLLLLLLLLLL#"    # 17
    LINHA "#LLLLLLLLLLLLLLLLLLLL#"    # 18
    LINHA "#LLLLLLLLLLLLLLLLLLLL#"    # 19
    LINHA "#LLLLLLLLLLLLLLLLLLLL#"    # 20
    LINHA "######################"    # 21

# Térreo. A escada sobe pela lateral oeste da loja; cafeteria e depósito
# ficam abaixo dela.
mapa_terreo:
    LINHA "##################ww##"    #  0  vitrine
    LINHA "#####SSSSSSSSSSSSSSSS#"    #  1
    LINHA "#####SSSSSSSSSSSSSSSS#"    #  2
    LINHA "#^^^!SSSSSSSSSSSSSSSS#"    #  3  topo da escada
    LINHA "#^^^!SSSSSSSSSSSSSSSS#"    #  4
    LINHA "#^^^!SSSSSSSSSSSSSSSS#"    #  5
    LINHA "#^^^!SSSSSSSSSSSSSSSS#"    #  6
    LINHA "#^^^!SSSSSSSSSSSSSSSS#"    #  7
    LINHA "#^^^!SSSSSSSSSSSSSSSS#"    #  8
    LINHA "#^^^!SSSSSSSSSSSSSSSS#"    #  9
    LINHA "#^^^SSSSSSSSSSSSSSSSS#"    # 10  pé da escada
    LINHA "#SSSSSSSSSSSSSSSSSSSS#"    # 11
    LINHA "eSSSSSSSSSSSSSSSSSSSS#"    # 12  porta da rua
    LINHA "eSSSSSSSSSSSSSSSSSSSS#"    # 13
    LINHA "#####CCC######DD######"    # 14  passagens
    LINHA "#CCCCCCCCCC#DDDDDDDDD#"    # 15  cafeteria | depósito
    LINHA "#CCCCCCCCCC#DDDDDDDDD#"    # 16
    LINHA "#CCCCCCCCCC#DDDDDDDDD#"    # 17
    LINHA "#CCCCCCCCCC#DDDDDDDDD#"    # 18
    LINHA "#CCCCCCCCCC#DDDDDDDDD#"    # 19
    LINHA "#CCCCCCCCCC#DDDDDDDDD#"    # 20
    LINHA "######################"    # 21

.align 8
comodos_cima:
    COMODO 1, 3, 3, 7, nome_escada
    COMODO 1, 9, 3, 13, nome_hospedes
    COMODO 1, 1, 7, 14, nome_corredor
    COMODO 8, 1, 20, 7, nome_cozinha
    COMODO 8, 9, 20, 14, nome_sala
    COMODO 1, 15, 20, 20, nome_sala
comodos_cima_fim:

comodos_terreo:
    COMODO 1, 3, 3, 10, nome_escada
    COMODO 1, 1, 20, 13, nome_loja
    COMODO 1, 14, 10, 20, nome_cafeteria
    COMODO 12, 14, 20, 20, nome_deposito
comodos_terreo_fim:

transicoes_cima:
    ESCADA 1*TILE, 4*TILE, 3*TILE, TILE, 1, 2*TILE+8, 4*TILE+8, DIR_SUL
transicoes_cima_fim:

transicoes_terreo:
    ESCADA 1*TILE, 3*TILE, 3*TILE, 10, 0, 2*TILE+8, 2*TILE+8, DIR_NORTE
transicoes_terreo_fim:

luzes_cima:
    LUZ 60, 20, 30, 80, 202, 148, 94, OS_CHAMA            # arandela do patamar
    LUZ 96, 120, 30, 90, 162, 122, 81, OS_CHAMA           # teto do corredor
    LUZ 96, 210, 30, 70, 122, 94, 68
    LUZ 150, 24, 16, 80, 81, 108, 189                     # luar pela janela da cozinha
    LUZ 230, 24, 16, 80, 81, 108, 189
    LUZ 305, 24, 16, 80, 81, 108, 189
    LUZ 240, 82, 30, 90, 255, 189, 108, OS_CHAMA          # pendente da mesa
    LUZ 32, 206, 20, 50, 255, 202, 108, OS_CHAMA          # luminária da escrivaninha
    LUZ 20, 176, 24, 70, 74, 101, 176                     # janela do quarto de hóspedes
    LUZ 214, 150, 20, 130, 94, 162, 255, OS_TV            # brilho da TV
    LUZ 254, 202, 34, 100, 255, 182, 101, OS_CHAMA        # luminária de pé
    LUZ 42, 252, 40, 50, 255, 216, 122                    # luz de leitura da cama do Ícaro
    LUZ 150, 290, 10, 140, 120, 90, 70                    # luz geral fraca da sala
luzes_cima_fim:

luzes_terreo:
    LUZ 176, 18, 40, 120, 200, 120, 100                   # placa B-SIDE, luz morna
    LUZ 176, 104, 40, 130, 235, 170, 100, OS_CHAMA        # pendentes da loja
    LUZ 176, 168, 40, 130, 235, 170, 100, OS_CHAMA
    LUZ 96, 22, 40, 80, 220, 160, 95                      # luzes de latão das estantes
    LUZ 256, 22, 40, 80, 220, 160, 95
    LUZ 270, 162, 30, 70, 243, 189, 108                   # luminária do balcão
    LUZ 296, 18, 20, 70, 74, 101, 176                     # vitrine
    LUZ 14, 200, 20, 90, 255, 162, 74                     # poste da rua pela porta
    LUZ 40, 110, 20, 70, 148, 108, 74                     # escada
    LUZ 46, 296, 40, 90, 255, 176, 94, OS_CHAMA           # pendentes da cafeteria
    LUZ 126, 300, 40, 90, 255, 176, 94, OS_CHAMA
    LUZ 140, 248, 20, 70, 255, 189, 81, OS_CHAMA          # vitrola
    LUZ 256, 282, 40, 130, 255, 250, 189, OS_FALHA        # lâmpada do depósito
luzes_terreo_fim:

decalques_cima:
    DECALQUE QUADRO_1, 2, 0, FACE_SUL, 38
    DECALQUE QUADRO_3, 4, 0, FACE_SUL, 38
    DECALQUE TV, 12, 8, FACE_SUL, 40
    DECALQUE TELA_TV, 12, 8, FACE_SUL, 40, CAM_EMISSIVA, OS_TV
    DECALQUE POSTER_1, 0, 16, FACE_LESTE, 38
    DECALQUE POSTER_3, 0, 18, FACE_LESTE, 38
decalques_cima_fim:

decalques_terreo:
    DECALQUE PLACA, 8, 0, FACE_SUL, 46
    DECALQUE PLACA_LETRAS, 8, 0, FACE_SUL, 46, CAM_EMISSIVA
    DECALQUE LOUSA, 1, 14, FACE_SUL, 40
    DECALQUE QUADRO_DISCO_2, 3, 14, FACE_SUL, 42
    DECALQUE QUADRO_DISCO_1, 8, 14, FACE_SUL, 44
decalques_terreo_fim:

.section .data
.align 8
# Em .data: o motor monta a lista de profundidade a partir destes objetos.
objetos_cima:
    # patamar e corredor
    TAPETE PASSADEIRA, 88, 40
    MOVEL PLANTA, 97, 17
    # cozinha
    MOVEL BANCADA_LISA, 128, 16
    MOVEL BANCADA_LISA, 144, 16
    MOVEL BANCADA_PIA, 160, 16
    MOVEL BANCADA_LISA, 176, 16
    MOVEL BANCADA_FOGAO, 192, 16
    MOVEL BANCADA_LISA, 208, 16
    MOVEL LIXEIRA, 228, 19
    MOVEL GELADEIRA, 129, 97
    TAPETE TAPETE_COZINHA, 220, 64
    MOVEL2 MESA_COZINHA, 224, 70
    MOVEL CADEIRA_OESTE, 211, 75
    MOVEL CADEIRA_LESTE, 259, 75
    MOVEL PLANTA, 322, 18
    # quarto de hóspedes: só cama, mesa e janela
    MOVEL2 CAMA_HOSPEDES, 18, 146
    MOVEL2 ESCRIVANINHA, 17, 199
    MOVEL CADEIRA_NORTE, 28, 186
    # sala de estar
    TAPETE TAPETE_SALA, 184, 168
    MOVEL3 RACK, 196, 145
    MOVEL2 ESTANTE, 272, 145
    MOVEL3 SOFA, 196, 212
    MOVEL LUMINARIA, 250, 200
    MOVEL PUFE, 160, 220
    MOVEL PLANTA, 322, 146
    # cama do Ícaro: barras no chão, colchão quase no teto
    MOVEL4 CAMA_ICARO, 17, 241, 0
    BLOQUEIO 17, 241, 3, 3
    BLOQUEIO 62, 241, 3, 3
    BLOQUEIO 17, 270, 3, 3
    BLOQUEIO 62, 270, 3, 3
    BLOQUEIO 65, 247, 2, 20
objetos_cima_fim:

objetos_terreo:
    # loja
    MOVEL2 ESTANTE_DISCOS, 80, 17
    MOVEL2 ESTANTE_DISCOS, 240, 17
    MOVEL2 CAIXOTE, 128, 80
    MOVEL2 CAIXOTE, 208, 80
    MOVEL2 CAIXOTE, 128, 144
    MOVEL2 CAIXOTE, 208, 144
    MOVEL BANQUINHO, 275, 147
    MOVEL4 BALCAO, 256, 160
    TAPETE CAPACHO, 18, 192
    MOVEL PLANTA, 310, 18
    MOVEL PLANTA, 82, 196
    # cafeteria, com o vinil tocando
    MOVEL3 BALCAO_CAFE, 17, 241
    MOVEL2 VITROLA, 129, 241
    SOLTO DISCO, 141, 248, 16, CAM_ORDENADA, AN_DISCO
    SOLTO NOTA, 150, 248, 30, CAM_EMISSIVA, AN_NOTAS
    MOVEL CATALOGO, 162, 242
    MOVEL MESA_BISTRO, 40, 290
    MOVEL CADEIRA_OESTE, 28, 291
    MOVEL CADEIRA_LESTE, 54, 291
    MOVEL MESA_BISTRO, 120, 296
    MOVEL CADEIRA_OESTE, 108, 297
    MOVEL CADEIRA_LESTE, 134, 297
    MOVEL PLANTA, 148, 312
    # depósito: estantes, caixas e a caixa marcada
    MOVEL2 PRATELEIRA, 192, 241
    MOVEL2 PRATELEIRA, 272, 241
    MOVEL3 PRATELEIRA_MARCADA, 224, 280
    MOVEL2 CAIXAS_PILHA, 300, 310
    MOVEL CAIXA_PEQUENA, 196, 310
objetos_terreo_fim:

.section .bss
.align 16
itens_cima:   .skip MAX_ITENS * IT_TAM
itens_terreo: .skip MAX_ITENS * IT_TAM

.section .data
.global andar_cima
.global andar_terreo
.align 8
andar_cima:
    .quad mapa_cima
    .quad objetos_cima, (objetos_cima_fim - objetos_cima) / OBJ_TAM
    .quad luzes_cima, (luzes_cima_fim - luzes_cima) / LUZ_TAM
    .quad comodos_cima, (comodos_cima_fim - comodos_cima) / COM_TAM
    .quad transicoes_cima, (transicoes_cima_fim - transicoes_cima) / TR_TAM
    .quad nome_andar_cima
    .quad 0xff3a2826                                  # ambiente (ABGR): azul-arroxeado escuro
    .quad decalques_cima, (decalques_cima_fim - decalques_cima) / DC_TAM
    .quad itens_cima, 0
    .quad 0, 0                                        # escada plana em cima
andar_terreo:
    .quad mapa_terreo
    .quad objetos_terreo, (objetos_terreo_fim - objetos_terreo) / OBJ_TAM
    .quad luzes_terreo, (luzes_terreo_fim - luzes_terreo) / LUZ_TAM
    .quad comodos_terreo, (comodos_terreo_fim - comodos_terreo) / COM_TAM
    .quad transicoes_terreo, (transicoes_terreo_fim - transicoes_terreo) / TR_TAM
    .quad nome_terreo
    .quad 0xff1e2834                                  # ambiente morno
    .quad decalques_terreo, (decalques_terreo_fim - decalques_terreo) / DC_TAM
    .quad itens_terreo, 0
    .quad 11, 5                                       # degraus sobem 5 px por linha até a linha 3
.section .note.GNU-stack,"",@progbits
