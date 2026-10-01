from .BaseDataModel import BaseDataModel
from .db_schemes import Project
from .enums.DataBaseEnum import DataBaseEnum

class ProjectModel(BaseDataModel):
    def __init__(self, db_client: object):
        super().__init__(db_client)
        
        # Set the collection name and collection object for projects
        self.collection_name = DataBaseEnum.COLLECTION_PROJECT_NAME.value
        self.collection = self.db_client[self.collection_name]
    
    # Create a new project in the database    
    async def create_project(self, project: Project):
        project_dict = project.model_dump(exclude_unset=True)  # Convert Pydantic model to dictionary, excluding unset fields
        result = await self.collection.insert_one(project_dict)
        return str(result.inserted_id)
    
    # Retrieve a project by its project_id, or create a new one if it doesn't exist
    async def get_project_or_create_one(self, project_id: str):
        
        project = await self.collection.find_one({"project_id": project_id})
        if project:
            return Project(**project) # Return the existing project as a Pydantic model
        else:
            # Create a new project if it doesn't exist
            # Create a new Project instance with the provided project_id
            print(f"Project with ID {project_id} not found. Creating a new project.")
            new_project = Project(project_id=project_id)
            await self.create_project(new_project)
            return new_project
        
        
    
    async  def get_all_projects(self, page: int = 1, page_size: int = 10):
        
        # Calculate the number of documents to skip based on the page and page_size
        total_documents = await self.collection.count_documents({})
        
        # calculate number of pages based on total documents and page size
        total_pages = (total_documents + page_size - 1) // page_size
        
        
        skip = (page - 1) * page_size
        cursor = self.collection.find().skip(skip).limit(page_size)
        
        projects = []
        async for doc in cursor:
            projects.append(Project(**doc))
        return projects, total_pages