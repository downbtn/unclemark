import cv2
import numpy as np

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (7, 7), 0)

    # Adaptive threshold
    thresh = cv2.adaptiveThreshold(
        blur, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        31, 5
    )

    # Edges
    edges = cv2.Canny(blur, 50, 150)

    # Combine
    combined = cv2.bitwise_or(thresh, edges)

    # FILL the object
    kernel = np.ones((7, 7), np.uint8)
    combined = cv2.dilate(combined, kernel, iterations=2)
    combined = cv2.morphologyEx(combined, cv2.MORPH_CLOSE, kernel, iterations=2)

    contours, _ = cv2.findContours(
        combined, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    if contours:
        cnt = max(contours, key=cv2.contourArea)
        area = cv2.contourArea(cnt)

        print("Area:", area)  # debug

        if area > 500:   # LOWER threshold
            x, y, w, h = cv2.boundingRect(cnt)

            # DRAW rectangle
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # DRAW top-left dot
            cv2.circle(frame, (x, y), 6, (0, 0, 255), -1)

            # DRAW text
            cv2.putText(
                frame, f"({x},{y})",
                (x + 10, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6, (0, 0, 255), 2
            )

    cv2.imshow("Detected", frame)
    cv2.imshow("Mask", combined)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
