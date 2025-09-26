import uuid
import json
import psycopg2
from pgvector.psycopg2 import register_vector
from sentence_transformers import SentenceTransformer
from sample import SAMPLE_PROJECTS

DB_HOST = "localhost"
DB_NAME = "lxp"
DB_USER = "postgres"
DB_PASS = "postgres"

model = SentenceTransformer("all-MiniLM-L6-v2")

def get_conn():
    conn = psycopg2.connect(host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASS)
    register_vector(conn)
    return conn

def insert_project(proj):
    conn = get_conn()
    cur = conn.cursor()
    project_id = str(uuid.uuid4())
    emb = model.encode(proj["project_description"]).astype("float32").tolist()

    cur.execute(
        """
        INSERT INTO projects (project_id, project_name, project_description, required_skills, project_embedding)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (project_id, proj["project_name"], proj["project_description"], json.dumps(proj["required_skills"]), emb)
    )

    conn.commit()
    cur.close()
    conn.close()

    print(f"Inserted project: {proj['project_name']} (ID: {project_id})")
    return project_id


# project_id = insert_project(SAMPLE_PROJECTS)
# print("Inserted project ID:", project_id)

# print("Hello")

for p in SAMPLE_PROJECTS:
    insert_project(p)