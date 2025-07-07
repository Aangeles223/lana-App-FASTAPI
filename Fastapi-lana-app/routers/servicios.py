from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
import models
from schemas import ServicioCreate, ServicioOut
import database

router = APIRouter(prefix="/servicios", tags=["Servicios"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=ServicioOut)
def crear_servicio(
    nombre: str = Query(..., min_length=2, max_length=100, description="Nombre del servicio"),
    descripcion: str = Query(..., min_length=2, max_length=255, description="Descripción del servicio"),
    db: Session = Depends(get_db)
):
    nuevo_servicio = models.Servicios(
        nombre=nombre,
        descripcion=descripcion
    )
    db.add(nuevo_servicio)
    db.commit()
    db.refresh(nuevo_servicio)
    return nuevo_servicio

@router.get("/", response_model=list[ServicioOut])
def listar_servicios(db: Session = Depends(get_db)):
    return db.query(models.Servicios).all()

@router.put("/{servicio_id}", response_model=ServicioOut)
def actualizar_servicio(
    servicio_id: int,
    nombre: str = Query(..., min_length=2, max_length=100, description="Nombre del servicio"),
    descripcion: str = Query(..., min_length=2, max_length=255, description="Descripción del servicio"),
    db: Session = Depends(get_db)
):
    db_servicio = db.query(models.Servicios).filter(models.Servicios.id == servicio_id).first()
    if not db_servicio:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    db_servicio.nombre = nombre
    db_servicio.descripcion = descripcion
    db.commit()
    db.refresh(db_servicio)
    return db_servicio

@router.delete("/{servicio_id}", response_model=dict)
def eliminar_servicio(servicio_id: int, db: Session = Depends(get_db)):
    db_servicio = db.query(models.Servicios).filter(models.Servicios.id == servicio_id).first()
    if not db_servicio:
        raise HTTPException(status_code=404, detail="Servicio no encontrado")
    db.delete(db_servicio)
    db.commit()
    return {"detail": "Servicio eliminado correctamente"}