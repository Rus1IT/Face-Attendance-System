# main.py
import cv2
import cvzone
import time
import random
import pickle
import face_recognition
import threading
from datetime import datetime

from config import CAM_WIDTH, CAM_HEIGHT, DISPLAY_DURATION
from database import get_student_info, mark_attendance, add_new_student_to_db
from face_module import load_encodings, process_frame_for_faces, find_match
from ui_manager import load_ui_elements, draw_student_info, get_student_image, draw_welcome_screen, draw_scanning_ui, draw_take_photo_screen
from gesture_keyboard import draw_and_process_keyboard
from anti_spoofing import LivenessDetector

# Threaded camera class
class VideoStream:
    def __init__(self, src=0, width=640, height=480):
        self.stream = cv2.VideoCapture(src)
        self.stream.set(3, width)
        self.stream.set(4, height)
        (self.grabbed, self.frame) = self.stream.read()
        self.stopped = False
        threading.Thread(target=self.update, args=(), daemon=True).start()

    def update(self):
        while True:
            if self.stopped:
                return
            (self.grabbed, self.frame) = self.stream.read()

    def read(self):
        return self.grabbed, self.frame

    def stop(self):
        self.stopped = True
        self.stream.release()

print("Starting camera...")
cap = VideoStream(src=0, width=CAM_WIDTH, height=CAM_HEIGHT)
time.sleep(1.0) 

imgBackground_original, imgModeList = load_ui_elements()
encodeListKnown, studentIds = load_encodings()

print("Loading anti-spoofing model...")
liveness_detector = LivenessDetector(model_path="model/l_version_1_300.pt", confidence=0.6)
print("Model loaded.")

# Mouse control
click_position = None

def mouse_click(event, x, y, flags, param):
    global click_position
    if event == cv2.EVENT_LBUTTONDOWN:
        click_position = (x, y)

cv2.namedWindow("Face Attendance System")
cv2.setMouseCallback("Face Attendance System", mouse_click)

# Global states
app_state = 'WELCOME' 
mode_type = 0 
current_student_id = -1
student_info = None
img_student = None
display_start_time = 0

temp_student_img = None 
new_student_name = ""

# Background thread variables
cached_faces = []
cached_liveness_status = -1
cached_liveness_conf = 0.0
is_processing = False 

def process_faces_background(frame_to_process):
    # Async face processing (YOLO + Face Rec)
    global cached_faces, cached_liveness_status, cached_liveness_conf
    global current_student_id, student_info, img_student, mode_type, app_state, display_start_time
    global is_processing

    try:
        # Check liveness
        liveness_status, liveness_conf, bbox = liveness_detector.check_liveness(frame_to_process)
        cached_liveness_status = liveness_status
        cached_liveness_conf = liveness_conf

        if bbox is not None:
            faceCurFrame, encodeCurFrame = process_frame_for_faces(frame_to_process, bbox)
            cached_faces = faceCurFrame
            
            # Recognize if real face
            if liveness_status == 1 and encodeCurFrame:
                matched_id = find_match(encodeCurFrame[0], encodeListKnown, studentIds)
                if matched_id:
                    current_student_id = matched_id
                    student_info = get_student_info(current_student_id)
                    
                    if student_info:
                        img_student = get_student_image(current_student_id)
                        last_attendance = student_info.get('last_attendance_time')
                        
                        if isinstance(last_attendance, str):
                            last_attendance = datetime.strptime(last_attendance, "%Y-%m-%d %H:%M:%S")
                        elif last_attendance is None:
                            last_attendance = datetime(2000, 1, 1)
                            
                        secondsElapsed = (datetime.now() - last_attendance).total_seconds()
                        
                        # Update attendance
                        if secondsElapsed > 30:
                            mark_attendance(current_student_id, student_info.get('total_attendance', 0))
                            student_info['total_attendance'] = student_info.get('total_attendance', 0) + 1 
                            mode_type = 2 
                        else:
                            mode_type = 3 
                        
                        app_state = 'SHOW_RESULT'
                        display_start_time = time.time()
        else:
            cached_faces = []
            
    except Exception as e:
        print(f"Bg thread error: {e}")
    finally:
        is_processing = False

