"""Candidato: perna de balanço t1 com perna de apoio corrente da fase 07."""
from pathlib import Path
from PIL import Image, ImageDraw
R=Path(__file__).resolve().parents[1]
C=Path(__file__).resolve().parent/'novos-candidatos'
plans={
 'icaro': {'top':315,'clear':[(190,315),(248,315),(270,482),(145,482),(150,449),(181,423)],'add':[(190,315),(253,315),(270,482),(190,482),(181,447),(188,414)]},
 'eva': {'top':308,'clear':[(186,308),(245,308),(261,482),(156,482),(162,450),(189,418)],'add':[(189,308),(249,308),(264,482),(134,482),(160,450),(188,420)]}}
for person,plan in plans.items():
 t1=Image.open(C/f'{person}-07-t1-contato.png').convert('RGBA')
 cur=Image.open(R/person/'07.png').convert('RGBA')
 mask=Image.new('L',t1.size);ImageDraw.Draw(mask).polygon(plan['clear'],fill=255)
 out=t1.copy();a=out.load();m=mask.load()
 for y in range(plan['top'],482):
  for x in range(384):
   if m[x,y]:a[x,y]=(0,0,0,0)
 add=Image.new('L',t1.size);ImageDraw.Draw(add).polygon(plan['add'],fill=255)
 out.paste(cur,(0,0),add)
 out.save(C/f'{person}-07-t1-apoio-atual.png')
 sheet=Image.new('RGB',(384*3,512),'#e4dfd4')
 for i,path in enumerate([R/person/'06.png',C/f'{person}-07-t1-apoio-atual.png',R/person/'08.png']):
  im=Image.open(path).convert('RGBA');bg=Image.new('RGB',im.size,'#e4dfd4');bg.paste(im,(0,0),im);ImageDraw.Draw(bg).line((0,480,383,480),fill='red');sheet.paste(bg,(i*384,0))
 sheet.save(C/f'{person}-060708-t1-apoio-atual.png')
