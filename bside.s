.intel_syntax noprefix

# B-Side: sala isométrica em tiles. Toda a lógica está em Assembly x86-64.
# ABI System V (Linux); a Raylib cuida apenas de janela, entrada e desenho.

.equ POS_X, 0
.equ POS_Y, 4
.equ DIRECAO, 8
.equ ANDANDO, 12
.equ TEMPO, 16
.equ TECLA_CIMA, 20
.equ TECLA_BAIXO, 24
.equ TECLA_ESQUERDA, 28
.equ TECLA_DIREITA, 32

.section .rodata
titulo:         .asciz "B-Side | loja de vinis"
caminho_icaro_final: .asciz "assets/icaro-andar-final.png"
caminho_icaro:  .asciz "assets/icaro-andar-rascunho.png"
erro_recursos:  .asciz "Nao foi possivel carregar as texturas. Execute a partir da raiz do repositorio."
erro_janela:    .asciz "Nao foi possivel abrir uma janela grafica."
ajuda:          .asciz "B-SIDE  ICARO: WASD                                    ESC: sair"
txt_piso: .asciz "assets/textura-piso-pedra-pixel.png"
txt_madeira: .asciz "assets/textura-madeira.png"
txt_prateleira: .asciz "assets/textura-prateleira.png"
txt_folhagem: .asciz "assets/textura-folhagem.png"
txt_tapete: .asciz "assets/textura-tapete.png"
txt_papel_parede: .asciz "assets/textura-papel-parede.png"
txt_metal: .asciz "assets/textura-metal.png"
txt_pedra: .asciz "assets/textura-pedra.png"
txt_capas: .asciz "assets/capas-vinis.png"
variavel_captura: .asciz "BSIDE_CAPTURE"
variavel_colisoes: .asciz "BSIDE_COLISOES"
caminho_captura: .asciz "captura.png"

.align 8
origem_zero:    .float 0.0, 0.0
tamanho_celula: .float 384.0, 512.0
tamanho_sprite: .float 75.0, 100.0
limite_delta:   .float 0.05
velocidade:     .float 4.0
diagonal_horizontal: .float 0.55901699
diagonal_vertical: .float 1.11803399
meia_largura_tile: .float 16.0
meia_altura_tile: .float 8.0
zoom_jogo:      .float 1.5
zoom_unidade:   .float 1.0
zoom_centro_x:  .float 640.0
zoom_centro_y:  .float 370.0
zoom_neg_x:     .float -640.0
zoom_neg_y:     .float -370.0
um:             .float 1.0
zero:           .float 0.0
tempo_ciclo:    .float 0.8
dez:            .float 10.0
ancora_x:       .float 37.5
ancora_y:       .float 93.75

# Losangos lógicos 32x16; a câmera aplica zoom uniforme de 1,5x ao mundo.
# A matriz 192x144 mantém o tamanho da loja, sem alterar a física.
origem_x:       .float 640.0
origem_y:       .float 360.0
inverso_32:     .float 0.03125
inverso_16:     .float 0.0625
inverso_8:      .float 0.125
largura_mundo:  .float 192.0
altura_mundo:   .float 144.0
amostra_x:      .float 5.5
amostra_y:      .float 2.75
centro_camera_x: .float 640.0
centro_camera_y: .float 370.0

# UVs de cada losango: topo, direita, base e esquerda.
uv_losango: .float 0.5, 0.0, 1.0, 0.5, 0.5, 1.0, 0.0, 0.5
ordem_losango_topo: .byte 0, 3, 2, 1
ordem_losango_face: .byte 0, 1, 2, 3

# Retângulos do piso e dos móveis: x, y, largura, altura, tipo (ASCII).
# O espaço continua com 192x144 células; portas são trechos sem parede.
.align 4
layout_pisos:
    .long 7, 102, 88, 38, 'F'        # cafeteria em madeira
    .long 8, 49, 42, 48, 'L'         # sala de escuta acarpetada
    .long 102, 6, 84, 38, 'W'        # estoque e oficina metálicos
    .long 153, 68, 33, 42, 'T'       # banheiro em pedra clara
    .long 26, 116, 18, 11, '7'       # tapete da cafeteria
    .long 31, 132, 10, 5, '7'        # capacho da entrada
    .long 14, 60, 29, 25, '9'        # tapete da sala de escuta
    .long 78, 69, 24, 12, '9'        # destaque de lançamentos
    .long 43, 97, 23, 3, '7'         # passagem principal
    .long 128, 43, 18, 4, '7'        # acesso ao estoque
layout_pisos_fim:

layout_paredes:
    .long 0, 0, 192, 3, '5'          # limite externo
    .long 0, 141, 25, 3, '5'
    .long 44, 141, 148, 3, '5'       # vão da entrada
    .long 0, 3, 3, 138, '5'
    .long 189, 3, 3, 138, '5'
    .long 7, 47, 44, 2, '8'          # sala de escuta
    .long 7, 96, 44, 2, '8'
    .long 7, 49, 2, 47, '8'
    .long 49, 49, 2, 11, '8'
    .long 49, 72, 2, 9, '8'
    .long 49, 91, 2, 5, '8'          # duas portas para a sala
    .long 6, 100, 34, 2, '8'         # cafeteria / salão
    .long 47, 100, 22, 2, '8'
    .long 76, 100, 20, 2, '8'        # duas passagens largas
    .long 101, 6, 2, 37, '8'         # separação do corredor de serviço
    .long 101, 43, 27, 2, '8'        # oficina / salão, duas portas
    .long 146, 43, 18, 2, '8'
    .long 177, 43, 9, 2, '8'
    .long 102, 25, 23, 2, '8'        # estoque / oficina
    .long 137, 25, 21, 2, '8'
    .long 168, 25, 18, 2, '8'        # dois vãos entre as áreas
    .long 151, 68, 2, 10, '8'        # banheiro com acessos alternativos
    .long 151, 89, 2, 5, '8'
    .long 151, 102, 2, 8, '8'
    .long 184, 68, 2, 42, '8'
    .long 153, 68, 31, 2, '8'
    .long 153, 109, 31, 2, '8'
    .long 166, 72, 2, 8, '8'         # divisória da cabine
    .long 166, 85, 2, 14, '8'
layout_paredes_fim:

layout_mobiliario:
    # Salão: ilhas baixas de capas com corredores transversais amplos.
    .long 58, 51, 2, 14, '1'
    .long 78, 51, 2, 14, '1'
    .long 98, 51, 2, 14, '1'
    .long 118, 51, 2, 14, '1'
    .long 138, 51, 2, 14, '1'
    .long 64, 79, 2, 13, '1'
    .long 84, 79, 2, 13, '1'
    .long 104, 79, 2, 13, '1'
    .long 124, 79, 2, 13, '1'
    .long 144, 79, 2, 13, '1'
    .long 55, 68, 2, 2, '2'
    .long 74, 68, 2, 2, '2'
    .long 112, 68, 2, 2, '2'
    .long 133, 68, 2, 2, '2'
    .long 72, 94, 2, 2, '2'
    .long 128, 94, 2, 2, '2'
    .long 52, 47, 2, 2, '4'
    .long 146, 47, 2, 2, '4'
    .long 147, 96, 2, 2, '4'

    # Cafeteria: balcão, máquina de espresso e mesas compactas.
    .long 27, 126, 15, 2, '3'
    .long 33, 124, 1, 1, 'm'
    .long 24, 118, 1, 1, 'd'
    .long 45, 126, 1, 1, 'd'
    .long 57, 116, 1, 1, 'd'
    .long 69, 127, 1, 1, 'd'
    .long 10, 106, 2, 2, '4'
    .long 88, 106, 2, 2, '4'

    # Escuta: estantes laterais, toca-discos central e plantas.
    .long 11, 55, 2, 13, '1'
    .long 43, 55, 2, 13, '1'
    .long 17, 72, 1, 1, '6'
    .long 35, 72, 1, 1, '6'
    .long 27, 82, 1, 1, '6'
    .long 10, 91, 2, 2, '4'
    .long 45, 91, 2, 2, '4'

    # Estoque/oficina: estantes altas, caixas e bancada de reparos.
    .long 107, 8, 2, 14, '1'
    .long 123, 8, 2, 14, '1'
    .long 144, 8, 2, 14, '1'
    .long 175, 8, 2, 14, '1'
    .long 109, 29, 2, 12, '1'
    .long 178, 29, 2, 12, '1'
    .long 114, 15, 2, 2, '2'
    .long 132, 16, 2, 2, '2'
    .long 158, 14, 2, 2, '2'
    .long 117, 33, 2, 2, '2'
    .long 165, 34, 2, 2, '2'
    .long 139, 34, 18, 2, '3'
    .long 160, 37, 2, 2, '4'

    # Banheiro: lavatório, cabine e louças sanitárias.
    .long 157, 75, 1, 1, 's'
    .long 174, 80, 1, 1, 't'
    .long 174, 94, 1, 1, 't'
    .long 178, 73, 2, 2, '4'
