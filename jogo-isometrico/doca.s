.intel_syntax noprefix

# Fuga pela doca: três pontos na mesma tela. Em cada um, Ícaro espera na área
# segura enquanto os anjos escutam; no 4º pulso do metrônomo, a nota do
# alto-falante certo o faz berrar, os anjos voam até ele e abre-se uma janela
# para correr até a próxima área. O alto-falante isca leva os anjos para o
# caminho. Qualquer erro reinicia só o ponto atual.

.include "estruturas.inc"
.include "personagens.inc"

.equ D_INATIVO, 0
.equ D_ESCUTANDO, 1
.equ D_ATRAINDO, 2
.equ D_FALHA, 3
.equ D_ISCA, 4
.equ D_SUCESSO, 5
.equ D_FIM, 6

.section .rodata
.align 4
mil_d:          .float 1000.0
tempo_falha:    .float 1.6
tempo_isca:     .float 0.9
tempo_sucesso:  .float 1.1
vel_anjo:       .float 170.0
meio_d:         .float 0.5
zero_d:         .float 0.0
um_d:           .float 1.0
flash_cheio:    .float 1.0
tremor_falha:   .float 0.5
janela_acesa:   .float 0.45          # fração do pulso em que o símbolo fica aceso
texto_pulso:    .asciz "Toque no 4º pulso"
texto_midi:     .asciz "MIDI conectado"
texto_teclado:  .asciz "teclas 1-4"
texto_corra:    .asciz "CORRA!"
numeros:        .asciz "1\0002\0003\0004"

.section .bss
.align 8
doca_ponto:     .skip 8
.align 4
.global doca_concluida
.global doca_estado
.global doca_ponto
doca_estado:    .skip 4
doca_t:         .skip 4
doca_janela:    .skip 4
doca_concluida: .skip 4

.section .text
.global doca_iniciar
.global atualizar_doca
.global desenhar_doca_mundo
.global desenhar_doca_tela

.extern alto_falantes
.extern icaro
.extern andar_indice
.extern delta_quadro
.extern controle_jogador
.extern controle_salvo
.extern flash_alfa
.extern flash_branco
.extern tremor
.extern nota_evento
.extern nota_valida
.extern metro_iniciar
.extern metro_parar
.extern metro_fase
.extern metro_ativo
.extern midi_fd
.extern tocar_som
.extern mostrar_ator
.extern ator_ptr
.extern ator_andar_ate
.extern ator_parado
.extern teleportar
.extern desenhar_pose_tela
.extern largura_tela
.extern altura_tela
.extern altura_hud
.extern fonte_hud
.extern zoom
.extern DrawRectangle
.extern DrawText
.extern MeasureText
.extern pose_ANJO_POUSADO
.extern conj_ANJO_VOO
.extern pose_ANJO_GRITO
.extern pose_AREA_SEGURA
.extern pose_ANEL
.extern pose_NOTA_0

# rdi = ponto da doca.
doca_iniciar:
    sub rsp, 8
    mov qword ptr [rip + doca_ponto], rdi
    mov dword ptr [rip + doca_concluida], 0
    call reiniciar_ponto
    add rsp, 8
    ret

# Ícaro na área de partida, anjos nos poleiros, metrônomo do ponto.
reiniciar_ponto:
    push rbx
    push r12
    push r13
    mov rbx, qword ptr [rip + doca_ponto]
    cvtsi2ss xmm0, dword ptr [rbx + DP_INI_X]
    movss dword ptr [rip + icaro], xmm0
    cvtsi2ss xmm0, dword ptr [rbx + DP_INI_Y]
    movss dword ptr [rip + icaro + 4], xmm0
    xor r12d, r12d
.poleiro:
    cmp r12d, dword ptr [rbx + DP_N_ANJOS]
    jge .anjos_prontos
    mov r13, qword ptr [rbx + DP_POLEIROS]
    imul eax, r12d, 12
    add r13, rax
    mov edi, dword ptr [rbx + DP_ANJO0]
    add edi, r12d
    mov esi, dword ptr [rip + andar_indice]
    cvtsi2ss xmm0, dword ptr [r13]
    cvtsi2ss xmm1, dword ptr [r13 + 4]
    cvtsi2ss xmm2, dword ptr [r13 + 8]
    xor edx, edx
    lea rcx, [rip + pose_ANJO_POUSADO]
    mov r8d, AF_HD
    call mostrar_ator
    inc r12d
    jmp .poleiro
