from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models
from schemas import PagoFijoCreate, PagoFijoOut
import database

router = APIRouter(prefix="/pagos_fijos", tags=["Pagos Fijos"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=PagoFijoOut)
def crear_pago_fijo(pago: PagoFijoCreate, db: Session = Depends(get_db)):
    nuevo_pago = models.PagosFijos(**pago.dict())
    db.add(nuevo_pago)
    db.commit()
    db.refresh(nuevo_pago)
    return nuevo_pago

@router.get("/", response_model=list[PagoFijoOut])
def listar_pagos_fijos(db: Session = Depends(get_db)):
    return db.query(models.PagosFijos).all()

@router.put("/{pago_id}", response_model=PagoFijoOut)
def actualizar_pago_fijo(pago_id: int, pago: PagoFijoCreate, db: Session = Depends(get_db)):
    db_pago = db.query(models.PagosFijos).filter(models.PagosFijos.id == pago_id).first()
    if not db_pago:
        raise HTTPException(status_code=404, detail="Pago fijo no encontrado")
    for key, value in pago.dict().items():
        setattr(db_pago, key, value)
    db.commit()
    db.refresh(db_pago)
    return db_pago

@router.delete("/{pago_id}", response_model=dict)
def eliminar_pago_fijo(pago_id: int, db: Session = Depends(get_db)):
    db_pago = db.query(models.PagosFijos).filter(models.PagosFijos.id == pago_id).first()
    if not db_pago:
        raise HTTPException(status_code=404, detail="Pago fijo no encontrado")
    db.delete(db_pago)
    db.commit()
    return {"detail": "Pago fijo eliminado correctamente"}