layout_mobiliario_fim:

uv_materiais:
    .float 0.0, 0.0, 0.5, 0.0, 0.5, 0.5, 0.0, 0.5
    .float 0.5, 0.0, 1.0, 0.0, 1.0, 0.5, 0.5, 0.5
    .float 0.0, 0.5, 0.5, 0.5, 0.5, 1.0, 0.0, 1.0
    .float 0.5, 0.5, 1.0, 0.5, 1.0, 1.0, 0.5, 1.0
raio_prato:     .float 4.8
raio_miolo:     .float 1.6
raio_planta:    .float 9.0
raio_mesa:      .float 6.5
raio_cafe:      .float 2.0
raio_louca:     .float 5.2
raio_bacia:     .float 2.4

.section .data
.align 16
# x, y projetados sem câmera, direção, andando, tempo, cima, baixo, esquerda, direita
icaro: .float -896.0, 1704.0
       .long 4, 0
       .float 0.0
       .long 87, 83, 65, 68

.section .bss
.align 16
textura_icaro: .skip 20
textura_piso: .skip 20
textura_madeira: .skip 20
textura_prateleira: .skip 20
textura_folhagem: .skip 20
textura_tapete: .skip 20
textura_papel_parede: .skip 20
textura_metal: .skip 20
textura_pedra: .skip 20
textura_capas: .skip 20
mapa_tiles: .skip 27648
delta_quadro:  .skip 4
capturar:      .skip 4
mostrar_colisoes: .skip 4
desenhar_topo: .skip 4
camera_x:      .skip 4
camera_y:      .skip 4
.align 16
quad_atual:    .skip 32
posicao_teste: .skip 8
tipo_atual:    .skip 4
altura_atual:  .skip 4
sx_atual:      .skip 4
sy_atual:      .skip 4
material_atual: .skip 4
luz_atual:     .skip 4
tx_atual:      .skip 4
ty_atual:      .skip 4
.align 16
uv_atual:      .skip 32
quad_capa:     .skip 32

.section .text
.extern InitWindow
.extern CloseWindow
.extern SetTargetFPS
.extern WindowShouldClose
.extern GetFrameTime
.extern IsKeyDown
.extern BeginDrawing
.extern EndDrawing
.extern ClearBackground
.extern LoadTexture
.extern FileExists
.extern UnloadTexture
.extern DrawTexturePro
.extern DrawRectangle
.extern DrawText
.extern DrawLine
.extern DrawCircle
.extern rlPushMatrix
.extern rlPopMatrix
.extern rlTranslatef
.extern rlScalef
.extern rlSetTexture
.extern rlBegin
.extern rlColor4ub
.extern rlTexCoord2f
.extern rlVertex2f
.extern rlEnd
.extern IsWindowReady
.extern TakeScreenshot
.extern rlDrawRenderBatchActive
.extern getenv
.extern puts
.global main
.type main, @function

main:
    push rbp
    mov rbp, rsp
    sub rsp, 16

    mov edi, 1280
    mov esi, 720
    lea rdx, [rip + titulo]
    call InitWindow
    call IsWindowReady
    test al, al
    jz .falha_janela
    mov edi, 60
    call SetTargetFPS

    lea rdi, [rip + variavel_captura]
    call getenv
    test rax, rax
    setne al
    movzx eax, al
    mov dword ptr [rip + capturar], eax
    lea rdi, [rip + variavel_colisoes]
    call getenv
    test rax, rax
    setne al
    movzx eax, al
    mov dword ptr [rip + mostrar_colisoes], eax

    lea rdi, [rip + caminho_icaro_final]
    call FileExists
    test al, al
    jz .usar_icaro_rascunho
    lea rsi, [rip + caminho_icaro_final]
    jmp .carregar_icaro
.usar_icaro_rascunho:
    lea rsi, [rip + caminho_icaro]
.carregar_icaro:
    lea rdi, [rip + textura_icaro]
    call LoadTexture
    lea rdi, [rip + textura_piso]
    lea rsi, [rip + txt_piso]
    call LoadTexture
    lea rdi, [rip + textura_madeira]
    lea rsi, [rip + txt_madeira]
    call LoadTexture
    lea rdi, [rip + textura_prateleira]
    lea rsi, [rip + txt_prateleira]
    call LoadTexture
    lea rdi, [rip + textura_folhagem]
    lea rsi, [rip + txt_folhagem]
    call LoadTexture
    lea rdi, [rip + textura_tapete]
    lea rsi, [rip + txt_tapete]
    call LoadTexture
    lea rdi, [rip + textura_papel_parede]
    lea rsi, [rip + txt_papel_parede]
    call LoadTexture
    lea rdi, [rip + textura_metal]
    lea rsi, [rip + txt_metal]
    call LoadTexture
    lea rdi, [rip + textura_pedra]
    lea rsi, [rip + txt_pedra]
    call LoadTexture
    lea rdi, [rip + textura_capas]
    lea rsi, [rip + txt_capas]
    call LoadTexture

    cmp dword ptr [rip + textura_icaro], 0
    je .erro
    cmp dword ptr [rip + textura_piso], 0
    je .erro
    cmp dword ptr [rip + textura_madeira], 0
    je .erro
    cmp dword ptr [rip + textura_prateleira], 0
    je .erro
    cmp dword ptr [rip + textura_folhagem], 0
    je .erro
    cmp dword ptr [rip + textura_tapete], 0
    je .erro
    cmp dword ptr [rip + textura_papel_parede], 0
    je .erro
    cmp dword ptr [rip + textura_metal], 0
    je .erro
    cmp dword ptr [rip + textura_pedra], 0
    je .erro
    cmp dword ptr [rip + textura_capas], 0
    je .erro

    call gerar_mapa

.quadro:
    call WindowShouldClose
    test eax, eax
    jne .fechar

    call GetFrameTime
    minss xmm0, dword ptr [rip + limite_delta]
    movss dword ptr [rip + delta_quadro], xmm0

    lea rdi, [rip + icaro]
    call atualizar_personagem
    movss xmm0, dword ptr [rip + centro_camera_x]
    subss xmm0, dword ptr [rip + icaro + POS_X]
    movss dword ptr [rip + camera_x], xmm0
    movss xmm0, dword ptr [rip + centro_camera_y]
    subss xmm0, dword ptr [rip + icaro + POS_Y]
    movss dword ptr [rip + camera_y], xmm0

    call BeginDrawing
    mov edi, 0xff101018
    call ClearBackground
    # Zoom de câmera em torno do personagem; o HUD é desenhado depois, sem escala.
    call rlPushMatrix
    movss xmm0, dword ptr [rip + zoom_centro_x]
    movss xmm1, dword ptr [rip + zoom_centro_y]
    xorps xmm2, xmm2
    call rlTranslatef
    movss xmm0, dword ptr [rip + zoom_jogo]
    movss xmm1, xmm0
    movss xmm2, dword ptr [rip + zoom_unidade]
    call rlScalef
    movss xmm0, dword ptr [rip + zoom_neg_x]
    movss xmm1, dword ptr [rip + zoom_neg_y]
    xorps xmm2, xmm2
    call rlTranslatef
    call desenhar_mapa
    call rlDrawRenderBatchActive
    call rlPopMatrix
    call rlDrawRenderBatchActive

