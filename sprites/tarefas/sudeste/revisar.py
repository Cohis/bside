from pathlib import Path
import json,math
R=Path(__file__).parent
# Coordenadas estimadas visualmente nas células, não landmarks automáticos.
# Cada lado contém quadril, joelho, tornozelo, ponta do pé.
medidas={
'icaro':[
[[204,311],[231,383],[244,443],[269,455],[180,311],[149,365],[115,416],[144,434]],
[[204,301],[229,350],[223,417],[253,433],[179,300],[145,362],[96,408],[125,429]],
[[204,313],[185,390],[158,454],[187,471],[180,313],[210,373],[208,432],[228,448]],
[[204,313],[167,387],[117,438],[140,456],[180,313],[214,380],[249,426],[272,436]],
[[204,311],[161,381],[114,426],[144,443],[180,312],[208,384],[235,453],[265,469]],
[[204,308],[154,379],[106,435],[132,456],[180,309],[207,378],[212,451],[240,469]],
[[204,311],[217,371],[218,401],[231,419],[180,312],[177,389],[169,451],[191,470]],
[[204,311],[235,371],[264,415],[286,430],[180,313],[144,388],[116,437],[137,454]]],
'eva':[
[[204,306],[231,382],[245,457],[275,476],[178,307],[146,376],[107,430],[132,449]],
[[204,309],[232,371],[221,445],[258,463],[178,309],[157,374],[119,432],[146,456]],
[[204,303],[164,375],[147,432],[173,451],[178,304],[209,372],[217,425],[244,442]],
[[204,303],[156,383],[107,458],[133,480],[178,304],[216,380],[255,455],[282,468]],
[[204,303],[154,382],[112,432],[143,448],[178,304],[209,378],[229,452],[260,466]],
[[204,306],[159,386],[109,447],[137,466],[178,307],[201,388],[210,460],[241,477]],
[[204,305],[241,358],[222,404],[239,426],[178,306],[167,388],[167,470],[197,489]],
[[204,303],[235,375],[258,425],[286,442],[178,305],[146,387],[113,449],[141,466]]]
}
for c,frames in medidas.items():
 qs=[]
 for n,pts in enumerate(frames,1):
  juntas={}
  for j,lado in enumerate(['esquerda','direita']):
   juntas[lado]=dict(zip(['quadril','joelho','tornozelo','ponta_pe'],pts[j*4:j*4+4]));juntas[lado]['contato_chao']=(lado==('esquerda' if n<5 else 'direita')) or n in [1,5]
  qs.append({'fase':n,'juntas':juntas,'natureza':'estimativa visual; quadril/joelho oclusos pela roupa; erro ~5-10px, ponta ~3px'})
 recuos=[]
 for ini,lado in [(0,'esquerda'),(4,'direita')]:
  for a,b in zip(qs[ini:ini+3],qs[ini+1:ini+4]):
   p=a['juntas'][lado]['ponta_pe'];q=b['juntas'][lado]['ponta_pe'];recuos.append(round(((p[0]-q[0])+.35*(p[1]-q[1]))/(.70710678*(1+.35**2)),2))
 (R/c/'rastreamento.json').write_text(json.dumps({'metodo':'estimativa visual nas células, não medição anatômica exata','quadros':qs,'recuo_local_estimado_transicoes_apoio':recuos,'calibracao_aprovada':False,'motivo':'Recuo e projeção irregulares; uma velocidade constante não elimina patinação.'},ensure_ascii=False,indent=2))
 pend=['Recuo do apoio irregular em x/y; calibração de deslocamento ainda não aprovada.','Variação de proporção torso/pernas entre fases, preservada no enquadramento pela cabeça e não escondida com deformação.','Reprodução temporal contínua e chão marcado ainda pendentes; GIFs preparados não equivalem a aprovação.']
 if c=='icaro':pend+=['02: compressão do corpo e inversão prematura dos braços em relação01.','07: pé em balanço permanece atrás; passagem incompleta.','08: braço distante oculto exige conferência de oclusão na transição08→01.']
 else:pend+=['03: pé elevado muito adiante, aproxima-se da fase avanço; precisa ajustar passagem.','07: perna correta após terceira tentativa, mas joelho/elevação excessivos em relação03.','02: braço próximo perde avanço cedo em relação01.']
 rev={'aprovado':False,'quadros_revisados':list(range(1,9)),'transicoes_revisadas':['04→05','08→01'],'observacoes':['16 células exportadas por escala uniforme NEAREST e translação; nenhuma deformação ou espelhamento.','Contato direito05 reclassificado da primeira tentativa de01; mapeamento registrado em selecionados.json.','Eva01 corrigida sem pulseira; Ícaro pulseira esquerda nas vistas visíveis.','Pranchas claras e escuras e GIFs100/400ms disponíveis.','Inspeção estática de04→05 e08→01 revela variação de torso/projeção; não aprovada.'],'pendencias':pend,'passada_teste_px_por_quadro':None,'recuo_local_estimado_transicoes_apoio':recuos}
 (R/c/'revisao.json').write_text(json.dumps(rev,ensure_ascii=False,indent=2))
print('Revisões gravadas sem aprovação visual.')
