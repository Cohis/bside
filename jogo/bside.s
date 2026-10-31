.intel_syntax noprefix

# B-Side: Fase 1 em visão top-down 3/4. Toda a lógica está em Assembly x86-64.
# ABI System V (Linux); a Raylib cuida apenas de janela, entrada e desenho.
# As plantas, móveis e luzes ficam em fase1.s; a arte, em assets/tileset-bside.png.

.include "estruturas.inc"
.include "tileset.inc"

.equ POS_X, 0
.equ POS_Y, 4
.equ DIRECAO, 8
.equ ANDANDO, 12
.equ TEMPO, 16
.equ TECLA_CIMA, 20
.equ TECLA_BAIXO, 24
.equ TECLA_ESQUERDA, 28
.equ TECLA_DIREITA, 32

.equ LARGURA_TELA, 1280
.equ ALTURA_TELA, 720
.equ BLEND_ADITIVO, 1
.equ BLEND_MULTIPLICADO, 2
.equ FILTRO_TRILINEAR, 2
.equ TECLA_F11, 300
.equ TECLA_ENTER, 257
.equ TECLA_ALT_ESQ, 342
.equ TECLA_ALT_DIR, 346
.equ QUADRO_CAPTURA, 45

.section .rodata
titulo:         .asciz "B-Side | Fase 1"
caminho_icaro_final: .asciz "assets/icaro-andar-final.png"
caminho_icaro:  .asciz "assets/icaro-andar-rascunho.png"
caminho_tileset: .asciz "assets/tileset-bside.png"
caminho_luz:    .asciz "assets/luz.png"
caminho_vinheta: .asciz "assets/vinheta.png"
caminho_musica: .asciz "assets/musica-fundo.mp3"
erro_recursos:  .asciz "Nao foi possivel carregar as texturas. Execute a partir da raiz do repositorio."
erro_janela:    .asciz "Nao foi possivel abrir uma janela grafica."
controles:      .asciz "WASD mover    F11 tela cheia    ESC sair"
separador:      .asciz "/"
variavel_captura: .asciz "BSIDE_CAPTURE"
variavel_colisoes: .asciz "BSIDE_COLISOES"
variavel_ponto: .asciz "BSIDE_PONTO"
formato_ponto:  .asciz "%d %d %d"
caminho_captura: .asciz "captura.png"

.align 16
um:             .float 1.0
zero:           .float 0.0
meio:           .float 0.5
limite_delta:   .float 0.05
velocidade:     .float 56.0
diagonal:       .float 0.70710678
tempo_ciclo:    .float 0.8
dez:            .float 10.0
velocidade_fade: .float 4.0
c_255:          .float 255.0

mapa_l:         .float 384.0              # LARGURA_MAPA * TILE
mapa_a:         .float 528.0              # ALTURA_MAPA * TILE
altura_foco:    .float 18.0               # a câmera mira o tronco, não os pés

# Sprite: quadro 384x512, figura de 424 px e âncora (192,480), reduzidos
# para ~36 px de altura no mundo.
tamanho_celula: .float 384.0, 512.0
tamanho_sprite: .float 32.60, 43.47
ancora_x:       .float 16.302
ancora_y:       .float 40.755

# Caixa dos pés usada na colisão.
pe_lado:        .float 6.0
pe_cima:        .float 4.0
pe_baixo:       .float 1.0

# Recortes fixos.
recorte_luz:    .float 0.0, 0.0, 128.0, 128.0
recorte_vinheta: .float 0.0, 0.0, 320.0, 180.0
raio_luz_icaro: .float 60.0
cor_luz_icaro:  .long 0xff5a4a50          # ABGR: luz fraca que mantém Ícaro legível

# Constantes das oscilações.
os_chama_freq:  .float 8.0
os_chama_amp:   .float 0.1
os_chama_base:  .float 0.9
os_tv_f1:       .float 11.0
os_tv_f2:       .float 2.3
os_tv_amp:      .float 0.3
os_tv_base:     .float 0.7
os_falha_f1:    .float 1.3
os_falha_f2:    .float 17.0
os_falha_limiar: .float 0.55
os_falha_apagada: .float 0.12
os_neon_f1:     .float 0.7
os_neon_f2:     .float 29.0
os_neon_limiar: .float 0.8
os_neon_fraco:  .float 0.35

# Disco girando e notas subindo.
disco_rotacao:  .float 3.5
pi:             .float 3.14159265
disco_rx:       .float 5.0
disco_ry:       .float 2.6
disco_cx:       .float 8.0
disco_cy:       .float 5.0
notas_ritmo:    .float 0.45
um_terco:       .float 0.33333333
notas_subida:   .float 22.0
notas_balanco:  .float 4.0
dois_pi:        .float 6.2831853
notas_fase:     .float 2.1
volume_musica:  .float 0.5

.section .data
.align 16
# x, y (pés, px do mundo), direção, andando, tempo, cima, baixo, esquerda, direita
icaro: .float 72.0, 444.0
       .long DIR_SUL, 0
       .float 0.0
       .long 87, 83, 65, 68
cor_atual: .long -1

.section .bss
.align 16
textura_icaro:   .skip 20
textura_tileset: .skip 20
textura_luz:     .skip 20
textura_vinheta: .skip 20
.align 16
musica:          .skip 56                 # Music (AudioStream 32, frameCount, looping, ctxType, ctxData)
musica_ok:       .skip 4
mapa_luz:        .skip 48                 # RenderTexture2D (44 bytes)
tabela_tile:     .skip 1024               # por caractere: índice, classe, variantes, válido
andar_ptr:       .skip 8
fade_transicao:  .skip 8
comodo_nome:     .skip 8
andar_indice:    .skip 4
delta_quadro:    .skip 4
tempo:           .skip 4
capturar:        .skip 4
mostrar_colisoes: .skip 4
contador_quadros: .skip 4
camera_x:        .skip 4
camera_y:        .skip 4
desloc_x:        .skip 4
desloc_y:        .skip 4
fade_alfa:       .skip 4
fade_fase:       .skip 4                  # 0 parado, 1 escurecendo, 2 clareando
icaro_desenhado: .skip 4
ponto_lido:      .skip 12
# Tamanho da janela e o que depende dele (recalculado quando ela muda).
largura_tela:    .skip 4
altura_tela:     .skip 4
altura_hud:      .skip 4
fonte_hud:       .skip 4
zoom:            .skip 4                  # inteiro, guardado como float
vista_l:         .skip 4                  # área visível em px do mundo
vista_a:         .skip 4
metade_vista_l:  .skip 4
metade_vista_a:  .skip 4
.align 16
recorte_tela:    .skip 16                 # mapa de luz, invertido em y
destino_tela:    .skip 16
destino_vinheta: .skip 16
rec_origem:      .skip 16
rec_destino:     .skip 16
vec_pivo:        .skip 8
rotacao_atual:   .skip 4

.section .text
.extern InitWindow
.extern CloseWindow
.extern SetTargetFPS
.extern WindowShouldClose
.extern GetFrameTime
.extern GetTime
.extern IsKeyDown
.extern IsKeyPressed
.extern ToggleBorderlessWindowed
.extern GetScreenWidth
.extern GetScreenHeight
.extern BeginDrawing
.extern EndDrawing
.extern ClearBackground
.extern LoadTexture
.extern FileExists
.extern UnloadTexture
.extern GenTextureMipmaps
.extern SetTextureFilter
.extern LoadRenderTexture
.extern UnloadRenderTexture
.extern BeginTextureMode
.extern EndTextureMode
.extern BeginBlendMode
.extern EndBlendMode
.extern DrawTexturePro
.extern DrawRectangle
.extern DrawRectangleLines
.extern DrawText
.extern MeasureText
.extern rlPushMatrix
.extern rlPopMatrix
.extern rlTranslatef
.extern rlScalef
.extern IsWindowReady
.extern InitAudioDevice
.extern CloseAudioDevice
.extern LoadMusicStream
.extern UnloadMusicStream
.extern PlayMusicStream
.extern UpdateMusicStream
.extern SetMusicVolume
.extern TakeScreenshot
.extern rlDrawRenderBatchActive
.extern getenv
.extern puts
.extern sscanf
.extern sinf
.extern cosf
.extern andares
.extern tipos_tile
.extern n_tipos_tile
.global main
.type main, @function

