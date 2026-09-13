from arduino_iot_cloud import ArduinoCloudClient
from arduino_credentials import DEVICE_ID, SECRET_KEY

from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go

from collections import deque
import threading
import time

MAX_POINTS = 100

x_data = deque(maxlen=MAX_POINTS)
y_data = deque(maxlen=MAX_POINTS)
z_data = deque(maxlen=MAX_POINTS)


client = ArduinoCloudClient(
    device_id=DEVICE_ID,
    username=DEVICE_ID,
    password=SECRET_KEY,
    sync_mode=True
)

client.register("Accelerometer_X", value=None)
client.register("Accelerometer_Y", value=None)
client.register("Accelerometer_Z", value=None)


def collect_data():
    client.start()

    while True:
        client.update()

        x = client["Accelerometer_X"]
        y = client["Accelerometer_Y"]
        z = client["Accelerometer_Z"]

        if x is not None:
            x_data.append(float(x))

        if y is not None:
            y_data.append(float(y))

        if z is not None:
            z_data.append(float(z))

        time.sleep(0.1)


# Start Cloud data collection
data_thread = threading.Thread(
    target=collect_data,
    daemon=True
)

data_thread.start()


app = Dash(__name__)

app.layout = html.Div([
    html.H1("Live Accelerometer Data"),

    dcc.Graph(id="accelerometer-graph"),

    dcc.Interval(
        id="interval-component",
        interval=500,
        n_intervals=0
    )
])


@app.callback(
    Output("accelerometer-graph", "figure"),
    Input("interval-component", "n_intervals")
)
def update_graph(n):

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        y=list(x_data),
        mode="lines",
        name="Accelerometer X"
    ))

    fig.add_trace(go.Scatter(
        y=list(y_data),
        mode="lines",
        name="Accelerometer Y"
    ))

    fig.add_trace(go.Scatter(
        y=list(z_data),
        mode="lines",
        name="Accelerometer Z"
    ))

    fig.update_layout(
        title="Live Accelerometer X, Y, Z",
        xaxis_title="Sample",
        yaxis_title="Acceleration",
        yaxis=dict(range=[-2, 2]),
        xaxis=dict(
            range=[0, MAX_POINTS]
        )
    )

    return fig


if __name__ == "__main__":
    app.run(debug=False)