from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from schemas import UsuarioLogin
import models
from sqlalchemy import func
from auth import crear_token
from schemas import UsuarioCreate, UsuarioOut
from schemas import CambiarContrasena
import database
import bcrypt

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=list[UsuarioOut])
def listar_usuarios(db: Session = Depends(get_db)):
    return db.query(models.Usuarios).all()

@router.get("/{usuario_id}/saldo")
def obtener_saldo(usuario_id: int, db: Session = Depends(get_db)):
    ingresos = db.query(func.sum(models.Transacciones.monto)).filter(
        models.Transacciones.usuario_id == usuario_id,
        models.Transacciones.tipo == "ingreso"
    ).scalar() or 0
    egresos = db.query(func.sum(models.Transacciones.monto)).filter(
        models.Transacciones.usuario_id == usuario_id,
        models.Transacciones.tipo == "egreso"
    ).scalar() or 0
    saldo = float(ingresos) - float(egresos)
    return {"saldo": saldo}

@router.post("/login")
async def login(usuario: UsuarioLogin, db: Session = Depends(get_db)):
    db_usuario = db.query(models.Usuarios).filter(models.Usuarios.email == usuario.email).first()
    if db_usuario and bcrypt.checkpw(usuario.contraseña.encode('utf-8'), db_usuario.contraseña.encode('utf-8')):
        token = crear_token({"sub": db_usuario.email, "usuario_id": db_usuario.id})
        return {
            "message": f"Bienvenido {db_usuario.nombre}, correo y contraseña correctos.",
            "access_token": token,
            "token_type": "bearer"
        }
    raise HTTPException(status_code=401, detail="Correo o contraseña incorrectos.")

@router.post("/", response_model=UsuarioOut)
def crear_usuario(usuario: UsuarioCreate, db: Session = Depends(get_db)):
    db_usuario = db.query(models.Usuarios).filter(models.Usuarios.email == usuario.email).first()
    if db_usuario:
        raise HTTPException(status_code=400, detail="El correo ya está registrado.")
    # Encriptar la contraseña
    hashed_password = bcrypt.hashpw(usuario.contraseña.encode('utf-8'), bcrypt.gensalt())
    nuevo_usuario = models.Usuarios(
        nombre=usuario.nombre,
        apellidos=usuario.apellidos,
        email=usuario.email,
        contraseña=hashed_password.decode('utf-8'),
        telefono=usuario.telefono
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return nuevo_usuario


@router.put("/{usuario_id}", response_model=UsuarioOut)
def actualizar_usuario(usuario_id: int, usuario: UsuarioCreate, db: Session = Depends(get_db)):
    db_usuario = db.query(models.Usuarios).filter(models.Usuarios.id == usuario_id).first()
    if not db_usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    # Encriptar la contraseña si se actualiza
    hashed_password = bcrypt.hashpw(usuario.contraseña.encode('utf-8'), bcrypt.gensalt())
    db_usuario.nombre = usuario.nombre
    db_usuario.apellidos = usuario.apellidos
    db_usuario.email = usuario.email
    db_usuario.contraseña = hashed_password.decode('utf-8')
    db_usuario.telefono = usuario.telefono
    db.commit()
    db.refresh(db_usuario)
    return db_usuario

@router.put("/{usuario_id}/cambiar_contrasena")
def cambiar_contrasena(usuario_id: int, datos: CambiarContrasena, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuarios).filter(models.Usuarios.id == usuario_id).first()
    if not usuario or not bcrypt.checkpw(datos.contrasena_actual.encode('utf-8'), usuario.contraseña.encode('utf-8')):
        raise HTTPException(status_code=401, detail="Contraseña actual incorrecta")
    hashed = bcrypt.hashpw(datos.contrasena_nueva.encode('utf-8'), bcrypt.gensalt())
    usuario.contraseña = hashed.decode('utf-8')
    db.commit()
    return {"detail": "Contraseña actualizada correctamente"}

@router.delete("/{usuario_id}", response_model=dict)
def eliminar_usuario(usuario_id: int, db: Session = Depends(get_db)):
    db_usuario = db.query(models.Usuarios).filter(models.Usuarios.id == usuario_id).first()
    if not db_usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    db.delete(db_usuario)
    db.commit()
    return {"detail": "Usuario eliminado correctamente"}