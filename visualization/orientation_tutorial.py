import numpy as np
import plotly.graph_objects as go

# Generate curve data
t = np.linspace(-1, 1, 100)
x = t + t**2
y = t - t**2
xm = np.min(x) - 1.5
xM = np.max(x) + 1.5
ym = np.min(y) - 1.5
yM = np.max(y) + 1.5
N = 50
s = np.linspace(-1, 1, N)
xx = s + s**2
yy = s - s**2
vx = 1 + 2 * s
vy = 1 - 2 * s  # v=(vx, vy) is the velocity
speed = np.sqrt(vx**2 + vy**2)
ux = vx / speed  # (ux, uy) unit tangent vector, (-uy, ux) unit normal vector
uy = vy / speed

xend = xx + ux  # end coordinates for the unit tangent vector at (xx, yy)
yend = yy + uy

xnoe = xx - uy  # end coordinates for the unit normal vector at (xx,yy)
ynoe = yy + ux


# Create figure
fig = go.Figure(
    data=[
        go.Scatter(
            x=x, y=y, name="frame", mode="lines", line=dict(width=2, color="blue")
        ),
        go.Scatter(
            x=x, y=y, name="curve", mode="lines", line=dict(width=2, color="blue")
        ),
    ],
    layout=go.Layout(
        width=600,
        height=600,
        xaxis=dict(range=[xm, xM], autorange=False, zeroline=False),
        yaxis=dict(range=[ym, yM], autorange=False, zeroline=False),
        title="Moving Frenet Frame Along a Planar Curve",
        hovermode="closest",
        updatemenus=[
            dict(
                type="buttons",
                buttons=[dict(label="Play", method="animate", args=[None])],
            )
        ],
    ),
    frames=[
        go.Frame(
            data=[
                go.Scatter(
                    x=[xx[k], xend[k], xx[k], xnoe[k], None, 0, 1, None, 1, -1],
                    y=[yy[k], yend[k], yy[k], ynoe[k], None, 0, 2, None, -1, -1],
                    mode="lines",
                    line=dict(color="red", width=2),
                )
            ]
        )
        for k in range(N)
    ],
)

fig.show()