.anjos_prontos:
    mov edi, dword ptr [rbx + DP_BPM]
    call metro_iniciar
    mov dword ptr [rip + doca_estado], D_ESCUTANDO
    mov dword ptr [rip + controle_jogador], 1
    mov dword ptr [rip + controle_salvo], 1
    pop r13
    pop r12
    pop rbx
    ret

# edi = índice do alto-falante -> rax = ele.
falante:
    shl edi, 4
    lea rax, [rip + alto_falantes]
    add rax, rdi
    ret

# edi, esi = centro da área -> eax = 1 se os pés de Ícaro estão dentro.
icaro_na_area:
    cvttss2si eax, dword ptr [rip + icaro]
    sub eax, edi
    cdq
    xor eax, edx
    sub eax, edx
    cmp eax, RAIO_AREA
    jg .fora
    cvttss2si eax, dword ptr [rip + icaro + 4]
    sub eax, esi
    cdq
    xor eax, edx
    sub eax, edx
    cmp eax, RAIO_AREA
    jg .fora
    mov eax, 1
    ret
.fora:
    xor eax, eax
    ret

# edi = alto-falante: berro, o grito dos anjos levantando voo e eles voando até
# ele, um ao lado do outro.
atrair:
    push rbx
    push r12
    push r13
    push r14
    sub rsp, 8
    call falante
    mov r13, rax
    mov edi, SOM_BERRO
    call tocar_som
    mov edi, SOM_GRITO_ANJO
    call tocar_som
    call metro_parar
    mov rbx, qword ptr [rip + doca_ponto]
    xor r12d, r12d
.anjo_voa:
    cmp r12d, dword ptr [rbx + DP_N_ANJOS]
    jge .fim_atrair
    mov r14d, dword ptr [rbx + DP_ANJO0]
    add r14d, r12d
    mov edi, r14d
    call ator_ptr
    # em voo, a vista segue a direção do movimento
    lea rcx, [rip + conj_ANJO_VOO]
    mov qword ptr [rax + AT_CONJ], rcx
    # destino: em volta da corneta, 12 px entre um e outro
    imul eax, r12d, 12
    sub eax, 12
    add eax, dword ptr [r13 + FAL_X]
    cvtsi2ss xmm0, eax
    mov eax, r12d
    and eax, 1
    imul eax, eax, 8
    add eax, dword ptr [r13 + FAL_Y]
    add eax, 4
    cvtsi2ss xmm1, eax
    mov eax, dword ptr [r13 + FAL_Z]
    add eax, 4
    cvtsi2ss xmm2, eax
    movss xmm3, dword ptr [rip + vel_anjo]
    mov edi, r14d
    call ator_andar_ate
    inc r12d
    jmp .anjo_voa
.fim_atrair:
    add rsp, 8
    pop r14
    pop r13
    pop r12
    pop rbx
    ret

# Anjos que chegaram pousam (e voltam a escutar com a coroa girando devagar).
pousar_anjos:
    push rbx
    push r12
    push r13
    mov rbx, qword ptr [rip + doca_ponto]
    xor r12d, r12d
.pousar:
    cmp r12d, dword ptr [rbx + DP_N_ANJOS]
    jge .fim_pousar
    mov edi, dword ptr [rbx + DP_ANJO0]
    add edi, r12d
    call ator_ptr
    cmp dword ptr [rax + AT_MOVENDO], 0
    jne .proximo_pouso
    lea rcx, [rip + conj_ANJO_VOO]
    cmp qword ptr [rax + AT_CONJ], rcx
    jne .proximo_pouso
    mov qword ptr [rax + AT_CONJ], 0
    lea rcx, [rip + pose_ANJO_POUSADO]
    mov qword ptr [rax + AT_POSE], rcx
