import uvicorn
import json
from fastapi import FastAPI
from utils.database import execute_query_json
from controllers.PokeRequestController import insert_poke_request, update_poke_request, select_poke_request, get_all_request, delete_poke_report
from models.PokeRequest import PokeRequest
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    query = "SELECT * FROM pokequeue.MESSAGES"
    result = await execute_query_json(query)
    result_dict = json.loads(result)
    return result_dict

@app.get("/api/version")
async def version():
    return {"Version" : "1.0.0"}

@app.get("/api/request/{id}")
async def select_request(id : int):
    return await select_poke_request(id)

@app.get("/api/request")
async def select_all_request():
    return await get_all_request()

@app.post("/api/request")
async def create_request(poke_request: PokeRequest):
    return await insert_poke_request(poke_request)

@app.put("/api/request")
async def update_request(poke_request: PokeRequest):
    return await update_poke_request(poke_request)

# Tarea 1: Crea un nuevo endpoint en la API (ej. DELETE /api/report/{report_id} )
@app.delete("/api/report/{report_id}")
async def delete_request(report_id: int):
    return await delete_poke_report(report_id)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)