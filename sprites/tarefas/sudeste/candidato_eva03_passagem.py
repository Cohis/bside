"""Ensaio localizado para recuar pé direito em balanço de Eva 03."""
from pathlib import Path
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parent;C=R/'candidatos-apoio'
src=Image.open(R/'eva/03.png').convert('RGBA')
mask=Image.new('L',src.size)
ImageDraw.Draw(mask).polygon([(189,315),(250,315),(321,482),(208,482),(210,430),(195,370)],fill=255)
inp=src.load();m=mask.load();out=src.copy();pix=out.load();moved=[]
for y in range(512):
 dx=round(-28*max(0,min(1,(y-320)/(455-320))))
 for x in range(384):
  if m[x,y] and inp[x,y][3]:moved.append((x+dx,y,inp[x,y]));pix[x,y]=(0,0,0,0)
for x,y,pixel in moved:
 if 0<=x<384:pix[x,y]=pixel
out.save(C/'eva-03-passagem-curta.png')
sheet=Image.new('RGB',(1152,512),'#ededeb')
for i,n in enumerate((2,3,4)):
 path=C/'eva-03-passagem-curta.png' if n==3 else R/'eva'/f'{n:02}.png'
 im=Image.open(path).convert('RGBA');bg=Image.new('RGB',im.size,'#ededeb');bg.paste(im,(0,0),im);ImageDraw.Draw(bg).line((0,480,383,480),fill='teal');sheet.paste(bg,(i*384,0))
sheet.save(C/'eva-020304-passagem-curta.png')
