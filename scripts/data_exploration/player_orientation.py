import pathlib

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# TODO create feature to map "continious" change without a flip between 180 and -180


def calc_start_orientation(play_df: pd.DataFrame, track_df: pd.DataFrame) -> pd.Series:
    df = pd.merge(
        left=track_df[["gameId", "playId", "playDirection", "team"]],
        right=play_df[["gameId", "playId", "possessionTeam"]],
        how="left",
        on=["gameId", "playId"],
    )
    is_in_possession: pd.Series = df["team"] == df["possessionTeam"]
    is_right_direction: pd.Series = df["playDirection"] == "right"

    possession_right = is_in_possession & is_right_direction
    not_possession_left = ~(is_in_possession | is_right_direction)
    bool_result = possession_right | not_possession_left

    return pd.Series(np.where(bool_result, 90, 270), name="startOrientation")


def _calc_left_start(orientation: pd.Series) -> np.ndarray:
    # 270 deg
    orientation_recalculated = np.zeros_like(orientation)
    ind = orientation.between(90, 270)  # -180, 0
    orientation_recalculated[ind] = orientation[ind] - 270
    ind = orientation.between(270, 360)  # 0, 90
    orientation_recalculated[ind] = orientation[ind] - 270
    ind = orientation.between(0, 90)  # 90, 180
    orientation_recalculated[ind] = orientation[ind] - 90
    return orientation_recalculated


def _calc_right_start(orientation: pd.Series) -> np.ndarray:
    # 90 deg
    orientation_recalculated = np.zeros_like(orientation)
    ind = orientation.between(90, 270)  # 0, 180
    orientation_recalculated[ind] = orientation[ind] - 90
    ind = orientation.between(270, 360)  # -180, -90
    orientation_recalculated[ind] = orientation[ind] - (180 + 270)
    ind = orientation.between(0, 90)  # -90, 0
    orientation_recalculated[ind] = orientation[ind] - 90
    return orientation_recalculated


def calc_orientation_deviation(
    orientation_value: pd.Series, orientation_start: pd.Series
) -> pd.Series:
    orientation_recalculated = np.zeros_like(orientation_value)
    is_right = orientation_start == 90
    orientation_recalculated[is_right] = _calc_right_start(orientation_value[is_right])
    is_left = orientation_start == 270
    orientation_recalculated[is_left] = _calc_left_start(orientation_value[is_left])
    return pd.Series(orientation_recalculated, name="orientationDeviation")


def filter_od_line_players(
    track_df: pd.DataFrame, filter_df: pd.DataFrame
) -> pd.DataFrame:
    return pd.merge(
        filter_df,
        track_df,
        on=["gameId", "playId", "nflId"],
        how="left",
        validate="1:m",
    )


def get_od_line_players(scout_df: pd.DataFrame) -> pd.DataFrame:
    line_identifiers = ["Pass Block", "Pass Rush"]
    lines_bool = scout_df["pff_role"].isin(line_identifiers)
    return scout_df.loc[lines_bool, ["gameId", "playId", "nflId"]]


if __name__ == "__main__":
    data_path = pathlib.Path(__file__).parent / ".." / ".." / "data"

    # load data
    week_id = 1
    tracking_filepath = data_path / f"week{week_id}.csv"
    tracking_df = pd.read_csv(tracking_filepath, dtype={"nflId": pd.Int64Dtype()})
    tracking_df = tracking_df.fillna(value={"nflId": -9999})

    play_data_filepath = data_path / "plays.csv"
    play_data_df = pd.read_csv(play_data_filepath)

    scouting_filepath = data_path / "pffScoutingData.csv"
    scouting_df = pd.read_csv(scouting_filepath)

    #
    line_players_df = get_od_line_players(scout_df=scouting_df)
    tracking_df = filter_od_line_players(tracking_df, line_players_df)
    # temporary fix as not all weeks are used
    tracking_df = tracking_df.dropna(subset="frameId")
    tracking_df["startOrientation"] = calc_start_orientation(
        play_df=play_data_df, track_df=tracking_df
    )
    tracking_df["orientationDeviation"] = calc_orientation_deviation(
        tracking_df["o"], tracking_df["startOrientation"]
    )
    tracking_df["orientationDeviation"] = tracking_df["orientationDeviation"].abs()

    orientation_stats = tracking_df.groupby(["gameId", "playId", "nflId"]).agg(
        {"orientationDeviation": "max"}
    )
    sns.displot(orientation_stats, x="orientationDeviation")
    plt.show()
    print("blub")
