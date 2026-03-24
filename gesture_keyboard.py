# gesture_keyboard.py
import cv2
import cvzone
from cvzone.HandTrackingModule import HandDetector

# Initialize hand detector (max 1 hand for precision)
detector = HandDetector(detectionCon=0.8, maxHands=1)

class KeyButton:
    def __init__(self, pos, text, size=(50, 50)):
        self.pos = pos
        self.size = size
        self.text = text

# Create compact QWERTY layout for 640x480 screen
buttonList = []
keys = [["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
        ["A", "S", "D", "F", "G", "H", "J", "K", "L"],
        ["Z", "X", "C", "V", "B", "N", "M"]]

# Add letter buttons with row offsets
for i, row in enumerate(keys):
    for j, key in enumerate(row):
        x_offset = 20 + (i * 30) 
        buttonList.append(KeyButton([x_offset + j * 60, 220 + i * 60], key))

# Add special keys (DEL, SPACE, SAVE)
buttonList.append(KeyButton([20, 400], "DEL", (120, 50)))
buttonList.append(KeyButton([160, 400], "SPACE", (280, 50)))
buttonList.append(KeyButton([460, 400], "SAVE", (150, 50)))

keyboard_delay = 0

def draw_and_process_keyboard(img, current_text):
    global keyboard_delay
    action = None
    
    # Detect hands
    hands, img = detector.findHands(img, flipType=False) 
    
    # Draw all keyboard buttons
    for button in buttonList:
        x, y = button.pos
        w, h = button.size
        cvzone.cornerRect(img, (x, y, w, h), 10, rt=0, colorC=(0, 255, 0))
        cv2.rectangle(img, button.pos, (x + w, y + h), (255, 0, 255), cv2.FILLED)
        cv2.putText(img, button.text, (x + 10, y + 35),
                    cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 2)
                    
    if hands and keyboard_delay == 0:
        hand = hands[0]
        lmList = hand["lmList"]
        
        if lmList:
            # Landmark 8: Index finger tip (Cursor)
            # Landmark 4: Thumb tip (Click trigger)
            x8, y8, _ = lmList[8]   
            x4, y4, _ = lmList[4]   
            
            for button in buttonList:
                x, y = button.pos
                w, h = button.size
                
                # Check hover state (Index finger over button)
                if x < x8 < x + w and y < y8 < y + h:
                    # Highlight button on hover
                    cv2.rectangle(img, (x - 5, y - 5), (x + w + 5, y + h + 5), (175, 0, 175), cv2.FILLED)
                    cv2.putText(img, button.text, (x + 10, y + 35), cv2.FONT_HERSHEY_PLAIN, 2, (255, 255, 255), 3)
                    
                    # Calculate distance between thumb and index finger (Pinch gesture)
                    l, _, img = detector.findDistance((x8, y8), (x4, y4), img)
                    
                    # Pinch threshold for click registration
                    if l < 35:
                        cv2.rectangle(img, button.pos, (x + w, y + h), (0, 255, 0), cv2.FILLED)
                        
                        # Handle key actions
                        if button.text == "DEL":
                            current_text = current_text[:-1]
                        elif button.text == "SPACE":
                            current_text += " "
                        elif button.text == "SAVE":
                            action = "SAVE"
                        else:
                            current_text += button.text
                            
                        # Set delay to prevent multiple clicks
                        keyboard_delay = 20 

    if keyboard_delay > 0:
        keyboard_delay -= 1
        
    return img, current_text, action