import pathlib
from typing import Any, Union

import dash
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from dash import dcc, html

# draw thin grey line of trajectory?
# draw graph lines between players?
# show player orientation
# show player motion direction
# visualize speed, or acceleration (heatlike?)
# each team one color or symbol
# mouse over information (jersey num etc)


def map_angle(angle: Union[int, float]) -> Union[int, float]:
    angle = angle % 360
    if 0 <= angle <= 90:
        return 90 - angle
    else:
        return 360 - (angle - 90)


def create_angles_lines(
    x: list[Union[int, float]],
    y: list[Union[int, float]],
    angle: list[Union[int, float]],
) -> tuple[list[Union[int, float]], list[Union[int, float]]]:
    angle = [map_angle(value) for value in angle]
    lines_x, lines_y = [], []
    for x0, y0, angle_deg in zip(x, y, angle):
        angle_rad = np.deg2rad(angle_deg)
        angle_x = np.cos(angle_rad)
        angle_y = np.sin(angle_rad)
        x1 = x0 + angle_x
        y1 = y0 + angle_y
        segment_x = [x0, x1, None]
        segment_y = [y0, y1, None]
        lines_x.extend(segment_x)
        lines_y.extend(segment_y)
    return lines_x, lines_y


def map_direction(
    play_df: pd.DataFrame,
) -> dict[str, Any]:
    play_angle = list(play_df["dir"])
    play_x = list(play_df["x"])
    play_y = list(play_df["y"])
    x, y = create_angles_lines(x=play_x, y=play_y, angle=play_angle)
    return {
        "x": x,
        "y": y,
        "mode": "lines",
        "line": {"color": "blue"},
        "name": "motion",
    }


def map_orientation(
    play_df: pd.DataFrame,
) -> dict[str, Any]:
    play_angle = list(play_df["o"])
    play_x = list(play_df["x"])
    play_y = list(play_df["y"])
    x, y = create_angles_lines(x=play_x, y=play_y, angle=play_angle)
    return {
        "x": x,
        "y": y,
        "mode": "lines",
        "line": {"color": "red"},
        "name": "orientation",
    }


data_path = pathlib.Path(__file__).parent / ".." / "data"

# pick week
week_id = 1  # [1, 8]
if week_id not in set(range(1, 9)):
    raise ValueError("Invalid week. Allowed values in [1, 8].")

# load data
tracking_filepath = data_path / f"week{week_id}.csv"
tracking_df = pd.read_csv(tracking_filepath)
tracking_df = pd.concat(
    [pd.read_csv(data_path / f"week{week_id}.csv") for week_id in range(1, 9)]
)

scout_filepath = data_path / "pffScoutingData.csv"
scout_df = pd.read_csv(scout_filepath)

dropdown_play_ids = tracking_df["playId"].unique().tolist()
dropdown_play_ids = sorted(dropdown_play_ids)

dropdown_game_ids = tracking_df["gameId"].unique().tolist()
dropdown_game_ids = sorted(dropdown_game_ids)

# set animation start gameId and playId
start_value_game_id = dropdown_game_ids[0]
start_value_play_id = tracking_df[tracking_df["gameId"] == start_value_game_id][
    "playId"
][0]

app = dash.Dash()
app.layout = html.Div(
    [
        dcc.Dropdown(dropdown_game_ids, start_value_game_id, id="game-id"),
        dcc.Dropdown(id="play-id"),
        dcc.Graph(id="figure"),
    ]
)


@app.callback(
    dash.Output("play-id", "options"),
    dash.Input("game-id", "value"),
)
def set_play_ids_options(selected_game_id):
    game_df = tracking_df[tracking_df["gameId"] == selected_game_id]
    game_play_ids = game_df["playId"].unique().tolist()
    game_play_ids = sorted(game_play_ids)
    return [{"label": play_id, "value": play_id} for play_id in game_play_ids]


@app.callback(
    dash.Output("play-id", "value"),
    dash.Input("play-id", "options"),
)
def set_play_id_value(available_options):
    return available_options[0]["value"]


