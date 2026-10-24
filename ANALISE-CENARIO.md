# Planta da loja, câmera e colisões

## Planta e câmera

A matriz permanece com 192 × 144 células. Cada losango mede 32 × 16 pixels antes do zoom; a projeção usa `sx = 640 + 16(x − y)` e `sy = 360 + 8(x + y)`. A janela continua em 1280 × 720, com zoom 1,5×. A câmera acompanha os pés de Ícaro e mantém o personagem no centro da área de jogo.

As áreas ficam distribuídas em torno do salão principal:

- **Entrada e cafeteria**, no lado sul: capacho, piso de madeira, balcão, máquina de espresso e mesas.
- **Salão de vinis**, no centro: ilhas de estantes baixas, caixas de discos, plantas e tapete de lançamentos. Corredores cruzados contornam as ilhas.
- **Sala de escuta**, na ala oeste: piso acarpetado, estantes laterais e três toca-discos destacados.
- **Estoque e oficina**, ao norte: piso metálico, prateleiras altas, caixas e bancada de reparos.
- **Banheiro**, na ala leste: lavatório, cabine e louças sanitárias.

Portas com vãos largos conectam as alas. Há duas passagens entre cafeteria e salão, sala de escuta e salão, estoque e área de serviço, além de dois acessos para o banheiro. O ponto inicial de Ícaro é a célula `(36, 132)`, dentro da entrada.

## Tipos da matriz

`mapa_tiles`, em `bside.s`, determina tanto o que é desenhado quanto o que bloqueia o movimento. As tabelas `layout_pisos`, `layout_paredes` e `layout_mobiliario` descrevem os retângulos do cenário.

| Tipo | Desenho | Movimento |
|---|---|---|
| `0` | Piso de pedra do salão | Livre |
| `1` | Estante de discos | Bloqueado |
| `2` | Caixa expositora | Bloqueado |
| `3` | Balcão ou bancada | Bloqueado |
| `4` | Planta | Bloqueado |
| `5` | Limite externo | Bloqueado |
| `6` | Toca-discos | Bloqueado |
| `7`, `9` | Tapetes | Livre |
| `8` | Parede interna | Bloqueado |
| `F` | Piso de madeira da cafeteria | Livre |
| `L` | Carpete da sala de escuta | Livre |
| `W` | Piso metálico da oficina | Livre |
| `T` | Piso de pedra do banheiro | Livre |
| `d` | Mesa de cafeteria | Bloqueado |
| `m` | Máquina de espresso | Bloqueado |
| `s` | Pia | Bloqueado |
| `t` | Vaso sanitário | Bloqueado |

Paredes e móveis compartilham a mesma matriz de colisão. As faces e os detalhes usam as texturas existentes de pedra, madeira, metal, papel de parede e tapete; capas coloridas ficam concentradas nas estantes.

## Movimento e conferência

Antes de aceitar uma posição, o jogo converte os pés de Ícaro para coordenadas da matriz. O ponto central e quatro amostras em volta precisam cair em piso livre. O jogo testa os eixos separadamente para permitir que ele deslize ao longo de móveis e paredes.

`BSIDE_COLISOES=1` mostra o contorno magenta das células sólidas, permitindo comparar a arte com a área bloqueada. A malha foi percorrida a partir da entrada para conferir a conexão das seis áreas; os pontos do salão, sala de escuta, estoque, oficina e banheiro permanecem alcançáveis.
