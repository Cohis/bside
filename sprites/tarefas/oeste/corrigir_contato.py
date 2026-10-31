"""Corrige a altura inconsistente das pernas geradas na vista oeste.

Somente as linhas abaixo do quadril inferior são remapeadas por vizinho mais
próximo. O tronco, os braços, a cabeça, a paleta e o alfa não são alterados.
Os originais normalizados são guardados antes da primeira correção.
"""
from pathlib import Path
from PIL import Image, ImageDraw
import json, shutil, hashlib

RAIZ = Path(__file__).resolve().parent
TOPO = 350
SOLO = 480


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def corrigir(caminho, original, destino):
    imagem = Image.open(original).convert('RGBA')
    limite = imagem.getbbox()[3]
    if limite <= TOPO:
        raise ValueError(f'Figura sem pernas: {original}')
    saida = Image.new('RGBA', imagem.size)
    origem = imagem.load()
    alvo = saida.load()
    for y in range(imagem.height):
        sy = y if y < TOPO else TOPO + round((y - TOPO) * (limite - TOPO) / (SOLO - TOPO))
        sy = min(imagem.height - 1, sy)
        for x in range(imagem.width):
            alvo[x, y] = origem[x, sy]
    saida.save(destino)
    return {'entrada': str(original.relative_to(RAIZ)),
            'sha256_entrada': sha(original),
            'saida': str(destino.relative_to(RAIZ)),
            'sha256_saida': sha(destino),
            'linha_fixa_final': TOPO,
            'contato_inferior_original': limite,
            'contato_inferior_corrigido': saida.getbbox()[3],
            'alvo_contato': SOLO,
            'metodo': 'remapeamento vertical local por vizinho mais próximo abaixo da linha 350; corrige comprimento inconsistente gerado, sem suavização'}


def main():
    registros = []
    for personagem in ('icaro', 'eva'):
        pasta = RAIZ / personagem
        backup = RAIZ / 'edicoes' / 'originais' / personagem
        backup.mkdir(parents=True, exist_ok=True)
        for n in range(1, 9):
            nome = f'{n:02}.png'
            alvo = pasta / nome
            origem = backup / nome
            if not origem.exists():
                shutil.copy2(alvo, origem)
            registros.append({'personagem': personagem, 'quadro': n,
                              **corrigir(alvo, origem, alvo)})
    (RAIZ / 'edicoes' / 'correcao-contato.json').write_text(
        json.dumps(registros, ensure_ascii=False, indent=2) + '\n')
    for personagem in ('icaro', 'eva'):
        prancha = Image.new('RGB', (384 * 4, 536 * 2), '#e4dfd4')
        desenho = ImageDraw.Draw(prancha)
        for n in range(1, 9):
            quadro = Image.open(RAIZ / personagem / f'{n:02}.png').convert('RGBA')
            x, y = (n - 1) % 4 * 384, (n - 1) // 4 * 536
            prancha.paste(quadro, (x, y + 24), quadro)
            desenho.text((x + 12, y + 6), f'{personagem} {n:02}', fill='black')
            desenho.line((x, y + 24 + SOLO, x + 384, y + 24 + SOLO), fill='#c05b43', width=1)
        prancha.save(RAIZ / f'{personagem}-prancha-correcao.png')
    print('16 quadros corrigidos; originais preservados e log gravado.')


if __name__ == '__main__':
    main()
