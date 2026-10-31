"""Enquadra uma geração inteira sem deformar membros nem suavizar pixels."""
import argparse
import json
from pathlib import Path
from PIL import Image

p = argparse.ArgumentParser(description=__doc__)
p.add_argument('entrada', type=Path)
p.add_argument('saida', type=Path)
p.add_argument('--altura', type=int, default=424)
p.add_argument('--solo', type=int, default=480)
p.add_argument('--eixo', type=float, help='Eixo corporal na geração, em pixels; padrão: centro do recorte')
p.add_argument('--escala', type=float, help='Escala uniforme explícita, preferível entre quadros equivalentes')
a = p.parse_args()
im = Image.open(a.entrada).convert('RGBA')
alfa = im.getchannel('A')
# A geração pode incluir ruído invisível de alfa 1–7 longe do personagem.
# Não extrai fundos opacos nem elimina componentes conectados à figura.
im.putalpha(alfa.point(lambda v: 0 if v < 8 else v))
caixa = im.getbbox()
if caixa is None:
    raise SystemExit('Imagem vazia')
x0, y0, x1, y1 = caixa
escala = a.escala if a.escala is not None else a.altura / (y1-y0)
eixo = a.eixo if a.eixo is not None else (x0+x1)/2
recorte = im.crop(caixa)
tamanho = (round(recorte.width*escala), round(recorte.height*escala))
recorte = recorte.resize(tamanho, Image.Resampling.NEAREST)
x = round(192-(eixo-x0)*escala)
y = a.solo-recorte.height
if x < 4 or y < 4 or x+recorte.width > 380 or a.solo > 508:
    raise SystemExit(f'Figura sem margem segura: {(x,y,*tamanho)}')
saida = Image.new('RGBA', (384,512))
# paste sem máscara preserva os valores de alfa, sem multiplicá-los.
saida.paste(recorte, (x,y))
a.saida.parent.mkdir(parents=True, exist_ok=True)
saida.save(a.saida)
a.saida.with_suffix('.transformacao.json').write_text(json.dumps({
    'entrada':str(a.entrada.resolve()),'caixa_original':caixa,
    'escala_uniforme':escala,'interpolacao':'vizinho mais próximo',
    'ruido_alfa_removido':'somente valores menores que 8/255',
    'posicao':[x,y],'eixo_original':eixo,'ancora':[192,480],
},ensure_ascii=False,indent=2)+'\n')