.hud:
    mov edi, 0
    mov esi, 684
    mov edx, 1280
    mov ecx, 36
    mov r8d, 0xd9161a20
    call DrawRectangle
    lea rdi, [rip + ajuda]
    mov esi, 22
    mov edx, 693
    mov ecx, 17
    mov r8d, 0xffe5dbcb
    call DrawText
    cmp dword ptr [rip + capturar], 0
    je .fim_desenho
    mov dword ptr [rip + capturar], 0
    call rlDrawRenderBatchActive
    lea rdi, [rip + caminho_captura]
    call TakeScreenshot
.fim_desenho:
    call EndDrawing
    jmp .quadro

.falha_janela:
    lea rdi, [rip + erro_janela]
    call puts
    mov eax, 1
    leave
    ret
.erro:
    lea rdi, [rip + erro_recursos]
    call puts
    mov dword ptr [rbp - 4], 1
    jmp .descarregar
.fechar:
    mov dword ptr [rbp - 4], 0
.descarregar:
    cmp dword ptr [rip + textura_icaro], 0
    je .pular_icaro
    lea rdi, [rip + textura_icaro]
    call descarregar_textura
.pular_icaro:
    cmp dword ptr [rip + textura_piso], 0
    je .pular_piso
    lea rdi, [rip + textura_piso]
    call descarregar_textura
.pular_piso:
    cmp dword ptr [rip + textura_madeira], 0
    je .pular_madeira
    lea rdi, [rip + textura_madeira]
    call descarregar_textura
.pular_madeira:
    cmp dword ptr [rip + textura_prateleira], 0
    je .pular_prateleira
    lea rdi, [rip + textura_prateleira]
    call descarregar_textura
.pular_prateleira:
    cmp dword ptr [rip + textura_folhagem], 0
    je .pular_folhagem
    lea rdi, [rip + textura_folhagem]
    call descarregar_textura
.pular_folhagem:
    cmp dword ptr [rip + textura_tapete], 0
    je .pular_tapete
    lea rdi, [rip + textura_tapete]
    call descarregar_textura
.pular_tapete:
    cmp dword ptr [rip + textura_papel_parede], 0
    je .pular_papel
    lea rdi, [rip + textura_papel_parede]
    call descarregar_textura
.pular_papel:
    cmp dword ptr [rip + textura_metal], 0
    je .pular_metal
    lea rdi, [rip + textura_metal]
    call descarregar_textura
.pular_metal:
    cmp dword ptr [rip + textura_pedra], 0
    je .pular_pedra
    lea rdi, [rip + textura_pedra]
    call descarregar_textura
.pular_pedra:
    cmp dword ptr [rip + textura_capas], 0
    je .pular_capas
    lea rdi, [rip + textura_capas]
    call descarregar_textura
.pular_capas:
    call CloseWindow
    mov eax, dword ptr [rbp - 4]
    leave
    ret

# rdi aponta para Texture2D; xmm0..5 e edi seguem a ABI de DrawTexturePro.
# Como o primeiro argumento de DrawTexturePro é um struct de 20 bytes,
# ele vai para a pilha e Color (último argumento) ocupa edi.
desenhar_textura:
    sub rsp, 40
    mov rax, qword ptr [rdi]
    mov qword ptr [rsp], rax
    mov rax, qword ptr [rdi + 8]
    mov qword ptr [rsp + 8], rax
    mov eax, dword ptr [rdi + 16]
    mov dword ptr [rsp + 16], eax
    mov edi, -1
    call DrawTexturePro
    add rsp, 40
    ret

descarregar_textura:
    sub rsp, 40
    mov rax, qword ptr [rdi]
    mov qword ptr [rsp], rax
    mov rax, qword ptr [rdi + 8]
    mov qword ptr [rsp + 8], rax
    mov eax, dword ptr [rdi + 16]
    mov dword ptr [rsp + 16], eax
    call UnloadTexture
    add rsp, 40
    ret

# Atualiza uma personagem. Movimento em dois eixos para deslizar nas bordas.
atualizar_personagem:
    push rbp
    mov rbp, rsp
    push rbx
    push r12
    push r13
    push r14
    push r15
    sub rsp, 24
    mov r12, rdi
    xor ebx, ebx                   # entrada horizontal: D - A
    xor r13d, r13d                 # entrada vertical: S - W

    mov edi, dword ptr [r12 + TECLA_ESQUERDA]
    call IsKeyDown
    sub ebx, eax
    mov edi, dword ptr [r12 + TECLA_DIREITA]
    call IsKeyDown
    add ebx, eax
    mov edi, dword ptr [r12 + TECLA_CIMA]
    call IsKeyDown
    sub r13d, eax
    mov edi, dword ptr [r12 + TECLA_BAIXO]
    call IsKeyDown
    add r13d, eax

    mov dword ptr [r12 + ANDANDO], 0
    mov eax, ebx
    or eax, r13d
    jz .fim_atualizacao

    # Projeta as teclas nos eixos da grade: D=(+16,+8), S=(-16,+8).
    # W+D e A+S viram deslocamentos horizontais sobre a linha de losangos.
    mov r14d, ebx
    sub r14d, r13d                 # componente X projetada
    mov r15d, ebx
    add r15d, r13d                 # componente Y projetada

    movss xmm2, dword ptr [rip + delta_quadro]
    mulss xmm2, dword ptr [rip + velocidade]
    test ebx, ebx
    jz .normalizacao_pronta
    test r13d, r13d
    jz .normalizacao_pronta
    cmp ebx, r13d
    je .diagonal_vertical
    mulss xmm2, dword ptr [rip + diagonal_horizontal]
    jmp .normalizacao_pronta
.diagonal_vertical:
    mulss xmm2, dword ptr [rip + diagonal_vertical]
.normalizacao_pronta:
    cvtsi2ss xmm0, r14d
    mulss xmm0, dword ptr [rip + meia_largura_tile]
    mulss xmm0, xmm2
    movss dword ptr [rsp], xmm0
    cvtsi2ss xmm0, r15d
    mulss xmm0, dword ptr [rip + meia_altura_tile]
    mulss xmm0, xmm2
    movss dword ptr [rsp + 4], xmm0

    # A direção da animação acompanha o deslocamento projetado na tela.
    mov ebx, r14d
    mov r13d, r15d

    # Índices: N, NE, E, SE, S, SW, W, NW.
    test r13d, r13d
    js .norte
    jg .sul
    test ebx, ebx
    js .oeste
    mov dword ptr [r12 + DIRECAO], 2
    jmp .direcao_pronta
.norte:
    test ebx, ebx
    js .noroeste
    jg .nordeste
    mov dword ptr [r12 + DIRECAO], 0
    jmp .direcao_pronta
.nordeste:
    mov dword ptr [r12 + DIRECAO], 1
    jmp .direcao_pronta
.noroeste:
    mov dword ptr [r12 + DIRECAO], 7
    jmp .direcao_pronta
.sul:
    test ebx, ebx
    js .sudoeste
    jg .sudeste
    mov dword ptr [r12 + DIRECAO], 4
    jmp .direcao_pronta
