from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DecimalField, DateField, TimeField, SelectField, SubmitField, HiddenField
from wtforms.validators import DataRequired, Email, EqualTo, Length, NumberRange

# Formulario de inicio de sesión
class LoginForm(FlaskForm):
    username = StringField('Nombre de Usuario', validators=[
        DataRequired(message="El nombre de usuario es obligatorio."),
        Length(min=3, max=50, message="El nombre de usuario debe tener entre 3 y 50 caracteres.")
    ])
    password = PasswordField('Contraseña', validators=[
        DataRequired(message="La contraseña es obligatoria.")
    ])
    submit = SubmitField('Iniciar Sesión')

# Formulario de registro de usuario
class RegistroForm(FlaskForm):
    nombre = StringField('Nombre Completo', validators=[
        DataRequired(message="El nombre es obligatorio."),
        Length(min=3, max=100, message="El nombre debe tener entre 3 y 100 caracteres.")
    ])
    correo = StringField('Correo Electrónico', validators=[
        DataRequired(message="El correo electrónico es obligatorio."),
        Email(message="Por favor, ingresa un correo electrónico válido.")
    ])
    username = StringField('Nombre de Usuario', validators=[
        DataRequired(message="El nombre de usuario es obligatorio."),
        Length(min=3, max=50, message="El nombre de usuario debe tener entre 3 y 50 caracteres.")
    ])
    password = PasswordField('Contraseña', validators=[
        DataRequired(message="La contraseña es obligatoria."),
        Length(min=6, max=100, message="La contraseña debe tener al menos 6 caracteres.")
    ])
    confirm_password = PasswordField('Confirmar Contraseña', validators=[
        DataRequired(message="Por favor, confirma tu contraseña."),
        EqualTo('password', message="Las contraseñas no coinciden.")
    ])
    role = SelectField('Rol', choices=[
        ('cliente', 'Cliente'),
        ('administrador', 'Administrador')
    ], validators=[DataRequired(message="Selecciona un rol.")])
    submit = SubmitField('Registrarse')

# Formulario para vuelos
class VueloForm(FlaskForm):
    vuelo_id = StringField('ID del Vuelo', validators=[
        DataRequired(message="El ID del vuelo es obligatorio."),
        Length(min=1, max=10, message="El ID del vuelo debe tener entre 1 y 10 caracteres.")
    ])
    operador = StringField('Operador', validators=[
        DataRequired(message="El operador es obligatorio."),
        Length(max=100, message="El operador debe tener un máximo de 100 caracteres.")
    ])
    matricula = StringField('Matrícula', validators=[
        DataRequired(message="La matrícula es obligatoria."),
        Length(max=50, message="La matrícula debe tener un máximo de 50 caracteres.")
    ])
    precio = DecimalField('Precio', validators=[
        DataRequired(message="El precio es obligatorio."),
        NumberRange(min=0, message="El precio debe ser positivo.")
    ])
    salida = StringField('Ciudad de Salida', validators=[
        DataRequired(message="La ciudad de salida es obligatoria.")
    ])
    llegada = StringField('Ciudad de Llegada', validators=[
        DataRequired(message="La ciudad de llegada es obligatoria.")
    ])
    fecha_salida = DateField('Fecha de Salida', validators=[
        DataRequired(message="La fecha de salida es obligatoria.")
    ])
    hora_salida = TimeField('Hora de Salida', validators=[
        DataRequired(message="La hora de salida es obligatoria.")
    ])
    fecha_llegada = DateField('Fecha de Llegada', validators=[
        DataRequired(message="La fecha de llegada es obligatoria.")
    ])
    hora_llegada = TimeField('Hora de Llegada', validators=[
        DataRequired(message="La hora de llegada es obligatoria.")
    ])
    tipo_vuelo = SelectField('Tipo de Vuelo', choices=[
        ('ida', 'Ida'), 
        ('redondo', 'Redondo'), 
        ('directo', 'Directo'), 
        ('escalas', 'Con Escalas')
    ], validators=[DataRequired(message="Selecciona un tipo de vuelo.")])
    modo_vuelo = SelectField('Modo de Vuelo', choices=[
        ('comercial', 'Comercial'), 
        ('privado', 'Privado'), 
        ('publico', 'Público'), 
        ('ejecutivo', 'Ejecutivo')
    ], validators=[DataRequired(message="Selecciona un modo de vuelo.")])
    submit = SubmitField('Guardar Vuelo')

