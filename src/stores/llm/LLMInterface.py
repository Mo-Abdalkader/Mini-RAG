from abc import ABC, abstractmethod

class LLMInterface(ABC):
    
    @abstractmethod
    def set_generation_model(self, model_id:str):
        pass
    
    @abstractmethod
    def set_embedding_model(self, model_id:str, embedding_size: int):
        pass
    
    @abstractmethod
    def generate_text(self, prompt:str, chat_history:list=[], max_output_token:int=None, temperature:float=None):
        pass
    
    @abstractmethod
    def embed_text(self, text:str, document_type:str=None): # document_type: knowing if it is a document can improve the vector quality than if it is a query
        pass
    
    @abstractmethod
    def construct_prompt(self, prompt:str, role:str): # to rephrase the prompt, apply some kind or process before passing the prompt to the model
        pass
    
    