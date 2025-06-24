from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models
from sqlalchemy import func
from datetime import date
from schemas import PresupuestoCreate, PresupuestoOut
import database

router = APIRouter(prefix="/presupuestos", tags=["Presupuestos"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=PresupuestoOut)
def crear_presupuesto(presupuesto: PresupuestoCreate, db: Session = Depends(get_db)):
    nuevo_presupuesto = models.Presupuestos(**presupuesto.dict())
    db.add(nuevo_presupuesto)
    db.commit()
    db.refresh(nuevo_presupuesto)
    return nuevo_presupuesto

@router.get("/", response_model=list[PresupuestoOut])
def listar_presupuestos(db: Session = Depends(get_db)):
    return db.query(models.Presupuestos).all()

@router.get("/validar_pago_fijo")
def validar_pago_fijo(usuario_id: int, pago_fijo_id: int, mes: int = None, anio: int = None, db: Session = Depends(get_db)):
    hoy = date.today()
    if mes is None:
        mes = hoy.month
    if anio is None:
        anio = hoy.year

    pago = db.query(models.PagosFijos).filter(
        models.PagosFijos.id == pago_fijo_id,
        models.PagosFijos.usuario_id == usuario_id
    ).first()
    if not pago:
        raise HTTPException(status_code=404, detail="Pago fijo no encontrado")

    presupuesto = db.query(models.Presupuestos).filter(
        models.Presupuestos.usuario_id == usuario_id,
        models.Presupuestos.categoria_id == pago.categoria_id,
        models.Presupuestos.mes == mes,
        models.Presupuestos.anio == anio
    ).first()
    if not presupuesto:
        raise HTTPException(status_code=404, detail="Presupuesto no encontrado para la categoría")

    # Suma de egresos en la categoría en el mes
    total_egresos = db.query(func.sum(models.Transacciones.monto)).filter(
        models.Transacciones.usuario_id == usuario_id,
        models.Transacciones.categoria_id == pago.categoria_id,
        models.Transacciones.tipo == "egreso",
        func.extract('month', models.Transacciones.fecha) == mes,
        func.extract('year', models.Transacciones.fecha) == anio
    ).scalar() or 0

    disponible = float(presupuesto.monto_mensual) - float(total_egresos)
    puede_pagar = disponible >= float(pago.monto)

    return {
        "presupuesto": float(presupuesto.monto_mensual),
        "gastado": float(total_egresos),
        "disponible": disponible,
        "monto_pago_fijo": float(pago.monto),
        "puede_pagar": puede_pagar
    }

@router.put("/{presupuesto_id}", response_model=PresupuestoOut)
def actualizar_presupuesto(presupuesto_id: int, presupuesto: PresupuestoCreate, db: Session = Depends(get_db)):
    db_presupuesto = db.query(models.Presupuestos).filter(models.Presupuestos.id == presupuesto_id).first()
    if not db_presupuesto:
        raise HTTPException(status_code=404, detail="Presupuesto no encontrado")
    for key, value in presupuesto.dict().items():
        setattr(db_presupuesto, key, value)
    db.commit()
    db.refresh(db_presupuesto)
    return db_presupuesto

@router.delete("/{presupuesto_id}", response_model=dict)
def eliminar_presupuesto(presupuesto_id: int, db: Session = Depends(get_db)):
    db_presupuesto = db.query(models.Presupuestos).filter(models.Presupuestos.id == presupuesto_id).first()
    if not db_presupuesto:
        raise HTTPException(status_code=404, detail="Presupuesto no encontrado")
    db.delete(db_presupuesto)
    db.commit()
    return {"detail": "Presupuesto eliminado correctamente"}