.intel_syntax noprefix

# Roteiro da Fase 1: encadeia os objetivos (o pedido do Anderson na loja, achar o
# disco, sair do galpão, atravessar a doca), os eventos (a caixa que cai, estática,
# névoa, Mael na janela), as interações com E, a melodia que o jogador precisa
# tocar num lugar certo e as mensagens curtas do que Ícaro examina.
#
# Um programa é uma lista de comandos de 32 bytes (sala2.s). Há dois em execução:
# o principal e o da interação que o jogador acionou; o segundo pausa o primeiro.

.include "estruturas.inc"
.include "personagens.inc"

.equ PG_PC, 0
.equ PG_ESPERA, 8
.equ PG_T, 12
.equ PG_ARG, 16
.equ PG_RET, 24                      # retorno de CHAMA (um nível)
.equ PG_TAM, 32

.equ E_NADA, 0
.equ E_TEMPO, 1
.equ E_MENSAGEM, 2
.equ E_ESCURO, 3
.equ E_CLARO, 4
.equ E_FLAG, 5
.equ E_DOCA, 6

.equ TECLA_E, 69
.equ TECLA_ENTER, 257
.equ TECLA_ESPACO, 32

.section .rodata
variavel_cena:  .asciz "BSIDE_CENA"
variavel_sala:  .asciz "BSIDE_SALA"
variavel_ponto_r: .asciz "BSIDE_PONTO"
cena_galpao:    .asciz "galpao"
aviso_cena:     .asciz "BSIDE_CENA: rotulo nao encontrado; comecando do inicio."
texto_objetivo: .asciz "OBJETIVO"
.align 4
mil:            .float 1000.0
cem_r:          .float 100.0
vel_texto:      .float 60.0          # caracteres por segundo
um_rt:          .float 1.0
zero_rt:        .float 0.0
meio_rt:        .float 0.5
vel_nevoa:      .float 1.2
vel_flash:      .float 1.6
vel_foco:       .float 5.0
salto_foco:     .float 160.0
altura_cabeca:  .float 54.0
amp_tremor:     .float 3.0
freq_tremor_x:  .float 73.0
freq_tremor_y:  .float 91.0
nevoa_vel_1x:   .float 7.0
nevoa_vel_1y:   .float 2.5
nevoa_vel_2x:   .float -4.5
nevoa_vel_2y:   .float 1.5
nevoa_escala_2: .float 0.55
nevoa_parallax: .float 0.7
c_200:          .float 200.0
c_150:          .float 150.0
c_255r:         .float 255.0
origem_iso_r:   .float 352.0

.align 8
tabela_ops:
    .quad op_fim, op_mensagem, op_espera, op_escurece, op_clareia, op_andar, op_ator, op_ator_fixo
    .quad op_esconde, op_pose, op_ator_dir, op_teleporta, op_camera, op_som, op_musica, op_zumbido
    .quad op_nevoa, op_perturba, op_libera, op_trava, op_aguarda, op_flag, op_se_flag, op_salta
    .quad op_chama, op_volta, op_objetivo, op_interacoes, op_doca, op_rotulo, op_direcao, op_treme
    .quad op_clarao, op_move, op_melodia

.section .bss
.align 16
prog_principal: .skip PG_TAM
prog_interacao: .skip PG_TAM
.global flags
flags:          .skip N_FLAGS
texto_visivel:  .skip 512
.align 8
.global controle_jogador
.global controle_salvo
.global perturbacao
.global foco_x
.global foco_y
.global flash_alfa
.global flash_branco
.global tremor
mensagem:       .skip 8
objetivo:       .skip 8
interacoes:     .skip 8
interacao_atual: .skip 8
melodia:        .skip 8
melodia_passo:  .skip 4
n_interacoes:   .skip 4
controle_jogador: .skip 4
controle_salvo: .skip 4
mensagem_ativa: .skip 4
mensagem_mostrados: .skip 4          # float: caracteres já revelados
mensagem_total: .skip 4
e_consumido:    .skip 4
perturbacao:    .skip 4
nevoa_alfa:     .skip 4
nevoa_alvo:     .skip 4
flash_alfa:     .skip 4
flash_branco:   .skip 4
tremor:         .skip 4
foco_ativo:     .skip 4
foco_mx:        .skip 4
foco_my:        .skip 4
foco_x:         .skip 4              # alvo da câmera na tela isométrica (pés)
foco_y:         .skip 4
foco_pular:     .skip 4

.section .text
.global iniciar_roteiro
.global atualizar_roteiro
.global tecla_movimento
.global atualizar_foco
.global aplicar_tremor
.global desenhar_nevoa
.global desenhar_mundo_roteiro
.global desenhar_tela_roteiro
.global roteiro_ativo
.global teleportar

.extern roteiro_principal
.extern icaro
.extern icaro_iso_x
.extern icaro_iso_y
.extern tempo
.extern delta_quadro
.extern andar_indice
.extern andar_ptr
.extern andares
.extern comodo_nome
.extern fade_fase
.extern zoom
.extern largura_tela
.extern altura_tela
.extern altura_hud
.extern fonte_hud
.extern desloc_x
.extern desloc_y
.extern camera_x
.extern camera_y
.extern textura_nevoa
.extern rec_origem
.extern rec_destino
.extern vec_pivo
.extern rotacao_atual
.extern desenhar_recorte
.extern desenhar_pose_tela
.extern mostrar_ator
.extern ator_ptr
.extern ator_andar_ate
.extern nota_evento
.extern tocar_som
.extern volume_trilha
.extern volume_zumbido
.extern doca_iniciar
.extern doca_concluida
.extern atualizar_doca
.extern desenhar_doca_mundo
.extern desenhar_doca_tela
.extern pose_CLARAO
.extern pose_TECLA_E
.extern IsKeyDown
.extern IsKeyPressed
.extern DrawRectangle
.extern DrawRectangleLines
.extern DrawText
.extern MeasureText
.extern getenv
.extern strcmp
.extern puts
.extern sinf

