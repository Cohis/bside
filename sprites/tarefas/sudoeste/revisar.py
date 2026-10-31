from pathlib import Path
import json
D=Path(__file__).resolve().parent
if (D/'correcoes'/'correcoes-selecionadas.json').exists():
 raise SystemExit('Revisão corrigida registrada em revisao.json e teste-chao.json; este script antigo sobrescreveria os dados.')
# Estimativas visuais na célula normalizada; não são o guia ideal nem medição automática.
pes={'icaro':[
 [[139,488],[249,470]],[[164,479],[262,443]],[[221,484],[180,451]],[[259,475],[139,471]],[[254,467],[120,481]],[[279,474],[137,480]],[[222,414],[153,485]],[[139,478],[249,466]]],
'eva':[
 [[140,480],[240,453]],[[155,494],[263,455]],[[224,488],[171,424]],[[263,489],[145,448]],[[258,481],[125,490]],[[279,470],[140,490]],[[232,463],[164,489]],[[122,501],[247,476]]]
}
for c in pes:
 frames=[]
 for i,feet in enumerate(pes[c],1):
  apoio='esquerda' if i<=4 else 'direita';legs={}
  for side,idx in [('esquerda',0),('direita',1)]:
   toe=feet[idx]; ankle=[toe[0]+16,toe[1]-17];hip=[205 if idx==0 else 179,310+({2:4,6:4,4:-2,8:-2}.get(i,0))]; knee=[round((hip[0]+ankle[0])/2)-8,round((hip[1]+ankle[1])/2)]
   legs[side]={'quadril':hip,'joelho':knee,'tornozelo':ankle,'ponta_pe':toe,'contato_chao':side==apoio or i in [1,5],'confianca':'baixa nas juntas ocultas; média na ponta visível','observacao':'quadril e joelho inferidos sob a roupa; tornozelo inferido dentro do calçado; ponta estimada visualmente, não ponto rastreado automaticamente'}
  frames.append({'fase':i,'apoio_principal':apoio,'juntas':legs})
 support=[pes[c][i][0][0] for i in range(4)]+[pes[c][i][1][0] for i in range(4,8)]
 dx=[support[i+1]-support[i] for i in [0,1,2,4,5,6]]; avg=sum(dx)/6
 tracking={'tipo':'estimativa visual manual, não medição validada','incerteza_px':{'ponta_pe':5,'tornozelo':8,'quadril':10,'joelho':20},'quadros':frames,'recuo_apoio_x_por_transicao':dx,'passada_teste_px_por_quadro':round(avg/.70710678,2),'calibracao_aprovada':False,'observacao':'Recuo em x positivo pois personagem olha esquerda; sequência irregular e projeção vertical não segue plano constante. Média apenas inicial para teste de chão, não comprovação de ausência de patinação.'}
 (D/c/'rastreamento.json').write_text(json.dumps(tracking,ensure_ascii=False,indent=2))
 pend=['Ícaro07: três tentativas; v3 corrige identidade da perna mas eleva excessivamente o pé/joelho. Reprovado, requer diagnóstico do coordenador.','Recepções02/06 têm flexão insuficiente do apoio; a queda global de4px não corrige anatomia.','Recuo de apoio irregular em x/y e variação de comprimento/projeção nos avanços; continuidade com chão ainda não aprovada.'] if c=='icaro' else ['Eva03-v2 melhora lado e direção do joelho, mas elevação é maior que a passagem07: assimetria do ciclo.','Eva02 tem proporção de pernas maior; exportação usa escala uniforme.335 para preservar a sola inteira, cabeça difere levemente.','Eva04-v2 corrige troca de pernas, mas projeção do apoio altera o chão aparente. Eva08 apresenta extensão maior e pé próximo à margem inferior.','Recepções02/06 têm flexão insuficiente; irregularidade de apoio, escala e projeção exige correção antes de aprovação.']
 review={'aprovado':False,'quadros_revisados':list(range(1,9)),'transicoes_revisadas':['04→05','08→01'],'observacoes':['16 PNGs produzidos e exportados, 8 por personagem; fundo alpha real, dimensões384x512, sem duplicatas exatas.','Pranchas claras/escuras e GIFs100/400ms gerados. Inspeção estática realizada; reprodução contínua e teste de chão NÃO foram aprovados.','Escala pela cabeça/topo-queixo e eixo do tronco; preserva deslocamento projetado da sola sem alinhá-la artificialmente480.','Roupa e acessórios mantidos; Ícaro pulseira esquerda, Eva sem pulseira.'],'pendencias':pend,'passada_teste_px_por_quadro':tracking['passada_teste_px_por_quadro'],'calibracao_aprovada':False,'validacao_temporal_realizada':False}
 (D/c/'revisao.json').write_text(json.dumps(review,ensure_ascii=False,indent=2))
(D/'REVISAO.md').write_text('# Sudoeste — produção entregue para revisão\n\n16 células exportadas,21 gerações preservadas. As duas combinações estão REPROVADAS/PENDENTES. Consulte revisao.json por personagem.\n\nÍcaro07 atingiu três tentativas: v1 mantém pé atrás, v2 troca a perna elevada, v3 corrige o lado mas eleva demais. Não repetir sem novo diagnóstico. Eva05-v2 corrige contato trocado;03-v2 corrige perna distante;04-v2 corrige avanço trocado.\n\nEnquadramento uniforme e sem suavização, marcos de cabeça observados manualmente. Nenhum membro foi deformado. As solas não foram niveladas em480. A variação de tamanho/projeção restante é explícita.\n\nRastreamento é estimado visualmente e não garante anatomia oculta. GIFs são instrumentos de revisão, sua existência não significa aprovação temporal.\n')
print('Revisões e rastreamento salvos')
