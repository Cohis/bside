"""Candidatos de recuo de apoio por remapeamento horizontal local nearest."""
from pathlib import Path
from PIL import Image,ImageDraw
R=Path(__file__).resolve().parents[1];C=R/'edicoes/novos-candidatos'
plans={'icaro':{2:13,3:10,6:16,7:18},'eva':{2:5,3:12}}
for p,frames in plans.items():
 for n,final_dx in frames.items():
  src=Image.open(R/p/f'{n:02}.png').convert('RGBA');inp=src.load();out=Image.new('RGBA',src.size);pix=out.load()
  hip=317 if p=='icaro' else 305
  for y in range(512):
   dy=max(0,min(1,(y-hip)/(460-hip)));shift=round(final_dx*dy)
   for x in range(384):
    if y>=455:w=1
    elif x<=155:w=0
    elif x>=205:w=1
    else:w=(x-155)/50
    sx=x-round(shift*w)
    pix[x,y]=inp[sx,y] if 0<=sx<384 else (0,0,0,0)
  out.save(C/f'{p}-{n:02}-apoio-h.png')
 for n in frames:
  nums=[n-1,n,n+1]
  sheet=Image.new('RGB',(384*3,512),'#e4dfd4')
  for i,k in enumerate(nums):
   path=C/f'{p}-{k:02}-apoio-h.png' if k in frames else R/p/f'{k:02}.png'
   im=Image.open(path).convert('RGBA');bg=Image.new('RGB',im.size,'#e4dfd4');bg.paste(im,(0,0),im);ImageDraw.Draw(bg).line((0,480,383,480),fill='red');sheet.paste(bg,(384*i,0))
  sheet.save(C/f'{p}-{n:02}-apoio-h-prancha.png')