# Escolhe por onde o roteiro começa. BSIDE_PONTO sem BSIDE_CENA mantém o
# passeio livre (só inspeção de cômodos).
iniciar_roteiro:
    push rbx
    push r12
    sub rsp, 8
    mov dword ptr [rip + foco_pular], 1
    lea rdi, [rip + variavel_cena]
    call getenv
    mov r12, rax
    test r12, r12
    jnz .com_cena
    lea rdi, [rip + variavel_sala]
    call getenv
    test rax, rax
    jz .sem_sala
    cmp byte ptr [rax], '2'
    jne .sem_sala
    lea r12, [rip + cena_galpao]
    jmp .com_cena
.sem_sala:
    lea rdi, [rip + variavel_ponto_r]
    call getenv
    test rax, rax
    jz .do_inicio
    mov dword ptr [rip + controle_jogador], 1
    mov dword ptr [rip + controle_salvo], 1
    jmp .fim_iniciar_r
.do_inicio:
    lea rax, [rip + roteiro_principal]
    mov qword ptr [rip + prog_principal + PG_PC], rax
    jmp .fim_iniciar_r
.com_cena:
    lea rbx, [rip + roteiro_principal]
.procurar_rotulo:
    mov eax, dword ptr [rbx + CMD_OP]
    cmp eax, OP_FIM
    je .rotulo_ausente
    cmp eax, OP_ROTULO
    jne .proximo_cmd
    mov rdi, qword ptr [rbx + CMD_P]
    mov rsi, r12
    call strcmp
    test eax, eax
    jz .rotulo_achado
.proximo_cmd:
    add rbx, CMD_TAM
    jmp .procurar_rotulo
.rotulo_ausente:
    lea rdi, [rip + aviso_cena]
    call puts
    lea rbx, [rip + roteiro_principal]
.rotulo_achado:
    mov qword ptr [rip + prog_principal + PG_PC], rbx
.fim_iniciar_r:
    add rsp, 8
    pop r12
    pop rbx
    ret

# eax = 1 enquanto o roteiro segura o controle (Ícaro não anda, escadas não disparam).
roteiro_ativo:
    xor eax, eax
    cmp dword ptr [rip + controle_jogador], 0
    sete al
    ret

# eax = 1 se E, Enter ou Espaço foram apertados neste quadro.
tecla_avancar:
    sub rsp, 8
    mov edi, TECLA_E
    call IsKeyPressed
    test al, al
    jnz .avancou
    mov edi, TECLA_ENTER
    call IsKeyPressed
    test al, al
    jnz .avancou
    mov edi, TECLA_ESPACO
    call IsKeyPressed
    test al, al
    jnz .avancou
    xor eax, eax
    add rsp, 8
    ret
.avancou:
    mov eax, 1
    add rsp, 8
    ret

# Substitui IsKeyDown para W, A, S, D: com o roteiro no controle, Ícaro fica parado.
tecla_movimento:
    cmp dword ptr [rip + controle_jogador], 0
    jne IsKeyDown
    xor eax, eax
    ret

# Um quadro do roteiro: mensagem, programas, interações e doca.
atualizar_roteiro:
    sub rsp, 8
    mov dword ptr [rip + e_consumido], 0
    call atualizar_mensagem
    cmp qword ptr [rip + prog_interacao + PG_PC], 0
    je .principal
    lea rdi, [rip + prog_interacao]
    call executar
    cmp qword ptr [rip + prog_interacao + PG_PC], 0
    jne .doca
    mov eax, dword ptr [rip + controle_salvo]
    mov dword ptr [rip + controle_jogador], eax
    jmp .doca
.principal:
    lea rdi, [rip + prog_principal]
    call executar
    call atualizar_interacoes
    call atualizar_melodia
.doca:
    call atualizar_doca
    call atualizar_efeitos
    add rsp, 8
    ret

atualizar_mensagem:
    sub rsp, 8
    cmp dword ptr [rip + mensagem_ativa], 0
    je .fim_mensagem
    movss xmm0, dword ptr [rip + delta_quadro]
    mulss xmm0, dword ptr [rip + vel_texto]
    addss xmm0, dword ptr [rip + mensagem_mostrados]
    movss dword ptr [rip + mensagem_mostrados], xmm0
    call tecla_avancar
    test eax, eax
    jz .fim_mensagem
    mov dword ptr [rip + e_consumido], 1
    cvtsi2ss xmm1, dword ptr [rip + mensagem_total]
    movss xmm0, dword ptr [rip + mensagem_mostrados]
    ucomiss xmm0, xmm1
    jae .fechar_mensagem
    movss dword ptr [rip + mensagem_mostrados], xmm1   # completa o texto
    jmp .fim_mensagem
.fechar_mensagem:
    mov dword ptr [rip + mensagem_ativa], 0
.fim_mensagem:
    add rsp, 8
    ret

# rdi = programa (prog_principal ou prog_interacao). Roda comandos até um esperar.
executar:
    push rbx
    push r12
    push r13
    mov rbx, rdi
