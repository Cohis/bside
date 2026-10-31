.intel_syntax noprefix

# Atores: personagens, anjos, clarões e os olhos de Mael.
# Cada ator tem pose (recorte em assets/personagens.png), posição no mundo e,
# se andar com conjunto de poses, troca de parado para caminhada sozinho.
# Na lista de profundidade, Ícaro e os atores entram juntos, ordenados por x + y.

.include "estruturas.inc"
.include "tileset.inc"

.equ ENTE_TAM, 16                    # chave (int), ponteiro do ator (0 = Ícaro)

.section .rodata
.align 4
um_a:           .float 1.0
escala_hd:      .float 0.094349      # 36,23 / 384: a redução da sprite do Ícaro
meio_a:         .float 0.5
zero_a:         .float 0.0
quase_parado:   .float 0.75          # px: chegou ao alvo
vel_pessoa:     .float 52.0

.section .bss
.align 16
.global atores
atores:         .skip MAX_ATORES * AT_TAM
entes:          .skip (MAX_ATORES + 1) * ENTE_TAM
n_entes:        .skip 4
proximo_ente:   .skip 4

.section .text
.global iniciar_atores
.global ator_ptr
.global mostrar_ator
.global ator_andar_ate
.global atualizar_atores
.global preparar_entes
.global desenhar_entes_ate
.global desenhar_entes_resto
.global desenhar_atores_emissivos
.global desenhar_pose_tela
.global ator_parado

.extern icaro_chave
.extern andar_indice
.extern delta_quadro
.extern textura_personagens
.extern textura_elenco_hd
.extern rec_origem
.extern rec_destino
.extern vec_pivo
.extern rotacao_atual
.extern desenhar_recorte
.extern desenhar_atlas
.extern desenhar_icaro
.extern cor_atual

# Todos escondidos.
iniciar_atores:
    lea rax, [rip + atores]
    mov ecx, MAX_ATORES
.esconder:
    mov dword ptr [rax + AT_ANDAR], -1
    mov dword ptr [rax + AT_MOVENDO], 0
    add rax, AT_TAM
    dec ecx
    jnz .esconder
    ret

# edi = índice -> rax = ator.
ator_ptr:
    mov eax, edi
    shl eax, 6
    lea rdx, [rip + atores]
    add rax, rdx
    ret

# edi = índice, esi = andar, xmm0, xmm1, xmm2 = x, y, z, rdx = conjunto ou 0,
# rcx = pose (usada se não houver conjunto), r8d = flags.
mostrar_ator:
    mov eax, edi
    shl eax, 6
    lea r9, [rip + atores]
    add r9, rax
    mov dword ptr [r9 + AT_ANDAR], esi
    movss dword ptr [r9 + AT_X], xmm0
    movss dword ptr [r9 + AT_Y], xmm1
    movss dword ptr [r9 + AT_Z], xmm2
    movss dword ptr [r9 + AT_ALVO_X], xmm0
    movss dword ptr [r9 + AT_ALVO_Y], xmm1
    movss dword ptr [r9 + AT_ALVO_Z], xmm2
    mov qword ptr [r9 + AT_CONJ], rdx
    test rdx, rdx
    jz .pose_direta
    mov rcx, qword ptr [rdx]         # parado, virado para o sul
    mov dword ptr [r9 + AT_DIR], 0
.pose_direta:
    mov qword ptr [r9 + AT_POSE], rcx
    mov dword ptr [r9 + AT_TEMPO], 0
    mov dword ptr [r9 + AT_MOVENDO], 0
    mov dword ptr [r9 + AT_FLAGS], r8d
    ret

# edi = índice, xmm0, xmm1, xmm2 = destino (x, y, z), xmm3 = velocidade (0 = passo de gente).
ator_andar_ate:
    mov eax, edi
    shl eax, 6
    lea r9, [rip + atores]
    add r9, rax
    movss dword ptr [r9 + AT_ALVO_X], xmm0
    movss dword ptr [r9 + AT_ALVO_Y], xmm1
    movss dword ptr [r9 + AT_ALVO_Z], xmm2
    ucomiss xmm3, dword ptr [rip + zero_a]
    ja .vel_dada
    movss xmm3, dword ptr [rip + vel_pessoa]
.vel_dada:
    movss dword ptr [r9 + AT_VEL], xmm3
    mov dword ptr [r9 + AT_MOVENDO], 1
    ret

# edi = índice -> eax = 1 se o ator já chegou (ou está escondido).
ator_parado:
    mov eax, edi
    shl eax, 6
    lea r9, [rip + atores]
    xor ecx, ecx
    cmp dword ptr [r9 + rax + AT_MOVENDO], 0
    sete cl
    mov eax, ecx
    ret

# Move, anima e escolhe a pose de cada ator visível.
atualizar_atores:
    push rbx
    push r12
    sub rsp, 24
    lea rbx, [rip + atores]
    mov r12d, MAX_ATORES