main:
    push rbp
    mov rbp, rsp
    sub rsp, 16

    mov edi, LARGURA_TELA
    mov esi, ALTURA_TELA
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
    lea rdi, [rip + textura_tileset]
    lea rsi, [rip + caminho_tileset]
    call LoadTexture
    lea rdi, [rip + textura_luz]
    lea rsi, [rip + caminho_luz]
    call LoadTexture
    lea rdi, [rip + textura_vinheta]
    lea rsi, [rip + caminho_vinheta]
    call LoadTexture

    cmp dword ptr [rip + textura_icaro], 0
    je .erro
    cmp dword ptr [rip + textura_tileset], 0
    je .erro
    cmp dword ptr [rip + textura_luz], 0
    je .erro
    cmp dword ptr [rip + textura_vinheta], 0
    je .erro

    call iniciar_musica

    # A sprite é reduzida ~5x; mipmaps evitam que ela cintile ao andar.
    lea rdi, [rip + textura_icaro]
    call GenTextureMipmaps
    sub rsp, 32
    lea rsi, [rip + textura_icaro]
    mov rax, qword ptr [rsi]
    mov qword ptr [rsp], rax
    mov rax, qword ptr [rsi + 8]
    mov qword ptr [rsp + 8], rax
    mov eax, dword ptr [rsi + 16]
    mov dword ptr [rsp + 16], eax
    mov edi, FILTRO_TRILINEAR
    call SetTextureFilter
    add rsp, 32

    call preparar_tiles
    lea rax, [rip + andares]
    mov rdi, qword ptr [rax]
    call ordenar_objetos
    lea rax, [rip + andares]
    mov rdi, qword ptr [rax + 8]
    call ordenar_objetos

    mov dword ptr [rip + andar_indice], 0
    call ler_ponto_inicial
    mov eax, dword ptr [rip + andar_indice]
    lea rdx, [rip + andares]
    mov rdx, qword ptr [rdx + rax*8]
    mov qword ptr [rip + andar_ptr], rdx

    # A fase abre saindo do preto.
    mov dword ptr [rip + fade_fase], 2
    movss xmm0, dword ptr [rip + um]
    movss dword ptr [rip + fade_alfa], xmm0

.quadro:
    call WindowShouldClose
    test al, al
    jne .fechar

    call atualizar_musica

    call GetFrameTime
    minss xmm0, dword ptr [rip + limite_delta]
    movss dword ptr [rip + delta_quadro], xmm0
    call GetTime
    cvtsd2ss xmm0, xmm0
    movss dword ptr [rip + tempo], xmm0
    call alternar_tela_cheia
    call atualizar_tela

    cmp dword ptr [rip + fade_fase], 0
    jne .sem_movimento
    lea rdi, [rip + icaro]
    call atualizar_personagem
    call verificar_transicoes
    jmp .movimento_pronto
.sem_movimento:
    mov dword ptr [rip + icaro + ANDANDO], 0
    mov dword ptr [rip + icaro + TEMPO], 0
.movimento_pronto:
    call atualizar_fade
    call atualizar_camera
    call atualizar_comodo
    call desenhar_luzes

    # O mundo é desenhado direto na resolução da janela, com zoom inteiro,
    # para cada pixel da arte virar um quadrado exato de pixels da tela.
    call BeginDrawing
    mov edi, 0xff0c080a
    call ClearBackground

    # Cena: piso e paredes, decalques, móveis ordenados com Ícaro e teto.
    call aplicar_camera
    call desenhar_tiles
    mov edi, CAM_CHAO
    call desenhar_camada
    call desenhar_ordenados
    mov edi, CAM_TETO
    call desenhar_camada
    call rlPopMatrix

    # A luz multiplica a cena; o que fica fora dela afunda no escuro.
    mov edi, BLEND_MULTIPLICADO
    call BeginBlendMode
    lea rsi, [rip + recorte_tela]
    lea rdx, [rip + destino_tela]
    call definir_recortes
    lea rdi, [rip + mapa_luz + 4]
    mov esi, -1
    call desenhar_recorte
    call EndBlendMode

    # Brilhos próprios (neon, TV, janelas) ficam por cima da luz.
    call aplicar_camera
    mov edi, CAM_EMISSIVA
    call desenhar_camada
    cmp dword ptr [rip + mostrar_colisoes], 0
    je .sem_colisoes
    call desenhar_colisoes
.sem_colisoes:
    call rlPopMatrix

    mov edi, BLEND_MULTIPLICADO
    call BeginBlendMode
    lea rsi, [rip + recorte_vinheta]
    lea rdx, [rip + destino_vinheta]
    call definir_recortes
    lea rdi, [rip + textura_vinheta]
    mov esi, -1
    call desenhar_recorte
    call EndBlendMode

    call desenhar_fade
    call desenhar_hud

    inc dword ptr [rip + contador_quadros]
    cmp dword ptr [rip + capturar], 0
    je .fim_desenho
    cmp dword ptr [rip + contador_quadros], QUADRO_CAPTURA
    jne .fim_desenho
    call rlDrawRenderBatchActive
    lea rdi, [rip + caminho_captura]
    call TakeScreenshot
    call EndDrawing
    jmp .fechar
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
    lea rdi, [rip + mapa_luz]
    call liberar_alvo
    call encerrar_musica
.descarregar:
    cmp dword ptr [rip + textura_icaro], 0
    je .pular_icaro
    lea rdi, [rip + textura_icaro]
    call descarregar_textura
.pular_icaro:
    cmp dword ptr [rip + textura_tileset], 0
    je .pular_tileset
    lea rdi, [rip + textura_tileset]
    call descarregar_textura
.pular_tileset:
    cmp dword ptr [rip + textura_luz], 0
    je .pular_luz
    lea rdi, [rip + textura_luz]
    call descarregar_textura
.pular_luz:
    cmp dword ptr [rip + textura_vinheta], 0
    je .pular_vinheta
    lea rdi, [rip + textura_vinheta]
    call descarregar_textura
.pular_vinheta:
    call CloseWindow
    mov eax, dword ptr [rbp - 4]
    leave
    ret

# Abre o áudio e toca a música de fundo em loop. Sem dispositivo de áudio, o jogo segue mudo.
iniciar_musica:
    sub rsp, 8
    mov dword ptr [rip + musica_ok], 0
    call InitAudioDevice
    lea rdi, [rip + musica]
    lea rsi, [rip + caminho_musica]
    call LoadMusicStream
    cmp qword ptr [rip + musica + 48], 0
    je .musica_fim
    mov byte ptr [rip + musica + 36], 1
    mov dword ptr [rip + musica_ok], 1
    movss xmm0, dword ptr [rip + volume_musica]
    lea r10, [rip + SetMusicVolume]
    call chamar_musica
    lea r10, [rip + PlayMusicStream]
    call chamar_musica
.musica_fim:
    add rsp, 8
    ret

# r10 = função da Raylib que recebe a Music (56 bytes) por valor, na pilha.
chamar_musica:
    sub rsp, 72
    lea rax, [rip + musica]
    mov ecx, 7
.copiar_musica:
    mov rdx, qword ptr [rax + rcx*8 - 8]
    mov qword ptr [rsp + rcx*8 - 8], rdx
    loop .copiar_musica
    call r10
    add rsp, 72
    ret

atualizar_musica:
    cmp dword ptr [rip + musica_ok], 0
    je .atualizar_fim
    sub rsp, 8
    lea r10, [rip + UpdateMusicStream]
    call chamar_musica
    add rsp, 8
.atualizar_fim:
    ret

encerrar_musica:
    cmp dword ptr [rip + musica_ok], 0
    je .encerrar_fim
    sub rsp, 8
    lea r10, [rip + UnloadMusicStream]
    call chamar_musica
    call CloseAudioDevice
    add rsp, 8
.encerrar_fim:
    ret

# rdi = RenderTexture2D. Passa a estrutura (44 bytes) por valor, na pilha.
iniciar_alvo:
    sub rsp, 56
    mov ecx, 6
.copiar_alvo:
    mov rax, qword ptr [rdi + rcx*8 - 8]
    mov qword ptr [rsp + rcx*8 - 8], rax
    loop .copiar_alvo
    call BeginTextureMode
    add rsp, 56
    ret

# rdi = RenderTexture2D; não faz nada se ela não chegou a ser criada.
liberar_alvo:
    cmp dword ptr [rdi], 0
    je .alvo_vazio
    sub rsp, 56
    mov ecx, 6
.copiar_liberacao:
    mov rax, qword ptr [rdi + rcx*8 - 8]
    mov qword ptr [rsp + rcx*8 - 8], rax
    loop .copiar_liberacao
    call UnloadRenderTexture
    add rsp, 56
