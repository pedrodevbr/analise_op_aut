# Automação da Emissão de Requisições

Aplicação para automatizar a pré-análise de reposição de materiais de estoque, auxiliando analistas na tomada de decisão.

## Funcionalidades

- **Carregamento de Dados**: Leitura e processamento de planilhas de diferentes fontes
- **Análise Automática**: Cálculos e classificação de consumo
- **Pesquisa de Mercado**: Integração com LLM (Claude) para verificar referências e preços
- **Validação de Textos**: Comparação de textos em português e espanhol
- **Exportação de Relatórios**: Geração de relatórios completos de análise
- **Templates**: Geração de templates para comunicação (cotação, material fracassado)

## Requisitos

- Python 3.8+
- Flask
- Pandas
- OpenPyXL
- Anthropic API (para integração com Claude)

## Instalação

1. Clone o repositório:
   ```
   git clone <url-do-repositorio>
   cd automacao-requisicoes
   ```

2. Crie e ative um ambiente virtual:
   ```
   python -m venv venv
   source venv/bin/activate  # No Windows: venv\Scripts\activate
   ```

3. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```

4. Configure as variáveis de ambiente (opcional):
   - Crie um arquivo `.env` na raiz do projeto
   - Adicione sua chave da API Anthropic:
     ```
     ANTHROPIC_API_KEY=sk-ant-api-key
     ```

## Uso

1. Inicie a aplicação:
   ```
   python run.py
   ```

2. Acesse a aplicação no navegador:
   ```
   http://localhost:5000
   ```

3. Carregue os arquivos XLSX necessários:
   - ZMMORDENSPLA (Ordens Planejadas)
   - 0053 (Informações Gerais)
   - 0130 (Consumo)
   - 0127 (Textos)
   - 0028 (Reservas)
   - MB51 (Movimentação)

4. Analise os materiais individualmente:
   - Gere sugestões automáticas
   - Realize pesquisa de mercado
   - Valide textos
   - Salve decisões
   - Exporte relatórios

## Estrutura do Projeto

```
automacao-requisicoes/
│
├── app.py                    # Arquivo principal da aplicação Flask
├── config.py                 # Configurações da aplicação
├── requirements.txt          # Dependências do projeto
├── run.py                    # Script para iniciar a aplicação
│
├── static/                   # Arquivos estáticos (CSS, JS, imagens)
│   ├── css/
│   │   └── styles.css
│   ├── js/
│   │   ├── main.js          # Script principal
│   │   ├── analytics.js     # Script para cálculos e análises
│   │   └── exportar.js      # Script para exportação de relatórios 
│   └── img/
│
├── templates/                # Templates HTML
│   ├── index.html           # Página principal
│   ├── analise.html         # Página de análise de material
│   └── relatorio.html       # Página de relatório
│
├── uploads/                  # Diretório para arquivos carregados
│
├── exports/                  # Diretório para relatórios exportados
│
└── utils/                    # Utilitários e funções auxiliares
    ├── __init__.py
    ├── data_processor.py    # Processamento de dados
    ├── calc.py              # Cálculos específicos
    ├── llm_api.py           # Integração com LLM (Claude)
    └── export.py            # Exportação de relatórios
```

## Fluxo de Trabalho

1. **Carregamento de Dados**:
   - Leitura de planilhas XLSX
   - Limpeza e conversão de tipos de dados
   - Concatenação de tabelas

2. **Análise Automática**:
   - Cálculo de TMD (Tempo Médio entre Demanda)
   - Cálculo de Coeficiente de Variação
   - Classificação de consumo (Suave, Errático, Intermitente, Esporádico)

3. **Pesquisa de Mercado**:
   - Verificação de referências
   - Validação de preços estimados
   - Busca de alternativas

4. **Tomada de Decisão**:
   - Sugestões automáticas
   - Decisão do analista (Repor, Não Repor, Aguardar)
   - Registro de observações

5. **Exportação de Resultados**:
   - Geração de relatório completo
   - Templates de comunicação

## Licença

Este projeto é para uso interno e não possui licença para distribuição.

## Contato

Para mais informações, entre em contato com o desenvolvedor ou com a equipe de manutenção.