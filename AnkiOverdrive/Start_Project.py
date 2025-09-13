from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.uic import loadUi
from PyQt5 import QtWidgets
from WebSocketThread import WebSocketThread
from overdrive import Overdrive

# C6:1B:24:97:D0:3D
class SetConnectionWindow(QMainWindow):
    def __init__(self):
        super(SetConnectionWindow, self).__init__()
        loadUi("set_connection_window.ui", self)

        self.predefined_mac_addresses = ["C6:1B:24:97:D0:3D", "A1:B2:C3:D4:E5:F6", "F1:E2:D3:C4:B5:A6","C6:61:17:46:7D:F8","EE:CB:65:B5:D6:4A"]
        self.macComboBox.addItems(self.predefined_mac_addresses)

        # Connect button
        self.connectButton.clicked.connect(self.connect_anki_vehicle)


        # Disconnect button
        self.disconnectButton.clicked.connect(self.disconnect_anki_vehicle)

        # Initialize Overdrive object
        self.car = None
        self.speed = 0
        self.prev_speed = 0

        # Bind arrow key events
        self.centralwidget.setFocusPolicy(Qt.StrongFocus)
        self.centralwidget.keyPressEvent = self.keyPressEvent

        # QLabel widgets for vehicle information
        self.locationLabel = self.findChild(QtWidgets.QLabel, "locationLabel")
        self.pieceLabel = self.findChild(QtWidgets.QLabel, "pieceLabel")
        self.speedLabel2 = self.findChild(QtWidgets.QLabel, "speedLabel2")
        self.clockwiseLabel = self.findChild(QtWidgets.QLabel, "clockwiseLabel")

        # Set text color to white for all labels
        self.locationLabel.setStyleSheet("color: white;")
        self.pieceLabel.setStyleSheet("color: white;")
        self.speedLabel2.setStyleSheet("color: white;")
        self.clockwiseLabel.setStyleSheet("color: white;")

        # Initialize WebSocketThread
        self.websocket_thread = WebSocketThread(self)
        self.websocket_thread.start()  # Start the WebSocketThread

    def connect_anki_vehicle(self):
        selected_mac_address = self.macComboBox.currentText()
        if selected_mac_address:
            try:
                self.car = Overdrive(selected_mac_address)
                self.car.setLocationChangeCallback(self.location_change_callback)
                QMessageBox.information(self, "Success",
                                        f"Connected to Anki vehicle with MAC address: {selected_mac_address}")

                # Send initial message after connecting to the car
                self.send_initial_message()

                self.connectButton.setEnabled(False)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error connecting to the Anki vehicle: {str(e)}")
        else:
            QMessageBox.warning(self, "Error", "Please select a MAC address")

    def send_initial_message(self):
        # Add any initial data you want to send after connecting to the car
        initial_message = {
            "type": 1,  # Use the appropriate type based on your server documentation
            "status": "connected"
        }
        self.websocket_thread.send_message(initial_message)

    ###########


    def disconnect_anki_vehicle(self):
        if self.car:
            try:
                self.car.disconnect()
                # Perform disconnection
                # You can add more code here for the disconnection process if needed
                QMessageBox.information(self, "Success", "Disconnected from Anki vehicle.")
                del self.car
                self.connectButton.setEnabled(True)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error disconnecting from the Anki vehicle: {str(e)}")
        else:
            QMessageBox.warning(self, "Error", "Please connect to the Anki vehicle first")


    def keyPressEvent(self, event):
        if self.car:
            if event.key() == Qt.Key_Up:  # Increase speed on arrow up key press
                self.speed += 100
                self.change_speed()
            elif event.key() == Qt.Key_Down:  # Decrease speed on arrow down key press
                if self.speed >= 100:
                    self.speed -= 100
                    self.change_speed()
            elif event.key() == Qt.Key_Left:  # Change lane left on arrow left key press
                self.change_lane_left()
            elif event.key() == Qt.Key_Right:  # Change lane right on arrow right key press
                self.change_lane_right()
            elif event.key() == Qt.Key_Space:  # Stop the car when space key is pressed
                self.speed = 0
                self.change_speed()
            elif event.key() == Qt.Key_B:
                self.speed= 300
                self.change_speed()
            elif event.key() == Qt.Key_P:
                self.ping_anki_vehicle()
            elif event.key() == Qt.Key_U:  # Perform U-turn on 'U' key press
                self.make_u_turn()
            elif event.key() == Qt.Key_Escape:  # Disconnect the car on 'Esc' key press
                self.disconnect_anki_vehicle()

    def change_speed(self):
        if self.car:
            try:
                self.car.changeSpeed(self.speed, 1000)
                self.update_speed_label()
                self.update_speed_color()  # Update the color of the label text based on speed change
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error changing speed: {str(e)}")

    def update_speed_label(self):
        if self.car:
            self.speedLabel.setText(f"Current Speed: {self.speed}")

    def update_speed_color(self):
        if self.car:
            # Change the color of the speedLabel text based on speed increase or decrease
            if self.speed > self.prev_speed:
                self.speedLabel.setStyleSheet("QLabel { color: green; }")
            elif self.speed < self.prev_speed:
                self.speedLabel.setStyleSheet("QLabel { color: red; }")
            else:
                self.speedLabel.setStyleSheet("QLabel { color: black; }")
            self.prev_speed = self.speed  # Update the previous speed

    def change_lane_left(self):
        if self.car:
            try:
                self.car.changeLaneLeft(1000, 1000)
                self.update_lane_label("left")
                self.update_lane_change_color("left")  # Update lane change color
            except Exception as e:
                self.display_error_message(f"Error changing lane left: {str(e)}")

    def change_lane_right(self):
        if self.car:
            try:
                self.car.changeLaneRight(1000, 1000)
                self.update_lane_label("right")
                self.update_lane_change_color("right")  # Update lane change color
            except Exception as e:
                self.display_error_message(f"Error changing lane right: {str(e)}")

    def update_lane_label(self, direction):
        if direction == "left":
            self.laneChangeLabel.setText("Changed lane to left")
        elif direction == "right":
            self.laneChangeLabel.setText("Changed lane to right")
        else:
            self.laneChangeLabel.setText("Unknown lane change")

    def update_lane_change_color(self, direction):
        if direction == "left":
            self.laneChangeLabel.setStyleSheet("QLabel { color: orange; }")  # Change color for left lane change
        elif direction == "right":
            self.laneChangeLabel.setStyleSheet("QLabel { color: yellow; }")  # Change color for right lane change
        else:
            self.laneChangeLabel.setStyleSheet(
                "QLabel { color: red; }")  # Reset color to default if unknown direction

    def ping_anki_vehicle(self):
        if self.car:
            try:
                self.car.ping()  # Use the ping function from the Overdrive SDK
                self.display_ping_message()  # Call the function to update the UI label
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error sending ping: {str(e)}")

    def display_ping_message(self):
        # Assuming pingLabel is a QLabel widget in your UI
        self.pingLabel.setText("Ping sent to Anki vehicle")
        self.pingLabel.setStyleSheet("QLabel { color: pink; }")  # Change label color to pink


