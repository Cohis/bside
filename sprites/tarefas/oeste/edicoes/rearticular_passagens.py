"""Candidatos de joelho baixo para a perna inteira em balanço, quadros 03/07."""
from pathlib import Path
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1];C=R/'edicoes/novos-candidatos'
def displace(y,points):
 if y<=points[0][0]:return points[0][1]
 for (a,u),(b,v) in zip(points,points[1:]):
  if y<=b:return u+(v-u)*(y-a)/(b-a)
 return 0
for p in ('icaro','eva'):
 # A alteração vai de 0 no quadril a cerca de 30 px no joelho e volta a 0 na sola.
 pts=[(322,0),(380,30),(425,16),(460,0),(512,0)] if p=='icaro' else [(312,0),(372,27),(420,14),(461,0),(512,0)]
 for n in (3,7):
  src=Image.open(R/p/f'{n:02}.png').convert('RGBA');inp=src.load();out=Image.new('RGBA',src.size);pix=out.load()
  for y in range(512):
   dy=displace(y,pts)
   for x in range(384):
    xw=1 if x<=150 else 0 if x>=205 else (205-x)/55
    sy=max(0,min(511,round(y-dy*xw)))
    pix[x,y]=inp[x,sy]
  out.save(C/f'{p}-{n:02}-rearticulado.png')
  sheet=Image.new('RGB',(1152,512),'#e4dfd4')
  for i,k in enumerate((n-1,n,n+1)):
   path=C/f'{p}-{k:02}-rearticulado.png' if k==n else R/p/f'{k:02}.png'
   im=Image.open(path).convert('RGBA');bg=Image.new('RGB',im.size,'#e4dfd4');bg.paste(im,(0,0),im);ImageDraw.Draw(bg).line((0,480,383,480),fill='red');sheet.paste(bg,(i*384,0))
  sheet.save(C/f'{p}-{n:02}-rearticulado-prancha.png')
