from fastapi import APIRouter, Depends, HTTPException, Query
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

# ----------- POST -----------
@router.post("/", response_model=PagoFijoOut)
def crear_pago_fijo(
    usuario_id: int = Query(..., description="ID del usuario"),
    servicio_id: int = Query(..., description="ID del servicio"),
    nombre: str = Query(..., min_length=2, max_length=100, description="Nombre del pago fijo"),
    monto: float = Query(..., description="Monto del pago fijo"),
    categoria_id: int = Query(..., description="ID de la categoría"),
    dia_pago: int = Query(..., description="Día del mes para el pago"),
    activo: int = Query(1, description="¿Activo? 1=Sí, 0=No"),
    pagado: int = Query(0, description="¿Pagado este mes? 1=Sí, 0=No"),
    ultima_fecha: str = Query(None, description="Última fecha de pago (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    nuevo_pago = models.PagosFijos(
        usuario_id=usuario_id,
        servicio_id=servicio_id,
        nombre=nombre,
        monto=monto,
        categoria_id=categoria_id,
        dia_pago=dia_pago,
        activo=activo,
        pagado=pagado,
        ultima_fecha=ultima_fecha
    )
    db.add(nuevo_pago)
    db.commit()
    db.refresh(nuevo_pago)
    return nuevo_pago

# ----------- GET -----------
@router.get("/", response_model=list[PagoFijoOut])
def listar_pagos_fijos(db: Session = Depends(get_db)):
    return db.query(models.PagosFijos).all()

@router.get("/proximos", response_model=list[PagoFijoOut])
def pagos_fijos_proximos(
    usuario_id: int,
    dias: int = 3,
    db: Session = Depends(get_db)
):
    """
    Devuelve los pagos fijos activos de un usuario cuya próxima fecha de pago
    está dentro de los próximos 'dias' días (por defecto 3) y que no han sido pagados este mes.
    """
    hoy = date.today()
    fecha_limite = hoy + timedelta(days=dias)

    pagos = db.query(models.PagosFijos).filter(
        models.PagosFijos.usuario_id == usuario_id,
        models.PagosFijos.activo == 1,
        models.PagosFijos.pagado == 0
    ).all()

    pagos_proximos = []
    for pago in pagos:
        año = hoy.year
        mes = hoy.month
        if pago.dia_pago < hoy.day:
            mes += 1
            if mes > 12:
                mes = 1
                año += 1
        try:
            proxima_fecha = date(año, mes, pago.dia_pago)
        except ValueError:
            from calendar import monthrange
            ultimo_dia = monthrange(año, mes)[1]
            proxima_fecha = date(año, mes, ultimo_dia)
        if hoy <= proxima_fecha <= fecha_limite:
            pagos_proximos.append(pago)

    return pagos_proximos

@router.get("/pagados", response_model=list[PagoFijoOut])
def pagos_fijos_pagados(
    usuario_id: int,
    db: Session = Depends(get_db)
):
    """
    Devuelve los pagos fijos activos de un usuario que ya han sido pagados este mes.
    """
    pagos = db.query(models.PagosFijos).filter(
        models.PagosFijos.usuario_id == usuario_id,
        models.PagosFijos.activo == 1,
        models.PagosFijos.pagado == 1
    ).all()
    return pagos

@router.get("/vencidos", response_model=list[PagoFijoOut])
def pagos_fijos_vencidos(
    usuario_id: int,
    db: Session = Depends(get_db)
):
    """
    Devuelve los pagos fijos activos de un usuario que ya vencieron este mes y no han sido pagados.
    """
    hoy = date.today()
    pagos = db.query(models.PagosFijos).filter(
        models.PagosFijos.usuario_id == usuario_id,
        models.PagosFijos.activo == 1,
        models.PagosFijos.pagado == 0
    ).all()

    pagos_vencidos = []
    for pago in pagos:
        año = hoy.year
        mes = hoy.month
        try:
            fecha_pago = date(año, mes, pago.dia_pago)
        except ValueError:
            from calendar import monthrange
            ultimo_dia = monthrange(año, mes)[1]
            fecha_pago = date(año, mes, ultimo_dia)
        if fecha_pago < hoy:
            pagos_vencidos.append(pago)

    return pagos_vencidos

# ----------- PUT -----------
@router.put("/{pago_id}", response_model=PagoFijoOut)
def actualizar_pago_fijo(
    pago_id: int,
    usuario_id: int = Query(..., description="ID del usuario"),
    categoria_id: int = Query(..., description="ID de la categoría"),
    monto: float = Query(..., description="Monto del pago fijo"),
    dia_pago: int = Query(..., description="Día del mes para el pago"),
    activo: int = Query(..., description="¿Activo? 1=Sí, 0=No"),
    pagado: int = Query(..., description="¿Pagado este mes? 1=Sí, 0=No"),
    db: Session = Depends(get_db)
):
    db_pago = db.query(models.PagosFijos).filter(models.PagosFijos.id == pago_id).first()
    if not db_pago:
        raise HTTPException(status_code=404, detail="Pago fijo no encontrado")
    db_pago.usuario_id = usuario_id
    db_pago.categoria_id = categoria_id
    db_pago.monto = monto
    db_pago.dia_pago = dia_pago
    db_pago.activo = activo
    db_pago.pagado = pagado
    db.commit()
    db.refresh(db_pago)
    return db_pago

@router.put("/{pago_id}/marcar_pagado", response_model=PagoFijoOut)
def marcar_pago_fijo_como_pagado(pago_id: int, db: Session = Depends(get_db)):
    """
    Marca un pago fijo como pagado (pagado = 1).
    """
    db_pago = db.query(models.PagosFijos).filter(models.PagosFijos.id == pago_id).first()
    if not db_pago:
        raise HTTPException(status_code=404, detail="Pago fijo no encontrado")
    db_pago.pagado = 1
    db.commit()
    db.refresh(db_pago)
    return db_pago

# ----------- DELETE -----------
@router.delete("/{pago_id}", response_model=dict)
def eliminar_pago_fijo(pago_id: int, db: Session = Depends(get_db)):
    db_pago = db.query(models.PagosFijos).filter(models.PagosFijos.id == pago_id).first()
    if not db_pago:
        raise HTTPException(status_code=404, detail="Pago fijo no encontrado")
    db.delete(db_pago)
    db.commit()
    return {"detail": "Pago fijo eliminado exitosamente"}