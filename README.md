# Bitespeed Identity Reconciliation

POST `/identify` endpoint that links contacts across multiple purchases using email/phone.
https://bitespeed-submission.harshal.engineer/identify

## Stack
- FastAPI + SQLite + SQLAlchemy + Pydantic

## Run locally

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

## Deploy on Render
https://bitespeed-submission.harshal.engineer/docs

## Endpoint

**POST** `/identify`
**GET** `/health`

```json
// request
{ "email": "foo@bar.com", "phoneNumber": "123456" }

// response
{
  "contact": {
    "primaryContatctId": 1,
    "emails": ["foo@bar.com"],
    "phoneNumbers": ["123456"],
    "secondaryContactIds": []
  }
}
```
