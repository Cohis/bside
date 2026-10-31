"""Candidatos de correção do contato com o solo, sem alterar tronco/cabeça."""
from pathlib import Path
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parent;C=R/'candidatos-solo';C.mkdir(exist_ok=True)
for p in ('icaro','eva'):
 anchor=330 if p=='icaro' else 324
 sheet=Image.new('RGB',(1536,1024),'#ededeb')
 for n in range(1,9):
  src=Image.open(R/p/f'{n:02}.png').convert('RGBA');bottom=src.getbbox()[3]
  out=Image.new('RGBA',(384,512))
  for y in range(512):
   sy=y if y<anchor else min(511,anchor+round((y-anchor)*(bottom-anchor)/(480-anchor)))
   out.paste(src.crop((0,sy,384,sy+1)),(0,y))
  out.save(C/f'{p}-{n:02}-solo.png')
  bg=Image.new('RGB',src.size,'#ededeb');bg.paste(out,(0,0),out);ImageDraw.Draw(bg).line((0,480,383,480),fill='#30a7ab')
  sheet.paste(bg,(((n-1)%4)*384,((n-1)//4)*512))
 sheet.save(C/f'{p}-prancha-solo.png')
