"""Ensaio de rearticulacao diagonal: coxa abaixa e se aproxima do eixo do corpo."""
from pathlib import Path
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1];C=R/'edicoes/novos-candidatos'
def interp(y,pts):
 if y<=pts[0][0]:return pts[0][1]
 for (a,u),(b,v) in zip(pts,pts[1:]):
  if y<=b:return u+(v-u)*(y-a)/(b-a)
 return 0
for p in ('icaro','eva'):
 vy=[(320,0),(382,49),(428,29),(455,8),(475,0)] if p=='icaro' else [(312,0),(375,45),(425,27),(455,7),(475,0)]
 vx=[(320,0),(350,18),(390,16),(425,9),(455,0)] if p=='icaro' else [(312,0),(348,17),(388,15),(425,8),(455,0)]
 for n in (3,7):
  src=Image.open(R/p/f'{n:02}.png').convert('RGBA');inp=src.load();out=Image.new('RGBA',src.size);pix=out.load()
  for y in range(512):
   dy=interp(y,vy);dx=interp(y,vx)
   for x in range(384):
    xw=1 if x<=145 else 0 if x>=210 else (210-x)/65
    sy=max(0,min(511,round(y-dy*xw)))
    sx=max(0,min(383,round(x-dx*xw)))
    pix[x,y]=inp[sx,sy]
  out.save(C/f'{p}-{n:02}-coxa-diagonal.png')
  sheet=Image.new('RGB',(1152,512),'#e4dfd4')
  for i,k in enumerate((n-1,n,n+1)):
   im=out if k==n else Image.open(R/p/f'{k:02}.png').convert('RGBA')
   bg=Image.new('RGB',im.size,'#e4dfd4');bg.paste(im,(0,0),im);ImageDraw.Draw(bg).line((0,480,383,480),fill='red');sheet.paste(bg,(i*384,0))
  sheet.save(C/f'{p}-{n:02}-coxa-diagonal-prancha.png')
