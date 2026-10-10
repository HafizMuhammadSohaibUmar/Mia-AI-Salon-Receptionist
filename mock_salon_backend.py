"""
Mock backend for the Retell salon agent. Lets you test the whole call flow
(availability -> booking -> deposit SMS -> reschedule/cancel) before wiring
a real booking system. Replace each function body with real calls later
(Phorest / Fresha / Google Calendar / Stripe) - the request/response shapes stay the same.

Run:   pip install fastapi uvicorn
       uvicorn mock_salon_backend:app --port 8000
Expose publicly for Retell (it must reach your URL):  ngrok http 8000   (or cloudflared)
Then edit the three tool URLs in Retell to use https://<your-tunnel>/retell.
"""
import os
from datetime import date
from fastapi import FastAPI, Request

app = FastAPI()
BOOKINGS = {}
API_KEY = os.environ.get("SALON_API_KEY", "")   # set this on the server; add the same value as an X-Api-Key header on each Retell tool

@app.middleware("http")
async def require_key(request: Request, call_next):
    if API_KEY and request.url.path.startswith("/retell") and request.headers.get("x-api-key") != API_KEY:
        from fastapi.responses import JSONResponse
        return JSONResponse({"error": "unauthorized"}, status_code=401)
    return await call_next(request)

@app.get("/health")
async def health():
    return {"ok": True}

def args_of(payload: dict) -> dict:
    # Retell sends {"name":..., "args": {...}, "call": {...}} by default
    return payload.get("args", payload)

@app.post("/retell/check-availability")
async def check_availability(req: Request):
    a = args_of(await req.json())
    try:
        d = date.fromisoformat(a["preferred_date"])
    except Exception:
        return {"slots_found": "false", "slot_options": ""}
    if d.weekday() == 6:  # Sunday = closed -> exercises the "no availability" path
        return {"slots_found": "false", "slot_options": ""}
    t = (a.get("preferred_time") or "").lower()
    if "morning" in t:
        times = ["9:30am", "10:30am", "11:30am"]
    elif "after" in t or "afternoon" in t or "evening" in t:
        times = ["2:00pm", "3:30pm", "5:00pm"]
    else:
        times = ["10:00am", "1:30pm", "4:00pm"]
    opts = [f"{d.strftime('%A %d %B')} at {x}" for x in times]
    return {"slots_found": "true", "slot_options": "; ".join(opts)}

@app.post("/retell/book")
async def book(req: Request):
    a = args_of(await req.json())
    bid = f"BK{len(BOOKINGS)+1:04d}"
    BOOKINGS[bid] = a
    needs_deposit = "colour" in (a.get("service", "").lower()) or "highlight" in a.get("service", "").lower()
    return {
        "booking_status": "confirmed",
        "booking_id": bid,
        "confirmed_slot": a.get("slot", ""),
        "deposit_required": "true" if needs_deposit else "false",
        "deposit_link": f"https://pay.example.com/{bid}" if needs_deposit else "",
    }

@app.post("/retell/update-booking")
async def update_booking(req: Request):
    a = args_of(await req.json())
    if a.get("action") == "cancel":
        return {"update_status": "done", "update_detail": "Your appointment has been cancelled."}
    return {"update_status": "done",
            "update_detail": f"Your appointment has been moved to {a.get('new_preferred_date','the new date')}."}
