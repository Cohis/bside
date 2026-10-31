.intel_syntax noprefix

# B-Side: Fase 1 em perspectiva isométrica. Toda a lógica está em Assembly x86-64.
# ABI System V (Linux); a Raylib cuida apenas de janela, entrada, áudio e desenho.
# Plantas, móveis e luzes ficam em fase1.s; a arte, em assets/tileset-iso.png.
#
# Projeção: o tile (tx, ty) tem o vértice de cima em
#   iso_x = 16 (tx - ty) + ORIGEM_ISO_X,   iso_y = 8 (tx + ty)
# e um ponto do mundo (x, y) em px cai em (x - y + ORIGEM_ISO_X, (x + y) / 2).

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
.equ MASCARA_OPACA, 0xffffffff
.equ MASCARA_TRANSPARENTE, 0x5cffffff   # alfa ~36% para a parede na frente de Ícaro

.section .rodata
titulo:         .asciz "B-Side | Fase 1"
caminho_icaro_final: .asciz "assets/icaro-andar-final.png"
caminho_icaro:  .asciz "assets/icaro-andar-rascunho.png"
caminho_tileset: .asciz "assets/tileset-iso.png"
caminho_personagens: .asciz "assets/personagens.png"
caminho_elenco_hd: .asciz "assets/elenco-hd.png"
caminho_nevoa:  .asciz "assets/nevoa.png"
caminho_luz:    .asciz "assets/luz.png"
caminho_vinheta: .asciz "assets/vinheta.png"
caminho_musica: .asciz "assets/musica-fundo.mp3"
erro_recursos:  .asciz "Nao foi possivel carregar as texturas. Execute a partir da raiz do repositorio."
erro_janela:    .asciz "Nao foi possivel abrir uma janela grafica."
controles:      .asciz "WASD mover    E interagir    1-4 notas    F11 tela cheia    ESC sair"
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
velocidade:     .float 56.0               # px do mundo por segundo
tempo_ciclo:    .float 0.8
dez:            .float 10.0
velocidade_fade: .float 4.0
c_255:          .float 255.0
c_16:           .float 16.0
inverso_16:     .float 0.0625
origem_iso_x:   .float 352.0              # ORIGEM_ISO_X

# Limites da projeção do andar (22 x 22 tiles), com folga para as paredes.
iso_min_x:      .float 0.0
iso_max_x:      .float 704.0
iso_min_y:      .float -56.0
iso_max_y:      .float 364.0
altura_foco:    .float 20.0               # a câmera mira o tronco, não os pés

# Sprite: quadro 384x512, figura de 424 px e âncora (192,480), reduzidos
# para ~40 px de altura na tela isométrica.
tamanho_celula: .float 384.0, 512.0
tamanho_sprite: .float 36.23, 48.30
ancora_x:       .float 18.113
ancora_y:       .float 45.283

# Caixa dos pés usada na colisão (px do mundo).
pe_lado:        .float 5.0
pe_cima:        .float 4.0
pe_baixo:       .float 1.0

recorte_luz:    .float 0.0, 0.0, 128.0, 128.0
recorte_vinheta: .float 0.0, 0.0, 320.0, 180.0
achatamento_luz: .float 0.6               # poças de luz são elipses 2:1 no chão
raio_luz_icaro: .float 60.0
cor_luz_icaro:  .long 0xff5a4a50          # ABGR: luz fraca que mantém Ícaro legível

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

disco_rotacao:  .float 3.5
pi:             .float 3.14159265
disco_rx:       .float 4.5
disco_ry:       .float 2.3
notas_ritmo:    .float 0.45
um_terco:       .float 0.33333333
notas_subida:   .float 22.0
notas_balanco:  .float 4.0
dois_pi:        .float 6.2831853
notas_fase:     .float 2.1
volume_musica:  .float 0.5
cem:            .float 100.0

.section .data
.align 16
# x, y (pés, px do mundo), direção, andando, tempo, cima, baixo, esquerda, direita
icaro: .float 104.0, 296.0
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
textura_personagens: .skip 20
textura_elenco_hd: .skip 20
textura_nevoa:   .skip 20
.align 16
musica:          .skip 56                 # Music (AudioStream 32, frameCount, looping, ctxType, ctxData)
musica_ok:       .skip 4
.align 16
mapa_luz:        .skip 48                 # RenderTexture2D (44 bytes)
tabela_tile:     .skip 2048               # por caractere: ponteiro para o tipo em tipos_tile
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
ponto_lido:      .skip 12
checar_oclusao:  .skip 4
# Ícaro na tela isométrica, recalculado a cada quadro.
icaro_iso_x:     .skip 4
icaro_iso_y:     .skip 4
icaro_elevacao:  .skip 4
icaro_chave:     .skip 4                  # x + y dos pés: profundidade
# Estado da parede que está sendo desenhada.
parede_sul:      .skip 4
parede_leste:    .skip 4
parede_altura:   .skip 4
parede_mascara:  .skip 4                  # cor aplicada à parede: opaca ou transparente
largura_tela:    .skip 4
altura_tela:     .skip 4
altura_hud:      .skip 4
fonte_hud:       .skip 4
zoom:            .skip 4
vista_l:         .skip 4
vista_a:         .skip 4
metade_vista_l:  .skip 4
metade_vista_a:  .skip 4
.align 16
recorte_tela:    .skip 16
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
.extern DrawLine
.extern DrawText
.extern MeasureText
.extern InitAudioDevice
.extern CloseAudioDevice
.extern LoadMusicStream
.extern UnloadMusicStream
.extern PlayMusicStream
.extern UpdateMusicStream
.extern SetMusicVolume
.extern rlPushMatrix
.extern rlPopMatrix
.extern rlTranslatef
.extern rlScalef
.extern IsWindowReady
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
.extern papeis
.global main
.type main, @function
# Estado e rotinas usados por atores.s, roteiro.s, ritmo.s e doca.s.
.global icaro
.global icaro_chave
.global icaro_iso_x
.global icaro_iso_y
.global tempo
.global delta_quadro
.global andar_indice
.global andar_ptr
.global comodo_nome
.global fade_fase
.global zoom
.global largura_tela
.global altura_tela
.global altura_hud
.global fonte_hud
.global desloc_x
.global desloc_y
.global camera_x
.global camera_y
.global textura_personagens
.global textura_elenco_hd
.global textura_nevoa
.global rec_origem
.global rec_destino
.global vec_pivo
.global rotacao_atual
.global cor_atual
.global desenhar_recorte
.global desenhar_atlas
.global desenhar_icaro
.global volume_trilha
.extern n_andares
.extern perturbacao
.extern foco_x
.extern foco_y
.extern iniciar_atores
.extern atualizar_atores
.extern preparar_entes
.extern desenhar_entes_ate
.extern desenhar_entes_resto
.extern desenhar_atores_emissivos
.extern iniciar_roteiro
.extern atualizar_roteiro
.extern tecla_movimento
.extern roteiro_ativo
.extern atualizar_foco
.extern aplicar_tremor
.extern desenhar_nevoa
.extern desenhar_mundo_roteiro
.extern desenhar_tela_roteiro
.extern iniciar_ritmo
.extern encerrar_ritmo
.extern atualizar_ritmo

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
    lea rdi, [rip + textura_personagens]
    lea rsi, [rip + caminho_personagens]
    call LoadTexture
    lea rdi, [rip + textura_elenco_hd]
    lea rsi, [rip + caminho_elenco_hd]
    call LoadTexture
    lea rdi, [rip + textura_nevoa]
    lea rsi, [rip + caminho_nevoa]
    call LoadTexture

    cmp dword ptr [rip + textura_icaro], 0
    je .erro
    cmp dword ptr [rip + textura_tileset], 0
    je .erro
    cmp dword ptr [rip + textura_luz], 0
    je .erro
    cmp dword ptr [rip + textura_vinheta], 0
    je .erro
    cmp dword ptr [rip + textura_personagens], 0
    je .erro
    cmp dword ptr [rip + textura_elenco_hd], 0
    je .erro
    cmp dword ptr [rip + textura_nevoa], 0
    je .erro

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

    # agente e anjo vêm em células 384x512 como o Ícaro: mesma redução
    lea rdi, [rip + textura_elenco_hd]
    call GenTextureMipmaps
    sub rsp, 32
    lea rsi, [rip + textura_elenco_hd]
    mov rax, qword ptr [rsi]
    mov qword ptr [rsp], rax
    mov rax, qword ptr [rsi + 8]
    mov qword ptr [rsp + 8], rax
    mov eax, dword ptr [rsi + 16]
    mov dword ptr [rsp + 16], eax
    mov edi, FILTRO_TRILINEAR
    call SetTextureFilter
    add rsp, 32

    # a névoa é ampliada: filtro bilinear deixa as manchas macias
    sub rsp, 32
    lea rsi, [rip + textura_nevoa]
    mov rax, qword ptr [rsi]
    mov qword ptr [rsp], rax
    mov rax, qword ptr [rsi + 8]
    mov qword ptr [rsp + 8], rax
    mov eax, dword ptr [rsi + 16]
    mov dword ptr [rsp + 16], eax
    mov edi, 1
    call SetTextureFilter
    add rsp, 32

    call preparar_tiles
    mov qword ptr [rbp - 16], 0
