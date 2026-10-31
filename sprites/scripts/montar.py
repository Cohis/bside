"""Valida quadros e monta folhas sem alterar os pixels dos personagens."""
import argparse, hashlib, json, shutil
from pathlib import Path
from PIL import Image
from rastreamento import normalizar as normalizar_rastreamento

p=argparse.ArgumentParser();p.add_argument('--previa',action='store_true');p.add_argument('--rascunho',action='store_true');a=p.parse_args()
if a.previa and a.rascunho:raise SystemExit('Escolha somente um modo: --previa ou --rascunho')
r=Path(__file__).resolve().parents[1];c=json.loads((r/'contrato.json').read_text());dest=r/('revisao' if a.rascunho else 'final');dest.mkdir(exist_ok=True)
dados={'celula':c['celula'],'ancora':c['ancora'],'direcoes':c['direcoes'],'duracao_quadro_ms':100,'loop':c['loop'],'personagens':{},'estado':'em_producao'}
falhas=[];resumo=[];imagens={}
for personagem in c['personagens']:
    dados['personagens'][personagem]={}
    for linha,direcao in enumerate(c['direcoes']):
        arquivos=[];hashes=set();aprovacao=r/'tarefas'/direcao/personagem/'revisao.json'
        rev=json.loads(aprovacao.read_text()) if aprovacao.exists() else {}
        for quadro in range(9):
            origem=r/'bases'/personagem/f'{direcao}.png' if quadro==0 else r/'tarefas'/direcao/personagem/f'{quadro:02d}.png'
            frame={'indice':quadro,'fase':c['fases'][quadro],'duracao_ms':None if quadro==0 else 100,'retangulo':{'x':quadro*384,'y':linha*512,'largura':384,'altura':512},'disponivel':origem.exists(),'arquivo':None}
            if origem.exists():
                frame['arquivo']='../'+str(origem.relative_to(r))
                im=Image.open(origem)
                if im.size!=(384,512) or im.mode!='RGBA':
                    falhas.append(f'{personagem}/{direcao}/{quadro}: dimensões/modo inválidos')
                else:
                    alfa=im.getchannel('A');bbox=alfa.getbbox();h=hashlib.sha256(im.tobytes()).hexdigest()
                    if not bbox:falhas.append(f'{personagem}/{direcao}/{quadro}: vazio')
                    elif min(bbox[0],bbox[1],384-bbox[2],512-bbox[3])<4:falhas.append(f'{personagem}/{direcao}/{quadro}: margem insuficiente')
                    if alfa.getextrema()[0]!=0:falhas.append(f'{personagem}/{direcao}/{quadro}: sem transparência')
                    if h in hashes:falhas.append(f'{personagem}/{direcao}/{quadro}: duplicado')
                    hashes.add(h);frame['sha256_pixels']=h;frame['caixa_visivel']=bbox
                    imagens[(personagem,direcao,quadro)]=im.copy()
            else:falhas.append(f'{personagem}/{direcao}/{quadro}: ausente')
            arquivos.append(frame)
        rastreamento=r/'tarefas'/direcao/personagem/'rastreamento.json'
        rastreado=json.loads(rastreamento.read_text()) if rastreamento.exists() else None
        conjunto=r/'tarefas'/direcao/'rastreamento.json'
        if rastreado is None and conjunto.exists():
            rastreado=json.loads(conjunto.read_text()).get(personagem)
        rastreado=normalizar_rastreamento(rastreado)
        dados['personagens'][personagem][direcao]={'quadros':arquivos,'revisao':rev,'rastreamento':rastreado,'passada_teste_px_por_quadro':rev.get('passada_teste_px_por_quadro',18)}
        if rev.get('aprovado') is not True:falhas.append(f'{personagem}/{direcao}: revisão visual pendente')
        resumo.append(f'| {personagem} | {direcao} | {sum(f["disponivel"] for f in arquivos)}/9 | {"aprovada" if rev.get("aprovado") else "pendente"} |')
erros_tecnicos=[f for f in falhas if not f.endswith('revisão visual pendente')]
if not a.previa and (erros_tecnicos or (falhas and not a.rascunho)):
    raise SystemExit('Montagem bloqueada:\n'+'\n'.join(erros_tecnicos if a.rascunho else falhas))
if not a.previa:
    for personagem in c['personagens']:
        folha=Image.new('RGBA',(3456,4096))
        for linha,direcao in enumerate(c['direcoes']):
            pasta=dest/'quadros'/personagem/direcao;pasta.mkdir(parents=True,exist_ok=True)
            for q in range(9):
                im=imagens[(personagem,direcao,q)];folha.paste(im,(q*384,linha*512));im.save(pasta/f'{q:02d}.png')
                dados['personagens'][personagem][direcao]['quadros'][q]['arquivo']=f'quadros/{personagem}/{direcao}/{q:02d}.png'
        folha.save(dest/(f'{personagem}-andar'+('-rascunho' if a.rascunho else '')+'.png'))
    dados['estado']='rascunho_nao_aprovado' if a.rascunho else 'concluido'
    (dest/('animacoes-rascunho.json' if a.rascunho else 'animacoes.json')).write_text(json.dumps(dados,ensure_ascii=False,indent=2)+'\n')
(dest/'dados-previa.js').write_text('window.ANIMACOES = '+json.dumps(dados,ensure_ascii=False)+';\n')
(r/'registros'/'verificacao-tecnica.json').write_text(json.dumps({'modo':'previa' if a.previa else 'rascunho' if a.rascunho else 'final','falhas':falhas,'quadros_encontrados':len(imagens)},ensure_ascii=False,indent=2)+'\n')
texto='# Validação das spritesheets\n\n'+('Entrega completa.' if not falhas else 'Em produção. As bases não representam ciclos de caminhada aprovados.')+'\n\n| Personagem | Direção | Quadros | Revisão visual |\n|---|---|---|---|\n'+'\n'.join(resumo)+'\n\nVerificação técnica: dimensões, RGBA, transparência, margem, células vazias e duplicação exata. Anatomia, paleta, estabilidade temporal e patinação exigem revisão visual independente.\n'
texto+='\n## Pendências por ciclo\n\n'
for personagem,ciclos in dados['personagens'].items():
    for direcao,ciclo in ciclos.items():
        pendencias=ciclo['revisao'].get('pendencias',[])
        if pendencias:
            texto+=f'### {personagem} · {direcao}\n\n'+'\n'.join('- '+str(item) for item in pendencias)+'\n\n'
(dest/'validacao.md').write_text(texto)
print(json.dumps({'quadros':len(imagens),'pendencias':len(falhas),'estado':dados['estado']},ensure_ascii=False))
