from pydantic import BaseModel

class TaskRequest(BaseModel):
    email: str
    secret: str
    url: str
