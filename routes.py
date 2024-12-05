from flask import Blueprint, request, render_template, redirect, url_for, flash, session
from db_connection import get_db_connection  # Conexión a la base de datos
from forms import VueloForm, ReservaForm, LoginForm, RegistroForm
from models import obtener_ticket_por_vuelo_id

app_routes = Blueprint('app_routes', __name__)

# Página de inicio
@app_routes.route('/')
def index():
    return render_template('index.html')

# Ruta para iniciar sesión
@app_routes.route('/iniciar_sesion', methods=['GET', 'POST'])
def iniciar_sesion():
    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM usuario WHERE username = %s", (username,))
        user = cursor.fetchone()

        if user and user[4] == password:
            session['user_id'] = user[0]
            session['username'] = user[1]
            session['role'] = user[5]

            flash('¡Inicio de sesión exitoso!', 'success')

            if user[5] == 'administrador':
                return redirect(url_for('app_routes.admin_dashboard'))
            return redirect(url_for('app_routes.bienvenida_cliente'))
        flash('Nombre de usuario o contraseña incorrectos.', 'danger')

        cursor.close()
        connection.close()

    return render_template('iniciar_sesion.html', form=form)
@app_routes.route('/admin_dashboard', methods=['GET'])
def admin_dashboard():
    if 'user_id' not in session or session.get('role') != 'administrador':
        flash("No tienes permisos para acceder a esta página", "danger")
        return redirect(url_for('app_routes.iniciar_sesion'))

    connection = get_db_connection()
    cursor = connection.cursor()

    # Obtener estadísticas generales
    cursor.execute("SELECT COUNT(*) FROM vueloandm")
    total_vuelos = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM reservas")
    total_reservas = cursor.fetchone()[0]

    cursor.execute("SELECT SUM(p.monto) FROM pagos p WHERE p.estado_pago = 'Pagado'")
    ganancias_totales = cursor.fetchone()[0] or 0

    # Obtener los vuelos registrados
    cursor.execute("SELECT vuelo_id, operador FROM vueloandm")
    vuelos = cursor.fetchall()

    cursor.close()
    connection.close()

    # Renderizar el panel con los datos correctos
    return render_template(
        'admin_dashboard.html', 
        vuelos=vuelos,
        total_vuelos=total_vuelos, 
        total_reservas=total_reservas, 
        ganancias_totales=ganancias_totales
    )
@app_routes.route('/gestion_asientos/<int:vuelo_id>', methods=['GET'])
def gestion_asientos(vuelo_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Obtener los detalles del vuelo
    cursor.execute("""
        SELECT *
        FROM vueloandm
        WHERE vuelo_id = %s
    """, (vuelo_id,))
    vuelo = cursor.fetchone()

    # Verificar que el vuelo exista
    if not vuelo:
        cursor.close()
        connection.close()
        flash("El vuelo no existe.", "danger")
        return redirect(url_for('app_routes.cliente_dashboard'))

    # Obtener los asientos para el vuelo específico
    cursor.execute("""
        SELECT a.asiento_id, a.numero_asiento, a.estado, u.nombre AS cliente
        FROM asientos a
        LEFT JOIN usuario u ON a.usuario_id = u.id
        WHERE a.vuelo_id = %s
        ORDER BY a.numero_asiento
    """, (vuelo_id,))
    asientos = cursor.fetchall()

    cursor.close()
    connection.close()

    # Renderizar la plantilla con los datos del vuelo y los asientos
    return render_template('gestion_asientos.html', vuelo=vuelo, asientos=asientos)




@app_routes.route('/seleccionar_vuelo_asientos', methods=['GET'])
def seleccionar_vuelo_asientos():
    connection = get_db_connection()
    cursor = connection.cursor()

    # Obtener la lista de vuelos
    cursor.execute("SELECT vuelo_id, operador FROM vueloandm")
    vuelos = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template('seleccionar_vuelo_asientos.html', vuelos=vuelos)



@app_routes.route('/crear_vuelo', methods=['GET', 'POST'])
def crear_vuelo():
    if request.method == 'POST':
        # Procesar datos del formulario
        vuelo_id = request.form['vuelo_id']
        operador = request.form['operador']
        matricula = request.form['matricula']
        precio = request.form['precio']
        salida = request.form['salida']
        llegada = request.form['llegada']
        fecha_salida = request.form['fecha_salida']
        hora_salida = request.form['hora_salida']
        fecha_llegada = request.form['fecha_llegada']
        hora_llegada = request.form['hora_llegada']
        tipo_vuelo = request.form['tipo_vuelo']
        modo_vuelo = request.form['modo_vuelo']
        asientos_disponibles = int(request.form['asientos_disponibles'])  # Aseguramos que sea un entero

        # Insertar datos del vuelo en la base de datos
        connection = get_db_connection()
        cursor = connection.cursor()

        vuelo_query = """
        INSERT INTO vueloandm (vuelo_id, operador, matricula, precio, salida, llegada, fecha_salida, hora_salida,
                               fecha_llegada, hora_llegada, tipo_vuelo, modo_vuelo, asientos_disponibles)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(vuelo_query, (vuelo_id, operador, matricula, precio, salida, llegada, fecha_salida, hora_salida,
                                     fecha_llegada, hora_llegada, tipo_vuelo, modo_vuelo, asientos_disponibles))
        
        # Crear asientos asociados al vuelo
        for i in range(1, asientos_disponibles + 1):
            numero_asiento = f"{i}"  # Generar número de asiento (puedes modificarlo para incluir filas y columnas como "1A", "1B")
            asiento_query = """
            INSERT INTO asientos (vuelo_id, numero_asiento, estado)
            VALUES (%s, %s, 'disponible')
            """
            cursor.execute(asiento_query, (vuelo_id, numero_asiento))

        # Guardar cambios en la base de datos
        connection.commit()
        cursor.close()
        connection.close()

        flash('Vuelo y asientos creados exitosamente.', 'success')
        return redirect(url_for('app_routes.admin_dashboard'))

    # Opciones dinámicas para tipo y modo de vuelo
    tipos_vuelo = ["ida", "redondo", "directo", "escalas"]
    modos_vuelo = ["comercial", "privado", "publico", "ejecutivo"]

    return render_template('crear_vuelo.html', tipos_vuelo=tipos_vuelo, modos_vuelo=modos_vuelo)

# Ruta para gestionar vuelos
@app_routes.route('/admin/vuelos', methods=['GET'])
def admin_vuelos():
    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, vuelo_id, operador, precio, salida, fecha_salida, hora_salida, 
               llegada, fecha_llegada, hora_llegada, tipo_vuelo, modo_vuelo, matricula, 
               asientos_disponibles
        FROM vueloandm
    """)
    vuelos = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template('admin_vuelos.html', vuelos=vuelos)



