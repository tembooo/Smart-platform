'''
import cv2

rtsp_url = "rtsp://admin:1345%21Abc@169.254.25.90:554/Streaming/Channels/101"

cap = cv2.VideoCapture(rtsp_url, cv2.CAP_FFMPEG)

# ست کردن بافر خیلی کوچک (یا صفر)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

while True:
    ret, frame = cap.read()
    if not ret:
        print("❌ Frame not received")
        break

    cv2.imshow("Live Stream", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
'''
# ffplay -rtsp_transport tcp -fflags nobuffer -flags low_delay -framedrop "rtsp://admin:1345%21Abc@169.254.25.90:554/Streaming/Channels/101"

import av
import cv2

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

for packet in container.demux(stream):
    for frame in packet.decode():
        img = frame.to_ndarray(format="bgr24")
        cv2.imshow("Live Zero-Delay", img)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
