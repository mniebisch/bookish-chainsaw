import functools
import multiprocessing
import pathlib
from typing import Any, Callable

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from mmfl.feature import orientation as orientation_feat
from mmfl.preprocessing import scouting as scouting_pp


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


def calc_actual_start_orientation(track_df: pd.DataFrame) -> pd.Series:
    """
    Assume frameId column is sorted in ascending order for each player.
    """
    start_orientation = (
        track_df.groupby(["gameId", "playId", "nflId"])
        .agg(actual_start_orientation=pd.NamedAgg(column="o", aggfunc="first"))
        .reset_index()
    )

    unrolled_start_orientation = pd.merge(
        track_df, start_orientation, how="left", on=["gameId", "playId", "nflId"]
    )
    return unrolled_start_orientation["actual_start_orientation"]


# TODO move to preprocessing
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


# TODO move to preprocessing
def get_od_line_players(scout_df: pd.DataFrame) -> pd.DataFrame:
    line_identifiers = ["Pass Block", "Pass Rush"]
    lines_bool = scout_df["pff_role"].isin(line_identifiers)
    return scout_df.loc[lines_bool, ["gameId", "playId", "nflId"]]


if __name__ == "__main__":
    data_path = pathlib.Path(__file__).parent / ".." / ".." / "data"

    # load data
    week_id = 1
    tracking_filepath = data_path / f"week{week_id}.csv"
    # tracking_df = pd.read_csv(tracking_filepath, dtype={"nflId": pd.Int64Dtype()})
    tracking_df = pd.concat(
        [
            pd.read_csv(
                data_path / f"week{week_id}.csv", dtype={"nflId": pd.Int64Dtype()}
            )
            for week_id in range(1, 9)
        ]
    )
    tracking_df = tracking_df.fillna(value={"nflId": -9999})

    play_data_filepath = data_path / "plays.csv"
    play_data_df = pd.read_csv(play_data_filepath)

    scouting_filepath = data_path / "pffScoutingData.csv"
    scouting_df = pd.read_csv(scouting_filepath)

    # TODO move to preprocessing
    # handle O- and D-line
    line_players_df = get_od_line_players(scout_df=scouting_df)
    tracking_df = filter_od_line_players(tracking_df, line_players_df)
    scouting_df = filter_od_line_players(scouting_df, line_players_df)

    # temporary fix as not all weeks are used
    tracking_df = tracking_df.dropna(subset="frameId")

    #  calculate difference types
    # # "theoretical difference" assuming a 90 or 270 degree start orientation
    tracking_df["theoretical_start_orientation"] = calc_start_orientation(
        play_df=play_data_df, track_df=tracking_df
    )

    def _calc_theo_diff(x: pd.DataFrame) -> pd.DataFrame:
        theo_diff = orientation_feat.calc_minimal_angle_difference(
            x["o"] - x["theoretical_start_orientation"]
        )
        return pd.DataFrame({"theoretical_diff": theo_diff, "frameId": x["frameId"]})

    def _calc_emp_diff(x: pd.DataFrame) -> pd.DataFrame:
        emp_diff = orientation_feat.calc_minimal_angle_difference(
            x["o"] - x["o"].iloc[0]
        )
        return pd.DataFrame({"empirical_diff": emp_diff, "frameId": x["frameId"]})

    def _calc_seq_diff(x: pd.DataFrame) -> pd.DataFrame:
        seq_diff = orientation_feat.calc_minimal_angle_difference(x["o"].diff())
        return pd.DataFrame({"sequential_diff": seq_diff, "frameId": x["frameId"]})

    def wrap_parallel(
        arg: tuple[list[Any], pd.DataFrame], func: Callable, group_names: list[str]
    ) -> pd.DataFrame:
        group_name_values, group = arg
        result = func(group)
        for col_name, col_value in zip(group_names, group_name_values):
            result[col_name] = col_value
        return result

    groupby_cols = ["gameId", "playId", "nflId"]

    diff_dfs = []
    for multi_func in [_calc_theo_diff, _calc_emp_diff, _calc_seq_diff]:
        calc_multi_func = functools.partial(
            wrap_parallel, func=multi_func, group_names=groupby_cols
        )

        with multiprocessing.Pool(multiprocessing.cpu_count()) as p:
            blub = p.map(
                calc_multi_func,
                [
                    (name, group)
                    for name, group in tracking_df.groupby(
                        groupby_cols, group_keys=True
                    )
                ],
            )
            blub = pd.concat(blub)
            diff_dfs.append(blub)

    diff_df = functools.reduce(
        lambda left, right: pd.merge(
            left, right, on=groupby_cols + ["frameId"], how="left"
        ),
        diff_dfs,
    )

    def max_abs_change(x: pd.Series) -> float:
        return x.abs().abs()

    agg_overview = {
        (lambda x: np.max(np.abs(x)), "max"): [
            "sequential_diff",
            "empirical_diff",
            "theoretical_diff",
        ],
        (lambda x: np.nanmean(np.abs(x)), "mean"): [
            "sequential_diff",
        ],
        (lambda x: np.nanmedian(np.abs(x)), "median"): [
            "sequential_diff",
        ],
        (lambda x: np.nanstd(np.abs(x)), "std"): [
            "sequential_diff",
        ],
        (lambda x: np.nansum(np.abs(x)), "accumulated"): [
            "sequential_diff",
        ],
    }

    agg_dict = {}
    for (agg_func, agg_name), columns in agg_overview.items():
        for column in columns:
            agg_dict[f"{column}_{agg_name}"] = pd.NamedAgg(
                column=column, aggfunc=agg_func
            )

    # TODO checkout cumsum
    # TODO visualize distribution
    # TODO visualize comparison with hits and stuff
    stats = diff_df.groupby(["gameId", "playId", "nflId"]).agg(**agg_dict)

    action_df = scouting_pp.revert_actions_one_hot_encoding(scouting_df)

    vis_df = pd.merge(stats, action_df, how="left", on=["gameId", "playId", "nflId"])

    vis_df = vis_df[vis_df["action"] != "nothing"]

    sns.boxplot(vis_df, y="empirical_diff_max", x="action")
    plt.show()
    print("blub")
