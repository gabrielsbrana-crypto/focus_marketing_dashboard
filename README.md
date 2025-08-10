
# Focus Marketing Dashboard

Dashboard em Streamlit para análise de campanhas da Focus Marketing.

## Rodar localmente
```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy no Streamlit Cloud
1. Suba estes arquivos para um repositório no GitHub (mantenha a estrutura).
2. No Streamlit Cloud, crie um novo app apontando para `app.py` na branch principal.
3. O Cloud instalará automaticamente as dependências do `requirements.txt`.
4. Se precisar, acesse **Manage App → Logs** para ver o status de build.

**Arquivos:**
- `app.py` – aplicação principal
- `focus_marketing_data.csv` – banco de dados fictício (500 campanhas)
- `requirements.txt` – dependências (inclui Plotly)
- `.streamlit/config.toml` – tema (dark + laranja)
