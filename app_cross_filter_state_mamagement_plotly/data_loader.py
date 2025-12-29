import pandas as pd
import numpy as np

# Constants
UNKNOWN = "Unknown"
DEFAULT_PATH = "Animal-Shelter-Operations.csv"

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
    df['Intake Date'] = pd.to_datetime(df['Intake Date'], errors='coerce')
    df['Outcome Date'] = pd.to_datetime(df['Outcome Date'], errors='coerce')

    # 3. Text Normalization
    text_cols = ['Animal Type', 'Intake Type', 'Outcome Type']
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].astype("string").str.strip().fillna(UNKNOWN)

    # 4. Derive 'intake_duration' (Days)
    if 'intake_duration' not in df.columns:
        if 'Intake Date' in df.columns and 'Outcome Date' in df.columns:
            df['intake_duration'] = (df['Outcome Date'] - df['Intake Date']).dt.days.fillna(0)
            df.loc[df['intake_duration'] < 0, 'intake_duration'] = 0
        else:
            df['intake_duration'] = 0

    # 5. Handle Boolean 'outcome_is_alive'
    if 'outcome_is_alive' in df.columns:
        df['outcome_is_alive'] = df['outcome_is_alive'].map({
            'TRUE': True, 'FALSE': False, 
            'True': True, 'False': False, 
            True: True, False: False,
            1: True, 0: False
        })
    else:
        df['outcome_is_alive'] = False

    # 6. Pre-calculate Years for Filtering
    df['Intake Year'] = df['Intake Date'].dt.year
    df['Outcome Year'] = df['Outcome Date'].dt.year

    return df