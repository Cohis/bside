"""Ensaio nearest para reduzir elevação do joelho esquerdo de Eva 07."""
from pathlib import Path
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parent;C=R/'candidatos-apoio';C.mkdir(exist_ok=True)
src=Image.open(R/'eva'/'07.png').convert('RGBA');inp=src.load();out=Image.new('RGBA',src.size);pix=out.load()
def desloc(y):
 pts=[(320,0),(365,18),(425,8),(456,0),(512,0)]
 if y<320:return 0
 for (a,u),(b,v) in zip(pts,pts[1:]):
  if y<=b:return u+(v-u)*(y-a)/(b-a)
 return 0
for y in range(512):
 base=desloc(y)
 for x in range(384):
  w=0 if x<=170 else 1 if x>=221 else (x-170)/51
  sy=max(0,min(511,round(y-base*w)))
  pix[x,y]=inp[x,sy]
out.save(C/'eva-07-joelho-baixo.png')
sheet=Image.new('RGB',(1152,512),'#ededeb')
for i,n in enumerate((6,7,8)):
 path=C/'eva-07-joelho-baixo.png' if n==7 else R/'eva'/f'{n:02}.png'
 im=Image.open(path).convert('RGBA');bg=Image.new('RGB',im.size,'#ededeb');bg.paste(im,(0,0),im);ImageDraw.Draw(bg).line((0,480,383,480),fill='teal');sheet.paste(bg,(384*i,0))
sheet.save(C/'eva-060708-joelho-baixo.png')