@app_routes.route('/admin_reservas', methods=['GET'])
def admin_reservas():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Consulta actualizada para incluir estado del pago
    cursor.execute("""
        SELECT r.reserva_id, r.fecha_reserva, r.asiento_id, v.salida, v.llegada, 
               v.fecha_salida, v.hora_salida, v.fecha_llegada, v.hora_llegada, 
               v.tipo_vuelo, v.precio, a.numero_asiento, 
               COALESCE(p.estado_pago, 'Pendiente') AS estado_pago
        FROM reservas r
        JOIN vueloandm v ON r.vuelo_id = v.vuelo_id
        JOIN asientos a ON r.asiento_id = a.asiento_id
        LEFT JOIN pagos p ON r.reserva_id = p.reserva_id
    """)
    reservas = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template('admin_reservas.html', reservas=reservas)


@app_routes.route('/admin_asientos/<int:vuelo_id>', methods=['GET', 'POST'])
def admin_asientos(vuelo_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    # Obtener los asientos del vuelo
    cursor.execute("""
        SELECT a.asiento_id, a.numero_asiento, a.estado, u.nombre
        FROM asientos a
        LEFT JOIN usuario u ON a.usuario_id = u.id
        WHERE a.vuelo_id = %s
    """, (vuelo_id,))
    asientos = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template('admin_asientos.html', asientos=asientos, vuelo_id=vuelo_id)



@app_routes.route('/actualizar_vuelo/<int:vuelo_id>', methods=['GET', 'POST'])
def actualizar_vuelo(vuelo_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    if request.method == 'POST':
        # Obtener datos del formulario
        operador = request.form['operador']
        precio = request.form['precio']
        salida = request.form['salida']
        fecha_salida = request.form['fecha_salida']
        hora_salida = request.form['hora_salida']
        llegada = request.form['llegada']
        fecha_llegada = request.form['fecha_llegada']
        hora_llegada = request.form['hora_llegada']
        tipo_vuelo = request.form['tipo_vuelo']
        modo_vuelo = request.form['modo_vuelo']
        matricula = request.form['matricula']
        nuevos_asientos_disponibles = int(request.form['asientos_disponibles'])

        # Obtener el número actual de asientos disponibles
        cursor.execute("SELECT asientos_disponibles FROM vueloandm WHERE vuelo_id = %s", (vuelo_id,))
        resultado = cursor.fetchone()

        if not resultado:
            flash("El vuelo no existe.", "danger")
            return redirect(url_for('app_routes.admin_vuelos'))

        asientos_anteriores = resultado[0]

        # Actualizar vuelo en la tabla `vueloandm`
        query = """
            UPDATE vueloandm
            SET operador = %s, precio = %s, salida = %s, fecha_salida = %s, hora_salida = %s,
                llegada = %s, fecha_llegada = %s, hora_llegada = %s, tipo_vuelo = %s, 
                modo_vuelo = %s, matricula = %s, asientos_disponibles = %s
            WHERE vuelo_id = %s
        """
        cursor.execute(query, (operador, precio, salida, fecha_salida, hora_salida, llegada, 
                               fecha_llegada, hora_llegada, tipo_vuelo, modo_vuelo, matricula, 
                               nuevos_asientos_disponibles, vuelo_id))

        # Actualizar la tabla `asientos` según el nuevo número de asientos disponibles
        if nuevos_asientos_disponibles > asientos_anteriores:
            # Agregar nuevos asientos
            for num_asiento in range(asientos_anteriores + 1, nuevos_asientos_disponibles + 1):
                query_asientos = """
                    INSERT INTO asientos (vuelo_id, numero_asiento, estado)
                    VALUES (%s, %s, 'disponible')
                """
                cursor.execute(query_asientos, (vuelo_id, num_asiento))
        elif nuevos_asientos_disponibles < asientos_anteriores:
            # Marcar como no disponibles los asientos excedentes
            query_asientos = """
                UPDATE asientos
                SET estado = 'no disponible'
                WHERE vuelo_id = %s AND numero_asiento > %s
            """
            cursor.execute(query_asientos, (vuelo_id, nuevos_asientos_disponibles))

        connection.commit()
        flash("Vuelo y asientos actualizados exitosamente.", "success")
        return redirect(url_for('app_routes.admin_vuelos'))

    # Si es método GET, mostrar los datos actuales del vuelo
    cursor.execute("SELECT * FROM vueloandm WHERE vuelo_id = %s", (vuelo_id,))
    vuelo = cursor.fetchone()

    cursor.close()
    connection.close()

    return render_template('actualizar_vuelo.html', vuelo=vuelo)



@app_routes.route('/reservas_pagadas')
def reservas_pagadas():
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""SELECT * FROM reservas_pagadas""")  # Modifica la consulta según tus datos
    reservas_pagadas = cursor.fetchall()
    cursor.close()
    connection.close()
    return render_template('reservas_pagadas.html', reservas_pagadas=reservas_pagadas)

@app_routes.route('/vuelos_pagados', methods=['GET', 'POST'])
def vuelos_pagados():
    connection = get_db_connection()
    cursor = connection.cursor()

    if request.method == 'POST':
        # Si se envió un formulario, procesamos la creación de un nuevo vuelo
        vuelo_id = request.form.get('vuelo_id')
        matricula = request.form.get('matricula')
        operador = request.form.get('operador')
        precio = request.form.get('precio')
        salida = request.form.get('salida')
        fecha_salida = request.form.get('fecha_salida')
        hora_salida = request.form.get('hora_salida')
        llegada = request.form.get('llegada')
        fecha_llegada = request.form.get('fecha_llegada')
        hora_llegada = request.form.get('hora_llegada')
        tipo_vuelo = request.form.get('tipo_vuelo')
        modo_vuelo = request.form.get('modo_vuelo')

        # Insertar nuevo vuelo
        cursor.execute("""
            INSERT INTO vueloandm (id, vuelo_id, matricula, operador, precio, salida, fecha_salida, hora_salida, llegada, fecha_llegada, hora_llegada, tipo_vuelo, modo_vuelo)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (session['user_id'], vuelo_id, matricula, operador, precio, salida, fecha_salida, hora_salida, llegada, fecha_llegada, hora_llegada, tipo_vuelo, modo_vuelo))
        connection.commit()
        flash('Vuelo creado exitosamente', 'success')

    # Obtener vuelos pagados
    cursor.execute("""
        SELECT v.vuelo_id, v.operador, v.precio, v.salida, v.llegada, v.fecha_salida, v.fecha_llegada, v.tipo_vuelo, v.modo_vuelo
        FROM vueloandm v
        JOIN pagos p ON v.vuelo_id = p.reserva_id
        WHERE p.estado_pago = 'Pagado'
    """)
    vuelos_pagados = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template('vuelos_pagados.html', vuelos_pagados=vuelos_pagados)


@app_routes.route('/borrar_vuelo/<int:vuelo_id>', methods=['POST'])
def borrar_vuelo(vuelo_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    # Elimina el vuelo
    cursor.execute("DELETE FROM vueloandm WHERE vuelo_id = %s", (vuelo_id,))
    connection.commit()

    flash('Vuelo eliminado exitosamente', 'success')
    cursor.close()
    connection.close()

    return redirect(url_for('app_routes.admin_dashboard'))


@app_routes.route('/reporte_ganancias', methods=['GET'])
def reporte_ganancias():
    if 'user_id' not in session or session.get('role') != 'administrador':
        flash("No tienes permisos para acceder a esta página", "danger")
        return redirect(url_for('app_routes.iniciar_sesion'))

    try:
        connection = get_db_connection()
        cursor = connection.cursor()

        # Consulta SQL
        cursor.execute("""
            SELECT DATE(fecha_pago) AS fecha, SUM(monto) AS total_ganancias
            FROM pagos
            WHERE estado_pago = 'Pagado'
            GROUP BY DATE(fecha_pago)
            ORDER BY fecha DESC
        """)
        ganancias = cursor.fetchall()
        print("Ganancias obtenidas:", ganancias)

    except Exception as e:
        print("Error al obtener los datos:", e)
        flash("Error al generar el reporte de ganancias.", "danger")
        ganancias = []

    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

    return render_template('reporte_ganancias.html', ganancias=ganancias)



# Estadísticas de métodos de pago
@app_routes.route('/estadisticas_pago', methods=['GET'])
def estadisticas_pago():
    if 'user_id' not in session or session.get('role') != 'administrador':
        flash("No tienes permisos para acceder a esta página", "danger")
        return redirect(url_for('app_routes.iniciar_sesion'))

    connection = get_db_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT metodo_pago, COUNT(*) AS cantidad
        FROM pagos
        WHERE estado_pago = 'Pagado'
        GROUP BY metodo_pago
        ORDER BY cantidad DESC
    """)
    estadisticas = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template('estadisticas_pago.html', estadisticas=estadisticas)
@app_routes.route('/recomendaciones', methods=['GET'])
def recomendaciones():
    # Obtener las recomendaciones de la base de datos
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT recomendacion_id, titulo, descripcion, imagen_url FROM recomendaciones")
    recomendaciones = cursor.fetchall()  # La tupla ahora incluye recomendacion_id
    cursor.close()
    connection.close()

    # Pasar las recomendaciones al template
    return render_template('recomendaciones.html', recomendaciones=recomendaciones)

@app_routes.route('/eliminar_recomendacion/<int:id>', methods=['POST'])
def eliminar_recomendacion(id):
    connection = get_db_connection()
    cursor = connection.cursor()

    # Eliminar la recomendación
    cursor.execute("DELETE FROM recomendaciones WHERE recomendacion_id = %s", (id,))
    connection.commit()
    cursor.close()
    connection.close()

    flash("Recomendación eliminada exitosamente.", "success")
    return redirect(url_for('app_routes.recomendaciones'))
import os
from flask import Flask, request, render_template, redirect, url_for, flash, Blueprint
from werkzeug.utils import secure_filename



# Configuración para subir imágenes
UPLOAD_FOLDER = 'static/uploads'  # Carpeta donde se guardarán las imágenes
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}


@app_routes.route('/actualizar_recomendacion/<int:id>', methods=['GET', 'POST'])
def actualizar_recomendacion(id):
    connection = get_db_connection()
    cursor = connection.cursor()

    # Obtener los datos actuales de la recomendación
    cursor.execute("SELECT recomendacion_id, titulo, descripcion, imagen_url FROM recomendaciones WHERE recomendacion_id = %s", (id,))
    recomendacion = cursor.fetchone()

    if not recomendacion:
        flash("Recomendación no encontrada.", "danger")
        return redirect(url_for('app_routes.recomendaciones'))

    if request.method == 'POST':
        # Capturar los datos actualizados desde el formulario
        titulo = request.form.get('titulo')
        descripcion = request.form.get('descripcion')

        # Manejo de la imagen subida
        if 'imagen' in request.files and request.files['imagen']:
            imagen = request.files['imagen']
            nombre_archivo = secure_filename(imagen.filename)
            ruta_imagen = os.path.join(UPLOAD_FOLDER, nombre_archivo)
            imagen.save(ruta_imagen)
        else:
            nombre_archivo = recomendacion[3]  # Mantener la imagen anterior

        # Actualizar la recomendación en la base de datos
        cursor.execute("""
            UPDATE recomendaciones
            SET titulo = %s, descripcion = %s, imagen_url = %s
            WHERE recomendacion_id = %s
        """, (titulo, descripcion, nombre_archivo, id))
        connection.commit()

        flash("Recomendación actualizada exitosamente.", "success")
        return redirect(url_for('app_routes.recomendaciones'))

    # Renderizar el formulario con los datos actuales
    cursor.close()
    connection.close()
    return render_template('actualizar_recomendacion.html', recomendacion=recomendacion)



def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Asegúrate de que la carpeta exista
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
@app_routes.route('/crear_recomendacion', methods=['GET', 'POST'])
def crear_recomendacion():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("SELECT vuelo_id, salida, llegada FROM vueloandm")
    vuelos = cursor.fetchall()

    if request.method == 'POST':
        # Procesar el formulario
        titulo = request.form['titulo']
        descripcion = request.form['descripcion']
        vuelo_id = request.form['vuelo_id']
        imagen = request.files['imagen']

        # Guardar imagen en una carpeta
        imagen_path = os.path.join('static/uploads', imagen.filename)
        imagen.save(imagen_path)

        # Insertar recomendación
        cursor.execute("""
            INSERT INTO recomendaciones (titulo, descripcion, vuelo_id, imagen_url)
            VALUES (%s, %s, %s, %s)
        """, (titulo, descripcion, vuelo_id, f'uploads/{imagen.filename}'))
        connection.commit()

        flash("Recomendación creada exitosamente.", "success")
        return redirect(url_for('app_routes.admin_dashboard'))

    cursor.close()
    connection.close()
    return render_template('crear_recomendacion.html', vuelos=vuelos)


@app_routes.route('/admin/crear_promocion', methods=['GET', 'POST'])
def crear_promocion():
    if request.method == 'POST':
        codigo = request.form.get('codigo')
        descripcion = request.form.get('descripcion')
        descuento = request.form.get('descuento')
        fecha_inicio = request.form.get('fecha_inicio')
        fecha_fin = request.form.get('fecha_fin')

        connection = get_db_connection()
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO promociones (codigo, descripcion, descuento, fecha_inicio, fecha_fin)
            VALUES (%s, %s, %s, %s, %s)
        """, (codigo, descripcion, descuento, fecha_inicio, fecha_fin))
        connection.commit()
        cursor.close()
        connection.close()

        flash('Promoción creada exitosamente.', 'success')
        return redirect(url_for('app_routes.listar_promociones'))

    return render_template('crear_promocion.html')

@app_routes.route('/admin/promociones', methods=['GET'])
def listar_promociones():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        SELECT promocion_id, codigo, descripcion, descuento, fecha_inicio, fecha_fin
        FROM promociones
    """)
    promociones = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template('administrar_promociones.html', promociones=promociones)


@app_routes.route('/admin/promociones/editar/<int:promocion_id>', methods=['GET', 'POST'])
def editar_promocion(promocion_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    if request.method == 'POST':
        codigo = request.form.get('codigo')
        descripcion = request.form.get('descripcion')
        descuento = request.form.get('descuento')
        fecha_inicio = request.form.get('fecha_inicio')
        fecha_fin = request.form.get('fecha_fin')

        cursor.execute("""
            UPDATE promociones
            SET codigo = %s, descripcion = %s, descuento = %s, fecha_inicio = %s, fecha_fin = %s
            WHERE promocion_id = %s
        """, (codigo, descripcion, descuento, fecha_inicio, fecha_fin, promocion_id))
        connection.commit()
        cursor.close()
        connection.close()

        flash('Promoción actualizada exitosamente.', 'success')
        return redirect(url_for('app_routes.listar_promociones'))

    cursor.execute("SELECT * FROM promociones WHERE promocion_id = %s", (promocion_id,))
    promocion = cursor.fetchone()
    cursor.close()
    connection.close()

    return render_template('editar_promocion.html', promocion=promocion)

@app_routes.route('/admin/promociones/borrar/<int:promocion_id>', methods=['POST'])
def borrar_promocion(promocion_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    cursor.execute("DELETE FROM promociones WHERE promocion_id = %s", (promocion_id,))
    connection.commit()
    cursor.close()
    connection.close()

    flash('Promoción eliminada exitosamente.', 'success')
    return redirect(url_for('app_routes.listar_promociones'))



@app_routes.route('/bienvenida')
def bienvenida_cliente():
    # Verifica si el cliente inició sesión
    if 'user_id' not in session or session.get('role') != 'cliente':
        flash("Por favor, inicia sesión primero", "danger")
        return redirect(url_for('app_routes.iniciar_sesion'))
    # Muestra la página de bienvenida
    return render_template('bienvenida_cliente_aerolinea.html')


@app_routes.route('/cliente_dashboard', methods=['GET'])
def cliente_dashboard():
    if 'user_id' not in session or session.get('role') != 'cliente':
        flash("No tienes permisos para acceder a esta página", "danger")
        return redirect(url_for('app_routes.iniciar_sesion'))

    cliente_id = session['user_id']

    try:
        # Conexión a la base de datos
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Consulta para obtener las reservas del cliente
        cursor.execute("""
            SELECT r.reserva_id, v.salida, v.llegada, v.fecha_salida, v.hora_salida,
                   v.fecha_llegada, v.hora_llegada, v.precio
            FROM reservas r
            JOIN vueloandm v ON r.vuelo_id = v.vuelo_id
            WHERE r.usuario_id = %s
        """, (cliente_id,))
        reservas = cursor.fetchall()

        cursor.close()
        connection.close()

        # Renderizar la plantilla con las reservas
        return render_template('cliente_dashboard.html', reservas=reservas)

    except Exception as e:
        flash(f"Error al cargar las reservas: {str(e)}", "danger")
        return render_template('cliente_dashboard.html', reservas=[])
@app_routes.route('/seleccionar_asientos/<int:vuelo_id>', methods=['GET', 'POST'])
def seleccionar_asientos(vuelo_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)  # Usar dictionary=True para trabajar con nombres de columnas

    if request.method == 'POST':
        # Obtener el asiento seleccionado
        asiento_id = request.form.get('asiento_id')
        if not asiento_id:
            flash("Por favor selecciona un asiento.", "danger")
            return redirect(url_for('app_routes.seleccionar_asientos', vuelo_id=vuelo_id))

        # Verificar que el asiento esté disponible
        cursor.execute("""
            SELECT estado
            FROM asientos
            WHERE asiento_id = %s
        """, (asiento_id,))
        asiento = cursor.fetchone()

        if not asiento or asiento['estado'] != 'disponible':
            flash("El asiento seleccionado no está disponible.", "danger")
            return redirect(url_for('app_routes.seleccionar_asientos', vuelo_id=vuelo_id))

        # Guardar el asiento seleccionado en la sesión
        session['asiento_seleccionado'] = asiento_id

        # Actualizar el estado del asiento
        try:
            cursor.execute("""
                UPDATE asientos
                SET estado = 'ocupado', usuario_id = %s
                WHERE asiento_id = %s
            """, (session.get('user_id'), asiento_id))
            connection.commit()
            flash(f"El asiento número {asiento_id} ha sido reservado exitosamente.", "success")
        except Exception as e:
            connection.rollback()
            flash(f"Error al reservar el asiento: {e}", "danger")
        finally:
            cursor.close()
            connection.close()

        # Redirigir a la selección de vuelo
        return redirect(url_for('app_routes.seleccionar_vuelo', vuelo_id=vuelo_id))

    # Obtener los asientos ordenados por `numero_asiento`
    cursor.execute("""
        SELECT asiento_id AS id, numero_asiento AS numero, estado
        FROM asientos
        WHERE vuelo_id = %s
        ORDER BY numero_asiento
    """, (vuelo_id,))
    asientos_raw = cursor.fetchall()

    # Organizar los asientos en filas de 6
    filas = []
    fila_actual = []
    for index, asiento in enumerate(asientos_raw):
        fila_actual.append({
            'id': asiento['id'],
            'numero': asiento['numero'],  # Número secuencial del asiento
            'estado': asiento['estado']  # Estado del asiento (disponible/ocupado)
        })
        if (index + 1) % 6 == 0:  # Cambiar de fila después de 6 asientos
            filas.append(fila_actual)
            fila_actual = []
    if fila_actual:  # Agregar la última fila si tiene elementos
        filas.append(fila_actual)

    cursor.close()
    connection.close()

    # Enviar los asientos organizados a la plantilla
    return render_template('seleccionar_asientos.html', vuelo_id=vuelo_id, asientos=filas)




@app_routes.route('/reservar_asiento/<int:vuelo_id>', methods=['POST'])
def reservar_asiento(vuelo_id):
    connection = get_db_connection()
    cursor = connection.cursor()

    # Obtener el asiento seleccionado
    asiento_id = request.form.get('asiento_id')
    if not asiento_id:
        flash("Por favor selecciona un asiento.", "danger")
        return redirect(url_for('app_routes.seleccionar_asientos', vuelo_id=vuelo_id))

    # Verificar que el asiento esté disponible
    cursor.execute("""
        SELECT estado
        FROM asientos
        WHERE asiento_id = %s
    """, (asiento_id,))
    asiento = cursor.fetchone()

    if not asiento or asiento[0] != 'disponible':
        flash("El asiento seleccionado no está disponible.", "danger")
        cursor.close()
        connection.close()
        return redirect(url_for('app_routes.seleccionar_asientos', vuelo_id=vuelo_id))

    # Guardar el asiento seleccionado en la sesión
    session['asiento_seleccionado'] = asiento_id

    # Actualizar el estado del asiento
    try:
        cursor.execute("""
            UPDATE asientos
            SET estado = 'ocupado', usuario_id = %s
            WHERE asiento_id = %s
        """, (session.get('user_id'), asiento_id))
        connection.commit()
        flash("Asiento reservado exitosamente!", "success")
    except Exception as e:
        connection.rollback()
        flash(f"Error al reservar el asiento: {e}", "danger")
    finally:
        cursor.close()
        connection.close()

    # Redirigir directamente al panel del cliente con detalles actualizados
    return redirect(url_for('app_routes.cliente_dashboard', vuelo_id=vuelo_id, asiento_id=asiento_id))


@app_routes.route('/buscar_vuelo', methods=['POST'])
def buscar_vuelo():
    salida = request.form.get('salida')
    llegada = request.form.get('llegada')
    tipo_vuelo = request.form.get('tipo_vuelo')  # Filtro adicional
    modo_vuelo = request.form.get('modo_vuelo')  # Filtro adicional

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    query = """
        SELECT * FROM vueloandm 
        WHERE salida = %s AND llegada = %s
    """
    params = [salida, llegada]

    if tipo_vuelo:
        query += " AND tipo_vuelo = %s"
        params.append(tipo_vuelo)

    if modo_vuelo:
        query += " AND modo_vuelo = %s"
        params.append(modo_vuelo)

    cursor.execute(query, params)
    vuelos = cursor.fetchall()

    cursor.close()
    connection.close()

    if vuelos:
        return render_template('vuelos_disponibles.html', vuelos=vuelos)
    else:
        flash("No se encontraron vuelos con los criterios seleccionados.", "warning")
        return render_template('vuelos_disponibles.html', vuelos=[])

@app_routes.route('/cancelar_ticket/<int:ticket_id>', methods=['GET', 'POST'])
def cancelar_ticket(ticket_id):
    # Verifica si el usuario tiene acceso
    if 'user_id' not in session:
        flash("Debes iniciar sesión para realizar esta acción.", "warning")
        return redirect(url_for('app_routes.iniciar_sesion'))

    # Lógica para cancelar el ticket
    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        # Eliminar el ticket basado en su ID
        cursor.execute("DELETE FROM tickets WHERE id = %s", (ticket_id,))
        connection.commit()
        flash("El ticket ha sido cancelado exitosamente.", "success")
    except Exception as e:
        connection.rollback()
        flash(f"Error al cancelar el ticket: {str(e)}", "danger")
    finally:
        cursor.close()
        connection.close()

    # Redirige a la página de bienvenida o a la lista de tickets
    return redirect(url_for('app_routes.bienvenida_cliente_aerolinea.html'))


@app_routes.route('/promociones_cliente', methods=['GET'])
def mostrar_promociones_cliente():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    cursor.execute("""
        SELECT promocion_id, codigo, descripcion, descuento, fecha_inicio, fecha_fin
        FROM promociones
    """)
    promociones = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template('promociones_cliente.html', promociones=promociones)


@app_routes.route('/seleccionar_vuelo/<int:vuelo_id>', methods=['GET', 'POST'])
def seleccionar_vuelo(vuelo_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Obtener los detalles del vuelo seleccionado
    cursor.execute("SELECT * FROM vueloandm WHERE vuelo_id = %s", (vuelo_id,))
    vuelo = cursor.fetchone()

    # Verificar el asiento seleccionado en la sesión
    asiento_id = session.get('asiento_seleccionado')
    if asiento_id:
        cursor.execute("SELECT numero_asiento FROM asientos WHERE asiento_id = %s", (asiento_id,))
        asiento = cursor.fetchone()
    else:
        asiento = None

    cursor.close()
    connection.close()

    if not asiento_id or not asiento:
        flash("No se ha seleccionado un asiento. Por favor, selecciona uno.", "danger")
        return redirect(url_for('app_routes.seleccionar_asientos', vuelo_id=vuelo_id))

    numero_asiento = asiento['numero_asiento']

    if request.method == 'POST':
        # Redirigir a confirmar reserva
        return redirect(url_for('app_routes.confirmar_reserva', vuelo_id=vuelo_id, asiento_id=asiento_id))

    # Renderizar la plantilla con detalles del vuelo y asiento
    return render_template('seleccionar_vuelo.html', vuelo=vuelo, numero_asiento=numero_asiento, asiento_id=asiento_id)

@app_routes.route('/confirmar_reserva', methods=['GET', 'POST'])
def confirmar_reserva():
    vuelo_id = request.args.get('vuelo_id')  # Obtener el ID del vuelo desde la URL
    asiento_id = request.args.get('asiento_id')  # Obtener el ID del asiento desde la URL
    usuario_id = session.get('user_id')  # ID del usuario autenticado

    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Obtener los detalles del vuelo
    cursor.execute("SELECT * FROM vueloandm WHERE vuelo_id = %s", (vuelo_id,))
    vuelo = cursor.fetchone()

    # Obtener los detalles del asiento
    cursor.execute("SELECT * FROM asientos WHERE asiento_id = %s", (asiento_id,))
    asiento = cursor.fetchone()

    cursor.close()
    connection.close()

    if not vuelo or not asiento:
        flash("No se encontraron los detalles del vuelo o asiento.", "danger")
        return redirect(url_for('app_routes.cliente_dashboard'))

    if request.method == 'POST':
        # Procesar la confirmación de reserva
        connection = get_db_connection()
        cursor = connection.cursor()
        try:
            # Insertar la reserva
            cursor.execute("""
                INSERT INTO reservas (usuario_id, vuelo_id, asiento_id, fecha_reserva)
                VALUES (%s, %s, %s, NOW())
            """, (usuario_id, vuelo_id, asiento_id))
            connection.commit()

            # Actualizar el estado del asiento
            cursor.execute("""
                UPDATE asientos
                SET estado = 'ocupado'
                WHERE asiento_id = %s
            """, (asiento_id,))
            connection.commit()

            flash("Reserva confirmada exitosamente.", "success")
        except Exception as e:
            connection.rollback()
            flash(f"Error al confirmar la reserva: {e}", "danger")
        finally:
            cursor.close()
            connection.close()

        return redirect(url_for('app_routes.resumen_reserva'))

    # Renderizar la plantilla de confirmación
    return render_template('confirmar_reserva.html', vuelo=vuelo, numero_asiento=asiento['numero_asiento'])
@app_routes.route('/reservar_vuelo/<int:vuelo_id>', methods=['POST'])
def reservar_vuelo(vuelo_id):
    asiento_id = session.get('asiento_seleccionado')

    if not asiento_id:
        flash("No se puede completar la reserva sin un asiento.", "danger")
        return redirect(url_for('app_routes.seleccionar_asientos', vuelo_id=vuelo_id))

    connection = get_db_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            INSERT INTO reservas (vuelo_id, asiento_id, usuario_id)
            VALUES (%s, %s, %s)
        """, (vuelo_id, asiento_id, session.get('user_id')))
        connection.commit()
        flash("Reserva completada con éxito.", "success")
    except Exception as e:
        connection.rollback()
        flash(f"Error al completar la reserva: {e}", "danger")
    finally:
        cursor.close()
        connection.close()

    return redirect(url_for('app_routes.cliente_dashboard'))


