import numpy as np
import tqdm
from matplotlib import pyplot as plt

from mmfl.feature.light import tools, utils

# IDEAS
# 1. Hits on QB with and without O-Line
# 2. Area around QB blocked by O-Line
#   draw traces for all D-Line players and calc difference with D-Line and O-line img


# TODO check cone aggregation (overlay thingy)


if __name__ == "__main__":
    week_id = 1
    game_id = 2021090900
    play_id = 97
    # frame_id = 2
    qb_radius = 0.5
    oline_radius = 0.3
    phi_max = 30
    phi_num = 140

    tracking_df = tools.load_tracking_week(week_id=week_id)
    tracking_df.loc[:, "o"] = utils.map_angle(tracking_df.loc[:, "o"])
    tracking_df.loc[:, "dir"] = utils.map_angle(tracking_df.loc[:, "dir"])

    frames_max = tracking_df[
        (tracking_df["gameId"] == game_id) & (tracking_df["playId"] == play_id)
    ]["frameId"].max()
    light_hits = []
    print("a")
    for frame_id in tqdm.tqdm(range(1, frames_max + 1)):
        play_field = tools.create_field_frame(
            tracking_df=tracking_df,
            game_id=game_id,
            play_id=play_id,
            frame_id=frame_id,
            qb_radius=qb_radius,
            oline_radius=oline_radius,
            phi_max=phi_max,
            phi_num=phi_num,
        )
        play_field.calc_player_interactions()
        light_hit = tools.calc_interaction_matrix(play_field=play_field)
        light_hits.append(light_hit)

    print("b")
    light_hits = np.stack(light_hits)
    qb_hits = light_hits[:, :, -1]
    qb_hit_series = np.sum(qb_hits, axis=1)

    for dline_player_row_ind in range(light_hits.shape[1]):
        dline_series = light_hits[:, dline_player_row_ind, -1]
        plt.plot(dline_series)

    # light qb received in total
    # light qb received per dline player
    plt.plot(qb_hit_series)
    plt.show()

    # TODO find traces that are blocked by oline and would hit qb instead
    light_blocked_player = light_hits[:, :, :-1].sum(axis=1)
    for oplayer_col_ind in range(light_blocked_player.shape[1]):
        plt.plot(light_blocked_player[:, oplayer_col_ind])
    light_blocked_total = light_blocked_player.sum(axis=1)
    plt.plot(light_blocked_total)
    plt.show()

    print("oi")
