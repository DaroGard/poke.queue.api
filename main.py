import uvicorn
import json
from fastapi import FastAPI
from utils.database import execute_query_json
from controllers.PokeRequestController import insert_poke_request
from models.PokeRequest import PokeRequest
app = FastAPI()

@app.get("/")
async def root():
    query = "SELECT * FROM pokequeue.MESSAGES"
    result = await execute_query_json(query)
    result_dict = json.loads(result)
    return result_dict

@app.get("/api/version")
async def version():
    return {"Version" : "0.1.0"}

@app.post("/api/request")
async def create_request(poke_request: PokeRequest):
    return await insert_poke_request(poke_request)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)