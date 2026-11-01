# Constantes e deslocamentos de campos compartilhados por bside.s e fase1.s
# (versão isométrica).

.equ TILE, 16
.equ LARGURA_MAPA, 22
.equ ALTURA_MAPA, 22
.equ ALTURA_PAREDE, 48
.equ ALTURA_CORTE, 8                 # parede rebaixada na frente de Ícaro
.equ ORIGEM_ISO_X, 352               # 16 * ALTURA_MAPA: o canto oeste fica em x = 0

# Descritor de andar: um campo de 8 bytes por entrada.
.equ AND_MAPA, 0
.equ AND_OBJETOS, 8
.equ AND_N_OBJETOS, 16
.equ AND_LUZES, 24
.equ AND_N_LUZES, 32
.equ AND_COMODOS, 40
.equ AND_N_COMODOS, 48
.equ AND_TRANSICOES, 56
.equ AND_N_TRANSICOES, 64
.equ AND_NOME, 72
.equ AND_AMBIENTE, 80
.equ AND_DECALQUES, 88
.equ AND_N_DECALQUES, 96
.equ AND_ITENS, 104                  # lista de profundidade montada no início
.equ AND_N_ITENS, 112
.equ AND_ESCADA_BASE, 120            # linha onde os degraus tocam o chão
.equ AND_ESCADA_PASSO, 128           # px de altura por linha de degrau (0 = escada plana)

# Objeto (80 bytes): pegada no chão (px do mundo), recorte, âncora e efeitos.
.equ OBJ_FX, 0
.equ OBJ_FY, 4
.equ OBJ_FW, 8
.equ OBJ_FD, 12
.equ OBJ_SX, 16
.equ OBJ_SY, 20
.equ OBJ_SL, 24
.equ OBJ_SA, 28
.equ OBJ_AX, 32                      # vértice de baixo da pegada, dentro do sprite
.equ OBJ_AY, 36
.equ OBJ_Z, 40                       # elevação acima do chão
.equ OBJ_CHAVE, 44                   # profundidade (x + y do tile mais à frente)
.equ OBJ_CAMADA, 48
.equ OBJ_CX, 52
.equ OBJ_CY, 56
.equ OBJ_CL, 60
.equ OBJ_CA, 64
.equ OBJ_ANIM, 68
.equ OBJ_OSC, 72
.equ OBJ_TAM, 80

# Luz (32 bytes): posição no mundo, altura e raio em px da tela isométrica.
.equ LUZ_X, 0
.equ LUZ_Y, 4
.equ LUZ_Z, 8
.equ LUZ_RAIO, 12
.equ LUZ_COR, 16
.equ LUZ_OSC, 20
.equ LUZ_TAM, 32

# Cômodo (24 bytes): retângulo em tiles, inclusivo, e nome para o HUD.
.equ COM_X0, 0
.equ COM_Y0, 4
.equ COM_X1, 8
.equ COM_Y1, 12
.equ COM_NOME, 16
.equ COM_TAM, 24

# Transição de escada (32 bytes): gatilho em px e ponto de chegada dos pés.
.equ TR_X, 0
.equ TR_Y, 4
.equ TR_L, 8
.equ TR_A, 12
.equ TR_DESTINO, 16
.equ TR_CHEGADA_X, 20
.equ TR_CHEGADA_Y, 24
.equ TR_DIRECAO, 28
.equ TR_TAM, 32

# Tipo de tile (32 bytes): losango (piso) ou topo (parede) no atlas, classe,
# variantes, papel de parede e altura.
.equ TT_CHAR, 0
.equ TT_SX, 4
.equ TT_SY, 8
.equ TT_CLASSE, 12
.equ TT_VARIANTES, 16
.equ TT_PAPEL, 20
.equ TT_ALTURA, 24
.equ TT_TAM, 32

# Papel de parede (32 bytes): faces sul e leste e, se houver, o brilho de cada uma.
.equ PP_SUL_X, 0
.equ PP_SUL_Y, 4
.equ PP_LESTE_X, 8
.equ PP_LESTE_Y, 12
.equ PP_BRILHO_SUL_X, 16
.equ PP_BRILHO_SUL_Y, 20
.equ PP_BRILHO_LESTE_X, 24
.equ PP_BRILHO_LESTE_Y, 28
.equ PP_TAM, 32
.equ PAPEL_VIZINHO, 0xff             # a face usa o papel do piso que ela encara
.equ PAPEL_ESCADA, 14                # laterais dos degraus

# Decalque de parede (48 bytes): quadro, TV ou placa presos a uma face.
.equ DC_TX, 0
.equ DC_TY, 4
.equ DC_FACE, 8
.equ DC_N, 12
.equ DC_ZTOPO, 16
.equ DC_SX, 20
.equ DC_SY, 24
.equ DC_SL, 28
.equ DC_SA, 32
.equ DC_CAMADA, 36
.equ DC_OSC, 40
.equ DC_TAM, 48
.equ FACE_SUL, 0
.equ FACE_LESTE, 1

