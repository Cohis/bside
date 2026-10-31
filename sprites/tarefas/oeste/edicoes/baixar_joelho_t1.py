"""Ensaios de remapeamento local, sem interpolação, para reduzir joelho alto t1."""
from pathlib import Path
from PIL import Image, ImageDraw
R=Path(__file__).resolve().parents[1]
C=Path(__file__).resolve().parent/'novos-candidatos'

def lerp(points,y):
    if y<=points[0][0]:return points[0][1]
    for (a,u),(b,v) in zip(points,points[1:]):
        if y<=b:return u+(v-u)*(y-a)/(b-a)
    return points[-1][1]

for person in ('icaro','eva'):
 for n in (3,7):
  src=Image.open(R/person/f'{n:02}.png').convert('RGBA')
  out=Image.new('RGBA',src.size)
  inp=src.load();pix=out.load()
  # Máximo 22 px no joelho e 8 no calçado em balanço. Zero no quadril e no solo.
  ypoints=([(310,0),(365,22),(430,9),(460,0),(512,0)] if person=='icaro'
           else [(297,0),(358,20),(425,8),(455,0),(512,0)])
  for y in range(512):
   base=lerp(ypoints,y)
   for x in range(384):
    # Sem deslocamento na perna de apoio, à direita da tela.
    xweight=1 if x<=155 else 0 if x>=204 else (204-x)/49
    sy=min(511,max(0,round(y-base*xweight)))
    pix[x,y]=inp[x,sy]
  out.save(C/f'{person}-{n:02}-joelho-baixo.png')
 # Prancha de vizinhanças
 for middle in (3,7):
  nums=(2,3,4) if middle==3 else (6,7,8)
  sheet=Image.new('RGB',(1152,512),'#e4dfd4')
  for i,k in enumerate(nums):
   path=C/f'{person}-{k:02}-joelho-baixo.png' if k==middle else R/person/f'{k:02}.png'
   im=Image.open(path).convert('RGBA');bg=Image.new('RGB',im.size,'#e4dfd4');bg.paste(im,(0,0),im)
   ImageDraw.Draw(bg).line((0,480,383,480),fill='red')
   sheet.paste(bg,(384*i,0))
  sheet.save(C/f'{person}-{middle:02}-joelho-baixo-prancha.png')
