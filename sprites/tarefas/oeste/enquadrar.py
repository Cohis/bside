"""Montagem técnica uniforme, sem alteração de anatomia ou cor."""
from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
R=Path(__file__).parent
# Eixo de torso observado nos raws; escala calibrada por cabeça/torso, não bbox da passada.
E={'icaro':[550,530,570,570,570,520,570,550],'eva':[525,480,545,530,545,490,540,540]}
selecionados={('icaro',8):'08-raw-t2.png',('eva',4):'04-raw-t2.png',('eva',6):'06-raw-t2.png'}
for c in E:
 prancha=Image.new('RGB',(384*4,536*2),'#e4dfd4'); d=ImageDraw.Draw(prancha)
 for n in range(1,9):
  p=R/c/selecionados.get((c,n),f'{n:02}-raw.png'); im=Image.open(p).convert('RGBA'); im.putalpha(im.getchannel('A').point(lambda v:0 if v<8 else v)); box=im.getbbox()
  escala=.35; bob={1:0,2:5,3:-2,4:-3,5:0,6:5,7:-2,8:-3}[n]
  pos=(round(192-E[c][n-1]*escala),round(56+bob-box[1]*escala))
  red=im.resize((round(im.width*escala),round(im.height*escala)),Image.Resampling.NEAREST)
  out=Image.new('RGBA',(384,512));out.paste(red,pos);out.save(R/c/f'{n:02}.png')
  (R/c/f'{n:02}.transformacao.json').write_text(json.dumps({'entrada':str(p.resolve()),'escala_uniforme':escala,'interpolacao':'vizinho mais próximo','posicao_imagem_inteira':pos,'eixo_torso_original_estimado':E[c][n-1],'topo_cabeca_destino':56+bob,'ancora':[192,480],'criterio':'Escala comum por comparação visual da cabeça e torso; bob nominal preservado. Não alinhado pelo pé mais baixo.','ruido_alfa_removido':'somente alfa <8'},ensure_ascii=False,indent=2))
  x=((n-1)%4)*384;y=((n-1)//4)*536;prancha.paste(out,(x,y+24),out);d.text((x+12,y+6),f'{c} {n:02}',fill='black')
 prancha.save(R/f'{c}-prancha.png')
