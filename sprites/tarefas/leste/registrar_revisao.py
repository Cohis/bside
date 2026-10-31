"""Registra rastreamento visual aproximado, sem alegar juntas visíveis sob roupa."""
import json,statistics
from pathlib import Path
r=Path(__file__).resolve().parent
# Por fase: quadril central; joelho, tornozelo e ponta do pé esquerdo; idem direito.
medidas={
'icaro':[
[[192,310],[218,386],[237,447],[282,464],[166,390],[137,444],[170,478]],
[[192,315],[219,384],[235,451],[278,475],[158,390],[134,438],[151,476]],
[[192,302],[180,391],[168,453],[211,476],[239,357],[211,412],[238,442]],
[[192,306],[153,389],[118,447],[144,477],[238,377],[274,423],[316,438]],
[[192,307],[153,388],[120,422],[152,468],[218,383],[234,445],[278,475]],
[[192,311],[151,391],[116,414],[149,460],[216,383],[231,444],[278,475]],
[[192,303],[171,370],[143,394],[166,440],[212,378],[219,443],[252,474]],
[[192,307],[244,377],[275,424],[317,438],[160,386],[145,443],[169,477]]],
'eva':[
[[192,299],[226,377],[263,449],[305,470],[157,384],[124,436],[147,475]],
[[192,301],[225,374],[269,448],[309,474],[154,387],[119,426],[152,465]],
[[192,283],[178,386],[178,451],[218,475],[231,354],[236,413],[280,423]],
[[192,292],[153,380],[119,444],[144,476],[239,374],[276,430],[319,432]],
[[192,289],[154,377],[120,430],[148,473],[224,379],[235,445],[289,474]],
[[192,299],[153,385],[115,418],[133,473],[231,381],[233,445],[292,475]],
[[192,293],[213,355],[145,420],[162,455],[194,390],[193,447],[230,477]],
[[192,292],[246,378],[280,426],[318,431],[165,386],[143,435],[166,476]]]
}
for person,rows in medidas.items():
 frames=[]
 for i,(hip,lk,la,lt,rk,ra,rt) in enumerate(rows,1):
  lados={}
  for lado,k,a,t in [('esquerda',lk,la,lt),('direita',rk,ra,rt)]:
   contato=lado==('esquerda' if i<=4 else 'direita') or i in (1,5)
   lados[lado]={'quadril':hip,'joelho':k,'tornozelo':a,'ponta_pe':t,'contato_chao':contato,'confianca':'estimativa visual','oclusao':'Quadril e joelho inferidos sob calça; tornozelo sob barra. Ponta do tênis visível.','incerteza_px':{'quadril':8,'joelho':12,'tornozelo':8,'ponta_pe':5}}
  frames.append({'fase':i,'centro_quadril':hip,'juntas':lados,'status':'pendente: fase incorreta' if i==7 else 'inspecionado estaticamente'})
 # Recuo por intervalos contato -> fim do apoio. Ainda provisório pois07 não passou.
 passo_l=(rows[0][2][0]-rows[3][2][0])/3
 passo_r=(rows[4][5][0]-rows[7][5][0])/3
 passo=round((passo_l+passo_r)/2,1)
 (r/person/'rastreamento.json').write_text(json.dumps({'direcao':'leste','sistema':'pixels da célula384x512; direita anatômica próxima; esquerda distante','metodo':'Leitura visual sobre prancha quadriculada, estimativas arredondadas. Não são medidas de captura de movimento.','quadros':frames,'recuo_apoio_px_por_quadro':{'esquerda_intervalo01_04':round(passo_l,1),'direita_intervalo05_08':round(passo_r,1),'media_provisoria':passo,'observacao':'Recuo não uniforme:01→02 e05→06 são menores que02→03.07 inadequado impede aprovação do loop; velocidade só para diagnóstico.'}},ensure_ascii=False,indent=2))
 rev={'aprovado':False,'observacoes':['Oito PNGsRGBA384x512 entregues, sem células vazias/duplicatas ou cortes.','Pulseira de Ícaro no braço esquerdo distante; pernas reconhecidas por bolso próximo.','Ícaro02 corrigiu lateral; Eva06 corrigiu contrabalanço e anatomia das mangas.','Inspeção estática em fundos claro/escuro e de cada transição feita; GIFs100ms e400ms produzidos para revisão temporal do coordenador.','Não se declara aprovação temporal por existência doGIF.','Enquadramento uniforme da figura inteira, eixo manual do tronco, sem espelhamento nem deformação; alturas420–428px preservam oscilação discreta.','Paleta/material e contorno preservados visualmente; a geração possui variações finas de tons e desenho de pixels, sem quantização forçada.'], 'quadros_revisados':list(range(1,9)),'transicoes_revisadas':['01→02','02→03','03→04','04→05','05→06','06→07','07→08','08→01'],'passada_teste_px_por_quadro':passo,'passada_teste_status':'provisória, usar para diagnóstico; não certifica ausência de patinação','pendencias':['07: pé em balanço ficou atrás do apoio, sugere saída/recepção em vez de passagem sob quadril. Corrigir com guia explícito; não gerar novas tentativas cegas.','Verificar novamente ciclo100ms/400ms e chão após corrigir07; recuo do apoio é desigual.'],'evidencias':{'tecnica':'tecnica.json','rastreamento':'rastreamento.json','prancha_clara':f'../{person}-inspecao-claro.png','prancha_escura':f'../{person}-inspecao-escuro.png','loop100ms':f'../{person}-loop.gif','loop400ms':f'../{person}-lento.gif'}}
 if person=='icaro':rev['pendencias'].append('07: braço próximo continua recuado como06; falta transição para o avanço de08.')
 (r/person/'revisao.json').write_text(json.dumps(rev,ensure_ascii=False,indent=2))
