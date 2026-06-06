from stores.llm.LLMInterface import LLMInterface # ..LLMInterface
from stores.llm.LLMEnums import OpenAIEnums
from openai import OpenAI
import logging

class OpenAIProvider(LLMInterface):
    def __init__(self, api_key: str, 
                 api_url:str = None, # OpenAI also can be used with something like Ollama, but we must define the URL or ollama instead of the default one of OpenAI
                 default_input_max_characters:int=1000,  # to save the budget, it is okay to modify this max value, but for now make the default 1000 
                 default_generation_max_output_tokens: int=1000,
                 default_generation_temperature:float=0.1): 
        self.api_key = api_key
        self.api_url = api_url
        
        self.default_input_max_characters = default_input_max_characters
        self.default_generation_max_output_tokens = default_generation_max_output_tokens
        self.default_generation_temperature = default_generation_temperature
        
        # -----------------------------
        self.generation_model_id = None
        
        self.embedding_model_id = None
        self.embedding_size = None
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.api_url if self.api_url and len(self.api_url) else None # To avoid taking the url='' from the .env file 
        )
         
        self.enums = OpenAIEnums
        
        self.logger = logging.getLogger(__name__)
        # ----------------------------
        
    def set_generation_model(self, model_id: str):
        self.generation_model_id = model_id
        
    def set_embedding_model(self, model_id: str, embedding_size: int):
        self.generation_model_id = model_id
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
        
        chat_history.append(
            self.construct_prompt(prompt=prompt, role=OpenAIEnums.USER.value)
        )
        
        response = self.client.chat.completions.create(
            messages=chat_history,
            model=self.generation_model_id,
            max_tokens=max_output_token,
            temperature=temperature,
            
            extra_body={"num_ctx": 8192},
        )
        
        if not response or not response.choices or len(response.choices) == 0 or not response.choices[0].message:
            self.logger.error(f"Error while generating text with OpenAI") # User message should not be added to the logger
            return None
        # raise NotImplementedError

        return response.choices[0].message.content
        
        
    def embed_text(self, text:str, document_type:str=None): # document_type: knowing if it is a document can improve the vector quality than if it is a query
        if not self.client:
            # raise ValueError("Problem in embed_text function")
            self.logger.error(f"OpenAI client was not set")
            return None
        
        if not self.embedding_model_id:
            self.logger.error(f"Embedding model for OpenAI was not set")
            
        
        response = self.client.embeddings.create(
            input=text,
            model=self.embedding_model_id,
        )
        
        if not response or not response.data or len(response.data) == 0 or not response.data[0].embedding:
            self.logger.error(f"Error while embedding text with OpenAI")
            return None
        
        return response.data[0].embedding
    
    def construct_prompt(self, prompt:str, role:str):
        return {
            "role":role,
            "content":self.process_text(prompt)
        }
        
    