.proximo_pouso:
    inc r12d
    jmp .pousar
.fim_pousar:
    pop r13
    pop r12
    pop rbx
    ret

# Os anjos gritam; tela vermelha e tremor; o ponto recomeça depois.
falhar:
    push rbx
    push r12
    push r13
    mov dword ptr [rip + doca_estado], D_FALHA
    movss xmm0, dword ptr [rip + tempo_falha]
    movss dword ptr [rip + doca_t], xmm0
    mov dword ptr [rip + controle_jogador], 0
    call metro_parar
    mov edi, SOM_GRITO
    call tocar_som
    movss xmm0, dword ptr [rip + flash_cheio]
    movss dword ptr [rip + flash_alfa], xmm0
    mov dword ptr [rip + flash_branco], 0
    movss xmm0, dword ptr [rip + tremor_falha]
    movss dword ptr [rip + tremor], xmm0
    mov rbx, qword ptr [rip + doca_ponto]
    xor r12d, r12d
.gritar:
    cmp r12d, dword ptr [rbx + DP_N_ANJOS]
    jge .fim_falhar
    mov edi, dword ptr [rbx + DP_ANJO0]
    add edi, r12d
    call ator_ptr
    lea rcx, [rip + pose_ANJO_GRITO]
    mov qword ptr [rax + AT_POSE], rcx
    mov qword ptr [rax + AT_CONJ], 0
    mov dword ptr [rax + AT_MOVENDO], 0
    inc r12d
    jmp .gritar
.fim_falhar:
    pop r13
    pop r12
    pop rbx
    ret

atualizar_doca:
    push rbx
    push r12
    sub rsp, 8
    mov rbx, qword ptr [rip + doca_ponto]
    mov eax, dword ptr [rip + doca_estado]
    cmp eax, D_ESCUTANDO
    je .escutando
    cmp eax, D_ATRAINDO
    je .atraindo
    cmp eax, D_FALHA
    je .em_falha
    cmp eax, D_ISCA
    je .em_isca
    cmp eax, D_SUCESSO
    je .em_sucesso
    jmp .fim_doca

.escutando:
    mov edi, dword ptr [rbx + DP_INI_X]
    mov esi, dword ptr [rbx + DP_INI_Y]
    call icaro_na_area
    test eax, eax
    jz .falha_agora                  # um passo fora da hora: eles escutam
    cmp dword ptr [rip + nota_evento], 0
    jl .fim_doca
    mov edi, dword ptr [rbx + DP_CERTO]
    call falante
    mov edi, dword ptr [rax + FAL_NOTA]
    call nota_valida
    test eax, eax
    jz .tentar_isca
    mov edi, dword ptr [rbx + DP_CERTO]
    call atrair
    mov dword ptr [rip + doca_estado], D_ATRAINDO
    cvtsi2ss xmm0, dword ptr [rbx + DP_JANELA]
    divss xmm0, dword ptr [rip + mil_d]
    movss dword ptr [rip + doca_t], xmm0
    movss dword ptr [rip + doca_janela], xmm0
    jmp .fim_doca
.tentar_isca:
    mov edi, dword ptr [rbx + DP_ISCA]
    test edi, edi
    js .falha_agora
    call falante
    mov edi, dword ptr [rax + FAL_NOTA]
    call nota_valida
    test eax, eax
    jz .falha_agora
    mov edi, dword ptr [rbx + DP_ISCA]
    call atrair
    mov dword ptr [rip + doca_estado], D_ISCA
    movss xmm0, dword ptr [rip + tempo_isca]
    movss dword ptr [rip + doca_t], xmm0
    mov dword ptr [rip + controle_jogador], 0
    jmp .fim_doca
.falha_agora:
    call falhar
    jmp .fim_doca

.atraindo:
    call pousar_anjos
    mov edi, dword ptr [rbx + DP_FIM_X]
    mov esi, dword ptr [rbx + DP_FIM_Y]
    call icaro_na_area
    test eax, eax
    jnz .chegou
    call contar_tempo
    test eax, eax
    jz .fim_doca
    call falhar
    jmp .fim_doca
