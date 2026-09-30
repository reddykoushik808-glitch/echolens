import os
import logging
from typing import Dict, List, Any

logger = logging.getLogger("echolens.groq")

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

SYSTEM_PROMPT = """You are EchoLens, a product intelligence analyst.
You answer Product Managers using customer feedback analytics and retrieved historical memory.
Never invent evidence.
Distinguish observed trends from causal claims.
If the available data does not support a conclusion, say so.
Prefer concise, evidence-backed answers.
Mention relevant time periods.
When historical context is important, explain how the situation changed over time."""

def get_groq_client():
    if not GROQ_API_KEY:
        return None
    try:
        from groq import Groq
        return Groq(api_key=GROQ_API_KEY)
    except Exception as e:
        logger.warning(f"Could not initialize Groq client: {e}")
        return None

def answer_product_question(
    question: str,
    memories: List[Dict[str, Any]],
    analytics: Dict[str, Any],
    releases: List[Dict[str, Any]] = None
) -> Dict[str, Any]:
    
    client = get_groq_client()
    
    # Format context strings for LLM
    memories_str = "\n".join([f"- {m.get('text', '')}" for m in memories]) if memories else "No historical memories retrieved."
    
    topics_summary = ", ".join([f"{t['name']}: {t['count']} records ({t['percentage']}%)" for t in analytics.get('top_topics', [])])
    emerging_str = ", ".join([f"{e['name']}: {e['change_pct']}% change" for e in analytics.get('emerging_issues', [])])
    
    releases_str = "No recent product releases recorded."
    if releases:
        releases_str = "\n".join([f"- {r.get('date', '')}: {r.get('feature', '')} ({r.get('description', '')})" for r in releases])
    elif any("Checkout Redesign" in m.get("text", "") for m in memories):
        releases_str = "- 2026-02-15: Checkout Redesign (Redesigned checkout flow to improve speed and simplify steps)"

    user_content = f"""USER QUESTION:
{question}

RETRIEVED HINDSIGHT HISTORICAL MEMORIES:
{memories_str}

CALCULATED FEEDBACK ANALYTICS:
Total Feedback Analyzed: {analytics.get('total_feedback', 0)}
Sentiment Breakdown: Positive {analytics.get('positive_percentage', 0)}%, Neutral {analytics.get('neutral_percentage', 0)}%, Negative {analytics.get('negative_percentage', 0)}%
Top Topics: {topics_summary}
Emerging Trends: {emerging_str}

PRODUCT RELEASES CONTEXT:
{releases_str}

Please provide a clear, concise, evidence-backed product insight answering the user's question directly based on the context above."""

    if client:
        try:
            # Send single Groq LLM completion request
            completion = client.chat.completions.create(
                model=GROQ_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_content}
                ],
                temperature=0.3,
                max_tokens=500
            )
            answer_text = completion.choices[0].message.content.strip()
            return {
                "answer": answer_text,
                "demo_mode": False
            }
        except Exception as e:
            logger.error(f"Groq API call failed: {e}. Falling back to deterministic response.")

    # Fallback deterministic generator for Demo Mode
    q_lower = question.lower()
    if "checkout redesign" in q_lower or "checkout" in q_lower or "after the" in q_lower:
        fallback_answer = (
            "After the checkout redesign on Feb 15, 2026, checkout-related negative feedback decreased significantly from 42% "
            "down to 27% over the following month. Customers reported faster loading times and improved UI on mobile devices. "
            "However, payment-related complaints (specifically UPI transaction timeouts and bank deduction errors) "
            "emerged as the primary new issue during March 2026, increasing by 34%."
        )
    elif "complaining" in q_lower or "issues" in q_lower or "negative" in q_lower:
        fallback_answer = (
            "Based on recent customer conversations, the primary active complaints revolve around Payment Failures (21% of negative feedback) "
            "and Mobile Experience bugs. In March 2026, UPI transaction timeouts and netbanking 502 errors saw a notable rise."
        )
    elif "sentiment" in q_lower or "change" in q_lower or "trend" in q_lower:
        fallback_answer = (
            "Overall customer sentiment has improved by 5% over the 3-month period, reaching 62% positive sentiment in March. "
            "The improvement was driven by the February 15 checkout performance optimization, though negative sentiment spiked slightly "
            "in mid-March due to payment gateway delays."
        )
    else:
        fallback_answer = (
            f"Based on historical memory and analytics across {analytics.get('total_feedback', 0)} feedback records, "
            f"positive sentiment is currently at {analytics.get('positive_percentage', 0)}%. The top customer topics are "
            f"{topics_summary}. Following recent release updates, checkout speed has improved while payment failure reports require investigation."
        )

    return {
        "answer": fallback_answer,
        "demo_mode": True
    }
