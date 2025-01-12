from fastapi import FastAPI, HTTPException, Depends
from typing import Annotated
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import SessionLocal, engine
import models
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()


origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class TransactionsBase(BaseModel):
    amount: float
    category: str
    description: str
    is_income: bool
    date: str

class TransactionsModels(TransactionsBase):
    id: int

    class Config:
        from_attributes = True



def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
    

db_dependency = Annotated[Session,Depends(get_db)]

models.Base.metadata.create_all(bind=engine)


@app.post("/transactions/", response_model=TransactionsModels)
async def create_transactions(transactions: TransactionsBase, db: db_dependency):
    try:
        db_transactions = models.Transactions(**transactions.model_dump())
        db.add(db_transactions)
        db.commit()
        db.refresh(db_transactions)
        return db_transactions
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/transactions/", response_model=list[TransactionsModels])
async def read_transactions(db: db_dependency,skip: int = 0, limit: int = 100):
    transactions = db.query(models.Transactions).offset(skip).limit(limit).all()
    return transactions

