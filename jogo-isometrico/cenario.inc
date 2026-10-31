# Macros de dados de cenário usadas por fase1.s e sala2.s: plantas, móveis,
# luzes, decalques, cômodos, escadas e papéis de parede.

.macro LINHA texto
9:  .ascii "\texto"
    .if (. - 9b) - LARGURA_MAPA
    .error "linha do mapa com largura diferente de LARGURA_MAPA"
    .endif
.endm

# Pedaço de móvel na posição (x, y) do objeto inteiro. colide=0 dispensa a colisão.
.macro PEDACO nome, x, y, colide=1, camada=CAM_ORDENADA, anim=AN_NENHUMA, osc=OS_FIXA
    .long (\x) + S_\nome\()_OX, (\y) + S_\nome\()_OY, S_\nome\()_W, S_\nome\()_D
    .long S_\nome\()_X, S_\nome\()_Y, S_\nome\()_L, S_\nome\()_A
    .long S_\nome\()_AX, S_\nome\()_AY, 0
    .long (\x) + S_\nome\()_OX + S_\nome\()_KX + (\y) + S_\nome\()_OY + S_\nome\()_KY
    .long \camada
    .if \colide
    .long (\x) + S_\nome\()_OX + 1, (\y) + S_\nome\()_OY + 1, S_\nome\()_W - 2, S_\nome\()_D - 2
    .else
    .long 0, 0, 0, 0
    .endif
    .long \anim, \osc, 0
.endm

.macro MOVEL nome, x, y, colide=1
    PEDACO \nome, \x, \y, \colide
.endm
.macro MOVEL2 nome, x, y, colide=1
    PEDACO \nome\()_0, \x, \y, \colide
    PEDACO \nome\()_1, \x, \y, \colide
.endm
.macro MOVEL3 nome, x, y, colide=1
    MOVEL2 \nome, \x, \y, \colide
    PEDACO \nome\()_2, \x, \y, \colide
.endm
.macro MOVEL4 nome, x, y, colide=1
    MOVEL3 \nome, \x, \y, \colide
    PEDACO \nome\()_3, \x, \y, \colide
.endm

# Tapete ou passadeira: no chão, sem colisão, antes de tudo que fica de pé.
.macro TAPETE nome, x, y
    PEDACO \nome, \x, \y, 0, CAM_CHAO
.endm

# Peça solta (disco, notas): ponto no mundo, elevação e âncora no centro do sprite.
.macro SOLTO nome, x, y, z, camada, anim, osc=OS_FIXA
    .long \x, \y, 0, 0
    .long S_\nome\()_X, S_\nome\()_Y, S_\nome\()_L, S_\nome\()_A
    .long S_\nome\()_L / 2, S_\nome\()_A / 2, \z, (\x) + (\y) + 1, \camada
    .long 0, 0, 0, 0
    .long \anim, \osc, 0
.endm

# Só colisão, sem desenho (barras da cama do Ícaro).
.macro BLOQUEIO cx, cy, cl, ca
    .long 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, CAM_INVISIVEL
    .long \cx, \cy, \cl, \ca
    .long AN_NENHUMA, OS_FIXA, 0
.endm

.macro DECALQUE nome, tx, ty, face, ztopo, camada=CAM_CHAO, osc=OS_FIXA
    .long \tx, \ty, \face, S_\nome\()_N, \ztopo
    .long S_\nome\()_X, S_\nome\()_Y, S_\nome\()_L, S_\nome\()_A, \camada, \osc, 0
.endm

.macro LUZ x, y, z, raio, r, g, b, osc=OS_FIXA
    .long \x, \y, \z, \raio, (\r) | ((\g) << 8) | ((\b) << 16) | (255 << 24), \osc, 0, 0
.endm

.macro COMODO x0, y0, x1, y1, nome
    .long \x0, \y0, \x1, \y1
    .quad \nome
.endm

.macro ESCADA x, y, l, a, destino, chegada_x, chegada_y, direcao
    .long \x, \y, \l, \a, \destino, \chegada_x, \chegada_y, \direcao
.endm

.macro PAPEL nome
    .long S_PAREDE_SUL_\nome\()_X, S_PAREDE_SUL_\nome\()_Y, S_PAREDE_LESTE_\nome\()_X, S_PAREDE_LESTE_\nome\()_Y
    .long -1, -1, -1, -1
.endm
.macro PAPEL_BRILHO nome
    .long S_PAREDE_SUL_\nome\()_X, S_PAREDE_SUL_\nome\()_Y, S_PAREDE_LESTE_\nome\()_X, S_PAREDE_LESTE_\nome\()_Y
    .long S_BRILHO_SUL_\nome\()_X, S_BRILHO_SUL_\nome\()_Y, S_BRILHO_LESTE_\nome\()_X, S_BRILHO_LESTE_\nome\()_Y
.endm
