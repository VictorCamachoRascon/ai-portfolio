import pandas as pd

def load_csv(path: str, **read_csv_kwargs) -> pd.DataFrame:
    """
    Read a CSV into a DataFrame.
    Example override: load_csv("file.csv", sep=";", dtype=str)
    """
    return pd.read_csv(path, **read_csv_kwargs)

