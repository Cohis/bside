from pathlib import Path
import json,math
p=Path(__file__).parent
pes={'icaro':[((245,415),(155,460)),((225,450),(120,450)),((180,474),(244,427)),((135,466),(260,430)),((150,468),(270,447)),((130,418),(222,464)),((160,418),(217,470)),((255,398),(170,455))], 'eva':[((245,414),(155,453)),((245,440),(165,465)),((180,460),(225,416)),((155,450),(250,416)),((155,462),(250,447)),((145,422),(225,449)),((160,410),(220,459)),((265,396),(190,451))]}
for c,frames in pes.items():
    rast=[]
    for n,(e,d) in enumerate(frames,1):
        bob=[0,4,0,-2,0,4,0,-2][n-1];hip=(192,300+bob) if c=='icaro' else (192,285+bob)
        juntas={}
        for lado,pe,dx in [('esquerda',e,-12),('direita',d,12)]:
            juntas[lado]={'quadril':[hip[0]+dx,hip[1]],'joelho':[(hip[0]+pe[0])/2+12,(hip[1]+pe[1])/2],'tornozelo':[pe[0]-5,pe[1]-14],'ponta_pe':list(pe),'natureza':'Estimativa visual aproximada. Joelho e quadril ocultos pela calça; ponto do pé estimado na prancha, incerteza ±8px. Não detecção automática.'}
        rast.append({'quadro':n,'centro_quadril':list(hip),'juntas':juntas,'apoio_previsto':'esquerda' if n<=4 else 'direita','apoio_observado_confiavel':False})
    (p/c/'rastreamento.json').write_text(json.dumps({'direcao':'nordeste','personagem':c,'metodo':'anotação visual da prancha; articulações ocultas inferidas','quadros':rast},indent=2,ensure_ascii=False))
    pend=['Recuo do apoio inconsistente e identidade anatômica ambígua entre fases; calibração de chão não validada.','Passagem07 mantém calcanhar atrás e pouca projeção anterior do joelho; lembra recepção06.','Comprimento aparente de pernas varia; enquadramento usa cabeça/pescoço, não corrige anatomia.','Loop contínuo e chão marcado ainda não aprovados; GIFs100/400ms preparados apenas para revisão.']
    if c=='icaro':pend+=['02 aparenta apoiar perna direita em vez de esquerda.','03 separação anatômica das pernas ambígua.','04 pulseira mudou para braço direito próximo, contrabalanço errado.','06 pulseira aparece perto do cotovelo direito e trajeto do braço distante incoerente.','04→05 muda braço bruscamente;08→01 preserva fase geral mas varia extensão.']
    else:pend+=['04 braço próximo dobra para frente e mão some; não é recuo natural.','05 terceiro candidato reprovado: manga parece nascer na cintura e braços não acompanham pernas;3 tentativas registradas.','06 braço próximo fica oculto em posição incoerente, longe de um recuo natural.','04→05 muda o desenho das mangas;08→01 ainda precisa ajustar apoio.']
    rev={'aprovado':False,'quadros_revisados':list(range(1,9)),'transicoes_revisadas':['04→05','08→01'],'observacoes':['16células da direção exportadas, arte exclusivamente image_gen, sem espelhamento/deformação.','Transparência real, margens e ausência de duplicatas verificadas por script.','Escala uniforme calibrada por marco cabeça/pescoço estimado; conferir novamente após correções.','Primeiro contato copiou pose do recorte; corrigido com base+guia sem recorte de movimento.'],'pendencias':pend,'passada_teste_px_por_quadro':None,'calibracao':{'validada':False,'motivo':'Não é possível ajustar chão com fidelidade enquanto troca de apoio e anatomia estiverem ambíguas.'},'limite_tentativas':{'05':3},'revisao_temporal_concluida':False}
    (p/c/'revisao.json').write_text(json.dumps(rev,indent=2,ensure_ascii=False))
(p/'LEIA-ME.md').write_text('''# Nordeste — pacote para correção

16 PNGs individuais384×512,22 gerações preservadas, prompts integrais, transformações uniformes e rastreamento aproximado. Nenhum ciclo aprovado. Consulte `icaro/revisao.json` e `eva/revisao.json` antes de montar entrega.

As pranchas claro/escuro e GIFs100/400ms são material de revisão. Não comprovam continuidade. Enquadramento só recorta e escala uniformemente com vizinho mais próximo, preservando alfa. Não foi aplicado deslocamento artificial de pés ou deformação.

Diagnóstico: o modelo conserva cabelo/torso razoavelmente, mas confunde braços anatômicos em câmera traseira diagonal e tende a converter passagem em pé recolhido para trás. A correção deve usar guias explícitos de ombro-cotovelo-pulso e trajeto do joelho, sem copiar candidatos reprovados. Eva05 já atingiu3 tentativas; nenhuma repetição adicional sem novo diagnóstico do coordenador.
''')
