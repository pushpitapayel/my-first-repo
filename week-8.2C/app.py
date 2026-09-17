from arduino_iot_cloud import ArduinoCloudClient
from arduino_credentials import DEVICE_ID, SECRET_KEY

from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objects as go

from collections import deque
import threading
import time


MAX_POINTS = 100

data_buffers = {
    "Accelerometer_X": deque(maxlen=MAX_POINTS),
    "Accelerometer_Y": deque(maxlen=MAX_POINTS),
    "Accelerometer_Z": deque(maxlen=MAX_POINTS)
}

latest_update = None

data_lock = threading.Lock()

client = ArduinoCloudClient(
    device_id=DEVICE_ID,
    username=DEVICE_ID,
    password=SECRET_KEY,
    sync_mode=True
)

client.register("Accelerometer_X", value=None)
client.register("Accelerometer_Y", value=None)
client.register("Accelerometer_Z", value=None)


def get_accelerometer_data(client):


    global latest_update

    client.update()

    x = client["Accelerometer_X"]
    y = client["Accelerometer_Y"]
    z = client["Accelerometer_Z"]

    if x is not None and y is not None and z is not None:

        x = float(x)
        y = float(y)
        z = float(z)

        with data_lock:

            # Store values in the buffers
            data_buffers["Accelerometer_X"].append(x)
            data_buffers["Accelerometer_Y"].append(y)
            data_buffers["Accelerometer_Z"].append(z)

            # Sample number
            sample_number = len(data_buffers["Accelerometer_X"]) - 1

            latest_update = {
                "x": [
                    [sample_number],
                    [sample_number],
                    [sample_number]
                ],
                "y": [
                    [x],
                    [y],
                    [z]
                ]
            }

    return x, y, z


def collect_data():
    client.start()

    while True:
        get_accelerometer_data(client)
        time.sleep(0.1)

data_thread = threading.Thread(
    target=collect_data,
    daemon=True
)

data_thread.start()

app = Dash(__name__)

app.layout = html.Div([

    html.H1("Live Accelerometer Data"),

    dcc.Graph(
        id="accelerometer-graph",

        figure=go.Figure(
            data=[
                go.Scatter(
                    x=[],
                    y=[],
                    mode="lines",
                    name="Accelerometer X"
                ),
                go.Scatter(
                    x=[],
                    y=[],
                    mode="lines",
                    name="Accelerometer Y"
                ),
                go.Scatter(
                    x=[],
                    y=[],
                    mode="lines",
                    name="Accelerometer Z"
                )
            ],

            layout=go.Layout(
                title="Live Accelerometer X, Y, Z",
                xaxis_title="Sample",
                yaxis_title="Acceleration",
                yaxis=dict(range=[-2, 2])
            )
        )
    ),

    dcc.Interval(
        id="interval-component",
        interval=200,
        n_intervals=0
    )
])


@app.callback(
    Output("accelerometer-graph", "extendData"),
    Input("interval-component", "n_intervals")
)
def update_graph(n):

    with data_lock:

        if latest_update is None:
            return (
                {
                    "x": [[], [], []],
                    "y": [[], [], []]
                },
                [0, 1, 2],
                MAX_POINTS
            )

        update = latest_update

    return update, [0, 1, 2], MAX_POINTS


if __name__ == "__main__":
    app.run(debug=False)