.alvo_vazio:
    ret

# F11 ou Alt+Enter alternam entre janela e tela cheia sem borda.
alternar_tela_cheia:
    sub rsp, 8
    mov edi, TECLA_F11
    call IsKeyPressed
    test al, al
    jnz .alternar
    mov edi, TECLA_ENTER
    call IsKeyPressed
    test al, al
    jz .fim_alternar
    mov edi, TECLA_ALT_ESQ
    call IsKeyDown
    test al, al
    jnz .alternar
    mov edi, TECLA_ALT_DIR
    call IsKeyDown
    test al, al
    jz .fim_alternar
.alternar:
    call ToggleBorderlessWindowed
.fim_alternar:
    add rsp, 8
    ret

# Lê o tamanho da janela. Quando ele muda (início ou F11), recalcula o zoom
# inteiro (altura / 240), o HUD, a área visível e recria o mapa de luz.
atualizar_tela:
    push rbx
    push r12
    sub rsp, 8
    call GetScreenWidth
    mov ebx, eax
    call GetScreenHeight
    mov r12d, eax
    cmp ebx, dword ptr [rip + largura_tela]
    jne .tela_mudou
    cmp r12d, dword ptr [rip + altura_tela]
    je .fim_tela
.tela_mudou:
    mov dword ptr [rip + largura_tela], ebx
    mov dword ptr [rip + altura_tela], r12d
    mov eax, r12d
    xor edx, edx
    mov ecx, 240
    div ecx
    cmp eax, 1
    jge .zoom_pronto
    mov eax, 1
.zoom_pronto:
    cvtsi2ss xmm0, eax
    movss dword ptr [rip + zoom], xmm0
    # A fonte padrão tem 10 px; múltiplos de 10 mantêm as letras nítidas.
    mov eax, r12d
    xor edx, edx
    mov ecx, 360
    div ecx
    imul eax, eax, 10
    cmp eax, 20
    jge .fonte_pronta
    mov eax, 20
.fonte_pronta:
    mov dword ptr [rip + fonte_hud], eax
    imul eax, eax, 9
    xor edx, edx
    mov ecx, 5
    div ecx
    mov dword ptr [rip + altura_hud], eax

    cvtsi2ss xmm0, ebx
    divss xmm0, dword ptr [rip + zoom]
    movss dword ptr [rip + vista_l], xmm0
    mulss xmm0, dword ptr [rip + meio]
    movss dword ptr [rip + metade_vista_l], xmm0
    mov eax, r12d
    sub eax, dword ptr [rip + altura_hud]
    cvtsi2ss xmm0, eax
    divss xmm0, dword ptr [rip + zoom]
    movss dword ptr [rip + vista_a], xmm0
    mulss xmm0, dword ptr [rip + meio]
    movss dword ptr [rip + metade_vista_a], xmm0

    cvtsi2ss xmm0, ebx
    cvtsi2ss xmm1, r12d
    xorps xmm2, xmm2
    subss xmm2, xmm1
    mov qword ptr [rip + recorte_tela], 0
    movss dword ptr [rip + recorte_tela + 8], xmm0
    movss dword ptr [rip + recorte_tela + 12], xmm2
    mov qword ptr [rip + destino_tela], 0
    movss dword ptr [rip + destino_tela + 8], xmm0
    movss dword ptr [rip + destino_tela + 12], xmm1
    mov eax, r12d
    sub eax, dword ptr [rip + altura_hud]
    cvtsi2ss xmm1, eax
    mov qword ptr [rip + destino_vinheta], 0
    movss dword ptr [rip + destino_vinheta + 8], xmm0
    movss dword ptr [rip + destino_vinheta + 12], xmm1

    # Mapa de luz do tamanho da janela: ambiente e luzes, depois multiplica a cena.
    lea rdi, [rip + mapa_luz]
    call liberar_alvo
    lea rdi, [rip + mapa_luz]
    mov esi, ebx
    mov edx, r12d
    call LoadRenderTexture
.fim_tela:
    add rsp, 8
    pop r12
    pop rbx
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

# rsi = recorte de origem, rdx = destino (4 floats cada). Zera pivô e rotação.
definir_recortes:
    movups xmm0, xmmword ptr [rsi]
    movaps xmmword ptr [rip + rec_origem], xmm0
    movups xmm0, xmmword ptr [rdx]
    movaps xmmword ptr [rip + rec_destino], xmm0
    mov qword ptr [rip + vec_pivo], 0
    mov dword ptr [rip + rotacao_atual], 0
    ret

# rdi = Texture2D, esi = cor. Usa rec_origem, rec_destino, vec_pivo e rotacao_atual.
# O Texture2D (20 bytes) vai pela pilha; a cor, último argumento, em edi.
desenhar_recorte:
    sub rsp, 40
    mov rax, qword ptr [rdi]
    mov qword ptr [rsp], rax
    mov rax, qword ptr [rdi + 8]
    mov qword ptr [rsp + 8], rax
    mov eax, dword ptr [rdi + 16]
    mov dword ptr [rsp + 16], eax
    movq xmm0, qword ptr [rip + rec_origem]
    movq xmm1, qword ptr [rip + rec_origem + 8]
    movq xmm2, qword ptr [rip + rec_destino]
    movq xmm3, qword ptr [rip + rec_destino + 8]
    movq xmm4, qword ptr [rip + vec_pivo]
    movss xmm5, dword ptr [rip + rotacao_atual]
    mov edi, esi
    call DrawTexturePro
    add rsp, 40
    ret

# Recorte do tileset sem escala. edi,esi = origem; edx,ecx = tamanho;
# r8d,r9d = destino em px do mundo. A cor vem de cor_atual.
desenhar_atlas:
    cvtsi2ss xmm0, edi
    movss dword ptr [rip + rec_origem], xmm0
    cvtsi2ss xmm0, esi
    movss dword ptr [rip + rec_origem + 4], xmm0
    cvtsi2ss xmm0, edx
    movss dword ptr [rip + rec_origem + 8], xmm0
    movss dword ptr [rip + rec_destino + 8], xmm0
    cvtsi2ss xmm0, ecx
    movss dword ptr [rip + rec_origem + 12], xmm0
    movss dword ptr [rip + rec_destino + 12], xmm0
    cvtsi2ss xmm0, r8d
    movss dword ptr [rip + rec_destino], xmm0
    cvtsi2ss xmm0, r9d
    movss dword ptr [rip + rec_destino + 4], xmm0
    mov qword ptr [rip + vec_pivo], 0
    mov dword ptr [rip + rotacao_atual], 0
    lea rdi, [rip + textura_tileset]
    mov esi, dword ptr [rip + cor_atual]
    jmp desenhar_recorte

# edi = índice do tile no atlas, esi = tx, edx = ty.
desenhar_tile:
    mov r8d, esi
    shl r8d, 4
    mov r9d, edx
    shl r9d, 4
    mov esi, edi
    shr esi, 5
    shl esi, 4
    and edi, 31
    shl edi, 4
    mov edx, TILE
    mov ecx, TILE
    jmp desenhar_atlas

# Expande a legenda de fase1.s numa tabela indexada pelo caractere:
# byte 0 = índice no atlas, 1 = classe, 2 = variantes, 3 = 1 (válido).
preparar_tiles:
    lea rsi, [rip + tipos_tile]
    mov ecx, dword ptr [rip + n_tipos_tile]
    lea r9, [rip + tabela_tile]
.proximo_tipo:
    test ecx, ecx
    jz .fim_tipos
    mov eax, dword ptr [rsi + TT_CHAR]
    and eax, 0xff
    mov edx, dword ptr [rsi + TT_INDICE]
    and edx, 0xff
    mov r8d, dword ptr [rsi + TT_CLASSE]
    shl r8d, 8
    or edx, r8d
    mov r8d, dword ptr [rsi + TT_VARIANTES]
    shl r8d, 16
    or edx, r8d
    or edx, 0x01000000
    mov dword ptr [r9 + rax*4], edx
    add rsi, TT_TAM
    dec ecx
    jmp .proximo_tipo
.fim_tipos:
    ret

# rdi = descritor do andar. Ordena os objetos pela base (inserção estável),
# para que o desenho em profundidade só precise percorrer a lista.
ordenar_objetos:
    mov r8, qword ptr [rdi + AND_OBJETOS]
    mov r9, qword ptr [rdi + AND_N_OBJETOS]
    mov ecx, 1
