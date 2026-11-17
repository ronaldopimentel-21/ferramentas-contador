# Gera reforma-ncm.json a partir do banco oficial da Calculadora RTC (Receita, MIT).
# uso: python extrair_reforma.py <calculadora-pro.db> reforma-ncm.json
import sqlite3,json,sys,datetime
db,saida=sys.argv[1],sys.argv[2]
c=sqlite3.connect(db); hoje=datetime.date.today().isoformat()
vig=lambda ini,fim: (fim is None or fim[:10]>=hoje)   # vigente hoje ou futura (ex.: IS em 2027)
versao=c.execute('select VRBD_VERSAO_BASE_DADO,VRBD_DATA,VRBD_DESCRICAO from VERSAO_BASE_DADO order by VRBD_ID desc limit 1').fetchone()
red={}
for cl,tb,v,ini,fim in c.execute('select PERE_CLTR_ID,PERE_TBTO_ID,PERE_VALOR,PERE_INICIO_VIGENCIA,PERE_FIM_VIGENCIA from PERCENTUAL_REDUCAO'):
    if vig(ini,fim): red.setdefault(cl,{})[{2:'cbs',3:'ibs',4:'ibsMun'}.get(tb,str(tb))]=v
ccl={}
q='''select ct.CLTR_ID,ct.CLTR_CD,ct.CLTR_DESCRICAO,s.SITR_CD,ct.CLTR_INICIO_VIGENCIA,ct.CLTR_FIM_VIGENCIA,
 (select group_concat(t.TBTO_SIGLA) from TRIBUTO_SITUACAO_TRIBUTARIA ts join TRIBUTO t on t.TBTO_ID=ts.TRST_TBTO_ID where ts.TRST_SITR_ID=s.SITR_ID)
 from CLASSIFICACAO_TRIBUTARIA ct left join SITUACAO_TRIBUTARIA s on s.SITR_ID=ct.CLTR_SITR_ID'''
for i,cd,desc,sit,ini,fim,trib in c.execute(q):
    if vig(ini,fim): ccl[i]={'cd':cd,'d':desc,'cst':sit,'red':red.get(i,{}),'is':(trib or '')=='IS','ini':(ini or '')[:10]}
exc={}
for ncm,na,ini,fim in c.execute('select ENCM_NCM_CD,ENCM_NCMA_ID,ENCM_INICIO_VIGENCIA,ENCM_FIM_VIGENCIA from EXCECAO_NCM_APLICAVEL'):
    if vig(ini,fim): exc.setdefault(na,[]).append(ncm)
regras=[]
for na,ncm,cl,anx,item,ini,fim in c.execute('select n.NCMA_ID,n.NCMA_NCM_CD,n.NCMA_CLTR_ID,a.ANXO_NUMERO,a.ANXO_NUMERO_ITEM,n.NCMA_INICIO_VIGENCIA,n.NCMA_FIM_VIGENCIA from NCM_APLICAVEL n left join ANEXO a on a.ANXO_ID=n.NCMA_ANXO_ID'):
    if vig(ini,fim) and cl in ccl:
        r={'p':ncm,'c':ccl[cl]['cd'],'is':ccl[cl]['is'],'ini':max((ini or '')[:10],ccl[cl]['ini']),'a':(f'Anexo {anx}'+(f', item {item}' if item else '')) if anx else ''}
        if na in exc: r['x']=exc[na]
        regras.append(r)
cls={}
for v in ccl.values():
    if not v['is'] and any(r['c']==v['cd'] and not r['is'] for r in regras): cls[v['cd']]={'d':v['d'],'cst':v['cst'],'red':v['red']}
json.dump({'fonte':'Calculadora RTC - Receita Federal (github.com/ReceitaFederal/calculadora-rtc-regime-regular, MIT)',
  'versao':versao[0],'data_versao':versao[1][:10],'extraido_em':hoje,'regras':regras,'cclasstrib':cls},
  open(saida,'w',encoding='utf-8'),ensure_ascii=False,separators=(',',':'))
print(versao, len(regras),'regras', len(cls),'cClassTrib usados')
