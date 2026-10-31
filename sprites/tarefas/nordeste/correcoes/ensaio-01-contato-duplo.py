"""Ensaio de rearticulação integral das pernas, sem tocar no tronco/acessórios."""
from pathlib import Path
from PIL import Image

p=Path(__file__).resolve().parent.parent
config={
 'icaro': {'cut':300,'seam0':198,'seam1':214,'left_src_bottom':449,'right_src_bottom':480,'left_dx':30,'left_dy':31,'right_dx':-43,'right_dy':-4,'arms':[(90,300,150,335)]},
 'eva': {'cut':272,'seam0':197,'seam1':214,'left_src_bottom':455,'right_src_bottom':483,'left_dx':28,'left_dy':27,'right_dx':-38,'right_dy':-3,'arms':[(90,272,153,340),(240,272,310,330)]},
}
for nome,c in config.items():
 base=Image.open(p/nome/'01.png').convert('RGBA')
 doador=Image.open(p/nome/'07.png').convert('RGBA')
 out=base.copy();cut=c['cut']
 for y in range(cut,512):
  for x in range(90,310):out.putpixel((x,y),(0,0,0,0))
 # Junta o membro de apoio ao quadril antes do membro que avança.
 for lado in ('right','left'):
  fim_src=c[f'{lado}_src_bottom']; fim_dst=fim_src+c[f'{lado}_dy']; escala=(fim_dst-cut)/(fim_src-cut)
  for yd in range(cut,510):
   ys=round(cut+(yd-cut)/escala)
   if ys<cut or ys>=512:continue
   t=max(0,min(1,(ys-cut)/(fim_src-cut)))
   sep=round(c['seam0']+(c['seam1']-c['seam0'])*t)
   desloc=round(c[f'{lado}_dx']*t)
   for xd in range(95,305):
    xs=xd-desloc
    if xs<95 or xs>=305:continue
    if lado=='left' and xs>=sep:continue
    if lado=='right' and xs<sep:continue
    cor=doador.getpixel((xs,ys))
    if cor[3]<8:continue
    # Mãos da referência não pertencem à calça.
    if nome=='icaro' and ys<349 and (xs<155 or xs>235):continue
    if nome=='eva' and ys<348 and (xs<152 or xs>238):continue
    out.putpixel((xd,yd),cor)
 for x0,y0,x1,y1 in c['arms']:
  out.paste(base.crop((x0,y0,x1,y1)),(x0,y0))
 out.save(p/'correcoes'/f'{nome}-01-contato-duplo-ensaio.png')
 fundo=Image.new('RGBA',out.size,'#eee');fundo.alpha_composite(out)
 fundo.convert('RGB').save(p/'correcoes'/f'{nome}-01-contato-duplo-fundo.png')
