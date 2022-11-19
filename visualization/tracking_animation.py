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

data_path = pathlib.Path(__file__).parent / ".." / "data"

# pick week
week_id = 1  # [1, 8]
if week_id not in set(range(1, 9)):
    raise ValueError("Invalid week. Allowed values in [1, 8].")

# load data
tracking_filepath = data_path / f"week{week_id}.csv"
tracking_df = pd.read_csv(tracking_filepath)

dropdown_play_ids = tracking_df["playId"].unique().tolist()
dropdown_play_ids = [play_id for play_id in sorted(dropdown_play_ids)]

app = dash.Dash()
app.layout = html.Div(
    [
        html.H1("Hallo Christina", id="title"),
        dcc.Dropdown(dropdown_play_ids, dropdown_play_ids[0], id="play-id"),
        dcc.Graph(id="figure"),
    ]
)


@app.callback(
    dash.Output("figure", "figure"),
    dash.Input("play-id", "value"),
)
def update_figure(play_id):
    play_df = tracking_df[tracking_df["playId"] == play_id]
    scatter_groups = play_df["team"].unique()

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
        data_dict = {
            "x": list(team_frame_df["x"]),
            "y": list(team_frame_df["y"]),
            "mode": "markers",
            "name": scatter_group,
        }
        fig_dict["data"].append(data_dict)

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
