import cv2 as cv
from datetime import datetime
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

contador = 0
lastState = "Cerrada"

def createVisit(visit):
    global lastState
    now = datetime.now()
    timestamp = now.strftime("%m_%d_%Y")
    num = db.child("Puerta").child("historial").child(timestamp).child("visitas").get().val()
    hour = now.strftime("%H:%M")
    if visit == "Abierta" and lastState =="Cerrada":
        print("Nuevo visitante\n")
        newVisit = db.child("Puerta").child("historial").child(timestamp).get().val()
        if(newVisit==None):
            db.child("Puerta").child("historial").child(timestamp).update({"hora0":hour ,"visitas":1 })
        else:
            db.child("Puerta").child("historial").child(timestamp).update({"hora"+str(num):hour ,"visitas": num +1 })
    
    lastState = visit 
    #print(f"Valores de ciclo: \n Status: {visit} \n Num_Visitas: {num} \n lastState: {lastState} \n  TimeStamp {timestamp}\n")


def face_detect(frame, target,instaces, scale, model):
    global contador
    grayFrame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    grayFrame = cv.equalizeHist(grayFrame)
    width = int(grayFrame.shape[1]) /scale
    height = int(grayFrame.shape[0])/scale
    print(width,height)
    dsize = (int(width), int(height))
    grayFrame = cv.resize(grayFrame, dsize, interpolation = cv.INTER_AREA)
    instaces = target.detectMultiScale(grayFrame, scaleFactor=1.1, minNeighbors=5, minSize=(30,30), maxSize=(200,200))
    
    for i in range(0, len(instaces)):
        realArea      = [int(instaces[i][0]*scale),int(instaces[i][1]*scale),int(instaces[i][2]*scale),int(instaces[i][3]*scale)]
        face          = grayFrame[instaces[i]]
        face          = 1.2*face
        filtered      = np.zeros((256, 256, 1), dtype = "uint8")
        img           = np.array(face, dtype=np.float32)
        filtered      = cv.bilateralFilter(img,2,15,15)
        equalized     = np.array(filtered, dtype="uint8")
        proccesedFace = cv.equalizeHist(equalized)
        conf, predictedID   = model.predict(proccesedFace)
        print(predictedID)
        print(conf)
        if(predictedID==0 and conf <100):
            contador+=1
            if(contador >=20):
                db.child("Puerta").update({"lock": 0})
                prediction = format("Welcome!!")
                #cv.putText(frame,prediction,(realArea[0] -10,realArea[1]-20),cv.FONT_HERSHEY_PLAIN, 1.0, (0,255,0), 3)
                cv.rectangle(frame,realArea, (0,255,0),6)
                cv.imshow("Detector", frame)
            else:
                prediction = format("Determining")
                #cv.putText(frame,prediction,(realArea[0] -10,realArea[1]-20),cv.FONT_HERSHEY_PLAIN, 1.0, (100,100,0), 3)
                cv.rectangle(frame,realArea, (100,100,0),6)
                cv.imshow("Detector", frame)
            
            
        else:
            contador = 0
            prediction = format("Not target!")
            #cv.putText(frame,prediction,(realArea[0] -10,realArea[1]-20),cv.FONT_HERSHEY_PLAIN, 1.0, (0,0,255), 3)
            cv.rectangle(frame,realArea, (0,0,255),6)
            cv.imshow("Detector", frame)  

    if (len(instaces)==0):
        cv.imshow("Detector", frame)


model = cv.face.LBPHFaceRecognizer_create()
model.read("faceModel.xml")
print("Modelo cargado")
faces_haar = cv.CascadeClassifier(cv.data.haarcascades+'haarcascade_frontalface_default.xml')
camera = cv.VideoCapture(2)
faces = []
# if !camera.isOpened():
#     print("Error leyendo cámara\n")
while(True):
    visit = db.child("Puerta").child("status").get().val()
    #createVisit(visit)
    if(db.child("Puerta").child("isCamera").get().val() == 1):
        rec, frame = camera.read()
        face_detect(frame,faces_haar,faces,1.5,model)
        if cv.waitKey(5) == 27:
            break
        db.child("Puerta").update({"lock": 1})
cv.destroyAllWindows()
