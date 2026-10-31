# Sprites de caminhada — Ícaro e Eva

Consulte `validacao.md` para o estado real da produção. Enquanto houver revisões pendentes, esta pasta contém apenas ferramentas de prévia; as duas folhas finais ainda não estão liberadas.

Abra `previa.html` no navegador. A página funciona localmente, sem instalação ou servidor. Escolha personagem, direção e pose. Use pausa e os botões de quadro para inspecionar as transições. O fundo claro, escuro ou quadriculado permite conferir transparência. O chão marcado e a passada de teste ajudam a observar patinação; eles não são desenhados nos PNGs. A opção de rastreamento mostra as juntas estimadas sobre o personagem: esquerda em laranja e direita em azul. O texto abaixo da imagem informa as pendências do ciclo selecionado. Valores de passada são provisórios enquanto a revisão estiver pendente.

## Formato contratado

- Célula: 384 × 512 pixels; âncora de posição do personagem: (192,480).
- Folha: 3456 × 4096 pixels, nove colunas e oito linhas.
- Coluna0: parado. Colunas1–8: caminhada,100ms por quadro, ciclo de800ms.
- Linhas: norte, nordeste, leste, sudeste, sul, sudoeste, oeste, noroeste.
- Norte mostra costas; sul mostra frente. Os lados esquerdo/direito das fases são anatômicos.
- Caminhada no lugar: a engine controla o deslocamento. A pose parada não entra no loop.

Quando aprovadas, as folhas serão `icaro-andar.png` e `eva-andar.png`; `animacoes.json` descreverá os retângulos, durações e caminhos dos quadros individuais em `quadros/`.

Referências, bases, guias, gerações e prompts ficam nas pastas vizinhas. Os originais na raiz do projeto não foram alterados. Integração com engine não faz parte desta entrega.
