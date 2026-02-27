from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from db import engine, get_db, Base
from schemas import IdentifyRequest, IdentifyResponse
from service import reconcile
import models 

# create tables on startup
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Bitespeed Identity Reconciliation")


@app.post("/identify", response_model=IdentifyResponse)
def identify(payload: IdentifyRequest, db: Session = Depends(get_db)):
    if not payload.email and not payload.phoneNumber:
        raise HTTPException(status_code=400, detail="email or phoneNumber required")

    result = reconcile(db, email=payload.email, phone=payload.phoneNumber)

    return {"contact": result}