.chegou:
    mov dword ptr [rip + doca_estado], D_SUCESSO
    movss xmm0, dword ptr [rip + tempo_sucesso]
    movss dword ptr [rip + doca_t], xmm0
    mov dword ptr [rip + controle_jogador], 0
    mov dword ptr [rip + icaro + 12], 0
    mov edi, ATOR_AGENTE
    cvtsi2ss xmm0, dword ptr [rbx + DP_AGENTE_X]
    cvtsi2ss xmm1, dword ptr [rbx + DP_AGENTE_Y]
    call teleportar
    jmp .fim_doca

.em_falha:
    call contar_tempo
    test eax, eax
    jz .fim_doca
    call reiniciar_ponto
    jmp .fim_doca

.em_isca:
    call contar_tempo
    test eax, eax
    jz .fim_doca
    call falhar
    jmp .fim_doca

.em_sucesso:
    call pousar_anjos
    call contar_tempo
    test eax, eax
    jz .fim_doca
    mov dword ptr [rip + doca_estado], D_FIM
    mov dword ptr [rip + doca_concluida], 1
    mov dword ptr [rip + controle_salvo], 0
.fim_doca:
    add rsp, 8
    pop r12
    pop rbx
    ret

# eax = 1 quando doca_t chega a zero.
contar_tempo:
    movss xmm0, dword ptr [rip + doca_t]
    subss xmm0, dword ptr [rip + delta_quadro]
    movss dword ptr [rip + doca_t], xmm0
    xor eax, eax
    ucomiss xmm0, dword ptr [rip + zero_d]
    ja .ainda
    mov eax, 1
.ainda:
    ret

# eax = 1 se ainda há ponto em jogo (escutando ou atraindo).
doca_em_jogo:
    xor eax, eax
    mov ecx, dword ptr [rip + doca_estado]
    cmp ecx, D_ESCUTANDO
    jb .fora_jogo
    cmp ecx, D_ISCA
    ja .fora_jogo
    mov eax, 1
.fora_jogo:
    ret

# Pulso atual: eax = pulso no compasso (0..3), xmm0 = fração dentro do pulso.
pulso_atual:
    movss xmm0, dword ptr [rip + metro_fase]
    xor eax, eax
    ucomiss xmm0, dword ptr [rip + zero_d]
    jb .antes_do_primeiro
    roundss xmm1, xmm0, 1
    cvttss2si eax, xmm1
    and eax, 3
    subss xmm0, xmm1
    ret
.antes_do_primeiro:
    mov eax, -1
    movss xmm0, dword ptr [rip + um_d]
    ret

# Dentro da câmera, depois da luz: áreas seguras, anel do pulso e símbolos.
desenhar_doca_mundo:
    push rbx
    push r12
    push r13
    push r14
    sub rsp, 8
    call doca_em_jogo
    test eax, eax
    jz .fim_mundo
    mov rbx, qword ptr [rip + doca_ponto]
    mov edi, dword ptr [rbx + DP_INI_X]
    mov esi, dword ptr [rbx + DP_INI_Y]
    call marca_area
    mov edi, dword ptr [rbx + DP_FIM_X]
    mov esi, dword ptr [rbx + DP_FIM_Y]
    call marca_area
    cmp dword ptr [rip + doca_estado], D_ESCUTANDO
    jne .fim_mundo
    call pulso_atual
    mov r13d, eax                    # pulso no compasso
    xor r14d, r14d                   # 1 = acender símbolo
    cmp eax, 3
    jne .simbolos
    ucomiss xmm0, dword ptr [rip + janela_acesa]
    ja .simbolos
    mov r14d, 1
.simbolos:
    mov edi, dword ptr [rbx + DP_CERTO]
    mov esi, r13d
    mov edx, r14d
    call marca_falante
    mov edi, dword ptr [rbx + DP_ISCA]
    test edi, edi
    js .fim_mundo
    mov esi, r13d
    mov edx, r14d
    call marca_falante
.fim_mundo:
    add rsp, 8
    pop r14
    pop r13
    pop r12
    pop rbx
    ret