# Item da lista de profundidade (16 bytes).
.equ IT_CHAVE, 0
.equ IT_TIPO, 4
.equ IT_DADO, 8
.equ IT_TAM, 16
.equ IT_BLOCO, 0                     # dado = índice do tile
.equ IT_OBJETO, 1                    # dado = ponteiro do objeto
.equ MAX_ITENS, 800

# Classes de tile.
.equ CL_PISO, 0
.equ CL_PAREDE, 1
.equ CL_DEGRAU, 2
.equ CL_VAO, 3

# Camadas de desenho.
.equ CAM_CHAO, 0
.equ CAM_ORDENADA, 1
.equ CAM_EMISSIVA, 3
.equ CAM_INVISIVEL, 9

# Animações de objeto.
.equ AN_NENHUMA, 0
.equ AN_DISCO, 1
.equ AN_NOTAS, 2

# Oscilação de brilho (luzes e objetos emissivos).
.equ OS_FIXA, 0
.equ OS_CHAMA, 1
.equ OS_TV, 2
.equ OS_FALHA, 3
.equ OS_NEON, 4

# Direções da sprite: N, NE, E, SE, S, SW, W, NW (na tela).
.equ DIR_NORTE, 0
.equ DIR_SUL, 4

# ------------------------------------------------------------------
# Sala 2 (galpão e doca): atores, roteiro, interações e doca.

# Oscilações controladas pelo roteiro (vazio quando perturbacao = 0).
.equ OS_ROTEIRO, 5                   # luz firme que passa a falhar
.equ OS_ESTATICA, 6                  # tela apagada que passa a chiar

# Ator (64 bytes): personagem, anjo, clarão ou olhos de Mael.
.equ AT_X, 0                         # pés, px do mundo (float)
.equ AT_Y, 4
.equ AT_Z, 8                         # elevação (float)
.equ AT_ANDAR, 12                    # -1 = escondido
.equ AT_POSE, 16                     # ponteiro para a pose atual
.equ AT_CONJ, 24                     # conjunto de 8 poses (parado S L N O, anda S L N O) ou 0
.equ AT_TEMPO, 32                    # relógio da animação (float)
.equ AT_DIR, 36                      # 0 sul, 1 leste, 2 norte, 3 oeste (na tela)
.equ AT_ALVO_X, 40
.equ AT_ALVO_Y, 44
.equ AT_ALVO_Z, 48
.equ AT_VEL, 52                      # px/s enquanto se move (float)
.equ AT_MOVENDO, 56
.equ AT_FLAGS, 60
.equ AT_TAM, 64
.equ MAX_ATORES, 28
.equ AF_SOMBRA, 1
.equ AF_EMISSIVO, 2                  # desenhado depois da luz
.equ AF_UMA_VEZ, 4                   # some ao fim da animação
.equ AF_HD, 8                        # pose em textura_elenco_hd (384x512), reduzida como o Ícaro

# Pose (32 bytes), gerada de personagens.inc pela macro POSE.
.equ PS_X, 0
.equ PS_Y, 4
.equ PS_L, 8
.equ PS_A, 12
.equ PS_N, 16
.equ PS_AX, 20
.equ PS_AY, 24
.equ PS_FPS, 28                      # quadros por segundo; 0 = só o primeiro
.equ PS_TAM, 32

# Comando de roteiro (32 bytes).
.equ CMD_OP, 0
.equ CMD_A, 4
.equ CMD_B, 8
.equ CMD_C, 12
.equ CMD_D, 16
.equ CMD_E, 20
.equ CMD_P, 24                       # ponteiro (texto, pose, programa)
.equ CMD_TAM, 32

