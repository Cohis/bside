"""Pranchas e GIFs dos candidatos 03/07; não altera os quadros de produção."""
from pathlib import Path
from PIL import Image, ImageDraw
R=Path(__file__).resolve().parents[1]
C=R/'edicoes/novos-candidatos'
for p in ('icaro','eva'):
    frames=[]
    speed=43 if p=='icaro' else 39
    for n in range(1,9):
        path=C/f'{p}-{n:02}-rearticulado.png' if n in (3,7) else R/p/f'{n:02}.png'
        im=Image.open(path).convert('RGBA')
        bg=Image.new('RGB',im.size,'#e4dfd4'); bg.paste(im,(0,0),im)
        d=ImageDraw.Draw(bg)
        d.line((0,480,383,480),fill='#c05b43')
        for x in range(-384+n*speed,768,80):d.line((x,481,x,498),fill='#855e43',width=2)
        d.line((192,480,192,495),fill='#327dc1')
        frames.append(bg)
    for ms in (100,400):
        frames[0].save(C/f'{p}-rearticulado-{ms}ms.gif',save_all=True,append_images=frames[1:],duration=ms,loop=0)
    sheet=Image.new('RGB',(1536,1072),'#e4dfd4');d=ImageDraw.Draw(sheet)
    for i,im in enumerate(frames):
        x=(i%4)*384;y=(i//4)*536;sheet.paste(im,(x,y+24));d.text((x+12,y+6),f'{p} {i+1:02}',fill='black')
    sheet.save(C/f'{p}-rearticulado-ciclo.png')