# edi, esi = centro da área (mundo).
marca_area:
    sub rsp, 8
    lea rcx, [rip + pose_AREA_SEGURA]
    mov eax, edi
    sub eax, esi
    add eax, ORIGEM_ISO_X
    sub eax, dword ptr [rcx + PS_AX]
    mov r9d, eax
    lea eax, [rdi + rsi]
    sar eax, 1
    sub eax, dword ptr [rcx + PS_AY]
    mov esi, eax
    mov edi, r9d
    mov edx, 1
    xor r8d, r8d
    call desenhar_pose_tela
    add rsp, 8
    ret

# edi = alto-falante, esi = pulso no compasso, edx = 1 aceso.
# Anel no chão a cada pulso e símbolo da nota acima da corneta.
marca_falante:
    push rbx
    push r12
    push r13
    push r14
    push r15
    mov r14d, esi
    mov r15d, edx
    call falante
    mov rbx, rax
    mov eax, dword ptr [rbx + FAL_X]
    sub eax, dword ptr [rbx + FAL_Y]
    add eax, ORIGEM_ISO_X
    mov r12d, eax                    # x na tela
    mov eax, dword ptr [rbx + FAL_X]
    add eax, dword ptr [rbx + FAL_Y]
    sar eax, 1
    mov r13d, eax                    # y do chão na tela
    test r14d, r14d
    js .sem_anel
    lea rcx, [rip + pose_ANEL]
    mov edi, r12d
    sub edi, dword ptr [rcx + PS_AX]
    mov esi, r13d
    sub esi, dword ptr [rcx + PS_AY]
    mov edx, 1
    xor r8d, r8d
    call desenhar_pose_tela
.sem_anel:
    # símbolo: NOTA_0..3 são poses de 32 bytes em sequência
    mov eax, dword ptr [rbx + FAL_NOTA]
    shl eax, 5
    lea rcx, [rip + pose_NOTA_0]
    add rcx, rax
    mov edi, r12d
    sub edi, dword ptr [rcx + PS_AX]
    mov esi, r13d
    sub esi, dword ptr [rbx + FAL_Z]
    sub esi, 12
    sub esi, dword ptr [rcx + PS_AY]
    mov edx, 1
    mov r8d, r15d
    call desenhar_pose_tela
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbx
    ret

# Na tela: os 4 pulsos do compasso, as teclas das notas e a janela da corrida.
desenhar_doca_tela:
    push rbx
    push r12
    push r13
    push r14
    push r15
    sub rsp, 16
    call doca_em_jogo
    test eax, eax
    jz .fim_tela
    mov r12d, dword ptr [rip + fonte_hud]
    cvttss2si r15d, dword ptr [rip + zoom]
    cmp dword ptr [rip + doca_estado], D_ATRAINDO
    je .barra_janela
    cmp dword ptr [rip + doca_estado], D_ESCUTANDO
    jne .fim_tela

    # pulsos: 4 quadrados centrados acima do HUD; o 4º maior e vermelho
    call pulso_atual
    mov r13d, eax
    mov ebx, r12d                    # lado
    mov eax, dword ptr [rip + altura_tela]
    sub eax, dword ptr [rip + altura_hud]
    sub eax, r12d
    sub eax, r12d
    sub eax, r12d
    mov dword ptr [rsp], eax         # y dos pulsos
    mov eax, dword ptr [rip + largura_tela]
    imul ecx, r12d, 7
    sub eax, ecx
    sar eax, 1
    mov dword ptr [rsp + 4], eax     # x do primeiro
    xor r14d, r14d
.pulso:
    cmp r14d, 4
    jge .legenda_pulso
    imul edi, r14d, 2
    imul edi, ebx
    add edi, dword ptr [rsp + 4]
    mov esi, dword ptr [rsp]
    mov edx, ebx
    mov ecx, ebx
    mov r8d, 0xff4a4048              # apagado
    cmp r14d, 3
    jne .cor_pulso
    mov r8d, 0xff3a3a90              # acento apagado
