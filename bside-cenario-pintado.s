.intel_syntax noprefix

# B-Side: uma sala 2.5D. Toda a lógica do jogo está em Assembly x86-64.
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
caminho_mapa:   .asciz "assets/b-side-sala-sprites.png"
caminho_icaro_final: .asciz "assets/icaro-andar-final.png"
caminho_eva_final:   .asciz "assets/eva-andar-final.png"
caminho_icaro:  .asciz "assets/icaro-andar-rascunho.png"
caminho_eva:    .asciz "assets/eva-andar-rascunho.png"
erro_recursos:  .asciz "Nao foi possivel carregar o mapa ou as sprites. Execute a partir da raiz do repositorio."
erro_janela:    .asciz "Nao foi possivel abrir uma janela grafica."
ajuda:          .asciz "ICARO  WASD     EVA  SETAS                  ESC  sair"
variavel_captura: .asciz "BSIDE_CAPTURE"
variavel_colisoes: .asciz "BSIDE_COLISOES"
caminho_captura: .asciz "captura.png"

.align 8
origem_bg:      .float 0.0, 0.0
tamanho_bg:     .float 1672.0, 940.0
destino_bg:     .float 0.0, 0.0
tamanho_tela:   .float 1280.0, 720.0
origem_zero:    .float 0.0, 0.0
tamanho_celula: .float 384.0, 512.0
tamanho_sprite: .float 165.0, 220.0
limite_delta:   .float 0.05
velocidade:     .float 190.0
diagonal:       .float 0.70710678
um:             .float 1.0
zero:           .float 0.0
tempo_ciclo:    .float 0.8
dez:            .float 10.0
ancora_x:       .float 82.5
ancora_y:       .float 206.25

# Coordenadas da janela 1280x720. Os polígonos cobrem a silhueta
# dos móveis, com pequena folga para que os pés não entrem na madeira.
min_x:          .float 45.0
max_x:          .float 1235.0
min_y:          .float 415.0
max_y:          .float 673.0
parede_esq_x:   .float 185.0
parede_esq_y:   .float 520.0
distancia_personagens2: .float 1296.0
.align 8
expo_esq:       .float 190.0, 386.0
                .float 553.0, 374.0
                .float 564.0, 547.0
                .float 389.0, 634.0
                .float 190.0, 624.0
                .float 190.0, 386.0
expo_dir:       .float 884.0, 378.0
                .float 1096.0, 389.0
                .float 1103.0, 622.0
                .float 933.0, 622.0
                .float 884.0, 378.0
balcao:         .float 1030.0, 296.0
                .float 1279.0, 296.0
                .float 1279.0, 673.0
                .float 1154.0, 673.0
                .float 1030.0, 296.0

.section .data
.align 16
# x, y, direção, andando, tempo, cima, baixo, esquerda, direita
icaro: .float 708.0, 605.0
       .long 4, 0
       .float 0.0
       .long 87, 83, 65, 68
eva:   .float 810.0, 598.0
       .long 4, 0
       .float 0.0
       .long 265, 264, 263, 262

.section .bss
.align 16
textura_mapa:  .skip 20
textura_icaro: .skip 20
textura_eva:   .skip 20
delta_quadro:  .skip 4
capturar:      .skip 4
mostrar_colisoes: .skip 4

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

    lea rdi, [rip + textura_mapa]
    lea rsi, [rip + caminho_mapa]
    call LoadTexture
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
    lea rdi, [rip + caminho_eva_final]
    call FileExists
    test al, al
    jz .usar_eva_rascunho
    lea rsi, [rip + caminho_eva_final]
    jmp .carregar_eva
.usar_eva_rascunho:
    lea rsi, [rip + caminho_eva]
.carregar_eva:
    lea rdi, [rip + textura_eva]
    call LoadTexture

    cmp dword ptr [rip + textura_mapa], 0
    je .erro
    cmp dword ptr [rip + textura_icaro], 0
    je .erro
    cmp dword ptr [rip + textura_eva], 0
    je .erro

