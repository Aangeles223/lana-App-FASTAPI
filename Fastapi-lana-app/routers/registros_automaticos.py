from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import models
from schemas import RegistroAutomaticoCreate, RegistroAutomaticoOut
import database

router = APIRouter(prefix="/registros_automaticos", tags=["Registros Automáticos"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=RegistroAutomaticoOut)
def crear_registro_automatico(
    transaccion_id: int = Query(..., description="ID de la transacción"),
    origen: str = Query(..., min_length=3, max_length=20, description="Origen (pago_fijo/sistema)"),
    db: Session = Depends(get_db)
):
    nuevo_registro = models.RegistrosAutomaticos(
        transaccion_id=transaccion_id,
        origen=origen
        # fecha_generada se pone por defecto en la BD
    )
    db.add(nuevo_registro)
    db.commit()
    db.refresh(nuevo_registro)
    return nuevo_registro


@router.get("/", response_model=list[RegistroAutomaticoOut])
def listar_registros_automaticos(db: Session = Depends(get_db)):
    return db.query(models.RegistrosAutomaticos).all()

@router.put("/{registro_id}", response_model=RegistroAutomaticoOut)
def actualizar_registro_automatico(
    registro_id: int,
    transaccion_id: int = Query(..., description="ID de la transacción"),
    origen: str = Query(..., min_length=3, max_length=20, description="Origen (pago_fijo/sistema)"),
    db: Session = Depends(get_db)
):
    db_registro = db.query(models.RegistrosAutomaticos).filter(models.RegistrosAutomaticos.id == registro_id).first()
    if not db_registro:
        raise HTTPException(status_code=404, detail="Registro automático no encontrado")
    db_registro.transaccion_id = transaccion_id
    db_registro.origen = origen
    db.commit()
    db.refresh(db_registro)
    return db_registro

@router.delete("/{registro_id}", response_model=dict)
def eliminar_registro_automatico(registro_id: int, db: Session = Depends(get_db)):
    db_registro = db.query(models.RegistrosAutomaticos).filter(models.RegistrosAutomaticos.id == registro_id).first()
    if not db_registro:
        raise HTTPException(status_code=404, detail="Registro automático no encontrado")
    db.delete(db_registro)
    db.commit()
    return {"detail": "Registro automático eliminado correctamente"}