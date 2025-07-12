import sqlite3
from datetime import datetime
from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from pydantic import BaseModel
from typing import List, Dict
from dotenv import load_dotenv
import uvicorn
from os import getenv
from sqlalchemy.orm import Session

from stylemail import seed_user_style, generate_email, generate_nudge_summary, generate_nudge_email
from stylemail.vectorstore import UserVectorStore
from stylemail.config import Config
from services import get_auth_token, get_nudge_data
from database import init_db, get_db, Employee, Nudge, NudgeSummary, NudgeEmail

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
    # Initialize PostgreSQL database
    init_db()
    
    # Connect to SQLite and create table (legacy support)
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
def fetch_nudge_data_endpoint(req: FetchNudgeDataRequest, db: Session = Depends(get_db)):
    """Fetch nudge data from PostgreSQL database"""
    try:
        # Query nudges for the employee
        nudges = db.query(Nudge).filter(
            Nudge.employee_id == req.employee_id,
            Nudge.status == "active"
        ).all()
        
        # Format nudges similar to API response
        nudge_data = {
            "data": [
                {
                    "id": nudge.id,
                    "config": {
                        "message": nudge.title,
                        "metaData": nudge.instructions,
                        "threshold": nudge.threshold,
                        "dateRange": {
                            "from": nudge.date_range_from.isoformat() if nudge.date_range_from else None,
                            "to": nudge.date_range_to.isoformat() if nudge.date_range_to else None
                        },
                        "priorDateRange": {
                            "from": nudge.prior_date_range_from.isoformat() if nudge.prior_date_range_from else None,
                            "to": nudge.prior_date_range_to.isoformat() if nudge.prior_date_range_to else None
                        },
                        "metric": nudge.metric_name,
                        "unit": nudge.unit,
                        "operator": nudge.operator
                    },
                    "nudge_type": nudge.nudge_type,
                    "metric_value": nudge.metric_value
                }
                for nudge in nudges
            ]
        }
        
        return nudge_data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/nudge-email")
def nudge_email_endpoint(req: FetchNudgeDataRequest, db: Session = Depends(get_db)):
    """Generate nudge email from PostgreSQL data"""
    try:
        # Query nudges for the employee
        nudges_data = db.query(Nudge).filter(
            Nudge.employee_id == req.employee_id,
            Nudge.status == "active"
        ).all()
        
        # Prepare nudge data for email generation
        nudges = [
            {
                "title": nudge.title,
                "instructions": nudge.instructions or "No Instructions",
                "metrics": (
                    f"Threshold: {nudge.threshold or 'N/A'}, "
                    f"Date Range: {nudge.date_range_from.isoformat() if nudge.date_range_from else 'N/A'} to {nudge.date_range_to.isoformat() if nudge.date_range_to else 'N/A'}, "
                    f"Prior Date Range: {nudge.prior_date_range_from.isoformat() if nudge.prior_date_range_from else 'N/A'} to {nudge.prior_date_range_to.isoformat() if nudge.prior_date_range_to else 'N/A'}, "
                    f"Metric: {nudge.metric_name or 'N/A'}, "
                    f"Value: {nudge.metric_value or 'N/A'}, "
                    f"Unit: {nudge.unit or 'N/A'}, "
                    f"Operator: {nudge.operator or 'N/A'}"
                )
            }
            for nudge in nudges_data
        ]

        # Generate nudge email
        result = generate_nudge_email(req.user_id, req.prompt, nudges, store=store, openai_api_key=config.openai_api_key)
        
        # Save generated email to database
        nudge_snippet = ", ".join([nudge["title"] for nudge in nudges])
        email_record = NudgeEmail(
            employee_id=req.employee_id,
            subject=result.get("subject", "Nudge Email"),
            body=result.get("body", ""),
            nudge_snippet=nudge_snippet
        )
        db.add(email_record)
        db.commit()
        
        return result
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/nudge-summary")
def nudge_summary_endpoint(req: FetchNudgeDataRequest, db: Session = Depends(get_db)):
    """Generate nudge summary from PostgreSQL data"""
    try:
        # Query nudges for the employee
        nudges_data = db.query(Nudge).filter(
            Nudge.employee_id == req.employee_id,
            Nudge.status == "active"
        ).all()
        
        print(f"[nudge_summary] Fetched {len(nudges_data)} nudges from database")
        
        # Prepare nudge data for summary generation
        nudges = [
            {
                "title": nudge.title,
                "instructions": nudge.instructions or "No Instructions",
                "metrics": (
                    f"Threshold: {nudge.threshold or 'N/A'}, "
                    f"Date Range: {nudge.date_range_from.isoformat() if nudge.date_range_from else 'N/A'} to {nudge.date_range_to.isoformat() if nudge.date_range_to else 'N/A'}, "
                    f"Prior Date Range: {nudge.prior_date_range_from.isoformat() if nudge.prior_date_range_from else 'N/A'} to {nudge.prior_date_range_to.isoformat() if nudge.prior_date_range_to else 'N/A'}, "
                    f"Metric: {nudge.metric_name or 'N/A'}, "
                    f"Value: {nudge.metric_value or 'N/A'}, "
                    f"Unit: {nudge.unit or 'N/A'}, "
                    f"Operator: {nudge.operator or 'N/A'}"
                )
            }
            for nudge in nudges_data
        ]

        # Prepare nudge snippet for comparison
        nudge_snippet = ", ".join([nudge["title"] for nudge in nudges])

        # Check if summary already exists with matching nudge snippet
        existing_summary = db.query(NudgeSummary).filter(
            NudgeSummary.employee_id == req.employee_id,
            NudgeSummary.nudge_snippet == nudge_snippet
        ).first()
        
        if existing_summary:
            print(f"[nudge_summary] Found existing summary for employee {req.employee_id}")
            return {"summary": existing_summary.summary}

        # Generate nudge summary
        result = generate_nudge_summary(req.employee_id, req.prompt, nudges, store=store, openai_api_key=config.openai_api_key)

        # Insert new summary into the database
        summary_record = NudgeSummary(
            employee_id=req.employee_id,
            summary=result["summary"],
            nudge_snippet=nudge_snippet
        )
        db.add(summary_record)
        db.commit()

        return result
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