.quadro:
    call WindowShouldClose
    test eax, eax
    jne .fechar

    call GetFrameTime
    minss xmm0, dword ptr [rip + limite_delta]
    movss dword ptr [rip + delta_quadro], xmm0

    lea rdi, [rip + icaro]
    call atualizar_personagem
    lea rdi, [rip + eva]
    call atualizar_personagem

    call BeginDrawing
    mov edi, 0xff101018
    call ClearBackground
    lea rdi, [rip + textura_mapa]
    movq xmm0, qword ptr [rip + origem_bg]
    movq xmm1, qword ptr [rip + tamanho_bg]
    movq xmm2, qword ptr [rip + destino_bg]
    movq xmm3, qword ptr [rip + tamanho_tela]
    movq xmm4, qword ptr [rip + origem_zero]
    xorps xmm5, xmm5
    call desenhar_textura

    cmp dword ptr [rip + mostrar_colisoes], 0
    je .sem_malha
    lea rdi, [rip + expo_esq]
    mov esi, 5
    mov edx, 0xff4288ff
    call desenhar_poligono
    lea rdi, [rip + expo_dir]
    mov esi, 4
    mov edx, 0xff4288ff
    call desenhar_poligono
    lea rdi, [rip + balcao]
    mov esi, 4
    mov edx, 0xff4288ff
    call desenhar_poligono
.sem_malha:

    # Os pés mais ao fundo são desenhados primeiro.
    movss xmm0, dword ptr [rip + icaro + POS_Y]
    ucomiss xmm0, dword ptr [rip + eva + POS_Y]
    ja .eva_primeiro
    lea rdi, [rip + icaro]
    lea rsi, [rip + textura_icaro]
    call desenhar_personagem
    lea rdi, [rip + eva]
    lea rsi, [rip + textura_eva]
    call desenhar_personagem
    jmp .hud
.eva_primeiro:
    lea rdi, [rip + eva]
    lea rsi, [rip + textura_eva]
    call desenhar_personagem
    lea rdi, [rip + icaro]
    lea rsi, [rip + textura_icaro]
    call desenhar_personagem

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
    cmp dword ptr [rip + textura_mapa], 0
    je .pular_mapa
    lea rdi, [rip + textura_mapa]
    call descarregar_textura
.pular_mapa:
    cmp dword ptr [rip + textura_icaro], 0
    je .pular_icaro
    lea rdi, [rip + textura_icaro]
    call descarregar_textura
.pular_icaro:
    cmp dword ptr [rip + textura_eva], 0
    je .pular_eva
    lea rdi, [rip + textura_eva]
    call descarregar_textura
.pular_eva:
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
    sub rsp, 8
    mov r12, rdi
    xor ebx, ebx                   # dx = -1, 0 ou +1
    xor r13d, r13d                 # dy = -1, 0 ou +1

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
    movss xmm2, dword ptr [rip + delta_quadro]
    mulss xmm2, dword ptr [rip + velocidade]
    test ebx, ebx
    jz .fator_pronto
    test r13d, r13d
    jz .fator_pronto
    mulss xmm2, dword ptr [rip + diagonal]
.fator_pronto:
    cvtsi2ss xmm0, ebx
    mulss xmm0, xmm2
    addss xmm0, dword ptr [r12 + POS_X]
    movss xmm1, dword ptr [r12 + POS_Y]
    movss dword ptr [rsp], xmm2
    mov r8, r12
    call pode_andar
    test eax, eax
    jz .pular_x
    movss xmm0, dword ptr [rsp + 0]
    cvtsi2ss xmm1, ebx
    mulss xmm0, xmm1
    addss xmm0, dword ptr [r12 + POS_X]
    movss dword ptr [r12 + POS_X], xmm0
    test ebx, ebx
    jz .pular_x
    mov dword ptr [r12 + ANDANDO], 1
.pular_x:
    cvtsi2ss xmm1, r13d
    mulss xmm1, dword ptr [rsp]
    addss xmm1, dword ptr [r12 + POS_Y]
    movss xmm0, dword ptr [r12 + POS_X]
    movss dword ptr [rsp + 4], xmm1
    mov r8, r12
    call pode_andar
    test eax, eax
    jz .pular_y
    movss xmm1, dword ptr [rsp + 4]
    movss dword ptr [r12 + POS_Y], xmm1
    test r13d, r13d
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
    add rsp, 8
    pop r13
    pop r12
    pop rbx
    pop rbp
    ret

