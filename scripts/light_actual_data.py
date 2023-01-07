import matplotlib.pyplot as plt

from mmfl.feature.light import field, player, tools, utils

# IDEAS
# 1. Hits on QB with and without O-Line
# 2. Area around QB blocked by O-Line
#   draw traces for all D-Line players and calc difference with D-Line and O-line img


# TODO check cone aggregation (overlay thingy)


if __name__ == "__main__":
    week_id = 1
    game_id = 2021090900
    play_id = 97
    frame_id = 3
    qb_radius = 0.5
    oline_radius = 0.3
    phi_max = 30
    phi_num = 140

    tracking_df = tools.load_tracking_week(week_id=week_id)
    tracking_df.loc[:, "o"] = utils.map_angle(tracking_df.loc[:, "o"])
    tracking_df.loc[:, "dir"] = utils.map_angle(tracking_df.loc[:, "dir"])

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
    actual_pocket = play_field.calc_pocket_components()

    # vis
    plt.imshow(actual_pocket)
    qb_x = play_field.get_x_ind(play_field.quater_back.x_pos)
    qb_y = play_field.get_y_ind(play_field.quater_back.y_pos)
    plt.scatter([qb_x], [qb_y], s=10, marker="s")

    oline_xs = [play_field.get_x_ind(op.x_pos) for op in play_field.oline_players]
    oline_ys = [play_field.get_y_ind(op.y_pos) for op in play_field.oline_players]
    plt.scatter(oline_xs, oline_ys, s=10, marker="d")

    dline_xs = [play_field.get_x_ind(dp.x_pos) for dp in play_field.dline_players]
    dline_ys = [play_field.get_y_ind(dp.y_pos) for dp in play_field.dline_players]
    plt.scatter(dline_xs, dline_ys, s=10, marker="o")

    plt.show()

    print("fu")
