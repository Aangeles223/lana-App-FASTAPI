from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models
from schemas import TransaccionCreate, TransaccionOut
import database

router = APIRouter(prefix="/transacciones", tags=["Transacciones"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=TransaccionOut)
def crear_transaccion(transaccion: TransaccionCreate, db: Session = Depends(get_db)):
    nueva_transaccion = models.Transacciones(**transaccion.dict())
    db.add(nueva_transaccion)
    db.commit()
    db.refresh(nueva_transaccion)
    return nueva_transaccion

@router.get("/", response_model=list[TransaccionOut])
def listar_transacciones(db: Session = Depends(get_db)):
    return db.query(models.Transacciones).all()

@router.put("/{transaccion_id}", response_model=TransaccionOut)
def actualizar_transaccion(transaccion_id: int, transaccion: TransaccionCreate, db: Session = Depends(get_db)):
    db_transaccion = db.query(models.Transacciones).filter(models.Transacciones.id == transaccion_id).first()
    if not db_transaccion:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")
    for key, value in transaccion.dict().items():
        setattr(db_transaccion, key, value)
    db.commit()
    db.refresh(db_transaccion)
    return db_transaccion

@router.delete("/{transaccion_id}", response_model=dict)
def eliminar_transaccion(transaccion_id: int, db: Session = Depends(get_db)):
    db_transaccion = db.query(models.Transacciones).filter(models.Transacciones.id == transaccion_id).first()
    if not db_transaccion:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")
    db.delete(db_transaccion)
    db.commit()
    return {"detail": "Transacción eliminada correctamente"}