.laco:
    mov r12, qword ptr [rbx + PG_PC]
    test r12, r12
    jz .sair
    mov eax, dword ptr [rbx + PG_ESPERA]
    cmp eax, E_NADA
    je .despachar
    cmp eax, E_TEMPO
    je .espera_tempo
    cmp eax, E_MENSAGEM
    je .espera_mensagem
    cmp eax, E_ESCURO
    je .espera_escuro
    cmp eax, E_CLARO
    je .espera_claro
    cmp eax, E_FLAG
    je .espera_flag
    cmp eax, E_DOCA
    je .espera_doca
    jmp .espera_cumprida
.espera_tempo:
    movss xmm0, dword ptr [rbx + PG_T]
    subss xmm0, dword ptr [rip + delta_quadro]
    movss dword ptr [rbx + PG_T], xmm0
    ucomiss xmm0, dword ptr [rip + zero_rt]
    ja .sair
    jmp .espera_cumprida
.espera_mensagem:
    cmp dword ptr [rip + mensagem_ativa], 0
    jne .sair
    jmp .espera_cumprida
.espera_escuro:
    cmp dword ptr [rip + fade_fase], 4
    jne .sair
    jmp .espera_cumprida
.espera_claro:
    cmp dword ptr [rip + fade_fase], 0
    jne .sair
    jmp .espera_cumprida
.espera_flag:
    mov eax, dword ptr [rbx + PG_ARG]
    lea rcx, [rip + flags]
    cmp byte ptr [rcx + rax], 0
    je .sair
    jmp .espera_cumprida
.espera_doca:
    cmp dword ptr [rip + doca_concluida], 0
    je .sair
.espera_cumprida:
    mov dword ptr [rbx + PG_ESPERA], E_NADA
.despachar:
    mov eax, dword ptr [r12 + CMD_OP]
    add qword ptr [rbx + PG_PC], CMD_TAM
    cmp eax, N_OPS
    jae .laco
    lea rcx, [rip + tabela_ops]
    jmp qword ptr [rcx + rax*8]
.sair:
    pop r13
    pop r12
    pop rbx
    ret

op_fim:
    mov qword ptr [rbx + PG_PC], 0
    jmp .sair

op_mensagem:
    mov rsi, qword ptr [r12 + CMD_P]
    mov qword ptr [rip + mensagem], rsi
    mov dword ptr [rip + mensagem_mostrados], 0
    # conta caracteres (bytes que não são continuação UTF-8)
    xor ecx, ecx
.contar:
    movzx eax, byte ptr [rsi]
    test eax, eax
    jz .contado
    inc rsi
    and eax, 0xc0
    cmp eax, 0x80
    je .contar
    inc ecx
    jmp .contar
.contado:
    mov dword ptr [rip + mensagem_total], ecx
    mov dword ptr [rip + mensagem_ativa], 1
    mov dword ptr [rbx + PG_ESPERA], E_MENSAGEM
    jmp .laco

op_espera:
    cvtsi2ss xmm0, dword ptr [r12 + CMD_A]
    divss xmm0, dword ptr [rip + mil]
    movss dword ptr [rbx + PG_T], xmm0
    mov dword ptr [rbx + PG_ESPERA], E_TEMPO
    jmp .laco

op_escurece:
    cmp dword ptr [rip + fade_fase], 4
    je .laco
    mov dword ptr [rip + fade_fase], 3
    mov dword ptr [rbx + PG_ESPERA], E_ESCURO
    jmp .laco

op_clareia:
    mov dword ptr [rip + fade_fase], 2
    mov dword ptr [rbx + PG_ESPERA], E_CLARO
    jmp .laco

op_andar:
    mov eax, dword ptr [r12 + CMD_A]
    mov dword ptr [rip + andar_indice], eax
    lea rdx, [rip + andares]
    mov rdx, qword ptr [rdx + rax*8]
    mov qword ptr [rip + andar_ptr], rdx
    mov qword ptr [rip + comodo_nome], 0
    cvtsi2ss xmm0, dword ptr [r12 + CMD_B]
    movss dword ptr [rip + icaro], xmm0
    cvtsi2ss xmm0, dword ptr [r12 + CMD_C]
    movss dword ptr [rip + icaro + 4], xmm0
    mov eax, dword ptr [r12 + CMD_D]
    mov dword ptr [rip + icaro + 8], eax
    mov dword ptr [rip + foco_pular], 1
    jmp .laco

op_ator:
    xor ecx, ecx
    mov rdx, qword ptr [r12 + CMD_P]
    jmp ator_comum
op_ator_fixo:
    xor edx, edx
    mov rcx, qword ptr [r12 + CMD_P]
ator_comum:
    mov edi, dword ptr [r12 + CMD_A]
    mov esi, dword ptr [r12 + CMD_B]
    mov r8d, esi
    shr r8d, 8                       # flags no byte de cima de B
    movsx esi, sil                   # andar (−1 aceito)
    cvtsi2ss xmm0, dword ptr [r12 + CMD_C]
    cvtsi2ss xmm1, dword ptr [r12 + CMD_D]
    cvtsi2ss xmm2, dword ptr [r12 + CMD_E]
    call mostrar_ator
    jmp .laco

op_esconde:
    mov edi, dword ptr [r12 + CMD_A]
    call ator_ptr
    mov dword ptr [rax + AT_ANDAR], -1
    jmp .laco

op_pose:
    mov edi, dword ptr [r12 + CMD_A]
    call ator_ptr
    mov rcx, qword ptr [r12 + CMD_P]
    mov qword ptr [rax + AT_POSE], rcx
    mov qword ptr [rax + AT_CONJ], 0
    mov dword ptr [rax + AT_TEMPO], 0
    jmp .laco

op_ator_dir:
    mov edi, dword ptr [r12 + CMD_A]
    call ator_ptr
    mov ecx, dword ptr [r12 + CMD_B]
    mov dword ptr [rax + AT_DIR], ecx
    jmp .laco

