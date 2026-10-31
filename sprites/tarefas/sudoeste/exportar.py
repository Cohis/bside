from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
D=Path(__file__).resolve().parent
if (D/'correcoes'/'correcoes-selecionadas.json').exists():
 raise SystemExit('Há correções manuais selecionadas. Use correcoes/aplicar.py para preservar a composição e os originais.')
# Marcos manuais observados: topo do cabelo, queixo, eixo do tronco em raw.
# Escala uniforme por cabeça, jamais pelo comprimento variável da passada.
marcos={'icaro':[(157,528,550),(193,552,550),(163,534,550),(165,525,540),(169,534,550),(155,531,550),(156,532,550),(171,541,540)],'eva':[(151,543,540),(65,469,540),(147,532,550),(82,498,550),(78,490,540),(158,546,530),(157,538,540),(75,475,540)]}
versoes={'icaro':{7:'-v3'},'eva':{3:'-v2',4:'-v2',5:'-v2'}}
selecao={}; tecnica={}
for c in marcos:
 frames=[]; checks=[]; selecao[c]={}
 for n,(top,chin,axis) in enumerate(marcos[c],1):
  raw=D/'raws'/f'{c}-{n:02}{versoes[c].get(n,"")}.png';im=Image.open(raw).convert('RGBA');im.putalpha(im.getchannel('A').point(lambda a:0 if a<8 else a));box=im.getbbox();sc=(136 if c=='icaro' else 140)/(chin-top)
  if c=='eva' and n==2: sc=.335 # Limite uniforme para preservar sola inteira; proporção fica pendente.
  crop=im.crop(box);crop=crop.resize((round(crop.width*sc),round(crop.height*sc)),Image.Resampling.NEAREST)
  bob={2:4,6:4,4:-2,8:-2}.get(n,0)
  pos=(round(192-(axis-box[0])*sc),round(56+bob+(box[1]-top)*sc))
  out=Image.new('RGBA',(384,512));out.paste(crop,pos);p=D/c/f'{n:02}.png';out.save(p)
  trans={'entrada':str(raw),'caixa_original':box,'escala_uniforme':sc,'interpolacao':'vizinho mais próximo','posicao':pos,'eixo_original':axis,'ancora':[192,480],'metodo':'topo e queixo manuais, escala da cabeça; eixo pelo tronco; bob de recepção +4 e avanço -2; NÃO alinhamento pela sola','marcos_cabeca_raw':[top,chin],'incerteza_marcos_raw_px':5}
  p.with_suffix('.transformacao.json').write_text(json.dumps(trans,ensure_ascii=False,indent=2));selecao[c][str(n)]=str(raw)
  bbox=out.getbbox();checks.append({'fase':n,'tamanho':out.size,'modo':out.mode,'bbox':bbox,'margens_ok':bbox[0]>=4 and bbox[1]>=4 and bbox[2]<=380 and bbox[3]<=508,'transparencia':out.getchannel('A').getextrema()==(0,255),'hash_pixels':hashlib.sha256(out.tobytes()).hexdigest()});frames.append(out)
 for bg,label in [('#f5f3ef','claro'),('#242735','escuro')]:
  sheet=Image.new('RGB',(1536,1064),bg);draw=ImageDraw.Draw(sheet)
  for i,im in enumerate(frames):
   xy=(i%4*384,i//4*532+20);sheet.paste(im,xy,im);draw.text((xy[0]+8,xy[1]-16),f'{c} {i+1:02}',fill='#888888')
  sheet.save(D/f'{c}-prancha-{label}.png')
 rgb=[]
 for im in frames:
  a=Image.new('RGB',im.size,'#e7e8eb');a.paste(im,(0,0),im);rgb.append(a)
 for ms in [100,400]:rgb[0].save(D/f'{c}-loop-{ms}ms.gif',save_all=True,append_images=rgb[1:],duration=ms,loop=0)
 tecnica[c]={'quadros':checks,'duplicatas':len(set(x['hash_pixels'] for x in checks))!=8}
(D/'selecionados.json').write_text(json.dumps(selecao,indent=2));(D/'tecnica.json').write_text(json.dumps(tecnica,indent=2))
print(json.dumps(tecnica,indent=2))
