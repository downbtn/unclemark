import cv2
from ultralytics import YOLO

# Load pretrained YOLO model
model = YOLO("yolov8n.pt")  # nano = fastest

# Open webcam (0 = default camera)
cap = cv2.VideoCapture(0)

if not cap.isOpened():
    raise RuntimeError("Could not open webcam")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Run inference on the frame
    results = model(frame, conf=0.25, verbose=False)

    # Default if nothing detected
    top_left = None

    # If at least one detection exists
    if len(results[0].boxes) > 0:
        # Take the largest box (often the main object)
        boxes = results[0].boxes.xyxy.cpu().numpy()

        # Choose the largest bounding box by area
        areas = (boxes[:, 2] - boxes[:, 0]) * (boxes[:, 3] - boxes[:, 1])
        idx = areas.argmax()

        x1, y1, x2, y2 = boxes[idx]
        top_left = (int(x1), int(y1))

        # Draw bounding box and point
        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
        cv2.circle(frame, top_left, 6, (0, 0, 255), -1)

        print("Top-left:", top_left)

    # Display frame
    cv2.imshow("Webcam Detection", frame)

    # Press 'q' to quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