.sudeste:
    mov dword ptr [r12 + DIRECAO], 3
    jmp .direcao_pronta
.sudoeste:
    mov dword ptr [r12 + DIRECAO], 5
    jmp .direcao_pronta
.oeste:
    mov dword ptr [r12 + DIRECAO], 6

.direcao_pronta:
    movss xmm0, dword ptr [r12 + POS_X]
    addss xmm0, dword ptr [rsp]
    movss xmm1, dword ptr [r12 + POS_Y]
    mov r8, r12
    call pode_andar
    test eax, eax
    jz .pular_x
    movss xmm0, dword ptr [r12 + POS_X]
    addss xmm0, dword ptr [rsp]
    movss dword ptr [r12 + POS_X], xmm0
    movss xmm0, dword ptr [rsp]
    ucomiss xmm0, dword ptr [rip + zero]
    jz .pular_x
    mov dword ptr [r12 + ANDANDO], 1
.pular_x:
    movss xmm1, dword ptr [r12 + POS_Y]
    addss xmm1, dword ptr [rsp + 4]
    movss xmm0, dword ptr [r12 + POS_X]
    movss dword ptr [rsp + 8], xmm1
    mov r8, r12
    call pode_andar
    test eax, eax
    jz .pular_y
    movss xmm1, dword ptr [rsp + 8]
    movss dword ptr [r12 + POS_Y], xmm1
    movss xmm0, dword ptr [rsp + 4]
    ucomiss xmm0, dword ptr [rip + zero]
    jz .pular_y
    mov dword ptr [r12 + ANDANDO], 1
.pular_y:
    cmp dword ptr [r12 + ANDANDO], 0
    jne .avancar_ciclo
    mov dword ptr [r12 + TEMPO], 0
    jmp .fim_atualizacao
.avancar_ciclo:
    movss xmm0, dword ptr [r12 + TEMPO]
    addss xmm0, dword ptr [rip + delta_quadro]
    ucomiss xmm0, dword ptr [rip + tempo_ciclo]
    jb .guardar_tempo
    subss xmm0, dword ptr [rip + tempo_ciclo]
.guardar_tempo:
    movss dword ptr [r12 + TEMPO], xmm0
.fim_atualizacao:
    add rsp, 24
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbx
    pop rbp
    ret

# xmm0=x, xmm1=y; eax=1 se o apoio está livre.
pode_andar:
    sub rsp, 8
    movss dword ptr [rip + posicao_teste], xmm0
    movss dword ptr [rip + posicao_teste + 4], xmm1
    call ponto_livre
    test eax, eax
    jz .bloqueado
    movss xmm0, dword ptr [rip + posicao_teste]
    addss xmm0, dword ptr [rip + amostra_x]
    movss xmm1, dword ptr [rip + posicao_teste + 4]
    addss xmm1, dword ptr [rip + amostra_y]
    call ponto_livre
    test eax, eax
    jz .bloqueado
    movss xmm0, dword ptr [rip + posicao_teste]
    subss xmm0, dword ptr [rip + amostra_x]
    movss xmm1, dword ptr [rip + posicao_teste + 4]
    addss xmm1, dword ptr [rip + amostra_y]
    call ponto_livre
    test eax, eax
    jz .bloqueado
    movss xmm0, dword ptr [rip + posicao_teste]
    addss xmm0, dword ptr [rip + amostra_x]
    movss xmm1, dword ptr [rip + posicao_teste + 4]
    subss xmm1, dword ptr [rip + amostra_y]
    call ponto_livre
    test eax, eax
    jz .bloqueado
    movss xmm0, dword ptr [rip + posicao_teste]
    subss xmm0, dword ptr [rip + amostra_x]
    movss xmm1, dword ptr [rip + posicao_teste + 4]
    subss xmm1, dword ptr [rip + amostra_y]
    call ponto_livre
    test eax, eax
    jz .bloqueado
.livre:
    mov eax, 1
.bloqueado:
    add rsp, 8
    ret

# rdi=x, rsi=y, rdx=largura, rcx=altura, r8=tipo. Preenche uma área row-major.
preencher_retangulo:
    push rbx
    push r12
    push r13
    push r14
    push r15
    mov r12d, edi
    mov r13d, esi
    mov r14d, edx
    mov r15d, ecx
    mov ebx, r8d
    xor r10d, r10d
.linha_retangulo:
    cmp r10d, r15d
    jge .fim_retangulo
    xor r9d, r9d
.coluna_retangulo:
    cmp r9d, r14d
    jge .proxima_linha_retangulo
    mov eax, r13d
    add eax, r10d
    imul eax, eax, 192
    add eax, r12d
    add eax, r9d
    lea rcx, [rip + mapa_tiles]
    mov byte ptr [rcx + rax], bl
    inc r9d
    jmp .coluna_retangulo
.proxima_linha_retangulo:
    inc r10d
    jmp .linha_retangulo
.fim_retangulo:
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbx
    ret

# Gera a planta extensa da loja. Todos os objetos usam a mesma matriz para arte e colisão.
gerar_mapa:
    push rbx
    push r12
    push r13
    push r14
    sub rsp, 8
    lea rdi, [rip + mapa_tiles]
    mov ecx, 27648
    mov al, '0'
    rep stosb

    lea rdi, [rip + layout_pisos]
    mov esi, (layout_pisos_fim - layout_pisos) / 20
    call aplicar_layout
    lea rdi, [rip + layout_paredes]
    mov esi, (layout_paredes_fim - layout_paredes) / 20
    call aplicar_layout
    lea rdi, [rip + layout_mobiliario]
    mov esi, (layout_mobiliario_fim - layout_mobiliario) / 20
    call aplicar_layout

    add rsp, 8
    pop r14
    pop r13
    pop r12
    pop rbx
    ret

# Aplica uma tabela de retângulos à matriz usada pelo desenho e pela física.
aplicar_layout:
    push r12
    push r13
    sub rsp, 8
    mov r12, rdi
    mov r13d, esi
.proximo_retangulo:
    test r13d, r13d
    jz .fim_layout
    mov edi, dword ptr [r12]
    mov esi, dword ptr [r12 + 4]
    mov edx, dword ptr [r12 + 8]
    mov ecx, dword ptr [r12 + 12]
    mov r8d, dword ptr [r12 + 16]
    call preencher_retangulo
    add r12, 20
    dec r13d
    jmp .proximo_retangulo
.fim_layout:
    add rsp, 8
    pop r13
    pop r12
    ret

# Converte o ponto projetado do pé para tile e consulta a mesma matriz da arte.
# wx=(x-640)/32+(y-360)/16; wy=(y-360)/16-(x-640)/32.
ponto_livre:
    subss xmm0, dword ptr [rip + origem_x]
    mulss xmm0, dword ptr [rip + inverso_32]
    subss xmm1, dword ptr [rip + origem_y]
    mulss xmm1, dword ptr [rip + inverso_16]
    movss xmm2, xmm1
    addss xmm2, xmm0
    subss xmm1, xmm0
    xor eax, eax
    ucomiss xmm2, dword ptr [rip + zero]
    jb .fim_ponto
    ucomiss xmm1, dword ptr [rip + zero]
    jb .fim_ponto
    ucomiss xmm2, dword ptr [rip + largura_mundo]
    jae .fim_ponto
    ucomiss xmm1, dword ptr [rip + altura_mundo]
    jae .fim_ponto
    cvttss2si ecx, xmm2
    cvttss2si edx, xmm1
    imul edx, edx, 192
    add edx, ecx
    lea rcx, [rip + mapa_tiles]
    movzx eax, byte ptr [rcx + rdx]
    cmp al, '0'
    je .ponto_livre
    cmp al, '7'
    je .ponto_livre
    cmp al, '9'
    je .ponto_livre
    cmp al, 'F'
    je .ponto_livre
    cmp al, 'L'
    je .ponto_livre
    cmp al, 'W'
    je .ponto_livre
    cmp al, 'T'
    sete al
    ret
