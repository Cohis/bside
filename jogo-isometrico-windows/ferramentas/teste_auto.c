/* Robô de teste da Sala 2 (só para `make teste`; o jogo não usa este arquivo).
 *
 * Ligado com -Wl,--wrap=IsKeyDown,--wrap=IsKeyPressed,--wrap=EndDrawing, troca
 * o teclado por decisões tomadas a cada quadro a partir do estado do jogo.
 *   BSIDE_BOT=loja    tenta a porta antes da hora, pega o bilhete, erra uma nota e
 *                     toca D-C-G no depósito, lê a etiqueta e sai para o galpão
 *   BSIDE_BOT=galpao  anda até a 7ª estante, pega o disco e fala com o agente
 *   BSIDE_BOT=doca    atravessa os 3 pontos; erra de propósito uma vez no 2º
 * Salva capturas em teste/ e sai com 0 se chegou ao fim, 1 se estourou o tempo.
 */
#include <math.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

bool __real_IsKeyDown(int tecla);
bool __real_IsKeyPressed(int tecla);
void __real_EndDrawing(void);
void TakeScreenshot(const char *arquivo);
void rlDrawRenderBatchActive(void);

extern float icaro[];
extern int controle_jogador, metro_ativo, doca_estado, andar_indice;
extern float metro_fase;
extern char *doca_ponto;
extern int alto_falantes[];
extern unsigned char flags[];

enum { K_W = 87, K_A = 65, K_S = 83, K_D = 68, K_E = 69, K_1 = 49 };

static bool segura[512], aperta[512];
static int quadro, modo = -1, passo_galpao, pontos_feitos, estado_antes = -1;
static int ultimo_pulso = -1, falhas, quadro_fim = -1;
static char captura[64];

bool __wrap_IsKeyDown(int t) { return t >= 0 && t < 512 && segura[t]; }
bool __wrap_IsKeyPressed(int t) { return t >= 0 && t < 512 && aperta[t]; }

static void capturar(const char *nome) { snprintf(captura, sizeof captura, "teste/%s.png", nome); }

/* Anda um eixo de cada vez: +x = D+S, -x = A+W, +y = S+A, -y = W+D. */
static bool andar_ate(float x, float y)
{
    float dx = x - icaro[0], dy = y - icaro[1];
    if (fabsf(dx) > 2.0f) {
        if (dx > 0) segura[K_D] = segura[K_S] = true;
        else segura[K_A] = segura[K_W] = true;
        return false;
    }
    if (fabsf(dy) > 2.0f) {
        if (dy > 0) segura[K_S] = segura[K_A] = true;
        else segura[K_W] = segura[K_D] = true;
        return false;
    }
    return true;
}

static void decidir_galpao(void)
{
    static const float rota1[][2] = {{28, 52}, {28, 262}, {64, 262}};
    static const float rota2[][2] = {{64, 280}, {260, 280}, {260, 310}};
    static int quadro_disco = -1;
    if (flags[2] && quadro_disco < 0) quadro_disco = quadro;
    if (quadro == quadro_disco + 110) capturar("galpao_mael");
    if (controle_jogador == 0) {
        if (quadro % 30 == 0) aperta[K_E] = true;     /* fecha mensagens */
        return;
    }
    if (!flags[2]) {
        if (passo_galpao < 3) {
            if (andar_ate(rota1[passo_galpao][0], rota1[passo_galpao][1])) passo_galpao++;
        } else if (quadro % 20 == 0) {
            capturar("galpao_caixa");
            aperta[K_E] = true;
        }
        return;
    }
    if (passo_galpao == 3) { capturar("galpao_disco"); passo_galpao = 4; }
    if (passo_galpao < 7) {
        if (andar_ate(rota2[passo_galpao - 4][0], rota2[passo_galpao - 4][1])) passo_galpao++;
    } else if (!flags[3] && quadro % 20 == 0) {
        capturar("galpao_agente");
        aperta[K_E] = true;
    }
    if (andar_indice == 3 && quadro_fim < 0) quadro_fim = quadro + 90;
}