.equ OP_FIM, 0
.equ OP_MENSAGEM, 1                  # P = texto (espera E)
.equ OP_ESPERA, 2                    # A = ms
.equ OP_ESCURECE, 3                  # fade para o preto (espera)
.equ OP_CLAREIA, 4                   # fade do preto (espera)
.equ OP_ANDAR, 5                     # A = andar, B, C = x, y de Ícaro, D = direção
.equ OP_ATOR, 6                      # A = ator, B = andar | flags << 8, C, D = x, y, P = conjunto
.equ OP_ATOR_FIXO, 7                 # idem, E = z, P = pose
.equ OP_ESCONDE, 8                   # A = ator
.equ OP_POSE, 9                      # A = ator, P = pose (zera conjunto)
.equ OP_ATOR_DIR, 10                 # A = ator, B = direção (0 S, 1 L, 2 N, 3 O)
.equ OP_TELEPORTA, 11                # A = ator, B, C = destino (clarão nos dois pontos)
.equ OP_CAMERA, 12                   # A, B = foco em px do mundo; A = -1 volta a seguir Ícaro
.equ OP_SOM, 13                      # A = som
.equ OP_MUSICA, 14                   # A = volume da trilha em %
.equ OP_ZUMBIDO, 15                  # A = volume do zumbido em %
.equ OP_NEVOA, 16                    # A = opacidade alvo em %
.equ OP_PERTURBA, 17                 # A = 0/1: estática nas telas e luzes falhando
.equ OP_LIBERA, 18                   # devolve o controle ao jogador
.equ OP_TRAVA, 19                    # o roteiro toma o controle
.equ OP_AGUARDA, 20                  # A = flag (jogador livre até ela acender)
.equ OP_FLAG, 21                     # A = flag
.equ OP_SE_FLAG, 22                  # A = flag; se acesa, pula para P
.equ OP_SALTA, 23                    # pula para P
.equ OP_CHAMA, 24                    # pula para P e guarda o retorno (um nível)
.equ OP_VOLTA, 25
.equ OP_OBJETIVO, 26                 # P = texto (0 apaga)
.equ OP_INTERACOES, 27               # P = lista, A = quantidade
.equ OP_DOCA, 28                     # P = ponto da doca (espera concluir)
.equ OP_ROTULO, 29                   # P = nome (BSIDE_CENA pula para cá)
.equ OP_DIRECAO, 30                  # A = direção da sprite de Ícaro
.equ OP_TREME, 31                    # A = ms de tremor da câmera
.equ OP_CLARAO, 32                   # A = 0 vermelho, 1 branco
.equ OP_MOVE, 33                     # A = ator, B, C, D = destino x, y, z, E = px/s
.equ OP_MELODIA, 34                  # P = melodia esperada (0 desarma)
.equ N_OPS, 35

# Sons (índice em tabela_sons, ritmo.s).
.equ SOM_NOTA0, 0
.equ SOM_TIQUE, 4
.equ SOM_BERRO, 5
.equ SOM_GRITO, 6
.equ SOM_ESTATICA, 7
.equ SOM_CLARAO, 8
.equ SOM_BAQUE, 9
.equ SOM_GRITO_ANJO, 10              # anjos levantando voo (áudio do usuário)
.equ N_SONS, 11

# Interação (48 bytes): retângulo em px do mundo, andar, flags e programa.
.equ IN_X, 0
.equ IN_Y, 4
.equ IN_L, 8
.equ IN_A, 12
.equ IN_ANDAR, 16
.equ IN_EXIGE, 20                    # flag necessária (-1 nenhuma)
.equ IN_SOME, 24                     # flag que esconde a interação (-1 nenhuma)
.equ IN_ROTULO, 32
.equ IN_PROGRAMA, 40
.equ IN_TAM, 48

# Alto-falante da doca (16 bytes).
.equ FAL_X, 0
.equ FAL_Y, 4
.equ FAL_Z, 8                         # altura da corneta
.equ FAL_NOTA, 12
.equ FAL_TAM, 16

# Ponto da fuga (64 bytes), gerado por ferramentas/gerar_doca.py.
.equ DP_INI_X, 0                     # centro da área segura de partida
.equ DP_INI_Y, 4
.equ DP_FIM_X, 8                     # centro da área segura de chegada
.equ DP_FIM_Y, 12
.equ DP_BPM, 16
.equ DP_JANELA, 20                   # ms para chegar depois da nota
.equ DP_FALANTE0, 24                 # primeiro alto-falante do ponto (os outros vêm em seguida)
.equ DP_N_FALANTES, 28
.equ DP_ANJO0, 32                    # primeiro ator-anjo do ponto
.equ DP_N_ANJOS, 36
.equ DP_POLEIROS, 40                 # ponteiro: x, y, z (long) por anjo
.equ DP_AGENTE_X, 48                 # onde o agente espera na área de chegada
.equ DP_AGENTE_Y, 52
.equ DP_TAM, 64
.equ RAIO_AREA, 14                   # px: Ícaro está na área se |dx| e |dy| <= isto
.equ RAIO_PEGA, 16                   # px: anjo a menos disso pega Ícaro
.equ N_FLAGS, 64

# Atores fixos da Sala 2.
.equ ATOR_HANK, 0
.equ ATOR_AGENTE, 3
.equ ATOR_MAEL, 4
.equ ATOR_ANJO, 5                    # 5..20: anjos (os de um trecho da fuga)
.equ N_ANJOS, 16
.equ ATOR_CLARAO_A, 21
.equ ATOR_CLARAO_B, 22
.equ ATOR_BILHETE, 23                # Sala 1: bilhete no balcão, lista e caixa do depósito
.equ ATOR_LISTA, 24
.equ ATOR_CAIXA, 25

# Melodia (36 bytes): notas a tocar dentro de um retângulo para acender uma flag.
.equ MEL_ANDAR, 0
.equ MEL_X, 4                        # retângulo em px do mundo
.equ MEL_Y, 8
.equ MEL_L, 12
.equ MEL_A, 16
.equ MEL_FLAG, 20
.equ MEL_N, 24
.equ MEL_NOTAS, 28                   # até 8 bytes, índices de notas_midi
.equ MEL_TAM, 36
