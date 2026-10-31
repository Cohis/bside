# Constantes e deslocamentos de campos compartilhados por bside.s e fase1.s.

.equ TILE, 16
.equ LARGURA_MAPA, 24
.equ ALTURA_MAPA, 33

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

# Objeto (64 bytes): destino, recorte no atlas, ordenação, colisão e efeitos.
.equ OBJ_X, 0
.equ OBJ_Y, 4
.equ OBJ_L, 8
.equ OBJ_A, 12
.equ OBJ_SX, 16
.equ OBJ_SY, 20
.equ OBJ_SL, 24
.equ OBJ_SA, 28
.equ OBJ_BASE, 32
.equ OBJ_CAMADA, 36
.equ OBJ_CX, 40
.equ OBJ_CY, 44
.equ OBJ_CL, 48
.equ OBJ_CA, 52
.equ OBJ_ANIM, 56
.equ OBJ_OSC, 60
.equ OBJ_TAM, 64

# Luz (32 bytes).
.equ LUZ_X, 0
.equ LUZ_Y, 4
.equ LUZ_RAIO, 8
.equ LUZ_COR, 12
.equ LUZ_OSC, 16
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

# Tipo de tile (16 bytes): caractere do mapa, índice no atlas, classe, variantes.
.equ TT_CHAR, 0
.equ TT_INDICE, 4
.equ TT_CLASSE, 8
.equ TT_VARIANTES, 12
.equ TT_TAM, 16

# Classes de tile. Só CL_PISO deixa passar.
.equ CL_PISO, 0
.equ CL_TOPO, 1
.equ CL_FACE, 2
.equ CL_COLUNA, 3
.equ CL_SOLIDO, 4

# Camadas de desenho.
.equ CAM_CHAO, 0
.equ CAM_ORDENADA, 1
.equ CAM_TETO, 2
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

# Direções da sprite: N, NE, E, SE, S, SW, W, NW.
.equ DIR_NORTE, 0
.equ DIR_SUL, 4
