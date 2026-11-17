# Gera NF-e de EXEMPLO (dados inventados) para teste do simulador.
itens1=[('ARROZ BRANCO TIPO 1 5KG','10063021',2500.00,0.07),('LEITE UHT INTEGRAL 1L','04012010',1800.00,0.07),
        ('SABONETE BARRA 90G','34011190',600.00,0.18),('CERVEJA LATA 350ML','22030000',1200.00,0.25),
        ('PARAFUSO SEXTAVADO ZINCADO','73181500',350.00,0.18)]
itens2=[('NOTEBOOK 15 POL 8GB','84713012',4200.00,0.12),('CAMISETA ALGODAO ADULTO','61091000',890.00,0.18),
        ('CIMENTO COMUM SACO 50KG','25232910',1450.00,0.12),('DIPIRONA 500MG CX 10 COMP','30049099',320.00,0.18)]
def nfe(n,itens,frete=0):
    det=''
    for i,(x,ncm,v,ai) in enumerate(itens,1):
        fr=round(frete/len(itens),2); bc=v+fr
        det+=f'''<det nItem="{i}"><prod><cProd>EX{n}{i:02d}</cProd><xProd>{x}</xProd><NCM>{ncm}</NCM><CFOP>5102</CFOP><uCom>UN</uCom><qCom>1</qCom><vProd>{v:.2f}</vProd>{f"<vFrete>{fr:.2f}</vFrete>" if fr else ""}</prod>
<imposto><ICMS><ICMS00><orig>0</orig><CST>00</CST><vBC>{bc:.2f}</vBC><pICMS>{ai*100:.2f}</pICMS><vICMS>{bc*ai:.2f}</vICMS></ICMS00></ICMS>
<PIS><PISAliq><CST>01</CST><vBC>{bc:.2f}</vBC><pPIS>1.65</pPIS><vPIS>{bc*0.0165:.2f}</vPIS></PISAliq></PIS>
<COFINS><COFINSAliq><CST>01</CST><vBC>{bc:.2f}</vBC><pCOFINS>7.60</pCOFINS><vCOFINS>{bc*0.076:.2f}</vCOFINS></COFINSAliq></COFINS></imposto></det>
'''
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<nfeProc xmlns="http://www.portalfiscal.inf.br/nfe" versao="4.00"><NFe><infNFe Id="NFe-EXEMPLO-{n}" versao="4.00">
<ide><cUF>35</cUF><natOp>VENDA (EXEMPLO FICTICIO)</natOp><mod>55</mod><serie>1</serie><nNF>{n}</nNF><dhEmi>2026-11-10T10:00:00-03:00</dhEmi><tpNF>1</tpNF><cMunFG>3550308</cMunFG></ide>
<emit><CNPJ>00000000000000</CNPJ><xNome>EMPRESA EXEMPLO LTDA (FICTICIA)</xNome><enderEmit><UF>SP</UF></enderEmit></emit>
{det}</infNFe></NFe></nfeProc>'''
open('exemplo-nfe-1001.xml','w',encoding='utf-8').write(nfe(1001,itens1,frete=60))
open('exemplo-nfe-1002.xml','w',encoding='utf-8').write(nfe(1002,itens2))
print('ok')
