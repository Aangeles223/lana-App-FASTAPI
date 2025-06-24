from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models
from datetime import datetime, timedelta, date
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

@router.get("/proximos", response_model=list[PagoFijoOut])
def pagos_fijos_proximos(usuario_id: int, dias: int = 3, db: Session = Depends(get_db)):
    hoy = date.today()
    fecha_limite = hoy + timedelta(days=dias)
    pagos = db.query(models.PagosFijos).filter(
        models.PagosFijos.usuario_id == usuario_id,
        models.PagosFijos.activo == 1
    ).all()

    pagos_proximos = []
    for pago in pagos:
        # Calcula la próxima fecha de pago
        año = hoy.year
        mes = hoy.month
        # Si el día de pago ya pasó este mes, calcula para el mes siguiente
        if pago.dia_pago < hoy.day:
            mes += 1
            if mes > 12:
                mes = 1
                año += 1
        try:
            proxima_fecha = date(año, mes, pago.dia_pago)
        except ValueError:
            # Si el mes no tiene ese día (ej: 30 en febrero), usa el último día del mes
            from calendar import monthrange
            ultimo_dia = monthrange(año, mes)[1]
            proxima_fecha = date(año, mes, ultimo_dia)
        # Si la próxima fecha de pago está dentro del rango, agregar a la lista
        if hoy <= proxima_fecha <= fecha_limite:
            pagos_proximos.append(pago)
    return pagos_proximos

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