from downloaders import BaseDownloader
import pandas as pd


def main():
    _ = BaseDownloader(auto_extract=False).download(
        "https://zenodo.org/records/7534071/files/230106_frozen_metadata.csv.gz",
        "data/230106_frozen_metadata.csv.gz",
    )
    lotus = pd.read_csv("data/230106_frozen_metadata.csv.gz")

    df = (
        lotus[["structure_inchikey", "structure_smiles_2D"]]
        .drop_duplicates()
        .reset_index(drop=True)
    )

    df["structure_inchikey"] = df["structure_inchikey"].apply(lambda x: x.split("-")[0])

    df = df.drop_duplicates(subset="structure_inchikey").reset_index(drop=True)

    df = df[df["structure_smiles_2D"].str.contains("C", case=False)].reset_index(
        drop=True
    )  # Keep only rows with 'C' or 'c' in the smiles
    df.drop_duplicates(subset="structure_inchikey", inplace=True)

    df.columns = ["id", "smiles"]

    df.to_csv("data/230106_lotus_inchikey_smiles.csv", index=False)


if __name__ == "__main__":
    main()
