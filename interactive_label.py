from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QMouseEvent

class InteractiveVideoLabel(QLabel):
    """A custom QLabel that handles mouse events to allow the user to draw a bounding box (BBox) for object tracking"""

    # signal emitted when the user finishes drawing
    bbox_drawn = pyqtSignal(int, int, int, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.start_point = None
        self.current_point = None
        self.is_drawing = False

    def mousePressEvent(self, event: QMouseEvent):
        """Triggered when the user presses a mouse button"""
        if event.button() == Qt.LeftButton:
            self.start_point = (event.x(), event.y())
            self.current_point = self.start_point
            self.is_drawing = True

    def mouseMoveEvent(self, event: QMouseEvent):
        """Triggered when the user drags the mouse while holding the button."""
        if self.is_drawing:
            self.current_point = (event.x(), event.y())

    def mouseReleaseEvent(self, event: QMouseEvent):
        """Triggered when the user releases the mouse button."""
        if event.button() == Qt.LeftButton and self.is_drawing:
            self.is_drawing = False
            self.current_point = (event.x(), event.y())
            
            # calculate the top left corner (x,y) and the width/height
            x1, y1 = self.start_point
            x2, y2 = self.current_point
            
            x = min(x1, x2)
            y = min(y1, y2)
            w = abs(x2 - x1)
            h = abs(y2 - y1)
            
            #safety check: ensure it's a valid rectangle (prevents accidental clicks)
            if w > 10 and h > 10:
                # emit the signal to notify the MainWindow
                self.bbox_drawn.emit(x, y, w, h)