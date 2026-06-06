from stores.llm.LLMInterface import LLMInterface
from stores.llm.LLMEnums import CohereEnums, DocumentTypeEnum
import cohere
import logging 

class CohereProvider(LLMInterface):
    
    def __init__(self, api_key: str, 
                default_input_max_characters:int=1000,  # to save the budget, it is okay to modify this max value, but for now make the default 1000 
                default_generation_max_output_tokens: int=1000,
                default_generation_temperature:float=0.1): 
        
        self.api_key = api_key
        
        self.default_input_max_characters = default_input_max_characters
        self.default_generation_max_output_tokens = default_generation_max_output_tokens
        self.default_generation_temperature = default_generation_temperature
        
        # -----------------------------
        self.generation_model_id = None
        
        self.embedding_model_id = None
        self.embedding_size = None
        
        self.client = cohere.Client(api_key=self.api_key)
        
        self.enums = CohereEnums
        
        self.logger = logging.getLogger(__name__)
        
        
    def set_generation_model(self, model_id: str):
        self.generation_model_id = model_id
        
    def set_embedding_model(self, model_id: str, embedding_size: int):
        self.embedding_model_id = model_id
        self.embedding_size = embedding_size
        
    def process_text(self, text:str): # helper method, it is okay not to be included to the interface (maybe the other providers does not use it)    
        return text[:self.default_input_max_characters].strip()

    def generate_text(self, prompt:str, chat_history:list=[], max_output_token:int=None, temperature:float=None):    
        if not self.client:
            # raise ValueError("Problem in embed_text function")
            self.logger.error(f"OpenAI client was not set")
            return None
        
        if not self.generation_model_id:
            self.logger.error(f"Generation model for OpenAI was not set")
        
        max_output_token = max_output_token if max_output_token is not None else self.default_generation_max_output_tokens
        temperature = temperature if temperature is not None else self.default_generation_temperature
        
        response = self.client.chat(
            model=self.generation_model_id,
            chat_history=chat_history,
            message = self.process_text(prompt), 
            temperature= temperature,
            max_tokens=max_output_token
        ) 
        
        if not response or not response.text:
            self.logger.error(f"Error while generating text with Cohere")
    
        return response.text
        
    def embed_text(self, text:str, document_type:str=None): # document_type: knowing if it is a document can improve the vector quality than if it is a query
        if not self.client:
            self.logger.error(f"Cohere client was not set")
            return None
        
        if not self.embedding_model_id:
            self.logger.error(f"Embedding model for Cohere was not set")
        
        input_type = CohereEnums.DOCUMENT.value
        if document_type == DocumentTypeEnum.QUERY.value:
            input_type = CohereEnums.QUERY.value
        
        response = self.client.embed(
            model = self.embedding_model_id,
            texts = [self.process_text(text)], # texts = [self.process_text(t) for t in text], 
            input_type=input_type,
            embedding_types=["float"] # HIII 4
        )
        
        
        if not response or not response.embeddings or not response.embeddings.float: # or not response.embeddings.float # HIII 4
            self.logger.error(f"Error while embedding text with Cohere")
            return None
        
        return response.embeddings.float[0] # response.embeddings[0] # response.embeddings.float[0] # HIII4
    
    def construct_prompt(self, prompt:str, role:str):
        return {
            "role":role,
            "text":self.process_text(prompt)
        }