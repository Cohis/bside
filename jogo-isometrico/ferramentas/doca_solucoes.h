/* Gerado por ferramentas/gerar_doca.py. Não editar à mão.
 * Para o robô de teste: em cada ponto da fuga, a nota da solução, a de uma
 * armadilha e o caminho (ms desde a nota, x, y) que o solucionador achou. */

static const short cam_doca_1[][3] = {{0, 66, 38}, {500, 42, 38}, {3500, 42, 182}};
static const short cam_doca_2[][3] = {{0, 50, 190}, {83, 54, 190}, {500, 54, 170}, {1333, 94, 170}, {1416, 94, 166}, {1500, 98, 166}, {1583, 98, 162}, {1666, 102, 162}, {1750, 102, 158}, {1833, 106, 158}, {1916, 106, 154}, {3583, 186, 154}, {4666, 186, 206}, {4750, 182, 206}};
static const short cam_doca_3[][3] = {{0, 178, 202}, {83, 182, 202}, {416, 182, 218}, {750, 198, 218}, {1750, 198, 170}, {3916, 302, 170}, {6000, 302, 270}, {6083, 306, 270}, {6916, 306, 310}};
static const short cam_patio_1[][3] = {{0, 34, 34}, {2000, 130, 34}, {3666, 130, 114}};
static const short cam_patio_2[][3] = {{0, 130, 122}, {83, 134, 122}, {333, 134, 134}, {2166, 222, 134}, {4166, 222, 38}};
static const short cam_patio_3[][3] = {{0, 226, 34}, {250, 226, 22}, {4000, 226, 202}};
static const short cam_patio_4[][3] = {{0, 226, 210}, {166, 234, 210}, {1750, 234, 286}, {1916, 242, 286}, {2250, 242, 302}, {2333, 246, 302}, {2416, 246, 306}, {2500, 250, 306}, {2583, 250, 310}, {2666, 254, 310}, {2750, 254, 314}, {2833, 258, 314}, {2916, 258, 318}, {3083, 266, 318}, {3166, 266, 322}, {3250, 270, 322}, {3333, 270, 326}, {4416, 322, 326}, {4500, 322, 322}};
static const short cam_quebramar_1[][3] = {{0, 42, 42}, {333, 58, 42}, {1416, 58, 94}, {1500, 62, 94}, {1583, 62, 98}, {1666, 66, 98}, {1750, 66, 102}, {1833, 70, 102}, {2166, 70, 118}, {4583, 186, 118}};
static const short cam_quebramar_2[][3] = {{0, 194, 122}, {416, 174, 122}, {500, 174, 118}, {666, 182, 118}, {2000, 182, 182}, {4666, 54, 182}, {5583, 54, 226}};
static const short cam_quebramar_3[][3] = {{0, 50, 234}, {83, 54, 234}, {666, 54, 262}, {5333, 278, 262}, {6416, 278, 314}};

#define N_PONTOS_FUGA 10
static const int fuga_nota[] = {3, 2, 1, 0, 3, 2, 1, 1, 0, 3};
static const int fuga_nota_armadilha[] = {0, 0, 0, 1, 0, 0, 0, 0, 1, 0};
static const short (*const fuga_caminho[])[3] = {cam_doca_1, cam_doca_2, cam_doca_3, cam_patio_1, cam_patio_2, cam_patio_3, cam_patio_4, cam_quebramar_1, cam_quebramar_2, cam_quebramar_3};
static const int fuga_n_caminho[] = {(int)(sizeof cam_doca_1 / sizeof cam_doca_1[0]), (int)(sizeof cam_doca_2 / sizeof cam_doca_2[0]), (int)(sizeof cam_doca_3 / sizeof cam_doca_3[0]), (int)(sizeof cam_patio_1 / sizeof cam_patio_1[0]), (int)(sizeof cam_patio_2 / sizeof cam_patio_2[0]), (int)(sizeof cam_patio_3 / sizeof cam_patio_3[0]), (int)(sizeof cam_patio_4 / sizeof cam_patio_4[0]), (int)(sizeof cam_quebramar_1 / sizeof cam_quebramar_1[0]), (int)(sizeof cam_quebramar_2 / sizeof cam_quebramar_2[0]), (int)(sizeof cam_quebramar_3 / sizeof cam_quebramar_3[0])};
