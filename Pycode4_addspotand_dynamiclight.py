import av
import cv2
import mediapipe as mp
import numpy as np

rtsp_url = "rtsp://admin:1345%21Abc@169.254.25.90:554/Streaming/Channels/101"

options = {
    "rtsp_transport": "tcp",
    "fflags": "nobuffer",
    "flags": "low_delay",
    "framedrop": "1",
    "strict": "experimental"
}

container = av.open(rtsp_url, options=options)
stream = container.streams.video[0]

# =========================
# MediaPipe Hands
# =========================
mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

# =========================
# نقاط قابل جابجایی ROI (۲۰ نقطه)
# =========================
roi_points = [(100 + i * 20, 100 + (i % 5) * 20) for i in range(20)]
dragging_idx = None

def mouse_event(event, x, y, flags, param):
    global dragging_idx, roi_points
    if event == cv2.EVENT_LBUTTONDOWN:
        for i, (px, py) in enumerate(roi_points):
            if abs(x - px) < 10 and abs(y - py) < 10:
                dragging_idx = i
                break
    elif event == cv2.EVENT_MOUSEMOVE and dragging_idx is not None:
        roi_points[dragging_idx] = (x, y)
    elif event == cv2.EVENT_LBUTTONUP:
        dragging_idx = None

cv2.namedWindow("Hand Detection")
cv2.setMouseCallback("Hand Detection", mouse_event)

# =========================
# پنجره چراغ وضعیت
# =========================
status_win = "Status Light"
cv2.namedWindow(status_win, cv2.WND_PROP_FULLSCREEN)
cv2.setWindowProperty(status_win, cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
cv2.moveWindow(status_win, 1920, 0)  # فرض: مانیتور اول 1920x1080 است

# =========================
# حلقه اصلی
# =========================
for packet in container.demux(stream):
    for frame in packet.decode():
        img = frame.to_ndarray(format="bgr24")
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        result = hands.process(img_rgb)

        pts = np.array(roi_points, np.int32).reshape((-1, 1, 2))
        inside = False

        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                mp_drawing.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)
                for lm in hand_landmarks.landmark:
                    h, w, _ = img.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    if cv2.pointPolygonTest(pts, (cx, cy), False) >= 0:
                        inside = True
                        break

        # تغییر رنگ ROI
        border_color = (0, 255, 0) if not inside else (0, 0, 255)
        fill_color = (0, 255, 0, 30) if not inside else (0, 0, 255, 30)

        # پر کردن خیلی کمرنگ (transparency)
        overlay = img.copy()
        cv2.fillPoly(overlay, [pts], fill_color[:3])  # پر کردن
        img = cv2.addWeighted(overlay, 0.2, img, 0.8, 0)  # شفافیت کم

        # رسم بوردر
        cv2.polylines(img, [pts], isClosed=True, color=border_color, thickness=2)

        # رسم دایره روی نقاط
        for (px, py) in roi_points:
            cv2.circle(img, (px, py), 5, (0, 255, 255), -1)

        # چراغ وضعیت (Full screen مانیتور دوم)
        status_img = np.zeros((1080, 1920, 3), dtype=np.uint8)
        light_color = (0, 255, 0) if not inside else (0, 0, 255)
        cv2.circle(status_img, (960, 540), 300, light_color, -1)

        cv2.imshow("Hand Detection", img)
        cv2.imshow(status_win, status_img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cv2.destroyAllWindows()
