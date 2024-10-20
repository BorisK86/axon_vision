from viewer import Viewer
from streamer import Streamer
from detector import Detector
import multiprocessing as mp


class Analyzer:

    def __init__(self, path: str):
        self._path = path

        viewer_in, detector_out = mp.Pipe()
        detector_in, streamer_out = mp.Pipe()

        self._components = [
            Viewer(viewer_in),
            Detector(detector_in, detector_out),
            Streamer(path, streamer_out)
        ]

    def start(self) -> None:
        for component in self._components:
            component.start()

    def stop(self) -> None:
        for component in self._components:
            component.stop()
        for component in self._components:
            component.join()
