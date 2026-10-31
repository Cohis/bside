.intel_syntax noprefix

# Entrada musical e sons. Um único sistema valida notas e pulsos para todos os
# desafios: as 4 notas vêm do teclado MIDI (ALSA rawmidi, /dev/snd/midiC*D0,
# lido sem bloquear) ou das teclas 1-4; a nota vale pela classe (nota % 12),
# em qualquer oitava. O metrônomo marca compassos de 4 pulsos; o 4º é o acento.

.include "estruturas.inc"

.equ O_RDONLY_NONBLOCK, 0x800
.equ TECLA_1, 49
.equ SOM_TAM, 40                     # Sound: AudioStream (32) + frameCount
.equ TOLERANCIA_MS, 150

.section .rodata
caminho_midi:   .asciz "/dev/snd/midiC0D0"
.align 8
caminhos_sons:
    .quad som_nota0, som_nota1, som_nota2, som_nota3, som_tique, som_berro, som_grito, som_estatica, som_clarao
    .quad som_baque, som_grito_anjo
som_nota0:      .asciz "assets/sons/nota0.wav"
som_nota1:      .asciz "assets/sons/nota1.wav"
som_nota2:      .asciz "assets/sons/nota2.wav"
som_nota3:      .asciz "assets/sons/nota3.wav"
som_tique:      .asciz "assets/sons/tique.wav"
som_berro:      .asciz "assets/sons/berro.wav"
som_grito:      .asciz "assets/sons/grito.wav"
som_estatica:   .asciz "assets/sons/estatica.wav"
som_clarao:     .asciz "assets/sons/clarao.wav"
som_baque:      .asciz "assets/sons/baque.wav"
som_grito_anjo: .asciz "assets/sons/grito-anjo.wav"
caminho_zumbido: .asciz "assets/sons/zumbido.wav"
# Classes das 4 notas do jogo (Dó, Ré, Mi, Sol). Mudar aqui e em gerar_sons.py.
.global notas_midi
notas_midi:     .byte 0, 2, 4, 7

.align 4
sessenta:       .float 60.0
atraso_inicio:  .float 0.8           # s até o primeiro pulso
tolerancia:     .float 0.150
meio_r:         .float 0.5
um_r:           .float 1.0
volume_tique:   .float 0.55
volume_acento:  .float 1.0
cem:            .float 100.0

.section .data
.align 4
.global midi_fd
midi_fd:        .long -1

.section .bss
.align 16
sons:           .skip N_SONS * SOM_TAM
zumbido:        .skip 56
zumbido_ok:     .skip 4
.align 4
.global nota_evento
.global metro_ativo
.global metro_pulso
.global metro_fase
nota_evento:    .skip 4              # nota tocada neste quadro (0..3, 4 = fora do jogo, -1 nenhuma)
nota_no_acento: .skip 4              # 1 se ela caiu no 4º pulso, dentro da tolerância
metro_ativo:    .skip 4
metro_t0:       .skip 4
metro_periodo:  .skip 4
metro_pulso:    .skip 4              # último pulso inteiro já tocado
metro_fase:     .skip 4              # pulsos desde t0 (float)
midi_status:    .skip 4
midi_dados:     .skip 4
midi_nota:      .skip 4
buffer_midi:    .skip 64
nome_midi:      .skip 24

.section .text
.global iniciar_ritmo
.global encerrar_ritmo
.global atualizar_ritmo
.global tocar_som
.global metro_iniciar
.global metro_parar
.global nota_valida
.global volume_zumbido

.extern tempo
.extern open
.extern read
.extern close
.extern IsKeyPressed
.extern LoadSound
.extern UnloadSound
.extern PlaySound
.extern SetSoundVolume
.extern LoadMusicStream
.extern UnloadMusicStream
.extern PlayMusicStream
.extern UpdateMusicStream
.extern SetMusicVolume
.extern IsAudioDeviceReady

# Abre o primeiro teclado MIDI e carrega os sons. Sem áudio ou sem MIDI, segue.
iniciar_ritmo:
    push rbx
    push r12
    sub rsp, 8
    mov dword ptr [rip + nota_evento], -1
    # nome com o dígito da placa trocável: /dev/snd/midiC?D0
    lea rsi, [rip + caminho_midi]
    lea rdi, [rip + nome_midi]
    mov ecx, 18
    rep movsb
    xor ebx, ebx
.tentar_midi:
    cmp ebx, 4
    jge .sem_midi
    lea eax, [rbx + '0']
    mov byte ptr [rip + nome_midi + 14], al
    lea rdi, [rip + nome_midi]
    mov esi, O_RDONLY_NONBLOCK
    xor eax, eax
    call open
    test eax, eax
    jns .midi_aberto
    inc ebx
    jmp .tentar_midi
.midi_aberto:
    mov dword ptr [rip + midi_fd], eax
.sem_midi:
    call IsAudioDeviceReady
    test al, al
    jz .fim_iniciar
    xor ebx, ebx
