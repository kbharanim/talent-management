-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Skills table
CREATE TABLE IF NOT EXISTS skills (
    skill_id UUID PRIMARY KEY,
    skill_name TEXT UNIQUE
);

-- Users table
CREATE TABLE IF NOT EXISTS users (
    user_id UUID PRIMARY KEY,
    full_name TEXT,
    profile_text TEXT,
    profile_embedding VECTOR(384)  -- embedding dimension
);

-- User skills table
CREATE TABLE IF NOT EXISTS user_skills (
    user_id UUID REFERENCES users(user_id),
    skill_id UUID REFERENCES skills(skill_id),
    proficiency_score INT,
    PRIMARY KEY(user_id, skill_id)
);

-- Projects table
CREATE TABLE IF NOT EXISTS projects (
    project_id UUID PRIMARY KEY,
    project_name TEXT,
    project_description TEXT,
    required_skills JSON,
    project_embedding VECTOR(384)  -- embedding dimension
);