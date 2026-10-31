from PIL import Image,ImageDraw
from pathlib import Path
import json,hashlib
p=Path(__file__).parent
# Cabeça/torso medidos visualmente; coordenadas estimadas, não escala pela passada.
marcos={'icaro':[(100,545,565),(230,635,575),(180,580,555),(165,565,560),(170,575,555),(168,580,565),(170,574,550),(190,605,565)],'eva':[(95,497,580),(180,540,575),(176,544,560),(160,540,560),(180,540,565),(195,560,560),(160,535,550),(150,530,560)]}
bob=[0,4,0,-2,0,4,0,-2]
for c,linhas in marcos.items():
    tecnica=[];frames=[]
    for n,(topo,pescoco,eixo) in enumerate(linhas,1):
        raw=p/'raw'/f'{c}-{n:02}.png';im=Image.open(raw).convert('RGBA');im.putalpha(im.getchannel('A').point(lambda v:0 if v<8 else v));bb=im.getbbox()
        escala=(148 if c=='icaro' else 130)/(pescoco-topo)
        cut=im.crop(bb);cut=cut.resize((round(cut.width*escala),round(cut.height*escala)),Image.Resampling.NEAREST)
        x=round(192+(bb[0]-eixo)*escala);y=round(56+bob[n-1]+(bb[1]-topo)*escala)
        assert x>=4 and y>=4 and x+cut.width<=380 and y+cut.height<=508,(c,n,x,y,cut.size)
        out=Image.new('RGBA',(384,512));out.paste(cut,(x,y));out.save(p/c/f'{n:02}.png');frames.append(out)
        tr={'entrada':str(raw.resolve()),'caixa_original':bb,'escala_uniforme':escala,'posicao':[x,y],'eixo_original':eixo,'ancora':[192,480],'interpolacao':'vizinho mais próximo','calibracao':'estimativa visual da altura cabelo-pescoço, não altura da passada','marcos_raw':[topo,pescoco,eixo],'topo_alvo':56+bob[n-1]}
        (p/c/f'{n:02}.transformacao.json').write_text(json.dumps(tr,indent=2,ensure_ascii=False))
        tecnica.append({'quadro':n,'dimensoes':out.size,'modo':out.mode,'caixa':out.getbbox(),'transparente':out.getchannel('A').getextrema()==(0,255),'sha256':hashlib.sha256(out.tobytes()).hexdigest()})
    assert len({t['sha256'] for t in tecnica})==8
    (p/c/'tecnica.json').write_text(json.dumps(tecnica,indent=2))
    for fundo,nome in [('#eeeeeb','claro'),('#252830','escuro')]:
        sheet=Image.new('RGB',(1536,1064),fundo);d=ImageDraw.Draw(sheet)
        for n,im in enumerate(frames):
            x=(n%4)*384;y=(n//4)*532;sheet.paste(im,(x,y),im);d.text((x+12,y+512),str(n+1),fill='#777777')
        sheet.save(p/f'{c}-prancha-{nome}.png')
    rgb=[]
    for im in frames:
        bg=Image.new('RGBA',im.size,'#eeeeeb');bg.alpha_composite(im);rgb.append(bg.convert('RGB'))
    for ms,nome in [(100,'normal'),(400,'lento')]:rgb[0].save(p/f'{c}-{nome}.gif',save_all=True,append_images=rgb[1:],duration=ms,loop=0)
