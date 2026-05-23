from enum import Enum

class VectorDBEnums(Enum):
    QDRANT = "QDRANT" # This is a 'Memory based database' unlike mongodb which is 'Engine based database' 
    
class DistanceMethodEnums(Enum):
    COSINE = "cosine"
    DOT = "dot"