"""Regera evidências técnicas após as edições locais na direção oeste."""
from pathlib import Path
from PIL import Image, ImageDraw
import json, hashlib, shutil

R = Path(__file__).resolve().parent
F = R / 'edicoes'


def sha(im):
    return hashlib.sha256(im.tobytes()).hexdigest()


def ajustar_y(y, origem):
    if y < 350:
        return y
    return round(350 + (y - 350) * 130 / (origem - 350))


def main():
    log = json.loads((F / 'correcao-contato.json').read_text())
    dados = {(e['personagem'], e['quadro']): e for e in log}
    for personagem in ('icaro', 'eva'):
        pasta = R / personagem
        frames = []
        verificacoes = []
        for n in range(1, 9):
            im = Image.open(pasta / f'{n:02}.png').convert('RGBA')
            alfa = im.getchannel('A')
            bbox = im.getbbox()
            verificacoes.append({'quadro': n, 'dimensoes': list(im.size), 'modo': im.mode,
                                 'bbox': list(bbox), 'alfa_extremos': list(alfa.getextrema()),
                                 'margem_minima': min(bbox[0], bbox[1], 384-bbox[2], 512-bbox[3]),
                                 'sha256_pixels': sha(im)})
            bg = Image.new('RGB', im.size, '#e4dfd4')
            bg.paste(im, (0, 0), im)
            d = ImageDraw.Draw(bg)
            d.line((0, 480, 383, 480), fill='#c05b43', width=1)
            # Chão marcado que desloca 18 px/quadro na direção oposta ao caminhar.
            for x in range(-384 + n*18, 768, 54):
                d.line((x, 481, x, 489), fill='#855e43', width=1)
            frames.append(bg)
        frames[0].save(pasta/'revisao-loop.gif', save_all=True, append_images=frames[1:], duration=100, loop=0)
        frames[0].save(pasta/'revisao-lenta.gif', save_all=True, append_images=frames[1:], duration=400, loop=0)
        prancha = Image.new('RGB', (1536, 1072), '#e4dfd4')
        pd = ImageDraw.Draw(prancha)
        for n, frame in enumerate(frames, 1):
            x, y = (n-1)%4*384, (n-1)//4*536
            prancha.paste(frame, (x, y+24))
            pd.text((x+12, y+6), f'{personagem} {n:02}', fill='black')
        prancha.save(R/f'{personagem}-prancha-corrigida.png')
        hashes = [q['sha256_pixels'] for q in verificacoes]
        (pasta/'validacao-tecnica.json').write_text(json.dumps({
            'quadros': verificacoes, 'duplicados_exatos': len(set(hashes)) != 8,
            'edicao': 'correção local da variação vertical sob linha y=350, por vizinho mais próximo',
            'referencia_log': 'edicoes/correcao-contato.json'}, ensure_ascii=False, indent=2)+'\n')
        original_tracking = F/'originais'/personagem/'rastreamento.json'
        original_tracking.parent.mkdir(parents=True, exist_ok=True)
        if not original_tracking.exists():
            shutil.copy2(pasta/'rastreamento.json', original_tracking)
        tracking = json.loads(original_tracking.read_text())
        for quadro in tracking['quadros']:
            n = quadro['quadro']
            contato_antigo = dados[(personagem,n)]['contato_inferior_original']
            for chave in ('quadril_estimado',):
                p = quadro.get(chave)
                if p:
                    p[1] = ajustar_y(p[1], contato_antigo)
            for lado in ('esquerda','direita'):
                for chave in ('joelho_estimado_oculto','tornozelo_estimado','ponta_pe_observada_aproximada'):
                    p = quadro[lado].get(chave)
                    if p:
                        p[1] = ajustar_y(p[1], contato_antigo)
            if personagem == 'eva' and n == 7:
                # Variante raw t2 selecionada depois da correção vertical;
                # os pontos anteriores correspondiam a outra pose.
                quadro['quadril_estimado'] = [190, 303]
                quadro['esquerda'] = {
                    'joelho_estimado_oculto': [225, 391],
                    'tornozelo_estimado': [243, 447],
                    'ponta_pe_observada_aproximada': [238, 467]}
                quadro['direita'] = {
                    'joelho_estimado_oculto': [176, 390],
                    'tornozelo_estimado': [184, 459],
                    'ponta_pe_observada_aproximada': [176, 477]}
                quadro['incerteza_px'] = {'quadril': 12, 'joelhos': 20,
                                          'tornozelos': 10, 'pontas': 8}
            if personagem == 'eva' and n == 3:
                quadro['direita'] = {
                    'joelho_estimado_oculto': [225, 398],
                    'tornozelo_estimado': [232, 445],
                    'ponta_pe_observada_aproximada': [209, 465]}
                quadro['incerteza_px'] = {'quadril': 10, 'joelhos': 20,
                                          'tornozelos': 10, 'pontas': 8}
            if personagem == 'icaro' and n == 3:
                quadro['direita'] = {
                    'joelho_estimado_oculto': [178, 394],
                    'tornozelo_estimado': [177, 443],
                    'ponta_pe_observada_aproximada': [150, 466]}
                quadro['incerteza_px'] = {'quadril': 10, 'joelhos': 20,
                                          'tornozelos': 10, 'pontas': 8}
            if personagem == 'icaro' and n == 7:
                quadro['esquerda'] = {
                    'joelho_estimado_oculto': [177, 403],
                    'tornozelo_estimado': [181, 451],
                    'ponta_pe_observada_aproximada': [143, 468]}
                quadro['incerteza_px'] = {'quadril': 10, 'joelhos': 20,
                                          'tornozelos': 10, 'pontas': 8}
        tracking['metodo'] += ' Coordenadas y transferidas pela correção local registrada; estimativas, não novas medições.'
        tracking['advertencia'] = 'Pontos de joelhos ocultos e de pés são estimados; não certificam contato ou ausência de patinação. Passagens ainda pendentes.'
        (pasta/'rastreamento.json').write_text(json.dumps(tracking,ensure_ascii=False,indent=2)+'\n')
        revisao = json.loads((pasta/'revisao.json').read_text())
        revisao['aprovado'] = False
        revisao['observacoes'] = [
            'Oito PNGs RGBA384x512, transparência real, sem cortes ou duplicatas exatas.',
            'Altura do contato inferior estabilizada em y≈480; cabeça/tronco e identidade permaneceram nos pixels originais.',
            'Correção local por vizinho mais próximo registrada em edicoes/correcao-contato.json.',
            'Translação das metades inferiores foi rejeitada por fusão. Composição localizada dos próprios pixels adotada em Ícaro 03/07 e Eva 03; Eva 07 usa variante t2 já gerada.',
            'Prancha e loops 100/400 ms com chão marcado regenerados.'
        ]
        revisao['pendencias'] = ([
            '03/07: pés de balanço foram aproximados por recorte e rotação local; revisar oclusão e continuidade no loop antes da aprovação.',
            'A transição 04→05 e 08→01 ainda precisa ser aprovada em reprodução temporal contínua.',
            'Recuo horizontal do pé de apoio ainda irregular; chão marcado não certifica ausência de patinação.'
        ] if personagem=='icaro' else [
            '03: pé em balanço foi aproximado por recorte e rotação local; revisar oclusão no loop. 07 foi trocado para variante t2, ainda ligeiramente atrás do quadril.',
            '02 ainda apresenta escala de cabeça/tronco distinta dos quadros vizinhos.',
            '04/06: contrabalanço do braço próximo ainda precisa de correção.',
            'A transição 04→05 e 08→01 ainda precisa ser aprovada em reprodução temporal contínua.',
            'Recuo horizontal do pé de apoio ainda irregular; chão marcado não certifica ausência de patinação.'
        ])
        revisao['alturas_bbox_inferior_px'] = {str(q['quadro']):q['bbox'][3] for q in verificacoes}
        (pasta/'revisao.json').write_text(json.dumps(revisao,ensure_ascii=False,indent=2)+'\n')
    print('Pranchas, loops, rastreamento, QA e revisão do oeste atualizados.')


if __name__ == '__main__':
    main()