@app_routes.route('/resumen_reserva', methods=['GET'])
def resumen_reserva():
    usuario_id = session.get('user_id')
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT r.reserva_id, r.fecha_reserva, v.salida, v.llegada, v.fecha_salida, v.hora_salida,
               v.fecha_llegada, v.hora_llegada, v.tipo_vuelo, v.modo_vuelo, v.precio, a.numero_asiento
        FROM reservas r
        JOIN vueloandm v ON r.vuelo_id = v.vuelo_id
        JOIN asientos a ON r.asiento_id = a.asiento_id
        WHERE r.usuario_id = %s
        ORDER BY r.reserva_id DESC
        LIMIT 1
    """, (usuario_id,))
    reserva = cursor.fetchone()

    cursor.close()
    connection.close()

    if not reserva:
        flash("No se encontró ninguna reserva reciente.", "warning")
        return redirect(url_for('app_routes.cliente_dashboard'))

    return render_template('resumen_reserva.html', reserva=reserva)
@app_routes.route('/pago/<int:reserva_id>', methods=['GET', 'POST'])
def pago(reserva_id):
    usuario_id = session.get('user_id')
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT r.reserva_id, v.precio
        FROM reservas r
        JOIN vueloandm v ON r.vuelo_id = v.vuelo_id
        WHERE r.reserva_id = %s AND r.usuario_id = %s
    """, (reserva_id, usuario_id))
    reserva = cursor.fetchone()

    if not reserva:
        flash("Reserva no encontrada.", "danger")
        return redirect(url_for('app_routes.cliente_dashboard'))

    if request.method == 'POST':
        metodo_pago = request.form.get('metodo_pago')
        ultimos_cuatro_digitos = request.form.get('ultimos_cuatro_digitos')

        cursor.execute("""
            INSERT INTO pagos (reserva_id, monto, metodo_pago, ultimos_cuatro_digitos, estado_pago, fecha_pago)
            VALUES (%s, %s, %s, %s, 'Pagado', NOW())
        """, (reserva_id, reserva['precio'], metodo_pago, ultimos_cuatro_digitos))
        connection.commit()

        flash('Pago realizado exitosamente', 'success')
        return redirect(url_for('app_routes.confirmacion_pago', reserva_id=reserva_id))

    cursor.close()
    connection.close()

    return render_template('pago.html', reserva_id=reserva_id, precio=reserva['precio'])
