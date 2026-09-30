from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from backend.models.schemas import ChatRequest
from backend.routes.upload import GLOBAL_SESSION_DATA, ensure_initial_session_loaded
from backend.services.hindsight import recall_memories
from backend.services.groq_agent import answer_product_question

router = APIRouter()

@router.post("/agent/chat")
async def chat_with_agent(req: ChatRequest) -> Dict[str, Any]:
    question = req.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    ensure_initial_session_loaded()
    df = GLOBAL_SESSION_DATA.get('df')
    analytics = GLOBAL_SESSION_DATA.get('analytics', {})
    releases_df = GLOBAL_SESSION_DATA.get('releases_df')

    # Step 1: Recall memories from Hindsight
    recalled_memories = recall_memories(question, top_k=4)

    # Step 2: Extract sample relevant raw feedback quotes (for UI evidence expandable section)
    sample_feedback = []
    if df is not None and not df.empty:
        q_words = [w.lower() for w in question.split() if len(w) > 3]
        matches = []
        for row in df.itertuples():
            text_lower = row.review_text.lower()
            match_score = sum(1 for w in q_words if w in text_lower)
            if match_score > 0:
                matches.append((match_score, row))
        
        matches.sort(key=lambda x: x[0], reverse=True)
        selected_rows = [m[1] for m in matches[:3]] if matches else df.sample(min(3, len(df))).itertuples()
        
        for r in selected_rows:
            sample_feedback.append({
                "feedback_id": getattr(r, 'feedback_id', 'FB-100'),
                "text": r.review_text,
                "channel": getattr(r, 'channel', 'App Review'),
                "rating": getattr(r, 'rating', 3),
                "date": str(r.created_at.date()) if hasattr(r.created_at, 'date') else str(r.created_at)
            })

    # Step 3: Extract relevant release context
    releases_list = []
    if releases_df is not None and not releases_df.empty:
        for _, r in releases_df.iterrows():
            releases_list.append({
                "date": str(r['date'].date()) if hasattr(r['date'], 'date') else str(r['date']),
                "feature": str(r['feature']),
                "description": str(r['description'])
            })
    else:
        releases_list.append({
            "date": "2026-02-15",
            "feature": "Checkout Redesign",
            "description": "Redesigned checkout flow to improve speed and simplify steps"
        })

    # Step 4: Groq LLM synthesis (1 single API call)
    groq_res = answer_product_question(
        question=question,
        memories=recalled_memories,
        analytics=analytics,
        releases=releases_list
    )

    return {
        "status": "success",
        "question": question,
        "answer": groq_res["answer"],
        "memories_used": recalled_memories,
        "evidence": {
            "feedback": sample_feedback,
            "releases": releases_list
        },
        "metrics": {
            "records_analyzed": len(df) if df is not None else 500,
            "product_releases_count": len(releases_list),
            "memories_count": len(recalled_memories)
        },
        "demo_mode": groq_res["demo_mode"]
    }
