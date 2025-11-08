import os, requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=[os.getenv("CORS_ALLOW_ORIGIN","*")],
                   allow_methods=["*"], allow_headers=["*"])

RESEND_API_KEY = os.getenv("RESEND_API_KEY")
EMAIL_FROM = os.getenv("EMAIL_FROM", "onboarding@resend.dev")

class Mail(BaseModel):
    to: EmailStr
    subject: str
    text: str

@app.get("/health")
def health(): return {"ok": True}

@app.post("/email")
def send_email(m: Mail):
    r = requests.post("https://api.resend.com/emails",
        headers={"Authorization": f"Bearer {RESEND_API_KEY}",
                 "Content-Type": "application/json"},
        json={"from": EMAIL_FROM, "to": m.to, "subject": m.subject, "text": m.text})
    return {"status": r.status_code, "ok": r.ok}
