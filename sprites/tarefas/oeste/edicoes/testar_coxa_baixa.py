"""Ensaio mais forte de abaixar coxa/joelho, sem alterar PNGs de produção."""
from pathlib import Path
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1];C=R/'edicoes/novos-candidatos'
def disp(y,points):
 if y<=points[0][0]:return points[0][1]
 for (ya,a),(yb,b) in zip(points,points[1:]):
  if y<=yb:return a+(b-a)*(y-ya)/(yb-ya)
 return 0
for p in ('icaro','eva'):
 pts=[(320,0),(382,49),(428,29),(455,8),(475,0),(512,0)] if p=='icaro' else [(312,0),(375,45),(425,27),(455,7),(475,0),(512,0)]
 for n in (3,7):
  src=Image.open(R/p/f'{n:02}.png').convert('RGBA');inp=src.load();out=Image.new('RGBA',src.size);pix=out.load()
  for y in range(512):
   dy=disp(y,pts)
   for x in range(384):
    xw=1 if x<=145 else 0 if x>=205 else (205-x)/60
    sy=max(0,min(511,round(y-dy*xw)))
    pix[x,y]=inp[x,sy]
  out.save(C/f'{p}-{n:02}-coxa-baixa.png')
  sheet=Image.new('RGB',(1152,512),'#e4dfd4')
  for i,k in enumerate((n-1,n,n+1)):
   im=out if k==n else Image.open(R/p/f'{k:02}.png').convert('RGBA')
   bg=Image.new('RGB',im.size,'#e4dfd4');bg.paste(im,(0,0),im);ImageDraw.Draw(bg).line((0,480,383,480),fill='red');sheet.paste(bg,(i*384,0))
  sheet.save(C/f'{p}-{n:02}-coxa-baixa-prancha.png')
