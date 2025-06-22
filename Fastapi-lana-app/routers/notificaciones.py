from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models
from schemas import NotificacionCreate, NotificacionOut
import database

router = APIRouter(prefix="/notificaciones", tags=["Notificaciones"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=NotificacionOut)
def crear_notificacion(notificacion: NotificacionCreate, db: Session = Depends(get_db)):
    nueva_notificacion = models.Notificaciones(**notificacion.dict())
    db.add(nueva_notificacion)
    db.commit()
    db.refresh(nueva_notificacion)
    return nueva_notificacion

@router.get("/", response_model=list[NotificacionOut])
def listar_notificaciones(db: Session = Depends(get_db)):
    return db.query(models.Notificaciones).all()

@router.put("/{notificacion_id}/leer", response_model=NotificacionOut)
def marcar_como_leida(notificacion_id: int, db: Session = Depends(get_db)):
    db_notificacion = db.query(models.Notificaciones).filter(models.Notificaciones.id == notificacion_id).first()
    if not db_notificacion:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")
    db_notificacion.leido = 1
    db.commit()
    db.refresh(db_notificacion)
    return db_notificacion

@router.delete("/{notificacion_id}", response_model=dict)
def eliminar_notificacion(notificacion_id: int, db: Session = Depends(get_db)):
    db_notificacion = db.query(models.Notificaciones).filter(models.Notificaciones.id == notificacion_id).first()
    if not db_notificacion:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")
    db.delete(db_notificacion)
    db.commit()
    return {"detail": "Notificación eliminada correctamente"}