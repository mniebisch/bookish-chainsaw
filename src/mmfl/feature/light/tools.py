import pathlib

import numpy as np
import pandas as pd

from mmfl.feature.light import field, player

__all__ = [
    "create_field_frame",
    "load_tracking_week",
]


def get_data_path() -> pathlib.Path:
    return pathlib.Path(__file__).parent / ".." / ".." / ".." / ".." / "data"


def load_tracking_week(week_id: int) -> pd.DataFrame:
    data_path = get_data_path()
    tracking_filepath = data_path / f"week{week_id}.csv"
    tracking_df = pd.read_csv(tracking_filepath, dtype={"nflId": pd.Int64Dtype()})
    tracking_df = tracking_df.fillna(value={"nflId": -9999})
    return tracking_df


def load_tracking_data() -> pd.DataFrame:
    week_ids = range(1, 9)
    weeks = [load_tracking_week(week_id=week_id) for week_id in week_ids]
    return pd.concat(weeks)


def load_scouting_data() -> pd.DataFrame:
    data_path = get_data_path()
    scouting_filepath = data_path / "pffScoutingData.csv"
    return pd.read_csv(scouting_filepath)


def get_players(roles: list[str] | str) -> pd.DataFrame:
    """
    roles = ["Pass Block"] -> O-line
    roles = ["Pass Rush"] -> D-Line
    roles = ["Pass"] -> QB
    roles = ["Pass Block", "Pass Rush", "Pass"]
    """
    roles = [roles] if isinstance(roles, str) else roles
    scouting_df = load_scouting_data()
    lines_bool = scouting_df["pff_role"].isin(roles)
    return scouting_df.loc[lines_bool, ["gameId", "playId", "nflId"]]


def filter_roles(tracking_df: pd.DataFrame, roles: str | list[str]) -> pd.DataFrame:
    filter_df = get_players(roles=roles)
    tracking_filtered = pd.merge(
        filter_df,
        tracking_df,
        on=["gameId", "playId", "nflId"],
        how="left",
        validate="1:m",
    )
    # In case not all tracking weeks where used
    tracking_filtered = tracking_filtered.dropna(subset="frameId")
    return tracking_filtered


def create_field_frame(
    tracking_df: pd.DataFrame,
    game_id: int,
    play_id: int,
    frame_id: int,
    qb_radius: float,
    oline_radius: float,
    phi_max: float,
    phi_num: int,
) -> field.Field:
    frame_df = tracking_df[
        (tracking_df["gameId"] == game_id)
        & (tracking_df["playId"] == play_id)
        & (tracking_df["frameId"] == frame_id)
    ]
    return create_field_frame_df(
        tracking_df=frame_df,
        qb_radius=qb_radius,
        oline_radius=oline_radius,
        phi_max=phi_max,
        phi_num=phi_num,
    )


def create_field_frame_df(
    tracking_df: pd.DataFrame,
    qb_radius: float,
    oline_radius: float,
    phi_max: float,
    phi_num: int,
) -> field.Field:
    frame_df = tracking_df
    quater_back_df = filter_roles(frame_df, roles="Pass")
    oline_df = filter_roles(frame_df, roles="Pass Block")
    dline_df = filter_roles(frame_df, roles="Pass Rush")

    quater_back = player.OffensePlayer(
        x_pos=quater_back_df["x"].iloc[0],
        y_pos=quater_back_df["y"].iloc[0],
        orientation=quater_back_df["o"].iloc[0],
        speed=quater_back_df["s"].iloc[0],
        acceleration=quater_back_df["a"].iloc[0],
        sphere_radius=qb_radius,
        nfl_id=quater_back_df["nflId"].iloc[0],
    )
    oline_players = []
    for x, y, o, s, a, nfl_id in zip(
        oline_df["x"],
        oline_df["y"],
        oline_df["o"],
        oline_df["s"],
        oline_df["a"],
        oline_df["nflId"],
    ):
        oline_players.append(
            player.OffensePlayer(
                x_pos=x,
                y_pos=y,
                orientation=o,
                speed=s,
                acceleration=a,
                sphere_radius=oline_radius,
                nfl_id=nfl_id,
            )
        )
    dline_players = []
    for x, y, o, s, a, nfl_id in zip(
        dline_df["x"],
        dline_df["y"],
        dline_df["dir"],
        dline_df["s"],
        dline_df["a"],
        dline_df["nflId"],
    ):
        dline_players.append(
            player.DLinePlayer(
                x_pos=x,
                y_pos=y,
                orientation=o,
                speed=s,
                acceleration=a,
                phi_max=phi_max,
                phi_num=phi_num,
                nfl_id=nfl_id,
            )
        )
    return field.Field(
        oline_players=oline_players,
        dline_players=dline_players,
        quater_back=quater_back,
        play_direction="left",
    )


def calc_interaction_matrix(play_field: field.Field) -> np.ndarray:
    offense_ids = sorted(
        [offense_player.id for offense_player in play_field.oline_players]
    ) + [play_field.quater_back.id]
    dline_ids = sorted([dline_player.id for dline_player in play_field.dline_players])

    light_hit = np.zeros((len(dline_ids), len(offense_ids)), dtype=int)

    for dplayer in play_field.dline_players:
        for trace in dplayer.cone.traces:
            if trace.hit is not None:
                emitting_index = dline_ids.index(dplayer.id)
                receiving_index = offense_ids.index(trace.hit.id)
                light_hit[emitting_index, receiving_index] += 1

    return light_hit