# Main loop
while True:
    success, img = cap.read()
    if not success or img is None: 
        continue

    imgBackground = imgBackground_original.copy()
    
    cx, cy = -1, -1
    if click_position:
        cx, cy = click_position
        click_position = None 

    # --- WELCOME STATE ---
    if app_state == 'WELCOME':
        imgBackground, button_bbox = draw_welcome_screen(imgBackground)
        bx1, by1, bx2, by2 = button_bbox
        if bx1 <= cx <= bx2 and by1 <= cy <= by2:
            app_state = 'SCANNING'

    else:
        # --- ADD_STUDENT_NAME STATE ---
        if app_state == 'ADD_STUDENT_NAME':
            img, new_student_name, action = draw_and_process_keyboard(img, new_student_name)
            
            cv2.rectangle(img, (0, 0), (640, 50), (0, 0, 0), cv2.FILLED)
            cv2.putText(img, f"Name: {new_student_name}_", (10, 35), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            
            if action == 'SAVE' and len(new_student_name) > 0:
                print("Saving student...")
                new_id = str(random.randint(100000, 999999))
                cv2.imwrite(f'Images/{new_id}.jpg', temp_student_img)
                
                add_new_student_to_db(new_id, new_student_name)
                
                img_rgb = cv2.cvtColor(temp_student_img, cv2.COLOR_BGR2RGB)
                encode_temp = face_recognition.face_encodings(img_rgb)
                
                # Update encodings
                if encode_temp:
                    encodeListKnown.append(encode_temp[0])
                    studentIds.append(new_id)
                    with open('EncodeFile.p', 'wb') as f:
                        pickle.dump([encodeListKnown, studentIds], f)
                    print(f"Encodings updated for {new_student_name}")
                else:
                    print("No face found. Saved without encoding.")
                
                new_student_name = ""
                temp_student_img = None
                app_state = 'SCANNING'
                
        # Overlay camera frame
        imgBackground[162:162 + 480, 55:55 + 640] = img

    # --- SCANNING STATE ---
    if app_state == 'SCANNING':
        imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[0] 
        imgBackground, add_btn_bbox = draw_scanning_ui(imgBackground)
        ax1, ay1, ax2, ay2 = add_btn_bbox
        
        # Add new student button
        if ax1 <= cx <= ax2 and ay1 <= cy <= ay2:
            app_state = 'ADD_STUDENT_PHOTO'
            continue
            
        # Start background processing
        if not is_processing:
            is_processing = True
            threading.Thread(target=process_faces_background, args=(img.copy(),), daemon=True).start()

        # Draw UI from cache
        if cached_faces:
            if cached_liveness_status == 1:
                bbox_color = (0, 255, 0) # Green (Real)
                status_text = f"REAL {int(cached_liveness_conf*100)}%"
            elif cached_liveness_status == 0:
                bbox_color = (0, 0, 255) # Red (Fake)
                status_text = f"FAKE {int(cached_liveness_conf*100)}%"
            else:
                bbox_color = (255, 0, 0) # Blue (Checking)
                status_text = "CHECKING..."

            for faceLoc in cached_faces:
                y1, x2, y2, x1 = faceLoc 
                bbox_draw = 55 + x1, 162 + y1, x2 - x1, y2 - y1
                
                imgBackground = cvzone.cornerRect(imgBackground, bbox_draw, rt=0, colorC=bbox_color, colorR=bbox_color)
                cvzone.putTextRect(imgBackground, status_text, (bbox_draw[0], max(0, bbox_draw[1] - 15)), 
                                   scale=1.5, thickness=2, colorR=bbox_color, colorB=bbox_color)

    # --- SHOW_RESULT STATE ---
    elif app_state == 'SHOW_RESULT':
        imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[mode_type]
        if mode_type == 2 and student_info:
            imgBackground = draw_student_info(imgBackground, student_info, current_student_id, img_student)
            
        if time.time() - display_start_time > DISPLAY_DURATION:
            app_state = 'SCANNING'

    # --- ADD_STUDENT_PHOTO STATE ---
    elif app_state == 'ADD_STUDENT_PHOTO':
        imgBackground, photo_btn, back_btn = draw_take_photo_screen(imgBackground)
        px1, py1, px2, py2 = photo_btn
        bx1, by1, bx2, by2 = back_btn
        
        if px1 <= cx <= px2 and py1 <= cy <= py2:
            temp_student_img = img.copy() 
            print("Photo taken. Enter name.")
            app_state = 'ADD_STUDENT_NAME'
            
        elif bx1 <= cx <= bx2 and by1 <= cy <= by2:
            app_state = 'SCANNING'

    cv2.imshow("Face Attendance System", imgBackground)
    if cv2.waitKey(1) & 0xFF == ord('q'): 
        break

cap.stop()
cv2.destroyAllWindows()