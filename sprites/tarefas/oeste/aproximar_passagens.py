"""Aproxima os pés em balanço do eixo corporal nas passagens oeste 03/07.

Translada cada metade inferior, gradualmente a partir da cintura, sem
redimensionar pixels, pés ou acessórios. Os quadros pós-correção de contato
são preservados para comparação e reversão.
"""
from pathlib import Path
from PIL import Image, ImageDraw
import json, shutil, hashlib

RAIZ = Path(__file__).resolve().parent
PLANOS = {
    ('icaro', 3): {'divisao': 188, 'esquerda': 38, 'direita': -6},
    ('icaro', 7): {'divisao': 186, 'esquerda': 32, 'direita': -8},
    ('eva', 3): {'divisao': 195, 'esquerda': 9, 'direita': -47},
    ('eva', 7): {'divisao': 188, 'esquerda': 38, 'direita': -8},
}
INICIO = 336
FINAL = 450


def hash_file(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def editar(im, plano):
    out = Image.new('RGBA', im.size)
    src, dst = im.load(), out.load()
    divisao = plano['divisao']
    # Lado do pé de apoio primeiro, pé em balanço por cima onde se sobrepõem.
    lado_balanço = 'direita' if plano['direita'] < -20 else 'esquerda'
    ordem = ['esquerda', 'direita']
    ordem.remove(lado_balanço)
    ordem.append(lado_balanço)
    for y in range(im.height):
        if y < INICIO:
            for x in range(im.width):
                dst[x, y] = src[x, y]
            continue
        progresso = min(1, (y - INICIO) / (FINAL - INICIO))
        for lado in ordem:
            faixa = range(0, divisao) if lado == 'esquerda' else range(divisao, im.width)
            dx = round(plano[lado] * progresso)
            for x in faixa:
                xx = x + dx
                if 0 <= xx < im.width and src[x, y][3]:
                    dst[xx, y] = src[x, y]
    return out


def main():
    log = []
    for (personagem, n), plano in PLANOS.items():
        caminho = RAIZ / personagem / f'{n:02}.png'
        anterior = RAIZ / 'edicoes' / 'pos-contato' / personagem / f'{n:02}.png'
        anterior.parent.mkdir(parents=True, exist_ok=True)
        if not anterior.exists():
            shutil.copy2(caminho, anterior)
        im = Image.open(anterior).convert('RGBA')
        editado = editar(im, plano)
        editado.save(caminho)
        log.append({'personagem': personagem, 'quadro': n,
                    'anterior': str(anterior.relative_to(RAIZ)),
                    'sha256_anterior': hash_file(anterior),
                    'sha256_resultado': hash_file(caminho),
                    'divisao_px': plano['divisao'],
                    'deslocamento_final_px': {k: plano[k] for k in ('esquerda', 'direita')},
                    'rampa_y_px': [INICIO, FINAL],
                    'metodo': 'translação por linhas das duas metades inferiores; escala e paleta inalteradas; perna em balanço desenhada por cima'})
    (RAIZ / 'edicoes' / 'aproximar-passagens.json').write_text(json.dumps(log, ensure_ascii=False, indent=2) + '\n')
    for personagem in ('icaro', 'eva'):
        prancha = Image.new('RGB', (1536, 1072), '#e4dfd4')
        d = ImageDraw.Draw(prancha)
        for n in range(1, 9):
            im = Image.open(RAIZ / personagem / f'{n:02}.png').convert('RGBA')
            x, y = (n-1)%4*384, (n-1)//4*536
            prancha.paste(im, (x, y+24), im)
            d.text((x+12, y+6), f'{personagem} {n:02}', fill='black')
            d.line((x, y+504, x+384, y+504), fill='#c05b43', width=1)
        prancha.save(RAIZ / f'{personagem}-prancha-corrigida.png')
    print('Quatro passagens editadas; originais pós-contato e log preservados.')


if __name__ == '__main__':
    main()