.construir_andar:
    mov rax, qword ptr [rbp - 16]
    cmp rax, qword ptr [rip + n_andares]
    jge .andares_prontos
    lea rdx, [rip + andares]
    mov rdi, qword ptr [rdx + rax*8]
    call construir_itens
    inc qword ptr [rbp - 16]
    jmp .construir_andar
.andares_prontos:
    call iniciar_atores

    mov dword ptr [rip + andar_indice], 0
    call ler_ponto_inicial
    mov eax, dword ptr [rip + andar_indice]
    lea rdx, [rip + andares]
    mov rdx, qword ptr [rdx + rax*8]
    mov qword ptr [rip + andar_ptr], rdx
    call iniciar_musica
    call iniciar_ritmo
    call iniciar_roteiro

    # A fase abre saindo do preto.
    mov dword ptr [rip + fade_fase], 2
    movss xmm0, dword ptr [rip + um]
    movss dword ptr [rip + fade_alfa], xmm0

.quadro:
    call WindowShouldClose
    test al, al
    jne .fechar

    call GetFrameTime
    minss xmm0, dword ptr [rip + limite_delta]
    movss dword ptr [rip + delta_quadro], xmm0
    call GetTime
    cvtsd2ss xmm0, xmm0
    movss dword ptr [rip + tempo], xmm0
    call atualizar_musica
    call atualizar_ritmo
    call alternar_tela_cheia
    call atualizar_tela
    call atualizar_roteiro

    cmp dword ptr [rip + fade_fase], 0
    jne .sem_movimento
    lea rdi, [rip + icaro]
    call atualizar_personagem
    call roteiro_ativo
    test eax, eax
    jnz .movimento_pronto
    call verificar_transicoes
    jmp .movimento_pronto
.sem_movimento:
    mov dword ptr [rip + icaro + ANDANDO], 0
    mov dword ptr [rip + icaro + TEMPO], 0
.movimento_pronto:
    call atualizar_fade
    call atualizar_icaro_iso
    call atualizar_atores
    call atualizar_foco
    call atualizar_camera
    call aplicar_tremor
    call atualizar_comodo
    call desenhar_luzes

    call BeginDrawing
    mov edi, 0xff0c080a
    call ClearBackground

    # Cena: pisos, tapetes e, em ordem de profundidade, paredes, móveis e Ícaro.
    call aplicar_camera
    call desenhar_pisos
    mov dword ptr [rip + checar_oclusao], 0
    mov edi, CAM_CHAO
    call desenhar_camada
    call desenhar_itens
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

    # Brilhos próprios (placa, TV, janelas, notas) por cima da luz.
    call aplicar_camera
    call desenhar_emissivos
    call desenhar_atores_emissivos
    call desenhar_mundo_roteiro
    cmp dword ptr [rip + mostrar_colisoes], 0
    je .sem_colisoes
    call desenhar_colisoes
.sem_colisoes:
    call rlPopMatrix
    call desenhar_nevoa

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
    call desenhar_tela_roteiro

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
    call encerrar_ritmo
    call encerrar_musica
    lea rdi, [rip + mapa_luz]
    call liberar_alvo
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
    cmp dword ptr [rip + textura_personagens], 0
    je .pular_personagens
    lea rdi, [rip + textura_personagens]
    call descarregar_textura
.pular_personagens:
    cmp dword ptr [rip + textura_elenco_hd], 0
    je .pular_elenco_hd
    lea rdi, [rip + textura_elenco_hd]
    call descarregar_textura
.pular_elenco_hd:
    cmp dword ptr [rip + textura_nevoa], 0
    je .pular_nevoa
    lea rdi, [rip + textura_nevoa]
    call descarregar_textura
.pular_nevoa:
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

# edi = volume da trilha em %.
volume_trilha:
    cmp dword ptr [rip + musica_ok], 0
    je .fim_volume_trilha
    sub rsp, 8
    cvtsi2ss xmm0, edi
    divss xmm0, dword ptr [rip + cem]
    lea r10, [rip + SetMusicVolume]
    call chamar_musica
    add rsp, 8
.fim_volume_trilha:
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

# Recorte do atlas sem escala. edi,esi = origem; edx,ecx = tamanho;
# r8d,r9d = destino na tela isométrica. A cor vem de cor_atual.
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

# edi=tx, esi=ty -> eax = iso_x do vértice de cima, edx = iso_y.
iso_tile:
    mov eax, edi
    sub eax, esi
    shl eax, 4
    add eax, ORIGEM_ISO_X
    lea edx, [rdi + rsi]
    shl edx, 3
    ret

# Indexa tipos_tile pelo caractere: tabela_tile[c] = ponteiro do tipo.
preparar_tiles:
    lea rsi, [rip + tipos_tile]
    mov ecx, dword ptr [rip + n_tipos_tile]
    lea r9, [rip + tabela_tile]
.proximo_tipo:
    test ecx, ecx
    jz .fim_tipos
    mov eax, dword ptr [rsi + TT_CHAR]
    and eax, 0xff
    mov qword ptr [r9 + rax*8], rsi
    add rsi, TT_TAM
    dec ecx
    jmp .proximo_tipo
.fim_tipos:
    ret

# edi=tx, esi=ty -> rax = tipo do tile (0 fora do mapa ou sem legenda).
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
    mov rax, qword ptr [rdx + rcx*8]
.fim_info:
    ret

# edi=tx, esi=ty -> eax = classe do tile, ou 0xff fora do mapa.
classe_em:
    call info_tile
    test rax, rax
    jz .classe_indefinida
    mov eax, dword ptr [rax + TT_CLASSE]
    ret
.classe_indefinida:
    mov eax, 0xff
    ret

# edi=tx, esi=ty -> eax=1 se o tile é chão (piso, degrau ou vão), que uma face pode encarar.
e_chao:
    call classe_em
    cmp eax, CL_PISO
    je .sim_chao
    cmp eax, CL_DEGRAU
    je .sim_chao
    cmp eax, CL_VAO
    je .sim_chao
    xor eax, eax
    ret
