from pydantic import BaseModel, Field, validator
from typing import Optional
from bson.objectid import ObjectId
from datetime import datetime

class Asset(BaseModel):
    id: Optional[ObjectId] = Field(None, alias="_id")
    asset_project_id: ObjectId
    asset_type: str = Field(..., min_length=1)
    asset_name: str = Field(..., min_length=1) # Like file name, but we said asset to be more general
    asset_size: int = Field(ge=0, default=None)
    asset_config: dict = Field(default=None)
    
    asset_pushed_at: datetime = Field(default=datetime.utcnow)
    
    
    
    class Config:
        # Telling pydantic not to raise an error if you find a strange data type
        arbitrary_types_allowed = True # If i skipped this part Pydantic will raise an error because it does not recogniz the type of "ObjectID" from bson 
        
        
    @classmethod
    def get_indices(cls):
        return [
            {
                "key":[
                    ("asset_project_id", 1) # 1 ASC, -1 DSC
                ],
                "name":"asset_project_id_index_1",
                "unique":False, # If you fine this id before raise error
            },{
                
                "key":[
                    ("asset_project_id", 1),
                    ("asset_name", 1)
                ],
                "name":"asset_project_id_name_index_1",
                "unique":True, 
            }
        ]