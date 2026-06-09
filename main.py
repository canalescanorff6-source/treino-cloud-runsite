# -*- coding: utf-8 -*-
"""Treino Pro Max v4 - Nuvem pessoal para RunSite/FastAPI.
Use esta API para backup e sincronização do app Android.
"""
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
from datetime import datetime
import json
import os

TOKEN = os.getenv("TREINO_CLOUD_TOKEN", "troque-este-token")
DATA_DIR = Path(os.getenv("TREINO_CLOUD_DATA", "cloud_backups"))
DATA_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Treino Pro Max Personal Cloud", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class BackupPayload(BaseModel):
    user_email: str
    backup: dict


def safe_name(email: str) -> str:
    return email.replace("@", "_at_").replace("/", "_").replace("\\", "_").strip() or "usuario_local"


def check(auth: str | None):
    if auth != f"Bearer {TOKEN}":
        raise HTTPException(status_code=401, detail="Token inválido")

@app.get("/")
def root():
    return {"ok": True, "message": "Treino Pro Max Personal Cloud online", "docs": "/docs"}

@app.get("/health")
def health():
    return {"ok": True, "app": "Treino Pro Max Personal Cloud"}

@app.post("/sync/upload")
def upload(payload: BackupPayload, authorization: str | None = Header(default=None)):
    check(authorization)
    path = DATA_DIR / f"{safe_name(payload.user_email)}.json"
    content = {
        "updated_at": datetime.utcnow().isoformat(),
        "user_email": payload.user_email,
        "backup": payload.backup,
    }
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
