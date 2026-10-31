from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
p=Path(__file__).resolve().parent.parent
for nome in ('icaro','eva'):
 quadros=[];tecnica=[]
 for n in range(1,9):
  arq=p/nome/f'{n:02}.png';im=Image.open(arq).convert('RGBA');assert im.size==(384,512)
  a=im.getchannel('A');bb=im.getbbox();assert bb and bb[0]>=4 and bb[1]>=4 and bb[2]<=380 and bb[3]<=508
  tecnica.append({'quadro':n,'dimensoes':im.size,'modo':im.mode,'caixa':bb,'transparente':a.getextrema()==(0,255),'sha256':hashlib.sha256(im.tobytes()).hexdigest()});quadros.append(im)
 assert len({r['sha256'] for r in tecnica})==8
 (p/nome/'tecnica.json').write_text(json.dumps(tecnica,indent=2,ensure_ascii=False))
 for fundo,rotulo in (('#eeeeeb','claro'),('#252830','escuro')):
  folha=Image.new('RGB',(1536,1064),fundo);d=ImageDraw.Draw(folha)
  for n,im in enumerate(quadros):
   x=(n%4)*384;y=(n//4)*532;folha.paste(im,(x,y),im);d.text((x+12,y+512),str(n+1),fill='#777777')
  folha.save(p/f'{nome}-prancha-{rotulo}.png')
 imagens=[];pisos=[]
 for n,im in enumerate(quadros):
  bg=Image.new('RGBA',im.size,'#eeeeeb');bg.alpha_composite(im);imagens.append(bg.convert('RGB'))
  piso=Image.new('RGBA',im.size,'#eeeeeb');d=ImageDraw.Draw(piso)
  d.line((20,480,364,480),fill='#81919d',width=2)
  # Marcas deslocadas pelo passo projetado (~13 px/quadro) para revelar patinação.
  for k in range(-8,12):
   x=192+40*k-13*n
   if 0<=x<384:d.line((x,480,x,495),fill='#52616b',width=2)
  piso.alpha_composite(im)
  d=ImageDraw.Draw(piso);d.text((10,10),f'{nome} nordeste {n+1:02} • 13 px/q',fill='#333b47')
  pisos.append(piso.convert('RGB'))
 for frames,sufixo in ((imagens,''),(pisos,'-chao')):
  for dur,vel in ((100,'normal'),(400,'lento')):
   frames[0].save(p/f'{nome}-{vel}{sufixo}.gif',save_all=True,append_images=frames[1:],duration=dur,loop=0,disposal=2)
