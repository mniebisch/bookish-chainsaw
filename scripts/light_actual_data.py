import pathlib

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from mmfl.feature.light import field, player, utils

# IDEAS
# 1. Hits on QB with and without O-Line
# 2. Area around QB blocked by O-Line
#   draw traces for all D-Line players and calc difference with D-Line and O-line img


# TODO check cone aggregation (overlay thingy)


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
    line_identifiers = ["Pass Block", "Pass Rush", "Pass"]
    lines_bool = scout_df["pff_role"].isin(line_identifiers)
    return scout_df.loc[lines_bool, ["gameId", "playId", "nflId"]]


if __name__ == "__main__":
    data_path = pathlib.Path(__file__).parent / ".." / "data"

    # load data
    week_id = 1
    tracking_filepath = data_path / f"week{week_id}.csv"
    tracking_df = pd.read_csv(
        data_path / f"week{week_id}.csv", dtype={"nflId": pd.Int64Dtype()}
    )
    tracking_df = tracking_df.fillna(value={"nflId": -9999})

    play_data_filepath = data_path / "plays.csv"
    play_data_df = pd.read_csv(play_data_filepath)

    scouting_filepath = data_path / "pffScoutingData.csv"
    scouting_df = pd.read_csv(scouting_filepath)

    line_players_df = get_od_line_players(scout_df=scouting_df)
    tracking_df = filter_od_line_players(tracking_df, line_players_df)
    scouting_df = filter_od_line_players(scouting_df, line_players_df)

    # temporary fix as not all weeks are used
    tracking_df = tracking_df.dropna(subset="frameId")

    df = pd.merge(
        left=tracking_df,
        right=scouting_df[["gameId", "playId", "nflId", "pff_role"]],
        how="left",
        on=["gameId", "playId", "nflId"],
    )

    game_id = 2021090900
    play_id = 97
    frame_id = 3

    example_df = df[
        (df["gameId"] == game_id)
        & (df["playId"] == play_id)
        & (df["frameId"] == frame_id)
    ]

    example_df["o"] = utils.map_angle(example_df["o"])
    example_df["dir"] = utils.map_angle(example_df["dir"])

    quater_back_df = example_df[example_df["pff_role"] == "Pass"]
    oline_df = example_df[example_df["pff_role"] == "Pass Block"]
    dline_df = example_df[example_df["pff_role"] == "Pass Rush"]

    quater_back = player.OffensePlayer(
        x_pos=quater_back_df["x"].iloc[0],
        y_pos=quater_back_df["y"].iloc[0],
        orientation=quater_back_df["o"].iloc[0],
        speed=quater_back_df["s"].iloc[0],
        acceleration=quater_back_df["a"].iloc[0],
        sphere_radius=0.00001,
    )

    oline_players = []
    for x, y, o, s, a in zip(
        oline_df["x"], oline_df["y"], oline_df["o"], oline_df["s"], oline_df["a"]
    ):
        oline_players.append(
            player.OffensePlayer(
                x_pos=x,
                y_pos=y,
                orientation=o,
                speed=s,
                acceleration=a,
                sphere_radius=0.3,
            )
        )
    dline_players = []
    for x, y, o, s, a in zip(
        dline_df["x"], dline_df["y"], dline_df["dir"], dline_df["s"], dline_df["a"]
    ):
        dline_players.append(
            player.DLinePlayer(
                x_pos=x,
                y_pos=y,
                orientation=o,
                speed=s,
                acceleration=a,
                phi_max=30,
                phi_num=140,
            )
        )

    play_field = field.Field(
        oline_players=oline_players,
        dline_players=dline_players,
        quater_back=quater_back,
        play_direction="left",
    )
    play_field.calc_player_interactions()
    actual_pocket = play_field.calc_pocket_components()

    plt.imshow(actual_pocket)
    qb_x = play_field.get_x_ind(quater_back.x_pos)
    qb_y = play_field.get_y_ind(quater_back.y_pos)
    plt.scatter([qb_x], [qb_y], s=10, marker="s")

    oline_xs = [play_field.get_x_ind(op.x_pos) for op in oline_players]
    oline_ys = [play_field.get_y_ind(op.y_pos) for op in oline_players]
    plt.scatter(oline_xs, oline_ys, s=10, marker="d")

    dline_xs = [play_field.get_x_ind(dp.x_pos) for dp in dline_players]
    dline_ys = [play_field.get_y_ind(dp.y_pos) for dp in dline_players]
    plt.scatter(dline_xs, dline_ys, s=10, marker="o")

    plt.show()

    print("fu")
