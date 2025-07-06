from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models
from sqlalchemy import func
from schemas import ResumenCategoria
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

@router.get("/resumen", response_model=list[ResumenCategoria])
def resumen_transacciones(
    usuario_id: int,
    tipo: str,
    mes: int,
    anio: int,
    db: Session = Depends(get_db)
):
    resultados = (
        db.query(
            models.Transacciones.categoria_id,
            models.Categorias.nombre.label("categoria_nombre"),
            func.sum(models.Transacciones.monto).label("total")
        )
        .join(models.Categorias, models.Transacciones.categoria_id == models.Categorias.id)
        .filter(
            models.Transacciones.usuario_id == usuario_id,
            models.Transacciones.tipo == tipo,
            func.extract('month', models.Transacciones.fecha) == mes,
            func.extract('year', models.Transacciones.fecha) == anio
        )
        .group_by(models.Transacciones.categoria_id, models.Categorias.nombre)
        .all()
    )
    return [
        ResumenCategoria(
            categoria_id=r.categoria_id,
            categoria_nombre=r.categoria_nombre,
            total=float(r.total)
        ) for r in resultados
    ]

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

@router.get("/grafica/resumen_mensual", response_model=list[dict])
def resumen_mensual(
    usuario_id: int,
    anio: int,
    db: Session = Depends(get_db)
):
    """
    Devuelve el total de ingresos y egresos por mes para un usuario y año.
    """
    resultados = (
        db.query(
            func.extract('month', models.Transacciones.fecha).label("mes"),
            models.Transacciones.tipo,
            func.sum(models.Transacciones.monto).label("total")
        )
        .filter(
            models.Transacciones.usuario_id == usuario_id,
            func.extract('year', models.Transacciones.fecha) == anio
        )
        .group_by("mes", models.Transacciones.tipo)
        .order_by("mes")
        .all()
    )
    return [
        {
            "mes": int(r.mes),
            "tipo": r.tipo,
            "total": float(r.total)
        }
        for r in resultados
    ]