.ordem_externa:
    cmp rcx, r9
    jge .ordem_fim
    mov rax, rcx
    shl rax, 6
    lea r10, [r8 + rax]
    movdqu xmm0, xmmword ptr [r10]
    movdqu xmm1, xmmword ptr [r10 + 16]
    movdqu xmm2, xmmword ptr [r10 + 32]
    movdqu xmm3, xmmword ptr [r10 + 48]
    mov r11d, dword ptr [r10 + OBJ_BASE]
    mov rdx, rcx
.ordem_interna:
    test rdx, rdx
    jz .ordem_inserir
    lea rax, [rdx - 1]
    shl rax, 6
    lea r10, [r8 + rax]
    cmp dword ptr [r10 + OBJ_BASE], r11d
    jle .ordem_inserir
    movdqu xmm4, xmmword ptr [r10]
    movdqu xmmword ptr [r10 + 64], xmm4
    movdqu xmm4, xmmword ptr [r10 + 16]
    movdqu xmmword ptr [r10 + 80], xmm4
    movdqu xmm4, xmmword ptr [r10 + 32]
    movdqu xmmword ptr [r10 + 96], xmm4
    movdqu xmm4, xmmword ptr [r10 + 48]
    movdqu xmmword ptr [r10 + 112], xmm4
    dec rdx
    jmp .ordem_interna
.ordem_inserir:
    mov rax, rdx
    shl rax, 6
    lea r10, [r8 + rax]
    movdqu xmmword ptr [r10], xmm0
    movdqu xmmword ptr [r10 + 16], xmm1
    movdqu xmmword ptr [r10 + 32], xmm2
    movdqu xmmword ptr [r10 + 48], xmm3
    inc rcx
    jmp .ordem_externa
.ordem_fim:
    ret

# BSIDE_PONTO="andar x y" (tiles) escolhe onde Ícaro começa; útil para capturas.
ler_ponto_inicial:
    sub rsp, 8
    lea rdi, [rip + variavel_ponto]
    call getenv
    test rax, rax
    jz .fim_ponto
    mov rdi, rax
    lea rsi, [rip + formato_ponto]
    lea rdx, [rip + ponto_lido]
    lea rcx, [rip + ponto_lido + 4]
    lea r8, [rip + ponto_lido + 8]
    xor eax, eax
    call sscanf
    cmp eax, 3
    jne .fim_ponto
    mov eax, dword ptr [rip + ponto_lido]
    and eax, 1
    mov dword ptr [rip + andar_indice], eax
    mov eax, dword ptr [rip + ponto_lido + 4]
    shl eax, 4
    add eax, 8
    cvtsi2ss xmm0, eax
    movss dword ptr [rip + icaro + POS_X], xmm0
    mov eax, dword ptr [rip + ponto_lido + 8]
    shl eax, 4
    add eax, 12
    cvtsi2ss xmm0, eax
    movss dword ptr [rip + icaro + POS_Y], xmm0
.fim_ponto:
    add rsp, 8
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
    movzx eax, al
    sub ebx, eax
    mov edi, dword ptr [r12 + TECLA_DIREITA]
    call IsKeyDown
    movzx eax, al
    add ebx, eax
    mov edi, dword ptr [r12 + TECLA_CIMA]
    call IsKeyDown
    movzx eax, al
    sub r13d, eax
    mov edi, dword ptr [r12 + TECLA_BAIXO]
    call IsKeyDown
    movzx eax, al
    add r13d, eax

    mov dword ptr [r12 + ANDANDO], 0
    mov eax, ebx
    or eax, r13d
    jz .fim_atualizacao

    # Na vista 3/4 as teclas já apontam para os eixos do mapa.
    movss xmm2, dword ptr [rip + delta_quadro]
    mulss xmm2, dword ptr [rip + velocidade]
    test ebx, ebx
    jz .normalizacao_pronta
    test r13d, r13d
    jz .normalizacao_pronta
    mulss xmm2, dword ptr [rip + diagonal]
.normalizacao_pronta:
    cvtsi2ss xmm0, ebx
    mulss xmm0, xmm2
    movss dword ptr [rsp], xmm0
    cvtsi2ss xmm0, r13d
    mulss xmm0, xmm2
    movss dword ptr [rsp + 4], xmm0

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

# xmm0=x, xmm1=y dos pés; eax=1 se os quatro cantos da caixa dos pés estão livres.
pode_andar:
    sub rsp, 24
    movss dword ptr [rsp], xmm0
    movss dword ptr [rsp + 4], xmm1
    subss xmm0, dword ptr [rip + pe_lado]
    subss xmm1, dword ptr [rip + pe_cima]
    call ponto_solido
    test eax, eax
    jnz .bloqueado
    movss xmm0, dword ptr [rsp]
    addss xmm0, dword ptr [rip + pe_lado]
    movss xmm1, dword ptr [rsp + 4]
    subss xmm1, dword ptr [rip + pe_cima]
    call ponto_solido
    test eax, eax
    jnz .bloqueado
    movss xmm0, dword ptr [rsp]
    subss xmm0, dword ptr [rip + pe_lado]
    movss xmm1, dword ptr [rsp + 4]
    addss xmm1, dword ptr [rip + pe_baixo]
    call ponto_solido
    test eax, eax
    jnz .bloqueado
    movss xmm0, dword ptr [rsp]
    addss xmm0, dword ptr [rip + pe_lado]
    movss xmm1, dword ptr [rsp + 4]
    addss xmm1, dword ptr [rip + pe_baixo]
    call ponto_solido
    test eax, eax
    jnz .bloqueado
    mov eax, 1
    add rsp, 24
    ret
.bloqueado:
    xor eax, eax
    add rsp, 24
    ret

# xmm0=x, xmm1=y em px do mundo; eax=1 se o ponto cai em parede ou em
# retângulo de colisão de algum móvel do andar atual.
ponto_solido:
    push rbx
    push r12
    push r13
    ucomiss xmm0, dword ptr [rip + zero]
    jb .solido
    ucomiss xmm1, dword ptr [rip + zero]
    jb .solido
    cvttss2si r12d, xmm0
    cvttss2si r13d, xmm1
    mov edi, r12d
    sar edi, 4
    mov esi, r13d
    sar esi, 4
    call classe_em
    cmp eax, CL_PISO
    jne .solido
    mov rax, qword ptr [rip + andar_ptr]
    mov rbx, qword ptr [rax + AND_OBJETOS]
    mov rcx, qword ptr [rax + AND_N_OBJETOS]
.colisao_objeto:
    test rcx, rcx
    jz .livre
    mov edx, dword ptr [rbx + OBJ_CL]
    test edx, edx
    jz .proximo_objeto
    mov eax, dword ptr [rbx + OBJ_CX]
    cmp r12d, eax
    jl .proximo_objeto
    add eax, edx
    cmp r12d, eax
    jge .proximo_objeto
    mov eax, dword ptr [rbx + OBJ_CY]
    cmp r13d, eax
    jl .proximo_objeto
    add eax, dword ptr [rbx + OBJ_CA]
    cmp r13d, eax
    jge .proximo_objeto
    jmp .solido
.proximo_objeto:
    add rbx, OBJ_TAM
    dec rcx
    jmp .colisao_objeto
.livre:
    xor eax, eax
    jmp .fim_solido
.solido:
    mov eax, 1
.fim_solido:
    pop r13
    pop r12
    pop rbx
    ret

# edi=tx, esi=ty -> eax = entrada de tabela_tile (0 fora do mapa ou caractere sem legenda).
info_tile:
    xor eax, eax
    cmp edi, 0
    jl .fim_info
    cmp edi, LARGURA_MAPA
    jge .fim_info
    cmp esi, 0
    jl .fim_info
    cmp esi, ALTURA_MAPA
    jge .fim_info
    imul esi, esi, LARGURA_MAPA
    add esi, edi
    mov rdx, qword ptr [rip + andar_ptr]
    mov rdx, qword ptr [rdx + AND_MAPA]
    movzx ecx, byte ptr [rdx + rsi]
    lea rdx, [rip + tabela_tile]
    mov eax, dword ptr [rdx + rcx*4]
.fim_info:
    ret

# edi=tx, esi=ty -> eax = classe do tile, ou 0xff fora do mapa.
classe_em:
    call info_tile
    test eax, eax
    jz .classe_indefinida
    shr eax, 8
    and eax, 0xff
    ret
.classe_indefinida:
    mov eax, 0xff
    ret

