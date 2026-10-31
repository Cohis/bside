"""Seleciona a variante já gerada com melhor passagem esquerda de Eva oeste."""
from pathlib import Path
from PIL import Image
import json, shutil, hashlib

R=Path(__file__).resolve().parent
P=R/'eva'
raw=P/'07-raw-t2.png'
dest=P/'07.png'
backup=R/'edicoes'/'selecoes-anteriores'/'eva-07.png'
backup.parent.mkdir(parents=True,exist_ok=True)
if not backup.exists():
    shutil.copy2(dest,backup)
im=Image.open(raw).convert('RGBA')
im.putalpha(im.getchannel('A').point(lambda v:0 if v<8 else v))
box=im.getbbox()
escala=.35
eixo=540
pos=(round(192-eixo*escala),round(54-box[1]*escala))
red=im.resize((round(im.width*escala),round(im.height*escala)),Image.Resampling.NEAREST)
normal=Image.new('RGBA',(384,512))
normal.paste(red,pos)
solo_bruto=normal.getbbox()[3]
saida=Image.new('RGBA',(384,512))
src,dst=normal.load(),saida.load()
for y in range(512):
    sy=y if y<350 else min(511,350+round((y-350)*(solo_bruto-350)/130))
    for x in range(384):dst[x,y]=src[x,sy]
saida.save(dest)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
log={'personagem':'eva','quadro':7,'raw_escolhido':str(raw.relative_to(R)),
     'motivo':'pé em balanço mais próximo do eixo do quadril e claramente elevado; mantém o mesmo rosto, roupa e direção',
     'anterior':str(backup.relative_to(R)),'sha256_anterior':sha(backup),
     'escala_uniforme':escala,'eixo_raw':eixo,'posicao':pos,'topo_cabeca_destino':54,
     'contato_inferior_antes_correcao':solo_bruto,'contato_inferior_depois':saida.getbbox()[3],
     'sha256_resultado':sha(dest),'interpolacao':'vizinho mais próximo'}
(R/'edicoes'/'selecionar-eva07.json').write_text(json.dumps(log,ensure_ascii=False,indent=2)+'\n')
print('Eva oeste 07 selecionado da variante t2; anterior preservado.')
