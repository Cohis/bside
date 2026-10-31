"""Aplica remapeamento local de joelho após inspeção ampliada das quatro passagens."""
from pathlib import Path
from PIL import Image
import hashlib,json,shutil
R=Path(__file__).resolve().parents[1];E=R/'edicoes';C=E/'novos-candidatos';B=E/'pre-baixar-joelho';B.mkdir(exist_ok=True)
entries=[]
for p in ('icaro','eva'):
 (B/p).mkdir(exist_ok=True)
 for n in (3,7):
  target=R/p/f'{n:02}.png';candidate=C/f'{p}-{n:02}-joelho-baixo.png';backup=B/p/f'{n:02}.png'
  assert target.exists() and candidate.exists()
  if not backup.exists():shutil.copy2(target,backup)
  sha_before=hashlib.sha256(target.read_bytes()).hexdigest()
  shutil.copy2(candidate,target)
  im=Image.open(target).convert('RGBA');assert im.size==(384,512) and im.getbbox()[3]==480
  entries.append({'personagem':p,'quadro':n,'fonte_t1':str(backup.relative_to(R)),'candidato':str(candidate.relative_to(R)),
                  'sha_antes':sha_before,'sha_depois':hashlib.sha256(target.read_bytes()).hexdigest(),
                  'metodo':'Remapeamento espacial local por vizinho mais próximo; y 0 no quadril/solo, máximo 20–22 px no joelho, 8–9 px no calçado em balanço; x amortecido até zero na perna de apoio. Tronco/escala/câmera preservados.'})
(E/'joelho-baixo-adotado.json').write_text(json.dumps(entries,ensure_ascii=False,indent=2)+'\n')