.sim_chao:
    mov eax, 1
    ret

# edi=ty -> eax = altura do degrau naquela linha (0 se a escada do andar é plana).
elevacao_linha:
    mov rax, qword ptr [rip + andar_ptr]
    mov ecx, dword ptr [rax + AND_ESCADA_PASSO]
    test ecx, ecx
    jz .linha_plana
    mov eax, dword ptr [rax + AND_ESCADA_BASE]
    sub eax, edi
    imul eax, ecx
    shr ecx, 1
    sub eax, ecx                     # centro do degrau: meio passo abaixo da borda
    test eax, eax
    jg .fim_elevacao
.linha_plana:
    xor eax, eax
.fim_elevacao:
    ret

# rdi = descritor do andar. Monta a lista de profundidade: paredes, degraus
# elevados e móveis, ordenados pela chave x + y (inserção estável).
construir_itens:
    push rbx
    push r12
    push r13
    push r14
    push r15
    mov r15, rdi
    mov r14, qword ptr [rip + andar_ptr]
    mov qword ptr [rip + andar_ptr], r15
    mov rbx, qword ptr [r15 + AND_ITENS]
    xor r12d, r12d                   # quantidade de itens
    xor r13d, r13d                   # índice do tile
.item_tile:
    cmp r13d, LARGURA_MAPA * ALTURA_MAPA
    jge .itens_objetos
    mov eax, r13d
    xor edx, edx
    mov ecx, LARGURA_MAPA
    div ecx
    mov edi, edx
    mov esi, eax
    call classe_em
    cmp eax, CL_PAREDE
    je .incluir_tile
    cmp eax, CL_DEGRAU
    jne .proximo_item_tile
    cmp dword ptr [r15 + AND_ESCADA_PASSO], 0
    je .proximo_item_tile
.incluir_tile:
    mov eax, r13d
    xor edx, edx
    mov ecx, LARGURA_MAPA
    div ecx
    add eax, edx
    shl eax, 4
    add eax, TILE                    # centro do tile: 16 (tx + ty) + 16
    mov rcx, r12
    shl rcx, 4
    mov dword ptr [rbx + rcx + IT_CHAVE], eax
    mov dword ptr [rbx + rcx + IT_TIPO], IT_BLOCO
    mov eax, r13d
    mov qword ptr [rbx + rcx + IT_DADO], rax
    inc r12d
.proximo_item_tile:
    inc r13d
    jmp .item_tile
.itens_objetos:
    mov rsi, qword ptr [r15 + AND_OBJETOS]
    mov rcx, qword ptr [r15 + AND_N_OBJETOS]
.item_objeto:
    test rcx, rcx
    jz .ordenar_itens
    cmp dword ptr [rsi + OBJ_CAMADA], CAM_ORDENADA
    jne .proximo_item_objeto
    mov rdx, r12
    shl rdx, 4
    mov eax, dword ptr [rsi + OBJ_CHAVE]
    mov dword ptr [rbx + rdx + IT_CHAVE], eax
    mov dword ptr [rbx + rdx + IT_TIPO], IT_OBJETO
    mov qword ptr [rbx + rdx + IT_DADO], rsi
    inc r12d
.proximo_item_objeto:
    add rsi, OBJ_TAM
    dec rcx
    jmp .item_objeto
.ordenar_itens:
    mov ecx, 1
.ordem_externa:
    cmp ecx, r12d
    jge .ordem_fim
    mov rax, rcx
    shl rax, 4
    movdqu xmm0, xmmword ptr [rbx + rax]
    mov r11d, dword ptr [rbx + rax + IT_CHAVE]
    mov rdx, rcx
.ordem_interna:
    test rdx, rdx
    jz .ordem_inserir
    lea rax, [rdx - 1]
    shl rax, 4
    cmp dword ptr [rbx + rax + IT_CHAVE], r11d
    jle .ordem_inserir
    movdqu xmm1, xmmword ptr [rbx + rax]
    movdqu xmmword ptr [rbx + rax + IT_TAM], xmm1
    dec rdx
    jmp .ordem_interna
.ordem_inserir:
    mov rax, rdx
    shl rax, 4
    movdqu xmmword ptr [rbx + rax], xmm0
    inc ecx
    jmp .ordem_externa
.ordem_fim:
    mov qword ptr [r15 + AND_N_ITENS], r12
    mov qword ptr [rip + andar_ptr], r14
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbx
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
    add eax, 8
    cvtsi2ss xmm0, eax
    movss dword ptr [rip + icaro + POS_Y], xmm0
.fim_ponto:
    add rsp, 8
    ret

# Atualiza uma personagem. As teclas apontam para a tela (W sobe na tela);
# o vetor é levado para o chão isométrico, normalizado, e cada eixo do mundo
# é testado separadamente para deslizar nas paredes.
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
    xor ebx, ebx                   # entrada horizontal na tela: D - A
    xor r13d, r13d                 # entrada vertical na tela: S - W

    mov edi, dword ptr [r12 + TECLA_ESQUERDA]
    call tecla_movimento
    movzx eax, al
    sub ebx, eax
    mov edi, dword ptr [r12 + TECLA_DIREITA]
    call tecla_movimento
    movzx eax, al
    add ebx, eax
    mov edi, dword ptr [r12 + TECLA_CIMA]
    call tecla_movimento
    movzx eax, al
    sub r13d, eax
    mov edi, dword ptr [r12 + TECLA_BAIXO]
    call tecla_movimento
    movzx eax, al
    add r13d, eax

    mov dword ptr [r12 + ANDANDO], 0
    mov eax, ebx
    or eax, r13d
    jz .fim_atualizacao

    # Tela -> mundo: dx = ty + tx/2, dy = ty - tx/2; depois normaliza.
    # Com duas teclas, tx vale o dobro: a diagonal da tela vira um eixo do
    # chão (W+D anda para o norte do mapa, rente às paredes).
    cvtsi2ss xmm0, ebx
    test r13d, r13d
    jnz .diagonal_da_grade
    mulss xmm0, dword ptr [rip + meio]
.diagonal_da_grade:
    cvtsi2ss xmm1, r13d
    movss xmm2, xmm1
    addss xmm1, xmm0                 # dx
    subss xmm2, xmm0                 # dy
    movss dword ptr [rsp], xmm1
    movss dword ptr [rsp + 4], xmm2
    mulss xmm1, xmm1
    mulss xmm2, xmm2
    addss xmm1, xmm2
    sqrtss xmm1, xmm1
    movss xmm0, dword ptr [rip + delta_quadro]
    mulss xmm0, dword ptr [rip + velocidade]
    divss xmm0, xmm1
    movss xmm1, dword ptr [rsp]
    mulss xmm1, xmm0
    movss dword ptr [rsp], xmm1
    movss xmm1, dword ptr [rsp + 4]
    mulss xmm1, xmm0
    movss dword ptr [rsp + 4], xmm1

    # Índices da sprite pela direção na tela: N, NE, E, SE, S, SW, W, NW.
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

# xmm0=x, xmm1=y em px do mundo; eax=1 se o ponto cai em parede, vão ou móvel.
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
    je .testar_objetos
    cmp eax, CL_DEGRAU
    jne .solido
.testar_objetos:
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

atualizar_fade:
    movss xmm1, dword ptr [rip + delta_quadro]
    mulss xmm1, dword ptr [rip + velocidade_fade]
    movss xmm0, dword ptr [rip + fade_alfa]
    mov eax, dword ptr [rip + fade_fase]
    cmp eax, 1
    je .escurecer
    cmp eax, 2
    je .clarear
    cmp eax, 3
    je .escurecer_roteiro
    ret
