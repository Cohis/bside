"""Recorta e gira localmente pernas em balanço para testar passagens oeste.

Gera apenas candidatos em edicoes/candidatos; nenhum quadro de produção é
substituído sem revisão visual. A rotação usa os pixels do próprio quadro,
vizinho mais próximo e máscara anatômica desenhada sobre a perna.
"""
from pathlib import Path
from PIL import Image, ImageDraw
import math, json, hashlib

R = Path(__file__).resolve().parent
PLANOS = {
    ('eva',3): {
        'pivo': [213,346], 'graus': 18,
        'poligono': [(207,339),(248,340),(255,359),(278,375),(289,398),
                    (298,424),(300,468),(245,475),(231,439),(232,414),
                    (217,391),(211,365)]},
    ('icaro',3): {
        'pivo': [166,350], 'graus': -18,
        'poligono': [(137,349),(183,349),(183,369),(185,397),(176,426),
                    (175,457),(100,457),(100,418),(126,410),(130,390),
                    (132,360)],
        'costura_cintura': True},
    ('icaro',7): {
        'pivo': [165,340], 'graus': -12,
        'poligono': [(141,334),(187,334),(188,390),(194,420),(202,449),
                    (202,479),(100,479),(100,430),(124,410),(128,370)]},
}


def compor(im, plano):
    mascara=Image.new('L',im.size,0)
    ImageDraw.Draw(mascara).polygon(plano['poligono'],fill=255)
    m=mascara.load();src=im.load()
    base=im.copy();b=base.load()
    for y in range(im.height):
        for x in range(im.width):
            if m[x,y]:b[x,y]=(0,0,0,0)
    cx,cy=plano['pivo'];a=math.radians(plano['graus']);ca,sa=math.cos(a),math.sin(a)
    # Varredura inversa no destino: sem furos de arredondamento.
    recorte=Image.new('RGBA',im.size);out=recorte.load()
    for y in range(max(0,cy-10),min(im.height,cy+170)):
        for x in range(max(0,cx-110),min(im.width,cx+110)):
            dx,dy=x-cx,y-cy
            sx=round(cx+dx*ca+dy*sa)
            sy=round(cy-dx*sa+dy*ca)
            if 0<=sx<im.width and 0<=sy<im.height and m[sx,sy] and src[sx,sy][3]:
                out[x,y]=src[sx,sy]
    # Sobrepor por seleção de pixel, sem interpolar cores no encontro das
    # duas pernas. As bordas semitransparentes já vieram do raw original.
    o=recorte.load();b=base.load()
    for y in range(im.height):
        for x in range(im.width):
            novo=o[x,y]
            if novo[3] and (b[x,y][3] == 0 or novo[3] >= 128):
                b[x,y]=novo
    if plano.get('costura_cintura'):
        # O recorte deixa uma abertura de 1-5 px na junção superior. Reusar
        # a própria linha de tecido anterior mantém a cor e fecha a costura.
        pixel=base.load()
        for y in range(349,356):
            inicio=142+(y-349)
            for x in range(inicio,170):
                if pixel[x,y][3]:
                    break
                if src[x,348][3]:
                    pixel[x,y]=src[x,348]
    return base,mascara


def main():
    pasta=R/'edicoes'/'candidatos';pasta.mkdir(parents=True,exist_ok=True)
    logs=[]
    for (c,n),plano in PLANOS.items():
        preservado=R/'edicoes'/'pre-composicao'/c/f'{n:02}.png'
        origem=preservado if preservado.exists() else R/c/f'{n:02}.png'
        im=Image.open(origem).convert('RGBA')
        resultado,mask=compor(im,plano)
        saida=pasta/f'{c}-{n:02}-rotacao.png';resultado.save(saida)
        overlay=Image.new('RGBA',im.size,(255,0,0,0));overlay.putalpha(mask.point(lambda v:90 if v else 0))
        debug=im.copy();debug.alpha_composite(overlay);debug.save(pasta/f'{c}-{n:02}-mascara.png')
        sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
        logs.append({'personagem':c,'quadro':n,'origem':str(origem.relative_to(R)),
                     'sha256_origem':sha(origem),'candidato':str(saida.relative_to(R)),
                     'sha256_candidato':sha(saida),**plano,
                     'estado':'aguarda revisão visual; produção não alterada'})
    (pasta/'rotacoes.json').write_text(json.dumps(logs,ensure_ascii=False,indent=2)+'\n')
    print(f'{len(logs)} candidato(s) de composição criado(s), produção intacta.')


if __name__=='__main__':main()
