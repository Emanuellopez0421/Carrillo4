from db_connection import get_db_connection

# Gestión de usuarios
def get_user_by_username(username):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("SELECT * FROM usuario WHERE username = %s", (username,))
        user = cursor.fetchone()
        return user
    finally:
        cursor.close()
        connection.close()

def create_user(nombre, correo, username, password, role):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("""
            INSERT INTO usuario (nombre, correo, username, password, role) 
            VALUES (%s, %s, %s, %s, %s)
        """, (nombre, correo, username, password, role))
        connection.commit()
    finally:
        cursor.close()
        connection.close()

# Gestión de vuelos
def get_vuelos():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM vueloandm")
        vuelos = cursor.fetchall()
        return vuelos
    finally:
        cursor.close()
        connection.close()

def get_vuelo_by_id(vuelo_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM vueloandm WHERE vuelo_id = %s", (vuelo_id,))
        vuelo = cursor.fetchone()
        return vuelo
    finally:
        cursor.close()
        connection.close()

def create_vuelo(vuelo_data):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("""
            INSERT INTO vueloandm (vuelo_id, operador, matricula, precio, salida, llegada, 
                                   fecha_salida, hora_salida, fecha_llegada, hora_llegada, 
                                   tipo_vuelo, modo_vuelo)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            vuelo_data['vuelo_id'], vuelo_data['operador'], vuelo_data['matricula'],
            vuelo_data['precio'], vuelo_data['salida'], vuelo_data['llegada'],
            vuelo_data['fecha_salida'], vuelo_data['hora_salida'],
            vuelo_data['fecha_llegada'], vuelo_data['hora_llegada'],
            vuelo_data['tipo_vuelo'], vuelo_data['modo_vuelo']
        ))
        connection.commit()
    finally:
        cursor.close()
        connection.close()

def update_vuelo(vuelo_id, vuelo_data):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("""
            UPDATE vueloandm
            SET operador = %s, matricula = %s, precio = %s, salida = %s, llegada = %s, 
                fecha_salida = %s, hora_salida = %s, fecha_llegada = %s, hora_llegada = %s, 
                tipo_vuelo = %s, modo_vuelo = %s
            WHERE vuelo_id = %s
        """, (
            vuelo_data['operador'], vuelo_data['matricula'], vuelo_data['precio'],
            vuelo_data['salida'], vuelo_data['llegada'], vuelo_data['fecha_salida'],
            vuelo_data['hora_salida'], vuelo_data['fecha_llegada'], vuelo_data['hora_llegada'],
            vuelo_data['tipo_vuelo'], vuelo_data['modo_vuelo'], vuelo_id
        ))
        connection.commit()
    finally:
        cursor.close()
        connection.close()

def delete_vuelo(vuelo_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("DELETE FROM vueloandm WHERE vuelo_id = %s", (vuelo_id,))
        connection.commit()
    finally:
        cursor.close()
        connection.close()

# Gestión de pagos
def get_pagos():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM pagos")
        pagos = cursor.fetchall()
        return pagos
    finally:
        cursor.close()
        connection.close()

def create_pago(reserva_id, monto, metodo_pago, ultimos_cuatro_digitos):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("""
            INSERT INTO pagos (reserva_id, monto, metodo_pago, ultimos_cuatro_digitos, estado_pago, fecha_pago)
            VALUES (%s, %s, %s, %s, 'Pagado', NOW())
        """, (reserva_id, monto, metodo_pago, ultimos_cuatro_digitos))
        connection.commit()
    finally:
        cursor.close()
        connection.close()

# Gestión de tickets
def obtener_ticket_por_vuelo_id(vuelo_id):
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("""
            SELECT t.ticket_id, t.nombre_cliente, t.vuelo_id, v.salida, v.llegada, 
                   v.fecha_salida, v.hora_salida, v.fecha_llegada, v.hora_llegada, v.precio
            FROM tickets t
            JOIN vueloandm v ON t.vuelo_id = v.vuelo_id
            WHERE t.vuelo_id = %s
        """, (vuelo_id,))
        ticket = cursor.fetchone()
        return ticket
    finally:
        cursor.close()
        connection.close()

# Gestión de recomendaciones
def get_recomendaciones():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM recomendaciones")
        recomendaciones = cursor.fetchall()
        return recomendaciones
    finally:
        cursor.close()
        connection.close()

def create_recomendacion(titulo, descripcion, imagen_url):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("""
            INSERT INTO recomendaciones (titulo, descripcion, imagen_url)
            VALUES (%s, %s, %s)
        """, (titulo, descripcion, imagen_url))
        connection.commit()
    finally:
        cursor.close()
        connection.close()

def delete_recomendacion(recomendacion_id):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("DELETE FROM recomendaciones WHERE recomendacion_id = %s", (recomendacion_id,))
        connection.commit()
    finally:
        cursor.close()
        connection.close()

def update_recomendacion(recomendacion_id, titulo, descripcion, imagen_url):
    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        cursor.execute("""
            UPDATE recomendaciones
            SET titulo = %s, descripcion = %s, imagen_url = %s
            WHERE recomendacion_id = %s
        """, (titulo, descripcion, imagen_url, recomendacion_id))
        connection.commit()
    finally:
        cursor.close()
        connection.close()
