from sqlalchemy.orm import declarative_base, mapped_column
from sqlalchemy import Integer, String, TIMESTAMP, func, Enum, Text, TIMESTAMP, ForeignKey, DECIMAL, Date, Column

Base = declarative_base()

class Usuarios(Base):
    __tablename__ = "usuarios"
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre = mapped_column(String(100), nullable=False)
    apellidos = mapped_column(String(100), nullable=False)
    email = mapped_column(String(100), nullable=False, unique=True)
    contrasena = mapped_column(String(255), nullable=False)  # <--- SIN Ñ, SIN PASSWORD
    telefono = mapped_column(String(20), nullable=True)
    fecha_creacion = mapped_column(
        TIMESTAMP, nullable=False, server_default=func.current_timestamp()
    )

class Categorias(Base):
    __tablename__ = "categorias"
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre = mapped_column(String(100), nullable=False, unique=True)
    tipo = mapped_column(Enum('ingreso', 'egreso', 'ambos'), nullable=False)

class Notificaciones(Base):
    __tablename__ = "notificaciones"
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    usuario_id = mapped_column(Integer, ForeignKey("usuarios.id"), nullable=False)
    mensaje = mapped_column(Text, nullable=False)
    medio = mapped_column(Enum('email', 'sms'), nullable=False)
    tipo = Column(
        Enum(
            'exceso_presupuesto',
            'alerta_pago',
            'recordatorio',
            'pago_pendiente',
            'nuevo_ingreso',
            'pago_registrado',
            name="tipo_notificacion"
        ),
        nullable=False
    )
    leido = mapped_column(Integer, nullable=False, default=0, server_default="0")
    fecha_envio = mapped_column(TIMESTAMP, nullable=False, server_default=func.current_timestamp())


class Servicios(Base):
    __tablename__ = "servicios"
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    nombre = mapped_column(String(100), nullable=False)
    descripcion = mapped_column(Text, nullable=True)

class Transacciones(Base):
    __tablename__ = "transacciones"
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    usuario_id = mapped_column(Integer, ForeignKey("usuarios.id"), nullable=False)
    tipo = mapped_column(Enum('ingreso', 'egreso'), nullable=False)
    categoria_id = mapped_column(Integer, ForeignKey("categorias.id"), nullable=False)
    monto = mapped_column(DECIMAL(10, 2), nullable=False)
    fecha = mapped_column(Date, nullable=False)
    descripcion = mapped_column(Text, nullable=True)
    creado_en = mapped_column(TIMESTAMP, nullable=False, server_default=func.current_timestamp())

class PagosFijos(Base):
    __tablename__ = "pagos_fijos"
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    usuario_id = mapped_column(Integer, ForeignKey("usuarios.id"), nullable=False)
    servicio_id = mapped_column(Integer, ForeignKey("servicios.id"), nullable=False)
    nombre = mapped_column(String(100), nullable=False)
    monto = mapped_column(DECIMAL(10, 2), nullable=False)
    categoria_id = mapped_column(Integer, ForeignKey("categorias.id"), nullable=False)
    dia_pago = mapped_column(Integer, nullable=False)
    activo = mapped_column(Integer, nullable=False, default=1)
    pagado = mapped_column(Integer, nullable=False, default=0)
    ultima_fecha = mapped_column(Date, nullable=True)

class Presupuestos(Base):
    __tablename__ = "presupuestos"
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    usuario_id = mapped_column(Integer, ForeignKey("usuarios.id"), nullable=False)
    categoria_id = mapped_column(Integer, ForeignKey("categorias.id"), nullable=False)
    monto_mensual = mapped_column(DECIMAL(10, 2), nullable=False)
    mes = mapped_column(Integer, nullable=False)
    anio = mapped_column(Integer, nullable=False)

class RegistrosAutomaticos(Base):
    __tablename__ = "registros_automaticos"
    id = mapped_column(Integer, primary_key=True, autoincrement=True)
    transaccion_id = mapped_column(Integer, ForeignKey("transacciones.id"), nullable=False)
    origen = mapped_column(Enum('pago_fijo', 'sistema'), nullable=False)
    fecha_generada = mapped_column(TIMESTAMP, nullable=False, server_default=func.current_timestamp())