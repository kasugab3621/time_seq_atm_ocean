
import pandas as pd

def get_fieldbook(fpath: str) -> pd.DataFrame:
    df = pd.read_csv(
        fpath,
        dtype={
            "st_name": str,
            "JSTtime": str,
            "sonde_no": str,
        },
    )

    df["JSTtime"] = pd.to_datetime(df["JSTtime"].str.replace("_", " "))
    return df
