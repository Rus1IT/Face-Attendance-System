# face_module.py
import pickle
import face_recognition
import numpy as np
import cv2

def load_encodings(filepath='EncodeFile.p'):
    print("Loading encodings...")
    try:
        with open(filepath, 'rb') as file:
            encodeListKnownWithIds = pickle.load(file)
        print("Encodings loaded.")
        return encodeListKnownWithIds[0], encodeListKnownWithIds[1]
    except Exception as e:
        print(f"Error loading encodings: {e}")
        return [], []

def process_frame_for_faces(img, yolo_bbox):
    if yolo_bbox is None:
        return [], []
        
    x1, y1, x2, y2 = yolo_bbox
    
    # Convert bbox to (top, right, bottom, left) format
    css_bbox = (y1, x2, y2, x1)
    
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Get face encodings using known location to speed up processing
    encodeCurFrame = face_recognition.face_encodings(imgRGB, known_face_locations=[css_bbox])
    
    return [css_bbox], encodeCurFrame

def find_match(encodeFace, encodeListKnown, studentIds):
    # Check for empty database
    if not encodeListKnown or len(encodeListKnown) == 0:
        return None 

    # Compare faces and get distances
    matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
    faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
    
    if len(faceDis) == 0:
        return None

    # Find the best match index
    matchIndex = np.argmin(faceDis)

    # Verify if it's a true match
    if matches[matchIndex]:
        return studentIds[matchIndex]
        
    return None