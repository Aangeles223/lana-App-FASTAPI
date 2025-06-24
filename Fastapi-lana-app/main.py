from fastapi import FastAPI, Request, status
from routers import usuarios
import models
import database
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

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

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Error en el formato del JSON enviado. Verifica los campos y el formato."}
    )