.escurecer_roteiro:
    addss xmm0, xmm1
    ucomiss xmm0, dword ptr [rip + um]
    jb .guardar_fade
    mov dword ptr [rip + fade_fase], 4
    movss xmm0, dword ptr [rip + um]
    jmp .guardar_fade
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

# Posição de Ícaro na tela isométrica, elevação nos degraus e chave de profundidade.
atualizar_icaro_iso:
    sub rsp, 8
    xorps xmm0, xmm0
    movss dword ptr [rip + icaro_elevacao], xmm0
    cvttss2si edi, dword ptr [rip + icaro + POS_X]
    sar edi, 4
    cvttss2si esi, dword ptr [rip + icaro + POS_Y]
    sar esi, 4
    call classe_em
    cmp eax, CL_DEGRAU
    jne .sem_elevacao
    mov rax, qword ptr [rip + andar_ptr]
    mov ecx, dword ptr [rax + AND_ESCADA_PASSO]
    test ecx, ecx
    jz .sem_elevacao
    # e = (base * 16 - y) * passo / 16
    mov edx, dword ptr [rax + AND_ESCADA_BASE]
    shl edx, 4
    cvtsi2ss xmm0, edx
    subss xmm0, dword ptr [rip + icaro + POS_Y]
    cvtsi2ss xmm1, ecx
    mulss xmm0, xmm1
    mulss xmm0, dword ptr [rip + inverso_16]
    maxss xmm0, dword ptr [rip + zero]
    movss dword ptr [rip + icaro_elevacao], xmm0
.sem_elevacao:
    movss xmm0, dword ptr [rip + icaro + POS_X]
    movss xmm1, dword ptr [rip + icaro + POS_Y]
    movss xmm2, xmm0
    subss xmm2, xmm1
    addss xmm2, dword ptr [rip + origem_iso_x]
    movss dword ptr [rip + icaro_iso_x], xmm2
    addss xmm0, xmm1
    cvttss2si eax, xmm0
    mov dword ptr [rip + icaro_chave], eax
    mulss xmm0, dword ptr [rip + meio]
    subss xmm0, dword ptr [rip + icaro_elevacao]
    movss dword ptr [rip + icaro_iso_y], xmm0
    add rsp, 8
    ret

# Câmera presa à projeção do andar; num eixo menor que a tela, centralizada.
atualizar_camera:
    movss xmm0, dword ptr [rip + iso_max_x]
    subss xmm0, dword ptr [rip + iso_min_x]
    ucomiss xmm0, dword ptr [rip + vista_l]
    ja .camera_x_rola
    subss xmm0, dword ptr [rip + vista_l]
    mulss xmm0, dword ptr [rip + meio]
    addss xmm0, dword ptr [rip + iso_min_x]
    jmp .camera_x_pronta
.camera_x_rola:
    movss xmm0, dword ptr [rip + foco_x]
    subss xmm0, dword ptr [rip + metade_vista_l]
    maxss xmm0, dword ptr [rip + iso_min_x]
    movss xmm1, dword ptr [rip + iso_max_x]
    subss xmm1, dword ptr [rip + vista_l]
    minss xmm0, xmm1
.camera_x_pronta:
    movss dword ptr [rip + camera_x], xmm0
    mulss xmm0, dword ptr [rip + zoom]
    cvtss2si eax, xmm0
    neg eax
    cvtsi2ss xmm0, eax
    movss dword ptr [rip + desloc_x], xmm0

    movss xmm0, dword ptr [rip + iso_max_y]
    subss xmm0, dword ptr [rip + iso_min_y]
    ucomiss xmm0, dword ptr [rip + vista_a]
    ja .camera_y_rola
    subss xmm0, dword ptr [rip + vista_a]
    mulss xmm0, dword ptr [rip + meio]
    addss xmm0, dword ptr [rip + iso_min_y]
    jmp .camera_y_pronta
.camera_y_rola:
    movss xmm0, dword ptr [rip + foco_y]
    subss xmm0, dword ptr [rip + altura_foco]
    subss xmm0, dword ptr [rip + metade_vista_a]
    maxss xmm0, dword ptr [rip + iso_min_y]
    movss xmm1, dword ptr [rip + iso_max_y]
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
    cmp ebx, OS_ROTEIRO
    je .oscilar_roteiro
    cmp ebx, OS_ESTATICA
    je .oscilar_estatica
    movss xmm0, dword ptr [rip + um]
    jmp .fim_oscilacao
# Luzes do galpão: firmes até o disco sair da caixa; depois, falhando.
.oscilar_roteiro:
    cmp dword ptr [rip + perturbacao], 0
    jne .oscilar_falha
    movss xmm0, dword ptr [rip + um]
    jmp .fim_oscilacao
# Telas e o brilho delas: apagadas até a perturbação; depois, chiando.
.oscilar_estatica:
    cmp dword ptr [rip + perturbacao], 0
    jne .oscilar_tv
    xorps xmm0, xmm0
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

# Mapa de luz: ambiente escuro do andar + poças de luz elípticas no chão.
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
    # centro na tela: (x - y + origem, (x + y) / 2 - z)
    mov eax, dword ptr [rbx + LUZ_X]
    sub eax, dword ptr [rbx + LUZ_Y]
    add eax, ORIGEM_ISO_X
    cvtsi2ss xmm2, eax
    mov eax, dword ptr [rbx + LUZ_X]
    add eax, dword ptr [rbx + LUZ_Y]
    sar eax, 1
    sub eax, dword ptr [rbx + LUZ_Z]
    cvtsi2ss xmm3, eax
    cvtsi2ss xmm1, dword ptr [rbx + LUZ_RAIO]
    movss xmm0, xmm2
    subss xmm0, xmm1
    movss dword ptr [rip + rec_destino], xmm0
    movss xmm4, xmm1
    mulss xmm4, dword ptr [rip + achatamento_luz]
    movss xmm0, xmm3
    subss xmm0, xmm4
    movss dword ptr [rip + rec_destino + 4], xmm0
    addss xmm1, xmm1
    movss dword ptr [rip + rec_destino + 8], xmm1
    addss xmm4, xmm4
    movss dword ptr [rip + rec_destino + 12], xmm4
    lea rdi, [rip + textura_luz]
    mov esi, r13d
    call desenhar_recorte
    add rbx, LUZ_TAM
    dec r12
    jmp .proxima_luz
.luz_icaro:
    movss xmm1, dword ptr [rip + raio_luz_icaro]
    movss xmm0, dword ptr [rip + icaro_iso_x]
    subss xmm0, xmm1
    movss dword ptr [rip + rec_destino], xmm0
    movss xmm0, dword ptr [rip + icaro_iso_y]
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

# Losangos do chão, com sombra junto às paredes de pé ao norte e a oeste.
desenhar_pisos:
    push rbx
    push r12
    push r13
    push r14
    push r15
    mov dword ptr [rip + cor_atual], -1
    xor r13d, r13d
.piso_linha:
    xor r12d, r12d
.piso_coluna:
    mov edi, r12d
    mov esi, r13d
    call info_tile
    test rax, rax
    jz .proximo_piso
    mov rbx, rax
    mov eax, dword ptr [rbx + TT_CLASSE]
    cmp eax, CL_PAREDE
    je .proximo_piso
    cmp eax, CL_DEGRAU
    jne .piso_plano
    mov rax, qword ptr [rip + andar_ptr]
    cmp dword ptr [rax + AND_ESCADA_PASSO], 0
    jne .proximo_piso                # degraus elevados são blocos na lista de profundidade
