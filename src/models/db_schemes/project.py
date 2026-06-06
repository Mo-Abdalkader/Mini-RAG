from pydantic import BaseModel, Field, validator
from typing import Optional
from bson.objectid import ObjectId

class Project(BaseModel):
    id: Optional [ObjectId] = Field(None, alias="_id")  # None it is optional | consider the ObjectId as a str
    
    project_id: str  = Field(..., min_length=1) # This value should be at least one char
    
    
    # We can create a custom validator
    @validator("project_id")
    def validate_project_id(cls, value):
        if not value.isalnum():
            raise ValueError("project_id must be alphanumeric")
        
        return value
    
    class Config:
        # Telling pydantic not to raise an error if you find a starge data type
        arbitrary_types_allowed = True # If i skipped this part Pydantic will raise an error because it does not recogniz the type of "ObjectID" from bson 
        
        
    @classmethod
    def get_indices(cls):
        return [
            {
                "key":[
                    ("project_id", 1) # 1 ASC, -1 DSC
                ],
                "name":"project_id_index_1",
                "unique":True, # If you fine this id before raise error
            }
        ]