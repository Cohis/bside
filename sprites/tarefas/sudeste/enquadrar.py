"""Enquadramento uniforme pelo tamanho observado da cabeça; não corrige anatomia."""
from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
R=Path(__file__).parent
selecoes={'icaro':['01-t2','02','03','04','01-t1','06','07','08-t2'],'eva':['01-t3','02','03','04','01-t1','06','07-t3','08-t2']}
# Queixo e eixo central da cabeça estimados visualmente nas gerações.
queixos={'icaro':[552,696,577,589,570,603,589,552],'eva':[525,633,541,507,533,567,520,530]}
eixos={'icaro':[610,650,600,595,600,625,630,615],'eva':[615,640,625,605,620,630,590,615]}
registro=[]
for c in selecoes:
 quadros=[]; tecnica=[]
 for i,tag in enumerate(selecoes[c],1):
  p=R/'raw'/f'{c}-{tag}.png';im=Image.open(p).convert('RGBA');im.putalpha(im.getchannel('A').point(lambda v:0 if v<8 else v));box=im.getbbox()
  escala=(148 if c=='icaro' else 139)/(queixos[c][i-1]-box[1]);rec=im.crop(box);rec=rec.resize((round(rec.width*escala),round(rec.height*escala)),Image.Resampling.NEAREST)
  pos=(round(200-(eixos[c][i-1]-box[0])*escala),56+{2:4,6:4,4:-2,8:-2}.get(i,0))
  out=Image.new('RGBA',(384,512));out.paste(rec,pos);out.save(R/c/f'{i:02}.png');quadros.append(out)
  tr={'entrada':str(p.resolve()),'caixa_original':box,'escala_uniforme':escala,'interpolacao':'vizinho mais próximo','posicao':pos,'ancora':[192,480],'metodo':'tamanho da cabeça até queixo estimado visualmente; chão não forçado','queixo_raw_estimado':queixos[c][i-1],'eixo_cabeca_raw_estimado':eixos[c][i-1],'ruido_alfa_removido':'somente <8/255'}
  (R/c/f'{i:02}.transformacao.json').write_text(json.dumps(tr,indent=2,ensure_ascii=False))
  b=out.getbbox();tecnica.append({'fase':i,'bbox':b,'rgba':out.mode=='RGBA','dimensoes':out.size,'margens_ok':b[0]>3 and b[1]>3 and b[2]<381 and b[3]<509,'sha256_pixels':hashlib.sha256(out.tobytes()).hexdigest(),'pixels_transparentes':out.getchannel('A').histogram()[0]})
  registro.append({'personagem':c,'fase':i,'raw':p.name,'reclassificacao':'gerado como01 mas observado contato direito05' if i==5 else None})
 (R/c/'tecnica.json').write_text(json.dumps(tecnica,indent=2))
 for nome,cor in [('claro','#ededeb'),('escuro','#20252b')]:
  prancha=Image.new('RGB',(384*4,542*2),cor);draw=ImageDraw.Draw(prancha)
  for i,im in enumerate(quadros):
   x=(i%4)*384;y=(i//4)*542;prancha.paste(im,(x,y),im);draw.text((x+12,y+515),f'{c} / {i+1:02}',fill='#bb7333')
  prancha.save(R/f'{c}-{nome}.png')
 frames=[]
 for im in quadros:
  f=Image.new('RGB',(384,512),'#dddddd');f.paste(im,(0,0),im);frames.append(f)
 for nome,ms in [('normal',100),('lento',400)]:frames[0].save(R/f'{c}-{nome}.gif',save_all=True,append_images=frames[1:],duration=ms,loop=0)
(R/'selecionados.json').write_text(json.dumps(registro,ensure_ascii=False,indent=2))