.piso_plano:
    # variante por um hash fixo da posição
    mov eax, r12d
    imul eax, eax, 7
    mov ecx, r13d
    imul ecx, ecx, 13
    add eax, ecx
    mov ecx, r12d
    imul ecx, r13d
    add eax, ecx
    xor edx, edx
    div dword ptr [rbx + TT_VARIANTES]
    imul r14d, edx, 34
    add r14d, dword ptr [rbx + TT_SX]
    mov edi, r12d
    mov esi, r13d
    call iso_tile
    lea r8d, [rax - 16]
    mov r9d, edx
    mov r15d, r8d
    mov edi, r14d
    mov esi, dword ptr [rbx + TT_SY]
    mov edx, 32
    mov ecx, 16
    call desenhar_atlas
    cmp dword ptr [rbx + TT_CLASSE], CL_PISO
    jne .proximo_piso
    # sombra da parede ao norte
    mov edi, r12d
    lea esi, [r13 - 1]
    call parede_alta
    test eax, eax
    jz .sem_sombra_norte
    mov edi, r12d
    mov esi, r13d
    call iso_tile
    lea r8d, [rax - 16]
    mov r9d, edx
    mov edi, S_SOMBRA_NORTE_X
    mov esi, S_SOMBRA_NORTE_Y
    mov edx, 32
    mov ecx, 16
    call desenhar_atlas
.sem_sombra_norte:
    lea edi, [r12 - 1]
    mov esi, r13d
    call parede_alta
    test eax, eax
    jz .proximo_piso
    mov edi, r12d
    mov esi, r13d
    call iso_tile
    lea r8d, [rax - 16]
    mov r9d, edx
    mov edi, S_SOMBRA_OESTE_X
    mov esi, S_SOMBRA_OESTE_Y
    mov edx, 32
    mov ecx, 16
    call desenhar_atlas
.proximo_piso:
    inc r12d
    cmp r12d, LARGURA_MAPA
    jl .piso_coluna
    inc r13d
    cmp r13d, ALTURA_MAPA
    jl .piso_linha
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbx
    ret

# edi=tx, esi=ty -> eax=1 se ali há parede alta (projeta sombra no chão).
parede_alta:
    call info_tile
    test rax, rax
    jz .nao_alta
    cmp dword ptr [rax + TT_CLASSE], CL_PAREDE
    jne .nao_alta
    cmp dword ptr [rax + TT_ALTURA], 40
    jl .nao_alta
    mov eax, 1
    ret
.nao_alta:
    xor eax, eax
    ret

# edi=tx, esi=ty da parede. Decide quais faces aparecem e como desenhá-la:
# paredes sem face visível (as da frente do prédio) ficam baixas; as que ficam
# entre a câmera e Ícaro mantêm a altura e ficam transparentes.
# Preenche parede_sul, parede_leste, parede_altura e parede_mascara.
estado_parede:
    push rbx
    push r12
    push r13
    mov r12d, edi
    mov r13d, esi
    call info_tile
    mov rbx, rax
    mov edi, r12d
    lea esi, [r13 + 1]
    call e_chao
    mov dword ptr [rip + parede_sul], eax
    lea edi, [r12 + 1]
    mov esi, r13d
    call e_chao
    mov dword ptr [rip + parede_leste], eax
    mov eax, dword ptr [rbx + TT_ALTURA]
    mov dword ptr [rip + parede_altura], eax
    mov dword ptr [rip + parede_mascara], MASCARA_OPACA
    mov ecx, dword ptr [rip + parede_sul]
    or ecx, dword ptr [rip + parede_leste]
    jz .rebaixar
    # transparência: centro da parede à frente de Ícaro e perto dele na tela
    mov eax, r12d
    add eax, r13d
    shl eax, 4
    add eax, TILE
    sub eax, dword ptr [rip + icaro_chave]
    cmp eax, 4
    jle .estado_pronto
    cmp eax, 8 * TILE
    jge .estado_pronto
    mov eax, r12d
    sub eax, r13d
    shl eax, 4
    cvttss2si ecx, dword ptr [rip + icaro + POS_X]
    sub eax, ecx
    cvttss2si ecx, dword ptr [rip + icaro + POS_Y]
    add eax, ecx
    mov ecx, eax
    neg ecx
    cmovs ecx, eax                   # ecx = |diferença horizontal na tela|
    cmp ecx, 5 * TILE
    jge .estado_pronto
    mov dword ptr [rip + parede_mascara], MASCARA_TRANSPARENTE
    jmp .estado_pronto
.rebaixar:
    mov eax, dword ptr [rip + parede_altura]
    cmp eax, ALTURA_CORTE
    jle .estado_pronto
    mov dword ptr [rip + parede_altura], ALTURA_CORTE
.estado_pronto:
    pop r13
    pop r12
    pop rbx
    ret

# edi=tx, esi=ty da parede, edx=tx, ecx=ty do chão encarado, r8 = tipo da parede.
# rax <- papel de parede da face.
papel_da_face:
    push rbx
    mov rbx, r8
    mov eax, dword ptr [rbx + TT_PAPEL]
    cmp eax, PAPEL_VIZINHO
    je .papel_do_vizinho
    # papel próprio (janelas): varia ao longo da parede
    mov r9d, eax
    lea eax, [rdi + rsi]
    xor edx, edx
    div dword ptr [rbx + TT_VARIANTES]
    lea eax, [r9 + rdx]
    jmp .papel_pronto
.papel_do_vizinho:
    mov edi, edx
    mov esi, ecx
    call info_tile
    test rax, rax
    jz .papel_padrao
    mov eax, dword ptr [rax + TT_PAPEL]
    jmp .papel_pronto
.papel_padrao:
    xor eax, eax
.papel_pronto:
    imul eax, eax, PP_TAM
    lea rdx, [rip + papeis]
    add rax, rdx
    pop rbx
    ret

# rdi = papel, esi = face, edx = altura, ecx = iso_x, r8d = iso_y do tile,
# r9d = 1 para desenhar o brilho em vez da parede. A face é recortada de baixo
# para cima, então a mesma imagem serve para parede cheia, rebaixada ou degrau.
desenhar_face:
    sub rsp, 8
    mov eax, PP_SUL_X
    cmp esi, FACE_SUL
    je .face_coluna
    mov eax, PP_LESTE_X
.face_coluna:
    test r9d, r9d
    jz .face_origem
    add eax, PP_BRILHO_SUL_X
.face_origem:
    mov r10d, dword ptr [rdi + rax]
    cmp r10d, -1
    je .face_vazia
    mov r11d, dword ptr [rdi + rax + 4]
    add r11d, ALTURA_PAREDE
    sub r11d, edx                    # origem y = sy + 48 - h
    mov r9d, r8d
    sub r9d, edx                     # destino y = iso_y - h
    lea r8d, [rcx - 16]
    lea ecx, [rdx + 16]
    mov edx, 32
    mov edi, r10d
    mov esi, r11d
    call desenhar_atlas
.face_vazia:
    add rsp, 8
    ret

# edi=tx, esi=ty, edx=face, ecx=camada. Desenha a fatia de cada decalque
# daquela camada que cobre esta face. Na camada emissiva respeita Ícaro na frente.
desenhar_decalques:
    push rbp
    mov rbp, rsp
    push rbx
    push r12
    push r13
    push r14
    push r15
    sub rsp, 40
    mov r12d, edi
    mov r13d, esi
    mov r14d, edx
    mov r15d, ecx
    call iso_tile
    mov dword ptr [rsp], eax
    mov dword ptr [rsp + 4], edx
    mov rax, qword ptr [rip + andar_ptr]
    mov rbx, qword ptr [rax + AND_DECALQUES]
    mov rcx, qword ptr [rax + AND_N_DECALQUES]
    mov qword ptr [rsp + 8], rcx