.ponto_livre:
    mov eax, 1
.fim_ponto:
    ret

# Desenha o piso visível e ordena os objetos por profundidade isométrica.
desenhar_mapa:
    push rbx
    push r12
    push r13
    push r14
    push r15
    xor r12d, r12d
.piso_x:
    xor r13d, r13d
.piso_y:
    mov edi, r12d
    mov esi, r13d
    call coordenada_tile
    cmp eax, -16
    jl .proximo_piso
    cmp eax, 1296
    jg .proximo_piso
    cmp ecx, -16
    jl .proximo_piso
    cmp ecx, 736
    jg .proximo_piso
    mov dword ptr [rip + sx_atual], eax
    mov dword ptr [rip + sy_atual], ecx
    mov eax, r13d
    imul eax, eax, 192
    add eax, r12d
    lea rcx, [rip + mapa_tiles]
    movzx edx, byte ptr [rcx + rax]
    xor r15d, r15d
    mov r14d, 222
    cmp edx, '7'
    je .piso_tapete
    cmp edx, '9'
    je .piso_lancamento
    cmp edx, 'F'
    je .piso_madeira
    cmp edx, 'L'
    je .piso_tapete
    cmp edx, 'W'
    je .piso_metal
    cmp edx, 'T'
    je .piso_pedra
    jmp .desenhar_piso
.piso_tapete:
    mov r15d, 4
    mov r14d, 228
    jmp .desenhar_piso
.piso_lancamento:
    mov r15d, 4
    mov r14d, 242
    jmp .desenhar_piso
.piso_madeira:
    mov r15d, 1
    mov r14d, 205
    jmp .desenhar_piso
.piso_metal:
    mov r15d, 6
    mov r14d, 218
    jmp .desenhar_piso
.piso_pedra:
    mov r15d, 7
    mov r14d, 230
    jmp .desenhar_piso
.desenhar_piso:
    mov edi, dword ptr [rip + sx_atual]
    mov esi, dword ptr [rip + sy_atual]
    mov edx, r15d
    mov dword ptr [rip + luz_atual], r14d
    call desenhar_losango
.proximo_piso:
    inc r13d
    cmp r13d, 144
    jl .piso_y
    inc r12d
    cmp r12d, 192
    jl .piso_x

    xor r14d, r14d
.camada:
    xor r12d, r12d
.objeto_x:
    mov r13d, r14d
    sub r13d, r12d
    js .proximo_x
    cmp r13d, 144
    jae .proximo_x
    mov eax, r13d
    imul eax, eax, 192
    add eax, r12d
    lea rcx, [rip + mapa_tiles]
    movzx ebx, byte ptr [rcx + rax]
    cmp ebx, '0'
    je .proximo_x
    cmp ebx, '7'
    je .proximo_x
    cmp ebx, '9'
    je .proximo_x
    cmp ebx, 'F'
    je .proximo_x
    cmp ebx, 'L'
    je .proximo_x
    cmp ebx, 'W'
    je .proximo_x
    cmp ebx, 'T'
    je .proximo_x
    mov edi, r12d
    mov esi, r13d
    call coordenada_tile
    cmp eax, -16
    jl .proximo_x
    cmp eax, 1296
    jg .proximo_x
    cmp ecx, -64
    jl .proximo_x
    cmp ecx, 784
    jg .proximo_x
    mov dword ptr [rip + tx_atual], r12d
    mov dword ptr [rip + ty_atual], r13d
    mov edi, eax
    mov esi, ecx
    mov edx, ebx
    call desenhar_movel
    cmp dword ptr [rip + mostrar_colisoes], 0
    je .proximo_x
    call desenhar_contorno_solido
.proximo_x:
    inc r12d
    cmp r12d, 192
    jl .objeto_x

    # Soma do mundo corresponde à profundidade vertical isométrica.
    movss xmm0, dword ptr [rip + icaro + POS_Y]
    subss xmm0, dword ptr [rip + origem_y]
    mulss xmm0, dword ptr [rip + inverso_8]
    cvttss2si eax, xmm0
    cmp eax, r14d
    jne .sem_icaro
    lea rdi, [rip + icaro]
    lea rsi, [rip + textura_icaro]
    call desenhar_personagem
.sem_icaro:
    inc r14d
    cmp r14d, 335
    jl .camada
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbx
    ret

# edi=x, esi=y -> eax,ecx = vértice superior do losango em pixels.
coordenada_tile:
    mov eax, edi
    sub eax, esi
    imul eax, eax, 16
    add eax, 640
    mov ecx, edi
    add ecx, esi
    imul ecx, ecx, 8
    add ecx, 360
    cvttss2si edx, dword ptr [rip + camera_x]
    add eax, edx
    cvttss2si edx, dword ptr [rip + camera_y]
    add ecx, edx
    ret

# Modo de inspeção: marca exatamente os tiles sólidos consultados pela física.
desenhar_contorno_solido:
    sub rsp, 8
    mov edi, dword ptr [rip + sx_atual]
    mov esi, dword ptr [rip + sy_atual]
    mov edx, edi
    add edx, 16
    mov ecx, esi
    add ecx, 8
    mov r8d, 0xffff00ff
    call DrawLine
    mov edi, dword ptr [rip + sx_atual]
    add edi, 16
    mov esi, dword ptr [rip + sy_atual]
    add esi, 8
    mov edx, dword ptr [rip + sx_atual]
    mov ecx, dword ptr [rip + sy_atual]
    add ecx, 16
    mov r8d, 0xffff00ff
    call DrawLine
    mov edi, dword ptr [rip + sx_atual]
    mov esi, dword ptr [rip + sy_atual]
    add esi, 16
    mov edx, edi
    sub edx, 16
    mov ecx, esi
    sub ecx, 8
    mov r8d, 0xffff00ff
    call DrawLine
    mov edi, dword ptr [rip + sx_atual]
    sub edi, 16
    mov esi, dword ptr [rip + sy_atual]
    add esi, 8
    mov edx, dword ptr [rip + sx_atual]
    mov ecx, dword ptr [rip + sy_atual]
    mov r8d, 0xffff00ff
    call DrawLine
    add rsp, 8
    ret

# quad_atual contém quatro Vector2; material_atual seleciona uma textura gerada.
preencher_quad:
    push r12
    push r13
    sub rsp, 8
    mov eax, dword ptr [rip + material_atual]
    imul eax, eax, 20
    lea rcx, [rip + textura_piso]
    mov edi, dword ptr [rcx + rax]
    call rlSetTexture
    mov edi, 7
    call rlBegin
    mov edi, dword ptr [rip + luz_atual]
    mov esi, edi
    mov edx, edi
    mov ecx, 255
    call rlColor4ub
    cmp dword ptr [rip + desenhar_topo], 0
    je .ordem_face
    lea r12, [rip + ordem_losango_topo]
    jmp .ordem_pronta
.ordem_face:
    lea r12, [rip + ordem_losango_face]
.ordem_pronta:
    xor r13d, r13d
.vertice:
    movzx eax, byte ptr [r12 + r13]
    lea rdx, [rip + uv_losango]
    movss xmm0, dword ptr [rdx + rax*8]
    movss xmm1, dword ptr [rdx + rax*8 + 4]
    call rlTexCoord2f
    movzx eax, byte ptr [r12 + r13]
    lea rdx, [rip + quad_atual]
    movss xmm0, dword ptr [rdx + rax*8]
    movss xmm1, dword ptr [rdx + rax*8 + 4]
    call rlVertex2f
    inc r13d
    cmp r13d, 4
    jl .vertice
    call rlEnd
    xor edi, edi
    call rlSetTexture
    add rsp, 8
    pop r13
    pop r12
    ret

