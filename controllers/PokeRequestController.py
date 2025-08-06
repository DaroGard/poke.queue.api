import json
import logging

from fastapi import HTTPException
from models.PokeRequest import PokeRequest
from utils.database import execute_query_json
from utils.AQueue import AQueue

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
        query = "exec pokequeue.create_poke_request ?"
        params = (poke_request.pokemon_type, )
        result = await execute_query_json(query, params, True)
        result_dict = json.loads(result)
        
        await AQueue().insert_message_on_queue(result)

        return result_dict
    except Exception as e:
        logger.error(f"Error Inserting report request {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")