@app.callback(
    dash.Output("figure", "figure"),
    dash.Input("game-id", "value"),
    dash.Input("play-id", "value"),
)
def update_figure(game_id, play_id):
    play_df = tracking_df[
        (tracking_df["playId"] == play_id) & (tracking_df["gameId"] == game_id)
    ]
    scatter_groups = play_df["team"].unique()

    scout_play_df = scout_df[
        (scout_df["playId"] == play_id) & (scout_df["gameId"] == game_id)
    ]

    # prepare animation
    frame_ids = np.arange(1, play_df["frameId"].max() + 1)
    fig_dict: dict[str, Union[list, dict[Any, Any]]] = {
        "data": [],
        "layout": {},
        "frames": [],
    }

    fig_dict["layout"]["xaxis"] = {"range": [0, 120], "title": "x"}
    fig_dict["layout"]["yaxis"] = {"range": [0, 53.3], "title": "y"}
    fig_dict["layout"]["hovermode"] = "closest"
    fig_dict["layout"]["updatemenus"] = [
        {
            "buttons": [
                {
                    "args": [
                        None,
                        {
                            "frame": {"duration": 100, "redraw": False},
                            "fromcurrent": True,
                            "transition": {
                                "duration": 300,
                                "easing": "quadratic-in-out",
                            },
                        },
                    ],
                    "label": "Play",
                    "method": "animate",
                },
                {
                    "args": [
                        [None],
                        {
                            "frame": {"duration": 0, "redraw": False},
                            "mode": "immediate",
                            "transition": {"duration": 0},
                        },
                    ],
                    "label": "Pause",
                    "method": "animate",
                },
            ],
            "direction": "left",
            "pad": {"r": 10, "t": 87},
            "showactive": False,
            "type": "buttons",
            "x": 0.1,
            "xanchor": "right",
            "y": 0,
            "yanchor": "top",
        }
    ]
    sliders_dict = {
        "active": 0,
        "yanchor": "top",
        "xanchor": "left",
        "currentvalue": {
            "font": {"size": 20},
            "prefix": "Frame:",
            "visible": True,
            "xanchor": "right",
        },
        "transition": {"duration": 300, "easing": "cubic-in-out"},
        "pad": {"b": 10, "t": 50},
        "len": 0.9,
        "x": 0.1,
        "y": 0,
        "steps": [],
    }

    # make initial frame
    intital_frame_id = 1
    frame_df = play_df[play_df["frameId"] == intital_frame_id]
    for scatter_group in scatter_groups:
        team_frame_df = frame_df[frame_df["team"] == scatter_group]
        # next TODO here
        data_dict = {
            "x": list(team_frame_df["x"]),
            "y": list(team_frame_df["y"]),
            "mode": "markers",
            "name": scatter_group,
        }
        fig_dict["data"].append(data_dict)
        fig_dict["data"].append(map_orientation(team_frame_df))
        fig_dict["data"].append(map_direction(team_frame_df))

    # make frames
    for frame_id in frame_ids:
        frame = {"data": [], "name": str(frame_id)}
        frame_df = play_df[play_df["frameId"] == frame_id]
        for scatter_group in scatter_groups:
            team_frame_df = frame_df[frame_df["team"] == scatter_group]
            data_dict = {
                "x": list(team_frame_df["x"]),
                "y": list(team_frame_df["y"]),
                "mode": "markers",
                "name": scatter_group,
            }
            frame["data"].append(data_dict)
            frame["data"].append(map_orientation(team_frame_df))
            frame["data"].append(map_direction(team_frame_df))

        fig_dict["frames"].append(frame)
        slider_step = {
            "args": [
                [frame_id],
                {
                    "frame": {"duration": 300, "redraw": False},
                    "mode": "immediate",
                    "transition": {"duration": 300},
                },
            ],
            "label": str(frame_id),
            "method": "animate",
        }
        sliders_dict["steps"].append(slider_step)

    fig_dict["layout"]["sliders"] = [sliders_dict]
    fig = go.Figure(fig_dict)
    return fig


if __name__ == "__main__":

    app.run_server(debug=True, use_reloader=False)
