# Como subir no Render

## Opção mais fácil

Crie um repositório no GitHub e envie os arquivos de dentro desta pasta `backend_render`.
No GitHub, a raiz precisa ficar assim:

```text
main.py
requirements.txt
Procfile
render.yaml
runtime.txt
data/content.json
```

## Configuração no Render

Crie um **Web Service** e use:

Build Command:
```bash
pip install -r requirements.txt
```

Start Command:
```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

Environment Variables:
```env
TREINO_API_TOKEN=treino-pro-max-online-2026
TREINO_ADMIN_TOKEN=admin-treino-pro-max-2026
TREINO_DATA_DIR=data
```

## Testes

Depois que publicar, abra:

```text
https://SEU-APP.onrender.com/health
```

Painel admin:

```text
https://SEU-APP.onrender.com/admin?token=admin-treino-pro-max-2026
```

## Onde muda o treino

Você não precisa mexer no GitHub para mudar treino. Use o painel admin.
Só mexe no GitHub se for mudar código.
