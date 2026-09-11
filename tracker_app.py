import os
import cv2
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.uic import loadUi

from tracker_engine import ObjectTracker

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Load the UI file
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        loadUi("tracker.ui", self)

        self.setWindowTitle("EyeGo Object Tracker")
        self.resize(1000, 900)

        # initialize the webcam (0 for the default camera)
        self.camera = cv2.VideoCapture(0)

        # initialize the tracking engine
        self.tracker_engine = ObjectTracker()
        
        # variable to store the clean frame for tracker initialization
        self.current_raw_frame = None

        #setup a timer for the live video feed
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30)

        #connect the mouse drawing signal to the tracker initialization method
        self.video_label.bbox_drawn.connect(self.initialize_tracker_with_bbox)

        self.status_label.setText("Status : Waiting for input...")

    def update_frame(self):
        """Reads a new frame from the webcam, handles drawing/tracking logic, and updates the UI"""
        is_success, frame = self.camera.read()
        if not is_success:
            return

        # keep a clean copy of the frame without any drawings
        self.current_raw_frame = frame.copy()

        # calculate scaling factors to match UI coordinates with real frame dimensions
        frame_h, frame_w = frame.shape[:2]
        label_w, label_h = self.video_label.width(), self.video_label.height()
        scale_x = frame_w / label_w
        scale_y = frame_h / label_h

        #Scenario 1: the user is currently dragging the mouse to draw
        if self.video_label.is_drawing and self.video_label.start_point and self.video_label.current_point:
            self.status_label.setText("Status : Drawing BBox...")

            x1 = int(self.video_label.start_point[0] * scale_x)
            y1 = int(self.video_label.start_point[1] * scale_y)
            x2 = int(self.video_label.current_point[0] * scale_x)
            y2 = int(self.video_label.current_point[1] * scale_y)
            
            # Draw a blue rectangle during the drag operation
            cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)

        #Scenario 2: tracking is active
        elif self.tracker_engine.is_tracking:
            success, bbox = self.tracker_engine.update_tracker(frame)
            if success:
                #object found: draw a green rectangle
                self.status_label.setText("Status : Tracking Active!")
                x, y, w, h = [int(v) for v in bbox]
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, "Tracking", (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            else:
                #object lost: show a red warning message
                self.status_label.setText("Status : Object Lost!")
                cv2.putText(frame, "Object Lost", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
                self.tracker_engine.stop_tracking()

        # Scenario 3: Idle
        else:
            if self.status_label.text() == "Status : Object Lost!":
                cv2.putText(frame, "Object Lost! Please draw a new BBox.", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
            else:
                self.status_label.setText("Status : Waiting for input...")

        # Display the processed frame on the UI
        self.display_frame(frame)

    def display_frame(self, frame):
        """Convert an OpenCV frame to QPixmap and display it on the QLabel"""
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w, ch = frame_rgb.shape
        bytes_per_line = ch * w

        q_img = QImage(frame_rgb.data, w, h, bytes_per_line, QImage.Format_RGB888)
        self.video_label.setPixmap(QPixmap.fromImage(q_img))
        self.video_label.setScaledContents(True)

    def initialize_tracker_with_bbox(self, ui_x, ui_y, ui_w, ui_h):
        """Triggered when the user finishes drawing the BBox
           Scales the coordinates and starts the tracking algorithm"""
        if self.current_raw_frame is None:
            return

        # Recalculate scaling factors for precision
        frame_h, frame_w = self.current_raw_frame.shape[:2]
        label_w, label_h = self.video_label.width(), self.video_label.height()
        scale_x = frame_w / label_w
        scale_y = frame_h / label_h

        # convert UI bounding box coordinates to actual frame coordinates
        real_x = int(ui_x * scale_x)
        real_y = int(ui_y * scale_y)
        real_w = int(ui_w * scale_x)
        real_h = int(ui_h * scale_y)

        real_bbox = (real_x, real_y, real_w, real_h)

        # Initialize the tracker with the clean frame and scaled coordinates
        self.tracker_engine.start_tracking(self.current_raw_frame, real_bbox)

    def closeEvent(self, event):
        """Handles the window close event to safely release the camera and prevent memory leaks."""        
        if self.camera.isOpened():
            self.camera.release()
        self.timer.stop()
        event.accept()


    def keyPressEvent(self, event):
        """if user press 'Q' the program exits"""
        if event.key() == Qt.Key_Q:
            self.close()