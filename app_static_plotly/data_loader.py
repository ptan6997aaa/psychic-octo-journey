import pandas as pd
import numpy as np

# Constants
UNKNOWN = "Unknown"
DEFAULT_PATH = "Animal-Shelter-Operations.csv"

# Live Outcome Definition for Logic
LIVE_OUTCOMES = [
    "ADOPTION", 
    "TRANSFER", 
    "RETURN TO OWNER", 
    "RTOS", 
    "RELOCATE"
]

def _normalize_text(s: pd.Series, unknown_label: str = UNKNOWN) -> pd.Series:
    """
    Cleans text columns: strips whitespace, handles empty strings/None/nan,
    and fills missing values with a default label.
    """
    s = s.astype("string").str.strip()
    s = s.replace({"": pd.NA, "nan": pd.NA, "None": pd.NA})
    return s.fillna(unknown_label)

def _parse_dates(s: pd.Series) -> pd.Series:
    """Parses dates safely using coerce to handle bad formats."""
    return pd.to_datetime(s, errors='coerce')

def load_data(path: str = DEFAULT_PATH) -> pd.DataFrame:
    """
    Main function to load, clean, and enrich the Animal Shelter dataset.
    """
    try:
        df = pd.read_csv(path)
    except FileNotFoundError:
        print(f"Error: File '{path}' not found. Returning empty DataFrame.")
        return pd.DataFrame()

    # 1. Normalize Header Names
    df.columns = df.columns.astype(str).str.strip()

    # 2. Date Parsing
    date_cols = ['Intake Date', 'Outcome Date']
    for col in date_cols:
        if col in df.columns:
            df[col] = _parse_dates(df[col])

    # 3. Text Normalization
    text_cols = ['Animal Type', 'Intake Type', 'Outcome Type']
    for col in text_cols:
        if col in df.columns:
            df[col] = _normalize_text(df[col])

    # 4. Derive 'intake_duration' (Days)
    if 'Intake Date' in df.columns and 'Outcome Date' in df.columns:
        delta = df['Outcome Date'] - df['Intake Date']
        df['intake_duration'] = delta.dt.days
        df.loc[df['intake_duration'] < 0, 'intake_duration'] = 0
    else:
        df['intake_duration'] = 0

    return df