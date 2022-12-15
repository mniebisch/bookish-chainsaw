import pathlib

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


def _calculate_df_time_diff(x: pd.DataFrame) -> float:
    min_time_idx = x["frameId"].idxmin()
    max_time_idx = x["frameId"].idxmax()
    time_delta = x["time"][max_time_idx] - x["time"][min_time_idx]
    return time_delta.total_seconds()


def calculate_df_time_diff(df: pd.DataFrame) -> pd.DataFrame:
    df = df.drop_duplicates(["gameId", "playId", "frameId"])
    df = df.copy()
    df["time"] = pd.to_datetime(df["time"])

    return (
        df.groupby(["gameId", "playId"])
        .apply(_calculate_df_time_diff)
        .reset_index(name="play_time")
    )


def _get_action_name(actions: list[str], column_name: str) -> str:
    actions_matches = [action for action in actions if action in column_name]
    if len(actions_matches) != 1:
        raise ValueError
    return actions_matches[0]


def extract_qb_action(df: pd.DataFrame, column_name: str) -> pd.DataFrame:
    """
    Intended to be applied to PFF Scouting data.
    Extract information if play resulted in hurry, sack, or hit.
    """
    actions = ["hit", "sack", "hurry"]
    valid_columns = [f"pff_{action}" for action in actions] + [
        f"pff_{action}Allowed" for action in actions
    ]
    action_name = _get_action_name(actions=actions, column_name=column_name)
    if column_name not in df.columns:
        raise ValueError("Seriously?")
    if column_name not in valid_columns:
        raise ValueError("Invalid quaterback action column name.")
    action_summary = (
        df.groupby(["gameId", "playId"]).agg({column_name: np.nansum}).reset_index()
    )
    action_summary[action_name] = action_summary[column_name] > 0.5
    action_summary = action_summary.drop(column_name, axis=1)
    return action_summary


if __name__ == "__main__":
    data_path = pathlib.Path(__file__).parent / ".." / "data"
    plays_filepath = data_path / "plays.csv"
    plays_df = pd.read_csv(plays_filepath)

    scout_filepath = data_path / "pffScoutingData.csv"
    scout_df = pd.read_csv(scout_filepath)

    qb_sack_df = extract_qb_action(scout_df, "pff_sack")
    check_sack_df = qb_sack_df.merge(
        plays_df[["gameId", "playId", "passResult"]], on=["gameId", "playId"]
    )

    sack_check = all((check_sack_df["passResult"] == "S") == check_sack_df["sack"])

    # for inspection
    check_sack_df.loc[(check_sack_df["passResult"] == "S") != check_sack_df["sack"]]
    scout_df.loc[(scout_df["gameId"] == 2021091210) & (scout_df["playId"] == 146)]

    weeks_dfs = [
        pd.read_csv(data_path / f"week{week_id}.csv") for week_id in range(1, 9)
    ]
    weeks_dfs = [calculate_df_time_diff(df) for df in weeks_dfs]
    play_time_df = pd.concat(weeks_dfs)

    blub = play_time_df.merge(
        plays_df[["gameId", "playId", "passResult"]], on=["gameId", "playId"]
    )

    sns.displot(blub, x="play_time", kind="kde", hue="passResult")
    plt.show()
