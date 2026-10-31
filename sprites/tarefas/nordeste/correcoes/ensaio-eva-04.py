from pathlib import Path
from PIL import Image,ImageDraw
p=Path(__file__).parent.parent
o=Image.open(p/'eva/04.png').convert('RGBA');d=Image.open(p/'eva/07.png').convert('RGBA');s=o.copy()
# Remove apenas a manga curvada para diante e mão ausente à direita do tronco.
for y in range(204,282):
 limite=223 if y<230 else 228 if y<248 else 232
 for x in range(limite,273):
  if o.getpixel((x,y))[3]:s.putpixel((x,y),(0,0,0,0))
# Manga direita do mesmo personagem/câmera, braço em recuo com mão legível.
mask=Image.new('L',d.size,0);m=ImageDraw.Draw(mask)
m.polygon([(217,193),(237,188),(246,207),(250,235),(261,273),(263,302),(262,326),(247,337),(223,329),(215,298),(220,267),(214,234)],fill=255)
arm=Image.new('RGBA',d.size);arm.paste(d,(0,0),Image.composite(d.getchannel('A'),Image.new('L',d.size),mask))
s.alpha_composite(arm)
s.save(Path(__file__).parent/'eva-04-ensaio.png')
bg=Image.new('RGBA',s.size,'#eee');bg.alpha_composite(s);bg.convert('RGB').save(Path(__file__).parent/'eva-04-ensaio-fundo.png')
