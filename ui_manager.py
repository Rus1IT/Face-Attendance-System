# ui_manager.py
import cv2
import cvzone
import os
import numpy as np

def load_ui_elements():
    imgBackground = cv2.imread('Resources/background.png')
    folderModePath = 'Resources/Modes'
    modePathList = os.listdir(folderModePath)
    imgModeList = [cv2.imread(os.path.join(folderModePath, path)) for path in modePathList]
    return imgBackground, imgModeList

def get_student_image(student_id):
    valid_extensions = ['.png', '.jpg', '.jpeg', '.webp', '.bmp']
    for ext in valid_extensions:
        img_path = f'Images/{student_id}{ext}'
        if os.path.exists(img_path):
            img_temp = cv2.imread(img_path)
            return cv2.resize(img_temp, (216, 216))
    return np.zeros((216, 216, 3), dtype=np.uint8)

def draw_student_info(imgBackground, studentInfo, student_id, imgStudent):
    cv2.putText(imgBackground, str(studentInfo.get('total_attendance', '')), (861, 125),
                cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 1)
    cv2.putText(imgBackground, str(studentInfo.get('major', '')), (1006, 550),
                cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
    cv2.putText(imgBackground, str(student_id), (1006, 493),
                cv2.FONT_HERSHEY_COMPLEX, 0.5, (255, 255, 255), 1)
    cv2.putText(imgBackground, str(studentInfo.get('standing', '')), (910, 625),
                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
    cv2.putText(imgBackground, str(studentInfo.get('year', '')), (1025, 625),
                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)
    cv2.putText(imgBackground, str(studentInfo.get('starting_year', '')), (1125, 625),
                cv2.FONT_HERSHEY_COMPLEX, 0.6, (100, 100, 100), 1)

    (w, h), _ = cv2.getTextSize(studentInfo.get('name', ''), cv2.FONT_HERSHEY_COMPLEX, 1, 1)
    offset = (414 - w) // 2
    cv2.putText(imgBackground, str(studentInfo.get('name', '')), (808 + offset, 445),
                cv2.FONT_HERSHEY_COMPLEX, 1, (50, 50, 50), 1)

    if imgStudent is not None:
        imgBackground[175:175 + 216, 909:909 + 216] = imgStudent
        
    return imgBackground

def draw_welcome_screen(imgBackground):
    overlay = imgBackground.copy()
    cv2.rectangle(overlay, (0, 0), (1280, 720), (0, 0, 0), cv2.FILLED)
    imgBackground = cv2.addWeighted(overlay, 0.7, imgBackground, 0.3, 0)
    
    cv2.putText(imgBackground, "Face Attendance System", (250, 200), 
                cv2.FONT_HERSHEY_SIMPLEX, 1.8, (255, 255, 255), 4)
    cv2.putText(imgBackground, "Developer: Ruslan Koldassov", (350, 320), 
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (200, 200, 200), 2)
    cv2.putText(imgBackground, "Course: Computer Vision", (350, 380), 
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (200, 200, 200), 2)
    cv2.putText(imgBackground, "University: SDU University", (350, 440), 
                cv2.FONT_HERSHEY_SIMPLEX, 1.2, (200, 200, 200), 2)
    
    btn_x1, btn_y1, btn_x2, btn_y2 = 500, 550, 780, 630
    cv2.rectangle(imgBackground, (btn_x1, btn_y1), (btn_x2, btn_y2), (0, 200, 0), cv2.FILLED)
    cv2.rectangle(imgBackground, (btn_x1, btn_y1), (btn_x2, btn_y2), (255, 255, 255), 2)
    cv2.putText(imgBackground, "START", (580, 605), 
                cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 255), 3)
    
    return imgBackground, (btn_x1, btn_y1, btn_x2, btn_y2)

def draw_scanning_ui(imgBackground):
    btn_x1, btn_y1, btn_x2, btn_y2 = 55, 80, 255, 130
    cv2.rectangle(imgBackground, (btn_x1, btn_y1), (btn_x2, btn_y2), (255, 150, 0), cv2.FILLED)
    cv2.putText(imgBackground, "ADD STUDENT", (65, 110), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
    
    return imgBackground, (btn_x1, btn_y1, btn_x2, btn_y2)

def draw_take_photo_screen(imgBackground):
    overlay = imgBackground.copy()
    cv2.rectangle(overlay, (808, 44), (1222, 677), (0, 0, 0), cv2.FILLED)
    imgBackground = cv2.addWeighted(overlay, 0.7, imgBackground, 0.3, 0)
    
    cv2.putText(imgBackground, "Align face and take photo", (830, 300), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

    photo_btn = (860, 350, 1170, 410) 
    cv2.rectangle(imgBackground, (photo_btn[0], photo_btn[1]), (photo_btn[2], photo_btn[3]), (0, 0, 255), cv2.FILLED)
    cv2.rectangle(imgBackground, (photo_btn[0], photo_btn[1]), (photo_btn[2], photo_btn[3]), (255, 255, 255), 2)
    cv2.putText(imgBackground, "TAKE PHOTO", (900, 390), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    back_btn = (55, 80, 155, 130)
    cv2.rectangle(imgBackground, (back_btn[0], back_btn[1]), (back_btn[2], back_btn[3]), (100, 100, 100), cv2.FILLED)
    cv2.putText(imgBackground, "BACK", (75, 110), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
                
    return imgBackground, photo_btn, back_btn