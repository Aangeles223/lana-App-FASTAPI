from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import models
from schemas import CategoriaCreate, CategoriaOut
import database

router = APIRouter(prefix="/categorias", tags=["Categorias"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=CategoriaOut)
def crear_categoria(categoria: CategoriaCreate, db: Session = Depends(get_db)):
    nueva_categoria = models.Categorias(**categoria.dict())
    db.add(nueva_categoria)
    db.commit()
    db.refresh(nueva_categoria)
    return nueva_categoria

@router.get("/", response_model=list[CategoriaOut])
def listar_categorias(db: Session = Depends(get_db)):
    return db.query(models.Categorias).all()

@router.put("/{categoria_id}", response_model=CategoriaOut)
def actualizar_categoria(categoria_id: int, categoria: CategoriaCreate, db: Session = Depends(get_db)):
    db_categoria = db.query(models.Categorias).filter(models.Categorias.id == categoria_id).first()
    if not db_categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    db_categoria.nombre = categoria.nombre
    db_categoria.tipo = categoria.tipo
    db.commit()
    db.refresh(db_categoria)
    return db_categoria

@router.delete("/{categoria_id}", response_model=dict)
def eliminar_categoria(categoria_id: int, db: Session = Depends(get_db)):
    db_categoria = db.query(models.Categorias).filter(models.Categorias.id == categoria_id).first()
    if not db_categoria:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    db.delete(db_categoria)
    db.commit()
    return {"detail": "Categoría eliminada correctamente"}