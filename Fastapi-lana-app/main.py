from fastapi import FastAPI
from routers import usuarios
import models
import database

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()

app.include_router(usuarios.router)

# Importaciones de los routers

# Notificaciones
from routers import notificaciones
app.include_router(notificaciones.router)

# Categorías
from routers import categorias
app.include_router(categorias.router)

# Usuarios
from routers import usuarios
app.include_router(usuarios.router)

# Servicios
from routers import servicios
app.include_router(servicios.router)

# Transacciones
from routers import transacciones
app.include_router(transacciones.router)

# Pagos Fijos
from routers import pagos_fijos
app.include_router(pagos_fijos.router)

# Presupuestos
from routers import presupuesto
app.include_router(presupuesto.router)

# Registros Automáticos
from routers import registros_automaticos   
app.include_router(registros_automaticos.router)