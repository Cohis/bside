"""Aplica o ajuste vertical aprovado visualmente; preserva versões anteriores e hashes."""
from pathlib import Path
from PIL import Image
import hashlib,json,shutil
R=Path(__file__).resolve().parent;C=R/'candidatos-solo';B=R/'originais-pre-solo';entries=[]
for p in ('icaro','eva'):
 (B/p).mkdir(parents=True,exist_ok=True)
 for n in range(1,9):
  target=R/p/f'{n:02}.png';candidate=C/f'{p}-{n:02}-solo.png';old=target.read_bytes();new=candidate.read_bytes()
  if old==new:continue
  backup=B/p/f'{n:02}.png'
  if not backup.exists():shutil.copy2(target,backup)
  before=Image.open(target).convert('RGBA').getbbox()[3]
  shutil.copy2(candidate,target)
  after=Image.open(target).convert('RGBA').getbbox()[3]
  assert after==480
  entries.append({'personagem':p,'fase':n,'bbox_inferior_antes':before,'bbox_inferior_depois':after,
                  'anterior':str(backup.relative_to(R)),'candidato':str(candidate.relative_to(R)),
                  'sha_antes':hashlib.sha256(old).hexdigest(),'sha_depois':hashlib.sha256(new).hexdigest(),
                  'metodo':'Remapeamento vertical por vizinho mais próximo abaixo de y330 Ícaro/y324 Eva; cabeça/tronco inalterados, apoio levado a y480.'})
(R/'correcao-solo.json').write_text(json.dumps(entries,ensure_ascii=False,indent=2)+'\n')
print(f'{len(entries)} quadros alterados; backups e hashes registrados')
