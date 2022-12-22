import pathlib

import numpy as np
import pandas as pd


def revert_one_hot_encoding(df: pd.DataFrame) -> pd.DataFrame:
    none_value = "nothing"
    action_columns = ["hit", "hurry", "sack"]
    action_columns = [f"pff_{column}" for column in action_columns]
    action_columns = action_columns + [f"{column}Allowed" for column in action_columns]

    action_matrix = np.isclose(df[action_columns], 1)
    nothing_column = np.all(np.logical_not(action_matrix), axis=1)
    action_df = pd.DataFrame(action_matrix, columns=action_columns)
    action_df[none_value] = nothing_column

    columns = ["gameId", "playId", "nflId"]

    output_df = df[columns]
    output_df["action"] = action_df.idxmax(axis=1)

    return output_df


def validate_actions(df: pd.DataFrame) -> np.bool_:
    columns = ["hit", "hurry", "sack"]
    columns = [f"pff_{column}" for column in columns]
    columns = columns + [f"{column}Allowed" for column in columns]

    action_matrix = np.isclose(df[columns], 1)
    row_sum = np.sum(action_matrix, axis=1)
    return np.any(row_sum > 1)


if __name__ == "__main__":
    data_path = pathlib.Path(__file__).parent / ".." / ".." / "data"
    scout_filepath = data_path / "pffScoutingData.csv"
    scout_df = pd.read_csv(scout_filepath)

    disabiguity = validate_actions(scout_df)

    fufu = revert_one_hot_encoding(scout_df)

    print("blub")