# Formulario para reservas
class ReservaForm(FlaskForm):
    vuelo_id = HiddenField('ID del Vuelo', validators=[
        DataRequired(message="El ID del vuelo es obligatorio.")
    ])
    submit = SubmitField('Reservar Vuelo')

# Formulario para promociones
class PromocionForm(FlaskForm):
    codigo = StringField('Código de Promoción', validators=[
        DataRequired(message="El código de la promoción es obligatorio."),
        Length(max=50, message="El código debe tener un máximo de 50 caracteres.")
    ])
    descripcion = StringField('Descripción', validators=[
        DataRequired(message="La descripción de la promoción es obligatoria."),
        Length(max=200, message="La descripción debe tener un máximo de 200 caracteres.")
    ])
    descuento = DecimalField('Descuento (%)', validators=[
        DataRequired(message="El descuento es obligatorio."),
        NumberRange(min=0, max=100, message="El descuento debe estar entre 0 y 100.")
    ])
    fecha_inicio = DateField('Fecha de Inicio', validators=[
        DataRequired(message="La fecha de inicio es obligatoria.")
    ])
    fecha_fin = DateField('Fecha de Fin', validators=[
        DataRequired(message="La fecha de fin es obligatoria.")
    ])
    submit = SubmitField('Guardar Promoción')
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DecimalField, DateField, TimeField, SelectField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length

class LoginForm(FlaskForm):
    username = StringField('Nombre de Usuario', validators=[
        DataRequired(), Length(min=3, max=50)
    ])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Iniciar Sesión')

class RegistroForm(FlaskForm):
    nombre = StringField('Nombre Completo', validators=[DataRequired(), Length(min=3, max=100)])
    correo = StringField('Correo Electrónico', validators=[DataRequired(), Email()])
    username = StringField('Nombre de Usuario', validators=[DataRequired(), Length(min=3, max=50)])
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirmar Contraseña', validators=[DataRequired(), EqualTo('password')])
    role = SelectField('Rol', choices=[('cliente', 'Cliente'), ('administrador', 'Administrador')])
    submit = SubmitField('Registrarse')

class VueloForm(FlaskForm):
    vuelo_id = StringField('ID del Vuelo', validators=[DataRequired()])
    operador = StringField('Operador', validators=[DataRequired()])
    matricula = StringField('Matrícula', validators=[DataRequired()])
    precio = DecimalField('Precio', validators=[DataRequired()])
    salida = StringField('Ciudad de Salida', validators=[DataRequired()])
    llegada = StringField('Ciudad de Llegada', validators=[DataRequired()])
    fecha_salida = DateField('Fecha de Salida', validators=[DataRequired()])
    hora_salida = TimeField('Hora de Salida', validators=[DataRequired()])
    fecha_llegada = DateField('Fecha de Llegada', validators=[DataRequired()])
    hora_llegada = TimeField('Hora de Llegada', validators=[DataRequired()])
    tipo_vuelo = SelectField('Tipo de Vuelo', choices=[
        ('ida', 'Ida'), ('redondo', 'Redondo'), ('directo', 'Directo'), ('escalas', 'Con Escalas')
    ])
    modo_vuelo = SelectField('Modo de Vuelo', choices=[
        ('comercial', 'Comercial'), ('privado', 'Privado'), ('ejecutivo', 'Ejecutivo')
    ])
    submit = SubmitField('Guardar Vuelo')
