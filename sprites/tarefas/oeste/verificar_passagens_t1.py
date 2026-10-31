"""Regenera evidências do oeste sem reverter o rastreamento manual existente."""
from pathlib import Path
from PIL import Image, ImageDraw
import hashlib, json
R=Path(__file__).resolve().parent
for person in ('icaro','eva'):
    velocidade_chao = 43 if person == 'icaro' else 39
    folder=R/person; frames=[]; checks=[]; hashes=[]
    for n in range(1,9):
        path=folder/f'{n:02}.png'; im=Image.open(path).convert('RGBA')
        bbox=im.getbbox(); h=hashlib.sha256(im.tobytes()).hexdigest();hashes.append(h)
        checks.append({'quadro':n,'dimensoes':list(im.size),'modo':im.mode,'bbox':list(bbox) if bbox else None,
                       'alfa_extremos':list(im.getchannel('A').getextrema()),
                       'margem_minima':min(bbox[0],bbox[1],384-bbox[2],512-bbox[3]) if bbox else 0,
                       'sha256_pixels':h})
        bg=Image.new('RGB',im.size,'#e4dfd4');bg.paste(im,(0,0),im);d=ImageDraw.Draw(bg)
        d.line((0,480,383,480),fill='#c05b43',width=1)
        # Terreno avançando à direita: o personagem encara a esquerda.
        for x in range(-384+n*velocidade_chao,768,80):d.line((x,481,x,498),fill='#855e43',width=2)
        d.line((192,480,192,495),fill='#327dc1',width=1)
        frames.append(bg)
    frames[0].save(folder/'revisao-loop.gif',save_all=True,append_images=frames[1:],duration=100,loop=0)
    frames[0].save(folder/'revisao-lenta.gif',save_all=True,append_images=frames[1:],duration=400,loop=0)
    sheet=Image.new('RGB',(1536,1072),'#e4dfd4');d=ImageDraw.Draw(sheet)
    for i,im in enumerate(frames):
        x=(i%4)*384;y=(i//4)*536;sheet.paste(im,(x,y+24));d.text((x+12,y+6),f'{person} {i+1:02}',fill='black')
    sheet.save(R/f'{person}-prancha-corrigida.png')
    (folder/'validacao-tecnica.json').write_text(json.dumps({
        'quadros':checks,'duplicados_exatos':len(set(hashes))!=8,
        'edicao':'Apoio Eva 02/06, variantes t1 03/07, joelhos e solas de balanço reduzidos por remapeamento local nearest, sem nova suavização.',
        'referencias_log':['edicoes/correcao-contato.json','edicoes/apoios-eva-02-06.json','edicoes/passagens-t1-adotadas.json','edicoes/joelho-baixo-adotado.json','edicoes/sola-baixa-adotada.json'],
        'chao_teste':f'{velocidade_chao} px/quadro à direita, calibrado pela média do recuo estimado nos dois apoios; não certifica ausência de patinação.'},ensure_ascii=False,indent=2)+'\n')
print('Pranchas, GIFs 100/400ms, chão de teste e validação técnica do oeste atualizados.')