op_teleporta:
    mov edi, dword ptr [r12 + CMD_A]
    cvtsi2ss xmm0, dword ptr [r12 + CMD_B]
    cvtsi2ss xmm1, dword ptr [r12 + CMD_C]
    call teleportar
    jmp .laco

op_camera:
    mov eax, dword ptr [r12 + CMD_A]
    cmp eax, -1
    je .camera_solta
    mov dword ptr [rip + foco_ativo], 1
    cvtsi2ss xmm0, eax
    movss dword ptr [rip + foco_mx], xmm0
    cvtsi2ss xmm0, dword ptr [r12 + CMD_B]
    movss dword ptr [rip + foco_my], xmm0
    jmp .laco
.camera_solta:
    mov dword ptr [rip + foco_ativo], 0
    jmp .laco

op_som:
    mov edi, dword ptr [r12 + CMD_A]
    call tocar_som
    jmp .laco

op_musica:
    mov edi, dword ptr [r12 + CMD_A]
    call volume_trilha
    jmp .laco

op_zumbido:
    mov edi, dword ptr [r12 + CMD_A]
    call volume_zumbido
    jmp .laco

op_nevoa:
    cvtsi2ss xmm0, dword ptr [r12 + CMD_A]
    divss xmm0, dword ptr [rip + cem_r]
    movss dword ptr [rip + nevoa_alvo], xmm0
    jmp .laco

op_perturba:
    mov eax, dword ptr [r12 + CMD_A]
    mov dword ptr [rip + perturbacao], eax
    jmp .laco

op_libera:
    mov dword ptr [rip + controle_jogador], 1
    mov dword ptr [rip + controle_salvo], 1
    jmp .laco

op_trava:
    mov dword ptr [rip + controle_jogador], 0
    mov dword ptr [rip + controle_salvo], 0
    jmp .laco

op_aguarda:
    mov eax, dword ptr [r12 + CMD_A]
    mov dword ptr [rbx + PG_ARG], eax
    mov dword ptr [rbx + PG_ESPERA], E_FLAG
    jmp .laco

op_flag:
    mov eax, dword ptr [r12 + CMD_A]
    lea rcx, [rip + flags]
    mov byte ptr [rcx + rax], 1
    jmp .laco

op_se_flag:
    mov eax, dword ptr [r12 + CMD_A]
    lea rcx, [rip + flags]
    cmp byte ptr [rcx + rax], 0
    je .laco
op_salta:
    mov rax, qword ptr [r12 + CMD_P]
    mov qword ptr [rbx + PG_PC], rax
    jmp .laco

op_chama:
    mov rax, qword ptr [rbx + PG_PC]
    mov qword ptr [rbx + PG_RET], rax
    mov rax, qword ptr [r12 + CMD_P]
    mov qword ptr [rbx + PG_PC], rax
    jmp .laco

op_volta:
    mov rax, qword ptr [rbx + PG_RET]
    mov qword ptr [rbx + PG_PC], rax
    jmp .laco

op_objetivo:
    mov rax, qword ptr [r12 + CMD_P]
    mov qword ptr [rip + objetivo], rax
    jmp .laco

op_interacoes:
    mov rax, qword ptr [r12 + CMD_P]
    mov qword ptr [rip + interacoes], rax
    mov eax, dword ptr [r12 + CMD_A]
    mov dword ptr [rip + n_interacoes], eax
    jmp .laco

op_doca:
    mov rdi, qword ptr [r12 + CMD_P]
    call doca_iniciar
    mov dword ptr [rbx + PG_ESPERA], E_DOCA
    jmp .laco

op_rotulo:
    jmp .laco

op_direcao:
    mov eax, dword ptr [r12 + CMD_A]
    mov dword ptr [rip + icaro + 8], eax
    jmp .laco

op_treme:
    cvtsi2ss xmm0, dword ptr [r12 + CMD_A]
    divss xmm0, dword ptr [rip + mil]
    movss dword ptr [rip + tremor], xmm0
    jmp .laco

op_clarao:
    movss xmm0, dword ptr [rip + um_rt]
    movss dword ptr [rip + flash_alfa], xmm0
    mov eax, dword ptr [r12 + CMD_A]
    mov dword ptr [rip + flash_branco], eax
    jmp .laco

op_move:
    mov edi, dword ptr [r12 + CMD_A]
    cvtsi2ss xmm0, dword ptr [r12 + CMD_B]
    cvtsi2ss xmm1, dword ptr [r12 + CMD_C]
    cvtsi2ss xmm2, dword ptr [r12 + CMD_D]
    cvtsi2ss xmm3, dword ptr [r12 + CMD_E]
    call ator_andar_ate
    jmp .laco

op_melodia:
    mov rax, qword ptr [r12 + CMD_P]
    mov qword ptr [rip + melodia], rax
    mov dword ptr [rip + melodia_passo], 0
    jmp .laco

