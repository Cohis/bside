from pathlib import Path
from PIL import Image
p=Path(__file__).parent.parent
o=Image.open(p/'icaro/06.png').convert('RGBA');d3=Image.open(p/'icaro/03.png').convert('RGBA');d7=Image.open(p/'icaro/07.png').convert('RGBA');s=o.copy()
# Apaga pequeno fragmento de pulseira indevida no braço direito e recompõe
# o contorno/pele com o mesmo braço sem pulseira no quadro 07.
for y in range(255,294):
 for x in range(230,250):
  s.putpixel((x,y),d7.getpixel((x+4,y-2)))
# O braço esquerdo é o braço anatômico que usa a pulseira.
for y in range(285,314):
 for x in range(111,144):
  c=d3.getpixel((x,y));xx,yy=x+11,y-2
  if c[3]:s.putpixel((xx,yy),c)
s.save(Path(__file__).parent/'icaro-06-ensaio.png')
