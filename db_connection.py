import mysql.connector
from mysql.connector import Error

def get_db_connection():
    """
    Establece una conexión a la base de datos MySQL.

    Retorna:
        conn: Objeto de conexión MySQL si la conexión es exitosa, de lo contrario None.
    """
    try:
        # Configuración de la conexión
        conn = mysql.connector.connect(
            host='localhost',        # Dirección del servidor
            user='root',             # Usuario de MySQL
            password='',             # Contraseña del usuario (vacía si no tiene)
            database='a_carillo',    # Nombre de la base de datos
            port=3306                # Puerto por defecto de MySQL
        )
        if conn.is_connected():
            print("Conexión exitosa a la base de datos")
            return conn
    except Error as e:
        print(f"Error al conectar a la base de datos: {e}")
        return None
