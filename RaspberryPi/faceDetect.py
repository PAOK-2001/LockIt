#import cv2 as cv
import numpy as np
import pyrebase

config       = {
  "apiKey": "AIzaSyA5Ok0ZAenmcds4H8BsoOtii0chhavTDNY",
  "authDomain": "lockit-a8bd0.firebaseapp.com",
  "databaseURL": "https://lockit-a8bd0-default-rtdb.firebaseio.com",
  "projectId": "lockit-a8bd0",
  "storageBucket": "lockit-a8bd0.appspot.com",
  "messagingSenderId": "73690065350",
  "appId": "1:73690065350:web:7af4dc9b09e0e5ec56eac7"
}

firebase     = pyrebase.initialize_app(config)
db           = firebase.database()

global contador
contador = 0

def face_detect(frame, target,instaces, scale, model):
    grayFrame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    grayFrame = cv.equalizeHist(grayFrame)
    grayFrame = cv.resize(grayFrame,(grayFrame.size().width /scale,grayFrame.size().height /scale))
    instaces = target.detectMultiScale(grayFrame, scaleFactor=1.1, minNeighbors=5, minSize=(30,30), maxSize=(200,200))
    
    for i in range(0,instaces.len()):
        realArea      = cv.Rect(cv.cvRound(instaces[i].x*scale),cv.cvRound(instaces[i].y*scale),cv.cvRound(instaces[i].width*scale),cv.cvRound(instaces[i].height*scale))
        face          = grayFrame(instaces[i])
        face          = 1.2*face
        filtered      = np.zeros((256, 256, 1), dtype = "uint8")
        img           = np.array(face, dtype=np.float32)
        filtered      = cv.bilateralFilter(img,2,15,15)
        equalized     = np.array(filtered, dtype="uint8")
        proccesedFace = cv.equalizeHist(equalized)
        predictedID   = model.predict(proccesedFace)
        print(predictedID+"\n")
        if(predictedID==0):
            contador+=1
            if(contador >=20):
                db.child("Puerta").update({"lock": 0})
                prediction = format("Welcome!!")
                cv.putText(frame,prediction,(realArea.x -10,realArea.y-20),cv.FONT_HERSHEY_PLAIN, 1.0, (0,255,0), 3)
                cv.rectangle(frame,realArea, (0,255,0),6)
                cv.imshow("Detector", frame)
            else:
                prediction = format("Determining")
                cv.putText(frame,prediction,(realArea.x -10,realArea.y-20),cv.FONT_HERSHEY_PLAIN, 1.0, (100,100,0), 3)
                cv.rectangle(frame,realArea, (100,100,0),6)
                cv.imshow("Detector", frame)
            
            
        else:
            contador = 0
            prediction = format("Not target!")
            cv.putText(frame,prediction,(realArea.x -10,realArea.y-20),cv.FONT_HERSHEY_PLAIN, 1.0, (0,0,255), 3)
            cv.rectangle(frame,realArea, (0,0,255),6)
            cv.imshow("Detector", frame)  

    if (instaces.len()==0):
        cv.imshow("Detector", frame)


model = cv.createLBPHFaceRecognizer()
model.read("faceModel.xml")
faces_haar = cv.CascadeClassifier('haarcascade_frontalface_default.xml')
camera = cv.VideoCapture(0)
faces = []
# if !camera.isOpened():
#     print("Error leyendo cámara\n")
while(True):
    if(db.child("Puerta").child("isCamera").get().val() == 1):
        frame = camera.read()
        face_detect(frame,faces_haar,faces,1.5,model)
        if cv.waitKey(5) == 27:
            break
        db.child("Puerta").update({"lock": 1})
cv.destroyAllWindows()
