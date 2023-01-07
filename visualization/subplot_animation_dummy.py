from typing import Any

import dash
import numpy as np
import plotly.graph_objects as go
from dash import dcc, html

if __name__ == "__main__":
    x = np.linspace(0, 3 * 2 * np.pi, num=100)
    y_cos = np.cos(x)
    y_sin = np.sin(x)

    fig_dict: dict[str, list | dict[Any, Any]] = {
        "data": [],
        "layout": {},
        "frames": [],
    }

    fig_dict["layout"]["xaxis"] = {"range": [x.min(), x.max()], "title": "x"}
    fig_dict["layout"]["yaxis"] = {"range": [-1, 1], "title": "y", "domain": [0, 0.45]}
    fig_dict["layout"]["yaxis2"] = {
        "range": [-1, 1],
        "title": "y2",
        "domain": [0.55, 1],
    }
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

    trace1 = {"x": x, "y": y_sin, "mode": "lines", "xaxis": "x", "yaxis": "y"}
    marker1 = {
        "x": [x[0]],
        "y": [y_sin[0]],
        "mode": "markers",
        "xaxis": "x",
        "yaxis": "y",
    }
    trace2 = {"x": x, "y": y_cos, "mode": "lines", "xaxis": "x", "yaxis": "y2"}
    marker2 = {
        "x": [x[0]],
        "y": [y_cos[0]],
        "mode": "markers",
        "xaxis": "x",
        "yaxis": "y2",
    }

    fig_dict["data"].append(trace1)
    # fig_dict["data"].append(marker1)
    fig_dict["data"].append(trace2)
    # fig_dict["data"].append(marker2)

    for index, x_value in enumerate(x):
        frame = {"data": [], "name": str(index)}
        data_dict1 = {
            "x": [x_value],
            "y": [y_sin[index]],
            "mode": "markers+lines",
            "xaxis": "x",
            "yaxis": "y",
        }
        data_dict2 = {
            "x": [x_value],
            "y": [y_cos[index]],
            "mode": "markers+lines",
            "xaxis": "x",
            "yaxis": "y2",
        }
        frame["data"].append(data_dict1)
        frame["data"].append(data_dict2)
        # frame["data"].append(trace1)
        # frame["data"].append(trace2)
        fig_dict["frames"].append(frame)
        slider_step = {
            "args": [
                [index],
                {
                    "frame": {"duration": 300, "redraw": True},
                    "mode": "immediate",
                    "transition": {"duration": 300},
                },
            ],
            "label": str(index),
            "method": "animate",
        }
        sliders_dict["steps"].append(slider_step)

    fig_dict["layout"]["sliders"] = [sliders_dict]
    fig = go.Figure(fig_dict)
    fig.show()
