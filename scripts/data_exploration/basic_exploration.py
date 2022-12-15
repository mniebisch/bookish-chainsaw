import pathlib

import pandas as pd

if __name__ == "__main__":
    file_name = "week1.csv"

    data_path = pathlib.Path("data")
    file_path = data_path / file_name

    df = pd.read_csv(file_path)
    print(df.head())
    print(len(df))