@app_routes.route('/confirmacion_pago/<int:reserva_id>')
def confirmacion_pago(reserva_id):
    usuario_id = session.get('user_id')
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT r.reserva_id, u.nombre AS nombre_cliente, v.salida, v.llegada, 
               v.fecha_salida, v.hora_salida, v.fecha_llegada, v.hora_llegada, 
               v.modo_vuelo, v.precio, p.estado_pago, a.numero_asiento
        FROM reservas r
        JOIN usuario u ON r.usuario_id = u.id
        JOIN vueloandm v ON r.vuelo_id = v.vuelo_id
        JOIN pagos p ON p.reserva_id = r.reserva_id
        JOIN asientos a ON r.asiento_id = a.asiento_id
        WHERE r.reserva_id = %s AND r.usuario_id = %s
    """, (reserva_id, usuario_id))
    
    ticket = cursor.fetchone()
    cursor.close()
    connection.close()
    
    if ticket is None:
        flash("Detalles del ticket no encontrados", "danger")
        return redirect(url_for('app_routes.cliente_dashboard'))

    return render_template('confirmacion_pago.html', ticket=ticket)

@app_routes.route('/ver_recomendaciones', methods=['GET'])
def ver_recomendaciones():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT r.recomendacion_id, r.titulo, r.descripcion, r.imagen_url, v.llegada, v.precio
            FROM recomendaciones r
            JOIN vueloandm v ON r.vuelo_id = v.vuelo_id
        """)
        recomendaciones = cursor.fetchall()
    except Exception as e:
        flash(f"Error al cargar recomendaciones: {e}", "danger")
        recomendaciones = []
    finally:
        cursor.close()
        connection.close()

    return render_template('ver_recomendaciones.html', recomendaciones=recomendaciones)

