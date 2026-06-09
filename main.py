# -*- coding: utf-8 -*-
"""Treino Pro Max v4.1 - Backend RunSite.
Nuvem pessoal + conteúdo remoto editável + painel admin simples.
"""
from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
from datetime import datetime
import json
import os

TOKEN = os.getenv("TREINO_CLOUD_TOKEN", "troque-este-token")
DATA_DIR = Path(os.getenv("TREINO_CLOUD_DATA", "cloud_backups"))
CONTENT_FILE = Path(os.getenv("TREINO_CONTENT_FILE", "content_config.json"))
DATA_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Treino Pro Max v4.1 Personal Cloud", version="4.1.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

class BackupPayload(BaseModel):
    user_email: str
    backup: dict

class ContentPayload(BaseModel):
    content: dict

def safe_name(email: str) -> str:
    return email.replace("@", "_at_").replace("/", "_").replace("\\", "_").strip() or "usuario_local"

def check(auth: str | None):
    if auth != f"Bearer {TOKEN}":
        raise HTTPException(status_code=401, detail="Token inválido")

def load_content():
    if not CONTENT_FILE.exists():
        CONTENT_FILE.write_text(json.dumps({"version":"v4.1-empty","settings":{},"workouts":[],"nutrition":{},"videos":{}}, ensure_ascii=False, indent=2), encoding="utf-8")
    return json.loads(CONTENT_FILE.read_text(encoding="utf-8"))

def save_content(data: dict):
    data["updated_at"] = datetime.utcnow().isoformat()
    CONTENT_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return data

@app.get("/")
def root():
    return {"ok": True, "message": "Treino Pro Max v4.1 Personal Cloud online", "docs": "/docs", "admin": "/admin"}

@app.get("/health")
def health():
    return {"ok": True, "app": "Treino Pro Max v4.1 Personal Cloud", "time": datetime.utcnow().isoformat()}

@app.post("/sync/upload")
def upload(payload: BackupPayload, authorization: str | None = Header(default=None)):
    check(authorization)
    path = DATA_DIR / f"{safe_name(payload.user_email)}.json"
    content = {"updated_at": datetime.utcnow().isoformat(), "user_email": payload.user_email, "backup": payload.backup}
    path.write_text(json.dumps(content, ensure_ascii=False, indent=2), encoding="utf-8")
    return {"ok": True, "saved": path.name, "updated_at": content["updated_at"]}

@app.get("/sync/download/{user_email}")
def download(user_email: str, authorization: str | None = Header(default=None)):
    check(authorization)
    path = DATA_DIR / f"{safe_name(user_email)}.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail="Backup não encontrado")
    return json.loads(path.read_text(encoding="utf-8"))

@app.get("/sync/list")
def list_backups(authorization: str | None = Header(default=None)):
    check(authorization)
    return {"ok": True, "backups": [p.name for p in DATA_DIR.glob("*.json")]}

@app.get("/content/config")
def get_content(authorization: str | None = Header(default=None)):
    check(authorization)
    return load_content()

@app.post("/content/config")
def post_content(payload: ContentPayload, authorization: str | None = Header(default=None)):
    check(authorization)
    saved = save_content(payload.content)
    return {"ok": True, "updated_at": saved.get("updated_at"), "version": saved.get("version")}

@app.get("/content/workouts")
def get_workouts(authorization: str | None = Header(default=None)):
    check(authorization)
    return {"ok": True, "workouts": load_content().get("workouts", [])}

@app.get("/content/videos")
def get_videos(authorization: str | None = Header(default=None)):
    check(authorization)
    return {"ok": True, "videos": load_content().get("videos", {})}

@app.get("/admin", response_class=HTMLResponse)
def admin():
    html = """
<!doctype html><html lang='pt-BR'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>
<title>Treino Pro Max v4.1 Admin</title>
<style>body{background:#07101a;color:#eff7ff;font-family:Arial;margin:0;padding:18px} .card{background:#0e1b2a;border:1px solid #16324a;border-radius:18px;padding:18px;max-width:1100px;margin:auto} textarea{width:100%;min-height:520px;background:#07101a;color:#dff;border:1px solid #2a536f;border-radius:12px;padding:12px;font-family:monospace} input{width:100%;background:#07101a;color:#fff;border:1px solid #2a536f;border-radius:10px;padding:12px;margin:8px 0} button{background:#00d2bd;color:#001015;border:0;border-radius:12px;padding:12px 16px;font-weight:bold;margin:6px 6px 6px 0} .muted{color:#9ab}.ok{color:#58ff9a}.bad{color:#ff7979}</style>
</head><body><div class='card'><h1>Treino Pro Max v4.1 — Painel RunSite</h1><p class='muted'>Edite o JSON abaixo para mudar treinos, dicas, vídeos e configurações sem gerar APK novo.</p>
<input id='token' placeholder='Cole o TREINO_CLOUD_TOKEN aqui'>
<button onclick='loadCfg()'>Carregar configuração</button><button onclick='saveCfg()'>Salvar configuração</button><button onclick='health()'>Testar servidor</button>
<p id='status' class='muted'></p><textarea id='cfg'></textarea></div>
<script>
function headers(){return {'Content-Type':'application/json','Authorization':'Bearer '+document.getElementById('token').value.trim()}}
async function loadCfg(){let r=await fetch('/content/config',{headers:headers()}); let t=await r.text(); if(!r.ok){status.innerHTML='<span class=bad>Erro: '+t+'</span>';return} cfg.value=JSON.stringify(JSON.parse(t),null,2); status.innerHTML='<span class=ok>Configuração carregada.</span>'}
async function saveCfg(){let obj=JSON.parse(cfg.value); let r=await fetch('/content/config',{method:'POST',headers:headers(),body:JSON.stringify({content:obj})}); let t=await r.text(); status.innerHTML=r.ok?'<span class=ok>Salvo: '+t+'</span>':'<span class=bad>Erro: '+t+'</span>'}
async function health(){let r=await fetch('/health'); status.innerHTML=await r.text()}
</script></body></html>
"""
    return HTMLResponse(html)
