from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models
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