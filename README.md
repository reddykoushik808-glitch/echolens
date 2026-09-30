# EchoLens

> **Customer feedback intelligence that remembers.**

EchoLens is a memory-powered product intelligence agent built for Product Managers. It processes customer feedback from CSV/Excel files, computes analytics and sentiment locally using Pandas, creates long-term memory summaries in **Hindsight**, and leverages **Groq** to deliver natural-language product insights.

---

## 1. Problem Solved

Product Managers receive thousands of feedback entries across app reviews, support tickets, surveys, and NPS scores. Generic AI tools summarize individual batches of feedback but forget historical context across releases. 

**EchoLens solves this by remembering how customer feedback changes over time.** It links feedback shifts to key product releases and historical trends.

---

## 2. Architecture

```
                               ┌─────────────────────────┐
                               │     Frontend (HTML/JS)  │
                               └────────────┬────────────┘
                                            │ HTTP / REST
                               ┌────────────▼────────────┐
                               │   FastAPI Backend Server │
                               └──────┬───────────┬──────┘
                                      │           │
                     ┌────────────────┴──┐     ┌──┴────────────────┐
                     │ Pandas & Local ML │     │  Hindsight Client │
                     │   (Analytics)     │     │ (Long-Term Memory)│
                     └───────────────────┘     └──────────┬────────┘
                                                          │
                                                ┌─────────▼────────┐
                                                │ Groq LLM Agent   │
                                                │ (Product Insight)│
                                                └──────────────────┘
```

### Component Breakdown
- **Pandas**: Deterministic analytics, sentiment scoring, topic extraction, and trend calculations performed locally.
- **Hindsight (`hindsight-client`)**: Long-term memory store. Retains periodic summaries and product release memories; recalls relevant memories when queried.
- **Groq (`groq`)**: LLM reasoning engine. Synthesizes answers using local analytics + recalled Hindsight memories.
- **FastAPI**: Lightweight REST backend routing upload, dashboard, insights, and agent endpoints.
- **Vanilla HTML/CSS/JS**: Fast, framework-free UI built with warm beige aesthetics matching the design system.

---

## 3. Tech Stack

- **Backend**: Python 3.10+, FastAPI, Uvicorn, Pandas, OpenPyXL, Scikit-Learn
- **Integrations**: `hindsight-client`, `groq`, `python-dotenv`
- **Frontend**: HTML5, Vanilla CSS3, JavaScript (ES6+), Chart.js
- **Styling**: Custom design tokens (Warm beige `#F6EFE5`, Cream `#FFFDF8`, Primary brown `#76543D`)

---

## 4. Cost-Conscious Architecture

EchoLens is optimized to minimize LLM and vector API usage:
1. **Bulk local processing**: Pandas handles all row-by-row cleaning, sentiment classification, topic extraction, and trend math.
2. **Batch Memory Summaries**: Instead of storing 5,000 individual feedback rows, EchoLens condenses data into 4–6 high-value periodic and release summaries sent to Hindsight via `retain_batch`.
3. **Single API Call Execution**:
   - 1 Upload pipeline
   - 1 Hindsight `retain_batch` per dataset
   - 1 Hindsight `recall` per user question
   - 1 Groq request per user question

---

## 5. How Hindsight & Groq Are Used

### Hindsight Integration
EchoLens uses the official `hindsight-client`:
```python
from hindsight_client import Hindsight

client = Hindsight(
    base_url=HINDSIGHT_API_URL,
    api_key=HINDSIGHT_API_KEY
)

# Retain batch summaries
client.retain_batch(bank_id="echolens", items=memories)

# Recall relevant historical memories
recalled = client.recall(bank_id="echolens", query=user_question, top_k=4)
```

### Groq Integration
```python
from groq import Groq

client = Groq(api_key=GROQ_API_KEY)
completion = client.chat.completions.create(
    model="llama-3.3-70b-versatile",
    messages=[
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_context}
    ]
)
```

---

## 6. Installation & Quickstart

### Prerequisites
- Python 3.9+ installed

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Configure Environment Variables
Copy `.env` and fill in your API credentials (optional for Demo Mode):
```env
GROQ_API_KEY=your_groq_api_key
GROQ_MODEL=llama-3.3-70b-versatile

HINDSIGHT_API_URL=https://api.hindsight.ai
HINDSIGHT_API_KEY=your_hindsight_api_key
HINDSIGHT_BANK_ID=echolens
```

### Step 3: Run the Application
Launch the FastAPI server with Uvicorn:
```bash
uvicorn backend.main:app --reload --port 8000
```
Open your browser at **`http://localhost:8000`**.

---

## 7. Recommended Demo Flow

1. Open **`http://localhost:8000`** (Home landing page).
2. Click **Get Started** &rarr; Sign in on **Login page** (Demo auth accepts any input).
3. On **Upload page**, click **Try Demo Dataset** (or drag & drop a custom CSV).
4. Watch the real-time **Processing checklist** and **Adding to Hindsight** status card.
5. Review the **Dashboard** overview (Total Feedback, Sentiment over time, Top Customer Issues, Emerging Trends).
6. Navigate to **Key Product Insights**.
7. Navigate to **Ask Agent** and ask:
   > *"What changed after the checkout redesign?"*
8. Observe:
   - AI Insight answer
   - Evidence count
   - Recalled **Hindsight Memories Used** accordion.

---

## 8. Known MVP Limitations

- Authentication is simulated locally for demo purposes (`localStorage`).
- Local sentiment classification uses a lightweight keyword & rating rule model when NLP libraries are unconfigured.
- Advanced multi-tenant bank isolation is configurable via `HINDSIGHT_BANK_ID`.
"# echolens" 
