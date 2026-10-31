from pathlib import Path
from PIL import Image
p=Path(__file__).parent.parent
ref=Image.open(p/'icaro/07.png').convert('RGBA')
for n in (1,8):
 original=Image.open(p/'icaro'/f'{n:02}.png').convert('RGBA');out=original.copy()
 for y in range(304,500):
  for x in range(90,310):out.putpixel((x,y),(0,0,0,0))
 for y in range(300,488):
  for x in range(90,310):
   c=ref.getpixel((x,y))
   if c[3]<8:continue
   # Apenas região abaixo da cintura; mão doadora rejeitada.
   if y<338 and (x<155 or x>245):continue
   xx,yy=(400-x,y+12) if n==1 else (x,y)
   if 0<=xx<384 and 302<=yy<508:out.putpixel((xx,yy),c)
 # Restaura mãos originais, mantidas por identidade e fase dos braços.
 for y in range(285,345):
  for x in list(range(95,155))+list(range(240,310)):
   c=original.getpixel((x,y))
   if c[3]>8:out.putpixel((x,y),c)
 out.save(Path(__file__).parent/f'icaro-{n:02}-pernas-ensaio.png')
 bg=Image.new('RGBA',out.size,'#eee');bg.alpha_composite(out);bg.convert('RGB').save(Path(__file__).parent/f'icaro-{n:02}-pernas-ensaio-fundo.png')
