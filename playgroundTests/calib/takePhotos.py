import cv2
import os

# === Configuration ===
output_dir = '/home/jur/calibImages/'
image_prefix = 'img'
image_format = 'jpg'
desired_resolution = [1280, 720]
desired_fps = 15

# Create output directory if it doesn't exist
os.makedirs(output_dir, exist_ok=True)

# Open webcam (use 0 or appropriate index)
cap = cv2.VideoCapture(2)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, desired_resolution[0])
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, desired_resolution[1])
cap.set(cv2.CAP_PROP_FPS, desired_fps)

print("[INFO] Press SPACE to save image, ESC to quit.")

img_counter = 0

while True:
    ret, frame = cap.read()
    if not ret:
        print("[ERROR] Failed to grab frame")
        break

    cv2.imshow("Calibration Capture (640x480)", frame)
    key = cv2.waitKey(1)

    if key % 256 == 27:  # ESC
        print("[INFO] Exiting.")
        break
    elif key % 256 == 32:  # SPACE
        filename = f"{image_prefix}_{img_counter:03d}.{image_format}"
        filepath = os.path.join(output_dir, filename)
        cv2.imwrite(filepath, frame)
        print(f"[SAVED] {filepath}")
        img_counter += 1

cap.release()
cv2.destroyAllWindows()