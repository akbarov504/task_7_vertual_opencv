import time
import cv2
import numpy as np
from multiprocessing import shared_memory


SHM_WIDTH = 640
SHM_HEIGHT = 480
SHM_CHANNELS = 3
SHM_FPS = 10


class SharedFrameReader:
    def __init__(self, shm_name, width, height, channels):
        self.shm_name = shm_name
        self.width = width
        self.height = height
        self.channels = channels
        self.frame_size = width * height * channels
        self.total_size = 16 + self.frame_size

        self.shm = None
        self.buf = None
        self.last_ts = 0
        self.prev_time = None
        self.fps = 0.0

    def connect(self):
        try:
            self.shm = shared_memory.SharedMemory(name=self.shm_name)
            self.buf = self.shm.buf
            print(f"[INFO] {self.shm_name} ga ulandi")
            return True
        except FileNotFoundError:
            return False

    def read(self):
        if self.buf is None:
            return None

        if self.buf[0] != 1:
            return None

        ts = int.from_bytes(self.buf[8:16], byteorder="little", signed=False)
        if ts == self.last_ts:
            return None

        arr = np.ndarray(
            (self.height, self.width, self.channels),
            dtype=np.uint8,
            buffer=self.buf[16:]
        )

        frame = arr.copy()
        self.last_ts = ts

        now = time.time()
        if self.prev_time is not None:
            dt = now - self.prev_time
            if dt > 0:
                instant_fps = 1.0 / dt
                self.fps = self.fps * 0.85 + instant_fps * 0.15
        self.prev_time = now

        return frame

    def close(self):
        if self.shm is not None:
            self.shm.close()


def main():
    out_reader = SharedFrameReader("out_camera_shm", SHM_WIDTH, SHM_HEIGHT, SHM_CHANNELS)
    in_reader = SharedFrameReader("in_camera_shm", SHM_WIDTH, SHM_HEIGHT, SHM_CHANNELS)

    print("[INFO] Shared memory reader start...")

    while not out_reader.connect():
        print("[WAIT] out_camera_shm kutilmoqda...")
        time.sleep(1)

    while not in_reader.connect():
        print("[WAIT] in_camera_shm kutilmoqda...")
        time.sleep(1)

    try:
        while True:
            frame_out = out_reader.read()
            frame_in = in_reader.read()

            if frame_out is not None:
                cv2.putText(frame_out, f"OUT FPS: {out_reader.fps:.1f}", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.imshow("OUT SHM REALTIME", frame_out)

            if frame_in is not None:
                cv2.putText(frame_in, f"IN FPS: {in_reader.fps:.1f}", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                cv2.imshow("IN SHM REALTIME", frame_in)

            if cv2.waitKey(1) & 0xFF == ord("q"):
                break

            time.sleep(0.001)

    finally:
        out_reader.close()
        in_reader.close()
        cv2.destroyAllWindows()


if __name__ == "__main__":
    main()