/* Flags de sala2.s: 1 saiu, 5 bilhete, 6 melodia, 7 endereço. */
static void decidir_loja(void)
{
    /* x, y e o que fazer ao chegar: 0 seguir, 1 apertar E, 2 tocar a melodia */
    static const int rota[][3] = {
        {176, 188, 0}, {30, 188, 1},                      /* porta, ainda sem endereço */
        {288, 188, 1},                                    /* bilhete no balcão */
        {240, 188, 0}, {240, 262, 0}, {208, 262, 1},      /* depósito: a lista */
        {288, 262, 2},                                    /* estante leste: melodia */
        {288, 262, 1},                                    /* etiqueta da caixa caída */
        {240, 262, 0}, {240, 188, 0}, {30, 188, 1},       /* porta, agora com endereço */
    };
    static const int notas[] = {2, 1, 0, 3};              /* E (errada), D, C, G */
    static int passo, nota, espera, porta_testada, quadro_melodia = -1;
    static const char *pendente;                          /* captura com o texto inteiro */
    static int quadro_pendente;
    static const unsigned char exigida[] = {0, 0, 5, 0, 0, 0, 6, 7, 0, 0, 1};
    if (flags[6] && quadro_melodia < 0) quadro_melodia = quadro;
    if (quadro == quadro_melodia + 32) capturar("loja_caixa_caindo");
    if (quadro == quadro_melodia + 70) capturar("loja_caixa_chao");
    if (controle_jogador == 0) {
        if (quadro % 30 == 0) aperta[K_E] = true;         /* completa e fecha mensagens */
        if (pendente && quadro % 30 == 15 && quadro - quadro_pendente > 20) { capturar(pendente); pendente = 0; }
        return;
    }
    if (passo == 2 && !porta_testada) {
        porta_testada = 1;
        if (flags[1]) { printf("robô: a porta abriu sem o endereço\n"); exit(1); }
    }
    if (passo >= (int)(sizeof rota / sizeof rota[0])) {
        if (andar_indice == 2 && quadro_fim < 0) quadro_fim = quadro + 30;
        return;
    }
    if (!andar_ate((float)rota[passo][0], (float)rota[passo][1])) return;
    int acao = rota[passo][2], flag = exigida[passo];
    if (acao == 0 || (flag && flags[flag])) { passo++; espera = 0; return; }
    if (++espera % 25) return;
    if (acao == 1) {
        static const char *nomes[] = {0, "loja_porta_trancada", "loja_bilhete", 0, 0, "loja_lista",
                                      0, "loja_etiqueta", 0, 0, "loja_porta"};
        pendente = nomes[passo];
        quadro_pendente = quadro;
        aperta[K_E] = true;
        if (!flag) passo++;                              /* só a mensagem: segue */
    } else if (nota < 4) {
        if (nota == 1) capturar("loja_melodia");
        aperta[K_1 + notas[nota++]] = true;
    }
}

static void decidir_doca(void)
{
    static int quadro_falha = -1;
    if (doca_estado == 3 && estado_antes != 3) quadro_falha = quadro;
    if (quadro == quadro_falha + 45) capturar("doca_grito");
    if (doca_estado != estado_antes) {
        char nome[32];
        snprintf(nome, sizeof nome, "doca_p%d_e%d", pontos_feitos + 1, doca_estado);
        if (doca_estado >= 1 && doca_estado <= 4) capturar(nome);
        if (doca_estado == 6 && estado_antes == 5) pontos_feitos++;
        estado_antes = doca_estado;
    }
    if (doca_estado == 1 && metro_ativo) {
        int alvo = (int)floorf(metro_fase + 0.5f);
        if (alvo % 4 == 3 && fabsf(metro_fase - alvo) < 0.04f && alvo != ultimo_pulso) {
            ultimo_pulso = alvo;
            int certo = *(int *)(doca_ponto + 24), isca = *(int *)(doca_ponto + 28);
            int falante = certo;
            if (pontos_feitos == 1 && falhas == 0 && isca >= 0) { falante = isca; falhas++; }
            aperta[K_1 + alto_falantes[falante * 4 + 3]] = true;
        }
    } else if (doca_estado == 2) {
        andar_ate((float)*(int *)(doca_ponto + 8), (float)*(int *)(doca_ponto + 12));
    } else if (doca_estado == 0 || doca_estado == 6) {
        if (quadro % 30 == 0) aperta[K_E] = true;     /* fecha mensagens */
    }
    if (pontos_feitos == 3 && quadro_fim < 0) quadro_fim = quadro + 120;
}

void __wrap_EndDrawing(void)
{
    if (captura[0]) {
        rlDrawRenderBatchActive();
        TakeScreenshot(captura);
        captura[0] = 0;
    }
    __real_EndDrawing();
    if (modo < 0) {
        const char *m = getenv("BSIDE_BOT");
        modo = m && strcmp(m, "galpao") == 0 ? 1 : m && strcmp(m, "doca") == 0 ? 2
             : m && strcmp(m, "loja") == 0 ? 3 : 0;
    }
    memset(segura, 0, sizeof segura);
    memset(aperta, 0, sizeof aperta);
    quadro++;
    if (modo == 1) decidir_galpao();
    else if (modo == 2) decidir_doca();
    else if (modo == 3) decidir_loja();
    if (quadro == quadro_fim) {
        printf("robô: fim no quadro %d (pontos %d, falhas provocadas %d)\n", quadro, pontos_feitos, falhas);
        exit(0);
    }
    if (quadro > 60 * 180) {
        printf("robô: tempo esgotado (pontos %d, estado %d, x %.0f y %.0f)\n", pontos_feitos, doca_estado, icaro[0], icaro[1]);
        exit(1);
    }
}