.ator:
    cmp dword ptr [rbx + AT_ANDAR], 0
    jl .proximo_ator
    movss xmm0, dword ptr [rbx + AT_TEMPO]
    addss xmm0, dword ptr [rip + delta_quadro]
    movss dword ptr [rbx + AT_TEMPO], xmm0

    cmp dword ptr [rbx + AT_MOVENDO], 0
    je .sem_movimento
    # vetor até o alvo
    movss xmm0, dword ptr [rbx + AT_ALVO_X]
    subss xmm0, dword ptr [rbx + AT_X]
    movss xmm1, dword ptr [rbx + AT_ALVO_Y]
    subss xmm1, dword ptr [rbx + AT_Y]
    movss xmm2, dword ptr [rbx + AT_ALVO_Z]
    subss xmm2, dword ptr [rbx + AT_Z]
    movss dword ptr [rsp], xmm0
    movss dword ptr [rsp + 4], xmm1
    movss dword ptr [rsp + 8], xmm2
    mulss xmm0, xmm0
    mulss xmm1, xmm1
    mulss xmm2, xmm2
    addss xmm0, xmm1
    addss xmm0, xmm2
    sqrtss xmm0, xmm0                # distância
    movss xmm3, dword ptr [rbx + AT_VEL]
    mulss xmm3, dword ptr [rip + delta_quadro]   # passo deste quadro
    ucomiss xmm0, xmm3
    ja .dar_passo
    # chegou
    movss xmm0, dword ptr [rbx + AT_ALVO_X]
    movss dword ptr [rbx + AT_X], xmm0
    movss xmm0, dword ptr [rbx + AT_ALVO_Y]
    movss dword ptr [rbx + AT_Y], xmm0
    movss xmm0, dword ptr [rbx + AT_ALVO_Z]
    movss dword ptr [rbx + AT_Z], xmm0
    mov dword ptr [rbx + AT_MOVENDO], 0
    jmp .sem_movimento
.dar_passo:
    divss xmm3, xmm0                 # fração do caminho
    movss xmm0, dword ptr [rsp]
    mulss xmm0, xmm3
    addss xmm0, dword ptr [rbx + AT_X]
    movss dword ptr [rbx + AT_X], xmm0
    movss xmm0, dword ptr [rsp + 4]
    mulss xmm0, xmm3
    addss xmm0, dword ptr [rbx + AT_Y]
    movss dword ptr [rbx + AT_Y], xmm0
    movss xmm0, dword ptr [rsp + 8]
    mulss xmm0, xmm3
    addss xmm0, dword ptr [rbx + AT_Z]
    movss dword ptr [rbx + AT_Z], xmm0
    # direção na tela: sx = dx - dy, sy = (dx + dy) / 2
    movss xmm0, dword ptr [rsp]
    subss xmm0, dword ptr [rsp + 4]  # sx
    movss xmm1, dword ptr [rsp]
    addss xmm1, dword ptr [rsp + 4]
    mulss xmm1, dword ptr [rip + meio_a]          # sy
    movaps xmm2, xmm0
    andps xmm2, xmmword ptr [rip + sem_sinal]
    movaps xmm3, xmm1
    andps xmm3, xmmword ptr [rip + sem_sinal]
    ucomiss xmm2, xmm3
    jbe .vertical
    mov eax, 1                       # leste
    ucomiss xmm0, dword ptr [rip + zero_a]
    ja .guardar_dir
    mov eax, 3                       # oeste
    jmp .guardar_dir
.vertical:
    xor eax, eax                     # sul
    ucomiss xmm1, dword ptr [rip + zero_a]
    ja .guardar_dir
    mov eax, 2                       # norte
.guardar_dir:
    cmp qword ptr [rbx + AT_CONJ], 0
    je .sem_movimento
    mov dword ptr [rbx + AT_DIR], eax

.sem_movimento:
    # pose do conjunto: parado (0..3) ou andando (4..7)
    mov rdx, qword ptr [rbx + AT_CONJ]
    test rdx, rdx
    jz .uma_vez
    mov eax, dword ptr [rbx + AT_DIR]
    cmp dword ptr [rbx + AT_MOVENDO], 0
    je .pose_conj
    add eax, 4
.pose_conj:
    mov rax, qword ptr [rdx + rax*8]
    mov qword ptr [rbx + AT_POSE], rax
.uma_vez:
    test dword ptr [rbx + AT_FLAGS], AF_UMA_VEZ
    jz .proximo_ator
    mov rdx, qword ptr [rbx + AT_POSE]
    cvtsi2ss xmm0, dword ptr [rdx + PS_FPS]
    mulss xmm0, dword ptr [rbx + AT_TEMPO]
    cvttss2si eax, xmm0
    cmp eax, dword ptr [rdx + PS_N]
    jl .proximo_ator
    mov dword ptr [rbx + AT_ANDAR], -1