.proximo_decalque:
    cmp qword ptr [rsp + 8], 0
    je .fim_decalques
    cmp dword ptr [rbx + DC_CAMADA], r15d
    jne .pular_decalque
    cmp dword ptr [rbx + DC_FACE], r14d
    jne .pular_decalque
    cmp r14d, FACE_SUL
    jne .decalque_leste
    # face sul: mesma linha, coluna dentro do decalque; fatia k = tx - tx0
    cmp dword ptr [rbx + DC_TY], r13d
    jne .pular_decalque
    mov eax, r12d
    sub eax, dword ptr [rbx + DC_TX]
    js .pular_decalque
    cmp eax, dword ptr [rbx + DC_N]
    jge .pular_decalque
    mov edi, eax
    shl edi, 4
    add edi, dword ptr [rbx + DC_SX]
    mov esi, eax
    shl esi, 3
    add esi, dword ptr [rbx + DC_SY]
    mov r8d, dword ptr [rsp]
    sub r8d, 16
    jmp .fatia_pronta
.decalque_leste:
    # face leste: mesma coluna; fatia m = ty - ty0, lida da direita para a esquerda
    cmp dword ptr [rbx + DC_TX], r12d
    jne .pular_decalque
    mov eax, r13d
    sub eax, dword ptr [rbx + DC_TY]
    js .pular_decalque
    cmp eax, dword ptr [rbx + DC_N]
    jge .pular_decalque
    mov esi, eax
    shl esi, 3
    add esi, dword ptr [rbx + DC_SY]
    mov edi, dword ptr [rbx + DC_N]
    sub edi, 1
    sub edi, eax
    shl edi, 4
    add edi, dword ptr [rbx + DC_SX]
    mov r8d, dword ptr [rsp]
.fatia_pronta:
    # [rsp+16..32]: origem x, origem y, destino x, destino y, altura da fatia
    mov dword ptr [rsp + 16], edi
    mov dword ptr [rsp + 20], esi
    mov dword ptr [rsp + 24], r8d
    mov eax, dword ptr [rsp + 4]
    add eax, 8
    sub eax, dword ptr [rbx + DC_ZTOPO]
    mov dword ptr [rsp + 28], eax
    mov eax, dword ptr [rbx + DC_N]
    dec eax
    shl eax, 3
    neg eax
    add eax, dword ptr [rbx + DC_SA]     # altura da fatia = A - 8 (N - 1)
    mov dword ptr [rsp + 32], eax
    cmp r15d, CAM_EMISSIVA
    jne .fatia_cor
    # Ícaro na frente do decalque esconde o brilho
    lea edi, [r12 + r13]
    shl edi, 4
    add edi, TILE
    mov esi, dword ptr [rsp + 24]
    mov edx, dword ptr [rsp + 28]
    mov ecx, 16
    mov r8d, dword ptr [rsp + 32]
    call sobrepoe_icaro
    test eax, eax
    jnz .pular_decalque
.fatia_cor:
    mov eax, dword ptr [rip + parede_mascara]
    mov dword ptr [rip + cor_atual], eax
    mov edi, dword ptr [rbx + DC_OSC]
    test edi, edi
    jz .fatia_desenho
    cvtsi2ss xmm0, r12d
    call oscilacao
    mov edi, -1
    call escalar_cor
    and eax, dword ptr [rip + parede_mascara]
    mov dword ptr [rip + cor_atual], eax
.fatia_desenho:
    mov edi, dword ptr [rsp + 16]
    mov esi, dword ptr [rsp + 20]
    mov edx, 16
    mov ecx, dword ptr [rsp + 32]
    mov r8d, dword ptr [rsp + 24]
    mov r9d, dword ptr [rsp + 28]
    call desenhar_atlas
    mov dword ptr [rip + cor_atual], -1
.pular_decalque:
    add rbx, DC_TAM
    dec qword ptr [rsp + 8]
    jmp .proximo_decalque
.fim_decalques:
    add rsp, 40
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbx
    pop rbp
    ret

# edi = chave do que vai ser desenhado, esi,edx = canto, ecx,r8d = largura, altura
# (tela isométrica). eax=1 se Ícaro está na frente e o retângulo cobre a figura dele.
sobrepoe_icaro:
    xor eax, eax
    cmp edi, dword ptr [rip + icaro_chave]
    jge .fim_sobrepoe
    cvttss2si r9d, dword ptr [rip + icaro_iso_x]
    cvttss2si r10d, dword ptr [rip + icaro_iso_y]
    lea r11d, [rsi + rcx]
    sub r9d, 16
    cmp r11d, r9d
    jle .fim_sobrepoe
    add r9d, 32
    cmp esi, r9d
    jge .fim_sobrepoe
    lea r11d, [rdx + r8]
    lea r9d, [r10 - 46]
    cmp r11d, r9d
    jle .fim_sobrepoe
    cmp edx, r10d
    jge .fim_sobrepoe
    mov eax, 1
.fim_sobrepoe:
    ret

# edi = índice do tile. Parede (faces visíveis, decalques e topo) ou degrau elevado.
desenhar_bloco:
    push rbx
    push r12
    push r13
    push r14
    push r15
    sub rsp, 16
    mov eax, edi
    xor edx, edx
    mov ecx, LARGURA_MAPA
    div ecx
    mov r12d, edx                    # tx
    mov r13d, eax                    # ty
    mov edi, r12d
    mov esi, r13d
    call info_tile
    mov rbx, rax
    mov edi, r12d
    mov esi, r13d
    call iso_tile
    mov dword ptr [rsp], eax
    mov dword ptr [rsp + 4], edx
    mov dword ptr [rip + cor_atual], -1
    cmp dword ptr [rbx + TT_CLASSE], CL_DEGRAU
    je .bloco_degrau

    mov edi, r12d
    mov esi, r13d
    call estado_parede
    mov r14d, dword ptr [rip + parede_altura]
    cmp dword ptr [rip + parede_sul], 0
    je .bloco_leste
    mov edi, r12d
    mov esi, r13d
    mov edx, r12d
    lea ecx, [r13 + 1]
    mov r8, rbx
    call papel_da_face
    mov rdi, rax
    mov eax, dword ptr [rip + parede_mascara]
    mov dword ptr [rip + cor_atual], eax
    mov esi, FACE_SUL
    mov edx, r14d
    mov ecx, dword ptr [rsp]
    mov r8d, dword ptr [rsp + 4]
    xor r9d, r9d
    call desenhar_face
    cmp r14d, dword ptr [rbx + TT_ALTURA]
    jne .bloco_leste
    mov edi, r12d
    mov esi, r13d
    mov edx, FACE_SUL
    mov ecx, CAM_CHAO
    call desenhar_decalques
.bloco_leste:
    cmp dword ptr [rip + parede_leste], 0
    je .bloco_topo
    mov edi, r12d
    mov esi, r13d
    lea edx, [r12 + 1]
    mov ecx, r13d
    mov r8, rbx
    call papel_da_face
    mov rdi, rax
    mov eax, dword ptr [rip + parede_mascara]
    mov dword ptr [rip + cor_atual], eax
    mov esi, FACE_LESTE
    mov edx, r14d
    mov ecx, dword ptr [rsp]
    mov r8d, dword ptr [rsp + 4]
    xor r9d, r9d
    call desenhar_face
    cmp r14d, dword ptr [rbx + TT_ALTURA]
    jne .bloco_topo
    mov edi, r12d
    mov esi, r13d
    mov edx, FACE_LESTE
    mov ecx, CAM_CHAO
    call desenhar_decalques
