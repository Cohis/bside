from pathlib import Path
from PIL import Image,ImageDraw
p=Path(__file__).parent.parent
fonte=Image.open(p/'eva/07.png').convert('RGBA')
mask=Image.new('L',fonte.size,0);m=ImageDraw.Draw(mask)
m.polygon([(217,193),(237,188),(246,207),(250,235),(261,273),(263,302),(262,326),(247,337),(223,329),(215,298),(220,267),(214,234)],fill=255)
braco=Image.new('RGBA',fonte.size);braco.paste(fonte,(0,0),Image.composite(fonte.getchannel('A'),Image.new('L',fonte.size),mask))
for n,ang in [(4,0),(5,-7),(6,3)]:
 o=Image.open(p/'eva'/f'{n:02}.png').convert('RGBA');s=o.copy()
 for y in range(203,320):
  lim=221 if y<235 else 220 if y<260 else 220 if y<285 else 223
  for x in range(lim,277):
   r,g,b,a=o.getpixel((x,y))
   # Apaga a manga original e sua mão. Pixels de calça não são tocados.
   roupa=r>125 and g>125 and b>125
   pele=r>115 and r>g*1.08 and g>b*1.08
   borda=a>0 and max(r,g,b)<75 and x>=242
   if a and (roupa or pele or borda):s.putpixel((x,y),(0,0,0,0))
 novo=braco.rotate(ang,resample=Image.Resampling.NEAREST,center=(222,190))
 s.alpha_composite(novo)
 out=Path(__file__).parent/f'eva-{n:02}-braco-ensaio.png';s.save(out)
 bg=Image.new('RGBA',s.size,'#eee');bg.alpha_composite(s);bg.convert('RGB').save(out.with_name(out.stem+'-fundo.png'))
