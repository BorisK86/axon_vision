from viewer import Viewer
from streamer import Streamer
from detector import Detector
import multiprocessing as mp


class Analyzer:

    def __init__(self, path: str):
        self._path = path

        self._stream_finished = mp.Event()
        viewer_in, detector_out = mp.Pipe()
        detector_in, streamer_out = mp.Pipe()

        self._components = [
            Viewer(viewer_in),
            Detector(detector_in, detector_out),
            Streamer(path, streamer_out, self._stream_finished)
        ]

    def start(self) -> None:
        for component in self._components:
            component.start()
        self._stream_finished.wait()
        self._stop()

    def _stop(self) -> None:
        for component in self._components:
            component.stop()
        for component in self._components:
            component.join()