# edi = ator, xmm0, xmm1 = destino. Clarão azul onde ele estava e onde aparece.
teleportar:
    push rbx
    push r12
    sub rsp, 24
    movss dword ptr [rsp], xmm0
    movss dword ptr [rsp + 4], xmm1
    call ator_ptr
    mov rbx, rax
    mov edi, ATOR_CLARAO_A
    mov esi, dword ptr [rbx + AT_ANDAR]
    movss xmm0, dword ptr [rbx + AT_X]
    movss xmm1, dword ptr [rbx + AT_Y]
    xorps xmm2, xmm2
    xor edx, edx
    lea rcx, [rip + pose_CLARAO]
    mov r8d, AF_EMISSIVO | AF_UMA_VEZ
    call mostrar_ator
    movss xmm0, dword ptr [rsp]
    movss xmm1, dword ptr [rsp + 4]
    movss dword ptr [rbx + AT_X], xmm0
    movss dword ptr [rbx + AT_Y], xmm1
    movss dword ptr [rbx + AT_ALVO_X], xmm0
    movss dword ptr [rbx + AT_ALVO_Y], xmm1
    mov dword ptr [rbx + AT_MOVENDO], 0
    mov edi, ATOR_CLARAO_B
    mov esi, dword ptr [rbx + AT_ANDAR]
    xorps xmm2, xmm2
    xor edx, edx
    lea rcx, [rip + pose_CLARAO]
    mov r8d, AF_EMISSIVO | AF_UMA_VEZ
    call mostrar_ator
    mov edi, SOM_CLARAO
    call tocar_som
    add rsp, 24
    pop r12
    pop rbx
    ret

# Procura a interação sob os pés de Ícaro; automática dispara sozinha, as
# outras esperam E. Só vale com o jogador no controle e nada na tela.
atualizar_interacoes:
    push rbx
    push r12
    push r13
    mov qword ptr [rip + interacao_atual], 0
    cmp dword ptr [rip + controle_jogador], 0
    je .fim_interacoes
    cmp dword ptr [rip + mensagem_ativa], 0
    jne .fim_interacoes
    cmp dword ptr [rip + fade_fase], 0
    jne .fim_interacoes
    mov rbx, qword ptr [rip + interacoes]
    mov r12d, dword ptr [rip + n_interacoes]
    cvttss2si r8d, dword ptr [rip + icaro]
    cvttss2si r9d, dword ptr [rip + icaro + 4]
    lea r10, [rip + flags]
.interacao:
    test r12d, r12d
    jz .fim_interacoes
    mov eax, dword ptr [rip + andar_indice]
    cmp dword ptr [rbx + IN_ANDAR], eax
    jne .proxima_interacao
    movsxd rax, dword ptr [rbx + IN_EXIGE]
    test rax, rax
    js .sem_exigencia
    cmp byte ptr [r10 + rax], 0
    je .proxima_interacao
.sem_exigencia:
    movsxd rax, dword ptr [rbx + IN_SOME]
    test rax, rax
    js .sem_sumico
    cmp byte ptr [r10 + rax], 0
    jne .proxima_interacao
.sem_sumico:
    mov eax, dword ptr [rbx + IN_X]
    cmp r8d, eax
    jl .proxima_interacao
    add eax, dword ptr [rbx + IN_L]
    cmp r8d, eax
    jge .proxima_interacao
    mov eax, dword ptr [rbx + IN_Y]
    cmp r9d, eax
    jl .proxima_interacao
    add eax, dword ptr [rbx + IN_A]
    cmp r9d, eax
    jge .proxima_interacao
    mov qword ptr [rip + interacao_atual], rbx
    cmp qword ptr [rbx + IN_ROTULO], 0
    je .disparar
    cmp dword ptr [rip + e_consumido], 0
    jne .fim_interacoes
    mov edi, TECLA_E
    call IsKeyPressed
    test al, al
    jz .fim_interacoes
.disparar:
    mov rax, qword ptr [rbx + IN_PROGRAMA]
    mov qword ptr [rip + prog_interacao + PG_PC], rax
    mov dword ptr [rip + prog_interacao + PG_ESPERA], E_NADA
    mov eax, dword ptr [rip + controle_jogador]
    mov dword ptr [rip + controle_salvo], eax
    mov dword ptr [rip + controle_jogador], 0
    mov qword ptr [rip + interacao_atual], 0
    lea rdi, [rip + prog_interacao]
    call executar
    cmp qword ptr [rip + prog_interacao + PG_PC], 0
    jne .fim_interacoes
    mov eax, dword ptr [rip + controle_salvo]
    mov dword ptr [rip + controle_jogador], eax
    jmp .fim_interacoes
.proxima_interacao:
    add rbx, IN_TAM
    dec r12d
    jmp .interacao
.fim_interacoes:
    pop r13
    pop r12
    pop rbx
    ret

# Melodia armada: com Ícaro no retângulo, cada nota certa avança um passo e a
# errada recomeça (vale como 1º passo se for a primeira nota). Sem metrônomo.
# Completa, acende a flag e desarma. Sair do retângulo também recomeça.
atualizar_melodia:
    mov rdx, qword ptr [rip + melodia]
    test rdx, rdx
    jz .fim_melodia
    cmp dword ptr [rip + controle_jogador], 0
    je .fim_melodia
    cmp dword ptr [rip + mensagem_ativa], 0
    jne .fim_melodia
    cmp dword ptr [rip + fade_fase], 0
    jne .fim_melodia
    mov eax, dword ptr [rip + andar_indice]
    cmp dword ptr [rdx + MEL_ANDAR], eax
    jne .fim_melodia
    cvttss2si r8d, dword ptr [rip + icaro]
    cvttss2si r9d, dword ptr [rip + icaro + 4]
    mov eax, dword ptr [rdx + MEL_X]
    cmp r8d, eax
    jl .fora_melodia
    add eax, dword ptr [rdx + MEL_L]
    cmp r8d, eax
    jge .fora_melodia
    mov eax, dword ptr [rdx + MEL_Y]
    cmp r9d, eax
    jl .fora_melodia
    add eax, dword ptr [rdx + MEL_A]
    cmp r9d, eax
    jge .fora_melodia
    mov ecx, dword ptr [rip + nota_evento]
    test ecx, ecx
    js .fim_melodia
    mov eax, dword ptr [rip + melodia_passo]
    movzx r10d, byte ptr [rdx + MEL_NOTAS + rax]
    cmp ecx, r10d
    je .nota_certa
    movzx r10d, byte ptr [rdx + MEL_NOTAS]
    xor eax, eax
    cmp ecx, r10d
    sete al
    mov dword ptr [rip + melodia_passo], eax
    ret
