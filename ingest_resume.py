import uuid
import psycopg2
from pgvector.psycopg2 import register_vector
from sentence_transformers import SentenceTransformer
from sample import SAMPLE_USERS

# DB connection
DB_HOST = "localhost"
DB_NAME = "lxp"
DB_USER = "postgres"
DB_PASS = "postgres"

model = SentenceTransformer("all-MiniLM-L6-v2")  # Embedding model

def get_conn():
    conn = psycopg2.connect(host=DB_HOST, dbname=DB_NAME, user=DB_USER, password=DB_PASS)
    register_vector(conn)
    return conn

def upsert_skill(cur, skill_name):
    cur.execute("SELECT skill_id FROM skills WHERE skill_name = %s", (skill_name,))
    r = cur.fetchone()
    if r:
        return r[0]
    skill_id = str(uuid.uuid4())
    cur.execute("INSERT INTO skills (skill_id, skill_name) VALUES (%s,%s)", (skill_id, skill_name))
    return skill_id

def insert_user(user):
    conn = get_conn()
    cur = conn.cursor()
    user_id = str(uuid.uuid4())
    emb = model.encode(user["profile_text"]).astype("float32").tolist()
    cur.execute(
        "INSERT INTO users (user_id, full_name, profile_text, profile_embedding) VALUES (%s,%s,%s,%s)",
        (user_id, user["full_name"], user["profile_text"], emb)
    )
    for sk, level in user.get("skills", {}).items():
        skill_id = upsert_skill(cur, sk)
        prof_score = int(level * 20)  # Scale 0-5 to 0-100
        cur.execute(
            "INSERT INTO user_skills (user_id, skill_id, proficiency_score) VALUES (%s,%s,%s)",
            (user_id, skill_id, prof_score)
        )
    conn.commit()
    cur.close()
    conn.close()
    print(f"Inserted user: {user['full_name']}")
    return user_id


for u in SAMPLE_USERS:
    insert_user(u)