# edi=tx, esi=ty -> eax = caractere da planta (0 fora do mapa).
caractere_em:
    xor eax, eax
    cmp edi, 0
    jl .fim_caractere
    cmp edi, LARGURA_MAPA
    jge .fim_caractere
    cmp esi, 0
    jl .fim_caractere
    cmp esi, ALTURA_MAPA
    jge .fim_caractere
    imul esi, esi, LARGURA_MAPA
    add esi, edi
    mov rdx, qword ptr [rip + andar_ptr]
    mov rdx, qword ptr [rdx + AND_MAPA]
    movzx eax, byte ptr [rdx + rsi]
.fim_caractere:
    ret

# edi=tx, esi=ty -> eax=1 se o vizinho fecha o topo da parede (parede ou fora do mapa).
parede_fechada:
    call classe_em
    cmp eax, CL_TOPO
    je .fechada
    cmp eax, CL_COLUNA
    je .fechada
    cmp eax, 0xff
    je .fechada
    xor eax, eax
    ret
.fechada:
    mov eax, 1
    ret

# Pés dentro de um degrau-gatilho iniciam a troca de andar.
verificar_transicoes:
    mov rax, qword ptr [rip + andar_ptr]
    mov rsi, qword ptr [rax + AND_TRANSICOES]
    mov rcx, qword ptr [rax + AND_N_TRANSICOES]
    cvttss2si r8d, dword ptr [rip + icaro + POS_X]
    cvttss2si r9d, dword ptr [rip + icaro + POS_Y]
.proxima_transicao:
    test rcx, rcx
    jz .fim_transicoes
    mov eax, dword ptr [rsi + TR_X]
    cmp r8d, eax
    jl .pular_transicao
    add eax, dword ptr [rsi + TR_L]
    cmp r8d, eax
    jge .pular_transicao
    mov eax, dword ptr [rsi + TR_Y]
    cmp r9d, eax
    jl .pular_transicao
    add eax, dword ptr [rsi + TR_A]
    cmp r9d, eax
    jge .pular_transicao
    mov qword ptr [rip + fade_transicao], rsi
    mov dword ptr [rip + fade_fase], 1
    ret
.pular_transicao:
    add rsi, TR_TAM
    dec rcx
    jmp .proxima_transicao
.fim_transicoes:
    ret

# Escurece, troca de andar no preto total e clareia de novo.
atualizar_fade:
    movss xmm1, dword ptr [rip + delta_quadro]
    mulss xmm1, dword ptr [rip + velocidade_fade]
    movss xmm0, dword ptr [rip + fade_alfa]
    mov eax, dword ptr [rip + fade_fase]
    cmp eax, 1
    je .escurecer
    cmp eax, 2
    je .clarear
    ret
.escurecer:
    addss xmm0, xmm1
    ucomiss xmm0, dword ptr [rip + um]
    jb .guardar_fade
    mov rsi, qword ptr [rip + fade_transicao]
    mov eax, dword ptr [rsi + TR_DESTINO]
    mov dword ptr [rip + andar_indice], eax
    lea rdx, [rip + andares]
    mov rdx, qword ptr [rdx + rax*8]
    mov qword ptr [rip + andar_ptr], rdx
    cvtsi2ss xmm0, dword ptr [rsi + TR_CHEGADA_X]
    movss dword ptr [rip + icaro + POS_X], xmm0
    cvtsi2ss xmm0, dword ptr [rsi + TR_CHEGADA_Y]
    movss dword ptr [rip + icaro + POS_Y], xmm0
    mov eax, dword ptr [rsi + TR_DIRECAO]
    mov dword ptr [rip + icaro + DIRECAO], eax
    mov qword ptr [rip + comodo_nome], 0
    mov dword ptr [rip + fade_fase], 2
    movss xmm0, dword ptr [rip + um]
    jmp .guardar_fade
.clarear:
    subss xmm0, xmm1
    ucomiss xmm0, dword ptr [rip + zero]
    ja .guardar_fade
    xorps xmm0, xmm0
    mov dword ptr [rip + fade_fase], 0
.guardar_fade:
    movss dword ptr [rip + fade_alfa], xmm0
    ret

# Câmera presa às bordas do andar; num eixo menor que a tela, o andar fica centralizado.
# desloc_x/desloc_y = translação já em pixels inteiros de tela.
atualizar_camera:
    movss xmm0, dword ptr [rip + mapa_l]
    ucomiss xmm0, dword ptr [rip + vista_l]
    ja .camera_x_rola
    subss xmm0, dword ptr [rip + vista_l]
    mulss xmm0, dword ptr [rip + meio]
    jmp .camera_x_pronta
.camera_x_rola:
    movss xmm0, dword ptr [rip + icaro + POS_X]
    subss xmm0, dword ptr [rip + metade_vista_l]
    maxss xmm0, dword ptr [rip + zero]
    movss xmm1, dword ptr [rip + mapa_l]
    subss xmm1, dword ptr [rip + vista_l]
    minss xmm0, xmm1
.camera_x_pronta:
    movss dword ptr [rip + camera_x], xmm0
    mulss xmm0, dword ptr [rip + zoom]
    cvtss2si eax, xmm0
    neg eax
    cvtsi2ss xmm0, eax
    movss dword ptr [rip + desloc_x], xmm0

    movss xmm0, dword ptr [rip + mapa_a]
    ucomiss xmm0, dword ptr [rip + vista_a]
    ja .camera_y_rola
    subss xmm0, dword ptr [rip + vista_a]
    mulss xmm0, dword ptr [rip + meio]
    jmp .camera_y_pronta
.camera_y_rola:
    movss xmm0, dword ptr [rip + icaro + POS_Y]
    subss xmm0, dword ptr [rip + altura_foco]
    subss xmm0, dword ptr [rip + metade_vista_a]
    maxss xmm0, dword ptr [rip + zero]
    movss xmm1, dword ptr [rip + mapa_a]
    subss xmm1, dword ptr [rip + vista_a]
    minss xmm0, xmm1
.camera_y_pronta:
    movss dword ptr [rip + camera_y], xmm0
    mulss xmm0, dword ptr [rip + zoom]
    cvtss2si eax, xmm0
    neg eax
    cvtsi2ss xmm0, eax
    movss dword ptr [rip + desloc_y], xmm0
    ret

# O nome do cômodo sob os pés de Ícaro vai para o HUD.
atualizar_comodo:
    cvttss2si r8d, dword ptr [rip + icaro + POS_X]
    sar r8d, 4
    cvttss2si r9d, dword ptr [rip + icaro + POS_Y]
    sar r9d, 4
    mov rax, qword ptr [rip + andar_ptr]
    mov rsi, qword ptr [rax + AND_COMODOS]
    mov rcx, qword ptr [rax + AND_N_COMODOS]
.proximo_comodo:
    test rcx, rcx
    jz .fim_comodo
    cmp r8d, dword ptr [rsi + COM_X0]
    jl .pular_comodo
    cmp r8d, dword ptr [rsi + COM_X1]
    jg .pular_comodo
    cmp r9d, dword ptr [rsi + COM_Y0]
    jl .pular_comodo
    cmp r9d, dword ptr [rsi + COM_Y1]
    jg .pular_comodo
    mov rax, qword ptr [rsi + COM_NOME]
    mov qword ptr [rip + comodo_nome], rax
    ret
.pular_comodo:
    add rsi, COM_TAM
    dec rcx
    jmp .proximo_comodo
.fim_comodo:
    ret

# Empilha a matriz da câmera: translação inteira em tela e zoom inteiro.
aplicar_camera:
    sub rsp, 8
    call rlPushMatrix
    movss xmm0, dword ptr [rip + desloc_x]
    movss xmm1, dword ptr [rip + desloc_y]
    xorps xmm2, xmm2
    call rlTranslatef
    movss xmm0, dword ptr [rip + zoom]
    movss xmm1, xmm0
    movss xmm2, dword ptr [rip + um]
    call rlScalef
    add rsp, 8
    ret

# edi = tipo de oscilação, xmm0 = semente (posição x). xmm0 <- fator de brilho.
oscilacao:
    push rbx
    sub rsp, 32
    mov ebx, edi
    movss dword ptr [rsp], xmm0
    cmp ebx, OS_CHAMA
    je .oscilar_chama
    cmp ebx, OS_TV
    je .oscilar_tv
    cmp ebx, OS_FALHA
    je .oscilar_falha
    cmp ebx, OS_NEON
    je .oscilar_neon
    movss xmm0, dword ptr [rip + um]
    jmp .fim_oscilacao
