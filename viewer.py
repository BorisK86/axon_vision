import cv2
import numpy as np
import multiprocessing as mp
from typing import Tuple
from datetime import datetime
from multiprocessing.connection import Connection


_text_properties = {
    'org':       (0, 30),
    'fontFace':  cv2.FONT_HERSHEY_SIMPLEX,
    'fontScale': 1,
    'color':     (255, 255, 255),
    'thickness': 2,
    'lineType':  cv2.LINE_AA
}

_contour_properties = {
    'color':     (0, 255, 0),
    'thickness': 2
}


class Viewer(mp.Process):

    def __init__(self, connection: Connection):
        super().__init__()
        self._connection = connection
        self._stop_event = mp.Event()

    @staticmethod
    def _draw_contours(frame: np.ndarray, contours: Tuple[np.ndarray]) -> None:
        for contour in contours:
            if cv2.contourArea(contour) < 300:
                continue
            (x, y, w, h) = cv2.boundingRect(contour)
            cv2.rectangle(img=frame, pt1=(x, y), pt2=(x + w, y + h), **_contour_properties)

    @staticmethod
    def _draw_time(frame: np.ndarray) -> None:
        time_now = datetime.now().strftime('%H:%M:%S.%f')
        cv2.rectangle(img=frame, pt1=(0, 0), pt2=(280, 40), color=(0, 0, 0), thickness=-1)
        cv2.putText(img=frame, text=time_now, **_text_properties)

    def run(self) -> None:
        print('Viewer started')
        while not self._stop_event.is_set():
            if not self._connection.poll(0.2):
                continue
            frame, frame_number, counters = self._connection.recv()
            self._draw_contours(frame, counters)
            self._draw_time(frame)
            cv2.imshow('Viewer', frame)
            cv2.waitKey(1)
        cv2.destroyAllWindows()
        print('Viewer stopped')

    def stop(self) -> None:
        self._stop_event.set()
