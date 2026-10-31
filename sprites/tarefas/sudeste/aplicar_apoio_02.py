"""Adota recuo do pé de apoio em 02 após inspeção 3× dos dois personagens."""
from pathlib import Path
from PIL import Image
import hashlib,json,shutil
R=Path(__file__).resolve().parent;C=R/'candidatos-apoio';B=R/'originais-pre-apoio02';log=[]
for p,dx in (('icaro',-23),('eva',-24)):
 (B/p).mkdir(parents=True,exist_ok=True)
 target=R/p/'02.png';candidate=C/f'{p}-02-apoio.png';backup=B/p/'02.png'
 if not backup.exists():shutil.copy2(target,backup)
 old=target.read_bytes();new=candidate.read_bytes();shutil.copy2(candidate,target)
 im=Image.open(target).convert('RGBA');assert im.size==(384,512) and im.getbbox()[3]==480
 log.append({'personagem':p,'fase':2,'dx_pe_apoio':dx,'anterior':str(backup.relative_to(R)),
             'candidato':str(candidate.relative_to(R)),'sha_antes':hashlib.sha256(old).hexdigest(),
             'sha_depois':hashlib.sha256(new).hexdigest(),
             'metodo':'Translação progressiva somente dos pixels da perna anatômica esquerda de apoio, 0 no quadril até deslocamento dx no calçado; paleta/contorno nearest preservados.'})
(R/'correcao-apoio02.json').write_text(json.dumps(log,ensure_ascii=False,indent=2)+'\n')
