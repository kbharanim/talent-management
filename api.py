from fastapi import FastAPI
from ingest_resume import insert_user
from ingest_project import insert_project
from match_project import match_project
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Enable CORS so React can talk to API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ResumeIn(BaseModel):
    full_name: str
    profile_text: str
    skills: dict = {}

class ProjectIn(BaseModel):
    project_name: str
    project_description: str
    required_skills: dict

@app.post("/ingest/resume")
def ingest_resume(r: ResumeIn):
    uid = insert_user(r.dict())
    return {"user_id": uid}

@app.post("/ingest/project")
def ingest_project_endpoint(p: ProjectIn):
    pid = insert_project(p.dict())
    return {"project_id": pid}

@app.get("/match/project/{project_id}")
def match_project_endpoint(project_id: str):
    res = match_project(project_id)
    if not res:
        return {"error":"Project not found"}
    return {"project_id": project_id, "candidates": res}