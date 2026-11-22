# Ferramentas grátis para contadores (Reforma Tributária)

Site: https://ferramentas.seldonsystems.com.br

| Ferramenta | O que faz |
|---|---|
| Analisador de NCM | Confere a planilha de produtos (existe, 8 dígitos, vigente, descrição) e mostra cClassTrib, redução de IBS/CBS e Imposto Seletivo por NCM |
| Simulador de impacto por produto | Lê XMLs de NF-e e compara a carga atual (ICMS, PIS, Cofins, ISS) com a de 2026, 2027–2028 e do regime pleno |

Cada ferramenta é um arquivo HTML único: roda no navegador, sem servidor e sem cadastro; os arquivos do usuário não saem do computador.

## Atualização automática
`.github/workflows/atualizar.yml` roda no dia 2 de cada mês: baixa a tabela NCM, monta a base oficial da Calculadora de Tributos da Receita
Federal, extrai as regras de redução por NCM, remonta as páginas e publica. Se um dado vier fora do esperado, nada é publicado e o site fica
na última versão boa.

Planilha Excel de cClassTrib (`/downloads/planilha-cclasstrib-ibs-cbs.xlsx`): gerada a cada montagem por `scripts/planilha_cclasstrib.py`, com IBS/CBS e Imposto Seletivo em abas separadas. Teste: `python scripts/test_cclasstrib.py` (a base da Receita mistura IBS/CBS e Imposto Seletivo na mesma lista; só IBS/CBS tem percentual de redução).

Local: `python scripts/build.py` (usa `dados/`); `--ncm` baixa a tabela; `--rtc <calculadora-pro.db>` extrai as regras.

## Fontes e licenças
- Regras de redução e de base de cálculo: [Calculadora de Tributos — Regime Regular](https://github.com/ReceitaFederal/calculadora-rtc-regime-regular), Receita Federal, licença MIT.
- Tabela NCM: Classif do Portal Único Siscomex, via [BrasilAPI](https://brasilapi.com.br).
- As ferramentas apontam e simulam; a classificação e a orientação ao cliente são do contador.

Seldon Gestão e Tecnologia Ltda. · contato@seldonsystems.com.br
