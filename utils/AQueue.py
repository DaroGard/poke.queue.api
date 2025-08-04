import os #Para cargar variables de ambiente
from azure.storage.queue import QueueClient, BinaryBase64DecodePolicy, BinaryBase64EncodePolicy #Instalar nueva libreria
from dotenv import load_dotenv

load_dotenv()

class AQueue:
    def __init__(self):
        self.azure_sak = os.getenv('AZURE_SAK')
        self.queue_name = os.getenv('QUEUE_NAME')
        self.queue_client = QueueClient.from_connection_string(self.azure_sak, self.queue_name) #Creacion del cliente
        self.queue_client.message_decode_policy = BinaryBase64DecodePolicy() #Decorador para decodificacion
        self.queue_client.message_encode_policy = BinaryBase64EncodePolicy() #Decorador para codificacion

    async def insert_message_on_queue(self, message: str): #Metodo para realizar insercion del mensaje.
        message_bytes = message.encode('utf-8')
        self.queue_client.send_message(
            self.queue_client.message_encode_policy.encode(message_bytes)
        )