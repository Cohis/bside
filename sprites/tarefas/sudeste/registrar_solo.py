"""Atualiza rastreio e revisão após correção local do chão, sem tocar PNGs."""
from pathlib import Path
import json
R=Path(__file__).resolve().parent
log=json.loads((R/'correcao-solo.json').read_text())
old={(e['personagem'],e['fase']):e['bbox_inferior_antes'] for e in log}
for person in ('icaro','eva'):
 anchor=330 if person=='icaro' else 324
 folder=R/person;tr=json.loads((folder/'rastreamento.json').read_text())
 for q in tr['quadros']:
  bottom=old.get((person,q['fase']),480)
  for side in ('esquerda','direita'):
   for name in ('quadril','joelho','tornozelo','ponta_pe'):
    pt=q['juntas'][side][name]
    if pt[1]>=anchor:
     pt[1]=anchor+round((pt[1]-anchor)*(480-anchor)/(bottom-anchor))
  q['natureza']+=' Coordenada y transferida pelo remapeamento de solo; estimativa, não landmark exato.'
 recuos=[]
 for start,side in ((0,'esquerda'),(4,'direita')):
  for a,b in zip(tr['quadros'][start:start+3],tr['quadros'][start+1:start+4]):
   p=a['juntas'][side]['ponta_pe'];q=b['juntas'][side]['ponta_pe']
   recuos.append(round(((p[0]-q[0])+.35*(p[1]-q[1]))/(.70710678*(1+.35**2)),2))
 tr['recuo_local_estimado_transicoes_apoio']=recuos
 tr['calibracao_aprovada']=False
 tr['motivo']='Solo inferior em y480, mas recuo/projeção dos pés ainda irregular; coordenadas anatômicas são estimadas.'
 (folder/'rastreamento.json').write_text(json.dumps(tr,ensure_ascii=False,indent=2)+'\n')
 rev=json.loads((folder/'revisao.json').read_text());rev['aprovado']=False
 rev['observacoes'].append('Solo normalizado em y480 por remapeamento vertical local nearest abaixo do quadril; versões anteriores e hashes em originais-pre-solo/ e correcao-solo.json.')
 rev['observacoes'].append('GIFs 100/400 ms e pranchas claras/escuras regenerados com marcas de chão móveis (24 px/fase como ensaio, sem calibração aprovada).')
 rev['pendencias']=[x for x in rev['pendencias'] if 'Chão dos quadros' not in x and 'ultrapassa chão' not in x and 'ultrapassam chão' not in x]
 if person=='icaro':
  rev['pendencias'].insert(0,'O contato inferior agora é y480, mas as fases 02→03 e 07→08 ainda mudam braços/oclusão abruptamente; recuo do apoio varia por fase.')
 else:
  rev['pendencias'].insert(0,'O contato inferior agora é y480, mas 07 mantém joelho de balanço alto e 03 aproxima-se demais de 04; recuo do apoio varia por fase.')
 rev['recuo_local_estimado_transicoes_apoio']=recuos
 (folder/'revisao.json').write_text(json.dumps(rev,ensure_ascii=False,indent=2)+'\n')
 print(person,'recuos',recuos)
