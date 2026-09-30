from pydantic import BaseModel
from typing import List, Dict, Optional, Any

class UploadResponse(BaseModel):
    filename: str
    record_count: int
    detected_columns: Dict[str, str]
    processing_status: str
    message: str

class AnalyticsOverview(BaseModel):
    total_feedback: int
    positive_percentage: float
    neutral_percentage: float
    negative_percentage: float
    positive_change: float
    top_topics: List[Dict[str, Any]]
    emerging_issues: List[Dict[str, Any]]
    sentiment_over_time: Dict[str, List[Any]]
    channel_distribution: Dict[str, int]
    date_range: Dict[str, str]

class InsightItem(BaseModel):
    id: str
    title: str
    description: str
    metric_label: str
    metric_type: str  # 'positive', 'warning', 'purple'
    evidence: Dict[str, Any]

class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str
    memories_used: List[Dict[str, Any]]
    evidence: List[Dict[str, Any]]
    metrics: Dict[str, Any]
    demo_mode: bool
