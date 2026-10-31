# Status — elenco da Sala 2

## Etapa atual

Etapa 1 — folhas de identidade. **Incompleta e bloqueada antes do portão de aprovação.**

## Pronto

- Briefing, ficha visual, contrato e lições da primeira onda lidos.
- Bases sul, leste, norte e sudeste de Ícaro e Eva, quadros aprovados de caminhada, folhas originais e imagens de contexto abertas para referência visual.
- As referências necessárias estão disponíveis no disco.

## Entregáveis da Etapa 1

- `agente/referencia-8-vistas.png` — não gerado.
- `anjo/referencia.png` — não gerado.
- `hank/referencia-8-vistas.png` — não gerado.
- `revisao/etapa1-prancha.png` — não montada.

Nenhuma imagem foi gerada ou rejeitada; nenhuma prancha foi apresentada para aprovação.

## Bloqueio e próximo passo

A ferramenta integrada `image_gen` não está disponível nesta sessão. A skill `imagegen` exige usá-la por padrão e proíbe mudar para a CLI/API sem confirmação explícita; por isso, nenhuma geração foi substituída por um fluxo alternativo.

Próximo passo: disponibilizar `image_gen` nesta sessão ou confirmar explicitamente o modo CLI/API e configurar `OPENAI_API_KEY` localmente. Depois, gerar as três folhas com referências visuais de Ícaro **e** Eva em cada chamada, montar a prancha comparativa, registrar prompts e verificações e então parar para aprovação.

## 30/out — agente carmesim refeito sem geração por IA

A pedido do usuário, o agente passou a ser a própria base da Eva repintada por script
(`jogo-isometrico/ferramentas/gerar_agente.py`), não mais o briefing de veste longa com máscara de
porcelana: farda militar preta com cinto, gola e punhos vermelhos e máscara preta cobrindo a
cabeça inteira, só os olhos azuis à mostra. Prontos: `agente/bases/<direcao>.png` (8 paradas,
384 × 512, âncora 192,480) e `agente/referencia-8-vistas.png`. Já integrado ao jogo (doca).
No galpão, a pedido do usuário, o agente agora aparece de pé com a pose sul nova (a sentada antiga saiu de cena). Falta: caminhada.

## 30/out — anjo a partir da folha do usuário

O usuário baixou `anjo/folha-original.png` (8 vistas em pé/andando, fundo preto, sem
contorno). Como a doca precisa de pousado, grito e voo, as três poses foram geradas no
ChatGPT (navegador do usuário, com autorização dele) usando essa folha como referência:
`anjo/poses-chatgpt.png`. `jogo-isometrico/ferramentas/gerar_anjo.py` recorta tudo para
`anjo/bases/` e `anjo/poses/`. No jogo: agachado nos cabeços escutando, voa de asas abertas
virado para onde vai, grita de pé. As 8 vistas ficam no atlas, ainda sem uso direto.
