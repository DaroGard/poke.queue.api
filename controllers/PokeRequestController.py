import os
import json
import logging

from fastapi import HTTPException
from models.PokeRequest import PokeRequest
from utils.database import execute_query_json
from utils.AQueue import AQueue
from utils.ABlob import ABlob
from azure.storage.blob import BlobServiceClient

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def select_poke_request( id : int ):
    try:
        query = "select * from pokequeue.requests where id = ?"
        params = (id,)
        result = await execute_query_json(query, params)
        result_dict = json.loads(result)
        return result_dict
    except Exception as e:
        logger.error(f"Error selecting report request {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

async def update_poke_request(poke_request: PokeRequest) -> dict:
    try:
        query = "exec pokequeue.update_poke_request ?, ?, ?"
        if not poke_request.url:
            poke_request.url = "";
        
        params = (poke_request.id, poke_request.status, poke_request.url)
        result = await execute_query_json(query, params, True)
        result_dict = json.loads(result)
        return result_dict
    except Exception as e:
        logger.error(f"Error updating report request {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

async def insert_poke_request(poke_request: PokeRequest) -> dict:
    try:
        query = "exec pokequeue.create_poke_request ?, ?" #Tarea 3: Modifica el endpoint de creación para aceptar el nuevo parámetro (sample_size ).
        params = (poke_request.pokemon_type, poke_request.sample_size ) #Tarea 3
        result = await execute_query_json(query, params, True)
        result_dict = json.loads(result)
        
        await AQueue().insert_message_on_queue(result)

        return result_dict
    except Exception as e:
        logger.error(f"Error Inserting report request {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
async def get_all_request() -> dict:
    query = """
        SELECT
            r.id as ReportId
            , s.description as Status
            , r.type as PokemonType
            , r.sample_size as SampleSize
            , r.url
            , r.created
            , r.updated
        FROM pokequeue.requests r
        INNER JOIN pokequeue.status s
        ON r.id_status = s.id
    """
    result = await execute_query_json (query)
    result_dict = json.loads(result)
    blob = ABlob()
    for record in result_dict:
        id = record['ReportId']
        record['url'] = f"{record['url']}?{blob.generate_sas(id)}"
    return result_dict



# Tarea 1: Implementar Eliminación Completa de Reportes
async def delete_poke_report(report_id: int):
    #Verificar que el reporte existe en Azure SQL DB.
    select_query = "SELECT * FROM pokequeue.requests WHERE id = ?"
    report = await execute_query_json(select_query, (report_id,))
    report_list = json.loads(report)

    if not report_list:
        # Manejar posibles errores
        raise HTTPException(status_code=404, detail="Report not found")

    try:
        container_name = os.getenv("AZURE_STORAGE_CONTAINER")
        blob_name = f"poke_report_{report_id}.csv"
        blob_service_client = BlobServiceClient.from_connection_string(
            os.getenv("AZURE_STORAGE_CONNECTION_STRING")
        )
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=blob_name)
        #Eliminar el archivo CSV correspondiente
        if blob_client.exists():
            blob_client.delete_blob()
        else:
            # Manejar posibles errores
            logger.error(f"Blob '{blob_name}' no encontrado, se continúa con la eliminación del registro en BD.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting blob: {str(e)}")
    # Eliminar el registro del reporte de la tabla en Azure SQL DB
    try:
        delete_query = "DELETE FROM pokequeue.requests WHERE id = ?"
        await execute_query_json(delete_query, (report_id,), needs_commit=True)
    except Exception as e:
        # Manejar posibles errores
        raise HTTPException(status_code=500, detail=f"Error deleting from database: {str(e)}")

    return {"detail": "Report deleted correctly"}