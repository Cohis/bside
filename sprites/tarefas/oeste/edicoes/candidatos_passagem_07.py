"""Testa deslocamento progressivo do apoio nas variantes originais t1 de 07."""
from pathlib import Path
from PIL import Image, ImageDraw

R = Path(__file__).resolve().parents[1]
C = Path(__file__).resolve().parent / 'novos-candidatos'

plans = {
    'icaro': {'dx': 28, 'poly': [(191, 325), (246, 325), (250, 480), (151, 480), (160, 452), (186, 425)], 'start': 325},
    'eva': {'dx': -24, 'poly': [(190, 307), (245, 307), (250, 482), (163, 482), (171, 450), (190, 420)], 'start': 307},
}
for person, plan in plans.items():
    original = Image.open(C/f'{person}-07-t1-contato.png').convert('RGBA')
    mask = Image.new('L', original.size)
    ImageDraw.Draw(mask).polygon(plan['poly'], fill=255)
    src, m = original.load(), mask.load()
    output = original.copy(); out = output.load(); shifted = []
    for y in range(original.height):
        dx = round(plan['dx']*max(0, min(1,(y-plan['start'])/(465-plan['start']))))
        for x in range(original.width):
            if m[x,y] and src[x,y][3]:
                shifted.append((x+dx,y,src[x,y])); out[x,y]=(0,0,0,0)
    for x,y,pixel in shifted:
        if 0 <= x < original.width:out[x,y]=pixel
    output.save(C/f'{person}-07-t1-apoio.png')
    sheet=Image.new('RGB',(384*3,512),'#e4dfd4')
    for i,path in enumerate([R/person/'06.png',C/f'{person}-07-t1-apoio.png',R/person/'08.png']):
        im=Image.open(path).convert('RGBA');bg=Image.new('RGB',im.size,'#e4dfd4');bg.paste(im,(0,0),im);ImageDraw.Draw(bg).line((0,480,383,480),fill='red');sheet.paste(bg,(i*384,0))
    sheet.save(C/f'{person}-060708-t1-apoio.png')
