import os
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger("echolens.hindsight")

# In-memory store fallback for demo mode when API keys are unconfigured
_LOCAL_FALLBACK_MEMORIES: List[Dict[str, Any]] = []

def _get_config():
    return {
        "api_url": os.getenv("HINDSIGHT_API_URL", "https://api.hindsight.ai"),
        "api_key": os.getenv("HINDSIGHT_API_KEY", ""),
        "bank_id": os.getenv("HINDSIGHT_BANK_ID", "echolens"),
    }

def get_hindsight_client():
    cfg = _get_config()
    if not cfg["api_key"]:
        return None
    try:
        from hindsight_client import Hindsight
        return Hindsight(
            base_url=cfg["api_url"],
            api_key=cfg["api_key"]
        )
    except Exception as e:
        logger.warning(f"Could not initialize Hindsight client: {e}")
        return None

def retain_feedback_memories(memories: List[Dict[str, Any]], bank_id: str = None) -> bool:
    global _LOCAL_FALLBACK_MEMORIES
    cfg = _get_config()
    bank_id = bank_id or cfg["bank_id"]
    
    # Store locally for fallback recall
    _LOCAL_FALLBACK_MEMORIES = memories

    client = get_hindsight_client()
    if not client:
        logger.info("Hindsight key not configured. Stored memories in Demo Mode.")
        return False

    try:
        # Prepare batch payloads
        items_to_retain = []
        for mem in memories:
            text = mem.get("text", "")
            metadata = {k: v for k, v in mem.items() if k != "text"}
            items_to_retain.append({
                "content": text,
                "metadata": metadata
            })
        
        # Call official Hindsight retain_batch / retain
        if hasattr(client, "retain_batch"):
            client.retain_batch(bank_id=bank_id, items=items_to_retain)
        elif hasattr(client, "retain"):
            for item in items_to_retain:
                client.retain(bank_id=bank_id, content=item["content"], metadata=item["metadata"])
        logger.info(f"Successfully retained {len(memories)} summaries in Hindsight bank '{bank_id}'.")
        return True
    except Exception as e:
        logger.error(f"Error calling Hindsight retain API: {e}")
        return False

def recall_memories(query: str, bank_id: str = None, top_k: int = 4) -> List[Dict[str, Any]]:
    global _LOCAL_FALLBACK_MEMORIES
    cfg = _get_config()
    bank_id = bank_id or cfg["bank_id"]
    client = get_hindsight_client()

    if client:
        try:
            if hasattr(client, "recall"):
                res = client.recall(bank_id=bank_id, query=query, top_k=top_k)
                # Parse returned memories
                recalled = []
                if isinstance(res, list):
                    for item in res:
                        if isinstance(item, dict):
                            recalled.append({
                                "text": item.get("content", item.get("text", str(item))),
                                "metadata": item.get("metadata", {}),
                                "source": "Hindsight API"
                            })
                        else:
                            recalled.append({"text": str(item), "source": "Hindsight API"})
                    if recalled:
                        return recalled
        except Exception as e:
            logger.error(f"Hindsight recall API failed, using fallback: {e}")

    # Fallback to local memory matching for Demo Mode
    query_lower = query.lower()
    matched = []
    
    if not _LOCAL_FALLBACK_MEMORIES:
        # Provide baseline demo memories if none loaded
        _LOCAL_FALLBACK_MEMORIES = [
            {
                "text": "Product Release Memory: On Feb 15, 2026, the team deployed the Checkout Redesign release. Customer feedback immediately following the release showed a 35% decline in checkout performance complaints (from 42% down to 27% of total negative feedback).",
                "type": "release_impact",
                "feature": "Checkout Redesign",
                "date": "2026-02-15"
            },
            {
                "text": "Emerging Trend Memory (March 2026): Payment failure complaints (specifically UPI transaction timeouts, bank deduction without order confirmation, and HDFC netbanking error 502) increased by 34% in March 2026.",
                "type": "emerging_issue",
                "topic": "payments",
                "date": "2026-03-31"
            },
            {
                "text": "January 2026 Summary: Checkout-related feedback was strongly negative (42% of negative comments). Customers frequently reported slow loading and payment-screen freezes on mobile.",
                "type": "monthly_summary",
                "period": "January 2026",
                "date": "2026-01-31"
            },
            {
                "text": "February 2026 Summary: A checkout redesign was released on February 15. Customer feedback after the release showed fewer checkout-performance complaints, while app stability remained constant.",
                "type": "monthly_summary",
                "period": "February 2026",
                "date": "2026-02-28"
            }
        ]

    for mem in _LOCAL_FALLBACK_MEMORIES:
        text = mem.get("text", "")
        # Basic keyword relevance scoring
        score = sum(1 for word in query_lower.split() if word in text.lower() and len(word) > 3)
        matched.append((score, mem))

    matched.sort(key=lambda x: x[0], reverse=True)
    return [item[1] for item in matched[:top_k]]
