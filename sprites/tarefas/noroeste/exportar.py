"""Enquadramento inteiro e pranchas; não redesenha nem deforma membros."""
from pathlib import Path
import json, subprocess, hashlib
from PIL import Image, ImageDraw

PASTA=Path(__file__).resolve().parent
RAIZ=PASTA.parents[2]
selecionados={c:{f: f'{c}-{f:02d}-t{3 if f==1 else 1}.png' for f in range(1,9)} for c in ('icaro','eva')}
topos=[0,56,60,56,54,56,60,56,54]
resultados={}
for c,quadros in selecionados.items():
    resultados[c]=[]
    imagens=[]
    for f,nome in quadros.items():
        origem=PASTA/'raw'/nome
        im=Image.open(origem).convert('RGBA')
        im.putalpha(im.getchannel('A').point(lambda v:0 if v<8 else v))
        caixa=im.getbbox()
        escala=.35
        # Escala fixa pela cabeça/torso e eixo observado na cintura; pés não determinam enquadramento.
        eixo=550 if c=='icaro' else 545
        solo=topos[f]+round((caixa[3]-caixa[1])*escala)
        destino=PASTA/c/f'{f:02d}.png'
        subprocess.run(['python',str(RAIZ/'sprites/scripts/normalizar.py'),str(origem),str(destino),'--escala',str(escala),'--solo',str(solo),'--eixo',str(eixo)],check=True)
        final=Image.open(destino)
        imagens.append(final.copy())
        resultados[c].append({'quadro':f,'raw':nome,'dimensoes':list(final.size),'modo':final.mode,'bbox':final.getbbox(),'sha256':hashlib.sha256(final.tobytes()).hexdigest(),'topo_planejado':topos[f],'eixo_raw':eixo,'escala':escala})
    for tema,cor in [('claro','#efeee8'),('escuro','#252930')]:
        prancha=Image.new('RGB',(384*4,540*2),cor)
        d=ImageDraw.Draw(prancha)
        for f,im in enumerate(imagens):
            x=(f%4)*384;y=(f//4)*540
            prancha.paste(im,(x,y+24),im)
            d.text((x+12,y+8),f'{c} NO {f+1:02d}',fill='#000000' if tema=='claro' else '#ffffff')
        prancha.save(PASTA/f'{c}-{tema}.png')
    for duracao in [100,400]:
        cenas=[]
        for im in imagens:
            cena=Image.new('RGB',(384,512),'#efeee8');cena.paste(im,(0,0),im);cenas.append(cena)
        cenas[0].save(PASTA/f'{c}-{duracao}ms.gif',save_all=True,append_images=cenas[1:],duration=duracao,loop=0)
    assert len({v['sha256'] for v in resultados[c]})==8
    assert all(v['dimensoes']==[384,512] and v['modo']=='RGBA' for v in resultados[c])
    assert all(v['bbox'][0]>3 and v['bbox'][1]>3 and v['bbox'][2]<381 and v['bbox'][3]<509 for v in resultados[c])
(PASTA/'tecnica.json').write_text(json.dumps(resultados,ensure_ascii=False,indent=2))
(PASTA/'selecionados.json').write_text(json.dumps(selecionados,ensure_ascii=False,indent=2))
print('16 células exportadas; dimensões, margens e unicidade verificadas. Aprovação visual separada.')
# As duas correções locais aprovadas da pulseira são reaplicadas após qualquer
# reexportação; o QA recalcula hashes, pranchas e GIFs das células resultantes.
subprocess.run(['python', str(PASTA/'corrigir-pulseira.py')], check=True)
subprocess.run(['python', str(PASTA/'atualizar-qa.py')], check=True)
