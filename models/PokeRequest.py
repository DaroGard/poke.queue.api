from pydantic import BaseModel, Field
from typing import Optional

class PokeRequest(BaseModel):
    id: Optional[int] = Field(
        default=None,
        ge=1,
        description="Request ID"
    )

    pokemon_type: Optional[str] = Field(
        default=None,
        description="Pokemon Type",
        pattern="^[a-zA-Z0-9_]+$"
    )

    url: Optional[str] = Field(
        default=None,
        description="Request URL",
        pattern="^https?://[^\s]+$"
    )

    status: Optional[str] = Field(
        default=None,
        description="Request Status",
        pattern="^(sent|completed|failed|inprogress)$"
    )

    #Tarea 3: Actualiza el modelo Pydantic (opcional, gt=0 ).
    sample_size: Optional[int] = Field(
        default=None, 
        gt=0
    )