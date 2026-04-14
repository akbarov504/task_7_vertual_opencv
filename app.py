import cv2
import time
import threading

OUT_URL = "udp://127.0.0.1:23000"
IN_URL = "udp://127.0.0.1:23001"


class StreamReader:
    def __init__(self, url, name):
        self.url = url
        self.name = name
        self.cap = None
        self.frame = None
        self.lock = threading.Lock()
        self.running = False
        self.thread = None
        self.last_frame_time = None
        self.fps = 0.0

    def open(self):
        if self.cap is not None:
            try:
                self.cap.release()
            except Exception:
                pass

        self.cap = cv2.VideoCapture(self.url, cv2.CAP_FFMPEG)

        if not self.cap.isOpened():
            print(f"[ERROR] {self.name} stream ochilmadi: {self.url}")
            return False

        print(f"[INFO] {self.name} stream ochildi")
        return True

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self.update, daemon=True)
        self.thread.start()

    def update(self):
        while self.running:
            if self.cap is None or not self.cap.isOpened():
                if not self.open():
                    time.sleep(0.5)
                    continue

            ret, frame = self.cap.read()
            if not ret:
                print(f"[WARN] {self.name} reconnect...")
                try:
                    self.cap.release()
                except Exception:
                    pass
                self.cap = None
                time.sleep(0.3)
                continue

            now = time.time()
            if self.last_frame_time is not None:
                dt = now - self.last_frame_time
                if dt > 0:
                    instant_fps = 1.0 / dt
                    self.fps = self.fps * 0.85 + instant_fps * 0.15
            self.last_frame_time = now

            with self.lock:
                self.frame = frame

    def read_latest(self):
        with self.lock:
            if self.frame is None:
                return None
            return self.frame.copy()

    def stop(self):
        self.running = False
        if self.thread is not None:
            self.thread.join(timeout=1)
        if self.cap is not None:
            try:
                self.cap.release()
            except Exception:
                pass


out_stream = StreamReader(OUT_URL, "OUT")
in_stream = StreamReader(IN_URL, "IN")

out_stream.start()
in_stream.start()

print("[INFO] UDP realtime stream ishlayapti. Chiqish uchun q bosing.")

try:
    while True:
        frame_out = out_stream.read_latest()
        frame_in = in_stream.read_latest()

        if frame_out is not None:
            cv2.putText(frame_out, f"OUT FPS: {out_stream.fps:.1f}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.imshow("OUT UDP REALTIME", frame_out)

        if frame_in is not None:
            cv2.putText(frame_in, f"IN FPS: {in_stream.fps:.1f}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            cv2.imshow("IN UDP REALTIME", frame_in)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

finally:
    out_stream.stop()
    in_stream.stop()
    cv2.destroyAllWindows()