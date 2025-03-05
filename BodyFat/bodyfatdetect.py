import os
import cv2
import numpy as np
import time
import pandas as pd
import joblib


model_path = 'BodyFat/newtrainedmodel.pkl'
model = joblib.load(model_path)

position = (50, 50)
font = cv2.FONT_HERSHEY_SIMPLEX  
font_scale = 1  
color = (0, 0, 0) 
thickness = 2  

# Function to calculate pixel per cm ratio
def calculate_pixel_per_cm(reference_height_pixels, user_height_cm):
    return user_height_cm / reference_height_pixels

# Segment the body part using edge detection
def segment_body_parts(gray_image):
    blurred = cv2.GaussianBlur(gray_image, (5, 5), 0)
    edges = cv2.Canny(blurred, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    return contours

# Calculate the circumference of body parts from contours
def calculate_circumferences(contours):
    body_parts_circumference = [cv2.arcLength(contour, True) for contour in contours]
    return body_parts_circumference

# Capture image from camera with live preview
def capture_image(nam, camera_index=0, delay=10):
    cap = cv2.VideoCapture(camera_index)
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return None

    print(f"Adjust your posture. Camera will capture image in {delay} seconds.")

    start_time = time.time()
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read image from camera.")
            return None

        # Show live preview from the camera
        cv2.imshow(f"Camera Preview for  {nam}. (Wait for {delay} seconds to capture image)", frame)

        # Check if the delay time has passed
        if time.time() - start_time >= delay:
            break

        # Allow the user to exit the camera preview early by pressing 'q'
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cap.release()
            cv2.destroyAllWindows()
            return None

    cap.release()
    cv2.destroyAllWindows()
    
    return frame

# Function to edit image and select the body part
def edit_image(image):
    edited_image = image.copy()
    drawing = False
    start_point = (-1, -1)
    end_point = (-1, -1)

    def draw_rectangle(event, x, y, flags, param):
        nonlocal start_point, end_point, drawing
        if event == cv2.EVENT_LBUTTONDOWN:
            drawing = True
            start_point = (x, y)

        elif event == cv2.EVENT_MOUSEMOVE and drawing:
            end_point = (x, y)
        elif event == cv2.EVENT_LBUTTONUP:
            drawing = False
            end_point = (x, y)

    # Set up the mouse callback
    cv2.namedWindow("Edit Image")
    cv2.setMouseCallback("Edit Image", draw_rectangle)

    while True:
        temp_image = edited_image.copy()
        if start_point != (-1, -1) and end_point != (-1, -1):
            cv2.rectangle(temp_image, start_point, end_point, (0, 255, 0), 2)

        text = f"Mark/Mention position in Input Image. (Q / C- Next)"
        cv2.putText(temp_image, text, position, font, 0.6, color, thickness)
        cv2.imshow("Edit Image", temp_image)

        key = cv2.waitKey(1) & 0xFF
        if key == ord('q'):
            break
        elif key == ord('c'):
            break

    cv2.destroyAllWindows()
    return start_point, end_point

# Function to capture height in pixels
def get_height_pixels(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        global known_height_pixels
        known_height_pixels = y
        print(f"Height in pixels captured: {known_height_pixels}")

# Function to get user input for height, weight, age, gender, and body part
# def get_user_input():
#     height = float(input("Enter your height (cm): "))
#     weight = float(input("Enter your weight (kg): "))
#     age = int(input("Enter your age: "))
#     gender = input("Enter your gender (male/female): ").strip().lower()
#     body_part = input("Enter the body part for fat percentage prediction (Neck, Abdomen, Waist, Hip, Thigh, Biceps): ").strip().lower()
    
#     return {
#         'Height': height,
#         'Weight': weight,
#         'Age': age,
#         'Gender': gender,
#         'BodyPart': body_part
#     }

# Main function to process images, calculate circumferences, and predict body fat
def main_predict(user_data):
    global known_height_pixels
    known_height_pixels = 0

    # Get user input
    # user_data = get_user_input()

    # Capture reference image from camera
    print("Capturing reference image...")
    nam = "reference"
    reference_image = capture_image(nam, delay=10)
    if reference_image is None:
        return

    # Display the reference image and ask for user height
    cv2.imshow("Captured Input Image. (Enter - Continue)", reference_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # Get user height
    user_height_cm = user_data['Height']

    # Get height in pixels from reference image
    print("Click to measure your height in pixels from the reference image.")
    text = f"Mark/Mention position in Input Image. (Enter - Continue)"
    cv2.putText(reference_image, text, position, font, 0.6, color, thickness)
    cv2.imshow("Reference Image", reference_image)
    cv2.setMouseCallback("Reference Image", get_height_pixels)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    if known_height_pixels == 0:
        print("Error: Height in pixels not captured.")
        return

    # Calculate pixel per cm ratio
    pixel_per_cm = calculate_pixel_per_cm(known_height_pixels, user_height_cm)

    # Directions to capture
    directions = ["front", "back", "left side", "right side"]
    circumferences_cm = []

    for direction in directions:
        nam = direction
        print(f"Capturing body part image from the {direction} view...")
        body_part_image = capture_image(nam, delay=10)
        if body_part_image is None:
            return

        # Show the captured body part image
        cv2.imshow(f"Captured {direction.capitalize()} View. (Enter - Continue)", body_part_image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

        # Edit the body part image
        start_point, end_point = edit_image(body_part_image)

        if start_point != (-1, -1) and end_point != (-1, -1):
            x1, y1 = start_point
            x2, y2 = end_point

            x1, y1 = max(x1, 0), max(y1, 0)
            x2, y2 = min(x2, body_part_image.shape[1]), min(y2, body_part_image.shape[0])

            selected_region = body_part_image[y1:y2, x1:x2]
            if selected_region.size == 0:
                print(f"Error: No valid region selected in {direction} view.")
                return

            gray_selected_region = cv2.cvtColor(selected_region, cv2.COLOR_BGR2GRAY)
            selected_contours = segment_body_parts(gray_selected_region)

            if selected_contours:
                body_parts_circumference = calculate_circumferences(selected_contours)
                circumference_cm = body_parts_circumference[0] * pixel_per_cm
                print(f"Circumference Measurement (in cm) for {direction} view: {circumference_cm}")
                circumferences_cm.append(circumference_cm)
            else:
                msg = f"Error: No contours found in {direction} view."
                return [msg, 0]
        else:
            msg =f"Error: No valid selection made in {direction} view."
            return [msg, 0]
    
    # Calculate average circumference from all views
    if circumferences_cm:
        avg_circumference_cm = np.mean(circumferences_cm)
        print(f"Average Circumference Measurement (in cm): {avg_circumference_cm}")

        # Prepare data for prediction
        input_data = {
            'Age': [user_data['Age']],
            'Gender': [0 if user_data['Gender'] == 'male' else 1],
            'Weight': [user_data['Weight']],
            'Height': [user_data['Height']],
            'Neck': [avg_circumference_cm if user_data['BodyPart'] == 'neck' else 0],
            'Chest': [0],
            'Abdomen': [avg_circumference_cm if user_data['BodyPart'] == 'abdomen' else 0],
            'Hip': [avg_circumference_cm if user_data['BodyPart'] == 'hip' else 0],
            'Thigh': [avg_circumference_cm if user_data['BodyPart'] == 'thigh' else 0],
            'Waist': [avg_circumference_cm if user_data['BodyPart'] == 'waist' else 0],
            'Biceps': [avg_circumference_cm if user_data['BodyPart'] == 'biceps' else 0],
            'neck%': [0],
            'chest%': [0],
            'abdom%': [0],
            'hip%': [0],
            'thigh%': [0],
            'waist%': [0],
            'biceps%': [0]
        }

        input_df = pd.DataFrame(input_data)

        # Predict body fat percentage
        predicted_body_fat = model.predict(input_df)
        predicted_fat_percentage = predicted_body_fat[0] * 100
        msg = f"Predicted body fat percentage for {user_data['BodyPart'].capitalize()}: {predicted_fat_percentage:.2f}%"
        return predicted_fat_percentage * 100
    else:
        msg = "Error: No valid circumferences calculated."
        return [msg, 0]


# if __name__ == '__main__':
#     main() 

