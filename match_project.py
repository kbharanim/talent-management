import psycopg2
from pgvector.psycopg2 import register_vector
import numpy as np
import json

DB_HOST = "localhost"
DB_NAME = "lxp"
DB_USER = "postgres"
DB_PASS = "postgres"

def get_conn():
    conn = psycopg2.connect(host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASS)
    register_vector(conn)
    return conn

def cosine_similarity(a, b):
    a = np.array(a, dtype=np.float32)
    b = np.array(b, dtype=np.float32)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

def match_project(project_id, top_n=5):
    conn = get_conn()
    cur = conn.cursor()
    
    # Get project embedding and required skills
    cur.execute("SELECT project_embedding, required_skills FROM projects WHERE project_id=%s", (project_id,))
    proj_row = cur.fetchone()
    if not proj_row:
        print("Project not found")
        return []
    
    proj_emb, required_skills = proj_row

    # ✅ Convert embeddings & skills safely
    proj_emb = np.array(proj_emb, dtype=np.float32)
    if isinstance(required_skills, str):
        required_skills = json.loads(required_skills)
    elif required_skills is None:
        required_skills = {}

    # Get all users
    cur.execute("SELECT user_id, full_name, profile_embedding FROM users")
    users = cur.fetchall()
    
    results = []
    for u_id, u_name, u_emb in users:
        u_emb = np.array(u_emb, dtype=np.float32)  # ✅ Ensure vector is numeric
        sim = cosine_similarity(u_emb, proj_emb)
        
        # Get user's skills
        cur.execute("""
            SELECT s.skill_name, us.proficiency_score 
            FROM user_skills us 
            JOIN skills s ON s.skill_id = us.skill_id 
            WHERE us.user_id=%s
        """, (u_id,))
        user_skills = {row[0]: row[1] for row in cur.fetchall()}
        
        skill_gap = {}
        for skill, req_score in required_skills.items():
            user_score = user_skills.get(skill, 0)
            skill_gap[skill] = max(0, req_score*20 - user_score)
        
        results.append({
            "user_id": u_id,
            "name": u_name,
            "similarity": round(sim, 3),
            "skill_gap": skill_gap
        })
    
    # Sort by similarity descending
    results = sorted(results, key=lambda x: x["similarity"], reverse=True)
    conn.close()
    return results[:top_n]


project_id = "058fc63c-4246-4f97-aacd-c8e67ba2c397"  # Replace with real ID from ingest_project.py
matches = match_project(project_id)
print("Top Candidates:")
for m in matches:
    print(m)