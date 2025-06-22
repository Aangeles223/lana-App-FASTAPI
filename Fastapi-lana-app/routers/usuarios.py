from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models
from schemas import UsuarioCreate, UsuarioOut
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

@router.delete("/{usuario_id}", response_model=dict)
def eliminar_usuario(usuario_id: int, db: Session = Depends(get_db)):
    db_usuario = db.query(models.Usuarios).filter(models.Usuarios.id == usuario_id).first()
    if not db_usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    db.delete(db_usuario)
    db.commit()
    return {"detail": "Usuario eliminado correctamente"}