.bloco_topo:
    mov eax, dword ptr [rip + parede_mascara]
    mov dword ptr [rip + cor_atual], eax
    mov edi, dword ptr [rbx + TT_SX]
    mov esi, dword ptr [rbx + TT_SY]
    mov edx, 32
    mov ecx, 16
    mov r8d, dword ptr [rsp]
    sub r8d, 16
    mov r9d, dword ptr [rsp + 4]
    sub r9d, r14d
    call desenhar_atlas
    jmp .fim_bloco

.bloco_degrau:
    # Degrau: caixa de madeira da altura da linha, com o piso do degrau em cima.
    mov edi, r13d
    call elevacao_linha
    mov r14d, eax
    lea r15, [rip + papeis]
    add r15, PAPEL_ESCADA * PP_TAM
    mov edi, r12d
    lea esi, [r13 + 1]
    call classe_em
    cmp eax, CL_PAREDE
    je .degrau_leste
    mov rdi, r15
    mov esi, FACE_SUL
    mov edx, r14d
    mov ecx, dword ptr [rsp]
    mov r8d, dword ptr [rsp + 4]
    xor r9d, r9d
    call desenhar_face
.degrau_leste:
    lea edi, [r12 + 1]
    mov esi, r13d
    call classe_em
    cmp eax, CL_PAREDE
    je .degrau_topo
    mov rdi, r15
    mov esi, FACE_LESTE
    mov edx, r14d
    mov ecx, dword ptr [rsp]
    mov r8d, dword ptr [rsp + 4]
    xor r9d, r9d
    call desenhar_face
.degrau_topo:
    mov eax, r12d
    imul eax, eax, 7
    add eax, r13d
    and eax, 3
    imul edi, eax, 34
    add edi, dword ptr [rbx + TT_SX]
    mov esi, dword ptr [rbx + TT_SY]
    mov edx, 32
    mov ecx, 16
    mov r8d, dword ptr [rsp]
    sub r8d, 16
    mov r9d, dword ptr [rsp + 4]
    sub r9d, r14d
    call desenhar_atlas
.fim_bloco:
    mov dword ptr [rip + cor_atual], -1
    add rsp, 16
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbx
    ret

# edi = camada. Desenha os objetos daquela camada na ordem da lista.
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

# Paredes, degraus e móveis em ordem de profundidade, com Ícaro no meio.
desenhar_itens:
    push rbx
    push r12
    sub rsp, 8
    call preparar_entes
    mov rax, qword ptr [rip + andar_ptr]
    mov rbx, qword ptr [rax + AND_ITENS]
    mov r12, qword ptr [rax + AND_N_ITENS]
.proximo_item:
    test r12, r12
    jz .fim_itens
    # Ícaro e atores mais ao fundo que este item vêm antes dele
    mov edi, dword ptr [rbx + IT_CHAVE]
    call desenhar_entes_ate
    cmp dword ptr [rbx + IT_TIPO], IT_OBJETO
    je .item_objeto_desenho
    mov edi, dword ptr [rbx + IT_DADO]
    call desenhar_bloco
    jmp .item_feito
.item_objeto_desenho:
    mov rdi, qword ptr [rbx + IT_DADO]
    call desenhar_objeto
.item_feito:
    add rbx, IT_TAM
    dec r12
    jmp .proximo_item
.fim_itens:
    call desenhar_entes_resto
    add rsp, 8
    pop r12
    pop rbx
    ret

# rdi = objeto. O vértice de baixo da pegada cai na âncora do sprite.
desenhar_objeto:
    push rbx
    push r12
    push r13
    sub rsp, 16
    mov rbx, rdi
    mov eax, dword ptr [rbx + OBJ_FX]
    add eax, dword ptr [rbx + OBJ_FW]
    mov ecx, dword ptr [rbx + OBJ_FY]
    add ecx, dword ptr [rbx + OBJ_FD]
    mov edx, eax
    sub edx, ecx
    add edx, ORIGEM_ISO_X
    mov r12d, edx                    # âncora x na tela
    add eax, ecx
    sar eax, 1
    sub eax, dword ptr [rbx + OBJ_Z]
    mov r13d, eax                    # âncora y na tela
    mov dword ptr [rsp], r12d
    mov dword ptr [rsp + 4], r13d
    sub r12d, dword ptr [rbx + OBJ_AX]
    sub r13d, dword ptr [rbx + OBJ_AY]
    cmp dword ptr [rip + checar_oclusao], 0
    je .objeto_visivel
    mov edi, dword ptr [rbx + OBJ_CHAVE]
    mov esi, r12d
    mov edx, r13d
    mov ecx, dword ptr [rbx + OBJ_SL]
    mov r8d, dword ptr [rbx + OBJ_SA]
    call sobrepoe_icaro
    test eax, eax
    jnz .fim_objeto
.objeto_visivel:
    mov dword ptr [rip + cor_atual], -1
    mov edi, dword ptr [rbx + OBJ_OSC]
    test edi, edi
    jz .cor_objeto_pronta
    cvtsi2ss xmm0, dword ptr [rbx + OBJ_FX]
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
    mov r8d, r12d
    mov r9d, r13d
    call desenhar_atlas
    cmp dword ptr [rbx + OBJ_ANIM], AN_DISCO
    jne .fim_objeto
    mov edi, dword ptr [rsp]
    mov esi, dword ptr [rsp + 4]
    call desenhar_reflexo_disco
    jmp .fim_objeto
.objeto_notas:
    mov rdi, rbx
    mov esi, r12d
    mov edx, r13d
    call desenhar_notas
.fim_objeto:
    mov dword ptr [rip + cor_atual], -1
    add rsp, 16
    pop r13
    pop r12
    pop rbx
    ret

# edi, esi = centro do vinil na tela. Dois reflexos dão a volta na elipse.
desenhar_reflexo_disco:
    push rbx
    push r12
    push r13
    sub rsp, 16
    mov ebx, edi
    mov r13d, esi
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
    cvtsi2ss xmm1, r13d
    addss xmm0, xmm1
    cvttss2si esi, xmm0
    cvtsi2ss xmm1, ebx
    addss xmm1, dword ptr [rsp + 4]
    cvttss2si edi, xmm1
    mov edx, 2
    mov ecx, 1
    mov r8d, 0xffb4a0a0
    call DrawRectangle
    inc r12d
    cmp r12d, 2
    jl .reflexo
    add rsp, 16
    pop r13
    pop r12
    pop rbx
    ret

# rdi = nota, esi,edx = canto do sprite. Três notas sobem da vitrola e somem.
desenhar_notas:
    push rbx
    push r12
    push r13
    push r14
    push r15
    sub rsp, 16
    mov rbx, rdi
    mov r14d, esi
    mov r15d, edx
    xor r12d, r12d
.nota:
    cvtsi2ss xmm0, r12d
    mulss xmm0, dword ptr [rip + um_terco]
    movss xmm1, dword ptr [rip + tempo]
    mulss xmm1, dword ptr [rip + notas_ritmo]
    addss xmm0, xmm1
    cvttss2si eax, xmm0
    cvtsi2ss xmm1, eax
    subss xmm0, xmm1
    movss dword ptr [rsp], xmm0
    mulss xmm0, dword ptr [rip + dois_pi]
    cvtsi2ss xmm1, r12d
    mulss xmm1, dword ptr [rip + notas_fase]
    addss xmm0, xmm1
    call sinf
    mulss xmm0, dword ptr [rip + notas_balanco]
    cvtsi2ss xmm1, r14d
    addss xmm0, xmm1
    cvttss2si r13d, xmm0
    movss xmm0, dword ptr [rsp]
    mulss xmm0, dword ptr [rip + notas_subida]
    cvtsi2ss xmm1, r15d
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
    mov r8d, r13d
    mov r9d, dword ptr [rsp + 8]
    call desenhar_atlas
    inc r12d
    cmp r12d, 3
    jl .nota
    add rsp, 16
    pop r15
    pop r14
    pop r13
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
    cvttss2si r8d, dword ptr [rip + icaro_iso_x]
    sub r8d, 8
    cvttss2si r9d, dword ptr [rip + icaro_iso_y]
    sub r9d, 4
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
    movss xmm0, dword ptr [rip + icaro_iso_x]
    subss xmm0, dword ptr [rip + ancora_x]
    movss dword ptr [rip + rec_destino], xmm0
    movss xmm0, dword ptr [rip + icaro_iso_y]
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

