"""Quantifica resíduo de deslizamento com base nos pontos visuais já rastreados."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
report={}
for p,v in (('icaro',43),('eva',39)):
 folder=R/p;tr=json.loads((folder/'rastreamento.json').read_text())
 if not tr.get('correcao_sola_baixa_aplicada'):
  for n in (3,7):
   q=next(x for x in tr['quadros'] if x['quadro']==n)
   side='direita' if n==3 else 'esquerda'
   q[side]['tornozelo_estimado'][1]+=8 if p=='icaro' else 5
   q[side]['ponta_pe_observada_aproximada'][1]+=11 if p=='icaro' else 7
   q['incerteza_px']['pontas']=12
  tr['correcao_sola_baixa_aplicada']=True
 tr['passada_teste_px_por_quadro']=v
 tr['formula']='Velocidade visual calibrada pela média de deslocamento x dos dois apoios em 3 intervalos; marcas do chão à direita. Não certifica contato sem imagem temporal.'
 tr['advertencia']='Pontos estimados com incerteza ≈10–12 px. Resíduo de patinação calculado em x; projeção vertical da sola/oclusão exige revisão visual.'
 (folder/'rastreamento.json').write_text(json.dumps(tr,ensure_ascii=False,indent=2)+'\n')
 phases=[]
 for start,side in ((1,'esquerda'),(5,'direita')):
  xs=[next(q for q in tr['quadros'] if q['quadro']==n)[side]['ponta_pe_observada_aproximada'][0] for n in range(start,start+4)]
  residual=[x-v*i for i,x in enumerate(xs)]
  phases.append({'fases':list(range(start,start+4)),'perna_apoio':side,'pontas_x_estimadas':xs,
                 'recuo_por_intervalo':[xs[i+1]-xs[i] for i in range(3)],
                 'velocidade_teste_px_quadro':v,'residuo_mundo_x':residual,
                 'amplitude_residuo_px':max(residual)-min(residual)})
 report[p]=phases
 rev=json.loads((folder/'revisao.json').read_text());rev['aprovado']=False;rev['passada_teste_px_por_quadro']=v
 notas=['Sola em balanço 03/07 baixada por remapeamento nearest local; pé de apoio preservado, anteriores e hashes em edicoes/pre-sola-baixa/ e edicoes/sola-baixa-adotada.json.',
        f'Chão de teste calibrado em {v} px/quadro com rastreamento visual; resíduos x em edicoes/avaliacao-apoio-24out.json.']
 for nota in notas:
  if nota not in rev['observacoes']:rev['observacoes'].append(nota)
 rev['pendencias']=[
  'O resíduo do pé de apoio contra chão móvel ainda chega a 15–18 px em alguns meios-ciclos, comparável à incerteza do rastreio; patinação não pode ser descartada.',
  'Passagens 03/07 têm sola mais baixa e pé elevado sem membro fundido na ampliação 3×; naturalidade e continuidade exigem observação temporal contínua a 100/400 ms.',
 ]
 if p=='eva':rev['pendencias'].append('Eva 02 parece variar de escala na prancha, embora largura medida da cabeça (190 px) esteja na faixa vizinha 181–192; não há base para redimensionamento uniforme.')
 (folder/'revisao.json').write_text(json.dumps(rev,ensure_ascii=False,indent=2)+'\n')
(R/'edicoes/avaliacao-apoio-24out.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({p:[x['amplitude_residuo_px'] for x in report[p]] for p in report},ensure_ascii=False))