.oscilar_chama:
    movss xmm0, dword ptr [rip + tempo]
    mulss xmm0, dword ptr [rip + os_chama_freq]
    addss xmm0, dword ptr [rsp]
    call sinf
    mulss xmm0, dword ptr [rip + os_chama_amp]
    addss xmm0, dword ptr [rip + os_chama_base]
    jmp .fim_oscilacao
.oscilar_tv:
    movss xmm0, dword ptr [rip + tempo]
    mulss xmm0, dword ptr [rip + os_tv_f1]
    call sinf
    movss dword ptr [rsp + 4], xmm0
    movss xmm0, dword ptr [rip + tempo]
    mulss xmm0, dword ptr [rip + os_tv_f2]
    call sinf
    mulss xmm0, dword ptr [rsp + 4]
    mulss xmm0, dword ptr [rip + os_tv_amp]
    addss xmm0, dword ptr [rip + os_tv_base]
    jmp .fim_oscilacao
.oscilar_falha:
    movss xmm0, dword ptr [rip + tempo]
    mulss xmm0, dword ptr [rip + os_falha_f1]
    call sinf
    movss dword ptr [rsp + 4], xmm0
    movss xmm0, dword ptr [rip + tempo]
    mulss xmm0, dword ptr [rip + os_falha_f2]
    addss xmm0, dword ptr [rsp]
    call sinf
    mulss xmm0, dword ptr [rsp + 4]
    ucomiss xmm0, dword ptr [rip + os_falha_limiar]
    ja .falha_apagada
    movss xmm0, dword ptr [rip + um]
    jmp .fim_oscilacao
.falha_apagada:
    movss xmm0, dword ptr [rip + os_falha_apagada]
    jmp .fim_oscilacao
.oscilar_neon:
    movss xmm0, dword ptr [rip + tempo]
    mulss xmm0, dword ptr [rip + os_neon_f1]
    call sinf
    movss dword ptr [rsp + 4], xmm0
    movss xmm0, dword ptr [rip + tempo]
    mulss xmm0, dword ptr [rip + os_neon_f2]
    call sinf
    mulss xmm0, dword ptr [rsp + 4]
    ucomiss xmm0, dword ptr [rip + os_neon_limiar]
    ja .neon_fraco
    movss xmm0, dword ptr [rip + um]
    jmp .fim_oscilacao
.neon_fraco:
    movss xmm0, dword ptr [rip + os_neon_fraco]
.fim_oscilacao:
    add rsp, 32
    pop rbx
    ret

# edi = cor RGBA, xmm0 = fator. eax <- cor com R, G e B multiplicados (alfa mantido).
escalar_cor:
    mov r8d, edi
    xor eax, eax
    xor ecx, ecx
.escalar_canal:
    mov edx, r8d
    shr edx, cl
    and edx, 0xff
    cvtsi2ss xmm1, edx
    mulss xmm1, xmm0
    cvttss2si edx, xmm1
    cmp edx, 255
    jle .canal_teto
    mov edx, 255
.canal_teto:
    test edx, edx
    jns .canal_pronto
    xor edx, edx
.canal_pronto:
    shl edx, cl
    or eax, edx
    add ecx, 8
    cmp ecx, 24
    jl .escalar_canal
    and r8d, 0xff000000
    or eax, r8d
    ret

# Mapa de luz: ambiente escuro do andar + luzes somadas (blend aditivo).
desenhar_luzes:
    push rbx
    push r12
    push r13
    lea rdi, [rip + mapa_luz]
    call iniciar_alvo
    mov rax, qword ptr [rip + andar_ptr]
    mov edi, dword ptr [rax + AND_AMBIENTE]
    call ClearBackground
    mov edi, BLEND_ADITIVO
    call BeginBlendMode
    call aplicar_camera
    lea rsi, [rip + recorte_luz]
    lea rdx, [rip + destino_tela]
    call definir_recortes

    mov rax, qword ptr [rip + andar_ptr]
    mov rbx, qword ptr [rax + AND_LUZES]
    mov r12, qword ptr [rax + AND_N_LUZES]
.proxima_luz:
    test r12, r12
    jz .luz_icaro
    cvtsi2ss xmm0, dword ptr [rbx + LUZ_X]
    mov edi, dword ptr [rbx + LUZ_OSC]
    call oscilacao
    mov edi, dword ptr [rbx + LUZ_COR]
    call escalar_cor
    mov r13d, eax
    cvtsi2ss xmm1, dword ptr [rbx + LUZ_RAIO]
    cvtsi2ss xmm0, dword ptr [rbx + LUZ_X]
    subss xmm0, xmm1
    movss dword ptr [rip + rec_destino], xmm0
    cvtsi2ss xmm0, dword ptr [rbx + LUZ_Y]
    subss xmm0, xmm1
    movss dword ptr [rip + rec_destino + 4], xmm0
    addss xmm1, xmm1
    movss dword ptr [rip + rec_destino + 8], xmm1
    movss dword ptr [rip + rec_destino + 12], xmm1
    lea rdi, [rip + textura_luz]
    mov esi, r13d
    call desenhar_recorte
    add rbx, LUZ_TAM
    dec r12
    jmp .proxima_luz
.luz_icaro:
    movss xmm1, dword ptr [rip + raio_luz_icaro]
    movss xmm0, dword ptr [rip + icaro + POS_X]
    subss xmm0, xmm1
    movss dword ptr [rip + rec_destino], xmm0
    movss xmm0, dword ptr [rip + icaro + POS_Y]
    subss xmm0, dword ptr [rip + altura_foco]
    subss xmm0, xmm1
    movss dword ptr [rip + rec_destino + 4], xmm0
    addss xmm1, xmm1
    movss dword ptr [rip + rec_destino + 8], xmm1
    movss dword ptr [rip + rec_destino + 12], xmm1
    lea rdi, [rip + textura_luz]
    mov esi, dword ptr [rip + cor_luz_icaro]
    call desenhar_recorte
    call rlPopMatrix
    call EndBlendMode
    call EndTextureMode
    pop r13
    pop r12
    pop rbx
    ret

# Percorre a planta: escolhe a variante de cada tile pelos vizinhos e
# escurece o piso junto às paredes.
desenhar_tiles:
    push rbx
    push r12
    push r13
    push r14
    push r15
    mov dword ptr [rip + cor_atual], -1
    xor r13d, r13d
.tile_linha:
    xor r12d, r12d
.tile_coluna:
    mov edi, r12d
    mov esi, r13d
    call info_tile
    test eax, eax
    jz .proximo_tile
    mov ebx, eax
    movzx r14d, al
    mov r15d, ebx
    shr r15d, 8
    and r15d, 0xff
    cmp r15d, CL_TOPO
    je .variante_topo
    cmp r15d, CL_FACE
    je .variante_face
    cmp r15d, CL_COLUNA
    je .variante_coluna
    # Pisos e sólidos simples: variante por um hash fixo da posição.
    mov eax, r12d
    imul eax, eax, 7
    mov ecx, r13d
    imul ecx, ecx, 13
    add eax, ecx
    mov ecx, r12d
    imul ecx, r13d
    add eax, ecx
    xor edx, edx
    mov ecx, ebx
    shr ecx, 16
    and ecx, 0xff
    div ecx
    add r14d, edx
    jmp .desenhar_tile_atual
.variante_topo:
    # Máscara de lados abertos: N=1, L=2, S=4, O=8.
    xor r15d, r15d
    mov edi, r12d
    lea esi, [r13 - 1]
    call parede_fechada
    test eax, eax
    jnz .topo_leste
    or r15d, 1
.topo_leste:
    lea edi, [r12 + 1]
    mov esi, r13d
    call parede_fechada
    test eax, eax
    jnz .topo_sul
    or r15d, 2
.topo_sul:
    mov edi, r12d
    lea esi, [r13 + 1]
    call parede_fechada
    test eax, eax
    jnz .topo_oeste
    or r15d, 4
.topo_oeste:
    lea edi, [r12 - 1]
    mov esi, r13d
    call parede_fechada
    test eax, eax
    jnz .topo_pronto
    or r15d, 8
.topo_pronto:
    add r14d, r15d
    jmp .desenhar_tile_atual
.variante_face:
    # Seis peças: (rodaforro, meio, rodapé) x (coluna par, ímpar).
    mov edi, r12d
    lea esi, [r13 - 1]
    call classe_em
    cmp eax, CL_FACE
    jne .face_superior
    mov edi, r12d
    lea esi, [r13 + 1]
    call classe_em
    cmp eax, CL_FACE
    jne .face_inferior
    mov r15d, 2
    jmp .face_paridade
