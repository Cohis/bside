"""Ensaios de recuo do apoio 02, preservando quadro original e estética."""
from pathlib import Path
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parent;C=R/'candidatos-apoio';C.mkdir(exist_ok=True)
plans={
 'icaro':{'poly':[(180,330),(251,330),(313,482),(199,482),(192,430),(183,365)],'dx':-23},
 'eva':{'poly':[(170,324),(250,324),(288,482),(168,482),(173,430),(174,365)],'dx':-24}}
for p,plan in plans.items():
 src=Image.open(R/p/'02.png').convert('RGBA');mask=Image.new('L',src.size);ImageDraw.Draw(mask).polygon(plan['poly'],fill=255)
 inp=src.load();m=mask.load();out=src.copy();pix=out.load();moved=[]
 for y in range(512):
  dx=round(plan['dx']*max(0,min(1,(y-330)/(465-330))))
  for x in range(384):
   if m[x,y] and inp[x,y][3]:moved.append((x+dx,y,inp[x,y]));pix[x,y]=(0,0,0,0)
 for x,y,pixel in moved:
  if 0<=x<384:pix[x,y]=pixel
 out.save(C/f'{p}-02-apoio.png')
 sheet=Image.new('RGB',(1152,512),'#ededeb')
 for i,n in enumerate((1,2,3)):
  path=C/f'{p}-02-apoio.png' if n==2 else R/p/f'{n:02}.png'
  im=Image.open(path).convert('RGBA');bg=Image.new('RGB',im.size,'#ededeb');bg.paste(im,(0,0),im);ImageDraw.Draw(bg).line((0,480,383,480),fill='teal');sheet.paste(bg,(384*i,0))
 sheet.save(C/f'{p}-010203-apoio.png')
