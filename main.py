# main.py
from fastapi import FastAPI, Request
import httpx
import sqlite3

ACCESS_TOKEN = "APP_USR-6230544144933573-021211-723d98ffe98f56d27b7b442db7032a19-2265986164"  # sandbox

app = FastAPI()

def init_db():
    conn = sqlite3.connect("payments.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id TEXT PRIMARY KEY,
            status TEXT,
            amount REAL,
            payer_email TEXT,
            date_created TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

@app.post("/webhook")
async def webhook(request: Request):
    body = await request.json()
    print("Notificación recibida:", body)

    payment_id = body.get("data", {}).get("id")
    if not payment_id:
        return {"status": "no id"}

    headers = {"Authorization": f"Bearer {ACCESS_TOKEN}"}
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"https://api.mercadopago.com/v1/payments/{payment_id}", headers=headers)
        data = resp.json()

    conn = sqlite3.connect("payments.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO payments (id, status, amount, payer_email, date_created)
        VALUES (?, ?, ?, ?, ?)
    """, (
        str(data["id"]),
        data["status"],
        data["transaction_amount"],
        data["payer"]["email"],
        data["date_created"]
    ))
    conn.commit()
    conn.close()

    return {"status": "saved"}