####################################### sending to the Server #####################
    def send_data(self, data):
        # Use WebSocketThread to send data
        self.websocket_thread.send_message(data)

    def send_coop_awareness_update(self, car_id, intended_range_mm, vehicle_type, length_mm, width_mm,
                                   longitudal_acceleration, yaw_rate, acceleration_control, exterior_lights):
        """
        Send the CoopAwarenessUpdate message to the server.
        """
        coop_awareness_message = {
            "type": 3,
            "car_id": car_id,
            "intended_range_in_mm": intended_range_mm,
            "vehicle_type": vehicle_type,
            "length": length_mm,
            "width": width_mm,
            "longitudal_acceleration": longitudal_acceleration,
            "yaw_rate": yaw_rate,
            "acceleration_control": acceleration_control,
            "exterior_lights": exterior_lights
        }
        self.send_data(coop_awareness_message)

    def location_change_callback(self, addr, location, piece, speed, clockwise):
        self.locationLabel.setText(f"Location: {location}")
        self.pieceLabel.setText(f"Piece ID: {piece}")
        self.speedLabel2.setText(f"Speed: {speed}")
        self.clockwiseLabel.setText(f"Clockwise: {clockwise}")

        # Assuming you have access to these values in your callback
        self.send_position_update(location, piece, 0, speed)
        self.send_transition_update(piece, 0, 50, clockwise)

        # Sending CoopAwarenessUpdate message
        self.send_coop_awareness_update("12345678", 4000, "Car", 800, 400, 0, 0,
                                        {"brake_pedal_engaged": False, "gas_pedal_engaged": True,
                                         "emergency_brake_engaged": False, "collision_warning_engaged": False,
                                         "acc_engaged": False, "cruise_control_engaged": False,
                                         "speed_limiter_engaged": False},
                                        True)


    def send_tracking_message(self, is_tracking):
        tracking_message = {
            "type": 5,
            "isTracking": is_tracking
        }

        self.send_data(tracking_message)

    def send_position_update(self, location_id, road_piece_id, offset_from_road_center_mm, speed_mm_per_sec):
        position_update_message = {
            "type": 1,  # Corrected to 1 for position update
            "location_id": location_id,
            "road_piece_id": road_piece_id,
            "offset_from_road_center_mm": offset_from_road_center_mm,
            "speed_mm_per_sec": speed_mm_per_sec
        }
        self.send_data(position_update_message)

    def send_transition_update(self, road_piece_id, previous_road_piece_id, offset_from_road_center_mm,
                               driving_direction):
        # Convert boolean to integer if needed
        driving_direction = int(driving_direction)

        transition_update_message = {
            "type": 2,
            "road_piece_id": road_piece_id,
            "previous_road_piece_id": previous_road_piece_id,
            "offset_from_road_center_mm": offset_from_road_center_mm,
            "driving_direction": driving_direction
        }
        self.send_data(transition_update_message)

    # You might need to adjust the
    def closeEvent(self, event):
        # Override the closeEvent method to handle window close
        self.websocket_thread.running = False
        if self.car:
            try:
                self.car.disconnect()
            except Exception as e:
                print(f"Error disconnecting from the Anki vehicle: {str(e)}")
        event.accept()

###########
class WelcomeWindow(QMainWindow):
    def __init__(self):
        super(WelcomeWindow, self).__init__()
        loadUi("welcome_window.ui", self)
        self.startButton.clicked.connect(self.open_set_connection_window)
        self.websocket_thread = WebSocketThread(self)
        self.websocket_thread.start()
    def open_set_connection_window(self):
        self.set_connection_window = SetConnectionWindow()
        self.set_connection_window.show()
        self.close()

def main():
    app = QApplication([])
    window = WelcomeWindow()
    window.show()
    app.exec_()

if __name__ == '__main__':
    main()

