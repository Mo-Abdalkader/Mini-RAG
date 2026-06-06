from .BaseDataModel import BaseDataModel
from .db_schemes import Project
from .enums.DatabaseEnum import DataBaseEnum

class ProjectModel(BaseDataModel):
    def __init__(self, db_client):
        super().__init__(db_client)
        self.collection = self.db_client[DataBaseEnum.COLLECTION_PROJECT_NAME.value]
        
    # Important - Review this function again
    @classmethod
    async def create_instance(cls, db_client:object):
        instance = cls(db_client)
        await instance.init_collection()
        return instance
        
    # We should call the init collection function at the init of the project, but it can't be called there because the init can not be async so, will create another function to call both of them
    async def init_collection(self):
        all_collections = await self.db_client.list_collection_names()
        
        if DataBaseEnum.COLLECTION_PROJECT_NAME.value not in all_collections:
            self.collection = self.db_client[DataBaseEnum.COLLECTION_PROJECT_NAME.value]
            
            indices = Project.get_indices()
            for index in indices:
                await self.collection.create_index(
                    index["key"],
                    name=index["name"],
                    unique=index["unique"]
                )
            
    
    async def create_project(self, project: Project): # NOTE: collection is a motor object so it should be a async
        result = await self.collection.insert_one(project.dict(by_alias=True, exclude_unset=True)) # Insert_one takes a dict so we need to convert the project pydantic into dict
        # by_alias=True      -> to use the `_id` alias name
        # exclude_unset=True -> to remove all of the unset values and do not add it to the database (we have to fill it to prevent ignoring)
        
        # We need to await to wait to collect the data | If we didn't we will face and error 
        project.id = result.inserted_id
        return project
    
    async def get_project_or_create_one(self, project_id: str):
        record = await self.collection.find_one({
            "project_id": project_id
        }) # there is .fine({}) to find everything that matches
        
        if record is None:
            # create new project
            project = Project(project_id=project_id)
            project = await self.create_project(project=project)
            
            return project
        
        return Project(**record)
    
    # We can not just import all of the pages at once, it is not efficient, so we need to use pagination, import a bunch by a bunch
    async def get_all_projects(self, page:int = 1, page_size:int = 10):
        # count total number of documents
        total_documents = self.collection.count_documents({}) # the dict is like a filter, but we need to count all of the records NO FILTERS!
        
        # calculate total number of pages
        total_pages = total_documents // page_size
        if total_documents % page_size > 0: # instead of math.ceil(total_documents/page_size)
            total_pages += 1
            
        cursor = self.collection.find().skip((page-1) * page_size).limit(page_size) # In the current page we need to skip the precious content 
        # document = list(cursor) # It is okay but it is not memory efficient
        projects = []
        async for document in cursor:
            projects.append(
                Project(**document)
            )
        
        return projects, total_pages