from pathlib import Path
from PIL import Image,ImageDraw
p=Path(__file__).parent.parent
base=Image.open(p/'eva/07.png').convert('RGBA');donor=Image.open(p/'eva/03.png').convert('RGBA')
out=base.copy()
# Remove o pé de balanço retido atrás.
for y in range(335,459):
 limite=185 if y<370 else 193 if y<423 else 190
 for x in range(75,limite):
  if base.getpixel((x,y))[3]:out.putpixel((x,y),(0,0,0,0))
# Transpõe a perna levantada da passagem oposta sem espelho.
mask=Image.new('L',donor.size,0);d=ImageDraw.Draw(mask)
d.polygon([(195,280),(223,281),(234,300),(242,337),(253,380),(258,423),(256,449),(205,448),(197,425),(204,385),(199,345),(189,315)],fill=255)
perna=Image.new('RGBA',donor.size)
perna.paste(donor,(0,0),Image.composite(donor.getchannel('A'),Image.new('L',donor.size),mask))
shift=Image.new('RGBA',donor.size);shift.alpha_composite(perna,(-35,6))
out.alpha_composite(shift)
out.save(Path(__file__).parent/'eva-07-ensaio.png')
bg=Image.new('RGBA',out.size,'#eee');bg.alpha_composite(out);bg.convert('RGB').save(Path(__file__).parent/'eva-07-ensaio-fundo.png')
