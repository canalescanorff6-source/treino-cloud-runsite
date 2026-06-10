import os
import json
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException, Header, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

APP_NAME = "Treino Pro Max Online API"
APP_VERSION = "5.0-online-final"
DATA_DIR = Path(os.getenv("TREINO_DATA_DIR", "data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)
DB_PATH = DATA_DIR / "treino_online.db"
CONTENT_PATH = DATA_DIR / "content.json"

API_TOKEN = os.getenv("TREINO_API_TOKEN", "treino-pro-max-online-2026")
ADMIN_TOKEN = os.getenv("TREINO_ADMIN_TOKEN", "admin-treino-pro-max-2026")

app = FastAPI(title=APP_NAME, version=APP_VERSION)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def now_iso() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"

def db():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    con = db()
    cur = con.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS profiles (
        device_id TEXT PRIMARY KEY,
        name TEXT,
        age INTEGER,
        weight REAL,
        height REAL,
        goal TEXT,
        level TEXT,
        updated_at TEXT
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS workout_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        device_id TEXT,
        day TEXT,
        exercise TEXT,
        weight REAL,
        reps INTEGER,
        sets INTEGER,
        rpe REAL,
        notes TEXT,
        created_at TEXT
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS measurements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        device_id TEXT,
        body_weight REAL,
        chest REAL,
        arm REAL,
        waist REAL,
        leg REAL,
        notes TEXT,
        created_at TEXT
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS backups (
        device_id TEXT PRIMARY KEY,
        payload TEXT,
        updated_at TEXT
    )
    """)
    con.commit()
    con.close()

def check_token(token: Optional[str], admin: bool = False):
    expected = ADMIN_TOKEN if admin else API_TOKEN
    if not token or token != expected:
        raise HTTPException(status_code=401, detail="Token inválido")

def read_content() -> Dict[str, Any]:
    if CONTENT_PATH.exists():
        return json.loads(CONTENT_PATH.read_text(encoding="utf-8"))
    return {"version": "empty", "weekly_plan": [], "exercise_library": []}

def write_content(payload: Dict[str, Any]):
    payload["updated_at"] = now_iso()
    CONTENT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

@app.on_event("startup")
def startup():
    init_db()
    if not CONTENT_PATH.exists():
        default = Path(__file__).parent / "data" / "content.json"
        if default.exists():
            pass

@app.get("/health")
def health():
    return {"ok": True, "app": APP_NAME, "version": APP_VERSION, "time": now_iso()}

@app.get("/", response_class=HTMLResponse)
def home():
    return f"""
    <!doctype html><html lang="pt-BR"><head><title>Treino Pro Max Online</title>
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <style>
    body{{margin:0;font-family:Arial;background:linear-gradient(135deg,#020617,#0f172a);color:#f8fafc;padding:24px}}
    .card{{max-width:850px;margin:18px auto;background:#111827;border:1px solid #263247;border-radius:22px;padding:22px;box-shadow:0 10px 30px #0008}}
    h1{{font-size:34px;margin:0 0 10px}} a{{color:#38bdf8}} code{{background:#020617;padding:5px 8px;border-radius:8px}}
    .pill{{display:inline-block;background:#064e3b;color:#bbf7d0;padding:6px 10px;border-radius:999px;font-weight:bold}}
    </style></head><body><div class="card">
    <span class="pill">ONLINE</span><h1>Treino Pro Max Online</h1>
    <p>Servidor online para o APK. O app salva perfil, histórico, medidas, progresso e conteúdo pelo Render.</p>
    <p><b>Status:</b> <a href="/health">/health</a> &nbsp; <b>Documentação:</b> <a href="/docs">/docs</a></p>
    <p><b>Painel admin:</b> <code>/admin?token=SUA_SENHA_ADMIN</code></p>
    <p>Versão: {APP_VERSION}</p></div></body></html>
    """

@app.get("/admin", response_class=HTMLResponse)
def admin(token: str = ""):
    check_token(token, admin=True)
    content = json.dumps(read_content(), ensure_ascii=False, indent=2)
    return f"""
    <!doctype html><html lang="pt-BR"><head><title>Admin Treino Pro Max</title>
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <style>
    body{{font-family:Arial;background:#020617;color:#f8fafc;padding:16px;margin:0}}
    .wrap{{max-width:1100px;margin:auto}} .card{{background:#111827;border:1px solid #263247;border-radius:18px;padding:16px;margin:12px 0}}
    textarea{{width:100%;height:62vh;background:#020617;color:#d1fae5;border:1px solid #334155;border-radius:12px;padding:12px;font-family:monospace;font-size:13px;box-sizing:border-box}}
    button{{background:#22c55e;color:#052e16;border:0;border-radius:12px;padding:12px 18px;font-weight:bold;margin:8px 8px 8px 0}}
    input{{width:100%;padding:10px;background:#0f172a;color:white;border:1px solid #334155;border-radius:10px;box-sizing:border-box}}
    a{{color:#38bdf8}} pre{{white-space:pre-wrap;color:#e2e8f0}}
    </style></head><body><div class="wrap">
    <h1>Painel Admin - Treino Pro Max</h1>
    <div class="card"><p>Altere treinos, exercícios, dicas e alimentação no JSON abaixo. Depois clique em salvar. O APK baixa esse conteúdo do Render.</p>
    <input id="token" value="{token}" placeholder="Token admin"></div>
    <div class="card"><textarea id="json">{content}</textarea><br>
    <button onclick="save()">Salvar conteúdo</button>
    <button onclick="downloadJson()">Baixar JSON</button>
    <a href="/api/admin/export?token={token}" target="_blank">Exportar dados</a>
    <pre id="out"></pre></div></div>
    <script>
    async function save(){{
      const token=document.getElementById('token').value;
      try{{
        const payload=JSON.parse(document.getElementById('json').value);
        const r=await fetch('/api/content',{{method:'PUT',headers:{{'Content-Type':'application/json','X-Admin-Token':token}},body:JSON.stringify(payload)}});
        document.getElementById('out').textContent=await r.text();
      }}catch(e){{document.getElementById('out').textContent='Erro: '+e;}}
    }}
    function downloadJson(){{
      const blob=new Blob([document.getElementById('json').value],{{type:'application/json'}});
      const a=document.createElement('a'); a.href=URL.createObjectURL(blob); a.download='treino_content.json'; a.click();
    }}
    </script></body></html>
    """

@app.get("/api/content")
def get_content(x_api_token: Optional[str] = Header(None), token: str = ""):
    check_token(x_api_token or token)
    return read_content()

@app.put("/api/content")
async def update_content(request: Request, x_admin_token: Optional[str] = Header(None)):
    check_token(x_admin_token, admin=True)
    payload = await request.json()
    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="JSON precisa ser objeto")
    write_content(payload)
    return {"ok": True, "message": "Conteúdo atualizado", "version": payload.get("version"), "updated_at": payload.get("updated_at")}

class Profile(BaseModel):
    device_id: str
    name: str = ""
    age: Optional[int] = None
    weight: Optional[float] = None
    height: Optional[float] = None
    goal: str = "Hipertrofia e ganho de massa"
    level: str = "Voltando"

@app.post("/api/profile")
def save_profile(p: Profile, x_api_token: Optional[str] = Header(None)):
    check_token(x_api_token)
    con = db()
    con.execute("""
    INSERT INTO profiles(device_id,name,age,weight,height,goal,level,updated_at)
    VALUES(?,?,?,?,?,?,?,?)
    ON CONFLICT(device_id) DO UPDATE SET name=excluded.name, age=excluded.age, weight=excluded.weight,
    height=excluded.height, goal=excluded.goal, level=excluded.level, updated_at=excluded.updated_at
    """, (p.device_id, p.name, p.age, p.weight, p.height, p.goal, p.level, now_iso()))
    con.commit(); con.close()
    return {"ok": True, "message": "Perfil salvo"}

@app.get("/api/profile/{device_id}")
def get_profile(device_id: str, x_api_token: Optional[str] = Header(None)):
    check_token(x_api_token)
    con = db(); row = con.execute("SELECT * FROM profiles WHERE device_id=?", (device_id,)).fetchone(); con.close()
    return dict(row) if row else {}

class WorkoutLog(BaseModel):
    device_id: str
    day: str = ""
    exercise: str
    weight: float = 0
    reps: int = 0
    sets: int = 1
    rpe: float = 8
    notes: str = ""

@app.post("/api/workout-log")
def add_workout_log(w: WorkoutLog, x_api_token: Optional[str] = Header(None)):
    check_token(x_api_token)
    con = db()
    con.execute("""INSERT INTO workout_logs(device_id,day,exercise,weight,reps,sets,rpe,notes,created_at) VALUES(?,?,?,?,?,?,?,?,?)""",
        (w.device_id, w.day, w.exercise, w.weight, w.reps, w.sets, w.rpe, w.notes, now_iso()))
    con.commit(); con.close()
    return {"ok": True, "message": "Treino salvo online"}

@app.get("/api/workout-log/{device_id}")
def list_workout_logs(device_id: str, x_api_token: Optional[str] = Header(None), limit: int = 100):
    check_token(x_api_token)
    con = db(); rows = con.execute("SELECT * FROM workout_logs WHERE device_id=? ORDER BY id DESC LIMIT ?", (device_id, limit)).fetchall(); con.close()
    return [dict(r) for r in rows]

class Measurement(BaseModel):
    device_id: str
    body_weight: float = 0
    chest: float = 0
    arm: float = 0
    waist: float = 0
    leg: float = 0
    notes: str = ""

@app.post("/api/measurement")
def add_measurement(m: Measurement, x_api_token: Optional[str] = Header(None)):
    check_token(x_api_token)
    con = db()
    con.execute("""INSERT INTO measurements(device_id,body_weight,chest,arm,waist,leg,notes,created_at) VALUES(?,?,?,?,?,?,?,?)""",
        (m.device_id, m.body_weight, m.chest, m.arm, m.waist, m.leg, m.notes, now_iso()))
    con.commit(); con.close()
    return {"ok": True, "message": "Medidas salvas"}

@app.get("/api/measurements/{device_id}")
def list_measurements(device_id: str, x_api_token: Optional[str] = Header(None), limit: int = 50):
    check_token(x_api_token)
    con = db(); rows = con.execute("SELECT * FROM measurements WHERE device_id=? ORDER BY id DESC LIMIT ?", (device_id, limit)).fetchall(); con.close()
    return [dict(r) for r in rows]

@app.get("/api/progress/{device_id}")
def get_progress(device_id: str, x_api_token: Optional[str] = Header(None)):
    check_token(x_api_token)
    con = db()
    logs = con.execute("SELECT * FROM workout_logs WHERE device_id=? ORDER BY id DESC LIMIT 50", (device_id,)).fetchall()
    measures = con.execute("SELECT * FROM measurements WHERE device_id=? ORDER BY id DESC LIMIT 10", (device_id,)).fetchall()
    con.close()
    total_sets = sum(int(r["sets"] or 0) for r in logs)
    max_weight = max([float(r["weight"] or 0) for r in logs], default=0)
    advice = "Continue registrando os treinos. "
    if len(logs) >= 3:
        advice += "Boa sequência. Se completou as repetições com técnica limpa, aumente carga aos poucos."
    else:
        advice += "Faça pelo menos 3 registros para uma análise melhor."
    return {"total_recent_logs": len(logs), "total_recent_sets": total_sets, "max_recent_weight": max_weight,
            "last_logs": [dict(r) for r in logs[:10]], "measurements": [dict(r) for r in measures], "analysis": advice}

@app.post("/api/backup/{device_id}")
async def upload_backup(device_id: str, request: Request, x_api_token: Optional[str] = Header(None)):
    check_token(x_api_token)
    payload = await request.json()
    con = db()
    con.execute("""INSERT INTO backups(device_id,payload,updated_at) VALUES(?,?,?) ON CONFLICT(device_id) DO UPDATE SET payload=excluded.payload, updated_at=excluded.updated_at""",
        (device_id, json.dumps(payload, ensure_ascii=False), now_iso()))
    con.commit(); con.close()
    return {"ok": True, "message": "Backup salvo"}

@app.get("/api/backup/{device_id}")
def download_backup(device_id: str, x_api_token: Optional[str] = Header(None)):
    check_token(x_api_token)
    con = db(); row = con.execute("SELECT * FROM backups WHERE device_id=?", (device_id,)).fetchone(); con.close()
    if not row: return {"ok": False, "message": "Sem backup"}
    return {"ok": True, "updated_at": row["updated_at"], "payload": json.loads(row["payload"])}

@app.get("/api/admin/export")
def admin_export(token: str = ""):
    check_token(token, admin=True)
    con = db()
    data = {
        "content": read_content(),
        "profiles": [dict(r) for r in con.execute("SELECT * FROM profiles").fetchall()],
        "workout_logs": [dict(r) for r in con.execute("SELECT * FROM workout_logs ORDER BY id DESC").fetchall()],
        "measurements": [dict(r) for r in con.execute("SELECT * FROM measurements ORDER BY id DESC").fetchall()],
        "exported_at": now_iso(),
    }
    con.close()
    return JSONResponse(data, headers={"Content-Disposition": "attachment; filename=treino_pro_max_backup.json"})