.carregar_som:
    cmp ebx, N_SONS
    jge .carregar_zumbido
    imul eax, ebx, SOM_TAM
    lea rdi, [rip + sons]
    add rdi, rax
    lea rax, [rip + caminhos_sons]
    mov rsi, qword ptr [rax + rbx*8]
    call LoadSound
    inc ebx
    jmp .carregar_som
.carregar_zumbido:
    lea rdi, [rip + zumbido]
    lea rsi, [rip + caminho_zumbido]
    call LoadMusicStream
    cmp qword ptr [rip + zumbido + 48], 0
    je .fim_iniciar
    mov byte ptr [rip + zumbido + 36], 1          # em laço
    mov dword ptr [rip + zumbido_ok], 1
    xorps xmm0, xmm0
    lea r10, [rip + SetMusicVolume]
    call chamar_zumbido
    lea r10, [rip + PlayMusicStream]
    call chamar_zumbido
.fim_iniciar:
    add rsp, 8
    pop r12
    pop rbx
    ret

encerrar_ritmo:
    push rbx
    mov edi, dword ptr [rip + midi_fd]
    test edi, edi
    js .sem_fd
    call close
.sem_fd:
    cmp dword ptr [rip + zumbido_ok], 0
    je .fim_encerrar
    lea r10, [rip + UnloadMusicStream]
    call chamar_zumbido
.fim_encerrar:
    pop rbx
    ret

# r10 = função da Raylib que recebe a Music do zumbido por valor (xmm0 passa direto).
chamar_zumbido:
    sub rsp, 72
    lea rax, [rip + zumbido]
    mov ecx, 7
.copiar_zumbido:
    mov rdx, qword ptr [rax + rcx*8 - 8]
    mov qword ptr [rsp + rcx*8 - 8], rdx
    loop .copiar_zumbido
    call r10
    add rsp, 72
    ret

# edi = volume em %.
volume_zumbido:
    cmp dword ptr [rip + zumbido_ok], 0
    je .fim_volume
    sub rsp, 8
    cvtsi2ss xmm0, edi
    divss xmm0, dword ptr [rip + cem]
    lea r10, [rip + SetMusicVolume]
    call chamar_zumbido
    add rsp, 8
.fim_volume:
    ret

# edi = som; xmm0 não é usado. Toca com o volume atual do som.
tocar_som:
    cmp edi, N_SONS
    jae .sem_som
    imul eax, edi, SOM_TAM
    lea rsi, [rip + sons]
    add rsi, rax
    cmp qword ptr [rsi], 0           # buffer vazio: não carregou
    je .sem_som
    sub rsp, 56
    mov ecx, 5
.copiar_som:
    mov rax, qword ptr [rsi + rcx*8 - 8]
    mov qword ptr [rsp + rcx*8 - 8], rax
    loop .copiar_som
    call PlaySound
    add rsp, 56
.sem_som:
    ret

# edi = som, xmm0 = volume (0..1).
volume_som:
    cmp edi, N_SONS
    jae .sem_volume
    imul eax, edi, SOM_TAM
    lea rsi, [rip + sons]
    add rsi, rax
    cmp qword ptr [rsi], 0
    je .sem_volume
    sub rsp, 56
    mov ecx, 5
.copiar_volume:
    mov rax, qword ptr [rsi + rcx*8 - 8]
    mov qword ptr [rsp + rcx*8 - 8], rax
    loop .copiar_volume
    call SetSoundVolume
    add rsp, 56
.sem_volume:
    ret

# edi = batidas por minuto. O primeiro pulso cai depois de atraso_inicio.
metro_iniciar:
    cvtsi2ss xmm1, edi
    movss xmm0, dword ptr [rip + sessenta]
    divss xmm0, xmm1
    movss dword ptr [rip + metro_periodo], xmm0
    movss xmm0, dword ptr [rip + tempo]
    addss xmm0, dword ptr [rip + atraso_inicio]
    movss dword ptr [rip + metro_t0], xmm0
    mov dword ptr [rip + metro_pulso], -1
    mov dword ptr [rip + metro_ativo], 1
    ret

metro_parar:
    mov dword ptr [rip + metro_ativo], 0
    ret

# Lê teclado MIDI e teclas 1-4, avança o metrônomo e toca os sons de retorno.
atualizar_ritmo:
    push rbx
    push r12
    push r13
    mov dword ptr [rip + nota_evento], -1
    mov dword ptr [rip + nota_no_acento], 0
    cmp dword ptr [rip + zumbido_ok], 0
    je .ler_midi
    lea r10, [rip + UpdateMusicStream]
    call chamar_zumbido

.ler_midi:
    mov edi, dword ptr [rip + midi_fd]
    test edi, edi
    js .ler_teclas
    lea rsi, [rip + buffer_midi]
    mov edx, 64
    call read
    test rax, rax
    jle .ler_teclas
    mov r12, rax
    xor ebx, ebx
