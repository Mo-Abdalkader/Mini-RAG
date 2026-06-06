from pydantic import BaseModel, Field, validator
from typing import Optional
from bson.objectid import ObjectId

class DataChunk(BaseModel):
    id: Optional [ObjectId] = Field(None, alias="_id")  # None it is optional 
    chunk_text: str = Field(..., min_length=1)          # ... means this field if required
    chunk_metadata: dict 
    chunk_order: int = Field(..., gt=0) # gt = greater than
    chunk_project_id: ObjectId
    chunk_asset_id: ObjectId
        
    class Config:
        arbitrary_types_allowed = True
        
    @classmethod
    def get_indices(cls):
        return [
            {
                "key":[
                    ("chunk_project_id", 1) # 1 ASC, -1 DSC
                ],
                "name":"chunk_project_id_index_1",
                "unique":False, # If you fine this id before raise error
            }
        ]
        
        
class RetrievedDocument(BaseModel):
    text: str
    score: float