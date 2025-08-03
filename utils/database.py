from dotenv import load_dotenv
import os
import pyodbc
import logging
import json
import asyncio # Asegúrate de importar asyncio si usas async/await directamente

load_dotenv()

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

driver = os.getenv('SQL_DRIVER')
server = os.getenv('SQL_SERVER')
database = os.getenv('SQL_DATABASE')
username = os.getenv('SQL_USERNAME')
password = os.getenv('SQL_PASSWORD')

connection_string = f"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}"


async def get_db_connection():
    try:
        logger.info(f"Intentando conectar a la base de datos...")
        conn = pyodbc.connect(connection_string, timeout=10)
        logger.info("Conexión exitosa a la base de datos.")
        return conn
    except pyodbc.Error as e:
        logger.error(f"Error de conexión a la base de datos: {str(e)}")
        raise Exception(f"Error de conexión a la base de datos: {str(e)}")
    except Exception as e:
         logger.error(f"Error inesperado durante la conexión: {str(e)}")
         raise

async def execute_query_json(sql_template, params=None, needs_commit=False):

    conn = None
    cursor = None
    try:
        conn = await get_db_connection()
        cursor = conn.cursor()
        param_info = "(sin parámetros)" if not params else f"(con {len(params)} parámetros)"
        logger.info(f"Ejecutando consulta {param_info}: {sql_template}")

        if params:
            cursor.execute(sql_template, params)
        else:
            cursor.execute(sql_template)

        results = []
        if cursor.description:
            columns = [column[0] for column in cursor.description]
            logger.info(f"Columnas obtenidas: {columns}")
            for row in cursor.fetchall():
                processed_row = [str(item) if isinstance(item, (bytes, bytearray)) else item for item in row]
                results.append(dict(zip(columns, processed_row)))
        else:
             logger.info("La consulta no devolvió columnas (posiblemente INSERT/UPDATE/DELETE).")

        if needs_commit:
            logger.info("Realizando commit de la transacción.")
            conn.commit()

        return json.dumps(results, default=str)

    except pyodbc.Error as e:
        logger.error(f"Error ejecutando la consulta (SQLSTATE: {e.args[0]}): {str(e)}")
        if conn and needs_commit:
            try:
                logger.warning("Realizando rollback debido a error.")
                conn.rollback()
            except pyodbc.Error as rb_e:
                 logger.error(f"Error durante el rollback: {rb_e}")

        raise Exception(f"Error ejecutando consulta: {str(e)}") from e
    except Exception as e:
        logger.error(f"Error inesperado durante la ejecución de la consulta: {str(e)}")
        raise # Relanza el error inesperado
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
            logger.info("Conexión cerrada.")