# edi=sx, esi=sy, edx=cor. Geometria única para todos os tiles.
desenhar_losango:
    sub rsp, 24
    mov dword ptr [rip + desenhar_topo], 1
    mov dword ptr [rsp + 16], edx
    mov dword ptr [rsp + 0], edi
    mov dword ptr [rsp + 4], esi
    mov eax, edi
    cvtsi2ss xmm0, eax
    movss dword ptr [rip + quad_atual], xmm0
    mov eax, esi
    cvtsi2ss xmm0, eax
    movss dword ptr [rip + quad_atual + 4], xmm0
    mov eax, edi
    add eax, 16
    cvtsi2ss xmm0, eax
    movss dword ptr [rip + quad_atual + 8], xmm0
    mov eax, esi
    add eax, 8
    cvtsi2ss xmm0, eax
    movss dword ptr [rip + quad_atual + 12], xmm0
    mov eax, edi
    cvtsi2ss xmm0, eax
    movss dword ptr [rip + quad_atual + 16], xmm0
    mov eax, esi
    add eax, 16
    cvtsi2ss xmm0, eax
    movss dword ptr [rip + quad_atual + 20], xmm0
    mov eax, edi
    sub eax, 16
    cvtsi2ss xmm0, eax
    movss dword ptr [rip + quad_atual + 24], xmm0
    mov eax, esi
    add eax, 8
    cvtsi2ss xmm0, eax
    movss dword ptr [rip + quad_atual + 28], xmm0
    mov eax, dword ptr [rsp + 16]
    mov dword ptr [rip + material_atual], eax
    call preencher_quad
    add rsp, 24
    ret

# edi=sx, esi=sy, edx=tile ASCII. Paredes e móveis ocupam o mesmo tile sólido.
desenhar_movel:
    push rbx
    sub rsp, 16
    mov dword ptr [rip + sx_atual], edi
    mov dword ptr [rip + sy_atual], esi
    mov dword ptr [rip + tipo_atual], edx
    mov ebx, 17
    cmp edx, '5'
    jne .nao_borda
    mov ebx, 18
    jmp .altura_pronta
.nao_borda:
    cmp edx, '1'
    jne .nao_estante
    mov ebx, 32
    jmp .altura_pronta
.nao_estante:
    cmp edx, '2'
    jne .nao_caixa
    mov ebx, 12
    jmp .altura_pronta
.nao_caixa:
    cmp edx, '4'
    jne .nao_planta
    mov ebx, 9
    jmp .altura_pronta
.nao_planta:
    cmp edx, '6'
    jne .nao_audicao
    mov ebx, 15
    jmp .altura_pronta
.nao_audicao:
    cmp edx, '8'
    jne .nao_parede_interna
    mov ebx, 54
    jmp .altura_pronta
.nao_parede_interna:
    cmp edx, '3'
    jne .nao_balcao
    mov ebx, 18
    jmp .altura_pronta
.nao_balcao:
    cmp edx, 'm'
    jne .nao_maquina
    mov ebx, 13
    jmp .altura_pronta
.nao_maquina:
    cmp edx, 'd'
    jne .nao_mesa_cafe
    mov ebx, 7
    jmp .altura_pronta
.nao_mesa_cafe:
    cmp edx, 's'
    jne .nao_pia
    mov ebx, 10
    jmp .altura_pronta
.nao_pia:
    cmp edx, 't'
    jne .altura_pronta
    mov ebx, 8
.altura_pronta:
    mov dword ptr [rip + altura_atual], ebx
    # Faces verticais: dois quadriláteros formados a partir do topo.
    mov edi, dword ptr [rip + sx_atual]
    mov esi, dword ptr [rip + sy_atual]
    sub esi, ebx
    mov edx, 1
    cmp dword ptr [rip + tipo_atual], '1'
    je .prateleira_topo
    cmp dword ptr [rip + tipo_atual], '4'
    jne .nao_topo_planta
    mov edx, 3
    jmp .topo
.nao_topo_planta:
    cmp dword ptr [rip + tipo_atual], '6'
    jne .nao_topo_mesa
    mov edx, 6
    jmp .topo
.nao_topo_mesa:
    cmp dword ptr [rip + tipo_atual], 'm'
    jne .nao_topo_maquina
    mov edx, 6
    jmp .topo
.nao_topo_maquina:
    cmp dword ptr [rip + tipo_atual], 's'
    je .topo_pedra
    cmp dword ptr [rip + tipo_atual], 't'
    je .topo_pedra
    cmp dword ptr [rip + tipo_atual], '8'
    jne .nao_topo_parede
    mov edx, 5
    jmp .topo
.topo_pedra:
    mov edx, 7
    jmp .topo
.nao_topo_parede:
    cmp dword ptr [rip + tipo_atual], '5'
    jne .topo
    mov edx, 7
    jmp .topo
.prateleira_topo:
    mov edx, 2
    jmp .topo
.topo:
    mov dword ptr [rip + luz_atual], 255
    call desenhar_losango
    # Face direita: vértices 1,2,2+h,1+h.
    movq xmm0, qword ptr [rip + quad_atual + 8]
    movq qword ptr [rip + quad_atual], xmm0
    movq xmm0, qword ptr [rip + quad_atual + 16]
    movq qword ptr [rip + quad_atual + 8], xmm0
    movss xmm0, dword ptr [rip + quad_atual + 12]
    cvtsi2ss xmm1, dword ptr [rip + altura_atual]
    addss xmm0, xmm1
    movss dword ptr [rip + quad_atual + 20], xmm0
    movss xmm0, dword ptr [rip + quad_atual + 8]
    movss dword ptr [rip + quad_atual + 16], xmm0
    movss xmm0, dword ptr [rip + quad_atual + 4]
    addss xmm0, xmm1
    movss dword ptr [rip + quad_atual + 28], xmm0
    movss xmm0, dword ptr [rip + quad_atual]
    movss dword ptr [rip + quad_atual + 24], xmm0
.face_r:
    cmp dword ptr [rip + tipo_atual], '1'
    jne .face_r_material_pronto
    mov dword ptr [rip + material_atual], 1
.face_r_material_pronto:
    mov dword ptr [rip + luz_atual], 210
    mov dword ptr [rip + desenhar_topo], 0
    call preencher_quad
    # Outra face é produzida a partir das coordenadas do tile.
    mov edi, dword ptr [rip + sx_atual]
    mov esi, dword ptr [rip + sy_atual]
    sub esi, dword ptr [rip + altura_atual]
    mov edx, 1
    cmp dword ptr [rip + tipo_atual], '1'
    jne .face_material_nao_estante
    mov edx, 1
    jmp .refazer
.face_material_nao_estante:
    cmp dword ptr [rip + tipo_atual], '4'
    jne .face_material_nao_planta
    mov edx, 3
    jmp .refazer
.face_material_nao_planta:
    cmp dword ptr [rip + tipo_atual], '6'
    jne .face_material_nao_mesa
    mov edx, 6
    jmp .refazer
.face_material_nao_mesa:
    cmp dword ptr [rip + tipo_atual], 'm'
    jne .face_material_nao_maquina
    mov edx, 6
    jmp .refazer
.face_material_nao_maquina:
    cmp dword ptr [rip + tipo_atual], 's'
    je .face_material_pedra
    cmp dword ptr [rip + tipo_atual], 't'
    je .face_material_pedra
    cmp dword ptr [rip + tipo_atual], '8'
    jne .face_material_nao_parede
    mov edx, 5
    jmp .refazer
.face_material_pedra:
    mov edx, 7
    jmp .refazer
.face_material_nao_parede:
    cmp dword ptr [rip + tipo_atual], '5'
    jne .refazer
    mov edx, 7
