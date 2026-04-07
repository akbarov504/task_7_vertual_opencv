import cv2

cap = cv2.VideoCapture("/dev/video40", cv2.CAP_V4L2)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Frame olinmadi")
        break

    cv2.imshow("OUT Virtual Cam", frame)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
cv2.destroyAllWindows()