# xmm0=x, xmm1=y, r8=personagem ativa; eax=1 se o apoio está livre.
pode_andar:
    sub rsp, 8
    xor eax, eax
    ucomiss xmm0, dword ptr [rip + min_x]
    jb .bloqueado
    ucomiss xmm0, dword ptr [rip + max_x]
    ja .bloqueado
    ucomiss xmm1, dword ptr [rip + min_y]
    jb .bloqueado
    ucomiss xmm1, dword ptr [rip + max_y]
    ja .bloqueado

    # Porta/vitrine à esquerda: o chão só começa abaixo da soleira.
    ucomiss xmm0, dword ptr [rip + parede_esq_x]
    jae .verificar_expos
    ucomiss xmm1, dword ptr [rip + parede_esq_y]
    jb .bloqueado

.verificar_expos:
    lea rdi, [rip + expo_esq]
    mov esi, 5
    call dentro_poligono
    test eax, eax
    jnz .bloqueado
    lea rdi, [rip + expo_dir]
    mov esi, 4
    call dentro_poligono
    test eax, eax
    jnz .bloqueado
    lea rdi, [rip + balcao]
    mov esi, 4
    call dentro_poligono
    test eax, eax
    jnz .bloqueado
    # Os dois personagens mantêm espaço para não atravessarem seus corpos.
    lea rdi, [rip + icaro]
    cmp r8, rdi
    jne .comparar_icaro
    lea rdi, [rip + eva]
.comparar_icaro:
    movss xmm2, xmm0
    subss xmm2, dword ptr [rdi + POS_X]
    mulss xmm2, xmm2
    movss xmm3, xmm1
    subss xmm3, dword ptr [rdi + POS_Y]
    mulss xmm3, xmm3
    addss xmm2, xmm3
    ucomiss xmm2, dword ptr [rip + distancia_personagens2]
    jb .bloqueado
.livre:
    mov eax, 1
.bloqueado:
    add rsp, 8
    ret

# Polígono convexo em sentido horário na imagem, mais o primeiro repetido.
# O produto vetorial mantém o ponto do mesmo lado de cada aresta.
# rdi=vértices, esi=número de arestas, xmm0=x, xmm1=y; eax=1 dentro.
dentro_poligono:
    mov ecx, esi
.aresta:
    movss xmm2, dword ptr [rdi]
    movss xmm3, dword ptr [rdi + 4]
    movss xmm4, dword ptr [rdi + 8]
    subss xmm4, xmm2               # dx da aresta
    movss xmm5, dword ptr [rdi + 12]
    subss xmm5, xmm3               # dy da aresta
    movss xmm6, xmm1
    subss xmm6, xmm3
    mulss xmm6, xmm4
    movss xmm7, xmm0
    subss xmm7, xmm2
    mulss xmm7, xmm5
    subss xmm6, xmm7
    ucomiss xmm6, dword ptr [rip + zero]
    jb .fora
    add rdi, 8
    dec ecx
    jnz .aresta
    mov eax, 1
    ret
.fora:
    xor eax, eax
    ret

# Sobreposição opcional para inspecionar o contorno dos móveis.
desenhar_poligono:
    push rbp
    mov rbp, rsp
    push rbx
    push r12
    push r13
    push r14
    mov r13, rdi
    mov r12d, esi
    mov r14d, edx
.lado:
    movss xmm0, dword ptr [r13]
    cvttss2si edi, xmm0
    movss xmm0, dword ptr [r13 + 4]
    cvttss2si esi, xmm0
    movss xmm0, dword ptr [r13 + 8]
    cvttss2si edx, xmm0
    movss xmm0, dword ptr [r13 + 12]
    cvttss2si ecx, xmm0
    mov r8d, r14d
    call DrawLine
    add r13, 8
    dec r12d
    jnz .lado
    pop r14
    pop r13
    pop r12
    pop rbx
    pop rbp
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
    subss xmm0, dword ptr [rip + ancora_x]
    movss dword ptr [rsp + 40], xmm0
    movss xmm0, dword ptr [r12 + POS_Y]
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
