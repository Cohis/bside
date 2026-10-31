"""Ensaios: baixar apenas a sola de balanço de 03/07 para passo menos alto."""
from pathlib import Path
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1];C=R/'edicoes/novos-candidatos'
def valor(y,pts):
 if y<=pts[0][0]:return pts[0][1]
 for (a,u),(b,v) in zip(pts,pts[1:]):
  if y<=b:return u+(v-u)*(y-a)/(b-a)
 return pts[-1][1]
for p in ('icaro','eva'):
 pts=[(325,0),(365,4),(425,15),(450,11),(470,0),(512,0)] if p=='icaro' else [(315,0),(358,3),(420,11),(447,8),(468,0),(512,0)]
 for n in (3,7):
  src=Image.open(R/p/f'{n:02}.png').convert('RGBA');inp=src.load();out=Image.new('RGBA',src.size);pix=out.load()
  for y in range(512):
   dy=valor(y,pts)
   for x in range(384):
    w=1 if x<=150 else 0 if x>=205 else (205-x)/55
    sy=max(0,min(511,round(y-dy*w)))
    pix[x,y]=inp[x,sy]
  out.save(C/f'{p}-{n:02}-sola-baixa.png')
  sheet=Image.new('RGB',(1152,512),'#e4dfd4')
  for i,k in enumerate((n-1,n,n+1)):
   path=C/f'{p}-{k:02}-sola-baixa.png' if k==n else R/p/f'{k:02}.png'
   im=Image.open(path).convert('RGBA');bg=Image.new('RGB',im.size,'#e4dfd4');bg.paste(im,(0,0),im);ImageDraw.Draw(bg).line((0,480,383,480),fill='red');sheet.paste(bg,(384*i,0))
  sheet.save(C/f'{p}-{n:02}-sola-baixa-prancha.png')
