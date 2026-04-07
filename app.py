import cv2
import time

OUT_DEVICE = "/dev/video40"
IN_DEVICE = "/dev/video41"


def open_cam(dev, name):
    cap = cv2.VideoCapture(dev, cv2.CAP_V4L2)
    if not cap.isOpened():
        print(f"[ERROR] {name} ochilmadi: {dev}")
    return cap


cap_out = open_cam(OUT_DEVICE, "OUT")
cap_in = open_cam(IN_DEVICE, "IN")

prev_time = time.time()

while True:
    ret_out, frame_out = cap_out.read()
    ret_in, frame_in = cap_in.read()

    # reconnect
    if not ret_out:
        print("[WARN] OUT reconnect...")
        cap_out.release()
        cap_out = open_cam(OUT_DEVICE, "OUT")
        continue

    if not ret_in:
        print("[WARN] IN reconnect...")
        cap_in.release()
        cap_in = open_cam(IN_DEVICE, "IN")
        continue

    # FPS hisoblash
    current_time = time.time()
    fps = 1 / (current_time - prev_time)
    prev_time = current_time

    # FPS chiqarish
    cv2.putText(frame_out, f"OUT FPS: {int(fps)}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.putText(frame_in, f"IN FPS: {int(fps)}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow("OUT Virtual Cam", frame_out)
    cv2.imshow("IN Virtual Cam", frame_in)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap_out.release()
cap_in.release()
cv2.destroyAllWindows()
