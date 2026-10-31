"""Registra o ponto real de retomada sem considerar um arquivo como aprovação."""
from pathlib import Path
from datetime import datetime, timezone
import hashlib,json
r=Path(__file__).resolve().parents[1]
c=json.loads((r/'contrato.json').read_text())
originais=json.loads((r/'referencias/originais.json').read_text())
bases=json.loads((r/'bases/congeladas.json').read_text())
integridade={}
for personagem,registro in originais.items():
    p=r.parent/registro['original']
    integridade[str(p.relative_to(r.parent))]=hashlib.sha256(p.read_bytes()).hexdigest()==registro['sha256']
for personagem,direcoes in bases.items():
    for direcao,registro in direcoes.items():
        p=r.parent/registro['arquivo']
        integridade[str(p.relative_to(r.parent))]=hashlib.sha256(p.read_bytes()).hexdigest()==registro['sha256']
ciclos=[]
for direcao in c['direcoes']:
    for personagem in c['personagens']:
        pasta=r/'tarefas'/direcao/personagem
        presentes=[f for f in range(1,9) if (pasta/f'{f:02d}.png').exists()]
        revisao=json.loads((pasta/'revisao.json').read_text()) if (pasta/'revisao.json').exists() else {}
        ciclos.append({'personagem':personagem,'direcao':direcao,'quadros_celula':presentes,'faltam':[f for f in range(1,9) if f not in presentes],
                       'revisao_aprovada':revisao.get('aprovado') is True,'pendencias':revisao.get('pendencias',[]),
                       'revisao':str((pasta/'revisao.json').relative_to(r)) if revisao else None})
dados={'atualizado_utc':datetime.now(timezone.utc).isoformat(),'integridade_fontes':integridade,
       'bases':16,'caminhada_em_celulas':sum(len(c['quadros_celula']) for c in ciclos),'caminhada_necessaria':128,
       'ciclos_aprovados':sum(c['revisao_aprovada'] for c in ciclos),'ciclos':ciclos,
       'observacao':'Raws e candidatos não contam como células prontas. Presença de células não equivale a aprovação.'}
(r/'registros/inventario-atual.json').write_text(json.dumps(dados,ensure_ascii=False,indent=2)+'\n')
print(json.dumps({k:v for k,v in dados.items() if k not in ['ciclos','integridade_fontes']},ensure_ascii=False))
if not all(integridade.values()):raise SystemExit('Integridade das referências/bases alterada: conferir inventário.')
