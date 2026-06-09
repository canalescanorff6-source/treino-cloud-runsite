# Treino Pro Max v4.1 - Backend RunSite

Suba estes arquivos na raiz do repositório do RunSite.

## Start command

```bash
uvicorn main:app --host 0.0.0.0 --port ${PORT:-8080}
```

## Variáveis

- TREINO_CLOUD_TOKEN: token grande que você também coloca no app.
- TREINO_CLOUD_DATA: cloud_backups
- TREINO_CONTENT_FILE: content_config.json

## Testes

- /health
- /admin
- /docs

## No app

Abra Conteúdo remoto RunSite, coloque a URL do RunSite e o token. Clique em baixar conteúdo.
