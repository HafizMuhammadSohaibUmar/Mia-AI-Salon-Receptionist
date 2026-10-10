# Mia AI Salon Receptionist

Mia is a Retell voice receptionist for salons and aesthetic clinics. This project includes an importable conversation-flow export and a FastAPI mock booking backend for demonstrations.

## Conversation flow

- Collects the service, stylist preference, date, name, and confirmed phone number.
- Checks availability, offers returned slots, and confirms booking details.
- Routes deposit bookings through a Retell SMS node, with a failure fallback.
- Handles reschedule and cancellation requests, salon questions, callback details, and human transfer.
- Includes post-call analysis fields for outcome, service, appointment, deposit SMS, caller type, and sentiment.

The prompts disclose that Mia is an AI receptionist and instruct her to avoid collecting card details or giving medical advice.

## Run the mock backend

Requires Python 3.10 or later. From this directory:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:SALON_API_KEY = "your-random-secret"
python -m uvicorn mock_salon_backend:app --host 0.0.0.0 --port 8000
```

`GET /health` returns `{"ok": true}`. The `.env.example` file documents configuration; the app reads process environment variables and does not automatically load `.env` files. If `SALON_API_KEY` is unset, the mock endpoints accept unauthenticated requests.

## Configure Retell

1. Import `Retell Salon Receptionist (Mia) v1.json` into Retell.
2. Expose the backend through an HTTPS tunnel or host it at an HTTPS URL.
3. Replace the placeholder URL in each of the three custom tools with your backend URL, keeping its `/retell/...` path.
4. Replace each `X-Api-Key` placeholder with the same value as `SALON_API_KEY`. Keep credentials out of committed exports.
5. Ensure tools send JSON with arguments under `args`, matching the request example below. Check the imported request configuration in Retell before testing.
6. Customize the salon name, hours, services, cancellation policy, deposit amount, and transfer number in the default dynamic variables. The supplied transfer number is a placeholder.
7. Configure a Retell phone number and SMS capability for live calls, deposit texts, and transfers. Test these separately from the mock backend.

## Backend contract

All three endpoints accept POST requests with JSON and an `X-Api-Key` header when authentication is enabled. Both a Retell envelope and arguments at the JSON root are accepted.

```json
{
  "name": "check_availability",
  "args": {
    "service": "women's cut",
    "preferred_date": "2026-10-12",
    "preferred_time": "morning"
  }
}
```

| Endpoint | Behavior |
| --- | --- |
| `/retell/check-availability` | Returns three simulated slots; Sundays and invalid dates return no availability. |
| `/retell/book` | Stores a booking in memory and returns a reference. Colour and highlight services return a placeholder deposit link. |
| `/retell/update-booking` | Returns a simulated cancellation or reschedule confirmation. |

Response flags such as `slots_found` and `deposit_required` are strings (`"true"` / `"false"`) to match the flow's conditions.

## Demo limitations

This is a conversation prototype, not a production booking integration. Availability is synthetic, bookings disappear on restart, slots are not reserved, and updates do not look up or modify stored bookings. Deposit links use `pay.example.com` and cannot collect payments. Callback details are collected in the conversation but have no dedicated persistence or notification endpoint.

Before using real appointments, connect a booking provider, implement validated booking updates and persistent storage, generate real payment links, and wire callback notifications to the salon team. Configure and verify SMS delivery and human transfer in Retell.
