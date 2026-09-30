import os
import shutil
from pathlib import Path
from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional, Dict, Any

from backend.services.data_processor import process_file_data, process_release_data
from backend.services.analytics import compute_analytics, generate_memory_summaries
from backend.services.hindsight import retain_feedback_memories

router = APIRouter()

# In-memory global state for active demo session
GLOBAL_SESSION_DATA: Dict[str, Any] = {
    'df': None,
    'releases_df': None,
    'analytics': None,
    'memories': [],
    'filename': 'demo_feedback.csv',
    'record_count': 0,
    'detected_columns': {},
    'hindsight_synced': False
}

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
DEMO_CSV_PATH = str(_PROJECT_ROOT / "data" / "demo_feedback.csv")
DEMO_RELEASES_PATH = str(_PROJECT_ROOT / "data" / "demo_releases.csv")

def ensure_initial_session_loaded():
    if GLOBAL_SESSION_DATA['df'] is None:
        if os.path.exists(DEMO_CSV_PATH):
            df, detected = process_file_data(DEMO_CSV_PATH)
            releases_df = None
            if os.path.exists(DEMO_RELEASES_PATH):
                releases_df = process_release_data(DEMO_RELEASES_PATH)
            
            analytics = compute_analytics(df, releases_df)
            memories = generate_memory_summaries(df, releases_df)
            
            # Retain batch in Hindsight
            synced = retain_feedback_memories(memories)

            GLOBAL_SESSION_DATA['df'] = df
            GLOBAL_SESSION_DATA['releases_df'] = releases_df
            GLOBAL_SESSION_DATA['analytics'] = analytics
            GLOBAL_SESSION_DATA['memories'] = memories
            GLOBAL_SESSION_DATA['filename'] = 'demo_feedback.csv'
            GLOBAL_SESSION_DATA['record_count'] = len(df)
            GLOBAL_SESSION_DATA['detected_columns'] = detected
            GLOBAL_SESSION_DATA['hindsight_synced'] = synced

@router.post("/upload")
async def upload_dataset(
    feedback_file: Optional[UploadFile] = File(None),
    release_file: Optional[UploadFile] = File(None),
    is_demo: Optional[bool] = Form(False)
):
    upload_dir = os.path.join(os.path.dirname(__file__), "..", "..", "temp_uploads")
    os.makedirs(upload_dir, exist_ok=True)

    if is_demo or not feedback_file:
        ensure_initial_session_loaded()
        return {
            "filename": "demo_feedback.csv",
            "record_count": GLOBAL_SESSION_DATA['record_count'],
            "detected_columns": GLOBAL_SESSION_DATA['detected_columns'],
            "processing_status": "completed",
            "hindsight_synced": GLOBAL_SESSION_DATA['hindsight_synced'],
            "message": "Demo dataset loaded successfully."
        }

    # Save uploaded feedback file
    fb_path = os.path.join(upload_dir, feedback_file.filename)
    with open(fb_path, "wb") as buffer:
        shutil.copyfileobj(feedback_file.file, buffer)

    rel_path = None
    releases_df = None
    if release_file:
        rel_path = os.path.join(upload_dir, release_file.filename)
        with open(rel_path, "wb") as buffer:
            shutil.copyfileobj(release_file.file, buffer)
        releases_df = process_release_data(rel_path)

    try:
        df, detected = process_file_data(fb_path)
        analytics = compute_analytics(df, releases_df)
        memories = generate_memory_summaries(df, releases_df)

        synced = retain_feedback_memories(memories)

        # Update global session
        GLOBAL_SESSION_DATA['df'] = df
        GLOBAL_SESSION_DATA['releases_df'] = releases_df
        GLOBAL_SESSION_DATA['analytics'] = analytics
        GLOBAL_SESSION_DATA['memories'] = memories
        GLOBAL_SESSION_DATA['filename'] = feedback_file.filename
        GLOBAL_SESSION_DATA['record_count'] = len(df)
        GLOBAL_SESSION_DATA['detected_columns'] = detected
        GLOBAL_SESSION_DATA['hindsight_synced'] = synced

        return {
            "filename": feedback_file.filename,
            "record_count": len(df),
            "detected_columns": detected,
            "processing_status": "completed",
            "hindsight_synced": synced,
            "message": f"Successfully processed {len(df)} records and stored memories in Hindsight."
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to process file: {str(e)}")
