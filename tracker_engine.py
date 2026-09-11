import cv2

class ObjectTracker:
    """Handles the initialization and updating of the OpenCV object tracker
       We use CSRT for its high accuracy, scale handling, and robustness against occlusion (relative to other tracker in OpenCV)"""
    def __init__(self):
        self.tracker = None
        self.is_tracking = False

    def start_tracking(self, frame, bbox):
        """Initializes the CSRT tracker with the starting frame and the selected bounding box"""
        #create a CSRT tracker instance
        self.tracker = cv2.TrackerCSRT_create()
        #initialize it with the current frame and coordinates
        self.tracker.init(frame, bbox)
        self.is_tracking = True

    def update_tracker(self, frame):
        """Updates the tracker with the new frame
        Returns: 
            - is_success (bool): True if the object is found, False if lost.
            - bbox (tuple): The new coordinates (x, y, w, h)"""
        
        if not self.is_tracking or self.tracker is None:
            return False, None

        # OpenCV tracker update function
        is_success, bbox = self.tracker.update(frame)
        return is_success, bbox

    def stop_tracking(self):
        """Stops the tracking process and clears the tracker object."""
        self.tracker = None
        self.is_tracking = False