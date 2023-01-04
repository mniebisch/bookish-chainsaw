import matplotlib.pyplot as plt
import numpy as np

from mmfl.feature.light import field, geometric_object, player

if __name__ == "__main__":
    oline_players_coords = [(10, 30), (10, 10), (40, 30), (40, 10)]
    oline_players = [
        player.OffensePlayer(
            x_pos=x_pos,
            y_pos=y_pos,
            orientation=0,
            speed=1,
            acceleration=1,
            sphere_radius=4,
        )
        for x_pos, y_pos in oline_players_coords
    ]
    dline_players = [
        player.DLinePlayer(
            x_pos=20,
            y_pos=20,
            orientation=-180,
            speed=1,
            acceleration=1,
            phi_max=30,
            phi_num=60,
        )
    ]
    quater_back = player.OffensePlayer(
        x_pos=5, y_pos=20, orientation=0, speed=1, acceleration=1, sphere_radius=1
    )

    play_field = field.Field(
        oline_players=oline_players,
        dline_players=dline_players,
        quater_back=quater_back,
        play_direction="left",
    )
    play_field.calc_player_interactions()
    blub = play_field.calc_convex_grid()

    oi = play_field.draw_cone(defense_player=play_field.dline_players[0])

    plt.imshow(blub)
    plt.show()
    plt.imshow(oi > 0)
    plt.show()

    print("oi")
