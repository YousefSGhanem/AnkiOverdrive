import json
import threading
from websocket import create_connection
import time

class WebSocketThread(threading.Thread):
    def __init__(self, set_connection_window):
        super(WebSocketThread, self).__init__()
        self.set_connection_window = set_connection_window
        self.websocket_url = "ws://localhost:8080/ws"
        self.ws = None
        self.running = True  # Flag to control the thread execution

    def run(self):
        while self.running:  # Use the flag to control the loop
            try:
                self.ws = create_connection(self.websocket_url)
                print("WebSocket is opened")
                while self.running:  # Use the flag to control the loop
                    message = self.ws.recv()
                    if not message:
                        break
                    if not self.is_valid_json(message):
                        print("Received invalid JSON message:", message)
                        continue
                    self.on_message(message)
            except Exception as e:
                print(f"Error in WebSocketThread: {e}")
                self.close()
                time.sleep(1)

    def is_valid_json(self, message):
        try:
            json.loads(message)
            return True
        except ValueError:
            return False

    def on_message(self, message):
        # Handle incoming WebSocket messages
        # Assuming the server sends the coordinates in the format {"x": 123, "y": 456}
        try:
            data = json.loads(message)
            if "x" in data and "y" in data and data["x"] != 0 and data["y"] != 0:
                x_coordinate = data["x"]
                y_coordinate = data["y"]
                print(f"Received coordinates: X={x_coordinate}, Y={y_coordinate}")
                # Update your GUI with the received coordinates if needed
                # self.set_connection_window.update_coordinates(x_coordinate, y_coordinate)
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON message: {e}")

    def send_message(self, message):
        try:
            if self.ws:
                # Introduce a delay before sending the message
                time.sleep(2.0)  # Adjust the delay time as needed
                self.ws.send(json.dumps(message))
        except Exception as e:
            print(f"Error sending WebSocket message: {e}")

    def close(self):
        try:
            if self.ws:
                self.ws.close()
        except Exception as e:
            print(f"Error closing WebSocket connection: {e}")