# Depois da luz: brilho das janelas, decalques emissivos e objetos emissivos.
desenhar_emissivos:
    push rbx
    push r12
    push r13
    push r14
    push r15
    sub rsp, 16
    mov dword ptr [rip + checar_oclusao], 1
    mov rax, qword ptr [rip + andar_ptr]
    mov rbx, qword ptr [rax + AND_ITENS]
    mov r12, qword ptr [rax + AND_N_ITENS]
.emissivo_item:
    test r12, r12
    jz .emissivo_objetos
    cmp dword ptr [rbx + IT_TIPO], IT_BLOCO
    jne .proximo_emissivo
    mov eax, dword ptr [rbx + IT_DADO]
    xor edx, edx
    mov ecx, LARGURA_MAPA
    div ecx
    mov r13d, edx                    # tx
    mov r14d, eax                    # ty
    mov edi, r13d
    mov esi, r14d
    call info_tile
    mov r15, rax
    cmp dword ptr [r15 + TT_CLASSE], CL_PAREDE
    jne .proximo_emissivo
    mov edi, r13d
    mov esi, r14d
    call estado_parede
    mov eax, dword ptr [rip + parede_altura]
    cmp eax, dword ptr [r15 + TT_ALTURA]
    jne .proximo_emissivo            # parede rebaixada não mostra janela nem quadro
    cmp dword ptr [rip + parede_mascara], MASCARA_OPACA
    jne .proximo_emissivo            # nem a transparente
    mov edi, r13d
    mov esi, r14d
    call iso_tile
    mov dword ptr [rsp], eax
    mov dword ptr [rsp + 4], edx
    cmp dword ptr [rip + parede_sul], 0
    je .emissivo_leste
    mov edi, r13d
    mov esi, r14d
    mov edx, FACE_SUL
    call brilho_da_face
    mov edi, r13d
    mov esi, r14d
    mov edx, FACE_SUL
    mov ecx, CAM_EMISSIVA
    call desenhar_decalques
.emissivo_leste:
    mov edi, r13d
    mov esi, r14d
    call estado_parede
    cmp dword ptr [rip + parede_leste], 0
    je .proximo_emissivo
    mov edi, r13d
    mov esi, r14d
    mov edx, FACE_LESTE
    call brilho_da_face
    mov edi, r13d
    mov esi, r14d
    mov edx, FACE_LESTE
    mov ecx, CAM_EMISSIVA
    call desenhar_decalques
.proximo_emissivo:
    add rbx, IT_TAM
    dec r12
    jmp .emissivo_item
.emissivo_objetos:
    mov edi, CAM_EMISSIVA
    call desenhar_camada
    mov dword ptr [rip + checar_oclusao], 0
    add rsp, 16
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbx
    ret

# edi=tx, esi=ty, edx=face de uma parede cheia: desenha o brilho do papel, se houver.
brilho_da_face:
    push rbx
    push r12
    push r13
    push r14
    push r15
    sub rsp, 16
    mov r12d, edi
    mov r13d, esi
    mov r14d, edx
    call info_tile
    mov r8, rax
    mov edi, r12d
    mov esi, r13d
    mov edx, r12d
    lea ecx, [r13 + 1]
    cmp r14d, FACE_SUL
    je .brilho_papel
    lea edx, [r12 + 1]
    mov ecx, r13d
.brilho_papel:
    call papel_da_face
    mov rbx, rax
    mov eax, PP_BRILHO_SUL_X
    cmp r14d, FACE_SUL
    je .brilho_existe
    mov eax, PP_BRILHO_LESTE_X
.brilho_existe:
    cmp dword ptr [rbx + rax], -1
    je .sem_brilho
    mov edi, r12d
    mov esi, r13d
    call iso_tile
    mov r15d, eax
    mov dword ptr [rsp], edx
    # Ícaro na frente da janela esconde o brilho
    lea edi, [r12 + r13]
    shl edi, 4
    add edi, TILE
    lea esi, [r15 - 16]
    mov edx, dword ptr [rsp]
    sub edx, ALTURA_PAREDE
    mov ecx, 32
    mov r8d, ALTURA_PAREDE + 16
    call sobrepoe_icaro
    test eax, eax
    jnz .sem_brilho
    mov dword ptr [rip + cor_atual], -1
    mov rdi, rbx
    mov esi, r14d
    mov edx, ALTURA_PAREDE
    mov ecx, r15d
    mov r8d, dword ptr [rsp]
    mov r9d, 1
    call desenhar_face
.sem_brilho:
    add rsp, 16
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbx
    ret

# edi,esi = (x0,y0) e edx,ecx = (x1,y1) em px do mundo; r8d = cor. Linha na tela isométrica.
linha_mundo:
    sub rsp, 8
    mov r9d, edi
    sub r9d, esi
    add r9d, ORIGEM_ISO_X
    lea r10d, [rdi + rsi]
    sar r10d, 1
    mov r11d, edx
    sub r11d, ecx
    add r11d, ORIGEM_ISO_X
    lea eax, [rdx + rcx]
    sar eax, 1
    mov edi, r9d
    mov esi, r10d
    mov edx, r11d
    mov ecx, eax
    call DrawLine
    add rsp, 8
    ret

# edi,esi = canto, edx,ecx = largura e altura (px do mundo), r8d = cor.
retangulo_mundo:
    push rbx
    push r12
    push r13
    push r14
    push r15
    mov r12d, edi
    mov r13d, esi
    lea r14d, [rdi + rdx]
    lea r15d, [rsi + rcx]
    mov ebx, r8d
    mov edi, r12d
    mov esi, r13d
    mov edx, r14d
    mov ecx, r13d
    mov r8d, ebx
    call linha_mundo
    mov edi, r14d
    mov esi, r13d
    mov edx, r14d
    mov ecx, r15d
    mov r8d, ebx
    call linha_mundo
    mov edi, r14d
    mov esi, r15d
    mov edx, r12d
    mov ecx, r15d
    mov r8d, ebx
    call linha_mundo
    mov edi, r12d
    mov esi, r15d
    mov edx, r12d
    mov ecx, r13d
    mov r8d, ebx
    call linha_mundo
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbx
    ret

# Modo de inspeção: tiles sólidos em magenta, móveis em ciano, escadas em amarelo.
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
    cmp eax, CL_DEGRAU
    je .proxima_colisao
    mov edi, r12d
    shl edi, 4
    mov esi, r13d
    shl esi, 4
    mov edx, TILE
    mov ecx, TILE
    mov r8d, 0x90ff00ff
    call retangulo_mundo
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
    call retangulo_mundo
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
    call retangulo_mundo
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
desenhar_hud:
    push rbx
    push r12
    push r13
    push r14
    push r15
    mov r13d, dword ptr [rip + fonte_hud]
    mov r15d, dword ptr [rip + altura_tela]
    sub r15d, dword ptr [rip + altura_hud]
    mov r14d, dword ptr [rip + altura_hud]
    sub r14d, r13d
    shr r14d, 1
    add r14d, r15d
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
