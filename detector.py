import cv2
import imutils
import multiprocessing as mp
from multiprocessing.connection import Connection


class Detector(mp.Process):

    def __init__(self, connection_in: Connection, connection_out: Connection):
        super().__init__()
        self._connection_in = connection_in
        self._connection_out = connection_out
        self._stop_event = mp.Event()

    def run(self) -> None:
        counter = 0
        prev_frame = None
        print('Detector started')
        while not self._stop_event.is_set():
            if not self._connection_in.poll(0.2):
                continue
            frame, frame_number = self._connection_in.recv()
            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            if counter == 0:
                prev_frame = gray_frame
                counter += 1
            else:
                diff = cv2.absdiff(gray_frame, prev_frame)
                thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)[1]
                thresh = cv2.dilate(thresh, None, iterations=2)
                cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                cnts = imutils.grab_contours(cnts)
                prev_frame = gray_frame
                self._connection_out.send([frame, frame_number, cnts])
        print('Detector stopped')

    def stop(self) -> None:
        self._stop_event.set()
