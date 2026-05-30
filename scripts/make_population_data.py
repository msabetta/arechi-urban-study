import pathlib
import pandas as pd
import requests
import zipfile
import io

PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT_CSV = PROJECT_ROOT / "data" / "processed" / "popolazione_1951_2021.csv"


def download_csv(url: str) -> pd.DataFrame:
    """Scarica il CSV da `url` e restituisce un DataFrame."""
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    # ISTAT CSV uses semicolon delimiter and includes a description line before the header.
    return pd.read_csv(io.StringIO(resp.text), sep=';', skiprows=1)


def extract_zip(url: str, inner_csv_name: str) -> pd.DataFrame:
    """Scarica un archivio ZIP e legge il CSV al suo interno."""
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    with zipfile.ZipFile(io.BytesIO(resp.content)) as z:
        with z.open(inner_csv_name) as f:
            # ISTAT CSV inside zip has a description line before the header and uses ';' as delimiter.
            return pd.read_csv(f, sep=';', skiprows=1)


def clean_population(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and aggregate the ISTAT population CSV.

    The source contains columns:
    - "Codice comune"
    - "Comune"
    - "Età"
    - "Totale maschi"
    - "Totale femmine"
    - "Totale"

    We aggregate total population per comune (summing across ages), rename columns to match expected schema, and set a placeholder density (NaN).
    """
    # Rename relevant columns
    column_map = {
        "Codice comune": "id",
        "Comune": "area_name",
        "Totale": "population",
    }
    # Rename columns according to mapping
    df = df.rename(columns=column_map)
    # Keep only needed columns and aggregate population per comune (summing across ages)
    df = df[["id", "area_name", "population"]]
    df = df.groupby(["id", "area_name"], as_index=False)["population"].sum()
    # Add placeholder density column
    df["density"] = pd.NA
    return df


def main():
    # ------------------------------------------------------------
    # 👉  SOSTITUISCI QUI L'URL DEL TUO FILE (CSV o ZIP)
    # ------------------------------------------------------------
    URL = "https://demo.istat.it/data/posas/POSAS_2026_it_065_Salerno.zip"
    # Se è un ZIP: inner_csv = "population.csv"
    # ------------------------------------------------------------
    try:
        if URL.lower().endswith(".zip"):
            df = extract_zip(URL, inner_csv_name="POSAS_2026_it_065_Salerno.csv")
        else:
            df = download_csv(URL)

        df_clean = clean_population(df)
        OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
        df_clean.to_csv(OUT_CSV, index=False)
        print(f"✅  File creato: {OUT_CSV}")
    except Exception as e:
        print(f"Errore durante il download o la conversione: {e}")


if __name__ == "__main__":
    main()
