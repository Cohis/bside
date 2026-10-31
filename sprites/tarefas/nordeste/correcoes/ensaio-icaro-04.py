from pathlib import Path
from PIL import Image
p=Path(__file__).parent.parent
original=Image.open(p/'icaro/04.png').convert('RGBA')
doador=Image.open(p/'icaro/08.png').convert('RGBA')
saida=original.copy()
# Braço esquerdo anatômico (à esquerda da tela): transfere o punho e pulseira
# do quadro 08, mantendo pixel intacto e sem espelhamento.
for y in range(270,335):
    for x in range(99,145):
        if original.getpixel((x,y))[3] and x<140:
            saida.putpixel((x,y),(0,0,0,0))
for y in range(250,316):
    for x in range(98,146):
        pixel=doador.getpixel((x,y))
        xx,yy=x+3,y+17
        if pixel[3] and xx<145 and yy<335:
            saida.putpixel((xx,yy),pixel)
# Braço direito anatômico: substitui somente antebraço e mão pelo quadro 08
# com a mesma câmera, retirando a pulseira incorreta.
for y in range(249,305):
    for x in range(241,301):
        if original.getpixel((x,y))[3]:
            saida.putpixel((x,y),(0,0,0,0))
for y in range(239,294):
    for x in range(250,304):
        pixel=doador.getpixel((x,y))
        xx,yy=x-10,y+10
        if pixel[3] and 0<=xx<384 and 0<=yy<512:
            saida.putpixel((xx,yy),pixel)
saida.save(Path(__file__).parent/'icaro-04-ensaio.png')