.face_superior:
    xor r15d, r15d
    jmp .face_paridade
.face_inferior:
    mov r15d, 4
.face_paridade:
    mov eax, r12d
    and eax, 1
    add r15d, eax
    add r14d, r15d
    jmp .desenhar_tile_atual
.variante_coluna:
    # Colunas verticais (janela lateral, porta, guarda-corpo): ponta, meio, ponta.
    mov edi, r12d
    mov esi, r13d
    call caractere_em
    mov r15d, eax
    mov edi, r12d
    lea esi, [r13 - 1]
    call caractere_em
    cmp eax, r15d
    jne .desenhar_tile_atual
    mov edi, r12d
    lea esi, [r13 + 1]
    call caractere_em
    cmp eax, r15d
    jne .coluna_inferior
    add r14d, 1
    jmp .desenhar_tile_atual
.coluna_inferior:
    add r14d, 2
.desenhar_tile_atual:
    mov edi, r14d
    mov esi, r12d
    mov edx, r13d
    call desenhar_tile

    mov eax, ebx
    shr eax, 8
    and eax, 0xff
    cmp eax, CL_PISO
    jne .proximo_tile
    mov edi, r12d
    lea esi, [r13 - 1]
    call classe_em
    cmp eax, CL_FACE
    jne .sem_sombra_norte
    mov edi, T_SOMBRA_NORTE
    mov esi, r12d
    mov edx, r13d
    call desenhar_tile
.sem_sombra_norte:
    lea edi, [r12 - 1]
    mov esi, r13d
    call classe_em
    cmp eax, CL_TOPO
    je .sombra_oeste
    cmp eax, CL_COLUNA
    jne .proximo_tile
.sombra_oeste:
    mov edi, T_SOMBRA_OESTE
    mov esi, r12d
    mov edx, r13d
    call desenhar_tile
.proximo_tile:
    inc r12d
    cmp r12d, LARGURA_MAPA
    jl .tile_coluna
    inc r13d
    cmp r13d, ALTURA_MAPA
    jl .tile_linha
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbx
    ret

# edi = camada. Desenha, na ordem da lista, os objetos daquela camada.
desenhar_camada:
    push rbx
    push r12
    push r13
    mov r13d, edi
    mov rax, qword ptr [rip + andar_ptr]
    mov rbx, qword ptr [rax + AND_OBJETOS]
    mov r12, qword ptr [rax + AND_N_OBJETOS]
.objeto_camada:
    test r12, r12
    jz .fim_camada
    cmp dword ptr [rbx + OBJ_CAMADA], r13d
    jne .pular_objeto_camada
    mov rdi, rbx
    call desenhar_objeto
.pular_objeto_camada:
    add rbx, OBJ_TAM
    dec r12
    jmp .objeto_camada
.fim_camada:
    pop r13
    pop r12
    pop rbx
    ret

# Móveis em ordem de base com Ícaro inserido na profundidade dos pés.
desenhar_ordenados:
    push rbx
    push r12
    push r13
    cvttss2si r13d, dword ptr [rip + icaro + POS_Y]
    mov dword ptr [rip + icaro_desenhado], 0
    mov rax, qword ptr [rip + andar_ptr]
    mov rbx, qword ptr [rax + AND_OBJETOS]
    mov r12, qword ptr [rax + AND_N_OBJETOS]
.objeto_ordenado:
    test r12, r12
    jz .fim_ordenados
    cmp dword ptr [rbx + OBJ_CAMADA], CAM_ORDENADA
    jne .pular_ordenado
    cmp dword ptr [rip + icaro_desenhado], 0
    jne .desenhar_ordenado
    cmp dword ptr [rbx + OBJ_BASE], r13d
    jle .desenhar_ordenado
    call desenhar_icaro
    mov dword ptr [rip + icaro_desenhado], 1
.desenhar_ordenado:
    mov rdi, rbx
    call desenhar_objeto
.pular_ordenado:
    add rbx, OBJ_TAM
    dec r12
    jmp .objeto_ordenado
.fim_ordenados:
    cmp dword ptr [rip + icaro_desenhado], 0
    jne .ordenados_prontos
    call desenhar_icaro
.ordenados_prontos:
    pop r13
    pop r12
    pop rbx
    ret

# rdi = objeto. Aplica a oscilação de brilho e as animações.
desenhar_objeto:
    push rbx
    sub rsp, 16
    mov rbx, rdi
    mov dword ptr [rip + cor_atual], -1
    mov edi, dword ptr [rbx + OBJ_OSC]
    test edi, edi
    jz .cor_objeto_pronta
    cvtsi2ss xmm0, dword ptr [rbx + OBJ_X]
    call oscilacao
    mov edi, -1
    call escalar_cor
    mov dword ptr [rip + cor_atual], eax
.cor_objeto_pronta:
    cmp dword ptr [rbx + OBJ_ANIM], AN_NOTAS
    je .objeto_notas
    mov edi, dword ptr [rbx + OBJ_SX]
    mov esi, dword ptr [rbx + OBJ_SY]
    mov edx, dword ptr [rbx + OBJ_SL]
    mov ecx, dword ptr [rbx + OBJ_SA]
    mov r8d, dword ptr [rbx + OBJ_X]
    mov r9d, dword ptr [rbx + OBJ_Y]
    call desenhar_atlas
    cmp dword ptr [rbx + OBJ_ANIM], AN_DISCO
    jne .fim_objeto
    mov rdi, rbx
    call desenhar_reflexo_disco
    jmp .fim_objeto
.objeto_notas:
    mov rdi, rbx
    call desenhar_notas
.fim_objeto:
    mov dword ptr [rip + cor_atual], -1
    add rsp, 16
    pop rbx
    ret

# rdi = disco. Dois reflexos dão a volta na elipse do vinil.
desenhar_reflexo_disco:
    push rbx
    push r12
    sub rsp, 24
    mov rbx, rdi
    xor r12d, r12d
.reflexo:
    movss xmm0, dword ptr [rip + tempo]
    mulss xmm0, dword ptr [rip + disco_rotacao]
    cvtsi2ss xmm1, r12d
    mulss xmm1, dword ptr [rip + pi]
    addss xmm0, xmm1
    movss dword ptr [rsp], xmm0
    call cosf
    mulss xmm0, dword ptr [rip + disco_rx]
    movss dword ptr [rsp + 4], xmm0
    movss xmm0, dword ptr [rsp]
    call sinf
    mulss xmm0, dword ptr [rip + disco_ry]
    cvtsi2ss xmm1, dword ptr [rbx + OBJ_Y]
    addss xmm1, dword ptr [rip + disco_cy]
    addss xmm0, xmm1
    cvttss2si esi, xmm0
    cvtsi2ss xmm1, dword ptr [rbx + OBJ_X]
    addss xmm1, dword ptr [rip + disco_cx]
    addss xmm1, dword ptr [rsp + 4]
    cvttss2si edi, xmm1
    mov edx, 2
    mov ecx, 1
    mov r8d, 0xffb4a0a0
    call DrawRectangle
    inc r12d
    cmp r12d, 2
    jl .reflexo
    add rsp, 24
    pop r12
    pop rbx
    ret

# rdi = nota. Três notas sobem da vitrola, balançam e somem.
desenhar_notas:
    push rbx
    push r12
    sub rsp, 24
    mov rbx, rdi
    xor r12d, r12d
