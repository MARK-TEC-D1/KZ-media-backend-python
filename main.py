import os, requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
import resend
from fastapi import HTTPException


app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=[os.getenv("CORS_ALLOW_ORIGIN","*")],
                   allow_methods=["*"], allow_headers=["*"])

RESEND_API_KEY = os.getenv("RESEND_API_KEY","re_N9fktzXT_MaNBuDwD6aCnhUboY4nFDvuS")
EMAIL_FROM = os.getenv("EMAIL_FROM", "onboarding@resend.dev")

class Mail(BaseModel):
    to: EmailStr
    subject: str
    text: str

@app.get("/health")
def health(): return {"ok": True}

@app.post("/email")
def send_email(m: Mail):
    api_key = os.getenv("RESEND_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="RESEND_API_KEY no configurada")
    resend.api_key = api_key

    sender = os.getenv("EMAIL_FROM", "onboarding@resend.dev")
    if not (m.text or m.html):
        raise HTTPException(status_code=400, detail="Debes enviar 'text' o 'html'")

    payload = {
        "from": sender,
        "to": [m.to],              # Resend espera lista
        "subject": m.subject,
        **({"html": m.html} if m.html else {"text": m.text}),
    }

    try:
        r = resend.Emails.send(payload)  # devuelve dict con 'id'
        return {"ok": True, "id": r.get("id")}
    except Exception as e:
        # Resend da mensajes útiles en el error
        raise HTTPException(status_code=502, detail=f"Resend error: {e}")