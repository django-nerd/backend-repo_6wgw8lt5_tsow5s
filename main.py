import os
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from database import db, create_document, get_documents
from bson import ObjectId

app = FastAPI(title="Soccer Training API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Soccer Training Backend is running"}

# Schema endpoint for viewer tools
@app.get("/schema")
def get_schema():
    from schemas import Video, Analysis, Session
    return {
        "video": Video.model_json_schema(),
        "analysis": Analysis.model_json_schema(),
        "session": Session.model_json_schema(),
    }

# Video endpoints
class VideoIn(BaseModel):
    title: str
    url: str
    duration: Optional[float] = None
    team: Optional[str] = None
    player: Optional[str] = None
    tags: List[str] = []

@app.post("/api/videos")
def create_video(video: VideoIn):
    vid = create_document("video", video.model_dump())
    return {"id": vid}

@app.get("/api/videos")
def list_videos(tag: Optional[str] = None, player: Optional[str] = None):
    query = {}
    if tag:
        query["tags"] = {"$in": [tag]}
    if player:
        query["player"] = player
    vids = get_documents("video", query)
    # Normalize ObjectId
    for v in vids:
        v["_id"] = str(v.get("_id"))
    return vids

# Analysis endpoints
class AnalysisIn(BaseModel):
    video_id: str
    time: float
    note: Optional[str] = None
    tag: Optional[str] = None
    created_by: Optional[str] = None

@app.post("/api/analysis")
def create_analysis(a: AnalysisIn):
    # Basic FK validation
    try:
        _ = db["video"].find_one({"_id": ObjectId(a.video_id)})
        if _ is None:
            raise HTTPException(status_code=404, detail="Video not found")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid video_id")
    aid = create_document("analysis", a.model_dump())
    return {"id": aid}

@app.get("/api/analysis")
def list_analysis(video_id: str):
    try:
        q = {"video_id": video_id}
        items = get_documents("analysis", q)
        for it in items:
            it["_id"] = str(it.get("_id"))
        return items
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Session endpoints
class SessionIn(BaseModel):
    title: str
    date: Optional[str] = None
    drills: List[str] = []
    notes: Optional[str] = None
    video_ids: List[str] = []

@app.post("/api/sessions")
def create_session(s: SessionIn):
    sid = create_document("session", s.model_dump())
    return {"id": sid}

@app.get("/api/sessions")
def list_sessions():
    sessions = get_documents("session")
    for s in sessions:
        s["_id"] = str(s.get("_id"))
    return sessions

@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        from database import db

        if db is not None:
            response["database"] = "✅ Available"
            response["database_url"] = "✅ Configured"
            response["database_name"] = db.name if hasattr(db, 'name') else "✅ Connected"
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
                response["database"] = "✅ Connected & Working"
            except Exception as e:
                response["database"] = f"⚠️  Connected but Error: {str(e)[:50]}"
        else:
            response["database"] = "⚠️  Available but not initialized"

    except ImportError:
        response["database"] = "❌ Database module not found (run enable-database first)"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:50]}"

    import os
    response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
    response["database_name"] = "✅ Set" if os.getenv("DATABASE_NAME") else "❌ Not Set"

    return response

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
