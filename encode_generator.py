# encode_generator.py
import cv2
import face_recognition
import pickle
import os

folderPath = 'Images'
pathList = os.listdir(folderPath)
print("Images found:", pathList)

imgList = []
studentIds = []

# Load images and extract student IDs from filenames
for path in pathList:
    imgList.append(cv2.imread(os.path.join(folderPath, path)))
    studentIds.append(os.path.splitext(path)[0])

print("Student IDs:", studentIds)

def findEncodings(imagesList):
    # Generate face encodings for known images
    encodeList = []
    for img in imagesList:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList

print("Encoding started (this may take a few minutes)...")
encodeListKnown = findEncodings(imgList)
encodeListKnownWithIds = [encodeListKnown, studentIds]
print("Encoding complete!")

# Save encodings and IDs to a pickle file
with open("EncodeFile.p", 'wb') as file:
    pickle.dump(encodeListKnownWithIds, file)
    
print("File EncodeFile.p saved successfully.")