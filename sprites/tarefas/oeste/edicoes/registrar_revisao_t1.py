"""Atualiza rastreamento aproximado e pendências após a comparação visual t1."""
from pathlib import Path
import json
R=Path(__file__).resolve().parents[1]
points={
 'icaro':{
   3:{'quadril':[190,309],'esquerda':[[212,399],[205,452],[167,474]],'direita':[[151,359],[159,414],[132,432]]},
   7:{'quadril':[190,314],'esquerda':[[152,360],[165,415],[138,438]],'direita':[[213,402],[195,452],[159,474]]}},
 'eva':{
   3:{'quadril':[190,282],'esquerda':[[212,391],[203,450],[166,474]],'direita':[[156,352],[158,409],[143,439]]},
   7:{'quadril':[190,303],'esquerda':[[148,359],[159,413],[137,439]],'direita':[[214,397],[206,452],[173,475]]}}
}
for person in points:
 folder=R/person
 tracking=json.loads((folder/'rastreamento.json').read_text())
 for n,vals in points[person].items():
  q=next(x for x in tracking['quadros'] if x['quadro']==n)
  q['quadril_estimado']=vals['quadril']
  for side in ('esquerda','direita'):
   q[side]=dict(zip(('joelho_estimado_oculto','tornozelo_estimado','ponta_pe_observada_aproximada'),vals[side]))
  q['incerteza_px']={'quadril':12,'joelhos':20,'tornozelos':12,'pontas':10}
 tracking['metodo']+=' Pontos 03/07 atualizados por inspeção das variantes t1 na prancha; margens de erro explícitas.'
 tracking['passada_teste_px_por_quadro']=40
 tracking['formula']='40 px/quadro é velocidade visual aproximada de teste; pontos medidos por inspeção, sem certificação de patinação.'
 tracking['advertencia']='Pontos estimados. Passagem 03/07 separa visualmente os pés, mas joelho elevado e velocidade do apoio ainda exigem revisão temporal e de anatomia.'
 (folder/'rastreamento.json').write_text(json.dumps(tracking,ensure_ascii=False,indent=2)+'\n')
 rev=json.loads((folder/'revisao.json').read_text());rev['aprovado']=False
 rev['observacoes']=[
  'Oito PNGs RGBA 384×512, transparência real, sem cortes ou duplicatas exatas.',
  'Base, identidade, proporção e paleta preservadas dos próprios raws; correções de contato registradas.',
  'Passagens 03/07 substituídas pelas variantes t1 próprias, sem compor pernas ou criar novos pixels; versões anteriores e hashes preservados em edicoes/passagens-t1-adotadas.json.',
  'Prancha e GIFs 100/400 ms regenerados com chão marcado a 40 px/quadro. Os pés em balanço ficam visivelmente elevados.',
 ]
 if person=='eva':rev['observacoes'].append('Em 02/06, pé de apoio recebeu remapeamento localizado +20 px; originais preservados em edicoes/pre-apoiar-eva/.')
 rev['pendencias']=[
  '03/07 apresentam elevação de joelho acentuada em relação às outras fases; conferir leitura de caminhada e comprimentos no loop temporal.',
  'O pé de apoio ainda não recua uniformemente contra as marcas do chão em todas as fases; possível patinação, especialmente nas transições 04→05 e 08→01.',
 ]
 if person=='eva':rev['pendencias'].append('A cabeça e o tronco do quadro 02 parecem maiores que nos vizinhos; identidade e escala exigem revisão.')
 rev['passada_teste_px_por_quadro']=40
 (folder/'revisao.json').write_text(json.dumps(rev,ensure_ascii=False,indent=2)+'\n')
