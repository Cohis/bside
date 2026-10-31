from pathlib import Path
from PIL import Image,ImageDraw
p=Path(__file__).parent.parent
base=Image.open(p/'icaro/07.png').convert('RGBA');donor=Image.open(p/'icaro/03.png').convert('RGBA')
out=base.copy()
# Retira porção visível da perna em balanço antiga atrás do corpo.
for y in range(342,453):
 limite=184 if y<365 else 194 if y<423 else 188
 for x in range(92,limite):
  if base.getpixel((x,y))[3]:out.putpixel((x,y),(0,0,0,0))
# Perna anatomicamente correspondente no quadro de passagem oposta.
mask=Image.new('L',donor.size,0);d=ImageDraw.Draw(mask)
d.polygon([(200,301),(232,303),(254,325),(260,365),(270,395),(277,439),(260,449),(229,443),(213,420),(214,394),(204,360),(198,323)],fill=255)
perna=Image.new('RGBA',donor.size)
perna.paste(donor,(0,0),Image.composite(donor.getchannel('A'),Image.new('L',donor.size),mask))
for y in range(301,375):
 for x in range(190,280):
  r,g,b,a=perna.getpixel((x,y))
  if a and r>90 and r>g*1.15 and g>b*1.05:
   perna.putpixel((x,y),(0,0,0,0))
shift=Image.new('RGBA',donor.size);shift.alpha_composite(perna,(-30,0))
girada=shift.rotate(-15,resample=Image.Resampling.NEAREST,center=(175,310))
out.alpha_composite(girada)
out.save(Path(__file__).parent/'icaro-07-ensaio.png')
bg=Image.new('RGBA',out.size,'#eee');bg.alpha_composite(out);bg.convert('RGB').save(Path(__file__).parent/'icaro-07-ensaio-fundo.png')
