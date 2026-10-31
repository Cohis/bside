"""Enquadramento técnico dos sprites; não deforma nem redesenha membros."""
import subprocess,json,hashlib
from pathlib import Path
from PIL import Image,ImageDraw
r=Path(__file__).resolve().parent
raiz=r.parents[2]
# Eixos do tronco identificados visualmente nos raws (não o centro entre pés).
eixos={'icaro':[550,565,558,568,555,566,560,558],'eva':[560,560,574,581,583,584,565,550]}
# Altura total mantém a pequena oscilação de quadril da caminhada.
alturas=[424,420,426,428,424,420,426,428]
for person in ('icaro','eva'):
 quadros=[];checks=[]
 for i in range(1,9):
  raw=r/f'raws/{person}-{i:02}.png';out=r/f'{person}/{i:02}.png'
  subprocess.run(['python',str(raiz/'sprites/scripts/normalizar.py'),str(raw),str(out),'--altura',str(alturas[i-1]),'--eixo',str(eixos[person][i-1])],check=True)
  im=Image.open(out).convert('RGBA');a=im.getchannel('A');box=a.getbbox()
  checks.append({'fase':i,'dimensoes':list(im.size),'modo':im.mode,'caixa':box,'alfa':a.getextrema(),'sha256':hashlib.sha256(im.tobytes()).hexdigest()})
  quadros.append(im)
 for color,name in [((244,244,239),'claro'),((35,38,45),'escuro')]:
  sheet=Image.new('RGB',(384*4,540*2),color);d=ImageDraw.Draw(sheet)
  for i,im in enumerate(quadros):
   x=(i%4)*384;y=(i//4)*540
   sheet.paste(im,(x,y+24),im);d.text((x+10,y+5),f'{person} {i+1:02}',fill=(140,140,140))
  sheet.save(r/f'{person}-inspecao-{name}.png')
 frames=[]
 for im in quadros:
  bg=Image.new('RGB',(384,512),(225,225,225));bg.paste(im,(0,0),im);frames.append(bg)
 frames[0].save(r/f'{person}-loop.gif',save_all=True,append_images=frames[1:],duration=100,loop=0)
 frames[0].save(r/f'{person}-lento.gif',save_all=True,append_images=frames[1:],duration=400,loop=0)
 (r/person/'tecnica.json').write_text(json.dumps({'quadros':checks,'duplicatas':len({q['sha256'] for q in checks})!=8,'criterio_enquadramento':'Eixo do tronco manual; escala uniforme por altura de fase, vizinho mais próximo, alfa menor que8 removido. Sem deformar partes.'},ensure_ascii=False,indent=2))
