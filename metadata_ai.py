# %%
import pandas as pd
import json
from datetime import datetime, timezone, timedelta

df = pd.read_parquet('metadata_ai_keyword_summary.parquet')

def is_right_summary(x):
    if 'high_level_summary' in x:
        return True
    if 'unstructured_summary' in x:
        return True

def is_in_last_n_hours(upload_date_str: str, n_hours: int) -> bool:
    """
    Determine if upload_date_str (UTC) is between "now" and "N hours ago".
    Supported formats:
      - 'YYYY-MM-DDTHH:MM:SS[.ffffff]'
      - 'YYYY-MM-DDTHH:MM:SS[.ffffff]Z'
      - 'YYYY-MM-DDTHH:MM:SS[.ffffff]+00:00'
    """
    # Parse ISO format string
    dt = datetime.fromisoformat(upload_date_str.replace('Z', '+00:00'))
    # If parsed datetime has no timezone, treat as UTC
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    # Get current UTC
    now = datetime.now(timezone.utc)
    # Compare range
    return now - timedelta(hours=n_hours) <= dt <= now

def dataframe_to_json(df: pd.DataFrame):
    tmp = json.loads(df.to_json())
    keys = list(tmp.keys())
    result = []
    for idx in range(len(tmp[keys[0]])):
        item_dict = dict()
        for key in keys:
            item_dict[key] = tmp[key][str(idx)]
        result.append(item_dict)
    return json.dumps(result)


today_str = str(datetime.today().date())

df = df[df['upload_date'].apply(lambda s: is_in_last_n_hours(s, 24))]
df = df.reset_index(drop=True)

with open(f'metadata_ai_{today_str}_full.json', 'w') as f:
    f.write(dataframe_to_json(df))

df = df[df.keywords.apply(lambda x: len(x)>0)].reset_index(drop=True)
df = df.reset_index(drop=True)

with open(f'metadata_ai_{today_str}_filtered.json', 'w') as f:
    f.write(dataframe_to_json(df))
# %%