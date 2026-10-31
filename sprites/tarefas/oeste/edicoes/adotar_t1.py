"""Adota passagens t1 dos raws já existentes, preservando as versões anteriores."""
from pathlib import Path
from PIL import Image
import hashlib,json,shutil
R=Path(__file__).resolve().parents[1]
E=R/'edicoes'; C=E/'novos-candidatos'; B=E/'pre-t1-passagem';B.mkdir(exist_ok=True)
entries=[]
for person in ('icaro','eva'):
 (B/person).mkdir(exist_ok=True)
 for n in (3,7):
  target=R/person/f'{n:02}.png'; src=C/f'{person}-{n:02}-t1-contato.png'; backup=B/person/f'{n:02}.png'
  assert src.exists() and target.exists()
  if not backup.exists():shutil.copy2(target,backup)
  before=hashlib.sha256(target.read_bytes()).hexdigest()
  shutil.copy2(src,target)
  after=hashlib.sha256(target.read_bytes()).hexdigest()
  im=Image.open(target).convert('RGBA')
  assert im.size==(384,512) and im.getbbox() is not None
  entries.append({'personagem':person,'quadro':n,'fonte':str(src.relative_to(R)),'raw_original':f'{person}/{n:02}-raw-t1.png','versao_anterior':str(backup.relative_to(R)),'sha_antes':before,'sha_depois':after,'metodo':'Normalização existente dos raws t1, alfa<8 removido, redimensionamento nearest .35 e contato inferior ajustado por vizinho mais próximo. Sem composição das pernas ou interpolação.'})
(E/'passagens-t1-adotadas.json').write_text(json.dumps(entries,ensure_ascii=False,indent=2)+'\n')
