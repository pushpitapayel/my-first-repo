from arduino_iot_cloud import ArduinoCloudClient
from arduino_credentials import DEVICE_ID, SECRET_KEY
import time

client = ArduinoCloudClient(
    device_id=DEVICE_ID,
    username=DEVICE_ID,
    password=SECRET_KEY,
    sync_mode=True
)

client.register("Accelerometer_X")
client.register("Accelerometer_Y")
client.register("Accelerometer_Z")

client.start()

while True:
    client.update()

    print(
        "X:", client["Accelerometer_X"],
        "Y:", client["Accelerometer_Y"],
        "Z:", client["Accelerometer_Z"]
    )

    time.sleep(0.5)