.nota_certa:
    inc eax
    mov dword ptr [rip + melodia_passo], eax
    cmp eax, dword ptr [rdx + MEL_N]
    jl .fim_melodia
    movsxd rax, dword ptr [rdx + MEL_FLAG]
    lea rcx, [rip + flags]
    mov byte ptr [rcx + rax], 1
    mov qword ptr [rip + melodia], 0
    ret
.fora_melodia:
    mov dword ptr [rip + melodia_passo], 0
.fim_melodia:
    ret

# Névoa e flash aproximam-se dos alvos; o tremor se esgota.
atualizar_efeitos:
    movss xmm2, dword ptr [rip + delta_quadro]
    movss xmm0, dword ptr [rip + nevoa_alvo]
    subss xmm0, dword ptr [rip + nevoa_alfa]
    movss xmm1, xmm2
    mulss xmm1, dword ptr [rip + vel_nevoa]
    minss xmm1, dword ptr [rip + um_rt]
    mulss xmm0, xmm1
    addss xmm0, dword ptr [rip + nevoa_alfa]
    movss dword ptr [rip + nevoa_alfa], xmm0
    movss xmm0, dword ptr [rip + flash_alfa]
    movss xmm1, xmm2
    mulss xmm1, dword ptr [rip + vel_flash]
    subss xmm0, xmm1
    maxss xmm0, dword ptr [rip + zero_rt]
    movss dword ptr [rip + flash_alfa], xmm0
    movss xmm0, dword ptr [rip + tremor]
    subss xmm0, xmm2
    maxss xmm0, dword ptr [rip + zero_rt]
    movss dword ptr [rip + tremor], xmm0
    ret

# Alvo da câmera (pés, na tela isométrica): Ícaro ou o ponto que o roteiro pediu.
# Seguindo Ícaro, a câmera não atrasa; indo ou voltando de um ponto, desliza.
atualizar_foco:
    cmp dword ptr [rip + foco_ativo], 0
    je .foco_icaro
    movss xmm0, dword ptr [rip + foco_mx]
    subss xmm0, dword ptr [rip + foco_my]
    addss xmm0, dword ptr [rip + origem_iso_r]
    movss xmm1, dword ptr [rip + foco_mx]
    addss xmm1, dword ptr [rip + foco_my]
    mulss xmm1, dword ptr [rip + meio_rt]
    jmp .foco_desliza
.foco_icaro:
    movss xmm0, dword ptr [rip + icaro_iso_x]
    movss xmm1, dword ptr [rip + icaro_iso_y]
    movss xmm2, xmm0
    subss xmm2, dword ptr [rip + foco_x]
    andps xmm2, xmmword ptr [rip + sem_sinal_rt]
    ucomiss xmm2, dword ptr [rip + um_rt]
    jbe .foco_salta                  # já colada em Ícaro
.foco_desliza:
    cmp dword ptr [rip + foco_pular], 0
    jne .foco_salta
    movss xmm2, xmm0
    subss xmm2, dword ptr [rip + foco_x]
    andps xmm2, xmmword ptr [rip + sem_sinal_rt]
    ucomiss xmm2, dword ptr [rip + salto_foco]
    ja .foco_salta
    movss xmm3, dword ptr [rip + delta_quadro]
    mulss xmm3, dword ptr [rip + vel_foco]
    minss xmm3, dword ptr [rip + um_rt]
    subss xmm0, dword ptr [rip + foco_x]
    mulss xmm0, xmm3
    addss xmm0, dword ptr [rip + foco_x]
    subss xmm1, dword ptr [rip + foco_y]
    mulss xmm1, xmm3
    addss xmm1, dword ptr [rip + foco_y]
.foco_salta:
    movss dword ptr [rip + foco_x], xmm0
    movss dword ptr [rip + foco_y], xmm1
    mov dword ptr [rip + foco_pular], 0
    ret

# Depois de atualizar_camera: balança o deslocamento enquanto houver tremor.
aplicar_tremor:
    movss xmm0, dword ptr [rip + tremor]
    ucomiss xmm0, dword ptr [rip + zero_rt]
    jbe .sem_tremor
    sub rsp, 8
    movss xmm0, dword ptr [rip + tempo]
    mulss xmm0, dword ptr [rip + freq_tremor_x]
    call sinf
    mulss xmm0, dword ptr [rip + amp_tremor]
    mulss xmm0, dword ptr [rip + zoom]
    cvtss2si eax, xmm0
    cvtsi2ss xmm0, eax
    addss xmm0, dword ptr [rip + desloc_x]
    movss dword ptr [rip + desloc_x], xmm0
    movss xmm0, dword ptr [rip + tempo]
    mulss xmm0, dword ptr [rip + freq_tremor_y]
    call sinf
    mulss xmm0, dword ptr [rip + amp_tremor]
    mulss xmm0, dword ptr [rip + zoom]
    cvtss2si eax, xmm0
    cvtsi2ss xmm0, eax
    addss xmm0, dword ptr [rip + desloc_y]
    movss dword ptr [rip + desloc_y], xmm0
    add rsp, 8
.sem_tremor:
    ret

