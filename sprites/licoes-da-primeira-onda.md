# Correções que as próximas direções devem evitar

Estas observações complementam o contrato; não alteram bases, ritmo ou câmera.

1. O nome da fase não basta. Descreva qual perna está próxima da câmera, qual sustenta, onde passa o pé elevado e qual braço avança. A geração pode repetir a última pose mesmo com número diferente.
2. Em03/07, o pé elevado passa perto da perna de apoio. Pé estendido muito à frente já sugere04/08; não aprovar isso como passagem. Inspecionar lado anatômico e tipo de pose são duas verificações separadas.
3. Em02/06, conferir a flexão da perna de apoio e a saída do pé traseiro, além do contrabalanço dos braços. Roupa e bolso visível ajudam a rastrear o membro, mas não substituem anatomia.
4. A âncora(192,480) é a posição do personagem no cenário. Alinhar toda sola mais baixa em480 apaga a projeção do recuo do apoio nas vistas frontal/traseira/diagonal. Fixar o eixo e a escala pela cabeça/torso e preservar os pisos projetados.
5. Não usar boundingbox da pose inteira como eixo automático: braço e cabelo alteram a caixa. Não esticar membros nem usar escala diferente nos eixos.
6. Pulseira de Ícaro é esquerda anatômica. A base leste já esconde a pulseira no braço distante; não recolocar no braço próximo. Sudeste/sudoeste/nordeste/noroeste exigem raciocinar pela lateral, não espelhar.
7. Referências com todas as vistas podem induzir câmera errada. Usar como principais a base e o recorte exclusivo da direção; originais e vizinhas são apoio de identidade.
8. Registro de rastreamento deve separar observação de estimativa. Joelho sob calça larga não é um ponto medido com precisão; documente a oclusão. A passada de teste deve vir do recuo observado do apoio.

Cada direção exige revisão independente do coordenador após a revisão do agente. Não declarar final por ter todos os arquivos.