# Ruta para ver el detalle de una recomendación y reservar
@app_routes.route('/detalle_recomendacion/<int:recomendacion_id>', methods=['GET', 'POST'])
def detalle_recomendacion(recomendacion_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Obtener los datos de la recomendación
    cursor.execute("""
        SELECT r.titulo, r.descripcion, r.imagen_url, v.vuelo_id, v.llegada, 
               v.fecha_salida, v.hora_salida, v.fecha_llegada, v.hora_llegada, v.precio
        FROM recomendaciones r
        JOIN vueloandm v ON r.vuelo_id = v.vuelo_id
        WHERE r.recomendacion_id = %s
    """, (recomendacion_id,))
    recomendacion = cursor.fetchone()

    if not recomendacion:
        flash("Recomendación no encontrada.", "danger")
        return redirect(url_for('app_routes.ver_recomendaciones'))

    if request.method == 'POST':
        usuario_id = session.get('user_id')
        lugar_salida = request.form.get('lugar_salida')  # Capturar el origen desde el formulario
        asiento_id = request.form.get('asiento_id')

        # Insertar la reserva en la base de datos
        cursor.execute("""
            INSERT INTO reservas_recomendaciones_nueva 
            (usuario_id, vuelo_id, asiento_id, lugar_salida, fecha_reserva)
            VALUES (%s, %s, %s, %s, NOW())
        """, (usuario_id, recomendacion['vuelo_id'], asiento_id, lugar_salida))
        connection.commit()
        reserva_id = cursor.lastrowid

        flash("Reserva realizada. Procede al pago.", "success")
        return redirect(url_for('app_routes.pago_recomendacion', reserva_id=reserva_id))

    cursor.close()
    connection.close()
    return render_template('detalle_recomendaciones.html', recomendacion=recomendacion)



@app_routes.route('/pago_recomendacion/<int:reserva_id>', methods=['GET', 'POST'])
def pago_recomendacion(reserva_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        # Obtener la reserva correspondiente
        cursor.execute("""
            SELECT rr.reserva_id, rr.vuelo_id, v.precio
            FROM reservas_recomendaciones_nueva rr
            JOIN vueloandm v ON rr.vuelo_id = v.vuelo_id
            WHERE rr.reserva_id = %s
        """, (reserva_id,))
        reserva = cursor.fetchone()

        # Validar que la reserva exista
        if not reserva:
            flash("Reserva no encontrada. Verifica tu selección.", "danger")
            return redirect(url_for('app_routes.ver_recomendaciones'))

        # Procesar el formulario de pago
        if request.method == 'POST':
            metodo_pago = request.form.get('metodo_pago')

            # Insertar el pago en la base de datos
            cursor.execute("""
                INSERT INTO pagos_recomendaciones (reserva_id, monto, metodo_pago, estado_pago, fecha_pago)
                VALUES (%s, %s, %s, 'Pagado', NOW())
            """, (reserva_id, reserva['precio'], metodo_pago))
            connection.commit()

            flash("Pago realizado exitosamente.", "success")
            return redirect(url_for('app_routes.confirmacion_pago_recomendacion', reserva_id=reserva_id))

    except Exception as e:
        flash(f"Error al procesar el pago: {str(e)}", "danger")

    finally:
        cursor.close()
        connection.close()

    # Renderizar la página de pago
    return render_template('pago_recomendaciones.html', reserva=reserva)



# Ruta para confirmar el pago
@app_routes.route('/confirmacion_pago_recomendacion/<int:reserva_id>', methods=['GET'])
def confirmacion_pago_recomendacion(reserva_id):
    usuario_id = session.get('user_id')
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT rr.reserva_id, u.nombre AS nombre_cliente, v.salida, v.llegada, 
                   v.fecha_salida, v.hora_salida, v.fecha_llegada, v.hora_llegada, 
                   v.modo_vuelo, v.precio, rr.asiento_id
            FROM reservas_recomendaciones_nueva rr
            JOIN usuario u ON rr.usuario_id = u.id
            JOIN vueloandm v ON rr.vuelo_id = v.vuelo_id
            WHERE rr.reserva_id = %s AND rr.usuario_id = %s
        """, (reserva_id, usuario_id))
        ticket = cursor.fetchone()

        if not ticket:
            flash("Detalles del ticket no encontrados.", "danger")
            return redirect(url_for('app_routes.ver_recomendaciones'))

        # Si los detalles existen, redirigir al boleto
        return redirect(url_for('app_routes.boleto_recomendacion', reserva_id=reserva_id))

    except Exception as e:
        flash(f"Error al obtener detalles: {e}", "danger")
    finally:
        cursor.close()
        connection.close()
# Ruta para mostrar el boleto después del pago
@app_routes.route('/boleto_recomendacion/<int:reserva_id>', methods=['GET'])
def boleto_recomendacion(reserva_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    cursor.execute("""
        SELECT rr.reserva_id, u.nombre AS cliente, rr.lugar_salida, v.llegada, 
               v.fecha_salida, v.hora_salida, v.fecha_llegada, v.hora_llegada, 
               v.modo_vuelo, v.precio, rr.asiento_id
        FROM reservas_recomendaciones_nueva rr
        JOIN usuario u ON rr.usuario_id = u.id
        JOIN vueloandm v ON rr.vuelo_id = v.vuelo_id
        WHERE rr.reserva_id = %s
    """, (reserva_id,))
    boleto = cursor.fetchone()

    if not boleto:
        flash("Boleto no encontrado.", "danger")
        return redirect(url_for('app_routes.ver_recomendaciones'))

    cursor.close()
    connection.close()
    return render_template('boleto_recomendacion.html', boleto=boleto)


 



# Ruta para ver las reservas
# Ruta para ver las reservas
@app_routes.route('/mis_reservas_recomendaciones', methods=['GET'])
def mis_reservas_recomendaciones():
    usuario_id = session.get('user_id')
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    try:
        # Obtener datos directamente desde la tabla `reservas_recomendaciones_nueva`
        cursor.execute("""
            SELECT rr.reserva_id, rr.lugar_salida, rr.asiento_id, rr.fecha_reserva, 
                   v.salida AS salida, v.llegada AS llegada, v.fecha_salida, v.fecha_llegada, 
                   v.hora_salida, v.hora_llegada, v.precio
            FROM reservas_recomendaciones_nueva rr
            JOIN vueloandm v ON rr.vuelo_id = v.vuelo_id
            WHERE rr.usuario_id = %s
        """, (usuario_id,))
        reservas = cursor.fetchall()
    except Exception as e:
        flash(f"Error al cargar reservas: {e}", "danger")
        reservas = []
    finally:
        cursor.close()
        connection.close()

    return render_template('mis_reservas_recomendaciones.html', reservas=reservas)


@app_routes.route('/boleto', methods=['POST'])
def generar_boleto():
    vuelo_id = request.form.get('vuelo_id')
    if not vuelo_id:
        flash('ID del vuelo no proporcionado.', 'danger')
        return redirect(url_for('app_routes.cliente_dashboard'))

    ticket = obtener_ticket_por_vuelo_id(vuelo_id)
    if not ticket:
        flash('No se encontró información para este ID de vuelo.', 'danger')
        return redirect(url_for('app_routes.cliente_dashboard'))

    return render_template('boleto.html', ticket=ticket)


def obtener_ticket_por_vuelo_id(vuelo_id):
    try:
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT t.ticket_id, t.nombre_cliente, t.vuelo_id, v.salida, v.llegada, 
                   v.fecha_salida, v.hora_salida, v.fecha_llegada, v.hora_llegada, v.precio
            FROM tickets t
            JOIN vueloandm v ON t.vuelo_id = v.vuelo_id
            WHERE t.vuelo_id = %s
        """, (vuelo_id,))

        ticket = cursor.fetchone()

        cursor.close()
        connection.close()

        return ticket
    except Exception as e:
        print(f"Error al obtener los datos del ticket: {str(e)}")
        return None
    
@app_routes.route('/mis_reservas', methods=['GET'])
def mis_reservas():
    # Verificar si el cliente está autenticado
    if 'user_id' not in session or session.get('role') != 'cliente':
        flash("Debes iniciar sesión para acceder a tus reservas.", "danger")
        return redirect(url_for('app_routes.iniciar_sesion'))

    cliente_id = session['user_id']

    connection = None
    cursor = None
    try:
        # Conexión a la base de datos
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Obtener las reservas pagadas del cliente
        cursor.execute(
            """
            SELECT r.reserva_id, v.vuelo_id, v.salida, v.llegada, v.fecha_salida, 
                   v.hora_salida, v.fecha_llegada, v.hora_llegada, a.numero_asiento, 
                   v.precio, p.estado_pago
            FROM reservas r
            JOIN vueloandm v ON r.vuelo_id = v.vuelo_id
            JOIN pagos p ON p.reserva_id = r.reserva_id
            JOIN asientos a ON r.asiento_id = a.asiento_id
            WHERE r.usuario_id = %s AND p.estado_pago = 'Pagado'
            """,
            (cliente_id,)
        )

        reservas = cursor.fetchall()

    except Exception as e:
        flash(f"Ocurrió un error al obtener tus reservas: {str(e)}", "danger")
        reservas = []

    finally:
        # Asegurarse de cerrar la conexión
        if cursor:
            cursor.close()
        if connection:
            connection.close()

    # Renderizar las reservas
    return render_template('mis_reservas.html', reservas=reservas)


@app_routes.route('/imprimir_boleto/<int:reserva_id>', methods=['GET'])
def imprimir_boleto(reserva_id):
    # Verificar si el cliente está autenticado
    if 'user_id' not in session or session.get('role') != 'cliente':
        flash("Debes iniciar sesión para imprimir tu boleto.", "danger")
        return redirect(url_for('app_routes.iniciar_sesion'))

    try:
        # Conexión a la base de datos
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)

        # Obtener los detalles de la reserva y vuelo
        cursor.execute(
            """
            SELECT r.reserva_id, u.nombre AS nombre_cliente, v.salida, v.llegada, 
                   v.fecha_salida, v.hora_salida, v.fecha_llegada, v.hora_llegada, 
                   v.precio, a.numero_asiento, p.estado_pago
            FROM reservas r
            JOIN usuario u ON r.usuario_id = u.id
            JOIN vueloandm v ON r.vuelo_id = v.vuelo_id
            JOIN pagos p ON p.reserva_id = r.reserva_id
            JOIN asientos a ON r.asiento_id = a.asiento_id
            WHERE r.reserva_id = %s AND p.estado_pago = 'Pagado'
            """,
            (reserva_id,)
        )

        ticket = cursor.fetchone()

        cursor.close()
        connection.close()

        if not ticket:
            flash("No se encontraron los detalles del boleto.", "danger")
            return redirect(url_for('app_routes.mis_reservas'))

        # Renderizar el boleto para imprimir
        return render_template('boleto_imprimir.html', ticket=ticket)

    except Exception as e:
        flash(f"Ocurrió un error al obtener los datos del boleto: {str(e)}", "danger")
        return redirect(url_for('app_routes.mis_reservas'))



@app_routes.route('/registro', methods=['GET', 'POST'])
def registro():
    form = RegistroForm()

    if form.validate_on_submit():
        nombre = form.nombre.data
        correo = form.correo.data
        username = form.username.data
        password = form.password.data
        role = form.role.data

        connection = get_db_connection()
        cursor = connection.cursor()

        cursor.execute("SELECT * FROM usuario WHERE username = %s OR correo = %s", (username, correo))
        if cursor.fetchone():
            flash('El nombre de usuario o correo ya está en uso.', 'danger')
        else:
            cursor.execute("""
                INSERT INTO usuario (nombre, correo, username, password, role)
                VALUES (%s, %s, %s, %s, %s)
            """, (nombre, correo, username, password, role))
            connection.commit()
            flash('¡Registro exitoso! Puedes iniciar sesión ahora.', 'success')
            return redirect(url_for('app_routes.iniciar_sesion'))

        cursor.close()
        connection.close()

    return render_template('registro.html', form=form)

@app_routes.route('/cerrar_sesion')
def cerrar_sesion():
    session.clear()
    flash('¡Has cerrado sesión exitosamente!', 'success')
    return redirect(url_for('app_routes.iniciar_sesion'))