.byte_midi:
    cmp rbx, r12
    jge .ler_midi                    # pode haver mais no buffer do kernel
    lea rax, [rip + buffer_midi]
    movzx eax, byte ptr [rax + rbx]
    inc rbx
    test al, 0x80
    jz .dado_midi
    cmp al, 0xf8
    jae .byte_midi                   # tempo real: não muda o status corrente
    cmp al, 0xf0
    jae .status_sistema
    mov dword ptr [rip + midi_status], eax
    mov dword ptr [rip + midi_dados], 0
    jmp .byte_midi
.status_sistema:
    mov dword ptr [rip + midi_status], 0
    jmp .byte_midi
.dado_midi:
    mov ecx, dword ptr [rip + midi_status]
    test ecx, ecx
    jz .byte_midi
    and ecx, 0xf0
    cmp ecx, 0xc0
    je .um_dado
    cmp ecx, 0xd0
    je .um_dado
    cmp dword ptr [rip + midi_dados], 0
    jne .segundo_dado
    mov dword ptr [rip + midi_nota], eax
    mov dword ptr [rip + midi_dados], 1
    jmp .byte_midi
.um_dado:
    jmp .byte_midi
.segundo_dado:
    mov dword ptr [rip + midi_dados], 0   # status corrente: o próximo par é outra nota
    cmp ecx, 0x90
    jne .byte_midi
    test eax, eax
    jz .byte_midi                    # note-on com velocidade 0 = soltar
    mov eax, dword ptr [rip + midi_nota]
    xor edx, edx
    mov ecx, 12
    div ecx                          # edx = classe da nota
    xor ecx, ecx
    lea r8, [rip + notas_midi]
.procurar_classe:
    cmp ecx, 4
    jge .classe_fora
    movzx eax, byte ptr [r8 + rcx]
    cmp eax, edx
    je .classe_achada
    inc ecx
    jmp .procurar_classe
.classe_fora:
    mov ecx, 4
.classe_achada:
    mov dword ptr [rip + nota_evento], ecx
    jmp .byte_midi

.ler_teclas:
    xor ebx, ebx
.tecla_nota:
    cmp ebx, 4
    jge .nota_lida
    lea edi, [rbx + TECLA_1]
    call IsKeyPressed
    test al, al
    jz .proxima_tecla
    mov dword ptr [rip + nota_evento], ebx
.proxima_tecla:
    inc ebx
    jmp .tecla_nota
.nota_lida:
    mov edi, dword ptr [rip + nota_evento]
    test edi, edi
    js .metronomo
    cmp edi, 4
    jge .metronomo
    call tocar_som                   # SOM_NOTA0 + n

.metronomo:
    cmp dword ptr [rip + metro_ativo], 0
    je .fim_ritmo
    movss xmm0, dword ptr [rip + tempo]
    subss xmm0, dword ptr [rip + metro_t0]
    divss xmm0, dword ptr [rip + metro_periodo]
    movss dword ptr [rip + metro_fase], xmm0
    # pulso mais próximo e distância até ele, para julgar a nota deste quadro
    cmp dword ptr [rip + nota_evento], 0
    jl .tique
    movss xmm1, xmm0
    addss xmm1, dword ptr [rip + meio_r]
    roundss xmm1, xmm1, 1            # piso de fase + 0,5
    cvttss2si eax, xmm1
    test eax, eax
    js .tique
    mov ecx, eax
    and ecx, 3
    cmp ecx, 3
    jne .tique
    subss xmm0, xmm1
    andps xmm0, xmmword ptr [rip + sem_sinal_r]
    mulss xmm0, dword ptr [rip + metro_periodo]
    ucomiss xmm0, dword ptr [rip + tolerancia]
    ja .tique
    mov dword ptr [rip + nota_no_acento], 1
.tique:
    movss xmm0, dword ptr [rip + metro_fase]
    roundss xmm0, xmm0, 1
    cvttss2si eax, xmm0
    cmp eax, dword ptr [rip + metro_pulso]
    jle .fim_ritmo
    mov dword ptr [rip + metro_pulso], eax
    test eax, eax
    js .fim_ritmo
    # o 4º pulso toca mais forte
    and eax, 3
    cmp eax, 3
    je .acento
    movss xmm0, dword ptr [rip + volume_tique]
    jmp .tocar_tique
.acento:
    movss xmm0, dword ptr [rip + volume_acento]
.tocar_tique:
    mov edi, SOM_TIQUE
    call volume_som
    mov edi, SOM_TIQUE
    call tocar_som
.fim_ritmo:
    pop r13
    pop r12
    pop rbx
    ret

# edi = nota esperada -> eax = 1 se a nota deste quadro é ela e caiu no 4º pulso.
nota_valida:
    xor eax, eax
    cmp dword ptr [rip + nota_evento], edi
    jne .fim_valida
    mov eax, dword ptr [rip + nota_no_acento]
.fim_valida:
    ret

.section .rodata
.align 16
sem_sinal_r: .long 0x7fffffff, 0x7fffffff, 0x7fffffff, 0x7fffffff

.section .note.GNU-stack,"",@progbits