.cor_pulso:
    cmp r14d, r13d
    jne .desenha_pulso
    mov r8d, 0xffe8e0d8
    cmp r14d, 3
    jne .desenha_pulso
    mov r8d, 0xff4060ff              # acento aceso
    sub edi, 3
    sub esi, 3
    add edx, 6
    add ecx, 6
.desenha_pulso:
    call DrawRectangle
    inc r14d
    jmp .pulso
.legenda_pulso:
    lea rdi, [rip + texto_pulso]
    mov esi, r12d
    call MeasureText
    mov esi, dword ptr [rip + largura_tela]
    sub esi, eax
    sar esi, 1
    mov edx, dword ptr [rsp]
    sub edx, r12d
    sub edx, r12d
    lea rdi, [rip + texto_pulso]
    mov ecx, r12d
    mov r8d, 0xffe8e0d8
    call DrawText

    # as 4 notas com as teclas, à direita dos pulsos
    mov eax, dword ptr [rsp + 4]
    imul ecx, r12d, 9
    add eax, ecx
    mov dword ptr [rsp + 8], eax
    xor r14d, r14d
.tecla_nota:
    cmp r14d, 4
    jge .estado_midi
    mov eax, r14d
    shl eax, 5
    lea rcx, [rip + pose_NOTA_0]
    add rcx, rax
    imul edi, r14d, 12
    imul edi, r15d
    add edi, dword ptr [rsp + 8]
    mov esi, dword ptr [rsp]
    mov edx, r15d
    mov r8d, 1
    call desenhar_pose_tela
    imul esi, r14d, 12
    imul esi, r15d
    add esi, dword ptr [rsp + 8]
    lea rdi, [rip + numeros]
    lea rdi, [rdi + r14*2]
    mov eax, r15d
    imul eax, eax, 3
    add esi, eax
    mov edx, dword ptr [rsp]
    imul eax, r15d, 13
    add edx, eax
    mov ecx, r12d
    mov r8d, 0xffb8c0c8
    call DrawText
    inc r14d
    jmp .tecla_nota
.estado_midi:
    lea rdi, [rip + texto_teclado]
    cmp dword ptr [rip + midi_fd], 0
    jl .texto_entrada
    lea rdi, [rip + texto_midi]
.texto_entrada:
    imul esi, r12d, 9
    neg esi
    add esi, dword ptr [rsp + 4]
    mov edx, dword ptr [rsp]
    mov ecx, r12d
    mov r8d, 0xff9aa8b8
    call DrawText
    jmp .fim_tela

.barra_janela:
    # CORRA! e o tempo que resta, no alto da área de jogo
    mov eax, dword ptr [rip + largura_tela]
    shr eax, 1
    mov r13d, eax                    # largura total da barra
    mov edi, dword ptr [rip + largura_tela]
    sub edi, eax
    sar edi, 1
    mov ebx, edi
    mov esi, r12d
    imul esi, esi, 3
    mov edx, r13d
    mov ecx, r12d
    shr ecx, 1
    mov r8d, 0xa0000000
    call DrawRectangle
    movss xmm0, dword ptr [rip + doca_t]
    divss xmm0, dword ptr [rip + doca_janela]
    maxss xmm0, dword ptr [rip + zero_d]
    cvtsi2ss xmm1, r13d
    mulss xmm0, xmm1
    cvttss2si edx, xmm0
    mov edi, ebx
    mov esi, r12d
    imul esi, esi, 3
    mov ecx, r12d
    shr ecx, 1
    mov r8d, 0xff60e0a0
    call DrawRectangle
    lea rdi, [rip + texto_corra]
    imul esi, r12d, 2
    call MeasureText
    mov esi, dword ptr [rip + largura_tela]
    sub esi, eax
    sar esi, 1
    mov edx, r12d
    lea rdi, [rip + texto_corra]
    imul ecx, r12d, 2
    shr ecx, 1
    add ecx, r12d
    mov r8d, 0xff60e0a0
    call DrawText
.fim_tela:
    add rsp, 16
    pop r15
    pop r14
    pop r13
    pop r12
    pop rbx
    ret

.section .note.GNU-stack,"",@progbits
