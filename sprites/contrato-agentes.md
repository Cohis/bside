# Contrato de execução por direção

O coordenador revisou e congelou as 16 bases em `bases/congeladas.json`. Leia `ficha-visual.md`, `contrato.json`, este arquivo e o plano do usuário. Não modifique arquivos comuns. Escreva apenas em `tarefas/<sua-direcao>/`.

## Entradas

- Originais intactos: `/home/icaro/Documentos/AOC/Ícaro.png` e `eva.png`.
- Recortes: `referencias/<personagem>/<direcao>.png`; inspecione também as duas vizinhas na ordem circular do contrato.
- Base fixa: `bases/<personagem>/<direcao>.png` (384×512), mais o raw selecionado em `registros/geracoes/` se necessário.
- Guias anatômicos: `guias/<direcao>/01.png` a `08.png` e JSONs com juntas, apoio e deslocamento de teste. Laranja = esquerda anatômica, azul = direita. Guias são esquemáticos: não copiar cores ou contorno, respeitar proporções da base.
- As pernas mantêm 90+90 unidades no esqueleto 3D, projetadas na câmera; o guia representa movimento sob a calça larga. A aparência da base manda nas proporções finais.

## Produção obrigatória

Use `image_gen` embutido, uma imagem por chamada, um personagem por imagem, fundo alpha real. Não usar fallback CLI, não deformar membros por código nem simular caminhada deslocando a figura inteira. Pode gerar Ícaro e Eva em paralelo, com fases compatíveis. Não gere grade de várias poses em uma chamada.

1. Contatos 01 e 05 para ambos.
2. Passagens 03 e 07 para ambos.
3. Inspecione e revise esses quatro quadros de cada personagem antes de prosseguir.
4. Recepções 02 e 06.
5. Avanços 04 e 08.
6. Revise oito fases e transições 04→05, 08→01; crie pranchas de inspeção e opcionalmente GIF de revisão, além dos PNGs.

Cada chamada recebe a BASE FIXA, o GUIA DA FASE e imagens aprovadas pertinentes. Nunca usar somente o último quadro. Leia/view_image de cada imagem local antes de referenciar na geração. Registre o prompt integral, caminhos e resultado em sua pasta. A imagem gerada deve ser copiada para sua pasta; não deixar dependência somente de ~/.codex/generated_images.

Modelo de prompt: "Produza somente [personagem], direção [direção], fase [número/descrição]. A base define identidade, escala, câmera, paleta e acabamento. O guia define pose. Preserve membros, roupa e acessórios. Apoio [lado]; balanço [lado]; contatos [descrição]. Modifique apenas o necessário. Corpo inteiro, fundo transparente, sem texto, objetos, mudança de perspectiva ou suavização."

## Anatomia e ritmo

01 contato esquerdo; 02 recepção esquerda; 03 passagem direita; 04 avanço direito; 05 contato direito; 06 recepção direita; 07 passagem esquerda; 08 avanço esquerdo. Sempre pelo menos um pé no chão. Braço oposto à perna. Apoio recua em relação ao corpo; balanço levanta, passa e avança. Quadril desce na recepção. Frente/costas usam profundidade, sobreposição e flexão, não pernas abrindo lateralmente. Pulseira de Ícaro sempre no ESQUERDO: no leste fica no braço distante, não no próximo. Sem espelhamento.

## Exportação e alinhamento

`python sprites/scripts/normalizar.py RAW SAIDA [--altura 424] [--solo 480] [--eixo EIXO_RAW] [--escala FATOR]` é somente enquadramento técnico: remove ruído alfa <8, recorta, aplica uma escala uniforme por vizinho mais próximo, posiciona. Não redesenha. Use altura/bob apropriados à fase, evite normalizar o movimento vertical a zero. Preferir escala baseada na cabeça/torso da base e eixo corporal; não recentrar automaticamente entre pés a cada fase, pois isso cria oscilação lateral. A ferramenta gera JSON da transformação. Compare cabeça e proporções para evitar redimensionamento variável.

PNG individual final: `tarefas/<direcao>/<personagem>/01.png` … `08.png`, RGBA 384×512. Não copiar a pose parada para fingir movimento. A coluna 00 será fornecida pelo coordenador a partir da base. Não escrever na pasta final.

`revisao.json` por personagem: `{"aprovado":true/false,"observacoes":[...],"quadros_revisados":[1,2,3,4,5,6,7,8],"transicoes_revisadas":["04→05","08→01"],"pendencias":[...]}`. Só marque aprovado se as verificações forem realmente realizadas e passarem. Verifique transparência sobre claro/escuro, margens, identidade, mesma câmera, pernas, comprimento, mãos/pés, apoio, ausência de duplicatas e continuidade. Registre medidas/rastreamento de quadril, joelhos, tornozelos e ponta dos pés, distinguindo oclusão de desaparecimento. O coordenador fará revisão independente.

Após três tentativas malsucedidas para o mesmo defeito, registre a pendência e informe o coordenador com diagnóstico; não declare conclusão. Não delegue a outros agentes. Não altere as bases congeladas; informe um problema encontrado nelas.
