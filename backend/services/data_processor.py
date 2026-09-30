import os
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Tuple, Optional

POSSIBLE_FEEDBACK_COLS = ['review_text', 'feedback', 'review', 'comment', 'text', 'description', 'message', 'content']
POSSIBLE_DATE_COLS = ['created_at', 'date', 'timestamp', 'time', 'datetime', 'created']
POSSIBLE_CHANNEL_COLS = ['channel', 'source', 'medium', 'platform', 'origin']
POSSIBLE_CUSTOMER_COLS = ['customer_id', 'user_id', 'user', 'customer', 'client_id', 'author']
POSSIBLE_RATING_COLS = ['rating', 'score', 'stars', 'satisfaction']

def detect_columns(df: pd.DataFrame) -> Dict[str, str]:
    columns_lower = {col.lower().strip(): col for col in df.columns}
    detected = {}

    for target_key, candidate_list in [
        ('review_text', POSSIBLE_FEEDBACK_COLS),
        ('created_at', POSSIBLE_DATE_COLS),
        ('channel', POSSIBLE_CHANNEL_COLS),
        ('customer_id', POSSIBLE_CUSTOMER_COLS),
        ('rating', POSSIBLE_RATING_COLS)
    ]:
        found = None
        for cand in candidate_list:
            if cand in columns_lower:
                found = columns_lower[cand]
                break
        if not found:
            # Fallback substring match
            for col_lower, original_col in columns_lower.items():
                if any(cand in col_lower for cand in candidate_list):
                    found = original_col
                    break
        if found:
            detected[target_key] = found

    # Must at least have a text column
    if 'review_text' not in detected:
        # Pick the longest text string column
        text_cols = df.select_dtypes(include=['object', 'string']).columns
        if len(text_cols) > 0:
            detected['review_text'] = text_cols[0]
        else:
            detected['review_text'] = df.columns[0]

    return detected

def process_file_data(file_path: str) -> Tuple[pd.DataFrame, Dict[str, str]]:
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.csv':
        try:
            df = pd.read_csv(file_path)
        except Exception:
            try:
                df = pd.read_csv(file_path, on_bad_lines='skip')
            except Exception:
                df = pd.read_csv(file_path, engine='python', on_bad_lines='skip')
    elif ext in ['.xlsx', '.xls']:
        df = pd.read_excel(file_path)
    else:
        raise ValueError(f"Unsupported file format: {ext}")

    if df.empty:
        raise ValueError("Uploaded dataset is empty")

    detected = detect_columns(df)
    
    # Standardize Dataframe
    cleaned_df = pd.DataFrame()

    # Text
    cleaned_df['review_text'] = df[detected['review_text']].astype(str).fillna('')
    
    # Feedback ID
    if 'feedback_id' in df.columns:
        cleaned_df['feedback_id'] = df['feedback_id']
    else:
        cleaned_df['feedback_id'] = [f"FB-{1000 + i}" for i in range(len(df))]

    # Date
    if 'created_at' in detected:
        cleaned_df['created_at'] = pd.to_datetime(df[detected['created_at']], errors='coerce')
    else:
        # Synthetic date sequence over last 90 days
        base_date = datetime.now() - timedelta(days=90)
        cleaned_df['created_at'] = [base_date + timedelta(hours=i * (90 * 24 / max(len(df), 1))) for i in range(len(df))]
    
    # Fill missing dates if any coercion failed
    if cleaned_df['created_at'].isnull().any():
        cleaned_df['created_at'] = cleaned_df['created_at'].ffill().fillna(datetime.now())

    # Channel
    if 'channel' in detected:
        cleaned_df['channel'] = df[detected['channel']].astype(str).fillna('Direct')
    else:
        cleaned_df['channel'] = 'App Review'

    # Customer ID
    if 'customer_id' in detected:
        cleaned_df['customer_id'] = df[detected['customer_id']].astype(str).fillna('Anonymous')
    else:
        cleaned_df['customer_id'] = [f"CUST-{i+1000}" for i in range(len(df))]

    # Rating
    if 'rating' in detected:
        cleaned_df['rating'] = pd.to_numeric(df[detected['rating']], errors='coerce').fillna(3)
    else:
        cleaned_df['rating'] = 3

    return cleaned_df, detected

def process_release_data(file_path: str) -> pd.DataFrame:
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.csv':
        try:
            df = pd.read_csv(file_path)
        except Exception:
            try:
                df = pd.read_csv(file_path, on_bad_lines='skip')
            except Exception:
                df = pd.read_csv(file_path, engine='python', on_bad_lines='skip')
    elif ext in ['.xlsx', '.xls']:
        df = pd.read_excel(file_path)
    else:
        return pd.DataFrame()

    if df.empty:
        return pd.DataFrame()

    # Standardize column names
    cols = {col.lower(): col for col in df.columns}
    
    date_col = next((cols[c] for c in cols if 'date' in c), df.columns[0])
    feature_col = next((cols[c] for c in cols if 'feature' in c or 'name' in c or 'title' in c), df.columns[min(1, len(df.columns)-1)])
    desc_col = next((cols[c] for c in cols if 'desc' in c or 'detail' in c or 'note' in c), df.columns[min(2, len(df.columns)-1)])

    releases_df = pd.DataFrame({
        'date': pd.to_datetime(df[date_col], errors='coerce'),
        'feature': df[feature_col].astype(str),
        'description': df[desc_col].astype(str)
    })
    
    return releases_df.sort_values('date').dropna(subset=['date'])