# Duas camadas da textura de névoa correndo em direções diferentes, em tela cheia.
desenhar_nevoa:
    movss xmm0, dword ptr [rip + nevoa_alfa]
    ucomiss xmm0, dword ptr [rip + zero_rt]
    jbe .sem_nevoa
    sub rsp, 8
    # camada 1: 1 texel por px do mundo
    cvtsi2ss xmm0, dword ptr [rip + largura_tela]
    divss xmm0, dword ptr [rip + zoom]
    movss dword ptr [rip + rec_origem + 8], xmm0
    mov eax, dword ptr [rip + altura_tela]
    sub eax, dword ptr [rip + altura_hud]
    cvtsi2ss xmm0, eax
    divss xmm0, dword ptr [rip + zoom]
    movss dword ptr [rip + rec_origem + 12], xmm0
    movss xmm0, dword ptr [rip + tempo]
    mulss xmm0, dword ptr [rip + nevoa_vel_1x]
    addss xmm0, dword ptr [rip + camera_x]
    movss dword ptr [rip + rec_origem], xmm0
    movss xmm0, dword ptr [rip + tempo]
    mulss xmm0, dword ptr [rip + nevoa_vel_1y]
    addss xmm0, dword ptr [rip + camera_y]
    movss dword ptr [rip + rec_origem + 4], xmm0
    call destino_nevoa
    movss xmm0, dword ptr [rip + nevoa_alfa]
    mulss xmm0, dword ptr [rip + c_200]
    call cor_nevoa
    mov esi, eax
    lea rdi, [rip + textura_nevoa]
    call desenhar_recorte
    # camada 2: manchas maiores e mais lentas, com parallax
    movss xmm0, dword ptr [rip + rec_origem + 8]
    mulss xmm0, dword ptr [rip + nevoa_escala_2]
    movss dword ptr [rip + rec_origem + 8], xmm0
    movss xmm0, dword ptr [rip + rec_origem + 12]
    mulss xmm0, dword ptr [rip + nevoa_escala_2]
    movss dword ptr [rip + rec_origem + 12], xmm0
    movss xmm0, dword ptr [rip + camera_x]
    mulss xmm0, dword ptr [rip + nevoa_parallax]
    movss xmm1, dword ptr [rip + tempo]
    mulss xmm1, dword ptr [rip + nevoa_vel_2x]
    addss xmm0, xmm1
    movss dword ptr [rip + rec_origem], xmm0
    movss xmm0, dword ptr [rip + camera_y]
    mulss xmm0, dword ptr [rip + nevoa_parallax]
    movss xmm1, dword ptr [rip + tempo]
    mulss xmm1, dword ptr [rip + nevoa_vel_2y]
    addss xmm0, xmm1
    movss dword ptr [rip + rec_origem + 4], xmm0
    call destino_nevoa
    movss xmm0, dword ptr [rip + nevoa_alfa]
    mulss xmm0, dword ptr [rip + c_150]
    call cor_nevoa
    mov esi, eax
    lea rdi, [rip + textura_nevoa]
    call desenhar_recorte
    add rsp, 8
.sem_nevoa:
    ret

destino_nevoa:
    mov qword ptr [rip + rec_destino], 0
    cvtsi2ss xmm0, dword ptr [rip + largura_tela]
    movss dword ptr [rip + rec_destino + 8], xmm0
    mov eax, dword ptr [rip + altura_tela]
    sub eax, dword ptr [rip + altura_hud]
    cvtsi2ss xmm0, eax
    movss dword ptr [rip + rec_destino + 12], xmm0
    mov qword ptr [rip + vec_pivo], 0
    mov dword ptr [rip + rotacao_atual], 0
    ret

# xmm0 = alfa (0..255) -> eax = branco com esse alfa.
cor_nevoa:
    minss xmm0, dword ptr [rip + c_255r]
    cvttss2si eax, xmm0
    shl eax, 24
    or eax, 0x00ffffff
    ret

# Dentro da câmera, depois da luz: marcas da doca.
desenhar_mundo_roteiro:
    sub rsp, 8
    call desenhar_doca_mundo
    add rsp, 8
    ret

# ---------------------------------------------------------------- tela

# Em coordenadas de tela, depois do HUD.
desenhar_tela_roteiro:
    sub rsp, 8
    call desenhar_flash
    call desenhar_objetivo
    call desenhar_aviso_e
    call desenhar_doca_tela
    call desenhar_mensagem
    add rsp, 8
    ret

desenhar_flash:
    sub rsp, 8
    movss xmm0, dword ptr [rip + flash_alfa]
    ucomiss xmm0, dword ptr [rip + zero_rt]
    jbe .sem_flash
    mulss xmm0, dword ptr [rip + c_150]
    cvttss2si r8d, xmm0
    shl r8d, 24
    or r8d, 0x002020d0               # vermelho
    cmp dword ptr [rip + flash_branco], 0
    je .flash_cor
    or r8d, 0x00ffffff
.flash_cor:
    xor edi, edi
    xor esi, esi
    mov edx, dword ptr [rip + largura_tela]
    mov ecx, dword ptr [rip + altura_tela]
    call DrawRectangle
.sem_flash:
    add rsp, 8
    ret

