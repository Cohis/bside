"""Aplica apenas os candidatos aprovados para uso como rascunho da direção."""

from pathlib import Path
from PIL import Image, ImageDraw
import hashlib
import json
import shutil

D = Path(__file__).resolve().parent.parent
C = D / 'correcoes'
O = C / 'originais'
selecoes = {
    'icaro': {'02': 'icaro-02-imagemgerada-normalizada.png',
              '07': 'icaro-07-composicao-v1.png'},
    'eva': {'02': 'eva-02-imagemgerada-normalizada.png',
            '03': 'eva-03-composicao-v2.png'},
}

for personagem, fases in selecoes.items():
    for fase, nome in fases.items():
        destino = D / personagem / f'{fase}.png'
        anterior = O / personagem / f'{fase}.png'
        anterior.parent.mkdir(parents=True, exist_ok=True)
        if not anterior.exists():
            shutil.copy2(destino, anterior)
            shutil.copy2(destino.with_suffix('.transformacao.json'),
                         anterior.with_suffix('.transformacao.json'))
        origem = C / nome
        imagem = Image.open(origem).convert('RGBA')
        assert imagem.size == (384, 512)
        imagem.save(destino)
        metadados = {
            'entrada': str(origem.resolve()),
            'original_preservado': str(anterior.resolve()),
            'interpolacao': 'vizinho mais próximo',
            'ancora': [192, 480],
            'metodo': ('composição localizada de pixels do próprio personagem'
                       if fase in ('03', '07') else
                       'edição guiada, normalizada na célula por vizinho mais próximo'),
            'estado': 'candidato selecionado para revisão; ciclo não aprovado',
        }
        destino.with_suffix('.transformacao.json').write_text(
            json.dumps(metadados, ensure_ascii=False, indent=2) + '\n')

selecionados = json.loads((D / 'selecionados.json').read_text())
for personagem, fases in selecoes.items():
    for fase, nome in fases.items():
        selecionados[personagem][str(int(fase))] = str((C / nome).resolve())
(D / 'selecionados.json').write_text(json.dumps(selecionados, ensure_ascii=False, indent=2) + '\n')

tecnica = {}
for personagem in ('icaro', 'eva'):
    quadros = [Image.open(D / personagem / f'{fase:02}.png').convert('RGBA')
               for fase in range(1, 9)]
    resultados = []
    for fase, imagem in enumerate(quadros, 1):
        bbox = imagem.getbbox()
        resultados.append({
            'fase': fase, 'tamanho': imagem.size, 'modo': imagem.mode,
            'bbox': bbox,
            'margens_ok': bbox[0] >= 4 and bbox[1] >= 4 and bbox[2] <= 380 and bbox[3] <= 508,
            'transparencia': imagem.getchannel('A').getextrema() == (0, 255),
            'hash_pixels': hashlib.sha256(imagem.tobytes()).hexdigest(),
        })
    tecnica[personagem] = {
        'quadros': resultados,
        'duplicatas': len({r['hash_pixels'] for r in resultados}) != 8,
    }
    for fundo, nome in (('#f5f3ef', 'claro'), ('#242735', 'escuro')):
        prancha = Image.new('RGB', (1536, 1064), fundo)
        desenhar = ImageDraw.Draw(prancha)
        for i, imagem in enumerate(quadros):
            x, y = i % 4 * 384, i // 4 * 532 + 20
            prancha.paste(imagem, (x, y), imagem)
            desenhar.text((x + 8, y - 16), f'{personagem} {i + 1:02}', fill='#888888')
        prancha.save(D / f'{personagem}-prancha-{nome}.png')
    opacos = []
    for imagem in quadros:
        fundo = Image.new('RGB', imagem.size, '#e7e8eb')
        fundo.paste(imagem, (0, 0), imagem)
        opacos.append(fundo)
    for duracao in (100, 400):
        opacos[0].save(D / f'{personagem}-loop-{duracao}ms.gif',
                       save_all=True, append_images=opacos[1:], duration=duracao, loop=0)
(D / 'tecnica.json').write_text(json.dumps(tecnica, ensure_ascii=False, indent=2) + '\n')
print('Quatro quadros substituídos com originais preservados; pranchas e loops atualizados.')
