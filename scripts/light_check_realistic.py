import matplotlib.pyplot as plt
import numpy as np
from skimage import draw

from mmfl.feature.light import field, player

if __name__ == "__main__":
    muh = np.zeros((53, 120))
    muh[15, 10] = 4
    muh[35, 25] = 4
    muh[20, 50] = 4
    muh[20, 5] = 4
    muh[40, 30] = 1
    muh[10, 20] = 1

    plt.imshow(muh)
    plt.show()

    oline_players_coords = [(10, 15), (25, 35), (50, 20)]
    oline_players = [
        player.OffensePlayer(
            x_pos=x_pos,
            y_pos=y_pos,
            orientation=0,
            speed=1,
            acceleration=1,
            sphere_radius=2,
        )
        for x_pos, y_pos in oline_players_coords
    ]
    dline_players = [
        player.DLinePlayer(
            x_pos=30,
            y_pos=40,
            orientation=-135,
            speed=1,
            acceleration=1,
            phi_max=30,
            phi_num=60,
        ),
        player.DLinePlayer(
            x_pos=20,
            y_pos=10,
            orientation=135,
            speed=1,
            acceleration=1,
            phi_max=30,
            phi_num=60,
        ),
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
    blub = play_field.default_pocket()

    oi = play_field.draw_cone(defense_player=play_field.dline_players[0])
    oi2 = play_field.draw_cone(defense_player=play_field.dline_players[1])

    fu = (oi + oi2) > 0

    fig, axs = plt.subplots(1, 3)
    axs[0].imshow(oi > 0)
    axs[1].imshow(oi2 > 0)
    axs[2].imshow(fu)
    plt.show()

    default_pocket = blub
    defense_light = fu
    pocket_light = np.logical_and(defense_light, default_pocket)
    actual_pocket = default_pocket - np.logical_not(pocket_light).astype(int)
    actual_pocket = np.where(np.isclose(actual_pocket, 0), 1, 0)
    actual_pocket = play_field.calc_pocket_components()
    fig, axs = plt.subplots(1, 4)
    axs[0].imshow(default_pocket)
    axs[1].imshow(defense_light)
    axs[2].imshow(pocket_light)
    axs[3].imshow(actual_pocket)
    plt.show()

    print("oi")