.proximo_ator:
    add rbx, AT_TAM
    dec r12d
    jnz .ator
    add rsp, 24
    pop r12
    pop rbx
    ret

# rdi = ator -> eax = quadro atual da pose.
quadro_do_ator:
    mov rdx, qword ptr [rdi + AT_POSE]
    xor eax, eax
    mov ecx, dword ptr [rdx + PS_FPS]
    test ecx, ecx
    jz .quadro_pronto
    cvtsi2ss xmm0, ecx
    mulss xmm0, dword ptr [rdi + AT_TEMPO]
    cvttss2si eax, xmm0
    xor edx, edx
    mov rcx, qword ptr [rdi + AT_POSE]
    div dword ptr [rcx + PS_N]
    mov eax, edx
.quadro_pronto:
    ret

# rdi = ator. Sombra (se houver) e a pose na tela isométrica.
desenhar_ator:
    push rbx
    push r12
    push r13
    mov rbx, rdi
    # pés na tela: (x - y + origem, (x + y) / 2)
    movss xmm0, dword ptr [rbx + AT_X]
    subss xmm0, dword ptr [rbx + AT_Y]
    cvttss2si r12d, xmm0
    add r12d, ORIGEM_ISO_X
    movss xmm0, dword ptr [rbx + AT_X]
    addss xmm0, dword ptr [rbx + AT_Y]
    mulss xmm0, dword ptr [rip + meio_a]
    cvttss2si r13d, xmm0
    test dword ptr [rbx + AT_FLAGS], AF_SOMBRA
    jz .sem_sombra
    mov dword ptr [rip + cor_atual], -1
    mov edi, S_SOMBRA_PES_X
    mov esi, S_SOMBRA_PES_Y
    mov edx, S_SOMBRA_PES_L
    mov ecx, S_SOMBRA_PES_A
    lea r8d, [r12 - 8]
    lea r9d, [r13 - 4]
    call desenhar_atlas
.sem_sombra:
    cvttss2si eax, dword ptr [rbx + AT_Z]
    sub r13d, eax
    mov rdi, rbx
    call quadro_do_ator
    mov rdx, qword ptr [rbx + AT_POSE]
    imul eax, dword ptr [rdx + PS_L]
    add eax, dword ptr [rdx + PS_X]
    cvtsi2ss xmm0, eax
    movss dword ptr [rip + rec_origem], xmm0
    cvtsi2ss xmm0, dword ptr [rdx + PS_Y]
    movss dword ptr [rip + rec_origem + 4], xmm0
    # no atlas, 1 px da pose = 1 px do mundo; em alta resolução, reduz como o Ícaro
    movss xmm1, dword ptr [rip + um_a]
    lea rdi, [rip + textura_personagens]
    test dword ptr [rbx + AT_FLAGS], AF_HD
    jz .escala_pronta
    movss xmm1, dword ptr [rip + escala_hd]
    lea rdi, [rip + textura_elenco_hd]
.escala_pronta:
    cvtsi2ss xmm0, dword ptr [rdx + PS_L]
    movss dword ptr [rip + rec_origem + 8], xmm0
    mulss xmm0, xmm1
    movss dword ptr [rip + rec_destino + 8], xmm0
    cvtsi2ss xmm0, dword ptr [rdx + PS_A]
    movss dword ptr [rip + rec_origem + 12], xmm0
    mulss xmm0, xmm1
    movss dword ptr [rip + rec_destino + 12], xmm0
    cvtsi2ss xmm2, r12d
    cvtsi2ss xmm0, dword ptr [rdx + PS_AX]
    mulss xmm0, xmm1
    subss xmm2, xmm0
    movss dword ptr [rip + rec_destino], xmm2
    cvtsi2ss xmm2, r13d
    cvtsi2ss xmm0, dword ptr [rdx + PS_AY]
    mulss xmm0, xmm1
    subss xmm2, xmm0
    movss dword ptr [rip + rec_destino + 4], xmm2
    mov qword ptr [rip + vec_pivo], 0
    mov dword ptr [rip + rotacao_atual], 0
    mov esi, -1
    call desenhar_recorte
    pop r13
    pop r12
    pop rbx
    ret

