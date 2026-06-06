from .BaseController import BaseController
from models.db_schemes import Project, DataChunk
from stores.llm.LLMEnums import DocumentTypeEnum

import json
from typing import List

class NLPController(BaseController):
    
    def __init__(self, vectordb_client, generation_client, embedding_client, template_parser):
        super().__init__()
        
        self.vectordb_client  = vectordb_client
        self.generation_client = generation_client
        self.embedding_client  = embedding_client
        self.template_parser = template_parser
        
    def create_collection_name(self, project_id:str):
        return f"collection_{project_id}".strip()
    
    def reset_vector_db_collection(self, project: Project):
        collection_name = self.create_collection_name(project_id=project.project_id)
        self.vectordb_client.delete_collection(collection_name=collection_name)
        
    def get_vector_db_collection_info(self, project: Project):
        collection_name = self.create_collection_name(project_id=project.project_id)
        collection_info = self.vectordb_client.get_collection_info(collection_name=collection_name)
                
        return json.loads(
            json.dumps(collection_info, default=lambda x:x.__dict__)
        )
    
    def index_into_vector_db(self, project: Project, chunks: List[DataChunk], chunks_ids: List[int], do_reset: bool = False):
        # step 1 : get collection name
        collection_name = self.create_collection_name(project_id=project.project_id)
        
        # step 2 : manage items
        texts  = [c.chunk_text for c in chunks]
        metadata = [c.chunk_metadata for c in chunks]
        vectors = [
            self.embedding_client.embed_text(text=text, document_type=DocumentTypeEnum.DOCUMENT.value)
            
            for text in texts
        ]
        
        # step 3 : create collection if not exists
        _ = self.vectordb_client.create_collection(
            collection_name=collection_name,
            embedding_size = self.embedding_client.embedding_size,
            do_reset=do_reset,
        )
        
        # step 4 : insert into vector db
        _ = self.vectordb_client.insert_many(
            collection_name=collection_name,
            texts=texts,
            metadata=metadata,
            vectors=vectors,
            record_ids=chunks_ids
        )
        
        return True
    
    def search_vector_db_collection(self, project: Project, text: str, limit: int = 10):
        # step 1: get collection name
        collection_name = self.create_collection_name(project_id=project.project_id)
        
        # ste2 : get text embedding vector
        vector = self.embedding_client.embed_text(text=text,
                                                 document_type=DocumentTypeEnum.QUERY.value)
        
        if not vector or len(vector) == 0:
            return False
        
        # step 3: do semantic search
        results = self.vectordb_client.search_by_vector(
            collection_name= collection_name,
            vector=vector,
            limit=limit
        )
        
        if not results:
            return False
        
        return results # we updated the 'search_by_vector' function so now it returns a dict no need to convert it 
        
        # return json.loads(
        #     json.dumps(results, default=lambda x:x.__dict__)
        # )
        
        
    def answer_rag_question(self, project: Project, query: str, limit: int = 10):
        
        # step 1: retrieve related document
        retrieved_document = self.search_vector_db_collection(
            project=project,
            text=query,
            limit=limit
            )
        
        if not retrieved_document or len(retrieved_document) == 0:
            return None, None, None # Because the call is waiting for 3 variables
        
        # ste2: construct system prompt
        system_prompt = self.template_parser.get("rag", "system_prompt")
        
        # document_prompts = []
        # for idx, doc in enumerate(retrieved_document):
        #     document_prompts.append(
        #         self.template_parser.get("rag", "document_prompt", {
        #             "doc_num": idx+1,
        #             "chunk_text": doc.text,
        #         })
        #     )
            
        # Use comprehension list instead
        
        document_prompts = "\n".join([
            self.template_parser.get("rag", "document_prompt", {
                    "doc_num": idx+1,
                    "chunk_text": doc.text,
                })
            
            for idx, doc in enumerate(retrieved_document)
        ])
        
        footer_prompt = self.template_parser.get("rag", "footer_prompt",{
            "query":query
        })
        
        chat_history = [
            # Add the system prompt once at the beginning of the chat history before the current one  
            self.generation_client.construct_prompt(
                prompt=system_prompt,
                role=self.generation_client.enums.SYSTEM.value,
            )
        ]
        
        full_prompt = "\n\n".join([document_prompts, footer_prompt])
        
#         full_prompt = """You are a strict QA assistant. Answer the question at the end using only the context provided below.

# Context:
# 1. Khaled works at Al-Majd Software Company as a network engineer. His monthly salary is $4500, and he is Ibrahim's cousin and Ahmed's brother.
# 2. The company's secret project carries the code name 'Phoenix 99', and its files are stored in safe number 4 on the third floor.

# Question: How much is Khaled's monthly salary and what is his job title?
# Answer:
# """
        
        answer = self.generation_client.generate_text(
            prompt = full_prompt,
            chat_history=chat_history,
        )
        
        return answer, full_prompt, chat_history