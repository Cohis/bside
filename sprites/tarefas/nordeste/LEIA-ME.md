# Nordeste — revisão após edição controlada

As 16 células continuam em `icaro/` e `eva/`, RGBA 384×512, oito fases por personagem. Os originais dos oito quadros retocados estão preservados em `correcoes/*-antes.png`; os demais permaneceram intactos. As transformações de cada quadro indicam fontes e operação. Nenhum dos dois ciclos está aprovado.

Ícaro: 02 agora mostra apoio esquerdo, 04/06 trazem a pulseira no pulso esquerdo anatômico, 07 aproxima o pé de balanço da perna de apoio. Eva: 04–06 têm manga direita contínua e mão visível, 07 aproxima o pé de balanço. Tudo foi composto com pixels dos próprios quadros nordeste, sem espelhamento de personagem ou acessórios; geração pontual adicional para 01/08 foi rejeitada.

`*-prancha-claro/escuro.png`, `*-normal/lento.gif` (100/400ms), `*-normal/lento-chao.gif` e `*-chao-prancha.png` mostram a revisão. O piso marcado usa uma hipótese de 13 px/quadro, **não calibrada**. Os arquivos `icaro/revisao.json` e `eva/revisao.json` registram as pendências. Em ambos, 07→08 e 08→01 ainda mudam o pé de apoio e a projeção de forma brusca; o contato esquerdo de 01 não segue o guia. Não usar esta direção como animação final sem reautoria das pernas 01/08 e inspeção de novo.

`correcoes/reautoria-01-08.json` indexa os candidatos recusados. A tentativa manual de substituir o par de pernas criou corte de cintura e foi preservada somente como diagnóstico, sem alterar os PNGs ativos.

Não executar `enquadrar.py` durante a montagem: ele recompõe os quadros a partir de `raw/` e apagaria as correções. Para atualizar técnica, pranchas e GIFs sem modificar quadros, usar `python correcoes/atualizar_evidencias.py` nesta pasta.

Em 24/out, foram testados novos enxertos integrais de calça e tênis da fase 07 na 08 e rearticulação separada dos dois membros para 01, sempre mantendo tronco e acessórios originais. Os quatro ensaios foram rejeitados: o 01 rompe/afina contornos e fragmenta calçados; o 08 repete a pose de 07, congela o apoio e não fecha 08→01. Nenhum PNG ativo foi alterado. Cópias de 01/08 e suas transformações, hashes SHA-256, ensaios e motivos estão em `correcoes/originais-01-08-2026-10-24/manifesto.json`.
