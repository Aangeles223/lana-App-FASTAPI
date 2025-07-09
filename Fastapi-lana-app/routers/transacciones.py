from fastapi import APIRouter, Depends, HTTPException, Query
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
def crear_transaccion(
    usuario_id: int = Query(...),
    categoria_id: int = Query(...),
    monto: float = Query(...),
    tipo: str = Query(...),
    fecha: str = Query(...),
    descripcion: str = Query(None),
    db: Session = Depends(get_db)
):
    # Si es egreso, guarda el monto como negativo
    if tipo.lower() == "egreso" and monto > 0:
        monto = -monto
    # Si es ingreso, asegura que el monto sea positivo
    if tipo.lower() == "ingreso" and monto < 0:
        monto = abs(monto)
    nueva_transaccion = models.Transacciones(
        usuario_id=usuario_id,
        categoria_id=categoria_id,
        monto=monto,
        tipo=tipo,
        fecha=fecha,
        descripcion=descripcion
    )
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
def actualizar_transaccion(
    transaccion_id: int,
    usuario_id: int = Query(..., description="ID del usuario"),
    categoria_id: int = Query(..., description="ID de la categoría"),
    monto: float = Query(..., description="Monto de la transacción"),
    tipo: str = Query(..., min_length=3, max_length=10, description="Tipo de transacción (ingreso/egreso)"),
    fecha: str = Query(..., description="Fecha de la transacción (YYYY-MM-DD)"),
    descripcion: str = Query(None, max_length=255, description="Descripción de la transacción"),
    db: Session = Depends(get_db)
):
    db_transaccion = db.query(models.Transacciones).filter(models.Transacciones.id == transaccion_id).first()
    if not db_transaccion:
        raise HTTPException(status_code=404, detail="Transacción no encontrada")
    # Lógica para signo del monto
    if tipo.lower() == "egreso" and monto > 0:
        monto = -monto
    if tipo.lower() == "ingreso" and monto < 0:
        monto = abs(monto)
    db_transaccion.usuario_id = usuario_id
    db_transaccion.categoria_id = categoria_id
    db_transaccion.monto = monto
    db_transaccion.tipo = tipo
    db_transaccion.fecha = fecha
    db_transaccion.descripcion = descripcion
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


@router.get("/historial/{usuario_id}", response_model=list[TransaccionOut])
def historial_transacciones(usuario_id: int, db: Session = Depends(get_db)):
    """
    Devuelve todas las transacciones (movimientos) de un usuario, ordenadas por fecha descendente.
    """
    historial = db.query(models.Transacciones).filter(
        models.Transacciones.usuario_id == usuario_id
    ).order_by(models.Transacciones.fecha.desc()).all()
    return historial