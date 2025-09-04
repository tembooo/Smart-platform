import av
import cv2
import mediapipe as mp

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

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=2,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

for packet in container.demux(stream):
    for frame in packet.decode():
        img = frame.to_ndarray(format="bgr24")

        # تبدیل به RGB برای MediaPipe
        img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        result = hands.process(img_rgb)

        if result.multi_hand_landmarks:
            for hand_landmarks in result.multi_hand_landmarks:
                # رسم نقاط دست
                mp_drawing.draw_landmarks(img, hand_landmarks, mp_hands.HAND_CONNECTIONS)

        cv2.imshow("Hand Detection", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cv2.destroyAllWindows()