.refazer:
    call desenhar_losango
    movq xmm0, qword ptr [rip + quad_atual + 16]
    movq qword ptr [rip + quad_atual], xmm0
    movq xmm0, qword ptr [rip + quad_atual + 24]
    movq qword ptr [rip + quad_atual + 8], xmm0
    cvtsi2ss xmm1, dword ptr [rip + altura_atual]
    movss xmm0, dword ptr [rip + quad_atual + 12]
    addss xmm0, xmm1
    movss dword ptr [rip + quad_atual + 20], xmm0
    movss xmm0, dword ptr [rip + quad_atual + 8]
    movss dword ptr [rip + quad_atual + 16], xmm0
    movss xmm0, dword ptr [rip + quad_atual + 4]
    addss xmm0, xmm1
    movss dword ptr [rip + quad_atual + 28], xmm0
    movss xmm0, dword ptr [rip + quad_atual]
    movss dword ptr [rip + quad_atual + 24], xmm0
.face_l:
    mov dword ptr [rip + luz_atual], 175
    mov dword ptr [rip + desenhar_topo], 0
    call preencher_quad
    # Vinis e vegetação têm marca visual distinta dos blocos de parede.
    cmp dword ptr [rip + tipo_atual], '5'
    je .fim_movel
    cmp dword ptr [rip + tipo_atual], '4'
    je .planta
    cmp dword ptr [rip + tipo_atual], '2'
    je .disco
    cmp dword ptr [rip + tipo_atual], '6'
    je .disco
    cmp dword ptr [rip + tipo_atual], '1'
    je .detalhe_estante
    cmp dword ptr [rip + tipo_atual], '8'
    je .detalhe_parede
    cmp dword ptr [rip + tipo_atual], '3'
    je .balcao
    cmp dword ptr [rip + tipo_atual], 'm'
    je .maquina_cafe
    cmp dword ptr [rip + tipo_atual], 'd'
    je .mesa_cafe
    cmp dword ptr [rip + tipo_atual], 's'
    je .pia
    cmp dword ptr [rip + tipo_atual], 't'
    je .sanitario
    mov edi, dword ptr [rip + sx_atual]
    sub edi, 13
    mov esi, dword ptr [rip + sy_atual]
    add esi, 8
    sub esi, dword ptr [rip + altura_atual]
    mov edx, edi
    add edx, 26
    mov ecx, esi
    add ecx, 10
    mov r8d, 0xff4cc4ed
    call DrawLine
    jmp .fim_movel
.detalhe_estante:
    mov eax, dword ptr [rip + tx_atual]
    add eax, dword ptr [rip + ty_atual]
    and eax, 3
    test eax, eax
    jz .capa_estante
    cmp eax, 1
    jne .fim_movel
    mov edi, dword ptr [rip + sx_atual]
    sub edi, 13
    mov esi, dword ptr [rip + sy_atual]
    sub esi, dword ptr [rip + altura_atual]
    add esi, 9
    mov edx, 3
    mov ecx, 8
    mov r8d, 0xffd6a765
    call DrawRectangle
    mov edi, dword ptr [rip + sx_atual]
    sub edi, 9
    mov esi, dword ptr [rip + sy_atual]
    sub esi, dword ptr [rip + altura_atual]
    add esi, 10
    mov edx, 3
    mov ecx, 7
    mov r8d, 0xff8d9fb2
    call DrawRectangle
    mov edi, dword ptr [rip + sx_atual]
    sub edi, 5
    mov esi, dword ptr [rip + sy_atual]
    sub esi, dword ptr [rip + altura_atual]
    add esi, 8
    mov edx, 2
    mov ecx, 8
    mov r8d, 0xffb86468
    call DrawRectangle
    jmp .fim_movel
.capa_estante:
    mov edi, dword ptr [rip + sx_atual]
    sub edi, 15
    mov esi, dword ptr [rip + sy_atual]
    sub esi, dword ptr [rip + altura_atual]
    add esi, 8
    mov edx, 15
    mov ecx, 19
    mov r8d, 0xffb69359
    call DrawRectangle
    call desenhar_capa
    jmp .fim_movel
.detalhe_parede:
    mov eax, dword ptr [rip + tx_atual]
    and eax, 15
    cmp eax, 5
    jne .fim_movel
    mov edi, dword ptr [rip + sx_atual]
    sub edi, 10
    mov esi, dword ptr [rip + sy_atual]
    sub esi, dword ptr [rip + altura_atual]
    add esi, 13
    mov edx, 14
    mov ecx, 19
    mov r8d, 0xffac874f
    call DrawRectangle
    mov edi, dword ptr [rip + sx_atual]
    sub edi, 8
    mov esi, dword ptr [rip + sy_atual]
    sub esi, dword ptr [rip + altura_atual]
    add esi, 15
    mov edx, 10
    mov ecx, 15
    mov r8d, 0xff684b44
    call DrawRectangle
    jmp .fim_movel
.disco:
    mov edi, dword ptr [rip + sx_atual]
    mov esi, dword ptr [rip + sy_atual]
    add esi, 8
    sub esi, dword ptr [rip + altura_atual]
    movss xmm0, dword ptr [rip + raio_prato]
    mov edx, 0xff121418
    call DrawCircle
    mov edi, dword ptr [rip + sx_atual]
    mov esi, dword ptr [rip + sy_atual]
    add esi, 8
    sub esi, dword ptr [rip + altura_atual]
    movss xmm0, dword ptr [rip + raio_miolo]
    mov edx, 0xffd784ba
    call DrawCircle
    jmp .fim_movel
.balcao:
    mov edi, dword ptr [rip + sx_atual]
    sub edi, 13
    mov esi, dword ptr [rip + sy_atual]
    add esi, 8
    sub esi, dword ptr [rip + altura_atual]
    mov edx, edi
    add edx, 26
    mov ecx, esi
    add ecx, 9
    mov r8d, 0xff5ea4d5
    call DrawLine
    # A bancada da oficina ganha marcas de ferramenta; a da cafeteria, um caixa.
    cmp dword ptr [rip + tx_atual], 100
    jae .ferramenta_bancada
    mov eax, dword ptr [rip + tx_atual]
    and eax, 7
    cmp eax, 1
    jne .fim_movel
    mov edi, dword ptr [rip + sx_atual]
    sub edi, 4
    mov esi, dword ptr [rip + sy_atual]
    sub esi, dword ptr [rip + altura_atual]
    add esi, 4
    mov edx, 8
    mov ecx, 5
    mov r8d, 0xff313c3b
    call DrawRectangle
    mov edi, dword ptr [rip + sx_atual]
    sub edi, 2
    mov esi, dword ptr [rip + sy_atual]
    sub esi, dword ptr [rip + altura_atual]
    add esi, 5
    mov edx, 3
    mov ecx, 2
    mov r8d, 0xff81c6e5
    call DrawRectangle
    jmp .fim_movel
.ferramenta_bancada:
    mov eax, dword ptr [rip + tx_atual]
    and eax, 3
    test eax, eax
    jne .fim_movel
    mov edi, dword ptr [rip + sx_atual]
    sub edi, 5
    mov esi, dword ptr [rip + sy_atual]
    sub esi, dword ptr [rip + altura_atual]
    add esi, 5
    mov edx, 10
    mov ecx, 2
    mov r8d, 0xff478dc5
    call DrawRectangle
    jmp .fim_movel
