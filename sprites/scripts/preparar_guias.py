"""Gera esquemas de pose; estes desenhos nunca entram nos sprites finais."""
from pathlib import Path
import json
import math
from PIL import Image, ImageDraw

raiz = Path(__file__).resolve().parents[1]
c = json.loads((raiz/'contrato.json').read_text())
passada = [36,18,0,-18,-36,-18,0,18]
elevacao = [0,0,0,0,0,12,24,18]
quadril = [165,160,165,169,165,160,165,169]
cores = {'esquerda':'#c34812','direita':'#1263b9'}
for indice,direcao in enumerate(c['direcoes']):
    theta = indice*math.pi/4
    def projetar(lateral, frente, altura):
        x = 192-lateral*math.cos(theta)+frente*math.sin(theta)
        y = 480-altura-.35*(lateral*math.sin(theta)+frente*math.cos(theta))
        return [round(x,2),round(y,2)]
    pasta = raiz/'guias'/direcao
    pasta.mkdir(parents=True,exist_ok=True)
    for fase in range(1,9):
        f = fase-1
        im = Image.new('RGB',(384,512),'#f4f3ed')
        d = ImageDraw.Draw(im)
        d.line((0,480,384,480),fill='#a7a7a7')
        d.line((192,20,192,496),fill='#d0cfc8')
        centro = projetar(0,0,quadril[f])
        d.line((192,165,192,centro[1]),fill='#444444',width=4)
        d.ellipse((162,95,222,165),outline='#444444',width=3)
        joints = {}
        for lado,lateral,offset in [('esquerda',18,0),('direita',-18,4)]:
            k = (f+offset)%8
            frente,alto = passada[k],elevacao[k]
            z_hip = quadril[f]
            # IK de dois segmentos com comprimento 90: joelho flexiona para frente.
            vx,vz = frente,alto+12-z_hip
            dist = math.hypot(vx,vz)
            h = math.sqrt(max(0,90**2-(dist/2)**2))
            joelho_f = vx/2 + (-vz/dist)*h
            joelho_z = z_hip+vz/2+(vx/dist)*h
            pontos = {
                'quadril':projetar(lateral,0,z_hip),
                'joelho':projetar(lateral,joelho_f,joelho_z),
                'tornozelo':projetar(lateral,frente,alto+12),
                'ponta_pe':projetar(lateral,frente+13,alto),
                'calcanhar':projetar(lateral,frente-8,alto),
                'contato_chao':alto==0,
                'avanco_local':frente,'elevacao_local':alto,
            }
            joints[lado] = pontos
            cor=cores[lado]
            d.line([tuple(pontos[n]) for n in ['quadril','joelho','tornozelo','ponta_pe']],fill=cor,width=5)
            d.line([tuple(pontos[n]) for n in ['calcanhar','ponta_pe']],fill=cor,width=5)
            for n in ['quadril','joelho','tornozelo']:
                x,y=pontos[n];d.ellipse((x-4,y-4,x+4,y+4),fill=cor)
            # Braço oposto à perna: ombro -> cotovelo -> mão.
            ombro=projetar(lateral*1.6,0,quadril[f]+99)
            mao=projetar(lateral*1.6,-frente*.65,quadril[f]+17)
            cotovelo=[(ombro[0]+mao[0])/2,(ombro[1]+mao[1])/2-3]
            d.line([tuple(ombro),tuple(cotovelo),tuple(mao)],fill=cor,width=4)
        d.text((12,12),f'{direcao.upper()} / {fase:02d}',fill='#222222')
        d.text((12,30),c['fases'][fase],fill='#222222')
        d.text((12,52),'Laranja: esquerda anatomica',fill=cores['esquerda'])
        d.text((12,68),'Azul: direita anatomica',fill=cores['direita'])
        d.ellipse((188,476,196,484),outline='#111111',width=2)
        im.save(pasta/f'{fase:02d}.png')
        (pasta/f'{fase:02d}.json').write_text(json.dumps({
            'direcao':direcao,'fase':fase,'descricao':c['fases'][fase],
            'ancora':[192,480],'centro_quadril':centro,'juntas':joints,
            'apoio_principal':'esquerda' if fase<=4 else 'direita',
            'observacao':'Guia esquemático de fase; preservar proporções da base. Não copiar desenho ou cores do guia para o personagem.',
            'deslocamento_por_quadro_projetado':[round(18*math.sin(theta),3),round(-6.3*math.cos(theta),3)],
        },ensure_ascii=False,indent=2)+'\n')
print('64 guias de fase e registros anatômicos gerados.')
