from pydantic import BaseModel, EmailStr, validator, Field
from typing import Optional
from datetime import datetime, date
from enum import Enum as PyEnum
from enum import Enum
import re

# usuaruio.py
class UsuarioBase(BaseModel):
    nombre: str = Field(..., example="Juan", description="Nombre del usuario")
    apellidos: str = Field(..., example="Pérez", description="Apellidos del usuario")
    email: EmailStr = Field(..., example="juan@example.com", description="Correo electrónico")

class UsuarioUpdate(UsuarioBase):
    telefono: str = Field(..., example="5551234567", description="Teléfono de contacto")

class UsuarioCreate(UsuarioBase):
    contraseña: str = Field(..., example="MiContraseña123", description="Contraseña segura")
    telefono: str = Field(..., example="5551234567", description="Teléfono de contacto")

    @validator('contraseña')
    def password_strong(cls, v):
        if len(v) < 8:
            raise ValueError('La contraseña debe tener al menos 8 caracteres')
        if not re.search(r'[A-Z]', v):
            raise ValueError('La contraseña debe tener al menos una letra mayúscula')
        if not re.search(r'[a-z]', v):
            raise ValueError('La contraseña debe tener al menos una letra minúscula')
        if not re.search(r'[0-9]', v):
            raise ValueError('La contraseña debe tener al menos un número')
        if not re.search(r'[\W_]', v):
            raise ValueError('La contraseña debe tener al menos un caracter especial')
        return v

    @validator('telefono')
    def telefono_valido(cls, v):
        if v is not None:
            if not re.fullmatch(r'\d{10}', v):
                raise ValueError('El teléfono debe tener exactamente 10 dígitos numéricos')
        return v

class UsuarioOut(UsuarioBase):
    id: int
    telefono: Optional[str] = None
    fecha_creacion: Optional[datetime] = None

    class Config:
        orm_mode = True
# usuaruio.py

# categoria.py
class TipoCategoriaEnum(str, Enum):
    ingreso = "ingreso"
    egreso = "egreso"
    ambos = "ambos"

class CategoriaBase(BaseModel):
    nombre: str
    tipo: TipoCategoriaEnum  # Solo acepta 'ingreso', 'egreso' o 'ambos'

class CategoriaCreate(CategoriaBase):
    pass

class CategoriaOut(CategoriaBase):
    id: int

    class Config:
        orm_mode = True
# categoria.py

# notificacion.py
class MedioNotificacionEnum(str, Enum):
    email = "email"
    sms = "sms"

class TipoNotificacionEnum(str, Enum):
    exceso_presupuesto = "exceso_presupuesto"
    alerta_pago = "alerta_pago"
    recordatorio = "recordatorio"
    pago_pendiente = "pago_pendiente"
    nuevo_ingreso = "nuevo_ingreso"
    pago_registrado = "pago_registrado"

class NotificacionBase(BaseModel):
    usuario_id: int
    mensaje: str
    medio: MedioNotificacionEnum
    tipo: TipoNotificacionEnum

class NotificacionCreate(BaseModel):
    usuario_id: int
    mensaje: str
    medio: str
    tipo: TipoNotificacionEnum

class NotificacionOut(NotificacionBase):
    id: int
    leido: int
    fecha_envio: Optional[datetime] = None

    class Config:
        orm_mode = True
# notificacion.py

# servicio.py
class ServicioBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None

class ServicioCreate(ServicioBase):
    pass

class ServicioOut(ServicioBase):
    id: int

    class Config:
        orm_mode = True
# servicio.py

#transaccion.py
class TipoTransaccionEnum(str, Enum):
    ingreso = "ingreso"
    egreso = "egreso"

class TransaccionBase(BaseModel):
    usuario_id: int
    tipo: TipoTransaccionEnum
    categoria_id: int
    monto: float
    fecha: date
    descripcion: Optional[str] = None

class TransaccionCreate(TransaccionBase):
    pass

class TransaccionOut(TransaccionBase):
    id: int
    creado_en: datetime

    class Config:
        orm_mode = True
# transaccion.py

# pago_fijo.py
class PagoFijoBase(BaseModel):
    usuario_id: int
    servicio_id: int
    nombre: str
    monto: float
    categoria_id: int
    dia_pago: int
    activo: int = 1
    pagado: int = 0
    ultima_fecha: Optional[date] = None

class PagoFijoCreate(PagoFijoBase):
    pass

class PagoFijoOut(PagoFijoBase):
    id: int

    class Config:
        orm_mode = True
# pago_fijo.py

#presupuesto.py
class PresupuestoBase(BaseModel):
    usuario_id: int
    categoria_id: int
    monto_mensual: float
    mes: int
    anio: int

class PresupuestoCreate(PresupuestoBase):
    pass

class PresupuestoOut(PresupuestoBase):
    id: int

    class Config:
        orm_mode = True
# presupuesto.py

# registro_automatico.py
class OrigenRegistroEnum(str, PyEnum):
    pago_fijo = "pago_fijo"
    sistema = "sistema"

class RegistroAutomaticoBase(BaseModel):
    transaccion_id: int
    origen: OrigenRegistroEnum

class RegistroAutomaticoCreate(RegistroAutomaticoBase):
    pass

class RegistroAutomaticoOut(RegistroAutomaticoBase):
    id: int
    fecha_generada: datetime

    class Config:
        orm_mode = True
# registro_automatico.py

# autenticacion.py
class UsuarioLogin(BaseModel):
    email: str
    contraseña: str
# autenticacion.py

#graficos.py
class ResumenCategoria(BaseModel):
    categoria_id: int
    categoria_nombre: str
    total: float
# graficos.py

#contrasena.py
class CambiarContrasena(BaseModel):
    contrasena_actual: str
    contrasena_nueva: str
# contrasena.py