import numpy as np
import pandas as pd

from mmfl.feature.light import tools, utils

"""
How to use with groupby.

import functools

foo = functools.partial(
    calc_light_metrics, 
    qb_radius=qb_radius, 
    oline_radius=oline_radius, 
    phi_max=phi_max, 
    phi_num=phi_num
)

df.groupby(['xyz']).apply(foo)

"""


def calc_light_metrics(
    frame_df: pd.DataFrame,
    qb_radius: float,
    oline_radius: float,
    phi_max: int,
    phi_num: int,
) -> dict:
    """
    frame_df: DataFrame of a single play.
    """
    # adapt angles from NFL data to unit circle
    frame_df.loc[:, "o"] = utils.map_angle(frame_df.loc[:, "o"])
    frame_df.loc[:, "dir"] = utils.map_angle(frame_df.loc[:, "dir"])

    play_field = tools.create_field_frame_df(
        tracking_df=frame_df,
        qb_radius=qb_radius,
        oline_radius=oline_radius,
        phi_max=phi_max,
        phi_num=phi_num,
    )
    play_field.calc_player_interactions()

    light_hit = tools.calc_interaction_matrix(play_field=play_field)

    # Quarterback hit metric
    qb_hits = light_hit[:, -1]
    qb_hits_sum = np.sum(qb_hits)
    qb_hits_dline_attribution: dict[str, int] = {
        dline_id: qb_hit
        for dline_id, qb_hit in zip(
            sorted([dline_player.id for dline_player in play_field.dline_players]),
            qb_hits,
        )
    }
    # O-Line block metric
    oline_block_sum = np.sum(light_hit[:, :-1])
    oline_block_attribution = np.sum(light_hit[:, :-1], axis=0)
    oline_block_attribution = {
        oline_id: block
        for oline_id, block in zip(
            sorted([offense_player.id for offense_player in play_field.oline_players]),
            oline_block_attribution,
        )
    }

    return {
        "qb_hits": {
            "total": qb_hits_sum,
            "dline_attribution": qb_hits_dline_attribution,
        },
        "oline_blocks": {
            "total": oline_block_sum,
            "oline_attribution": oline_block_attribution,
        },
    }