desenhar_objetivo:
    push rbx
    push r12
    push r13
    push r14
    sub rsp, 8
    mov rbx, qword ptr [rip + objetivo]
    test rbx, rbx
    jz .sem_objetivo
    mov r12d, dword ptr [rip + fonte_hud]
    lea rdi, [rip + texto_objetivo]
    mov esi, r12d
    call MeasureText
    mov r13d, eax                    # largura do rótulo
    mov rdi, rbx
    mov esi, r12d
    call MeasureText
    mov r14d, eax                    # largura do texto
    # fundo: de f/2 a f/2 + f + rótulo + f + texto + f, altura 2f
    mov edi, r12d
    shr edi, 1
    mov esi, edi
    lea edx, [r13 + r14]
    lea edx, [rdx + r12*2]
    add edx, r12d
    mov ecx, r12d
    add ecx, r12d
    mov r8d, 0xb0100a0c
    call DrawRectangle
    lea rdi, [rip + texto_objetivo]
    mov esi, r12d
    mov edx, r12d
    mov ecx, r12d
    mov r8d, 0xff4ac8f0
    call DrawText
    mov rdi, rbx
    lea esi, [r12 + r13]
    add esi, r12d
    mov edx, r12d
    mov ecx, r12d
    mov r8d, 0xffe8e0d8
    call DrawText
.sem_objetivo:
    add rsp, 8
    pop r14
    pop r13
    pop r12
    pop rbx
    ret

# Tecla E sobre a cabeça de Ícaro e o que ela faz.
desenhar_aviso_e:
    push rbx
    push r12
    push r13
    mov rbx, qword ptr [rip + interacao_atual]
    test rbx, rbx
    jz .sem_aviso
    cmp qword ptr [rbx + IN_ROTULO], 0
    je .sem_aviso
    cmp dword ptr [rip + controle_jogador], 0
    je .sem_aviso
    # posição na tela: (iso * zoom) + deslocamento da câmera
    movss xmm0, dword ptr [rip + icaro_iso_x]
    mulss xmm0, dword ptr [rip + zoom]
    addss xmm0, dword ptr [rip + desloc_x]
    cvttss2si r12d, xmm0
    movss xmm0, dword ptr [rip + icaro_iso_y]
    subss xmm0, dword ptr [rip + altura_cabeca]
    mulss xmm0, dword ptr [rip + zoom]
    addss xmm0, dword ptr [rip + desloc_y]
    cvttss2si r13d, xmm0
    cvttss2si edx, dword ptr [rip + zoom]
    mov eax, edx
    imul eax, eax, 11
    sar eax, 1
    mov edi, r12d
    sub edi, eax
    mov esi, r13d
    lea rcx, [rip + pose_TECLA_E]
    xor r8d, r8d
    call desenhar_pose_tela
    cvttss2si eax, dword ptr [rip + zoom]
    imul eax, eax, 8
    lea esi, [r12 + rax]
    mov edx, r13d
    mov rdi, qword ptr [rbx + IN_ROTULO]
    mov ecx, dword ptr [rip + fonte_hud]
    mov r8d, 0xffe8e0d8
    call DrawText
.sem_aviso:
    pop r13
    pop r12
    pop rbx
    ret

# Caixa de mensagem acima do HUD, centrada, com o texto revelado aos poucos.
desenhar_mensagem:
    push rbx
    push r12
    push r13
    push r14
    push r15
    cmp dword ptr [rip + mensagem_ativa], 0
    je .sem_mensagem
    # copia só os caracteres já revelados
    cvttss2si ecx, dword ptr [rip + mensagem_mostrados]
    mov rsi, qword ptr [rip + mensagem]
    lea rdi, [rip + texto_visivel]
    lea r8, [rdi + 508]
.copiar_texto:
    cmp rdi, r8
    jae .copiado
    movzx eax, byte ptr [rsi]
    test eax, eax
    jz .copiado
    mov edx, eax
    and edx, 0xc0
    cmp edx, 0x80
    je .continuacao
    test ecx, ecx
    jz .copiado
    dec ecx
.continuacao:
    mov byte ptr [rdi], al
    inc rsi
    inc rdi
    jmp .copiar_texto
.copiado:
    mov byte ptr [rdi], 0

    mov r12d, dword ptr [rip + fonte_hud]
    # tamanho da caixa pelo texto inteiro, para ela não crescer enquanto escreve
    mov rdi, qword ptr [rip + mensagem]
    mov esi, r12d
    call MeasureText
    lea r13d, [rax + r12*2]          # largura da caixa
    mov rsi, qword ptr [rip + mensagem]
    mov r14d, 1
.linhas:
    movzx eax, byte ptr [rsi]
    test eax, eax
    jz .linhas_contadas
    inc rsi
    cmp eax, 10
    jne .linhas
    inc r14d
    jmp .linhas
.linhas_contadas:
    imul r14d, r12d                  # altura do texto (aprox.: linhas x fonte)
    lea r15d, [r14 + r12*2]          # altura da caixa
    mov ebx, dword ptr [rip + largura_tela]
    sub ebx, r13d
    sar ebx, 1                       # x da caixa
    mov esi, dword ptr [rip + altura_tela]
    sub esi, dword ptr [rip + altura_hud]
    sub esi, r15d
    sub esi, r12d
    mov r14d, esi                    # y da caixa
    mov edi, ebx
    mov edx, r13d
    mov ecx, r15d
    mov r8d, 0xe8100a0c
    call DrawRectangle
    mov edi, ebx
    mov esi, r14d
    mov edx, r13d
    mov ecx, r15d
    mov r8d, 0xff5a4a50
    call DrawRectangleLines
    lea rdi, [rip + texto_visivel]
    lea esi, [rbx + r12]
    lea edx, [r14 + r12]
    mov ecx, r12d
    mov r8d, 0xffe0e6ec
    call DrawText
.sem_mensagem:
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbx
    ret

.section .rodata
.align 16
sem_sinal_rt: .long 0x7fffffff, 0x7fffffff, 0x7fffffff, 0x7fffffff

.section .note.GNU-stack,"",@progbits
