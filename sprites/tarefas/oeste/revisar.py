from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
R=Path(__file__).parent
# Estimativas visuais sobre células exportadas; joelhos ocultos por tecido.
pts={
'icaro':[( (186,311),(147,393),(143,446),(91,470),(238,395),(278,433),(249,469)),((191,315),(164,395),(161,460),(121,487),(244,397),(287,438),(265,465)),((190,309),(203,402),(211,462),(182,484),(161,394),(159,437),(119,460)),((190,301),(221,382),(251,430),(222,454),(159,378),(139,420),(91,433)),((191,309),(224,393),(267,438),(235,465),(154,390),(145,445),(91,464)),((191,312),(243,399),(288,441),(259,471),(160,393),(163,453),(118,472)),((190,314),(160,405),(163,448),(119,464),(218,409),(224,472),(193,483)),((192,310),(157,389),(145,431),(95,454),(229,392),(252,437),(220,458))],
'eva':[((190,281),(169,371),(145,433),(106,457),(240,380),(257,428),(236,448)),((190,301),(154,386),(164,460),(119,489),(252,398),(290,444),(274,470)),((190,282),(191,383),(194,441),(157,467),(237,394),(265,421),(245,446)),((190,281),(244,375),(256,431),(222,458),(159,367),(140,423),(97,440)),((190,276),(242,374),(261,428),(239,456),(155,374),(145,431),(100,453)),((191,300),(244,395),(274,443),(257,469),(156,394),(160,467),(112,489)),((190,277),(155,371),(143,422),(108,443),(225,386),(228,457),(192,481)),((190,278),(159,372),(142,423),(96,443),(229,383),(249,432),(219,458))]}
for c in pts:
 checks=[]; hashes=[]; frames=[]; rast=[]
 for n,v in enumerate(pts[c],1):
  p=R/c/f'{n:02}.png';im=Image.open(p);bb=im.getbbox();a=im.getchannel('A');h=hashlib.sha256(im.tobytes()).hexdigest();hashes.append(h)
  checks.append({'quadro':n,'dimensoes':list(im.size),'modo':im.mode,'bbox':bb,'alfa_extremos':a.getextrema(),'margem_minima':min(bb[0],bb[1],384-bb[2],512-bb[3]),'sha256_pixels':h})
  q,je,te,pe,jd,td,pd=v
  rast.append({'quadro':n,'quadril_estimado':q,'esquerda':{'joelho_estimado_oculto':je,'tornozelo_estimado':te,'ponta_pe_observada_aproximada':pe},'direita':{'joelho_estimado_oculto':jd,'tornozelo_estimado':td,'ponta_pe_observada_aproximada':pd},'incerteza_px':{'quadril':10,'joelhos':18,'tornozelos':8,'pontas':6}})
  bg=Image.new('RGB',im.size,'#ddd7ca'); bg.paste(im,(0,0),im);frames.append(bg)
 frames[0].save(R/c/'revisao-loop.gif',save_all=True,append_images=frames[1:],duration=100,loop=0)
 frames[0].save(R/c/'revisao-lenta.gif',save_all=True,append_images=frames[1:],duration=350,loop=0)
 recuo=(pts[c][2][2][0]-pts[c][0][2][0])/2
 info={'metodo':'Estimativas manuais sobre as células finais. Joelhos inferidos sob calça larga; não são medição anatômica precisa.','quadros':rast,'passada_teste_px_por_quadro':round(recuo,1),'formula':'(tornozelo esquerdo x03 - x01)/2','advertencia':'Estimativa de teste parcial. Recuo não é uniforme; não implica ausência de patinação.'}
 (R/c/'rastreamento.json').write_text(json.dumps(info,ensure_ascii=False,indent=2))
 (R/c/'validacao-tecnica.json').write_text(json.dumps({'quadros':checks,'duplicados_exatos':len(set(hashes))!=8},ensure_ascii=False,indent=2))
 pend=['Altura dos contatos de solo varia entre fases após alinhamento pela cabeça/torso; proporção das pernas e ritmo precisam de correção artística.','Recuo do apoio irregular; velocidade única não elimina patinação.','Loops GIF normal/lento exportados; inspeção temporal contínua ainda não realizada. Revisão estática de oito fases e junções realizada.']
 if c=='eva':pend+=['03: pé em balanço ainda atrás do quadril após três tentativas, parece saída do apoio.','07: pé elevado mais adiantado que uma passagem; três tentativas registradas.','04/06: perna/bolso corrigidos mas braço próximo ainda recua, comprometendo contrabalanço.']
 else:pend+=['03/07: elevação corrigida na segunda tentativa, mas tornozelo elevado ainda adiantado e joelho pouco legível sob calça.']
 rev={'aprovado':False,'observacoes':['8 PNGs RGBA384x512 completos, transparência real, sem duplicados exatos, sem cortes.','Câmera oeste e identidade preservadas. Ícaro mantém pulseira no braço esquerdo próximo.','Escala uniforme0.35 e alinhamento estimado por torso/cabeça; nenhum membro deformado, nenhum espelhamento.','04→05 e08→01: mudança de pé/altura de solo ainda salta.'],'quadros_revisados':list(range(1,9)),'transicoes_revisadas':['04→05','08→01'],'pendencias':pend,'passada_teste_px_por_quadro':round(recuo,1)}
 (R/c/'revisao.json').write_text(json.dumps(rev,ensure_ascii=False,indent=2))
print('16 células; pranchas, loops, rastreamentos e revisões gravados.')
