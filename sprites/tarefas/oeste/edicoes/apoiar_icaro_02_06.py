"""Candidatos de recuo de Ícaro 02/06 com a perna de apoio isolada."""
from pathlib import Path
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1];C=R/'edicoes/novos-candidatos'
plans={2:{'dx':13,'poly':[(157,314),(219,314),(210,365),(204,421),(210,480),(70,480),(81,420),(119,362)]},
       6:{'dx':16,'poly':[(154,318),(217,318),(206,365),(202,421),(209,480),(68,480),(76,420),(112,365)]}}
for n,plan in plans.items():
 src=Image.open(R/'icaro'/f'{n:02}.png').convert('RGBA');mask=Image.new('L',src.size);ImageDraw.Draw(mask).polygon(plan['poly'],fill=255)
 inp=src.load();m=mask.load();out=src.copy();pix=out.load();lifted=[]
 for y in range(512):
  dx=round(plan['dx']*max(0,min(1,(y-314)/(465-314))))
  for x in range(384):
   if m[x,y] and inp[x,y][3]:lifted.append((x+dx,y,inp[x,y]));pix[x,y]=(0,0,0,0)
 for x,y,pixel in lifted:
  if 0<=x<384:pix[x,y]=pixel
 out.save(C/f'icaro-{n:02}-apoio-poligono.png')
 sheet=Image.new('RGB',(1152,512),'#e4dfd4')
 for i,k in enumerate((n-1,n,n+1)):
  path=C/f'icaro-{k:02}-apoio-poligono.png' if k==n else R/'icaro'/f'{k:02}.png'
  im=Image.open(path).convert('RGBA');bg=Image.new('RGB',im.size,'#e4dfd4');bg.paste(im,(0,0),im);ImageDraw.Draw(bg).line((0,480,383,480),fill='red');sheet.paste(bg,(384*i,0))
 sheet.save(C/f'icaro-{n:02}-apoio-poligono-prancha.png')
