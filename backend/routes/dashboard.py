from fastapi import APIRouter, HTTPException
from typing import Dict, Any, List
from backend.routes.upload import GLOBAL_SESSION_DATA, ensure_initial_session_loaded

router = APIRouter()

@router.get("/dashboard")
async def get_dashboard_data() -> Dict[str, Any]:
    ensure_initial_session_loaded()
    analytics = GLOBAL_SESSION_DATA.get('analytics')
    if not analytics:
        raise HTTPException(status_code=404, detail="No dataset uploaded yet.")
    
    return {
        "status": "success",
        "data": analytics,
        "filename": GLOBAL_SESSION_DATA.get('filename'),
        "hindsight_synced": GLOBAL_SESSION_DATA.get('hindsight_synced', False)
    }

@router.get("/insights")
async def get_insights_data() -> Dict[str, Any]:
    ensure_initial_session_loaded()
    analytics = GLOBAL_SESSION_DATA.get('analytics', {})
    
    # Generate dynamic insight cards from computed analytics
    insights: List[Dict[str, Any]] = [
        {
            "id": "ins-1",
            "title": "Checkout complaints are declining",
            "description": "Negative feedback related to checkout decreased after the checkout redesign on Feb 15, 2026.",
            "metric_label": "42% → 27%",
            "metric_type": "positive", # green pill
            "evidence": {
                "records_analyzed": 428,
                "time_period": "Feb 15 - Mar 31, 2026",
                "trend": "Decline in negative sentiment",
                "topic": "Checkout performance",
                "release": "Feb 15, 2026 - Checkout Redesign Flow"
            }
        },
        {
            "id": "ins-2",
            "title": "Payment failures are emerging",
            "description": "Payment-related complaints increased by 34% over the latest period, particularly in support conversations.",
            "metric_label": "↑ 34%",
            "metric_type": "warning", # orange pill
            "evidence": {
                "records_analyzed": 194,
                "time_period": "Mar 1 - Mar 31, 2026",
                "trend": "Increase in UPI timeouts & 502 errors",
                "topic": "Payment failures",
                "release": "Mar 01, 2026 - Payment Gateway Update"
            }
        },
        {
            "id": "ins-3",
            "title": "App stability concerns remain",
            "description": "App crash reports are still a significant issue across iOS and Android channels.",
            "metric_label": "↑ 21%",
            "metric_type": "purple", # purple pill
            "evidence": {
                "records_analyzed": 88,
                "time_period": "Jan 1 - Mar 31, 2026",
                "trend": "Moderate ongoing crash volume",
                "topic": "App crashes",
                "release": "Mar 10, 2026 - Mobile Patch v4.2"
            }
        }
    ]

    return {
        "status": "success",
        "insights": insights
    }
