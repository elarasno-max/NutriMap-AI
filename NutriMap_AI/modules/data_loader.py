from pathlib import Path
import pandas as pd

def load_csv(source):
    """Load a CSV path or uploaded file-like object."""
    return pd.read_csv(source)

def load_demo_data(path=None):
    path = Path(path) if path else Path(__file__).resolve().parents[1] / "data" / "sample_data.csv"
    return pd.read_csv(path)

def load_template(path=None):
    path = Path(path) if path else Path(__file__).resolve().parents[1] / "data" / "dataset_template.csv"
    return pd.read_csv(path)