.nota:
    # fase = parte fracionária de (tempo * ritmo + k/3)
    cvtsi2ss xmm0, r12d
    mulss xmm0, dword ptr [rip + um_terco]
    movss xmm1, dword ptr [rip + tempo]
    mulss xmm1, dword ptr [rip + notas_ritmo]
    addss xmm0, xmm1
    cvttss2si eax, xmm0
    cvtsi2ss xmm1, eax
    subss xmm0, xmm1
    movss dword ptr [rsp], xmm0
    # balanço lateral
    mulss xmm0, dword ptr [rip + dois_pi]
    cvtsi2ss xmm1, r12d
    mulss xmm1, dword ptr [rip + notas_fase]
    addss xmm0, xmm1
    call sinf
    mulss xmm0, dword ptr [rip + notas_balanco]
    cvtsi2ss xmm1, dword ptr [rbx + OBJ_X]
    addss xmm0, xmm1
    cvttss2si eax, xmm0
    mov dword ptr [rsp + 4], eax
    # subida e alfa
    movss xmm0, dword ptr [rsp]
    mulss xmm0, dword ptr [rip + notas_subida]
    cvtsi2ss xmm1, dword ptr [rbx + OBJ_Y]
    subss xmm1, xmm0
    cvttss2si eax, xmm1
    mov dword ptr [rsp + 8], eax
    movss xmm0, dword ptr [rip + um]
    subss xmm0, dword ptr [rsp]
    mulss xmm0, dword ptr [rip + c_255]
    cvttss2si eax, xmm0
    shl eax, 24
    or eax, 0x00ffffff
    mov dword ptr [rip + cor_atual], eax
    mov edi, dword ptr [rbx + OBJ_SX]
    mov esi, dword ptr [rbx + OBJ_SY]
    mov edx, dword ptr [rbx + OBJ_SL]
    mov ecx, dword ptr [rbx + OBJ_SA]
    mov r8d, dword ptr [rsp + 4]
    mov r9d, dword ptr [rsp + 8]
    call desenhar_atlas
    inc r12d
    cmp r12d, 3
    jl .nota
    add rsp, 24
    pop r12
    pop rbx
    ret

# Sombra no chão e o quadro da animação de caminhada.
desenhar_icaro:
    push rbp
    mov rbp, rsp
    sub rsp, 16
    mov dword ptr [rip + cor_atual], -1
    mov edi, S_SOMBRA_PES_X
    mov esi, S_SOMBRA_PES_Y
    mov edx, S_SOMBRA_PES_L
    mov ecx, S_SOMBRA_PES_A
    cvttss2si r8d, dword ptr [rip + icaro + POS_X]
    sub r8d, 8
    cvttss2si r9d, dword ptr [rip + icaro + POS_Y]
    sub r9d, 3
    call desenhar_atlas

    xor eax, eax
    cmp dword ptr [rip + icaro + ANDANDO], 0
    je .quadro_escolhido
    movss xmm0, dword ptr [rip + icaro + TEMPO]
    mulss xmm0, dword ptr [rip + dez]
    cvttss2si eax, xmm0
    and eax, 7
    inc eax
.quadro_escolhido:
    imul eax, eax, 384
    cvtsi2ss xmm0, eax
    movss dword ptr [rip + rec_origem], xmm0
    mov eax, dword ptr [rip + icaro + DIRECAO]
    imul eax, eax, 512
    cvtsi2ss xmm0, eax
    movss dword ptr [rip + rec_origem + 4], xmm0
    movq xmm0, qword ptr [rip + tamanho_celula]
    movq qword ptr [rip + rec_origem + 8], xmm0
    movss xmm0, dword ptr [rip + icaro + POS_X]
    subss xmm0, dword ptr [rip + ancora_x]
    movss dword ptr [rip + rec_destino], xmm0
    movss xmm0, dword ptr [rip + icaro + POS_Y]
    subss xmm0, dword ptr [rip + ancora_y]
    movss dword ptr [rip + rec_destino + 4], xmm0
    movq xmm0, qword ptr [rip + tamanho_sprite]
    movq qword ptr [rip + rec_destino + 8], xmm0
    mov qword ptr [rip + vec_pivo], 0
    mov dword ptr [rip + rotacao_atual], 0
    lea rdi, [rip + textura_icaro]
    mov esi, -1
    call desenhar_recorte
    leave
    ret

# Modo de inspeção: paredes em magenta, colisão de móveis em ciano, escadas em amarelo.
desenhar_colisoes:
    push rbx
    push r12
    push r13
    xor r13d, r13d
.colisao_linha:
    xor r12d, r12d
.colisao_coluna:
    mov edi, r12d
    mov esi, r13d
    call classe_em
    cmp eax, CL_PISO
    je .proxima_colisao
    mov edi, r12d
    shl edi, 4
    mov esi, r13d
    shl esi, 4
    mov edx, TILE
    mov ecx, TILE
    mov r8d, 0x90ff00ff
    call DrawRectangleLines
.proxima_colisao:
    inc r12d
    cmp r12d, LARGURA_MAPA
    jl .colisao_coluna
    inc r13d
    cmp r13d, ALTURA_MAPA
    jl .colisao_linha

    mov rax, qword ptr [rip + andar_ptr]
    mov rbx, qword ptr [rax + AND_OBJETOS]
    mov r12, qword ptr [rax + AND_N_OBJETOS]
.colisao_objeto_desenho:
    test r12, r12
    jz .colisao_escadas
    mov edx, dword ptr [rbx + OBJ_CL]
    test edx, edx
    jz .pular_colisao_objeto
    mov edi, dword ptr [rbx + OBJ_CX]
    mov esi, dword ptr [rbx + OBJ_CY]
    mov ecx, dword ptr [rbx + OBJ_CA]
    mov r8d, 0xffffff00
    call DrawRectangleLines
.pular_colisao_objeto:
    add rbx, OBJ_TAM
    dec r12
    jmp .colisao_objeto_desenho
.colisao_escadas:
    mov rax, qword ptr [rip + andar_ptr]
    mov rbx, qword ptr [rax + AND_TRANSICOES]
    mov r12, qword ptr [rax + AND_N_TRANSICOES]
.colisao_escada:
    test r12, r12
    jz .fim_desenho_colisoes
    mov edi, dword ptr [rbx + TR_X]
    mov esi, dword ptr [rbx + TR_Y]
    mov edx, dword ptr [rbx + TR_L]
    mov ecx, dword ptr [rbx + TR_A]
    mov r8d, 0xff00ffff
    call DrawRectangleLines
    add rbx, TR_TAM
    dec r12
    jmp .colisao_escada
.fim_desenho_colisoes:
    pop r13
    pop r12
    pop rbx
    ret

desenhar_fade:
    sub rsp, 8
    movss xmm0, dword ptr [rip + fade_alfa]
    ucomiss xmm0, dword ptr [rip + zero]
    jbe .sem_fade
    mulss xmm0, dword ptr [rip + c_255]
    cvttss2si r8d, xmm0
    shl r8d, 24
    xor edi, edi
    xor esi, esi
    mov edx, dword ptr [rip + largura_tela]
    mov ecx, dword ptr [rip + altura_tela]
    call DrawRectangle
.sem_fade:
    add rsp, 8
    ret

# Faixa inferior: andar / cômodo à esquerda, controles à direita.
# Tamanhos proporcionais à altura da janela (fonte_hud, altura_hud).
desenhar_hud:
    push rbx
    push r12
    push r13
    push r14
    push r15
    mov r13d, dword ptr [rip + fonte_hud]
    mov r15d, dword ptr [rip + altura_tela]
    sub r15d, dword ptr [rip + altura_hud]       # topo da faixa
    mov r14d, dword ptr [rip + altura_hud]
    sub r14d, r13d
    shr r14d, 1
    add r14d, r15d                               # y do texto, centralizado
    xor edi, edi
    mov esi, r15d
    mov edx, dword ptr [rip + largura_tela]
    mov ecx, dword ptr [rip + altura_hud]
    mov r8d, 0xf0140c10
    call DrawRectangle
    mov rax, qword ptr [rip + andar_ptr]
    mov rbx, qword ptr [rax + AND_NOME]
    mov rdi, rbx
    mov esi, r13d
    mov edx, r14d
    mov ecx, r13d
    mov r8d, 0xffcbdbe5
    call DrawText
    mov rdi, rbx
    mov esi, r13d
    call MeasureText
    # separador a 0,6 fonte depois do nome do andar
    lea r12d, [r13 + rax]
    imul eax, r13d, 3
    xor edx, edx
    mov ecx, 5
    div ecx
    add r12d, eax
    lea rdi, [rip + separador]
    mov esi, r12d
    mov edx, r14d
    mov ecx, r13d
    mov r8d, 0xff6a5a5a
    call DrawText
    mov rdi, qword ptr [rip + comodo_nome]
    test rdi, rdi
    jz .hud_controles
    lea esi, [r12 + r13]
    mov edx, r14d
    mov ecx, r13d
    mov r8d, 0xff6ab4e8
    call DrawText
.hud_controles:
    lea rdi, [rip + controles]
    mov esi, r13d
    call MeasureText
    mov esi, dword ptr [rip + largura_tela]
    sub esi, r13d
    sub esi, eax
    lea rdi, [rip + controles]
    mov edx, r14d
    mov ecx, r13d
    mov r8d, 0xff8a8f9a
    call DrawText
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbx
    ret

.section .note.GNU-stack,"",@progbits
