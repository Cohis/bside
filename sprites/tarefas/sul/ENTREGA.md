# Direção sul — pacote completo para revisão

16 quadros de caminhada gerados individualmente e exportados em RGBA384×512, oito de Ícaro e oito de Eva. As poses paradas pertencem ao pacote comum. Nenhuma alteração fora desta pasta.

`icaro/01.png` a `08.png` e `eva/01.png` a `08.png` são os selecionados. Originais gerados e tentativas rejeitadas estão em `raws/`; prompts integrais e referências em `registros/`; cada PNG selecionado tem JSON da transformação. Enquadramento é uniforme por imagem com vizinho mais próximo, sem redesenho ou espelhamento.

As chaves01/03/05/07 foram aceitas pelo coordenador. O ciclo completo foi inspecionado quadro a quadro nas pranchas `icaro-ciclo.png` e `eva-ciclo.png`, com atenção04→05 e08→01. GIFs normal100ms e lento400ms foram preparados, assim como `previa-revisao.html`. A inspeção temporal contínua no navegador não foi realizada pelo agente; isso está explicitamente pendente.

`validar.py` reproduz checagens técnicas e rastreamento. `rastreamento.json` distingue medidas da borda dos calçados e estimativas das juntas ocultas. Recuos do apoio variam bastante no último impulso; média de deslocamento não garante ausência de patinação. Diferenças negativas de1–2px no fechamento estão dentro da incerteza±3px da borda/rotação. Nenhuma irregularidade foi ocultada por deformação.

**Aprovação final: pendente.** Os dois `revisao.json` mantêm `aprovado:false`, com resultado técnico positivo e pendências visuais explícitas para o coordenador. Não declarar a direção concluída até a revisão temporal e do chão marcado.
