import pandas as pd
import numpy as np

UNKNOWN = "Unknown"
DEFAULT_PATH = "Animal-Shelter-Operations.csv"

# Used if outcome_is_alive is not present in CSV
LIVE_OUTCOMES = [
    "ADOPTION",
    "TRANSFER",
    "RETURN TO OWNER",
    "RTOS",
    "RELOCATE",
]


def _normalize_text(s: pd.Series, unknown_label: str = UNKNOWN) -> pd.Series:
    s = s.astype("string").str.strip()
    s = s.replace({"": pd.NA, "nan": pd.NA, "None": pd.NA})
    return s.fillna(unknown_label)


def _parse_dates(s: pd.Series) -> pd.Series:
    return pd.to_datetime(s, errors="coerce")


def _generate_dummy_data(n: int = 1000) -> pd.DataFrame:
    np.random.seed(42)
    dates = pd.date_range(start="2020-01-01", end="2023-12-31", periods=n)
    outcome_dates = dates + pd.to_timedelta(np.random.randint(1, 60, n), unit="D")

    df = pd.DataFrame(
        {
            "Animal Type": np.random.choice(
                ["DOG", "CAT", "BIRD", "OTHER"], n, p=[0.5, 0.4, 0.05, 0.05]
            ),
            "Intake Type": np.random.choice(
                ["STRAY", "OWNER SURRENDER", "PUBLIC ASSIST", "SEIZED"], n
            ),
            "Outcome Type": np.random.choice(
                ["ADOPTION", "TRANSFER", "RETURN TO OWNER", "EUTHANASIA", "DIED"],
                n,
                p=[0.4, 0.3, 0.2, 0.08, 0.02],
            ),
            "Intake Date": dates,
            "Outcome Date": outcome_dates,
        }
    )
    return df


def load_data(path: str = DEFAULT_PATH) -> pd.DataFrame:
    try:
        df = pd.read_csv(path)
    except FileNotFoundError:
        df = _generate_dummy_data()

    # Normalize column names
    df.columns = df.columns.astype(str).str.strip()

    # Ensure required columns exist
    for col in ["Animal Type", "Intake Type", "Outcome Type"]:
        if col not in df.columns:
            df[col] = UNKNOWN

    # Parse dates if present
    for col in ["Intake Date", "Outcome Date"]:
        if col in df.columns:
            df[col] = _parse_dates(df[col])
        else:
            df[col] = pd.NaT

    # Normalize text columns
    for col in ["Animal Type", "Intake Type", "Outcome Type"]:
        df[col] = _normalize_text(df[col])

    # intake_duration
    delta = df["Outcome Date"] - df["Intake Date"]
    df["intake_duration"] = delta.dt.days
    df["intake_duration"] = df["intake_duration"].fillna(0)
    df.loc[df["intake_duration"] < 0, "intake_duration"] = 0

    # outcome_is_alive: use existing column if provided; otherwise derive from Outcome Type
    if "outcome_is_alive" in df.columns:
        if df["outcome_is_alive"].dtype == object:
            df["outcome_is_alive"] = df["outcome_is_alive"].map(
                {"TRUE": True, "FALSE": False, True: True, False: False}
            )
        df["outcome_is_alive"] = df["outcome_is_alive"].fillna(False).astype(bool)
    else:
        df["outcome_is_alive"] = df["Outcome Type"].isin(LIVE_OUTCOMES)

    # Year fields for filtering / trend clicks
    df["Intake Year"] = df["Intake Date"].dt.year
    df["Outcome Year"] = df["Outcome Date"].dt.year

    return df
