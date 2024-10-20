import cv2
import multiprocessing as mp
from multiprocessing.connection import Connection


class Streamer(mp.Process):

    def __init__(self, path: str, connection: Connection):
        super().__init__()
        self._path = path
        self._connection = connection
        self._stop_event = mp.Event()

    def run(self) -> None:
        video = cv2.VideoCapture(self._path)
        frame_count = int(video.get(cv2.CAP_PROP_FRAME_COUNT))
        fps = video.get(cv2.CAP_PROP_FPS)
        dt_ms = int(1000/fps)
        frame_number = 0
        print(f'Streamer started: {frame_count} frames @ {fps} FPS')
        while not self._stop_event.is_set():
            if frame_number == frame_count:
                break
            ret, frame = video.read()
            if ret:
                self._connection.send([frame, frame_number])
                cv2.waitKey(dt_ms)
            frame_number += 1
        video.release()
        print('Streamer stopped')

    def stop(self) -> None:
        self._stop_event.set()
