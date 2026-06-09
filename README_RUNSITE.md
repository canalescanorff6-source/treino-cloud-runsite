# Treino Pro Max v4 - Backend para RunSite

Este pacote é só a nuvem pessoal do app Android. O app Kivy/APK não roda como site.

## Comando de start

```bash
uvicorn main:app --host 0.0.0.0 --port 8080
```

Se o RunSite usar variável PORT, use:

```bash
uvicorn main:app --host 0.0.0.0 --port $PORT
```

## Variáveis de ambiente

- `TREINO_CLOUD_TOKEN`: crie uma senha/token grande. Use o mesmo token dentro do app.
- `TREINO_CLOUD_DATA`: opcional. Padrão: `cloud_backups`.

## Teste

Depois do deploy, abra:

`/health`

Deve retornar:

```json
{"ok": true, "app": "Treino Pro Max Personal Cloud"}
```

## No app Android

Na tela **Nuvem pessoal**, coloque:

- API URL: `https://SEU-LINK-DO-RUNSITE`
- Token: o mesmo valor de `TREINO_CLOUD_TOKEN`

Não coloque `/health` no campo da API URL.
