"""Adota as quatro passagens de sola reduzida após inspeção 3×."""
from pathlib import Path
from PIL import Image
import hashlib,json,shutil
R=Path(__file__).resolve().parents[1];E=R/'edicoes';C=E/'novos-candidatos';B=E/'pre-sola-baixa';log=[]
for p in ('icaro','eva'):
 (B/p).mkdir(parents=True,exist_ok=True)
 for n in (3,7):
  target=R/p/f'{n:02}.png';candidate=C/f'{p}-{n:02}-sola-baixa.png';backup=B/p/f'{n:02}.png'
  if not backup.exists():shutil.copy2(target,backup)
  before=target.read_bytes();after=candidate.read_bytes();shutil.copy2(candidate,target)
  im=Image.open(target).convert('RGBA');assert im.size==(384,512) and im.getbbox()[3]==480
  log.append({'personagem':p,'quadro':n,'anterior':str(backup.relative_to(R)),
              'candidato':str(candidate.relative_to(R)),'sha_antes':hashlib.sha256(before).hexdigest(),
              'sha_depois':hashlib.sha256(after).hexdigest(),
              'metodo':'Remapeamento vertical local nearest na perna de balanço, máximo 15 px Ícaro / 11 px Eva na sola; zero no quadril e chão; pé de apoio intacto.'})
(E/'sola-baixa-adotada.json').write_text(json.dumps(log,ensure_ascii=False,indent=2)+'\n')
