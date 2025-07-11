import sqlite3
from datetime import datetime
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from pydantic import BaseModel
from typing import List, Dict
from dotenv import load_dotenv
import uvicorn
from os import getenv

from stylemail import seed_user_style, generate_email, generate_nudge_summary, generate_nudge_email
from stylemail.vectorstore import UserVectorStore
from stylemail.config import Config
from services import get_auth_token, get_nudge_data

# Load environment variables
load_dotenv()

def create_employee_nudge_summary_table():
    """Create the employee_nudge_summary table in SQLite if it doesn't exist."""
    try:
        sql_connection = sqlite3.connect("laudio_client1.db")
        print("[server] SQLite connection successful.")
        
        # Create table if it doesn't exist
        cursor = sql_connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS employee_nudge_summary (
                employee_id INT PRIMARY KEY,
                created_date DATETIME DEFAULT CURRENT_TIMESTAMP,
                summary TEXT,
                nudge_snippet TEXT
            );
        ''')
        sql_connection.commit()
        cursor.close()
    except Exception as e:
        print(f"[server] SQLite connection failed: {e}")


config: Config = None
store: UserVectorStore = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global config

    redis_host = getenv("REDIS_HOST")
    redis_port = getenv("REDIS_PORT")
    redis_db = int(getenv("REDIS_DB")) if getenv("REDIS_DB") else None
    redis_password = getenv("REDIS_PASSWORD")
    openai_api_key = getenv("OPENAI_API_KEY")

    auth_part = f":{redis_password}@" if redis_password else ""

    config = Config.load(
        openai_api_key=openai_api_key,
        redis_host=redis_host,
        redis_port=redis_port,
        redis_db=redis_db,
        redis_password=redis_password,
    )
    print("[server] Loaded config:", config)
    global store
    store = UserVectorStore(
        host=config.redis_host,
        port=config.redis_port,
        db=config.redis_db,
        password=config.redis_password,
    )
    # Connect to SQLite and create table
    create_employee_nudge_summary_table()

    try:
        pong = store.redis.ping()
        print(f"[server] Redis connection successful: {pong}")
    except Exception as e:
        print(f"[server] Redis connection failed: {e}")

    yield


app = FastAPI(lifespan=lifespan)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


@app.get("/health")
def health_check():
    """Health check endpoint to verify the API is running."""
    return {
        "status": "healthy",
        "redis": "connected" if store and store.redis.ping() else "disconnected",
        "message": "StyleMail API is running"
    }


class SeedRequest(BaseModel):
    user_id: str
    samples: list[str]


class GenerateRequest(BaseModel):
    user_id: str
    subject: str
    prompt: str


@app.post("/seed")
def seed(req: SeedRequest):
    try:
        seed_user_style(req.user_id, req.samples, store=store, openai_api_key=config.openai_api_key)
        return {"status": "ok"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


class NudgeSummaryRequest(BaseModel):
    user_id: str
    prompt: str
    nudges: List[Dict[str, str]]


@app.post("/generate")
def generate(req: GenerateRequest):
    try:
        result = generate_email(req.user_id, req.subject, req.prompt, store=store, openai_api_key=config.openai_api_key)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


class FetchNudgeDataRequest(BaseModel):
    user_id: str
    prompt: str
    email: str
    password: str
    employee_id: str

@app.post("/fetch-nudge-data")
def fetch_nudge_data(req: FetchNudgeDataRequest):
    try:
        # Get authentication token
        auth_token = get_auth_token(req.email, req.password)
        
        nudge_data = get_nudge_data(auth_token, req.employee_id)
        
        return nudge_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/nudge-email")
def nudge_email(req: FetchNudgeDataRequest):
    try:
        # Get authentication token
        auth_token = get_auth_token(req.email, req.password)
        
        # Fetch nudge data
        nudge_data = get_nudge_data(auth_token, req.employee_id)
        
        # Prepare nudge data for email generation
        nudges = [
            {
                "title": nudge.get("config", {}).get("message", "No Title"),
                "instructions": nudge.get("config", {}).get("metaData", "No Instructions"),
                "metrics": (
                    f"Threshold: {nudge.get('config', {}).get('threshold', 'N/A')}, "
                    f"Date Range: {nudge.get('config', {}).get('dateRange', {}).get('from', 'N/A')} to {nudge.get('config', {}).get('dateRange', {}).get('to', 'N/A')}, "
                    f"Prior Date Range: {nudge.get('config', {}).get('priorDateRange', {}).get('from', 'N/A')} to {nudge.get('config', {}).get('priorDateRange', {}).get('to', 'N/A')}, "
                    f"Metric: {nudge.get('config', {}).get('metric', 'N/A')}, "
                    f"Unit: {nudge.get('config', {}).get('unit', 'N/A')}, "
                    f"Operator: {nudge.get('config', {}).get('operator', 'N/A')}"
                )
            }
            for nudge in nudge_data.get("data", [])
        ]

        # Generate nudge email
        result = generate_nudge_email(req.user_id, req.prompt, nudges, store=store, openai_api_key=config.openai_api_key)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/nudge-summary")
def nudge_summary(req: FetchNudgeDataRequest):
    try:
        # Get authentication token
        auth_token = get_auth_token(req.email, req.password)
        
        # Fetch nudge data
        nudge_data = get_nudge_data(auth_token, req.employee_id)
        
        print(f"[nudge_summary] Fetched nudge data: {len(nudge_data.get('data', []))}")
        # Prepare nudge data for summary generation
        nudges = [
            {
                "title": nudge.get("config", {}).get("message", "No Title"),
                "instructions": nudge.get("config", {}).get("metaData", "No Instructions"),
                "metrics": (
                    f"Threshold: {nudge.get('config', {}).get('threshold', 'N/A')}, "
                    f"Date Range: {nudge.get('config', {}).get('dateRange', {}).get('from', 'N/A')} to {nudge.get('config', {}).get('dateRange', {}).get('to', 'N/A')}, "
                    f"Prior Date Range: {nudge.get('config', {}).get('priorDateRange', {}).get('from', 'N/A')} to {nudge.get('config', {}).get('priorDateRange', {}).get('to', 'N/A')}, "
                    f"Metric: {nudge.get('config', {}).get('metric', 'N/A')}, "
                    f"Unit: {nudge.get('config', {}).get('unit', 'N/A')}, "
                    f"Operator: {nudge.get('config', {}).get('operator', 'N/A')}"
                )
            }
            for nudge in nudge_data.get("data", [])
        ]

        # Prepare nudge snippet for comparison
        nudge_snippet = ", ".join([nudge.get("title", "No Title") for nudge in nudges])

        # Check if summary already exists with matching nudge snippet
        sql_connection = sqlite3.connect("laudio_client1.db")
        cursor = sql_connection.cursor()
        cursor.execute("SELECT summary FROM employee_nudge_summary WHERE employee_id = ?", (req.employee_id,))
        existing_summary = cursor.fetchone()

        cursor.execute("SELECT nudge_snippet FROM employee_nudge_summary WHERE employee_id = ?", (req.employee_id,))
        existing_nudge_snippet = cursor.fetchone()
        if existing_nudge_snippet and existing_nudge_snippet[0] == nudge_snippet:
            return {"summary": existing_summary[0]}

        if existing_summary:
            return {"summary": existing_summary[0]}

        # Generate nudge summary
        result = generate_nudge_summary(req.employee_id, req.prompt, nudges, store=store, openai_api_key=config.openai_api_key)

        # Insert new summary into the database
        nudge_snippet = ", ".join([nudge.get("title", "No Title") for nudge in nudges])
        cursor.execute(
            "INSERT INTO employee_nudge_summary (employee_id, created_date, summary, nudge_snippet) VALUES (?, ?, ?, ?)",
            (req.employee_id, datetime.now(), result["summary"], nudge_snippet)
        )
        sql_connection.commit()
        cursor.close()

        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
