import numpy as np
import cv2

def generate_test_image(width=512, height=512, filename='assets/testImage.png'):
    # Create an empty image with RGB mode
    img = np.zeros((height, width, 3), dtype=np.uint8)
    
    # Generate color gradients
    for y in range(height):
        for x in range(width):
            r = int((x / width) * 255)  # Horizontal gradient for red
            g = int((y / height) * 255)  # Vertical gradient for green
            b = int(((x + y) / (width + height)) * 255)  # Diagonal gradient for blue
            img[y, x] = (b, g, r)  # OpenCV uses BGR format
    
    # Draw some shapes
    #cv2.rectangle(img, (width//4, height//4), (width//2, height//2), (0, 255, 255), -1)  # Yellow rectangle
    #cv2.circle(img, (width//3 + 50, height//3 + 50), 50, (255, 0, 255), -1)  # Magenta circle
    
    # Add random noise
    #noise = np.random.randint(0, 50, (height, width, 3), dtype=np.uint8)
    img = np.clip(img, 0, 255)  # Add noise to image
    
    # Save and show image
    cv2.imwrite(filename, img)

# Generate and display the image
generate_test_image()