import pandas as pd
from .config import REQUIRED_COLUMNS, NUMERIC_COLUMNS

RANGES = {
    "Latitude": (-90, 90), "Longitude": (-180, 180), "Survey_Year": (1900, 2100),
    "Soil_pH": (0, 14), "Iodized_Salt_Access": (0, 100), "Anemia_Prevalence": (0, 100),
    "Iron_Deficiency_Prevalence": (0, 100), "Dietary_Diversity": (0, 20),
    "Median_Urinary_Iodine": (0, 5000), "Water_Fluoride": (0, 100),
}

def validate_dataset(df):
    issues=[]
    missing=[c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing: issues.append("Missing required columns: " + ", ".join(missing))
    if not missing:
        for col in ["Latitude","Longitude","Survey_Year"]:
            converted=pd.to_numeric(df[col], errors="coerce")
            if converted.isna().any(): issues.append(f"{col} contains non-numeric or missing values")
        for col,(lo,hi) in RANGES.items():
            if col in df.columns:
                vals=pd.to_numeric(df[col], errors="coerce")
                if ((vals < lo) | (vals > hi)).any(): issues.append(f"{col} has values outside the broad validation range {lo}–{hi}")
    return {"valid": len(issues)==0, "issues": issues, "missing_required": missing}

def clean_dataset(df):
    """Conservative cleaning: coerce numeric columns, remove exact duplicates, retain missing values."""
    out=df.copy()
    before=len(out)
    out=out.drop_duplicates().copy()
    duplicates=before-len(out)
    for col in NUMERIC_COLUMNS:
        if col in out.columns: out[col]=pd.to_numeric(out[col], errors="coerce")
    # Invalid measurements are marked missing rather than silently clipped.
    invalid_counts={}
    for col,(lo,hi) in RANGES.items():
        if col in out.columns:
            mask=(out[col] < lo) | (out[col] > hi)
            invalid_counts[col]=int(mask.sum())
            out.loc[mask,col]=pd.NA
    return out, {"duplicates_removed":duplicates,"invalid_values_marked_missing":invalid_counts}

def missing_summary(df):
    return pd.DataFrame({"missing_count":df.isna().sum(),"missing_percent":(df.isna().mean()*100).round(1)})