# edi = x, esi = y na tela (canto de cima), edx = escala (inteira), rcx = pose, r8d = quadro.
# Desenha uma pose do atlas em coordenadas de tela (retratos, close, ícones).
desenhar_pose_tela:
    mov eax, r8d
    imul eax, dword ptr [rcx + PS_L]
    add eax, dword ptr [rcx + PS_X]
    cvtsi2ss xmm0, eax
    movss dword ptr [rip + rec_origem], xmm0
    cvtsi2ss xmm0, dword ptr [rcx + PS_Y]
    movss dword ptr [rip + rec_origem + 4], xmm0
    cvtsi2ss xmm0, dword ptr [rcx + PS_L]
    movss dword ptr [rip + rec_origem + 8], xmm0
    mov eax, dword ptr [rcx + PS_L]
    imul eax, edx
    cvtsi2ss xmm1, eax
    movss dword ptr [rip + rec_destino + 8], xmm1
    cvtsi2ss xmm0, dword ptr [rcx + PS_A]
    movss dword ptr [rip + rec_origem + 12], xmm0
    mov eax, dword ptr [rcx + PS_A]
    imul eax, edx
    cvtsi2ss xmm1, eax
    movss dword ptr [rip + rec_destino + 12], xmm1
    cvtsi2ss xmm0, edi
    movss dword ptr [rip + rec_destino], xmm0
    cvtsi2ss xmm0, esi
    movss dword ptr [rip + rec_destino + 4], xmm0
    mov qword ptr [rip + vec_pivo], 0
    mov dword ptr [rip + rotacao_atual], 0
    lea rdi, [rip + textura_personagens]
    mov esi, -1
    jmp desenhar_recorte

# Monta a lista de entes do quadro: Ícaro e os atores não emissivos deste andar.
preparar_entes:
    push rbx
    push r12
    lea r8, [rip + entes]
    mov eax, dword ptr [rip + icaro_chave]
    mov dword ptr [r8], eax
    mov qword ptr [r8 + 8], 0
    mov r9d, 1
    lea rbx, [rip + atores]
    mov r12d, MAX_ATORES
    mov r10d, dword ptr [rip + andar_indice]
.ente:
    cmp dword ptr [rbx + AT_ANDAR], r10d
    jne .proximo_ente
    test dword ptr [rbx + AT_FLAGS], AF_EMISSIVO
    jnz .proximo_ente
    movss xmm0, dword ptr [rbx + AT_X]
    addss xmm0, dword ptr [rbx + AT_Y]
    cvttss2si eax, xmm0
    # inserção ordenada
    mov ecx, r9d
.desloca:
    test ecx, ecx
    jz .insere
    lea edx, [rcx - 1]
    shl edx, 4
    cmp dword ptr [r8 + rdx], eax
    jle .insere
    movdqu xmm1, xmmword ptr [r8 + rdx]
    movdqu xmmword ptr [r8 + rdx + ENTE_TAM], xmm1
    dec ecx
    jmp .desloca
.insere:
    shl ecx, 4
    mov dword ptr [r8 + rcx], eax
    mov qword ptr [r8 + rcx + 8], rbx
    inc r9d
.proximo_ente:
    add rbx, AT_TAM
    dec r12d
    jnz .ente
    mov dword ptr [rip + n_entes], r9d
    mov dword ptr [rip + proximo_ente], 0
    pop r12
    pop rbx
    ret

# edi = chave do item que vai ser desenhado: antes dele, todo ente mais ao fundo.
desenhar_entes_ate:
    push rbx
    push r12
    sub rsp, 8
    mov r12d, edi
.ate:
    mov eax, dword ptr [rip + proximo_ente]
    cmp eax, dword ptr [rip + n_entes]
    jge .fim_ate
    shl eax, 4
    lea rbx, [rip + entes]
    add rbx, rax
    cmp dword ptr [rbx], r12d
    jge .fim_ate
    inc dword ptr [rip + proximo_ente]
    mov rdi, qword ptr [rbx + 8]
    test rdi, rdi
    jz .ente_icaro
    call desenhar_ator
    jmp .ate
.ente_icaro:
    call desenhar_icaro
    jmp .ate
.fim_ate:
    add rsp, 8
    pop r12
    pop rbx
    ret

desenhar_entes_resto:
    sub rsp, 8
    mov edi, 0x7fffffff
    call desenhar_entes_ate
    add rsp, 8
    ret

# Atores emissivos (clarões, olhos de Mael) por cima da luz.
desenhar_atores_emissivos:
    push rbx
    push r12
    sub rsp, 8
    lea rbx, [rip + atores]
    mov r12d, MAX_ATORES
.emissivo:
    mov eax, dword ptr [rip + andar_indice]
    cmp dword ptr [rbx + AT_ANDAR], eax
    jne .proximo_emissivo
    test dword ptr [rbx + AT_FLAGS], AF_EMISSIVO
    jz .proximo_emissivo
    mov rdi, rbx
    call desenhar_ator
.proximo_emissivo:
    add rbx, AT_TAM
    dec r12d
    jnz .emissivo
    add rsp, 8
    pop r12
    pop rbx
    ret

.section .rodata
.align 16
sem_sinal: .long 0x7fffffff, 0x7fffffff, 0x7fffffff, 0x7fffffff

.section .note.GNU-stack,"",@progbits
