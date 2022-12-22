import numpy as np
import pandas as pd

__all__ = ["naming_actions_columns", "revert_actions_one_hot_encoding"]


def naming_actions_columns() -> list[str]:
    action_columns = ["hit", "hurry", "sack"]
    action_columns = [f"pff_{column}" for column in action_columns]
    action_columns = action_columns + [f"{column}Allowed" for column in action_columns]
    return action_columns


def revert_actions_one_hot_encoding(df: pd.DataFrame) -> pd.DataFrame:
    none_value = "nothing"
    action_columns = naming_actions_columns()

    action_matrix = np.isclose(df[action_columns], 1)
    action_df = pd.DataFrame(action_matrix, columns=action_columns)

    nothing = np.all(np.logical_not(action_matrix), axis=1)
    pass_block = df["pff_role"] == "Pass Block"
    pass_rush = df["pff_role"] == "Pass Rush"

    action_df[f"{none_value}_block"] = np.logical_and(nothing, pass_block)
    action_df[f"{none_value}_rush"] = np.logical_and(nothing, pass_rush)

    #  action_df[none_value] = nothing_column

    columns = ["gameId", "playId", "nflId"]

    labels_df = df[columns]
    labels_df["action"] = action_df.idxmax(axis=1)

    return labels_df