.maquina_cafe:
    mov edi, dword ptr [rip + sx_atual]
    sub edi, 7
    mov esi, dword ptr [rip + sy_atual]
    sub esi, dword ptr [rip + altura_atual]
    add esi, 2
    mov edx, 14
    mov ecx, 9
    mov r8d, 0xff303b3d
    call DrawRectangle
    mov edi, dword ptr [rip + sx_atual]
    sub edi, 4
    mov esi, dword ptr [rip + sy_atual]
    sub esi, dword ptr [rip + altura_atual]
    add esi, 4
    mov edx, 7
    mov ecx, 3
    mov r8d, 0xffa0a684
    call DrawRectangle
    mov edi, dword ptr [rip + sx_atual]
    add edi, 4
    mov esi, dword ptr [rip + sy_atual]
    sub esi, dword ptr [rip + altura_atual]
    add esi, 11
    movss xmm0, dword ptr [rip + raio_cafe]
    mov edx, 0xffc5e1ee
    call DrawCircle
    jmp .fim_movel
.mesa_cafe:
    mov edi, dword ptr [rip + sx_atual]
    mov esi, dword ptr [rip + sy_atual]
    add esi, 8
    sub esi, dword ptr [rip + altura_atual]
    movss xmm0, dword ptr [rip + raio_mesa]
    mov edx, 0xff4d79b7
    call DrawCircle
    mov edi, dword ptr [rip + sx_atual]
    add edi, 2
    mov esi, dword ptr [rip + sy_atual]
    add esi, 7
    sub esi, dword ptr [rip + altura_atual]
    movss xmm0, dword ptr [rip + raio_cafe]
    mov edx, 0xffcee6f1
    call DrawCircle
    jmp .fim_movel
.pia:
    mov edi, dword ptr [rip + sx_atual]
    sub edi, 8
    mov esi, dword ptr [rip + sy_atual]
    sub esi, dword ptr [rip + altura_atual]
    add esi, 3
    mov edx, 16
    mov ecx, 8
    mov r8d, 0xffd7ded7
    call DrawRectangle
    mov edi, dword ptr [rip + sx_atual]
    sub edi, 3
    mov esi, dword ptr [rip + sy_atual]
    sub esi, dword ptr [rip + altura_atual]
    add esi, 5
    mov edx, 6
    mov ecx, 3
    mov r8d, 0xff71827e
    call DrawRectangle
    mov edi, dword ptr [rip + sx_atual]
    mov esi, dword ptr [rip + sy_atual]
    sub esi, dword ptr [rip + altura_atual]
    add esi, 1
    mov edx, edi
    add edx, 3
    mov ecx, esi
    add ecx, 4
    mov r8d, 0xffaeb9ae
    call DrawLine
    jmp .fim_movel
.sanitario:
    mov edi, dword ptr [rip + sx_atual]
    sub edi, 5
    mov esi, dword ptr [rip + sy_atual]
    sub esi, dword ptr [rip + altura_atual]
    add esi, 1
    mov edx, 10
    mov ecx, 4
    mov r8d, 0xffe1e6dc
    call DrawRectangle
    mov edi, dword ptr [rip + sx_atual]
    mov esi, dword ptr [rip + sy_atual]
    add esi, 7
    sub esi, dword ptr [rip + altura_atual]
    movss xmm0, dword ptr [rip + raio_louca]
    mov edx, 0xffd6ddd3
    call DrawCircle
    mov edi, dword ptr [rip + sx_atual]
    mov esi, dword ptr [rip + sy_atual]
    add esi, 7
    sub esi, dword ptr [rip + altura_atual]
    movss xmm0, dword ptr [rip + raio_bacia]
    mov edx, 0xff77847d
    call DrawCircle
    jmp .fim_movel
.planta:
    mov edi, dword ptr [rip + sx_atual]
    mov esi, dword ptr [rip + sy_atual]
    sub esi, 8
    movss xmm0, dword ptr [rip + raio_planta]
    mov edx, 0xff2d7551
    call DrawCircle
.fim_movel:
    add rsp, 16
    pop rbx
    ret

# Seleciona uma das quatro capas da prancha e a encaixa na face da estante.
desenhar_capa:
    sub rsp, 8
    mov eax, dword ptr [rip + tx_atual]
    mov edx, dword ptr [rip + ty_atual]
    imul edx, edx, 3
    add eax, edx
    and eax, 3
    mov r9d, eax
    test eax, 1
    jz .capa_esquerda
    mov eax, 256
    cvtsi2ss xmm0, eax
    movss dword ptr [rip + quad_capa], xmm0
    jmp .capa_y
.capa_esquerda:
    movss xmm0, dword ptr [rip + zero]
    movss dword ptr [rip + quad_capa], xmm0
.capa_y:
    test r9d, 2
    jz .capa_superior
    mov eax, 256
    cvtsi2ss xmm0, eax
    movss dword ptr [rip + quad_capa + 4], xmm0
    jmp .capa_tamanho
.capa_superior:
    movss xmm0, dword ptr [rip + zero]
    movss dword ptr [rip + quad_capa + 4], xmm0
.capa_tamanho:
    mov eax, 256
    cvtsi2ss xmm0, eax
    movss dword ptr [rip + quad_capa + 8], xmm0
    movss dword ptr [rip + quad_capa + 12], xmm0
    mov eax, dword ptr [rip + sx_atual]
    sub eax, 14
    cvtsi2ss xmm0, eax
    movss dword ptr [rip + quad_capa + 16], xmm0
    mov eax, dword ptr [rip + sy_atual]
    sub eax, dword ptr [rip + altura_atual]
    add eax, 10
    cvtsi2ss xmm0, eax
    movss dword ptr [rip + quad_capa + 20], xmm0
    mov eax, 13
    cvtsi2ss xmm0, eax
    movss dword ptr [rip + quad_capa + 24], xmm0
    mov eax, 17
    cvtsi2ss xmm0, eax
    movss dword ptr [rip + quad_capa + 28], xmm0
    lea rdi, [rip + textura_capas]
    movq xmm0, qword ptr [rip + quad_capa]
    movq xmm1, qword ptr [rip + quad_capa + 8]
    movq xmm2, qword ptr [rip + quad_capa + 16]
    movq xmm3, qword ptr [rip + quad_capa + 24]
    movq xmm4, qword ptr [rip + origem_zero]
    xorps xmm5, xmm5
    call desenhar_textura
    add rsp, 8
    ret

# rdi = personagem; rsi = Texture2D. Recorta a linha/direção e a pose.
desenhar_personagem:
    push rbp
    mov rbp, rsp
    push r12
    push r13
    sub rsp, 64
    mov r12, rdi
    mov r13, rsi

    xor eax, eax
    cmp dword ptr [r12 + ANDANDO], 0
    je .quadro_escolhido
    movss xmm0, dword ptr [r12 + TEMPO]
    mulss xmm0, dword ptr [rip + dez]
    cvttss2si eax, xmm0
    and eax, 7
    inc eax
.quadro_escolhido:
    imul eax, eax, 384
    cvtsi2ss xmm0, eax
    movss dword ptr [rsp + 32], xmm0
    mov eax, dword ptr [r12 + DIRECAO]
    imul eax, eax, 512
    cvtsi2ss xmm0, eax
    movss dword ptr [rsp + 36], xmm0

movss xmm0, dword ptr [r12 + POS_X]
    addss xmm0, dword ptr [rip + camera_x]
    subss xmm0, dword ptr [rip + ancora_x]
    movss dword ptr [rsp + 40], xmm0
    movss xmm0, dword ptr [r12 + POS_Y]
    addss xmm0, dword ptr [rip + camera_y]
    subss xmm0, dword ptr [rip + ancora_y]
    movss dword ptr [rsp + 44], xmm0

    movq xmm0, qword ptr [rsp + 32]
    movq xmm1, qword ptr [rip + tamanho_celula]
    movq xmm2, qword ptr [rsp + 40]
    movq xmm3, qword ptr [rip + tamanho_sprite]
    movq xmm4, qword ptr [rip + origem_zero]
    xorps xmm5, xmm5
    mov rdi, r13
    call desenhar_textura

    add rsp, 64
    pop r13
    pop r12
    pop rbp
    ret

.section .note.GNU-stack,"",@progbits
